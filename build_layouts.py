#!/usr/bin/env python3
"""Render four three-tier layout variants for Tiffany's review.

50/25/25 weighted composition in 1080x1920 portrait. The dominant
50% zone is always the menu. The two 25% zones vary per variant:

  A — As asked     : brand top, menu middle, static promo bottom
  B — Video header : video-loop top, menu middle, logo+QR bottom
  C — Video footer : brand top, menu middle, video-loop bottom
  D — Two-up split : brand top, menu middle, [video | promo] bottom

Outputs to output/options/. Contact sheet at output/options/contact_sheet.png.
"""
from PIL import Image, ImageDraw, ImageFont, ImageOps
import segno
import os, io, json, random

W, H = 1080, 1920
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "output", "options")
os.makedirs(OUT_DIR, exist_ok=True)

BRAND_LOGO = os.path.join(HERE, "assets", "ts_farms_logo_brand.png")
SPECIALS_PATH = os.path.join(HERE, "specials.json")

# Load weekly content
try:
    with open(SPECIALS_PATH) as f:
        _s = json.load(f)
    SPECIAL_LINE = _s.get("line", "First market of the season — say hi at the booth!")
    MARKET_DATE = _s.get("date", "2026-05-02")
except Exception:
    SPECIAL_LINE = "First market of the season — say hi at the booth!"
    MARKET_DATE = "2026-05-02"

# Palette
BG_DARK = (22, 22, 22)
BG_GRAD = (34, 34, 34)
INK = (245, 240, 230)
INK_DIM = (190, 185, 175)
YELLOW = (245, 197, 24)
YELLOW_DARK = (210, 160, 0)
RED_ACCENT = (200, 60, 50)
VIDEO_FRAME = (60, 60, 60)
PROMO_BAND = (40, 30, 20)

# Fonts
F_DISPLAY = "/usr/share/fonts/truetype/noto/NotoSans-Black.ttf"
F_BODY_BOLD = "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf"
F_BODY = "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf"
F_NARROW_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSansNarrow-Bold.ttf"
F_ITALIC = "/usr/share/fonts/truetype/ubuntu/Ubuntu-RI.ttf"

def font(p, s):
    return ImageFont.truetype(p if os.path.exists(p) else F_BODY_BOLD, s)

def text_w(d, s, fnt):
    b = d.textbbox((0,0), s, font=fnt); return b[2]-b[0]
def text_h(d, s, fnt):
    b = d.textbbox((0,0), s, font=fnt); return b[3]-b[1]


def make_chalkboard_bg(W, H):
    img = Image.new("RGB", (W, H), BG_DARK)
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        c = tuple(int(BG_DARK[i] + (BG_GRAD[i]-BG_DARK[i])*t) for i in range(3))
        d.line([(0,y),(W,y)], fill=c)
    rng = random.Random(7)
    for _ in range(int(W*H*0.0012)):
        x, y = rng.randint(0,W-1), rng.randint(0,H-1)
        v = rng.randint(40, 60)
        d.point((x,y), fill=(v,v,v))
    for _ in range(80):
        x, y = rng.randint(0,W-200), rng.randint(0,H-1)
        L = rng.randint(40, 220)
        c = rng.randint(28,46)
        d.line([(x,y),(x+L,y)], fill=(c,c,c))
    return img


def load_brand_logo_white():
    """Load the brand logo as white sketch with transparent background.

    Uses the original grayscale brightness as inverse alpha: dark sketch
    pixels become opaque white, bright background pixels become transparent.
    Paste with the returned image as its own mask:
        img.paste(logo, (x, y), logo)
    """
    src = Image.open(BRAND_LOGO).convert("RGBA")
    # Flatten any alpha onto white so we have a clean RGB
    flat = Image.new("RGB", src.size, (255, 255, 255))
    flat.paste(src, mask=src.split()[3] if src.mode == "RGBA" else None)
    # Inverted grayscale = alpha (dark sketch -> 255 alpha, white bg -> 0 alpha)
    alpha = ImageOps.invert(flat.convert("L"))
    # Solid white image with that alpha
    out = Image.new("RGBA", src.size, (255, 255, 255, 0))
    out.putalpha(alpha)
    return out


