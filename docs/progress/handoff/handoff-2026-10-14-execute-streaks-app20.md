# Handoff, Streaks v1.1.0 execute, app module, resume at task 20

Written 2026-10-14 by the frontend builder (senior frontend dev agent), after task 19, at about 37 percent of its context. The brief says not to start a new task past about 30 percent, so task 20 was not started.

## Where it stands
- HEAD `9e3dc37` `feat(app): the habit's year view P2, opening it and ticking a day (task 19, R33, R34, R32, R30)`.
- Node 137 of 137. Chromium 95 passed, 18 xfailed. WebKit 94 passed, 1 skipped (CO-1), 18 xfailed. No WebKit failure at HEAD.
- Evidence of task 19 in `docs/modules/app/qa/red-first/20261014-155649-chromium/`, `docs/modules/app/qa/functional/20261014-161055-chromium/` and `.../functional/20261014-161257-webkit/` (the committed tree), and the earlier pair `.../functional/20261014-160452-chromium/` and `.../functional/20261014-160657-webkit/`.
- `docs/modules/app/BUILD.md` section "v1.1.0 task 19" holds the record, five judgment calls and the README reconcile facts.
- Still open from task 18 and untouched, per the orchestrator. The two `BLOCKED_B1` rows of W22 in `tests/browser/test_day_editor.py` (owner ruling H-03).

## Resume point, task 20 (P4, and P1 over P4, R39, R36)
1. Read spec R39, R36 (rule 4) and Tasks line 20. qa.md Feature "The overview popup and the year of all habits" (the three P4 scenarios, "The band's Year opens P4", "P4 on a phone covers P3", "P4 closes and gives focus back to the Year that opened it" with five rows), Feature "The day editor" ("A P4 day opens P1 over P4 on a desktop" and the two P4 rows of "On a phone the chosen day stays in sight above P1", 390x844 2026-09-22 "any value" and 390x844 2025-10-10 "above 0"), and the W table. Golden `docs/design/overview-year.html` with `overview-year.md`, checklist P4-01 to P4-11.
2. Write the P4 tests first. The three P4 scenarios go into `tests/browser/test_overview.py`. "A P4 day opens P1 over P4" and the two P4 rows of W22 go into `tests/browser/test_day_editor.py` (W22's P4 rows carry no mark). Run them once with `--runxfail` in Chromium for RED into `docs/modules/app/qa/red-first/<ts>-chromium/`.
3. Code.
   - `calendar.js`. `layOutMonths(container, todayKey, { idPrefix, cellClass, openCell, closedCell })` is ready for P4, with `idPrefix` "amo" and `cellClass` "hc". The golden's P4 open cell is the day-cell button of the band (`type`, `class="hc"`, `data-key`, `aria-haspopup="dialog"`, `aria-current="date"` for today, a ring svg), named "<yearDate>, <count> of <total> habits". The closed cell is `<span class="hc closed" aria-hidden="true"><svg viewBox="0 0 40 40" aria-hidden="true"><text class="c-num dim" x="20" y="20" dy=".352em">11</text></svg></span>`. Each render renames every P4 button and redraws its ring with `drawRing(svg, doneFlags(habits, key), { today, day })` and `flagChange(button, "pop", animate && changed)`. `drawOverview` has the same rename and redraw loop over `heatmapCells`, so look for one shared helper (DRY, behaviour checked on both).
   - `popups.js`. P4's months and its legend (`div.yr-tools > div.legend`, `drawLegend`).
   - `app.js`. P4 opens from the band's `button.btn-all` (`onPageClick`) and from P3's `button.btn-all` (`onPopupClick`), with Close focused and the opener kept for the focus return (both the same generic path as P2). `render` redraws P4 while it is open (R32). A P4 day already opens P1 through `dayButtonOf` in `onPopupClick`, and `markOpenDay` marks every `button.hc`, so P4's day gets `is-open`. `keepDayInSight` takes the host's `.sheet-head` and `.sheet-body`, which P4 has, so rule 4 should scroll P4 for 2025-10-10.
4. Marks to remove at task 20 (five). W9 `test_today.py::test_R32_R39_a_tick_in_p1_over_p4_updates_p4_and_p3_beneath_it`, W14 `test_popups.py::test_R40_popups_stack_and_esc_closes_the_top_one_only`, and in `test_popups.py` the rows "1280x800 P4" of W15 and W16 and "390x844 P3 then P4" of W18. Read each against its scenario before removing it.
5. Builder self-check. `{temp}/claude/{project-id}/4a8da624-d66b-4188-ba8b-ec57b5279a9d/scratchpad/probe_p2.py` (scratch, outside the project) compares P2 with its golden by pixels. Copy it for P4 (`overview-year.html`, opened from the band's Year at 1280 and from P3's Year below 1024).
6. Remove the marks, run Node, Chromium and WebKit with evidence, BUILD.md section, tick spec task 20, credential gate, commit.

## Gotchas
- The golden's rings are `<use class="seg on" href="#a3-0"/>`, the app draws `<path class="seg on" d="...">` (spec Contracts, the goldens' `<defs>` are not copied). So `conftest.canon_tree` against `overview-year.html` differs at every ring by design. Compare P4's months with the ring svgs read through `ring_parts` and `golden_arcs`, or leave the rings out of the tree comparison and check them on their own.
- In WebKit a mouse click on a button inside an open popup leaves focus on the `dialog` element (qa.md engine table, Q3 accepted). `conftest.focus_after_a_click_in_a_popup(engine, handle, dialog_selector)` asserts it per engine.
- P4 on a desktop is 980 wide and centred, at most 752 tall at 800. Measure boxes after the `rise` animation has ended (`getAnimations().length === 0`).
- Source and docs through Write and Edit only. Task 19 slipped once with `sed -i` on `tests/browser/test_popups.py` (named in BUILD.md, the diff was checked).
- `grep -P` fails here (locale). Check long dashes with Python (`chr(0x2014)`, `chr(0x2013)`).
- A second builder works in `examples/split`. Its processes and files are not ours.

## Processes
None left running. After the last run a sweep by name (python, node, playwright, chrome, headless, webkit, MiniBrowser, bash, sh, cmd) with creation time and command line found only the shell running the sweep. The conftest servers stop themselves and check their ports refuse connections. The scratch probe's server was stopped (exit code read back). No background shell was started.
