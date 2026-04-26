#!/usr/bin/env python3
"""Render the TS Farms / Barnyard Grill portrait menu for the LED standee.

Output: 1080x1920 PNG. Loadable on the HD-M10 LedArt app as a single slide.
Iteration 1: layout + content. Native panel resolution to be confirmed and
re-exported once we have it.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import segno
import os
import io
import math
import random

# ---- canvas ----
W, H = 1080, 1920
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "output", "menu_2026-05-02_portrait.png")
LOGO_PATH = os.path.join(HERE, "assets", "ts_farms_logo_chalk.png")

# ---- palette ----
BG_DARK = (22, 22, 22)
BG_GRAD = (34, 34, 34)
INK = (245, 240, 230)
INK_DIM = (190, 185, 175)
YELLOW = (245, 197, 24)
YELLOW_DARK = (210, 160, 0)
RED_ACCENT = (200, 60, 50)

# ---- fonts ----
F_DISPLAY = "/usr/share/fonts/truetype/noto/NotoSans-Black.ttf"
F_DISPLAY_FALLBACK = "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf"
F_BODY_BOLD = "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf"
F_BODY = "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf"
F_NARROW_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSansNarrow-Bold.ttf"
F_ITALIC = "/usr/share/fonts/truetype/ubuntu/Ubuntu-RI.ttf"

def font(path, size):
    if not os.path.exists(path):
        path = F_DISPLAY_FALLBACK
    return ImageFont.truetype(path, size)

# ---- background with chalkboard speckle ----
img = Image.new("RGB", (W, H), BG_DARK)
draw = ImageDraw.Draw(img)
# subtle vertical gradient
for y in range(H):
    t = y / H
    r = int(BG_DARK[0] + (BG_GRAD[0]-BG_DARK[0]) * t)
    g = int(BG_DARK[1] + (BG_GRAD[1]-BG_DARK[1]) * t)
    b = int(BG_DARK[2] + (BG_GRAD[2]-BG_DARK[2]) * t)
    draw.line([(0, y), (W, y)], fill=(r, g, b))

# chalk speckle / texture
random.seed(1)
for _ in range(2400):
    x = random.randint(0, W-1)
    y = random.randint(0, H-1)
    a = random.randint(8, 26)
    draw.point((x, y), fill=(a+30, a+30, a+30))
# faint horizontal smudges
for _ in range(60):
    x = random.randint(0, W-200)
    y = random.randint(0, H-1)
    L = random.randint(40, 220)
    c = random.randint(28, 44)
    draw.line([(x, y), (x+L, y)], fill=(c, c, c))


def text_w(d, s, fnt):
    bbox = d.textbbox((0, 0), s, font=fnt)
    return bbox[2] - bbox[0]
def text_h(d, s, fnt):
    bbox = d.textbbox((0, 0), s, font=fnt)
    return bbox[3] - bbox[1]


# ---- Yellow brushy banner ----
def brush_banner(d, x, y, w, h, label, label_font, fill=YELLOW, text_color=(20,20,20)):
    # main rounded rect with mild rotation feel via offset corners
    pad = 6
    rect = (x, y, x+w, y+h)
    d.rounded_rectangle(rect, radius=14, fill=fill)
    # ragged edge marks
    for i in range(8):
        dx = random.randint(-10, 10)
        dy = random.randint(-3, 3)
        d.ellipse((x-12+dx, y+5+dy, x-2+dx, y+h-5+dy), fill=fill)
        d.ellipse((x+w-8+dx, y+5+dy, x+w+10+dx, y+h-5+dy), fill=fill)
    # darker bottom shadow
    d.rounded_rectangle((x+3, y+h-8, x+w-3, y+h-2), radius=6, fill=YELLOW_DARK)
    tw = text_w(d, label, label_font)
    th = text_h(d, label, label_font)
    d.text((x + w/2 - tw/2, y + h/2 - th/1.5), label, font=label_font, fill=text_color)


def hr(y, color=(60,60,60), thickness=2, x1=80, x2=W-80):
    draw.line([(x1, y), (x2, y)], fill=color, width=thickness)


# ====================================================================
# HEADER — TS FARMS logo centered, BARNYARD GRILL wordmark below, tagline
# ====================================================================
HDR_TOP = 24

# logo centered
logo = Image.open(LOGO_PATH).convert("RGBA")
lw = 280
lh = int(logo.height * (lw / logo.width))
logo = logo.resize((lw, lh), Image.LANCZOS)
img.paste(logo, ((W - lw)//2, HDR_TOP), logo)

# Title block centered below logo
def draw_shadowed(d, xy, txt, fnt, fill, shadow=(0,0,0), offset=4):
    x, y = xy
    d.text((x+offset, y+offset), txt, font=fnt, fill=shadow)
    d.text((x, y), txt, font=fnt, fill=fill)

# BARNYARD GRILL on one line, sized to fit
f_title = font(F_DISPLAY, 96)
title_text = "BARNYARD GRILL"
tw = text_w(draw, title_text, f_title)
title_y = HDR_TOP + lh + 8
# yellow BARNYARD + ink GRILL: render as two pieces to preserve color split
f_b = font(F_DISPLAY, 96)
barn_w = text_w(draw, "BARNYARD ", f_b)
grill_w = text_w(draw, "GRILL", f_b)
total_w = barn_w + grill_w
sx = (W - total_w) // 2
draw_shadowed(draw, (sx, title_y), "BARNYARD", f_b, YELLOW)
draw_shadowed(draw, (sx + barn_w, title_y), "GRILL", f_b, INK)

# tagline centered
f_tag = font(F_ITALIC, 34)
tagline = "Where the farm meets the flame"
tagw = text_w(draw, tagline, f_tag)
draw.text(((W - tagw)//2, title_y + 110), tagline, font=f_tag, fill=INK_DIM)

# ====================================================================
# THIS WEEK ribbon
# ====================================================================
TW_Y = 410
brush_banner(draw, 80, TW_Y, W-160, 72, "THIS WEEK",
             font(F_DISPLAY, 44))
# placeholder special text — farmer/THE_USER swaps weekly
f_special = font(F_BODY_BOLD, 32)
special_line = "First market of the season — say hi at the booth!"
sw = text_w(draw, special_line, f_special)
draw.text((W/2 - sw/2, TW_Y + 84), special_line, font=f_special, fill=INK)

# ====================================================================
# BREAKFAST SANDWICHES
# ====================================================================
BS_Y = 560
brush_banner(draw, 80, BS_Y, 580, 60, "BREAKFAST SANDWICHES",
             font(F_DISPLAY, 32))

f_item = font(F_BODY_BOLD, 38)
f_price = font(F_NARROW_BOLD, 38)
f_desc = font(F_BODY, 22)

def menu_row(y, name, price, desc, x=80, total_w=W-160):
    draw.text((x, y), name, font=f_item, fill=INK)
    pw = text_w(draw, f"${price}", f_price)
    draw.text((x + total_w - pw, y), f"${price}", font=f_price, fill=YELLOW)
    # dotted leader
    nw = text_w(draw, name, f_item)
    leader_x1 = x + nw + 18
    leader_x2 = x + total_w - pw - 14
    if leader_x2 > leader_x1:
        for lx in range(leader_x1, leader_x2, 12):
            draw.ellipse((lx, y+26, lx+3, y+29), fill=(80,80,80))
    if desc:
        words = desc.split()
        line = ""
        ly = y + 48
        max_w = total_w
        for word in words:
            test = (line + " " + word).strip()
            if text_w(draw, test, f_desc) > max_w:
                draw.text((x, ly), line, font=f_desc, fill=INK_DIM)
                ly += 28
                line = word
            else:
                line = test
        if line:
            draw.text((x, ly), line, font=f_desc, fill=INK_DIM)
        return ly + 30
    return y + 52

y = BS_Y + 80
y = menu_row(y, "OINKER", "10",
             "Sausage patty (your choice of flavor), cheese, egg, lettuce, tomato — hand-crafted English Muffin")
y = menu_row(y, "CLUCKER", "10",
             "Chicken sausage patty, cheese, egg, lettuce, tomato — hand-crafted English Muffin")
y = menu_row(y, "OINKIN' CLUCK", "10",
             "Bacon, egg, cheese, lettuce, tomato — hand-crafted English Muffin")
y = menu_row(y, "SUNNY SIDE UP", "9",
             "Two fried eggs, cheese, lettuce, tomato — hand-crafted English Muffin")

BS_END = y + 8

# ====================================================================
# SAUSAGE FLAVORS + ALA CARTE — side by side
# ====================================================================
SA_Y = BS_END + 6

# left block: Sausage flavors
brush_banner(draw, 80, SA_Y, 460, 54, "SAUSAGE FLAVORS",
             font(F_DISPLAY, 28))
f_flavor = font(F_BODY_BOLD, 28)
flavors = ["Apple Maple", "Breakfast", "Jalapeño Chipotle"]
for i, fl in enumerate(flavors):
    draw.text((100, SA_Y + 70 + i*36), f"•  {fl}", font=f_flavor, fill=INK)

# right block: Ala carte
brush_banner(draw, 560, SA_Y, 440, 54, "ALA CARTE",
             font(F_DISPLAY, 30))
f_alc_item = font(F_BODY_BOLD, 28)
f_alc_price = font(F_NARROW_BOLD, 28)
ala = [("Fried Egg", "1"), ("Double Meat", "2.50"), ("Bottled Water", "1.50")]
for i, (n, p) in enumerate(ala):
    yy = SA_Y + 70 + i*36
    draw.text((580, yy), n, font=f_alc_item, fill=INK)
    pw = text_w(draw, f"${p}", f_alc_price)
    draw.text((1000-pw, yy), f"${p}", font=f_alc_price, fill=YELLOW)

SA_END = SA_Y + 70 + 3*36 + 8

# ====================================================================
# BURGERS
# ====================================================================
BG_Y = SA_END + 8
brush_banner(draw, 80, BG_Y, 380, 60, "BURGERS",
             font(F_DISPLAY, 36))

y = BG_Y + 80
y = menu_row(y, "CHEESEBURGER", "9",
             "4oz beef patty, cheese — hand-crafted bun")
y = menu_row(y, "BARNYARD BURGER", "12",
             "4oz beef patty, egg, cheese, lettuce, tomato, pickle, onion — hand-crafted bun")
y = menu_row(y, "BACON BURGER", "13",
             "4oz beef patty, bacon, cheese, lettuce, tomato, pickle, onion — hand-crafted bun")

BG_END = y + 4

# ====================================================================
# FRIES — two-up
# ====================================================================
FR_Y = BG_END
brush_banner(draw, 80, FR_Y, 280, 54, "FRIES",
             font(F_DISPLAY, 30))
f_fr_item = font(F_BODY_BOLD, 30)
draw.text((100, FR_Y + 68), "Fries", font=f_fr_item, fill=INK)
draw.text((420, FR_Y + 68), "$4", font=font(F_NARROW_BOLD, 32), fill=YELLOW)
draw.text((560, FR_Y + 68), "Cheese Fries", font=f_fr_item, fill=INK)
draw.text((950, FR_Y + 68), "$5", font=font(F_NARROW_BOLD, 32), fill=YELLOW)

FR_END = FR_Y + 54 + 56

# ====================================================================
# FOOTER — origin line + QR + market info
# Anchor footer to the bottom so it always renders
# ====================================================================
FT_BLOCK_H = 270
FT_Y = H - FT_BLOCK_H - 30

hr(FT_Y - 14, color=(60,60,60), thickness=2)

# QR code on right
qr = segno.make("https://ts-farms.localline.ca", error="H")
qr_buf = io.BytesIO()
qr.save(qr_buf, kind="png", scale=10, dark="#f5f0e6", light="#1a1a1a", border=1)
qr_buf.seek(0)
qr_img = Image.open(qr_buf).convert("RGB")
qr_size = 200
qr_img = qr_img.resize((qr_size, qr_size), Image.NEAREST)
img.paste(qr_img, (W - qr_size - 80, FT_Y))

# left text block
f_origin = font(F_BODY_BOLD, 26)
f_origin_sm = font(F_BODY, 22)
f_market_hdr = font(F_DISPLAY, 30)
draw.text((80, FT_Y), "All meats come from our farm.", font=f_origin, fill=INK)
draw.text((80, FT_Y + 34), "We only use local produce.", font=f_origin, fill=INK)
draw.text((80, FT_Y + 84), "Find us at Montgomery Farmers Market", font=f_market_hdr, fill=YELLOW)
draw.text((80, FT_Y + 122), "Saturdays 9 am — May through October", font=f_origin_sm, fill=INK_DIM)

# QR caption (centered under QR)
f_qrcap = font(F_BODY_BOLD, 20)
qr_x = W - qr_size - 80
cap1 = "ORDER ANYTIME"
cw = text_w(draw, cap1, f_qrcap)
draw.text((qr_x + qr_size/2 - cw/2, FT_Y + qr_size + 4), cap1, font=f_qrcap, fill=YELLOW)
cap2 = "ts-farms.localline.ca"
cw2 = text_w(draw, cap2, f_origin_sm)
draw.text((qr_x + qr_size/2 - cw2/2, FT_Y + qr_size + 28), cap2, font=f_origin_sm, fill=INK_DIM)

# bottom signature
f_sig = font(F_ITALIC, 22)
sig = "TS Farms · New Vienna, Ohio · (937) 763-3917"
sw = text_w(draw, sig, f_sig)
draw.text((W/2 - sw/2, H - 50), sig, font=f_sig, fill=INK_DIM)

# Save
os.makedirs(os.path.dirname(OUT), exist_ok=True)
img.save(OUT, "PNG", optimize=True)
print(f"Wrote {OUT} ({os.path.getsize(OUT)} bytes)")
