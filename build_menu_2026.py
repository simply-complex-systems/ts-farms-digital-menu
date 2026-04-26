#!/usr/bin/env python3
"""TS Farms / Barnyard Grill — 2026 menu reframe.

Single shippable 1080x1920 portrait, built from a strict design system.
Three tiers, 50/25/25 weighted (480 / 960 / 480). Even-numbered fonts and
spacing on an 8pt grid. Original line-art TS Farms logo (white-on-dark
via alpha mask). No fries section this year.

Run:  python build_menu_2026.py
Out:  output/menu_<date>_portrait.png
"""
from PIL import Image, ImageDraw, ImageFont, ImageOps
import segno
import os
import io
import json


# ============================================================================
# DESIGN SYSTEM — locked. Everything in this script reads from these constants.
# ============================================================================

# Canvas — 1080x1920 portrait, three tiers at 480/960/480
W, H = 1080, 1920
TIER_TOP = 480
TIER_MID = 960
TIER_BOT = 480

# 8pt spacing grid — every padding / gap is one of these.
PAD_TIGHT     = 8
PAD_DEFAULT   = 16
PAD_SECTION   = 24
PAD_TIER      = 32
PAD_GENEROUS  = 40

# Type scale — even numbers. Same size used for every instance of each role.
FONT_DISPLAY  = 80   # the BARNYARD GRILL wordmark
FONT_BANNER   = 32   # every section banner: THIS WEEK, BREAKFAST, BURGERS, ALA CARTE
FONT_ITEM     = 32   # every menu item name
FONT_PRICE    = 32   # every menu item price (matches item baseline)
FONT_DESC     = 20   # every menu item description
FONT_TAG      = 24   # tagline (italic) and special-line text
FONT_META     = 22   # bottom-tier text
FONT_CAPTION  = 18   # small QR caption / footer line

# Fixed object sizes (8pt grid where applicable)
HEIGHT_BANNER = 48        # every banner — same height
ROW_ITEM      = 64        # every item row with description (FONT_ITEM + gap + FONT_DESC + margin)
ROW_COMPACT   = 40        # ala carte rows (no description)
DIVIDER_W     = 2

# Color — predictable scheme common to grill/menu register
BG          = (26, 26, 26)
INK         = (245, 240, 230)
INK_DIM     = (184, 180, 168)
ACCENT      = (245, 197, 24)
ACCENT_DARK = (212, 160, 23)
DIVIDER     = (64, 64, 64)
SHADOW      = (0, 0, 0)

# Side gutter — applied to every horizontal element
GUTTER = 48


# ============================================================================
# Paths and weekly data
# ============================================================================

HERE = os.path.dirname(os.path.abspath(__file__))
BRAND_LOGO = os.path.join(HERE, "assets", "ts_farms_logo_brand.png")
SPECIALS_PATH = os.path.join(HERE, "specials.json")

DEFAULT_SPECIAL = "First market of the season — say hi at the booth!"
DEFAULT_DATE = "2026-05-02"
try:
    with open(SPECIALS_PATH) as f:
        _s = json.load(f)
    SPECIAL_LINE = _s.get("line", DEFAULT_SPECIAL)
    MARKET_DATE = _s.get("date", DEFAULT_DATE)
except Exception:
    SPECIAL_LINE = DEFAULT_SPECIAL
    MARKET_DATE = DEFAULT_DATE

OUT = os.path.join(HERE, "output", f"menu_{MARKET_DATE}_portrait.png")


# ============================================================================
# Font loaders
# ============================================================================

F_DISPLAY     = "/usr/share/fonts/truetype/noto/NotoSans-Black.ttf"
F_BODY_BOLD   = "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf"
F_BODY        = "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf"
F_ITALIC      = "/usr/share/fonts/truetype/ubuntu/Ubuntu-RI.ttf"
F_NARROW_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSansNarrow-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path if os.path.exists(path) else F_BODY_BOLD, size)


# ============================================================================
# Helpers
# ============================================================================

def text_w(d, s, fnt):
    b = d.textbbox((0, 0), s, font=fnt)
    return b[2] - b[0]


def text_h(d, s, fnt):
    b = d.textbbox((0, 0), s, font=fnt)
    return b[3] - b[1]


def load_brand_logo_white():
    """White-line-on-transparent rendering of the canonical TS Farms logo."""
    src = Image.open(BRAND_LOGO).convert("RGBA")
    flat = Image.new("RGB", src.size, (255, 255, 255))
    flat.paste(src, mask=src.split()[3] if src.mode == "RGBA" else None)
    alpha = ImageOps.invert(flat.convert("L"))
    out = Image.new("RGBA", src.size, (255, 255, 255, 0))
    out.putalpha(alpha)
    return out


def make_qr(url, size_px):
    qr = segno.make(url, error="H")
    buf = io.BytesIO()
    qr.save(buf, kind="png", scale=10, dark="#f5f0e6", light="#1a1a1a", border=1)
    buf.seek(0)
    qr_img = Image.open(buf).convert("RGB")
    return qr_img.resize((size_px, size_px), Image.NEAREST)


