from __future__ import annotations

import hashlib
import os
from functools import lru_cache
from pathlib import Path
from typing import Final
from urllib.parse import quote_plus

from PIL import Image, ImageDraw, ImageFont

_CARD_STYLE_VERSION: Final[str] = "v11"
_STARS_FONT_SIZE: Final[int] = 195
_AMOUNT_FONT_SIZE: Final[int] = 60
_STARS_ICON_GAP: Final[int] = 30
_ROWS_GAP: Final[int] = 42
_GROUP_OFFSET_Y: Final[int] = 0
_STAR_ALPHA_THRESHOLD: Final[int] = 130
_AMOUNT_TEXT_ALPHA: Final[int] = int(round(255 * 0.8))
_GRADIENT_FROM: Final[tuple[int, int, int]] = (255, 255, 255)
_GRADIENT_TO: Final[tuple[int, int, int]] = (212, 212, 212)
_JPEG_QUALITY: Final[int] = 94


def build_check_card_preview_url(
    *,
    stars_count: int,
    amount_usd: str,
    seed: str,
    base_url: str | None = None,
) -> str:
    try:
        relative_path = render_check_card(
            stars_count=stars_count,
            amount_usd=amount_usd,
            seed=seed,
        )
    except Exception:
        text = quote_plus(f"{stars_count} Stars\n~{_normalize_amount_value(amount_usd)}$")
        return f"https://placehold.co/1600x1000/14120b/f8d85a.jpg?font=poppins&text={text}"

    resolved_base_url = (base_url or os.getenv("SERVER_URL", "")).strip().rstrip("/")
    if not resolved_base_url:
        text = quote_plus(f"{stars_count} Stars\n~{_normalize_amount_value(amount_usd)}$")
        return f"https://placehold.co/1600x1000/14120b/f8d85a.jpg?font=poppins&text={text}"
    return f"{resolved_base_url}{relative_path}"


