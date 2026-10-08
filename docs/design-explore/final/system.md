# Streaks design system

**Phase** design, steps 5, 6 and 8 · **Date** 2026-10-08 · **Direction** round 1 B, "Quiet beads", with the changes in `round-1/DECISION.md`
**Tokens** `system.css` (every golden copies its `:root` block and the two bead-size media queries, same names and values)
**Data** `sample-history.json` is the one source for every screen

## Skills loaded and what they changed

| Skill | Loaded | What transferred | What did not, and why |
|---|---|---|---|
| `taste-skill:taste-skill` | yes, invoked | Zero long dashes. One accent locked across the app (the bead green), one danger colour used only for errors and the delete action. A documented radius rule. Button, form and focus contrast checks with recorded ratios. Label above the input, message below it, no placeholder as label. Empty and error states designed, not left blank. Press feedback (scale on `:active`). Motion only for feedback, gated by reduced motion. Phosphor icons only, never hand drawn. No eyebrows, no middle-dot strings, no decorative dots. Copy self-audit. | React, Tailwind, Motion, web fonts and the image strategy are ruled out by the brief (static page, zero dependencies, offline). Its dark-mode rule is overridden by the brief (one light theme, a theme switcher is a non-goal). Hero, landing and bento rules do not apply to a one-screen tool. |
| `frontend-design:frontend-design` | yes, invoked | A compact token plan (4 to 6 core colours, one type family). One memorable element (the bead and its thread), everything around it quiet. No all-caps labels, no labels above content that add nothing. Motion only where it answers an action. Plain, active copy (the button says Add, the dialog button says Delete habit). | Its push for a distinctive typeface is overridden by the brief (system font stacks only). |

Design read. A personal one-screen tool for one person on a phone, calm and steady, built in plain CSS on system fonts, with the bead thread as the single expressive element.

## Principles
1. **The thread is the streak.** A run of done days is drawn as a thick thread through the beads. A dashed thread into an open today says the run still holds, with no extra words.
2. **Done differs by shape, not only colour.** Done is a filled bead with a check. Not done is a hollow ring. Heatmap levels differ by form and size first, tone second.
3. **Quiet around the beads.** One green, one neutral family, no cards except the heatmap panel and the dialog, no decoration.
4. **Whole pixels for round things.** Beads and heat dots use integer sizes so they stay round after pixel snapping.

## Colour roles

| Token | Hex | Role and where it is used |
|---|---|---|
| `--bg` | #F2F5F3 | Page background. Fill of a not-done bead. The 3 px gap around the today ring. |
| `--surface` | #FAFCFB | Heatmap panel and dialog. |
| `--field` | #FDFEFE | Text input fill. |
| `--wash` | #E5ECE9 | Icon button hover fill, secondary button hover fill, note banner, disabled input fill. |
| `--ink` | #1C2523 | Primary text (habit names, today label, typed text, titles). Focus ring. |
| `--ink-soft` | #52605B | Secondary text (date, streak line, weekday labels, axis labels, legend, notes, dialog body). Icons at rest. |
| `--bead` | #3B6B60 | Done bead, run thread, dashed holding thread, primary button, heat level 3. |
| `--bead-deep` | #2E5A50 | Brand word, current streak text, primary button hover, done bead hover, heat level 4. |
| `--on-bead` | #F7FAF9 | Check mark and button text on `--bead`, `--bead-deep`, `--danger`, `--danger-deep`. |
| `--ring` | #7E8E88 | Not-done bead stroke, input border, secondary button border, today ring (strip and heatmap), heat level 0 ring. |
| `--thread` | #C6D0CC | Thin thread between beads that are not a run (decorative). Disabled button fill, disabled input border. |
| `--danger` | #A23B32 | Field error text, error input border, "Delete habit" button. |
| `--danger-deep` | #84302A | "Delete habit" hover. |
| `--heat-1` | #78968B | Heatmap level 1 dot. |
| `--heat-2` | #4F7C70 | Heatmap level 2 dot. |
| `--heat-3` | = `--bead` | Heatmap level 3 dot. |
| `--heat-4` | = `--bead-deep` | Heatmap level 4 dot. |
| `--focus` | = `--ink` | Focus ring. |
| `--scrim` | `--ink` at 50% | Dialog backdrop. |
| `--shadow-dialog` | `--ink` tinted | `0 16px 48px` at 18% plus `0 2px 6px` at 8%. Dialog only. Nothing else casts a shadow. |

