# Direction D, Orbit Rings

File `d.html`. Render checks and screenshots in `checks/d/`.

## Thesis
Each habit is a ring of its last seven days that fills through the week. The current streak sits in the ring's centre, the best streak sits to its right. Left is Current, right is Best, both named.

Design read. A personal one-screen habit tool, phone first, futuristic but minimal in a layered dark charcoal like a chat app, plain CSS and SVG on system fonts, with the ring as the one expressive element. Dials 6 variance, 4 motion, 4 density.

## The bet
- **The ring is the week and the control.** The seven day buttons sit on an open orbit, oldest at lower left, today at lower right, clockwise over the top. Two done days in a row are joined by a thick amber arc, so a run reads as a lit stretch of orbit. A dashed arc from a done yesterday into an open today says the streak still holds. A run that started before the week trails off into the gap at the bottom.
- **Current at the centre, Best beside it.** Current is the big amber number inside the ring with the word Current above it. Best is a smaller white number to the right with the word Best above it. Best reads as second by size and colour.
- **The 12-week grid is a field of small rings.** Each day is a small ring with one segment per habit. A done habit lights its segment thick and amber, a missed one stays a thin grey line. A day with every habit done also fills its core. The day number sits in each ring, so a missed date is easy to find and tap. Newest week on top, so the recent missed days are the first thing seen.
- **The day editor shows the change.** On a phone it is a bottom sheet and the page scrolls so the chosen day stays visible above it, outlined in amber. Its header carries that day's ring large. Each habit row shows Current and Best, so a tick visibly moves the numbers, the small ring in the header, the cell in the grid and the card ring behind.
- **Desktop tiles.** At 1280 the rings tile two by two with the new-habit form in the next free tile (a dashed slot), and the grid sits in a sticky panel on the right. The whole key screen fits in 1280 by 800.

## What it costs
- Each phone card is about 214 px tall, so three habits fill the first screen at 390 by 844 and the grid starts below the fold. Twelve habits make a long page.
- The ring spends space on weekday letters and an open gap. A strip of seven cells would be smaller.
- Day buttons carry the day of the month only. The weekday is the letter outside each node.
- Tick targets on the ring are 44 px circles spaced 56 px apart, so they are fine, but they are not in a straight row, which takes a moment to learn.

## 1.0 rules this changes
- **Heatmap levels.** 1.0 shades each day in five tones by share done. Here each day shows one segment per habit, lit when done, and a filled core when all are done. With three habits this matches levels 0, 1, 2 and 4 one to one. The accessible name is unchanged ("Tue 22 Sep, 1 of 3 habits").
- **Heatmap orientation.** 1.0 has weeks as columns with the newest on the right. Here weeks are rows with the newest on top, seven weekday columns, on every width.
- **The strip.** 1.0 shows the weekday and day number in a straight row. Here the seven days sit on the ring, number in the node, weekday letter outside.
- **Best shows "days".** The Best block reads Best, the number, then "days" (or "day" for one), to sit level with Current. The day editor rows keep the plain "Best 9" form.
- **New habit form sits below the habits** on every width, as in 1.0, but drawn as a dashed slot.

## Tokens
| Token | Value | Role |
|---|---|---|
| `--bg` | #18191C | page, dark charcoal |
| `--surface` | #212226 | habit cards, grid panel |
| `--surface-2` | #2A2B30 | dialogs, banners |
| `--raise` | #35373D | row hover in dialogs, open day |
| `--field` | #121316 | input fill |
| `--line` | #33353B | card and dialog edges |
| `--track` | #4A4C53 | orbit track (decorative, the nodes carry state) |
| `--ring` | #7C7F88 | not-done outlines, input border |
| `--ink` | #EDEEF0 | text, focus ring |
| `--ink-soft` | #A8ABB2 | labels, date, grid numbers |
| `--amber` | #FFB020 | the one accent. Done, runs, Current, Add |
| `--on-amber` | #18191C | text on amber and on danger |
| `--danger` | #FF6B66 | errors, Delete habit |

Type is the system sans stack only. Radius rule is controls 10, containers 16, sheets 20, round things are circles.

## Contrast (computed in `checks/d/check.py`)
| Pair | Ratio |
|---|---|
| ink on bg, body text | 15.14 |
| ink-soft on surface, labels | 6.91 |
| amber on bg, accent | 9.61 |
| amber on surface, Current number | 8.69 |
| on-amber on amber, Add and done day numbers | 9.61 |
| on-amber on danger, Delete habit | 6.32 |
| danger on bg, field error | 6.32 |
| ring on surface, not-done outline (3 to 1 needed) | 3.97 |

## Motion
On load each lit arc draws itself once. After a tick, the node, the grid cell and the editor's tick pop briefly and a changed number rises in. Dialogs fade and rise, the phone sheet slides up. All of it is off under reduced motion, and the arcs then show at once.

## Suggestions (not built)
- Previous and next day arrows in the day editor, to walk back through missed days without closing it.
- Anchor the desktop day editor beside the chosen cell instead of the centre of the screen.
- A small marker on rows of the grid where a habit was added, once a start date is stored (1.0 stores none).
- Let the ring's run arcs carry a faint glow only on today, as the single reward moment, if the owner wants more spark.
