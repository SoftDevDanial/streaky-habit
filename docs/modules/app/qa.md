# QA: app

> Test contract. Functional cases run against the RUNNING app, once in headless Chromium and once in headless WebKit. Fidelity runs in Chromium after functional is green in both engines.
> Every scenario is tagged `@R#` and maps to a requirement in `spec.md`.
> Written by the solutions architect (sdlc planner), 2026-10-08 (1.0, sealed, full text at git tag `v1.0.0`).
> v1.1.0 rewrite by the planner (solutions architect role), 2026-10-13. Scenario titles end with `(v1.1.0 new)` or `(v1.1.0 changed)`. A changed scenario replaces its 1.0 form, which stays at tag `v1.0.0`. Scenarios of retired requirements (R7, R8, R9, R18) and 1.0 scenarios with no v1.1.0 form are kept as text under "Feature: Retired in v1.1.0" at the end of the Gherkin, each with a `# Retired in v1.1.0` comment, and their tests are removed. A scenario that applies a clarify gate part 2 ruling names its item in its title ("CG-n ruled") and asserts the answer that `spec.md` applies. The owner ruled all ten items, CG-10 to CG-19, on 2026-10-13 with the recommended answers (ledger S1 row 4, S3 row 2, S4 row 3, S7 row 12, `../ROADMAP.md`, v1.1.0, Clarify gate). The coverage count per R# is at the end of this file.
> Changed 2026-10-13 after the plan check (B1, F1, F3 to F6, F8, F9). The 21 titles that now read "CG-n ruled" first read "pending CG-n" (F1). Other changes carry their own dated note where they were made.
> Changed 2026-10-13 after the plan re-check (F12, F13, F14, N9). The new section "Scenarios that wait on a later task" names, for W1 to W22, the task from which each is green (F12). "Controls are watched failing first" lists the stubs for names and files under test (F13). Two new scenarios (`@R6 @R32` and `@R32`) succeed two `test_tick.py` tests that had no scenario (F14). The Feature "Two engines" names its two finder checks (N9). Each change carries its own dated note.
> Changed 2026-10-14 in execute (planner touch-up, ledger H-03, S1 row 8, S7 row 15). H-03, the two P3 rows "2026-07-20" of W22 hold through P3's room for rule 4 (spec R36), built at task 20, and one new `@R36` scenario checks the room. Q1 and Q2, two lines follow the goldens as ruled ORCH (the field's box with twelve habits, the Overview button's computed `flex`). Q3, two scenarios name the popup's `dialog` as WebKit's focus after a click inside a popup. Each change carries its own dated note.
> Changed 2026-10-14 in execute (planner follow-up, ledger H-03, owner ruling 2026-10-14 16:32 "Same fix for P4 (Recommended)"). The room scenario covers the host of P1, P3 or P4, with two P4 rows, and W22's row "390x844 P4 2025-10-10" holds through P4's room. One new `@R36` scenario holds a gap smaller than a day with twelve habits (ruled ORCH). The fidelity inputs scenario waits on a WebKit measurement at task 26 (ruled ORCH). Each change carries its own dated note.
> Changed 2026-10-15 in execute (planner touch after step 5, ledger S1 rows 16 to 20, S3 row 3, S4 row 5, S7 rows 16 and 18). Six new scenarios and one new Examples row give each test that the step 5 solver round added a scenario or row of its own (code review WR-01, WR-04, WR-05 and WR-07, the QA re-check). Eight scenarios gain the lines the round's tests now check (WR-01 to WR-03). The pop scenario names the width each ring is read at (Q-25-1). The engine table gains the focus return on a close (CR-01, WR-06, with the code review re-check's correction) and the Escape pace (Q-25-2). "Controls are watched failing first", the conftest table and one delete scenario record what tasks 21 and 22 found. 175 live scenarios. Each change carries its own dated note.
> Phase skills. The plan phase has none assigned. The builder of each UI task loads the design row of `docs/phase-skills.md` (`taste-skill`, `frontend-design`) before writing UI (spec, Tasks).

## How these scenarios run

### The running app
- Serve from the project root, on a free port, bound to loopback only.
  `python -m http.server <port> --bind 127.0.0.1`
  The app is at `http://127.0.0.1:<port>/`. Python serves `.js` as `text/javascript` (measured in 1.0). The type it gives `src/icon.svg` comes from Python's `mimetypes` and is recorded by task 11's probe P3. A wrong type shows as a failed image load in the `@R29` scenario, never as a silent pass.
- The `@R1` sub-path scenario needs a second server for the parent folder of the project root, `python -m http.server <port2> --bind 127.0.0.1 --directory ..` (run from the project root), with the app at `http://127.0.0.1:<port2>/streaks/`.

### The tests
- The builder implements every functional scenario as pytest test functions in `tests/browser/test_*.py` with Playwright's sync API and the helpers in `tests/browser/conftest.py`. pytest-playwright is not installed and is not needed. The `@R42` and storage unit scenarios are Node tests in `tests/ring.test.js` and `tests/storage.test.js` (`node --test "tests/**/*.test.js"`), each `test()` title starting with its tag.
- Test function names start with the tag, for example `test_R31_done_today_presses_and_unpresses`, so `-k R31` selects a requirement. A Scenario Outline may be `pytest.mark.parametrize` over its Examples rows or one function looping over them. Each row is asserted.
- Command per engine (Git Bash), from the project root, capped at 20 minutes each.
  `STREAKS_EVIDENCE_DIR=docs/modules/app/qa/functional/<datetimestamp>-<engine>/ timeout 1200 python -m pytest tests/browser -q -rA --engine <engine>`
  with `<engine>` `chromium` and then `webkit`. With no `STREAKS_BASE_URL` the conftest starts and stops its own two servers, as in 1.0. The bare CLAUDE.md command `python -m pytest tests/browser -q` runs Chromium. The 20-minute cap leaves room for WebKit, whose Windows driver waits five animation frames per locator action (research webkit-testing, section 2). Task 11 records the WebKit run time, and a run that ends within two minutes of the cap is reported.
- The QA finder runs the suite once per engine and the Node suite once, and reads each test against its scenario. A test whose assertions are weaker than the scenario's `Then` lines is a FAIL of that scenario even when green. A skipped test is BLOCKED, never PASS, except a skip from the `chromium_only` marker in a WebKit run, which is counted and listed with its reason as a skip (also never a pass).
- Every Playwright wait has a timeout, 5 seconds per expectation unless a step says otherwise. No unbounded wait anywhere.
- Every functional scenario runs in both engines. A scenario with no engine line expects the same result in both. Where a `Then` reads "in Chromium ..." and "In WebKit ...", each engine asserts its own sentence (spec Invariants, engine note). File checks that start no browser (for example `@R2`) give the same result in either run.

### Chromium-only scenarios
| # | Scenario | Reason (the marker's text) |
|---|---|---|
| CO-1 | `@R29` The icon is amber in a dark theme and dark amber in a light theme | WebKit draws the colour scheme of SVG images by its own rules, open WebKit bugs 199134 and 316640 (research save-warning-and-tab-icon, B8 item 4). WebKit's result is recorded once, as information, in task 11's baseline evidence |

Task 11's probe may add a row only for Chromium-only tooling (class (c) of spec task 11), with its measured reason written here before the marker is used. An engine difference by design (class (b)) is written into its scenario as an "in Chromium ... In WebKit ..." sentence instead. The fidelity pixel gate is Chromium only by the owner's ruling (ledger S5 row 2) and is not part of the pytest suite.

### Rules every test follows
- **Real gestures only** for user actions. `click`, `dblclick`, `hover`, `keyboard.type`, `keyboard.press`, `mouse.*`, `touchscreen.tap`, and `fill` for typing into the field. Tests never call app code (the app exposes none) and never write app state except by seeding `localStorage` before the app loads, and by the storage drivers below.
- **Reading is allowed.** DOM attributes and text, computed styles, bounding boxes, `localStorage.getItem`, `document.activeElement`, `document.getAnimations()`.
- **Time** is controlled only with Playwright's clock (`page.clock`), never with a hook in the app. Every context uses `timezone_id="Asia/Kuala_Lumpur"` (UTC+8 all year, no DST) and every instant is written with an explicit `+08:00` offset. DST is covered by the habit-logic unit tests. `Event.timeStamp` follows an installed clock in both engines (research webkit-testing, section 2), so the guard scenarios install the clock and pause it.
- **Seeding** (tests only, never the shipped default). Before the app loads, open `<base>__seed__` (a same-origin 404 page from `http.server`, so no app code runs), call `localStorage.setItem("streaks.state", <text>)`, then open the app URL. The fidelity gate seeds through the harness's `--candidate-init-script`, whose script is the clipboard stand-in followed by one `setItem` (Fidelity gate). The live gate's control seeds through `__seed__` too (Cold-boot live-e2e gate).
- **Storage failures are driven from the test side only** (research save-warning-and-tab-icon, A3). Each driver is an init script added after seeding, test-side and never shipped. No driver touches `localStorage` at its top level, because an init script also runs in the blank first document, where storage access is denied.

  | Driver | What it does | Switch |
  |---|---|---|
  | D-a | Replaces `Storage.prototype.setItem` with a function that throws `new DOMException("test quota", "QuotaExceededError")` while failing, and calls the real `setItem` otherwise | `storage_switch(page, failing)` dispatches `new CustomEvent("test:storage", { detail: failing })` on `window` |
  | D-b | Redefines `window.localStorage` with a getter that throws `new DOMException("test denied", "SecurityError")` while failing, and returns the real store otherwise | the same event |
  | D-c | Replaces `Storage.prototype.getItem` with a function that throws while failing | the same event |
  | D-d | A real quota fill. `fill_quota(page)` writes `test.fill.<n>` keys with `page.evaluate` until even one more character is refused (60 second cap). `clear_fill(page)` removes them | none, the engine throws its own error |
  | D-e | D-a whose thrown value is an object with `name`, `code` and `message` getters that each log the console marker `test:storage-read:<property>` | the same event |

  Whether WebKit lets an init script redefine `window.localStorage` (D-b) is probe P1 of task 11. If it does not, the D-b scenarios get a `chromium_only` row with that measured reason, and D-c carries the boot path in WebKit.
- **The clipboard is always a stand-in** (constitution, Browser gates). `open_app` and `live_e2e.py` add the init script `CLIPBOARD_STANDIN` to every context before anything else. When `navigator.clipboard` exists, it replaces `writeText`, `write`, `readText` and `read` on `Clipboard.prototype` with functions that log the console marker `test:clipboard:<method>` and resolve, and never reach the system clipboard. It adds no property to `window`. The app has no copy feature, so no scenario expects a marker, and any marker in a run is a finding. Never a save and restore of the real clipboard. The fidelity captures that press (P1, P2, P3, P4 and M1, through their after-load scripts) get the stand-in through their seed script, because the plugin harness loads exactly one candidate init script. Each seed script starts with the exact text of `CLIPBOARD_STANDIN`, a copy that `@R28` compares with the conftest's text so the two cannot drift, and each after-load script refuses to click until the stand-in is in place (Fidelity gate). The captures that press nothing (K1, S1, S3 and the controls) need no stand-in by the constitution, and K1 and S3 get it anyway through the same seed scripts. Added 2026-10-13 after the plan check (F4). The five after-load scripts click, and their context first had no stand-in.
- **Hiding the tab** is simulated test-side, as in 1.0. Override the `document.visibilityState` and `document.hidden` getters on the page with `Object.defineProperty` and dispatch a `visibilitychange` event on `document`.
- **No context sets `is_mobile`** (it breaks `mouse.wheel` in WebKit). Touch uses `has_touch` (`open_app(touch=True)`).
- **The page guard in ordinary scenarios** (R14, CG-11 ruled). For 500 ms after a mouse or touch click inside a popup (its backdrop included, since a backdrop click targets the dialog element), the page and any popup open beneath it ignore clicks. `Event.timeStamp` does not move under a fixed clock (measured in 1.0). So a scenario that clicks the page, or a popup that lay beneath, after a click inside a popup opens with `install_time=NOON` and calls `let_guard_pass(page)` before that click. Scenarios do not repeat this step in their text, except the guard scenarios themselves. Closing with Escape starts no window. A scenario that confirms a delete with the mouse uses `confirm_delete`, and one that confirms with the keyboard presses Tab and Enter from Cancel.
- **Measured press points.** A scenario that presses a point to prove what lies behind a popup finds the point by measuring bounding boxes, and checks that a control of the named kind really lies under it (`document.elementFromPoint` after the popup closes, or before it opens). A layout change can then fail the precondition but never pass the scenario because nothing is there.
- **Controls are watched failing first** (constitution, Gates and evidence). Each new or changed scenario's test runs once before its task's code lands, and is recorded RED on the assertion that states the property (never on an import error or a fixture error), in `docs/modules/app/qa/red-first/<datetimestamp>-<engine>/`. A Node test of a new export of `src/` (`arcPath` and `legendCounts` of the new `src/ring.js`, task 13) sees RED through the throwaway stub that `../habit-logic/qa.md` states once (named data, "The RED-first method for a new export"). The changed `storage.js` results (`saveHabits`, `loadHabits`, task 14) need no stub, because their 1.0 forms fail the new assertions. A browser test that reaches the app through the page needs none either, because a missing control fails a locator expectation on the property. The live gate is written after the app is built, so its watched failure is its control run (Cold-boot live-e2e gate). Added 2026-10-13 after the plan check (F5, F6).
  A helper that a task adds to `conftest.py` only to drive or read the app (a locator, a storage driver, a log) is test code written with its test before the RED run, so it needs no stub, and the RED comes from the app. A test whose subject is itself a name or a file that its own task creates would fail at import, on a missing fixture or on a missing file. It gets a throwaway stub by the method of `../habit-logic/qa.md`, of the right kind with a wrong value, run once with its RED kept and never committed. The table lists every such case in the plan. Added 2026-10-13 after the plan re-check (F13). The method first reached ES module exports only, so the three `test_engines.py` tests of task 11 would have failed at import or on a missing fixture.

  | Task | Scenarios | Missing before the task's code | Throwaway stub, never committed | Seen RED on |
  |---|---|---|---|---|
  | 11 | "The run uses the engine it was asked for", "An unknown engine is refused before any browser starts", "One helper launches every browser" (`test_engines.py`) | the `--engine` option, the `engine` fixture, `launch`, `LAUNCH_ARGS`, the `-<engine>` end of `EVIDENCE_DIR` | in `conftest.py`, `--engine` added with no choices, an `engine` fixture that returns the option's value, a `launch(playwright, engine)` that launches Chromium for any engine and never raises, `LAUNCH_ARGS` set to `{"chromium": [], "webkit": []}`, `EVIDENCE_DIR` built as in 1.0, and the 1.0 `browser` fixture left as it is | one run with `--engine webkit` and `STREAKS_EVIDENCE_DIR` set. The browser type is "chromium", the evidence folder does not end with "-webkit", `--engine firefox --collect-only` exits 0 and names no choices, `launch(playwright, "firefox")` raises nothing, `.launch(` appears outside `launch`, `live_e2e.py` does not import `launch`, and `LAUNCH_ARGS["chromium"]` is `[]` |
  | 12 | "The icon file is the goldens' icon, byte for byte" (`test_entry.py`) | `src/icon.svg` | an empty `src/icon.svg` | its bytes differ from the decoded href |
  | 13 | the `@R42` Node scenarios (`tests/ring.test.js`) | `src/ring.js` | the stub that `../habit-logic/qa.md` states, with `new Date()` in it for "ring.js is pure" | each value, and the purity scan |
  | 26 | "The fidelity state scripts are right" (`test_fidelity_inputs.py`) | each state script that task 26 adds (Fidelity gate) | an empty file of each new name | each script's text checks |

  Changed 2026-10-15 in execute (planner touch after step 5, the qa notes of tasks 21 and 22, ledger S7 row 16 and S3 row 3). The sentence "A browser test that reaches the app through the page needs none either" did not hold for every browser test of tasks 21 to 25, in two cases. (a) The gesture cannot finish before the code exists. At task 21 a click on Add waited on the form submission that the CSP's `form-action 'none'` blocks until Playwright's timeout, and at task 22 a bin opened nothing, so most delete tests stopped in their Given. (b) The property already holds before the code, for example "No message while typing" and "Loading writes nothing". The RED then comes from a throwaway stub of `src/` of the right kind with a wrong value (a), or from a planted defect that breaks the property (b), never committed and gone before the code is written. `BUILD.md` names each task's stubs and defects under "RED first".

- **A test that waits on a later task** follows the rule in spec, Tasks, and the next section names each one. Added 2026-10-13 after the plan re-check (F12).
- `docs/design/` is read-only. Tests read the goldens and `sample-history.json` and never write there.

### Scenarios that wait on a later task
Each scenario below sits in a file whose task comes before the task that lands the last feature it uses. It follows the one rule of spec, Tasks ("A test that waits on a later task"). Its test is run once and recorded RED before the code of the task that writes it, and it is green from the task in the fifth column with no mark. Written before that task, it carries `pytest.mark.xfail(strict=True, reason="task N")`, in an Outline only on the rows that wait (`pytest.param(..., marks=...)`). That task removes the mark. A marked test that passes early fails the run, and the builder acts as the spec says. No mark is left after task 22. ~~W21 and W22 are written at the task they wait on, so they carry no mark.~~ W21 and W22 are written at the task they wait on, so they carry no mark, except W22's two P3 rows "2026-07-20", which wait on task 20 (changed 2026-10-14 in execute, ledger H-03, see the note under the table). Added 2026-10-13 after the plan re-check (F12). The plan first said how such a test behaves only for W1 and W2, as "stay RED".

| # | Scenario | File, written at task | What waits (other rows are green at once) | Green from task (the mark's reason) | The feature that task lands |
|---|---|---|---|---|---|
| W1 | The page links the icon and the policy lets it load | `test_entry.py`, 12 | the scenario | 15 | a boot with no page error |
| W2 | The app works from a sub-path | `test_entry.py`, 12 | the scenario | 21 | the add |
| W3 | English under a German browser locale | `test_render.py`, 15 | the scenario | 19 | P2 |
| W4 | A new habit shows no Best block | `test_render.py`, 15 | the scenario | 21 | the add |
| W5 | The fades follow the rows and a resize | `test_render.py`, 15 | the scenario | 21 | the add |
| W6 | Small rings carry no number and no today circle | `test_render.py`, 15 | the scenario | 18 | P1 (P3 lands at 17) |
| W7 | One Done today updates every place at once, and only what changed moves | `test_today.py`, 16 | the scenario | 19 | P2 |
| W8 | A tick in P1 over P3 updates P3 and the row, and leaves today's ring alone | `test_today.py`, 16 | the scenario | 18 | P1 ticks (P3 lands at 17) |
| W9 | A tick in P1 over P4 updates P4 and P3 beneath it | `test_today.py`, 16 | the scenario | 20 | P4 and P1 over P4 |
| W10 | A tick in P2 updates P2, the row and the band | `test_today.py`, 16 | the scenario | 19 | P2 |
| W11 | Each edit saves once, and opening or closing a popup saves nothing | `test_today.py`, 16 | the scenario | 22 | the delete (P1 lands at 18, P2 at 19, P4 at 20, the add at 21) |
| W12 | Best back to 0 removes the Best block in every place | `test_today.py`, 16 | the P1 row, the P2 row. The Done today row is green at 16 | 18, 19 | P1, P2 |
| W13 | A tick that changes Current and leaves Best moves Current only | `test_today.py`, 16 | the P1 row, the P2 row | 18, 19 | P1, P2 |
| W14 | Popups stack and Esc closes the top one only | `test_popups.py`, 17 | the scenario | 20 | P4 from P3's Year, P1 over P4 |
| W15 | A backdrop click closes that popup only | `test_popups.py`, 17 | rows "P3, then P1" and "P1 from the band" (18), "P2 for Read" (19), "P4 from the band's Year" (20), the two M1 rows and "P2 for Read, then M1" (22). The 800x900 P3 row is green at 17 | 18, 19, 20, 22 by row | P1, P2, P4, M1 from a bin |
| W16 | A click inside the box, or a drag that leaves it, closes nothing | `test_popups.py`, 17 | every row, P1 (18), P2 (19), P4 (20), M1 (22) | 18, 19, 20, 22 by row | P1, P2, P4, M1 from a bin |
| W17 | Tab never reaches a control outside the top popup | `test_popups.py`, 17 | every row, "P3, then P1" (18), P2 (19), M1 (22) | 18, 19, 22 by row | P1, P2, M1 from a bin |
| W18 | Every popup is modal and the page does not scroll under it | `test_popups.py`, 17 | rows P1 (18), P2 (19), "P3, then P4" (20), M1 (22). The P3 row is green at 17 | 18, 19, 20, 22 by row | P1, P2, P4, M1 from a bin |
| W19 | A day before a habit was added can be ticked | `test_year.py`, 19 | the scenario | 21 | the add |
| W20 | Deleting one of twelve opens the composer again | `test_add.py`, 21 | the scenario | 22 | the delete |
| W21 | Every context has the clipboard stand-in | `test_engines.py` (task 11's file), written at 19 | nothing, no mark | 19 | Year (Done today lands at 16) |
| W22 | On a phone the chosen day stays in sight above P1 | `test_day_editor.py`, the four P3 rows at 18, the two P4 rows written at 20 | ~~nothing, no mark~~ the two P3 rows "2026-07-20" | ~~18 and 20 by row~~ 18 for the two P3 rows "2026-09-22", 20 for the two P3 rows "2026-07-20" and the two P4 rows | P4, and ~~P3's room~~ the room of P1's host, P3 or P4, for rule 4 (spec R36, H-03) |

Changed 2026-10-14 in execute (planner touch-up, ledger H-03, owner ruling 2026-10-14 16:05 "Fix, give P3 room"). W22's two P3 rows "2026-07-20" could not turn green at task 18, because P3 had nothing to scroll on a phone (blocker B1, `BUILD.md` task 18, evidence `docs/modules/app/qa/day-editor-b1/20261014-153746-chromium/`). They hold as written once P3 gets its room (spec R36), which task 20 builds. Today `test_day_editor.py` carries them with the mark `BLOCKED_B1`, which names a blocker, not a task. The builder of task 20 changes it on both rows to `xfail(strict=True, reason="task 20")` and removes it in task 20's commit (spec, task 20). The builder edits the test. The W22 row first read "nothing, no mark" and "18 and 20 by row".

Added 2026-10-14 in execute (planner follow-up, owner ruling H-03 of 16:32 "Same fix for P4 (Recommended)"). W22's row "390x844 P4 2025-10-10" holds as written through P4's room (spec R36), which task 20 builds with P4, so the row carries no mark. Without the room it could not pass, because P4's body ends with October 2025 and 10 October 2025 would stay under P1 even at P4's largest scroll (worked out from `system.css`, task 20 measures it first). The W22 row's last cell first read "P3's room for rule 4".

### Engine differences by design
| Behaviour | Chromium | WebKit | Source |
|---|---|---|---|
| Focus after a mouse click on a button | the clicked button | no element (`document.activeElement` is `body`), whatever had focus before | spec Invariants, research webkit-testing section 2. Task 11's probe confirms it |
| Focus after a mouse click on a button inside an open popup (added at task 18) | the clicked button | the popup's `dialog` element, not `body` (measured at task 18 on P1's ticks, in WebKit 26.5) | WebKit's mouse press finds no mouse-focusable element and focuses the modal dialog. A click on a popup's text with no control focuses the dialog in both engines. Scenarios that read "In WebKit document.activeElement is body" after a click inside a popup assert the dialog. Added 2026-10-14 in execute (planner touch-up, Q3, ruled ORCH). The two such scenarios, "Ticking a past day in P1" and "Ticking a day in the year view", now name the dialog in their own text |
| Focus after a keyboard press on a button | the button | the button | both engines |
| Focus the app sets (Cancel on M1, Close on P2, P3 and P4, the first tick on P1, the opener on close, the field after a name error or Dismiss, rule 3 after a delete) | as the requirement says | as the requirement says | spec R40, the app sets it by hand |
| Focus back on the opener when a popup closes (R40, added 2026-10-15) | the browser's own restore inside `close()` lands on the same opener before the app's close handler runs | an opener pressed with the mouse never had focus (rows above), so the browser's restore does not land on it and only the app's focus does | Code review WR-06 and its re-check, with a planted defect that sets no focus on close, under which every close-focus test stays green in Chromium and fails in WebKit. So R40's return of focus to the opener is proven by the WebKit run. In Chromium a focus read after the popup's close event (`watch_close` and `wait_for_close` in `conftest.py`) shows that nothing moved focus after the app's handler, not that the app moved it. A test reads what that handler clears (P1's `is-open` marks and the host's room of spec R36) after the close event, never on the opener's focus alone (code review CR-01). Added 2026-10-15 in execute (planner touch after step 5, code review CR-01 and WR-06, with the re-check's correction to the solver's wording) |
| Tab reaches every button | yes | yes, on Windows | research webkit-testing section 2 |
| `detail` of the second of two quick taps | 2, and a `dblclick` follows (measured at task 11) | 1, and no `dblclick` (measured at task 11) | no scenario depends on it, the R13 guard is spatial first |
| CSP refusal | a console error and a `securitypolicyviolation` event | a `securitypolicyviolation` event and one console error, wording measured at task 11 | scenarios assert the event, never the console text |
| Colour scheme of the SVG tab icon | follows the scheme | open WebKit bugs, the light colour in both schemes (measured at task 11) | CO-1 |
| Serialisation of the computed `outline` shorthand (added at task 11) | `rgb(28, 37, 35) solid 2px` | `2px solid rgb(28, 37, 35)` | the longhands `outline-width`, `outline-style`, `outline-color` and `outline-offset` are equal in both, so scenarios read the longhands, never the shorthand string |
| Three Escape presses sent back to back over P1, P4 and P3, opened by keyboard at 390 x 844 (measured at task 25) | all three close (5 of 5 runs) | P3 stays open (5 of 5 runs) | `docs/modules/app/qa/escape-pace-probe/20261014-231840-chromium-webkit/results.json`. With each press sent once the previous popup has lost its `open` attribute, both engines close all three (5 of 5). Engine timing, not an app defect, and an app Escape handler is a non-goal (spec Non-goals). A scenario that closes several popups with Escape sends each press once the previous popup has closed, as a person's presses are paced (`BUILD.md` task 25, judgment call 3). Added 2026-10-15 in execute (planner touch after step 5, Q-25-2 of task 25, ledger S7 row 18) |

#### Task 11 measurements (2026-10-14)
Added 2026-10-14 by the frontend builder (app task 11), from the probe run and the WebKit baseline in `docs/modules/app/qa/webkit-baseline/20261014-125500-webkit/` (`probes.json`, `baseline.md`). Chromium 149.0.7827.55 and WebKit 26.5 (Playwright 1.61.0), headless, on this Windows machine.
- **Focus after a mouse click on a button.** Confirmed as the spec's engine note says. A mouse click on a button with nothing focused, and a click on a button after typing in a field, leave `document.activeElement` as the clicked button in Chromium and as `body` in WebKit (also on the 1.0 app, a click on Add after typing). Tab and then Enter or Space leave the button focused in both.
- **Two quick taps** (`has_touch`, two `touchscreen.tap` at one point). Both engines send pointerdown, touchstart, pointerup, touchend, mousedown, mouseup, click per tap. The second tap's `click` has `detail` 2 in Chromium, followed by `dblclick`, and `detail` 1 in WebKit with no `dblclick`. A mouse `dblclick` gives `detail` 1 then 2 and a `dblclick` in both.
- **P1, `Object.defineProperty(window, "localStorage", ...)` in an init script (driver D-b).** Honoured by both engines. `localStorage` is an own accessor of `window` (configurable, no descriptor on `Window.prototype`) in both. While failing a read throws the script's `SecurityError`, after the switch a set and get round trip works, and the 1.0 app boots with it and no page error. So the D-b scenarios need no Chromium-only row. In WebKit the init script also runs in the blank first document (`about:blank`), as qa.md's driver rule assumes.
- **P2, quota fill (driver D-d).** Both engines refuse at 5242672 characters of values in 18 keys (`QuotaExceededError`, code 22), and refuse one more character. The fill took 10 ms in Chromium and 3 ms in WebKit (0.03 s and 0.01 s wall), far inside the 60 second cap.
- **P3.** `python -m http.server` here serves an `.svg` file as `image/svg+xml`, which Python's `mimetypes` also gives for `icon.svg`.
- **`getComputedStyle(dialog, "::backdrop")`.** Reported by both engines with the same values on the 1.0 dialog (`animation-name` `scrim-in` and `animation-duration` `0.18s` without reduced motion, `none` and `0s` with it, `background-color` `rgba(28, 37, 35, 0.5)`). The backdrop half of the `@R23` scenario needs no class (b) line.
- **CSP console text** for a refused `fetch`. Chromium logs two errors, "Connecting to '<url>' violates the following Content Security Policy directive: "connect-src 'none'". The action has been blocked." and "Fetch API cannot load <url>. Refused to connect because it violates the document's Content Security Policy.". WebKit logs one, "Refused to connect to <url> because it does not appear in the connect-src directive of the Content Security Policy.". Both fire `securitypolicyviolation` with `violatedDirective` `connect-src`, and both name `connect-src`. The rejected `fetch` reads "TypeError: Failed to fetch" in Chromium and "TypeError: Load failed" in WebKit.
- **Computed `outline`** on keyboard focus, see the table row above (the four 1.0 `test_R22_focus_rings_on_keyboard_focus` rows fail in WebKit on the shorthand string alone).
- **CO-1, information only.** The goldens' icon payload drawn as an image under `color_scheme` dark and light gives (255, 176, 32) and (154, 91, 0) in Chromium, and (154, 91, 0) in both schemes in WebKit.
- **Clipboard on `http://127.0.0.1`.** A secure context in both engines, `navigator.clipboard` and `Clipboard` exist, and with `CLIPBOARD_STANDIN` loaded `Clipboard.prototype.writeText` is no longer the native function in either engine.

