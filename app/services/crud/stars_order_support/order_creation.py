from __future__ import annotations

import asyncio
from typing import Any

from aiohttp import ClientError
from sqlalchemy import and_, select

from app.enums.stars_order import StarsOrderProductType, StarsOrderStatus, StarsPaymentProvider
from app.models.sql import User
from app.models.sql.stars_order import StarsOrder
from app.services.postgres import SQLSessionContext
from app.stars import build_stars_pack, get_premium_pack, price_usd_for_cents
from app.utils.time import datetime_now

from .constants import BALANCE_IN_PROGRESS_ORDER_STATUSES, EXTERNAL_PAYMENT_PROVIDERS


async def create_stars_order(
    *,
    service: Any,
    provider: StarsPaymentProvider,
    user_id: int,
    recipient_username: str,
    stars_count: int,
    provider_unavailable_error_cls: type[Exception],
    validation_error_cls: type[Exception],
    insufficient_balance_error_cls: type[Exception],
    balance_in_progress_error_cls: type[Exception],
    stars_order_error_cls: type[Exception],
) -> Any:
    if provider == StarsPaymentProvider.BALANCE:
        try:
            stars_pack = build_stars_pack(stars_count=stars_count)
        except ValueError as error:
            raise validation_error_cls("Invalid stars count.") from error
        return await create_balance_product_order(
            service=service,
            user_id=user_id,
            recipient_username=recipient_username,
            stars_count=stars_count,
            amount_cents=stars_pack.price_cents,
            product_type=StarsOrderProductType.STARS,
            validation_error_cls=validation_error_cls,
            insufficient_balance_error_cls=insufficient_balance_error_cls,
            balance_in_progress_error_cls=balance_in_progress_error_cls,
        )

    if provider not in EXTERNAL_PAYMENT_PROVIDERS:
        raise provider_unavailable_error_cls(f"{provider.value} payment is not supported.")
    service._ensure_provider_configured(provider=provider)
    return await create_external_order(
        service=service,
        user_id=user_id,
        recipient_username=recipient_username,
        stars_count=stars_count,
        provider=provider,
        product_type=StarsOrderProductType.STARS,
        validation_error_cls=validation_error_cls,
        provider_unavailable_error_cls=provider_unavailable_error_cls,
        stars_order_error_cls=stars_order_error_cls,
    )


async def create_premium_order(
    *,
    service: Any,
    provider: StarsPaymentProvider,
    user_id: int,
    recipient_username: str,
    months: int,
    provider_unavailable_error_cls: type[Exception],
    validation_error_cls: type[Exception],
    insufficient_balance_error_cls: type[Exception],
    balance_in_progress_error_cls: type[Exception],
    stars_order_error_cls: type[Exception],
) -> Any:
    premium_pack = get_premium_pack(months=months)
    if provider == StarsPaymentProvider.BALANCE:
        return await create_balance_product_order(
            service=service,
            user_id=user_id,
            recipient_username=recipient_username,
            stars_count=0,
            amount_cents=premium_pack.price_cents,
            product_type=StarsOrderProductType.PREMIUM,
            premium_months=premium_pack.months,
            validation_error_cls=validation_error_cls,
            insufficient_balance_error_cls=insufficient_balance_error_cls,
            balance_in_progress_error_cls=balance_in_progress_error_cls,
        )

    if provider not in EXTERNAL_PAYMENT_PROVIDERS:
        raise provider_unavailable_error_cls(f"{provider.value} payment is not supported.")
    service._ensure_provider_configured(provider=provider)
    return await create_external_order(
        service=service,
        user_id=user_id,
        recipient_username=recipient_username,
        stars_count=0,
        provider=provider,
        product_type=StarsOrderProductType.PREMIUM,
        premium_months=premium_pack.months,
        forced_amount_cents=premium_pack.price_cents,
        validation_error_cls=validation_error_cls,
        provider_unavailable_error_cls=provider_unavailable_error_cls,
        stars_order_error_cls=stars_order_error_cls,
    )


