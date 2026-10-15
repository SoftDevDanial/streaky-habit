# Code review evidence, app, v1.1.0 step 5

Written by the code-review finder (read-only), 2026-10-15. HEAD `4e860ff`. The verdict is `docs/modules/app/findings/code-review.md`. This folder is the record of the runs behind it.

## What was run, and where
- A throwaway copy of HEAD, made with `git -c core.autocrlf=false archive 4e860ff` into the session scratchpad and extracted there (`cr-streaks/copy-lf`). Every mutant was served from memory by a `ThreadingHTTPServer` on `127.0.0.1` (`tools/mutrun.py.txt`), and the copy's own pytest suite ran against it through `STREAKS_BASE_URL`. No file of the repository was written by any run. The copy's `src/` was never changed on disk.
- Node mutants of habit-logic ran through an in-memory module load hook. They are recorded in `docs/modules/habit-logic/qa/code-review/20261015-125001/`.
- Three probe test files were added to the scratch copy only (`probes/*.py.txt`, stored here with a `.txt` ending so no pytest run collects them).
- The copy's live gate ran against four mutants (`tools/gaterun.py.txt`). Its evidence folders were written inside the scratch copy, not here.
- Static checks on the working tree, `static-checks.txt`.

## Files
| File | What it holds |
|---|---|
| `runs.txt` | the runner's JSON line for every run of the first set, with the command and clock time of each block |
| `runs-2.txt` | three more runs against the whole repository suite (A11, A11b, A17), made after the first draft of the verdict |
| `mutants/definitions.jsonl` | every mutant, its file, the exact text replaced, the replacement and the tests it ran against |
| `tools/mutrun.py.txt`, `tools/gaterun.py.txt` | the two runners as run |
| `probes/test_cr_probe.py.txt` | the capture probe, the held click on a beneath popup's backdrop, P2 and P4 reopened after a scroll |
| `probes/test_cr_r36_sync.py.txt` | the failing `@R36` row read two ways, 8 tries each |
| `probes/test_cr_fades.py.txt` | `more-below` at the end of the frame at device scale 1, 2, 2.625 and 3 |
| `static-checks.txt` | the stylesheet diff, the source scans, the README symbol lookup, helper use counts, the stand-in predicate cases, the lost 1.0 guards |

Correction to `runs.txt` line 1 (2026-10-15, same run). It says each block is copied as printed. The verdicts, counts, PIDs, ports and clock times are as printed. Long `failing` lists, the `copy` path and the R36 sync and fades `shown` lines are shortened, each in parentheses or with "...".

## Controls
- Unmutated full suite through the in-memory server, Chromium, 347 passed and 1 skipped (the sub-path test, skipped because the runner names a base URL and no sub-path URL). The harness reproduces the suite.
- Unmutated probes green in both engines. Unmutated live gate, GATE PASS in both engines, 21 of 21 steps.
- Each probe was watched failing under a mutant (P-G0, P-G1, P-A17, and the R36 synchronised read under A2, 8 of 8 red).

## Results, mutants of src/ (Chromium unless named)
| Mutant | Change | Result |
|---|---|---|
| A1 | `onPopupClose` sets no focus on a connected opener | SURVIVED 29 tests in Chromium (the browser's own focus restore), KILLED 29 of 29 in WebKit |
| A2 | `clearDayRoom` not called | KILLED |
| A3 | the 500 ms window inclusive | KILLED |
| A4 | the pressed popup counted beneath itself | KILLED |
| A5 | `detail` 2 no longer held | KILLED |
| A7 | a refused tick saves | KILLED, on "a tick on a day outside the year was saved" |
| A8 | the warning re-inserted while saves keep failing | KILLED, on "the warning was replaced while saves kept failing" |
| A9 | the 12-habit note written again on every render | SURVIVED 34 |
| A11 | every P2 bead pops on every edit | SURVIVED 29 (Chromium) and 3 (WebKit), and the whole repository suite but the CR-01 race row (runs-2) |
| A11b | every P1 tick pops on every edit | SURVIVED 39 (Chromium) and 39 (WebKit), and the whole repository suite, 347 (runs-2) |
| A11c, A11d, A11f | every Done today dot, band ring, Overview ring pops | KILLED |
| A11e | P1's mini ring pops on every edit | SURVIVED, equivalent (every accepted P1 tick changes that ring) |
| A12, A12b | today threads right, the year start threads left | KILLED (P2's golden comparison) |
| A14 | no branch for a gap smaller than a day | KILLED |
| A15 | P3's newest week unlabelled | KILLED (rollover test only) |
| A16 | `is-open` kept after P1 closes | KILLED |
| A17 | a popup body not set to its top on opening | SURVIVED 68 and the whole repository suite, 347 (runs-2). The probe shows P2 reopens at 900 and P4 at 3332 without it |
| A18 | the first control may be a hidden one | KILLED |
| A19 | a stale `bump` left on an unchanged value | SURVIVED, no visible effect (read as equivalent) |
| A20 | `pop` never removed | SURVIVED, no visible effect (read as equivalent) |
| A22, A23, A24 | rollover focus, P1 opener, `is-open` re-mark | KILLED |
| A30, A31, A32 | opener box, keyboard starts the window, release alone closes | KILLED |
| A43 | P1 tick numbers as of the chosen day | KILLED |
| A50 | `stopPropagation` for `stopImmediatePropagation` | SURVIVED, equivalent by measurement in both engines (probe) |
| A51 | the day check every 45, 60, 85 and 115 s | SURVIVED all four (1 and 14 tests) |
| A53 | focus moved to the field after an add | KILLED |
| A56 | rows rebuilt on every render | KILLED |
| A60 | P1's tick list built only once | SURVIVED 57, and 101 of 102 wider (the one failure is the CR-01 race row) |
| A65 | the legend drawn only once | SURVIVED 20, 181, and the whole repository suite (347) |
| B1 | every created svg, path, circle and text in the HTML namespace | SURVIVED 76, and the whole repository suite but the CR-01 race row |
| B2 | the rollover saves | KILLED |
| B3 | Dismiss saves | SURVIVED 82 and the whole repository suite |
| B4 | a rejected name saves | SURVIVED 19 and the whole repository suite (347) |
| B5, B6 | Cancel saves, any popup close saves | KILLED |

Live gate. G1 (A1) GATE PASS in Chromium, GATE FAIL in WebKit at step 07 "day editor closed" on focus. G2 (nothing saved) GATE FAIL at step 11 "reloaded". G3 (A11) GATE PASS.

## Probes
- Capture probe, both engines, `["capture"]`. A `stopPropagation` in a capture listener on the event's target keeps the target's own bubble listener from running.
- Held click on a beneath popup's backdrop (M1 over P2 at 1280 x 800, two presses at (5, 5)), both engines. P2 stays open unmutated and with A50. It closes with no hold (P-G0) and with only the page held (P-G1). No repository test presses there.
- R36 release read, the row `360x780 P3 2026-07-20` clicking Close. Chromium, as written 5 of 8 tries read `["293px", "293px"]`, after the close event 8 of 8 read `["24px", ""]`. WebKit 16 of 16 read `["24px", ""]`. The synchronised read under A2 is red 8 of 8.
- Fades at the frame's end, scale 1, 2, 2.625 and 3, both engines, `more-below` absent in all 16 cases. No defect.
