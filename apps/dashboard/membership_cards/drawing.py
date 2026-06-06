"""
Reusable ReportLab drawing components for ASCAI membership cards.
"""
from __future__ import annotations

from math import sin, cos, pi

from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth

from .assets import load_logo_reader, load_photo_reader, make_qr_reader


CARD_W = 85.6 * mm
CARD_H = 54 * mm

GREEN = colors.HexColor("#007A3D")
RED = colors.HexColor("#CE1126")
YELLOW = colors.HexColor("#FCD116")
GOLD = colors.HexColor("#B68A2C")
WHITE = colors.HexColor("#FFFFFF")
DARK = colors.HexColor("#222222")
MUTED = colors.HexColor("#6A5A42")
PAPER = colors.HexColor("#FCFAF4")
PALE_GOLD = colors.HexColor("#E8D9B8")


def _fit_text(canvas, text, x, y, max_width, font="Helvetica-Bold", size=7.4, color=DARK):
    current = size
    while current > 4.5 and stringWidth(str(text), font, current) > max_width:
        current -= 0.25
    canvas.setFillColor(color)
    canvas.setFont(font, current)
    canvas.drawString(x, y, str(text))


def _center_text(canvas, text, x, y, width, font="Helvetica-Bold", size=8, color=DARK):
    canvas.setFillColor(color)
    canvas.setFont(font, size)
    canvas.drawCentredString(x + width / 2, y, str(text))


def _star_path(canvas, cx, cy, radius):
    points = []
    for i in range(10):
        angle = -pi / 2 + i * pi / 5
        r = radius if i % 2 == 0 else radius * 0.42
        points.append((cx + cos(angle) * r, cy + sin(angle) * r))
    path = canvas.beginPath()
    path.moveTo(*points[0])
    for point in points[1:]:
        path.lineTo(*point)
    path.close()
    return path


def _draw_security_pattern(canvas, x, y, w, h):
    canvas.saveState()
    canvas.setStrokeColor(PALE_GOLD)
    canvas.setLineWidth(0.18)
    for offset in range(-80, 140, 8):
        canvas.line(x + offset * mm / 4, y, x + offset * mm / 4 + h * 0.9, y + h)
    for offset in range(-30, 170, 9):
        canvas.line(x + offset * mm / 4, y + h, x + offset * mm / 4 + h * 0.75, y)
    canvas.setStrokeColor(colors.HexColor("#F1E7CD"))
    for ix in range(7, 84, 9):
        for iy in range(7, 53, 9):
            canvas.circle(x + ix * mm, y + iy * mm, 0.9 * mm, stroke=1, fill=0)
    canvas.restoreState()


def _draw_colosseum_watermark(canvas, x, y, w):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#DDD2BD"))
    canvas.setFillColor(colors.HexColor("#DDD2BD"))
    canvas.setLineWidth(0.55)
    h = w * 0.35
    canvas.arc(x, y, x + w, y + h * 1.6, 3, 176)
    canvas.line(x + 2 * mm, y + h * 0.24, x + w - 2 * mm, y + h * 0.24)
    columns = 8
    gap = w / columns
    for index in range(columns):
        cx = x + gap * index + gap * 0.5
        canvas.roundRect(cx - gap * 0.24, y + h * 0.45, gap * 0.48, h * 0.42, 1.4 * mm, stroke=1, fill=0)
        canvas.line(cx - gap * 0.32, y + h * 0.34, cx + gap * 0.32, y + h * 0.34)
    canvas.restoreState()


def _draw_card_shell(canvas, x, y):
    canvas.saveState()
    canvas.setFillColor(PAPER)
    canvas.setStrokeColor(colors.HexColor("#D8CDBB"))
    canvas.setLineWidth(0.55)
    canvas.roundRect(x, y, CARD_W, CARD_H, 3.2 * mm, stroke=1, fill=1)
    _draw_security_pattern(canvas, x, y, CARD_W, CARD_H)
    canvas.restoreState()


