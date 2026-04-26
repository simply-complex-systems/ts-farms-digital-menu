# ts-farms-digital-menu

Digital menu for the **Barnyard Grill** booth at TS Farms' Saturday market.
Renders a 1080×1920 portrait PNG for an LED standee (HD-M10 controller, loaded
via the LedArt mobile app over Wi-Fi).

First market: **Saturday 2026-05-02**, Montgomery Farmers Market, 9 am.

## What this repo produces

`build_menu.py` writes `output/menu_2026-05-02_portrait.png` — a single-slide
menu image at 1080×1920 with:

- TS Farms chalk logo + Barnyard Grill wordmark + tagline
- **THIS WEEK** ribbon (the modular weekly-special slot)
- Breakfast Sandwiches (Oinker / Clucker / Oinkin' Cluck / Sunny Side Up)
- Sausage Flavors + Ala Carte (side-by-side)
- Burgers (Cheeseburger / Barnyard Burger / Bacon Burger)
- Fries (Fries / Cheese Fries)
- Footer: origin line, market schedule, working QR to `ts-farms.localline.ca`

## Run

```
pip install -r requirements.txt
python build_menu.py
```

Output lands in `output/menu_2026-05-02_portrait.png`. Send that file to the
phone running LedArt and push it to the LED unit.

## Weekly cadence

To refresh the special, edit one line in `build_menu.py`:

```python
special_line = "Your special here"
```

Re-run `python build_menu.py` and re-upload via LedArt.

## Display target

Built to **1080×1920 portrait**. The HD-M10 controller's true native
resolution should be confirmed against the actual unit (LedArt → device
page). When confirmed, update `W, H` in `build_menu.py` and re-export.
The menu re-flows; layout is anchored top-and-bottom with proportional
zones in between.

## Layout zones

| Zone               | Purpose                              | Modular? |
|--------------------|--------------------------------------|----------|
| Header             | Logo + wordmark + tagline            | Stable   |
| **THIS WEEK**      | Weekly special                       | **Swap weekly** |
| Breakfast Sandwiches | Core menu                          | Stable   |
| Sausage Flavors    | Sausage patty options for the Oinker | Update if flavors change |
| Ala Carte          | Add-ons + bottled water              | Stable   |
| Burgers            | Core menu                            | Stable   |
| Fries              | Sides                                | Stable   |
| Footer             | Origin claim, market schedule, QR    | Stable   |

## Repo layout

```
build_menu.py               renderer
requirements.txt            Pillow + segno
assets/
  ts_farms_logo_chalk.png   logo composited into the header
reference/
  barnyard_grill_design_reference.jpeg   the menu we're translating to portrait
  led_unit_ledart_app.jpeg               LedArt pairing flow reference
output/
  menu_2026-05-02_portrait.png           current render
```

## Source content

Menu items, descriptions, and prices come from the existing Barnyard Grill
chalkboard reference at `reference/barnyard_grill_design_reference.jpeg`.
The retail catalog (raw cuts, dairy, eggs, etc.) is *not* on this surface —
that lives at [ts-farms.localline.ca](https://ts-farms.localline.ca) and is
reachable from the QR code on the menu.

## Operations

- **Power-on test**: load the file onto the LED unit a day before market.
  Check legibility from ~8 ft. Confirm no edge clipping.
- **Backup**: keep the latest PNG on the operator's phone gallery and on a
  USB stick. The HD-M10 controllers usually accept USB program load as a
  fallback if Wi-Fi pairing fails on market morning.
- **Paper fallback**: print one copy on letter-size for the booth in case
  the unit fails entirely.
