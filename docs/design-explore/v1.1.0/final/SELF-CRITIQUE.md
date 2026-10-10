# Self-critique (design step 8)

**Date** 2026-10-11
**Files walked** `system.md`, `system.css`, the nine goldens and their `.md` files, `sample-history.json`, `MANIFEST.md`, `LINKS.json`
**Evidence** `checks/check.py` and `checks/results.json` (97 of 97 asserts pass), screenshots in `checks/shots/` (27), side by side with f2 in `checks/compare/` (23, golden left, f2 right), probes in `checks/peek.py`
**Skills applied** `taste-skill:taste-skill` and `frontend-design:frontend-design`, both invoked. What transferred is at the top of `system.md`

## Walk against the checklist

| Check | Result | How it was checked |
|---|---|---|
| One primary action per view | K1, S1, S3 Add (disabled in S3). P1 none, ticks are toggles. P2 none, Delete habit is quiet. P3 and P4 none. M1 Delete habit (danger) with Cancel | screenshots |
| Spacing and radius on the scale | yes, f2's values unchanged, f2's 2 px grid literals named in `system.md` | style block equal to `system.css` in every screen golden (asserted) |
| AA contrast | every text pair 4.5 or more, every graphic 3 or more, lifted pair 5.17 | `data.contrast()` from `system.css`, asserted |
| Every state present | K1, P1, P2, P3, P4, M1, S1, S3 as screens, S2 (3), S4, S5 on the sheet | `MANIFEST.md` against the inventory |
| Real, consistent copy | every string from f2, which took it from the brainstorm and the round briefs | read against f2 and `BRIEF.md` |
| Figures | Current and Best on every golden equal `sample-history.json`. 83 band rings in four goldens, 83 P3 rings in two, 366 P4 rings, 366 beads, all equal the history | asserted |
| No template tells | no eyebrows, no all-caps labels, no middle-dot strings, no long dashes (0 in `final/`, asserted), no gradients but the functional fades, Phosphor icons only, one accent | sweep |
| 360, 390, 1280 | no sideways scroll at 360, no page scroll at 1280 for K1, S1, S3 and every popup golden | asserted |
| Console and network | 0 errors, 0 requests | asserted on 27 loads |
| Reduced motion | all animation off | system rule unchanged from f2 |

## Check results in numbers

| Measure | Result |
|---|---|
| Ring numbers, vertical ink offset from the ring's centre | at most 0.25 px at 390 (P3, P4) and 1280 (band, P4), all goldens |
| Bead numbers, vertical | at most 0.125 px at 390, 0.25 px at 1280 |
| Lifted pair | open day's thin segment computes to `rgb(168, 171, 178)` (`--ink-soft`), 5.17 to 1 on `--raise` |
| Targets under 44 | only day cells, all inherited from f2. P2 at 1280 40 by 40, P4 at 1280 42 by 44, P3 at 360 43.1 by 46 |
| Pixels that differ from f2 (threshold 24 of 255) | 0.00 percent for every golden and width except P2 (1.34 at 360, 1.21 at 390, 0.41 at 1280, the bead numbers) |

## Every visible difference from f2, and why

| # | Difference | Where | Reason |
|---|---|---|---|
| 1 | No Prototype states tab. On a phone the header starts 30 px higher. On a desktop the date sits at the right edge | every golden | The brief bars the tab, it was review tooling. The compare screenshots hide it on the f2 side too, so the diffs show only real changes |
| 2 | A thin not-done segment on the open day draws in `--ink-soft` | `day-editor.html` (band at 1280, P3 on a phone), and on hover everywhere | Ruling 1, 2.97 to 5.17 |
| 3 | Ring numbers sit up to 0.25 px higher (`dy .352em` for `.367em`) | every ring | Ruling 2. f2 measured 0.34 px low on average at 390, 0.5 at worst. Below the diff threshold, invisible at 1x |
| 4 | Bead numbers sit about 0.7 px higher on a phone, and use proportional figures | `year-view.html` | Ruling 2. f2's beads were 0.72 px low. This is the only difference the pixel diff sees |
| 5 | K1 under P3 and P4 is drawn without its band | `overview.html`, `overview-year.html` | Never visible on a phone (full-screen sheets). At 1280 P4 hides all but 5 px a side, and P3 cannot open at 1280 at all. Kept the goldens within the session's context budget |
| 6 | `overview.html` at 1280 shows P3 as the 520 px dialog over a band-less K1 | `overview.html` | f2 cannot open P3 at 1024 and up. The render is reference only, said in `MANIFEST.md` |

