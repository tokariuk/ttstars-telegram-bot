from __future__ import annotations

from typing import Annotated, Optional

from fastapi import APIRouter, Query, Request, status

from app.models.dto.miniapp import (
    MeResponse,
    ProfileStatsResponse,
    PromoActivateRequest,
    PromoActivateResponse,
    ReferralMemberResponse,
    ReferralsResponse,
    ReferralWithdrawRequest,
    ReferralWithdrawResponse,
)
from app.services.crud import UserService
from app.stars import price_usd_for_cents

from ..deps import CurrentUser, StarsOrderServiceDep, UserServiceDep, resolve_bot_username
from ..errors import ApiError, ErrorCode, conflict, not_found, validation_error
from ..serializers import build_user_response

router = APIRouter(prefix="/me", tags=["profile"])


@router.get("", summary="Current user with lifetime purchase stats")
async def get_me(
    auth: CurrentUser,
    stars_order_service: StarsOrderServiceDep,
) -> MeResponse:
    stats = await stars_order_service.profile_stats(user_id=auth.user.id)
    return MeResponse(
        user=build_user_response(auth.user),
        stats=ProfileStatsResponse(
            total_stars_purchased=stats.total_stars_purchased,
            total_premiums_purchased=stats.total_premiums_purchased,
            total_stars_amount_cents=stats.total_stars_amount_cents,
            total_stars_amount_usd=price_usd_for_cents(stats.total_stars_amount_cents),
            total_premiums_amount_cents=stats.total_premiums_amount_cents,
            total_premiums_amount_usd=price_usd_for_cents(stats.total_premiums_amount_cents),
        ),
    )


@router.get("/referrals", summary="Referral program overview and members")
async def get_referrals(
    request: Request,
    auth: CurrentUser,
    user_service: UserServiceDep,
    limit: Annotated[int, Query(ge=1, le=200)] = 60,
) -> ReferralsResponse:
    bot_username = await resolve_bot_username(request)
    overview = await user_service.referral_overview(
        user_id=auth.user.id,
        bot_username=bot_username,
        referrals_limit=limit,
    )
    if overview is None:
        not_found("Referrals are unavailable.")
    return ReferralsResponse(
        referral_link=overview.referral_link,
        referral_balance_cents=overview.referral_balance_cents,
        referral_balance_usd=price_usd_for_cents(overview.referral_balance_cents),
        referral_earned_cents=overview.referral_earned_cents,
        referral_earned_usd=price_usd_for_cents(overview.referral_earned_cents),
        level1_count=overview.level1_count,
        level2_count=overview.level2_count,
        level3_count=overview.level3_count,
        members=[
            ReferralMemberResponse(
                user_id=member.user_id,
                name=member.name,
                level=member.level,
                joined_at=member.joined_at,
            )
            for member in overview.referrals
        ],
    )


@router.post("/referrals/withdraw", summary="Move referral earnings into the main balance")
async def withdraw_referrals(
    auth: CurrentUser,
    user_service: UserServiceDep,
    payload: Optional[ReferralWithdrawRequest] = None,
) -> ReferralWithdrawResponse:
    transferred = await user_service.withdraw_referral_balance_to_main(
        user_id=auth.user.id,
        amount_cents=payload.amount_cents if payload is not None else None,
    )
    if transferred <= 0:
        conflict("No referral funds were transferred.", code=ErrorCode.NOTHING_TO_WITHDRAW)
    user = await user_service.get(user_id=auth.user.id)
    if user is None:
        not_found("User was not found.")
    return ReferralWithdrawResponse(
        transferred_amount_cents=transferred,
        transferred_amount_usd=price_usd_for_cents(transferred),
        user=build_user_response(user),
    )


@router.post("/promo", summary="Activate a promo code and credit the balance")
async def activate_promo(
    payload: PromoActivateRequest,
    auth: CurrentUser,
    user_service: UserServiceDep,
) -> PromoActivateResponse:
    try:
        amount_cents = await user_service.activate_promo_code(
            user_id=auth.user.id,
            code=payload.code,
        )
    except UserService.PromoCodeAlreadyUsedError as error:
        conflict(str(error), code=ErrorCode.PROMO_ALREADY_USED)
    except UserService.PromoCodeInvalidError as error:
        validation_error(str(error), code=ErrorCode.PROMO_INVALID)
    except UserService.PromoCodeError as error:
        raise ApiError(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code=ErrorCode.INTERNAL,
            message=str(error),
        ) from error
    user = await user_service.get(user_id=auth.user.id)
    if user is None:
        not_found("User was not found after promo activation.")
    return PromoActivateResponse(
        activated_amount_cents=amount_cents,
        activated_amount_usd=price_usd_for_cents(amount_cents),
        user=build_user_response(user),
    )
