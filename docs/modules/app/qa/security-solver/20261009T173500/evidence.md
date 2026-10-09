# Solver evidence: app, security round

Run 20261009T173500, security solver. Base `495937c`. Commits: SEC-01 `12445c9`, SEC-02 `442ca9a`, SEC-03 to SEC-05 `1477ecf`, and the closing docs commit that holds this folder and the "Solver (2026-10-09)" section of `../../../findings/security.md`.

## Method

- Probes run against the working tree, real mouse and touch input, headless Chromium, the clock only pinned to 2026-10-08 12:00 +08:00. Each served the app with its own `python -m http.server <free port> --bind 127.0.0.1`, stopped by PID. Probes write nothing. Where a probe needs the state before a fix, it serves the fixed file with the fix removed in memory (`page.route`), so `src/` is never touched.
- Tests: `python -m pytest tests/browser -q` (starts and stops its own two servers) and `node --test "tests/**/*.test.js"`.
- "Red" for a new test: it fails on the tree without the fix. Two ways, both shown: the test run against the pre-fix `src/` (before the edit), and the code-review finder's mutant runner `mut.py` with this round's mutants (`mutants_security.py`, `run_mutants.py`), which patches the served files in memory and runs the suite. A mutant is KILLED when a test fails. The final pass of every mutant ran on the final tree with `--maxfail 1`.
- Event timing in the tests: Playwright's installed clock moves `Event.timeStamp`, a fixed clock does not (`probe_00`). So the delete tests open the page with `install_time`, freeze the clock for a gesture that must land inside the window (two presses at the same instant on any machine), and pass the window with `page.clock.run_for` and no sleep. Only the cold-boot gate `live_e2e.py`, which uses the real clock by rule, pauses for real (600 ms three times in its delete step).

## probe_00: does page.clock move Event.timeStamp (`probe_00_event_timestamp_and_page_clock.py`)

```
mouse, installed and running: event.timeStamp = [75, 381, 832], gaps 1-2 and 2-3 = [306, 451]
touch, installed and running: event.timeStamp = [65, 376, 829], gaps 1-2 and 2-3 = [311, 453]
mouse, installed and paused: event.timeStamp = [5000, 5000, 5450], gaps 1-2 and 2-3 = [0, 450]
touch, installed and paused: event.timeStamp = [5000, 5000, 5450], gaps 1-2 and 2-3 = [0, 450]
mouse, set_fixed_time: event.timeStamp = [60, 370, 372], gaps 1-2 and 2-3 = [310, 2]
```
Clicks 1 and 2 are 300 ms apart in real time, clicks 2 and 3 are `run_for(450)` apart. Installed and paused: 0 and 450. Fixed: real time.

## SEC-01, part 1: double click or tap on the trash button deletes through the dialog

Pre-fix reproduction, `probe_05f_repro_sample.py` of the audit, on `495937c`:
```
desktop 1440x900, mouse:  single click there -> 3 habits, dialog open.  DOUBLE click there -> ['Read 20 pages', 'Stretch 10 minutes'] dialog open=False
phone 390x844, touch:     DOUBLE tap there   -> 3 habits, dialog open   (borderline width, as the audit said)
phone 412x915, touch:     DOUBLE tap there   -> ['Read 20 pages', 'Stretch 10 minutes'] dialog open=False
```
After the fix, same probe, same commands: 3 habits and the dialog open in all three cases, `stored` unchanged.

New tests, run on the unfixed `src/` before the fix edit: `6 failed, 5 passed` of the 11 `SEC01` tests. The 6 red: the four `test_SEC01_R13_a_double_click_or_tap_on_the_trash_button_cannot_delete` cases (mouse and touch, 1440x900 and 412x915), `..._a_click_inside_the_window_is_ignored_and_one_after_it_deletes` and `..._every_opening_starts_the_window_again`. Each failed at "the dialog is still open" (the second press had confirmed the delete). The 5 green on both trees are the controls that guard against over-blocking: Cancel, Esc and the backdrop at the instant of opening (3), a deliberate click after the window deletes, Enter on "Delete habit" after the window deletes.

Mutants (`mutants_security.py`, S1-*), final tree, `--maxfail 1`:

| Mutant | Verdict |
|---|---|
| S1-window-0 (no guard) | KILLED |
| S1-window-50 | KILLED (`..._a_click_inside_the_window_is_ignored_...` and the page-listens-again test) |
| S1-window-5000 | KILLED (every test that confirms a delete) |
| S1-no-prevent | KILLED |
| S1-first-opening-only | KILLED (the four double-press tests and the re-arm test) |
| S1-inverted | KILLED |
| S1-holds-cancel | KILLED (Cancel at once, and the Cancel double-press tests) |
| S1-bubble-phase | SURVIVED, expected equivalent: a cancelled click cancels the form submit in either phase. The capture phase stays as ruled, so that a later listener on the button or the form cannot stop the event first. |

## SEC-01, part 2 (the coordinator's addition): the second click after the dialog closed

