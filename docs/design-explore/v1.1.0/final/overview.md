# P3 Overview popup (phone)

**Golden** `overview.html`
**Inventory** P3, the overview on a phone (C5)
**Opened from** the Overview button in K1's header, below 1024 px only

## Intent
Give the phone the same 12 weeks the desktop band shows, sized for a thumb, and a way into any day (P1) and into the year (P4).

## What the golden shows
A full-screen sheet. Head with the title, hint, Year and Close. Weeks as rows, newest on top (5 to 10 October first), a 34 px month column, M T W T F S S across the top, the None to All legend right aligned under the grid. Rings 42 px in 48 px cells at 390, 40 in 46 at 360, numbers 16.8 and 16 px. Today's ring has the ink circle. Sunday 11 October is an empty cell.

The 1280 render shows the centred 520 px dialog P3 becomes from 768 px, over K1. It is for reference only. At 1024 px and up the Overview button is hidden, the band in `today.html` is the overview, and P3 cannot open. K1 underneath is today.html's K1, band included, so every popup golden draws the same K1.

## Exact copy

| Element | Text |
|---|---|
| Title (h2) | Last 12 weeks |
| Hint | Tap a day to change it. |
| Year | Year, accessible name "Year view, all habits" |
| Close | "Close" |
| Day names | "Mon 20 Jul, 2 of 3 habits" through "Sat 10 Oct, 1 of 3 habits" |
| Legend | None, All |

## Width notes
At 360 a cell is 43.1 wide by 46 tall, inherited from f2 (the round 1 brief allows 40 at 360).

## Links
A day to `day-editor.html` (22 September). Year to `overview-year.html`. Close and Esc to `today.html`.