Not visible, for the builder. Arcs are `<use>` of shared paths, ring svgs drop IE's `focusable`, `data-act` and `data-fk` hooks are gone, popups are `<dialog open>` with a `.scrim` and `inert` behind (system stand-ins), `states.html` carries the part of `system.css` its frames use.

## What I changed while composing

| # | Found | Change |
|---|---|---|
| 1 | A CSS strut (`.bead::before`, baseline flex) centred beads at 1280 but left them 0.72 px low at 390. Measured that HTML text snaps its baseline to whole pixels, so 0.28 high or 0.72 low were the only choices | Bead numbers became SVG text, the ring's own method, which moves in quarter pixels |
| 2 | f2's `.367em` left P3 rings 0.5 px low at 390 | Measured the figures' half height, `.352em`, for rings and beads |
| 3 | Writing K1's band under every popup ran the context budget down | Drew K1 without the band only where it can never show (difference 5) |

## Open for the owner
1. **Horizontal ink.** `text-anchor:middle` centres the advance, not the ink. Numbers with a "1" sit up to 0.83 px left in the band, 1.05 px in P3 at 390, 0.78 px in beads. The brief's measure was vertical (ink rows), and it passes. A horizontal fix needs per-glyph offsets tied to one font, so I left it.
2. **Desktop day cells under 44.** P2 40 by 40 and P4 42 by 44 at 1280, P3 43.1 wide at 360, all f2. WCAG 2.5.8 (24 px) is met. Larger would cost the three-months-across layout.
3. **Phone header at 8 px from the top** now the tab is gone. It is f2's padding. A 12 px top (the desktop value) would read calmer.

## Copy the brainstorm does not word (for the owner's ruling)

| Copy | Where | Origin |
|---|---|---|
| Overview, accessible name "Overview, today N of T habits done" | phone header | F |
| Last 12 weeks, Tap a day to change it. | band, P3 | round 1, kept by F |
| None, All | legends | round 1 |
| Year, "Year view, all habits", "Year view, Read 20 pages" | band, P3, rows | F and F2 |
| Done today, "Done today, Read 20 pages" | rows | F |
| Current, Best, days, day, No streak yet | rows, P2 | brainstorm words, F's layout |
| The last 12 months, Tap a day to mark it done or not done., Done, Not done | P2 | F |
| All habits, The last 12 months, Tap a day to change it. | P4 | F2 brief |
| Delete "Read 20 pages" (bin name) | rows | F2 brief |
| Delete habit | P2 button, M1 confirm | brainstorm |
| Tuesday 22 September, 1 of 3 habits, Current 4 days, Best 9 | P1 | round 1 D |
| "Ddd D Mon, N of T habits", "Ddd D Mon YYYY, N of T habits", "Mark Ddd D Mon YYYY as done" | day names | 1.0 rule, year added by F2 |
| "0 of 0 habits" | S1 day names | the 1.0 rule applied literally |
| Saturday 10 October | header date | 1.0 |
| Close, Dismiss note, New habit, Add | dialogs, S5, composer | 1.0 and round 1 |

## Interaction rules I specified or carried from f2 (for approval)
1. Focus on open. P1 the first tick, P2, P3 and P4 Close, M1 Cancel. Closing returns focus to the control that opened it.
2. Esc closes the top layer only. On a phone P1, then P4, then P3. The backdrop closes P1, P2, P4 and M1 on a desktop, and P1 and M1 on a phone.
3. After a delete from a row, focus goes to the next row's bin, the previous one when the last row went, the field when the list empties. From P2 it goes to the next row's Year.
4. On a phone P1 opens as a bottom sheet and its host (P3 or P4) scrolls so the chosen day stays in sight above it, outlined.
5. A tick anywhere (Done today, P1, P2) redraws every ring, row, Current and Best at once.
6. Ring and bead numbers are SVG text on the baseline at the shape's centre, dropped `.352em`.
7. Name errors show when Add is pressed, the typed text stays, typing clears the error. Dismiss note moves focus to the field.
