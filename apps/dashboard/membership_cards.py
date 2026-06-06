"""
Membership card PDF generation for paid ASCAI dues.

The PDF is rendered with Pillow so production does not depend on a browser
binary. The design intentionally follows the attached ASCAI reference: two
card faces, rounded print-card proportions, Cameroon color bands, logo/photo/QR
blocks, benefits, contact information, and validity details.
"""
from __future__ import annotations

from io import BytesIO
from pathlib import Path

import qrcode
from django.contrib.staticfiles import finders
from django.urls import reverse
from django.utils import timezone
from PIL import Image, ImageDraw, ImageFont, ImageOps


SCALE = 2
CARD_WIDTH = 1011
CARD_HEIGHT = 638
W = CARD_WIDTH * SCALE
H = CARD_HEIGHT * SCALE

GREEN = "#0b6f4f"
DEEP_GREEN = "#063d30"
RED = "#d71925"
YELLOW = "#f4c430"
GOLD = "#b47a12"
DARK_GOLD = "#8d5d08"
INK = "#151515"
MUTED = "#6d5b43"
PAPER = "#fbf8ef"
PAPER_2 = "#f4edde"
LINE = "#d8c8aa"


def _s(value):
    return int(round(value * SCALE))


def _box(box):
    return tuple(_s(v) for v in box)


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
            return ImageFont.truetype(candidate, size=_s(size))
    return ImageFont.load_default()


def _text(draw, xy, text, size, fill=INK, bold=False, italic=False, anchor=None):
    draw.text((_s(xy[0]), _s(xy[1])), str(text), font=_font(size, bold=bold, italic=italic), fill=fill, anchor=anchor)


def _text_width(draw, text, font):
    left, _, right, _ = draw.textbbox((0, 0), str(text), font=font)
    return right - left


def _fit_font(draw, text, max_width, start_size, bold=False, italic=False, min_size=12):
    size = start_size
    while size > min_size:
        font = _font(size, bold=bold, italic=italic)
        if _text_width(draw, text, font) <= _s(max_width):
            return font
        size -= 1
    return _font(min_size, bold=bold, italic=italic)


def _draw_centered(draw, box, text, size, fill=INK, bold=False):
    x1, y1, x2, y2 = box
    draw.text((_s((x1 + x2) / 2), _s((y1 + y2) / 2)), str(text), font=_font(size, bold=bold), fill=fill, anchor="mm")


def _open_logo(size):
    logo_path = finders.find("images/apple-touch-icon.png") or finders.find("images/web-app-manifest-512x512.png")
    if not logo_path:
        return None
    logo = Image.open(logo_path).convert("RGBA")
    pixels = logo.load()
    xs = []
    ys = []
    for y in range(logo.height):
        for x in range(logo.width):
            r, g, b, a = pixels[x, y]
            if a and not (r > 245 and g > 245 and b > 245):
                xs.append(x)
                ys.append(y)
    if xs and ys:
        bbox = (min(xs), min(ys), max(xs) + 1, max(ys) + 1)
        logo = logo.crop(bbox)
    logo.thumbnail((_s(size), _s(size)), Image.LANCZOS)
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
        image = Image.new("RGB", (_s(size), _s(size)), "#e7efe9")
        draw = ImageDraw.Draw(image)
        initials = "".join(part[:1] for part in member.user.get_display_name().split()[:2]).upper() or "A"
        draw.text((_s(size / 2), _s(size / 2)), initials, fill=GREEN, font=_font(64, bold=True), anchor="mm")
    else:
        image = ImageOps.fit(image, (_s(size), _s(size)), Image.LANCZOS)

    return image


def _qr_image(data, size):
    qr = qrcode.QRCode(box_size=12, border=1)
    qr.add_data(data)
    qr.make(fit=True)
    image = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    return image.resize((_s(size), _s(size)), Image.Resampling.NEAREST)


