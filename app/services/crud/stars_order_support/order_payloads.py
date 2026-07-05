from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.enums.stars_order import StarsOrderProductType
from app.gifts import get_gift_pack_by_id
from app.stars import build_stars_pack, get_premium_pack, normalize_recipient_username


@dataclass(frozen=True, slots=True)
class BalanceOrderPayload:
    recipient_username: str
    recipient_user_id: int | None
    gift_id: str | None
    gift_message: str | None
    gift_sender_private: bool | None


@dataclass(frozen=True, slots=True)
class ExternalOrderPayload:
    recipient_username: str
    stars_count: int
    amount_cents: int
    premium_months: int | None
    recipient_user_id: int | None
    gift_id: str | None
    gift_message: str | None
    gift_sender_private: bool | None
    description: str


async def prepare_balance_order_payload(
    *,
    service: Any,
    recipient_username: str,
    product_type: StarsOrderProductType,
    recipient_user_id: int | None,
    gift_id: str | None,
    gift_message: str | None,
    gift_sender_private: bool | None,
    validation_error_cls: type[Exception],
) -> BalanceOrderPayload:
    if product_type in {
        StarsOrderProductType.STARS,
        StarsOrderProductType.PREMIUM,
    }:
        normalized_username = _normalized_username_or_raise(
            recipient_username=recipient_username,
            error_text="Invalid recipient username.",
            validation_error_cls=validation_error_cls,
        )
        return BalanceOrderPayload(
            recipient_username=normalized_username,
            recipient_user_id=recipient_user_id,
            gift_id=None,
            gift_message=None,
            gift_sender_private=None,
        )

    if product_type == StarsOrderProductType.TOPUP:
        return BalanceOrderPayload(
            recipient_username="balance",
            recipient_user_id=None,
            gift_id=None,
            gift_message=None,
            gift_sender_private=None,
        )

    if product_type != StarsOrderProductType.GIFT:
        raise validation_error_cls("Unsupported order product type.")

    normalized_username = _normalized_username_or_raise(
        recipient_username=recipient_username,
        error_text="Gift recipient username is invalid.",
        validation_error_cls=validation_error_cls,
    )
    normalized_gift_id = (gift_id or "").strip()
    if not normalized_gift_id:
        raise validation_error_cls("Gift ID is required.")
    if gift_sender_private is None:
        raise validation_error_cls("Gift sender visibility is required.")

    resolved_recipient_user_id = await service._resolve_gift_recipient_user_id(
        recipient_username=normalized_username,
        recipient_user_id=recipient_user_id,
    )
    if resolved_recipient_user_id is None or resolved_recipient_user_id <= 0:
        raise validation_error_cls("Gift recipient username is invalid.")

    normalized_gift_message = service._normalize_gift_message(gift_message)
    return BalanceOrderPayload(
        recipient_username=normalized_username,
        recipient_user_id=resolved_recipient_user_id,
        gift_id=normalized_gift_id,
        gift_message=normalized_gift_message,
        gift_sender_private=gift_sender_private,
    )


async def prepare_external_order_payload(
    *,
    service: Any,
    user_id: int,
    recipient_username: str,
    stars_count: int,
    product_type: StarsOrderProductType,
    premium_months: int | None,
    forced_amount_cents: int | None,
    recipient_user_id: int | None,
    gift_id: str | None,
    gift_message: str | None,
    gift_sender_private: bool | None,
    validation_error_cls: type[Exception],
) -> ExternalOrderPayload:
    if product_type == StarsOrderProductType.STARS:
        return _prepare_external_stars_payload(
            recipient_username=recipient_username,
            stars_count=stars_count,
            premium_months=premium_months,
            validation_error_cls=validation_error_cls,
        )

    if product_type == StarsOrderProductType.PREMIUM:
        return _prepare_external_premium_payload(
            recipient_username=recipient_username,
            premium_months=premium_months,
            forced_amount_cents=forced_amount_cents,
            validation_error_cls=validation_error_cls,
        )

    if product_type == StarsOrderProductType.GIFT:
        return await _prepare_external_gift_payload(
            service=service,
            recipient_username=recipient_username,
            forced_amount_cents=forced_amount_cents,
            recipient_user_id=recipient_user_id,
            gift_id=gift_id,
            gift_message=gift_message,
            gift_sender_private=gift_sender_private,
            validation_error_cls=validation_error_cls,
        )

    if product_type == StarsOrderProductType.TOPUP:
        return _prepare_external_topup_payload(
            user_id=user_id,
            forced_amount_cents=forced_amount_cents,
            validation_error_cls=validation_error_cls,
        )

    raise validation_error_cls("Unsupported order product type.")


