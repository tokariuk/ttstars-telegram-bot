from __future__ import annotations

# ruff: noqa: E501
import asyncio
import contextlib
import html
import logging
import time
from datetime import datetime
from typing import Final

from aiogram import Bot, F, Router
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputRichMessage,
    Message,
    PreCheckoutQuery,
)
from aiogram_i18n import I18nContext, I18nMiddleware

from app.enums.stars_order import (
    StarsOrderProductType,
    StarsOrderStatus,
    StarsPaymentProvider,
)
from app.enums.stars_sell_order import StarsSellOrderStatus
from app.models.config import AppConfig
from app.models.dto.user import UserDto
from app.services.crud import StarsOrderService, StarsSellOrderService, UserService
from app.services.crud.stars_order import PaymentCheckOutcome, PaymentCheckResult
from app.services.crypto_pay import CryptoPayService
from app.services.telegram_gifts import TelegramGiftService
from app.services.ton_pay import TonPayService
from app.stars import price_usd_for_cents
from app.telegram.keyboards.callback_data.order import (
    CDOrderCheckoutCancel,
    CDStarsSellInvoiceCancel,
)
from app.utils.localization import normalize_i18n_locale

logger: Final[logging.Logger] = logging.getLogger(name=__name__)
router: Final[Router] = Router(name=__name__)
_stars_orders_task: asyncio.Task[None] | None = None
_ton_payments_task: asyncio.Task[None] | None = None
_CLOSE_RESULT_NOTICE_CALLBACK: Final[str] = "storefront_close_result_notice"


def _close_notice_button_text(*, i18n: I18nContext, language: str) -> str:
    with i18n.use_locale(normalize_i18n_locale(language)):
        return str(i18n.messages.check_notice_close_button())


def _tx_line(tx_hash: str | None) -> str:
    if not tx_hash:
        return ""
    return f"\nTX: <code>{html.escape(tx_hash)}</code>"


def _completed_text(
    *,
    i18n: I18nContext,
    product_type: StarsOrderProductType,
    stars_count: int,
    recipient: str,
    recipient_user_id: int | None,
    premium_months: int | None,
    amount_usd: str,
    tx_hash: str | None,
) -> str:
    if product_type == StarsOrderProductType.TOPUP:
        return i18n.get("messages-order_result_completed_topup", amount=amount_usd)
    if product_type == StarsOrderProductType.GIFT:
        return i18n.get(
            "messages-order_result_completed_gift",
            recipient_user_id=recipient_user_id or 0,
            amount_usd=amount_usd,
        )
    if product_type == StarsOrderProductType.PREMIUM:
        return i18n.get(
            "messages-order_result_completed_premium",
            recipient=html.escape(recipient),
            premium_months=premium_months or 0,
            tx_line=_tx_line(tx_hash),
        )
    return i18n.get(
        "messages-order_result_completed_stars",
        recipient=html.escape(recipient),
        stars_count=stars_count,
        tx_line=_tx_line(tx_hash),
    )


def _failed_text(
    *,
    i18n: I18nContext,
    product_type: StarsOrderProductType,
    amount_usd: str,
) -> str:
    if product_type == StarsOrderProductType.TOPUP:
        return i18n.get("messages-order_result_failed_topup")
    if product_type == StarsOrderProductType.GIFT:
        return i18n.get("messages-order_result_failed_gift", amount_usd=amount_usd)
    if product_type == StarsOrderProductType.PREMIUM:
        return i18n.get("messages-order_result_failed_premium", amount_usd=amount_usd)
    return i18n.get("messages-order_result_failed_stars", amount_usd=amount_usd)


def _i18n_context_for_language(*, i18n_middleware: I18nMiddleware, language: str) -> I18nContext:
    return i18n_middleware.new_context(
        locale=normalize_i18n_locale(language),
        data={},
    )


def _as_datetime_text(value: object) -> str:
    if value is None:
        return "-"
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    return str(value)


def _needs_hot_payment_poll(result: PaymentCheckResult) -> bool:
    if result.outcome in {
        PaymentCheckOutcome.PROCESSING,
        PaymentCheckOutcome.COMPLETED,
        PaymentCheckOutcome.FAILED,
    }:
        return True

    order = result.order
    return (
        order is not None
        and order.payment_provider == StarsPaymentProvider.TON_PAY
        and order.status == StarsOrderStatus.PENDING_PAYMENT
    )