def _paste_rounded(base, image, xy, radius, border=GOLD, border_width=3, fill=None):
    x, y = xy
    w, h = image.size
    if fill:
        ImageDraw.Draw(base).rounded_rectangle(_box((x, y, x + w / SCALE, y + h / SCALE)), radius=_s(radius), fill=fill)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w, h), radius=_s(radius), fill=255)
    base.paste(image, (_s(x), _s(y)), mask)
    ImageDraw.Draw(base).rounded_rectangle(
        _box((x, y, x + w / SCALE, y + h / SCALE)),
        radius=_s(radius),
        outline=border,
        width=_s(border_width),
    )


def _draw_security_pattern(draw):
    for offset in range(-CARD_HEIGHT, CARD_WIDTH + CARD_HEIGHT, 38):
        draw.line(_box((offset, 30, offset + 420, CARD_HEIGHT - 30)), fill="#efe5d2", width=_s(1))
    for offset in range(0, CARD_WIDTH + CARD_HEIGHT, 46):
        draw.line(_box((offset, 32, offset - 390, CARD_HEIGHT - 28)), fill="#f7efe1", width=_s(1))
    for x in range(52, CARD_WIDTH - 50, 52):
        for y in range(55, CARD_HEIGHT - 45, 52):
            draw.ellipse(_box((x - 7, y - 7, x + 7, y + 7)), outline="#f0e4cf", width=_s(1))


def _draw_colosseum_watermark(draw, x, y, width, alpha_color="#e2d6c2"):
    height = width * 0.38
    draw.arc(_box((x, y, x + width, y + height * 1.3)), 183, 358, fill=alpha_color, width=_s(5))
    draw.line(_box((x + 10, y + height, x + width - 10, y + height)), fill=alpha_color, width=_s(4))
    column_count = 9
    gap = width / column_count
    for i in range(column_count):
        cx = x + i * gap + gap * 0.5
        draw.rounded_rectangle(_box((cx - gap * 0.26, y + height * 0.38, cx + gap * 0.26, y + height * 0.82)), radius=_s(8), outline=alpha_color, width=_s(3))
        draw.line(_box((cx - gap * 0.34, y + height * 0.9, cx + gap * 0.34, y + height * 0.9)), fill=alpha_color, width=_s(3))


def _star(draw, center, radius, fill):
    draw.regular_polygon((_s(center[0]), _s(center[1]), _s(radius)), 5, rotation=-18, fill=fill)


def _draw_shell(draw):
    draw.rounded_rectangle(_box((18, 18, CARD_WIDTH - 18, CARD_HEIGHT - 18)), radius=_s(34), fill=PAPER, outline="#d4cec1", width=_s(2))
    draw.rounded_rectangle(_box((24, 24, CARD_WIDTH - 24, CARD_HEIGHT - 24)), radius=_s(28), outline="#ffffff", width=_s(2))
    _draw_security_pattern(draw)


def _draw_front_ribbons(draw):
    draw.line([(_s(-32), _s(535)), (_s(70), _s(570)), (_s(185), _s(604)), (_s(330), _s(657))], fill=RED, width=_s(72), joint="curve")
    draw.line([(_s(-28), _s(507)), (_s(82), _s(546)), (_s(204), _s(588)), (_s(350), _s(642))], fill=GREEN, width=_s(54), joint="curve")
    draw.line([(_s(-22), _s(477)), (_s(100), _s(517)), (_s(230), _s(555)), (_s(373), _s(604))], fill=YELLOW, width=_s(34), joint="curve")
    draw.line([(_s(-12), _s(450)), (_s(120), _s(488)), (_s(257), _s(526)), (_s(392), _s(567))], fill=PAPER, width=_s(24), joint="curve")
    draw.line([(_s(-20), _s(496)), (_s(94), _s(535)), (_s(218), _s(575)), (_s(360), _s(628))], fill=DARK_GOLD, width=_s(4), joint="curve")
    _star(draw, (170, 557), 21, YELLOW)