### `tests/browser/conftest.py` (shared fixtures and helpers, at least these)
| Helper | Does |
|---|---|
| `--engine` option, `engine` fixture | `pytest_addoption` adds `--engine` with the choices `chromium` and `webkit`, default `chromium`. The session fixture `engine` returns it (R30) |
| `ENGINES`, `LAUNCH_ARGS`, `launch(playwright, engine)` | the one place a browser is launched, `getattr(playwright, engine).launch(headless=True, args=LAUNCH_ARGS[engine])`, with `["--force-color-profile=srgb"]` for Chromium and `[]` for WebKit. Any other engine raises `ValueError` |
| `browser` fixture | one browser per session from `launch`, closed at session end |
| `chromium_only(reason=...)` marker | registered in `pytest_configure`. `pytest_collection_modifyitems` turns it into a skip with that reason when the engine is not Chromium |
| `BASE_URL`, `SUBPATH_URL`, `EVIDENCE_DIR` | as 1.0. When `STREAKS_BASE_URL` is absent the conftest starts and stops its own two servers. `EVIDENCE_DIR` ends with `-<engine>` |
| `SAMPLE_HABITS`, `TWELVE`, `sample_state()`, `twelve_state()` | v1.1.0 changed. The habits of `docs/design/sample-history.json` (read-only), converted from its 366-character `done` strings (each `"1"` at position i becomes the key `from` plus i days), as `{ name, done }` only. `SAMPLE_HABITS` is the first three, `TWELVE` all twelve. The two functions return the text `{"version":1,"habits":[...]}`. All of this holds from task 12 on. At task 11 these names still serve the 1.0 tests, so `SAMPLE_HABITS`, `SAMPLE_LEVELS` and the state helpers read `tests/fixtures/sample-history-v1.0.0.json` (habit-logic task 6) under their 1.0 meaning, and task 12 switches them when it removes the 1.0 files (spec, tasks 11 and 12) |
| `DESIGN_V10_DIR` | tasks 11 and 12 only. `tests/fixtures/design-v1.0.0/`, the four 1.0 goldens the 1.0 browser tests read (spec, task 11). Removed at task 12 with its readers. Changed 2026-10-13 after the plan check (B1, F3). This table first had a row `SAMPLE_V10` for the 1.0 sample, while task 11 kept the 1.0 tests on the names `SAMPLE_HABITS` and `SAMPLE_LEVELS`. The row is gone, because the switch happens at task 12 for every name at once |
| `TZ`, `TODAY`, `NOON`, `PAUSE_AT` | `"Asia/Kuala_Lumpur"`, `"2026-10-10"`, `"2026-10-10T12:00:00+08:00"`, `"2026-10-10T12:00:20+08:00"` |
| `open_app(browser, viewport=(390, 844), locale="en-US", reduced_motion="no-preference", fixed_time=NOON, install_time=None, storage=None, init_script=None, record=False, path="", base_url=None, count_writes=False, touch=False)` | as 1.0 (seeding, then the init script, then recording, then the app URL), with these v1.1.0 changes. The clipboard stand-in is added to the context first. `init_script` may be a list (a storage driver and the write counter). `color_scheme="dark"` (one dark theme, no app rule reads the scheme). No `is_mobile` |
| `CLIPBOARD_STANDIN` | the stand-in init script above, its one home. The two fidelity seed scripts start with a copy of the same text, which `test_fidelity_inputs.py` compares with it (`@R28`) |
| `FAIL_SETITEM`, `FAIL_GETTER`, `FAIL_GETITEM`, `FAIL_SETITEM_PROBE` | the init scripts of drivers D-a, D-b, D-c and D-e |
| `storage_switch(page, failing)`, `fill_quota(page)`, `clear_fill(page)` | the switch and the quota fill of the driver table |
| `GUARD_WINDOW_MS` | 500, the spec's number written out (R14, CG-11 ruled). The edge scenarios press at this value minus 1 ms and at this value |
| `let_guard_pass(page)` | runs the installed clock `GUARD_WINDOW_MS + 100` ms. It fails at once on a page opened without `install_time` |
| `confirm_delete(page, opener)` | v1.1.0 changed. Clicks M1's Delete habit at the centre of the largest part of its box that lies outside the opener's box (the bin or P2's Delete habit), and fails at once when no such part exists. It replaces 1.0's wait for the Delete habit window, which R13 retires |
| `dialog_title(name)` | `'Delete "' + "⁨" + name + "⁩" + '"?'`, as 1.0 (SEC-02, SEC-06) |
| `encode(habits)` | the compact text `{"version":1,"habits":[...]}` that `encodeState` writes (`json.dumps` with `separators=(",", ":")` and `ensure_ascii=False`) |
| `stored(page)`, `record(page)`, `write_count(page)`, `hide_tab(page)`, `show_tab(page)` | as 1.0 |
| `row(page, name)`, `bin_btn`, `year_btn`, `done_btn`, `band_day(page, key)`, `p3_day`, `p4_day`, `bead(page, key)`, `tick(page, name)` | locators by habit name (the row's `h3`), by accessible name, or by `data-key` inside the band, P3, P4 or P2 |
| `focused(page)` | the accessible name of `document.activeElement`, or `"body"` |
| `press_twice(page, x, y, how)` | two presses at one point at the same instant of a paused clock, `how` being `"mouse"` (`mouse.dblclick`) or `"touch"` (two `touchscreen.tap`) |
| `animation_log(page)` | a test-side handle (`page.evaluate_handle`) on an array that a `document` listener fills with each `animationstart` (its `animationName` and its target's class list). It adds no property to `window` |
| `mutation_log(page, selector)` | a test-side handle on the child additions and removals a `MutationObserver` sees on one element |
| `watch_close(page, selector)`, `wait_for_close(watch)` | added at task 22. A test-side listener for a dialog's next `close` event, added after the app's, and a wait for it bounded at 5 seconds. Once it has come, the app's close handler has run (Engine differences by design, the focus back on the opener). Row added 2026-10-15 |

Changed 2026-10-15 in execute (planner touch after step 5, task 21's qa note 2, ledger S7 row 16). This table named `press_twice`, `animation_log` and `mutation_log` before `conftest.py` held them. Each came with the first test that used it, `press_twice` at task 22, `mutation_log` at task 23 and `animation_log` at task 25, so a helper here can land after the table names it. The row for `watch_close` and `wait_for_close` is new.

### Named starting states
- **the sample day.** `open_app` with the clock fixed at `2026-10-10T12:00:00+08:00` and storage `sample_state()`. Today is Saturday 10 October 2026. Habits in order "Read 20 pages", "Stretch 10 minutes", "No phone after 11pm". Read is done today, the others are not. Viewport 390 x 844 unless the scenario says 360 x 780 or 1280 x 800.
- **twelve habits.** As the sample day with storage `twelve_state()`. Seven of the twelve are done today.
- **a fresh day.** As the sample day with no storage at all.
- **N plain habits.** Storage `{"version":1,"habits":[{"name":"Habit 1","done":[]}, ..., {"name":"Habit N","done":[]}]}`, clock as above.
- **the clock installed and paused.** `install_time` at `2026-10-10T12:00:00+08:00`, then `page.clock.pause_at(PAUSE_AT)` once the page is open, so two presses in one step happen at the same instant on any machine.
- Measured sample values (spec R6, R35, R39). Last 14 days, newest first, D done. Read `DDDD.DD.DD.DD.`, Stretch `.DD..D.D.DDD..`, No phone `..DDDDDDD.DDD.`. Read Current 4 and Best 9, Stretch 2 and 5, No phone 0 and 14.

### Processes and evidence
- The QA finder starts each server in the background (or lets the conftest do it), records each PID, waits for it with a bounded poll (every 250 ms, gives up after 10 seconds and reports BLOCKED), runs the suite, stops each server by PID and confirms the port refuses connections. All of it goes in its `PROCESSES` block. Each run also lists every `Playwright.exe`, `chrome.exe` and `python.exe` it started and confirms none is left.
- Screenshots or logs a test saves go to `STREAKS_EVIDENCE_DIR`. The verdict goes to `docs/modules/app/findings/qa.md`, with the pass, fail and skip counts per engine.

## Functional test cases (Gherkin)

```gherkin
Feature: Shipped entry point, stylesheet and icon
  # tests/browser/test_entry.py (task 12), except where a scenario names another file
  # W1 and W2 wait on a later task ("Scenarios that wait on a later task", added 2026-10-13 after the plan re-check, F12)

  @R1
  Scenario: Head, CSP, icon link and relative URLs (v1.1.0 changed)
    Given the file index.html at the project root
    Then it starts with "<!doctype html>" and its html element has lang "en"
    And its head element children, ignoring comments, are these, in this order
      | element | attributes and text                                                                                                                                                                                       |
      | meta    | charset "utf-8"                                                                                                                                                                                           |
      | meta    | http-equiv "Content-Security-Policy", content "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'"      |
      | meta    | name "viewport", content "width=device-width, initial-scale=1, viewport-fit=cover"                                                                                                                       |
      | title   | "Danial's Streaky Habit"                                                                                                                                                                                  |
      | link    | rel "icon", type "image/svg+xml", href "src/icon.svg"                                                                                                                                                     |
      | link    | rel "stylesheet", href "src/styles.css"                                                                                                                                                                   |
      | script  | type "module", src "src/app.js"                                                                                                                                                                           |
    And a comment in the head names Phosphor Icons (MIT) with "x", "plus", "trash" and "check", and names the mark as the app's own
    And no src or href attribute in index.html starts with "/" or contains "://"
    And no element in index.html has an xmlns attribute
    And every import specifier in src/*.js starts with "./"

  @R1 @R29
  Scenario: The app works from a sub-path (v1.1.0 changed)
    Given the project's parent folder is served and the clock is fixed at 2026-10-10T12:00:00+08:00 with no storage
    When the page opens SUBPATH_URL
    Then ul.rows holds one li.empty and div.ovg-cols holds 83 button.hc
    And the href property of the icon link is SUBPATH_URL followed by "src/icon.svg"
    And the user can add "Read 20 pages" with the field and Add, and one li.row appears

  @R1
  Scenario: The static skeleton and the five dialogs (v1.1.0 changed)
    Given a fresh day
    Then the body's element children are, in order, the sprite svg, div.app, dialog.dlg-ov, dialog.dlg-all, dialog.dlg-year, dialog.dlg-day and dialog.dlg-del
    And the sprite has width "0", height "0", aria-hidden "true" and focusable "false", and holds the symbols "i-x", "i-plus", "i-check" and "i-trash" in that order, whose path data equal those of docs/design/today.html
    And svg.mark has viewBox "0 0 28 28", aria-hidden "true" and focusable "false" and one path whose d equals the mark's path in docs/design/today.html
    And no dialog has the open attribute, and the dialogs carry these attributes
      | dialog   | class list          | role        | aria-modal | aria-labelledby | aria-describedby |
      | dlg-ov   | dlg-full dlg-ov     | none        | true       | ov-title        | none             |
      | dlg-all  | dlg-full dlg-all    | none        | true       | all-title       | all-sub          |
      | dlg-year | dlg-full dlg-year   | none        | true       | yr-title        | yr-sub           |
      | dlg-day  | dlg-day             | none        | true       | day-title       | day-sub          |
      | dlg-del  | dlg-del             | alertdialog | true       | del-title       | del-body         |
    And the document holds no element with the class "scrim" or "below-desktop" and no element with an inert attribute
    And M1's two buttons are "Cancel" with the classes "btn btn-secondary" and "Delete habit" with the classes "btn btn-danger", both type "button", inside div.dlg-actions, and the document holds no form other than form.composer

  @R2
  Scenario: The stylesheet is system.css without its stand-ins, with the listed changes (v1.1.0 changed)
    Given the text of src/styles.css
    And the text of docs/design/system.css from ":root{" up to, and not including, the comment that starts "/* ---------- golden stand-ins"
    When the golden text gets changes 2 and 3 of spec R2, as these exact replacements
      | golden text                                                   | becomes                                                                         |
      | dialog[open]::backdrop, .scrim{ animation:fade 180ms var(--ease); } | dialog[open]::backdrop{ animation:fade 180ms var(--ease); }                     |
      | dialog::backdrop{ background:var(--scrim); }                  | dialog::backdrop{ background:var(--scrim, rgba(10,11,13,.74)); }                |
      | .dlg-day::backdrop{ background:var(--scrim-soft); }           | .dlg-day::backdrop{ background:var(--scrim-soft, rgba(10,11,13,.52)); }         |
    And both texts have comments removed and runs of whitespace collapsed to one space
    Then the two texts are identical
    And src/styles.css contains none of ".scrim", "dialog[open]{" and ".below-desktop"

  @R29
  Scenario: The icon file is the goldens' icon, byte for byte (v1.1.0 new)
    Given the href of the link with rel "icon" in today.html, day-editor.html, year-view.html, overview.html, overview-year.html, delete-dialog.html, today-empty.html and today-full.html
    Then the eight hrefs are identical and start with "data:image/svg+xml,", and states.html has no icon link
    And the bytes of src/icon.svg equal the UTF-8 bytes of the percent-decoded text after the first comma of that href, with nothing added or removed
    And src/icon.svg parses as XML whose root element is "{http://www.w3.org/2000/svg}svg" with viewBox "0 0 16 16"

  @R29 @R25
  Scenario: The page links the icon and the policy lets it load (v1.1.0 new)
    Given the sample day opened with record=True
    Then the document holds exactly one link whose rel contains "icon", and its href property is BASE_URL followed by "src/icon.svg"
    When the test, in the page, registers a securitypolicyviolation listener and then loads that href into a new Image
    Then the image fires load within 5 seconds with a natural width above 0
    And no securitypolicyviolation event has fired 2 seconds after the load
    And no console error and no page error was recorded

  @R29 @chromium_only
  Scenario: The icon is amber in a dark theme and dark amber in a light theme (v1.1.0 new)
    # chromium_only, reason CO-1 of the table above
    Given the same-origin page "__seed__" showing src/icon.svg in an img element drawn at 160 by 160 pixels
    When the colour scheme is emulated "dark"
    Then a pixel inside a filled part of the mark (a point the test names from the path data) reads rgb(255, 176, 32) in a screenshot of the img
    When the colour scheme is emulated "light"
    Then the same pixel reads rgb(154, 91, 0)

  @R26
  Scenario: No sample data in the shipped files (v1.1.0 changed)
    # tests/browser/test_platform.py
    Given the text of index.html and of every file under src/
    Then none contains any of the twelve habit names of docs/design/sample-history.json, and none contains "sample-history"

  @R26
  Scenario Outline: Query strings and fragments do not seed (v1.1.0 changed)
    # tests/browser/test_platform.py
    Given the clock is fixed at 2026-10-10T12:00:00+08:00 and there is no storage
    When the page opens "<path>"
    Then ul.rows holds one li.empty and no li.row, and stored(page) is null

    Examples:
      | path       |
      | ?demo=1    |
      | ?seed      |
      | #sample    |

  @R26
  Scenario: No globals and no hooks
    # tests/browser/test_platform.py
    Given the sample day
    When the own property names of window are read on the app page and on the same-origin page "__seed__" in the same context
    Then every name present on the app page is also present on the "__seed__" page

Feature: Two engines
  # tests/browser/test_engines.py holds the first three scenarios (task 11, seen RED through the conftest stubs of
  # "Controls are watched failing first") and the last one (written at task 19, W21). The fourth and the fifth are
  # finder checks on run output, and no test function holds them. The QA finder reads the fourth from the -rA output of
  # its Chromium and WebKit runs, and the fifth is read from the evidence of the live gate's runs at task 28.
  # Changed 2026-10-13 after the plan check (F3). This Feature first went into the 1.0 file test_platform.py, which
  # task 12 removes, and its last scenario presses Done today and Year, which the 1.0 app of task 11 does not have.
  # Changed 2026-10-13 after the plan re-check (N9, F13). Task 11 first put the two finder checks into test_engines.py.

  @R30
  Scenario: The run uses the engine it was asked for (v1.1.0 new)
    Given a run of the browser suite
    Then the name of the session browser's type equals the run's --engine value, and equals "chromium" when the command line carries no --engine
    And when STREAKS_EVIDENCE_DIR is set, the last part of its path ends with "-" followed by that engine

  @R30
  Scenario: An unknown engine is refused before any browser starts (v1.1.0 new)
    When the test runs "python -m pytest tests/browser --engine firefox --collect-only -q" with the parent run's STREAKS_BASE_URL and STREAKS_SUBPATH_URL, capped at 60 seconds
    Then it exits with code 4 and its error output names the choices "chromium" and "webkit"
    And calling launch(playwright, "firefox") raises ValueError

  @R30
  Scenario: One helper launches every browser (v1.1.0 new)
    Given the text of every file under tests/browser/
    Then ".launch(" appears only inside the function launch in conftest.py, and "launch_persistent_context" and "connect_over_cdp" appear nowhere
    And live_e2e.py imports launch from conftest.py
    And LAUNCH_ARGS gives ["--force-color-profile=srgb"] for chromium and [] for webkit
    And "is_mobile" appears nowhere

  @R30
  Scenario: A Chromium-only test is a counted skip with its reason in WebKit (v1.1.0 new)
    # checked by the QA finder from the -rA output of both runs
    Given the marker chromium_only is listed by "python -m pytest tests/browser --markers"
    When the suite runs with --engine webkit and -rA
    Then every test marked chromium_only is reported SKIPPED with its written reason, and none is reported PASSED
    And the number of such skips equals the number of rows in the Chromium-only table of this file
    When the suite runs with --engine chromium and -rA
    Then the same tests are reported PASSED

  @R30
  Scenario Outline: The live gate records its engine (v1.1.0 new)
    # checked by the QA finder on the gate's evidence
    Given a run of "python tests/browser/live_e2e.py --engine <engine>" with its base URL and output folder
    Then its summary.json names the engine "<engine>" and the browser.version Playwright reported for it
    And live_e2e.py holds no engine name other than in its --engine choices

    Examples:
      | engine   |
      | chromium |
      | webkit   |

  @R30
  Scenario: Every context has the clipboard stand-in (v1.1.0 new)
    # tests/browser/test_engines.py, written at task 19
    Given the sample day
    Then either navigator.clipboard is absent, or Clipboard.prototype.writeText is not the browser's native function
    And no console marker starting "test:clipboard:" is recorded through a run of this scenario's gestures (Done today on Stretch, then Year on Read and Close)

Feature: First visit and header
  # tests/browser/test_render.py (task 15)
  # W3 waits on a later task ("Scenarios that wait on a later task", added 2026-10-13 after the plan re-check, F12)

  @R3 @R35 @R42
  Scenario: The empty first screen (v1.1.0 changed)
    Given a fresh day at 1280 x 800
    Then ul.rows holds exactly one li.empty
    And its svg has viewBox "0 0 120 120" and aria-hidden "true" and holds circle.e-orbit (cx 60, cy 60, r 50) and circle.e-core (cx 60, cy 60, r 18), and its div holds p.lead "No habits yet." and p.line "Add one you want to do every day."
    And there is no li.row and div.banners has no child element
    And the field is enabled with value "", Add is enabled, #nh-msg is hidden and empty with the class list "field-msg", and the field has no aria-invalid
    And div.ovg-cols holds 83 button.hc named from "Mon 20 Jul, 0 of 0 habits" to "Sat 10 Oct, 0 of 0 habits" and one span.hc with aria-hidden "true" in the place of 2026-10-11
    And every one of the 83 rings holds one circle.seg (r 15) without the class "on", no circle.c-core, and a text.c-num with its day number and without the class "on"
    And only the 2026-10-10 button has aria-current "date" and a circle.c-today
    And the band's legend holds span "None", one svg holding one circle.seg and nothing else, and span "All"
    And stored(page) is null
    When the viewport becomes 390 x 844
    Then the Overview button's ring holds one circle.seg and no text element, and the button's aria-label is "Overview, today 0 of 0 habits done"

  @R4
  Scenario: Brand, mark and date (v1.1.0 changed)
    Given the sample day
    Then header.top's element children are div.brand, button.ov-btn and time.date, in that order
    And div.brand holds svg.mark and then h1.word "Streaky Habit"
    And the computed fill of the mark's path is rgb(255, 176, 32)
    And time.date has datetime "2026-10-10" and the text "Saturday 10 October"

  @R4
  Scenario Outline: The date follows the device clock (v1.1.0 changed)
    Given the clock is fixed at <instant> with no storage
    Then time.date has datetime "<key>" and the text "<text>"

    Examples:
      | instant                   | key        | text                |
      | 2026-10-05T09:00:00+08:00 | 2026-10-05 | Monday 5 October    |
      | 2026-10-07T23:59:59+08:00 | 2026-10-07 | Wednesday 7 October |
      | 2027-01-01T00:00:30+08:00 | 2027-01-01 | Friday 1 January    |

  @R4 @R38
  Scenario Outline: The header on a phone and on a desktop (v1.1.0 new)
    Given the sample day at <viewport>
    Then the computed display of button.ov-btn is "<overview>"
    And time.date lies <date place>

    # Changed 2026-10-14 in execute (planner touch-up, Q2, ledger S7 row 15, ruled ORCH to the golden). The two phone
    # rows first read ~~inline-flex~~, the value system.css writes. button.ov-btn is a grid item of header.top, so the
    # browser blockifies its display, and today.html itself computes "flex" at 360 and 390 in Chromium and in WebKit
    # (measured at task 15, BUILD.md task 15, Q2). The golden is the truth, so the rows read "flex".
    Examples:
      | viewport | overview    | date place                                                                                                   |
      | 360x780  | flex        | on its own line, its top below the bottom of div.brand                                                       |
      | 390x844  | flex        | on its own line, its top below the bottom of div.brand                                                       |
      | 1280x800 | none        | on the brand line, its vertical centre between the top and bottom of div.brand, its right edge within 1 px of the right edge of header.top |

  @R4
  Scenario: English under a German browser locale (v1.1.0 changed)
    Given the sample day with locale "de-DE"
    Then the date reads "Saturday 10 October" and the Overview button's aria-label is "Overview, today 1 of 3 habits done"
    And the band's 2026-07-20 is named "Mon 20 Jul, 2 of 3 habits" and its month labels read "Jul", "Aug", "Sep" and "Oct"
    When the user clicks "Year view, Read 20 pages"
    Then P2's first month title reads "October 2026" and the bead 2026-10-10 is named "Mark Sat 10 Oct 2026 as done"
```
```gherkin
Feature: Rows, numbers and the list frame
  # tests/browser/test_render.py (task 15)
  # W4 and W5 wait on a later task ("Scenarios that wait on a later task", added 2026-10-13 after the plan re-check, F12)

  @R5 @R6
  Scenario: Rows in stored order (v1.1.0 changed)
    Given the sample day
    Then ul.rows has aria-labelledby "h-habits" and holds 3 li.row whose h3.r-name texts are "Read 20 pages", "Stretch 10 minutes" and "No phone after 11pm", with ids "rn-1", "rn-2" and "rn-3"
    And each row's element children are div.r-head (holding the h3 and then button.btn-bin), p.stats with id "rs-N", button.btn-year and button.btn-done, in that order
    And the bins are named 'Delete "Read 20 pages"', 'Delete "Stretch 10 minutes"' and 'Delete "No phone after 11pm"', have type "button" and aria-haspopup "dialog", and each holds an svg.ph using "#i-trash"
    And the Year buttons read "Year", are named "Year view, Read 20 pages", "Year view, Stretch 10 minutes" and "Year view, No phone after 11pm", and have type "button" and aria-haspopup "dialog"
    And the Done today buttons read "Done today", are named "Done today, Read 20 pages", "Done today, Stretch 10 minutes" and "Done today, No phone after 11pm", have type "button", aria-pressed "true", "false" and "false", and aria-describedby "rs-1", "rs-2" and "rs-3", and each holds span.dot with an svg using "#i-check"

  @R6
  Scenario Outline: Current and Best for the sample (v1.1.0 changed)
    Given the sample day
    Then p.stats of "<habit>" holds span.stat.cur with span.lbl "Current" and then <current>
    And after it span.stat.best with span.lbl "Best" and span.val holding b.num "<best>"

    Examples:
      | habit               | current                                          | best |
      | Read 20 pages       | span.val holding b.num "4" and span.unit "days"  | 9    |
      | Stretch 10 minutes  | span.val holding b.num "2" and span.unit "days"  | 5    |
      | No phone after 11pm | span.none "No streak yet"                        | 14   |

  @R6 @R31
  Scenario: Twelve habits show the goldens' numbers (v1.1.0 new)
    Given twelve habits
    Then the rows show, in this order, these numbers and Done today states
      | habit                   | Current       | Best | Done today pressed |
      | Read 20 pages           | 4 days        | 9    | true               |
      | Stretch 10 minutes      | 2 days        | 5    | false              |
      | No phone after 11pm     | No streak yet | 14   | false              |
      | Drink 2 litres of water | 1 day         | 11   | true               |
      | Walk 8,000 steps        | 1 day         | 11   | false              |
      | Journal one page        | 8 days        | 11   | true               |
      | Practise guitar         | 1 day         | 11   | true               |
      | Cook dinner at home     | 5 days        | 11   | true               |
      | Lights out by midnight  | 2 days        | 11   | false              |
      | Meditate 5 minutes      | 2 days        | 11   | true               |
      | Floss                   | 1 day         | 11   | true               |
      | Learn 10 Malay words    | 1 day         | 11   | false              |
    And a Current of 1 has span.unit "day", and every other Current number has span.unit "days"

  @R6 @R10
  Scenario: A new habit shows no Best block (v1.1.0 changed)
    Given the sample day
    When the user adds "Drink water"
    Then the fourth row's p.stats holds only span.stat.cur, with span.lbl "Current" and span.none "No streak yet", and no span.stat.best element

  @R5 @R21
  Scenario Outline: The page never scrolls and the composer stays put (v1.1.0 changed)
    Given <state> at <viewport>
    Then document.documentElement.scrollHeight equals the viewport height and scrollWidth is at most the viewport width
    # Changed 2026-10-14 in execute (planner touch-up, Q1, ledger S7 row 15, ruled ORCH to the golden). This line first
    # read ~~And the bounding box of form.composer equals its box for a fresh day at that viewport~~. With twelve habits
    # the 12-habit note grows form.composer upward in today-full.html (checklist S3-07 and S3-08, composer top 622
    # against 670 at 360x780, 686 against 734 at 390x844, 686 against 714 at 1280x800, measured on the goldens at task
    # 15), while the field keeps its box. So the field is checked in every row and the composer in the other six.
    And the bounding box of the field (#nh) equals its box for a fresh day at that viewport
    And, unless the state is twelve habits, the bounding box of form.composer equals its box for a fresh day at that viewport

    Examples:
      | state          | viewport |
      | a fresh day    | 360x780  |
      | the sample day | 360x780  |
      | twelve habits  | 360x780  |
      | a fresh day    | 390x844  |
      | the sample day | 390x844  |
      | twelve habits  | 390x844  |
      | a fresh day    | 1280x800 |
      | the sample day | 1280x800 |
      | twelve habits  | 1280x800 |

  @R5
  Scenario: The list scrolls inside its frame and shows where more lies (v1.1.0 new)
    Given twelve habits at 390 x 844
    Then div.frame's scrollHeight is greater than its clientHeight, its scrollTop is 0, and div.frame-wrap has the class "more-below" and not "more-above"
    When the user turns the mouse wheel down by 200 pixels over div.frame
    Then div.frame's scrollTop is above 0, window.scrollY is 0, and div.frame-wrap has both "more-above" and "more-below"
    When the user turns the mouse wheel down by 3000 pixels over div.frame
    Then div.frame is scrolled to its end, and div.frame-wrap has "more-above" and not "more-below"
    When the user turns the mouse wheel up by 3000 pixels over div.frame
    Then div.frame-wrap has "more-below" and not "more-above"

  @R5
  Scenario: The fades follow the rows and a resize (v1.1.0 new)
    Given 4 plain habits at 390 x 844
    Then div.frame's scrollHeight equals its clientHeight and div.frame-wrap has neither "more-above" nor "more-below"
    When the viewport becomes 390 x 520
    Then div.frame's scrollHeight is greater than its clientHeight and div.frame-wrap has "more-below"
    When the viewport becomes 390 x 844 again
    Then div.frame-wrap has neither class
    When the user adds "Habit 5", "Habit 6" and "Habit 7"
    Then div.frame's scrollHeight is greater than its clientHeight
    And div.frame-wrap has "more-above" exactly when div.frame's scrollTop is above 0, and "more-below" exactly when its scrollTop plus its clientHeight is less than its scrollHeight, and has at least one of the two

Feature: The overview band
  # tests/browser/test_render.py (task 15)

  @R35 @R42
  Scenario: The band on a desktop (v1.1.0 new)
    Given the sample day at 1280 x 800
    Then section.band has aria-labelledby "h-ov" and the computed display "grid"
    And div.band-meta holds div.band-head (h2#h-ov "Last 12 weeks" and then button.btn-all of type "button" with aria-haspopup "dialog", named "Year view, all habits", reading "Year"), then p.hint "Tap a day to change it.", then div.legend with aria-hidden "true"
    And div.ovg-cols has role "group", aria-labelledby "h-ov" and 104 element children. An empty div with aria-hidden "true", seven div.og-wd with aria-hidden "true" reading "M", "T", "W", "T", "F", "S" and "S", then for each of 12 weeks one div.og-mo with aria-hidden "true" and its 7 cells
    And the og-mo texts read "Jul" over week 1, "Aug" over week 3, "Sep" over week 8 and "Oct" over week 12, and are empty over the other weeks
    And the cells are 83 button.hc of type "button" with aria-haspopup "dialog" and data-key from "2026-07-20" to "2026-10-10", one day apart in grid order, then one empty span.hc with aria-hidden "true" for Sunday 11 October
    And each button is named "<shortDate>, <n> of 3 habits", n being the number of the three habits done that day, for example "Mon 20 Jul, 2 of 3 habits", "Tue 22 Sep, 1 of 3 habits" and "Sat 10 Oct, 1 of 3 habits"
    And only the 2026-10-10 button has aria-current "date"
    And of the 83 rings, 2 have no path.seg with the class "on", 16 have one, 47 have two, and 18 have three together with circle.c-core and a text.c-num with the class "on"
    And the legend holds span "None", four svg rings with 0, 1, 2 and 3 path.seg on (the fourth with circle.c-core), and span "All", and no legend ring has a text element or a circle.c-today

  @R35
  Scenario Outline: The band shows from 1024 pixels (v1.1.0 new)
    Given the sample day at <viewport>
    Then the computed display of section.band is "<display>" and div.ovg-cols holds 83 button.hc

    Examples:
      | viewport | display |
      | 390x844  | none    |
      | 1023x800 | none    |
      | 1024x800 | grid    |
      | 1280x800 | grid    |

Feature: Rings and the legend
  # tests/ring.test.js (task 13) for the Node scenarios, tests/browser/test_render.py (task 15) for the rest
  # W6 waits on a later task ("Scenarios that wait on a later task", added 2026-10-13 after the plan re-check, F12)

  @R42
  Scenario: arcPath reproduces the goldens' shared arcs (v1.1.0 new)
    # Node
    Given the d attributes of the paths "a3-0" to "a3-2" in docs/design/today.html and "a12-0" to "a12-11" in docs/design/today-full.html
    Then arcPath(i, 3) equals the d of "a3-i" for i 0 to 2, and arcPath(i, 12) equals the d of "a12-i" for i 0 to 11

  @R42
  Scenario Outline: arcPath for other numbers of habits (v1.1.0 new)
    # Node. The values follow the arc rule of spec R42 and were computed with it while planning
    Then arcPath(<i>, <n>) is "<d>"

    Examples:
      | n | i | d                                      |
      | 2 | 0 | M22.86 5.28A15 15 0 0 1 22.86 34.72   |
      | 2 | 1 | M17.14 34.72A15 15 0 0 1 17.14 5.28   |
      | 5 | 0 | M22.81 5.27A15 15 0 0 1 33.14 12.77   |
      | 5 | 1 | M34.88 18.12A15 15 0 0 1 30.93 30.27  |
      | 5 | 2 | M26.39 33.57A15 15 0 0 1 13.61 33.57  |
      | 5 | 3 | M9.07 30.27A15 15 0 0 1 5.12 18.12    |
      | 5 | 4 | M6.86 12.77A15 15 0 0 1 17.19 5.27    |

  @R42
  Scenario Outline: legendCounts (v1.1.0 new)
    # Node
    Then legendCounts(<n>) is <counts>

    Examples:
      | n  | counts          |
      | 0  | [0]             |
      | 1  | [0, 1]          |
      | 2  | [0, 1, 2]       |
      | 3  | [0, 1, 2, 3]    |
      | 4  | [0, 2, 3, 4]    |
      | 5  | [0, 2, 4, 5]    |
      | 12 | [0, 4, 8, 12]   |

  @R42
  Scenario: ring.js is pure (v1.1.0 new)
    # Node
    Given the text of src/ring.js
    Then it has no import statement and contains none of "document", "window", "globalThis", "localStorage" and "Date"
    And its exports are exactly arcPath and legendCounts

  @R42
  Scenario: A ring's parts and their order (v1.1.0 new)
    Given the sample day at 1280 x 800
    Then the band's 2026-10-10 ring is an svg with viewBox "0 0 40 40" and aria-hidden "true" whose children are, in order, circle.c-today (cx 20, cy 20, r 19.2), three path.seg whose d attributes are arcPath(0, 3), arcPath(1, 3) and arcPath(2, 3) with only the first having the class "on", and text.c-num (x 20, y 20, dy ".352em") reading "10" without the class "on"
    And the 2026-07-21 ring holds three path.seg with the class "on", then circle.c-core (cx 20, cy 20, r 11.5), then text.c-num "21" with the class "on", and no circle.c-today
    And the 2026-09-27 ring holds three path.seg without the class "on" and no circle.c-core

  @R42
  Scenario Outline: Rings for no habit and for one habit (v1.1.0 new)
    Given the clock is fixed at 2026-10-10T12:00:00+08:00, the viewport is 1280 x 800 and storage holds <storage>
    Then the band's 2026-10-10 ring holds circle.c-today, then <segment>, then <core>, then text.c-num "10" <number class>

    Examples:
      | storage                                                       | segment                               | core                | number class           |
      | {"version":1,"habits":[]}                                     | one circle.seg (r 15) without "on"    | no circle.c-core    | without the class "on" |
      | {"version":1,"habits":[{"name":"Read","done":[]}]}            | one circle.seg (r 15) without "on"    | no circle.c-core    | without the class "on" |
      | {"version":1,"habits":[{"name":"Read","done":["2026-10-10"]}]} | one circle.seg (r 15) with "on"      | circle.c-core       | with the class "on"    |

  @R42
  Scenario: Twelve habits draw twelve segments (v1.1.0 new)
    Given twelve habits at 1280 x 800
    Then every band ring holds twelve path.seg whose d attributes are arcPath(0, 12) to arcPath(11, 12)
    And the legend holds "None", four rings with 0, 4, 8 and 12 of their twelve path.seg on (the last with circle.c-core), and "All"

  @R42
  Scenario: Small rings carry no number and no today circle (v1.1.0 new)
    Given the sample day at 390 x 844
    Then the Overview button's ring holds three path.seg, only the first with "on", and no text and no circle.c-today
    When the user clicks Overview and then P3's "Sat 10 Oct, 1 of 3 habits"
    Then div.day-mini's ring holds three path.seg, only the first with "on", and no text, no circle.c-today and no circle.c-core

  @R42
  Scenario: Every svg part in the page and the popups is in the SVG namespace and draws (v1.1.0 new)
    # Added 2026-10-15 in execute (planner touch after step 5, code review WR-01 (a), the QA re-check, spec R42's note of
    # 2026-10-15). The 1.0 review's guard, lost when the tests were written again. An svg, use, path, circle or text in
    # the HTML namespace draws nothing and has no getBBox. The test came with the step 5 solver round (commit adcb981).
    Given the sample day at 1280 x 800
    Then the first path.seg of the band's 2026-10-10 ring has a getBBox() wider than 0
    When the user clicks the band's Year and then P4's "Tue 22 Sep 2026, 1 of 3 habits", so P1 opens over P4
    Then every svg, use, path, circle and text in the document is in the SVG namespace, and each of the five names is there at least once
    When the user presses Escape twice, then clicks "Year view, Read 20 pages" and P2's Delete habit, so M1 opens over P2
    Then every svg, use, path, circle and text in the document is in the SVG namespace, and each of the five names is there at least once
    Given, in a second context, the sample day at 390 x 844
    Then the first path.seg of the Overview button's ring has a getBBox() wider than 0
    When the user clicks Overview
    Then the first path.seg of P3's 2026-10-10 ring has a getBBox() wider than 0
    And every svg, use, path, circle and text in the document is in the SVG namespace, and each of the five names is there at least once
    Given, in a third context, storage holding "{" at 390 x 844, so S1 shows with the note
    Then li.empty's circle.e-orbit has a getBBox() wider than 0
    And every svg, use, path, circle and text in the document is in the SVG namespace, and each of the five names is there at least once

Feature: Done today and every view at once
  # tests/browser/test_today.py (task 16)
  # W7 to W13 wait on later tasks ("Scenarios that wait on a later task", added 2026-10-13 after the plan re-check, F12)

  @R31 @R16
  Scenario Outline: Done today presses and unpresses (v1.1.0 new)
    Given the sample day and a handle to "Done today, <habit>"
    When the user clicks it
    Then the same handle is still connected to the document and its aria-pressed is "<pressed>"
    And the row of "<habit>" reads Current "<current>" and Best "<best>"
    And the band's 2026-10-10 is named "Sat 10 Oct, <count> of 3 habits"
    And in stored(page) the done list of "<habit>" <stored> "2026-10-10"
    And in Chromium that button has focus. In WebKit document.activeElement is body

    Examples:
      | habit               | pressed | current | best | count | stored           |
      | Stretch 10 minutes  | true    | 3 days  | 5    | 2     | contains         |
      | Read 20 pages       | false   | 3 days  | 9    | 0     | does not contain |
      | No phone after 11pm | true    | 1 day   | 14   | 2     | contains         |

  @R31
  Scenario: Keyboard presses keep focus (v1.1.0 new)
    Given the sample day
    When the user presses Tab until "Done today, Stretch 10 minutes" has focus, then presses Space
    Then that button has aria-pressed "true", is still document.activeElement, and its row reads "Current 3 days"
    When the user presses Enter
    Then it has aria-pressed "false", is still document.activeElement, and its row reads "Current 2 days" and "Best 5"

  @R31 @R16
  Scenario: Pressing twice restores the saved value (v1.1.0 new)
    Given the sample day and the stored text S
    When the user clicks "Done today, Stretch 10 minutes" twice
    Then stored(page) parses to the same object as S

  @R32 @R16
  Scenario: One Done today updates every place at once, and only what changed moves (v1.1.0 new)
    Given the sample day at 1280 x 800 with count_writes
    When the user clicks "Done today, Stretch 10 minutes"
    Then exactly one write was made
    And the Stretch row reads "Current 3 days" and "Best 5", its Current span.val has the class "bump" and its Best span.val does not
    And Stretch's Done today button has the class "pop", and Read's and No phone's Done today buttons do not
    And no element of the Read row or the No phone row has the class "bump"
    And the band's 2026-10-10 is named "Sat 10 Oct, 2 of 3 habits", its first two path.seg have the class "on", and the button has the class "pop"
    And no other band button has the class "pop"
    And span.ov-ring has the class "pop", and the Overview button is named "Overview, today 2 of 3 habits done" with the first two path.seg of its ring on
    When the user clicks "Year view, Stretch 10 minutes"
    Then the bead 2026-10-10 has aria-pressed "true" and the classes "on", "today" and "l", and the bead 2026-10-09 has the class "r"

  @R32 @R37
  Scenario: A tick in P1 over P3 updates P3 and the row, and leaves today's ring alone (v1.1.0 new)
    Given the sample day at 390 x 844
    When the user clicks Overview, then P3's "Tue 22 Sep, 1 of 3 habits", then the tick "Read 20 pages"
    Then P3's 2026-09-22 button is named "Tue 22 Sep, 2 of 3 habits", has its first and third path.seg on, and has the classes "pop" and "is-open"
    And the Read row under the popups reads "Current 4 days" and "Best 13", with "bump" on its Best span.val and not on its Current span.val
    And the band's 2026-09-22 (in the DOM, not displayed) is named "Tue 22 Sep, 2 of 3 habits"
    And the Overview button is still named "Overview, today 1 of 3 habits done" and span.ov-ring has no "pop"

  @R32 @R39
  Scenario: A tick in P1 over P4 updates P4 and P3 beneath it (v1.1.0 new)
    Given the sample day at 390 x 844
    When the user clicks Overview, then P3's Year, then P4's "Tue 22 Sep 2026, 1 of 3 habits", then the tick "Stretch 10 minutes"
    Then P4's 2026-09-22 button is named "Tue 22 Sep 2026, 2 of 3 habits" and has the class "pop"
    And P3's 2026-09-22 button is named "Tue 22 Sep, 2 of 3 habits"
    And the Stretch row still reads "Current 2 days" and "Best 5" and no element of it has "bump"

  @R32 @R34
  Scenario: A tick in P2 updates P2, the row and the band (v1.1.0 new)
    Given the sample day at 1280 x 800
    When the user clicks "Year view, No phone after 11pm" and then the bead 2026-10-09
    Then P2's p.yr-stats holds Current "8" "days" with "bump" on that span.val, and Best "14"
    And the No phone row reads "Current 8 days" and "Best 14"
    And the band's 2026-10-09 is named "Fri 9 Oct, 3 of 3 habits", holds circle.c-core and a text.c-num with the class "on", and has the class "pop"

  @R32 @R16
  Scenario: Each edit saves once, and opening or closing a popup saves nothing (v1.1.0 new)
    Given the sample day at 1280 x 800 with count_writes
    When the user opens and closes P2 (Year on Read, then Close), P4 (the band's Year, then Close) and P1 (the band's 2026-09-22, then Close)
    Then no write was made
    When the user clicks "Done today, Stretch 10 minutes"
    Then 1 write was made in all
    When the user ticks Read in P1 for 2026-09-22 and closes P1
    Then 2 writes were made in all
    When the user ticks the bead 2026-10-09 in No phone's P2 and closes P2
    Then 3 writes were made in all
    When the user adds "Drink water"
    Then 4 writes were made in all
    When the user deletes "Drink water" with its bin and confirm_delete
    Then 5 writes were made in all, and stored(page) equals encode of the habits on screen

  @R6 @R32
  Scenario Outline: Best back to 0 removes the Best block in every place (v1.1.0 new)
    # Succeeds test_R6_best_goes_back_to_zero_in_place_when_the_only_tick_is_undone of the 1.0 test_tick.py, which
    # guarded a 1.0 defect. The tick path updated the stats in place and left behind the Best element it had added
    # when Best fell back to 0. The P1 and P2 rows are W12. Added 2026-10-13 after the plan re-check (F14).
    Given 1 plain habits (one habit "Habit 1" with no done day) at 1280 x 800, with <popup>
    Then the row of "Habit 1" has p.stats holding only span.stat.cur, with span.lbl "Current" and span.none "No streak yet"
    When the user clicks <control>
    Then the row's p.stats holds span.stat.cur with span.val holding b.num "1" and span.unit "day", then span.stat.best with span.lbl "Best" and span.val holding b.num "1"
    And <after a tick>
    When the user clicks <control> again
    Then the row's p.stats holds only span.stat.cur, with span.lbl "Current" and span.none "No streak yet", and no span.stat.best element
    And <after an untick>

    Examples:
      | popup                                | control               | after a tick                                                                                                 | after an untick                                                                                       |
      | no popup open                        | "Done today, Habit 1" | "Done today, Habit 1" has aria-pressed "true"                                                                | "Done today, Habit 1" has aria-pressed "false"                                                        |
      | P1 open for 2026-10-10 from the band | the tick "Habit 1"    | the tick's span.tstat holds span.tcur "Current 1 day" and then a span "Best 1"                               | the tick's span.tstat holds only span.tcur.none "No streak yet", and no span "Best"                   |
      | P2 open for "Habit 1"                | the bead 2026-10-10   | P2's p.yr-stats holds span.stat.cur with b.num "1" and span.unit "day", then span.stat.best with b.num "1"   | P2's p.yr-stats holds only span.stat.cur, with span.none "No streak yet", and no span.stat.best element |

  @R32
  Scenario Outline: A tick that changes Current and leaves Best moves Current only (v1.1.0 new)
    # Succeeds test_JC3_a_tick_writes_only_the_text_that_changed of the 1.0 test_tick.py (BUILD.md item 3, JC3). JC3 kept
    # a tick from writing a text again, because the 1.0 streak line was a live region (1.0 R6, aria-live polite) and a
    # screen reader may read a rewritten text again. In every v1.1.0 golden only #nh-msg carries aria-live, so that
    # reason lapses and no scenario counts text writes. What stays is R32's rule that an element whose value did not
    # change carries no class from the edit. "One Done today updates every place at once, and only what changed moves"
    # holds it for Done today, and the rows below hold it in P1 and P2. Both rows are W13. Added 2026-10-13 after the
    # plan re-check (F14).
    Given the sample day at 1280 x 800, with <popup>
    When the user clicks <control>
    Then the Stretch row reads "Current 3 days" and "Best 5", with "bump" on its Current span.val and not on its Best span.val
    And no element of the Read row or the No phone row has the class "bump"
    And <popup stats>

    Examples:
      | popup                                | control                       | popup stats                                                                                                       |
      | P1 open for 2026-10-10 from the band | the tick "Stretch 10 minutes" | the tick's span.tstat reads "Current 3 days" and "Best 5"                                                         |
      | P2 open for "Stretch 10 minutes"     | the bead 2026-10-10           | P2's p.yr-stats holds Current "3" "days" with "bump" on that span.val, and Best "5" without "bump" on its span.val |

Feature: Popups
  # tests/browser/test_popups.py (task 17)
  # W14 to W18 wait on later tasks ("Scenarios that wait on a later task", added 2026-10-13 after the plan re-check, F12)

  @R40
  Scenario: Popups stack and Esc closes the top one only (v1.1.0 new)
    Given the sample day at 390 x 844
    When the user clicks Overview, then P3's Year, then P4's "Tue 22 Sep 2026, 1 of 3 habits"
    Then dialog.dlg-ov, dialog.dlg-all and dialog.dlg-day are open and each matches ":modal"
    And document.elementFromPoint at the centre of P1's div.dlg-box lies inside dialog.dlg-day
    When the user presses Escape
    Then P1 is closed, P4 and P3 are open, and focus is on P4's 2026-09-22 button
    When the user presses Escape
    Then P4 is closed, P3 is open, and focus is on P3's Year
    When the user presses Escape
    Then no dialog is open and focus is on the Overview button

  @R40 @R14
  Scenario Outline: A backdrop click closes that popup only (v1.1.0 new)
    Given the sample day at <viewport> with <popups> open
    When the user clicks the viewport point (5, 5), which lies outside the top popup's box (checked)
    Then <closed> is closed, <open> is open, and focus is on <focus>

    Examples:
      | viewport | popups                                         | closed | open | focus                             |
      | 390x844  | M1, from 'Delete "Stretch 10 minutes"'         | M1     | none | 'Delete "Stretch 10 minutes"'     |
      | 1280x800 | M1, from 'Delete "Stretch 10 minutes"'         | M1     | none | 'Delete "Stretch 10 minutes"'     |
      | 390x844  | P3, then P1 for 2026-09-22                     | P1     | P3   | P3's 2026-09-22 button            |
      | 1280x800 | P1 for 2026-09-22 from the band                | P1     | none | the band's 2026-09-22 button      |
      | 1280x800 | P2 for Read                                    | P2     | none | "Year view, Read 20 pages"        |
      | 1280x800 | P4 from the band's Year                        | P4     | none | the band's Year                   |
      | 1280x800 | P2 for Read, then M1 from its Delete habit     | M1     | P2   | P2's Delete habit                 |
      | 800x900  | P3                                             | P3     | none | the Overview button               |

  @R40 @R14
  Scenario Outline: A click inside the box, or a drag that leaves it, closes nothing (v1.1.0 new)
    Given the sample day at <viewport> with <popup> open
    When the user clicks inside its div.dlg-box 6 pixels right of and below its top-left corner (padding, no control there, checked)
    Then it is still open
    When the user presses the mouse button on <title>, moves the mouse to the viewport point (5, 5) and releases it there
    Then it is still open

    Examples:
      | viewport | popup                                   | title          |
      | 390x844  | M1, from 'Delete "Stretch 10 minutes"'  | #del-title     |
      | 1280x800 | P1 for 2026-09-22 from the band         | h2#day-title   |
      | 1280x800 | P2 for Read                             | h2#yr-title    |
      | 1280x800 | P4 from the band's Year                 | h2#all-title   |

  @R40
  Scenario Outline: Tab never reaches a control outside the top popup (v1.1.0 new)
    Given the sample day at <viewport> with <popups> open
    When the user presses Tab <n> times
    Then after each press document.activeElement is not a control outside the top popup

    Examples:
      | viewport | popups                                  | n  |
      | 390x844  | P3, then P1 for 2026-09-22              | 6  |
      | 1280x800 | P2 for Read                             | 10 |
      | 390x844  | M1, from 'Delete "Read 20 pages"'       | 4  |

  @R40
  Scenario Outline: Every popup is modal and the page does not scroll under it (v1.1.0 new)
    Given the sample day at <viewport>
    When the user opens <popup>
    Then every open dialog matches ":modal" and the computed overflow of html is "hidden"
    When the user presses Escape until no dialog is open
    Then the computed overflow of html is "visible"

    Examples:
      | viewport | popup                                   |
      | 390x844  | P3                                      |
      | 390x844  | P3, then P4 from its Year               |
      | 390x844  | P2 for Read                             |
      | 1280x800 | P1 for 2026-09-22 from the band         |
      | 390x844  | M1, from 'Delete "Read 20 pages"'       |

Feature: The overview popup and the year of all habits
  # tests/browser/test_overview.py (tasks 17 and 20)

  @R38 @R42
  Scenario: The Overview button opens P3 (v1.1.0 new, CG-16 ruled)
    Given the sample day at 390 x 844
    Then button.ov-btn has type "button", aria-haspopup "dialog", aria-label "Overview, today 1 of 3 habits done" and the text "Overview", and holds span.ov-ring with aria-hidden "true" whose svg is 28 by 28 pixels with three path.seg, only the first on
    When the user clicks it
    Then dialog.dlg-ov is open and matches ":modal", Close has focus, and its div.sheet-body has scrollTop 0
    And its head holds h2#ov-title "Last 12 weeks", p.hint "Tap a day to change it.", button.btn-all named "Year view, all habits" and button.icon-btn named "Close", in that order
    And div.ovg-rows has role "group", aria-labelledby "ov-title" and 104 element children. An empty div, seven div.og-wd reading "M", "T", "W", "T", "F", "S" and "S", then 12 rows of one div.og-mo and 7 cells
    And the rows run newest first. Row 1 holds the buttons for Monday 5 to Saturday 10 October and an empty span.hc with aria-hidden "true" for Sunday 11 October, and row 12 holds Monday 20 to Sunday 26 July
    And the og-mo texts read "Oct" in row 1, "Sep" in row 5, "Aug" in row 10 and "Jul" in row 12, and are empty in the other rows
    And the 83 buttons have the same names and rings as the band's, the 2026-10-10 one with aria-current "date" and circle.c-today
    And after the grid, div.legend with aria-hidden "true" holds "None", four rings and "All"

  @R38 @R40
  Scenario Outline: P3 closes and gives focus back to Overview (v1.1.0 new)
    Given the sample day at 390 x 844 with P3 open
    When the user <action>
    Then P3 is closed and focus is on the Overview button

    Examples:
      | action         |
      | clicks Close   |
      | presses Escape |

  @R38 @R22
  Scenario: P3 cannot be reached on a desktop (v1.1.0 new)
    Given the sample day at 1280 x 800 with nothing focused
    When the user presses Tab 95 times
    Then focus never lands on the Overview button and dialog.dlg-ov never opens

  @R39 @R42
  Scenario: The band's Year opens P4 (v1.1.0 new)
    Given the sample day at 1280 x 800
    When the user clicks the band's "Year view, all habits"
    Then dialog.dlg-all is open over K1 and matches ":modal", Close has focus, and its div.sheet-body has scrollTop 0
    And its head holds h2#all-title "All habits", p#all-sub.dlg-sub "The last 12 months", Close, and div.yr-tools with p.hint "Tap a day to change it." and div.legend (aria-hidden "true", "None", four rings, "All")
    And div.months.months-all holds 13 section.month, newest first, labelled by "amo-2026-10", "amo-2026-9" and so on to "amo-2025-10" (the month without a leading zero), whose h3 with those ids read "October 2026" to "October 2025"
    And each month's div.mgrid has role "group", is labelled by its h3, and holds seven span.mwd with aria-hidden "true" reading "M", "T", "W", "T", "F", "S" and "S", then its lead cells, then one cell per day
    And the grids hold 366 button.hc named from "Fri 10 Oct 2025, 3 of 3 habits" to "Sat 10 Oct 2026, 1 of 3 habits", 21 span.hc.closed for 11 to 31 October 2026 each holding an svg with only a text.c-num.dim reading its day, 9 span.hc.blank for 1 to 9 October 2025 and 39 span.hc.lead, every span with aria-hidden "true"
    And the lead cells number 3 in October 2026, 1 in September 2026, 5 in August 2026, 2 in July 2026 and 2 in October 2025
    And only the 2026-10-10 button has aria-current "date" and a circle.c-today
    And of the 366 rings, 18 have no segment on, 96 have one, 153 have two and 99 have three with circle.c-core

  @R39
  Scenario: P4 on a phone covers P3 (v1.1.0 new)
    Given the sample day at 390 x 844 with P3 open
    When the user clicks P3's Year
    Then P4 is open over P3, P3 is still open, P4's div.dlg-box covers the viewport (0, 0, 390, 844), and P4's Close has focus

  @R39 @R40
  Scenario Outline: P4 closes and gives focus back to the Year that opened it (v1.1.0 new)
    Given the sample day at <viewport> with P4 open from <opener>
    When the user <action>
    Then P4 is closed, <still open>, and focus is on <opener>

    Examples:
      | viewport | opener          | action                               | still open        |
      | 1280x800 | the band's Year | clicks Close                         | no dialog is open |
      | 1280x800 | the band's Year | presses Escape                       | no dialog is open |
      | 1280x800 | the band's Year | clicks the viewport point (5, 5)     | no dialog is open |
      | 390x844  | P3's Year       | clicks Close                         | P3 is open        |
      | 390x844  | P3's Year       | presses Escape                       | P3 is open        |

  @R39
  Scenario: P4 opens again at its top after it closed scrolled (v1.1.0 new)
    # Added 2026-10-15 in execute (planner touch after step 5, code review WR-04, the QA re-check). The test came with
    # the step 5 solver round (commit 5b07fc4). P3 has no such scenario, because its body has nothing to scroll once the
    # room of spec R36 is gone ("On a phone the host of P1 gets room ...", its after column).
    Given the sample day at 390 x 844 with P4 open from P3's Year
    When the user clicks P4's "Fri 10 Oct 2025, 3 of 3 habits", so P1 opens over P4 and rule 4 scrolls P4's div.sheet-body
    And the user presses Escape twice, P1 closing and then P4, with P4's div.sheet-body at a scrollTop above 0 before each press
    And the user clicks P3's Year again
    Then P4 is open and its div.sheet-body has scrollTop 0

Feature: The day editor
  # tests/browser/test_day_editor.py (tasks 18 and 20)
  # Task 20 writes the scenarios and rows that use P4, among them the two P4 rows of W22 ("Scenarios that wait on a
  # later task", added 2026-10-13 after the plan re-check, F12)
  # Task 20 also builds P3's room for rule 4 (spec R36, ledger H-03), so it writes the scenario "On a phone P3 gets room
  # while P1 is open over it, and loses it when P1 closes" with no mark, and it turns W22's two P3 rows "2026-07-20"
  # green. Added 2026-10-14 in execute (planner touch-up, ledger H-03).
  # Changed 2026-10-14 in execute (planner follow-up, owner ruling H-03 of 16:32 "Same fix for P4 (Recommended)").
  # The room belongs to P1's host, P3 or P4, so that scenario is now titled "On a phone the host of P1 gets room while
  # P1 is open over it, and loses it when P1 closes" (the title above is struck in its own comment). Task 20 also
  # writes "With twelve habits on a phone the chosen day's top meets the host's head" with no mark (ruled ORCH).

  @R36 @R42
  Scenario: A band day opens P1 (v1.1.0 new)
    Given the sample day at 1280 x 800
    When the user clicks the band's "Tue 22 Sep, 1 of 3 habits"
    Then dialog.dlg-day is open and matches ":modal", and the tick "Read 20 pages" has focus
    And div.day-mini with aria-hidden "true" holds a ring of three path.seg, only the third on, and no text, no circle.c-core and no circle.c-today
    And h2#day-title reads "Tuesday 22 September" and p#day-sub reads "1 of 3 habits"
    And ul.day-list holds three li, each with a button.tick of type "button", as follows
      | name                | aria-pressed | class "on" | aria-describedby | span.tstat                                        |
      | Read 20 pages       | false        | no         | ts-1             | span.tcur "Current 4 days", then span "Best 9"     |
      | Stretch 10 minutes  | false        | no         | ts-2             | span.tcur "Current 2 days", then span "Best 5"     |
      | No phone after 11pm | true         | yes        | ts-3             | span.tcur.none "No streak yet", then span "Best 14" |
    And each tick holds span.tbox with an svg using "#i-check", then span.tname with the habit's name, then span.tstat with the id named above
    And every button.hc with data-key "2026-09-22" in the document has the class "is-open", and no other button.hc has it

  @R36 @R40
  Scenario Outline: P1 closes and gives focus back to its day (v1.1.0 new)
    Given the sample day at 1280 x 800 with P1 open for 2026-09-22 from the band
    When the user <action>
    Then P1 is closed, no button.hc has the class "is-open", and focus is on the band's 2026-09-22 button

    Examples:
      | action                           |
      | clicks Close                     |
      | presses Escape                   |
      | clicks the viewport point (5, 5) |

  @R36
  Scenario: P1 lists the habits there are when it opens (v1.1.0 new)
    # Added 2026-10-15 in execute (planner touch after step 5, code review WR-05 (a), the QA re-check). P1's list is
    # built at each opening, so an add or a delete made while P1 is closed shows the next time it opens. The test came
    # with the step 5 solver round (commit 5b07fc4).
    Given the sample day at 1280 x 800
    When the user clicks the band's "Tue 22 Sep, 1 of 3 habits"
    Then P1's ticks are named "Read 20 pages", "Stretch 10 minutes" and "No phone after 11pm", in that order, and p#day-sub reads "1 of 3 habits"
    When the user presses Escape, adds "Drink water" and clicks the band's 2026-09-22 again
    Then P1's ticks are named "Read 20 pages", "Stretch 10 minutes", "No phone after 11pm" and "Drink water", in that order, and p#day-sub reads "1 of 4 habits"
    When the user presses Escape, deletes "Stretch 10 minutes" with its bin and confirm_delete, and clicks the band's 2026-09-22 again
    Then P1's ticks are named "Read 20 pages", "No phone after 11pm" and "Drink water", in that order, and p#day-sub reads "1 of 3 habits"

  @R36
  Scenario Outline: On a phone the chosen day stays in sight above P1 (v1.1.0 new)
    # The two P3 rows "2026-07-20" hold as written through P3's room for rule 4 (spec R36, owner ruling H-03,
    # 2026-10-14 16:05). test_day_editor.py carries them with the mark BLOCKED_B1 until task 20 changes it to
    # xfail(strict=True, reason="task 20") and removes it (W22). Added 2026-10-14 in execute (planner touch-up, H-03).
    # The P4 row "2025-10-10" holds as written through P4's room (spec R36, owner ruling H-03 of 16:32), built at task
    # 20 with P4, so it carries no mark. Added 2026-10-14 in execute (planner follow-up, H-03).
    Given the sample day at <viewport>
    When the user opens <host> and clicks its day button for <day>
    Then P1 is open as a sheet at the bottom of the viewport, over <host>
    And the host's button for <day> lies fully between the bottom of the host's div.sheet-head and the top of P1's div.dlg-box, and has the class "is-open"
    And the host's div.sheet-body has scrollTop <scroll>

    Examples:
      | viewport | host                         | day        | scroll                                    |
      | 390x844  | P3 (Overview)                | 2026-09-22 | 0, as the golden draws it                 |
      | 360x780  | P3 (Overview)                | 2026-09-22 | 0, as the golden draws it                 |
      | 390x844  | P3 (Overview)                | 2026-07-20 | above 0, so the host had to scroll        |
      | 360x780  | P3 (Overview)                | 2026-07-20 | above 0, so the host had to scroll        |
      | 390x844  | P4 (Overview, then Year)     | 2026-09-22 | any value                                 |
      | 390x844  | P4 (Overview, then Year)     | 2025-10-10 | above 0, so the host had to scroll        |

  @R36
  Scenario Outline: On a phone the host of P1 gets room while P1 is open over it, and loses it when P1 closes (v1.1.0 new, H-03 ruled)
    # Added 2026-10-14 in execute (planner touch-up, ledger H-03, owner ruling 2026-10-14 16:05 "Fix, give P3 room").
    # Written at task 20 into test_day_editor.py with no mark, as "A P4 day opens P1 over P4 on a desktop" is.
    # The 800x900 row checks that no room appears from 768 px, where P1 is a centred dialog and rule 4 does not apply.
    # Changed 2026-10-14 in execute (planner follow-up, owner ruling H-03 of 16:32 "Same fix for P4 (Recommended)").
    # The title first read ~~On a phone P3 gets room while P1 is open over it, and loses it when P1 closes~~ and every
    # step named P3. The steps now name the host, the two P4 rows are new, P3's check of scrollHeight before P1 opens is
    # dropped, and P3's checks of scrollHeight and scrollTop after P1 closes moved into the <after> column, because P4's
    # body scrolls on its own. Task 20 measures the P4 rows on its code before the room (spec R36) and keeps that RED.
    Given the sample day at <viewport> with <host> open
    Then the host's div.sheet-body has the computed padding-bottom "24px" and no inline padding-bottom
    When the user clicks the host's button for <day>
    Then P1 is open over the host, and the host's div.sheet-body has a computed padding-bottom <room>
    When the user <action>
    Then P1 is closed, the host is open, and focus is on the host's button for <day>
    And the host's div.sheet-body has the computed padding-bottom "24px" and no inline padding-bottom, and the host's button for <day> lies fully inside the visible part of that div.sheet-body
    And <after>

    Examples:
      | viewport | host                     | day        | action                           | room                                                                                                     | after |
      | 390x844  | P3 (Overview)            | 2026-07-20 | presses Escape                   | within 1 px of the height of dialog.dlg-day, which is the distance from P1's top edge to the viewport's bottom | P3's div.sheet-body has its scrollHeight equal to its clientHeight and scrollTop 0 |
      | 360x780  | P3 (Overview)            | 2026-07-20 | clicks Close                     | within 1 px of the height of dialog.dlg-day, which is the distance from P1's top edge to the viewport's bottom | P3's div.sheet-body has its scrollHeight equal to its clientHeight and scrollTop 0 |
      | 390x844  | P3 (Overview)            | 2026-09-22 | clicks the viewport point (5, 5) | within 1 px of the height of dialog.dlg-day, which is the distance from P1's top edge to the viewport's bottom | P3's div.sheet-body has its scrollHeight equal to its clientHeight and scrollTop 0 |
      | 800x900  | P3 (Overview)            | 2026-07-20 | presses Escape                   | of "24px", the stylesheet's, with no inline padding-bottom                                               | P3's div.sheet-body has its scrollHeight equal to its clientHeight and scrollTop 0 |
      | 390x844  | P4 (Overview, then Year) | 2025-10-10 | presses Escape                   | within 1 px of the height of dialog.dlg-day, and P3's div.sheet-body beneath P4 has no inline padding-bottom | P3 is still open beneath P4, and its div.sheet-body has no inline padding-bottom |
      | 360x780  | P4 (Overview, then Year) | 2025-10-10 | clicks Close                     | within 1 px of the height of dialog.dlg-day, and P3's div.sheet-body beneath P4 has no inline padding-bottom | P3 is still open beneath P4, and its div.sheet-body has no inline padding-bottom |

  @R36
  Scenario Outline: With twelve habits on a phone the chosen day's top meets the host's head (v1.1.0 new, ruled ORCH)
    # Added 2026-10-14 in execute (planner follow-up, ruled ORCH by the orchestrator on the planner touch-up's
    # contradiction 2, spec R36 "A gap smaller than a day"). Written at task 20 into test_day_editor.py with no mark.
    # Task 20 measures the gap first and keeps that run as RED. The precondition line below is checked, so a layout
    # where the whole day fits fails the precondition and never passes the row by accident.
    Given twelve habits at <viewport>
    When the user opens <host> and clicks its day button for <day>
    Then P1 is open as a sheet at the bottom of the viewport, over <host>
    And the distance from the bottom of the host's div.sheet-head to the top of P1's div.dlg-box is smaller than the height of the host's button for <day> (checked)
    And the top of the host's button for <day> lies within 1 px of the bottom of the host's div.sheet-head, the host's div.sheet-body has scrollTop above 0, and the button has the class "is-open"

    Examples:
      | viewport | host                     | day        |
      | 390x844  | P3 (Overview)            | 2026-07-20 |
      | 360x780  | P4 (Overview, then Year) | 2025-10-10 |

  @R36 @R39
  Scenario: A P4 day opens P1 over P4 on a desktop (v1.1.0 new)
    Given the sample day at 1280 x 800 with P4 open from the band's Year
    When the user clicks P4's "Tue 22 Sep 2026, 1 of 3 habits"
    Then P1 is open over P4 with the title "Tuesday 22 September", and P4 is still open
    And the band's and P4's 2026-09-22 buttons have the class "is-open"
    When the user presses Escape
    Then P1 is closed, P4 is open, and focus is on P4's 2026-09-22 button

  @R36 @R3
  Scenario: A day opens P1 when there are no habits (v1.1.0 new, CG-12 ruled)
    Given a fresh day at 1280 x 800
    When the user clicks the band's "Sat 10 Oct, 0 of 0 habits"
    Then P1 is open with h2#day-title "Saturday 10 October" and p#day-sub "0 of 0 habits"
    And div.day-mini's ring holds one circle.seg without "on" and nothing else
    And ul.day-list holds exactly one li.day-empty reading "No habits yet." and no button.tick
    And Close has focus

  @R37 @R32
  Scenario: Ticking a past day in P1 (v1.1.0 new)
    Given the sample day at 1280 x 800 with count_writes, P1 open for 2026-09-22 from the band, and a handle to the tick "Read 20 pages"
    When the user clicks that tick
    # Changed 2026-10-15 in execute (planner touch after step 5, code review WR-02). The next line gained "no other tick
    # has "pop"", because R32 says an element that did not change carries no class from the edit.
    Then the same handle is still connected, has aria-pressed "true" and the classes "on" and "pop", no other tick has "pop", and P1 is still open
    And its span.tstat reads "Current 4 days" and "Best 13"
    And p#day-sub reads "2 of 3 habits" and the mini ring has its first and third path.seg on
    And the band's 2026-09-22 is named "Tue 22 Sep, 2 of 3 habits" and keeps "is-open"
    And the Read row reads "Best 13", and exactly one write was made
    # Changed 2026-10-14 in execute (planner touch-up, Q3, ledger S1 row 8, ruled ORCH). The next line first ended
    # ~~In WebKit document.activeElement is body~~. Measured at task 18, a mouse click on a button inside an open popup
    # leaves focus on the popup's dialog element in WebKit (Engine differences by design).
    And in Chromium the tick has focus. In WebKit document.activeElement is dialog.dlg-day, not body

  @R37
  Scenario: Keyboard ticks keep focus, and a second tick restores the saved value (v1.1.0 new)
    Given the sample day at 1280 x 800, the stored text S, and P1 opened for 2026-09-22 by keyboard (Tab to the band's 2026-09-22, then Enter)
    When the user presses Tab (focus moves from "Read 20 pages" to "Stretch 10 minutes") and then Space
    Then "Stretch 10 minutes" has aria-pressed "true", is still document.activeElement, and p#day-sub reads "2 of 3 habits"
    When the user presses Enter
    Then it has aria-pressed "false", still has focus, p#day-sub reads "1 of 3 habits", and stored(page) parses to the same object as S

  @R37 @R31
  Scenario: Ticking today in P1 presses Done today (v1.1.0 new)
    Given the sample day at 1280 x 800 with P1 open for 2026-10-10 from the band
    When the user clicks the tick "Stretch 10 minutes"
    Then "Done today, Stretch 10 minutes" has aria-pressed "true" and its row reads "Current 3 days"
    And the band's 2026-10-10 is named "Sat 10 Oct, 2 of 3 habits"

Feature: A habit's year view
  # tests/browser/test_year.py (task 19)
  # W19 waits on a later task ("Scenarios that wait on a later task", added 2026-10-13 after the plan re-check, F12)

  @R33 @R6
  Scenario: Year opens the habit's year view (v1.1.0 new)
    Given the sample day at 390 x 844
    When the user clicks "Year view, Read 20 pages"
    Then dialog.dlg-year is open and matches ":modal", Close has focus, and its div.sheet-body has scrollTop 0
    And h2#yr-title reads "Read 20 pages" and p#yr-sub reads "The last 12 months"
    And div.yr-mid holds p.yr-stats with span.stat.cur (span.lbl "Current", span.val holding b.num "4" and span.unit "days") and span.stat.best (span.lbl "Best", span.val holding b.num "9"), then button.btn-del of type "button", without aria-haspopup, holding an svg using "#i-trash" and the text "Delete habit"
    And div.yr-tools holds p.hint "Tap a day to mark it done or not done." and p.yr-legend with aria-hidden "true" holding span.mini.on, span "Done", span.mini and span "Not done"
    And div.months holds 13 section.month, newest first, labelled by "mo-2026-10" to "mo-2025-10" (the month without a leading zero, for example "mo-2026-9"), whose h3 read "October 2026" to "October 2025"
    And each month's div.mgrid has role "group" and holds seven span.mwd, then its span.yc.lead cells, then one cell per day
    And the grids hold 366 button.yc of type "button" named from "Mark Fri 10 Oct 2025 as done" to "Mark Sat 10 Oct 2026 as done", 250 with aria-pressed "true" and the class "on", the other 116 with aria-pressed "false" and none of "on", "l" and "r"
    And each bead button holds span.bead with an svg holding one text element (x "50%", y "50%", dy ".352em") reading its day number
    And the bead classes match the golden. 127 have "on", "l" and "r", 56 have "on" and "l" only, 56 have "on" and "r" only, and 11 have "on" alone
    And only the 2026-10-10 bead has "today" and aria-current "date", and it has "on" and "l" and not "r"
    And the 2025-10-10 bead has "on" and "r" and not "l"
    And 21 span.yc.closed (11 to 31 October 2026) each hold span.bead with its number, 9 span.yc.blank (1 to 9 October 2025) and 39 span.yc.lead are empty, and every span cell has aria-hidden "true"

  @R33 @R40
  Scenario Outline: P2 closes and gives focus back to its Year (v1.1.0 new)
    Given the sample day at <viewport> with P2 open for Read
    When the user <action>
    Then P2 is closed and focus is on "Year view, Read 20 pages"

    Examples:
      | viewport | action                           |
      | 390x844  | clicks Close                     |
      | 390x844  | presses Escape                   |
      | 1280x800 | clicks Close                     |
      | 1280x800 | presses Escape                   |
      | 1280x800 | clicks the viewport point (5, 5) |

  @R33
  Scenario: P2 opens again at its top after it closed scrolled (v1.1.0 new)
    # Added 2026-10-15 in execute (planner touch after step 5, code review WR-04, the QA re-check). The test came with
    # the step 5 solver round (commit 5b07fc4).
    Given the sample day at 390 x 844 with P2 open for Read
    When the user turns the mouse wheel down by 900 pixels over P2's div.sheet-body
    Then its scrollTop is above 0
    When the user presses Escape, P2 closes, and the user clicks "Year view, Read 20 pages" again
    Then P2 is open and its div.sheet-body has scrollTop 0

  @R33
  Scenario Outline: P2 per width (v1.1.0 new)
    Given the sample day at <viewport> with P2 open for Read
    Then its div.dlg-box <box>
    And the sections "mo-2026-10", "mo-2026-9" and "mo-2026-8" lie <months>

    Examples:
      | viewport | box                                                         | months                                  |
      | 390x844  | covers the viewport (0, 0, 390, 844)                        | one under the other                     |
      | 1280x800 | is 980 pixels wide, centred, and at most 752 pixels tall    | side by side, their tops within 1 pixel |

  @R34 @R32
  Scenario: Ticking a day in the year view (v1.1.0 new)
    Given the sample day at 390 x 844 with count_writes, P2 open for "No phone after 11pm", and a handle to the bead 2026-10-09
    When the user clicks that bead
    Then the same handle is still connected, has aria-pressed "true" and the classes "on", "l" and "pop", and not "r"
    # Changed 2026-10-15 in execute (planner touch after step 5, code review WR-02). The next line gained "and no other
    # bead has "pop", 2026-10-08 included". A neighbour whose thread changed did not change its done state (R32, R34).
    And the bead 2026-10-08 has gained "r", and no other bead has "pop", 2026-10-08 included
    And p.yr-stats holds Current "8" "days" and Best "14"
    And exactly one write was made and the No phone row reads "Current 8 days"
    # Changed 2026-10-14 in execute (planner touch-up, Q3, ledger S1 row 8, ruled ORCH). The next line first ended
    # ~~In WebKit document.activeElement is body~~. Measured at task 18 and asserted so at task 19, a mouse click on a
    # button inside an open popup leaves focus on the popup's dialog element in WebKit (Engine differences by design).
    And in Chromium the bead has focus. In WebKit document.activeElement is dialog.dlg-year, not body

  @R34 @R16
  Scenario: Untick and tick again (v1.1.0 new)
    Given the sample day with P2 open for "Read 20 pages" and the stored text S
    When the user clicks the bead 2026-10-08
    Then it has aria-pressed "false" and none of "on", "l" and "r", the bead 2026-10-07 has lost "r", the bead 2026-10-09 has lost "l", and p.yr-stats holds Current "2" "days"
    When the user clicks it again
    Then the classes of the three beads are as before the first click and stored(page) parses to the same object as S

  @R34 @R10
  Scenario: A day before a habit was added can be ticked (v1.1.0 new)
    Given the sample day at 1280 x 800
    When the user adds "Drink water", clicks "Year view, Drink water" and clicks the bead 2026-03-15
    Then that bead has aria-pressed "true" and the class "on"
    And the last habit in stored(page) is {"name":"Drink water","done":["2026-03-15"]}
    And P2's stats read "Current" with "No streak yet" and "Best" "1"

  @R34
  Scenario: No control exists after today or before the year (v1.1.0 new)
    Given the sample day with P2 open for Read
    Then no button in the document has data-key "2026-10-11" or "2025-10-09"
    And the cell for 11 October 2026 is a span.yc.closed and the cell for 9 October 2025 is a span.yc.blank

  @R34 @R22
  Scenario: Beads are reached and ticked with the keyboard (v1.1.0 new)
    Given the sample day with nothing focused
    When the user presses Tab until "Year view, Stretch 10 minutes" has focus and presses Enter
    Then P2 is open for Stretch and Close has focus
    When the user presses Tab twice
    Then focus is on "Mark Thu 1 Oct 2026 as done", which has aria-pressed "true", after Delete habit
    When the user presses Space
    Then that bead has aria-pressed "false" and is still document.activeElement
```
```gherkin
Feature: Add a habit
  # tests/browser/test_add.py (task 21)
  # W20 waits on a later task ("Scenarios that wait on a later task", added 2026-10-13 after the plan re-check, F12)

  @R10 @R16 @R32
  Scenario: The first habit on a fresh day (v1.1.0 changed)
    Given a fresh day at 390 x 844
    When the user clicks the field, types "Read 20 pages" and clicks Add
    Then li.empty is gone and ul.rows holds one li.row with h3#rn-1 "Read 20 pages"
    And its p.stats holds span.stat.cur with "Current" and span.none "No streak yet" and no span.stat.best, and its Done today has aria-pressed "false"
    And the field's value is "", #nh-msg is hidden and empty with the class list "field-msg", and the field has no aria-invalid
    And the band's 2026-10-10 (in the DOM) is named "Sat 10 Oct, 0 of 1 habits" and its ring holds one circle.seg without "on"
    And the Overview button is named "Overview, today 0 of 1 habits done"
    And stored(page) is exactly '{"version":1,"habits":[{"name":"Read 20 pages","done":[]}]}'
    And in Chromium focus is on Add. In WebKit document.activeElement is body

  @R10 @R32
  Scenario: Enter adds at the bottom, trimmed, and the band recounts (v1.1.0 changed)
    Given the sample day at 1280 x 800
    When the user types "  Drink water  " into the field and presses Enter
    Then the fourth li.row has h3#rn-4 "Drink water"
    And the band's 2026-07-21 is named "Tue 21 Jul, 3 of 4 habits" and its ring holds four path.seg with the d attributes arcPath(0, 4) to arcPath(3, 4), three of them on, and no circle.c-core
    And the band's 2026-10-10 is named "Sat 10 Oct, 1 of 4 habits"
    # Added 2026-10-15 in execute (planner touch after step 5, code review WR-03). The legend is drawn again when the
    # number of habits changes (R42, R32), and no line read it after an add.
    And the band's legend holds "None", four rings with 0, 2, 3 and 4 of their four path.seg on (the d attributes arcPath(0, 4) to arcPath(3, 4), the last ring with circle.c-core), and "All"
    And the last habit in stored(page) is {"name":"Drink water","done":[]}
    And the field is still document.activeElement

  @R10
  Scenario: The frame scrolls to show the new row (v1.1.0 new, CG-15 ruled)
    Given 6 plain habits at 390 x 844 with div.frame scrolled to its top
    When the user types "Habit 7" into the field and presses Enter
    Then div.frame's scrollHeight is greater than its clientHeight and its scrollTop is above 0, so a scroll was needed
    And the bounding box of the seventh li.row lies fully inside the visible box of div.frame
    And the field is still document.activeElement

  @R11
  Scenario Outline: Rejected names keep the text and show one message above the field (v1.1.0 changed)
    # Changed 2026-10-15 in execute (planner touch after step 5, code review WR-01 (b)). The Given gained "with
    # count_writes" and the last line "and no write was made". A save of the same habits writes the same text, so only
    # the count shows that a refused name saved nothing (R16).
    Given the sample day at <viewport> with count_writes, the stored text S and the field's top position P
    When the user types "<typed>" into the field and clicks Add
    Then #nh-msg is shown with the class list "field-msg err" and reads "<message>"
    And the bottom of #nh-msg is at or above the top of the field, and the field's top is still P
    And the field has aria-invalid "true", its value is still "<typed>", and it is document.activeElement in both engines
    And there are still 3 li.row, stored(page) equals S, and no write was made

    Examples:
      | viewport | typed                                               | message                            |
      | 390x844  |                                                     | Name the habit first.              |
      | 390x844  |                                                     | Name the habit first.              |
      | 390x844  | Walk to the end of the street and back after dinner | Keep it to 40 characters or fewer. |
      | 390x844  | Read twenty pages before bed every night.           | Keep it to 40 characters or fewer. |
      | 390x844  | read 20 pages                                       | You already track this habit.      |
      | 390x844  |  STRETCH 10 MINUTES                                 | You already track this habit.      |
      | 1280x800 |                                                     | Name the habit first.              |
    # Row 2 types three spaces. Row 6 types " STRETCH 10 MINUTES " with a leading and a trailing space.

  @R11
  Scenario: Exactly 40 characters is accepted (v1.1.0 changed)
    Given the sample day
    When the user types "Read twenty pages before bed every night" and clicks Add
    Then a fourth li.row has that name, and #nh-msg is hidden and empty

  @R11
  Scenario: No message while typing (v1.1.0 changed)
    Given the sample day
    When the user types "Walk to the end of the street and back after dinner" without submitting
    Then #nh-msg is hidden and empty and the field has no aria-invalid

  @R11
  Scenario: Typing clears a message at once (v1.1.0 new)
    Given the sample day
    When the user clicks Add with the field empty
    Then #nh-msg reads "Name the habit first." and the field has aria-invalid "true"
    When the user types "D"
    Then #nh-msg is hidden and empty with the class list "field-msg", the field has no aria-invalid, and its value is "D"

  @R11
  Scenario: One message at a time, replaced, then cleared on success (v1.1.0 changed)
    Given the sample day
    When the user clicks Add with the field empty
    Then #nh-msg reads "Name the habit first."
    When the user types "read 20 pages"
    Then #nh-msg is hidden and empty
    When the user presses Enter
    Then #nh-msg reads only "You already track this habit."
    When the user clears the field, types "Drink water" and presses Enter
    Then #nh-msg is hidden and empty, the field has no aria-invalid, and there are 4 li.row

  @R12
  Scenario: The twelfth habit closes the composer (v1.1.0 changed)
    Given 11 plain habits
    When the user types "Habit 12" and clicks Add
    Then there are 12 li.row, each with its bin, and form.composer has the class "is-full"
    And the field and Add have the disabled attribute
    And #nh-msg is shown with the class list "field-msg note" and reads "You track 12 habits, the most this app holds. Delete one to add another."
    And the field has aria-describedby "nh-msg" and no aria-invalid
    And document.activeElement is neither the field nor any control in ul.rows (the app moved no focus)

  @R12
  Scenario: A render at twelve habits does not write the note again (v1.1.0 new)
    # Added 2026-10-15 in execute (planner touch after step 5, code review WR-05 (b), the QA re-check, spec R12's note
    # of 2026-10-15). The test came with the step 5 solver round (commit 5b07fc4).
    Given twelve habits, #nh-msg holding the 12-habit note, and mutation_log on #nh-msg
    When the user clicks the first row's Done today
    Then its aria-pressed has flipped
    And #nh-msg saw no child added or removed, and still holds the 12-habit note

  @R12
  Scenario Outline: Twelve habits at load (v1.1.0 changed)
    Given twelve habits at <viewport>
    Then form.composer has the class "is-full", the field and Add are disabled, and #nh-msg holds the 12-habit note with the class list "field-msg note"

    Examples:
      | viewport |
      | 390x844  |
      | 1280x800 |

  @R12 @R15
  Scenario: Deleting one of twelve opens the composer again (v1.1.0 changed)
    Given twelve habits
    When the user clicks 'Delete "Floss"' and confirm_delete
    Then there are 11 li.row, form.composer has no "is-full", the field and Add are enabled, and #nh-msg is hidden and empty with the class list "field-msg"

Feature: Delete a habit
  # tests/browser/test_delete.py (task 22)

  @R13
  Scenario: A bin opens M1 with focus on Cancel (v1.1.0 changed)
    Given the sample day
    When the user clicks 'Delete "Read 20 pages"'
    Then dialog.dlg-del is open and matches ":modal"
    And #del-title reads dialog_title("Read 20 pages") and #del-body reads "Its history is deleted too."
    And its buttons are "Cancel" and then "Delete habit", both of type "button"
    And document.activeElement is Cancel in both engines
    And the computed overflow of html is "hidden", and after the mouse wheel turns down by 800 pixels window.scrollY is 0

  @R13 @R33
  Scenario: Delete habit in the year view opens M1 over it (v1.1.0 new)
    Given the sample day with P2 open for Read
    When the user clicks P2's Delete habit
    Then M1 is open over P2, both match ":modal", #del-title reads dialog_title("Read 20 pages"), and Cancel has focus

  @R13
  Scenario: A long name wraps in the title and the box keeps its width (v1.1.0 changed)
    Given the clock is fixed at 2026-10-10T12:00:00+08:00, the viewport is 390 x 844, and storage holds one habit "Read twenty pages before bed every night" with no done days
    When the user clicks its bin
    Then dialog.dlg-del is 358 pixels wide and #del-title spans more than one 26 pixel line

  # The time-free guard (spec R13, CG-10 ruled 2026-10-13, ledger S3 row 2). When M1 opens the app records the box of the control
  # that opened it. Delete habit ignores a mouse or touch activation (detail above 0) whose point lies inside that box,
  # or whose detail is above 1. A keyboard activation (detail 0) always acts. Nothing depends on time. The overlap
  # point is found by measuring, and each scenario checks that the bin lies under it before M1 opens and Delete habit
  # after, so a layout change can fail the precondition but never pass the scenario because nothing is there.

  @R13
  Scenario Outline: A slow double click on a bin that lies under Delete habit cannot delete (v1.1.0 new, CG-10 ruled)
    Given <state> at <viewport> with <input> input and the clock installed and paused
    And the point where a row's bin and M1's Delete habit overlap, found by opening M1 from each row's bin once and closing it with Escape (the test fails when no row overlaps, and writes the measured boxes to the evidence)
    When the user presses that point once (M1 opens for that row), the clock runs 2000 ms, and the user presses the same point again
    Then M1 is still open for that habit, every row is still listed, nothing was written, and stored(page) equals the text before
    When the user presses Escape
    Then M1 is closed and focus is on that row's bin

    Examples:
      | state          | viewport | input |
      | the sample day | 1280x800 | mouse |
      | the sample day | 1280x800 | touch |
      | twelve habits  | 390x844  | mouse |
      | twelve habits  | 390x844  | touch |

  @R13
  Scenario Outline: A fast double click or double tap on a bin under Delete habit cannot delete (v1.1.0 changed, CG-10 ruled)
    Given <state> at <viewport> with <input> input, the clock installed and paused, and the overlap point found as above
    When the user presses that point twice at the same instant (press_twice)
    Then M1 is still open for that habit, every row is still listed, nothing was written, and stored(page) equals the text before
    And the detail of each click that reached Delete habit, read by a test-side capture listener, is written to the evidence (information for task 11's tap probe)
    When the user presses Escape
    Then M1 is closed and focus is on that row's bin

    Examples:
      | state          | viewport | input |
      | the sample day | 1280x800 | mouse |
      | the sample day | 1280x800 | touch |
      | twelve habits  | 390x844  | mouse |
      | twelve habits  | 390x844  | touch |

  @R13
  Scenario: A press with a click count of 2 on Delete habit, away from the bin, does nothing (v1.1.0 new, CG-10 ruled)
    Given the sample day at 390 x 844, the clock installed and paused, and M1 open from 'Delete "Stretch 10 minutes"'
    And a point of Delete habit outside the bin's box (checked)
    When the user moves the mouse to that point and presses and releases the button with a click count of 2 (one click event whose detail is 2)
    Then M1 is still open, 3 rows are listed, nothing was written, and stored(page) equals the text before

  @R13 @R15
  Scenario Outline: One press on Delete habit away from the bin deletes at once (v1.1.0 changed, CG-10 ruled)
    Given the sample day at <viewport> with <input> input, count_writes, and the clock installed and paused
    When the user presses 'Delete "Stretch 10 minutes"' and, at the same instant, presses Delete habit at a point outside the bin's box (checked)
    Then M1 is closed, the rows are "Read 20 pages" and "No phone after 11pm", and exactly one write was made

    Examples:
      | viewport | input |
      | 390x844  | mouse |
      | 390x844  | touch |
      | 1280x800 | mouse |

  @R13 @R15
  Scenario: Enter on Delete habit deletes at once (v1.1.0 changed, CG-10 ruled)
    Given the sample day with count_writes, the clock installed and paused, and 'Delete "Stretch 10 minutes"' focused by Tab
    When the user presses Enter (M1 opens with focus on Cancel), Tab (focus moves to Delete habit) and Enter, at the same instant
    Then M1 is closed, the rows are "Read 20 pages" and "No phone after 11pm", exactly one write was made, and focus is on 'Delete "No phone after 11pm"'

  @R13 @R15
  Scenario: The keyboard deletes even when Delete habit lies over the bin (v1.1.0 new, CG-10 ruled)
    Given the sample day at 1280 x 800, the clock installed and paused, and the row whose bin lies under M1's Delete habit, found as above
    When the user presses Tab until that bin has focus, then presses Enter, Tab and Enter
    Then that habit is gone and 2 rows remain

  # Keep (spec R14).

  @R14
  Scenario Outline: Cancel, Esc and a backdrop click keep the habit and give focus back (v1.1.0 changed)
    Given the sample day at <viewport> and the stored text S
    When the user opens M1 from <opener> and then <action>
    Then M1 is closed, 3 rows are listed, Stretch reads "Current 2 days" and "Best 5", stored(page) equals S, and focus is on <opener>
    And <others>

    Examples:
      | viewport | opener                                           | action                               | others                  |
      | 390x844  | 'Delete "Stretch 10 minutes"'                    | clicks Cancel                        | no other dialog is open |
      | 390x844  | 'Delete "Stretch 10 minutes"'                    | presses Escape                       | no other dialog is open |
      | 390x844  | 'Delete "Stretch 10 minutes"'                    | clicks the viewport point (5, 5)     | no other dialog is open |
      | 1280x800 | P2's Delete habit, with P2 open for Stretch      | clicks Cancel                        | P2 is still open        |
      | 1280x800 | P2's Delete habit, with P2 open for Stretch      | presses Escape                       | P2 is still open        |
      | 1280x800 | P2's Delete habit, with P2 open for Stretch      | clicks the viewport point (5, 5)     | P2 is still open        |

  @R14
  Scenario: Esc after an earlier delete still keeps the habit (v1.1.0 changed)
    # Added 2026-10-15 in execute (planner touch after step 5, task 22's qa note, ledger S3 row 3). This scenario guards
    # 1.0's defect where M1 kept the returnValue of a delete, so a later Esc deleted again. That defect does not
    # reproduce in Chromium 149, so its RED at task 22 came from the same defect planted in app state, a confirm flag
    # never reset (BUILD.md task 22, RED first, run G). The steps are unchanged.
    Given the sample day
    When the user deletes "No phone after 11pm" with its bin and confirm_delete
    And then opens M1 from 'Delete "Stretch 10 minutes"' and presses Escape
    Then "Stretch 10 minutes" is still listed

  @R14
  Scenario Outline: Cancel, Esc and a backdrop click work at the instant of opening (v1.1.0 changed)
    Given the sample day and the clock installed and paused
    When the user clicks 'Delete "Stretch 10 minutes"' and at the same instant <action>
    Then M1 is closed, 3 rows are listed, focus is on 'Delete "Stretch 10 minutes"', nothing was written, and stored(page) equals the text before

    Examples:
      | action                           |
      | clicks Cancel                    |
      | presses Escape                   |
      | clicks the viewport point (5, 5) |

  @R14
  Scenario: Cancel still works right after a click inside the box (v1.1.0 changed)
    Given the sample day, the clock installed and paused, and M1 open from 'Delete "Read 20 pages"'
    When the user clicks inside div.dlg-box 6 pixels right of and below its top-left corner (M1 stays open) and at the same instant clicks Cancel
    Then M1 is closed

  # The tap-through guard (spec R14, CG-11 ruled 2026-10-13, ledger S3 row 2). For 500 ms after a mouse or touch click inside any
  # popup (detail above 0, its backdrop included), measured in event.timeStamp, a click on the page or on a popup that
  # was already open beneath it is cancelled. Clicks inside that same popup, and in popups opened after it, are never
  # held. Closing with the keyboard starts no window. The control behind is checked to lie under the press point.

  @R14
  Scenario Outline: A double press on a backdrop does not reach the control behind it (v1.1.0 changed, CG-11 ruled)
    Given the sample day at <viewport> with <input> input, the clock installed and paused, and <popups> open
    And the centre of <behind> lies outside the top popup's box (checked)
    When the user presses that point twice at the same instant (press_twice)
    Then the top popup is closed, <behind> lies under that point (checked), <result>, and stored(page) equals the text before

    Examples:
      | viewport | input | popups                                 | behind                                        | result                                   |
      | 390x844  | mouse | M1, from 'Delete "Read 20 pages"'      | "Done today, Stretch 10 minutes"              | it still has aria-pressed "false"        |
      | 390x844  | touch | M1, from 'Delete "Read 20 pages"'      | "Done today, Stretch 10 minutes"              | it still has aria-pressed "false"        |
      | 1280x800 | mouse | M1, from 'Delete "Read 20 pages"'      | the band's "Mon 20 Jul, 2 of 3 habits"        | no P1 is open                            |
      | 1280x800 | touch | M1, from 'Delete "Read 20 pages"'      | the band's "Mon 20 Jul, 2 of 3 habits"        | no P1 is open                            |
      | 1280x800 | mouse | P1 for 2026-09-22, from the band       | the band's "Mon 20 Jul, 2 of 3 habits"        | no P1 is open                            |
      | 390x844  | mouse | P3, then P1 for 2026-09-22             | P3's "Mon 5 Oct, 3 of 3 habits"               | P3 is open and no P1 is open             |
      | 390x844  | touch | P3, then P1 for 2026-09-22             | P3's "Mon 5 Oct, 3 of 3 habits"               | P3 is open and no P1 is open             |
      | 1280x800 | mouse | P2 for Read, then M1 from its Delete habit | P2's backdrop at the point (5, 5), outside both boxes | P2 is still open                  |
    # Row 8 added 2026-10-15 in execute (planner touch after step 5, code review WR-07, the QA re-check), the test id
    # [1280x800-mouse-P2-then-M1]. It presses the point (5, 5), not a centre. The first press closes M1 from its
    # backdrop, and the second lands on P2's dialog element, which is P2's backdrop. P2 lay beneath M1, so that press is
    # held and P2 stays open (R14).

  @R14
  Scenario Outline: A double press on Close does not reach the control behind it (v1.1.0 new, CG-11 ruled)
    Given the sample day at <viewport> with <input> input, the clock installed and paused, and <popups> open
    When the user presses the centre of the top popup's Close twice at the same instant (press_twice)
    Then the top popup is closed, <behind> lies under that point (checked), and <result>

    Examples:
      | viewport | input | popups                            | behind                          | result                            |
      | 390x844  | mouse | P2 for Read                       | the Overview button             | P3 is not open                    |
      | 390x844  | touch | P2 for Read                       | the Overview button             | P3 is not open                    |
      | 390x844  | mouse | P3                                | the Overview button             | P3 is not open                    |
      | 390x844  | mouse | P3, then P4 from its Year         | P3's Close                      | P3 is still open                  |
      | 1280x800 | mouse | P1 for 2026-09-22, from the band  | a band day button               | no P1 is open                     |

  @R14 @R10
  Scenario Outline: A double press on the backdrop over Add does not add a typed name (v1.1.0 changed, CG-11 ruled)
    Given the sample day at 390 x 844 with <input> input, the clock installed and paused, "Drink water" typed in the field, and M1 open from 'Delete "Read 20 pages"'
    And the centre of Add lies outside M1's box (checked)
    When the user presses that point twice at the same instant (press_twice)
    Then M1 is closed, Add lies under that point (checked), the field still holds "Drink water", 3 rows are listed, and nothing was written

    Examples:
      | input |
      | mouse |
      | touch |

  @R14 @R15
  Scenario: A double click on Delete habit deletes once and nothing behind acts (v1.1.0 changed, CG-11 ruled)
    Given twelve habits at 390 x 844 with count_writes, mouse input, the clock installed and paused, the Done today state of every habit, and M1 open from 'Delete "Journal one page"'
    And a point of Delete habit outside the bin's box (checked)
    When the user double clicks that point (mouse.dblclick)
    Then M1 is closed, "Journal one page" is gone, 11 rows are listed and exactly one write was made
    And a Done today button lies under that point (checked), and its aria-pressed equals that habit's state before
    And stored(page) equals the text before with only "Journal one page" taken out

  @R14
  Scenario Outline: The layer behind listens again once the window has passed (v1.1.0 changed, CG-11 ruled)
    Given the sample day at 390 x 844 with <input> input, the clock installed and paused, and P2 for Read closed by a press on its Close
    When 499 ms pass and the user presses the Overview button
    Then P3 is not open
    When 1 ms more passes and the user presses it again
    Then P3 is open

    Examples:
      | input |
      | mouse |
      | touch |

  @R14
  Scenario Outline: Closing with the keyboard holds nothing (v1.1.0 changed, CG-11 ruled)
    Given the sample day, the clock installed and paused, and M1 open from a click on 'Delete "Read 20 pages"'
    When the user presses <key>
    Then M1 is closed and focus is on 'Delete "Read 20 pages"'
    When the user clicks "Done today, Stretch 10 minutes" at the same instant
    Then its aria-pressed is "true"

    Examples:
      | key    |
      | Enter  |
      | Space  |
      | Escape |
    # Enter and Space act on Cancel, which has focus.

  @R14
  Scenario: Clicks inside the same popup, or in a popup opened after it, are never held (v1.1.0 new, CG-11 ruled)
    Given the sample day at 390 x 844, the clock installed and paused
    When the user clicks "Year view, Read 20 pages", and at the same instant clicks the beads 2026-10-06 and 2026-10-03
    Then both beads have aria-pressed "true"
    When at the same instant the user clicks P2's Delete habit and then M1's Cancel
    Then M1 is closed and P2 is open
    When at the same instant the user clicks the bead 2026-10-02
    Then it still has aria-pressed "true", because P2 lay beneath M1 when Cancel was clicked
    When 500 ms pass and the user clicks it again
    Then it has aria-pressed "false"

  # Delete (spec R15).

  @R15 @R32
  Scenario: Deleting from a bin moves focus to the next bin and recounts (v1.1.0 changed)
    Given the sample day at 1280 x 800
    When the user clicks 'Delete "Stretch 10 minutes"' and confirm_delete
    Then M1 is closed and 2 li.row remain, "Read 20 pages" (rn-1) and "No phone after 11pm" (rn-2)
    And focus is on 'Delete "No phone after 11pm"'
    And the band's 2026-07-21 is named "Tue 21 Jul, 2 of 2 habits" and holds circle.c-core, and the band's 2026-10-10 is named "Sat 10 Oct, 1 of 2 habits"
    # Added 2026-10-15 in execute (planner touch after step 5, code review WR-03). The legend is drawn again when the
    # number of habits changes (R42, R32), and no line read it after a delete.
    And the band's legend holds "None", three rings with 0, 1 and 2 of their two path.seg on (the d attributes arcPath(0, 2) and arcPath(1, 2), the last ring with circle.c-core), and "All"
    And stored(page) holds the two remaining sample habits, unchanged, in order

  @R15
  Scenario: Deleting the last row moves focus to the bin above (v1.1.0 changed)
    Given the sample day
    When the user clicks 'Delete "No phone after 11pm"' and confirm_delete
    Then 2 rows remain and focus is on 'Delete "Stretch 10 minutes"'
    And the band's 2026-10-10 is named "Sat 10 Oct, 1 of 2 habits"

  @R15 @R3
  Scenario: Deleting the only habit shows the empty list (v1.1.0 changed)
    Given a fresh day
    When the user adds "Read 20 pages", clicks its Done today, then deletes it with its bin and confirm_delete
    Then ul.rows holds li.empty and no li.row, and focus is on the field
    And the band's 2026-10-10 is named "Sat 10 Oct, 0 of 0 habits" and its ring holds one circle.seg without "on"
    # Added 2026-10-15 in execute (planner touch after step 5, code review WR-03).
    And the band's legend holds span "None", one svg holding one circle.seg and nothing else, and span "All"
    And stored(page) is exactly '{"version":1,"habits":[]}'

  @R15 @R33
  Scenario Outline: Deleting from the year view closes both popups and moves focus (v1.1.0 new, CG-18 ruled)
    Given <state> at 390 x 844
    When the user clicks "Year view, <habit>", then P2's Delete habit, then confirm_delete
    Then no dialog is open, "<habit>" is no longer listed, and focus is on <focus>

    Examples:
      | state                                                                                  | habit               | focus                                                       |
      | the sample day                                                                         | Read 20 pages       | "Year view, Stretch 10 minutes", the row now at its place   |
      | the sample day                                                                         | No phone after 11pm | "Year view, Stretch 10 minutes", the row above (CG-18)      |
      | the clock fixed at 2026-10-10T12:00:00+08:00 and storage {"version":1,"habits":[{"name":"Read","done":[]}]} | Read                | the field                                                   |

  @R15
  Scenario: History goes with the habit (v1.1.0 changed)
    Given the sample day
    When the user deletes "Stretch 10 minutes" with its bin and confirm_delete, and then adds "Stretch 10 minutes"
    Then the new last row reads "Current" with "No streak yet" and no Best, and its Done today has aria-pressed "false"
    When the user clicks "Year view, Stretch 10 minutes"
    Then no bead in P2 has the class "on"

  @R15
  Scenario: A focused row out of sight is scrolled into view (v1.1.0 new)
    Given twelve habits at 390 x 844
    When the user presses Tab until 'Delete "Read 20 pages"' has focus, turns the mouse wheel down by 3000 pixels over div.frame (focus stays on that bin, now out of sight), and presses Enter, Tab and Enter
    Then "Read 20 pages" is gone, focus is on 'Delete "Stretch 10 minutes"', and that bin's bounding box lies fully inside the visible box of div.frame

  # The title's name (SEC-02 and SEC-06 of 1.0, spec R13). Wherever a scenario says the title reads dialog_title(name),
  # the text is 'Delete "', U+2068, the name as shown, U+2069, '"?'. The two marks are invisible.

  @R13
  Scenario Outline: The title shows the name without bidi format characters, and its quotes stay in place (v1.1.0 changed)
    Given a fresh day and storage holding one habit named <stored>
    When the user clicks its bin
    Then #del-title has one text node, no child element, and the text 'Delete "', U+2068, <shown>, U+2069, '"?'
    And, measured by the position of each character, the opening quote lies left of every visible character of the name, the closing quote lies right of all of them, and the question mark lies right of the closing quote

    Examples:
      | stored                                          | shown                                |
      | U+202E then "Reversed text here"                | "Reversed text here"                 |
      | "Read 20 pages", U+202E, " dleiys .gnp"         | "Read 20 pages dleiys .gnp"          |
      | "a", U+202E, "b", U+202E, "c", U+202E           | "abc"                                |
      | U+202B then "abc def"                           | "abc def"                            |
      | U+2067 then "abc def"                           | "abc def"                            |
      | U+05D0, U+2066, "abc" (SEC-06)                  | U+05D0, "abc"                        |
      | U+05D0, U+2068, "abc" (SEC-06)                  | U+05D0, "abc"                        |
      | a Hebrew word, U+2066 (SEC-06)                  | the Hebrew word                      |
      | a Hebrew word, " abc", U+2066 (SEC-06)          | the Hebrew word, " abc"              |
      | U+0645, U+2066, "x" (SEC-06)                    | U+0645, "x"                          |
      | "x", U+2069, U+202E, "y z" (residual (b))       | "xy z"                               |
      | "x", U+2029, U+202E, "y z" (residual (b))       | "xy z"                               |
      | U+05D0, U+2066, "abc", U+2069 (a matched pair)  | U+05D0, "abc"                        |
      | "Read 20 pages"                                 | "Read 20 pages"                      |
      | a Hebrew word, " ", another Hebrew word         | the same                             |
      | U+05D0                                          | U+05D0                               |

  @R13
  Scenario: Every character of the stripped set is left out of the title
    Given storage holding one habit named "x", then each of U+202A to U+202E, U+2066 to U+2069, U+0085, U+001C to U+001E and U+2029 (14 characters) with an "x" after each
    When the user clicks its bin
    Then the text of #del-title is 'Delete "', U+2068, fifteen times "x", U+2069, '"?'

  @R13
  Scenario: The neighbours of the stripped ranges and other invisible characters stay in the title
    Given storage holding one habit named "x", then each of U+0084, U+0086, U+001B, U+001F, U+2028, U+202F, U+2065, U+206A, U+200E, U+200F, U+061C, U+200B, U+200C, U+200D, U+2060 and U+FEFF with an "x" after each
    When the user clicks its bin
    Then the text of #del-title is 'Delete "', U+2068, the stored name unchanged, U+2069, '"?'

  @R13 @R15
  Scenario: Only the title's copy loses the characters, and the habit named in it is the one deleted (v1.1.0 changed)
    Given storage holding two habits, U+05D0 U+2066 "abc" and "Other habit", with count_writes
    When the user clicks the first bin
    Then the text of #del-title is 'Delete "', U+2068, U+05D0, "abc", U+2069, '"?'
    And the h3 texts are the stored name and "Other habit", and the first bin's aria-label is 'Delete "' followed by the stored name and '"'
    And storage is byte for byte what was seeded and no write was made
    When the user presses Tab and Enter (Delete habit, by keyboard)
    Then one habit remains, "Other habit", in the list and in storage
```
```gherkin
Feature: Kept on the device
  # tests/browser/test_storage.py (task 23). The storage unit scenarios are in tests/storage.test.js (task 14)

  @R16 @R41
  Scenario: saveHabits reports whether the write worked, and loadHabits whether the read did (v1.1.0 new)
    # Node, with a stand-in global localStorage per case. Each case restores the global afterwards
    Given a stand-in localStorage whose setItem stores the value
    Then saveHabits(habits) returns true and the stand-in holds encodeState(habits)
    Given a stand-in whose setItem throws an object that is not an Error
    Then saveHabits returns false and does not throw
    Given a global localStorage whose getter throws
    Then saveHabits returns false and loadHabits returns { habits: [], reset: false, saveFailed: true }
    Given a stand-in whose getItem returns null
    Then loadHabits returns { habits: [], reset: false, saveFailed: false } and setItem was not called
    Given a stand-in whose getItem returns "{" and whose setItem throws
    Then loadHabits returns { habits: [], reset: true, saveFailed: true }
    Given a stand-in whose getItem returns "{" and whose setItem stores the value
    Then loadHabits returns { habits: [], reset: true, saveFailed: false } and the stand-in holds '{"version":1,"habits":[]}'
    Given a stand-in whose getItem returns the encoded sample
    Then loadHabits returns the sample habits, reset false and saveFailed false, and setItem was not called

  @R16 @R32
  Scenario: Changes survive a reload and a closed tab (v1.1.0 changed)
    Given the sample day at 1280 x 800
    When the user clicks "Done today, Stretch 10 minutes", ticks Read in P1 for 2026-09-22 from the band and closes P1, ticks the bead 2026-10-09 in No phone's P2 and closes P2, and adds "Drink water"
    And the page reloads
    Then the rows are "Read 20 pages" (Current 4 days, Best 13), "Stretch 10 minutes" (Current 3 days, Best 5, Done today pressed), "No phone after 11pm" (Current 8 days, Best 14) and "Drink water" (No streak yet, no Best)
    And stored(page) is exactly encode of the three sample habits with "2026-09-22" added to Read's done list, "2026-10-10" to Stretch's and "2026-10-09" to No phone's, each list in ascending order, followed by {"name":"Drink water","done":[]}
    When the user deletes "Drink water" with its bin and confirm_delete, and the page reloads
    Then the three rows read as above and stored(page) holds no "Drink water"
    When the page is closed and a new page in the same context opens the app
    Then the same three rows and numbers show

  @R16
  Scenario: Loading writes nothing (v1.1.0 changed)
    Given storage holds the sample as pretty-printed JSON (indented, with line breaks), the clock is fixed at 2026-10-10T12:00:00+08:00, and count_writes
    When the page opens and 2 seconds pass
    Then stored(page) is still the identical pretty-printed text and no write was made
    And the three rows show the sample's numbers

  @R17
  Scenario Outline: Unreadable saved data resets the list and shows the note (v1.1.0 changed)
    Given the clock is fixed at 2026-10-10T12:00:00+08:00, the viewport is 1280 x 800, and storage holds <raw>
    When the page opens
    Then div.banners holds exactly one child, div.banner.note with role "status", holding p "Your saved habits could not be read, so the list was reset." and button.icon-btn of type "button" named "Dismiss note" holding an svg using "#i-x"
    And ul.rows holds li.empty and no li.row
    And the band's 2026-10-10 is named "Sat 10 Oct, 0 of 0 habits"
    And stored(page) is exactly '{"version":1,"habits":[]}'

    Examples:
      | case                      | raw                                                                              |
      | not JSON                  | {                                                                                |
      | JSON null                 | null                                                                             |
      | an array                  | []                                                                               |
      | wrong version             | {"version":2,"habits":[]}                                                        |
      | version as text           | {"version":"1","habits":[]}                                                      |
      | no habits array           | {"version":1,"habits":{}}                                                        |
      | 13 habits                 | {"version":1,"habits":[13 habits named "H1" to "H13", each with done []]}         |
      | empty name                | {"version":1,"habits":[{"name":"","done":[]}]}                                   |
      | untrimmed name            | {"version":1,"habits":[{"name":" Read","done":[]}]}                              |
      | 41 characters             | {"version":1,"habits":[{"name":"Read twenty pages before bed every night.","done":[]}]} |
      | duplicate ignoring case   | {"version":1,"habits":[{"name":"Read","done":[]},{"name":"read","done":[]}]}     |
      | name not text             | {"version":1,"habits":[{"name":5,"done":[]}]}                                    |
      | done not a list           | {"version":1,"habits":[{"name":"Read","done":"2026-10-08"}]}                     |
      | impossible date           | {"version":1,"habits":[{"name":"Read","done":["2026-02-30"]}]}                   |
      | date with a time          | {"version":1,"habits":[{"name":"Read","done":["2026-10-08T00:00"]}]}             |
      | habit is null             | {"version":1,"habits":[null]}                                                    |

  @R17
  Scenario Outline: Readable edge cases load without a note (v1.1.0 changed)
    Given the clock is fixed at 2026-10-10T12:00:00+08:00 and storage holds <raw>
    When the page opens
    Then div.banners has no child and <result>

    Examples:
      | raw                                                                                                   | result                                                                                                              |
      | {"version":1,"habits":[]}                                                                             | li.empty is shown                                                                                                   |
      | {"version":1,"habits":[{"name":"Read","done":["2026-10-10"],"color":"red"}],"theme":"dark"}           | one row "Read" with Done today pressed, and after the user clicks that Done today, stored(page) contains neither "color" nor "theme" |
      | {"version":1,"habits":[{"name":"Read","done":["2026-10-10","2026-10-09","2026-10-10"]}]}              | the row reads "Current 2 days" and "Best 2"                                                                         |
      | {"version":1,"habits":[{"name":"Read","done":["2026-10-11"]}]}                                        | no button has data-key "2026-10-11", and the row reads "No streak yet" and "Best 1"                                  |
      | {"version":1,"habits":[{"name":"Read","done":[],"__proto__":{"polluted":true}}]}                      | one row "Read", and evaluating ({}).polluted in the page gives undefined                                            |

  @R17 @R22
  Scenario: Dismiss removes the note, moves focus to the field, and the note does not come back (v1.1.0 changed)
    # Changed 2026-10-15 in execute (planner touch after step 5, code review WR-01 (b)). The Given gained "and
    # count_writes" and the first Then "and no write was made after the reset save". The reset save of R17 is the one
    # save at load, and Dismiss saves nothing (R16).
    Given the clock is fixed at 2026-10-10T12:00:00+08:00, storage holds "{", and count_writes
    When the user clicks "Dismiss note"
    Then there is no div.banner.note, li.empty is still shown, the field is document.activeElement in both engines, and no write was made after the reset save
    When the page reloads
    Then there is no div.banner.note
    When storage is set to "{" again through the "__seed__" page and the app is opened again
    Then div.banner.note is shown again

  @R17
  Scenario Outline: The note sits between the top of the page and the list (v1.1.0 changed)
    Given the clock is fixed at 2026-10-10T12:00:00+08:00, the viewport is <viewport>, and storage holds "{"
    Then the top of div.banner.note is 12 pixels below the bottom of <above>, and the top of div.frame-wrap is 12 pixels below the bottom of div.banners

    Examples:
      | viewport | above        |
      | 390x844  | header.top   |
      | 1280x800 | section.band |

  @R17 @R41
  Scenario: An unreadable value whose reset save fails shows the warning above the note (v1.1.0 new, CG-17 ruled)
    Given the clock is fixed at 2026-10-10T12:00:00+08:00, storage holds "{", and the init script D-a
    When the page opens
    Then div.banners holds div.banner.warn and then div.banner.note, in that order
    And ul.rows holds li.empty, and stored(page) is still "{"
    When the switch is turned off (storage_switch(page, false)) and the user adds "Read 20 pages"
    Then there is no div.banner.warn, div.banner.note is still shown, and stored(page) is exactly '{"version":1,"habits":[{"name":"Read 20 pages","done":[]}]}'

  # The save warning (spec R41, research SW1 to SW8, statements (a) to (f) of research A2).

  @R41
  Scenario Outline: A cold boot with working storage shows no warning and writes nothing (v1.1.0 new)
    Given <state> with count_writes
    When 2 seconds pass
    Then there is no div.banner.warn and no write was made

    Examples:
      | state          |
      | a fresh day    |
      | the sample day |
      | twelve habits  |

  @R41
  Scenario: The first failing save shows the warning, and the change stays (v1.1.0 new)
    Given the sample day with the init script D-a and record=True
    Then there is no div.banner.warn, because the boot read works and loading saves nothing
    When the user clicks "Done today, Stretch 10 minutes"
    Then the first child of div.banners is div.banner.warn with role "status", holding exactly one element, p "Your habits are not being saved on this device. Changes will be lost when you close this tab.", and no button
    And the Stretch row reads "Current 3 days" and its Done today has aria-pressed "true"
    And stored(page) is still the sample text, and no page error was recorded

  @R41
  Scenario: While saves keep failing the warning stays the same element (v1.1.0 new)
    Given the sample day with the init script D-a, after the user clicked "Done today, Stretch 10 minutes", a handle H to div.banner.warn, and mutation_log on div.banners
    When the user clicks "Done today, Read 20 pages" and then adds "Drink water"
    Then H is still connected and is the only div.banner.warn in the document
    And div.banners saw no child added or removed since the handle was taken
    When the page reloads, the driver still failing
    Then there is no div.banner.warn and the rows show the stored sample

  @R41
  Scenario: The next working save removes the warning, and storage then holds what is on screen (v1.1.0 new)
    Given the sample day with the init script D-a, after the user clicked "Done today, Stretch 10 minutes" and "Done today, Read 20 pages" while saves failed, and mutation_log on div.banners
    When the switch is turned off and the user clicks "Done today, No phone after 11pm"
    Then there is no div.banner.warn and div.banners saw exactly one child removed
    And stored(page) is exactly encode of the sample habits with "2026-10-10" added to Stretch's and No phone's done lists and taken out of Read's

  @R41
  Scenario: Storage refused at boot shows the warning in the first render and clears when storage returns (v1.1.0 new)
    # If task 11's probe P1 shows that WebKit refuses the redefinition of window.localStorage, this scenario gets a
    # Chromium-only row with that measured reason, and the next scenario (D-c) carries the boot path in WebKit.
    Given storage holds the sample and the init script D-b
    When the page opens and its load event has fired, before any gesture
    Then div.banners holds div.banner.warn and no div.banner.note, and ul.rows holds li.empty and no li.row
    When the user adds "Read 20 pages"
    Then one row "Read 20 pages" is shown and div.banner.warn is still shown
    When the switch is turned off and the user adds "Stretch 10 minutes"
    Then there is no div.banner.warn, and stored(page) is exactly '{"version":1,"habits":[{"name":"Read 20 pages","done":[]},{"name":"Stretch 10 minutes","done":[]}]}'
    And no page error was recorded

  @R41
  Scenario: A read that throws at boot shows the warning, and the first working save clears it (v1.1.0 new)
    Given storage holds the sample and the init script D-c
    When the page opens and its load event has fired, before any gesture
    Then div.banners holds div.banner.warn and no div.banner.note, and ul.rows holds li.empty and no li.row
    When the user adds "Read 20 pages"
    Then there is no div.banner.warn, because setItem worked
    And after the switch is turned off, stored(page) is exactly '{"version":1,"habits":[{"name":"Read 20 pages","done":[]}]}'
    And no page error was recorded

  @R41
  Scenario: A real full quota shows the warning and clears when space returns (v1.1.0 new)
    # Driver D-d, the faithful case. The fill time per engine is task 11's probe P2
    Given the sample day with record=True
    When the test fills the quota (fill_quota) and the user clicks "Done today, Stretch 10 minutes", a change that makes the stored text longer
    Then div.banner.warn is shown and stored(page) is still the sample text
    When the test removes the filler (clear_fill) and the user clicks "Done today, Read 20 pages"
    Then there is no div.banner.warn and stored(page) is exactly encode of the sample with "2026-10-10" added to Stretch's done list and taken out of Read's
    And no page error was recorded

  @R41
  Scenario: The app never reads the error it catches (v1.1.0 new)
    Given the sample day with the init script D-e and record=True
    When the user clicks "Done today, Stretch 10 minutes"
    Then div.banner.warn is shown
    And no console marker starting "test:storage-read:" and no page error was recorded

Feature: Rolling over midnight
  # tests/browser/test_rollover.py (task 24). Each scenario installs the clock 30 seconds before the instant it pauses
  # at, opens the page, and pauses there (page.clock.pause_at), so no wall time passes before the clock runs.
  # Changed 2026-10-15 in execute (planner touch after step 5). "A page booted ten seconds before midnight shows the new
  # day thirty seconds after it" installs the clock 9 seconds before its pause, because it measures from the boot.

  @R19 @R35
  Scenario: The view moves to the new day within a minute while visible (v1.1.0 changed)
    Given storage holds the sample, the viewport is 1280 x 800, the clock is installed at 2026-10-10T23:59:00+08:00, and the page is open
    And the clock is paused at 2026-10-10T23:59:30+08:00
    When the clock runs for 29 seconds
    Then the date still reads "Saturday 10 October" and the band's 2026-10-10 still has aria-current "date"
    When the clock runs for 61 more seconds (to 2026-10-11T00:01:00+08:00)
    Then time.date has datetime "2026-10-11" and reads "Sunday 11 October"
    And the rows read Read "Current 4 days" and "Best 9", Stretch "No streak yet" and "Best 5", No phone "No streak yet" and "Best 14", and all three Done today buttons have aria-pressed "false"
    And the band still runs from 2026-07-20 to 2026-10-11, now as 84 buttons and no span.hc
    And the 2026-10-11 button is named "Sun 11 Oct, 0 of 3 habits" with aria-current "date" and circle.c-today, and the 2026-10-10 button is named "Sat 10 Oct, 1 of 3 habits" with neither
    And the Overview button is named "Overview, today 0 of 3 habits done"

  @R19
  Scenario: A page booted ten seconds before midnight shows the new day thirty seconds after it (v1.1.0 new)
    # Added 2026-10-15 in execute (planner touch after step 5, code review WR-01 (c), the QA re-check). It pins R19's
    # check every 30 seconds, which the scenario above cannot, since it reads only at 00:01:00. A page booted at about
    # 23:59:50 checks at about 00:00:20, and a check every 45 seconds or more first runs after 00:00:30. The test came
    # with the step 5 solver round (commit adcb981).
    Given storage holds the sample, the viewport is 1280 x 800, the clock is installed at 2026-10-10T23:59:50+08:00, and the page is open
    And the clock is paused at 2026-10-10T23:59:59+08:00
    When the clock runs for 900 ms (to 23:59:59.9)
    Then time.date still has datetime "2026-10-10" and reads "Saturday 10 October"
    When the clock runs for 30100 ms more (to 2026-10-11T00:00:30+08:00)
    Then the date, the rows, their Done today states, the band and the Overview button read as "The view moves to the new day within a minute while visible" lists them after the rollover

  @R19 @R35 @R38
  Scenario: The band and P3 move when a new week starts (v1.1.0 changed, CG-16 ruled)
    Given storage holds the sample, the viewport is 1280 x 800, the clock is installed at 2026-10-11T23:59:00+08:00 and paused at 2026-10-11T23:59:30+08:00
    When the clock runs for 90 seconds
    Then the band runs from 2026-07-27 to 2026-10-18, as 78 buttons and six empty span.hc for 13 to 18 October
    And its month labels read "Jul" over week 1, "Aug" over week 2, "Sep" over week 7 and "Oct" over week 11
    And the 2026-10-12 button is named "Mon 12 Oct, 0 of 3 habits" and has aria-current "date"
    And the rows read "No streak yet" with "Best 9", "No streak yet" with "Best 5" and "No streak yet" with "Best 14"
    When the viewport becomes 390 x 844 and the user clicks Overview
    Then P3's row 1 holds Monday 12 October and six empty cells, and its row 12 starts on Monday 27 July
    And its month labels read "Oct" in rows 1 and 2, "Sep" in row 6, "Aug" in row 11 and "Jul" in row 12, and are empty in the other rows

  @R19 @R33
  Scenario: An open year view moves to the new year (v1.1.0 new)
    Given storage holds the sample, the viewport is 390 x 844, the clock is installed at 2026-10-10T23:59:00+08:00 and paused at 23:59:30, and P2 is open for Read
    When the clock runs for 90 seconds
    Then P2 is still open, and its 2026-10-11 cell is a bead button named "Mark Sun 11 Oct 2026 as done" with aria-pressed "false", the class "today" and aria-current "date"
    And 12 to 31 October 2026 are 20 span.yc.closed, and the 2026-10-10 bead has no "today"
    And October 2025 holds 10 span.yc.blank (1 to 10 October) and no button for 2025-10-10, and P2 holds 366 bead buttons
    And p.yr-stats holds Current "4" "days" and Best "9"

  @R19 @R36
  Scenario: An open day editor keeps its day and shows today's numbers (v1.1.0 new)
    Given storage holds the sample, the viewport is 1280 x 800, the clock is installed at 2026-10-10T23:59:00+08:00 and paused at 23:59:30, and P1 is open for 2026-09-22 from the band
    When the clock runs for 90 seconds
    Then P1 is still open with "Tuesday 22 September" and "1 of 3 habits"
    And its ticks read Read "Current 4 days" and "Best 9", Stretch "No streak yet" and "Best 5", and No phone "No streak yet" and "Best 14"
    And the band's 2026-10-11 has aria-current "date"

  @R19
  Scenario: The composer keeps its text and its focus (v1.1.0 changed)
    Given storage holds the sample, the clock is installed at 2026-10-10T23:59:00+08:00 and paused at 23:59:30, and the user has typed "Drink" into the field without submitting
    When the clock runs for 90 seconds
    Then the date reads "Sunday 11 October", the field's value is "Drink", and the field is document.activeElement

  @R19
  Scenario: An error message survives the rollover (v1.1.0 changed)
    Given storage holds the sample, the clock is installed at 2026-10-10T23:59:00+08:00 and paused at 23:59:30, and the user has clicked Add with the field empty
    When the clock runs for 90 seconds
    Then #nh-msg still reads "Name the habit first." with the class list "field-msg err", and the field still has aria-invalid "true"

  @R19 @R22
  Scenario: Focus on a Done today button stays on it (v1.1.0 changed)
    Given storage holds the sample, the clock is installed at 2026-10-10T23:59:00+08:00 and paused at 23:59:30, the user has pressed Tab until "Done today, Read 20 pages" has focus, and a handle to it
    When the clock runs for 90 seconds
    Then document.activeElement is "Done today, Read 20 pages" and has aria-pressed "false", because Done today now means 11 October

  @R19 @R22
  Scenario: Focus on a day that stays in view stays on that day (v1.1.0 new)
    Given storage holds the sample, the viewport is 390 x 844, the clock is installed at 2026-10-10T23:59:00+08:00 and paused at 23:59:30, P2 open for Read by keyboard, and focus moved by Tab to "Mark Sat 10 Oct 2026 as done"
    When the clock runs for 90 seconds
    Then focus is on the bead 2026-10-10, which no longer has "today"

  @R19 @R22
  Scenario Outline: Focus whose day leaves the view goes to the top popup's first focus, or to the page's first control (v1.1.0 new, CG-14 ruled)
    Given storage holds the sample, the viewport is <viewport>, the clock is installed at <installed> and paused 30 seconds later, <popup>, and focus moved by Tab to <focused>
    When the clock runs for 90 seconds
    Then focus is on <target>

    Examples:
      | viewport | installed                 | popup                          | focused                                 | target                         |
      | 1280x800 | 2026-10-11T23:59:00+08:00 | no popup open                  | the band's "Mon 20 Jul, 2 of 3 habits"  | the band's Year                |
      | 1280x800 | 2026-10-10T23:59:00+08:00 | P4 open from the band's Year   | P4's "Fri 10 Oct 2025, 3 of 3 habits"   | P4's Close                     |
      | 390x844  | 2026-10-10T23:59:00+08:00 | P2 open for Read               | "Mark Fri 10 Oct 2025 as done"          | P2's Close                     |
      | 390x844  | 2026-10-11T23:59:00+08:00 | P3 open                        | P3's "Mon 20 Jul, 2 of 3 habits"        | P3's Close                     |

  @R19 @R37
  Scenario: P1 open on the oldest day of the year when midnight passes (v1.1.0 new, CG-19 ruled)
    Given storage holds the sample, the viewport is 1280 x 800, count_writes, the clock is installed at 2026-10-10T23:59:00+08:00 and paused at 23:59:30, P4 open from the band's Year, P1 open for 2025-10-10 from P4, and the stored text S
    When the clock runs for 90 seconds
    Then P1 is still open with the title "Friday 10 October" and p#day-sub "3 of 3 habits", and P4 holds no button for 2025-10-10
    When the user clicks the tick "Read 20 pages"
    Then the tick still has aria-pressed "true", nothing was written, and stored(page) equals S
    When the user presses Escape
    Then P1 is closed, P4 is open, and focus is on P4's Close

  @R20
  Scenario: The view moves at once when the tab is shown again (v1.1.0 changed)
    Given storage holds the sample, the viewport is 1280 x 800, the clock is installed at 2026-10-10T23:58:00+08:00, and the page is open
    And the clock is paused at 2026-10-10T23:59:00+08:00
    And the test marks the tab hidden (hide_tab)
    And the system time is set to 2026-10-11T07:30:00+08:00 (page.clock.set_system_time, which fires no timer)
    Then the date still reads "Saturday 10 October"
    When the test marks the tab visible (show_tab)
    Then, without advancing the clock, the date reads "Sunday 11 October"
    And the rows, the band and the Overview button equal those of the first @R19 scenario after the rollover

Feature: Platform
  # tests/browser/test_platform.py (task 25)

  @R21
  Scenario Outline: Nothing scrolls at 360 pixels (v1.1.0 changed)
    Given <state> at 360 x 780 with <popups> open
    Then document.documentElement.scrollWidth is at most 360 and its scrollHeight is 780

    Examples:
      | state          | popups                              |
      | the sample day | none                                |
      | a fresh day    | none                                |
      | twelve habits  | none                                |
      | the sample day | P3                                  |
      | the sample day | P3, then P1 for 2026-09-22          |
      | the sample day | P3, then P4 from its Year           |
      | the sample day | P2 for Read                         |
      | the sample day | M1, from 'Delete "Read 20 pages"'   |

  @R21
  Scenario: Sizes at 360 pixels (v1.1.0 changed)
    Given the sample day at 360 x 780
    Then every bin, Year button, Done today button and the Overview button is at least 44 by 44 pixels, and the field and Add are 48 pixels tall
    When the user opens P2 for Read
    Then every span.bead is 34 by 34 pixels and Close is 44 by 44
    When the user closes P2 and opens P3
    Then every P3 day cell is 46 pixels tall and between 42.6 and 43.6 pixels wide, its ring svg is 40 by 40, and P3's Year and Close are at least 44 by 44
    When the user opens P4 from P3's Year
    Then every P4 day cell is 46 pixels tall with a 40 by 40 ring
    When the user opens P1 from P4's 2026-09-22
    Then every tick is at least 60 pixels tall and P1's Close is 44 by 44
    When the user presses Escape three times and opens M1 from 'Delete "Read 20 pages"'
    Then M1's Cancel and Delete habit are 48 pixels tall
    And in a second context at 360 x 780 with storage "{", the Dismiss note button is 44 by 44

  @R21
  Scenario: Sizes at 390 pixels (v1.1.0 new)
    Given the sample day at 390 x 844
    When the user opens P2 for Read
    Then every span.bead is 36 by 36 pixels and every bead button is 44 pixels tall
    When the user closes P2 and opens P3
    Then every P3 day cell is 48 pixels tall with a 42 by 42 ring
    When the user opens P4 from P3's Year
    Then every P4 day cell is 48 pixels tall with a 42 by 42 ring

  @R22
  Scenario: Tab order on a phone (v1.1.0 changed)
    Given the sample day at 390 x 844 with nothing focused
    When the user presses Tab 12 times
    Then focus visits, in order, the Overview button, then for Read, Stretch and No phone in turn its bin, its Year and its Done today, then the field, then Add

  @R22 @R35
  Scenario: Tab order on a desktop (v1.1.0 new)
    Given the sample day at 1280 x 800 with nothing focused
    When the user presses Tab 95 times
    Then focus visits, in order, the band's Year, the 83 band day buttons oldest first (Mon 20 Jul to Sun 26 Jul, then Mon 27 Jul, and so on to Sat 10 Oct), then for each row its bin, its Year and its Done today, then the field, then Add

  @R22 @R17
  Scenario Outline: Tab order with the note (v1.1.0 changed)
    Given the clock is fixed at 2026-10-10T12:00:00+08:00, the viewport is <viewport>, storage holds "{", and nothing is focused
    When the user presses Tab <presses> times
    Then focus visits, in order, <order>

    Examples:
      | viewport | presses | order                                                                         |
      | 390x844  | 4       | the Overview button, "Dismiss note", the field, Add                          |
      | 1280x800 | 87      | the band's Year, its 83 day buttons, "Dismiss note", the field, Add          |

  @R22
  Scenario Outline: Focus rings on keyboard focus (v1.1.0 changed)
    Given <state>
    When the user presses Tab until <target> has focus
    Then <ring element>'s computed outline-color is "rgb(237, 238, 240)", its outline-style "solid", its outline-width "2px" and its outline-offset "<offset>"

    Examples:
      | state                                                    | target                                 | ring element                        | offset |
      | the sample day at 390 x 844                              | the Overview button                    | the button                          | 2px    |
      | the sample day at 390 x 844                              | "Year view, Read 20 pages"             | the button                          | 2px    |
      | the sample day at 390 x 844                              | "Done today, Read 20 pages"            | the button                          | 2px    |
      | the sample day at 390 x 844                              | the field                              | the field                           | 2px    |
      | the sample day at 390 x 844                              | Add                                    | the button                          | 3px    |
      | the sample day at 1280 x 800                             | the band's Year                        | the button                          | 2px    |
      | the sample day at 1280 x 800                             | the band's "Mon 20 Jul, 2 of 3 habits" | the button                          | -2px   |
      | the sample day at 390 x 844, P2 opened for Read by keyboard | P2's Close                          | the button                          | -2px   |
      | the sample day at 390 x 844, P2 opened for Read by keyboard | P2's Delete habit                   | the button                          | 2px    |
      | the sample day at 390 x 844, P2 opened for Read by keyboard | "Mark Thu 1 Oct 2026 as done"       | its span.bead                       | 3px    |
      | the sample day at 1280 x 800, P1 opened for 2026-09-22 by keyboard | the tick "Stretch 10 minutes" | the button                       | -2px   |
      | the sample day at 390 x 844, M1 opened from Read's bin by keyboard | Cancel                       | the button                          | 3px    |
      | storage "{" at 390 x 844                                 | "Dismiss note"                         | the button                          | -2px   |

  @R22
  Scenario: A focused bin shows its glyph in the danger colour, and a focused bead has no ring of its own (v1.1.0 new)
    Given the sample day at 390 x 844
    When the user presses Tab until 'Delete "Read 20 pages"' has focus
    Then the bin's computed outline is the 2px "rgb(237, 238, 240)" ring with offset "-2px", and its computed color is "rgb(255, 107, 102)"
    When the user opens P2 for Read by keyboard and presses Tab until "Mark Thu 1 Oct 2026 as done" has focus
    Then that bead button's computed outline-style is "none" and its span.bead carries the ring

  @R22
  Scenario: A mouse click draws no ring (v1.1.0 changed)
    Given the sample day
    When the user clicks "Done today, Stretch 10 minutes"
    Then that button does not match ":focus-visible" and its computed outline-style is "none"
    And in Chromium it has focus. In WebKit document.activeElement is body

  @R22 @R40
  Scenario: Every popup can be used with the keyboard alone (v1.1.0 new)
    Given the sample day at 390 x 844 with nothing focused
    When the user presses Tab (the Overview button has focus) and Enter
    Then P3 is open and Close has focus
    When the user presses Shift+Tab
    Then P3's Year has focus
    When the user presses Enter
    Then P4 is open and Close has focus
    When the user presses Tab
    Then focus is on P4's "Thu 1 Oct 2026, 2 of 3 habits"
    When the user presses Enter
    Then P1 is open with the title "Thursday 1 October" and the tick "Read 20 pages" has focus
    When the user presses Space
    Then that tick has aria-pressed "false" and p#day-sub reads "1 of 3 habits"
    When the user presses Escape three times
    Then no dialog is open and the Overview button has focus

  @R23
  Scenario: Transitions without reduced motion (v1.1.0 changed)
    Given the sample day at 1280 x 800 with reduced motion "no-preference"
    Then after load and before any gesture document.getAnimations() is empty
    And the computed transition-duration is "0.17s, 0.17s, 0.17s, 0.12s" for every button.btn-done and button.btn-year, "0.17s, 0.17s, 0.12s" for every button.btn-bin, "0.17s" for every button.hc, "0.17s, 0.12s" for button.ov-btn and for Add
    When the user opens P1 for 2026-09-22 from the band
    Then every button.tick has "0.17s" and every span.tbox "0.17s, 0.17s"
    When the user closes P1 and opens P2 for Read
    Then every span.bead has "0.17s, 0.17s, 0.12s"

  @R23
  Scenario Outline: Popups rise and backdrops fade (v1.1.0 changed)
    Given the sample day at <viewport> with reduced motion "no-preference"
    When the user opens <popup>
    Then its div.dlg-box has the computed animation-name "<name>" and animation-duration "<duration>", and its ::backdrop has the animation-name "fade" and animation-duration "0.18s"
    # Whether WebKit's getComputedStyle reports the ::backdrop pseudo-element is task 11's probe. If it does not, the
    # backdrop half becomes a class (b) line here with the measured value.

    Examples:
      | viewport | popup                               | name  | duration |
      | 390x844  | P2 for Read                         | rise  | 0.22s    |
      | 390x844  | P3                                  | rise  | 0.22s    |
      | 1280x800 | P4 from the band's Year             | rise  | 0.22s    |
      | 1280x800 | P1 for 2026-09-22 from the band     | sheet | 0.26s    |
      | 390x844  | M1, from 'Delete "Read 20 pages"'   | rise  | 0.22s    |

  @R23 @R32
  Scenario: A change pops what changed and bumps its number, and replays on the next change (v1.1.0 new)
    # Changed 2026-10-15 in execute (planner touch after step 5, Q-25-1 of task 25, ledger S7 row 18, and code review
    # WR-02). The first Given read ~~the sample day at 1280 x 800 with reduced motion "no-preference" and
    # animation_log~~, the first Then ~~within 1 second the log holds, and holds only, "pop" on Stretch's span.dot,
    # "pop" on the svg of the band's 2026-10-10, "pop" on the svg in span.ov-ring and "bump" on Stretch's Current
    # span.val~~, and the line after it ~~And their computed animation-durations are "0.26s", "0.3s", "0.3s" and
    # "0.28s"~~. From 1024 px the Overview button is not displayed (R4, R38), below 1024 px the band is not, and an
    # element that is not displayed starts no animation, so no one width shows both rings play. The Overview button's
    # ring is seen playing at 390 x 844 and read by its class and computed animation at 1280 x 800. The last two Then
    # lines gained "and no "pop" on any other ..." (WR-02).
    Given the sample day at 390 x 844 with reduced motion "no-preference" and animation_log
    When the user clicks "Done today, Stretch 10 minutes"
    Then within 1 second the log holds, and holds only, "pop" on Stretch's span.dot, "pop" on the svg in span.ov-ring and "bump" on Stretch's Current span.val, with the computed animation-durations "0.26s", "0.3s" and "0.28s"
    Given, in a second context, the sample day at 1280 x 800 with reduced motion "no-preference" and animation_log
    When the user clicks "Done today, Stretch 10 minutes"
    Then within 1 second the log holds, and holds only, "pop" on Stretch's span.dot, "pop" on the svg of the band's 2026-10-10 and "bump" on Stretch's Current span.val, with the computed animation-durations "0.26s", "0.3s" and "0.28s"
    And span.ov-ring has the class "pop", and its svg has the computed animation-name "pop" and animation-duration "0.3s"
    When the user clicks the same button again 100 ms later (real time), while the first pop still runs
    Then within 1 second the log holds a second "pop" on Stretch's span.dot and a second "bump" on its Current span.val
    When the user opens P1 for 2026-09-22 from the band and clicks the tick "Read 20 pages"
    Then the log gains "pop" on that tick's span.tbox with the duration "0.26s", and no "pop" on any other tick's span.tbox
    When the user closes P1, opens P2 for Read and clicks the bead 2026-10-06
    Then the log gains "pop" on that bead's span.bead with the duration "0.26s", and no "pop" on any other bead's span.bead

  @R23
  Scenario: Everything appears at once under reduced motion (v1.1.0 changed)
    Given the sample day at 1280 x 800 with reduced motion "reduce"
    Then every element, and its ::before and ::after, has every computed transition-duration value "0s" and the animation-name "none"
    When the user clicks "Done today, Stretch 10 minutes" and opens P2 for Read
    Then document.getAnimations() is empty, P2's div.dlg-box has the animation-name "none", and its ::backdrop has the animation-name "none"

  @R24
  Scenario: Markup in a name stays text everywhere (v1.1.0 changed)
    Given a fresh day at 1280 x 800 and a record of every JavaScript dialog the page opens
    When the user types "<img src=x onerror=alert(1)>" and clicks Add
    Then h3#rn-1 has the text content "<img src=x onerror=alert(1)>" and no child element, and the document holds no img element
    And the row's bin is named 'Delete "<img src=x onerror=alert(1)>"', its Year "Year view, <img src=x onerror=alert(1)>" and its Done today "Done today, <img src=x onerror=alert(1)>"
    When the user clicks its Year
    Then h2#yr-title has that text content and no child element
    When the user presses Escape and clicks the band's "Sat 10 Oct, 0 of 1 habits"
    Then P1's tick is named "<img src=x onerror=alert(1)>", and its span.tname has that text content and no child element
    When the user presses Escape and clicks the row's bin
    Then #del-title has the text content dialog_title("<img src=x onerror=alert(1)>") and no child element
    And no JavaScript dialog opened and no page error was recorded

  @R24
  Scenario: No HTML sinks in the source
    Given the text of every file under src/
    Then none contains "innerHTML", "outerHTML", "insertAdjacentHTML", "document.write", "eval(" or "new Function"

  @R25
  Scenario: Every request stays on the device's own files (v1.1.0 changed)
    Given the sample day at 1280 x 800 opened with record=True, so the GET /__seed__ request is not in the log
    When the user clicks "Done today, Stretch 10 minutes", ticks Read in P1 for 2026-09-22 and closes P1, ticks the bead 2026-10-06 in Read's P2 and closes P2, opens and closes P4, adds "Drink water", deletes "Read 20 pages" with its bin and confirm_delete, and the page reloads
    Then every recorded request is a GET to the BASE_URL origin with no query string
    And every request path is "/", "/index.html", "/favicon.ico", "/src/styles.css", "/src/icon.svg" or "/src/<name>.js" for a file that exists in src/
    And no console message of type "error" and no page error was recorded

  @R25
  Scenario: The CSP is in force (v1.1.0 changed)
    Given the sample day
    When the test, in the page, registers a securitypolicyviolation listener and then evaluates fetch("https://example.com/")
    Then the promise rejects, and one securitypolicyviolation event fires whose effectiveDirective is "connect-src"

Feature: Retired in v1.1.0 (text kept, tests removed)
  # Each scenario below is the 1.0 text, unchanged except for this comment block and the comment above each. None is
  # run. The requirement or 1.0 rule each one tested is retired or replaced as its comment says.

  # Retired in v1.1.0, R7 retired (the 7-day strip is gone), replaced by R31 and R33.
  @R7
  Scenario Outline: The sample's week strips
    Given the sample day
    Then the strip of "<habit>" has exactly 7 button.day with type "button" and data-date 2026-10-02 to 2026-10-08 in order
    And their span.wd texts are Fri, Sat, Sun, Mon, Tue, Wed, Thu and their span.dm texts are 2, 3, 4, 5, 6, 7, 8
    And their aria-pressed values read "<pattern>" (D is "true", . is "false")
    And the strip <has> the attribute data-run-continues

    Examples:
      | habit               | pattern       | has         |
      | Read 20 pages       | . D D D D D D | does not have |
      | Stretch 10 minutes  | D D . D D D . | has         |
      | No phone after 11pm | . D . . D . D | does not have |

  # Retired in v1.1.0, R7 retired, replaced by R31 and R33.
  @R7
  Scenario: Day names, today, and nothing outside the window
    Given the sample day
    Then the day buttons of every strip are named "Mark Fri 2 Oct as done", "Mark Sat 3 Oct as done", "Mark Sun 4 Oct as done", "Mark Mon 5 Oct as done", "Mark Tue 6 Oct as done", "Mark Wed 7 Oct as done", "Mark Thu 8 Oct as done"
    And only the three 2026-10-08 buttons have aria-current "date"
    And no button in the document has a data-date before 2026-10-02 or after 2026-10-08

  # Retired in v1.1.0, R7 and R8 retired, replaced by R31, R33 and R34.
  @R7 @R8
  Scenario: The name does not change with the state
    Given the sample day
    When the user clicks Stretch's day 2026-10-08
    Then that button is still named "Mark Thu 8 Oct as done" and its aria-pressed is "true"

  # Retired in v1.1.0, R8 retired (ticking moves to Done today, the year view and the day editor), replaced by R31, R32, R34 and R37.
  @R8 @R16
  Scenario Outline: Toggling a day updates the bead in place, the streak, the heatmap and storage
    Given the sample day
    And a handle to the day button <date> of "<habit>"
    When the user clicks that day button
    Then the same handle is still connected to the document and its aria-pressed is "<pressed>"
    And the streak line of "<habit>" reads "<cur>" and "<best>"
    And the strip of "<habit>" <run> the attribute data-run-continues
    And the cell <date> has class "l<level>" and is named "<name>"
    And in stored(page) the done list of "<habit>" <stored> "<date>"

    Examples:
      | habit               | date       | pressed | cur     | best    | run           | level | name                       | stored               |
      | Stretch 10 minutes  | 2026-10-08 | true    | 4 days  | Best 9  | has           | 4     | Thu 8 Oct, 3 of 3 habits   | contains             |
      | Read 20 pages       | 2026-10-08 | false   | 5 days  | Best 14 | does not have | 1     | Thu 8 Oct, 1 of 3 habits   | does not contain     |
      | No phone after 11pm | 2026-10-07 | true    | 3 days  | Best 4  | does not have | 4     | Wed 7 Oct, 3 of 3 habits   | contains             |
      | Stretch 10 minutes  | 2026-10-04 | true    | 7 days  | Best 9  | has           | 2     | Sun 4 Oct, 2 of 3 habits   | contains             |
      | Stretch 10 minutes  | 2026-10-02 | false   | 3 days  | Best 9  | does not have | 0     | Fri 2 Oct, 0 of 3 habits   | does not contain     |
      | Read 20 pages       | 2026-10-02 | true    | 10 days | Best 14 | has           | 2     | Fri 2 Oct, 2 of 3 habits   | contains             |

  # Retired in v1.1.0, R8 retired, replaced by R31 (keyboard presses keep focus).
  @R8
  Scenario: Keyboard toggling keeps focus
    Given the sample day
    When the user presses Tab until Stretch's day 2026-10-08 has focus, then presses Space
    Then that button has aria-pressed "true" and is still document.activeElement
    When the user presses Enter
    Then that button has aria-pressed "false" and is still document.activeElement
    And the streak line of "Stretch 10 minutes" reads "3 days" and "Best 9"

  # Retired in v1.1.0, R8 retired, replaced by R31 (pressing twice restores the saved value).
  @R8
  Scenario: Ticking twice restores the saved value
    Given the sample day and the stored text S before any action
    When the user clicks Read's day 2026-10-05 twice
    Then stored(page) parses to the same object as S

  # Retired in v1.1.0, R9 retired (the heatmap becomes the overview band and P3), replaced by R35 and R38.
  @R9
  Scenario: The sample's heatmap
    Given the sample day
    Then h2.heat-title reads "Last 12 weeks"
    And div.months is aria-hidden and holds 4 spans: "Jul" with grid-column 1, "Aug" with 3, "Sep" with 8, "Oct" with 12
    And div.wdays is aria-hidden and its 7 spans read "Mon", "", "Wed", "", "Fri", "", "Sun"
    And div.cells holds 84 span.hc whose data-date run from 2026-07-20 to 2026-10-11, one day apart
    And for each of the 81 dates in heatmapLevels of sample-history.json, the cell has class "l<level>" with the file's level, role "img", and the name "<Ddd D Mon>, <n> of 3 habits" where n is the number of sample habits done that day
    And the cell 2026-10-08 has classes "hc l2 today", aria-current "date" and the name "Thu 8 Oct, 2 of 3 habits"
    And no other cell has class "today" or aria-current
    And the cells 2026-10-09, 2026-10-10 and 2026-10-11 have classes "hc future", aria-hidden "true", and no role, name or level class
    And div.legend is aria-hidden and reads "None", then five span.hc with classes l0, l1, l2, l3, l4, then "All"

  # Retired in v1.1.0, R9 retired, replaced by R35 and R19 (the band on a Monday).
  @R9
  Scenario: A Monday shows six future cells and a shifted grid
    Given the clock is fixed at 2026-10-12T12:00:00+08:00 with no storage
    Then div.cells runs from 2026-07-27 to 2026-10-18
    And the month labels are "Jul" at 1, "Aug" at 2, "Sep" at 7, "Oct" at 11
    And the cells 2026-10-13 to 2026-10-18 are future
    And the cell 2026-10-12 is named "Mon 12 Oct, 0 of 0 habits" and has class "today"

  # Retired in v1.1.0, the 500 ms Delete habit window is replaced by the time-free guard of R13 (CG-10).
  @R13 @R15
  Scenario Outline: A click inside the window is ignored and one after it deletes
    Given the sample day with <input> input, the clock installed and paused, and the dialog opened by a press for "Stretch 10 minutes"
    When 499 ms pass and the user presses "Delete habit"
    Then the dialog is still open, there are 3 li.habit, nothing was saved and stored(page) equals the text before
    When 1 ms more passes and the user presses "Delete habit" at the same point
    Then the dialog is closed, "Stretch 10 minutes" is gone and one save was made

    Examples:
      | input |
      | mouse |
      | touch |

  # Retired in v1.1.0, the 500 ms Delete habit window is replaced by R13's time-free guard. A keyboard activation now always acts.
  @R13 @R15
  Scenario: Enter on "Delete habit" inside the window is ignored and one after it deletes
    Given the sample day, the clock installed and paused, and the button "Delete Stretch 10 minutes" focused
    When the user presses Enter (the dialog opens and focus is on "Cancel"), presses Tab (focus moves to "Delete habit") and presses Enter at the same instant
    Then the dialog is still open, focus is on "Delete habit", there are 3 li.habit, nothing was saved and stored(page) equals the text before
    When 500 ms pass and the user presses Enter
    Then the dialog is closed, the rows are "Read 20 pages" and "No phone after 11pm" and one save was made

  # Retired in v1.1.0, no Delete habit window exists any more (R13, CG-10).
  @R13
  Scenario: Every opening starts the window again
    Given the sample day, the clock installed and paused, and the dialog opened for "Stretch 10 minutes", 600 ms passed, and Escape pressed
    When the user opens the dialog again and at once clicks "Delete habit"
    Then the dialog is still open and there are 3 li.habit
    When 600 ms pass and the user clicks "Delete habit"
    Then "Stretch 10 minutes" is gone

  # Retired in v1.1.0, replaced by "One press on Delete habit away from the bin deletes at once" (R13, R15).
  @R15
  Scenario: A deliberate click after the window deletes
    Given the sample day with the clock installed and the dialog open for "Stretch 10 minutes"
    When 600 ms pass and the user clicks "Delete habit"
    Then the dialog is closed and the rows are "Read 20 pages" and "No phone after 11pm"

  # Retired in v1.1.0, replaced by "Enter on Delete habit deletes at once" (R13, R15).
  @R15
  Scenario: Enter on "Delete habit" after the window deletes
    Given the sample day with the clock installed and the dialog open for "Stretch 10 minutes"
    When 600 ms pass, the user presses Tab (focus moves from Cancel to "Delete habit") and presses Enter
    Then the rows are "Read 20 pages" and "No phone after 11pm"

  # Retired in v1.1.0, the 1.0 layout had Cancel over the second habit's beads on small phones. By the v1.1.0 geometry of
  # system.css (computed while planning, not rendered), Cancel lies over row text or empty space at the planned sizes,
  # so no control lies under it to check. The page guard is covered by the backdrop, Close and Delete habit scenarios of R14.
  @R14
  Scenario Outline: A double click or double tap on Cancel does not tick the bead behind it
    Given the sample day at <size> with <input> input, the clock installed and paused, and the dialog open for "Read 20 pages"
    When the user presses the centre of "Cancel" twice at the same instant
    Then the dialog is closed and a day bead lies under that point (Cancel lies over the second habit's beads on small phones)
    And nothing was saved and stored(page) equals the text before

    Examples:
      | size    | input |
      | 375x667 | mouse |
      | 375x667 | touch |
      | 360x640 | mouse |
      | 360x640 | touch |

  # Retired in v1.1.0, R18 retired (a failed save is no longer silent), replaced by R41.
  @R18
  Scenario: Storage that cannot be used at all
    Given a context whose init script makes reading window.localStorage throw a DOMException named "SecurityError"
    And the clock is fixed at 2026-10-08T12:00:00+08:00
    When the page opens
    Then p.empty is shown and there is no div.note
    When the user adds "Read 20 pages" and clicks its day 2026-10-08
    Then the row shows "1 day" and "Best 1"
    And no page error was recorded

  # Retired in v1.1.0, R18 retired, replaced by R41.
  @R18
  Scenario: A save that fails
    Given the sample day with an init script that makes Storage.prototype.setItem throw a DOMException named "QuotaExceededError"
    When the user clicks Stretch's day 2026-10-08 and adds "Drink water"
    Then Stretch's streak line reads "4 days" and a fourth row "Drink water" is shown
    And #new-habit-msg is empty and no page error was recorded

  # Retired in v1.1.0, the 1.0 desktop had a left column for the note. Replaced by "The note sits between the top of the page and the list" (R17).
  @R17
  Scenario: On desktop the note sits in the left column
    Given the clock is fixed at 2026-10-08T12:00:00+08:00, the viewport is 1280 x 800 and storage holds "{"
    Then div.note's bounding box lies inside div.col-main's box (x 168, width 500)
    And section.heat starts at x 732

  # Retired in v1.1.0, the strip is gone (R7). Replaced by "Focus on a Done today button stays on it" (R19, R22).
  @R19 @R22
  Scenario: Focus on today's bead stays on today's bead
    Given storage holds the sample and the clock is installed at 2026-10-08T23:59:30+08:00
    And the user has pressed Tab until Read's day 2026-10-08 has focus
    When the clock runs for 90 seconds
    Then document.activeElement is the seventh day button of Read's strip, named "Mark Fri 9 Oct as done", with aria-current "date"
```
### Cold-boot live-e2e gate (`@R27`, both engines)
Run by `python tests/browser/live_e2e.py --engine <engine> --base-url http://127.0.0.1:<port>/ --out docs/modules/app/qa/live-e2e/<datetimestamp>-<engine>/`, once with `chromium` and once with `webkit`, after every other gate is green. Its file name keeps it out of pytest collection, because it uses the real clock and writes the gate's evidence.

**Control and baseline** (constitution, Gates and evidence). The gate compares the running app with the cold-boot rule, an empty store at the first visit, and it must be able to fail when the app does not start empty. Its control is the same script in the same engine, against the same server, run once with `--control seeded --out docs/modules/app/qa/live-e2e/<datetimestamp>-<engine>-control/` just before that engine's green run (the second scenario below). It seeds the sample through `__seed__` before the app loads, runs the same steps, and must stop at the first-visit step with `pass` false, failing on "stored(page) is null" and on `li.empty` "No habits yet.". Its evidence is kept as the RED capture beside the green run and is never overwritten. A control that passes the first-visit step means the gate cannot fail, and the gate is not met. The baseline is the gate's own prior run in the same engine. Added 2026-10-13 after the plan check (F5), the gate first named no control.

```gherkin
Feature: Cold boot, real gestures, evidence, in each engine

  @R27 @R30
  Scenario Outline: The headline flows on a cold start (v1.1.0 changed)
    Given the app is served from the project root by python -m http.server <port> --bind 127.0.0.1
    And a fresh headless <engine> context made through launch(), at 390 x 844, with empty storage, the real system clock (no page.clock) and no init script other than the clipboard stand-in
    And before any gesture, Clipboard.prototype.writeText is absent or is not the browser's native function
    And the test reads the browser's local date once (T) from about:blank before opening the app, and derives yesterday (Y)
    When the page opens BASE_URL with no query string or fragment
    Then ul.rows holds li.empty with "No habits yet." and "Add one you want to do every day.", there is no li.row and no banner, the Overview button is named "Overview, today 0 of 0 habits done", every band day button up to T is named "<shortDate>, 0 of 0 habits", T's has aria-current "date", and stored(page) is null
    When the user clicks the field, types "Read 20 pages" and clicks Add
    Then one row "Read 20 pages" reads "Current" with "No streak yet" and no Best, its Done today has aria-pressed "false", and the field is empty
    When the user clicks the field, types "Stretch 10 minutes" and presses Enter
    Then a second row "Stretch 10 minutes" shows under the first
    When the user clicks "Done today, Read 20 pages" and then "Done today, Stretch 10 minutes"
    Then both rows read "Current 1 day" and "Best 1", and the Overview button is named "Overview, today 2 of 2 habits done"
    When the user clicks Overview and then P3's button for Y
    Then P1 is open with the title longDate(Y) and "0 of 2 habits", and its first tick has focus
    When the user clicks the tick "Read 20 pages"
    Then it has aria-pressed "true", P1 reads "1 of 2 habits", and the tick reads "Current 2 days" and "Best 2"
    When the user clicks P1's Close
    Then P1 is closed and focus is on P3's button for Y, now named "<shortDate of Y>, 1 of 2 habits"
    When 600 ms pass and the user clicks P3's Close
    Then P3 is closed, focus is on the Overview button, and the Read row reads "Current 2 days" and "Best 2"
    When 600 ms pass and the user clicks "Year view, Stretch 10 minutes" and then the bead for Y
    Then that bead has aria-pressed "true" and P2's stats read Current "2" "days" and Best "2"
    When the user clicks P2's Close
    Then P2 is closed, focus is on "Year view, Stretch 10 minutes", and the Stretch row reads "Current 2 days" and "Best 2"
    When the page reloads
    Then both rows, their Done today states and their numbers are unchanged
    When the user clicks 'Delete "Stretch 10 minutes"'
    Then M1 is open, #del-title reads dialog_title("Stretch 10 minutes"), and Cancel has focus
    When the user clicks Cancel
    Then M1 is closed, 2 rows remain, and focus is on 'Delete "Stretch 10 minutes"'
    When 600 ms pass, the user clicks 'Delete "Stretch 10 minutes"' again, and clicks Delete habit at the centre of the largest part of it that lies outside the bin's box
    Then 1 row remains, focus is on 'Delete "Read 20 pages"', and the Overview button is named "Overview, today 1 of 1 habits done"
    When 600 ms pass, the user clicks the field, types "read 20 pages" and presses Enter
    Then #nh-msg reads "You already track this habit." with the class list "field-msg err", and the field still holds "read 20 pages" with aria-invalid "true"
    When the page reloads
    Then exactly one row "Read 20 pages" reads "Current 2 days" and "Best 2", with Done today pressed
    When the viewport becomes 1280 x 800
    Then the band is shown, and T's band button is named "<shortDate of T>, 1 of 1 habits" and holds circle.c-today, one circle.seg with "on", circle.c-core and a text.c-num with "on"
    When the user clicks Y's band button
    Then P1 is open with the title longDate(Y) and "1 of 1 habits", and the tick "Read 20 pages" is pressed
    When the user clicks P1's Close
    Then P1 is closed and focus is on Y's band button
    When 600 ms pass and the user clicks the band's Year
    Then P4 is open, Close has focus, and T's P4 button is named "<yearDate of T>, 1 of 1 habits"
    When the user presses Escape
    Then P4 is closed and focus is on the band's Year
    And the browser's local date is still T (otherwise the run is void and is repeated)
    And no console error and no page error was recorded, and every request meets the @R25 request rule (a GET to the BASE_URL origin with no query string, for "/", "/index.html", "/favicon.ico", "/src/styles.css", "/src/icon.svg" or "/src/<name>.js" for a file that exists in src/)
    And no console marker starting "test:clipboard:" was recorded

    Examples:
      | engine   |
      | chromium |
      | webkit   |

  @R27
  Scenario Outline: The gate fails when the app starts from saved habits (control, v1.1.0 new)
    # Run by the finder just before the green run of the same engine (spec task 28). Added 2026-10-13 after the plan check (F5).
    Given the app is served as in the scenario above, and a fresh headless <engine> context made through launch() with the clipboard stand-in
    And live_e2e.py runs with --control seeded, so before the app loads it opens the same-origin "__seed__" page and sets "streaks.state" to sample_state()
    When the page opens BASE_URL and the script runs its steps from the first visit on
    Then the run stops at the first-visit step with pass false, because ul.rows holds li.row elements and no li.empty, and stored(page) is not null
    And summary.json records "control": "seeded", the engine, browser.version and pass false, and names the first-visit step as the first failing step
    And the evidence folder ends with "-<engine>-control" and no earlier run's files are in it

    Examples:
      | engine   |
      | chromium |
      | webkit   |
```
- **Control mode.** `--control seeded` is the only option that changes what the script does, and it can only make the run fail. A run without it writes `"control": null` in `summary.json`, and only such a run can meet the gate. The seed in control mode is test-side data written through `__seed__`, never through the app (CLAUDE.md, constitution cold-boot rule).
- **Gestures.** Only `click`, `keyboard.type`, `keyboard.press`, `reload` and `set_viewport_size`. No `evaluate` that writes anything, except the control mode's one `setItem` on the `__seed__` page before the app loads. Reading the DOM, `localStorage` and the date is allowed. The 600 ms pauses use `page.wait_for_timeout` (the gate installs no clock). Each one follows a click inside a popup that is followed by a click on the page or on a popup that lay beneath it, because of the page guard of R14 (CG-11 ruled). A pause is not a gesture and changes nothing on the page.
- **Focus lines** are the ones the app sets, so they hold in both engines. The gate never asserts focus after a click on a button the app does not move focus from.
- **Evidence** in `docs/modules/app/qa/live-e2e/<datetimestamp>-<engine>/`. One full-page screenshot after each `Then` (`01-first-visit.png`, `02-added.png` and so on), `steps.json` (each step's name, gesture, expected, observed, pass and time), `console.json`, `network.json`, and `summary.json` (the engine, `browser.version`, the base URL, the date T at the start and at the end, the overall pass). The WebKit run's screenshots are kept as WebKit pictures for the owner (ledger S5 row 2). No artifact means the gate is not met. The control run writes the same files in its own `-control` folder, and a green run with no control capture of the same engine beside it does not meet the gate.
- The script starts nothing itself. The agent that runs it starts and stops the server, and declares it in `PROCESSES`.

### Fidelity scenarios (`@R28`, Chromium, run by the fidelity finder after functional is green in both engines)
```gherkin
Feature: Looks right

  @R28
  Scenario Outline: Each screen is 1-to-1 with its golden (v1.1.0 changed)
    Given the fidelity capture of "<screen>" at <viewport> as the Fidelity gate below defines it
    Then report.json has dimensions_match true and mismatch_pixels 0 at threshold 0.1
    And every FE element checklist row of "<screen>" matches

    Examples:
      | screen              | viewport |
      | today.html          | 360x780  |
      | today.html          | 390x844  |
      | today.html          | 1280x800 |
      | day-editor.html     | 360x780  |
      | day-editor.html     | 390x844  |
      | day-editor.html     | 1280x800 |
      | year-view.html      | 360x780  |
      | year-view.html      | 390x844  |
      | year-view.html      | 1280x800 |
      | overview.html       | 360x780  |
      | overview.html       | 390x844  |
      | overview-year.html  | 360x780  |
      | overview-year.html  | 390x844  |
      | overview-year.html  | 1280x800 |
      | delete-dialog.html  | 360x780  |
      | delete-dialog.html  | 390x844  |
      | delete-dialog.html  | 1280x800 |
      | today-empty.html    | 360x780  |
      | today-empty.html    | 390x844  |
      | today-empty.html    | 1280x800 |
      | today-full.html     | 360x780  |
      | today-full.html     | 390x844  |
      | today-full.html     | 1280x800 |

  @R28
  Scenario: The gate can pass and can fail (v1.1.0 new)
    Given the harness with each golden as both the golden and the candidate (served read-only by the app's server at /docs/design/<screen>.html), at each viewport the gate uses for it
    Then every report shows mismatch_pixels 0 and dimensions_match true (the control)
    Given the K1 capture of today.html taken without any state flag, so the app shows S1
    Then its report shows mismatch_pixels above 0 at each of the three viewports (the negative control. A gate that reports 0 here cannot fail)

  @R28
  Scenario: The fidelity state scripts are right (v1.1.0 changed)
    # tests/browser/test_fidelity_inputs.py (task 26), run in both engines like every pytest scenario
    # Changed 2026-10-13 after the plan check (F4). Each seed script first was one statement with no clipboard stand-in,
    # although the after-load scripts click. The stand-in lines and the control line below are new.
    Given tests/browser/fidelity/seed-sample.js and tests/browser/fidelity/seed-twelve.js
    Then each starts with the exact text of CLIPBOARD_STANDIN from conftest.py, and after it holds one statement, localStorage.setItem("streaks.state", <text>), whose text parses to exactly {"version":1,"habits":<the first three v1.1.0 sample habits>} and {"version":1,"habits":<all twelve>}, as { name, done } objects with each done list ascending
    When a page with the clock fixed at 2026-10-10T09:00:00 local time loads the app with the seed script as an init script and runs an after-load script as the body of an async function
    Then before the after-load script runs, either navigator.clipboard is absent or Clipboard.prototype.writeText is not the browser's native function
    # Added 2026-10-14 in execute (planner follow-up, ruled ORCH). WebKit's document.activeElement after a scripted
    # blur() inside an open popup is not measured yet, and a mouse click there leaves focus on the popup's dialog (Engine
    # differences by design). Task 26 measures it before asserting the next line. A WebKit value other than body goes
    # into the engine table with its measurement, and this line then asserts each engine's value (spec, task 26).
    And each after-load script leaves the state below, and document.activeElement is body
      | script                 | viewports           | state                                                                                                                           |
      | open-day-editor.js     | 360x780, 390x844    | P3 and P1 open, P1's title "Tuesday 22 September", P3's 2026-09-22 button with "is-open", P3's div.sheet-body at scrollTop 0     |
      | open-day-editor.js     | 1280x800            | P1 open over K1 with the title "Tuesday 22 September", the band's 2026-09-22 with "is-open", no other dialog open              |
      | open-year-view.js      | all three           | P2 open for "Read 20 pages", its div.sheet-body at scrollTop 0                                                                  |
      | open-overview.js       | 360x780, 390x844    | P3 open, its div.sheet-body at scrollTop 0                                                                                      |
      | open-overview-year.js  | 360x780, 390x844    | P3 and P4 open, P4's div.sheet-body at scrollTop 0                                                                              |
      | open-overview-year.js  | 1280x800            | P4 open over K1, no other dialog open                                                                                           |
      | open-delete-dialog.js  | all three           | M1 open and ":modal", its title dialog_title("Stretch 10 minutes"), no other dialog open                                        |
    And each after-load script throws when its state is not reached, so a broken script fails its capture instead of rendering a wrong state
    And no console marker starting "test:clipboard:" is recorded through any of these runs
    And in Chromium, where the fidelity gate runs, each after-load script throws before its first click, and no dialog opens, on a page whose init script is the setItem statement plus a different stand-in that redefines navigator.clipboard on the navigator object as an object whose four methods reject, so Clipboard.prototype.writeText stays native (the control. The page still has a stand-in, as the constitution requires of every context). In WebKit this line records whether navigator.clipboard exists and asserts nothing more, because the fidelity gate never runs there

  @R28
  Scenario: Every frame on the states sheet matches the live state (v1.1.0 changed)
    Given the states.html checklist rows below and the computed-style method of the Fidelity gate
    Then every row matches at 360 x 780 and at 1280 x 800
```

## FE element checklist
> Every visible or interactive element of every golden, one row each. Each row passes or fails on its own. Colours are the `system.css` tokens. A test reads them as the computed values in the token table. Sizes are CSS pixels at the widths the row names, and "phone" means 360 and 390, "desktop" 1280. The pixel diff covers positions. A row fails if its element is missing, extra, or off.

| Token | Computed value | Token | Computed value |
|---|---|---|---|
| `--bg`, `--on-amber` | rgb(24, 25, 28) | `--ring` | rgb(124, 127, 136) |
| `--surface` | rgb(33, 34, 38) | `--ink`, `--focus` | rgb(237, 238, 240) |
| `--surface-2` | rgb(42, 43, 48) | `--ink-soft` | rgb(168, 171, 178) |
| `--raise` | rgb(53, 55, 61) | `--closed` | rgb(92, 94, 102) |
| `--field` | rgb(18, 19, 22) | `--amber` | rgb(255, 176, 32) |
| `--line` | rgb(51, 53, 59) | `--amber-wash` | rgba(255, 176, 32, 0.09) |
| `--track` | rgb(74, 76, 83) | `--danger` | rgb(255, 107, 102) |
| `--scrim` | rgba(10, 11, 13, 0.74) | `--scrim-soft` | rgba(10, 11, 13, 0.52) |

### K1, golden `./docs/design/today.html` (the sample day, nothing open, 360, 390 and 1280)
| # | Element | Must match the golden |
|---|---|---|
| K1-01 | Page | `html` and `body` `--bg`, text `--ink`, 400 16px/24px on the system sans stack, no margin |
| K1-02 | Icon sprite | hidden `svg` (0 by 0, `position:absolute`, aria-hidden, focusable false) with the symbols `i-x`, `i-plus`, `i-check`, `i-trash` and the golden's path data. Nothing visible |
| K1-03 | Tab title and icon | `title` "Danial's Streaky Habit". The icon link points at `src/icon.svg` (R29). Neither is drawn in a page capture |
| K1-04 | App column | `div.app`, a flex column 12 apart, one viewport tall (min 480). Phone max 640 centred, padding 12 top, 16 sides (12 at 360), bottom 12 or the safe area. Desktop max 1040 centred (x 120 to 1160 at 1280), padding 12 by 24 |
| K1-05 | Header, phone | `header.top` grid, areas "brand ov" then "date date", column gap 12, row gap 6, items centred |
| K1-06 | Header, desktop | one line, areas "brand date", column gap 20, the date at the right end |
| K1-07 | Mark | `svg.mark` 28 by 28 (32 by 32 desktop) with the golden's path, `--amber` through currentColor, 10 left of the word, aria-hidden |
| K1-08 | Word | `h1.word` "Streaky Habit", 19px/24px 700 (21px desktop), letter-spacing -0.01em, no wrap, `--ink` |
| K1-09 | Overview button | phone only (not displayed from 1024). `button.ov-btn` 44 tall, padding 0 14 0 8, 10 radius, 1.5 `--ring` edge, clear, `--ink` 15/600 "Overview", 8 gap, named "Overview, today 1 of 3 habits done" |
| K1-10 | Overview ring | `span.ov-ring` holding a 28 by 28 ring of three segments, the first thick amber, the others thin `--ring`, no number, no today circle |
| K1-11 | Date | `time.date[datetime=2026-10-10]` "Saturday 10 October", 14px/20px `--ink-soft`, no wrap. Its own line on a phone, 16px at the right end on a desktop |
| K1-12 | Band card | desktop only (not displayed below 1024). `section.band` grid of 180 and the rest, 20 apart, `--surface`, 1 px `--line`, 16 radius, padding 14 20 12 |
| K1-13 | Band head and Year | `div.band-head` raised 10 (margin-top -10), `h2#h-ov` "Last 12 weeks" 16/24 600 no wrap at the left, `button.btn-all` "Year" at the right of the same line. 44 tall, at least 44 wide, padding 0 12, 1.5 `--ring` edge, 10 radius, clear, `--ink` 15/600, named "Year view, all habits" |
| K1-14 | Band hint | `p.hint` "Tap a day to change it." 14/20 `--ink-soft`, 2 below the head |
| K1-15 | Band legend | at the foot of the left column (margin-top auto, 6 bottom padding). "None", four 22 px rings (0, 1, 2 and 3 of 3, the last with the core), "All", 12/16 `--ink-soft`, 6 apart, aria-hidden |
| K1-16 | Band grid | `div.ovg-cols` role group labelled by `h-ov`, column flow, a 22 px label column and 12 equal week columns, rows 18 then 7 of 44 |
| K1-17 | Month axis | `div.og-mo` "Jul" over week 1, "Aug" week 3, "Sep" week 8, "Oct" week 12, the rest empty. 12/16 600 `--ink-soft`, 6 left padding, no wrap, aria-hidden |
| K1-18 | Weekday axis | seven `div.og-wd` "M T W T F S S" down the label column, 12/16 600 `--ink-soft`, centred on their rows, aria-hidden |
| K1-19 | Band day cells | 83 `button.hc` 52 by 44, centred in their columns, 12 radius, clear, each a 40 px ring. Names "Mon 20 Jul, 2 of 3 habits" to "Sat 10 Oct, 1 of 3 habits" |
| K1-20 | Ring segments | three 98 degree arcs on radius 15, clockwise from 12 o'clock in list order. Not done `--ring` 1.5, done `--amber` 3.5, no fill |
| K1-21 | Full days | the 18 days with all three done. An `--amber` core of radius 11.5 and the number in `--on-amber` 700 |
| K1-22 | Ring numbers | `text.c-num` 16px 600 `--ink-soft`, centred on the alphabetic baseline at y 20, dropped .352em, proportional figures |
| K1-23 | Today cell | Sat 10 Oct, aria-current date, a `--ink` circle of radius 19.2 at 1.4, its first segment thick (Read is done) |
| K1-24 | After today | Sun 11 Oct, an empty `span.hc`, aria-hidden, nothing drawn |
| K1-25 | Banners | `div.banners` empty and not displayed |
| K1-26 | Hidden heading | `h2#h-habits.sr` "Habits", clipped to 1 by 1, labelling `ul.rows` |
| K1-27 | List frame | `div.frame-wrap` and `div.frame`. `--surface`, 1 px `--line`, 16 radius, as tall as its three rows, no scroll, no fade shown, two 1 px sentinels round `ul.rows` |
| K1-28 | Row layout, phone | `li.row` grid, the name line ("name name name") over "stats year done", column gap 8 (6 at 360), row gap 12, padding 12 by 14 (12 by 12 at 360). Rows divided by 1 px `--line` |
| K1-29 | Row layout, desktop | one line, columns name, bin 56, stats 200, Year, Done today, 12 apart, padding 12 12 12 20 |
| K1-30 | Habit names | `h3.r-name#rn-N` "Read 20 pages", "Stretch 10 minutes", "No phone after 11pm", 16px/22px 600 (17px/24px desktop), `--ink`, wraps anywhere |
| K1-31 | Bins | `button.btn-bin` 44 circle, clear with a clear 1.5 edge, Phosphor trash 20 px in `--ink-soft`. Phone, at the right end of the name line, pulled 10 up and 10 right. Desktop, at the left of its 56 column. Named 'Delete "<name>"' |
| K1-32 | Number labels | `span.lbl` "Current" and "Best", 12/16 600 `--ink-soft`. Stats 14 apart (12 at 360, 20 desktop), Current at least 96 wide on a desktop |
| K1-33 | Current | `b.num` 22/26 700 `--amber`, tabular, letter-spacing -0.01em, then `span.unit` "days" 13/16 `--ink-soft` 4 to its right on the baseline. Read 4, Stretch 2 |
| K1-34 | No streak yet | No phone's `span.none` "No streak yet", 13/16 600 `--ink-soft`, 3 top padding |
| K1-35 | Best | `span.stat.best b.num` 22/26 600 `--ink`. 9, 5, 14 |
| K1-36 | Year buttons | `button.btn-year` "Year", 44 tall, at least 44 wide, padding 0 12 (0 10 at 360), 1.5 `--ring` edge, 10 radius, clear, `--ink` 15/600, named "Year view, <name>" |
| K1-37 | Done today, not pressed | Stretch and No phone. `button.btn-done` 44 tall, padding 0 12 0 9 (0 10 0 8 and 14px text at 360), 7 gap (6 at 360), outline like Year, a 22 px dot with a 2 px `--ring` edge and its check hidden, "Done today" |
| K1-38 | Done today, pressed | Read. `--amber` fill and edge, `--on-amber` text, the dot filled `--on-amber` with the amber Phosphor check (bold, 13 px) shown |
| K1-39 | Composer | `form.composer[novalidate]` at the bottom of the column, `--surface`, 1 px `--line`, 16 radius, padding 10 12 12 (12 desktop) |
| K1-40 | Field label | `label.add-label[for=nh]` "New habit" 14/20 600. Phone, above the field, 6 apart, 2 in from the left. Desktop, left of the field, centred on it, no wrap, 16 from the field's column |
| K1-41 | Field | `input#nh.input` 48 tall, padding 0 14, 10 radius, 1.5 `--ring` edge, `--field` fill, `--ink` 16px, empty, no placeholder, autocomplete off, spellcheck false, described by `nh-msg` |
| K1-42 | Add | `button#add-btn.btn.btn-primary[type=submit]` "Add" with the Phosphor plus 20 px, 48 tall, padding 0 18, 10 radius, `--amber` fill, `--on-amber` 16/600, 8 right of the field |
| K1-43 | Message line | `p#nh-msg.field-msg` with aria-live polite, hidden and empty |
| K1-44 | Nothing else | no dialog shown, no banner, no other control or text anywhere on the page |

### P1, golden `./docs/design/day-editor.html` (Tuesday 22 September open, 360, 390 and 1280)
| # | Element | Must match the golden |
|---|---|---|
| P1-01 | Layers, phone | P3 as a full sheet under `--scrim-soft`, then P1 as a bottom sheet. P3's 22 September cell is the open cell and lies in sight above the sheet, P3 not scrolled |
| P1-02 | Layers, desktop | K1 with its band under `--scrim-soft`, the band's 22 September the open cell, P1 a centred dialog 440 wide |
| P1-03 | Open day cell | `button.hc.is-open`, `--raise` fill, a 1.5 `--amber` inset edge, its thin segments in `--ink-soft` |
| P1-04 | Sheet, phone | `dialog.dlg-day` the full width at the bottom. `div.dlg-box` `--surface-2`, 1 px `--line` with no bottom edge, 20 radius on the top corners, padding 16 16 24, at most 85% of the viewport tall, the dialog shadow |
| P1-05 | Dialog, desktop | 20 radius all round, 1 px `--line` all round, padding 20, the dialog shadow |
| P1-06 | Head | `div.day-head` grid 56, the text, 44, 12 apart, centred |
| P1-07 | Mini ring | `div.day-mini` 56 by 56, three segments with the third (No phone) thick amber, no number, no core, no today circle, aria-hidden |
| P1-08 | Title | `h2#day-title` "Tuesday 22 September" 17/24 600 `--ink` |
| P1-09 | Subtitle | `p#day-sub.dlg-sub` "1 of 3 habits" 14/20 `--ink-soft`, 2 below |
| P1-10 | Close | `button.icon-btn` 44 circle, clear, Phosphor x 20 px in `--ink-soft`, named "Close" |
| P1-11 | Tick list | `ul.day-list` 12 below the head, no bullets, ticks 2 apart |
| P1-12 | Ticks | three `button.tick` the full width, at least 60 tall, padding 8 12, 12 radius, clear, a grid of the 28 box and the name over the numbers, 12 apart, left aligned. Named by the habit, state in aria-pressed |
| P1-13 | Box, off | Read and Stretch. `span.tbox` 28 circle, 2 px `--ring` edge, check hidden |
| P1-14 | Box, on | No phone. `--amber` fill and edge, the bold check 16 px in `--on-amber` |
| P1-15 | Tick names | `span.tname` 16/22 600 `--ink` |
| P1-16 | Tick numbers | `span.tstat` 13/18 `--ink-soft`, 12 apart. `span.tcur` "Current 4 days" and "Current 2 days" in `--amber` 600, "No streak yet" in `--ink-soft` 600, then "Best 9", "Best 5", "Best 14" |
| P1-17 | Focus not drawn | no focus ring on any tick (the capture blurs, R36 proves the focus) |

### P2, golden `./docs/design/year-view.html` (Read 20 pages, 360, 390 and 1280)
| # | Element | Must match the golden |
|---|---|---|
| P2-01 | Sheet, phone | `dialog.dlg-full.dlg-year` the whole viewport, no radius, no edge, no shadow, `--surface-2`, K1 hidden under it |
| P2-02 | Dialog, desktop | centred, 980 wide, at most the viewport less 48 tall (752 at 800), 1 px `--line`, 20 radius, the dialog shadow, over K1 under `--scrim` |
| P2-03 | Sheet head | `div.sheet-head` padding 12 16 (12 at 360, 16 24 12 on a desktop), 1 px `--line` under it |
| P2-04 | Title row | `div.head-top`, the text block 9 from the top. `h2#yr-title` "Read 20 pages" 19/26 700 `--ink`, `p#yr-sub.dlg-sub` "The last 12 months" 14/20 `--ink-soft`, Close pulled 6 right |
| P2-05 | Numbers | `div.yr-mid` 8 below, the numbers left and Delete habit right, bottoms aligned. `p.yr-stats` 20 apart. "Current" 12/16 600 over `b.num` "4" 34/38 700 `--amber` and "days". "Best" over "9" 26/32 600 `--ink` |
| P2-06 | Delete habit | `button.btn-del[type=button]` 44 tall, padding 0 12 0 10, 10 radius, clear edge and fill, `--ink-soft` 15/600, the trash 20 px, 6 gap, "Delete habit" |
| P2-07 | Hint | `div.yr-tools` 8 below, `p.hint` "Tap a day to mark it done or not done." 14/20 `--ink-soft` |
| P2-08 | Legend | `p.yr-legend` 12/16 `--ink-soft`, aria-hidden. A 16 px amber mini, "Done", a 16 px mini with a 2 px `--ring` edge, "Not done", 6 apart and 6 after "Done" |
| P2-09 | Body | `div.sheet-body` scrolls inside, padding 12 16 24 (16 24 24 on a desktop), at the top (October 2026 first), soft shadows at an edge with more behind it |
| P2-10 | Months layout | one month across on a phone, 20 apart. Three across on a desktop in 7 columns of 40, gaps 24 by 40 |
| P2-11 | Month titles | `h3` "October 2026" down to "October 2025", 15/22 600 `--ink`, 4 below, 2 in |
| P2-12 | Weekday letters | seven `span.mwd` "M T W T F S S", 11/16 600 `--ink-soft`, centred, 2 below |
| P2-13 | Lead cells | 39 empty `span.yc.lead` |
| P2-14 | Day cells | `button.yc` 44 tall on a phone (40 by 40 on a desktop), a bead of 36 (34 at 360, 32 on a desktop) with a 2 px edge |
| P2-15 | Not-done beads | 116. `--surface-2` fill, `--ring` edge, the number in `--ink` 600 15px (14px desktop), SVG text centred, dropped .352em, proportional |
| P2-16 | Done beads | 250. `--amber` fill and edge, the number in `--on-amber` 700 |
| P2-17 | Thread | an 8 px `--amber` bar through the centres between consecutive done days, each cell drawing its own half, so a run across a week or month edge leaves a stub |
| P2-18 | Today | 10 October 2026, done, its halo 3 px `--surface-2` then 1.5 px `--ink`, aria-current date |
| P2-19 | Closed days | 11 to 31 October 2026, the number alone in `--closed` 500, no edge, no fill, not a button |
| P2-20 | Empty days | 1 to 9 October 2025, nothing drawn |
| P2-21 | Day names | "Mark Fri 10 Oct 2025 as done" to "Mark Sat 10 Oct 2026 as done", state in aria-pressed |

### P3, golden `./docs/design/overview.html` (Last 12 weeks, 360 and 390. The 1280 render is reference only)
| # | Element | Must match the golden |
|---|---|---|
| P3-01 | Sheet | `dialog.dlg-full.dlg-ov` the whole viewport, `--surface-2`, K1 hidden under it |
| P3-02 | Head | `div.ov-head`, 8 apart. The text block 9 from the top with `h2#ov-title` "Last 12 weeks" 19/26 700 and `p.hint` "Tap a day to change it.", then Year (outline, 44 tall, named "Year view, all habits"), then Close pulled 6 right. Head padding 12 16 (12 at 360), `--line` under it |
| P3-03 | Grid | `div.ovg-rows` role group labelled by `ov-title`, a 34 px month column and 7 equal columns (43.1 wide at 360, about 46.3 at 390) |
| P3-04 | Weekday letters | seven `div.og-wd` "M T W T F S S" 12/16 600 `--ink-soft`, centred, 4 below |
| P3-05 | Month column | `div.og-mo` "Oct" row 1, "Sep" row 5, "Aug" row 10, "Jul" row 12, the rest empty, 12/16 600 `--ink-soft`, 2 in, centred on its row |
| P3-06 | Rows | twelve weeks newest first. Row 1 Mon 5 to Sat 10 October and an empty Sun 11, row 12 Mon 20 to Sun 26 July |
| P3-07 | Cells | `button.hc` 48 tall (46 at 360) with a 42 px ring (40 at 360), the number 16.8 px apparent at 390, 16 at 360 |
| P3-08 | Rings | as K1-20 to K1-23 on `--surface-2`, the today circle on Sat 10 October |
| P3-09 | Empty cell | Sun 11 October, an empty `span.hc` |
| P3-10 | Legend | under the grid, right aligned, 12 below, 6 in. "None", four rings, "All" |
| P3-11 | Body | `div.sheet-body` at the top, padding 12 16 24 (12 at the sides at 360) |

### P4, golden `./docs/design/overview-year.html` (All habits, 360, 390 and 1280)
| # | Element | Must match the golden |
|---|---|---|
| P4-01 | Sheet, phone | `dialog.dlg-full.dlg-all` the whole viewport over P3 (hidden under it), `--surface-2` |
| P4-02 | Dialog, desktop | centred 980 wide over K1 under `--scrim`, K1 showing only at the header and about 5 px at each side |
| P4-03 | Head | `div.head-top`, `h2#all-title` "All habits" 19/26 700, `p#all-sub.dlg-sub` "The last 12 months", Close |
| P4-04 | Tools | `div.yr-tools` with `p.hint` "Tap a day to change it." and the legend ("None", four rings, "All") on one line |
| P4-05 | Months | October 2026 down to October 2025, `h3` 15/22 600. One across on a phone, three across on a desktop in 294 px columns, gaps 24 by 20 |
| P4-06 | Grid | `div.mgrid` 7 equal columns on a phone, 7 of 42 on a desktop. Weekday letters 11/16 600 `--ink-soft` |
| P4-07 | Cells | `button.hc` 48 tall with a 42 ring at 390 (46 and 40 at 360), 44 tall with a 40 ring on a desktop, numbers 16px 600 |
| P4-08 | Rings | as K1-20 to K1-23, 366 of them, the today circle on Sat 10 October 2026. Names "Fri 10 Oct 2025, 3 of 3 habits" to "Sat 10 Oct 2026, 1 of 3 habits" |
| P4-09 | Closed days | 21 `span.hc.closed`, the number alone (`text.c-num.dim`) in `--closed` 500 |
| P4-10 | Empty and lead cells | 9 `span.hc.blank`, 39 lead cells, nothing drawn |
| P4-11 | Body | at the top, the soft edges of P2-09 |

### M1, golden `./docs/design/delete-dialog.html` (Delete "Stretch 10 minutes"? from its bin, 360, 390 and 1280)
| # | Element | Must match the golden |
|---|---|---|
| M1-01 | Page behind | K1 unchanged and inert. It cannot be clicked or focused |
| M1-02 | Backdrop | `--scrim` over the whole viewport (the native backdrop) |
| M1-03 | Dialog | `dialog.dlg-del` opened with showModal, role alertdialog, aria-modal true, labelled by `del-title`, described by `del-body`, centred both ways, `min(400px, 100vw - 32px)` wide (328 at 360, 358 at 390, 400 at 1280) |
| M1-04 | Box | `div.dlg-box` `--surface-2`, 1 px `--line`, 20 radius, 20 padding, the dialog shadow (0 24px 64px rgba(6, 7, 9, 0.55) and 0 2px 8px rgba(6, 7, 9, 0.4)) |
| M1-05 | Title | `h2#del-title` `Delete "Stretch 10 minutes"?` with straight quotes and the invisible U+2068 and U+2069 round the name, 17/26 600 `--ink`, wraps anywhere |
| M1-06 | Body | `p#del-body` "Its history is deleted too." 16/24 `--ink-soft`, 8 below the title, 20 above the buttons |
| M1-07 | Buttons row | `div.dlg-actions`, two equal columns 12 apart |
| M1-08 | Cancel | left. `button.btn.btn-secondary[type=button]` "Cancel", 48 tall, 10 radius, clear with a 1.5 `--ring` edge, `--ink` 16/600 |
| M1-09 | Delete habit | right. `button.btn.btn-danger[type=button]` "Delete habit", 48 tall, `--danger` fill, `--on-amber` 16/600, the only filled control |
| M1-10 | Focus not drawn | Cancel has focus on open but no ring shows in the capture (it blurs, R13 proves the focus) |

### S1, golden `./docs/design/today-empty.html` (a fresh day, 360, 390 and 1280)
| # | Element | Must match the golden |
|---|---|---|
| S1-01 | Shared frame | K1-01 to K1-09, K1-11 to K1-14, K1-16 to K1-18, K1-22, K1-24 to K1-26 and K1-39 to K1-44 hold. The rows below replace the rest. Where a listed K1 row and a row below both give a value, the row below wins and the K1 row holds for its style and layout only. In S1 that is K1-09, whose name "Overview, today 1 of 3 habits done" is S1-07's "Overview, today 0 of 0 habits done". Changed 2026-10-13 after the plan check (F9), the row first left open which value wins |
| S1-02 | Empty list | `li.empty` in the frame, a grid of 96 and the rest, 16 apart, padding 16, centred. Its 96 by 96 svg holds a dotted orbit (radius 50, `--ring` 1.5, dashes 2 and 6, round caps, no fill) round a `--track` core (radius 18, 2 stroke, no fill) |
| S1-03 | Lead and line | `p.lead` "No habits yet." 17/24 600 `--ink`, `p.line` "Add one you want to do every day." 14/20 `--ink-soft`, 4 below |
| S1-04 | Band rings | 83 day buttons each with one thin `--ring` circle of radius 15 and its number, named "<Ddd D Mon>, 0 of 0 habits", no core anywhere |
| S1-05 | Today | Sat 10 October with the today circle and aria-current, Sun 11 October an empty cell |
| S1-06 | Legend | "None", one 22 px ring of one thin circle, "All" |
| S1-07 | Overview button | its ring one thin circle, named "Overview, today 0 of 0 habits done" |
| S1-08 | Frame | holds only the empty state, as tall as it, no fade |
| S1-09 | Composer | enabled, empty, no message, where K1 has it |

### S3, golden `./docs/design/today-full.html` (twelve habits, 360, 390 and 1280)
| # | Element | Must match the golden |
|---|---|---|
| S3-01 | Shared frame | K1-01 to K1-09, K1-11 to K1-19, K1-22 to K1-26 and K1-28 to K1-38 hold for twelve rows. The rows below replace the rest. Where a listed K1 row and a row below both give a value, the row below wins and the K1 row holds for its style and layout only. In S3 those are K1-09 (the name, S3-09), K1-15 (the legend's rings, S3-05), K1-19 (the day names, S3-09), K1-30 (the names, S3-02) and K1-33 to K1-35, K1-37 and K1-38 (the numbers and the Done today states, S3-02). Changed 2026-10-13 after the plan check (F9), the row first left open which value wins |
| S3-02 | Twelve rows | the sample's twelve habits in order, with the Current, Best and Done today states of the `@R6` twelve-habit table |
| S3-03 | Frame scrolls | `div.frame` fills the space between the header (or the band) and the composer and scrolls inside, at its top. `div.frame-wrap.more-below` shows the bottom fade (36 tall, from 1 in on the left to 12 in on the right, `--fade-bot`), and no top fade |
| S3-04 | Twelve-segment rings | every band ring and the Overview ring have twelve 21 degree arcs, done thick amber, not done thin `--ring`. No band day has all twelve done, so no band ring has a core (the golden's only core is the legend's last ring, checked while planning) |
| S3-05 | Legend | "None", rings for 0, 4, 8 and 12 of 12 (the last with the core), "All" |
| S3-06 | Composer full | `form.composer.is-full`. The label in `--ink-soft`. The field disabled, `--surface-2` fill, `--line` edge, `--ink-soft` text. Add disabled, `--surface-2` fill, `--ink-soft` text, the not-allowed cursor |
| S3-07 | Note | `p#nh-msg.field-msg.note` "You track 12 habits, the most this app holds. Delete one to add another." 14/20 `--ink-soft`, above the field, 8 over it, 2 in |
| S3-08 | Field position | the field's box at each width equals K1's, because the note grows the composer upward |
| S3-09 | Names | the Overview button "Overview, today 7 of 12 habits done", band days such as "Mon 20 Jul, 7 of 12 habits" |
| S3-10 | No page scroll | the page is one viewport tall at each width (R5) |

### States sheet, golden `./docs/design/states.html` (S2, S4 and S5 frames, checked by computed style, no pixel diff, at 360 and 1280)
| # | Specimen | Must match the specimen in the live app |
|---|---|---|
| ST-01 | S2, Add pressed with no name | `p.field-msg.err` "Name the habit first." 14/20 in `--danger`, margin 0 0 8 2, above the field. The field has aria-invalid true and a `--danger` edge, the rest of the composer as K1. The field does not move (the message grows the composer upward) |
| ST-02 | S2, a name over 40 characters | the field holds "Read twenty pages of a novel before bed each night" (50 characters), the message "Keep it to 40 characters or fewer.", styled as ST-01 |
| ST-03 | S2, a name already tracked | the field holds "read 20 pages", the message "You already track this habit.", styled as ST-01 |
| ST-04 | S4, save warning | `div.banner.warn[role=status]` holding only `p` "Your habits are not being saved on this device. Changes will be lost when you close this tab.". `--amber-wash` fill (#2D271C over the page), 1 px `--amber` edge, 16 radius, padding 12 16, 15/22 `--ink`, the text with 1 px top and bottom padding, no button. In `div.banners` between the band (desktop) or the header (phone) and the list |
| ST-05 | S5, saved habits could not be read | `div.banner.note[role=status]` `--surface-2`, 1 px `--line`, 16 radius, padding 4 4 4 16, its text 15/22 with 10 px top and bottom padding, then the 44 px "Dismiss note" icon button with the Phosphor x. Above S1's empty list, 12 apart |
| ST-06 | Sheet chrome, not built | the sheet title "Streaky Habit states", the frame headings, `main.sheet` and its padding and gaps, the `.spec` and `.stack` grids, and the specimen ids `n1` to `n3` and `m1` to `m3`. None of them exists in the app |

## Fidelity gate
*(FE module, Chromium only (ledger S5 row 2). Run by the fidelity finder after functional is green in both engines.)*

- **Harness.** The sdlc browser-harness in frozen mode, run directly, `python "$CLAUDE_PLUGIN_ROOT/harness/fidelity.py"` (sdlc 2.6.0 when this was written, on this machine `{sdlc}/harness/fidelity.py`). It must accept `--candidate-init-script`, `--candidate-after-load` and `--fixed-time` (2.6.0 does, read while planning). The first run records the plugin version it ran from in `findings/fidelity.md`. The harness renders both sides in headless Chromium with `--force-color-profile=srgb` and `--hide-scrollbars`, and takes its screenshots with animations disabled.
- **Time.** Every run passes `--fixed-time 2026-10-10T09:00:00`, a local datetime. The harness sets no time zone, so the page sees `09:00` on Saturday 10 October in the machine's zone.
- **Viewport, dpr, scheme, page.** The viewports of the table below. `--dpr 1`. `--color-scheme dark`, the harness default. No rule of `system.css` or of any golden reads `prefers-color-scheme` (only the tab icon does, and a page capture does not draw it), so the scheme changes no pixel, and the control below would show it if it did. Full page (the page never scrolls, so the capture is the viewport).
- **Threshold and budget.** Per-pixel threshold 0.1 (the harness default). **Budget 0 mismatched pixels, and `dimensions_match` true.** The candidate uses the same CSS, the same DOM and the same system fonts on the same engine as the golden, so any pixel over 0.1 is a real difference. The budget is never widened to absorb a count. A non-zero count is a finding.
- **Control and baseline** (constitution, Gates and evidence). Before the 23 captures, each golden is compared with itself at each viewport the gate uses for it (the golden served read-only by the app's server at `/docs/design/<screen>.html`), and each report must show 0 and `dimensions_match` true. The negative control is today.html against the app with no state flag (the app shows S1), which must show a count above 0 at each of the three viewports. Both controls run in the same harness version and the same session as the captures.
- **Test-side state scripts** (in `tests/browser/fidelity/`, never shipped, never loaded by the app).
  - `seed-sample.js` and `seed-twelve.js`, passed as `--candidate-init-script`. Each is the exact text of `CLIPBOARD_STANDIN` (the clipboard stand-in, How these scenarios run), then one statement, `localStorage.setItem("streaks.state", <text>)`, the text `{"version":1,"habits":[...]}` of the first three or all twelve v1.1.0 sample habits as `{ name, done }` with date keys. They run before the app's scripts.
  - `open-day-editor.js` (below 1024 px it clicks Overview and then P3's 2026-09-22, from 1024 px the band's 2026-09-22), `open-year-view.js` ("Year view, Read 20 pages"), `open-overview.js` (Overview), `open-overview-year.js` (the band's Year from 1024 px, Overview and then P3's Year below), `open-delete-dialog.js` (the bin 'Delete "Stretch 10 minutes"', then it checks the title `Delete "`, `\u{2068}`, `Stretch 10 minutes`, `\u{2069}`, `"?`), passed as `--candidate-after-load` (the harness runs each as the body of an async function after load). Each first checks that the stand-in is in place (when `navigator.clipboard` exists, `Clipboard.prototype.writeText` is not the browser's native function) and throws before any click when it is not. Each clicks with `element.click()` (detail 0, so neither guard of R13 and R14 holds it), throws unless its state of the `@R28` table is reached, and ends with `document.activeElement.blur()`. The blur is required because the goldens draw no focus, and focus moved by script without a prior pointer gesture matches `:focus-visible` in Chromium (1.0 D12, measured as the whole M1 diff in 1.0).
  - `tests/browser/test_fidelity_inputs.py` proves each script (the `@R28` scenario above).
  - Why the stand-in sits in the seed scripts (constitution, Browser gates). The five after-load scripts click, so the capture drives the app, and the stand-in must be in the context before the page loads. The 2.6.0 harness adds only its own freeze script and the one `--candidate-init-script` file to the candidate context, so the seed script is the one place it can go. The golden side and the K1, S1 and S3 captures press nothing. Added 2026-10-13 after the plan check (F4).
- **Captures.**

  | Screen | Golden | Viewports | State flags |
  |---|---|---|---|
  | K1 | `./docs/design/today.html` | 360x780, 390x844, 1280x800 | `--candidate-init-script tests/browser/fidelity/seed-sample.js` |
  | P1 | `./docs/design/day-editor.html` | 360x780, 390x844, 1280x800 | `seed-sample.js` and `--candidate-after-load tests/browser/fidelity/open-day-editor.js` |
  | P2 | `./docs/design/year-view.html` | 360x780, 390x844, 1280x800 | `seed-sample.js` and `open-year-view.js` |
  | P3 | `./docs/design/overview.html` | 360x780, 390x844 | `seed-sample.js` and `open-overview.js` |
  | P4 | `./docs/design/overview-year.html` | 360x780, 390x844, 1280x800 | `seed-sample.js` and `open-overview-year.js` |
  | M1 | `./docs/design/delete-dialog.html` | 360x780, 390x844, 1280x800 | `seed-sample.js` and `open-delete-dialog.js` |
  | S1 | `./docs/design/today-empty.html` | 360x780, 390x844, 1280x800 | none (each harness render is a fresh context with empty storage) |
  | S3 | `./docs/design/today-full.html` | 360x780, 390x844, 1280x800 | `--candidate-init-script tests/browser/fidelity/seed-twelve.js` |

  23 captures. P3's 1280 render is reference only (MANIFEST), because P3 cannot open from 1024 px.
- **Command** (one per screen and viewport), from the project root with the app served.
  `python "$CLAUDE_PLUGIN_ROOT/harness/fidelity.py" --golden ./docs/design/<screen>.html --candidate http://127.0.0.1:<port>/ --viewport <WxH> --dpr 1 --color-scheme dark --fixed-time 2026-10-10T09:00:00 <state flags> --out ./docs/modules/app/qa/fidelity-<screen>-<WxH>/<datetimestamp>/`
- **Evidence.** `./docs/modules/app/qa/fidelity-<screen>-<WxH>/<datetimestamp>/` (`golden.png`, `candidate.png`, `diff.png`, `styles.json`, `report.json`), and the controls in `./docs/modules/app/qa/fidelity-controls/<datetimestamp>/`. Verdict in `./docs/modules/app/findings/fidelity.md`.
- **Method.** Screenshot both, pixel diff at the threshold above, the per-element computed-style check from `styles.json`, then every checklist row of the screen.
- **states.html** (no pixel diff, it is a specimen sheet, not a screen). At 360 x 780 and at 1280 x 800, the tester opens `states.html` from its file path and the running app in the same state, reached with real gestures. S2 by submitting on the sample day an empty field, then "Read twenty pages of a novel before bed each night", then "read 20 pages". S4 by the sample day with driver D-a and one press of "Done today, Stretch 10 minutes". S5 by storage "{". For each ST row it compares the specimen element's and the live element's computed `color`, `background-color`, border colours, styles and widths, `border-radius`, `padding`, `margin`, `font-size`, `font-weight` and `line-height`, and for buttons `width` and `height`. Specimen-only styling is left out. `main.sheet`, `.spec`, `.stack` and their headings, and the S5 frame's `div.frame` (the app's frame sits in `div.frame-wrap` with its sentinels, so `li.empty` and its children are compared instead).
- **Verdict.** 1-to-1 only, with no additions, subtractions or modifications.

## Regression
- Re-run the Node suite (`node --test "tests/**/*.test.js"`), the browser suite in Chromium and in WebKit (two runs, two evidence folders), the 23 fidelity captures with their controls and the states check in Chromium, and the `@R27` cold-boot gate in Chromium and in WebKit, in the final parallel all-modules pass. Each engine's pass, fail and skip counts and run time go into `docs/regression/REGRESSION.md`.

## Coverage by R#
Counted from the Gherkin above on 2026-10-13 by the planner, recounted by script after the plan-check fixes. A scenario with two tags counts for both. An outline counts once. ~~167 live scenarios (92 new, 71 changed, 4 unchanged from 1.0)~~ ~~169 live scenarios (94 new, 71 changed, 4 unchanged from 1.0, recounted 2026-10-14, see the last two notes of this paragraph)~~ 175 live scenarios (100 new, 71 changed, 4 unchanged from 1.0, recounted 2026-10-15, see the last note of this paragraph), 18 retired scenarios kept as text, 1 Chromium-only scenario (CO-1). Every live R# has at least one scenario. Changed 2026-10-13 after the plan check (F5), the live gate's control scenario added one new `@R27` scenario (164 and 89 before). Changed 2026-10-13 after the plan re-check (F14), the two successors of the `test_tick.py` tests added one `@R6 @R32` and one `@R32` scenario (165 and 90 before, R6 5 and R32 12 before). Changed 2026-10-14 in execute (planner touch-up, ledger H-03), the `@R36` scenario of P3's room added one new scenario, so the counts became 168 live scenarios (93 new, 71 changed, 4 unchanged) and R36 7 (6 before). Recounted by script. Changed 2026-10-14 in execute (planner follow-up, ruled ORCH), the `@R36` scenario of a gap smaller than a day with twelve habits added one new scenario, so 169 live scenarios (94 new, 71 changed, 4 unchanged), and R36 has 8. Recounted by script. Changed 2026-10-15 in execute (planner touch after step 5), six new scenarios, one each for `@R12`, `@R19`, `@R33`, `@R36`, `@R39` and `@R42`, give the tests of the step 5 solver round their own scenarios, so 175 live scenarios (100 new, 71 changed, 4 unchanged), R12 4, R19 11, R33 7, R36 9, R39 6 and R42 14. The round's eighth backdrop id is a new Examples row of an `@R14` outline, so R14 stays 13. Recounted by script.

| R# | Spec status | Live scenarios | Retired kept | R# | Spec status | Live scenarios | Retired kept |
|---|---|---|---|---|---|---|---|
| R1 | changed | 3 | 0 | R22 | changed | 13 | 1 |
| R2 | changed | 1 | 0 | R23 | changed | 4 | 0 |
| R3 | changed | 3 | 0 | R24 | changed | 2 | 0 |
| R4 | changed | 4 | 0 | R25 | changed | 3 | 0 |
| R5 | changed | 4 | 0 | R26 | unchanged | 3 | 0 |
| R6 | changed | 6 | 0 | R27 | changed | 2 (the live gate and its control, two engines each) | 0 |
| R7 | retired | 0 | 3 | R28 | changed | 4 | 0 |
| R8 | retired | 0 | 4 | R29 | new | 4 | 0 |
| R9 | retired | 0 | 2 | R30 | new | 7 | 0 |
| R10 | changed | 6 | 0 | R31 | new | 5 | 0 |
| R11 | changed | 5 | 0 | R32 | new | 14 | 0 |
| R12 | changed | ~~3~~ 4 (2026-10-15) | 0 | R33 | new | ~~6~~ 7 (2026-10-15) | 0 |
| R13 | changed | 13 | 3 | R34 | new | 6 | 0 |
| R14 | changed | 13 | 1 | R35 | new | 6 | 0 |
| R15 | changed | 12 | 4 | R36 | new | ~~8~~ 9 (6 before 2026-10-14, then 7 with H-03's room, 8 with the gap smaller than a day, 9 from 2026-10-15) | 0 |
| R16 | changed | 9 | 1 | R37 | new | 5 | 0 |
| R17 | changed | 6 | 1 | R38 | new | 5 | 0 |
| R18 | retired | 0 | 2 | R39 | new | ~~5~~ 6 (2026-10-15) | 0 |
| R19 | changed | ~~10~~ 11 (2026-10-15) | 1 | R40 | new | 10 | 0 |
| R20 | unchanged | 1 | 0 | R41 | new | 10 | 0 |
| R21 | changed | 4 | 0 | R42 | new | ~~13~~ 14 (2026-10-15) | 0 |

Scenarios that apply a clarify gate part 2 ruling (each names it in its title, all ruled 2026-10-13 with the recommended answers). CG-10, 6 (the R13 guard). CG-11, 7 (the R14 tap-through guard). CG-12, 1. CG-14, 1. CG-15, 1. CG-16, 2. CG-17, 1. CG-18, 1. CG-19, 1. CG-13 touches habit-logic only (its qa). Changed 2026-10-13 after the plan check (F1), this paragraph first listed them as waiting on open items.

FE element checklist rows. K1 44, P1 17, P2 21, P3 11, P4 11, M1 10, S1 9, S3 10, states sheet 6, 139 in all, covering all nine goldens.

