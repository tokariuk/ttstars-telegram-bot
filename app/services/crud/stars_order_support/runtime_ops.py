from __future__ import annotations

import asyncio
import logging
from typing import Any

from sqlalchemy import select

from app.enums.stars_order import StarsOrderProductType, StarsOrderStatus, StarsPaymentProvider
from app.models.sql import User
from app.models.sql.stars_order import StarsOrder
from app.services.postgres import SQLSessionContext
from app.utils.time import datetime_now

from .constants import REFERRAL_LEVELS_COUNT


async def poll_pending_orders(
    *,
    service: Any,
    limit: int,
    logger: logging.Logger,
    provider: StarsPaymentProvider | None = None,
) -> list[Any]:
    if limit <= 0:
        return []
    async with SQLSessionContext(session_pool=service.session_pool) as (repository, _uow):
        pending_orders = await repository.stars_orders.list_pending_for_polling(
            limit=limit,
            provider=provider,
        )
    if not pending_orders:
        return []

    semaphore = asyncio.Semaphore(service.poll_concurrency)

    async def verify_one(order_id: int) -> Any | None:
        async with semaphore:
            try:
                return await service.verify_order(order_id=order_id)
            except Exception:
                logger.exception(
                    "Failed to verify pending order %s in polling loop.",
                    order_id,
                )
                return None

    results = await asyncio.gather(
        *(verify_one(order.id) for order in pending_orders),
    )
    return [result for result in results if result is not None]


async def apply_referral_rewards(
    *,
    service: Any,
    order_id: int,
) -> None:
    if all(percent <= 0 for percent in service.referral_level_percents):
        return

    rewarded_user_ids: set[int] = set()
    async with SQLSessionContext(session_pool=service.session_pool) as (repository, _uow):
        session = repository.session
        order = await _load_locked_order(session=session, order_id=order_id)
        if order is None or order.referral_processed_at is not None:
            return

        if await _finalize_if_non_rewardable(session=session, order=order):
            return

        buyer = await _load_locked_user(session=session, user_id=order.user_id)
        if buyer is None:
            await _mark_referral_processed_empty(session=session, order=order)
            return

        reward_level_cents = await _apply_referral_chain(
            service=service,
            session=session,
            buyer=buyer,
            order=order,
            rewarded_user_ids=rewarded_user_ids,
        )
        _set_order_referral_totals(order=order, reward_level_cents=reward_level_cents)
        await session.commit()

    for user_id in rewarded_user_ids:
        await service._clear_user_cache(user_id=user_id)


async def mark_failed_and_refund(
    *,
    service: Any,
    order: Any,
    error_text: str,
    order_error_cls: type[Exception],
    logger: logging.Logger,
) -> Any:
    failed = await service._update_order(
        order_id=order.id,
        status=StarsOrderStatus.FAILED,
        failed_at=datetime_now(),
        fragment_error=error_text,
        provider_status="delivery_failed",
    )
    if failed is None:
        raise order_error_cls("Failed to mark order as failed.")

    if failed.amount_cents <= 0:
        return failed

    refunded = await service._credit_user_balance(
        user_id=failed.user_id,
        amount_cents=failed.amount_cents,
    )
    if not refunded:
        logger.error(
            (
                "Order %s failed, but refund to user balance failed "
                "(user_id=%s, amount_cents=%s)."
            ),
            failed.id,
            failed.user_id,
            failed.amount_cents,
        )
        return failed

    refunded_order = await service._update_order(
        order_id=failed.id,
        provider_status="delivery_failed_refunded_to_balance",
    )
    return refunded_order if refunded_order is not None else failed


async def _load_locked_order(*, session: Any, order_id: int) -> StarsOrder | None:
    return await session.scalar(
        select(StarsOrder).where(StarsOrder.id == order_id).with_for_update()
    )


async def _load_locked_user(*, session: Any, user_id: int) -> User | None:
    return await session.scalar(select(User).where(User.id == user_id).with_for_update())


async def _finalize_if_non_rewardable(*, session: Any, order: StarsOrder) -> bool:
    if order.product_type != StarsOrderProductType.TOPUP.value:
        return False
    await _mark_referral_processed_empty(session=session, order=order)
    return True


async def _mark_referral_processed_empty(*, session: Any, order: StarsOrder) -> None:
    order.referral_processed_at = datetime_now()
    order.referral_reward_total_cents = 0
    order.referral_reward_level1_cents = 0
    order.referral_reward_level2_cents = 0
    order.referral_reward_level3_cents = 0
    await session.commit()


async def _apply_referral_chain(
    *,
    service: Any,
    session: Any,
    buyer: User,
    order: StarsOrder,
    rewarded_user_ids: set[int],
) -> list[int]:
    reward_level_cents = [0, 0, 0]
    visited_user_ids: set[int] = {buyer.id}
    next_referrer_id = buyer.referrer_id

    for level in range(REFERRAL_LEVELS_COUNT):
        if next_referrer_id is None or next_referrer_id in visited_user_ids:
            break
        referrer = await _load_locked_user(session=session, user_id=next_referrer_id)
        if referrer is None:
            break

        visited_user_ids.add(referrer.id)
        reward_cents = service._calculate_referral_reward_cents(
            amount_cents=order.amount_cents,
            percent=service.referral_level_percents[level],
        )
        if reward_cents > 0:
            referrer.referral_balance_cents = int(referrer.referral_balance_cents) + reward_cents
            referrer.referral_earned_cents = int(referrer.referral_earned_cents) + reward_cents
            rewarded_user_ids.add(referrer.id)
        reward_level_cents[level] = reward_cents
        next_referrer_id = referrer.referrer_id
    return reward_level_cents


def _set_order_referral_totals(*, order: StarsOrder, reward_level_cents: list[int]) -> None:
    order.referral_reward_level1_cents = reward_level_cents[0]
    order.referral_reward_level2_cents = reward_level_cents[1]
    order.referral_reward_level3_cents = reward_level_cents[2]
    order.referral_reward_total_cents = sum(reward_level_cents)
    order.referral_processed_at = datetime_now()