def _draw_back_ribbons(draw):
    draw.line([(_s(-25), _s(36)), (_s(120), _s(58)), (_s(300), _s(34)), (_s(465), _s(-24))], fill=GREEN, width=_s(92), joint="curve")
    draw.line([(_s(230), _s(0)), (_s(470), _s(25)), (_s(720), _s(25)), (_s(1040), _s(-8))], fill=RED, width=_s(54), joint="curve")
    draw.line([(_s(292), _s(24)), (_s(518), _s(47)), (_s(760), _s(44)), (_s(1040), _s(14))], fill=YELLOW, width=_s(34), joint="curve")
    draw.line([(_s(270), _s(42)), (_s(515), _s(65)), (_s(760), _s(62)), (_s(1030), _s(34))], fill=DARK_GOLD, width=_s(4), joint="curve")
    draw.rectangle(_box((18, 604, CARD_WIDTH - 18, CARD_HEIGHT - 18)), fill=GOLD)
    for x in range(30, CARD_WIDTH - 20, 34):
        draw.line(_box((x, 610, x + 24, 634)), fill="#c9972d", width=_s(3))
        draw.line(_box((x + 24, 610, x, 634)), fill="#a66d0b", width=_s(2))
    _star(draw, (642, 43), 13, YELLOW)


def _draw_wordmark(draw, x, y):
    letters = [("A", GREEN), ("S", RED), ("C", RED), ("A", YELLOW), ("I", YELLOW)]
    current = _s(x)
    for letter, color in letters:
        font = _font(72, bold=True)
        draw.text((current, _s(y)), letter, font=font, fill=color)
        current += _text_width(draw, letter, font) + _s(7)


def _draw_logo_block(image, x, y, size, with_ring=True):
    draw = ImageDraw.Draw(image)
    logo = _open_logo(size)
    if with_ring:
        draw.ellipse(_box((x - 10, y - 10, x + size + 10, y + size + 10)), fill="#fffdf8", outline=GOLD, width=_s(4))
        letters = [("A", GREEN), ("S", RED), ("C", RED), ("A", YELLOW), ("I", YELLOW)]
        current = _s(x + 47)
        for letter, color in letters:
            font = _font(33, bold=True)
            draw.text((current, _s(y + 28)), letter, font=font, fill=color)
            current += _text_width(draw, letter, font) + _s(2)
        if logo:
            logo_copy = logo.copy()
            logo_copy.thumbnail((_s(size * 0.72), _s(size * 0.54)), Image.LANCZOS)
            lx = x + (size - logo_copy.size[0] / SCALE) / 2
            ly = y + 83
            image.paste(logo_copy, (_s(lx), _s(ly)), logo_copy)
        else:
            _draw_centered(draw, (x, y + 78, x + size, y + 155), "ASCAI", 34, GREEN, bold=True)
        draw.rounded_rectangle(_box((x + 38, y + size - 54, x + size - 38, y + size - 18)), radius=_s(9), fill="#f8f1df", outline=GOLD, width=_s(2))
        _draw_centered(draw, (x + 40, y + size - 51, x + size - 40, y + size - 20), "ASSOCIAZIONE STUDENTI", 10, INK, bold=True)
    else:
        if logo:
            logo_copy = logo.copy()
            logo_copy.thumbnail((_s(size * 0.88), _s(size * 0.62)), Image.LANCZOS)
            lx = x + (size - logo_copy.size[0] / SCALE) / 2
            ly = y + (size - logo_copy.size[1] / SCALE) / 2
            image.paste(logo_copy, (_s(lx), _s(ly)), logo_copy)
        _text(draw, (x + 44, y + 20), "ASCAI", 30, GREEN, bold=True)


