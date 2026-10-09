---
module: app
kind: code-review
run: regression
status: issues_found
counts: { blocker: 0, warning: 2, info: 4 }
---
# Code review, regression pass: app

Written by the code-review finder (read-only), regression --full under the ORCH economy ruling (ledger row 44). Base: `git diff fa58481 9ebc54e -- src index.html tests`, project HEAD `b5b1f86` (src, `index.html` and tests are identical to `9ebc54e`; `git diff e42eb2f 9ebc54e --stat -- src index.html tests` is empty). `findings/code-review.md` (the first review and its solver section) was not touched. Evidence: `docs/modules/app/qa/regression-code-review/20261009T221155/`.

## Verdict

**issues_found. 0 BLOCKER, 2 WARNING, 4 INFO.** The shipped source in the delta is correct. I found no bug, no unrequested code and no non-goal in the SEC-01 guards, the SEC-02 isolate or the SEC-06 strip, and the habit-logic seam is clean. What is weak is what the tests pin. I planted 21 mutants of the delta in memory and ran them against the committed tests: 15 died, 6 lived. One of the 6 is equivalent today. The other 5 are two real gaps in the SEC-01 tests, both on a requirement the spec states (RG-CR-01 and RG-CR-02). The rest is doc rot of the kind the constitution gives the reviewer to raise: four stale or loose lines in the README, a stale reconcile list in BUILD.md, a stale helper description in qa.md and two over-long comments.

Suites on the current tree: `node --test "tests/**/*.test.js"` 99 pass, 0 fail. `python -m pytest tests/browser -q -p no:cacheprovider` 176 passed, 0 skipped, both conftest servers stopped and refusing connections.

## BLOCKER

None. Checked for the BLOCKER class and clean:
- **Reverse audit.** Every new symbol maps to a dated ORCH note of R13: `DIALOG_GUARD_MS`, `withinGuard`, `dialogOpenedAt`, `dialogPressedAt`, `guardDialogClick`, `swallowTapThrough`, the `openingClick` parameter of `askToDelete` (SEC-01 note and Contracts "Guard window"); `view.containers().page` and `view.confirmButtonOf` (the same guards, BUILD judgment call 6); the `U+2068`/`U+2069` pair (SEC-02 note); `TITLE_STRIPPED` (SEC-06 note). The test helpers map to the same notes. No symbol maps to nothing.
- **Non-goals.** None built. The page guard is a click swallow, not an `inert` attribute and not a `.scrim`. No timer, no clock read of its own (`readToday` is still the only `new Date`), no new copy string, no toast, no network, no `window` property (grep of `src/`).
- **SEC-06 strip, security eye.** Details in "What I checked" below. It removes exactly the 14 code points of the R13 note, it cannot throw, and it touches only the title's copy.
- **`src/view.js` bytes.** 13300 bytes, 0 non-ASCII bytes (read as bytes, not as text). The escapes are `\u{...}` text. `src/app.js`, `src/storage.js`, `src/dates.js`, `src/habits.js`, `src/styles.css`, `index.html` also hold 0 non-ASCII bytes.

## WARNING

