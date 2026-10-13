# K1 Today, the key screen

**Golden** `today.html`
**Inventory** K1, habit list with the overview
**System** `system.md`, `system.css`
**Data** `sample-history.json`, today is Saturday 10 October 2026

## Intent
One glance shows what is done today and how long each run has lasted. Ticking today is one tap on Done today. Any past day can be opened from the overview, any day of a habit's last 12 months from its Year button. Only the habit list scrolls. The page never does, and the add field stays put below the list like a chat composer.

## Capabilities shown

| ID | Where |
|---|---|
| C1 Add a habit | "New habit" field and Add under the list |
| C2 Tick today and any past day | Done today on each row. An overview day opens P1 (`day-editor.html`). Year opens P2 (`year-view.html`) |
| C3 Current streak | "4 days", "2 days", "No streak yet" |
| C4 Best streak | "9", "5", "14" under the label Best |
| C5 Overview | The band "Last 12 weeks" from 1024 px, the Overview button below 1024 px (opens P3, `overview.html`). Year on the band opens P4 (`overview-year.html`) |
| C6 Delete a habit | The bin on every row (opens M1, `delete-dialog.html`) |
| C0 Look | Charcoal, one amber accent, the mark in the header |

## States on this screen

| Habit | Current | Best | Done today | Today's ring segment |
|---|---|---|---|---|
| Read 20 pages | 4 days | 9 | pressed, amber fill and check | thick amber (segment 1, from 12 o'clock) |
| Stretch 10 minutes | 2 days | 5 | not pressed | thin grey |
| No phone after 11pm | No streak yet | 14 | not pressed | thin grey |

The band shows 83 days, Monday 20 July to Saturday 10 October, weeks as columns with the newest on the right. Sunday 11 October is an empty cell (after today, closed). Each ring has one segment per habit in list order, clockwise from the top. A done habit is a thick amber arc (3.5), a not-done one a thin grey arc (1.5). A day with all three done fills its core amber and turns its number dark. Today's ring has a thin ink circle round it. Every ring was drawn from `sample-history.json` and the check script compares them one by one.

Below 1024 px the band is hidden. The Overview button carries today's ring (1 of 3) and its name adds ", today 1 of 3 habits done".

Not shown statically. Hover, focus and press (see `states.html`), the field errors (S2 in `states.html`), the save warning (`today-warning.html`), the 12-habit limit (`today-full.html`).

## Exact copy

| Element | Text |
|---|---|
| Page title | Danial's Streaky Habit |
| Brand (h1) | Streaky Habit |
| Date | Saturday 10 October (`<time datetime="2026-10-10">`) |
| Overview button | Overview, accessible name "Overview, today 1 of 3 habits done" |
| Band heading (h2) | Last 12 weeks |
| Band Year button | Year, accessible name "Year view, all habits" |
| Band hint | Tap a day to change it. |
| Band axes | Jul, Aug, Sep, Oct over the first week of each month. M T W T F S S down the side |
| Legend | None, four rings (0, 1, 2 and 3 of 3), All |
| Day names | "Mon 20 Jul, 2 of 3 habits" through "Sat 10 Oct, 1 of 3 habits" |
| List heading (visually hidden h2) | Habits |
| Habit names (h3) | Read 20 pages, Stretch 10 minutes, No phone after 11pm |
| Row labels | Current, Best. Units "days" and "day". "No streak yet" at 0 |
| Bin names | Delete "Read 20 pages" and so on, straight quotes |
| Year names | Year view, Read 20 pages and so on |
| Done today names | Done today, Read 20 pages and so on, state in `aria-pressed` |
| Field label | New habit |
| Button | Add, with Phosphor plus |

## Icons
Phosphor (MIT), inlined once as symbols. Trash (regular) on the bin, check (bold) in the Done today dot, plus (regular) on Add. The mark is `docs/brand/mark.svg` in one inline svg in the header, filled with `--amber` through currentColor, and again as the data URL favicon.

## Layout and sizes that matter

| Item | 360 x 780 | 390 x 844 | 1280 x 800 |
|---|---|---|---|
| App column | 12 side padding, 8 top | 16 side padding, 8 top | max 1040 centred, 12 top, 24 sides |
| Header | mark 28, word 19 bold, Overview button 44 tall at the right, date 14 on its own line | same | mark 32, word 21, date 16 at the right edge, one line |
| Band | hidden | hidden | 180 px left column (title, Year, hint, legend at the foot), grid of a 22 px label column and 12 week columns, 40 px rings in 52 x 44 cells |
| Row | two lines, name and bin, then Current, Best, Year, Done today. 12 top and bottom, 12 sides | same, 14 sides | one line, name, bin in a 56 px column, stats in 200 px, Year, Done today. 12 padding, 20 on the left |
| Row numbers | 22 px, Current amber 700, Best ink 600, tabular figures | same | same, Current block at least 96 wide so Best lines up |
| Buttons on a row | 44 tall, 10 radius, 1.5 ring edge | same | same |
| List frame | as tall as its rows, then scrolls. 16 radius, `--surface` | same | same |
| Composer | label above the field, field 48 tall, Add 48 tall, 8 apart, pinned to the bottom with 12 below | same | label left of the field, one line |

Alignment rules.
- The bin sits on the name line on a phone, top aligned, pulled 10 px up and right so its glyph lines up with the row's right edge. Done today stays on the second line, 12 px of clear space below the bin.
- The band's Year button sits on the title line of the left column, right aligned, never in the ring grid.
- Ring numbers sit on the alphabetic baseline at the ring's centre, dropped `.352em` (f2 used `.367em`, ruling 2), proportional figures. Measured ink centre 0 to 0.25 px from the ring's centre at 1280.

## Width notes
The phone layout (360 and 390) and the desktop layout (1280) are the same file. The band and the one-line rows switch on at 1024 px. Between 768 and 1023 the phone layout still applies, but popups are centred dialogs.

## Links out
Overview (phone) to `overview.html`. Band Year (1280) to `overview-year.html`. Any band day (1280) to `day-editor.html` for Tuesday 22 September. Year on Read 20 pages to `year-view.html`. The bin on Stretch 10 minutes to `delete-dialog.html`. See `LINKS.json`.