def _draw_small_icon(draw, center, kind):
    x, y = center
    draw.ellipse(_box((x - 22, y - 22, x + 22, y + 22)), fill=GOLD)
    if kind == "people":
        draw.ellipse(_box((x - 11, y - 10, x - 3, y - 2)), fill="white")
        draw.ellipse(_box((x + 3, y - 10, x + 11, y - 2)), fill="white")
        draw.rounded_rectangle(_box((x - 15, y + 2, x + 15, y + 13)), radius=_s(5), fill="white")
    elif kind == "calendar":
        draw.rounded_rectangle(_box((x - 12, y - 12, x + 12, y + 13)), radius=_s(3), outline="white", width=_s(3))
        draw.line(_box((x - 12, y - 5, x + 12, y - 5)), fill="white", width=_s(3))
    elif kind == "network":
        points = [(x - 10, y - 8), (x + 10, y - 8), (x, y + 11)]
        for a, b in [(0, 1), (1, 2), (2, 0)]:
            draw.line(_box((*points[a], *points[b])), fill="white", width=_s(3))
        for px, py in points:
            draw.ellipse(_box((px - 5, py - 5, px + 5, py + 5)), fill="white")
    elif kind == "support":
        draw.arc(_box((x - 13, y - 12, x + 13, y + 16)), 205, 520, fill="white", width=_s(4))
        draw.ellipse(_box((x - 13, y + 4, x - 6, y + 12)), fill="white")
        draw.ellipse(_box((x + 6, y + 4, x + 13, y + 12)), fill="white")
    else:
        draw.polygon([(_s(x - 15), _s(y - 2)), (_s(x), _s(y - 13)), (_s(x + 15), _s(y - 2)), (_s(x), _s(y + 13))], fill="white")
        draw.line(_box((x - 9, y + 3, x + 9, y + 3)), fill=GOLD, width=_s(2))


def _draw_shield(draw, box):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(_box((x1, y1, x2, y2)), radius=_s(11), fill=GREEN, outline="#1b8a63", width=_s(2))
    cx = (x1 + x2) / 2
    shield = [
        (_s(cx), _s(y1 + 16)),
        (_s(x2 - 25), _s(y1 + 27)),
        (_s(x2 - 31), _s(y2 - 31)),
        (_s(cx), _s(y2 - 15)),
        (_s(x1 + 25), _s(y2 - 31)),
        (_s(x1 + 31), _s(y1 + 27)),
    ]
    draw.polygon(shield, fill="#f7fbf8", outline=GOLD)
    draw.line(_box((cx - 14, y1 + 52, cx - 2, y1 + 65)), fill=GREEN, width=_s(5))
    draw.line(_box((cx - 2, y1 + 65, cx + 18, y1 + 41)), fill=GREEN, width=_s(5))


def _downsample(image):
    return image.resize((CARD_WIDTH, CARD_HEIGHT), Image.LANCZOS).convert("RGB")


def _draw_front(member, dues, verification_url):
    image = Image.new("RGB", (W, H), "#ffffff")
    draw = ImageDraw.Draw(image)
    _draw_shell(draw)
    _draw_front_ribbons(draw)
    _draw_colosseum_watermark(draw, 385, 334, 425, "#e5ddd0")

    _draw_logo_block(image, 78, 78, 245)

    _text(draw, (440, 72), "MEMBERSHIP CARD", 23, GOLD, bold=True)
    _draw_wordmark(draw, 438, 118)
    community_font = _fit_font(draw, "General Community", 310, 36, italic=True, min_size=26)
    draw.text((_s(440), _s(203)), "General Community", font=community_font, fill=GOLD)
    subtitle = "Associazione Studenti Camerunesi del Lazio"
    subtitle_font = _fit_font(draw, subtitle, 326, 17, bold=True, min_size=12)
    draw.text((_s(440), _s(247)), subtitle, font=subtitle_font, fill=INK)
    draw.line(_box((438, 272, 750, 272)), fill=GOLD, width=_s(2))

    avatar = _member_avatar(member, 188)
    _paste_rounded(image, avatar, (778, 119), radius=19, border=GOLD, border_width=4, fill="white")
    qr = _qr_image(verification_url, 126)
    _paste_rounded(image, qr, (812, 383), radius=10, border=GOLD, border_width=3, fill="white")

    full_name = member.user.get_display_name()
    role = "Member" if member.member_type != "sympathizer" else "Sympathizer"
    card_id = f"ASC-{dues.year}-{member.pk:03d}"
    issued = dues.payment_date or timezone.now().date()
    expires = dues.valid_until or dues.due_date.replace(month=12, day=31)
    rows = [
        ("Name:", full_name),
        ("Member ID:", card_id),
        ("Role:", role),
        ("Nationality:", "Cameroonian"),
        ("Issued:", issued.strftime("%m/%Y")),
        ("Expires:", expires.strftime("%m/%Y")),
    ]

    y = 314
    for label, value in rows:
        _text(draw, (438, y), label, 19, GOLD, bold=True)
        font = _fit_font(draw, value, 300, 22, bold=True)
        draw.text((_s(558), _s(y - 1)), str(value), font=font, fill=INK)
        y += 36

    sig_font = _fit_font(draw, full_name, 205, 27, italic=True, min_size=15)
    draw.text((_s(438), _s(552)), full_name, font=sig_font, fill=INK)
    draw.line(_box((438, 589, 635, 589)), fill=GOLD, width=_s(2))
    _text(draw, (462, 601), "Cardholder Signature", 14, INK)

    _text(draw, (722, 552), "ASCAI", 28, INK, italic=True)
    draw.line(_box((700, 589, 900, 589)), fill=GOLD, width=_s(2))
    _text(draw, (719, 601), "Authorized Signature", 14, INK)
    _text(draw, (719, 618), "ASCAI Executive Board", 13, INK)
    return _downsample(image)