### RG-CR-01: the 500 ms window is pinned only to "somewhere from 401 to 600 ms"   (test-strength)
- **File and symbol:** `tests/browser/test_delete.py::test_SEC01_R13_a_click_inside_the_window_is_ignored_and_one_after_it_deletes` (`run_for(GUARD_WINDOW_MS - 100)`, then `run_for(200)`) and `::test_SEC01_R14_the_page_listens_again_once_the_window_has_passed` (the same pair). `tests/browser/conftest.py`: `GUARD_WINDOW_MS`, `let_guard_pass` (`GUARD_WINDOW_MS + 100`). Against `src/app.js`: `DIALOG_GUARD_MS`, `withinGuard`.
- **Issue:** spec R13 says 500 ms and "less than 500 ms". The only tests that look at the edge click at 400 ms (must be ignored) and 600 ms (must act). Every other SEC-01 test presses twice at the same frozen instant (0 ms) or waits the full `let_guard_pass`. So any window length from 401 to 600 ms, and `<` versus `<=`, pass. `GUARD_WINDOW_MS` repeats the number, and "Keep it equal to DIALOG_GUARD_MS in src/app.js" is a comment nothing enforces.
- **Proof (mutants, in memory):** `DIALOG_GUARD_MS = 450` (G-450), `= 600` (G-600) and `<=` in `withinGuard` (G-le) all leave `test_delete.py` at 65 of 65 and the whole suite at 175 passed, 1 skipped (the skip is the sub-path test, which the runner does not serve). 300 (G-300) and 700 (G-700) do die, so the tests bound the window, only loosely. The edge is measurable to the millisecond: `probe_edge.py` (paused clock, same setup as the suite) shows the pristine app holds at 400 and 499 ms and acts at 500, 501 and 600 ms, for the Delete habit guard, the page guard and the keyboard path. G-450 acts at 499, G-600 holds at 500 and 501, G-le holds at 500.
- **Fix:** in the two tests replace the 400 ms and 200 ms steps with `page.clock.run_for(GUARD_WINDOW_MS - 1)` (still ignored) and then `page.clock.run_for(1)` (now acts). Keep `GUARD_WINDOW_MS = 500` as the spec number, so the tests fail for any other constant. The comment "Keep it equal" can then go, because the tests are what enforces it.

### RG-CR-02: the keyboard paths of both guards have no committed test, and spec R13 states one of them   (test-strength)
- **File and symbol:** `src/app.js::guardDialogClick` (no `event.detail` condition on the Delete habit veto) and `swallowTapThrough` (no `detail` condition either). Tests: none. `tests/browser/test_delete.py` has `test_SEC01_R15_enter_on_delete_habit_after_the_window_deletes` (after the window) and `test_SEC01_R14_closing_with_the_keyboard_does_not_hold_the_next_click` (the keyboard does not START the page window), but nothing presses Enter on "Delete habit" inside the window, and nothing sends a keyboard click to the page inside the page window.
- **Issue:** spec R13: "Delete habit ignores any activation (mouse, touch or keyboard) that comes less than 500 ms after the click that opened the dialog". qa.md has no scenario for it either. The behaviour is real (the security re-check measured it: Enter, Tab, Enter at about 250 ms is held, and Tab, Enter at 677 ms deletes), but only in a re-check probe script (`security-recheck/20261009T201546/probe_03_keyboard_and_reopen.py`), not in a test. The page-guard half (a keyboard click on the page inside the window is also swallowed) is recorded in findings/security.md, re-check "Observations (not filed)" item 3, and R13 is silent on it.
- **Proof (mutants, in memory):** G-kbd-delete-open (`if (event.detail > 0 && view.confirmButtonOf(...) && withinGuard(...))`, so a keyboard activation inside the window deletes) lives against `test_delete.py` and against the whole suite (175 passed, 1 skipped). P-kbd-click-passes (`swallowTapThrough` returns early when `event.detail === 0`) lives the same way. `probe_edge.py` row `kbd-delete-guard`: pristine holds at 400 and 499 ms, the mouse-only mutant lets the delete through at 400 ms.
- **Fix:** add one test in the SEC-01 block: under `pause_at`, focus "Delete Stretch 10 minutes", press Enter (dialog opens), Tab, Enter at the same instant, and assert the dialog is open, 3 rows, `write_count` 0 and `stored` unchanged. Then `run_for(GUARD_WINDOW_MS)`, Enter, and assert the delete. Add the matching scenario to qa.md next to "Enter on Delete habit after the window deletes". For the page half, the orchestrator should rule: either pin it (mouse Cancel, then Enter on the focused trash button at the same instant opens nothing) and add one sentence to R13, or leave it unspecified and accept that P-kbd-click-passes lives.

## INFO

