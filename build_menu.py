#!/usr/bin/env python3
"""TS Farms / Barnyard Grill — first-principles LED menu.

Single 1080x1920 portrait PNG for an HD-M10 LED standee, loaded via the
LedArt mobile app over Wi-Fi.

Standards: see docs/standards/STANDARD_FORMATTING.txt
                   docs/standards/STYLE_MARKETING.txt
                   docs/standards/APPLIED_TO_LED.md

Toggle positions in this build:
  ONE_VOICE          ON          — DejaVu Sans, regular + bold only
  ONE_INK            OFF, strict — black on white. No third color in v1.
  BREATHE            FULL        — 80 px outer margins, generous rhythm
  EARNED_DISTINCTION RELAXED     — reserved for the logo as expressive node
  ONE_EXPRESSIVE_NODE ON         — the TS Farms line-art logo carries
                                   the personality. Everything else is
                                   structure.

Layout (Hook -> Proof -> Action stack per STYLE_MARKETING):

  IDENTITY  (hook)   ~200 px   TS Farms logo, centered. No wordmark —
                               the logo + the food advertise the booth.
  PROMO     (hook)   ~160 px   featured-item zone — image when supplied,
                               THIS WEEK headline otherwise
  MENU      (proof)  ~1160 px  three sections: Breakfast, Burgers, Ala Carte
  ACTION    (action) ~240 px   QR + market info

Run:  python build_menu.py
Out:  output/menu_<date>_portrait.png
"""

from PIL import Image, ImageDraw, ImageFont
import segno
import os
import io
import json


# ============================================================================
# Canvas
# ============================================================================

W, H = 1080, 1920

# Margins (8-px grid)
MARGIN_X = 80
MARGIN_TOP = 80
MARGIN_BOTTOM = 80
CONTENT_W = W - 2 * MARGIN_X  # 920

# Zone heights — sum to (H - MARGIN_TOP - MARGIN_BOTTOM) = 1760.
# Menu is the proof — it earns the largest share. Identity and promo are
# the hook (smaller). Action is the terminal pause.
ZONE_IDENTITY = 200
ZONE_PROMO = 160
ZONE_MENU = 1160
ZONE_ACTION = 240
assert ZONE_IDENTITY + ZONE_PROMO + ZONE_MENU + ZONE_ACTION == H - MARGIN_TOP - MARGIN_BOTTOM

# Padding values — 8-px grid only
PAD_TIGHT = 8
PAD_DEFAULT = 16
PAD_SECTION = 32
PAD_GENEROUS = 64


# ============================================================================
# Type scale — LED-sized, hierarchy ratios from STANDARD's 5-level system.
# The logo is the only Level 1 element (the expressive node). All text
# starts at Level 2. The contrast between levels is the hierarchy signal.
# ============================================================================

T_SECTION = 48    # Level 2 — section banner (uppercase, bold)
T_PROMO = 56      # Level 2 — promo headline (THIS WEEK)
T_ITEM = 40       # Level 3 — item name (bold)
T_BODY = 26       # Level 4 — descriptions, supporting (regular)
T_CAPTION = 22    # Level 5 — captions, footer (regular)


# ============================================================================
# Color (ONE_INK OFF, strict in v1: ink + surface only)
# ============================================================================

INK = (0, 0, 0)
SURFACE = (255, 255, 255)
DIVIDER_ALPHA = 48  # ~19% opacity black, applied via RGBA composite


# ============================================================================
# Typeface — ONE_VOICE: DejaVu Sans, regular + bold
# ============================================================================

F_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
F_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def regular(size):
    return ImageFont.truetype(F_REGULAR, size)


def bold(size):
    return ImageFont.truetype(F_BOLD, size)


# ============================================================================
# Paths + weekly data
# ============================================================================

HERE = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(HERE, "assets", "ts_farms_logo_menu.png")
SPECIALS_PATH = os.path.join(HERE, "specials.json")

DEFAULT_SPECIAL = "First market of the season — say hi at the booth!"
DEFAULT_DATE = "2026-05-02"

try:
    with open(SPECIALS_PATH) as fh:
        _data = json.load(fh)
    SPECIAL_LINE = _data.get("line", DEFAULT_SPECIAL)
    MARKET_DATE = _data.get("date", DEFAULT_DATE)