async def _notify_order_result(
    *,
    bot: Bot,
    i18n_middleware: I18nMiddleware,
    user_service: UserService,
    result: PaymentCheckResult,
) -> None:
    order = result.order
    if order is None:
        return
    if result.outcome not in {PaymentCheckOutcome.COMPLETED, PaymentCheckOutcome.FAILED}:
        return

    user = await user_service.get(user_id=order.user_id)
    language = user.language if user is not None else "en"
    i18n = _i18n_context_for_language(
        i18n_middleware=i18n_middleware,
        language=language,
    )
    amount_usd = price_usd_for_cents(order.amount_cents)
    text = (
        _completed_text(
            i18n=i18n,
            product_type=order.product_type,
            stars_count=order.stars_count,
            recipient=order.recipient_username,
            recipient_user_id=order.recipient_user_id,
            premium_months=order.premium_months,
            amount_usd=amount_usd,
            tx_hash=order.fragment_tx_hash,
        )
        if result.outcome == PaymentCheckOutcome.COMPLETED
        else _failed_text(
            i18n=i18n,
            product_type=order.product_type,
            amount_usd=amount_usd,
        )
    )
    if order.checkout_message_id is not None:
        with contextlib.suppress(Exception):
            await bot.delete_message(
                chat_id=order.user_id,
                message_id=order.checkout_message_id,
            )
    with contextlib.suppress(Exception):
        await bot.send_rich_message(
            chat_id=order.user_id,
            rich_message=InputRichMessage(html=text),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=_close_notice_button_text(i18n=i18n, language=language),
                            callback_data=_CLOSE_RESULT_NOTICE_CALLBACK,
                        ),
                    ],
                ],
            ),
        )


async def _stars_orders_loop(
    *,
    bot: Bot,
    config: AppConfig,
    i18n_middleware: I18nMiddleware,
    stars_order_service: StarsOrderService,
    user_service: UserService,
) -> None:
    idle_interval = max(3, int(config.payments.poll_interval_seconds))
    hot_interval = min(3, idle_interval)
    batch_size = max(1, int(config.payments.poll_batch_size))
    postprocess_concurrency = max(1, min(16, int(config.payments.poll_concurrency)))
    logger.info(
        "Stars orders loop started: idle_interval=%ds hot_interval=%ds batch=%d verify_concurrency=%d postprocess_concurrency=%d",
        idle_interval,
        hot_interval,
        batch_size,
        stars_order_service.poll_concurrency,
        postprocess_concurrency,
    )
    while True:
        use_hot_interval = False
        started_at = time.monotonic()
        try:
            results = await stars_order_service.poll_pending_orders(limit=batch_size)
            if results:
                use_hot_interval = any(_needs_hot_payment_poll(result) for result in results)
                await _postprocess_poll_results(
                    results=results,
                    bot=bot,
                    i18n_middleware=i18n_middleware,
                    user_service=user_service,
                    concurrency=postprocess_concurrency,
                )
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Stars orders loop iteration failed.")
        elapsed = time.monotonic() - started_at
        target_interval = hot_interval if use_hot_interval else idle_interval
        sleep_seconds = max(0.2, target_interval - elapsed)
        await asyncio.sleep(sleep_seconds)


async def _ton_payments_fast_loop(
    *,
    bot: Bot,
    i18n_middleware: I18nMiddleware,
    stars_order_service: StarsOrderService,
    user_service: UserService,
) -> None:
    interval = 3
    batch_size = 50
    postprocess_concurrency = 4
    logger.info(
        "TON payments fast loop started: interval=%ds batch=%d",
        interval,
        batch_size,
    )
    while True:
        started_at = time.monotonic()
        try:
            results = await stars_order_service.poll_pending_provider_orders(
                provider=StarsPaymentProvider.TON_PAY,
                limit=batch_size,
            )
            if results:
                await _postprocess_poll_results(
                    results=results,
                    bot=bot,
                    i18n_middleware=i18n_middleware,
                    user_service=user_service,
                    concurrency=postprocess_concurrency,
                )
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("TON payments fast loop iteration failed.")
        elapsed = time.monotonic() - started_at
        await asyncio.sleep(max(0.2, interval - elapsed))


async def _postprocess_poll_results(
    *,
    results: list[PaymentCheckResult],
    bot: Bot,
    i18n_middleware: I18nMiddleware,
    user_service: UserService,
    concurrency: int,
) -> None:
    semaphore = asyncio.Semaphore(max(1, concurrency))

    async def _process_result(result: PaymentCheckResult) -> None:
        async with semaphore:
            try:
                await _notify_order_result(
                    bot=bot,
                    i18n_middleware=i18n_middleware,
                    user_service=user_service,
                    result=result,
                )
            except Exception:
                order_id = result.order.id if result.order is not None else "-"
                logger.exception(
                    "Failed to postprocess polled order result for order %s.",
                    order_id,
                )

    await asyncio.gather(*(_process_result(result) for result in results))


