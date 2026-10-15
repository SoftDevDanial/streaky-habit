# Handoff, Streaks v1.1.0 execute, app module, resume at task 25

Written 2026-10-14 by the frontend builder (senior frontend dev agent), after task 24, at about 36 percent of its context. The brief says not to start a new task past about 30 percent, so task 25 was not started.

## Where it stands
- HEAD `45eb4e8` `docs(app): BUILD.md task 24 names a process slip made after its commit (task 24)`, on top of `56aee14` `feat(app): the rollover redraws every view for the new day, with popups open and focus kept (task 24, R19, R20)`.
- Node 137 of 137. Chromium 278 passed. WebKit 277 passed, 1 skipped (CO-1). No WebKit failure at `56aee14`. No `xfail` mark in `tests/`.
- Evidence of task 24 in `docs/modules/app/qa/red-first/` (`20261014-223550-chromium` at HEAD, `20261014-223629-chromium` on the throwaway stub S, the planted defects and S2 from `20261014-223710-chromium` to `20261014-223921-chromium`) and `docs/modules/app/qa/functional/20261014-224134-chromium/` and `.../functional/20261014-224344-webkit/` (the committed tree).
- `docs/modules/app/BUILD.md` section "v1.1.0 task 24" holds the record, nine judgment calls, no open question, two process notes and the README reconcile facts.

## Resume point, task 25 (platform checks and anything they expose, R21 to R26)
1. Read spec R21 to R26 and Tasks line 25. Read qa.md Feature "Platform" (it starts right after Feature "Rolling over midnight", 18 scenarios with three Outlines, from "Nothing scrolls at 360 pixels" to "The CSP is in force"). Also read the three `@R26` scenarios in Feature "Shipped entry point, stylesheet and icon" ("No sample data in the shipped files", "Query strings and fragments do not seed", "No globals and no hooks"). They sit in that Feature but name `tests/browser/test_platform.py` as their file, and no test holds them yet. The 1.0 `test_platform.py` was removed at task 12 and stays at tag `v1.0.0` (`git show v1.0.0:tests/browser/test_platform.py` reads it without touching the tree).
2. Some of R21 to R25 is held already by earlier files (`test_render.py` `test_R5_R21_the_page_never_scrolls_and_the_composer_stays_put`, `test_entry.py` `test_R29_R25_the_page_links_the_icon_and_the_policy_lets_it_load`). Read them against the Platform scenarios before writing, so nothing is duplicated and nothing is left out.
3. Write `tests/browser/test_platform.py` and run it RED in Chromium into `docs/modules/app/qa/red-first/<ts>-chromium/`. Much of it may hold at HEAD (sizes, tab order, focus rings and motion come from the copied CSS, names reach the DOM as text). Each test that passes at HEAD needs a throwaway planted defect that shows it failing on its property (tasks 21 to 24 precedent, BUILD.md). "Anything they expose" (spec Tasks 25) is fixed in `src/` only when a test fails at HEAD on a real defect, and that fix is named in BUILD.md.
4. `conftest.py` has no `animation_log` yet (qa.md conftest table). The `@R23 @R32` scenario "A change pops what changed and bumps its number, and replays on the next change" needs it.
5. Run Node, Chromium and WebKit with evidence, BUILD.md section, tick spec task 25, credential gate, commit.

## Gotchas
- The rollover of task 24 runs `setInterval(checkDay, 30000)` from boot and checks again when the tab is shown. A test that installs a clock and runs it past local midnight sees the page move to the next day. A page opened with `fixed_time` (the default `NOON`) never rolls over.
- `popups.openFocusOf(dialog)` is now the one place that names each popup's first focus (`dayEditorFocus` is gone), and `view.firstControl()` gives the page's first shown control. Focus on a day button or a bead is found again after a new day through `dayPlace` and `dayControlAt` in `src/calendar.js`.
- `tab_to` now lives in `conftest.py` (moved from `test_delete.py`). It presses raw keys, so it works under a paused clock.
- Every tick goes through `tickDay` in `src/app.js`, which saves and draws only a tick that `toggleDay` accepted.
- The page guard of R14 holds any click on the page or on a popup beneath for 500 ms of `event.timeStamp` after a mouse or touch click inside a popup. A test that clicks the page right after a click inside a popup opens with `install_time` and calls `let_guard_pass(page)` first.
- A popup's `close` event is a queued task. A focus check after a close reads focus only after `conftest.watch_close` and `wait_for_close`.
- Under a paused installed clock a locator click can wait forever, and `page.wait_for_function` polls on animation frames by default, so it can hang too. Use raw `page.mouse`, `page.touchscreen` or `page.keyboard` at measured points, and poll from Python with a deadline. `expect`, `evaluate`, `bounding_box` and `input_value` work. CSS animations run in real time.
- WebKit lays `100dvh` out in 1/64 px units. Compare boxes within 0.5 px where a box depends on it. In WebKit a mouse click on a button inside an open popup leaves focus on the popup's `dialog`, outside a popup on `body`. WebKit writes the computed `outline` shorthand in another order (qa.md engine table), so focus ring checks read the longhands.
- Source and docs through Write and Edit only. No `sed -i`, no shell redirection of any kind (task 24 slipped once with `> /dev/null` in a read-only grep, recorded in BUILD.md). Scratch probes write only to the session scratchpad. `grep -P` fails here. Check long dashes with Python (`chr(0x2014)`, `chr(0x2013)`). The house rules keep colons and semicolons out of prose, comments included.
- A second builder works in `examples/split`. Its processes and files are not ours.

## Processes
None left running. Started this session and stopped. The conftest servers of each pytest run (two `python -m http.server` per run, stopped by the conftest, which checks each port refuses), the headless Chromium and WebKit of each run (closed at session end), and one Node test run. No scratch server was started.
