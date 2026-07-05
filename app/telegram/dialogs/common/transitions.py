from typing import Any, Mapping

from aiogram.fsm.state import State
from aiogram_dialog import DialogManager, StartMode


async def reset_stack_to(
    dialog_manager: DialogManager,
    state: State,
    data: Mapping[str, Any] | None = None,
) -> None:
    await dialog_manager.start(
        state=state,
        mode=StartMode.RESET_STACK,
        data=dict(data) if data else None,
    )