Question asked: does the second press of a double click or double tap on Cancel, on Delete habit or on the backdrop reach the page? Yes.

`probe_01_second_click_after_close.py` on the tree with part 1 only (real input, mouse `dblclick` and two touch taps, 600 ms past the opening window for Delete habit; the three-habit sample and twelve plain habits; points are the centre of the button, or for the backdrop the centre of the first day bead outside the dialog box). Lines that changed data (the other lines say "nothing changed" because the centre of that button has no control under it at that size):

| Size | Backdrop (mouse and touch) | Cancel | Delete habit |
|---|---|---|---|
| 390x844 | ticks Read's Fri 2 Oct bead | nothing under it | nothing under it |
| 412x915 | ticks the same bead | nothing under it | nothing under it |
| 1440x900 | ticks the same bead | nothing under it | nothing under it |
| 375x667 | ticks it | ticks Stretch's Sat 3 Oct bead (done count 57 to 56) | row deleted, then ticks a bead of the row that slid up under the button (mouse run: Stretch 57 to 56; touch run: No phone 33 to 34) |
| 360x640 | ticks it | ticks Stretch's Sat 3 Oct bead | row deleted, then ticks a bead of the row that slid up (mouse run: Stretch 57 to 56; touch run: No phone 33 to 32) |

Example line: `375x667 mouse cancel -> point (111,376) under it now: day bead 2026-10-03 of Stretch 10 minutes; STORED DATA CHANGED by the second press, done counts [56, 57, 33]->[56, 56, 33]`.

Counts with the part 2 fix removed in memory (`--no-page-guard` on both probes, the part 1 fix in place): `probe_01` 36 of 60 cases ticked something with the second press; `probe_02` below, 42 of 60 cases had a point to press and 24 of those changed something the first press does not explain (22 changed stored data, 8 left a dialog open, 6 of them lost the delete). No case in either probe deleted a habit the user had not asked about (the probes compare the surviving names with what the first press alone leaves). The same probes on the final tree: 0 of 60 and 0 of 42.

`probe_02_second_click_on_controls.py --no-page-guard` (the fix of part 2 removed in memory) puts the press where a trash button or a bead lies under the button (18 of the 60 cases have no such point, because nothing lies under that button at that size). What it found: ticked a bead (375x667, 360x640, Cancel and Delete habit), opened another habit's dialog (412x915 and 1440x900, Delete habit), and in 6 mouse cases at those two sizes lost the delete itself (the second click opened a dialog before the first dialog's `close` event ran, and that event then read the reset `returnValue`; the first habit stayed and a dialog for another habit was open). No case deleted a habit the user had not asked about.