def _normalized_username_or_raise(
    *,
    recipient_username: str,
    error_text: str,
    validation_error_cls: type[Exception],
) -> str:
    normalized_username = normalize_recipient_username(recipient_username)
    if normalized_username is None:
        raise validation_error_cls(error_text)
    return normalized_username


def _prepare_external_stars_payload(
    *,
    recipient_username: str,
    stars_count: int,
    premium_months: int | None,
    validation_error_cls: type[Exception],
) -> ExternalOrderPayload:
    normalized_username = _normalized_username_or_raise(
        recipient_username=recipient_username,
        error_text="Invalid recipient username.",
        validation_error_cls=validation_error_cls,
    )
    try:
        pack = build_stars_pack(stars_count=stars_count)
    except ValueError as error:
        raise validation_error_cls("Invalid stars count.") from error
    return ExternalOrderPayload(
        recipient_username=normalized_username,
        stars_count=pack.stars_count,
        amount_cents=pack.price_cents,
        premium_months=premium_months,
        recipient_user_id=None,
        gift_id=None,
        gift_message=None,
        gift_sender_private=None,
        description=f"Telegram Stars {pack.stars_count} for @{normalized_username}",
    )


def _prepare_external_premium_payload(
    *,
    recipient_username: str,
    premium_months: int | None,
    forced_amount_cents: int | None,
    validation_error_cls: type[Exception],
) -> ExternalOrderPayload:
    normalized_username = _normalized_username_or_raise(
        recipient_username=recipient_username,
        error_text="Invalid recipient username.",
        validation_error_cls=validation_error_cls,
    )
    if premium_months is None:
        raise validation_error_cls("Premium period is required.")
    premium_pack = get_premium_pack(months=premium_months)
    return ExternalOrderPayload(
        recipient_username=normalized_username,
        stars_count=0,
        amount_cents=(
            forced_amount_cents
            if forced_amount_cents is not None
            else premium_pack.price_cents
        ),
        premium_months=premium_pack.months,
        recipient_user_id=None,
        gift_id=None,
        gift_message=None,
        gift_sender_private=None,
        description=f"Telegram Premium {premium_pack.months} months for @{normalized_username}",
    )


async def _prepare_external_gift_payload(
    *,
    service: Any,
    recipient_username: str,
    forced_amount_cents: int | None,
    recipient_user_id: int | None,
    gift_id: str | None,
    gift_message: str | None,
    gift_sender_private: bool | None,
    validation_error_cls: type[Exception],
) -> ExternalOrderPayload:
    normalized_username = _normalized_username_or_raise(
        recipient_username=recipient_username,
        error_text="Gift recipient username is invalid.",
        validation_error_cls=validation_error_cls,
    )
    if gift_sender_private is None:
        raise validation_error_cls("Gift sender visibility is required.")
    normalized_gift_id = (gift_id or "").strip()
    if not normalized_gift_id:
        raise validation_error_cls("Gift ID is required.")
    if forced_amount_cents is None or forced_amount_cents <= 0:
        raise validation_error_cls("Gift amount is invalid.")
    gift_pack = get_gift_pack_by_id(gift_id=normalized_gift_id)
    if gift_pack is None:
        raise validation_error_cls("Unsupported gift ID.")

    resolved_recipient_user_id = await service._resolve_gift_recipient_user_id(
        recipient_username=normalized_username,
        recipient_user_id=recipient_user_id,
    )
    if resolved_recipient_user_id is None or resolved_recipient_user_id <= 0:
        raise validation_error_cls("Gift recipient username is invalid.")

    return ExternalOrderPayload(
        recipient_username=normalized_username,
        stars_count=0,
        amount_cents=forced_amount_cents,
        premium_months=None,
        recipient_user_id=resolved_recipient_user_id,
        gift_id=normalized_gift_id,
        gift_message=service._normalize_gift_message(gift_message),
        gift_sender_private=gift_sender_private,
        description=(
            f"Telegram Gift {gift_pack.label} "
            f"(gift_id={gift_pack.gift_id}) to @{normalized_username}"
        ),
    )


def _prepare_external_topup_payload(
    *,
    user_id: int,
    forced_amount_cents: int | None,
    validation_error_cls: type[Exception],
) -> ExternalOrderPayload:
    if forced_amount_cents is None or forced_amount_cents < 100:
        raise validation_error_cls("Top-up amount is invalid.")
    return ExternalOrderPayload(
        recipient_username="balance",
        stars_count=0,
        amount_cents=forced_amount_cents,
        premium_months=None,
        recipient_user_id=None,
        gift_id=None,
        gift_message=None,
        gift_sender_private=None,
        description=f"Balance top-up for user #{user_id}",
    )
