#!/usr/bin/env python3
"""TS Farms / Barnyard Grill — proof variants for layout review.

Produces a small set of layout variations that test plasticity along the
axes most likely to matter (logo prominence, wordmark presence, promo-zone
content). Each variant renders to output/proofs/<name>.png at full
resolution, plus a single contact sheet at output/proofs/contact_sheet.png
at 25% scale so all variants are visible in one frame.

Variants:
  A_baseline       The canonical build_menu.py output as-is.
  B_logo_dominant  Larger logo, smaller wordmark; logo gets more of
                   the identity zone budget.
  C_logo_only      No wordmark — strictest reading of ONE_EXPRESSIVE_NODE.
                   Identity zone shrinks; menu zone gets the saved space.
  D_promo_image    Promo zone holds a darkened image placeholder + caption,
                   showing what a featured-item shot would look like.

Run:  python3 build_proofs.py
Out:  output/proofs/<variant>.png + output/proofs/contact_sheet.png
"""

from PIL import Image, ImageDraw
import os

import build_menu as bm


HERE = os.path.dirname(os.path.abspath(__file__))
PROOF_DIR = os.path.join(HERE, "output", "proofs")
os.makedirs(PROOF_DIR, exist_ok=True)


# ============================================================================
# Variant A — baseline
# ============================================================================

def variant_a_baseline():
    """The canonical build_menu.py rendering. No overrides."""
    img = bm.build()
    return img


# ============================================================================
# Variant B — logo-dominant identity
# ============================================================================

