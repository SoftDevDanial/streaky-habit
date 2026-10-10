# P1 Day editor

**Golden** `day-editor.html`
**Inventory** P1, day editor (capability C2, any past day)
**Opened from** a day in the band (1280) or in P3 (phone), shown here for Tuesday 22 September 2026

## Intent
Fix any day for every habit at once. One tick per habit, and a tick moves that habit's Current and Best, the day's ring everywhere and today's ring if the day is today.

## What the golden shows

| Width | Layers, bottom to top |
|---|---|
| 360, 390 | P3 (full-screen sheet, the 22 September cell outlined), `--scrim-soft`, P1 as a bottom sheet. The chosen day stays in sight above the sheet |
| 1280 | K1 with the band (22 September outlined), `--scrim-soft`, P1 as a centred 440 px dialog |

The outlined day is the open state. `--raise` fill, a 1.5 `--amber` inset outline, and its thin not-done segments drawn in `--ink-soft` (ruling 1, 5.17 to 1 on `--raise`).

## Exact copy

| Element | Text |
|---|---|
| Title (h2) | Tuesday 22 September |
| Subtitle | 1 of 3 habits |
| Close | accessible name "Close", Phosphor x |
| Ticks | Read 20 pages, "Current 4 days", "Best 9" (off). Stretch 10 minutes, "Current 2 days", "Best 5" (off). No phone after 11pm, "No streak yet", "Best 14" (on) |

Current and Best in a tick are the habit's own numbers today, not as of the chosen day.

## Sizes that matter
Head grid 56 / text / 44, 12 apart. Mini ring 56 px, no number. Ticks at least 60 tall, 28 px round box, name 16/22 600, stats 13/18. Phone sheet padding 16 with 24 at the bottom, 20 radius on the top corners, at most 85% of the screen. Desktop padding 20, 20 radius.

## States not drawn
Hover on a tick (`--raise`), focus (ring inside the tick), the box popping after a tick.

## Links
Close, Esc or the backdrop return to `overview.html` on a phone and to `today.html` on a desktop. A tick stays in P1.
