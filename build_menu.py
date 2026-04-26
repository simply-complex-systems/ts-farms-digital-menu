#!/usr/bin/env python3
"""TS Farms / Barnyard Grill — menu builder.

Single shippable 1080x1920 portrait. Three tiers (480/960/480). Built from
a strict design system: 8pt grid, even fonts, same size per role, single
typeface family, no decorative noise. Original line-art TS Farms logo at top.
"""
from PIL import Image, ImageDraw, ImageFont, ImageOps
import segno
import os
import io
import json


# ============================================================================
# DESIGN SYSTEM — locked. Every visual element reads from these constants.
# ============================================================================

# Canvas — 1080x1920 portrait, three tiers exactly
W, H = 1080, 1920
TIER_TOP = 480
TIER_MID = 960
TIER_BOT = 480

# 8pt spacing grid — every padding / gap is one of these. No odd values.
PAD_TIGHT    = 8
PAD_DEFAULT  = 16
PAD_SECTION  = 24
PAD_TIER     = 32
PAD_GENEROUS = 40

# Type scale — even numbers. Same value used for every instance of each role.
FONT_DISPLAY = 80   # the BARNYARD GRILL wordmark
FONT_HEADER  = 32   # every section header (THIS WEEK, BREAKFAST, BURGERS, ALA CARTE)
FONT_ITEM    = 32   # every menu item name
FONT_PRICE   = 32   # every menu item price
FONT_DESC    = 20   # every menu item description
FONT_TAG     = 24   # tagline + special-line + market schedule
FONT_META    = 22   # bottom-tier origin line
FONT_CAPTION = 18   # QR caption

# Object sizes (8pt grid)
ROW_ITEM     = 64   # menu item row with description
ROW_COMPACT  = 40   # ala carte rows (no description)
RULE_W       = 2    # weight of every horizontal rule
GUTTER       = 64   # outer padding from canvas edges, applied uniformly

# Color palette — predictable, conservative, common to grill register
BG          = (24, 22, 20)      # warm near-black slate
INK         = (244, 234, 213)   # warm cream
INK_DIM     = (148, 138, 118)   # warm dim cream
ACCENT      = (212, 160, 23)    # mustard amber (less neon than pure yellow)
DIVIDER     = (44, 41, 37)      # warm dark gray (between tiers)


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
# Single typeface family — no mixing across roles
# ============================================================================

F_BOLD    = "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf"
F_REGULAR = "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf"
F_ITALIC  = "/usr/share/fonts/truetype/ubuntu/Ubuntu-RI.ttf"


def font(path, size):
    return ImageFont.truetype(path if os.path.exists(path) else F_BOLD, size)


# ============================================================================
# Helpers
# ============================================================================

def tw(d, s, fnt):
    b = d.textbbox((0, 0), s, font=fnt)
    return b[2] - b[0]


def load_brand_logo():
    """Original TS Farms line-art rendered as white sketch on transparent."""
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
    qr.save(buf, kind="png", scale=10, dark="#f4ead5", light="#181614", border=1)
    buf.seek(0)
    return Image.open(buf).convert("RGB").resize((size_px, size_px), Image.NEAREST)


# ============================================================================
# Atomic primitives — three of them. Every visual element flows through one.
# ============================================================================

