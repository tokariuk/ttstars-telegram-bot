from __future__ import annotations

import contextlib
from dataclasses import replace
from typing import Any

from aiogram.types import Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import MessageInput

from app.services.promo_codes import PromoCodeService
from app.stars import price_usd_for_cents

from ..helpers import (
    extract_broadcast_payload,
    parse_broadcast_options_input,
    parse_link_buttons,
    parse_order_id_input,
    parse_promo_create_input,
    parse_promo_limit_input,
    parse_promo_limit_value,
    parse_promo_quick_input,
    parse_promo_quick_single_input,
    parse_user_balance_input,
    parse_user_lookup_input,
    payload_with_buttons,
)
from ..states import AdminSG
from .shared import (
    i18n,
    load_broadcast_payload,
    promo_selected_code,
    promo_service,
    save_broadcast_payload,
    set_notice,
    set_promo_selected_code,
    stars_order_service,
    user_service,
)

_SKIP_WORDS = {"-", "skip", "пропустить", "пропустити"}


async def handle_broadcast_content_input(
    message: Message,
    _: MessageInput,
    dialog_manager: DialogManager,
) -> None:
    i18n_ctx = i18n(dialog_manager)
    payload = extract_broadcast_payload(message)
    if payload is None:
        set_notice(dialog_manager, str(i18n_ctx.messages.admin_broadcast_content_invalid()))
        await dialog_manager.switch_to(AdminSG.broadcast_content, show_mode=ShowMode.EDIT)
    else:
        save_broadcast_payload(dialog_manager=dialog_manager, payload=payload)
        await dialog_manager.switch_to(AdminSG.broadcast_options, show_mode=ShowMode.EDIT)
    with contextlib.suppress(Exception):
        await message.delete()


async def handle_broadcast_options_input(
    message: Message,
    _: MessageInput,
    dialog_manager: DialogManager,
) -> None:
    i18n_ctx = i18n(dialog_manager)
    payload = load_broadcast_payload(dialog_manager)
    if payload is None:
        set_notice(dialog_manager, str(i18n_ctx.messages.admin_broadcast_content_invalid()))
        await dialog_manager.switch_to(AdminSG.broadcast_content, show_mode=ShowMode.EDIT)
        with contextlib.suppress(Exception):
            await message.delete()
        return

    available_locales = list(user_service(dialog_manager).config.telegram.locales)
    try:
        target_languages, include_close_button = parse_broadcast_options_input(
            value=(message.text or "").strip(),
            available_locales=available_locales,
        )
    except ValueError as error:
        set_notice(
            dialog_manager,
            str(i18n_ctx.messages.admin_broadcast_options_invalid(error=str(error))),
        )
        await dialog_manager.switch_to(AdminSG.broadcast_options, show_mode=ShowMode.EDIT)
        with contextlib.suppress(Exception):
            await message.delete()
        return

    payload = replace(
        payload,
        target_languages=target_languages,
        include_close_button=include_close_button,
    )
    save_broadcast_payload(dialog_manager=dialog_manager, payload=payload)
    await dialog_manager.switch_to(AdminSG.broadcast_buttons, show_mode=ShowMode.EDIT)
    with contextlib.suppress(Exception):
        await message.delete()


async def handle_broadcast_buttons_input(
    message: Message,
    _: MessageInput,
    dialog_manager: DialogManager,
) -> None:
    i18n_ctx = i18n(dialog_manager)
    payload = load_broadcast_payload(dialog_manager)
    if payload is None:
        set_notice(dialog_manager, str(i18n_ctx.messages.admin_broadcast_content_invalid()))
        await dialog_manager.switch_to(AdminSG.broadcast_content, show_mode=ShowMode.EDIT)
        with contextlib.suppress(Exception):
            await message.delete()
        return

    raw = (message.text or "").strip()
    if raw.casefold() in _SKIP_WORDS:
        buttons = []
    else:
        try:
            buttons = parse_link_buttons(raw)
        except ValueError as error:
            set_notice(
                dialog_manager,
                str(i18n_ctx.messages.admin_broadcast_buttons_invalid(error=str(error))),
            )
            await dialog_manager.switch_to(AdminSG.broadcast_buttons, show_mode=ShowMode.EDIT)
            with contextlib.suppress(Exception):
                await message.delete()
            return

    payload = payload_with_buttons(payload, buttons=buttons)
    save_broadcast_payload(dialog_manager=dialog_manager, payload=payload)
    await dialog_manager.switch_to(AdminSG.broadcast_confirm, show_mode=ShowMode.EDIT)
    with contextlib.suppress(Exception):
        await message.delete()


