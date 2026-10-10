# Round 2 brief: Danial's Streaky Habit, v1.1.0

**Phase:** design (sdlc:design step 4, critique and converge) · **Date:** 2026-10-10 · **Ledger:** S7 row 3, S1 row 2,
H-02 · **Brainstorm:** "Round 1 rulings" at the end of `docs/brainstorm/brainstorm.md`
**Round 1 brief still applies** (`../BRIEF.md`: who, hard constraints, logo, the copy of every state). This file
says what the owner's pick changes. Where they differ, this file wins.

## The owner's pick (his words, 2026-10-10 21:43)
"1. I like Orbit Rings. 2. For dekstop, make the numbers in the calendar bigger. The habit should be fixed so th at
if thers multiple habit, it doesnt make the input field pushed down. 3. You know what, i think we need to change the
design. Design is like this instead. Colors, fonts and all of that is good. Instead, we list down the habits . Each
list will have 3 functionality. A button or icon to say that we did that habit today ( so its like a daily thing
someone needs to login and click it). But if they forget and they remember later on, they can click the second
button to open a modal. The modal will show all days of the year and we can click the date which we remember we
did. Each list will have its own current and best streak number both at the list level and modal level. The big
calendar on the right, we can have an overview at the top. So it will be an overview at the top, bottom is the div
that contains the list and its scrollable. Not the page but the div only. Outside of that div either before or
after, is the input. Design calendar wise for overview, i like the current orbit ones but just make the number
bigger. 4. For mobile, using the same logic before, have a fixed input below. Then at the top or a button somewhere
that will show overview calendar as a popup or a different page. Below that is the list and the same logic as
desktop."

Clarified 21:49: the year view shows **the last 12 months**. Tapping a day in the overview **opens that day**
(the day editor, every habit for that day).

## The one new direction: F "Orbit List"
**D Orbit Rings' colours, type and ring language, on the owner's list layout.**

Keep from `round-1/d.html` and `d.md`: the tokens (charcoal `--bg` #18191C, `--surface`, amber `--amber` #FFB020 as
the one accent, `--danger`, the radius rule), the system sans stack, the small orbit rings with one segment per
habit and a filled core when all are done, the day editor (P1), the delete dialog (M1), the motion rules. Drop the
big per-habit seven-day ring (ORCH reading (a), flagged).

## Layout
**Desktop, 1280 x 800. The page does not scroll.**
- Header: the mark and "Streaky Habit", today's date.
- **Overview at the top:** the last 12 weeks as D's small rings, **day numbers clearly bigger** than round 1
  (round 1 drew them about 11 px; aim for about 15 to 16 px and grow the rings to suit). It is a band across the
  top, so choose its orientation for the width (weeks as rows like round 1, or weeks as columns like 1.0) so the
  list below still gets real room. Say which you chose and why. The legend (None to All) stays. **Tapping a day
  opens the day editor (P1).** Days after today are closed.
- **Below it, the habit list in its own scroll frame.** Only this frame scrolls. It shows that it scrolls.
- **The add field sits below the list frame, outside it,** like a chat composer. It never moves when habits are
  added (ORCH reading (c), flagged).

**Phone, 390 x 844.**
- Header with an **Overview** button that opens the overview as a full-screen popup (P3), with the same rings,
  numbers sized for touch, tap a day to open P1, Close, Esc.
- The habit list fills the screen and scrolls in its own frame.
- **The add field is pinned to the bottom** of the screen, above the safe area, and never covered by the list.

## The habit row (three functions, his words)
| Part | What |
|---|---|
| Name | The habit's name, long names wrap or clip cleanly at 360 px |
| **Done today** | One button. Ticked when today is done, a second tap unticks it (ORCH reading (e)). The row's numbers and the overview's today cell update at once |
| **Year view** | A second button (a calendar icon with a label for screen readers) that opens P2 for this habit |
| **Current and Best** | Both on the row, labelled "Current" and "Best", for example Current 4 days and Best 9 |

## P2, the habit's year view (new)
- A dialog titled with the habit's name, with its **Current** and **Best** at the top.
- **The last 12 months:** today (Saturday 10 October 2026) back to the same date last year, Friday 10 October
  2025 (366 days with both ends), laid out month by month in D's ring language (one habit, so a day is done or not done, and done differs by more than colour).
  Days after today in October 2026 are closed. Tapping a past day ticks or unticks it, and Current, Best, the row
  and the overview update at once.
- **Delete habit** lives here (opens M1). (ORCH reading (d), flagged.)
- Close, Esc and the backdrop shut it. On a phone it may be a full-screen sheet.

## Sample data (must agree everywhere)
The three habits and their numbers from round 1 D: Read 20 pages Current 4, Best 9 · Stretch 10 minutes Current 2,
Best 5 · No phone after 11pm, no streak yet, Best 14. The last 12 weeks must match round 1 D's grid exactly. Extend
each history back to 10 October 2025 deterministically **without making any run longer than that habit's Best**.
Your check script asserts Current and Best from the histories for all three habits.

## Inventory for round 2
| ID | Screen, popup or state | Content |
|---|---|---|
| K1 | **Habit list with the overview (KEY SCREEN)** | Three habits as rows, the overview, the add field |
| P1 | Day editor | As round 1, opened from an overview day |
| P2 | **Year view (new)** | As above |
| P3 | **Overview popup (phone, new)** | As above |
| M1 | Delete dialog | `Delete "Stretch 10 minutes"?` "Its history is deleted too." Buttons "Cancel" and "Delete habit". Opened from P2 |
| S1 | First visit | "No habits yet." "Add one you want to do every day." Overview all empty |
| S2 | Name error | "Name the habit first.", "Keep it to 40 characters or fewer.", "You already track this habit." |
| S3 | 12 habits reached | "You track 12 habits, the most this app holds. Delete one to add another." Field and Add disabled. Twelve rows, so the list frame visibly scrolls and the add field has not moved |
| S4 | Save warning | "Your habits are not being saved on this device. Changes will be lost when you close this tab." |
| S5 | Saved habits could not be read | "Your saved habits could not be read, so the list was reset." with a dismiss button |

## Prototype rules
- One self-contained file `round-2/f.html`, inline CSS and JS, colours as custom properties, no network.
- Everything clickable through the design's own controls: Done today, the year view and a tick in it, an overview
  day and a tick in P1, Delete habit and M1, Esc and the backdrop to close.
- S1 to S5 behind a small "Prototype states" tab that **never covers content** at 390, 360 or 1280 px (round 1
  flag: the tab covered content in B, C, D and E), sits under any open popup's backdrop, and never overlaps the
  pinned add field.

## Output
`round-2/f.html`, `round-2/f.md` (what you took from round 1, every reading you made, the overview orientation and
why, contrast table, suggestions not built), render checks in `round-2/checks/f/`.