async def create_gift_order(
    *,
    service: Any,
    provider: StarsPaymentProvider,
    user_id: int,
    recipient_username: str,
    recipient_user_id: int | None,
    gift_key: str,
    gift_message: str | None,
    gift_sender_private: bool,
    provider_unavailable_error_cls: type[Exception],
    validation_error_cls: type[Exception],
    insufficient_balance_error_cls: type[Exception],
    balance_in_progress_error_cls: type[Exception],
    stars_order_error_cls: type[Exception],
) -> Any:
    gift = service._resolve_gift_pack(gift_key=gift_key)
    normalized_message = service._normalize_gift_message(gift_message)
    if provider == StarsPaymentProvider.BALANCE:
        return await create_balance_product_order(
            service=service,
            user_id=user_id,
            recipient_username=recipient_username,
            stars_count=0,
            amount_cents=gift.price_cents,
            product_type=StarsOrderProductType.GIFT,
            recipient_user_id=recipient_user_id,
            gift_id=gift.gift_id,
            gift_message=normalized_message,
            gift_sender_private=gift_sender_private,
            validation_error_cls=validation_error_cls,
            insufficient_balance_error_cls=insufficient_balance_error_cls,
            balance_in_progress_error_cls=balance_in_progress_error_cls,
        )

    if provider not in EXTERNAL_PAYMENT_PROVIDERS:
        raise provider_unavailable_error_cls(f"{provider.value} payment is not supported.")
    service._ensure_provider_configured(provider=provider)
    return await create_external_order(
        service=service,
        user_id=user_id,
        recipient_username=recipient_username,
        stars_count=0,
        provider=provider,
        product_type=StarsOrderProductType.GIFT,
        recipient_user_id=recipient_user_id,
        gift_id=gift.gift_id,
        gift_message=normalized_message,
        gift_sender_private=gift_sender_private,
        forced_amount_cents=gift.price_cents,
        validation_error_cls=validation_error_cls,
        provider_unavailable_error_cls=provider_unavailable_error_cls,
        stars_order_error_cls=stars_order_error_cls,
    )


async def create_topup_order(
    *,
    service: Any,
    provider: StarsPaymentProvider,
    user_id: int,
    amount_cents: int,
    provider_unavailable_error_cls: type[Exception],
    validation_error_cls: type[Exception],
    stars_order_error_cls: type[Exception],
) -> Any:
    if provider == StarsPaymentProvider.BALANCE:
        raise provider_unavailable_error_cls(
            "Balance provider is not supported for top-up orders."
        )
    if provider not in EXTERNAL_PAYMENT_PROVIDERS:
        raise provider_unavailable_error_cls(f"{provider.value} payment is not supported.")
    service._ensure_provider_configured(provider=provider)
    return await create_external_order(
        service=service,
        user_id=user_id,
        recipient_username="balance",
        stars_count=0,
        provider=provider,
        product_type=StarsOrderProductType.TOPUP,
        forced_amount_cents=amount_cents,
        validation_error_cls=validation_error_cls,
        provider_unavailable_error_cls=provider_unavailable_error_cls,
        stars_order_error_cls=stars_order_error_cls,
    )