async def handle_promo_create_input(
    message: Message,
    _: MessageInput,
    dialog_manager: DialogManager,
) -> None:
    i18n_ctx = i18n(dialog_manager)
    parsed = parse_promo_create_input((message.text or "").strip())
    if parsed is None:
        set_notice(dialog_manager, str(i18n_ctx.messages.admin_promo_create_invalid()))
        await dialog_manager.switch_to(AdminSG.promo_create, show_mode=ShowMode.EDIT)
        with contextlib.suppress(Exception):
            await message.delete()
        return

    code, amount_cents, max_activations = parsed
    service = promo_service(dialog_manager)
    try:
        created = await service.create_code(
            code=code,
            amount_cents=amount_cents,
            max_activations=max_activations,
        )
    except (PromoCodeService.InvalidCodeError, PromoCodeService.CodeAlreadyExistsError) as error:
        set_notice(
            dialog_manager,
            str(i18n_ctx.messages.admin_promo_create_failed(error=str(error))),
        )
        await dialog_manager.switch_to(AdminSG.promo_create, show_mode=ShowMode.EDIT)
    else:
        max_activations_text = (
            str(created.max_activations)
            if created.max_activations is not None
            else str(i18n_ctx.messages.admin_limit_unlimited())
        )
        set_notice(
            dialog_manager,
            str(
                i18n_ctx.messages.admin_promo_created(
                    code=created.code,
                    amount=price_usd_for_cents(created.amount_cents),
                    max_activations=max_activations_text,
                )
            ),
        )
        await dialog_manager.switch_to(AdminSG.promo_menu, show_mode=ShowMode.EDIT)
    with contextlib.suppress(Exception):
        await message.delete()


async def handle_promo_quick_input(
    message: Message,
    _: MessageInput,
    dialog_manager: DialogManager,
) -> None:
    i18n_ctx = i18n(dialog_manager)
    parsed = parse_promo_quick_single_input((message.text or "").strip())
    if parsed is None:
        set_notice(dialog_manager, str(i18n_ctx.messages.admin_promo_quick_invalid()))
        await dialog_manager.switch_to(AdminSG.promo_quick, show_mode=ShowMode.EDIT)
        with contextlib.suppress(Exception):
            await message.delete()
        return

    amount_cents, prefix = parsed
    service = promo_service(dialog_manager)
    try:
        created_codes = await service.create_unique_one_time_codes(
            amount_cents=amount_cents,
            count=1,
            prefix=prefix,
        )
    except PromoCodeService.Error as error:
        set_notice(
            dialog_manager,
            str(i18n_ctx.messages.admin_promo_quick_failed(error=str(error))),
        )
        await dialog_manager.switch_to(AdminSG.promo_quick, show_mode=ShowMode.EDIT)
    else:
        created = created_codes[0]
        set_notice(
            dialog_manager,
            str(
                i18n_ctx.messages.admin_promo_quick_done(
                    code=created.code,
                    amount=price_usd_for_cents(amount_cents),
                )
            ),
        )
        await dialog_manager.switch_to(AdminSG.promo_menu, show_mode=ShowMode.EDIT)
    with contextlib.suppress(Exception):
        await message.delete()


