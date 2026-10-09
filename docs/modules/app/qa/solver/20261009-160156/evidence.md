# Solver evidence: app, code-review round

Run 20261009-160156, dev solver. Base `01a262a`, final `c8acaaa` plus the closing docs commit. The verdict section is `../../../findings/code-review.md`, "Solver (2026-10-09)".

## Method

1. Each warning got a fix, then a proof that the new or changed check can fail: the reviewer's mutants (`../../code-review/20261009-154715/mutants.py`, `mutants_extra.py`) and the solver's own (`mutants_solver.py` here) are served from the working tree with the patch applied in memory by the reviewer's runner `mut.py`, through `run_mutants.py` here. No project file is written by a mutant run. A mutant is KILLED when at least one test fails, SURVIVED when none does.
2. Per warning the mutants were run with a `-k` filter on the tests that matter, right after the fix. At the end every mutant was run again against the final tree with the whole browser suite and `--maxfail 1` (below).
3. Where a mutant cannot be seen from a browser (S4, the parsed object returned) the same patch was applied to `src/storage.js` by hand for one `node --test tests/storage.test.js` run and reverted at once (`git diff src/storage.js` empty afterwards).
4. The browser suite ran as `python -m pytest tests/browser -q` with no environment variable set. The mutant runs set `STREAKS_BASE_URL` to the patched server, so the sub-path test is skipped there (1 skipped in each mutant run).

## Red then green per warning

| WR | Red | Green |
|---|---|---|
| WR-10 | Old conftest, nothing set: `Failed: STREAKS_BASE_URL must be set and end with '/'` on the first test (stash of the two files, one run, stash popped). Negative control of `_StaticServer` (`scratchpad/server_control.py`, not kept): every try collides with a foreign listener, `start` raised after 3.8 s, `stop` after it did not raise, no `http.server` child left | 115 passed, 0 skipped, no environment; both ports refused connections after the run (printed by the teardown) |
| WR-07 | `src/planted.css` with the three sample names, `sample-history` and two sinks: `test_R24_no_html_sinks_in_the_source` and `test_R26_no_sample_data_in_the_shipped_files` fail (`2 failed, 1 passed`); the old scan passes the same tree | 116 passed with the file removed |
| WR-01 | V1: `test_R28_the_rendered_page_has_the_markup_of_the_goldens` and `test_R5_every_svg_and_use_...` (both parameters). H4 and H8: `test_R28_the_open_dialog_has_the_markup_of_the_golden`. H5: `test_R28_the_rendered_page_...` | 119 passed |
| WR-02 | A1: `test_R14_cancel_esc_and_a_backdrop_click_keep_the_habit` x3. A2: `test_R11_rejected_names_...` x6. A3: `test_R19_the_view_moves_...` and `test_R20_...`. A4: `test_R17_dismiss_...`. A1b and A3b (rewrite the identical text) fail by the counter alone | 119 passed |
| WR-03 | S1, S2, S3: `test_R17_unsorted_and_duplicated_days_are_repaired_at_the_next_save`. S5: unreadable row "good dates then an impossible one". S6: unreadable row "duplicate name that is not next to its twin". S4 (by hand): 2 unit tests fail | 122 browser, 99 unit |
| WR-04 | A6-45s, A6-60s, A6-85s: `test_R19_a_page_booted_ten_seconds_before_midnight_...` and no other test | 123 passed |
| WR-05 | V3: `test_R19_the_heatmap_shifts_when_a_new_week_starts`. V4, V5: the Thursday to Friday tests (3). E6: 10 tests (rollover and the 6 tick rows) | 123 passed |
| WR-06 | V2: `test_R6_best_goes_back_to_zero_in_place_...`. V7: `test_R11_the_message_stays_until_the_next_submit_across_a_delete`. A5: `test_R10_the_first_habit_on_a_fresh_day`. A7: `test_R14_a_drag_that_starts_on_the_backdrop_...`. V6: `test_JC3_a_tick_writes_only_the_text_that_changed` | 127 passed |
| WR-08 | comment only; the import lines were read: `storage.js` and `view.js` import only `dates.js` and `habits.js` | 127 passed |
| WR-09 | documentation only | 127 passed |
| WR-11 | none possible (the deleted branch was unreachable, the deleted `else` could not change anything: control mutant C3 of the review was equivalent) | 127 passed, 99 unit |
| WR-12 | M-A (no `renderMonths` in `checkDay`): `test_R19_the_heatmap_shifts_when_a_new_week_starts`. M-B (none at boot): `test_R4_english_...`, `test_R9_...` x2. The other four items keep behaviour and every existing test | 127 passed, 99 unit |
| WR-13 | `live_e2e.py` before and after (`live-e2e-before/`, `live-e2e-after/`, same day, same tree apart from the script): 11 of 11 steps pass in both, `observed` identical for all 11 steps, `console.json` identical, `gesture` and `expected` of every step exchanged (the old call order had them the wrong way round) | 127 passed |

