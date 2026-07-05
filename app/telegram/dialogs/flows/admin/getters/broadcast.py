from __future__ import annotations

import html
from collections.abc import Sequence
from typing import Any

from aiogram_dialog import DialogManager

from ..handlers.shared import i18n, load_broadcast_payload, user_service
from ..helpers import BroadcastButton
from .common import consume_notice, with_notice


def _render_buttons_preview(*, payload_buttons: Sequence[BroadcastButton]) -> str:
    if not payload_buttons:
        return "—"
    lines: list[str] = []
    for item in payload_buttons:
        text = getattr(item, "text", "")
        url = getattr(item, "url", "")
        if isinstance(text, str) and isinstance(url, str) and text and url:
            lines.append(
                f'• <a href="{html.escape(url, quote=True)}">{html.escape(text)}</a>'
            )
    return "\n".join(lines) if lines else "—"


async def broadcast_content_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n_ctx = i18n(dialog_manager)
    text = with_notice(
        text=str(i18n_ctx.messages.admin_broadcast_content_prompt()),
        notice=consume_notice(dialog_manager),
    )
    return {
        "text": text,
        "back_button_text": i18n_ctx.buttons.admin_back_menu(),
    }


async def broadcast_buttons_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n_ctx = i18n(dialog_manager)
    text = with_notice(
        text=str(i18n_ctx.messages.admin_broadcast_buttons_prompt()),
        notice=consume_notice(dialog_manager),
    )
    return {
        "text": text,
        "skip_button_text": i18n_ctx.buttons.admin_skip(),
        "back_button_text": i18n_ctx.buttons.admin_back_menu(),
    }


def _render_target_locales(*, target_languages: list[str] | None) -> str:
    if target_languages is None:
        return "all"
    return ", ".join(target_languages) if target_languages else "all"


async def broadcast_options_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n_ctx = i18n(dialog_manager)
    payload = load_broadcast_payload(dialog_manager)
    target_languages = payload.target_languages if payload is not None else None
    include_close_button = payload.include_close_button if payload is not None else False
    available_locales = list(user_service(dialog_manager).config.telegram.locales)
    text = with_notice(
        text=str(
            i18n_ctx.messages.admin_broadcast_options_prompt(
                locales=", ".join(available_locales),
                selected_locales=_render_target_locales(target_languages=target_languages),
                close_button=(
                    str(i18n_ctx.messages.admin_broadcast_option_enabled())
                    if include_close_button
                    else str(i18n_ctx.messages.admin_broadcast_option_disabled())
                ),
            )
        ),
        notice=consume_notice(dialog_manager),
    )
    return {
        "text": text,
        "skip_button_text": i18n_ctx.buttons.admin_skip(),
        "back_button_text": i18n_ctx.buttons.admin_back_menu(),
    }


async def broadcast_confirm_getter(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    i18n_ctx = i18n(dialog_manager)
    payload = load_broadcast_payload(dialog_manager)
    if payload is None:
        base_text = str(i18n_ctx.messages.admin_broadcast_content_invalid())
    else:
        recipients = await user_service(dialog_manager).count_active(
            locales=payload.target_languages,
        )
        summary = str(
            i18n_ctx.messages.admin_broadcast_preview_ready(
                recipients=recipients,
                buttons=len(payload.buttons),
                locales=_render_target_locales(target_languages=payload.target_languages),
                close_button=(
                    str(i18n_ctx.messages.admin_broadcast_option_enabled())
                    if payload.include_close_button
                    else str(i18n_ctx.messages.admin_broadcast_option_disabled())
                ),
            )
        )
        preview_text = payload.text_html or "—"
        if payload.photo_file_id is not None:
            preview_text = f"<i>[Photo]</i>\n{preview_text}"
        buttons_text = _render_buttons_preview(payload_buttons=payload.buttons)
        base_text = (
            f"{summary}\n\n"
            f"<b>📝</b>\n{preview_text}\n\n"
            f"<b>🔗</b>\n{buttons_text}"
        )
    text = with_notice(
        text=base_text,
        notice=consume_notice(dialog_manager),
    )
    return {
        "text": text,
        "send_button_text": i18n_ctx.buttons.admin_send(),
        "restart_button_text": i18n_ctx.buttons.admin_restart(),
        "back_button_text": i18n_ctx.buttons.admin_back_menu(),
    }


__all__ = [
    "broadcast_buttons_getter",
    "broadcast_confirm_getter",
    "broadcast_content_getter",
    "broadcast_options_getter",
]
