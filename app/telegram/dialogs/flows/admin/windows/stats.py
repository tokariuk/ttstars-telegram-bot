from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Format

from ..getters import stats_getter
from ..handlers import show_menu
from ..ids import ADMIN_STATS_BACK_TO_MENU_BUTTON_ID
from ..states import AdminSG

stats_window: Window = Window(
    Format("{text}"),
    Button(
        Format("{back_button_text}"),
        id=ADMIN_STATS_BACK_TO_MENU_BUTTON_ID,
        on_click=show_menu,
    ),
    state=AdminSG.stats,
    getter=stats_getter,
)


__all__ = ["stats_window"]
