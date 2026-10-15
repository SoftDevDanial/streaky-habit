# Handoff, Streaks v1.1.0 execute, app module, after task 27

Written 2026-10-15 by the frontend builder (senior frontend dev agent), after task 27. Task 28 (the gates, run by the finders) was not started.

## Where it stands
- HEAD `4e860ff` `test(app): the v1.1.0 cold-boot live gate in both engines, with its seeded control (task 27, R27, R30)`, on top of `cf8d5c6`.
- Task 27 changed no file in `src/` and not `index.html`. It wrote `tests/browser/live_e2e.py` again, added `long_date` to `tests/browser/conftest.py`, ticked task 27 in `spec.md` and added the section "v1.1.0 task 27" to `docs/modules/app/BUILD.md`.
- Left unstaged and untouched, the orchestrator's `CLAUDE.md`, `docs/progress/STATE.md`, `STATE-LOG.md`, `process-ledger.md`, `docs/v1.1.0/CHANGE-LEDGER.md`, `docs/explain/` and the earlier handoffs.
- Suites at `4e860ff`'s code. Node 137 of 137. Chromium 348 passed (`docs/modules/app/qa/functional/20261015-075706-chromium/`). WebKit 347 passed, 1 skipped, CO-1 (`docs/modules/app/qa/functional/20261015-075929-webkit/`). The same counts as task 26's runs.

## Live gate evidence of task 27 (builder runs, T 2026-10-15)
| Engine | Control, red at the first visit on its property | Green, 21 of 21 |
|---|---|---|
| Chromium 149.0.7827.55 | `docs/modules/app/qa/live-e2e/20261015-075531-chromium-control/` | `docs/modules/app/qa/live-e2e/20261015-075537-chromium/` |
| WebKit 26.5 | `docs/modules/app/qa/live-e2e/20261015-075552-webkit-control/` | `docs/modules/app/qa/live-e2e/20261015-075558-webkit/` |

An earlier pair per engine (`20261015-075147-chromium-control`, `20261015-075156-chromium`, `20261015-075248-webkit-control`, `20261015-075255-webkit`) ran the text before `wait_until_still` covered P3 and P2, with the same verdicts. It is history, superseded by the table.

## What task 28 and the finders need to know
1. Task 28's live gate runs are the finders' own, each in a new folder. The script refuses an `--out` that already holds files, so a builder folder cannot be reused.
2. Per engine, one server from the project root (`python -m http.server <port> --bind 127.0.0.1`), the control first and the green run next against the same server, then stop the server and check that its port refuses. The two commands are in `BUILD.md`, "v1.1.0 task 27", "How to run".
3. Reading a control run. `summary.json` has `"control": "seeded"`, `pass` false (always, for a control), `first_failing_step` "first visit" and `control_red_on_its_property` true. In `steps.json` the step's `problems` start with "stored(page) is null" and `ul.rows holds li.empty with "No habits yet."`. The console line reads `CONTROL seeded RED at the first-visit step on its property`. A control run exits 1, and that exit code is not its verdict.
4. Reading a green run. `summary.json` has `"control": null`, `pass` true, `steps_run` and `steps_passed` 21, `first_failing_step` null, 0 requests outside the rule, 0 console errors, 0 page errors, 0 clipboard markers and `date_unchanged` true, with `engine` and `browser_version` (the R30 finder check "The live gate records its engine").
5. The run stops at the first failing step, in both modes. A red step names its failed properties in `steps.json` and on the console.
6. A run that crosses local midnight is void (`date_unchanged` false) and is repeated.
7. The gate uses the real clock. A green run took about 10 s in Chromium and 12 s in WebKit, a control about 6 s. Bound each run with a timeout anyway.
8. The script starts nothing. The agent that runs it starts and stops the server and declares it in `PROCESSES`.
9. The fidelity gate (Chromium, 23 captures and the states check) is the other half of task 28. qa.md "Fidelity gate" and task 26's handoff hold its inputs.
10. For the code reviewer. The clipboard stand-in check now sits in three test files (`test_engines.py` `STAND_IN_JS`, `test_fidelity_inputs.py` `STANDIN_IN_PLACE_JS`, and the `standIn` key of `live_e2e.py`'s `SNAPSHOT_JS`). `BUILD.md` judgment call 8 names it.
11. For the orchestrator. The live gate line of `CLAUDE.md` has no control command. The one to add is in `BUILD.md`, "v1.1.0 task 27", "How to run".

## Gotchas
- The standing ones of the task 26 handoff still hold (clicks under a paused clock, WebKit's Escape pacing, the page guard of R14, WebKit's focus after a mouse click).
- New at task 27. A click sent into a popup while it still rises made Playwright scroll P2's body 144 px first, in both engines (scratch probe). The gate waits until such a popup rests (`wait_until_still`).
- Process. Two read-only commands of task 27 ended with `2>&1`. Neither wrote a file. Check every command for redirection before it runs.

## Processes
None of task 27's left running. Every server, gate run, pytest run and probe was stopped and its port checked (the builder's return lists them by PID). At the closing sweep the `examples/split` builder's pytest run and its bounded poll loop were alive. They are not this module's.