### RG-CR-03: README lines that are stale or say more than the code does   (doc rot, fallback owner)
- **File:** `README.md`. Each line checked against the code, the ledger and spec.
  1. **Status table, `app` row, "gates green, closing".** The app is closed (STATE.md, ledger row 43, "CLOSED 2026-10-09"). Fix: "closed 2026-10-09", as the `habit-logic` row says.
  2. **"`src/view.js` owns every DOM lookup and write."** `src/app.js` also reads the DOM (`tick` calls `dayButton.getAttribute("data-date")`, `onDialogClose` reads `event.currentTarget.returnValue`, `onDialogPointerDown` and `onDialogClick` feed `isOutside` with `dialog.getBoundingClientRect()`) and writes it (`onDialogClick` calls `dialog.close("cancel")`). What WR-12 and BUILD judgment call 5 established is that every selector lives in `view.js`. Fix: "owns every selector and builds and updates the page's elements".
  3. **"Known limits" against spec and ledger.** The year-10000 row says "saves a day the app cannot read back". The spec SEC-05 note and findings/security.md SEC-05 say what follows: the next load calls the whole state unreadable and resets every habit with the S5 note. The combining-marks row says "only the user can type it"; the spec (SEC-02 threat-model note) says "only the person typing, or a sibling page on the origin (T9)" can plant such a name. The table also omits two accepted residuals the ledger carries: two open tabs, last save wins (CG-9, ledger Clarify-gate rulings) and blocked or full storage losing changes on reload with no message (CG-5). README "Saved data" says only that the page "keeps working in memory without a message". Fix: "the next load resets the whole list" in the year-10000 row, "typed by the user or planted by another page on the same origin" in the marks row, and two rows for CG-9 and CG-5 (or say the table lists only the limits found by the reviews).
  4. **"176 browser tests and 99 unit tests pass."** True now (run, see Evidence). An absolute count rots on the next added test, and v1.1.0 is planned to add some (ledger row 40). Fix: "all browser and unit tests pass (commands under Test it)", or keep the counts and label them "at 9ebc54e".
- **Proof:** `README.md` lines read against `src/app.js`, `docs/v1.0.0/CHANGE-LEDGER.md` and `docs/modules/app/spec.md`. Symbols the README cites all exist (grep): `localDateKey`, `addDays`, `weekWindow`, `toggleDay`, `currentStreak`, `bestStreak`, `heatmapCells`, `heatLevel`, `monthLabels`, `validateName`, `addHabit`, `deleteHabit`, `readToday`, `checkDay`, `STORAGE_KEY`, `encodeState`, `decodeState`, `loadHabits`, `saveHabits`, `onDialogClose`, `guardDialogClick`, `swallowTapThrough`, `DIALOG_GUARD_MS`, `TITLE_STRIPPED`.

### RG-CR-04: BUILD.md "For the README reconcile" lists do not have the SEC-01 names   (doc rot)
- **File:** `docs/modules/app/BUILD.md`, section "For the README reconcile", the `src/app.js` and `src/view.js` bullets.
- **Issue:** the `src/app.js` bullet does not list `guardDialogClick`, `swallowTapThrough`, `withinGuard` or `DIALOG_GUARD_MS`. The `src/view.js` exports bullet does not list `confirmButtonOf` (added by `12445c9`), and the SEC-06 sentence under it, "the export list is unchanged", sits over a list that is already one export short. Judgment call 6 does name the guard symbols and the README has them, so no reader is misled today. The section calls itself the input of the README reconcile, so the next reconcile (v1.1.0 changes the guard) starts from a stale list.
- **Proof:** `grep -n "^export" src/view.js` shows `confirmButtonOf`; `grep -n "confirmButtonOf\|guardDialogClick\|swallowTapThrough" docs/modules/app/BUILD.md` finds them only in judgment call 6.
- **Fix:** add the four names to the `app.js` bullet and `confirmButtonOf` to the `view.js` bullet, or replace both lists with "the functions and exports of the files (grep `^export`)" so they cannot go stale.

