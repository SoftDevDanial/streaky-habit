# Direction F, Orbit List

File `f.html`. Render checks, screenshots and `results.json` in `checks/f/`, made by `checks/f/check.py`.

## Thesis
D Orbit Rings' look on the owner's own layout. Each habit is a row with three things on it. Done today, a Year button that opens that habit's last 12 months, and its Current and Best. The last 12 weeks sit on top as an overview of D's small rings with bigger day numbers. Only the list scrolls. The add field sits below the list like a chat composer and never moves.

Design read. A personal one-screen habit tool for one person, phone first, dark charcoal with one amber accent, plain CSS and SVG on system fonts. Dials 5 variance, 4 motion, 5 density.

## What I took from round 1 D
- Every colour token, the system sans stack, the type scale and the radius rule (controls 10, containers 16, sheets 20, round things are circles).
- The small ring. One segment per habit, thick and amber when done, thin and grey when not, and a filled core when every habit is done. Redrawn on a 40 unit box so the day number can be 16 px.
- P1, the day editor, unchanged in content and behaviour. A bottom sheet on a phone, a centred dialog on a desktop, a tick in it moves the numbers everywhere.
- M1, the delete dialog, unchanged.
- The motion rules. A changed ring, tick or Done today dot pops once, a changed number rises in, dialogs rise and the phone sheet slides up. All of it is off under reduced motion.
- The empty state (a dotted orbit), the banners and the field errors.
- Dropped, as the brief says. The big seven-day ring on each habit.

## The overview orientation
**Weeks as columns on a desktop, newest on the right. Weeks as rows in the phone popup, newest on top.**

On a desktop the overview is a band across the top, so its height is what the list loses. Weeks as columns makes the band seven rings tall instead of twelve. At 1280 by 800 the band is 354 px tall and the list frame still gets 210 px in K1 (three rows with room) and 250 px in S3. Weeks as rows would have needed about 560 px and left the list almost nothing. Columns also match 1.0's orientation. The tab order runs day by day, oldest first.

The phone popup has the whole screen but only 360 to 390 px of width. Twelve columns of touch targets do not fit there, seven do. So the popup keeps round 1's rows, newest week on top, which is the layout the owner has already seen on a phone.

## Day number sizes (measured in the check)
| Where | Round 1 D | Round 2 F |
|---|---|---|
| Desktop overview, 1280 | 10.5 px in a 36 px ring | 16 px in a 40 px ring |
| Phone overview, 390 | 9.9 px in a 34 px ring | 16.8 px in a 42 px ring |
| Phone overview, 360 | not measured | 16 px in a 40 px ring |

## How each inventory row is reached
| ID | Control |
|---|---|
| K1 | The default view on load. Also "K1 Key screen" in Prototype states |
| P1 | Tap any day up to today in the overview band (desktop) or in the Overview popup (phone) |
| P2 | The Year button on any row |
| P3 | The Overview button in the phone header (below 1024 px wide) |
| M1 | Delete habit inside P2 |
| S1 to S5 | The Prototype states tab, top right of the header on a desktop and on its own line above the header on a phone |

Esc closes the top popup first (P1 over P3, M1 over P2). The backdrop closes P1, P2 on a desktop and M1. Close buttons close P1, P2 and P3.

