from __future__ import annotations

from app.models.dto.check import CheckDto
from app.models.dto.miniapp import (
    AdminPromoResponse,
    AdminUserResponse,
    CheckResponse,
    OrderResponse,
    PaymentCheckResponse,
    SellOrderResponse,
    UserResponse,
)
from app.models.dto.stars_order import StarsOrderDto
from app.models.dto.stars_sell_order import StarsSellOrderDto
from app.models.dto.user import UserDto
from app.services.crud import CheckService, StarsOrderService
from app.services.crud.stars_order import PaymentCheckResult
from app.services.promo_codes import PromoCodeInfo
from app.stars import price_usd_for_cents


def build_user_response(user: UserDto) -> UserResponse:
    return UserResponse(
        id=user.id,
        name=user.name,
        language=user.language,
        language_code=user.language_code,
        balance_cents=user.balance_cents,
        balance_usd=price_usd_for_cents(user.balance_cents),
        referral_balance_cents=user.referral_balance_cents,
        referral_balance_usd=price_usd_for_cents(user.referral_balance_cents),
        referral_earned_cents=user.referral_earned_cents,
        referral_earned_usd=price_usd_for_cents(user.referral_earned_cents),
        referrer_id=user.referrer_id,
        bot_blocked=user.bot_blocked,
    )


def build_order_response(
    *,
    stars_order_service: StarsOrderService,
    order: StarsOrderDto,
) -> OrderResponse:
    pricing = stars_order_service.checkout_pricing_for_order(order=order)
    return OrderResponse(
        id=order.id,
        product_type=order.product_type,
        status=order.status,
        is_open=order.is_open,
        recipient_username=order.recipient_username,
        stars_count=order.stars_count,
        premium_months=order.premium_months,
        amount_cents=order.amount_cents,
        amount_usd=price_usd_for_cents(order.amount_cents),
        payment_provider=order.payment_provider,
        payment_currency=order.payment_currency,
        checkout_total_cents=pricing.customer_total_cents,
        checkout_total_usd=price_usd_for_cents(pricing.customer_total_cents),
        checkout_fee_percent=pricing.fee_percent_text,
        checkout_url=order.checkout_url,
        provider_status=order.provider_status,
        created_at=order.created_at,
        updated_at=order.updated_at,
        paid_at=order.paid_at,
        fulfilled_at=order.fulfilled_at,
        canceled_at=order.canceled_at,
        failed_at=order.failed_at,
    )


def build_check_response(*, check: CheckDto, bot_username: str) -> CheckResponse:
    return CheckResponse(
        id=check.id,
        code=check.code,
        creator_id=check.creator_id,
        stars_count=check.stars_count,
        amount_cents=check.amount_cents,
        amount_usd=price_usd_for_cents(check.amount_cents),
        status=check.status,
        claim_username=check.claim_username,
        has_password=bool(check.claim_password_hash),
        recipient_id=check.recipient_id,
        link=CheckService.build_start_link(bot_username=bot_username, code=check.code),
        last_error=check.last_error,
        redeemed_at=check.redeemed_at,
        closed_at=check.closed_at,
        created_at=check.created_at,
        updated_at=check.updated_at,
    )


def build_sell_order_response(
    *,
    order: StarsSellOrderDto,
    invoice_link: str | None = None,
) -> SellOrderResponse:
    return SellOrderResponse(
        id=order.id,
        stars_count=order.stars_count,
        payout_method=order.payout_method,
        payout_wallet=order.payout_wallet,
        payout_amount_cents=order.payout_amount_cents,
        payout_amount_usd=price_usd_for_cents(order.payout_amount_cents),
        invoice_total_amount=order.invoice_total_amount,
        status=order.status,
        failure_reason=order.failure_reason,
        resolution_reason=order.resolution_reason,
        resolution_note=order.resolution_note,
        paid_stars_amount=order.paid_stars_amount,
        invoice_link=invoice_link,
        paid_at=order.paid_at,
        payout_available_at=order.payout_available_at,
        completed_at=order.completed_at,
        rejected_at=order.rejected_at,
        refunded_at=order.refunded_at,
        created_at=order.created_at,
        updated_at=order.updated_at,
    )


def build_admin_user_response(user: UserDto) -> AdminUserResponse:
    return AdminUserResponse(
        id=user.id,
        name=user.name,
        language=user.language,
        language_code=user.language_code,
        balance_cents=user.balance_cents,
        balance_usd=price_usd_for_cents(user.balance_cents),
        referral_balance_cents=user.referral_balance_cents,
        referral_balance_usd=price_usd_for_cents(user.referral_balance_cents),
        referral_earned_cents=user.referral_earned_cents,
        referral_earned_usd=price_usd_for_cents(user.referral_earned_cents),
        referrer_id=user.referrer_id,
        bot_blocked=user.bot_blocked,
        blocked_at=user.blocked_at,
    )


def build_promo_response(info: PromoCodeInfo) -> AdminPromoResponse:
    return AdminPromoResponse(
        code=info.code,
        amount_cents=info.amount_cents,
        amount_usd=price_usd_for_cents(info.amount_cents),
        activations=info.activations,
        max_activations=info.max_activations,
        created_at=info.created_at,
    )


def build_payment_check_response(
    *,
    stars_order_service: StarsOrderService,
    result: PaymentCheckResult,
) -> PaymentCheckResponse:
    order = (
        build_order_response(stars_order_service=stars_order_service, order=result.order)
        if result.order is not None
        else None
    )
    return PaymentCheckResponse(
        outcome=result.outcome.value,
        provider_status=result.provider_status,
        order=order,
    )
