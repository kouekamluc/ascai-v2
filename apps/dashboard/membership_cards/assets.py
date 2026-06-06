"""
Asset helpers for membership card HTML/PDF rendering (WeasyPrint).
"""
from __future__ import annotations

import base64
import json
from io import BytesIO
from pathlib import Path

import qrcode
from django.contrib.staticfiles import finders
from PIL import Image, ImageDraw, ImageFont, ImageOps


def _path_to_uri(path: str | Path) -> str:
    return Path(path).resolve().as_uri()


def _image_to_data_uri(image: Image.Image, fmt: str = "PNG") -> str:
    output = BytesIO()
    image.save(output, format=fmt)
    encoded = base64.b64encode(output.getvalue()).decode("ascii")
    mime = "image/png" if fmt.upper() == "PNG" else f"image/{fmt.lower()}"
    return f"data:{mime};base64,{encoded}"


def _trim_near_white(image: Image.Image) -> Image.Image:
    image = image.convert("RGBA")
    pixels = image.load()
    xs = []
    ys = []
    for y in range(image.height):
        for x in range(image.width):
            r, g, b, a = pixels[x, y]
            if a and not (r > 245 and g > 245 and b > 245):
                xs.append(x)
                ys.append(y)
    if not xs:
        return image
    return image.crop((min(xs), min(ys), max(xs) + 1, max(ys) + 1))


def resolve_logo_path() -> str | None:
    return (
        finders.find("images/ascai-logo.png")
        or finders.find("images/apple-touch-icon.png")
        or finders.find("images/web-app-manifest-512x512.png")
        or finders.find("images/ascai-logo-placeholder.svg")
    )


def resolve_logo_url() -> str | None:
    path = resolve_logo_path()
    return _path_to_uri(path) if path else None


def resolve_css_path() -> str:
    path = finders.find("members/css/membership_card.css")
    if not path:
        raise FileNotFoundError("members/css/membership_card.css not found in static files.")
    return path


def make_photo_data_uri(photo_field, full_name: str) -> str:
    initials = "".join(part[:1] for part in full_name.split()[:2]).upper() or "A"
    image = None
    if photo_field:
        try:
            photo_field.open("rb")
            image = Image.open(photo_field).convert("RGB")
            photo_field.close()
        except Exception:
            image = None

    if image is None:
        image = Image.new("RGB", (420, 420), "#e8f0ec")
        draw = ImageDraw.Draw(image)
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 150)
        except Exception:
            font = ImageFont.load_default()
        draw.text((210, 210), initials, fill="#007A3D", font=font, anchor="mm")

    image = ImageOps.fit(image, (420, 420), Image.LANCZOS)
    return _image_to_data_uri(image)


def make_qr_data_uri(payload: str | dict) -> str:
    if isinstance(payload, dict):
        payload = json.dumps(payload, separators=(",", ":"))
    qr = qrcode.QRCode(box_size=12, border=1)
    qr.add_data(payload)
    qr.make(fit=True)
    image = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    return _image_to_data_uri(image)


# ReportLab fallback helpers (legacy drawing.py)
def load_logo_reader():
    from reportlab.lib.utils import ImageReader

    path = resolve_logo_path()
    if not path:
        return None
    try:
        output = BytesIO()
        _trim_near_white(Image.open(path)).save(output, format="PNG")
        output.seek(0)
        return ImageReader(output)
    except Exception:
        return None


def load_photo_reader(photo_field, initials: str):
    from reportlab.lib.utils import ImageReader

    data_uri = make_photo_data_uri(photo_field, initials or "A")
    raw = base64.b64decode(data_uri.split(",", 1)[1])
    return ImageReader(BytesIO(raw))


def make_qr_reader(data: str):
    from reportlab.lib.utils import ImageReader

    raw = base64.b64decode(make_qr_data_uri(data).split(",", 1)[1])
    return ImageReader(BytesIO(raw))