def brush_banner(d, x, y, w, h, label, label_font, fill=YELLOW, text_color=(20,20,20)):
    rect = (x, y, x+w, y+h)
    d.rounded_rectangle(rect, radius=12, fill=fill)
    rng = random.Random(hash(label) & 0xffff)
    for _ in range(8):
        dx = rng.randint(-10,10); dy = rng.randint(-3,3)
        d.ellipse((x-12+dx, y+5+dy, x-2+dx, y+h-5+dy), fill=fill)
        d.ellipse((x+w-8+dx, y+5+dy, x+w+10+dx, y+h-5+dy), fill=fill)
    d.rounded_rectangle((x+3, y+h-7, x+w-3, y+h-2), radius=5, fill=YELLOW_DARK)
    tw = text_w(d, label, label_font); th = text_h(d, label, label_font)
    d.text((x + w/2 - tw/2, y + h/2 - th/1.5), label, font=label_font, fill=text_color)


def make_qr(url, size_px, dark="#f5f0e6", light="#1a1a1a"):
    qr = segno.make(url, error="H")
    buf = io.BytesIO()
    qr.save(buf, kind="png", scale=10, dark=dark, light=light, border=1)
    buf.seek(0)
    qr_img = Image.open(buf).convert("RGB")
    return qr_img.resize((size_px, size_px), Image.NEAREST)


# ---- ZONE RENDERERS ----

