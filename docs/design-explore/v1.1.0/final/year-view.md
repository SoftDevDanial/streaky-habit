# P2 Year view of one habit

**Golden** `year-view.html`
**Inventory** P2, the habit's year view (C2 any past day, C3, C4, C6 through Delete habit)
**Opened from** "Year view, Read 20 pages" on K1

## Intent
Show one habit's last 12 months, Friday 10 October 2025 to Saturday 10 October 2026 (366 days), newest month first, so a forgotten day anywhere in the year is one tap to fix.

## What the golden shows
Read 20 pages, Current 4 days, Best 9. 250 done days as amber beads, runs strung on an 8 px amber thread, today (10 October) done with its ink halo. 11 to 31 October 2026 closed and dim, 1 to 9 October 2025 empty. Phone, a full-screen sheet, one month across, 44 px cells, 36 px beads (34 under 380). Desktop, a 980 px dialog over K1 under `--scrim`, three months across, 40 px cells, 32 px beads, the body scrolls inside with its soft edge.

## Exact copy

| Element | Text |
|---|---|
| Title (h2) | Read 20 pages |
| Subtitle | The last 12 months |
| Stats | Current, 4, days. Best, 9 |
| Button | Delete habit, Phosphor trash, quiet |
| Hint | Tap a day to mark it done or not done. |
| Legend | Done, Not done |
| Months | October 2026 down to October 2025, weekday letters M T W T F S S |
| Day names | "Mark Fri 10 Oct 2025 as done" through "Mark Sat 10 Oct 2026 as done", state in `aria-pressed` |

## Ruling 2
Bead numbers are SVG text on the baseline at the bead's centre, dropped `.352em`, proportional figures. Measured ink 0.125 px or less from centre at 390, 0.25 at 1280 (f2 was 0.72 low on a phone).

## Width notes
Desktop day cells are 40 by 40, under 44, inherited from f2 (pointer layout, three months must fit). Listed for the owner in `SELF-CRITIQUE.md`.

## Links
Close, Esc and the backdrop (1280) return to `today.html`. Delete habit opens M1 (`delete-dialog.html` draws M1 for Stretch 10 minutes over K1, the same dialog).