async def create_balance_product_order(
    *,
    service: Any,
    user_id: int,
    recipient_username: str,
    stars_count: int,
    amount_cents: int,
    product_type: StarsOrderProductType,
    premium_months: int | None = None,
    recipient_user_id: int | None = None,
    gift_id: str | None = None,
    gift_message: str | None = None,
    gift_sender_private: bool | None = None,
    validation_error_cls: type[Exception],
    insufficient_balance_error_cls: type[Exception],
    balance_in_progress_error_cls: type[Exception],
) -> Any:
    prepared = await service._prepare_balance_order_payload(
        recipient_username=recipient_username,
        product_type=product_type,
        recipient_user_id=recipient_user_id,
        gift_id=gift_id,
        gift_message=gift_message,
        gift_sender_private=gift_sender_private,
        validation_error_cls=validation_error_cls,
    )

    async with SQLSessionContext(session_pool=service.session_pool) as (repository, _uow):
        session = repository.session

        user = await session.scalar(select(User).where(User.id == user_id).with_for_update())
        if user is None:
            raise validation_error_cls("User not found.")

        active_order = await session.scalar(
            select(StarsOrder)
            .where(
                and_(
                    StarsOrder.user_id == user_id,
                    StarsOrder.payment_provider == StarsPaymentProvider.BALANCE.value,
                    StarsOrder.status.in_(
                        [status.value for status in BALANCE_IN_PROGRESS_ORDER_STATUSES]
                    ),
                )
            )
            .order_by(StarsOrder.created_at.desc())
            .limit(1)
        )
        if active_order is not None:
            raise balance_in_progress_error_cls(
                f"Balance order {active_order.id} is already processing."
            )

        if int(user.balance_cents) < amount_cents:
            raise insufficient_balance_error_cls("Not enough balance.")

        user.balance_cents = int(user.balance_cents) - amount_cents
        order = StarsOrder(
            user_id=user_id,
            recipient_username=prepared.recipient_username,
            stars_count=stars_count,
            product_type=product_type.value,
            premium_months=premium_months,
            recipient_user_id=prepared.recipient_user_id,
            gift_id=prepared.gift_id,
            gift_message=prepared.gift_message,
            gift_sender_private=prepared.gift_sender_private,
            amount_cents=amount_cents,
            payment_provider=StarsPaymentProvider.BALANCE.value,
            payment_currency="USD",
            status=StarsOrderStatus.PAYMENT_CONFIRMED.value,
            provider_status="paid_from_balance",
            paid_at=datetime_now(),
        )
        session.add(order)
        await session.commit()
        created = order.dto()

    await service._clear_user_cache(user_id=user_id)
    return created


async def create_external_order(
    *,
    service: Any,
    user_id: int,
    recipient_username: str,
    stars_count: int,
    provider: StarsPaymentProvider,
    product_type: StarsOrderProductType,
    premium_months: int | None = None,
    forced_amount_cents: int | None = None,
    recipient_user_id: int | None = None,
    gift_id: str | None = None,
    gift_message: str | None = None,
    gift_sender_private: bool | None = None,
    validation_error_cls: type[Exception],
    provider_unavailable_error_cls: type[Exception],
    stars_order_error_cls: type[Exception],
) -> Any:
    prepared = await service._prepare_external_order_payload(
        user_id=user_id,
        recipient_username=recipient_username,
        stars_count=stars_count,
        product_type=product_type,
        premium_months=premium_months,
        forced_amount_cents=forced_amount_cents,
        recipient_user_id=recipient_user_id,
        gift_id=gift_id,
        gift_message=gift_message,
        gift_sender_private=gift_sender_private,
        validation_error_cls=validation_error_cls,
    )

    service._validate_provider_min_payment_amount(
        provider=provider,
        amount_cents=prepared.amount_cents,
    )

    checkout_pricing = service._build_checkout_pricing(
        provider=provider,
        net_amount_cents=prepared.amount_cents,
    )
    checkout_amount_usd = price_usd_for_cents(checkout_pricing.invoice_amount_cents)
    created = await service._create_order_record(
        user_id=user_id,
        recipient_username=prepared.recipient_username,
        stars_count=prepared.stars_count,
        amount_cents=prepared.amount_cents,
        payment_provider=provider,
        payment_currency=service._provider_currency(provider=provider),
        status=StarsOrderStatus.CREATING_PAYMENT,
        product_type=product_type,
        premium_months=prepared.premium_months,
        recipient_user_id=prepared.recipient_user_id,
        gift_id=prepared.gift_id,
        gift_message=prepared.gift_message,
        gift_sender_private=prepared.gift_sender_private,
    )

    try:
        updated = await service._create_and_attach_invoice(
            order=created,
            provider=provider,
            user_id=user_id,
            checkout_pricing=checkout_pricing,
            checkout_amount_usd=checkout_amount_usd,
            description=prepared.description,
        )
    except Exception as error:
        error_text = str(error).strip() or error.__class__.__name__
        await service._update_order(
            order_id=created.id,
            status=StarsOrderStatus.FAILED,
            failed_at=datetime_now(),
            fragment_error=error_text,
        )
        if isinstance(error, validation_error_cls):
            raise error
        if isinstance(error, (asyncio.TimeoutError, TimeoutError, ClientError)):
            raise provider_unavailable_error_cls("Payment provider is unavailable.") from error
        raise stars_order_error_cls("Failed to create payment invoice.") from error

    if updated is None:
        raise stars_order_error_cls("Failed to persist order invoice.")
    return updated
