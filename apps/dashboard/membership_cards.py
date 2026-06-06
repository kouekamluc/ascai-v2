"""
Membership card PDF generation for paid ASCAI dues.
"""
from __future__ import annotations

from io import BytesIO
from pathlib import Path

import qrcode
from django.contrib.staticfiles import finders
from django.urls import reverse
from django.utils import timezone
from PIL import Image, ImageDraw, ImageFont, ImageOps


CARD_WIDTH = 1011
CARD_HEIGHT = 638
GREEN = "#0d6b52"
DEEP_GREEN = "#10392f"
RED = "#d81924"
YELLOW = "#f2c94c"
GOLD = "#b67a12"
INK = "#141414"
MUTED = "#6b5d49"
PAPER = "#faf7ef"


def _font(size, bold=False, italic=False):
    candidates = []
    if bold:
        candidates.extend([
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/segoeuib.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ])
    elif italic:
        candidates.extend([
            "C:/Windows/Fonts/segoesc.ttf",
            "C:/Windows/Fonts/ariali.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
        ])
    candidates.extend([
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ])
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


def _text(draw, xy, text, size, fill=INK, bold=False, italic=False, anchor=None):
    draw.text(xy, str(text), font=_font(size, bold=bold, italic=italic), fill=fill, anchor=anchor)


def _fit_text(draw, text, max_width, start_size, bold=False, italic=False, min_size=18):
    size = start_size
    while size > min_size:
        font = _font(size, bold=bold, italic=italic)
        if draw.textbbox((0, 0), str(text), font=font)[2] <= max_width:
            return font
        size -= 1
    return _font(min_size, bold=bold, italic=italic)


def _open_logo(size):
    logo_path = finders.find("images/apple-touch-icon.png") or finders.find("images/web-app-manifest-512x512.png")
    if not logo_path:
        return None
    logo = Image.open(logo_path).convert("RGBA")
    logo.thumbnail((size, size), Image.LANCZOS)
    return logo


def _member_avatar(member, size):
    avatar = getattr(member.user, "avatar", None)
    image = None
    if avatar:
        try:
            avatar.open("rb")
            image = Image.open(avatar).convert("RGB")
            avatar.close()
        except Exception:
            image = None

    if image is None:
        image = Image.new("RGB", (size, size), "#e7efe9")
        draw = ImageDraw.Draw(image)
        initials = "".join(part[:1] for part in member.user.get_display_name().split()[:2]).upper() or "A"
        font = _font(72, bold=True)
        draw.text((size // 2, size // 2), initials, fill=GREEN, font=font, anchor="mm")

    image = ImageOps.fit(image, (size, size), Image.LANCZOS)
    return image


def _qr_image(data, size):
    qr = qrcode.QRCode(box_size=8, border=1)
    qr.add_data(data)
    qr.make(fit=True)
    image = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    return image.resize((size, size), Image.Resampling.NEAREST)


def _rounded_paste(base, image, xy, radius, border=GOLD, border_width=4):
    x, y = xy
    w, h = image.size
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w, h), radius=radius, fill=255)
    base.paste(image, xy, mask)
    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle((x, y, x + w, y + h), radius=radius, outline=border, width=border_width)


def _draw_background(draw, side):
    draw.rounded_rectangle((18, 18, CARD_WIDTH - 18, CARD_HEIGHT - 18), radius=36, fill=PAPER, outline="#ded8ca", width=2)
    for offset in range(-200, CARD_WIDTH, 42):
        draw.line((offset, 32, offset + 300, CARD_HEIGHT - 28), fill="#efe8d9", width=1)
    for offset in range(0, CARD_WIDTH + CARD_HEIGHT, 52):
        draw.line((offset, 32, offset - 300, CARD_HEIGHT - 28), fill="#f5eee1", width=1)

    if side == "front":
        draw.pieslice((-120, 420, 560, 980), 190, 292, fill=RED)
        draw.pieslice((-84, 372, 555, 860), 190, 292, fill=GREEN)
        draw.pieslice((-38, 360, 575, 780), 190, 292, fill=YELLOW)
        draw.pieslice((-40, 360, 535, 780), 190, 292, fill=PAPER)
        draw.regular_polygon((185, 562, 20), 5, rotation=-18, fill=YELLOW)
    else:
        draw.rectangle((18, 555, CARD_WIDTH - 18, CARD_HEIGHT - 18), fill=GOLD)
        draw.pieslice((-120, -190, 520, 245), 10, 178, fill=GREEN)
        draw.pieslice((130, -115, 980, 180), 4, 178, fill=RED)
        draw.pieslice((160, -80, 980, 155), 4, 178, fill=YELLOW)
        draw.regular_polygon((650, 43, 14), 5, rotation=-18, fill=YELLOW)


