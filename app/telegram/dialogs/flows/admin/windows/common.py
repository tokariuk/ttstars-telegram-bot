from typing import Any, cast

from aiogram.types import ContentType
from aiogram_dialog.api.entities.media import MediaAttachment
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.media.dynamic import MediaSelector


def _banner_selector(data: dict[str, Any]) -> MediaAttachment | None:
    banner_url = data.get("banner_url")
    if not isinstance(banner_url, str) or not banner_url:
        return None
    return MediaAttachment(type=ContentType.PHOTO, url=banner_url, use_pipe=True)


def banner_preview() -> DynamicMedia:
    return DynamicMedia(selector=cast(MediaSelector, _banner_selector))