The fix (`swallowTapThrough` on `div.page`, capture phase, 500 ms after a mouse or touch click in the dialog, `guardDialogClick` records the press, one helper `withinGuard` shared with the Delete arming). After it, same probes:
- `probe_01` after: all 60 lines "nothing changed" or "rows N to N-1" only (the first press's own effect). No tick, no second dialog.
- `probe_02` after: every case "first press did its job, second press changed nothing".

New tests, mutant `T-no-page-guard` (the pre-part-2 behaviour), `-k test_delete`: `15 failed, 30 passed`. The 15: the six backdrop cases (390x844, 412x915, 1440x900, mouse and touch), the two "backdrop over Add" cases, the four Cancel cases (375x667 and 360x640, mouse and touch), the two Delete habit cases, and `test_SEC01_R14_the_page_listens_again_once_the_window_has_passed`. Each failed because the second press reached the page (a tick, an add, or a second dialog).

Mutants T-*, final tree, `--maxfail 1`:

| Mutant | Verdict |
|---|---|
| T-no-page-guard | KILLED |
| T-no-stop (cancelled but not stopped, delegated handler still ticks) | KILLED |
| T-no-prevent (stopped but not cancelled, Add still submits) | KILLED (only by the two "over Add" cases) |
| T-keyboard-too (a keyboard click starts the guard) | KILLED (only by the Enter case of the keyboard test) |
| T-document-scope (guard on the document, so it also holds clicks in the dialog) | KILLED (the Cancel-after-a-click-in-the-box test and the inside-window test) |
| T-bubble-phase (after the delegated handlers) | KILLED |
| T-delete-only (only Delete habit starts the guard) | KILLED |
| T-never-recorded | KILLED |

## SEC-02: bidi override in a name garbles the confirmation title

Tests before the fix edit (the new override tests plus the title checks already changed to the new text): `15 failed, 148 passed`. The 15: 8 existing tests that now expect the marks (R13 modal, two R14 tests, the four SEC-01 double-press tests, R24 markup, the fidelity state script), and the override tests.

`probe_03_title_order.py` measures where the quotes and the name are drawn (left to right: opening quote, name characters, closing quote, question mark), once with the title line put back to `Delete "${habitName}"?` and once with the fix:

| Name | Before | With the fix |
|---|---|---|
| U+202E then "Reversed text here" | QUOTES MOVED (closing quote at 118, name from 266 down, question mark 110) | in place (name 250 to 231.., closing quote 261, question mark 269) |
| "Read 20 pages", U+202E, " dleiys .gnp" | QUOTES MOVED | in place |
| "a", U+202E, "b", U+202E, "c", U+202E | QUOTES MOVED | in place |
| U+202B (RLE) then "abc def" | QUOTES MOVED | in place |
| U+2067 (RLI) then "abc def" | QUOTES MOVED | in place |
| U+202D (LRO) then "abc def" | in place already | in place (left out of the tests: it does not discriminate) |

New residual found while measuring (not in the audit), with the fix applied:

| Name | With the fix |
|---|---|
| "x", U+2069, U+202E, "y z" | QUOTES MOVED (the U+2069 inside the name closes the title's own isolate) |
| "x", U+2069, U+2069, U+202E, "y z" | QUOTES MOVED |
| "x", U+2029, U+202E, "y z" (paragraph separator) | QUOTES MOVED |
| "x", U+0085, U+202E, "y z" | QUOTES MOVED |
| "x", U+001C, U+202E, "y z" | QUOTES MOVED |
| "x", newline, U+2028, U+202C (PDF), U+2066 (LRI), U+2068 (FSI) variants | in place |

So the isolate holds against unterminated overrides, embeddings and isolate openers, but not against a name that itself contains U+2069 or a paragraph separator. The complete fix is to reject bidi format characters in `validateName` (the audit's alternative), a `habit-logic` and product decision, so it is left open and written into spec R13 and the threat model. The combining-mark overprint stays accepted, as ruled.

Green: `162 passed` (browser), `99 pass` (unit). Bytes: `src/view.js` and `tests/browser/fidelity/open-delete-dialog.js` each hold the escape text `\u{2068}` and `\u{2069}` once, no raw U+2068 or U+2069 (e2 81 a8, e2 81 a9), and no non-ASCII byte at all (checked by a read-only byte count after the edit).

Fidelity of the dialog, harness `fidelity.py` (plugin 2.1.3), the qa.md flags, M1 at both sizes, with the marks in place:
```
390x844 : mismatch_pixels 0 of 443040, dimensions_match true, golden and candidate 390 x 1136
1280x800: mismatch_pixels 0 of 1071360, dimensions_match true, golden and candidate 1280 x 837
```
(run into the git-ignored `harness/_scratch/fidelity-m1-*-sec02/`; `docs/design/` only read.)

Mutants S2-*, final tree, `--maxfail 1`: S2-no-isolate, S2-fsi-only, S2-pdi-only, S2-marks-outside-quotes, S2-lri: all KILLED.

## Counts

| | At start | After SEC-01 part 1 | After SEC-01 part 2 | After SEC-02 and the docs |
|---|---|---|---|---|
| `python -m pytest tests/browser -q` | 127 passed | 138 passed | 157 passed | 162 passed |
| `node --test "tests/**/*.test.js"` | 99 pass | 99 | 99 | 99 pass, 0 fail |

New browser tests: 35 (SEC-01: 30, SEC-02: 5). Stability: `test_delete.py` ran 12 times serially, and 15 times as five parallel processes (three rounds), all green; one earlier red run found a real test race (the `close` event of an Escape is queued and can land after the next opening, which resets `returnValue`), fixed in the tests by waiting for the focus the close handler restores before reopening.

The cold-boot gate `live_e2e.py` (served copy, output in the git-ignored `harness/_scratch/live-e2e-sec01`, `-sec01b`, `-sec02`): 11 of 11 steps pass after each change. The official `@R27` run is the orchestrator's.

## Credential gate

`python -B {sdlc}/harness/credential_sweep.py --staged`, unpiped, exit 0 before each of the four commits (positive control true, negative control 0 false hits).

## Processes and process notes

PROCESSES: none alive that this round started (final sweep in the return message). What was started: `python -m http.server` children of the pytest runs (two per run, stopped by `conftest.py`, which prints that each port refuses connections), one per probe (stopped by PID in a `finally`, which prints the refusal check), one per `serve_and_run.py` call (live_e2e, fidelity), mutant-runner servers (threads inside the runner process) and their pytest children, and the headless Chromium of each. One run of the mutant runner was cut at the shell's 590 s `timeout`; no child of it was alive afterwards (checked by command line). One probe was started in the background by a command typo; it was killed by its exact PID tree (`taskkill /PID 46860 /T /F`, which took its own `http.server` and Chromium with it) and the follow-up sweep showed none of its processes. Another agent's pytest (`-B -m pytest tests/browser -q --tb=line -x`, PID 35644 at that time) and an `http.server` on port 41708 were running during the round and were left alone.

Lapses against the "Write and Edit tools only, no redirects, no heredocs" rule, all inside this round's own lane and harmless: one command piped a probe's output to `> /dev/null` by mistake (discarded output, nothing written), and one `python - <<'EOF'` that printed a line and wrote nothing. The `harness/_scratch/` outputs of `live_e2e.py` and the fidelity harness were written by those tools themselves into the project's git-ignored scratch folder.
