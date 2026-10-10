# P4 Overview year view

**Golden** `overview-year.html`
**Inventory** P4, every habit together over the last 12 months (C5)
**Opened from** "Year view, all habits", the Year button on the band (1280) or in P3's head (phone)

## Intent
The overview's own year. Every day of P2's 366 is drawn as the overview's ring, so a day reads the same in the band, P3, P4 and P1.

## What the golden shows
Months newest first, October 2026 to October 2025. 366 ring buttons, 21 closed days (11 to 31 October 2026, number only in `--closed` 500), 9 empty days (1 to 9 October 2025). Phone, a full-screen sheet over P3 (P3 is fully covered and not drawn), one month across, 42 px rings in 48 px cells (40 in 46 under 380). Desktop, a centred 980 px dialog over K1 under `--scrim`, three months across in 42 px columns, 40 px rings in 44 px cells, numbers 16 px. K1 is drawn without its band, which P4 covers except for 5 px at each side.

## Exact copy

| Element | Text |
|---|---|
| Title (h2) | All habits |
| Subtitle | The last 12 months |
| Hint | Tap a day to change it. |
| Legend | None, four rings, All |
| Day names | "Fri 10 Oct 2025, 3 of 3 habits" through "Sat 10 Oct 2026, 1 of 3 habits", with the year because P4 holds two Octobers |

## Width notes
Desktop cells are 42 by 44, under 44 wide, inherited from f2 (reading 20, three months across). Listed in `SELF-CRITIQUE.md`.

## Links
A day to `day-editor.html`. Close and Esc to `overview.html` on a phone and to `today.html` on a desktop, the backdrop to `today.html` (1280).