async def handle_promo_bulk_input(
    message: Message,
    _: MessageInput,
    dialog_manager: DialogManager,
) -> None:
    i18n_ctx = i18n(dialog_manager)
    parsed = parse_promo_quick_input((message.text or "").strip())
    if parsed is None:
        set_notice(dialog_manager, str(i18n_ctx.messages.admin_promo_bulk_invalid()))
        await dialog_manager.switch_to(AdminSG.promo_bulk, show_mode=ShowMode.EDIT)
        with contextlib.suppress(Exception):
            await message.delete()
        return

    amount_cents, count, prefix = parsed
    service = promo_service(dialog_manager)
    try:
        created_codes = await service.create_unique_one_time_codes(
            amount_cents=amount_cents,
            count=count,
            prefix=prefix,
        )
    except PromoCodeService.Error as error:
        set_notice(
            dialog_manager,
            str(i18n_ctx.messages.admin_promo_bulk_failed(error=str(error))),
        )
        await dialog_manager.switch_to(AdminSG.promo_bulk, show_mode=ShowMode.EDIT)
    else:
        codes_preview = "\n".join(code.code for code in created_codes[:40])
        set_notice(
            dialog_manager,
            str(
                i18n_ctx.messages.admin_promo_bulk_done(
                    count=len(created_codes),
                    amount=price_usd_for_cents(amount_cents),
                    codes=codes_preview,
                )
            ),
        )
        await dialog_manager.switch_to(AdminSG.promo_menu, show_mode=ShowMode.EDIT)
    with contextlib.suppress(Exception):
        await message.delete()


async def handle_promo_set_limit_input(
    message: Message,
    _: MessageInput,
    dialog_manager: DialogManager,
) -> None:
    i18n_ctx = i18n(dialog_manager)
    raw_value = (message.text or "").strip()
    selected_code = promo_selected_code(dialog_manager)
    limit_only = parse_promo_limit_value(raw_value)
    parsed = (
        (selected_code, (None if limit_only == 0 else limit_only))
        if selected_code is not None and limit_only is not None
        else parse_promo_limit_input(raw_value)
    )
    if parsed is None:
        set_notice(dialog_manager, str(i18n_ctx.messages.admin_promo_set_limit_invalid()))
        await dialog_manager.switch_to(AdminSG.promo_set_limit, show_mode=ShowMode.EDIT)
        with contextlib.suppress(Exception):
            await message.delete()
        return

    code, max_activations = parsed
    service = promo_service(dialog_manager)
    try:
        updated = await service.set_max_activations(
            code=code,
            max_activations=max_activations,
        )
    except PromoCodeService.CodeNotFoundError:
        set_notice(dialog_manager, str(i18n_ctx.messages.admin_promo_not_found()))
        await dialog_manager.switch_to(AdminSG.promo_menu, show_mode=ShowMode.EDIT)
    except PromoCodeService.Error as error:
        set_notice(
            dialog_manager,
            str(i18n_ctx.messages.admin_promo_set_limit_failed(error=str(error))),
        )
        await dialog_manager.switch_to(AdminSG.promo_set_limit, show_mode=ShowMode.EDIT)
    else:
        max_activations_text = (
            str(updated.max_activations)
            if updated.max_activations is not None
            else str(i18n_ctx.messages.admin_limit_unlimited())
        )
        set_notice(
            dialog_manager,
            str(
                i18n_ctx.messages.admin_promo_set_limit_done(
                    code=updated.code,
                    max_activations=max_activations_text,
                )
            ),
        )
        set_promo_selected_code(dialog_manager, updated.code)
        await dialog_manager.switch_to(AdminSG.promo_details, show_mode=ShowMode.EDIT)
    with contextlib.suppress(Exception):
        await message.delete()


