# Handoff, Streaks v1.1.0 execute, app module, resume at task 21

Written 2026-10-14 by the frontend builder (senior frontend dev agent), after task 20, at about 36 percent of its context. The brief says not to start a new task past about 30 percent, so task 21 was not started.

## Where it stands
- HEAD `185ad97` `feat(app): P4, P1 over P4 and the room of rule 4 (task 20, R39, R36)`.
- Node 137 of 137. Chromium 120 passed, 11 xfailed. WebKit 119 passed, 1 skipped (CO-1), 11 xfailed. No WebKit failure at HEAD.
- Evidence of task 20 in `docs/modules/app/qa/red-first/20261014-201624-chromium/` and `.../red-first/20261014-202139-chromium/` (the RED runs, the second with `measurements.json`), and `docs/modules/app/qa/functional/20261014-202919-chromium/` and `.../functional/20261014-203132-webkit/` (the committed tree).
- `docs/modules/app/BUILD.md` section "v1.1.0 task 20" holds the record, the measurements against the spec, six judgment calls and the README reconcile facts.
- Blocker B1 of task 18 is closed by the room. No `BLOCKED_B1` mark is left.

## Resume point, task 21 (the composer, R10, R11, R12)
1. Read spec R10, R11, R12 and Tasks line 21. qa.md Feature "Add a habit" and the W table rows W2, W4, W5, W19 and W20 ("Scenarios that wait on a later task").
2. Write `tests/browser/test_add.py` from Feature "Add a habit", and W20 "Deleting one of twelve opens the composer again" with `xfail(strict=True, reason="task 22")`. Run them RED in Chromium into `docs/modules/app/qa/red-first/<ts>-chromium/`.
3. Code. `src/app.js` has no `submit` listener on `form.composer` yet, so Add or Enter navigates (W19's RED at task 19 failed there). Add a `submit` listener with `preventDefault()`, the `input` listener of R11, the add through `addHabit` and `edit` (one save, R32), the messages of R11 (`#nh-msg` above the field, `aria-invalid`, focus to the field after a rejected name in both engines), and the scroll of `div.frame` so the new row lies fully inside it (CG-15). `view.renderComposerLimit` already draws R12's twelve-habit state, and `view.renderRows` already rebuilds the rows when the names change.
4. Marks to remove at task 21 (four). W2 `test_entry.py::test_R1_R29_the_app_works_from_a_sub_path`, W4 `test_render.py::test_R6_R10_a_new_habit_shows_no_best_block`, W5 `test_render.py::test_R5_the_fades_follow_the_rows_and_a_resize`, W19 `test_year.py::test_R34_R10_a_day_before_a_habit_was_added_can_be_ticked`. Read each against its scenario before removing it. W2 needs the sub-path server the conftest starts.
5. Run Node, Chromium and WebKit with evidence, BUILD.md section, tick spec task 21, credential gate, commit.

## Gotchas
- `syncDayButton` in `src/calendar.js` must draw the ring before it reads `animate`. Writing `animate && drawRing(...)` skips the drawing at boot (my slip at task 20, caught by the P3 scenario).
- WebKit lays `100dvh` out in 1/64 px units (a full-screen box measured 843.984375 tall at 844). Compare boxes within 0.5 px, as `test_year.py` and `test_overview.py` do.
- In WebKit a mouse click on a button inside an open popup leaves focus on the popup's `dialog` (qa.md engine table, Q3). `conftest.focus_after_a_click_in_a_popup` asserts it per engine. Outside a popup WebKit leaves `body`.
- Source and docs through Write and Edit only. No `sed -i`, no shell redirection. Scratch probes write only to relative paths from the project root.
- `grep -P` fails here (locale). Check long dashes with Python (`chr(0x2014)`, `chr(0x2013)`).
- A second builder works in `examples/split`. Its processes and files are not ours.

## Processes
None left running. After the last run a sweep by name (python, node, playwright, chrome, headless, webkit, MiniBrowser, bash, sh, cmd) with creation time and command line found only the shell running the sweep. The three scratch probe servers (PIDs 16600, 22756, 8564) were stopped by their probes and are gone. The conftest servers stop themselves. No background shell was started.