### RG-CR-05: qa.md restates a derived number and an old helper signature   (doc rot)
- **File:** `docs/modules/app/qa.md`, "conftest.py (shared fixtures and helpers)": the SEC-01 paragraph and the `open_app(...)` row.
- **Issue:** the paragraph says `let_guard_pass(page)` is "`page.clock.run_for(600)`". In code it is `GUARD_WINDOW_MS + 100`, so the 600 is a number derived from another number and rots with it (RG-CR-01's fix makes the same point for the tests). The `open_app` row is the 2026-10-08 shape and lacks `base_url` and `count_writes` (added by the code-review round, before `fa58481`, so not part of this delta; `touch` is covered by the dated paragraph below the table).
- **Fix:** "runs the clock past the guard window" instead of 600, and add `base_url=None, count_writes=False` to the row (or say the row is "at least these").

### RG-CR-06: two docblocks are essays and restate what the spec already holds   (comment rule, DRY across code and docs)
- **File and symbol:** `src/view.js::TITLE_STRIPPED` (a 9-line docblock) and `src/app.js::DIALOG_GUARD_MS` (7 lines), plus one sentence of `src/app.js::guardDialogClick`.
- **Issue:** the constitution asks for concise WHY comments and one home for a derivation. The mechanism behind `TITLE_STRIPPED` (an isolate opener in the name takes the title's U+2069, the isolate runs to the end of the line, after a right-to-left letter the quotes land on the wrong side) is in the code comment, in the spec R13 SEC-06 note and again in the SEC-06 threat-model note. The `DIALOG_GUARD_MS` story (the second click lands where the first one left the screen) is in the comment, in R13 SEC-01 and in T7. BUILD.md already points at the comment instead of restating it (judgment calls 6 and 10), which is the right direction, so the duplication is between code and spec. Separately, `guardDialogClick` says the capture phase is used "so that a later listener on the button or the form cannot stop the event before this runs". No such listener exists, and registering it for the bubble phase changes nothing (mutant G-bubble lives the whole suite and is equivalent). A future reader cannot tell whether the capture flag matters.
- **Fix:** keep what the code is and the one non-obvious why in 2 or 3 lines each, with "spec R13 note, SEC-06" and "spec R13 note, SEC-01 and T7" as the pointer. For the capture flag, either drop the hypothetical ("kept in the capture phase so nothing registered later can hide the click") or register in the bubble phase.

## What I checked and how

| Area | Method | Result |
|---|---|---|
| Delta source | read `src/app.js` and `src/view.js` whole, `src/storage.js` as the seam, the three source commits as diffs | no bug. Guards: the `-Infinity` start values make the first window false, each opening restarts it, the veto sits on a capture listener of the dialog, the swallow sits on `.page` so the dialog's own clicks are never held, keyboard clicks (`detail` 0) never start the page window, Cancel, Esc and the backdrop are never held |
| R# trace | each new symbol against the R13 SEC-01/SEC-02/SEC-06 notes, Contracts "Guard window", T7 | all map, no hallucination, no non-goal |
| SEC-06 strip: coverage | extracted the regex source from `src/view.js`, ran it over every code point U+0000 to U+10FFFF (surrogates skipped) | exactly 14 matches: U+001C, U+001D, U+001E, U+0085, U+2029, U+202A to U+202E, U+2066 to U+2069. Equal to the R13 list. The Unicode `Bidi_Control` set is U+061C, U+200E, U+200F plus the two ranges, so the three marks are the only bidi controls not stripped, by design (strong marks, they cannot open or close an isolate) |
| SEC-06 strip: can it throw | `replace` with a literal `/gu` regex on a string; names are strings by `decodeState` and `validateName`; lone surrogates pass through untouched (checked); the `g` regex is only used with `replace`, which resets `lastIndex`, so no shared state; no dynamic pattern, so no backtracking | cannot throw |
| SEC-06 strip: reach | `TITLE_STRIPPED` has one use, `openDeleteDialog`; the stored name, `fillRow`, the trash `aria-label` and storage are untouched (also pinned by the solver's mutants and by `test_SEC06_R13_only_the_titles_copy_loses_the_characters_and_the_habit_named_in_it_is_the_one_deleted`) | title only |
| SEC-06 strip: completeness | read the solver's `probe_12_bmp_sweep.py` and its evidence (every BMP code point, three name shapes, plus a 30336-name pair sweep, exact left edges) | none still moves the quotes. LF, CR and U+2028 were in that sweep. I did not re-run it |
| Tests of the delta | read `test_delete.py` whole, the diffs of `conftest.py`, `live_e2e.py`, the fidelity script and the small test edits; 21 mutants (below); `probe_edge.py` | the controls are real: `overlap_point` asserts the overlap and the hit targets, each tap-through test asserts a bead or Add lies under the second press, the Add test asserts the field keeps its text, every SEC-06 character is in or out of two lists of 14 and 16. Gaps: RG-CR-01, RG-CR-02 |
| Cross-module seam | `git diff de0156a 9ebc54e -- src/dates.js src/habits.js`, and `git diff de0156a HEAD -- src/dates.js src/habits.js tests/dates.test.js tests/habits.test.js tests/purity.test.js` | both empty. App imports only `localDateKey`, `MAX_HABITS`, `addHabit`, `deleteHabit`, `toggleDay`, `dayParts`, `longDate`, `shortDate`, `bestStreak`, `currentStreak`, `heatmapCells`, `monthLabels`, `runContinues`, `weekWindow`, `isDateKey`, `validateName`, and every one is an export. Grep for date and streak arithmetic in app, view and storage: the only clock read is `new Date()` in `readToday`, passed to `localDateKey`. No `getDay`, `% 7`, `toISOString`, `Intl`, no day arithmetic. `storage.js` sorts date keys with the same default `sort()` that `habits.js` `toggledHabit` uses (spec Storage contract), which is a stored-format rule, not a streak rule |
| README | every cited symbol grepped; `node --test` (99), `pytest` (176), the server command and the live-gate command run; limits table against the ledger and spec; CSP string against `index.html` (identical); CSS "three marked changes" against `src/styles.css` (three `Change n` markers); gate numbers against `summary.json` of the official live run (11 of 11) and `findings/fidelity.md` (6 of 6, 71 of 71); `git diff 321329c 9ebc54e -- src index.html` empty, so the fidelity verdict stands | RG-CR-03 |
| Doc drift | spec R13/R14/R15, Contracts, T7 and the SEC-02/SEC-05/SEC-06 notes, qa.md SEC-01/SEC-02/SEC-06 scenarios and conftest table, BUILD.md calls 6 and 10, against the code | consistent apart from RG-CR-04 and RG-CR-05. No `file:line` citation in `src/` or `tests/` (grep); `findings/security.md` keeps point-in-time `file:line` citations, which is an audit record, not a comment |
| Hygiene | byte scan for non-ASCII characters (so no em or en dash) in `README.md`, `CLAUDE.md`, the changed code and tests, BUILD.md; `git log fa58481..9ebc54e` messages | none. No vendor watermark in any commit message |
| Accepted limits | the slow double click past 500 ms, shared-origin read, year 10000, combining-mark overprint, unverified Safari and Firefox | not findings, as ruled |

## Mutants (in memory, `mut.py` of the first review, served from the working tree, no project file written)

Run 1 against `tests/browser/test_delete.py` (65 tests, baseline 65 passed), run 2 against the whole suite for the six that lived.

| Mutant | What it changes | Verdict | Failed |
|---|---|---|---|
| G-450 | `DIALOG_GUARD_MS` 450 | **lived** (whole suite too) | 0 |
| G-600 | `DIALOG_GUARD_MS` 600 | **lived** (whole suite too) | 0 |
| G-le | `withinGuard` uses `<=` | **lived** (whole suite too) | 0 |
| G-kbd-delete-open | Delete habit held only when `event.detail > 0` | **lived** (whole suite too) | 0 |
| P-kbd-click-passes | page swallow ignores clicks with `detail` 0 | **lived** (whole suite too) | 0 |
| G-bubble | `guardDialogClick` in the bubble phase | lived, equivalent today (RG-CR-06) | 0 |
| G-300, G-700 | window 300, 700 | killed | 2, 7 |
| G-no-open-stamp, G-open-stamp-once | opening time never or only once recorded | killed | 6, 5 |
| P-no-stop, P-no-prevent | swallow without `stopPropagation`, without `preventDefault` | killed | 13, 2 |
| P-bubble, P-on-document | swallow in the bubble phase, on the document | killed | 13, 2 |
| P-stamp-always, P-stamp-never-on-delete, P-stamp-only-backdrop | which clicks start the page window | killed | 2, 2, 6 |
| T-strip-whole, T-open-lri, T-close-missing, T-name-lowercased | strip over the finished title, FSI to LRI, no PDI, lower-cased name | killed | 26, 27, 26, 11 |

The SEC-06 regex itself was mutated 22 times by the solver (all killed, `security-solver/20261009T205500/`). I did not repeat those.

## Evidence

Folder `docs/modules/app/qa/regression-code-review/20261009T221155/`:
- `mutants_regression.py`, `run_mutants.py` (the 21 mutants and the runner that feeds them to the first review's `mut.py`), `mutants_output.txt` (run 1), `mutants_survivors_full_suite_output.txt` (run 2).
- `probe_edge.py`, `probe_edge_output.txt`: the 500 ms edge at 400, 499, 500, 501 and 600 ms for the pristine app and four mutants, three trials each (Delete habit guard, page guard, keyboard Delete habit).
- `readme_commands_check.py`, `readme_commands_output.txt`, `live-e2e-check/` (11 screenshots, `steps.json`, `console.json`, `network.json`, `summary.json`): the README server and live-gate commands run as written, 11 of 11, 0 console errors, 0 page errors, 0 requests outside the rule. It wrote into this folder, not into the official `qa/live-e2e/`, and it is not the official gate.
- Suite runs are in `readme_commands_output.txt` (99 unit, 176 browser, and the bare `node --test tests/` failing as the README says).

## Processes

PROCESSES: started, all stopped.
- `node --test` runs (two) and a few read-only `node -e` scripts (byte scan, regex enumeration), all exited.
- `python -m pytest tests/browser`: conftest's two `http.server` children (pid 50956 on 127.0.0.1:21781, pid 51992 on 127.0.0.1:21779), stopped by conftest, which printed that both ports refuse connections.
- Mutant runners (background shells, task ids `bl24hj289` and `b5em3xylc`, python runner pids 6968 and 47756): each ran one in-process server thread and one pytest child per mutant, waited for by the runner, both exited with code 0. A baseline run in the foreground before them.
- `probe_edge.py`: one `http.server` (pid 48208, port 30881) and one headless Chromium, stopped by exact PID with the port-refused check printed.
- `readme_commands_check.py`: one `http.server` (pid 49468, port 7939), stopped by exact PID with the port-refused check printed; `live_e2e.py` closed its own Chromium.
- Final sweep by command line (`Get-CimInstance Win32_Process`, matching python, node, `http.server`, pytest, headless, chrome, and my script and folder names): no python, node, `http.server`, pytest or Chromium process left. The only matches were the sweep's own shell chain and conhost helpers of the desktop app.
- Seen and not mine, not touched: another agent's `python -m pytest tests/browser` (pid 43160) with an `http.server` on port 3182 (pid 48068), present while the mutants ran (so wall times in `mutants_output.txt` are longer than the baseline's) and gone by the final sweep.
- Writes: only through the Write tool, into the evidence folder and this file. Scripts print to stdout, and `live_e2e.py` wrote its own output into `live-e2e-check/`. No heredoc, no redirection. `src/` was never touched (mutants are served from memory; `git status` shows only the untracked evidence folder). The clipboard was never touched.

## Solver (2026-10-09)

Written by the dev solver, ORCH rulings of 2026-10-09 (reversible). Test and doc work only: `src/`, `index.html`, `docs/design/` and `README.md` untouched, so the fidelity and live-gate verdicts stand. The finder's sections above are unchanged. Evidence: `docs/modules/app/qa/regression-solver/20261009T224718/` (`evidence.md`, `mutants_output.txt`, the two extra mutants and their runner).

### Status

| Finding | Status | Commits | Red | Green |
|---|---|---|---|---|
| RG-CR-01 (WARNING) | **RESOLVED** | `3c9afdf` tests, `e26edaa` qa.md | G-450, G-600, G-le (and my G-499, G-501) lived the old tests and each fails 4 of the new edge cases | the shipped code passes all four edge cases; full suite green |
| RG-CR-02 (WARNING) | **RESOLVED** for "Delete habit". The page guard's keyboard half is left unspecified by ruling | `dd86356` test, `b30c6c8` qa.md and spec.md | G-kbd-delete-open lived the old suite and fails the new test | the new test passes on the shipped code; full suite green |
| RG-CR-03 (INFO) | not mine: the orchestrator reconciles the README after the solver | none | n/a | n/a |
| RG-CR-04 (INFO) | **RESOLVED** | `137e90c` | `grep -n "^export" src/view.js` lists 22 names and the old bullet had 21; the old `app.js` bullet lacked four guard symbols | the bullets now hold all of them (checked by reading the list against the grep) |
| RG-CR-05 (INFO) | **RESOLVED** | `1ed506c` | qa.md said `run_for(600)` (also in the SEC-01 comment on `confirm_delete`) and the `open_app` row lacked `base_url` and `count_writes` | the text says `GUARD_WINDOW_MS + 100` and the row lists the signature of `conftest.py::open_app` as it is |
| RG-CR-06 (INFO) | accepted by ruling, not touched; G-bubble still lives and is still equivalent | none | n/a | n/a |

### What changed (for the README reconcile)

- `tests/browser/test_delete.py`: the two window-edge tests press at `GUARD_WINDOW_MS - 1` (ignored, `write_count` 0, `stored` unchanged) and then 1 ms later (acts), and now run for a mouse and a touch, because the ruling named both. New helpers `press_once` and `open_by_press` (`open_by_mouse` calls the second). New test `test_SEC01_R13_enter_on_delete_habit_inside_the_window_is_ignored_and_one_after_it_deletes`. The file has 68 tests (65 before).
- `tests/browser/conftest.py`: the comment on `GUARD_WINDOW_MS` says why the number is written out and not read from `src/` ("Keep it equal" is gone, the edge tests enforce it).
- `qa.md`: two scenarios became outlines at 499 ms and 1 ms more; a new Enter scenario; `let_guard_pass` described by `GUARD_WINDOW_MS + 100`; the `open_app` row complete; dated paragraphs for RG-CR-01 and RG-CR-05.
- `spec.md`, R13 note: one dated sentence that the page guard's keyboard half is unspecified and unpinned (v1.1.0 replaces the time window with a time-free guard).
- `BUILD.md`, "For the README reconcile": `guardDialogClick`, `swallowTapThrough`, `withinGuard`, `DIALOG_GUARD_MS` and `confirmButtonOf` listed.
- README lines this touches (RG-CR-03, the orchestrator's): "176 browser tests" is 179 now (the finder's point 4 already suggests dropping the absolute count). No other README line cites a changed name or number.

### Mutants (finder's runner, `-k test_delete`)

"Before" is the tests of `a3d3ed1`: the finder's own run for the killed ones, and my re-run of the six survivors (same verdicts, baseline 65 passed). "After" is my run against the final tests (HEAD `1ed506c`).

| Mutant | Before | After |
|---|---|---|
| G-450 | lived | KILLED, 4 failed |
| G-600 | lived | KILLED, 5 failed |
| G-le | lived | KILLED, 5 failed |
| G-kbd-delete-open | lived | KILLED, 1 failed |
| P-kbd-click-passes | lived | lives, unspecified by ruling |
| G-bubble | lived, equivalent | lives, equivalent (RG-CR-06) |
| G-499, G-501 (extra) | lived | KILLED, 4 failed each |
| the other 15 | killed (2 to 27 failed) | killed (2 to 27 failed) |

Of the finder's 21: 15 killed before, 19 now. The full per-mutant table with failure counts is in `evidence.md`; the runner's raw output is `mutants_output.txt`.

### Suites

`python -m pytest tests/browser -q -p no:cacheprovider`: 179 passed, 0 skipped (176 before: +2 for the touch variants of the two edge tests, +1 for the keyboard test). `node --test "tests/**/*.test.js"`: 99 pass, 0 fail (unchanged). Both run before every commit and at the end; the credential gate exited 0 before every commit. Fidelity and the live gate were not re-run: there is no `src/` change.

### Observations (not findings)

1. The old touch tests of SEC-01 press twice at one frozen instant, so they never showed that a touch tap's `event.timeStamp` follows Playwright's installed clock. The touch edge cases now do (the same mutants die for a touch as for a mouse).
2. `qa.md` still says "600 ms" in a few places that describe real waits or scenario steps (the Gherkin steps "600 ms pass", the @R27 gate "waits 600 ms for real", the gate's gesture note). They are values of a real pause, not a description of `let_guard_pass`, and `live_e2e.py` derives them the same way (`GUARD_WINDOW_MS + 100`); I left them as RG-CR-05 names the helper only.
3. P-kbd-click-passes (RG-CR-02, page-guard half) and G-bubble (RG-CR-06) still live. That is the ruled state; v1.1.0 replaces the time window, and its tests are the place to pin the new guard's keyboard behaviour.
