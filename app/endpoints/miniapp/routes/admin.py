from __future__ import annotations

from typing import Annotated, Optional

from fastapi import APIRouter, Query, Request

from app.enums.check import CheckStatus
from app.enums.stars_order import (
    StarsOrderProductType,
    StarsOrderStatus,
    StarsPaymentProvider,
)
from app.enums.stars_sell_order import StarsSellOrderResolutionReason, StarsSellOrderStatus
from app.models.dto.miniapp import (
    AdminBalanceOperation,
    AdminBalanceRequest,
    AdminBlockRequest,
    AdminChecksPageResponse,
    AdminOrdersPageResponse,
    AdminOrderStatsResponse,
    AdminProductStatResponse,
    AdminPromoCreateRequest,
    AdminPromoResponse,
    AdminPromosResponse,
    AdminSellCompleteRequest,
    AdminSellOrdersPageResponse,
    AdminSellRejectRequest,
    AdminSellResolveRequest,
    AdminSellStatsResponse,
    AdminStatsResponse,
    AdminUserDetailResponse,
    AdminUserResponse,
    AdminUsersPageResponse,
    AdminUserStatsResponse,
    CheckResponse,
    OkResponse,
    OrderResponse,
    PaymentCheckResponse,
    ProfileStatsResponse,
    SellOrderResponse,
)
from app.services.crud.stars_sell_order import (
    NotReadyForPayoutError,
    OrderNotFoundError,
    StatusConflictError,
)
from app.services.promo_codes import PromoCodeService
from app.stars import price_usd_for_cents
from app.utils.time import datetime_now

from ..deps import (
    CheckServiceDep,
    CurrentAdmin,
    PromoCodeServiceDep,
    StarsOrderServiceDep,
    StarsSellOrderServiceDep,
    UserServiceDep,
    resolve_bot_username,
)
from ..errors import ErrorCode, conflict, not_found, validation_error
from ..pricing import parse_usd_amount_to_cents
from ..serializers import (
    build_admin_user_response,
    build_check_response,
    build_order_response,
    build_payment_check_response,
    build_promo_response,
    build_sell_order_response,
)

router = APIRouter(prefix="/admin", tags=["admin"])


# --------------------------------------------------------------------------- #
# Dashboard
# --------------------------------------------------------------------------- #
@router.get("/stats", summary="Aggregated dashboard metrics")
async def admin_stats(
    _admin: CurrentAdmin,
    user_service: UserServiceDep,
    stars_order_service: StarsOrderServiceDep,
    stars_sell_order_service: StarsSellOrderServiceDep,
) -> AdminStatsResponse:
    total_users = await user_service.count()
    active_users = await user_service.count_active()
    users_with_balance = await user_service.count_with_positive_balance()
    total_balance_cents = await user_service.sum_balances_cents()
    orders = await stars_order_service.admin_stats()
    sell = await stars_sell_order_service.admin_stats()
    return AdminStatsResponse(
        users=AdminUserStatsResponse(
            total_users=total_users,
            active_users=active_users,
            users_with_balance=users_with_balance,
            total_balance_cents=total_balance_cents,
            total_balance_usd=price_usd_for_cents(total_balance_cents),
        ),
        orders=AdminOrderStatsResponse(
            total_orders=orders.total_orders,
            created_last_24h=orders.created_last_24h,
            created_last_7d=orders.created_last_7d,
            paid_last_24h=orders.paid_last_24h,
            paid_last_7d=orders.paid_last_7d,
            paid_amount_last_24h_cents=orders.paid_amount_last_24h_cents,
            paid_amount_last_24h_usd=price_usd_for_cents(orders.paid_amount_last_24h_cents),
            paid_amount_last_7d_cents=orders.paid_amount_last_7d_cents,
            paid_amount_last_7d_usd=price_usd_for_cents(orders.paid_amount_last_7d_cents),
            completed_amount_cents=orders.completed_amount_cents,
            completed_amount_usd=price_usd_for_cents(orders.completed_amount_cents),
            completed_stars_count=orders.completed_stars_count,
            status_counts={
                status.value: count for status, count in orders.status_counts.items()
            },
            completed_products={
                product.value: AdminProductStatResponse(
                    count=stat.count,
                    amount_cents=stat.amount_cents,
                    amount_usd=price_usd_for_cents(stat.amount_cents),
                    stars_count=stat.stars_count,
                )
                for product, stat in orders.completed_products.items()
            },
        ),
        sell=AdminSellStatsResponse(
            total_orders=sell.total_orders,
            total_paid_stars=sell.total_paid_stars,
            completed_payout_cents=sell.completed_payout_cents,
            completed_payout_usd=price_usd_for_cents(sell.completed_payout_cents),
            ready_for_payout_count=sell.ready_for_payout_count,
        ),
    )


