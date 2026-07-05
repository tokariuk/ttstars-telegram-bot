from typing import cast

from aiogram_dialog import DialogManager
from aiogram_i18n import I18nContext

from app.models.dto.user import UserDto


def get_i18n(dialog_manager: DialogManager) -> I18nContext:
    return cast(I18nContext, dialog_manager.middleware_data["i18n"])


def get_user(dialog_manager: DialogManager) -> UserDto:
    return cast(UserDto, dialog_manager.middleware_data["user"])