## Contrast (WCAG 2.x, measured with `harness/_scratch/design-final/contrast.py`)

### Text (AA needs 4.5:1)

| Foreground | Background | Ratio | Used for |
|---|---|---|---|
| `--ink` #1C2523 | `--bg` #F2F5F3 | 14.30 | habit names, today label, empty-state lead |
| `--ink` #1C2523 | `--surface` #FAFCFB | 15.23 | heatmap title, dialog title, Cancel text |
| `--ink` #1C2523 | `--field` #FDFEFE | 15.53 | typed text in the input |
| `--ink` #1C2523 | `--wash` #E5ECE9 | 13.08 | note text, Cancel hover text |
| `--ink-soft` #52605B | `--bg` #F2F5F3 | 6.01 | date, streak line, weekday labels, field note, empty-state line |
| `--ink-soft` #52605B | `--surface` #FAFCFB | 6.40 | axis labels, legend, dialog body |
| `--ink-soft` #52605B | `--wash` #E5ECE9 | 5.50 | disabled input text (exempt, still passes) |
| `--bead-deep` #2E5A50 | `--bg` #F2F5F3 | 7.10 | brand word, current streak |
| `--on-bead` #F7FAF9 | `--bead` #3B6B60 | 5.78 | Add |
| `--on-bead` #F7FAF9 | `--bead-deep` #2E5A50 | 7.42 | Add on hover |
| `--on-bead` #F7FAF9 | `--danger` #A23B32 | 6.23 | Delete habit |
| `--on-bead` #F7FAF9 | `--danger-deep` #84302A | 8.20 | Delete habit on hover |
| `--danger` #A23B32 | `--bg` #F2F5F3 | 5.96 | field error text |
| `--ink-soft` #52605B | `--thread` #C6D0CC | 4.18 | disabled Add text. Disabled controls are exempt from 1.4.3. Kept readable on purpose. |

### Controls and graphics (AA needs 3:1, WCAG 1.4.11)

| Element | Against | Ratio | Used for |
|---|---|---|---|
| `--ring` #7E8E88 | `--bg` | 3.13 | not-done bead stroke, today ring around the bead |
| `--ring` #7E8E88 | `--field` | 3.40 | input border |
| `--ring` #7E8E88 | `--surface` | 3.33 | Cancel border, heat level 0 ring, today ring in the heatmap |
| `--bead` #3B6B60 | `--bg` | 5.53 | done bead, run thread, dashed holding thread |
| `--on-bead` #F7FAF9 | `--bead` | 5.78 | check mark in a done bead (7.42 on hover) |
| `--danger` #A23B32 | `--field` | 6.48 | error input border |
| `--focus` #1C2523 | `--bg` / `--surface` / `--field` | 14.30 / 15.23 / 15.53 | focus ring |
| `--ink-soft` #52605B | `--bg` | 6.01 | trash icon at rest |
| `--ink` #1C2523 | `--wash` | 13.08 | trash and dismiss icons on hover |
| `--heat-1` #78968B | `--surface` | 3.12 | heat level 1 dot |
| `--heat-2` #4F7C70 | `--surface` | 4.58 | heat level 2 dot |
| `--heat-3` #3B6B60 | `--surface` | 5.89 | heat level 3 dot |
| `--heat-4` #2E5A50 | `--surface` | 7.56 | heat level 4 dot |
| `--surface` #FAFCFB | page under the 50% scrim (#878D8B) | 3.28 | dialog edge |
| `--thread` #C6D0CC | `--bg` | 1.44 | thin unjoined thread. Decorative, carries no state (the beads do), so no ratio is required. |

## Type
One family, the system rounded stack `ui-rounded, "SF Pro Rounded", system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif`. No web fonts. Numbers in the streak line and day numbers use `tabular-nums`.

| Token | Size / line | Weight | Used for |
|---|---|---|---|
| `--text-xs` | 12 / 16 | 400 | weekday label in the strip, heatmap axes, legend |
| `--text-sm` | 14 / 20 | 400, 600 for the current streak | streak line, field error, field note |
| `--text-md` | 16 / 24 | 400 body, 600 labels and buttons | body, input, buttons, "New habit" label, date, heatmap title, dialog body, note |
| `--text-md` in a 20 px line | 16 / 20 | 500 (renders 400 where no medium exists) | day number in the strip |
| `--text-lg` | 18 / 28 | 600 | habit name, dialog title, empty-state lead |
| `--text-xl` | 22 / 28 | 700, letter-spacing -0.01em | brand word "Streaks" |

