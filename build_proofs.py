#!/usr/bin/env python3
"""TS Farms / Barnyard Grill — proof variants for layout review.

Three variants, one per promo treatment, all sharing the canonical
identity/menu/action zones from build_menu.py:

  A · text     THIS WEEK headline + special line (the v1 ship)
  B · image    featured-item image placeholder + caption (when a hero
               photograph lands)
  C · video    promo video frame placeholder + caption (when LedArt
               video support is verified and an asset exists)

The wordmark axis was retired 2026-04-26: the TS Farms logo is
sufficient branding, the food advertises the booth.

Run:  python3 build_proofs.py
Out:  output/proofs/<slug>.png at full 1080x1920
      output/proofs/contact_sheet.png at 25% scale, 1x3 grid with labels
"""

from PIL import Image, ImageDraw
import os

import build_menu as bm


HERE = os.path.dirname(os.path.abspath(__file__))
PROOF_DIR = os.path.join(HERE, "output", "proofs")
os.makedirs(PROOF_DIR, exist_ok=True)


# ============================================================================
# Promo renderers — parameterized
# ============================================================================

def render_promo_text(img, y_start):
    """Text-only: THIS WEEK header + special line. The v1 ship."""
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

    cap_y = box[3] + pad
    bm.draw_centered(draw, cap_y, "THIS WEEK · PROMO VIDEO", bm.regular(bm.T_BODY))


PROMO_RENDERERS = {
    "text": render_promo_text,
    "image": render_promo_image,
    "video": render_promo_video,
}


# ============================================================================
# Variant builder
# ============================================================================

def build_variant(promo_kind: str):
    img = Image.new("RGB", (bm.W, bm.H), bm.SURFACE)

    y = bm.MARGIN_TOP
    bm.render_identity(img, y)
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

VARIANTS = [
    ("A · text",  "text"),
    ("B · image", "image"),
    ("C · video", "video"),
]


if __name__ == "__main__":
    rendered = []
    for label, kind in VARIANTS:
        slug = label.split("·")[0].strip().lower()
        img = build_variant(kind)
        out = os.path.join(PROOF_DIR, f"{slug}.png")
        img.save(out, "PNG", optimize=True)
        rendered.append((label, img))
        print(f"Wrote {out} ({os.path.getsize(out)} bytes)")

    sheet = make_contact_sheet(rendered, cols=3)
    sheet_path = os.path.join(PROOF_DIR, "contact_sheet.png")
    sheet.save(sheet_path, "PNG", optimize=True)
    print(f"Wrote {sheet_path} ({os.path.getsize(sheet_path)} bytes)")
