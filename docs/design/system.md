# Danial's Streaky Habit, design system v1.1.0

**Phase** design, steps 5, 6 and 8
**Date** 2026-10-11
**Direction** round 2 F2 "Orbit List, revised" (`round-2/f2.html`, `f2.md`, `f.md`), accepted by the owner ("Both looks good. We can procceed as usual")
**Tokens** `system.css`. Every golden inlines it byte for byte, and the check script compares each golden's style block with it
**Data** `sample-history.json` is the one source for every figure in every golden

## Skills loaded and what they changed

| Skill | Loaded | What transferred | What did not, and why |
|---|---|---|---|
| `taste-skill:taste-skill` | yes, invoked | Zero long dashes. One accent (amber) locked across every screen, one danger colour used only for errors and delete. A written radius rule. Button, form and focus contrast recorded for every pair. Label above the field on a phone, message next to the field it is about, no placeholder as label. Empty, error and full states designed. Press feedback by scale. Motion only as feedback, off under reduced motion. Phosphor icons only. No eyebrows, no middle-dot strings, no decorative dots. Copy self-audit | React, Tailwind, Motion, web fonts and the image strategy are ruled out by the stack (static page, zero dependencies, offline). Its dark-mode pairing rule is replaced by the brief (one theme, a switcher is a non-goal). Hero, landing and bento rules do not apply to a one-screen tool |
| `frontend-design:frontend-design` | yes, invoked | One memorable element (the orbit ring, one segment per habit), everything round it quiet. A compact palette of named roles. Plain, active copy (Done today, Add, Delete habit). Motion that answers an action, never on load. Structure that carries information, never decoration | Its push for a distinctive typeface is overridden by the brief (system font stacks only) |

Design read. A personal one-screen habit tool for one person on a phone, dark charcoal with one amber accent, plain CSS and SVG on system fonts, with the orbit ring as the single expressive element. Not a redesign. f2 is locked as it rendered, with the three compose rulings applied.

## Principles
1. **The ring is the day.** One segment per habit, clockwise from the top in list order. Done is a thick amber arc, not done a thin grey one, a full day fills its core. A day reads the same in the band, P3, P4 and P1's mini ring.
2. **The bead is a habit's day.** Done is a filled amber bead with a dark number, not done a hollow ring, and consecutive done days hang on one amber thread like the mark.
3. **Done differs by more than colour.** Stroke width and fill, never hue alone.
4. **Only the list scrolls.** The page is one screen tall at every width. The add field never moves.
5. **Numbers centre by their ink.** Every number in a ring or bead is SVG text on its alphabetic baseline at the shape's centre, dropped `.352em` (the measured half height of the figures), in proportional figures.

## Colour roles

