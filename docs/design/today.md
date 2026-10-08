# S1 Today (key screen)

**Golden** `today.html` · **System** `system.md`, `system.css` · **Data** `sample-history.json` · **Today** Thursday 8 October 2026

## Intent
Show in one glance what is done today and how long each run has lasted, and make ticking a day a single tap. The streak is drawn as well as counted. Done days are filled beads joined by a thick thread, and a dashed thread into today's open bead says the run still holds until the day is over.

## Capabilities shown

| ID | Where |
|---|---|
| C1 Add a habit | "New habit" field and Add button under the list |
| C2 Tick the week | Seven day beads per habit, Fri 2 to Thu 8 Oct, today on the right |
| C3 Current streak | "6 days", "3 days", "1 day" |
| C4 Best streak | "Best 14", "Best 9", "Best 4" |
| C5 12-week heatmap | "Last 12 weeks" panel, Mon 20 Jul to Sun 11 Oct |
| C6 Delete a habit | Trash button on each habit (opens M1, see `delete-dialog.md`) |
| C7 Kept on the device | Not visible. S5 covers the failure case. |

## States on this screen

| Habit | Strip, Fri 2 to Thu 8 (D done, . not) | Shows |
|---|---|---|
| Read 20 pages | . D D D D D D | Today done, a 6-day run joined by solid thread, thin fading thread at the left of Fri 2 |
| Stretch 10 minutes | D D . D D D . | Run carried in from Thu 1 Oct (`data-run-continues`, thick thread fading in at the left), a break on Sun 4, then the **holding** state, a dashed thread from Wed 7 into the open today bead. Streak 3 days because today is not over. |
| No phone after 11pm | . D . . D . D | Isolated done days with thin thread only, a 1-day streak that is today |

Heatmap. Levels 0, 1, 2 and 4 occur (level 3 cannot occur with 3 habits). Today (Thu 8 Oct, level 2) has the today ring. Fri 9 to Sun 11 Oct are blank and hidden from assistive tech. Every level is drawn exactly from `heatmapLevels`, verified by script against the file.

Not shown statically. Hover, focus and press states (see `states.html`, Component states), the field errors and the 12-habit limit (S3, S4 in `states.html`), the note (S5).

## Exact copy

| Element | Text |
|---|---|
| Brand (h1) | Streaks |
| Date | Thursday 8 October (`<time datetime="2026-10-08">`) |
| List heading (visually hidden h2) | Habits |
| Habit names (h3) | Read 20 pages · Stretch 10 minutes · No phone after 11pm |
| Streak lines | 6 days, Best 14 · 3 days, Best 9 · 1 day, Best 4 (two spans, no comma rendered) |
| Strip labels | Fri 2 · Sat 3 · Sun 4 · Mon 5 · Tue 6 · Wed 7 · Thu 8 (weekday above number) |
| Day bead names | "Mark Fri 2 Oct as done" through "Mark Thu 8 Oct as done", the same whether pressed or not |
| Delete names | Delete Read 20 pages · Delete Stretch 10 minutes · Delete No phone after 11pm |
| Field label | New habit |
| Button | Add |
| Heatmap heading (h2) | Last 12 weeks |
| Month axis | Jul · Aug · Sep · Oct (columns 1, 3, 8, 12) |
| Weekday axis | Mon · Wed · Fri · Sun (rows 1, 3, 5, 7) |
| Legend | None · All |
| Heatmap cell names | "Mon 20 Jul, 3 of 3 habits" through "Thu 8 Oct, 2 of 3 habits" |

## Layout and spacing that matter (measured)

| Item | 390 x 844 | 360 x 780 | 1280 x 800 |
|---|---|---|---|
| Page | 20px side padding, 24 top | same | 1040 max, centred at x 120, padding 40 / 48 |
| Header | brand and date on one baseline, 24 below | same | 32 below |
| Columns | one | one | main 500 at x 168, heatmap 380 at x 732, gap 64 |
| Habit tops | 77, 273, 469 | 77, 269, 461 | 101, 301, 501 |
| Day cell | 50 x 92 | 45.7 x 88 | 71.4 x 96 |
| Bead | 36 | 32 | 40 |
| Delete button | 44 x 44, right edge 12 past the content edge | same | same |
| Add form top | 673 (input 705 to 753, inside the first screen) | 661 | 709 |
| Input / Add | 256 / 82 wide, 48 tall, 12 apart | 226 / 82 | 406 / 82 |
| Heatmap panel | top 793, 350 wide, padding 20 x 16 | top 781, 320 wide | top 101 (level with the first habit), padding 24, sticky at 32 |
| Heat cell | 23.8 square | 21.3 | 24.9 |

Alignment rules.
- The habit name's first line is centred on the 44px delete button (8px top padding inside a 28px line).
- The trash glyph's right edge sits on the content edge (button pulled 12px right).
- The thread runs through the bead centres. A cell's left half belongs to the cell, so the joining thread is two halves that meet on the cell boundary.
- The dashed holding thread starts with a dash at the boundary between Wed 7 and Thu 8 and repeats 4 on, 3 off in both directions.
- Today's column is the rightmost in every strip and in the heatmap (row Thu).
- The heatmap panel top aligns with the first habit's top on desktop.

## Markup contract the build mirrors
- `header.top` > `h1.brand` + `p.date` > `time`.
- `main.layout` > `div.col-main` (list section, then `form.add`) + `section.heat`.
- Each habit is `li.habit` > `div.habit-head` (`h3.habit-name#hN-name` + `button.icon-btn`) + `p.streak` (`span.cur` + `span.best`) + `div.strip[role=group][aria-labelledby=hN-name]`.
- Each day is `button.day[type=button][data-date][aria-pressed][aria-label]`, today adds `aria-current="date"`. Inside, `span.day-label[aria-hidden]` (`span.wd` + `span.dm`) and `span.slot[aria-hidden]` > `span.bead` > the check `svg`. The check is always present and CSS shows it when pressed.
- Thread states are derived from `aria-pressed` and `aria-current` by CSS (`:has()` and `+`). The only extra attribute is `data-run-continues` on the strip when the day before the strip is done and the first day is done.
- The add form is `form.add[novalidate]` > `label.add-label[for=new-habit]` + `div.add-row` (`input.input#new-habit` + `button.btn.btn-primary[type=submit]`) + `p.field-msg#new-habit-msg[aria-live=polite]` (empty here, hidden by `:empty`).
- The heatmap is `section.heat` > `h2.heat-title` + `div.heat-grid` (`div.months[aria-hidden]`, `div.wdays[aria-hidden]`, `div.cells`) + `div.legend[aria-hidden]`. Cells are `span.hc.lN[data-date][role=img][aria-label]`, today adds `.today` and `aria-current="date"`, future cells are `span.hc.future[aria-hidden]` with no level class.