def section_header(d, x, y, w, label):
    """Section header: uppercase letter-spaced text + thin accent rule below.

    Replaces the v1.0.0 yellow brush ribbon with a flat conventional header.
    Returns the y after the header block (PAD_DEFAULT below the rule).
    """
    f = font(F_BOLD, FONT_HEADER)
    text = label.upper()
    width = tw(d, text, f)
    d.text((x + (w - width) // 2, y), text, font=f, fill=INK)
    rule_y = y + FONT_HEADER + PAD_TIGHT
    d.line([(x, rule_y), (x + w, rule_y)], fill=ACCENT, width=RULE_W)
    return rule_y + RULE_W + PAD_DEFAULT


def item_row(d, x, y, w, name, price, desc=None):
    """One menu item row. Name left, price right, optional description below.

    No dotted leader. Spatial alignment alone connects name to price. Returns
    the y after the row (ROW_ITEM if desc, ROW_COMPACT if not).
    """
    f_item = font(F_BOLD, FONT_ITEM)
    f_price = font(F_BOLD, FONT_PRICE)

    d.text((x, y), name, font=f_item, fill=INK)
    price_text = f"${price}"
    pw = tw(d, price_text, f_price)
    d.text((x + w - pw, y), price_text, font=f_price, fill=ACCENT)

    if desc:
        f_desc = font(F_REGULAR, FONT_DESC)
        d.text((x, y + FONT_ITEM + PAD_TIGHT // 2), desc, font=f_desc, fill=INK_DIM)
        return y + ROW_ITEM
    return y + ROW_COMPACT


def tier_divider(d, y):
    """Horizontal divider between tiers — same color, same weight."""
    d.line([(GUTTER, y), (W - GUTTER, y)], fill=DIVIDER, width=RULE_W)


# ============================================================================
# Tier renderers
# ============================================================================

def render_brand(img):
    """Tier 1 (0..480): logo, wordmark, tagline. Centered, symmetric."""
    d = ImageDraw.Draw(img)

    # Logo centered, modest size — it is the brand anchor, not the headline
    logo = load_brand_logo()
    lw = 240
    lh = round(logo.height * (lw / logo.width))
    logo = logo.resize((lw, lh), Image.LANCZOS)
    logo_y = PAD_TIER
    img.paste(logo, ((W - lw) // 2, logo_y), logo)

    # Wordmark BARNYARD GRILL — single color, no shadow, no color-split
    fb_size = FONT_DISPLAY
    while fb_size > 32:
        f_word = font(F_BOLD, fb_size)
        if tw(d, "BARNYARD GRILL", f_word) <= W - 2 * GUTTER:
            break
        fb_size -= 4
    word_w = tw(d, "BARNYARD GRILL", f_word)
    word_y = logo_y + lh + PAD_DEFAULT
    d.text(((W - word_w) // 2, word_y), "BARNYARD GRILL", font=f_word, fill=INK)

    # Tagline italic, dim
    f_tag = font(F_ITALIC, FONT_TAG)
    tag = "Where the farm meets the flame"
    tag_w = tw(d, tag, f_tag)
    tag_y = word_y + fb_size + PAD_DEFAULT
    d.text(((W - tag_w) // 2, tag_y), tag, font=f_tag, fill=INK_DIM)


def render_menu(img):
    """Tier 2 (480..1440): THIS WEEK + BREAKFAST + BURGERS + ALA CARTE.

    No fries. Same header treatment everywhere. Same row treatment everywhere.
    """
    d = ImageDraw.Draw(img)
    x = GUTTER
    w = W - 2 * GUTTER
    y = TIER_TOP + PAD_TIER

    # THIS WEEK — single special line below the header rule
    y = section_header(d, x, y, w, "This Week")
    f_special = font(F_REGULAR, FONT_TAG)
    sw = tw(d, SPECIAL_LINE, f_special)
    d.text(((W - sw) // 2, y), SPECIAL_LINE, font=f_special, fill=INK)
    y += FONT_TAG + PAD_SECTION

    # BREAKFAST SANDWICHES
    y = section_header(d, x, y, w, "Breakfast Sandwiches")
    y = item_row(d, x, y, w, "OINKER", "10",
                "Sausage patty (Apple Maple / Breakfast / Jalapeño Chipotle), cheese, egg, lettuce, tomato")
    y = item_row(d, x, y, w, "CLUCKER", "10",
                "Chicken sausage patty, cheese, egg, lettuce, tomato — English muffin")
    y = item_row(d, x, y, w, "OINKIN' CLUCK", "10",
                "Bacon, egg, cheese, lettuce, tomato — English muffin")
    y = item_row(d, x, y, w, "SUNNY SIDE UP", "9",
                "Two fried eggs, cheese, lettuce, tomato — English muffin")
    y += PAD_DEFAULT

    # BURGERS
    y = section_header(d, x, y, w, "Burgers")
    y = item_row(d, x, y, w, "CHEESEBURGER", "9",
                "4oz beef patty, cheese — hand-crafted bun")
    y = item_row(d, x, y, w, "BARNYARD BURGER", "12",
                "4oz beef, egg, cheese, lettuce, tomato, pickle, onion — hand-crafted bun")
    y = item_row(d, x, y, w, "BACON BURGER", "13",
                "4oz beef, bacon, cheese, lettuce, tomato, pickle, onion — hand-crafted bun")
    y += PAD_DEFAULT

    # ALA CARTE — compact rows, no descriptions
    y = section_header(d, x, y, w, "A La Carte")
    y = item_row(d, x, y, w, "Fried Egg", "1")
    y = item_row(d, x, y, w, "Double Meat", "2.50")
    y = item_row(d, x, y, w, "Bottled Water", "1.50")


def render_info(img):
    """Tier 3 (1440..1920): origin line, market info, QR. Centered stack.

    This zone is reserved for video/promo extension when we know what the
    LED unit can do. For now: clean static info block.
    """
    d = ImageDraw.Draw(img)
    y = TIER_TOP + TIER_MID + PAD_TIER

    # Origin line — small, dim, centered
    f_origin = font(F_BOLD, FONT_META)
    origin = "ALL MEATS FROM OUR FARM   ·   LOCAL PRODUCE"
    ow = tw(d, origin, f_origin)
    d.text(((W - ow) // 2, y), origin, font=f_origin, fill=INK_DIM)
    y += FONT_META + PAD_DEFAULT

    # Market title — accent color, larger
    f_market = font(F_BOLD, FONT_HEADER)
    market = "MONTGOMERY FARMERS MARKET"
    mw = tw(d, market, f_market)
    d.text(((W - mw) // 2, y), market, font=f_market, fill=ACCENT)
    y += FONT_HEADER + PAD_TIGHT

    # Schedule
    f_sched = font(F_REGULAR, FONT_TAG)
    sched = "Saturdays   ·   9 am   ·   May–October"
    sw = tw(d, sched, f_sched)
    d.text(((W - sw) // 2, y), sched, font=f_sched, fill=INK)
    y += FONT_TAG + PAD_SECTION

    # QR centered
    qr_size = 184
    qr = make_qr("https://ts-farms.localline.ca", qr_size)
    img.paste(qr, ((W - qr_size) // 2, y))
    y += qr_size + PAD_DEFAULT

    # Caption
    f_cap = font(F_BOLD, FONT_CAPTION)
    cap = "ORDER ANYTIME   ·   ts-farms.localline.ca"
    cw = tw(d, cap, f_cap)
    d.text(((W - cw) // 2, y), cap, font=f_cap, fill=ACCENT)


# ============================================================================
# Main
# ============================================================================

def build():
    img = Image.new("RGB", (W, H), BG)
    render_brand(img)
    tier_divider(ImageDraw.Draw(img), TIER_TOP)
    render_menu(img)
    tier_divider(ImageDraw.Draw(img), TIER_TOP + TIER_MID)
    render_info(img)
    return img


if __name__ == "__main__":
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img = build()
    img.save(OUT, "PNG", optimize=True)
    print(f"Wrote {OUT} ({os.path.getsize(OUT)} bytes)")
