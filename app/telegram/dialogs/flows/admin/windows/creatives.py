from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button, Row
from aiogram_dialog.widgets.style import Style
from aiogram_dialog.widgets.text import Format

from app.telegram.dialogs.common.ttstars_interface_emoji import (
    GIFT_EMOJI_ID,
    IMAGE_EMOJI_ID,
    LEFT_SQUARE_EMOJI_ID,
    LIGHTNING_EMOJI_ID,
    TELEGRAM_STAR_EMOJI_ID,
)

from ..getters import (
    creatives_gifts_getter,
    creatives_menu_getter,
    creatives_overview_getter,
    creatives_premium_getter,
    creatives_stars_getter,
)
from ..handlers import (
    acknowledge_creative_preview,
    show_creatives_gifts,
    show_creatives_menu,
    show_creatives_overview,
    show_creatives_premium,
    show_creatives_stars,
    show_menu,
)
from ..ids import (
    ADMIN_CREATIVES_BACK_TO_MENU_BUTTON_ID,
    ADMIN_CREATIVES_BACK_TO_SECTION_BUTTON_ID,
    ADMIN_CREATIVES_GIFT_ENTRY_BUTTON_IDS,
    ADMIN_CREATIVES_OPEN_GIFTS_BUTTON_ID,
    ADMIN_CREATIVES_OPEN_OVERVIEW_BUTTON_ID,
    ADMIN_CREATIVES_OPEN_PREMIUM_BUTTON_ID,
    ADMIN_CREATIVES_OPEN_STARS_BUTTON_ID,
    ADMIN_CREATIVES_OVERVIEW_ENTRY_BUTTON_IDS,
    ADMIN_CREATIVES_PREMIUM_PACK_BUTTON_IDS,
    ADMIN_CREATIVES_STARS_PACK_BUTTON_IDS,
)
from ..states import AdminSG
from .common import banner_preview


def _back_to_creatives_button() -> Button:
    return Button(
        Format("{back_to_section_button_text}"),
        id=ADMIN_CREATIVES_BACK_TO_SECTION_BUTTON_ID,
        on_click=show_creatives_menu,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    )


creatives_menu_window: Window = Window(
    banner_preview(),
    Format("{text}"),
    Row(
        Button(
            Format("{stars_button_text}"),
            id=ADMIN_CREATIVES_OPEN_STARS_BUTTON_ID,
            on_click=show_creatives_stars,
            style=Style(emoji_id=TELEGRAM_STAR_EMOJI_ID),
        ),
        Button(
            Format("{premium_button_text}"),
            id=ADMIN_CREATIVES_OPEN_PREMIUM_BUTTON_ID,
            on_click=show_creatives_premium,
            style=Style(emoji_id=LIGHTNING_EMOJI_ID),
        ),
    ),
    Row(
        Button(
            Format("{gifts_button_text}"),
            id=ADMIN_CREATIVES_OPEN_GIFTS_BUTTON_ID,
            on_click=show_creatives_gifts,
            style=Style(emoji_id=GIFT_EMOJI_ID),
        ),
        Button(
            Format("{overview_button_text}"),
            id=ADMIN_CREATIVES_OPEN_OVERVIEW_BUTTON_ID,
            on_click=show_creatives_overview,
            style=Style(emoji_id=IMAGE_EMOJI_ID),
        ),
    ),
    Button(
        Format("{back_to_menu_button_text}"),
        id=ADMIN_CREATIVES_BACK_TO_MENU_BUTTON_ID,
        on_click=show_menu,
        style=Style(emoji_id=LEFT_SQUARE_EMOJI_ID),
    ),
    state=AdminSG.creatives_menu,
    getter=creatives_menu_getter,
)

creatives_stars_window: Window = Window(
    banner_preview(),
    Format("{text}"),
    *(
        Button(
            Format(f"{{stars_{amount}_button_text}}"),
            id=button_id,
            on_click=acknowledge_creative_preview,
            style=Style(emoji_id=TELEGRAM_STAR_EMOJI_ID),
        )
        for amount, button_id in zip(
            (100, 150, 250, 350, 500, 750, 1000),
            ADMIN_CREATIVES_STARS_PACK_BUTTON_IDS,
            strict=True,
        )
    ),
    _back_to_creatives_button(),
    state=AdminSG.creatives_stars,
    getter=creatives_stars_getter,
)

creatives_premium_window: Window = Window(
    banner_preview(),
    Format("{text}"),
    *(
        Button(
            Format(f"{{premium_{months}_button_text}}"),
            id=button_id,
            on_click=acknowledge_creative_preview,
            style=Style(emoji_id=LIGHTNING_EMOJI_ID),
        )
        for months, button_id in zip(
            (3, 6, 12),
            ADMIN_CREATIVES_PREMIUM_PACK_BUTTON_IDS,
            strict=True,
        )
    ),
    _back_to_creatives_button(),
    state=AdminSG.creatives_premium,
    getter=creatives_premium_getter,
)

creatives_gifts_window: Window = Window(
    banner_preview(),
    Format("{text}"),
    Button(
        Format("{basic_gift_button_text}"),
        id=ADMIN_CREATIVES_GIFT_ENTRY_BUTTON_IDS[0],
        on_click=acknowledge_creative_preview,
        style=Style(emoji_id=GIFT_EMOJI_ID),
    ),
    Button(
        Format("{gift_collection_button_text}"),
        id=ADMIN_CREATIVES_GIFT_ENTRY_BUTTON_IDS[1],
        on_click=acknowledge_creative_preview,
        style=Style(emoji_id=GIFT_EMOJI_ID),
    ),
    _back_to_creatives_button(),
    state=AdminSG.creatives_gifts,
    getter=creatives_gifts_getter,
)

creatives_overview_window: Window = Window(
    banner_preview(),
    Format("{text}"),
    Button(
        Format("{stars_button_text}"),
        id=ADMIN_CREATIVES_OVERVIEW_ENTRY_BUTTON_IDS[0],
        on_click=acknowledge_creative_preview,
        style=Style(emoji_id=TELEGRAM_STAR_EMOJI_ID),
    ),
    Button(
        Format("{premium_button_text}"),
        id=ADMIN_CREATIVES_OVERVIEW_ENTRY_BUTTON_IDS[1],
        on_click=acknowledge_creative_preview,
        style=Style(emoji_id=LIGHTNING_EMOJI_ID),
    ),
    Button(
        Format("{gifts_button_text}"),
        id=ADMIN_CREATIVES_OVERVIEW_ENTRY_BUTTON_IDS[2],
        on_click=acknowledge_creative_preview,
        style=Style(emoji_id=GIFT_EMOJI_ID),
    ),
    _back_to_creatives_button(),
    state=AdminSG.creatives_overview,
    getter=creatives_overview_getter,
)


__all__ = [
    "creatives_gifts_window",
    "creatives_menu_window",
    "creatives_overview_window",
    "creatives_premium_window",
    "creatives_stars_window",
]