## Readings I made
1. **The Year button is a word, not an icon.** The brief asks for a calendar icon. No Phosphor calendar path is on disk (the project has no icons file, and round 1 a, b, c, d and e inline only x, plus, check and trash), and I may not draw one. So the button reads "Year" with the accessible name "Year view, Read 20 pages". A word is also clearer to a first-time user. Swap in Phosphor's calendar icon beside it when the path is copied from the package.
2. **Messages sit above the add field.** The three name errors and the 12-habit note appear at the top of the add bar, so the bar grows upward and the field stays put. Below the field, a wrapped note would push the field up. On a desktop the message lines up with the field, not the label.
3. **The list frame fits its rows, then scrolls.** With three habits the frame is as tall as its rows and the add bar stays docked at the bottom. As habits are added the frame grows until it meets the add bar, then scrolls. A fade at the top or bottom edge shows there are more rows behind it, and the cut row shows it too.
4. **The Prototype states tab sits in the page flow,** never fixed or floating, so it cannot cover content or the add field at any width. It sits under every popup's backdrop.
5. **The date on a phone** sits on its own line under the header, so "Done today" has its day in sight.
6. **The Overview button carries today's small ring,** so a Done today tap shows on a phone without opening the overview. Its accessible name adds "today 1 of 3 habits done".
7. **P2 shows the newest month first.** On a desktop it is a centred dialog with three months across and six in view, the rest scroll inside it with a soft edge shadow. On a phone it is a full-screen sheet, one month across, 44 px day cells.
8. **A P2 day is a bead.** Done is a filled amber bead with a dark number, not done is a hollow grey ring, today has D's halo. Done days in a row are joined by an amber thread, the idea of the mark (beads on one thread). A run that crosses a week or month edge leaves a short stub at that edge.
9. **The year's two Octobers.** October 2025 starts on the 10th, days 1 to 9 are left blank because they are outside the 12 months. October 2026 shows the 11th to the 31st dim, and they cannot be tapped. P2 has 366 day buttons.
10. **Delete habit in P2 is quiet.** Grey with D's bin icon at rest, red edge and text on hover. The red fill belongs to the confirm in M1, as D's bin did.
11. **Best has no unit.** "Best 9" as in the brief's example and the 1.0 rule. Current reads "4 days". "No streak yet" replaces the Current number at 0, and Best is hidden at 0.
12. **Best lines up down the list on a desktop.** The Current block has a fixed width, so Best sits in one column with or without a streak.
13. **The extended histories.** Before Monday 20 July each sample habit runs a seeded walk back to Friday 10 October 2025. No extended run reaches that habit's Best, and a run that would join the first run of the 12 weeks is cut on 19 July. A quiet fortnight from 22 December to 3 January makes the year look lived in. Best stays 9, 5 and 14 from round 1's twelve weeks, and the check asserts it from the histories.
14. **The nine extra habits in S3** get a full year of seeded history with runs up to 11 days.
15. **P1 on a phone opens over the Overview popup** as D's bottom sheet, and the popup scrolls so the chosen day stays visible above the sheet with its amber outline.
16. **Breakpoints.** The overview band shows from 1024 px. Below that the phone layout with the Overview button applies, and from 768 px the popups become centred dialogs.
17. **New copy, kept plain.** P2's subtitle "The last 12 months" and its hint "Tap a day to mark it done or not done." The overview keeps round 1's "Tap a day to change it."
18. **After a delete** from P2, M1 and P2 close together and focus moves to the next row's Year button (or the field when the list is empty).
19. **A new habit** scrolls the list to the bottom so its row is in sight.

## What it costs
- On a desktop the habit names sit far from their buttons on a 1040 px row. Rows are easy to scan by column, but the middle of the row is empty.
- At 1280 by 800 the list shows three and a half rows before it scrolls. Twelve habits is a lot of scrolling in a small frame.
- P2 is 366 buttons. Keyboard users tab through a long grid (see suggestions).
- The overview with twelve habits draws twelve short segments per ring, which reads as a dotted circle. That is D's rule, unchanged.

## Contrast (computed in `checks/f/check.py` from the page's own tokens)
| Pair | Ratio |
|---|---|
| ink on bg, body text | 15.14 |
| ink on surface, habit names | 13.69 |
| ink on surface-2, dialog text | 12.17 |
| ink-soft on bg, the date | 7.64 |
| ink-soft on surface, labels and overview numbers | 6.91 |
| ink-soft on surface-2, dialog labels and Delete habit at rest | 6.14 |
| amber on bg, accent | 9.61 |
| amber on surface, Current on a row | 8.69 |
| amber on surface-2, Current in P2 | 7.72 |
| on-amber on amber, Done today, Add, done numbers | 9.61 |
| on-amber on danger, Delete habit in M1 | 6.32 |
| danger on surface, field error | 5.71 |
| danger on surface-2, Delete habit in P2 on hover | 5.08 |
| ring on surface, not-done outline (3 to 1 needed) | 3.97 |
| ring on surface-2, not-done bead in P2 (3 to 1 needed) | 3.53 |
| ring on bg, Overview button edge (3 to 1 needed) | 4.39 |
| ring on field, input border (3 to 1 needed) | 4.64 |
| focus ring on bg and on surface-2 | 15.14 and 12.17 |

Done and not done differ by more than colour everywhere. Done today fills and shows a check, a P2 day fills solid against a hollow ring, an overview segment is thick against thin and a full day fills its core, and a P1 tick fills and shows a check.

## Suggestions (not built)
- Phosphor's calendar icon beside the word Year, copied from the package.
- Arrow keys inside the overview and the year view (one tab stop per grid, arrows move by day and week), instead of 84 and 366 tab stops.
- Previous and next day arrows in P1, to walk through missed days without closing it.
- A today summary in the band's empty left column on a desktop, today's ring large with "1 of 3 done".
- A jump to month in P2 on a phone, where a year is a long scroll.
- Mark where a habit started in P2 once a start date is stored (1.0 stores none).