Today's weekday and day number switch to `--ink` at 700. Weights in use are 400, 500, 600 and 700 only.

## Space
4 px base. `--space-1` 4 · `--space-2` 8 · `--space-3` 12 · `--space-4` 16 · `--space-5` 20 · `--space-6` 24 · `--space-7` 32 · `--space-8` 40 · `--space-9` 48 · `--space-10` 64. Every margin, padding and gap in the goldens is one of these, or zero.

| Where | Value |
|---|---|
| Page side padding, phone | 20 (`--space-5`) |
| Page top / bottom, phone | 24 / 48 |
| Page padding, desktop | 40 top, 48 sides, 48 bottom |
| Header to first habit | 24 phone, 32 desktop |
| Between habits | 32 |
| Name row to streak line | the 44 px head row, with the name 8 px from its top |
| Streak line to strip | 8 |
| Weekday and number to bead, inside a day cell | 8 (cell padding 4 top, 8 bottom) |
| List to "New habit", and add form to heatmap (phone) | 40 |
| Label to input | 8 |
| Input to button | 12 |
| Field message under the row | 8 |
| Note banner to list | 32 |
| Heatmap panel padding | 20 by 16 phone, 24 desktop |
| Heatmap title to grid | 12 · axis gap 8 · month row to cells 4 · grid to legend 12 |
| Desktop column gap | 64 |
| Dialog padding / title to body / body to buttons / between buttons | 24 / 8 / 24 / 12 |

## Radius
One rule, three values. **Controls are pills** (`--radius-pill` 999px) on the input, every button, and the day cell (its focus outline is a vertical capsule). **Round things are circles** (`--radius-round` 50%) on beads, heat dots, the today rings and icon buttons. **Containers are 20 px** (`--radius-panel`) on the heatmap panel, the note banner and the dialog. Nothing else has a radius.

## Sizes and touch targets

| Token | Value | Note |
|---|---|---|
| `--hit-min` | 44px | icon buttons are 44 by 44, day cells are at least 44 wide (45.7 at 360, 50 at 390, 71.4 at 1280) and 88 to 96 tall |
| `--control-h` | 48px | input and every button |
| `--icon` | 20px | trash and dismiss glyphs |
| `--page-max-phone` | 600px | single column cap below 900 px wide |
| `--page-max` | 1040px | two-column page at 900 px and up |
| `--heat-panel-w` | 380px | heatmap column on desktop |
| `--dialog-max` | 400px | dialog width cap, below that the viewport minus 20 px each side |

## The bead and the thread

| Part | Spec |
|---|---|
| Bead size | `--bead-size` 32px below 375 px wide, 36px from 375, 40px from 900. Whole pixels so the circle stays round. |
| Not done | Hollow circle, 2px `--ring` stroke (`--bead-stroke`), `--bg` fill, no check. |
| Done | `--bead` fill and stroke, Phosphor "check" (bold) in `--on-bead` at 56% of the bead. |
| Today | `aria-current="date"`. A ring outside the bead, 1.5px `--ring` (`--today-ring`) after a 3px `--bg` gap (`--today-gap`), drawn as `box-shadow: 0 0 0 3px var(--bg), 0 0 0 4.5px var(--ring)`. Weekday and number in `--ink` 700. Works on both open and done beads. |
| Hover (pointer only) | A not-done stroke turns `--bead`. A done bead's fill and stroke turn `--bead-deep`. |
| Press | Bead scales to 0.94 for 120ms. |
| Focus | 2px `--focus` outline on the whole day cell, offset 0, following its pill radius, so it reads as a vertical capsule around weekday, number and bead. It never collides with the today ring. |
| Hit area | The whole cell (`button.day`), never the bead alone. |
| Thin thread | 2px `--thread` line through every cell at the bead's centre line. Each cell draws its own left and right half. |
| Run thread | Two done days side by side are joined by a 4px `--bead` line (`--thread-run`). |
| Run carried in | If the first day in the strip is done and the day before the strip is also done, the strip gets `data-run-continues` and the first cell's left half is the 4px run thread fading in from transparent. |
| Older days | Without a carried run, the first cell's left half is the thin thread fading in from transparent. This says older days exist. |
| Future | Never drawn. The last cell has no right half. |
| Holding (dashed) | When yesterday is done and today is not, the 4px thread between them is dashed, 4px `--bead` dashes with 3px gaps (`--dash`, `--dash-gap`). Dash tiles are anchored on the boundary between the two cells, so the pattern is continuous. When today is ticked it becomes a solid run thread. When yesterday is not done there is no dashed thread, because the streak (if any) already ended. |

