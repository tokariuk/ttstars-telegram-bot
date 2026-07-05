from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Format

from ..getters import order_force_getter, order_retry_getter, orders_menu_getter
from ..handlers import (
    handle_order_force_input,
    handle_order_retry_input,
    show_menu,
    show_order_force,
    show_order_retry,
    show_orders_menu,
)
from ..ids import (
    ADMIN_ORDERS_BACK_TO_MENU_BUTTON_ID,
    ADMIN_ORDERS_FORCE_BUTTON_ID,
    ADMIN_ORDERS_RETRY_BUTTON_ID,
)
from ..states import AdminSG

orders_menu_window: Window = Window(
    Format("{text}"),
    Button(
        Format("{retry_button_text}"),
        id=ADMIN_ORDERS_RETRY_BUTTON_ID,
        on_click=show_order_retry,
    ),
    Button(
        Format("{force_button_text}"),
        id=ADMIN_ORDERS_FORCE_BUTTON_ID,
        on_click=show_order_force,
    ),
    Button(
        Format("{back_button_text}"),
        id=ADMIN_ORDERS_BACK_TO_MENU_BUTTON_ID,
        on_click=show_menu,
    ),
    state=AdminSG.orders_menu,
    getter=orders_menu_getter,
)

order_retry_window: Window = Window(
    Format("{text}"),
    MessageInput(handle_order_retry_input),
    Button(
        Format("{back_button_text}"),
        id=ADMIN_ORDERS_BACK_TO_MENU_BUTTON_ID,
        on_click=show_orders_menu,
    ),
    state=AdminSG.order_retry,
    getter=order_retry_getter,
)

order_force_window: Window = Window(
    Format("{text}"),
    MessageInput(handle_order_force_input),
    Button(
        Format("{back_button_text}"),
        id=ADMIN_ORDERS_BACK_TO_MENU_BUTTON_ID,
        on_click=show_orders_menu,
    ),
    state=AdminSG.order_force,
    getter=order_force_getter,
)


__all__ = [
    "order_force_window",
    "order_retry_window",
    "orders_menu_window",
]
