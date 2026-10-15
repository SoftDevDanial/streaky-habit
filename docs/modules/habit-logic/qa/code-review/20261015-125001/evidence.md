# Code review evidence, habit-logic, v1.1.0 step 5

Written by the code-review finder (read-only), 2026-10-15. HEAD `4e860ff`. The verdict is `docs/modules/habit-logic/findings/code-review.md`.

## What was run
- `node --test` on six unit files of a throwaway copy of HEAD (session scratchpad, `git -c core.autocrlf=false archive`), unmutated (control) and with 13 mutants of `src/dates.js` and `src/habits.js` applied in memory by a Node module load hook (`tools/*.mjs.txt`). The runner is the app evidence's `tools/mutrun.py.txt`. No file under `src/` was written anywhere.
- Two read-only `node -e` probes of `yearStart` and `yearMonths` at the edges of the four-digit year, on the working tree.

## Files
| File | What it holds |
|---|---|
| `runs.txt` | the JSON line of every run, the mutant definitions and the two probe outputs |
| `tools/nodemut.mjs.txt`, `tools/nodehooks.mjs.txt` | the in-memory hook as run |

## Results
- Control, 137 tests, 137 pass. The hook's own control (N1, `MAX_HABITS` 13) failed 2 tests, so the hook applies.
- H1 to H11, 11 of 11 KILLED, each by a test of the R# it breaks (R9, R10, R17, R18, R20).
- H12 and H13, aliased clock reads (`const Clock = Date`), SURVIVED. R16 names aliased reads as a residual left to review. H13 shows that the `@R20 @R16` test's equality line cannot see a clock read.
- `yearMonths("10000-01-05")` throws a `TypeError` in `dayParts` (a five-digit year key, from `localDateKey` on a device clock in the year 10000). Accepted residual SEC-05 of 1.0. The new symptom is noted in the app verdict's README finding.