# --------------------------------------------------------------------------- #
# Users
# --------------------------------------------------------------------------- #
@router.get("/users", summary="Search and paginate users")
async def admin_list_users(
    _admin: CurrentAdmin,
    user_service: UserServiceDep,
    page: Annotated[int, Query(ge=0)] = 0,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    search: Optional[str] = None,
    locale: Optional[str] = None,
    include_blocked: bool = True,
) -> AdminUsersPageResponse:
    users, has_next, total_pages = await user_service.list_admin_page(
        page=page,
        page_size=page_size,
        search=search,
        locale=locale,
        include_blocked=include_blocked,
    )
    return AdminUsersPageResponse(
        items=[build_admin_user_response(user) for user in users],
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=has_next,
    )


@router.get("/users/{user_id}", summary="A single user with lifetime purchase stats")
async def admin_get_user(
    user_id: int,
    _admin: CurrentAdmin,
    user_service: UserServiceDep,
    stars_order_service: StarsOrderServiceDep,
) -> AdminUserDetailResponse:
    user = await user_service.get(user_id=user_id)
    if user is None:
        not_found("User was not found.")
    stats = await stars_order_service.profile_stats(user_id=user_id)
    return AdminUserDetailResponse(
        user=build_admin_user_response(user),
        stats=ProfileStatsResponse(
            total_stars_purchased=stats.total_stars_purchased,
            total_premiums_purchased=stats.total_premiums_purchased,
            total_stars_amount_cents=stats.total_stars_amount_cents,
            total_stars_amount_usd=price_usd_for_cents(stats.total_stars_amount_cents),
            total_premiums_amount_cents=stats.total_premiums_amount_cents,
            total_premiums_amount_usd=price_usd_for_cents(stats.total_premiums_amount_cents),
        ),
    )


@router.post("/users/{user_id}/balance", summary="Adjust a user's main balance")
async def admin_adjust_balance(
    user_id: int,
    payload: AdminBalanceRequest,
    _admin: CurrentAdmin,
    user_service: UserServiceDep,
) -> AdminUserResponse:
    if await user_service.get(user_id=user_id) is None:
        not_found("User was not found.")
    if payload.operation == AdminBalanceOperation.SET:
        user = await user_service.set_balance(user_id=user_id, balance_cents=payload.amount_cents)
    elif payload.operation == AdminBalanceOperation.ADD:
        user = await user_service.add_balance(user_id=user_id, amount_cents=payload.amount_cents)
    else:
        user = await user_service.subtract_balance_clamped(
            user_id=user_id,
            amount_cents=payload.amount_cents,
        )
    if user is None:
        not_found("User was not found.")
    return build_admin_user_response(user)


@router.post("/users/{user_id}/block", summary="Block or unblock a user")
async def admin_block_user(
    user_id: int,
    payload: AdminBlockRequest,
    _admin: CurrentAdmin,
    user_service: UserServiceDep,
) -> AdminUserResponse:
    if await user_service.get(user_id=user_id) is None:
        not_found("User was not found.")
    user = await user_service.set_blocked_at(
        user_id=user_id,
        blocked_at=datetime_now() if payload.blocked else None,
    )
    if user is None:
        not_found("User was not found.")
    return build_admin_user_response(user)


# --------------------------------------------------------------------------- #
# Orders (stars / premium / gift / topup)
# --------------------------------------------------------------------------- #
@router.get("/orders", summary="Search and paginate every order and top-up")
async def admin_list_orders(
    _admin: CurrentAdmin,
    stars_order_service: StarsOrderServiceDep,
    page: Annotated[int, Query(ge=0)] = 0,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    user_id: Optional[int] = None,
    status: Optional[StarsOrderStatus] = None,
    provider: Optional[StarsPaymentProvider] = None,
    product_type: Optional[StarsOrderProductType] = None,
    search: Optional[str] = None,
) -> AdminOrdersPageResponse:
    orders, has_next, total_pages = await stars_order_service.list_admin_page(
        page=page,
        page_size=page_size,
        user_id=user_id,
        status=status,
        provider=provider,
        product_type=product_type,
        search=search,
    )
    return AdminOrdersPageResponse(
        items=[
            build_order_response(stars_order_service=stars_order_service, order=order)
            for order in orders
        ],
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=has_next,
    )


