# Handoff, Streaks v1.1.0 execute, app module, resume at task 24

Written 2026-10-14 by the frontend builder (senior frontend dev agent), after task 23, at about 32 percent of its context. The brief says not to start a new task past about 30 percent, so task 24 was not started.

## Where it stands
- HEAD `6472bb5` `feat(app): the save warning, the unreadable note and saves that survive a reload (task 23, R16, R17, R41)`.
- Node 137 of 137. Chromium 264 passed. WebKit 263 passed, 1 skipped (CO-1). No WebKit failure at HEAD. No `xfail` mark in `tests/`.
- Evidence of task 23 in `docs/modules/app/qa/red-first/` (`20261014-220834-chromium` at HEAD, `20261014-220942-chromium` on the throwaway stub S, the planted defect runs P-a to P-h from `20261014-221009-chromium` to `20261014-221255-chromium`) and `docs/modules/app/qa/functional/20261014-221528-chromium/` and `.../functional/20261014-221722-webkit/` (the committed tree).
- `docs/modules/app/BUILD.md` section "v1.1.0 task 23" holds the record, seven judgment calls, one open question for the planner (Dismiss with twelve habits, when the field is disabled) and the README reconcile facts.

## Resume point, task 24 (rollover with popups open, R19, R20, CG-14 and CG-19 ruled)
1. Read spec R19, R20, Contracts "Events and focus" (the Rollover line, `setInterval(checkDay, 30000)` started at boot and a `visibilitychange` listener that calls `checkDay` when visible) and Tasks line 24. Read qa.md Feature "Rolling over midnight" (it starts right after Feature "Kept on the device"). It holds eleven scenarios, one an Outline (CG-14), and its header comment says how each installs the clock 30 seconds before the instant it pauses at, opens the page and pauses there (`page.clock.pause_at`). `hide_tab` and `show_tab` are already in `conftest.py`.
2. No rollover code exists in `src/` yet (no `checkDay`, no interval, no `visibilitychange` listener). The app's one clock read is `readToday()` in `src/app.js`. At HEAD nothing moves at midnight, so most scenarios fail on their properties. Scenarios whose property already holds at HEAD (for example "The composer keeps its text and its focus" and "An error message survives the rollover") need a planted defect to be seen failing (tasks 21 to 23 precedent, BUILD.md).
3. Write `tests/browser/test_rollover.py` from that Feature and run it RED in Chromium into `docs/modules/app/qa/red-first/<ts>-chromium/`.
4. Code. `checkDay` compares `readToday()` with `state.todayKey` and, on a change, sets it and redraws in the same handler (`view.renderDate`, then `render`, which already redraws each open popup). P1 keeps `state.day`. P2 and P4 show the new year, P3 the new 12 weeks. Focus stays on the same element, or on the control for the same date and the same habit, else goes as CG-14 says (the top popup's open-focus target, or the page's first focusable control). CG-19 covers P1 closing after a rollover removed the day button that opened it, so `onPopupClose` must not focus an opener that has left the DOM.
5. Run Node, Chromium and WebKit with evidence, BUILD.md section, tick spec task 24, credential gate, commit.

## Gotchas
- The day grids are laid out again for a new day. `drawOverview` and `drawAllHabitsYear` in `src/calendar.js` keep a `laidOutFor` map per grid and rebuild the grid when `todayKey` changes, so after a rollover every band, P3 and P4 day button is a new element. Focus on a day, the opener kept in `openers` for P1, and the `is-open` marks of `popups.markOpenDay` all point at old elements unless they are found again by `data-key` after the redraw. Rows are updated in place by `view.renderRows`, so a focused Done today stays the same element.
- The save warning is drawn by `render` from `state.saveFailed` (task 23), so a rollover render leaves it as it is. `renderSaveWarning` writes only on a change of state.
- The page guard of R14 (task 22) holds any click on the page or on a popup beneath for 500 ms of `event.timeStamp` after a mouse or touch click inside a popup. A test that clicks the page right after a click inside a popup opens with an installed clock and calls `let_guard_pass(page)` first.
- A popup's `close` event is a queued task. A focus check after a close reads focus only after `conftest.watch_close` and `wait_for_close` (task 22).
- Under a paused installed clock a locator click can wait forever, so use raw `page.mouse` or `page.touchscreen` at measured points. `expect` and `evaluate` work. CSS animations run in real time.
- WebKit lays `100dvh` out in 1/64 px units. Compare boxes within 0.5 px where a box depends on it.
- In WebKit a mouse click on a button inside an open popup leaves focus on the popup's `dialog`. Outside a popup WebKit leaves `body`.
- Source and docs through Write and Edit only. No `sed -i`, no shell redirection of any kind (task 23 slipped once with `2>/dev/null`, recorded in BUILD.md). Scratch probes write only to the session scratchpad. `grep -P` fails here. Check long dashes with Python (`chr(0x2014)`, `chr(0x2013)`). The house rules keep colons and semicolons out of prose, comments included.
- A second builder works in `examples/split`. Its processes and files are not ours.

## Processes
None left running. Started this session and stopped. The conftest servers of each pytest run (two `python -m http.server` per run, stopped by the conftest, which checks each port refuses), the headless Chromium and WebKit of each run (closed at session end), one Node test run, and one scratch probe server (`python -m http.server` on `127.0.0.1:39379`, PID 10520), stopped by the probe's `finally`, port confirmed refusing.
