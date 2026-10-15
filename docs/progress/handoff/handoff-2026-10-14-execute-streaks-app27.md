# Handoff, Streaks v1.1.0 execute, app module, resume at task 27

Written 2026-10-14 by the frontend builder (senior frontend dev agent), after task 26. The orchestrator asked for a return by 00.10 and no start of task 27, so task 27 was not started.

## Where it stands
- HEAD `cf8d5c6` `test(app): the fidelity state scripts, each seed with the clipboard stand-in, and their checks (task 26, R28)`, on top of `5f5240b`.
- Node 137 of 137. Chromium 348 passed (`docs/modules/app/qa/functional/20261014-233936-chromium/`). WebKit 347 passed, 1 skipped, CO-1 (`docs/modules/app/qa/functional/20261014-234211-webkit/`). No xfail mark in `tests/`.
- Task 26 changed no file in `src/` and not `index.html`.
- `docs/modules/app/BUILD.md` section "v1.1.0 task 26" holds the two RED runs, the WebKit measurement, five judgment calls and no open question.
- The WebKit measurement the spec asked for. After each after-load script's `blur()`, `document.activeElement` is `body` in both engines for all 14 rows (`fidelity-blur-*.json` in each proof folder). The scripts send no mouse event, so the dialog focus of a mouse click does not arise. qa.md's engine table needs no new line.

## Resume point, task 27 (`tests/browser/live_e2e.py`, R27, R30)
1. Read spec Tasks line 27 and qa.md section "Cold-boot live-e2e gate (`@R27`, both engines)" with its two `@R27` scenarios (the gate and its control `--control seeded`).
2. `tests/browser/live_e2e.py` in the tree is the 1.0 form (`run(engine, base_url, out)`, argparse). Task 27 writes it again for v1.1.0. `git show v1.0.0:tests/browser/live_e2e.py` reads the 1.0 file without touching the tree.
3. The live gate's watched failure is its control run (qa.md "Controls are watched failing first"), which must fail at the first-visit step.
4. Run it in Chromium and in WebKit against a server you start and stop in a `finally`, with evidence in `docs/modules/app/qa/live-e2e/<datetimestamp>-<engine>/` and the control in `...-<engine>-control/`. Then Node, Chromium and WebKit suites, BUILD.md section, tick spec task 27, credential gate, commit.
5. Do not run the finders or task 28.

## Gotchas (new at task 26, then the standing ones)
- The fidelity tests build their context like the harness (`harness_page` in `test_fidelity_inputs.py`), not through `open_app`, because `open_app` adds `CLIPBOARD_STANDIN` itself. A second stand-in on the navigator object follows the seed, so no context can reach the system clipboard.
- Under a paused installed clock a locator click can wait forever, and `page.wait_for_function` polls on animation frames. Use raw `page.mouse`, `page.touchscreen` or `page.keyboard` and poll from Python with a deadline.
- In WebKit, Escape presses sent back to back are partly lost. Press each Escape once the previous popup has closed. A focus check after a close reads focus only after `conftest.watch_close` and `wait_for_close`.
- The page guard of R14 holds a page click for 500 ms of `event.timeStamp` after a mouse or touch click inside a popup. Under a fixed clock `event.timeStamp` does not move.
- WebKit lays `100dvh` out in 1/64 px units. A mouse click on a button inside an open popup leaves focus on the popup's `dialog` in WebKit, outside a popup on `body`.
- Source and docs through Write and Edit only. No `sed -i` and no shell redirection of any kind. Scratch probes write only to the session scratchpad. `grep -P` fails here. Check long dashes with Python. No colons or semicolons in prose, comments included.
- A second builder works in `examples/split`. Its processes and files are not ours.

## Processes
None left running. Each pytest run started its two conftest `python -m http.server` servers and stopped them (each run printed that its port refuses). The headless Chromium and WebKit of each run closed with it. One Node test run. No scratch server was started.