@router.get("/orders/{order_id}", summary="Fetch any order by id")
async def admin_get_order(
    order_id: int,
    _admin: CurrentAdmin,
    stars_order_service: StarsOrderServiceDep,
) -> OrderResponse:
    order = await stars_order_service.get(order_id=order_id)
    if order is None:
        not_found("Order was not found.")
    return build_order_response(stars_order_service=stars_order_service, order=order)


@router.post("/orders/{order_id}/verify", summary="Re-check an order's payment with the provider")
async def admin_verify_order(
    order_id: int,
    _admin: CurrentAdmin,
    stars_order_service: StarsOrderServiceDep,
) -> PaymentCheckResponse:
    if await stars_order_service.get(order_id=order_id) is None:
        not_found("Order was not found.")
    result = await stars_order_service.verify_order(order_id=order_id)
    return build_payment_check_response(stars_order_service=stars_order_service, result=result)


# --------------------------------------------------------------------------- #
# Sell orders
# --------------------------------------------------------------------------- #
@router.get("/sell-orders", summary="Search and paginate sell-Stars orders")
async def admin_list_sell_orders(
    _admin: CurrentAdmin,
    stars_sell_order_service: StarsSellOrderServiceDep,
    page: Annotated[int, Query(ge=0)] = 0,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    user_id: Optional[int] = None,
    status: Optional[StarsSellOrderStatus] = None,
    search: Optional[str] = None,
) -> AdminSellOrdersPageResponse:
    orders, has_next, total_pages = await stars_sell_order_service.list_admin_page(
        page=page,
        page_size=page_size,
        user_id=user_id,
        status=status,
        search=search,
    )
    return AdminSellOrdersPageResponse(
        items=[build_sell_order_response(order=order) for order in orders],
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=has_next,
    )


@router.get("/sell-orders/{order_id}", summary="Fetch a sell order by id")
async def admin_get_sell_order(
    order_id: int,
    _admin: CurrentAdmin,
    stars_sell_order_service: StarsSellOrderServiceDep,
) -> SellOrderResponse:
    order = await stars_sell_order_service.get(order_id=order_id)
    if order is None:
        not_found("Sell order was not found.")
    return build_sell_order_response(order=order)


@router.post("/sell-orders/{order_id}/complete", summary="Mark a sell order paid out")
async def admin_complete_sell_order(
    order_id: int,
    payload: AdminSellCompleteRequest,
    _admin: CurrentAdmin,
    stars_sell_order_service: StarsSellOrderServiceDep,
) -> SellOrderResponse:
    try:
        order = await stars_sell_order_service.mark_completed(
            order_id=order_id,
            allow_before_hold=payload.allow_before_hold,
            note=payload.note,
        )
    except OrderNotFoundError:
        not_found("Sell order was not found.")
    except NotReadyForPayoutError as error:
        conflict(str(error), code=ErrorCode.VALIDATION_ERROR)
    except StatusConflictError as error:
        conflict(str(error), code=ErrorCode.VALIDATION_ERROR)
    return build_sell_order_response(order=order)


@router.post("/sell-orders/{order_id}/reject", summary="Reject a sell order")
async def admin_reject_sell_order(
    order_id: int,
    payload: AdminSellRejectRequest,
    _admin: CurrentAdmin,
    stars_sell_order_service: StarsSellOrderServiceDep,
) -> SellOrderResponse:
    try:
        reason = StarsSellOrderResolutionReason(payload.reason)
    except ValueError:
        validation_error("Unsupported rejection reason.")
    try:
        order = await stars_sell_order_service.mark_rejected(
            order_id=order_id,
            reason=reason,
            note=payload.note,
        )
    except OrderNotFoundError:
        not_found("Sell order was not found.")
    except StatusConflictError as error:
        conflict(str(error), code=ErrorCode.VALIDATION_ERROR)
    return build_sell_order_response(order=order)