# ============================================================================
# Atomic primitives — every visual element flows through one of these
# ============================================================================

def draw_banner(d, x, y, w, label):
    """Yellow banner — same height (HEIGHT_BANNER) and same font (FONT_BANNER)
    everywhere it's used. Centered text, subtle shadow strip at the bottom."""
    d.rounded_rectangle((x, y, x + w, y + HEIGHT_BANNER), radius=10, fill=ACCENT)
    d.rounded_rectangle((x + 4, y + HEIGHT_BANNER - 8, x + w - 4, y + HEIGHT_BANNER - 4),
                        radius=4, fill=ACCENT_DARK)
    f = font(F_DISPLAY, FONT_BANNER)
    tw = text_w(d, label, f)
    th = text_h(d, label, f)
    d.text((x + w / 2 - tw / 2, y + HEIGHT_BANNER / 2 - th / 1.6),
           label, font=f, fill=(20, 20, 20))


def draw_item_row(d, x, y, w, name, price, desc=None):
    """One menu item row. Item + price baseline-aligned. Optional description
    on the line below in dim ink. Returns the y after the row + spacing."""
    f_item = font(F_BODY_BOLD, FONT_ITEM)
    f_price = font(F_NARROW_BOLD, FONT_PRICE)
    f_desc = font(F_BODY, FONT_DESC)

    # Name on left
    d.text((x, y), name, font=f_item, fill=INK)
    # Price on right
    price_text = f"${price}"
    pw = text_w(d, price_text, f_price)
    d.text((x + w - pw, y), price_text, font=f_price, fill=ACCENT)
    # Dotted leader between
    nw = text_w(d, name, f_item)
    leader_y = y + FONT_ITEM // 2 + 8
    for lx in range(x + nw + 12, x + w - pw - 12, 12):
        d.ellipse((lx, leader_y, lx + 4, leader_y + 4), fill=DIVIDER)

    if desc:
        # Description on next line, dim ink
        f_d = f_desc
        d.text((x, y + FONT_ITEM + 4), desc, font=f_d, fill=INK_DIM)
        return y + ROW_ITEM
    return y + ROW_COMPACT


def draw_divider(d, y):
    """Horizontal divider between tiers — same color, same weight everywhere."""
    d.line([(GUTTER, y), (W - GUTTER, y)], fill=DIVIDER, width=DIVIDER_W)


# ============================================================================
# Tier renderers
# ============================================================================