async def handle_user_add_balance_input(
    message: Message,
    _: MessageInput,
    dialog_manager: DialogManager,
) -> None:
    i18n_ctx = i18n(dialog_manager)
    parsed = parse_user_balance_input((message.text or "").strip())
    if parsed is None:
        set_notice(dialog_manager, str(i18n_ctx.messages.admin_users_add_balance_invalid()))
        await dialog_manager.switch_to(AdminSG.user_add_balance, show_mode=ShowMode.EDIT)
        with contextlib.suppress(Exception):
            await message.delete()
        return

    user_id, delta_cents, clear_all = parsed
    service = user_service(dialog_manager)
    current = await service.get(user_id=user_id)
    if current is None:
        set_notice(
            dialog_manager,
            str(i18n_ctx.messages.admin_users_not_found(user_id=user_id)),
        )
        await dialog_manager.switch_to(AdminSG.user_add_balance, show_mode=ShowMode.EDIT)
    else:
        if clear_all:
            updated = await service.set_balance(user_id=user_id, balance_cents=0)
        elif delta_cents > 0:
            updated = await service.add_balance(user_id=user_id, amount_cents=delta_cents)
        else:
            updated = await service.subtract_balance_clamped(
                user_id=user_id,
                amount_cents=abs(delta_cents),
            )

        if updated is None:
            set_notice(
                dialog_manager,
                str(i18n_ctx.messages.admin_users_not_found(user_id=user_id)),
            )
            await dialog_manager.switch_to(AdminSG.user_add_balance, show_mode=ShowMode.EDIT)
            with contextlib.suppress(Exception):
                await message.delete()
            return

        set_notice(
            dialog_manager,
            (
                str(
                    i18n_ctx.messages.admin_users_clear_balance_done(
                        user_id=user_id,
                        balance=price_usd_for_cents(updated.balance_cents),
                    )
                )
                if clear_all
                else (
                    str(
                        i18n_ctx.messages.admin_users_add_balance_done(
                            user_id=user_id,
                            amount=price_usd_for_cents(delta_cents),
                            balance=price_usd_for_cents(updated.balance_cents),
                        )
                    )
                    if delta_cents > 0
                    else str(
                        i18n_ctx.messages.admin_users_subtract_balance_done(
                            user_id=user_id,
                            amount=price_usd_for_cents(
                                max(0, current.balance_cents - updated.balance_cents),
                            ),
                            balance=price_usd_for_cents(updated.balance_cents),
                        )
                    )
                )
            ),
        )
        await dialog_manager.switch_to(AdminSG.users_menu, show_mode=ShowMode.EDIT)
    with contextlib.suppress(Exception):
        await message.delete()


async def handle_user_lookup_input(
    message: Message,
    _: MessageInput,
    dialog_manager: DialogManager,
) -> None:
    i18n_ctx = i18n(dialog_manager)
    user_id = parse_user_lookup_input((message.text or "").strip())
    if user_id is None:
        set_notice(dialog_manager, str(i18n_ctx.messages.admin_users_lookup_invalid()))
        await dialog_manager.switch_to(AdminSG.user_lookup_contact, show_mode=ShowMode.EDIT)
        with contextlib.suppress(Exception):
            await message.delete()
        return

    found_user = await user_service(dialog_manager).get(user_id=user_id)
    if found_user is None:
        set_notice(
            dialog_manager,
            str(i18n_ctx.messages.admin_users_not_found(user_id=user_id)),
        )
        await dialog_manager.switch_to(AdminSG.user_lookup_contact, show_mode=ShowMode.EDIT)
        with contextlib.suppress(Exception):
            await message.delete()
        return

    language_code = found_user.language_code or "-"
    blocked_at = (
        found_user.blocked_at.strftime("%Y-%m-%d %H:%M:%S")
        if found_user.blocked_at is not None
        else "-"
    )
    set_notice(
        dialog_manager,
        str(
            i18n_ctx.messages.admin_users_lookup_done(
                user_id=found_user.id,
                mention=found_user.mention,
                user_url=found_user.url,
                language=found_user.language,
                language_code=language_code,
                balance=price_usd_for_cents(found_user.balance_cents),
                referral_balance=price_usd_for_cents(found_user.referral_balance_cents),
                referral_earned=price_usd_for_cents(found_user.referral_earned_cents),
                referrer_id=found_user.referrer_id if found_user.referrer_id is not None else "-",
                blocked=str(found_user.bot_blocked).lower(),
                blocked_at=blocked_at,
            )
        ),
    )
    await dialog_manager.switch_to(AdminSG.users_menu, show_mode=ShowMode.EDIT)
    with contextlib.suppress(Exception):
        await message.delete()


def _order_outcome_label(
    *,
    i18n_ctx: Any,
    outcome: object,
) -> str:
    outcome_value = str(getattr(outcome, "value", outcome))
    if outcome_value == "pending":
        return str(i18n_ctx.messages.admin_orders_outcome_pending())
    if outcome_value == "processing":
        return str(i18n_ctx.messages.admin_orders_outcome_processing())
    if outcome_value == "completed":
        return str(i18n_ctx.messages.admin_orders_outcome_completed())
    if outcome_value == "failed":
        return str(i18n_ctx.messages.admin_orders_outcome_failed())
    if outcome_value == "canceled":
        return str(i18n_ctx.messages.admin_orders_outcome_canceled())
    return str(i18n_ctx.messages.admin_orders_outcome_not_found())


