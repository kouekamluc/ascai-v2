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
from django.templatetags.static import static
from PIL import Image, ImageDraw, ImageFont, ImageOps


def _image_to_data_uri(image: Image.Image, fmt: str = "PNG") -> str:
    output = BytesIO()
    image.save(output, format=fmt)
    encoded = base64.b64encode(output.getvalue()).decode("ascii")
    mime = "image/png" if fmt.upper() == "PNG" else f"image/{fmt.lower()}"
    return f"data:{mime};base64,{encoded}"


def _file_to_data_uri(path: str | Path) -> str:
    path = Path(path)
    suffix = path.suffix.lower()
    raw = path.read_bytes()
    encoded = base64.b64encode(raw).decode("ascii")
    if suffix == ".svg":
        return f"data:image/svg+xml;base64,{encoded}"
    if suffix in {".jpg", ".jpeg"}:
        return f"data:image/jpeg;base64,{encoded}"
    if suffix == ".webp":
        return f"data:image/webp;base64,{encoded}"
    return f"data:image/png;base64,{encoded}"


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
    """Card-safe logo only — never favicon/manifest assets (may include coat of arms)."""
    return (
        finders.find("images/ascai-logo-card.svg")
        or finders.find("images/ascai-logo-card.png")
        or finders.find("images/ascai-logo.png")
        or finders.find("images/ascai-logo-placeholder.svg")
    )


def make_logo_data_uri() -> str | None:
    path = resolve_logo_path()
    if not path:
        return None
    try:
        if Path(path).suffix.lower() == ".svg":
            return _file_to_data_uri(path)
        return _image_to_data_uri(_trim_near_white(Image.open(path)))
    except Exception:
        return None


def resolve_logo_static_url() -> str:
    if finders.find("images/ascai-logo-card.svg"):
        return static("images/ascai-logo-card.svg")
    if finders.find("images/ascai-logo-card.png"):
        return static("images/ascai-logo-card.png")
    if finders.find("images/ascai-logo.png"):
        return static("images/ascai-logo.png")
    return static("images/ascai-logo-placeholder.svg")


def resolve_watermark_data_uri() -> str | None:
    path = finders.find("members/images/colosseum-watermark.svg")
    return _file_to_data_uri(path) if path else None


def resolve_css_path() -> str:
    path = finders.find("members/css/membership_card.css")
    if not path:
        raise FileNotFoundError("members/css/membership_card.css not found in static files.")
    return path


def make_photo_data_uri(photo_field, full_name: str) -> str:
    initials = "".join(part[:1] for part in full_name.split()[:2]).upper() or "A"
    image = None
    if photo_field and getattr(photo_field, "name", None):
        try:
            with photo_field.open("rb") as handle:
                image = Image.open(handle).convert("RGB")
        except Exception:
            image = None

    if image is None:
        image = Image.new("RGB", (420, 420), "#e8f0ec")
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()
        for font_path in (
            "C:/Windows/Fonts/arialbd.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        ):
            try:
                font = ImageFont.truetype(font_path, 150)
                break
            except Exception:
                continue
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

    data_uri = make_logo_data_uri()
    if not data_uri:
        return None
    try:
        raw = base64.b64decode(data_uri.split(",", 1)[1])
        return ImageReader(BytesIO(raw))
    except Exception:
        return None


def load_photo_reader(photo_field, initials: str):
    from reportlab.lib.utils import ImageReader

    raw = base64.b64decode(make_photo_data_uri(photo_field, initials or "A").split(",", 1)[1])
    return ImageReader(BytesIO(raw))


def make_qr_reader(data: str):
    from reportlab.lib.utils import ImageReader

    raw = base64.b64decode(make_qr_data_uri(data).split(",", 1)[1])
    return ImageReader(BytesIO(raw))
