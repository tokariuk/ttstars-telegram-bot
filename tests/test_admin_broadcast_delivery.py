from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from aiogram.exceptions import TelegramRetryAfter
from aiogram.methods import SendMessage

from app.telegram.dialogs.flows.admin.handlers import actions
from app.telegram.dialogs.flows.admin.handlers.shared import (
    load_broadcast_payload,
    save_broadcast_payload,
)
from app.telegram.dialogs.flows.admin.helpers import (
    BroadcastDeliveryResult,
    BroadcastPayload,
    _deliver_to_user,
    deliver_broadcast,
    send_broadcast_preview,
)


class AdminBroadcastDeliveryTests(unittest.IsolatedAsyncioTestCase):
    def test_new_broadcasts_enable_link_preview_by_default(self) -> None:
        payload = BroadcastPayload(
            text_html="https://ttstars.xyz",
            photo_file_id=None,
            buttons=[],
            target_languages=None,
            include_close_button=False,
        )

        self.assertTrue(
            hasattr(payload, "link_preview_enabled"),
            "broadcast payload must carry the link-preview preference",
        )
        self.assertTrue(payload.link_preview_enabled)

    async def test_preview_disables_telegram_link_preview_when_requested(self) -> None:
        bot = SimpleNamespace(send_message=AsyncMock(return_value=object()))
        payload = BroadcastPayload(
            text_html="https://ttstars.xyz",
            photo_file_id=None,
            buttons=[],
            target_languages=None,
            include_close_button=False,
            link_preview_enabled=False,
        )

        await send_broadcast_preview(
            bot=bot,
            i18n=MagicMock(),
            chat_id=777,
            payload=payload,
        )

        self.assertTrue(bot.send_message.await_args.kwargs["disable_web_page_preview"])

    async def test_admin_can_toggle_link_preview_while_building_broadcast(self) -> None:
        dialog_manager = SimpleNamespace(dialog_data={}, switch_to=AsyncMock())
        save_broadcast_payload(
            dialog_manager=dialog_manager,
            payload=BroadcastPayload(
                text_html="https://ttstars.xyz",
                photo_file_id=None,
                buttons=[],
                target_languages=None,
                include_close_button=False,
            ),
        )
        callback = SimpleNamespace(answer=AsyncMock())
        toggle = getattr(actions, "broadcast_toggle_link_preview", None)

        self.assertIsNotNone(toggle, "link-preview toggle action is missing")
        if toggle is None:
            return
        await toggle(callback, MagicMock(), dialog_manager)

        payload = load_broadcast_payload(dialog_manager)
        self.assertIsNotNone(payload)
        if payload is not None:
            self.assertFalse(payload.link_preview_enabled)

    async def test_bulk_delivery_paces_chunks_to_avoid_flood_control(self) -> None:
        user_service = SimpleNamespace(
            count_active=AsyncMock(return_value=4),
            list_recipients=AsyncMock(
                side_effect=[[(1, "ru"), (2, "ru"), (3, "ru"), (4, "ru")], []]
            ),
        )
        payload = BroadcastPayload(
            text_html="Hello",
            photo_file_id=None,
            buttons=[],
            target_languages=None,
            include_close_button=False,
        )

        with (
            patch(
                "app.telegram.dialogs.flows.admin.helpers._deliver_to_user",
                new=AsyncMock(return_value="sent"),
            ),
            patch(
                "app.telegram.dialogs.flows.admin.helpers.asyncio.sleep",
                new=AsyncMock(),
            ) as sleep,
        ):
            result = await deliver_broadcast(
                bot=MagicMock(),
                i18n=MagicMock(),
                user_service=user_service,
                payload=payload,
                batch_size=4,
                concurrency=2,
            )

        self.assertEqual(result.sent, 4)
        sleep.assert_awaited_once()

    async def test_delivery_retries_repeated_flood_control_responses(self) -> None:
        method = SendMessage(chat_id=42, text="test")
        retry = TelegramRetryAfter(method=method, message="retry later", retry_after=0)
        bot = SimpleNamespace(send_message=AsyncMock(side_effect=[retry, retry, object()]))
        user_service = SimpleNamespace(set_blocked_at=AsyncMock())

        with patch(
            "app.telegram.dialogs.flows.admin.helpers.asyncio.sleep",
            new=AsyncMock(),
        ):
            result = await _deliver_to_user(
                bot=bot,
                i18n=MagicMock(),
                user_service=user_service,
                user_id=42,
                language="ru",
                payload=BroadcastPayload(
                    text_html="Hello",
                    photo_file_id=None,
                    buttons=[],
                    target_languages=None,
                    include_close_button=False,
                ),
                include_close_button=False,
            )

        self.assertEqual(result, "sent")
        self.assertEqual(bot.send_message.await_count, 3)

    async def test_send_action_previews_exact_payload_before_bulk_delivery(self) -> None:
        messages = MagicMock()
        messages.admin_broadcast_started.return_value = "started"
        messages.admin_broadcast_done.return_value = "done"
        i18n = SimpleNamespace(messages=messages)
        user_service = object()
        dialog_manager = SimpleNamespace(
            dialog_data={},
            middleware_data={"i18n": i18n, "user_service": user_service},
            switch_to=AsyncMock(),
        )
        payload = BroadcastPayload(
            text_html="<b>Campaign</b>",
            photo_file_id=None,
            buttons=[],
            target_languages=None,
            include_close_button=False,
        )
        save_broadcast_payload(dialog_manager=dialog_manager, payload=payload)
        bot = SimpleNamespace(send_message=AsyncMock(return_value=object()))
        callback = SimpleNamespace(
            answer=AsyncMock(),
            bot=bot,
            from_user=SimpleNamespace(id=777),
        )

        with patch.object(
            actions,
            "deliver_broadcast",
            new=AsyncMock(
                return_value=BroadcastDeliveryResult(total=1, sent=1, failed=0, blocked=0)
            ),
        ):
            await actions.broadcast_send(callback, MagicMock(), dialog_manager)

        bot.send_message.assert_awaited_once()
        self.assertEqual(bot.send_message.await_args.kwargs["chat_id"], 777)
        self.assertEqual(bot.send_message.await_args.kwargs["text"], "<b>Campaign</b>")


if __name__ == "__main__":
    unittest.main()
