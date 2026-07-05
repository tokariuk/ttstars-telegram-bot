from __future__ import annotations

from typing import cast

from aiogram_dialog import DialogManager

from app.services.crud import CheckService
from app.services.crud.stars_order import StarsOrderService
from app.services.crud.stars_sell_order import StarsSellOrderService
from app.services.crud.user import UserService

from .shared_constants import STATE_NOTICE_KEY


def stars_order_service(dialog_manager: DialogManager) -> StarsOrderService:
    return cast(StarsOrderService, dialog_manager.middleware_data["stars_order_service"])


def user_service(dialog_manager: DialogManager) -> UserService:
    return cast(UserService, dialog_manager.middleware_data["user_service"])


def check_service(dialog_manager: DialogManager) -> CheckService:
    return cast(CheckService, dialog_manager.middleware_data["check_service"])


def stars_sell_order_service(dialog_manager: DialogManager) -> StarsSellOrderService:
    return cast(
        StarsSellOrderService,
        dialog_manager.middleware_data["stars_sell_order_service"],
    )


def set_notice(dialog_manager: DialogManager, text: str) -> None:
    dialog_manager.dialog_data[STATE_NOTICE_KEY] = text


def clear_notice(dialog_manager: DialogManager) -> None:
    dialog_manager.dialog_data.pop(STATE_NOTICE_KEY, None)
