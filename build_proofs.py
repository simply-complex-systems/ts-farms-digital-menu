#!/usr/bin/env python3
"""TS Farms / Barnyard Grill — proof variants for layout review.

Renders a 2x3 matrix of layout options for Tiffany's review:

                Text promo      Image promo       Video promo
  No wordmark   A1              B1                C1
  With BG       A2              B2                C2

Each variant is the same canonical layout governed by
docs/standards/STYLE_MARKETING.txt — the only differences are:

  - Whether "BARNYARD GRILL" appears below the logo (sub-brand label)
  - Whether the promo zone holds a text headline, a featured-item image
    placeholder, or a video frame placeholder

Run:  python3 build_proofs.py
Out:  output/proofs/<slug>.png at full 1080x1920
      output/proofs/contact_sheet.png at 25% scale, 2x3 grid with labels
"""

from PIL import Image, ImageDraw
import os

import build_menu as bm


HERE = os.path.dirname(os.path.abspath(__file__))
PROOF_DIR = os.path.join(HERE, "output", "proofs")
os.makedirs(PROOF_DIR, exist_ok=True)


# ============================================================================
# Identity rendering — parameterized
# ============================================================================

def render_identity_param(img, y_start, *, with_wordmark: bool):
    """Identity zone with optional wordmark. When wordmark is absent, the
    logo gets the full identity zone (vertically centered)."""
    draw = ImageDraw.Draw(img)

    if with_wordmark:
        wordmark_h = bm.T_WORDMARK + bm.PAD_DEFAULT
        logo_max_h = bm.ZONE_IDENTITY - wordmark_h - bm.PAD_DEFAULT
    else:
        logo_max_h = bm.ZONE_IDENTITY - bm.PAD_DEFAULT

    logo = Image.open(bm.LOGO_PATH).convert("RGBA")
    logo_w = 720 if not with_wordmark else 640
    logo_h = round(logo.height * (logo_w / logo.width))
    if logo_h > logo_max_h:
        logo_h = logo_max_h
        logo_w = round(logo.width * (logo_h / logo.height))
    logo = logo.resize((logo_w, logo_h), Image.LANCZOS)

    if with_wordmark:
        logo_y = y_start
    else:
        # Center the logo in its zone
        logo_y = y_start + (bm.ZONE_IDENTITY - logo_h) // 2

    img.paste(logo, ((bm.W - logo_w) // 2, logo_y), logo)

    if with_wordmark:
        wordmark_y = logo_y + logo_h + bm.PAD_DEFAULT
        bm.draw_centered(draw, wordmark_y, "BARNYARD GRILL", bm.bold(bm.T_WORDMARK))


# ============================================================================
# Promo rendering — parameterized
# ============================================================================

def render_promo_text(img, y_start):
    """Text-only: THIS WEEK header + special line."""
    bm.render_promo(img, y_start)


def render_promo_image(img, y_start):
    """Featured-item image placeholder: dark band with centered caption,
    THIS WEEK + special line below."""
    draw = ImageDraw.Draw(img)
    pad = bm.PAD_DEFAULT
    cap_h = bm.T_BODY + pad

    box = (bm.MARGIN_X, y_start + pad,
           bm.W - bm.MARGIN_X, y_start + bm.ZONE_PROMO - cap_h - pad)
    draw.rectangle(box, fill=(40, 40, 40))

    label = "[ FEATURED ITEM IMAGE ]"
    f = bm.regular(bm.T_BODY)
    lw = bm.text_w(draw, label, f)
    lh = bm.text_h(draw, label, f)
    cx = (bm.W - lw) // 2
    cy = (box[1] + box[3] - lh) // 2
    draw.text((cx, cy), label, font=f, fill=(180, 180, 180))

    cap_y = box[3] + pad
    bm.draw_centered(draw, cap_y, "THIS WEEK · " + bm.SPECIAL_LINE, f)


def render_promo_video(img, y_start):
    """Video frame placeholder: dark band + play-triangle glyph, caption
    below identifies it as the video slot."""
    draw = ImageDraw.Draw(img)
    pad = bm.PAD_DEFAULT
    cap_h = bm.T_BODY + pad

    box = (bm.MARGIN_X, y_start + pad,
           bm.W - bm.MARGIN_X, y_start + bm.ZONE_PROMO - cap_h - pad)
    draw.rectangle(box, fill=(20, 20, 20))

    # Play-triangle, centered in the band
    bx0, by0, bx1, by1 = box
    cx = (bx0 + bx1) // 2
    cy = (by0 + by1) // 2
    tri_size = 36
    triangle = [
        (cx - tri_size // 2, cy - tri_size),
        (cx - tri_size // 2, cy + tri_size),
        (cx + tri_size, cy),
    ]
    draw.polygon(triangle, fill=(220, 220, 220))

    # Caption below the band
    cap_y = box[3] + pad
    bm.draw_centered(draw, cap_y, "THIS WEEK · PROMO VIDEO", bm.regular(bm.T_BODY))


PROMO_RENDERERS = {
    "text": render_promo_text,
    "image": render_promo_image,
    "video": render_promo_video,
}


# ============================================================================
# Variant builder — composes a full image from parameters
# ============================================================================

def build_variant(*, with_wordmark: bool, promo_kind: str):
    img = Image.new("RGB", (bm.W, bm.H), bm.SURFACE)

    y = bm.MARGIN_TOP
    render_identity_param(img, y, with_wordmark=with_wordmark)
    y += bm.ZONE_IDENTITY
    bm.draw_divider(img, y)

    PROMO_RENDERERS[promo_kind](img, y)
    y += bm.ZONE_PROMO
    bm.draw_divider(img, y)

    bm.render_menu(img, y)
    y += bm.ZONE_MENU
    bm.draw_divider(img, y)

    bm.render_action(img, y)
    return img


# ============================================================================
# Contact sheet
# ============================================================================

def make_contact_sheet(variants, cols=3):
    """Compose grid of variants at 25% scale with labels."""
    scale = 0.25
    cell_w = int(bm.W * scale)
    cell_h = int(bm.H * scale)
    label_h = 36
    pad = 32

    rows = (len(variants) + cols - 1) // cols
    sheet_w = pad + cols * (cell_w + pad)
    sheet_h = pad + rows * (cell_h + label_h + pad)

    sheet = Image.new("RGB", (sheet_w, sheet_h), bm.SURFACE)
    sd = ImageDraw.Draw(sheet)
    f_label = bm.bold(20)

    for i, (name, img) in enumerate(variants):
        col = i % cols
        row = i // cols
        x = pad + col * (cell_w + pad)
        y = pad + row * (cell_h + label_h + pad)
        thumb = img.resize((cell_w, cell_h), Image.LANCZOS)
        sheet.paste(thumb, (x, y))
        sd.rectangle((x - 1, y - 1, x + cell_w, y + cell_h), outline=(0, 0, 0), width=1)
        lw = bm.text_w(sd, name, f_label)
        sd.text((x + (cell_w - lw) // 2, y + cell_h + 8), name, font=f_label, fill=(0, 0, 0))

    return sheet


# ============================================================================
# Main
# ============================================================================

# 2x3 matrix: rows = wordmark on/off, cols = promo kind
VARIANTS = [
    # Top row — no Barnyard Grill wordmark
    ("A1 · logo only · text",   {"with_wordmark": False, "promo_kind": "text"}),
    ("B1 · logo only · image",  {"with_wordmark": False, "promo_kind": "image"}),
    ("C1 · logo only · video",  {"with_wordmark": False, "promo_kind": "video"}),
    # Bottom row — with Barnyard Grill wordmark
    ("A2 · with BG · text",     {"with_wordmark": True,  "promo_kind": "text"}),
    ("B2 · with BG · image",    {"with_wordmark": True,  "promo_kind": "image"}),
    ("C2 · with BG · video",    {"with_wordmark": True,  "promo_kind": "video"}),
]


if __name__ == "__main__":
    rendered = []
    for label, params in VARIANTS:
        slug = label.split("·")[0].strip().lower()
        img = build_variant(**params)
        out = os.path.join(PROOF_DIR, f"{slug}.png")
        img.save(out, "PNG", optimize=True)
        rendered.append((label, img))
        print(f"Wrote {out} ({os.path.getsize(out)} bytes)")

    sheet = make_contact_sheet(rendered, cols=3)
    sheet_path = os.path.join(PROOF_DIR, "contact_sheet.png")
    sheet.save(sheet_path, "PNG", optimize=True)
    print(f"Wrote {sheet_path} ({os.path.getsize(sheet_path)} bytes)")