def zone_brand(img, x0, y0, w, h):
    """Logo + wordmark + tagline. Variable height; centers within (x0,y0,w,h)."""
    d = ImageDraw.Draw(img)
    logo = load_brand_logo_white()
    lw = int(w * 0.42)
    lh = int(logo.height * (lw / logo.width))
    logo_resized = logo.resize((lw, lh), Image.LANCZOS)
    img.paste(logo_resized, (x0 + (w - lw)//2, y0 + 16), logo_resized)

    # BARNYARD GRILL wordmark
    f_b = font(F_DISPLAY, 84)
    title = "BARNYARD GRILL"
    bw = text_w(d, "BARNYARD ", f_b)
    gw = text_w(d, "GRILL", f_b)
    sx = x0 + (w - (bw+gw))//2
    ty = y0 + 16 + lh + 4
    d.text((sx+3, ty+3), "BARNYARD", font=f_b, fill=(0,0,0))
    d.text((sx, ty), "BARNYARD", font=f_b, fill=YELLOW)
    d.text((sx+bw+3, ty+3), "GRILL", font=f_b, fill=(0,0,0))
    d.text((sx+bw, ty), "GRILL", font=f_b, fill=INK)

    # Tagline
    f_tag = font(F_ITALIC, 30)
    tag = "Where the farm meets the flame"
    tw = text_w(d, tag, f_tag)
    d.text((x0 + (w - tw)//2, ty + 96), tag, font=f_tag, fill=INK_DIM)


def zone_menu(img, x0, y0, w, h):
    """The food menu — fits inside (x0, y0, w, h). Compressed for 50% zone."""
    d = ImageDraw.Draw(img)

    # THIS WEEK ribbon at top
    rib_h = max(54, int(h*0.07))
    brush_banner(d, x0+40, y0+8, w-80, rib_h, "THIS WEEK", font(F_DISPLAY, int(rib_h*0.55)))
    f_special = font(F_BODY_BOLD, max(20, int(h*0.025)))
    sw = text_w(d, SPECIAL_LINE, f_special)
    d.text((x0 + (w - sw)//2, y0 + rib_h + 16), SPECIAL_LINE, font=f_special, fill=INK)

    section_top = y0 + rib_h + 16 + text_h(d, "X", f_special) + 12

    # Compute rough scaling
    # Scale fonts for available height
    avail = h - (section_top - y0) - 12
    scale = avail / 1100.0  # tuned for 1100px nominal menu height
    scale = max(0.55, min(1.0, scale))

    f_sec = font(F_DISPLAY, int(36 * scale))
    f_item = font(F_BODY_BOLD, int(38 * scale))
    f_price = font(F_NARROW_BOLD, int(38 * scale))
    f_desc = font(F_BODY, int(22 * scale))
    f_inline = font(F_BODY_BOLD, int(28 * scale))

    def banner(y, label, ww):
        bh = int(64 * scale)
        brush_banner(d, x0+40, y, ww, bh, label, f_sec)
        return y + bh + 8

    def menu_row(y, name, price, desc=None):
        d.text((x0+40, y), name, font=f_item, fill=INK)
        pw = text_w(d, f"${price}", f_price)
        d.text((x0 + w - 40 - pw, y), f"${price}", font=f_price, fill=YELLOW)
        nw = text_w(d, name, f_item)
        for lx in range(x0+40 + nw + 14, x0 + w - 40 - pw - 8, int(12*scale)):
            d.ellipse((lx, y+int(28*scale), lx+3, y+int(31*scale)), fill=(80,80,80))
        ny = y + int(46*scale)
        if desc:
            words = desc.split(); line = ""
            ly = ny
            maxw = w - 80
            for word in words:
                t = (line + " " + word).strip()
                if text_w(d, t, f_desc) > maxw:
                    d.text((x0+40, ly), line, font=f_desc, fill=INK_DIM)
                    ly += int(28*scale); line = word
                else:
                    line = t
            if line:
                d.text((x0+40, ly), line, font=f_desc, fill=INK_DIM)
                ly += int(30*scale)
            return ly + 4
        return ny + 6

    y = section_top
    y = banner(y, "BREAKFAST SANDWICHES", w-80)
    y = menu_row(y, "OINKER", "10", "Sausage patty (your choice), cheese, egg, lettuce, tomato — English muffin")
    y = menu_row(y, "CLUCKER", "10", "Chicken sausage patty, cheese, egg, lettuce, tomato — English muffin")
    y = menu_row(y, "OINKIN' CLUCK", "10", "Bacon, egg, cheese, lettuce, tomato — English muffin")
    y = menu_row(y, "SUNNY SIDE UP", "9", "Two fried eggs, cheese, lettuce, tomato — English muffin")
    y += 4
    y = banner(y, "BURGERS", w-80)
    y = menu_row(y, "CHEESEBURGER", "9", "4oz beef patty, cheese — hand-crafted bun")
    y = menu_row(y, "BARNYARD BURGER", "12", "4oz beef, egg, cheese, LTOP — hand-crafted bun")
    y = menu_row(y, "BACON BURGER", "13", "4oz beef, bacon, cheese, LTOP — hand-crafted bun")
    y += 4
    # Compact two-column footer: Sausage flavors / Ala carte / Fries
    col_y = y
    half = (w - 80) // 2
    # left: ALA CARTE
    brush_banner(d, x0+40, col_y, half-8, int(54*scale), "ALA CARTE", font(F_DISPLAY, int(28*scale)))
    f_alc = font(F_BODY_BOLD, int(26*scale))
    f_alp = font(F_NARROW_BOLD, int(26*scale))
    for i,(n,p) in enumerate([("Fried Egg","1"),("Double Meat","2.50"),("Bottled Water","1.50")]):
        yy = col_y + int(70*scale) + i*int(34*scale)
        d.text((x0+50, yy), n, font=f_alc, fill=INK)
        pw = text_w(d, f"${p}", f_alp)
        d.text((x0+40+half-16-pw, yy), f"${p}", font=f_alp, fill=YELLOW)
    # right: FRIES
    brush_banner(d, x0+40+half+8, col_y, half-8, int(54*scale), "FRIES", font(F_DISPLAY, int(28*scale)))
    f_fr = font(F_BODY_BOLD, int(28*scale))
    f_frp = font(F_NARROW_BOLD, int(28*scale))
    for i,(n,p) in enumerate([("Fries","4"),("Cheese Fries","5")]):
        yy = col_y + int(70*scale) + i*int(36*scale)
        d.text((x0+50+half+8, yy), n, font=f_fr, fill=INK)
        pw = text_w(d, f"${p}", f_frp)
        d.text((x0 + w - 56 - pw, yy), f"${p}", font=f_frp, fill=YELLOW)


def zone_video(img, x0, y0, w, h, caption="LOOPED VIDEO", subcaption="Farm b-roll · cows · pigs · sunrise"):
    """Render a 'video plays here' zone with a film-strip-style frame."""
    d = ImageDraw.Draw(img)
    pad = 24
    inner = (x0+pad, y0+pad, x0+w-pad, y0+h-pad)
    # frame (film-strip border)
    d.rectangle(inner, fill=(28,28,28), outline=YELLOW, width=4)
    # sprocket holes top + bottom
    sp_h = 20; sp_w = 28
    sp_y_top = y0 + pad - sp_h - 6
    sp_y_bot = y0 + h - pad + 6
    n_sp = 8
    for i in range(n_sp):
        cx = x0 + pad + (w - 2*pad) * (i + 0.5) / n_sp
        d.rectangle((cx - sp_w/2, sp_y_top, cx + sp_w/2, sp_y_top + sp_h), fill=(60,60,60))
        d.rectangle((cx - sp_w/2, sp_y_bot, cx + sp_w/2, sp_y_bot + sp_h), fill=(60,60,60))
    # play icon centered
    cx = x0 + w//2; cy = y0 + h//2
    tri_size = min(80, h//4)
    d.polygon([(cx - tri_size//2, cy - tri_size//2),
               (cx - tri_size//2, cy + tri_size//2),
               (cx + tri_size//2, cy)], fill=YELLOW)
    # caption
    f_cap = font(F_DISPLAY, 36)
    cw = text_w(d, caption, f_cap)
    d.text((cx - cw//2, cy + tri_size//2 + 14), caption, font=f_cap, fill=INK)
    f_sub = font(F_ITALIC, 22)
    sw = text_w(d, subcaption, f_sub)
    d.text((cx - sw//2, cy + tri_size//2 + 56), subcaption, font=f_sub, fill=INK_DIM)


def zone_promo_static(img, x0, y0, w, h):
    """Static promo card: logo block + QR + farm photo placeholder + market info."""
    d = ImageDraw.Draw(img)
    pad = 28
    # Left half: photo placeholder
    half = (w - 2*pad - 16) // 2
    photo = (x0+pad, y0+pad, x0+pad+half, y0+h-pad)
    d.rectangle(photo, fill=(45,40,30), outline=(80,70,55), width=2)
    f_ph = font(F_ITALIC, 22)
    msg = "[ farm photo ]"
    cw = text_w(d, msg, f_ph)
    d.text(((photo[0]+photo[2])//2 - cw//2, (photo[1]+photo[3])//2 - 12), msg, font=f_ph, fill=INK_DIM)

    # Right half: market info + QR
    rx = x0 + pad + half + 16
    f_h = font(F_DISPLAY, 30)
    f_b = font(F_BODY_BOLD, 22)
    f_d = font(F_BODY, 20)
    d.text((rx, y0+pad), "Find us at", font=f_b, fill=INK_DIM)
    d.text((rx, y0+pad+24), "Montgomery", font=f_h, fill=YELLOW)
    d.text((rx, y0+pad+58), "Farmers Market", font=f_h, fill=YELLOW)
    d.text((rx, y0+pad+96), "Saturdays 9 am · May–Oct", font=f_d, fill=INK)

    # QR
    qr_size = min(140, h - 2*pad - 140)
    qr = make_qr("https://ts-farms.localline.ca", qr_size)
    qr_x = x0 + w - pad - qr_size
    qr_y = y0 + h - pad - qr_size - 30
    img.paste(qr, (qr_x, qr_y))
    f_qrc = font(F_BODY_BOLD, 18)
    cap = "ORDER ANYTIME"
    cw = text_w(d, cap, f_qrc)
    d.text((qr_x + qr_size//2 - cw//2, qr_y + qr_size + 4), cap, font=f_qrc, fill=YELLOW)


def zone_logo_qr(img, x0, y0, w, h):
    """Compact bottom-tier: logo + QR + market line."""
    d = ImageDraw.Draw(img)
    pad = 24
    # logo on left
    logo = load_brand_logo_white()
    lw = int(w * 0.30)
    lh = int(logo.height * (lw / logo.width))
    logo_resized = logo.resize((lw, lh), Image.LANCZOS)
    img.paste(logo_resized, (x0 + pad, y0 + (h-lh)//2), logo_resized)

    # QR on right
    qr_size = min(150, h - 2*pad)
    qr = make_qr("https://ts-farms.localline.ca", qr_size)
    qr_x = x0 + w - pad - qr_size
    qr_y = y0 + (h - qr_size)//2 - 14
    img.paste(qr, (qr_x, qr_y))
    f_qrc = font(F_BODY_BOLD, 18)
    cap = "ORDER ANYTIME"
    cw = text_w(d, cap, f_qrc)
    d.text((qr_x + qr_size//2 - cw//2, qr_y + qr_size + 4), cap, font=f_qrc, fill=YELLOW)

    # middle: market info
    mx = x0 + pad + lw + 24
    f_h = font(F_DISPLAY, 32)
    f_d = font(F_BODY, 22)
    d.text((mx, y0 + h//2 - 36), "Montgomery Farmers Market", font=f_h, fill=YELLOW)
    d.text((mx, y0 + h//2 + 4), "Saturdays 9 am · May–October", font=f_d, fill=INK_DIM)


def zone_two_up(img, x0, y0, w, h):
    """Bottom split: video carousel | promo banner."""
    d = ImageDraw.Draw(img)
    half = w // 2
    # Left: video carousel
    zone_video(img, x0, y0, half-8, h,
               caption="VIDEO LOOP",
               subcaption="Cows · pigs · meet your farmer")
    # Right: promo banner
    rx = x0 + half + 8
    rw = w - half - 8
    pad = 20
    d.rectangle((rx+pad, y0+pad, rx+rw-pad, y0+h-pad), fill=PROMO_BAND, outline=YELLOW, width=3)
    f_h = font(F_DISPLAY, 36)
    f_b = font(F_BODY_BOLD, 22)
    f_d = font(F_BODY, 20)
    cx = rx + rw//2
    head1 = "JOIN THE CSA"
    cw = text_w(d, head1, f_h)
    d.text((cx - cw//2, y0 + pad + 24), head1, font=f_h, fill=YELLOW)
    sub = "Weekly box · pickup or delivery"
    sw = text_w(d, sub, f_b)
    d.text((cx - sw//2, y0 + pad + 70), sub, font=f_b, fill=INK)
    # QR
    qr_size = min(120, h - 2*pad - 120)
    qr = make_qr("https://ts-farms.localline.ca/csa", qr_size)
    qr_x = cx - qr_size//2
    qr_y = y0 + pad + 110
    img.paste(qr, (qr_x, qr_y))
    cap = "Scan to subscribe"
    cw = text_w(d, cap, f_d)
    d.text((cx - cw//2, qr_y + qr_size + 8), cap, font=f_d, fill=INK_DIM)


# ---- VARIANT BUILDERS ----

def divider(img, y):
    d = ImageDraw.Draw(img)
    d.line([(60, y), (W-60, y)], fill=(70,70,70), width=2)


def build_variant_A():
    """Brand top (25%) | Menu middle (50%) | Static promo bottom (25%)."""
    img = make_chalkboard_bg(W, H)
    h_top = int(H * 0.25)
    h_mid = int(H * 0.50)
    h_bot = H - h_top - h_mid
    zone_brand(img, 0, 0, W, h_top)
    divider(img, h_top)
    zone_menu(img, 0, h_top, W, h_mid)
    divider(img, h_top + h_mid)
    zone_promo_static(img, 0, h_top + h_mid, W, h_bot)
    return img


def build_variant_B():
    """Video header (25%) | Menu middle (50%) | Logo+QR bottom (25%)."""
    img = make_chalkboard_bg(W, H)
    h_top = int(H * 0.25)
    h_mid = int(H * 0.50)
    h_bot = H - h_top - h_mid
    zone_video(img, 0, 0, W, h_top, caption="LOOPED VIDEO", subcaption="Farm b-roll · cows · pigs · sunrise")
    divider(img, h_top)
    zone_menu(img, 0, h_top, W, h_mid)
    divider(img, h_top + h_mid)
    zone_logo_qr(img, 0, h_top + h_mid, W, h_bot)
    return img


def build_variant_C():
    """Brand top (25%) | Menu middle (50%) | Video footer (25%)."""
    img = make_chalkboard_bg(W, H)
    h_top = int(H * 0.25)
    h_mid = int(H * 0.50)
    h_bot = H - h_top - h_mid
    zone_brand(img, 0, 0, W, h_top)
    divider(img, h_top)
    zone_menu(img, 0, h_top, W, h_mid)
    divider(img, h_top + h_mid)
    zone_video(img, 0, h_top + h_mid, W, h_bot, caption="LOOPED VIDEO / PROMO", subcaption="Cattle in the field · CSA pitch · weekly hero")
    return img


def build_variant_D():
    """Brand top (25%) | Menu middle (50%) | Two-up [video | promo] bottom (25%)."""
    img = make_chalkboard_bg(W, H)
    h_top = int(H * 0.25)
    h_mid = int(H * 0.50)
    h_bot = H - h_top - h_mid
    zone_brand(img, 0, 0, W, h_top)
    divider(img, h_top)
    zone_menu(img, 0, h_top, W, h_mid)
    divider(img, h_top + h_mid)
    zone_two_up(img, 0, h_top + h_mid, W, h_bot)
    return img


# ---- ADDITIONAL ZONE RENDERERS (variants E, F, G) ----

def zone_photo_hero(img, x0, y0, w, h, caption="Family-raised in New Vienna, Ohio"):
    """Hero farm photo placeholder with TS Farms logo overlaid + caption."""
    d = ImageDraw.Draw(img)
    pad = 16
    # Photo placeholder card
    d.rectangle((x0+pad, y0+pad, x0+w-pad, y0+h-pad), fill=(38, 32, 24), outline=(80, 70, 55), width=3)
    # Watermark text deep in the card
    f_ph = font(F_ITALIC, 28)
    msg = "[ hero farm photo — cattle at sunrise ]"
    cw = text_w(d, msg, f_ph)
    d.text((x0 + (w - cw)//2, y0 + h//2 - 60), msg, font=f_ph, fill=(95, 85, 65))
    # Logo overlay (centered, smaller)
    logo = load_brand_logo_white()
    lw = int(w * 0.22)
    lh = int(logo.height * (lw / logo.width))
    logo_resized = logo.resize((lw, lh), Image.LANCZOS)
    img.paste(logo_resized, (x0 + (w - lw)//2, y0 + 24), logo_resized)
    # Caption
    f_cap = font(F_BODY_BOLD, 28)
    cw = text_w(d, caption, f_cap)
    d.text((x0 + (w - cw)//2, y0 + h - pad - 50), caption, font=f_cap, fill=YELLOW)


# ---- ADDITIONAL VARIANT BUILDERS ----

def build_variant_E():
    """Equal thirds (33/33/33): brand top, menu middle, static promo bottom."""
    img = make_chalkboard_bg(W, H)
    third = H // 3
    zone_brand(img, 0, 0, W, third)
    divider(img, third)
    zone_menu(img, 0, third, W, third)
    divider(img, 2*third)
    zone_promo_static(img, 0, 2*third, W, H - 2*third)
    return img


def build_variant_F():
    """Photo-led top (25/50/25): hero photo + logo overlay top, menu middle, brand+QR bottom."""
    img = make_chalkboard_bg(W, H)
    h_top = int(H * 0.25)
    h_mid = int(H * 0.50)
    h_bot = H - h_top - h_mid
    zone_photo_hero(img, 0, 0, W, h_top)
    divider(img, h_top)
    zone_menu(img, 0, h_top, W, h_mid)
    divider(img, h_top + h_mid)
    zone_logo_qr(img, 0, h_top + h_mid, W, h_bot)
    return img


def build_variant_G_slide1():
    """Carousel slide 1: brand welcome — full-screen logo + tagline + CTA."""
    img = make_chalkboard_bg(W, H)
    d = ImageDraw.Draw(img)
    # Centered logo
    logo = load_brand_logo_white()
    lw = int(W * 0.72)
    lh = int(logo.height * (lw / logo.width))
    logo_resized = logo.resize((lw, lh), Image.LANCZOS)
    logo_y = int(H * 0.18)
    img.paste(logo_resized, ((W - lw)//2, logo_y), logo_resized)
    # BARNYARD GRILL wordmark — auto-fit to 92% of canvas width
    target_w = int(W * 0.92)
    fb_size = 140
    while fb_size > 40:
        f_b = font(F_DISPLAY, fb_size)
        if text_w(d, "BARNYARD GRILL", f_b) <= target_w:
            break
        fb_size -= 4
    bw = text_w(d, "BARNYARD ", f_b)
    gw = text_w(d, "GRILL", f_b)
    sx = (W - (bw + gw)) // 2
    ty = logo_y + lh + 40
    d.text((sx+5, ty+5), "BARNYARD", font=f_b, fill=(0,0,0))
    d.text((sx, ty), "BARNYARD", font=f_b, fill=YELLOW)
    d.text((sx+bw+5, ty+5), "GRILL", font=f_b, fill=(0,0,0))
    d.text((sx+bw, ty), "GRILL", font=f_b, fill=INK)
    # Tagline
    f_tag = font(F_ITALIC, 44)
    tag = "Where the farm meets the flame"
    tw = text_w(d, tag, f_tag)
    d.text(((W - tw)//2, ty + fb_size + 30), tag, font=f_tag, fill=INK_DIM)
    # CTA at bottom
    f_cta = font(F_DISPLAY, 56)
    cta = "Saturdays · 9 am · Montgomery"
    cw = text_w(d, cta, f_cta)
    d.text(((W - cw)//2, int(H * 0.78)), cta, font=f_cta, fill=YELLOW)
    # QR
    qr_size = 240
    qr = make_qr("https://ts-farms.localline.ca", qr_size)
    img.paste(qr, ((W - qr_size)//2, int(H * 0.84)))
    f_qrc = font(F_BODY_BOLD, 26)
    cap = "Order anytime · ts-farms.localline.ca"
    cw = text_w(d, cap, f_qrc)
    d.text(((W - cw)//2, int(H * 0.84) + qr_size + 10), cap, font=f_qrc, fill=INK_DIM)
    return img


def build_variant_G_slide2():
    """Carousel slide 2: the full menu, more breathable."""
    img = make_chalkboard_bg(W, H)
    d = ImageDraw.Draw(img)
    # Compact header
    f_h = font(F_DISPLAY, 80)
    head = "MENU"
    hw = text_w(d, head, f_h)
    d.text(((W - hw)//2, 60), head, font=f_h, fill=YELLOW)
    f_sub = font(F_ITALIC, 36)
    sub = "BARNYARD GRILL"
    sw = text_w(d, sub, f_sub)
    d.text(((W - sw)//2, 60 + 80 + 8), sub, font=f_sub, fill=INK_DIM)
    # The menu zone takes most of the canvas
    zone_menu(img, 0, 200, W, H - 280)
    return img


def build_variant_G_slide3():
    """Carousel slide 3: 'meet your farmer' + market info."""
    img = make_chalkboard_bg(W, H)
    d = ImageDraw.Draw(img)
    # Top: title
    f_h = font(F_DISPLAY, 96)
    head = "MEET YOUR"
    hw = text_w(d, head, f_h)
    d.text(((W - hw)//2, 80), head, font=f_h, fill=YELLOW)
    head2 = "FARMER"
    hw2 = text_w(d, head2, f_h)
    d.text(((W - hw2)//2, 80 + 110), head2, font=f_h, fill=INK)
    # Photo card
    pad = 80
    photo_y = 320
    photo_h = 600
    d.rectangle((pad, photo_y, W - pad, photo_y + photo_h), fill=(38, 32, 24), outline=(80, 70, 55), width=3)
    f_ph = font(F_ITALIC, 32)
    msg = "[ Tiffany on the farm ]"
    cw = text_w(d, msg, f_ph)
    d.text(((W - cw)//2, photo_y + photo_h//2 - 16), msg, font=f_ph, fill=(95, 85, 65))
    # Bio
    bio_y = photo_y + photo_h + 60
    f_b = font(F_BODY_BOLD, 38)
    f_d = font(F_BODY, 30)
    line1 = "Tiffany Shinkle"
    cw = text_w(d, line1, f_b)
    d.text(((W - cw)//2, bio_y), line1, font=f_b, fill=YELLOW)
    line2 = "TS Farms · New Vienna, Ohio · 22 years"
    cw = text_w(d, line2, f_d)
    d.text(((W - cw)//2, bio_y + 50), line2, font=f_d, fill=INK)
    line3 = "Ethically and sustainably produced."
    cw = text_w(d, line3, f_d)
    d.text(((W - cw)//2, bio_y + 90), line3, font=f_d, fill=INK_DIM)
    # Bottom: market + QR row
    f_m = font(F_DISPLAY, 40)
    market = "Find us at Montgomery Farmers Market"
    cw = text_w(d, market, f_m)
    d.text(((W - cw)//2, H - 280), market, font=f_m, fill=YELLOW)
    f_md = font(F_BODY, 28)
    days = "Saturdays 9 am · May–October"
    cw = text_w(d, days, f_md)
    d.text(((W - cw)//2, H - 230), days, font=f_md, fill=INK_DIM)
    qr_size = 160
    qr = make_qr("https://ts-farms.localline.ca", qr_size)
    img.paste(qr, ((W - qr_size)//2, H - 200))
    return img


def build_contact_sheet(items):
    """Grid of variants at thumbnail resolution with labels.

    items: list of (label, image) tuples. Auto-grids into 4 columns.
    """
    cols = 4
    rows = (len(items) + cols - 1) // cols
    pad = 24
    label_h = 80
    cell_w = W // 4
    cell_h = H // 4
    sheet_w = cols * cell_w + (cols + 1) * pad
    sheet_h = rows * (cell_h + label_h) + (rows + 1) * pad + 100  # +100 for title
    sheet = Image.new("RGB", (sheet_w, sheet_h), (15, 15, 15))
    d = ImageDraw.Draw(sheet)
    # title
    f_title = font(F_DISPLAY, 40)
    title = "BARNYARD GRILL — Layout Options · 2026-05-02"
    tw = text_w(d, title, f_title)
    d.text(((sheet_w - tw)//2, 16), title, font=f_title, fill=YELLOW)
    f_sub = font(F_ITALIC, 22)
    sub = "Pick one (or a hybrid). Bottom 25% reserved for video / promo per Tiffany's spec."
    sw = text_w(d, sub, f_sub)
    d.text(((sheet_w - sw)//2, 60), sub, font=f_sub, fill=INK_DIM)

    f_label = font(F_BODY_BOLD, 20)

    for idx, (label, variant) in enumerate(items):
        col = idx % cols
        row = idx // cols
        x = pad + col * (cell_w + pad)
        y = 100 + pad + row * (cell_h + label_h + pad)
        small = variant.resize((cell_w, cell_h), Image.LANCZOS)
        sheet.paste(small, (x, y))
        ly = y + cell_h + 8
        for line in label.split("\n"):
            lw = text_w(d, line, f_label)
            d.text((x + (cell_w - lw)//2, ly), line, font=f_label, fill=INK)
            ly += 26
    return sheet


# ---- MAIN ----

if __name__ == "__main__":
    print("Rendering variants...")
    A = build_variant_A(); A.save(os.path.join(OUT_DIR, f"menu_{MARKET_DATE}_variant_A.png"), "PNG", optimize=True); print("  A done")
    B = build_variant_B(); B.save(os.path.join(OUT_DIR, f"menu_{MARKET_DATE}_variant_B.png"), "PNG", optimize=True); print("  B done")
    C = build_variant_C(); C.save(os.path.join(OUT_DIR, f"menu_{MARKET_DATE}_variant_C.png"), "PNG", optimize=True); print("  C done")
    D = build_variant_D(); D.save(os.path.join(OUT_DIR, f"menu_{MARKET_DATE}_variant_D.png"), "PNG", optimize=True); print("  D done")
    E = build_variant_E(); E.save(os.path.join(OUT_DIR, f"menu_{MARKET_DATE}_variant_E.png"), "PNG", optimize=True); print("  E done")
    F = build_variant_F(); F.save(os.path.join(OUT_DIR, f"menu_{MARKET_DATE}_variant_F.png"), "PNG", optimize=True); print("  F done")
    G1 = build_variant_G_slide1(); G1.save(os.path.join(OUT_DIR, f"menu_{MARKET_DATE}_variant_G_slide1.png"), "PNG", optimize=True); print("  G1 done")
    G2 = build_variant_G_slide2(); G2.save(os.path.join(OUT_DIR, f"menu_{MARKET_DATE}_variant_G_slide2.png"), "PNG", optimize=True); print("  G2 done")
    G3 = build_variant_G_slide3(); G3.save(os.path.join(OUT_DIR, f"menu_{MARKET_DATE}_variant_G_slide3.png"), "PNG", optimize=True); print("  G3 done")
    sheet = build_contact_sheet([
        ("A — As asked\n(static brand · menu · promo)", A),
        ("B — Video header\n(loop top · menu · brand)", B),
        ("C — Video footer\n(brand · menu · loop)", C),
        ("D — Two-up bottom\n(brand · menu · video | CSA)", D),
        ("E — Equal thirds\n(brand · menu · promo · 33/33/33)", E),
        ("F — Photo-led top\n(hero photo · menu · brand)", F),
        ("G1 — Carousel slide 1\n(brand welcome)", G1),
        ("G2 — Carousel slide 2\n(menu)", G2),
        ("G3 — Carousel slide 3\n(meet your farmer)", G3),
    ])
    sheet.save(os.path.join(OUT_DIR, "contact_sheet.png"), "PNG", optimize=True); print("  contact_sheet done (9 thumbnails)")
    print(f"\nWrote 10 files to {OUT_DIR}")