## Heatmap
One grid for all habits, 12 columns (weeks, Monday first, newest on the right) by 7 rows (Monday to Sunday), filled column by column. Each cell is a square column of the grid (21.3 px at 360, 23.8 at 390, 24.9 at 1280) with one centred dot.

| Level | Meaning | Form | Size | Tone |
|---|---|---|---|---|
| 0 | none done | hollow ring, 1.5px stroke | 6px | `--ring` |
| 1 | up to a third | filled dot | 7px | `--heat-1` #78968B |
| 2 | up to two thirds | filled dot | 11px | `--heat-2` #4F7C70 |
| 3 | more than two thirds, not all | filled dot | 14px | `--heat-3` = `--bead` |
| 4 | all | filled dot | 17px | `--heat-4` = `--bead-deep` |
| future | after today | nothing drawn, `aria-hidden` | n/a | n/a |
| today | the cell for today | its level dot plus a 22px ring, 1.5px `--ring` | 22px ring | `--ring` |

Levels read apart without colour. 0 to 1 changes form (ring to filled dot). 1 to 2 is the largest size step (7 to 11) and the largest tone step (3.12 to 4.58 against the panel). Every filled dot reaches 3:1 against the panel. Level 3 cannot occur with 3 habits (2 of 3 is level 2, 3 of 3 is level 4), so it shows only in the legend in the sample.

Axes. Month labels (12/16, `--ink-soft`) sit over the first column whose Monday falls in that month (Jul col 1, Aug col 3, Sep col 8, Oct col 12 for the sample). Weekday labels show Mon, Wed, Fri and Sun only, against rows 1, 3, 5 and 7. Legend, right aligned under the grid, reads "None", the five level dots in 20px cells, "All". The axes and legend are `aria-hidden`. Each cell carries the full accessible name.