async def handle_order_retry_input(
    message: Message,
    _: MessageInput,
    dialog_manager: DialogManager,
) -> None:
    i18n_ctx = i18n(dialog_manager)
    parsed_order_id = parse_order_id_input((message.text or "").strip())
    if parsed_order_id is None:
        set_notice(dialog_manager, str(i18n_ctx.messages.admin_orders_input_invalid()))
        await dialog_manager.switch_to(AdminSG.order_retry, show_mode=ShowMode.EDIT)
        with contextlib.suppress(Exception):
            await message.delete()
        return

    result = await stars_order_service(dialog_manager).retry_fulfill_order(
        order_id=parsed_order_id,
    )
    if result.order is None:
        set_notice(
            dialog_manager,
            str(i18n_ctx.messages.admin_orders_not_found(order_id=parsed_order_id)),
        )
        await dialog_manager.switch_to(AdminSG.orders_menu, show_mode=ShowMode.EDIT)
        with contextlib.suppress(Exception):
            await message.delete()
        return

    set_notice(
        dialog_manager,
        str(
            i18n_ctx.messages.admin_orders_action_done(
                action=i18n_ctx.messages.admin_orders_action_retry(),
                order_id=result.order.id,
                outcome=_order_outcome_label(i18n_ctx=i18n_ctx, outcome=result.outcome),
                status=result.order.status.value,
                provider_status=result.order.provider_status or "—",
                tx_hash=result.order.fragment_tx_hash or "—",
                error=result.order.fragment_error or "—",
            )
        ),
    )
    await dialog_manager.switch_to(AdminSG.orders_menu, show_mode=ShowMode.EDIT)
    with contextlib.suppress(Exception):
        await message.delete()


async def handle_order_force_input(
    message: Message,
    _: MessageInput,
    dialog_manager: DialogManager,
) -> None:
    i18n_ctx = i18n(dialog_manager)
    parsed_order_id = parse_order_id_input((message.text or "").strip())
    if parsed_order_id is None:
        set_notice(dialog_manager, str(i18n_ctx.messages.admin_orders_input_invalid()))
        await dialog_manager.switch_to(AdminSG.order_force, show_mode=ShowMode.EDIT)
        with contextlib.suppress(Exception):
            await message.delete()
        return

    result = await stars_order_service(dialog_manager).force_fulfill_order(
        order_id=parsed_order_id,
    )
    if result.order is None:
        set_notice(
            dialog_manager,
            str(i18n_ctx.messages.admin_orders_not_found(order_id=parsed_order_id)),
        )
        await dialog_manager.switch_to(AdminSG.orders_menu, show_mode=ShowMode.EDIT)
        with contextlib.suppress(Exception):
            await message.delete()
        return

    if result.provider_status == "force_debit_failed":
        set_notice(
            dialog_manager,
            str(
                i18n_ctx.messages.admin_orders_force_debit_failed(
                    order_id=result.order.id,
                    amount=price_usd_for_cents(result.order.amount_cents),
                )
            ),
        )
        await dialog_manager.switch_to(AdminSG.orders_menu, show_mode=ShowMode.EDIT)
        with contextlib.suppress(Exception):
            await message.delete()
        return

    set_notice(
        dialog_manager,
        str(
            i18n_ctx.messages.admin_orders_action_done(
                action=i18n_ctx.messages.admin_orders_action_force(),
                order_id=result.order.id,
                outcome=_order_outcome_label(i18n_ctx=i18n_ctx, outcome=result.outcome),
                status=result.order.status.value,
                provider_status=result.order.provider_status or "—",
                tx_hash=result.order.fragment_tx_hash or "—",
                error=result.order.fragment_error or "—",
            )
        ),
    )
    await dialog_manager.switch_to(AdminSG.orders_menu, show_mode=ShowMode.EDIT)
    with contextlib.suppress(Exception):
        await message.delete()