def render_tier_brand(img):
    """Top tier (0..480): logo + wordmark + tagline. Centered, symmetric."""
    d = ImageDraw.Draw(img)

    # Logo — centered, height-budgeted.
    logo = load_brand_logo_white()
    logo_w = 320
    logo_h = round(logo.height * (logo_w / logo.width))
    logo_resized = logo.resize((logo_w, logo_h), Image.LANCZOS)
    logo_x = (W - logo_w) // 2
    logo_y = PAD_TIER
    img.paste(logo_resized, (logo_x, logo_y), logo_resized)

    # Wordmark BARNYARD GRILL — auto-fit to canvas with side gutters
    target_w = W - 2 * GUTTER
    fb_size = FONT_DISPLAY
    while fb_size > 32:
        f_b = font(F_DISPLAY, fb_size)
        if text_w(d, "BARNYARD GRILL", f_b) <= target_w:
            break
        fb_size -= 4
    bw = text_w(d, "BARNYARD ", f_b)
    gw = text_w(d, "GRILL", f_b)
    sx = (W - (bw + gw)) // 2
    word_y = logo_y + logo_h + PAD_DEFAULT
    d.text((sx + 4, word_y + 4), "BARNYARD", font=f_b, fill=SHADOW)
    d.text((sx, word_y), "BARNYARD", font=f_b, fill=ACCENT)
    d.text((sx + bw + 4, word_y + 4), "GRILL", font=f_b, fill=SHADOW)
    d.text((sx + bw, word_y), "GRILL", font=f_b, fill=INK)

    # Tagline italic, centered. Use font-size as line-height (text_h underestimates).
    f_tag = font(F_ITALIC, FONT_TAG)
    tag = "Where the farm meets the flame"
    tw = text_w(d, tag, f_tag)
    tag_y = word_y + fb_size + PAD_DEFAULT
    d.text(((W - tw) // 2, tag_y), tag, font=f_tag, fill=INK_DIM)


def render_tier_menu(img):
    """Middle tier (480..1440): THIS WEEK + sections. No fries."""
    d = ImageDraw.Draw(img)
    y = TIER_TOP + PAD_TIER
    inner_w = W - 2 * GUTTER

    # ---- THIS WEEK ribbon ----
    draw_banner(d, GUTTER, y, inner_w, "THIS WEEK")
    y += HEIGHT_BANNER + PAD_DEFAULT

    f_special = font(F_BODY, FONT_TAG)
    sw = text_w(d, SPECIAL_LINE, f_special)
    d.text(((W - sw) // 2, y), SPECIAL_LINE, font=f_special, fill=INK)
    y += FONT_TAG + PAD_DEFAULT

    # ---- BREAKFAST SANDWICHES ----
    draw_banner(d, GUTTER, y, inner_w, "BREAKFAST SANDWICHES")
    y += HEIGHT_BANNER + PAD_DEFAULT

    y = draw_item_row(d, GUTTER, y, inner_w, "OINKER", "10",
                     "Sausage patty (Apple Maple / Breakfast / Jalapeño Chipotle), cheese, egg, lettuce, tomato")
    y = draw_item_row(d, GUTTER, y, inner_w, "CLUCKER", "10",
                     "Chicken sausage patty, cheese, egg, lettuce, tomato — English muffin")
    y = draw_item_row(d, GUTTER, y, inner_w, "OINKIN' CLUCK", "10",
                     "Bacon, egg, cheese, lettuce, tomato — English muffin")
    y = draw_item_row(d, GUTTER, y, inner_w, "SUNNY SIDE UP", "9",
                     "Two fried eggs, cheese, lettuce, tomato — English muffin")
    y += PAD_DEFAULT

    # ---- BURGERS ----
    draw_banner(d, GUTTER, y, inner_w, "BURGERS")
    y += HEIGHT_BANNER + PAD_DEFAULT

    y = draw_item_row(d, GUTTER, y, inner_w, "CHEESEBURGER", "9",
                     "4oz beef patty, cheese — hand-crafted bun")
    y = draw_item_row(d, GUTTER, y, inner_w, "BARNYARD BURGER", "12",
                     "4oz beef, egg, cheese, lettuce, tomato, pickle, onion — hand-crafted bun")
    y = draw_item_row(d, GUTTER, y, inner_w, "BACON BURGER", "13",
                     "4oz beef, bacon, cheese, lettuce, tomato, pickle, onion — hand-crafted bun")
    y += PAD_DEFAULT

    # ---- ALA CARTE (compact rows, no descriptions) ----
    draw_banner(d, GUTTER, y, inner_w, "ALA CARTE")
    y += HEIGHT_BANNER + PAD_DEFAULT

    y = draw_item_row(d, GUTTER, y, inner_w, "Fried Egg", "1")
    y = draw_item_row(d, GUTTER, y, inner_w, "Double Meat", "2.50")
    y = draw_item_row(d, GUTTER, y, inner_w, "Bottled Water", "1.50")


def render_tier_info(img):
    """Bottom tier (1440..1920): origin line + market info + QR. Single coherent zone.

    Symmetric vertical stack centered on the canvas. Reserved space here is
    where Tiffany's video/promo content will go in a later iteration.
    """
    d = ImageDraw.Draw(img)
    y = TIER_TOP + TIER_MID + PAD_TIER

    # Origin line — small caps style header
    f_h = font(F_BODY_BOLD, FONT_META)
    head = "ALL MEATS FROM OUR FARM · LOCAL PRODUCE"
    hw = text_w(d, head, f_h)
    d.text(((W - hw) // 2, y), head, font=f_h, fill=INK_DIM)
    y += FONT_META + PAD_DEFAULT

    # Market title
    f_market = font(F_DISPLAY, 36)
    market = "MONTGOMERY FARMERS MARKET"
    mw = text_w(d, market, f_market)
    d.text(((W - mw) // 2, y), market, font=f_market, fill=ACCENT)
    y += 36 + PAD_TIGHT

    # Market schedule
    f_sched = font(F_BODY, FONT_META)
    sched = "Saturdays  ·  9 am  ·  May–October"
    sw = text_w(d, sched, f_sched)
    d.text(((W - sw) // 2, y), sched, font=f_sched, fill=INK)
    y += FONT_META + PAD_SECTION

    # QR — centered, large enough to scan
    qr_size = 192
    qr = make_qr("https://ts-farms.localline.ca", qr_size)
    qr_x = (W - qr_size) // 2
    img.paste(qr, (qr_x, y))
    y += qr_size + PAD_TIGHT

    # QR caption
    f_cap = font(F_BODY_BOLD, FONT_CAPTION)
    cap = "ORDER ANYTIME  ·  ts-farms.localline.ca"
    cw = text_w(d, cap, f_cap)
    d.text(((W - cw) // 2, y), cap, font=f_cap, fill=ACCENT)


# ============================================================================
# Main
# ============================================================================

def build():
    img = Image.new("RGB", (W, H), BG)
    render_tier_brand(img)
    draw_divider(ImageDraw.Draw(img), TIER_TOP)
    render_tier_menu(img)
    draw_divider(ImageDraw.Draw(img), TIER_TOP + TIER_MID)
    render_tier_info(img)
    return img


if __name__ == "__main__":
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img = build()
    img.save(OUT, "PNG", optimize=True)
    print(f"Wrote {OUT} ({os.path.getsize(OUT)} bytes)")
