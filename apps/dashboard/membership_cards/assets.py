"""
Asset helpers for PDF-safe logo, member photo, and QR loading.
"""
from __future__ import annotations

from io import BytesIO

import qrcode
from django.contrib.staticfiles import finders
from PIL import Image, ImageDraw, ImageFont, ImageOps
from reportlab.lib.utils import ImageReader


def _image_reader_from_pil(image: Image.Image) -> ImageReader:
    output = BytesIO()
    image.save(output, format="PNG")
    output.seek(0)
    return ImageReader(output)


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


def load_logo_reader():
    path = (
        finders.find("images/ascai-logo.png")
        or finders.find("images/apple-touch-icon.png")
        or finders.find("images/web-app-manifest-512x512.png")
    )
    if not path:
        return None
    try:
        return _image_reader_from_pil(_trim_near_white(Image.open(path)))
    except Exception:
        return None


def load_photo_reader(photo_field, initials: str):
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
    return _image_reader_from_pil(image)


def make_qr_reader(data: str):
    qr = qrcode.QRCode(box_size=12, border=1)
    qr.add_data(data)
    qr.make(fit=True)
    image = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    return _image_reader_from_pil(image)
