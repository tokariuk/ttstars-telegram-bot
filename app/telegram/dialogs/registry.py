from aiogram import Dispatcher
from aiogram_dialog import setup_dialogs as setup_dialog_manager

from app.telegram.dialogs.flows.admin.dialog import dialog as admin_dialog
from app.telegram.dialogs.flows.admin.router import router as admin_router
from app.telegram.dialogs.flows.storefront.dialog import dialog as storefront_dialog
from app.telegram.dialogs.flows.storefront.router import router as storefront_router


def register_dialogs(dispatcher: Dispatcher) -> None:
    dispatcher.include_routers(
        admin_router,
        storefront_router,
        admin_dialog,
        storefront_dialog,
    )
    setup_dialog_manager(dispatcher)