def _draw_logo(canvas, x, y, w, h, logo_reader, compact=False):
    canvas.saveState()
    canvas.setStrokeColor(GOLD)
    canvas.setLineWidth(0.55)
    canvas.setFillColor(WHITE)
    canvas.roundRect(x, y, w, h, 2.5 * mm, stroke=1, fill=1)
    if logo_reader:
        canvas.drawImage(logo_reader, x + w * 0.18, y + h * 0.28, w * 0.64, h * 0.42, preserveAspectRatio=True, mask="auto")
    else:
        canvas.setFont("Helvetica-Bold", 5.5)
        canvas.setFillColor(RED)
        canvas.drawCentredString(x + w / 2, y + h * 0.52, "ADD OFFICIAL")
        canvas.drawCentredString(x + w / 2, y + h * 0.37, "ASCAI LOGO")
    canvas.setFont("Helvetica-Bold", 8 if compact else 10)
    letters = [("A", GREEN), ("S", RED), ("C", RED), ("A", YELLOW), ("I", YELLOW)]
    total = sum(stringWidth(l, "Helvetica-Bold", 8 if compact else 10) for l, _ in letters) + (len(letters) - 1) * 0.45 * mm
    start = x + (w - total) / 2
    for letter, color in letters:
        canvas.setFillColor(color)
        canvas.drawString(start, y + h - (5.3 if compact else 6.3) * mm, letter)
        start += stringWidth(letter, "Helvetica-Bold", 8 if compact else 10) + 0.45 * mm
    if not compact:
        canvas.setFillColor(colors.HexColor("#FFF8E7"))
        canvas.setStrokeColor(GOLD)
        canvas.roundRect(x + 3.5 * mm, y + 2.4 * mm, w - 7 * mm, 5.2 * mm, 1 * mm, stroke=1, fill=1)
        _center_text(canvas, "ASSOCIAZIONE STUDENTI", x + 3.5 * mm, y + 3.9 * mm, w - 7 * mm, size=3.6)
    canvas.restoreState()


def _draw_cameroon_ribbon(canvas, x, y, front=True):
    canvas.saveState()
    if front:
        base_y = y + 1.7 * mm
        canvas.setLineCap(1)
        canvas.setStrokeColor(RED)
        canvas.setLineWidth(5.2 * mm)
        canvas.bezier(x - 4 * mm, base_y - 4 * mm, x + 16 * mm, base_y + 0.3 * mm, x + 38 * mm, base_y + 0.1 * mm, x + 55 * mm, base_y - 4.5 * mm)
        canvas.setStrokeColor(GREEN)
        canvas.setLineWidth(4 * mm)
        canvas.bezier(x - 4 * mm, base_y - 1.2 * mm, x + 16 * mm, base_y + 2.1 * mm, x + 38 * mm, base_y + 1.6 * mm, x + 55 * mm, base_y - 2.4 * mm)
        canvas.setStrokeColor(YELLOW)
        canvas.setLineWidth(2.6 * mm)
        canvas.bezier(x - 4 * mm, base_y + 1.7 * mm, x + 16 * mm, base_y + 3.5 * mm, x + 38 * mm, base_y + 2.7 * mm, x + 55 * mm, base_y + 0.2 * mm)
        canvas.setFillColor(YELLOW)
        canvas.drawPath(_star_path(canvas, x + 15 * mm, y + 3.5 * mm, 1.5 * mm), stroke=0, fill=1)
    else:
        canvas.setStrokeColor(GREEN)
        canvas.setLineWidth(8 * mm)
        canvas.bezier(x - 5 * mm, y + CARD_H - 6 * mm, x + 18 * mm, y + CARD_H - 2 * mm, x + 32 * mm, y + CARD_H - 5 * mm, x + 45 * mm, y + CARD_H + 4 * mm)
        canvas.setStrokeColor(RED)
        canvas.setLineWidth(5.5 * mm)
        canvas.bezier(x + 18 * mm, y + CARD_H + 3 * mm, x + 40 * mm, y + CARD_H - 1 * mm, x + 62 * mm, y + CARD_H - 2 * mm, x + CARD_W + 4 * mm, y + CARD_H + 1 * mm)
        canvas.setStrokeColor(YELLOW)
        canvas.setLineWidth(3.4 * mm)
        canvas.bezier(x + 24 * mm, y + CARD_H - 1.4 * mm, x + 42 * mm, y + CARD_H - 3 * mm, x + 64 * mm, y + CARD_H - 3.4 * mm, x + CARD_W + 4 * mm, y + CARD_H - 0.4 * mm)
    canvas.restoreState()


