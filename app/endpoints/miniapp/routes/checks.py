from __future__ import annotations

from typing import Annotated, Optional

from fastapi import APIRouter, Query, Request

from app.enums.check import CheckStatus
from app.models.dto.check import CheckDto
from app.models.dto.miniapp import (
    CheckResponse,
    ChecksPageResponse,
    CreateCheckRequest,
    UpdateCheckRequest,
)
from app.services.crud.check import (
    CheckCloseOutcome,
    InsufficientBalanceError,
)
from app.services.crud.check import (
    ValidationError as CheckValidationError,
)

from ..deps import CheckServiceDep, CurrentUser, resolve_bot_username
from ..errors import ErrorCode, conflict, not_found, validation_error
from ..serializers import build_check_response

router = APIRouter(prefix="/checks", tags=["checks"])


@router.post("", summary="Create a Stars gift-check funded from the balance")
async def create_check(
    request: Request,
    payload: CreateCheckRequest,
    auth: CurrentUser,
    check_service: CheckServiceDep,
) -> CheckResponse:
    try:
        check = await check_service.create_stars_check(
            creator_id=auth.user.id,
            stars_count=payload.stars_count,
            claim_username=payload.claim_username,
            claim_password=payload.claim_password,
        )
    except CheckValidationError as error:
        validation_error(str(error))
    except InsufficientBalanceError as error:
        conflict(str(error), code=ErrorCode.INSUFFICIENT_BALANCE)
    bot_username = await resolve_bot_username(request)
    return build_check_response(check=check, bot_username=bot_username)


@router.get("", summary="Paginated history of the user's checks")
async def list_checks(
    request: Request,
    auth: CurrentUser,
    check_service: CheckServiceDep,
    page: Annotated[int, Query(ge=0)] = 0,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    active_only: bool = False,
) -> ChecksPageResponse:
    if active_only:
        checks, has_next, total_pages = await check_service.list_active_page(
            creator_id=auth.user.id,
            page=page,
            page_size=page_size,
        )
    else:
        checks, has_next, total_pages = await check_service.list_recent_page(
            creator_id=auth.user.id,
            page=page,
            page_size=page_size,
        )
    bot_username = await resolve_bot_username(request)
    return ChecksPageResponse(
        items=[build_check_response(check=check, bot_username=bot_username) for check in checks],
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=has_next,
    )


@router.get("/{check_id}", summary="Fetch a single check by id")
async def get_check(
    request: Request,
    check_id: int,
    auth: CurrentUser,
    check_service: CheckServiceDep,
) -> CheckResponse:
    check = await check_service.get_creator_check(creator_id=auth.user.id, check_id=check_id)
    if check is None:
        not_found("Check was not found.")
    bot_username = await resolve_bot_username(request)
    return build_check_response(check=check, bot_username=bot_username)


@router.patch("/{check_id}", summary="Edit an active check's claim restrictions")
async def update_check(
    request: Request,
    check_id: int,
    payload: UpdateCheckRequest,
    auth: CurrentUser,
    check_service: CheckServiceDep,
) -> CheckResponse:
    current: Optional[CheckDto] = await check_service.get_creator_check(
        creator_id=auth.user.id,
        check_id=check_id,
    )
    if current is None:
        not_found("Check was not found.")
    if current.status != CheckStatus.ACTIVE:
        conflict("Only active checks can be edited.", code=ErrorCode.VALIDATION_ERROR)

    updated: Optional[CheckDto] = current
    try:
        if payload.update_username:
            updated = await check_service.update_claim_username(
                creator_id=auth.user.id,
                check_id=check_id,
                claim_username=payload.claim_username,
            )
        if payload.update_password and updated is not None:
            updated = await check_service.update_claim_password(
                creator_id=auth.user.id,
                check_id=check_id,
                claim_password=payload.claim_password,
            )
    except CheckValidationError as error:
        validation_error(str(error))
    if updated is None:
        conflict("Check could not be edited.", code=ErrorCode.VALIDATION_ERROR)
    bot_username = await resolve_bot_username(request)
    return build_check_response(check=updated, bot_username=bot_username)


@router.post("/{check_id}/close", summary="Close an active check and refund the balance")
async def close_check(
    request: Request,
    check_id: int,
    auth: CurrentUser,
    check_service: CheckServiceDep,
) -> CheckResponse:
    result = await check_service.close_check(creator_id=auth.user.id, check_id=check_id)
    if result.outcome == CheckCloseOutcome.NOT_FOUND or result.check is None:
        not_found("Check was not found.")
    if result.outcome != CheckCloseOutcome.CLOSED:
        conflict(
            f"Check cannot be closed ({result.outcome.value}).",
            code=ErrorCode.VALIDATION_ERROR,
        )
    bot_username = await resolve_bot_username(request)
    return build_check_response(check=result.check, bot_username=bot_username)