@router.post("/sell-orders/{order_id}/refund", summary="Mark a sell order refunded")
async def admin_refund_sell_order(
    order_id: int,
    payload: AdminSellResolveRequest,
    _admin: CurrentAdmin,
    stars_sell_order_service: StarsSellOrderServiceDep,
) -> SellOrderResponse:
    try:
        order = await stars_sell_order_service.mark_refunded(
            order_id=order_id,
            note=payload.note,
        )
    except OrderNotFoundError:
        not_found("Sell order was not found.")
    except StatusConflictError as error:
        conflict(str(error), code=ErrorCode.VALIDATION_ERROR)
    return build_sell_order_response(order=order)


# --------------------------------------------------------------------------- #
# Checks
# --------------------------------------------------------------------------- #
@router.get("/checks", summary="Search and paginate every check")
async def admin_list_checks(
    request: Request,
    _admin: CurrentAdmin,
    check_service: CheckServiceDep,
    page: Annotated[int, Query(ge=0)] = 0,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    creator_id: Optional[int] = None,
    status: Optional[CheckStatus] = None,
) -> AdminChecksPageResponse:
    checks, has_next, total_pages = await check_service.list_admin_page(
        page=page,
        page_size=page_size,
        creator_id=creator_id,
        status=status,
    )
    bot_username = await resolve_bot_username(request)
    return AdminChecksPageResponse(
        items=[build_check_response(check=check, bot_username=bot_username) for check in checks],
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=has_next,
    )


@router.get("/checks/{check_id}", summary="Fetch any check by id")
async def admin_get_check(
    request: Request,
    check_id: int,
    _admin: CurrentAdmin,
    check_service: CheckServiceDep,
) -> CheckResponse:
    check = await check_service.get(check_id=check_id)
    if check is None:
        not_found("Check was not found.")
    bot_username = await resolve_bot_username(request)
    return build_check_response(check=check, bot_username=bot_username)


@router.post("/checks/{check_id}/close", summary="Force-close a check and refund its creator")
async def admin_close_check(
    request: Request,
    check_id: int,
    _admin: CurrentAdmin,
    check_service: CheckServiceDep,
) -> CheckResponse:
    check = await check_service.get(check_id=check_id)
    if check is None:
        not_found("Check was not found.")
    result = await check_service.close_check(creator_id=check.creator_id, check_id=check_id)
    if result.check is None:
        not_found("Check was not found.")
    bot_username = await resolve_bot_username(request)
    return build_check_response(check=result.check, bot_username=bot_username)


# --------------------------------------------------------------------------- #
# Promo codes
# --------------------------------------------------------------------------- #
@router.get("/promo", summary="List promo codes")
async def admin_list_promo(
    _admin: CurrentAdmin,
    promo_code_service: PromoCodeServiceDep,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
) -> AdminPromosResponse:
    codes = await promo_code_service.list_codes(limit=limit)
    return AdminPromosResponse(items=[build_promo_response(info) for info in codes])


@router.post("/promo", summary="Create a promo code")
async def admin_create_promo(
    payload: AdminPromoCreateRequest,
    _admin: CurrentAdmin,
    promo_code_service: PromoCodeServiceDep,
) -> AdminPromoResponse:
    amount_cents = parse_usd_amount_to_cents(payload.amount_usd)
    code = (payload.code or "").strip()
    try:
        if code:
            info = await promo_code_service.create_code(
                code=code,
                amount_cents=amount_cents,
                max_activations=payload.max_activations,
            )
        else:
            created = await promo_code_service.create_unique_one_time_codes(
                amount_cents=amount_cents,
                count=1,
            )
            info = created[0]
    except PromoCodeService.CodeAlreadyExistsError as error:
        conflict(str(error), code=ErrorCode.VALIDATION_ERROR)
    except PromoCodeService.InvalidCodeError as error:
        validation_error(str(error))
    return build_promo_response(info)


@router.delete("/promo/{code}", summary="Delete a promo code")
async def admin_delete_promo(
    code: str,
    _admin: CurrentAdmin,
    promo_code_service: PromoCodeServiceDep,
) -> OkResponse:
    try:
        deleted = await promo_code_service.delete_code(code)
    except PromoCodeService.InvalidCodeError as error:
        validation_error(str(error))
    if not deleted:
        not_found("Promo code was not found.")
    return OkResponse(ok=True)