## Focus ring
2px solid `--focus` (`--focus-w`). Offset 3px on buttons, 2px on the input, 0 on day cells (outline follows the cell's pill shape), inset 2px (offset -2px) on 44px icon buttons. Shown on `:focus-visible` only, so mouse clicks do not draw it. Every ring sits against `--bg`, `--surface` or `--field`, all at 14:1 or more.

## Motion
Motion only answers an action. Nothing moves on load except the dialog's entrance, which itself answers the tap on delete. No loops.

| What | Duration | Easing |
|---|---|---|
| Bead fill and stroke change | 180ms (`--dur`) | `--ease` cubic-bezier(0.2, 0, 0, 1) |
| Check mark appears (opacity, scale 0.6 to 1) | 200ms (`--dur-enter`) | `--ease-out` cubic-bezier(0.16, 1, 0.3, 1) |
| Bead press (scale 0.94), button press (scale 0.98) | 120ms (`--dur-press`) | `--ease` |
| Heat dot size and tone change | 180ms | `--ease` |
| Icon button and button hover fills | 180ms | `--ease` |
| Dialog opens (backdrop fades in, dialog fades and rises 8px) | 180ms and 200ms | `--ease`, `--ease-out` |

**Reduced motion.** Under `prefers-reduced-motion: reduce` every transition and animation is switched off (`transition: none; animation: none` on all elements and pseudo-elements). State changes appear at once.

## Layers
Only two stacking layers exist. `--z-scrim` 10 for the dialog backdrop, `--z-dialog` 20 for the dialog. The bead's `z-index: 1` is local to its slot so it sits over its own thread. While the dialog is open the page behind it is `inert` and does not scroll (`html:has(.dialog[open])` gets `height: 100%; overflow: hidden`).

## Layout

| Width | Layout |
|---|---|
| Below 900px | One column, centred, max 600px. Top to bottom, header, note (S5 only), habits, add form, heatmap. |
| 900px and up | Page max 1040px. Header spans the page. Below it a grid of `minmax(0, 1fr)` and 380px with a 64px gap. The left column holds the note, habits and add form. The right column holds the heatmap panel, top aligned with the first habit, `position: sticky` 32px from the top. |

Header. "Streaks" (h1, `--text-xl`, `--bead-deep`) left, the date (`<time>`, `--text-md`, `--ink-soft`) right, on one baseline. The date is the full weekday and day and month, "Thursday 8 October".

## Component inventory and states

### Button (`.btn`)
48px tall pill, 0 24px padding, 16px 600, one line (`white-space: nowrap`), 2px border (transparent unless stated).

| Variant | Default | Hover | Press | Focus | Disabled |
|---|---|---|---|---|---|
| Primary (`.btn-primary`, "Add") | `--bead` fill, `--on-bead` text | `--bead-deep` fill | scale 0.98 | 2px `--focus` ring, 3px offset | `--thread` fill, `--ink-soft` text, `cursor: not-allowed`, no hover, no press |
| Secondary (`.btn-secondary`, "Cancel") | transparent, 2px `--ring` border, `--ink` text | `--wash` fill | scale 0.98 | same ring | not used |
| Danger (`.btn-danger`, "Delete habit", dialog only) | `--danger` fill, `--on-bead` text | `--danger-deep` fill | scale 0.98 | same ring | not used |

One primary per view. On S1 and S2 it is Add. In the dialog it is Delete habit (danger), with Cancel as the secondary.

### Text input (`.input`)
48px pill, 2px border, 0 20px padding, 16px `--ink` on `--field`. Label above (`.add-label`, 16/24 600), message below (`.field-msg`, 14/20, 8px gap). No placeholder. No `maxlength`, so the 40-character error can be reached.

| State | Look | Markup |
|---|---|---|
| Default | `--ring` border | `aria-describedby` points at the message line |
| Focus | border unchanged, 2px `--focus` outline 2px outside | `:focus-visible` |
| Error | `--danger` border, message in `--danger` | `aria-invalid="true"`, message has `.field-error` |
| Disabled | `--wash` fill, `--thread` border, `--ink-soft` text, label turns `--ink-soft` | `disabled` on input and button, message has `.field-note` |

The message line is one element (`#new-habit-msg`, `aria-live="polite"`) that is empty and hidden normally, holds an error with `.field-error`, or the 12-habit note with `.field-note`.

### Day bead (`button.day`)
Covered under "The bead and the thread". Its states are not done, done, today (open), today (done), hover, done hover, press and focus. `aria-pressed` carries done or not done. Today has `aria-current="date"`.

### Habit row (`li.habit`)
A head row (min 44px) holds the name (h3, 18/28 600, 8px from the top, wraps with `overflow-wrap: anywhere`) and the delete icon button, pulled 12px right so the glyph's right edge sits on the content edge. Then the streak line, then the strip.

| State | Streak line |
|---|---|
| With a streak | current streak ("1 day" or "N days") in `--bead-deep` 600, then "Best N" in `--ink-soft` 400, 12px apart |
| No streak yet | "No streak yet" in `--ink-soft` 600 (class `cur none`). If best is 0 the best element is not rendered at all. |

If current is 0 but best is above 0, the line reads "No streak yet" then "Best N".

### Icon button (`.icon-btn`)
44px circle, transparent, 20px Phosphor glyph in `--ink-soft`. On hover the fill turns `--wash` and the glyph `--ink`. On focus a 2px `--focus` ring sits 2px inside the edge. Used for delete (trash, regular) and dismiss (x, regular).

### Heatmap cell (`.hc`)
Levels 0 to 4, today, future blank, as specified above. `role="img"` with an accessible name. Future cells have no dot and are `aria-hidden`.

### Note banner (`.note`, S5)
`--wash` fill, 20px radius, padding 8 8 8 20, text 16/24 `--ink` with 8px vertical padding, dismiss icon button on the right, top aligned. `role="status"`. Sits at the top of the main column with 32px below. Dismiss removes it. It does not come back until saved data again fails to read.

### Empty list (`.empty`, S2 and S5)
"No habits yet." as a block lead (18/28 600 `--ink`), then "Add one you want to do every day." (16/24 `--ink-soft`), 4px apart. Takes the list's place.

### Dialog (`.dialog`, M1)
`<dialog>` opened with `showModal()`, `role="alertdialog"`, `aria-labelledby` the title, `aria-describedby` the body. `--surface`, 20px radius, 24px padding, `--shadow-dialog`, width `min(400px, 100% - 40px)`, centred in the viewport. Backdrop `--scrim` (the golden draws it with a `.scrim` element because it has no script). Title 18/28 600, body 16/24 `--ink-soft`, then a two-column button grid (12px gap) with Cancel (secondary) left and Delete habit (danger) right, equal widths. Focus moves to Cancel when it opens. Esc and Cancel close it, keep the habit, and return focus to the trash button that opened it. Delete habit removes the habit and its history, closes the dialog, and returns focus to the next habit's delete button, or to the input when no habit is left.

## Accessible names (one rule each)

| Element | Rule | Example |
|---|---|---|
| Day bead | Always "Mark Ddd D Mon as done". The label never changes and `aria-pressed="true"` says it is done. Changing a toggle's label with its state makes screen readers announce contradictions ("Mark as not done, pressed"), so the state lives only in `aria-pressed`. | "Mark Tue 6 Oct as done" |
| Strip | `role="group"` labelled by the habit name | "Read 20 pages" |
| Heatmap cell | "Ddd D Mon, N of T habits", T being the current number of habits. With no habits it is "0 of 0 habits". | "Tue 6 Oct, 2 of 3 habits" |
| Delete | "Delete " plus the habit name | "Delete Read 20 pages" |
| Dismiss | fixed | "Dismiss note" |
| Habit list | visually hidden h2 | "Habits" |

## Icons
Phosphor Icons (MIT), inlined as `<symbol>` paths and used with `<use>`: "check" bold (done bead), "trash" regular (delete), "x" regular (dismiss). Fill is `currentColor` or `--on-bead`. No other icons.

## Tokens B did not have, and changes to B's tokens

| Token or change | Reason |
|---|---|
| `--danger`, `--danger-deep` | B had no error or destructive colour. S3 errors and the dialog's Delete habit need one, kept to a single brick red that sits with the sage palette. |
| `--scrim`, `--shadow-dialog` | M1 needs a backdrop and the dialog is the only raised surface. Both tinted with `--ink`, no pure black. |
| `--wash` (was `--hover-wash`) | Renamed because it now also fills the note banner, the disabled input and the Cancel hover. Same hex. |
| `--halo` removed | The today ring now uses `--ring` so it meets 3:1 (B's halo was 1.91:1). |
| `--heat-0` removed | Level 0 now uses `--ring`, 3.33:1 against the panel (B's was 2.03:1). |
| `--heat-1` #B4CBC3 to #78968B, `--heat-2` #82A89C to #4F7C70, `--heat-3` and `--heat-4` now point at `--bead` and `--bead-deep` | DECISION change 1. Levels 1 and 2 needed a clear tone gap, and every dot now meets 3:1 against the panel. |
| `--dot-0` to `--dot-4`, `--dot-ring`, `--today-cell-ring`, `--legend-cell` | B sized dots in percent of the cell, which rendered some small dots as 7 by 8 px ovals after pixel snapping. Fixed whole-pixel sizes keep them round and set the new level sizes. |
| `--bead-size` from `clamp(32px, 9vw, 40px)` to 32 / 36 / 40 steps | Whole pixels keep beads round, and the steps match the old clamp at 360, 390 and desktop. |
| `--gutter` removed | Replaced by `--space-5` (20px) on phones, so side padding sits on the spacing scale. |
| `--text-*`, `--lh-*`, `--weight-*` | B used literal sizes (12, 14, 15, 16, 18, 21, 24) and a 650 weight. Normalised to a five-step scale and four weights that system fonts actually have. |
| `--space-1` to `--space-10` | B used literal spacing (6, 9, 10, 14, 18, 22, 28, 34, 72). Normalised to a 4px scale. |
| `--radius-pill`, `--radius-round`, `--radius-panel` | B's literal radii, named so the radius rule can be checked. |
| `--hit-min`, `--control-h`, `--icon`, `--bead-stroke`, `--thread-thin`, `--thread-run`, `--today-gap`, `--today-ring`, `--focus-w` | B's literal sizes, named because the build must match them exactly. |
| `--dash`, `--dash-gap` | B's dashed thread restarted its pattern at each cell edge. Named and anchored on the cell boundary so the dash rhythm is continuous. |
| `--page-max-phone`, `--page-max`, `--heat-panel-w`, `--dialog-max` | Layout widths. `--page-max-phone` is new and stops the single column from stretching on tablets. |
| `--dur-press`, `--dur`, `--dur-enter`, `--ease`, `--ease-out` | B's literal motion values, named so reduced motion and the build share one source. |
| `--z-scrim`, `--z-dialog` | The dialog is the only layered element, so the scale has two steps. |