async def _setup_crypto_pay_webhook(
    *,
    config: AppConfig,
    crypto_pay_service: CryptoPayService,
) -> None:
    if not crypto_pay_service.configured:
        return

    base_url = config.server.url.strip().rstrip("/")
    webhook_path = config.crypto_pay.webhook_path.strip()
    if not base_url:
        logger.warning("Skipping CryptoPay webhook setup: SERVER_URL is empty.")
        return
    if not webhook_path:
        logger.warning("Skipping CryptoPay webhook setup: CRYPTO_PAY_WEBHOOK_PATH is empty.")
        return

    normalized_path = webhook_path if webhook_path.startswith("/") else f"/{webhook_path}"
    webhook_url = f"{base_url}{normalized_path}"
    try:
        applied = await crypto_pay_service.set_webhook(webhook_url=webhook_url)
        if applied:
            logger.info("CryptoPay webhook configured: %s", webhook_url)
        else:
            logger.warning(
                "CryptoPay setWebhook API is unavailable; configure webhook manually in CryptoBot app: %s",
                webhook_url,
            )
    except Exception:
        logger.exception("Failed to configure CryptoPay webhook.")


@router.callback_query(CDOrderCheckoutCancel.filter())
async def cancel_checkout_order(
    callback: CallbackQuery,
    callback_data: CDOrderCheckoutCancel,
    stars_order_service: StarsOrderService,
    user: UserDto,
    i18n: I18nContext,
) -> None:
    order = await stars_order_service.cancel_order(
        user_id=user.id,
        order_id=callback_data.order_id,
    )
    if order is None:
        await callback.answer(str(i18n.messages.order_no_pending()))
        return

    if order.status == StarsOrderStatus.CANCELED:
        if isinstance(callback.message, Message):
            with contextlib.suppress(Exception):
                await callback.message.delete()
        await callback.answer(str(i18n.messages.order_canceled()))
        return

    await callback.answer(str(i18n.messages.order_cancel_unavailable()))


@router.callback_query(CDStarsSellInvoiceCancel.filter())
async def cancel_stars_sell_invoice(
    callback: CallbackQuery,
    callback_data: CDStarsSellInvoiceCancel,
    stars_sell_order_service: StarsSellOrderService,
    user: UserDto,
    i18n: I18nContext,
) -> None:
    order = await stars_sell_order_service.cancel_pending_order(
        user_id=user.id,
        order_id=callback_data.order_id,
    )
    if order is None:
        await callback.answer(str(i18n.messages.stars_sell_invoice_cancel_not_found()))
        return

    if order.status == StarsSellOrderStatus.CANCELED:
        if isinstance(callback.message, Message):
            with contextlib.suppress(Exception):
                await callback.message.delete()
        await callback.answer(str(i18n.messages.stars_sell_invoice_canceled()))
        return

    await callback.answer(str(i18n.messages.stars_sell_invoice_cancel_unavailable()))


@router.callback_query(F.data == _CLOSE_RESULT_NOTICE_CALLBACK)
async def close_order_result_notice(callback: CallbackQuery) -> None:
    if isinstance(callback.message, Message):
        with contextlib.suppress(Exception):
            await callback.message.delete()
    with contextlib.suppress(Exception):
        await callback.answer()


@router.pre_checkout_query(F.invoice_payload.startswith("stars_sell:"))
async def handle_stars_sell_pre_checkout(
    pre_checkout_query: PreCheckoutQuery,
    stars_sell_order_service: StarsSellOrderService,
) -> None:
    is_valid, error_message = await stars_sell_order_service.validate_pre_checkout(
        user_id=pre_checkout_query.from_user.id,
        payload=pre_checkout_query.invoice_payload,
        currency=pre_checkout_query.currency,
        total_amount=pre_checkout_query.total_amount,
    )
    await pre_checkout_query.answer(
        ok=is_valid,
        error_message=None if is_valid else (error_message or "Payment validation failed."),
    )


