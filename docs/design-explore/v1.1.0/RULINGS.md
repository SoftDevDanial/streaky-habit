# Design rulings, Streaks v1.1.0

**Date.** 2026-10-11 · **Ruled by.** the owner (**USER**), who picked the option recommended to him on each of four questions

The composer listed copy, interaction rules and points the brainstorm leaves open (`final/SELF-CRITIQUE.md`). They are ruled here so the plan phase does not have to guess. 1.0's rulings (`../RULINGS.md`) still stand, the browser floor among them, unless a ruling here replaces one.

## Added copy, approved (USER)
All copy in the "Copy the brainstorm does not word" table of `final/SELF-CRITIQUE.md` is approved as written.

## Interaction rules, approved (USER)
All seven rules in "Interaction rules I specified or carried from f2" of `final/SELF-CRITIQUE.md` are approved as written.

## Small points (USER)
| # | Point | Ruling |
|---|---|---|
| 1 | The phone header sat 8 px from the top once the Prototype states tab was gone, f2's padding (open item 3) | 12 px, the desktop value. Applied to `system.css` and every golden (`d786d25`) |
| 2 | Ring and bead numbers with a "1" sit up to about 1 px left of centre (`text-anchor:middle` centres the advance, not the ink). The vertical measure passes (open item 1) | Leave it. A fix would need per-glyph offsets tied to one font |
| 3 | Desktop day cells under 44 px, P2 40 by 40 and P4 42 by 44 at 1280, P3 43.1 wide at 360, all f2 (open item 2) | Accepted. WCAG 2.5.8 (24 px) is met, and larger cells would cost the three months across |

## The mark (USER)
Redraw the mark with the logo-design skill. Four directions, each checked by a separate QA agent, and the owner picks one on the design board. Streaky Habit's mark grows from the orbit ring. No "Danial" and no "D" in the mark. The pick replaces the one inline `<svg class="mark">` and the tab icon's data URI in every golden, then `final/checks/check.py` runs again.

**Three on the board (USER, 2026-10-11 17:40).** Five directions were drawn, T2 and T5 retired at QA (`logo/QA.md`). The owner chose to open the board with the three that passed, T1, T3 and T4, rather than draw a fourth.

**Board round 1 (USER, 2026-10-11 17:50).** Ratings T1 3, T3 1, T4 1, and Build on this on T1. His comment on T1, verbatim, "I like the old logo where 3 dots connected top right left and bottom left. I think we go with that logo but at top right dot, we add 1 outer line similar to top right of the dot similar to this logoto". The orchestrator sketched four readings (`.claude/logo-boards/shots/sketch-t6.png`, not a design). He picked A, the 1.0 mark with its open bead kept and one short outer arc, and moved the arc, "Instead of line at top right, try to do at top left dot instead." That is T6. T3 and T4 are out.

**No background, no tile (USER, 2026-10-11 20:40).** Asked about T6, then confirmed for Split. His words, "The logo will not have a background color or tile. So its just purely the yellow streak. Favicon, logo and everything uses the one without a background or in other words transparent background". The favicon is the mark alone in `#FFB020` on a transparent 16 x 16 ground, no `#18191C` tile. **T6 favicon exception (USER, same hour).** He accepted the open bead's 1 px ring at 16 px, as in 1.0's favicon (constraint 7 waived for that one feature).