def _draw_photo(canvas, card_data, x, y):
    initials = "".join(part[:1] for part in card_data.fullName.split()[:2]).upper() or "A"
    reader = load_photo_reader(card_data.photoField, initials)
    size = 17.8 * mm
    canvas.saveState()
    canvas.setFillColor(WHITE)
    canvas.setStrokeColor(GOLD)
    canvas.roundRect(x, y, size, size, 2 * mm, stroke=1, fill=1)
    canvas.drawImage(reader, x + 0.8 * mm, y + 0.8 * mm, size - 1.6 * mm, size - 1.6 * mm, preserveAspectRatio=True, mask="auto")
    canvas.restoreState()


def _draw_qr(canvas, card_data, x, y, size):
    reader = make_qr_reader(card_data.qrCodeData)
    canvas.saveState()
    canvas.setFillColor(WHITE)
    canvas.setStrokeColor(GOLD)
    canvas.roundRect(x, y, size, size, 1.1 * mm, stroke=1, fill=1)
    canvas.drawImage(reader, x + 1 * mm, y + 1 * mm, size - 2 * mm, size - 2 * mm, mask="auto")
    canvas.restoreState()


def draw_membership_card_front(canvas, x, y, card_data, logo_reader=None):
    logo_reader = logo_reader if logo_reader is not None else load_logo_reader()
    _draw_card_shell(canvas, x, y)
    _draw_colosseum_watermark(canvas, x + 34 * mm, y + 9.5 * mm, 38 * mm)
    _draw_cameroon_ribbon(canvas, x, y, front=True)

    _draw_logo(canvas, x + 5.5 * mm, y + 22.2 * mm, 25.5 * mm, 24.2 * mm, logo_reader)
    _draw_photo(canvas, card_data, x + 68 * mm, y + 28.5 * mm)
    _draw_qr(canvas, card_data, x + 70.4 * mm, y + 10.7 * mm, 14.5 * mm)

    canvas.setFillColor(GOLD)
    canvas.setFont("Helvetica-Bold", 6.8)
    canvas.drawString(x + 35.2 * mm, y + 46 * mm, "MEMBERSHIP CARD")
    canvas.setFont("Helvetica-Bold", 20)
    letters = [("A", GREEN), ("S", RED), ("C", RED), ("A", YELLOW), ("I", YELLOW)]
    cursor = x + 35 * mm
    for letter, color in letters:
        canvas.setFillColor(color)
        canvas.drawString(cursor, y + 36.5 * mm, letter)
        cursor += stringWidth(letter, "Helvetica-Bold", 20) + 0.6 * mm

    _fit_text(canvas, card_data.community, x + 35.3 * mm, y + 32.3 * mm, 29 * mm, font="Helvetica-Oblique", size=9.2, color=GOLD)
    canvas.setFillColor(DARK)
    canvas.setFont("Helvetica-Bold", 4.8)
    canvas.drawString(x + 35.3 * mm, y + 29.6 * mm, card_data.legalName)
    canvas.setStrokeColor(GOLD)
    canvas.line(x + 35.3 * mm, y + 28.7 * mm, x + 65.6 * mm, y + 28.7 * mm)

    rows = [
        ("Name:", card_data.fullName),
        ("Member ID:", card_data.memberId),
        ("Role:", card_data.role),
        ("Nationality:", card_data.nationality),
        ("Issued:", card_data.issuedDate),
        ("Expires:", card_data.expiryDate),
    ]
    row_y = y + 25.7 * mm
    for label, value in rows:
        canvas.setFillColor(GOLD)
        canvas.setFont("Helvetica-Bold", 5.2)
        canvas.drawString(x + 35.3 * mm, row_y, label)
        _fit_text(canvas, value, x + 46.5 * mm, row_y, 21 * mm, size=6.3)
        row_y -= 3.0 * mm

    canvas.setStrokeColor(GOLD)
    canvas.setFillColor(DARK)
    canvas.setFont("Helvetica-Oblique", 7)
    canvas.drawString(x + 35.2 * mm, y + 6.9 * mm, card_data.fullName)
    canvas.line(x + 35 * mm, y + 5.7 * mm, x + 53.6 * mm, y + 5.7 * mm)
    _center_text(canvas, "Cardholder Signature", x + 35 * mm, y + 4.3 * mm, 18.6 * mm, font="Helvetica", size=3.2)
    canvas.setFont("Helvetica-Oblique", 7)
    canvas.drawString(x + 60 * mm, y + 6.9 * mm, "ASCAI")
    canvas.line(x + 59.5 * mm, y + 5.7 * mm, x + 80.5 * mm, y + 5.7 * mm)
    _center_text(canvas, "Authorized Signature", x + 59.5 * mm, y + 4.3 * mm, 21 * mm, font="Helvetica", size=3.2)
    _center_text(canvas, "ASCAI Executive Board", x + 59.5 * mm, y + 3.1 * mm, 21 * mm, font="Helvetica", size=2.9)


