# 0001 — Build menu to 1080×1920 portrait, iterate from there

- **Status**: Accepted
- **Date**: 2026-04-26
- **Deciders**: Eric Pedersen
- **Context issue**: (no separate issue — locked during initial grounding session)

## Context

The booth display is an HD-M10-controlled LED standee uploaded via the LedArt
mobile app over Wi-Fi. The unit's true native pixel dimensions are not yet
confirmed (the controller and panel combo determine native resolution; common
totem sizes are 192×320, 320×576, 384×640, 640×1152). Confirming requires
either physically inspecting the unit or screenshotting LedArt's device page,
neither of which is on the critical path before the May 2nd opening market.

## Decision

We will build the v1 menu to **1080×1920 portrait PNG**, ship the file to
the farmer, and iterate to the unit's true native resolution once LedArt
either accepts or rejects/crops the file.

## Alternatives considered

### A. Block on confirming native resolution first

Rejected: adds days to the timeline before any iteration is possible, and
the layout is anchored top-and-bottom with proportional zones — re-export
to a different size is mechanical, not a redesign.

### B. Generate at every common HD-M10 native resolution upfront

Rejected: premature work. Most LED panels with HD-M10 controllers accept
upscaling/downscaling on load; the unit will tell us if it doesn't. Building
five variants now is YAGNI.

## Consequences

### Positive

- Unblocks the farmer to test the load-to-LedArt flow immediately.
- Layout decisions get exercised before native-resolution lock-in.
- Build script is path-independent and re-exports trivially.

### Negative

- One re-export step expected after confirmation.
- If the LED unit silently distorts the aspect ratio, we won't know without
  physical inspection. Mitigation: paper backup at first market.

### Neutral / open

- Will revisit after first market with empirical data on the unit.
