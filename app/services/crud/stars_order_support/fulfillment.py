from __future__ import annotations

import logging
from typing import Any

from app.enums.stars_order import StarsOrderProductType, StarsOrderStatus
from app.models.dto.stars_order import StarsOrderDto
from app.utils.time import datetime_now


async def fulfill_paid_order(  # noqa: C901
    *,
    service: Any,
    order_id: int,
    order_error_cls: type[Exception],
    logger: logging.Logger,
) -> StarsOrderDto:
    order = await service.get(order_id=order_id)
    if order is None:
        raise order_error_cls("Order not found during fulfillment.")
    if order.status == StarsOrderStatus.COMPLETED:
        return order
    if order.status == StarsOrderStatus.FAILED:
        return order
    if order.status not in {
        StarsOrderStatus.PAYMENT_CONFIRMED,
        StarsOrderStatus.FULFILLING,
    }:
        return order

    lock_token = await service._acquire_fulfill_lock(order_id=order.id)
    if lock_token is None:
        return order

    try:
        current = await service.get(order_id=order.id)
        if current is None:
            raise order_error_cls("Order not found during fulfillment.")
        if current.status == StarsOrderStatus.COMPLETED:
            return current
        if current.status == StarsOrderStatus.FAILED:
            return current

        if current.status == StarsOrderStatus.PAYMENT_CONFIRMED:
            transitioned = await service._transition_order_status(
                order_id=current.id,
                from_statuses=[StarsOrderStatus.PAYMENT_CONFIRMED],
                to_status=StarsOrderStatus.FULFILLING,
            )
            if transitioned is None:
                latest = await service.get(order_id=current.id)
                if latest is None:
                    raise order_error_cls("Order not found during fulfillment.")
                return latest
            current = transitioned

        if current.status != StarsOrderStatus.FULFILLING:
            return current

        if current.product_type == StarsOrderProductType.TOPUP:
            return await _fulfill_topup_order(
                service=service,
                order=current,
                order_error_cls=order_error_cls,
            )

        if current.product_type == StarsOrderProductType.GIFT:
            return await _fulfill_gift_order(
                service=service,
                order=current,
                order_error_cls=order_error_cls,
                logger=logger,
            )

        return await _fulfill_fragment_order(
            service=service,
            order=current,
            order_error_cls=order_error_cls,
            logger=logger,
        )
    finally:
        await service._release_fulfill_lock(order_id=order.id, lock_token=lock_token)


async def _fulfill_topup_order(
    *,
    service: Any,
    order: StarsOrderDto,
    order_error_cls: type[Exception],
) -> StarsOrderDto:
    credited = await service._credit_user_balance(
        user_id=order.user_id,
        amount_cents=order.amount_cents,
    )
    if not credited:
        retrying = await service._update_order(
            order_id=order.id,
            status=StarsOrderStatus.PAYMENT_CONFIRMED,
            provider_status="topup_credit_retry",
            fragment_error="Failed to credit user balance.",
            failed_at=None,
        )
        if retrying is None:
            raise order_error_cls("Failed to mark top-up order for retry.")
        return retrying

    completed_topup = await service._update_order(
        order_id=order.id,
        status=StarsOrderStatus.COMPLETED,
        provider_status="topup_completed",
        fragment_tx_hash=None,
        fulfilled_at=datetime_now(),
    )
    if completed_topup is None:
        raise order_error_cls("Failed to mark top-up order as completed.")
    return completed_topup


async def _fulfill_gift_order(
    *,
    service: Any,
    order: StarsOrderDto,
    order_error_cls: type[Exception],
    logger: logging.Logger,
) -> StarsOrderDto:
    if (
        order.recipient_user_id is None or order.recipient_user_id <= 0
    ) and not order.recipient_username:
        return await service._mark_failed_and_refund(
            order=order,
            error_text="Gift recipient is missing.",
        )
    if order.gift_id is None or not order.gift_id.strip():
        return await service._mark_failed_and_refund(
            order=order,
            error_text="Gift ID is missing.",
        )
    if not service.telegram_gift_service.configured:
        return await service._mark_failed_and_refund(
            order=order,
            error_text="Telegram gift service is not configured.",
        )

    try:
        await service.telegram_gift_service.send_gift(
            user_id=order.recipient_user_id,
            recipient_username=order.recipient_username,
            gift_id=order.gift_id,
            text=order.gift_message,
            is_private=order.gift_sender_private,
            pay_for_upgrade=False,
        )
    except Exception as error:
        error_text = str(error).strip() or "Unknown Telegram gift error."
        if service._is_retryable_delivery_error(error_text):
            retrying = await service._update_order(
                order_id=order.id,
                status=StarsOrderStatus.PAYMENT_CONFIRMED,
                fragment_error=error_text,
                provider_status="gift_delivery_retry",
                failed_at=None,
            )
            if retrying is None:
                raise order_error_cls("Failed to mark gift order for delivery retry.") from error
            return retrying

        return await service._mark_failed_and_refund(
            order=order,
            error_text=error_text,
        )

    completed_gift = await service._update_order(
        order_id=order.id,
        status=StarsOrderStatus.COMPLETED,
        provider_status="gift_confirmed",
        fragment_tx_hash=None,
        fulfilled_at=datetime_now(),
    )
    if completed_gift is None:
        raise order_error_cls("Failed to mark gift order as completed.")
    try:
        await service._apply_referral_rewards(order_id=completed_gift.id)
    except Exception:
        logger.exception(
            "Failed to apply referral rewards for gift order %s.",
            completed_gift.id,
        )
    return completed_gift


async def _fulfill_fragment_order(
    *,
    service: Any,
    order: StarsOrderDto,
    order_error_cls: type[Exception],
    logger: logging.Logger,
) -> StarsOrderDto:
    if not service.fragment_stars_service.configured:
        return await service._mark_failed_and_refund(
            order=order,
            error_text="Fragment service is not configured.",
        )

    try:
        if order.product_type == StarsOrderProductType.PREMIUM:
            if order.premium_months is None:
                raise RuntimeError("Premium period is missing.")
            purchase = await service.fragment_stars_service.buy_premium(
                recipient_username=order.recipient_username,
                months=order.premium_months,
            )
        else:
            purchase = await service.fragment_stars_service.buy_stars(
                recipient_username=order.recipient_username,
                stars_count=order.stars_count,
            )
    except Exception as error:
        error_text = str(error).strip() or "Unknown fragment delivery error."
        if service._is_retryable_delivery_error(error_text):
            retrying = await service._update_order(
                order_id=order.id,
                status=StarsOrderStatus.PAYMENT_CONFIRMED,
                fragment_error=error_text,
                provider_status="delivery_retry",
                failed_at=None,
            )
            if retrying is None:
                raise order_error_cls("Failed to mark order for delivery retry.") from error
            return retrying

        return await service._mark_failed_and_refund(
            order=order,
            error_text=error_text,
        )

    completed = await service._update_order(
        order_id=order.id,
        status=StarsOrderStatus.COMPLETED,
        provider_status=(
            "premium_confirmed"
            if order.product_type == StarsOrderProductType.PREMIUM
            else "confirmed"
        ),
        fragment_tx_hash=purchase.tx_hash,
        fulfilled_at=datetime_now(),
    )
    if completed is None:
        raise order_error_cls("Failed to mark order as completed.")
    try:
        await service._apply_referral_rewards(order_id=completed.id)
    except Exception:
        logger.exception(
            "Failed to apply referral rewards for order %s.",
            completed.id,
        )
    return completed