def variant_b_logo_dominant():
    """Bigger logo, smaller wordmark. Logo earns more of the hook share."""
    img = Image.new("RGB", (bm.W, bm.H), bm.SURFACE)
    draw = ImageDraw.Draw(img)

    # Override identity rendering inline.
    y = bm.MARGIN_TOP

    # Bigger logo — width 880 (was 640).
    logo = Image.open(bm.LOGO_PATH).convert("RGBA")
    logo_w = 880
    logo_h = round(logo.height * (logo_w / logo.width))
    # Cap at zone height minus wordmark + padding.
    smaller_wordmark = bm.T_BODY  # 26 — Level 4, structural
    max_h = bm.ZONE_IDENTITY - smaller_wordmark - bm.PAD_DEFAULT * 2
    if logo_h > max_h:
        logo_h = max_h
        logo_w = round(logo.width * (logo_h / logo.height))
    logo = logo.resize((logo_w, logo_h), Image.LANCZOS)
    img.paste(logo, ((bm.W - logo_w) // 2, y), logo)

    wordmark_y = y + logo_h + bm.PAD_DEFAULT
    bm.draw_centered(draw, wordmark_y, "BARNYARD GRILL", bm.bold(smaller_wordmark))

    y += bm.ZONE_IDENTITY
    bm.draw_divider(img, y)
    bm.render_promo(img, y)
    y += bm.ZONE_PROMO
    bm.draw_divider(img, y)
    bm.render_menu(img, y)
    y += bm.ZONE_MENU
    bm.draw_divider(img, y)
    bm.render_action(img, y)
    return img


# ============================================================================
# Variant C — logo only (no wordmark)
# ============================================================================

def variant_c_logo_only():
    """No wordmark below the logo. Strictest ONE_EXPRESSIVE_NODE.
    Saved vertical space goes to the menu zone."""
    # Re-budget: shrink identity zone, grow menu zone.
    saved = bm.T_WORDMARK + bm.PAD_DEFAULT  # 56 + 16 = 72
    identity_h = bm.ZONE_IDENTITY - saved
    menu_h = bm.ZONE_MENU + saved

    img = Image.new("RGB", (bm.W, bm.H), bm.SURFACE)
    draw = ImageDraw.Draw(img)

    y = bm.MARGIN_TOP

    logo = Image.open(bm.LOGO_PATH).convert("RGBA")
    logo_w = 720
    logo_h = round(logo.height * (logo_w / logo.width))
    if logo_h > identity_h - bm.PAD_DEFAULT:
        logo_h = identity_h - bm.PAD_DEFAULT
        logo_w = round(logo.width * (logo_h / logo.height))
    logo = logo.resize((logo_w, logo_h), Image.LANCZOS)
    # Vertical-center the logo in its zone.
    logo_y = y + (identity_h - logo_h) // 2
    img.paste(logo, ((bm.W - logo_w) // 2, logo_y), logo)

    y += identity_h
    bm.draw_divider(img, y)
    bm.render_promo(img, y)
    y += bm.ZONE_PROMO
    bm.draw_divider(img, y)

    # Menu rendered at original y but with extra room (we trust no overflow).
    bm.render_menu(img, y)
    y += menu_h
    bm.draw_divider(img, y)
    bm.render_action(img, y)
    return img


# ============================================================================
# Variant D — promo with image placeholder
# ============================================================================

def variant_d_promo_image():
    """Promo zone holds a placeholder for a featured-item image with a
    short caption, showing what the layout looks like when a real promo
    image lands. The placeholder is rendered as a flat dark band with
    centered caption to suggest the eventual hero shot."""
    img = Image.new("RGB", (bm.W, bm.H), bm.SURFACE)
    draw = ImageDraw.Draw(img)

    y = bm.MARGIN_TOP
    bm.render_identity(img, y)
    y += bm.ZONE_IDENTITY
    bm.draw_divider(img, y)

    # Custom promo: image-placeholder band + caption
    img_pad = bm.PAD_DEFAULT
    img_box_x0 = bm.MARGIN_X
    img_box_y0 = y + img_pad
    img_box_x1 = bm.W - bm.MARGIN_X
    img_box_y1 = y + bm.ZONE_PROMO - bm.T_BODY - img_pad - bm.PAD_DEFAULT
    draw.rectangle((img_box_x0, img_box_y0, img_box_x1, img_box_y1), fill=(40, 40, 40))
    # Placeholder caption inside the dark band, centered
    placeholder_label = "[ FEATURED ITEM IMAGE ]"
    f_inside = bm.regular(bm.T_BODY)
    pw = bm.text_w(draw, placeholder_label, f_inside)
    ph = bm.text_h(draw, placeholder_label, f_inside)
    draw.text(
        ((bm.W - pw) // 2, (img_box_y0 + img_box_y1 - ph) // 2),
        placeholder_label, font=f_inside, fill=(180, 180, 180),
    )
    # Caption below the band
    cap_y = img_box_y1 + bm.PAD_DEFAULT
    bm.draw_centered(draw, cap_y, "THIS WEEK · " + bm.SPECIAL_LINE, bm.regular(bm.T_BODY))

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

def make_contact_sheet(variants):
    """Compose a 2x2 grid of variants at 25% scale with labels."""
    scale = 0.25
    cell_w = int(bm.W * scale)   # 270
    cell_h = int(bm.H * scale)   # 480
    label_h = 36
    pad = 32

    cols = 2
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
        # Frame
        sd.rectangle((x - 1, y - 1, x + cell_w, y + cell_h), outline=(0, 0, 0), width=1)
        # Label below
        lw = bm.text_w(sd, name, f_label)
        sd.text((x + (cell_w - lw) // 2, y + cell_h + 8), name, font=f_label, fill=(0, 0, 0))

    return sheet


# ============================================================================
# Main
# ============================================================================

VARIANTS = [
    ("A · baseline", variant_a_baseline),
    ("B · logo dominant", variant_b_logo_dominant),
    ("C · logo only", variant_c_logo_only),
    ("D · promo image placeholder", variant_d_promo_image),
]


if __name__ == "__main__":
    rendered = []
    for label, fn in VARIANTS:
        slug = label.split("·")[0].strip().lower().replace(" ", "_")
        img = fn()
        out = os.path.join(PROOF_DIR, f"{slug}.png")
        img.save(out, "PNG", optimize=True)
        rendered.append((label, img))
        print(f"Wrote {out} ({os.path.getsize(out)} bytes)")

    sheet = make_contact_sheet(rendered)
    sheet_path = os.path.join(PROOF_DIR, "contact_sheet.png")
    sheet.save(sheet_path, "PNG", optimize=True)
    print(f"Wrote {sheet_path} ({os.path.getsize(sheet_path)} bytes)")
