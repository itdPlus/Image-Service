import io
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from PIL import Image, ImageDraw, ImageFont
from pilmoji import Pilmoji
from pydantic import BaseModel, field_validator

TEMPLATE_PATH         = Path(__file__).parent / "blank.jpg"
FONT_PATH             = Path(__file__).parent / "OnestVariable.ttf"
VERIFICATION_PNG_PATH = Path(__file__).parent / "verification_check.png"

FONT_SIZE_DISPLAY_NAME = 111
FONT_SIZE_USERNAME     = 54
FONT_SIZE_EMOJI        = 170

VERIFICATION_CHECK_SIZE   = 74
VERIFICATION_CHECK_GAP    = 16
VERIFICATION_CHECK_OFFSET_Y = 0

FONT_WEIGHT_DISPLAY_NAME = 700
FONT_WEIGHT_USERNAME     = 400

AVATAR_CENTER_X = 972
AVATAR_CENTER_Y = 280

EMOJI_OFFSET_X = -10
EMOJI_OFFSET_Y = -20

DISPLAY_NAME_Y = 624
USERNAME_Y     = 764

COLOR_DISPLAY_NAME = (255, 255, 255, 255)
COLOR_USERNAME     = (0xD0, 0x9E, 0x0A, 255)


app = FastAPI(title="Winner Card Generator")


class WinnerPayload(BaseModel):
    avatar:      str
    displayName: str
    username:    str
    verified:    bool = False

    @field_validator("username")
    @classmethod
    def strip_at(cls, v: str) -> str:
        return v.lstrip("@")


def _load_variable_font(size: int, weight: int) -> ImageFont.FreeTypeFont:
    if not FONT_PATH.exists():
        raise HTTPException(
            status_code=500,
            detail=f"Font file not found: {FONT_PATH}",
        )
    font = ImageFont.truetype(str(FONT_PATH), size)
    try:
        font.set_variation_by_axes([weight])
    except Exception:
        pass
    return font


def _center_x(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    img_width: int,
) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    return (img_width - text_width) // 2


def _get_text_width(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def _draw_verification_check(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    size: int = VERIFICATION_CHECK_SIZE,
) -> None:
    if not VERIFICATION_PNG_PATH.exists():
        raise HTTPException(
            status_code=500,
            detail=f"Verification PNG not found: {VERIFICATION_PNG_PATH}",
        )

    check_img = Image.open(VERIFICATION_PNG_PATH).convert("RGBA")

    if check_img.width != size or check_img.height != size:
        check_img = check_img.resize((size, size), Image.Resampling.LANCZOS)

    paste_x = int(x - size / 2)
    paste_y = int(y - size / 2)

    base_img = draw._image
    base_img.paste(check_img, (paste_x, paste_y), check_img)


def generate_winner_image(payload: WinnerPayload) -> bytes:
    if not TEMPLATE_PATH.exists():
        raise HTTPException(
            status_code=500,
            detail=f"Template file not found: {TEMPLATE_PATH}",
        )
    img = Image.open(TEMPLATE_PATH).convert("RGBA")
    img_w, _ = img.size

    draw = ImageDraw.Draw(img)

    font_name  = _load_variable_font(FONT_SIZE_DISPLAY_NAME, FONT_WEIGHT_DISPLAY_NAME)
    font_user  = _load_variable_font(FONT_SIZE_USERNAME,     FONT_WEIGHT_USERNAME)
    font_emoji = _load_variable_font(FONT_SIZE_EMOJI,        400)

    emoji_x = AVATAR_CENTER_X - FONT_SIZE_EMOJI // 2 + EMOJI_OFFSET_X
    emoji_y = AVATAR_CENTER_Y - FONT_SIZE_EMOJI // 2 + EMOJI_OFFSET_Y

    with Pilmoji(img) as pilmoji:
        pilmoji.text(
            (emoji_x, emoji_y),
            payload.avatar,
            font=font_emoji,
            fill=(255, 255, 255, 255),
        )

    x_name = _center_x(draw, payload.displayName, font_name, img_w)
    draw.text(
        (x_name, DISPLAY_NAME_Y),
        payload.displayName,
        font=font_name,
        fill=COLOR_DISPLAY_NAME,
    )

    if payload.verified:
        text_bbox   = draw.textbbox((x_name, DISPLAY_NAME_Y), payload.displayName, font=font_name)
        text_width  = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        check_x = x_name + text_width + VERIFICATION_CHECK_GAP + VERIFICATION_CHECK_SIZE // 2
        check_y = text_bbox[1] + text_height // 2 + VERIFICATION_CHECK_OFFSET_Y

        _draw_verification_check(draw, check_x, check_y, VERIFICATION_CHECK_SIZE)

    username_text = f"@{payload.username}"
    x_user = _center_x(draw, username_text, font_user, img_w)
    draw.text(
        (x_user, USERNAME_Y),
        username_text,
        font=font_user,
        fill=COLOR_USERNAME,
    )

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


@app.post("/save")
async def save_winner(payload: WinnerPayload) -> Response:
    png_bytes = generate_winner_image(payload)
    return Response(content=png_bytes, media_type="image/png")