@router.message(F.successful_payment)
async def handle_stars_sell_successful_payment(
    message: Message,
    bot: Bot,
    config: AppConfig,
    i18n_middleware: I18nMiddleware,
    stars_sell_order_service: StarsSellOrderService,
    user_service: UserService,
) -> None:
    payment = message.successful_payment
    if payment is None:
        return
    payload = (payment.invoice_payload or "").strip()
    if not payload.startswith("stars_sell:"):
        return

    order = await stars_sell_order_service.process_successful_payment(
        user_id=message.from_user.id if message.from_user is not None else 0,
        payload=payload,
        total_amount=int(payment.total_amount),
        telegram_payment_charge_id=payment.telegram_payment_charge_id,
        provider_payment_charge_id=payment.provider_payment_charge_id,
    )
    if order is None:
        return

    # Keep chat clean: remove invoice/receipt/service messages when possible.
    message_ids_to_delete: set[int] = {int(message.message_id)}
    if order.invoice_message_id is not None:
        message_ids_to_delete.add(int(order.invoice_message_id))
    if message.reply_to_message is not None:
        message_ids_to_delete.add(int(message.reply_to_message.message_id))
    for message_id in sorted(message_ids_to_delete):
        with contextlib.suppress(Exception):
            await bot.delete_message(chat_id=order.user_id, message_id=message_id)

    user = await user_service.get(user_id=order.user_id)
    language = user.language if user is not None else "en"
    i18n = _i18n_context_for_language(
        i18n_middleware=i18n_middleware,
        language=language,
    )

    payout_available_at = _as_datetime_text(order.payout_available_at)
    with contextlib.suppress(Exception):
        await bot.send_rich_message(
            chat_id=order.user_id,
            rich_message=InputRichMessage(
                html=str(
                    i18n.messages.stars_sell_payment_confirmed(
                        order_id=order.id,
                        stars_count=order.stars_count,
                        payout_amount=price_usd_for_cents(order.payout_amount_cents),
                        wallet=order.payout_wallet,
                        payout_available_at=payout_available_at,
                        hold_days_text=str(
                            i18n.messages.stars_sell_days(count=stars_sell_order_service.hold_days)
                        ),
                    )
                ),
            ),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=_close_notice_button_text(i18n=i18n, language=language),
                            callback_data=_CLOSE_RESULT_NOTICE_CALLBACK,
                        ),
                    ],
                ],
            ),
        )

    admin_chat_id = int(config.common.admin_chat_id)
    if admin_chat_id > 0:
        with contextlib.suppress(Exception):
            await bot.send_rich_message(
                chat_id=admin_chat_id,
                rich_message=InputRichMessage(
                    html=(
                        "<blockquote><b>⭐ New Stars Sell Payment</b></blockquote>\n\n"
                        "<table>"
                        f"<tr><td>Order</td><td><code>{order.id}</code></td></tr>"
                        f"<tr><td>User</td><td><code>{order.user_id}</code></td></tr>"
                        f"<tr><td>Stars paid</td><td><code>{order.stars_count}</code></td></tr>"
                        f"<tr><th>Payout</th><td><mark>{price_usd_for_cents(order.payout_amount_cents)} USD</mark></td></tr>"
                        f"<tr><td>Wallet</td><td><code>{html.escape(order.payout_wallet)}</code></td></tr>"
                        f"<tr><td>Available after</td><td><code>{html.escape(payout_available_at)}</code></td></tr>"
                        "</table>"
                    ),
                ),
            )


@router.startup()
async def start_stars_orders_loop(
    bot: Bot,
    config: AppConfig,
    i18n_middleware: I18nMiddleware,
    crypto_pay_service: CryptoPayService,
    stars_order_service: StarsOrderService,
    user_service: UserService,
) -> None:
    global _stars_orders_task, _ton_payments_task

    await _setup_crypto_pay_webhook(
        config=config,
        crypto_pay_service=crypto_pay_service,
    )

    if _stars_orders_task is None or _stars_orders_task.done():
        _stars_orders_task = asyncio.create_task(
            _stars_orders_loop(
                bot=bot,
                config=config,
                i18n_middleware=i18n_middleware,
                stars_order_service=stars_order_service,
                user_service=user_service,
            ),
            name="stars-orders-loop",
        )
    if _ton_payments_task is None or _ton_payments_task.done():
        _ton_payments_task = asyncio.create_task(
            _ton_payments_fast_loop(
                bot=bot,
                i18n_middleware=i18n_middleware,
                stars_order_service=stars_order_service,
                user_service=user_service,
            ),
            name="ton-payments-fast-loop",
        )


@router.shutdown()
async def stop_stars_orders_loop(
    telegram_gift_service: TelegramGiftService,
    ton_pay_service: TonPayService,
) -> None:
    global _stars_orders_task, _ton_payments_task

    tasks = [
        task
        for task in (_stars_orders_task, _ton_payments_task)
        if task is not None
    ]
    _stars_orders_task = None
    _ton_payments_task = None
    if not tasks:
        with contextlib.suppress(Exception):
            await telegram_gift_service.close()
        with contextlib.suppress(Exception):
            await ton_pay_service.close()
        return
    for task in tasks:
        task.cancel()
    for task in tasks:
        with contextlib.suppress(asyncio.CancelledError):
            await task
    with contextlib.suppress(Exception):
        await telegram_gift_service.close()
    with contextlib.suppress(Exception):
        await ton_pay_service.close()