except Exception:
    SPECIAL_LINE = DEFAULT_SPECIAL
    MARKET_DATE = DEFAULT_DATE

OUT = os.path.join(HERE, "output", f"menu_{MARKET_DATE}_portrait.png")


# ============================================================================
# Menu content — single source of truth
# ============================================================================

MENU = [
    ("Breakfast Sandwiches", [
        ("Oinker", "10",
         "Sausage patty, cheese, egg — choose Apple Maple, Breakfast, or Jalapeño"),
        ("Clucker", "10",
         "Chicken sausage patty, cheese, egg, lettuce, tomato, English muffin"),
        ("Oinkin' Cluck", "10",
         "Bacon, egg, cheese, lettuce, tomato, English muffin"),
        ("Sunny Side Up", "9",
         "Two fried eggs, cheese, lettuce, tomato, English muffin"),
    ]),
    ("Burgers", [
        ("Cheeseburger", "9",
         "Four-ounce beef patty, cheese, hand-crafted bun"),
        ("Barnyard Burger", "12",
         "Four-ounce beef, egg, cheese, lettuce, tomato, pickle, onion"),
        ("Bacon Burger", "13",
         "Four-ounce beef, bacon, cheese, lettuce, tomato, pickle, onion"),
    ]),
    ("Ala Carte", [
        ("Fried Egg", "1", None),
        ("Double Meat", "2.50", None),
        ("Bottled Water", "1.50", None),
    ]),
]


# ============================================================================
# Helpers
# ============================================================================

def text_w(draw, s, fnt):
    box = draw.textbbox((0, 0), s, font=fnt)
    return box[2] - box[0]


def text_h(draw, s, fnt):
    box = draw.textbbox((0, 0), s, font=fnt)
    return box[3] - box[1]


