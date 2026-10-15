# Handoff, Streaks v1.1.0 execute, app module, after task 27a

Written 2026-10-15 by the frontend builder (senior frontend dev agent), after task 27a. It replaces the counts and baselines of `handoff-2026-10-15-execute-streaks-app28.md`. Everything that handoff says about task 28's live gate and fidelity gate still holds unless this file says otherwise. Task 28 (the gates, run by the finders) was not started.

## Where it stands
- HEAD `e5767e5` `docs(app): task 27a proof record ...` on top of `4af5d75` `feat(app): Dismiss with the field disabled moves focus to the page's first control (task 27a, R17)`.
- Task 27a changed one symbol of `src/`, `dismissNote` in `src/view.js`. It focuses the field, or `firstControl()` when the field is disabled at twelve habits (owner ruling H-05). No markup, style, copy or motion change. `index.html`, `src/system.css` and `docs/design/` untouched.
- Tests. `tests/browser/test_storage.py` gains `test_R17_dismiss_with_the_field_disabled_moves_focus_to_the_pages_first_control_never_to_body` (rows `390x844-12`, `1280x800-12`, `390x844-11`). In `tests/browser/test_platform.py` one comment changed (the keyboard test's `wait_for_close(closed)`).
- `spec.md` task 27a ticked. `docs/modules/app/BUILD.md` section "v1.1.0 task 27a".
- Left unstaged and untouched, the orchestrator's `docs/modules/ROADMAP.md`, `docs/progress/STATE.md`, `docs/progress/process-ledger.md` and `docs/v1.1.0/CHANGE-LEDGER.md`. This handoff is new and uncommitted, for the orchestrator to commit with its records.

## Baselines for task 28 (replace the app28 handoff's)
| Suite | Folder | Count from the folder's own file |
|---|---|---|
| Node | `docs/modules/app/qa/functional/20261015-174935-node/` | 137 of 137 (`node-test.txt`, `junit.xml`) |
| Chromium | `docs/modules/app/qa/functional/20261015-174940-chromium/` | `junit.xml` tests 358, failures 0, errors 0, skipped 0 |
| WebKit | `docs/modules/app/qa/functional/20261015-175213-webkit/` | `junit.xml` tests 358, failures 0, errors 0, skipped 1 (CO-1) |

All three ran on the committed tree `4af5d75` (each `run.json` records HEAD and a clean `src/`). The 358 are the 348 of task 27, the 7 tests the step 5 solver round added, and the 3 rows of task 27a. By test id, WebKit differs from task 27's `20261015-075929-webkit` only by those 10 new ids, all passed, and CO-1 is the only test not passed.

The app28 handoff's suite line (Chromium 348, WebKit 347 and 1 skipped) is out of date. Its live gate folders of task 27 are builder history, run before the solver round and before 27a.

## What task 28 and the finders need to know
1. The rule of 27a is not on the live gate's path. The gate boots with no saved value, so the unreadable note never shows and Dismiss is never pressed. The gate's 21 steps and its control need no change.
2. The fidelity gate is not touched by 27a. No golden draws the note with the field disabled, and the markup, styles and copy are as they were.
3. The live gate, its control first and then the green run, per engine against one server, as `BUILD.md` "v1.1.0 task 27", "How to run" says. The script refuses an `--out` that already holds files.
4. For the code reviewer. `dismissNote`'s doc comment is new (what, why, no input, no output). `firstControl` is unchanged and is now used by `dismissNote` and by `firstFocusOfTopLayer` in `src/app.js`.
5. For QA. The 27a RED runs are `docs/modules/app/qa/red-first/20261015-174616-chromium/` and `20261015-174632-webkit/` (today's tree, the twelve-habit rows red on "document.activeElement is 'body'"), and `20261015-174651-chromium/` and `20261015-174703-webkit/` (the planted defect, the eleven-habit row red on focus going to the Overview button). The planted runs keep the defect's diff in `src-diff.txt`.
6. For the orchestrator. The README reconcile line is in `BUILD.md` "v1.1.0 task 27a", "For the README reconcile". `BUILD.md` names two process slips of this task under "Deviations" (a heredoc commit message, and `git` output piped into `tail`, `grep` or `sed` in three read-only commands).

## Gotchas
- The standing ones of the task 26 and 27 handoffs still hold (clicks under a paused clock, WebKit's Escape pacing, the page guard of R14, WebKit's focus after a mouse click, a click into a rising popup).
- From the spec's engine note, not measured again at 27a. A mouse click leaves focus on no button in WebKit, and the Dismiss button is removed with the note in both engines, so the app's own focus call is what puts focus on a control. The RED runs show `body` in both engines on today's tree.
- Each row of the new test took under 1 s in Chromium and under 2.5 s in WebKit in the proof runs (`junit.xml` times). No clock is installed. The default fixed time pins the date.

## Processes
None of task 27a's left running. Each pytest and node run went through a bounded scratch runner (`streaks-27a/run_suite.py` in the session scratchpad), and the WebKit full run was a background job with a bounded wait. Every runner, pytest and node PID, and the 16 `http.server` PIDs of the conftest, were checked gone, and the 16 ports were checked refusing (the builder's return lists them by PID). The closing sweep by name and command line found only the sweep's own shell.
