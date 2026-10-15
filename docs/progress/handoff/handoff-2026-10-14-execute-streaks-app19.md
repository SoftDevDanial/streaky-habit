# Handoff, Streaks v1.1.0 execute, app module, resume at task 19

Written 2026-10-14 by the frontend builder (senior frontend dev agent), at about 34 percent of its context, after task 18. The brief said not to start a new task past about 30 percent.

## Where it stands
- HEAD `d4fd38b` `feat(app): the day editor P1, opening a day and ticking it (task 18, R36, R37, R32)`.
- Node 137 of 137. Chromium 73 passed, 26 xfailed. WebKit 72 passed, 1 skipped (CO-1), 26 xfailed. No WebKit failure at HEAD.
- Evidence of task 18 in `docs/modules/app/qa/red-first/20261014-151839-chromium/`, `docs/modules/app/qa/functional/20261014-153509-chromium/`, `.../functional/20261014-153212-webkit/` (and the earlier `20261014-152547-chromium`, `20261014-152824-webkit`), `docs/modules/app/qa/day-editor-b1/20261014-153746-chromium/`.
- `docs/modules/app/BUILD.md` section "v1.1.0 task 18" holds the record, the blocker B1, the judgment calls and the README reconcile facts.

## Open for the orchestrator
- **B1 (blocker, two test rows).** R36 rule 4 cannot hold for P3's lower weeks on a phone. The golden P3 fits its 12 weeks with no overflow (sheet body scrollHeight equals clientHeight, 698 at 360x780, 762 at 390x844), and P1's sheet top sits at 487 and 551, so 2026-07-20 stays under P1. The W22 rows "390x844 P3 2026-07-20" and "360x780 P3 2026-07-20" in `tests/browser/test_day_editor.py` carry `BLOCKED_B1` (strict xfail naming the blocker). Recommended, a design-phase ruling that gives P3 room while P1 is open (rule 4 is owner-approved), else accept a residual, drop the rows and add a UAT note.
- **Q3 (qa.md wording).** In WebKit a mouse click on a button inside a modal popup leaves focus on the `dialog` element, not `body` (measured on P1's ticks). qa.md's engine table has a new dated row. The scenario lines "In WebKit document.activeElement is body" in "Ticking a past day in P1" and "Ticking a day in the year view" need the planner's wording.
- Judgment call 1, `pop` on `div.day-mini` after a tick (R32's letter, no CSS rule, so nothing moves).

## Resume point, task 19 (P2, R33, R34, R32, R30)
1. Read spec R33, R34 and Tasks line 19, qa.md Feature "A habit's year view" (lines about 954 to 1041), W3, W7, W10, W12 P2 row, W13 P2 row, W15 "1280x800 P2", W16 "1280x800 P2", W17 "1280x800 P2", W18 "390x844 P2", W19 (written at 19 with `xfail(strict=True, reason="task 21")`) and W21 (the `@R30` clipboard scenario into `tests/browser/test_engines.py`, no mark). Golden `docs/design/year-view.html` and `year-view.md`.
2. Write `tests/browser/test_year.py` and the W21 test first, run them once for RED into `docs/modules/app/qa/red-first/<ts>-chromium/`.
3. Code. `calendar.js` draws the month sections and beads (`yearMonths`, `yearDate`, `monthTitle`, classes `on`, `today`, `l`, `r`, closed and blank cells). `popups.js` P2's head (`#yr-title`, `p.yr-stats` through `view.renderStats`). `app.js` opens P2 from a row's Year (`view` needs a `yearIndexOf(target)` like `doneTodayIndexOf`), ticks a bead with `toggleDay(habits, index, key, today)` and redraws P2 in `render` while it is open. Close and focus return are already generic (`onPopupClose`). Delete habit in P2 is task 22's.
4. In WebKit expect focus on `dialog.dlg-year` after a mouse click on a bead (Q3), not `body`.
5. Remove the task 19 marks, run Node, Chromium and WebKit with evidence, BUILD.md section, tick spec, credential gate, commit.

## Gotchas
- `animate && drawRing(...)` short-circuits and skips the draw. Compute the change first (task 18 hit it in `renderDayEditor`).
- Scratch probes that start their own `http.server` and import `conftest.open_app(..., base_url=...)` live in the session scratchpad, never in the project.
- `grep -P` fails here (locale). Check long dashes with Python (`chr(0x2014)`, `chr(0x2013)`).
- A second builder works in `examples/split`. Its processes and files are not ours.

## Processes
None left running. Sweep after the last run by name (python, node, playwright, chrome, headless, webkit) and by the conftest ports, nothing found. No background shell was started.
