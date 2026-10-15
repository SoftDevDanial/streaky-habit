# Handoff, Streaks v1.1.0 execute, app module, resume at task 23

Written 2026-10-14 by the frontend builder (senior frontend dev agent), after task 22, at about 48 percent of its context. The brief says not to start a new task past about 30 percent, so task 23 was not started.

## Where it stands
- HEAD `9ed0a21` `feat(app): delete from a row and from P2, the time-free guard, the tap-through guard and focus after a delete (task 22, R13, R14, R15)`.
- Node 137 of 137. Chromium 226 passed, 0 xfailed. WebKit 225 passed, 1 skipped (CO-1), 0 xfailed. No WebKit failure at HEAD. No `xfail` mark is left in `tests/` (spec, Tasks, "No mark is left after task 22").
- Evidence of task 22 in `docs/modules/app/qa/red-first/` (the stub runs `20261014-212530-chromium`, `20261014-212904-chromium` and `20261014-214003-chromium`, the planted defect runs A to H from `20261014-213105-chromium` to `20261014-213935-chromium`, and `20261014-215130-chromium`), and `docs/modules/app/qa/functional/20261014-215237-chromium/` and `.../functional/20261014-215414-webkit/` (the committed tree).
- `docs/modules/app/BUILD.md` section "v1.1.0 task 22" holds the record, eight judgment calls and the README reconcile facts.

## Resume point, task 23 (persistence, the unreadable note, the save warning, R16, R17, R41)
1. Read spec R16, R17, R41, the Storage contract (`loadHabits` with `saveFailed`, `saveHabits` returning a boolean, both built at task 14) and Tasks line 23. Read qa.md Feature "Kept on the device" (it starts after Feature "Delete a habit"), the driver table D-a to D-e and "Storage failures are driven from the test side only" under "Rules every test follows", and the conftest table rows `FAIL_SETITEM`, `FAIL_GETTER`, `FAIL_GETITEM`, `FAIL_SETITEM_PROBE`, `storage_switch`, `fill_quota` and `clear_fill`. None of these helpers is in `conftest.py` yet. They are test code written with their tests before the RED run (qa.md, "Controls are watched failing first").
2. Write `tests/browser/test_storage.py` from that Feature and run it RED in Chromium into `docs/modules/app/qa/red-first/<ts>-chromium/`. At HEAD the app saves through `edit` and ignores what `saveHabits` and `loadHabits` report, and shows no banner, so the warning and note scenarios fail on their properties. Scenarios whose property already holds at HEAD (for example a reload keeps the habits, loading writes nothing) need a planted defect to be seen failing (task 21 and task 22 precedent, BUILD.md).
3. Code. `boot` reads `loadHabits()` whole (`reset` and `saveFailed`), `edit` reads `saveHabits`' result, and `view.js` draws `div.banners` (the S4 warning first and only while the latest save failed, inserted and removed only on a change of state, SW7, and the S5 note with Dismiss, which moves focus to the field). Tab order puts Dismiss after the Overview button below 1024 px and after the band from 1024 px (R22). The markup is in spec Contracts, "Banners".
4. Run Node, Chromium and WebKit with evidence, BUILD.md section, tick spec task 23, credential gate, commit.

## Gotchas
- The page guard of R14 (task 22) holds any click on the page or on a popup beneath for 500 ms of `event.timeStamp` after a mouse or touch click inside a popup. A test that clicks the page right after a click inside a popup opens with `install_time=NOON` and calls `let_guard_pass(page)` first (qa.md, "The page guard in ordinary scenarios"). No earlier test needed a change at task 22.
- A popup's `close` event is a queued task. In Chromium the browser's own focus restore can show the opener focused before the app's close handler runs, so a focus check right after a close can pass on the browser's work. `conftest.watch_close` and `wait_for_close` wait for it (BUILD.md task 22, judgment call 5). Earlier focus-after-close checks in `test_overview.py`, `test_year.py` and `test_day_editor.py` were not changed.
- Under a paused installed clock a locator click can wait forever, so use raw `page.mouse` or `page.touchscreen` at measured points. `expect` and `evaluate` work. Wait for a dialog's entrance with `getAnimations({ subtree: true })` and `finished` (CSS animations run in real time).
- `syncDayButton` in `src/calendar.js` must draw the ring before it reads `animate` (task 20 slip).
- WebKit lays `100dvh` out in 1/64 px units. Compare boxes within 0.5 px where a box depends on it.
- In WebKit a mouse click on a button inside an open popup leaves focus on the popup's `dialog`. Outside a popup WebKit leaves `body`.
- 1.0's M1 `returnValue` defect no longer reproduces in Chromium 149, so a planted defect of that kind goes in app state.
- Source and docs through Write and Edit only. No `sed -i`, no shell redirection. Scratch probes write only to the session scratchpad. `grep -P` fails here. Check long dashes with Python (`chr(0x2014)`, `chr(0x2013)`). The house rules keep colons and semicolons out of prose, comments included.
- A second builder works in `examples/split`. Its processes and files are not ours.

## Processes
None left running. Started this session and stopped. The conftest servers of each pytest run (they stop themselves and check the port), one background pytest shell (the first stub run, ended exit 1 on its own), and one scratch probe server (`python -m http.server` on 127.0.0.1:59964, PID 10316), stopped by the probe's `finally`, port confirmed refusing.