| Token | Value | Role and where it is used |
|---|---|---|
| `--bg` | #18191C | Page background. The text colour on amber and danger fills (as `--on-amber`) |
| `--surface` | #212226 | Band, list frame, composer. The cards of the main screen |
| `--surface-2` | #2A2B30 | Dialogs and sheets (P1, P2, P3, P4, M1), the S5 note, a not-done bead's fill, the disabled field |
| `--raise` | #35373D | Hover fill of buttons, ticks and day cells, the open day's fill |
| `--field` | #121316 | Text field fill |
| `--line` | #33353B | Hairlines. Frame and card edges, row dividers, sheet head divider (decorative) |
| `--track` | #4A4C53 | The empty-state core circle (decorative) |
| `--ring` | #7C7F88 | Every not-done outline. Thin segments, bead edges, tick boxes, the Done today dot, outline button edges, the field border |
| `--ink` | #EDEEF0 | Primary text, today's ring circle and bead halo, the focus ring (as `--focus`) |
| `--ink-soft` | #A8ABB2 | Secondary text, day numbers, icons at rest, and (ruling 1) a thin not-done segment on a hovered or open day |
| `--closed` | #5C5E66 | Day numbers after today in P2 and P4 (inactive) |
| `--amber` | #FFB020 | The one accent. Done segments, full cores, done beads and their thread, Current, Done today pressed, Add, the open day outline, the S4 banner edge, the mark |
| `--amber-hover` | #FFC24F | Hover of an amber fill |
| `--on-amber` | #18191C | Text and glyphs on amber and on danger fills |
| `--amber-wash` | rgba(255,176,32,.09) | S4 banner fill (#2D271C over the page) |
| `--danger` | #FF6B66 | Field errors and their border, the bin and Delete habit on hover and focus, M1's Delete habit fill |
| `--danger-hover` | #FF8D89 | M1's Delete habit on hover |
| `--scrim` | rgba(10,11,13,.74) | Backdrop of P2, P3, P4 and M1 |
| `--scrim-soft` | rgba(10,11,13,.52) | Backdrop of P1, lighter so the chosen day stays readable behind it |
| `--focus` | #EDEEF0 | Focus ring |
| `--shadow-dlg` | two dark layers | Dialogs and desktop sheets only. Nothing else casts a shadow |
| `--fade-top`, `--fade-bot` | `--surface` to clear | The list frame's scroll fades |

## Contrast (WCAG 2.x, computed from `system.css` by `checks/data.py` and again by `checks/check.py`)

### Text (AA needs 4.5 to 1)

| Foreground | Background | Ratio | Used for |
|---|---|---|---|
| `--ink` | `--bg` | 15.14 | brand word, body text |
| `--ink` | `--surface` | 13.69 | habit names, button labels, band title, empty lead |
| `--ink` | `--surface-2` | 12.17 | dialog and sheet titles, tick names, month names, S5 note |
| `--ink` | `--raise` | 10.25 | a label on a hovered button or tick |
| `--ink` | `--field` | 16.00 | typed text |
| `--ink` | wash over bg (#2D271C) | 12.75 | S4 warning text |
| `--ink-soft` | `--bg` | 7.64 | the date |
| `--ink-soft` | `--surface` | 6.91 | row labels and units, hints, band numbers, legend, field note |
| `--ink-soft` | `--surface-2` | 6.14 | subtitles, P3 and P4 numbers, Delete habit at rest, tick stats, disabled field text |
| `--ink-soft` | `--raise` | 5.17 | a number on a hovered or open day |
| `--amber` | `--surface` | 8.69 | Current on a row |
| `--amber` | `--surface-2` | 7.72 | Current in P2 and P1 |
| `--on-amber` | `--amber` | 9.61 | Done today pressed, Add, a number on a full core or a done bead |
| `--on-amber` | `--amber-hover` | 10.95 | the same on hover |
| `--on-amber` | `--danger` | 6.32 | Delete habit in M1 |
| `--on-amber` | `--danger-hover` | 7.89 | the same on hover |
| `--danger` | `--surface` | 5.71 | field error |
| `--danger` | `--surface-2` | 5.08 | Delete habit in P2 on hover |

### Controls and graphics (AA needs 3 to 1, WCAG 1.4.11)

| Element | Against | Ratio | Used for |
|---|---|---|---|
| `--ring` | `--surface` | 3.97 | not-done segment in the band, outline button edges, Done today dot |
| `--ring` | `--surface-2` | 3.53 | not-done bead, P3 and P4 not-done segment, tick box, Cancel edge |
| `--ring` | `--bg` | 4.39 | Overview button edge |
| `--ring` | `--field` | 4.64 | field border |
| **`--ink-soft`** | **`--raise`** | **5.17** | **ruling 1, a thin not-done segment on a hovered or open day (was `--ring` at 2.97)** |
| `--amber` | `--surface` | 8.69 | done segment in the band |
| `--amber` | `--surface-2` | 7.72 | done segment in P3 and P4, done bead and thread |
| `--amber` | `--raise` | 6.51 | the open day's outline, a done segment on a hovered day |
| `--amber` | `--bg` | 9.61 | S4 banner edge |
| `--ink` | `--surface` | 13.69 | today's ring circle in the band |
| `--ink` | `--surface-2` | 12.17 | today's ring circle in P3 and P4, today's bead halo |
| `--ink-soft` | `--surface` | 6.91 | bin icon at rest |
| `--danger` | `--surface` | 5.71 | bin icon and edge on hover and focus |
| `--danger` | `--field` | 6.68 | error field border |
| `--focus` | `--bg`, `--surface`, `--surface-2` | 15.14, 13.69, 12.17 | focus ring |

### Recorded, no ratio required

| Pair | Ratio | Why none is required |
|---|---|---|
| `--ring` on `--raise` | 2.97 | retired by ruling 1, no element draws it any more |
| `--closed` on `--surface-2` | 2.18 | days after today, inactive and not operable (WCAG exempts inactive components) |
| `--surface-2` on the page under `--scrim` | 1.36 | the dialog's edge. The dialog is the only thing not dimmed, and its title and buttons carry its meaning |
| `--line` on `--surface` | 1.30 | dividers, decorative |
| `--track` on `--surface` | 1.85 | the empty-state core, decorative |

## Type
One family, the system sans stack `ui-sans-serif, system-ui, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif`. No web fonts. Weights 400, 500, 600 and 700.

| Token | Size / line | Weight | Used for |
|---|---|---|---|
| `--t-2xs` | 11 / 16 | 600 | weekday letters in P2 and P4 months |
| `--t-xs` | 12 / 16 | 600 | row labels Current and Best, band axes, legend |
| (literal) | 13 / 16 or 18 | 400, 600 | units "days", "No streak yet" on a row, tick stats |
| `--t-sm` | 14 / 20 | 400, 600 | the date on a phone, hints, subtitles, field label and messages, a desktop bead number |
| `--t-btn` | 15 / 22 | 600 | Overview, Year, Done today, Delete habit, month names, a phone bead number |
| (literal) | 15 / 22 | 400 | banner text |
| `--t-md` | 16 / 22 or 24 | 400, 600 | body, the field, habit names on a phone, tick names, Add, band title |
| `--t-ov` | 16 | 600, 700 on a full core, 500 when closed | ring day numbers (16.8 px in P3 and P4 on a 390 phone, the ring is drawn at 42 on a 40 box) |
| `--t-lg` | 17 / 24 or 26 | 600 | habit names on a desktop, P1 and M1 titles, empty lead |
| `--t-xl` | 19 / 24 or 26 | 700 | brand word on a phone, sheet titles |
| (literal) | 21 / 24 | 700 | brand word on a desktop |
| `--t-stat` | 22 / 26 | 700 Current, 600 Best | numbers on a row, tabular figures |
| `--t-best-lg` | 26 / 32 | 600 | Best in P2 |
| `--t-cur-lg` | 34 / 38 | 700 | Current in P2 |

Row and P2 numbers use tabular figures so they line up. Ring and bead numbers use proportional figures and centre by their ink (principle 5).

## Space
4 px base. `--s-1` 4, `--s-2` 8, `--s-3` 12, `--s-4` 16, `--s-5` 20, `--s-6` 24, `--s-7` 32, `--s-8` 40. f2's literal values are kept where f2 used them (row padding 14, header row gap 6, brand gap 10, button paddings 7 to 14, field label gap 6, banner text padding 10), all on a 2 px grid, because the goldens must render as f2 did.

| Where | Value |
|---|---|
| App column, phone | 12 top (owner, 2026-10-11, f2 had 8), 16 sides (12 under 380 px), 12 bottom or the safe area |
| App column, desktop | max 1040, 12 top and bottom, 24 sides |
| Between header, band, banners, list and composer | 12 |
| Row padding | 12 by 14 on a phone (12 under 380), 12 with 20 on the left on a desktop |
| Row line gap (name to numbers), phone | 12 |
| Row column gap | 8 on a phone (6 under 380), 12 on a desktop |
| Band padding, desktop | 14 top, 20 sides, 12 bottom, 20 between its two columns |
| Composer padding | 10 top, 12 sides and bottom on a phone, 12 on a desktop |
| Sheet head and body, phone | 12 by 16 (12 under 380) |
| Sheet head and body, desktop | 16 by 24, body 24 at the bottom |
| Dialog padding (M1, desktop P1) | 20 |
| P1 bottom sheet padding | 16, 24 at the bottom |
| Between months in P2 and P4 | 20 on a phone, 24 by 40 (P2) and 24 by 20 (P4) on a desktop |

## Radius
One rule, four values. **Controls are 10** (`--r-ctl`) on every rectangular button and the field. **Containers are 16** (`--r-card`) on the band, the list frame, the composer and the banners. **Sheets are 20** (`--r-sheet`) on dialogs and desktop sheets, and on the top corners of P1's phone bottom sheet. **Round things are circles** (`--r-round`) on rings, beads, tick boxes, the Done today dot, the bin, icon buttons and the legend minis. Day cells in the overview have a 12 px radius so the hover and open fill reads as a soft tile round a ring (f2). Full-screen phone sheets have no radius.

## Elevation and layers
Flat by default. Surfaces step up in lightness, never by shadow. `--bg` (page) then `--surface` (cards) then `--surface-2` (dialogs and sheets) then `--raise` (hover and open). Only dialogs and desktop sheets cast `--shadow-dlg`. A popup sits over a backdrop, `--scrim` for P2, P3, P4 and M1 and `--scrim-soft` for P1. Popups stack in the order they open, so on a phone P1 sits over P3 or P4 and P4 over P3, each with its own backdrop. In the app they are `<dialog>` elements opened with `showModal()`, in the top layer. The goldens draw each backdrop as a `.scrim` element and each popup as `<dialog open>`, in document order (the stand-in block at the end of `system.css`). The page under any popup does not scroll (`html:has(dialog[open])`).

## Motion
Motion only answers an action. Nothing moves on load.

| What | Duration | Easing |
|---|---|---|
| Button, cell and tick fills and edges | 170ms (`--dur`) | `--ease` cubic-bezier(.2,0,0,1) |
| Press, scale .98 (buttons), .97 (Year, Done today), .94 (bin), .9 (bead) | 120ms (`--dur-press`) | `--ease` |
| A changed ring, Done today dot, tick box or bead pops once (scale .82 to 1.08 to 1) | 260 to 300ms | `--ease-out` cubic-bezier(.16,1,.3,1) |
| A changed number rises 6 px and fades in | 280ms | `--ease-out` |
| A dialog rises 8 px and fades in | 220ms (`--dur-enter`) | `--ease-out` |
| P1's phone sheet slides up 40 px | 260ms | `--ease-out` |
| A backdrop fades in | 180ms | `--ease` |

**Reduced motion.** Under `prefers-reduced-motion: reduce` every transition and animation is off on every element and pseudo-element. State changes appear at once.

## Breakpoints

| Width | Layout |
|---|---|
| Under 380 | Phone, tighter. 12 px side padding, Done today 14 px text, beads 34, P3 and P4 rings 40 in 46 px cells |
| 380 to 767 | Phone. Header with the Overview button, rows on two lines, P1 a bottom sheet, P2, P3 and P4 full-screen sheets, beads 36, P3 and P4 rings 42 in 48 px cells |
| 768 to 1023 | Phone layout, but every popup is a centred dialog. P2 and P4 two months across, beads 32 |
| 1024 and up | Desktop. The band replaces the Overview button, rows on one line, the composer label sits left of the field, P2 three months across |

## Sizes and touch targets

| Token | Value | Note |
|---|---|---|
| `--hit` | 44px | every button and icon button at least 44 by 44 |
| `--ctl-h` | 48px | the field, Add, Cancel and Delete habit |
| `--icon` | 20px | trash, x, plus |
| `--ov-ring` | 40px | ring in the band and in P4 on a desktop |
| `--ov-cell-h` | 44px | band and desktop P4 cell height |
| `--yc` | 44px phone, 40px from 768 | P2 day cell height |
| `--bead` | 36px, 34px under 380, 32px from 768 | P2 bead |
| `--app-max` | 1040px | desktop app column |

Day cells below 44 px, inherited from f2 unchanged. P3 at 360 is 43.1 by 46 (the round 1 brief allows 40 at 360). P2 on a desktop is 40 by 40 and P4 on a desktop 42 by 44, pointer layouts where 3 months must fit across (f2 readings 7 and 20). Each is listed in `SELF-CRITIQUE.md` for the owner.

## Component inventory

### Buttons

| Kind | Class | Look | Hover | Press | Focus | Disabled |
|---|---|---|---|---|---|---|
| Primary | `.btn.btn-primary` (Add) | `--amber` fill, `--on-amber` 16/600, 48 tall, 10 radius, Phosphor plus | `--amber-hover` | scale .98 | 2 px `--focus` ring, 3 px out | `--surface-2` fill, `--ink-soft` text, no hover |
| Secondary | `.btn.btn-secondary` (Cancel) | clear, 1.5 `--ring` edge, `--ink` | `--raise` fill | scale .98 | same | not used |
| Danger | `.btn.btn-danger` (M1 Delete habit) | `--danger` fill, `--on-amber` | `--danger-hover` | scale .98 | same | not used |
| Outline | `.btn-year`, `.btn-all` (Year) | clear, 1.5 `--ring` edge, `--ink` 15/600, 44 tall, at least 44 wide | `--raise` fill | scale .97 | 2 px ring, 2 px out | not used |
| Toggle | `.btn-done` (Done today) | outline with a 22 px `--ring` dot. Pressed, `--amber` fill, `--on-amber` text, dark dot with an amber check | `--raise`, pressed `--amber-hover` | scale .97, the dot pops | same | not used |
| Overview | `.ov-btn` | outline, today's 28 px ring before the word | `--raise` | scale .98 | same | not used |
| Quiet delete | `.btn-del` (P2 Delete habit) | clear, `--ink-soft` text and trash | `--danger` text and edge | none | same | not used |

One filled action per view. Add on the main screen, Delete habit (danger) in M1. Done today is a toggle, not an action, and it fills only when pressed.

### Icon button
`.icon-btn` (Close, Dismiss note) and `.btn-bin` (the row bin). A 44 px circle, a 20 px Phosphor glyph in `--ink-soft`. Close and Dismiss turn `--raise` with an `--ink` glyph on hover. The bin never fills. On hover its glyph and a 1.5 edge turn `--danger`, on keyboard focus the glyph turns `--danger` inside the white focus ring, drawn inside the circle (offset -2) so the frame never clips it.

### Ring
An SVG on a 40 unit box. Segments on radius 15, one per habit, clockwise from 12 o'clock, each `360 / N` degrees less a gap of `min(22, 30%)` degrees. With three habits each arc is 98 degrees, with twelve 21 degrees. Not done is `--ring` at 1.5, done `--amber` at 3.5. All done adds an `--amber` core of radius 11.5 and the number turns `--on-amber` 700. Today adds an `--ink` circle of radius 19.2 at 1.4. The number is `.c-num`, 16 px 600 `--ink-soft`, `text-anchor:middle`, on the alphabetic baseline at y 20 with `dy=".352em"`. No habits draws one thin circle. Sizes 40 in the band and desktop P4, 42 in P3 and phone P4 (40 under 380), 56 in P1 (no number), 28 in the Overview button (no number), 22 in the legend (no number). In the goldens each arc is a `<use>` of a shared path (`#a3-0` to `#a3-2`, `#a12-0` to `#a12-11`), the state class sits on the `<use>`.

| State | Look |
|---|---|
| Rest | clear cell |
| Hover (pointer) | `--raise` cell (12 radius), thin segments step up to `--ink-soft` (ruling 1) |
| Open (its P1 is open) | `--raise` cell with a 1.5 `--amber` inset outline, thin segments `--ink-soft` (ruling 1) |
| Focus | 2 px `--focus` ring inside the cell |
| Closed (after today) | band and P3, an empty cell. P4, the number alone in `--closed` 500, not a button |

### Bead (P2)
`.yc` cell, `.bead` circle. Not done, `--surface-2` fill and 2 px `--ring` edge, `--ink` number 600. Done, `--amber` fill and edge, `--on-amber` number 700. Today adds a halo, 3 px `--surface-2` gap then 1.5 px `--ink`. Two done days side by side are joined by an 8 px `--amber` thread through the centres (each cell draws its own half, so a run that crosses a week or month edge leaves a stub). Closed days after today show the number in `--closed` 500, no edge, not a button. Days before 10 October 2025 are empty. Hover turns the edge `--amber` (a done bead turns `--amber-hover`), press scales the bead to .9, focus draws the ring round the bead 3 px out. The number follows ruling 2. It is SVG text filling the bead (`<span class="bead"><svg><text x="50%" y="50%" dy=".352em">`), drawn the ring's way in `currentColor`, proportional figures (f2 used HTML text with grid centring and tabular figures, 0.72 px low on a phone).

### Row
`li.row`. Phone, two lines. The name (h3, 16/22 600, wraps anywhere) with the bin at the right end of its line, then Current and Best, Year and Done today. Desktop, one line. Name (17/24), the bin in a 56 px column, stats in 200 px, Year, Done today. Rows are divided by a 1 px `--line`. Tab order is bin, Year, Done today, which is also the reading order.

| State | Stats |
|---|---|
| With a streak | Current N days (or 1 day) in `--amber` 22/700, Best N in `--ink` 22/600 |
| No streak yet | "No streak yet" in 13/600 `--ink-soft` in place of the Current number, Best as above |
| Best 0 | the Best block is not drawn |

### Field
`.composer` > `.input` with `label.add-label` (New habit) and Add. 48 tall, 10 radius, 1.5 `--ring` edge, `--field` fill, 16 px. The message line `#nh-msg` sits above the field (it grows the bar upward, so the field never moves). On a desktop the label sits left of the field and the message above the field.

| State | Look |
|---|---|
| Default | `--ring` edge, message hidden |
| Focus | 2 px `--focus` ring 2 px out |
| Error (S2) | `--danger` edge, `aria-invalid="true"`, message in `--danger` |
| Full (S3) | field and Add disabled, `--surface-2` fill, `--line` edge, `--ink-soft` text and label, message as a note in `--ink-soft` |

### Dialog (M1)
`dialog.dlg-del`, `role="alertdialog"`. `--surface-2`, 20 radius, 1 px `--line` edge, `--shadow-dlg`, 20 padding, width `min(400px, 100vw - 32px)`, centred. Title 17/26 600, body 16/24 `--ink-soft`, then Cancel (secondary) and Delete habit (danger) in two equal columns 12 apart. `--scrim` backdrop.

### Sheet
P1 on a phone is a bottom sheet (20 radius on the top corners, no bottom edge, at most 85% of the screen tall, `--scrim-soft` backdrop). P2, P3 and P4 on a phone are full-screen sheets with a fixed head (title, subtitle or hint, Close) over a scrolling body whose top and bottom edges show a soft shadow when more is behind them. From 768 px they become centred dialogs (P1 440 wide, P3 520, P2 and P4 980), at most the screen less 48 tall.

### Band
Desktop only (1024 and up). `--surface` card, 16 radius. Left column 180 px with the title, the Year button on the same line, the hint and the legend at the foot. Right, the 12 weeks as columns, newest on the right, a 22 px weekday column, month names over the first week of each month.

### Popup (P3)
The overview on a phone. A full-screen sheet with the title, hint, Year and Close in the head. Weeks as rows, newest on top, a 34 px month column, weekday letters on top, the legend right aligned below.

### Banner
`.banner.warn` (S4) is the amber wash with an `--amber` edge, 15/22 `--ink`, 16 radius, `role="status"`, no dismiss. `.banner.note` (S5) is `--surface-2` with a `--line` edge, its text and a 44 px Dismiss note icon button.

### Empty list
`.empty` takes the list's place in S1 and S5. A 96 px dotted orbit (`--ring`, dashes 2 and 6) round a `--track` core, then "No habits yet." (17/24 600) and "Add one you want to do every day." (14/20 `--ink-soft`).

### Tick (P1)
`.tick`, a full-width row at least 60 tall, a 28 px round box (`--ring` edge, `--amber` fill and dark check when on), the habit name 16/22 600 and its Current and Best in 13/18 (Current in `--amber` 600, or "No streak yet" in `--ink-soft`). Hover `--raise`. State in `aria-pressed`.

### Legend
None, then rings for 0, a third, two thirds and all of the habits, then All. 22 px rings, 12 px `--ink-soft` words. P2 has its own, a 16 px done mini and a not-done mini with Done and Not done.

## Accessible names (one rule each)

| Element | Rule | Example |
|---|---|---|
| Overview day (band, P3) | "Ddd D Mon, N of T habits" | "Tue 22 Sep, 1 of 3 habits" |
| P4 day | the same with the year, because P4 holds two Octobers | "Tue 22 Sep 2026, 1 of 3 habits" |
| P2 day | always "Mark Ddd D Mon YYYY as done", state in `aria-pressed` | "Mark Sat 10 Oct 2026 as done" |
| Today | `aria-current="date"` on its cell or bead | |
| Done today | "Done today, " plus the name, state in `aria-pressed`, described by the row's numbers | "Done today, Read 20 pages" |
| Year on a row | "Year view, " plus the name | "Year view, Read 20 pages" |
| Year on the overview | fixed | "Year view, all habits" |
| Bin | "Delete " plus the name in straight quotes | Delete "Stretch 10 minutes" |
| Overview button | the word plus today's count, as the button's `aria-label` | "Overview, today 1 of 3 habits done" |
| Tick in P1 | the habit name, state in `aria-pressed` | "No phone after 11pm" |
| Close, Dismiss | fixed | "Close", "Dismiss note" |

## Icons
Phosphor Icons (MIT), inlined as symbols and used with `<use>`. x (regular, Close and Dismiss), plus (regular, Add), trash (regular, the bin and Delete habit), check (bold, Done today, ticks). No other icons. The mark is `docs/brand/mark.svg` in one inline `<svg class="mark">` in the header, coloured `--amber` through currentColor, so the redrawn logo swaps in as one element per golden (plus the data URL favicon).

## Tokens and rules changed from f2

| Change | Reason |
|---|---|
| No token added | Ruling 1 reuses `--ink-soft`. Ruling 2 is a markup and offset rule, not a token |
| Ring numbers `dy=".367em"` to `dy=".352em"` | Ruling 2. At 390 f2's rings sat 0.34 px low on average (0.5 at worst). `.352em` is the measured half height of the figures and puts every ring within 0.25 px at 360, 390 and 1280 |
| `--mono`, `--proto-bg`, `--proto-ink`, `--proto-line` removed | They only styled the Prototype states tab, which is review tooling, not the design |
| Header grid areas `"brand ov" "date date"` (phone) and `"brand date"` (desktop) | f2 reserved a "proto" area for the tab. Without it the date sits at the right edge on a desktop and the brand line starts at the top on a phone |
| `.hc.is-open .seg:not(.on)` and `button.hc:hover .seg:not(.on)` draw in `--ink-soft` | Ruling 1. The thin segment on `--raise` was 2.97 to 1, it is now 5.17 |
| A bead's number is SVG text (`.bead svg`, `.bead text`, `dy=".352em"`), proportional figures | Ruling 2. f2's HTML number sat 0.72 px low at 390 and 360. HTML text snaps its baseline to whole pixels, so no CSS offset could land it nearer than 0.28 px high, while SVG text moves in quarter pixels. Now within 0.125 px at 390 and 0.25 at 1280 |
| `.scrim`, `dialog[open]` fixed, `.below-desktop` | Golden stand-ins for `showModal()`, the top layer and the backdrop. The app does not need them |
| The scrim fades in with the backdrop's 180ms rule | The stand-in follows the backdrop it replaces |