def _draw_front(member, dues, verification_url):
    image = Image.new("RGB", (CARD_WIDTH, CARD_HEIGHT), "#ffffff")
    draw = ImageDraw.Draw(image)
    _draw_background(draw, "front")

    logo = _open_logo(250)
    if logo:
        image.paste(logo, (78, 72), logo)
        watermark = logo.resize((360, 360), Image.LANCZOS)
        watermark.putalpha(28)
        image.paste(watermark, (432, 266), watermark)

    _text(draw, (452, 76), "MEMBERSHIP CARD", 24, GOLD, bold=True)
    _text(draw, (438, 132), "ASCAI", 70, GREEN, bold=True)
    _text(draw, (545, 132), "SC", 70, RED, bold=True)
    _text(draw, (661, 132), "AI", 70, YELLOW, bold=True)
    _text(draw, (439, 205), "General Community", 43, GOLD, italic=True)
    _text(draw, (440, 248), "Associazione Studenti Camerunesi del Lazio", 19, INK, bold=True)

    avatar = _member_avatar(member, 188)
    _rounded_paste(image, avatar, (772, 118), radius=20)
    qr = _qr_image(verification_url, 126)
    _rounded_paste(image, qr, (803, 382), radius=10, border=GOLD, border_width=3)

    full_name = member.user.get_display_name()
    role = "Member" if member.member_type != "sympathizer" else "Sympathizer"
    nationality = "Cameroonian"
    card_id = f"ASC-{dues.year}-{member.pk:03d}"
    issued = dues.payment_date or timezone.now().date()
    expires = dues.valid_until or dues.due_date.replace(month=12, day=31)

    rows = [
        ("Name:", full_name),
        ("Member ID:", card_id),
        ("Role:", role),
        ("Nationality:", nationality),
        ("Issued:", issued.strftime("%m/%Y")),
        ("Expires:", expires.strftime("%m/%Y")),
    ]
    y = 302
    for label, value in rows:
        _text(draw, (438, y), label, 20, GOLD, bold=True)
        font = _fit_text(draw, value, 300, 23, bold=True)
        draw.text((555, y - 2), str(value), font=font, fill=INK)
        y += 37

    sig_font = _fit_text(draw, full_name, 210, 28, italic=True, min_size=18)
    draw.text((448, 554), full_name, font=sig_font, fill=INK)
    draw.line((438, 587, 630, 587), fill=GOLD, width=2)
    _text(draw, (465, 596), "Cardholder Signature", 16, INK)
    _text(draw, (742, 548), "ASCAI", 32, INK, italic=True)
    draw.line((700, 587, 895, 587), fill=GOLD, width=2)
    _text(draw, (716, 596), "Authorized Signature", 16, INK)
    _text(draw, (716, 615), "ASCAI Executive Board", 15, INK)
    return image


def _draw_back(dues, verification_url):
    image = Image.new("RGB", (CARD_WIDTH, CARD_HEIGHT), "#ffffff")
    draw = ImageDraw.Draw(image)
    _draw_background(draw, "back")

    logo = _open_logo(240)
    if logo:
        image.paste(logo, (82, 92), logo)
        watermark = logo.resize((410, 410), Image.LANCZOS)
        watermark.putalpha(24)
        image.paste(watermark, (600, 165), watermark)

    draw.rounded_rectangle((560, 86, 760, 124), radius=18, fill=GREEN)
    _text(draw, (660, 105), "CARD BENEFITS", 23, YELLOW, bold=True, anchor="mm")

    benefits = [
        "Access to ASCAI events and programs",
        "Participation in meetings and workshops",
        "Networking opportunities with members",
        "Community support and cultural activities",
        "Academic and career development resources",
    ]
    y = 165
    for item in benefits:
        draw.ellipse((526, y - 18, 570, y + 26), fill=GOLD)
        _text(draw, (548, y + 2), "✓", 23, "white", bold=True, anchor="mm")
        _text(draw, (598, y - 4), item, 20, INK)
        y += 58

    draw.line((18, 428, CARD_WIDTH - 18, 428), fill=GOLD, width=2)
    _text(draw, (72, 463), "CONTACT US", 22, GREEN, bold=True)
    contact = [
        "Via dei Laterani, 10 - 00184 Roma, Italia",
        "info@ascai.it",
        "+39 351 123 4567",
        "www.ascai.it",
        "@ascai.lazio",
    ]
    y = 505
    for item in contact:
        _text(draw, (72, y), item, 17, INK)
        y += 25

    draw.line((692, 468, 692, 590), fill=GOLD, width=2)
    qr = _qr_image(verification_url, 115)
    _rounded_paste(image, qr, (720, 476), radius=10, border=GOLD, border_width=3)
    draw.rounded_rectangle((855, 475, 984, 588), radius=12, fill=GREEN)
    _text(draw, (871, 494), "This card remains", 18, "white", bold=True)
    _text(draw, (871, 518), "the property of ASCAI.", 18, "white", bold=True)
    _text(draw, (871, 544), "If found, return", 17, "white")
    _text(draw, (871, 566), "to the address above.", 17, "white")
    _text(draw, (720, 615), "EMERGENCY CONTACT / VERIFICATION", 18, GOLD, bold=True)
    _text(draw, (720, 637 - 34), "+39 350 987 6543  |  verify@ascai.it", 19, INK, bold=True)
    return image


def generate_membership_card_pdf(dues, request):
    verification_url = request.build_absolute_uri(
        reverse("dashboard:membership_card_pdf", kwargs={"dues_id": dues.pk})
    )
    front = _draw_front(dues.member, dues, verification_url)
    back = _draw_back(dues, verification_url)
    output = BytesIO()
    front.save(output, format="PDF", save_all=True, append_images=[back], resolution=300.0)
    output.seek(0)
    return output