def draw_centered(draw, y, s, fnt, fill=INK):
    w = text_w(draw, s, fnt)
    draw.text(((W - w) // 2, y), s, font=fnt, fill=fill)


def draw_divider(img, y, alpha=DIVIDER_ALPHA):
    """Hairline divider drawn via RGBA composite for partial opacity."""
    overlay = Image.new("RGBA", (W, 1), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rectangle((MARGIN_X, 0, W - MARGIN_X, 1), fill=(0, 0, 0, alpha))
    img.paste(overlay, (0, y), overlay)


def make_qr(url, size_px):
    qr = segno.make(url, error="H")
    buf = io.BytesIO()
    qr.save(buf, kind="png", scale=10, dark="#000000", light="#FFFFFF", border=2)
    buf.seek(0)
    return Image.open(buf).convert("RGB").resize((size_px, size_px), Image.NEAREST)


def wrap_text(draw, s, fnt, max_w):
    """Greedy word-wrap. Returns a list of lines."""
    words = s.split()
    lines = []
    line = []
    for word in words:
        candidate = " ".join(line + [word]) if line else word
        if text_w(draw, candidate, fnt) <= max_w:
            line.append(word)
        else:
            if line:
                lines.append(" ".join(line))
            line = [word]
    if line:
        lines.append(" ".join(line))
    return lines


# ============================================================================
# Zone renderers
# ============================================================================

def render_identity(img, y_start):
    """IDENTITY (hook). The TS Farms line-art logo, centered in its zone.
    No wordmark — the logo and the food advertise the booth on their own.
    The logo is the only Level 1 element on the surface; everything else
    is structure.
    """
    logo_max_h = ZONE_IDENTITY - PAD_DEFAULT

    logo = Image.open(LOGO_PATH).convert("RGBA")
    logo_target_w = 720
    logo_target_h = round(logo.height * (logo_target_w / logo.width))
    if logo_target_h > logo_max_h:
        logo_target_h = logo_max_h
        logo_target_w = round(logo.width * (logo_target_h / logo.height))
    logo = logo.resize((logo_target_w, logo_target_h), Image.LANCZOS)

    logo_x = (W - logo_target_w) // 2
    logo_y = y_start + (ZONE_IDENTITY - logo_target_h) // 2
    img.paste(logo, (logo_x, logo_y), logo)


def render_promo(img, y_start):
    """PROMO (hook). The featured-item zone. v1 renders a clean THIS WEEK
    headline plus the weekly special line.

    Future iterations: replace the text block with a hero image of the
    featured item, or a video frame composite. The zone height is fixed
    so the surrounding rhythm is unaffected by the swap.
    """
    draw = ImageDraw.Draw(img)

    head_y = y_start + PAD_DEFAULT
    draw_centered(draw, head_y, "THIS WEEK", bold(T_PROMO))

    line_font = regular(T_BODY)
    block_y = head_y + T_PROMO + PAD_DEFAULT

    lines = wrap_text(draw, SPECIAL_LINE, line_font, CONTENT_W)
    for i, line in enumerate(lines):
        draw_centered(draw, block_y + i * (T_BODY + PAD_TIGHT), line, line_font)


def render_menu(img, y_start):
    """PROOF. The menu — three sections, even rhythm, no ornament.

    Each section header: Level 2, bold, uppercase, with a hairline
    underline that earns its place by separating header from items.

    Each item row: Level 3 bold name, right-flush Level 3 regular price,
    Level 4 regular description on the next line if present.
    """
    draw = ImageDraw.Draw(img)
    y = y_start + PAD_DEFAULT

    section_gap = PAD_SECTION
    item_gap = PAD_DEFAULT
    desc_gap = PAD_TIGHT

    f_section = bold(T_SECTION)
    f_item = bold(T_ITEM)
    f_price = regular(T_ITEM)
    f_desc = regular(T_BODY)

    for section_i, (section_label, items) in enumerate(MENU):
        if section_i > 0:
            y += section_gap

        draw.text((MARGIN_X, y), section_label.upper(), font=f_section, fill=INK)
        y += T_SECTION + PAD_TIGHT

        draw_divider(img, y)
        y += PAD_DEFAULT

        for name, price, desc in items:
            draw.text((MARGIN_X, y), name, font=f_item, fill=INK)
            price_text = f"${price}"
            pw = text_w(draw, price_text, f_price)
            draw.text((W - MARGIN_X - pw, y), price_text, font=f_price, fill=INK)
            y += T_ITEM

            if desc:
                y += desc_gap
                lines = wrap_text(draw, desc, f_desc, CONTENT_W)
                for line in lines:
                    draw.text((MARGIN_X, y), line, font=f_desc, fill=INK)
                    y += T_BODY + 4
                y -= 4  # remove the final inter-line gap
            y += item_gap


def render_action(img, y_start):
    """ACTION. QR + market info. The final, isolated decision surface.

    Per STYLE_MARKETING: the largest gap above any element on the page
    sits above the action. The reader crosses that gap as a micro-commitment.
    Layout: QR on left, info on right, both vertically centered in the zone.
    """
    draw = ImageDraw.Draw(img)

    qr_size = 200
    qr = make_qr("https://ts-farms.localline.ca", qr_size)

    qr_x = MARGIN_X
    qr_y = y_start + (ZONE_ACTION - qr_size) // 2
    img.paste(qr, (qr_x, qr_y))

    info_x = qr_x + qr_size + PAD_GENEROUS

    f_action = bold(T_SECTION)
    f_url = regular(T_BODY)
    f_meta = regular(T_CAPTION)

    line1 = "ORDER ANYTIME"
    line2 = "ts-farms.localline.ca"
    line3 = "Saturdays · 9 am · Montgomery Farmers Market"

    h_total = T_SECTION + PAD_DEFAULT + T_BODY + PAD_DEFAULT + T_CAPTION
    info_y = y_start + (ZONE_ACTION - h_total) // 2

    draw.text((info_x, info_y), line1, font=f_action, fill=INK)
    info_y += T_SECTION + PAD_DEFAULT

    draw.text((info_x, info_y), line2, font=f_url, fill=INK)
    info_y += T_BODY + PAD_DEFAULT

    draw.text((info_x, info_y), line3, font=f_meta, fill=INK)


# ============================================================================
# Main
# ============================================================================

def build():
    img = Image.new("RGB", (W, H), SURFACE)

    y = MARGIN_TOP
    render_identity(img, y)
    y += ZONE_IDENTITY

    draw_divider(img, y)
    render_promo(img, y)
    y += ZONE_PROMO

    draw_divider(img, y)
    render_menu(img, y)
    y += ZONE_MENU

    draw_divider(img, y)
    render_action(img, y)

    return img


if __name__ == "__main__":
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img = build()
    img.save(OUT, "PNG", optimize=True)
    print(f"Wrote {OUT} ({os.path.getsize(OUT)} bytes)")
