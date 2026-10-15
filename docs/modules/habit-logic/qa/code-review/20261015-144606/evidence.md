# Code review re-check evidence, habit-logic, v1.1.0 step 5

Written by the code-review finder (read-only), 2026-10-15. HEAD `c271938`, the solver round `4e860ff..c271938` (habit-logic commits `9fe4a70` and `0f7f68b`). The verdict is the section "Re-check 2026-10-15" of `docs/modules/habit-logic/findings/code-review.md`.

## What was run
- `node --test` on the six unit files of a throwaway copy of `c271938` (session scratchpad, `git -c core.autocrlf=false archive`, the same copy as the app re-check), unmutated and with seven mutants applied in memory by round 1's load hook. The definitions are `mutants/recheck-node.json`, the lines `runs.txt`. No file under `src/` was written anywhere.
- The H12 run once more by hand on `tests/purity.test.js`, to read the failure message.
- A per-file count of the six unit files.

## Results
- Control, 137 of 137. The hook's own control N1 failed 2 tests, so the hook applies.
- H12 (an alias of `Date` read inside `yearMonths`) KILLED on the whole unit suite, 136 of 137, only `@R20 @R16 yearMonths reads no clock, so two calls with one key give equal results` fails, with "a clock read, new Date() with no argument".
- H13 (`yearMonths` starts from the device's month through an alias) KILLED, the same test.
- H15 (`Date()` called as a function through an alias) and H16 (`now()` through an alias) KILLED, the same test. New mutants of this re-check.
- H14 (the alias taken at module scope, outside any function) SURVIVED the whole suite. The module is imported before the test puts its stand-in in place, so the alias holds the real `Date`. This is the residual R16 names (aliased reads are left to review). The test's comment says "a clock read inside a function body throws", so it claims no more than it does.
- Per file at `c271938`, dates 18, habits 43, sample-history 14, purity 6 (this module), ring 16, storage 40 (the app's), 137 in all.

## Records read
- `spec.md` tasks 6 to 9 read `[x]` under a dated note. `BUILD.md` "Tasks to commits" rows 6 to 9 carry `6188e66`, `964678b`, `9a79991` and `3676fe5`, and `git log -1` of each names its task in its subject. The R# list of each row is the spec task line's.
- `BUILD.md` "Final test run" still gives 1.0's counts as the last word (66 tests, 2026-10-09), WR-04 of the re-check.
- The solver's `docs/modules/habit-logic/qa/solver/20261015-142752-wr02-node/runs.jsonl` gives `"fail": 1` and a `failing` list of all six titles for H12 and H13. Its `.txt` captures show one failing title, as my runs do.