## Final run of every mutant against the final tree

Whole browser suite, `--maxfail 1`, `run_mutants.py <project root> <ids> 1`. Output shortened to the verdict and the first failing test.

| Mutant | Verdict | First failing test |
|---|---|---|
| C1 interval 300 s | KILLED | test_rollover: the view moves within a minute |
| C2 hook on window | KILLED | test_platform: no globals and no hooks |
| A1 keep path saves | KILLED | test_delete: R14 keep, cancel |
| A2 rejected name saves | KILLED | test_add: R11 rejected names |
| A3 rollover saves | KILLED | test_rollover: the view moves within a minute |
| A4 Dismiss saves | KILLED | test_storage: R17 dismiss |
| A5 add moves focus | KILLED | test_add: R10 first habit |
| A7 backdrop press only | KILLED | test_delete: R14 a drag that starts on the backdrop |
| A8 backdrop release only | KILLED | test_delete: R14 clicks inside, drags out |
| A1b, A3b same-text rewrites | KILLED | as A1 and A3 |
| S1, S2, S3 | KILLED | test_storage: repaired at the next save |
| S5 | KILLED | test_storage: unreadable, good dates then an impossible one |
| S6 | KILLED | test_storage: unreadable, duplicate name not next to its twin |
| A6 45 s, 60 s, 85 s | KILLED | test_rollover: booted ten seconds before midnight |
| V1 svg namespace | KILLED | test_render: markup of the goldens |
| V2 stale best | KILLED | test_tick: best back to zero |
| V3, V4, V5 | KILLED | test_rollover (week shift, then the Friday state) |
| V6 setText always writes | KILLED | test_tick: JC3 |
| V7 error cleared by render | KILLED | test_delete: the message stays across a delete |
| H4, H8 | KILLED | test_delete: the open dialog has the markup of the golden |
| H5 | KILLED | test_render: markup of the goldens |
| E4 preventDefault dropped | KILLED | test_add |
| E5 rollover rebuilds rows | KILLED | test_rollover: focus on today's bead |
| E6 heat cells rebuilt | KILLED | test_rollover: the view moves within a minute |
| M-A, M-B | KILLED | test_rollover (week shift), test_render (R4 German locale) |
| E1, E2, E3 | SURVIVED | the review rated all three equivalent on Chromium (N4, harmless check while hidden); not asked to be killed |
| C3 | not run | its patch text (the `else` of `syncDay`) was deleted by WR-11 |
| S4 | by hand, node | killed by 2 tests in `tests/storage.test.js` |

## Process accounting

Everything started was a child of one runner or test invocation and exited by itself or was stopped by its own teardown.

| What | PID | Port | At return |
|---|---|---|---|
| two `python -m http.server` per `python -m pytest tests/browser` run, started and stopped by conftest `pytest_configure` | printed by every run as `streaks tests: stopped http.server pid N, 127.0.0.1:P refuses connections` | free ports | STOPPED, port re-checked by the teardown |
| `run_gate.py` server (2 runs) | 16956 and 40164 | 7955 and 23544 | STOPPED, printed by the same teardown |
| `mut.py` servers, one per mutant run | runner threads, then one pytest child each | ephemeral | STOPPED, each pytest child closed its own headless Chromium |
| `server_control.py` blocker socket | in-process | ephemeral | closed |

Final sweep, after the last command: a PowerShell `Get-CimInstance Win32_Process` filtered to `python.exe`, `chrome.exe` and `headless_shell.exe` whose command line matches `http.server`, `mut.py`, `run_mutants`, `pytest` or `playwright` returned nothing. No process of another agent was touched.

## Declared deviations

- One `python - <<EOF` heredoc was typed by mistake early on (it printed `noop` and wrote nothing). No other heredoc, redirect or `tee`.
- WR-10 red proof used `git stash push -- <two files>` and `git stash pop`; the orchestrator's uncommitted progress files were not in the pathspec and were not touched.
- `src/planted.css` (WR-07) and the S4 patch of `src/storage.js` (WR-03) were written to the tree for one run each and removed or reverted before the commit; `git status` shows neither.
- `live-e2e-before/` and `live-e2e-after/` are the solver's before and after check of the WR-13 refactor. They are not the official `@R27` gate run, which is the orchestrator's.
