# Direction C, Daylight Instrument

**File** `c.html` · **Checks** `checks/c/` (script `check.py`, screenshots beside it)

## Thesis
Futuristic in daylight. The app reads like a precise instrument on a cool white page. Each habit is a channel with two oversized thin numerals, Current on the left in electric cobalt and Best on the right in ink, split by a 1 px rule. Past days sit in a matrix of small square gauges that fill from a zero line.

Design read. A personal one-screen habit tool for one person on a phone, shown to visitors, in a light precise-instrument language on system fonts and plain CSS, with the numerals as the single bold element. Dials 5 variance, 3 motion, 5 density.

## The bet and its cost
- **Bet.** The streak is the number, so the number is huge. A glance answers "how long is this run" and "how far from my best" without reading a label, and the left and right split answers the owner's "left side is current and right is best" by position and colour.
- **Bet.** The heatmap becomes a field of gauges. Each day is a small square that fills a quarter, a half, three quarters or all the way, so levels differ by fill height and not only by colour. It reads as an instrument readout, not a GitHub clone.
- **Cost.** The numerals take height. On a 390 px phone the first screen shows about two and a half habits, and the matrix sits below the add field, so past days need a scroll on a phone. On desktop the whole page fits in 1280 by 800.
- **Cost.** Light themes risk looking like a spreadsheet. The answer here is thin numerals, a single cobalt, square gauges with air around them, and rules only where they separate real content. No grid lines, glow or glass.

## Heatmap shape (changes a 1.0 rule on phones only)
- **720 px and up** keeps the 1.0 rule. 12 columns, one per week, newest on the right, rows Monday to Sunday.
- **Below 720 px** the same matrix is transposed. 7 weekday columns by 12 week rows, oldest week on top, today at the bottom right. Twelve columns cannot give 44 px tap targets on a phone, and every day must now be tappable (P1). Reading order stays chronological, left to right then top to bottom, so it is a pure transpose and today is always the last cell.
- The axis is a ruler. Each week carries its Monday date, and the month name appears on the first week of each month. Weekday names run along the other side.
- One DOM drives both shapes. Each label and cell carries its phone and desktop grid position as custom properties.

## Tokens (all on `:root`)
| Token | Hex | Role |
|---|---|---|
| `--bg` | #F5F7FB | cool white page |
| `--panel` | #FDFEFF | desktop faceplates, day editor, dialog, input |
| `--cell` | #E5EAF2 | empty gauge body (decorative) |
| `--rule` | #D6DCE7 | 1 px hairlines (decorative) |
| `--line` | #7A869C | control borders, gauge zero line (3:1 and up) |
| `--ink` | #0E1729 | text, Best numerals, today frame |
| `--ink-soft` | #4A5570 | labels, units, dates |
| `--cobalt` | #1E46FF | the one accent. Current numerals, done segments, gauge fill, Add |
| `--cobalt-deep` | #1535C9 | hover, focus ring, small accent text |
| `--danger` | #C21F35 | field errors, Delete habit |

Type is the system stack only. Numerals are weight 300 with tabular figures at 60 to 72 px on phones and 84 px on desktop. Radius grows with elevation, 2 px mini gauges, 4 px controls and cells, 8 px faceplates, 14 px floating surfaces.

## How each inventory row is reached
| ID | How |
|---|---|
| K1 | Default view. Tap any strip segment to tick it. Ticking today on "Stretch 10 minutes" moves Current from 4 to 5 and lifts today's gauge from a quarter to a half |
| P1 | Tap any past day in the "Last 12 weeks" matrix. Close with the x, Esc or the backdrop. Try Tuesday 22 September and tick "Read 20 pages". It closes the one gap between two runs, so Current and Best both jump to 38 and the gauge rises. Days after today are not buttons |
| M1 | The bin on any habit. Esc, Cancel or the backdrop keep it. Delete habit removes it |
| S1 to S5 | The dark dashed "Prototype states" button at the bottom right opens a list. S2 also works for real through the field (empty, 41 or more characters, or "read 20 pages") |

## Decisions worth flagging
- **Delete habit sits on the left and Cancel on the right.** The bin is always at the right edge of a habit, so a slow second click on the bin lands on Cancel or the backdrop, never on Delete habit. Focus opens on Cancel. This answers C6 without a delay.
- **No streak yet replaces the big numeral.** A big zero would contradict the copy rule, and the missing number is itself the signal. Best is hidden at 0 as in 1.0.
- **The day editor shows each habit's streak line and the day's own gauge with "N of 3 habits".** Nothing new is counted. These are the streak line and the cell's accessible name made visible, so a tick shows its effect at once.
- **Phone day editor is a bottom sheet** and the page scrolls so the opened day sits just above it. On desktop it opens beside the cell, with a light scrim so the numerals behind stay readable as they change.
- **With no habits the matrix cells are not buttons** (disabled), since there is nothing to tick.
- **Keyboard.** The matrix is one tab stop with arrow keys, in the direction of each layout.

## Check results (`python -B checks/c/check.py`)
- Console errors 0 at 390, 360 and 1280.
- Sideways scroll at 360 is 0 for K1, P1 open, S1, S2 and S3.
- Targets at 360. Matrix cell 40.8 px with a 42.8 px pitch, strip day 43.4 by 82, icon buttons 44 by 44, field and buttons 48 tall. At 390 the matrix cell is 45.1 and the strip day 47.7.
- Streaks from the history. Read 20 pages 18 and 19, Stretch 10 minutes 4 and 9, No phone after 11pm no streak and 6. After the 22 September tick Read 20 pages shows 38 and 38.
- Reduced motion. Transitions read 0s.

| Pair | Ratio | Use |
|---|---|---|
| ink on bg | 16.69 | body text |
| ink on panel | 17.73 | text on faceplates and dialogs |
| ink-soft on bg | 6.93 | labels, dates, units |
| ink-soft on panel | 7.36 | dialog body |
| cobalt on bg | 5.80 | accent, Current numerals, done segments |
| cobalt on panel | 6.16 | accent on faceplates, gauge fill |
| cobalt on cell | 5.15 | gauge fill against the empty gauge |
| on-cobalt on cobalt | 5.91 | Add label, check marks |
| cobalt-deep on panel | 8.72 | Current line in the day editor |
| danger on bg | 5.53 | field error |
| on-cobalt on danger | 5.63 | Delete habit |
| line on bg / panel / cell | 3.42 / 3.64 / 3.04 | control borders, gauge zero line |
| focus on bg / panel | 8.21 / 8.72 | focus ring |

## Suggestions (not built)
- Let the matrix scroll the phone page to the opened week when the day editor is closed with a tick, so the change is seen in place on long lists.
- A count-up on the numerals when a back-filled day merges two runs, kept under 300 ms and off under reduced motion.
- On desktop, the band under the rack leaves white space below the add field. A future round could try the add field as the rack's footer row instead.
- Swipe down to close the phone sheet, alongside Esc, the x and the backdrop.
