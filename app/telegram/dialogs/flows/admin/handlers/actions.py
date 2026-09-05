from __future__ import annotations

from dataclasses import replace

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Button

from app.services.promo_codes import PromoCodeService

from ..helpers import (
    deliver_broadcast,
    payload_with_buttons,
)
from ..states import AdminSG
from .shared import (
    clear_broadcast_payload,
    clear_promo_bulk_selected_codes,
    i18n,
    load_broadcast_payload,
    promo_bulk_selected_codes,
    promo_selected_code,
    promo_service,
    save_broadcast_payload,
    set_notice,
    set_promo_selected_code,
    user_service,
)


async def broadcast_skip_buttons(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    payload = load_broadcast_payload(dialog_manager)
    i18n_ctx = i18n(dialog_manager)
    if payload is None:
        set_notice(dialog_manager, str(i18n_ctx.messages.admin_broadcast_content_invalid()))
        await dialog_manager.switch_to(AdminSG.broadcast_content, show_mode=ShowMode.EDIT)
        return

    payload = payload_with_buttons(payload, buttons=[])
    save_broadcast_payload(dialog_manager=dialog_manager, payload=payload)
    await dialog_manager.switch_to(AdminSG.broadcast_confirm, show_mode=ShowMode.EDIT)


async def broadcast_skip_options(
    _: CallbackQuery,
    __: Button,
    dialog_manager: DialogManager,
) -> None:
    payload = load_broadcast_payload(dialog_manager)
    i18n_ctx = i18n(dialog_manager)
    if payload is None:
        set_notice(dialog_manager, str(i18n_ctx.messages.admin_broadcast_content_invalid()))
        await dialog_manager.switch_to(AdminSG.broadcast_content, show_mode=ShowMode.EDIT)
        return

    payload = replace(
        payload,
        target_languages=None,
        include_close_button=False,
    )
    save_broadcast_payload(dialog_manager=dialog_manager, payload=payload)
    await dialog_manager.switch_to(AdminSG.broadcast_buttons, show_mode=ShowMode.EDIT)


async def broadcast_send(
    callback: CallbackQuery,
    _: Button,
    dialog_manager: DialogManager,
) -> None:
    payload = load_broadcast_payload(dialog_manager)
    i18n_ctx = i18n(dialog_manager)
    if payload is None:
        set_notice(dialog_manager, str(i18n_ctx.messages.admin_broadcast_content_invalid()))
        await dialog_manager.switch_to(AdminSG.broadcast_content, show_mode=ShowMode.EDIT)
        return

    await callback.answer()
    set_notice(dialog_manager, str(i18n_ctx.messages.admin_broadcast_started()))
    await dialog_manager.switch_to(AdminSG.broadcast_confirm, show_mode=ShowMode.EDIT)

    bot = callback.bot
    if bot is None:
        set_notice(dialog_manager, str(i18n_ctx.messages.admin_broadcast_preview_failed()))
        await dialog_manager.switch_to(AdminSG.broadcast_confirm, show_mode=ShowMode.EDIT)
        return

    result = await deliver_broadcast(
        bot=bot,
        i18n=i18n_ctx,
        user_service=user_service(dialog_manager),
        payload=payload,
        target_languages=payload.target_languages,
        include_close_button=payload.include_close_button,
    )
    set_notice(
        dialog_manager,
        str(
            i18n_ctx.messages.admin_broadcast_done(
                total=result.total,
                sent=result.sent,
                failed=result.failed,
                blocked=result.blocked,
            )
        ),
    )
    clear_broadcast_payload(dialog_manager)
    await dialog_manager.switch_to(AdminSG.menu, show_mode=ShowMode.EDIT)


async def promo_delete_selected(
    callback: CallbackQuery,
    _: Button,
    dialog_manager: DialogManager,
) -> None:
    i18n_ctx = i18n(dialog_manager)
    selected = promo_selected_code(dialog_manager)
    if selected is None:
        set_notice(dialog_manager, str(i18n_ctx.messages.admin_promo_not_found()))
        await dialog_manager.switch_to(AdminSG.promo_menu, show_mode=ShowMode.EDIT)
        await callback.answer()
        return

    removed = await promo_service(dialog_manager).delete_code(selected)
    if not removed:
        set_notice(dialog_manager, str(i18n_ctx.messages.admin_promo_not_found()))
    else:
        set_notice(
            dialog_manager,
            str(i18n_ctx.messages.admin_promo_deleted(code=selected)),
        )
    set_promo_selected_code(dialog_manager, None)
    await dialog_manager.switch_to(AdminSG.promo_menu, show_mode=ShowMode.EDIT)
    await callback.answer()


async def promo_set_selected_one_time(
    callback: CallbackQuery,
    _: Button,
    dialog_manager: DialogManager,
) -> None:
    await _promo_set_selected_limit(
        callback=callback,
        dialog_manager=dialog_manager,
        max_activations=1,
    )


async def promo_toggle_selected(
    callback: CallbackQuery,
    _: Button,
    dialog_manager: DialogManager,
) -> None:
    selected = promo_selected_code(dialog_manager)
    i18n_ctx = i18n(dialog_manager)
    if selected is None:
        set_notice(dialog_manager, str(i18n_ctx.messages.admin_promo_not_found()))
        await dialog_manager.switch_to(AdminSG.promo_menu, show_mode=ShowMode.EDIT)
        await callback.answer()
        return
    service = promo_service(dialog_manager)
    code = await service.get_code(selected)
    if code is None:
        set_notice(dialog_manager, str(i18n_ctx.messages.admin_promo_not_found()))
        await dialog_manager.switch_to(AdminSG.promo_menu, show_mode=ShowMode.EDIT)
    else:
        await service.set_enabled(code=selected, enabled=not code.is_enabled)
        set_notice(
            dialog_manager,
            str(
                i18n_ctx.messages.admin_promo_toggle_done(
                    code=selected,
                    status=(
                        str(i18n_ctx.messages.admin_promo_status_disabled())
                        if code.is_enabled
                        else str(i18n_ctx.messages.admin_promo_status_active())
                    ),
                )
            ),
        )
        await dialog_manager.switch_to(AdminSG.promo_details, show_mode=ShowMode.EDIT)
    await callback.answer()


async def promo_set_selected_unlimited(
    callback: CallbackQuery,
    _: Button,
    dialog_manager: DialogManager,
) -> None:
    await _promo_set_selected_limit(
        callback=callback,
        dialog_manager=dialog_manager,
        max_activations=None,
    )


async def promo_cleanup_exhausted(
    callback: CallbackQuery,
    _: Button,
    dialog_manager: DialogManager,
) -> None:
    i18n_ctx = i18n(dialog_manager)
    service = promo_service(dialog_manager)
    codes = await service.list_codes(limit=500)
    exhausted_codes = [
        code.code
        for code in codes
        if code.max_activations is not None and code.activations >= code.max_activations
    ]

    removed = 0
    for code in exhausted_codes:
        if await service.delete_code(code):
            removed += 1

    set_notice(
        dialog_manager,
        str(i18n_ctx.messages.admin_promo_cleanup_done(count=removed)),
    )
    await dialog_manager.switch_to(AdminSG.promo_menu, show_mode=ShowMode.EDIT)
    await callback.answer()


async def promo_delete_bulk_selected(
    callback: CallbackQuery,
    _: Button,
    dialog_manager: DialogManager,
) -> None:
    i18n_ctx = i18n(dialog_manager)
    selected_codes = promo_bulk_selected_codes(dialog_manager)
    if not selected_codes:
        set_notice(dialog_manager, str(i18n_ctx.messages.admin_promo_bulk_delete_empty()))
        await dialog_manager.switch_to(AdminSG.promo_menu, show_mode=ShowMode.EDIT)
        await callback.answer()
        return

    removed = 0
    service = promo_service(dialog_manager)
    for code in selected_codes:
        if await service.delete_code(code):
            removed += 1

    clear_promo_bulk_selected_codes(dialog_manager)
    set_notice(
        dialog_manager,
        str(i18n_ctx.messages.admin_promo_bulk_delete_done(count=removed)),
    )
    await dialog_manager.switch_to(AdminSG.promo_menu, show_mode=ShowMode.EDIT)
    await callback.answer()


async def _promo_set_selected_limit(
    *,
    callback: CallbackQuery,
    dialog_manager: DialogManager,
    max_activations: int | None,
) -> None:
    i18n_ctx = i18n(dialog_manager)
    selected = promo_selected_code(dialog_manager)
    if selected is None:
        set_notice(dialog_manager, str(i18n_ctx.messages.admin_promo_not_found()))
        await dialog_manager.switch_to(AdminSG.promo_menu, show_mode=ShowMode.EDIT)
        await callback.answer()
        return

    service = promo_service(dialog_manager)
    try:
        updated = await service.set_max_activations(
            code=selected,
            max_activations=max_activations,
        )
    except PromoCodeService.Error:
        set_notice(dialog_manager, str(i18n_ctx.messages.admin_promo_not_found()))
        await dialog_manager.switch_to(AdminSG.promo_menu, show_mode=ShowMode.EDIT)
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
        await dialog_manager.switch_to(AdminSG.promo_details, show_mode=ShowMode.EDIT)
    await callback.answer()