def _draw_back(dues, verification_url):
    image = Image.new("RGB", (W, H), "#ffffff")
    draw = ImageDraw.Draw(image)
    _draw_shell(draw)
    _draw_back_ribbons(draw)
    _draw_colosseum_watermark(draw, 606, 170, 406, "#e0d4c1")

    _draw_logo_block(image, 84, 88, 190, with_ring=True)

    draw.rounded_rectangle(_box((560, 84, 772, 122)), radius=_s(18), fill=GREEN)
    _draw_centered(draw, (560, 84, 772, 122), "CARD BENEFITS", 20, YELLOW, bold=True)

    benefits = [
        ("people", "Access to ASCAI events and programs"),
        ("calendar", "Participation in meetings and workshops"),
        ("network", "Networking opportunities with members"),
        ("support", "Community support and cultural activities"),
        ("career", "Academic and career development resources"),
    ]
    y = 164
    for icon, item in benefits:
        _draw_small_icon(draw, (538, y), icon)
        _text(draw, (592, y - 10), item, 18, INK)
        y += 59

    draw.line(_box((18, 430, CARD_WIDTH - 18, 430)), fill=GOLD, width=_s(2))
    _text(draw, (70, 464), "CONTACT US", 20, GREEN, bold=True)

    contact = [
        ("pin", "Via dei Laterani, 10 - 00184 Roma, Italia"),
        ("mail", "info@ascai.it"),
        ("phone", "+39 351 123 4567"),
        ("web", "www.ascai.it"),
        ("social", "@ascai.lazio"),
    ]
    y = 490
    for icon, item in contact:
        draw.ellipse(_box((70, y - 5, 81, y + 6)), fill=GOLD)
        _text(draw, (94, y - 10), item, 13, INK)
        y += 16

    draw.line(_box((690, 468, 690, 591)), fill=GOLD, width=_s(2))
    qr = _qr_image(verification_url, 116)
    _paste_rounded(image, qr, (720, 458), radius=10, border=GOLD, border_width=3, fill="white")
    _draw_shield(draw, (858, 458, 982, 575))
    _text(draw, (874, 480), "This card remains", 10, "white", bold=True)
    _text(draw, (874, 498), "ASCAI property.", 10, "white", bold=True)
    _text(draw, (874, 524), "If found, return", 10, "white")
    _text(draw, (874, 542), "to ASCAI Lazio.", 10, "white")

    _text(draw, (720, 586), "EMERGENCY CONTACT / VERIFICATION", 15, DARK_GOLD, bold=True)
    _text(draw, (720, 605), "+39 350 987 6543 | verify@ascai.it", 13, INK, bold=True)
    return _downsample(image)


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
