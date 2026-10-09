# Evidence, regression code-review re-check: app (2026-10-09)

Written by the code-review finder (read-only), scoped re-check of `a3d3ed1..83396f6` (the solver's seven commits and the orchestrator's README reconcile). The section for the orchestrator to merge is `recheck-section.md`. `src/`, `index.html` and everything outside this folder were not touched: `git diff --quiet a3d3ed1 HEAD -- src index.html` exits 0 and `git status` lists only this folder.

## Files

| File | What it is | Run with (from the project root) |
|---|---|---|
| `recheck-section.md` | the section headed "## Re-check (2026-10-09)": verdict, RG-CR-07, "What held" with the measurement per item | n/a |
| `run_recheck_mutants.py`, `mutants_output.txt` | calls the regression finder's `run_mutants.py` (and through it the first review's `mut.py`, with `mutants_regression.py`) for: baseline on `test_delete`; G-450, G-600, G-le, G-kbd-delete-open, P-kbd-click-passes, G-bubble on `test_delete`; P-kbd-click-passes and G-bubble again on the whole browser suite. In memory, no project file written | `python -B docs/modules/app/qa/regression-recheck/20261009T231957/run_recheck_mutants.py .` |
| `mutants_recheck.py`, `run_extra_mutants.py`, `extra_mutants_output.txt` | four extra mutants that move one guard's window only (S-G1-499, S-G1-501 for "Delete habit"; S-G2-499, S-G2-501 for the page), to show each edge test pins its own guard. Same runner `mut.py`, `-k test_delete` | `python -B docs/modules/app/qa/regression-recheck/20261009T231957/run_extra_mutants.py .` |
| `probe_timestamp.py`, `probe_timestamp_output.txt` | does `Event.timeStamp` follow Playwright's installed clock for a mouse click, a tap and an Enter-made click, and does it ignore real time (700 ms real wait with the clock paused). A bare page, no project server | `python -B docs/modules/app/qa/regression-recheck/20261009T231957/probe_timestamp.py` |
| `run_suites.py`, `suites_output.txt` | `node --test "tests/**/*.test.js"` and `python -m pytest tests/browser -q -p no:cacheprovider` once each, tail of each output | `python -B docs/modules/app/qa/regression-recheck/20261009T231957/run_suites.py .` |
| `scan_hygiene.py`, `scan_hygiene_output.txt` | read-only: non-ASCII bytes in what `a3d3ed1..HEAD` added and in the touched files, vendor lines in the commit messages, BUILD.md `view.js` exports against `src/view.js`, BUILD.md `app.js` bullet against `src/app.js`, README code-map identifiers against `src/` | `python -B docs/modules/app/qa/regression-recheck/20261009T231957/scan_hygiene.py .` |

Every script saves its own output next to itself and writes nothing else. The mutants are served from memory by `mut.py`; `src/` is never patched on disk.

## Results at a glance

| Check | Result |
|---|---|
| `test_delete` baseline | 68 passed |
| G-450 / G-600 / G-le / G-kbd-delete-open | KILLED, 4 / 5 / 5 / 1 failed |
| P-kbd-click-passes / G-bubble | SURVIVED (ruled unspecified / equivalent), whole suite 178 passed, 1 skipped (sub-path test, not served by the runner) |
| S-G1-499 / S-G1-501 / S-G2-499 / S-G2-501 | KILLED, 2 / 3 / 2 / 2 failed, each by its own guard's edge test only |
| `Event.timeStamp` after `run_for(499)` / `(500)` / `(1)` | 499.000 / 500.000 / 1.000 for mouse, touch, keyboard; 700 ms of real waiting moves it by 0.000 |
| `node --test "tests/**/*.test.js"` | 99 pass, 0 fail |
| `python -m pytest tests/browser -q -p no:cacheprovider` | 179 passed in 44.72 s, both conftest servers refuse connections afterwards |
| Non-ASCII bytes in added lines | 0 |
| BUILD.md `view.js` exports vs `grep ^export` | 22 and 22, equal |
| New findings | RG-CR-07 (INFO, spec wording) |

## Processes

PROCESSES: started, all stopped.
- `run_recheck_mutants.py` (pid 50476) and its child `run_mutants.py` (pid 49340 for the second call), each call one in-process server thread and one pytest child per mutant, waited for by the runner; exit code 0 each. The whole-suite survivor runs had no conftest servers (the runner serves the app itself).
- `run_extra_mutants.py` (runner pid 51212), four pytest children, exit code 0.
- `probe_timestamp.py`: one headless Chromium, closed by the script (`browser.close()`), no server.
- `run_suites.py`: `node --test` (exited), `python -m pytest tests/browser` with conftest's two `http.server` children (pids 50448 on 127.0.0.1:20621 and 44156 on 127.0.0.1:5869), stopped by conftest, which printed that both ports refuse connections.
- Sweeps by command line (`Get-CimInstance Win32_Process`, read-only) after the runs: none of my processes remain. Seen and not mine, not touched: the sibling Split project's agent (`docs/modules/split-app/qa/regression-recheck/...run_mutants.py`, its pytest child, an `http.server` and `chrome-headless-shell` processes) and, once, one other `http.server` on port 19505, gone by the final sweep.
- Writes: Write tool only, into this folder. The scripts save their own output here. No heredoc, no redirection, no `sed -i`. The clipboard was never touched. Headless Chromium only. `.pytest_cache/` in the project root is ignored by git and dates from 14:21 today, not from my runs (all started with `-p no:cacheprovider`).