def _benefit_icon(canvas, cx, cy, index):
    canvas.setFillColor(GOLD)
    canvas.circle(cx, cy, 2.4 * mm, stroke=0, fill=1)
    canvas.setFillColor(WHITE)
    canvas.setStrokeColor(WHITE)
    canvas.setLineWidth(0.45)
    if index == 0:
        canvas.circle(cx - 0.9 * mm, cy + 0.7 * mm, 0.45 * mm, stroke=0, fill=1)
        canvas.circle(cx + 0.9 * mm, cy + 0.7 * mm, 0.45 * mm, stroke=0, fill=1)
        canvas.roundRect(cx - 1.7 * mm, cy - 1.3 * mm, 3.4 * mm, 1.2 * mm, 0.4 * mm, stroke=0, fill=1)
    elif index == 1:
        canvas.roundRect(cx - 1.25 * mm, cy - 1.25 * mm, 2.5 * mm, 2.5 * mm, 0.25 * mm, stroke=1, fill=0)
        canvas.line(cx - 1.25 * mm, cy + 0.45 * mm, cx + 1.25 * mm, cy + 0.45 * mm)
    elif index == 2:
        for angle in (0, 120, 240):
            rad = angle * pi / 180
            canvas.line(cx, cy, cx + cos(rad) * 1.55 * mm, cy + sin(rad) * 1.55 * mm)
        canvas.circle(cx, cy, 0.35 * mm, stroke=0, fill=1)
    elif index == 3:
        canvas.arc(cx - 1.4 * mm, cy - 1.2 * mm, cx + 1.4 * mm, cy + 1.4 * mm, 25, 205)
        canvas.circle(cx - 1.45 * mm, cy - 0.45 * mm, 0.35 * mm, stroke=0, fill=1)
        canvas.circle(cx + 1.45 * mm, cy - 0.45 * mm, 0.35 * mm, stroke=0, fill=1)
    else:
        path = canvas.beginPath()
        path.moveTo(cx, cy + 1.5 * mm)
        path.lineTo(cx + 1.7 * mm, cy)
        path.lineTo(cx, cy - 1.5 * mm)
        path.lineTo(cx - 1.7 * mm, cy)
        path.close()
        canvas.drawPath(path, stroke=0, fill=1)


