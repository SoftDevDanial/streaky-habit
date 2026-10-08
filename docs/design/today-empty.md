# S2 Today, first visit (empty)

**Golden** `today-empty.html` · **System** `system.md`, `system.css` · **Today** Thursday 8 October 2026

## Intent
The first thing a new user sees. The list is empty and says how to start, the add field is ready to type into, and the heatmap already shows its shape so the user knows what will fill in. Nothing is broken or missing, it is simply empty.

## Capabilities shown

| ID | Where |
|---|---|
| C1 Add a habit | "New habit" field and Add button, enabled, empty, no message |
| C5 12-week heatmap | Full grid, every past day at level 0 (hollow ring), today ringed, Fri 9 to Sun 11 Oct blank |
| C7 Kept on the device | The state a device shows when nothing has been saved yet |

## States on this screen
- Empty list. The empty message takes the place of the habit list.
- Add field default (no error, no note).
- Heatmap with no habits. 81 past cells at level 0, today (Thu 8 Oct) with the today ring around its level 0 ring, 3 future cells blank.
- The first flow continues from here. After typing "Read 20 pages" and pressing Add, the empty message is replaced by one habit row with 7 empty beads and "No streak yet" (see `states.html`, Habit list).

## Exact copy

| Element | Text |
|---|---|
| Brand (h1) | Streaks |
| Date | Thursday 8 October |
| List heading (visually hidden h2) | Habits |
| Empty message | No habits yet. Add one you want to do every day. (one paragraph, with "No habits yet." in a `strong` shown as a block lead) |
| Field label | New habit |
| Button | Add |
| Heatmap heading | Last 12 weeks |
| Axes and legend | Jul · Aug · Sep · Oct, Mon · Wed · Fri · Sun, None · All |
| Heatmap cell names | "Mon 20 Jul, 0 of 0 habits" through "Thu 8 Oct, 0 of 0 habits" |

## Layout and spacing that matter (measured)

| Item | 390 x 844 | 360 x 780 | 1280 x 800 |
|---|---|---|---|
| Empty message | top 77, 56 tall (28 lead + 4 + 24 line) | same | top 101, in the 500 main column |
| Add form | top 173 (40 below the message) | top 173 | top 197 |
| Input / Add | 256 / 82 | 226 / 82 | 406 / 82 |
| Heatmap panel | top 293, 40 below the form | top 293 | top 101, right column |

Alignment rules.
- The empty lead sits where the first habit name would sit, on the same left edge and at the same top (77 phone, 101 desktop).
- The whole first screen fits a 390 x 844 phone with the heatmap complete (panel ends at 588).
- On desktop the left column is short and the heatmap panel stays top aligned with the empty message. No filler is added.

## Markup contract the build mirrors
- Same page, header, `main.layout`, form and heatmap structure as S1 (`today.md`).
- The list section keeps its hidden "Habits" heading and holds `p.empty` > `strong` + text instead of `ul.habits`.
- Every past heatmap cell is `span.hc.l0`, and the today cell adds `.today` and `aria-current="date"`.
- No icons are used on this screen, so no symbol sprite is needed.