def render_check_card(*, stars_count: int, amount_usd: str, seed: str) -> str:
    amount_value = _normalize_amount_value(amount_usd)
    file_hash = hashlib.sha256(
        f"{_CARD_STYLE_VERSION}|{seed}|{stars_count}|{amount_value}".encode("utf-8")
    ).hexdigest()
    file_name = f"{file_hash[:24]}.jpg"

    output_dir = _checks_root() / "generated"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / file_name
    if output_path.is_file():
        return f"/assets/checks/generated/{file_name}"

    background = _background_template().copy()
    stars_icon = _stars_icon_overlay()
    stars_font = _load_font(path=_semibold_font_path(), size=_STARS_FONT_SIZE)
    amount_font = _load_font(path=_medium_font_path(), size=_AMOUNT_FONT_SIZE)

    stars_label = str(stars_count)
    amount_label = f"~{amount_value}$"
    draw = ImageDraw.Draw(background)
    stars_box = draw.textbbox((0, 0), stars_label, font=stars_font)
    amount_box = draw.textbbox((0, 0), amount_label, font=amount_font)

    stars_w = stars_box[2] - stars_box[0]
    stars_h = stars_box[3] - stars_box[1]
    amount_w = amount_box[2] - amount_box[0]
    amount_h = amount_box[3] - amount_box[1]

    icon_bbox = _stars_icon_bbox()
    icon_w = icon_bbox[2] - icon_bbox[0]
    icon_h = icon_bbox[3] - icon_bbox[1]

    line_w = stars_w + _STARS_ICON_GAP + icon_w
    line_h = max(stars_h, icon_h)
    group_h = line_h + _ROWS_GAP + amount_h

    canvas_w = int(background.width)
    canvas_h = int(background.height)
    line_x = int((canvas_w - line_w) // 2)
    line_y = int((canvas_h - group_h) // 2 + _GROUP_OFFSET_Y)

    stars_x = int(line_x)
    stars_y = int(line_y + (line_h - stars_h) // 2)
    _draw_gradient_text(
        image=background,
        text=stars_label,
        font=stars_font,
        x=stars_x,
        y=stars_y,
        alpha=255,
    )

    icon_visible_x = int(stars_x + stars_w + _STARS_ICON_GAP)
    icon_visible_y = int(line_y + (line_h - icon_h) // 2)
    icon_x = int(icon_visible_x - icon_bbox[0])
    icon_y = int(icon_visible_y - icon_bbox[1])
    background.alpha_composite(stars_icon, (int(round(icon_x)), int(round(icon_y))))

    amount_x = int((canvas_w - amount_w) // 2)
    amount_y = int(line_y + line_h + _ROWS_GAP)
    _draw_gradient_text(
        image=background,
        text=amount_label,
        font=amount_font,
        x=amount_x,
        y=amount_y,
        alpha=_AMOUNT_TEXT_ALPHA,
    )

    tmp_path = output_path.with_suffix(".tmp.jpg")
    background.convert("RGB").save(tmp_path, format="JPEG", quality=_JPEG_QUALITY, optimize=False)
    tmp_path.replace(output_path)
    return f"/assets/checks/generated/{file_name}"


def _draw_gradient_text(
    *,
    image: Image.Image,
    text: str,
    font: ImageFont.FreeTypeFont,
    x: int,
    y: int,
    alpha: int,
) -> None:
    draw = ImageDraw.Draw(image)
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    left_i, top_i, right_i, bottom_i = (
        int(left),
        int(top),
        int(right),
        int(bottom),
    )
    width = max(1, right_i - left_i)
    height = max(1, bottom_i - top_i)

    mask = Image.new("L", (width, height), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.text((-left_i, -top_i), text, font=font, fill=255)
    if alpha < 255:
        alpha_lut = [(value * alpha) // 255 for value in range(256)]
        mask = mask.point(alpha_lut)

    gradient = _text_gradient(width=width, height=height).copy()
    gradient.putalpha(mask)
    image.alpha_composite(gradient, (x, y))


@lru_cache(maxsize=64)
def _text_gradient(*, width: int, height: int) -> Image.Image:
    # Bilinear upscale from 2x2 gives the same diagonal blend as tx/ty mix,
    # but runs inside Pillow's C code and is much faster than Python loops.
    mix = Image.new("L", (2, 2))
    mix.putdata((0, 128, 128, 255))
    mix = mix.resize((width, height), resample=Image.Resampling.BILINEAR)

    base = Image.new("RGBA", (width, height), (*_GRADIENT_FROM, 255))
    target = Image.new("RGBA", (width, height), (*_GRADIENT_TO, 255))
    return Image.composite(target, base, mix)


def _solid_icon_bbox(icon: Image.Image) -> tuple[int, int, int, int]:
    alpha = icon.getchannel("A")
    threshold_lut = [255 if value >= _STAR_ALPHA_THRESHOLD else 0 for value in range(256)]
    mask = alpha.point(threshold_lut)
    bbox = mask.getbbox()
    if bbox is not None:
        return bbox
    fallback = alpha.getbbox()
    if fallback is not None:
        return fallback
    width, height = icon.size
    return (0, 0, width, height)


def _normalize_amount_value(raw: str) -> str:
    normalized = raw.strip().replace(" ", "")
    if not normalized:
        return "0,00"
    return normalized.replace(".", ",")


@lru_cache(maxsize=1)
def _project_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "assets" / "checks").is_dir():
            return parent
    return current.parents[5]


@lru_cache(maxsize=1)
def _checks_root() -> Path:
    return _project_root() / "assets" / "checks"


@lru_cache(maxsize=1)
def _background_template() -> Image.Image:
    return Image.open(_background_path()).convert("RGBA")


@lru_cache(maxsize=1)
def _stars_icon_overlay() -> Image.Image:
    return Image.open(_icon_path()).convert("RGBA")


@lru_cache(maxsize=1)
def _stars_icon_bbox() -> tuple[int, int, int, int]:
    return _solid_icon_bbox(_stars_icon_overlay())


def _background_path() -> Path:
    return _checks_root() / "backgrounds" / "stars_card_background.jpg"


def _icon_path() -> Path:
    return _checks_root() / "overlays" / "stars_icon_overlay.png"


def _medium_font_path() -> Path:
    return _checks_root() / "fonts" / "golos_text_medium.ttf"


def _semibold_font_path() -> Path:
    return _checks_root() / "fonts" / "golos_text_semibold.ttf"


@lru_cache(maxsize=8)
def _load_font(*, path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size=size)
