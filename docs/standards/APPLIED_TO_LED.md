# How the standards apply to this LED display

The portrait LED at the booth is a **digital promotion** asset (per
`STYLE_MARKETING.txt`). It competes for attention with every other booth
in the market. The reader did not ask to see it. It has seconds.

This file translates the abstract standard into the concrete decisions
this builder makes.

## Toggle positions

| Toggle               | Position    | Why                                                        |
|----------------------|-------------|------------------------------------------------------------|
| ONE_VOICE            | ON          | One typeface. Hierarchy by size + weight + case only.       |
| ONE_INK              | OFF, strict | Two colors only in v1: ink + surface. No brand color yet.   |
| BREATHE              | FULL        | Generous margins, generous vertical rhythm.                 |
| EARNED_DISTINCTION   | RELAXED     | Reserved for the logo as expressive node. No other ornament.|
| ONE_EXPRESSIVE_NODE  | ON          | The original TS Farms line-art logo carries personality.    |

## Typeface

**DejaVu Sans, regular and bold.** System font on Ubuntu, OFL-licensed,
deliberately neutral. Two weights. No italic. Hierarchy travels through
size and case alone, per ONE_VOICE.

Rejected: chalk-style fonts (decorative, signal "trying"), display fonts
with personality (compete with the logo as expressive node), narrow/condensed
variants (introduce a third weight axis).

## Color

White surface, black ink. Period.

The standard permits a brand-action color via ONE_INK OFF. v1 does not use
one. The hierarchy is intended to work entirely in grayscale per the
STYLE_MARKETING grayscale test. If a CTA-color iteration is wanted later,
it enters as one named color used on one structural role only (the QR/CTA
zone) — not sprinkled.

Why no color in v1: the LED unit will be photographed/screenshot and shared
in many contexts (LedArt previews, phone galleries, paper backups). Pure
black on white survives every translation. It also tests the typographic
hierarchy without color as a crutch.

## Type scale

The root standard's 5-level scale (16, 14, 12, 10, 8 pt) is sized for
print. The LED viewing distance (~8 ft, outdoors, in motion) requires
larger absolute pixels while preserving the same hierarchy ratios.

| Level | Role                          | LED size (px) | Weight  | Case            |
|-------|-------------------------------|---------------|---------|-----------------|
| 1     | Title (BARNYARD GRILL)        | 96            | Bold    | Uppercase       |
| 2     | Section banner                | 56            | Bold    | Uppercase       |
| 3     | Item name                     | 44            | Bold    | Sentence/Title  |
| 4     | Item description              | 30            | Regular | Sentence        |
| 5     | Caption / metadata / footer   | 24            | Regular | Sentence/Upper  |

Plus one expressive size for the promotional headline when present:
**128 px bold uppercase** (Level 1+, headline-as-expressive-node range,
only used when the promo zone has a hero headline rather than an image).

## Layout — Hook → Proof → Action

For a 1080×1920 portrait:

```
0     ┌─────────────────────────────────┐
      │  IDENTITY ZONE  (HOOK)          │  ~200 px
      │  TS Farms logo, centered. No    │
      │  wordmark — the logo + the food │
      │  advertise the booth.           │
280   ├─────────────────────────────────┤
      │                                 │
      │  PROMOTIONAL ZONE  (HOOK)       │  ~160 px
      │  Featured item / video frame    │
      │  / THIS WEEK headline           │
440   ├─────────────────────────────────┤
      │                                 │
      │  MENU ZONE  (PROOF)             │  ~1160 px
      │                                 │
      │  Three sections, even rhythm.   │
      │  Largest share — the proof      │
      │  earns the surface.             │
      │                                 │
1600  ├─────────────────────────────────┤
      │  ACTION ZONE  (ACTION)          │  ~240 px
      │  QR + market info               │
1840  └─────────────────────────────────┘
```

Margins: 80 px each side. Content width: 920 px.

### Wordmark decision (locked 2026-04-26)

The "BARNYARD GRILL" wordmark below the logo was retired. Rationale per
THE_USER: TS Farms is sufficient branding; Tiffany's flat-top grill keeps
people lined up the whole market — the booth doesn't need to advertise
what it is. The logo is the only Level 1 element on the surface. The
wordmark code path was removed from `build_menu.py`.

## The expressive node

The TS Farms line-art logo is the expressive node. It carries personality
(the barn, the cows, the fence, the hand-illustrated typography). Every
other element is structure: clean type, no ornament, even rhythm.

When a featured-item image lands in the promotional zone, that image
becomes the expressive node and the logo recedes to identity-anchor role.
Only one expressive node at a time, per `ONE_EXPRESSIVE_NODE`.

## Symmetry — the perceptual contract

Every margin equals its peer. Every gap between zones is one of a small
set of values. Vertical rhythm cascades predictably. The reader does not
notice the container.

The 8 px grid governs every padding/gap value: {8, 16, 24, 32, 40, 64, 80}.
No odd values. No fractional sizes.

## Survive

The output is a single PNG, 1080×1920, sRGB. No alpha. No transparency.
No exotic codec. It survives every step from build → LedArt upload → LED
display → phone gallery backup → paper printout if needed.

## What the v1 does NOT do (yet)

- Brand-action color on the CTA (intentional — see Color above)
- Promotional video (deferred until LedArt video support is verified)
- Multi-frame slideshow (single static frame is enough for first market)
- Per-item promotional imagery (specials.json holds line + date only;
  extend the schema when a real featured item lands)

These are kept as named gaps so future iterations close them deliberately.
