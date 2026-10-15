# Handoff, Streaks v1.1.0 execute, app module, resume at task 26

Written 2026-10-14 by the frontend builder (senior frontend dev agent), after task 25, at about 36 percent of its context. The orchestrator asked at 23.26 local time for a return by 00.10 and no start of task 26, so task 26 was not started.

## Where it stands
- HEAD `5f5240b` `test(app): the platform checks, sizes, keyboard, motion, names as text, requests and no hooks (task 25, R21 to R26)`, on top of `45eb4e8`.
- Node 137 of 137. Chromium 322 passed (`docs/modules/app/qa/functional/20261014-231919-chromium/`). WebKit 321 passed, 1 skipped, CO-1 (`docs/modules/app/qa/functional/20261014-232212-webkit/`). No xfail mark in `tests/`.
- Task 25 changed no file in `src/` and not `index.html`. The platform checks exposed no defect in either engine.
- `docs/modules/app/BUILD.md` section "v1.1.0 task 25" holds the RED runs, nine judgment calls and two open questions for the planner (the pop scenario names the Overview button's ring at 1280 px, where that button is not displayed, and an engine table line for the Escape pacing).

## Resume point, task 26 (the fidelity state scripts and `test_fidelity_inputs.py`, R28)
1. Read spec Tasks line 26 with its note of 2026-10-14 (planner follow-up, ruled ORCH). Before `test_fidelity_inputs.py` asserts that `document.activeElement` is `body` after each after-load script's `blur()`, measure that in WebKit with a popup open, because WebKit leaves focus on the popup's `dialog` after a mouse click inside it. A different WebKit value goes into qa.md's engine table with its measurement, and the scenario asserts each engine's value.
2. Read qa.md section "Fidelity gate" (it starts after the FE element checklist, near the end of the file) and the `@R28` scenario "The fidelity state scripts are right", qa.md "The clipboard is always a stand-in" (each seed script starts with the exact text of `CLIPBOARD_STANDIN`, each after-load script refuses to click until the stand-in is in place), and "Controls are watched failing first", row 26 (an empty file of each new script name is the throwaway stub, seen RED on each script's text checks).
3. The 1.0 forms stay at tag `v1.0.0`. `git show v1.0.0:tests/browser/test_fidelity_inputs.py` reads the 1.0 test without touching the tree. `tests/browser/fidelity/seed-sample.js` and `open-delete-dialog.js` are the 1.0 scripts still in the tree, which task 26 writes again (spec task 12, "stay as they are until task 27 and task 26 write them again").
4. Run RED in Chromium into `docs/modules/app/qa/red-first/<ts>-chromium/`, then the scripts, then Node, Chromium and WebKit into `docs/modules/app/qa/functional/<ts>-<engine>/`, BUILD.md section, tick spec task 26, credential gate, commit.
5. Do not run the finders or task 28. Task 27 (`live_e2e.py`) follows task 26.

## Gotchas (new at task 25, then the standing ones)
- A box read while a popup still rises carries the transform's rounding (45.99994 for 46 px). `settle` in `test_platform.py` waits until `document.getAnimations()` is empty, bounded at 2 seconds.
- In WebKit, Escape presses sent back to back are partly lost. With P1 over P4 over P3, three presses leave P3 open (5 of 5), while Chromium closes all three. Press each Escape once the previous popup has closed (`close_with_escape` in `test_platform.py`, the same way `test_popups.py` does). Evidence `docs/modules/app/qa/escape-pace-probe/20261014-231840-chromium-webkit/results.json`.
- From 1024 px the Overview button is not displayed, so its ring starts no animation there. Below 1024 px the band is not displayed.
- `animation_log(page)` and `animations(log)` are in `conftest.py`. Each entry has `name`, `tag`, `pseudo`, `classes`, `owner` (the nearest `aria-label`, else id) and `duration`.
- A RED run that loosens the CSP must not send a request off the machine. Task 25 loaded a scratch pytest plugin that adds `--host-resolver-rules=MAP * ~NOTFOUND , EXCLUDE 127.0.0.1` to Chromium's launch arguments (BUILD.md task 25, RED run 5).
- The page guard of R14 holds any click on the page or on a popup beneath for 500 ms of `event.timeStamp` after a mouse or touch click inside a popup. Under a fixed clock `event.timeStamp` does not move, so a page click after a click inside a popup needs `install_time` and `let_guard_pass(page)` first.
- A popup's `close` event is a queued task. A focus check after a close reads focus only after `conftest.watch_close` and `wait_for_close`.
- Under a paused installed clock a locator click can wait forever, and `page.wait_for_function` polls on animation frames. Use raw `page.mouse`, `page.touchscreen` or `page.keyboard` and poll from Python with a deadline. CSS animations run in real time.
- WebKit lays `100dvh` out in 1/64 px units. In WebKit a mouse click on a button inside an open popup leaves focus on the popup's `dialog`, outside a popup on `body`. Focus ring checks read the outline longhands.
- The rollover runs `setInterval(checkDay, 30000)` from boot. A page opened with `fixed_time` never rolls over.
- Source and docs through Write and Edit only. No `sed -i` and no shell redirection of any kind. Scratch probes write only to the session scratchpad. `grep -P` fails here. Check long dashes with Python. The house rules keep colons and semicolons out of prose, comments included.
- A second builder works in `examples/split`. Its processes and files are not ours.

## Processes
None left running. Started this session and stopped. The conftest servers of each pytest run (two `python -m http.server` per run, each stopped by the conftest, which checks its port refuses), the headless Chromium and WebKit of each run, one Node test run. No scratch server was started. The scratch Escape probe and the WebKit check of the new file ran through pytest with the same conftest servers.