def draw_membership_card_back(canvas, x, y, card_data, logo_reader=None):
    logo_reader = logo_reader if logo_reader is not None else load_logo_reader()
    _draw_card_shell(canvas, x, y)
    _draw_cameroon_ribbon(canvas, x, y, front=False)
    _draw_colosseum_watermark(canvas, x + 52 * mm, y + 20 * mm, 39 * mm)

    _draw_logo(canvas, x + 7 * mm, y + 31 * mm, 20 * mm, 15 * mm, logo_reader, compact=True)
    canvas.setFillColor(GREEN)
    canvas.roundRect(x + 47 * mm, y + 43.4 * mm, 21 * mm, 4.9 * mm, 2.1 * mm, stroke=0, fill=1)
    _center_text(canvas, "CARD BENEFITS", x + 47 * mm, y + 44.7 * mm, 21 * mm, size=5.2, color=YELLOW)

    benefits = [
        "Access to ASCAI events and programs",
        "Participation in meetings and workshops",
        "Networking opportunities with members",
        "Community support and cultural activities",
        "Academic and career development resources",
    ]
    benefit_y = y + 38.8 * mm
    for index, benefit in enumerate(benefits):
        _benefit_icon(canvas, x + 46.5 * mm, benefit_y + 0.8 * mm, index)
        _fit_text(canvas, benefit, x + 51.4 * mm, benefit_y, 30.5 * mm, font="Helvetica", size=4.6)
        benefit_y -= 5.2 * mm

    canvas.setStrokeColor(GOLD)
    canvas.line(x, y + 14.4 * mm, x + CARD_W, y + 14.4 * mm)
    canvas.setFillColor(GOLD)
    canvas.rect(x, y, CARD_W, 4.6 * mm, stroke=0, fill=1)
    canvas.setStrokeColor(colors.HexColor("#C69A3B"))
    for ix in range(1, 86, 4):
        canvas.line(x + ix * mm, y + 0.8 * mm, x + (ix + 2) * mm, y + 4 * mm)
        canvas.line(x + (ix + 2) * mm, y + 0.8 * mm, x + ix * mm, y + 4 * mm)

    canvas.setFillColor(GREEN)
    canvas.setFont("Helvetica-Bold", 5.5)
    canvas.drawString(x + 5.8 * mm, y + 10.8 * mm, "CONTACT US")
    contact_rows = [
        f"Address: {card_data.address}",
        f"Email: {card_data.email}",
        f"Phone: {card_data.phone}",
        f"Website: {card_data.website}",
        f"Social: {card_data.social}",
    ]
    contact_y = y + 8.8 * mm
    for row in contact_rows:
        _fit_text(canvas, row, x + 5.8 * mm, contact_y, 44 * mm, font="Helvetica", size=3.6)
        contact_y -= 1.95 * mm

    canvas.setStrokeColor(GOLD)
    canvas.line(x + 56.2 * mm, y + 4.6 * mm, x + 56.2 * mm, y + 13.4 * mm)
    _draw_qr(canvas, card_data, x + 59 * mm, y + 5.1 * mm, 12 * mm)
    canvas.setFillColor(GREEN)
    canvas.roundRect(x + 72.2 * mm, y + 5.1 * mm, 11.8 * mm, 12 * mm, 1.1 * mm, stroke=0, fill=1)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 3.2)
    canvas.drawString(x + 73.1 * mm, y + 13.3 * mm, "This card remains")
    canvas.drawString(x + 73.1 * mm, y + 11.7 * mm, "the property of ASCAI.")
    canvas.setFont("Helvetica", 3)
    canvas.drawString(x + 73.1 * mm, y + 9.4 * mm, "If found, please return")
    canvas.drawString(x + 73.1 * mm, y + 7.9 * mm, "to the address above.")
    canvas.setFillColor(DARK)
    _fit_text(canvas, f"Verification: {card_data.verificationEmail}", x + 59 * mm, y + 2.8 * mm, 25 * mm, font="Helvetica-Bold", size=3.4)
