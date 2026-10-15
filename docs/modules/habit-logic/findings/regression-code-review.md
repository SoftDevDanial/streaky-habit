---
module: habit-logic
kind: code-review
run: regression
status: clean
counts: { blocker: 0, warning: 0, info: 2 }
---
# Code review, regression re-check, habit-logic task 9a (v1.1.0)

Written by the code-review finder (read-only), 2026-10-15, for `sdlc:regression --full`, after one targeted solver pass. HEAD `c00bc8c`, whose `src/` and `tests/` equal `40848ce` (`git diff --stat 40848ce HEAD -- src tests index.html` is empty).

Scope is `git diff a6f7e18 40848ce -- src tests`. For this module that is `eafc9e5`, the bound on `yearMonths` in `src/habits.js` (constant `YEAR_VIEW_MONTHS`, the stop in the loop, the doc comment) and the new test `@R20 yearMonths ends for every key and returns at most 13 months` in `tests/habits.test.js` (worker harness `yearMonthsInWorker`, `farQuarterKeys`, `OUTCOMES`). The contract is `b3183c0`, habit-logic spec R20 "the bound", the Contracts row of `yearMonths`, task 9a and the Non-goals line of H-06, and the qa.md Scenario Outline of the same name. The findings it answers are SEC-R01 (`docs/modules/app/findings/regression-security.md`). App task 28a (`40848ce`) is judged in `docs/modules/app/findings/regression-code-review.md`, section "Re-check 2026-10-15, task 28a".

Evidence is in `docs/modules/habit-logic/qa/regression-code-review/20261015-230419/`.
- `mutants.txt`, six mutants of `yearMonths` run against `tests/habits.test.js` in scratch copies.
- `differential.txt`, before and after the bound on 143,870 valid keys.
- `fuzz.txt`, 156,530 far, negative and odd keys against the bounded function.
- `task28a-comment.txt`, the 28a diff and the check of the new comment against the markup and the CSS.

## Verdict

**clean. 0 BLOCKER, 0 WARNING, 2 INFO.**

- **The contract, no more.** The code change is one constant and one `||` clause in the stop of the walk, both R20 (the bound). No other function, export or import changed, and no non-goal was built. `yearMonths` makes no `isDateKey` call, and `localDateKey`, `yearStart`, `heatmapCells` and `toggleDay` are untouched.
- **Valid keys unchanged.** By reading, for a key that passes `isDateKey` the old stop is met on the 13th push, the same push at which `months.length` reaches 13, so the new stop never fires first. Measured, `differential.txt` gives 0 differences over 143,870 valid keys (the last day of every month of 0001 to 9999, 28 February, 29 February and 1 March of every year, every day of 0001, 0002, 9998 and 9999), with a control that does see a 12-month cut and a changed `kind`. The solver's own differential used other keys (first days of months) and also found 0.
- **Every other key ends.** `fuzz.txt`, 156,530 keys as `localDateKey` writes them for far, negative and Invalid Date clocks, and odd strings. All returned at most 13 months or threw, and the slowest call took 3.35 ms. The inner walk of `yearMonth` also ends, as `fuzz.txt` explains.
- **The test asserts the requirement and is a real control.** It asserts termination ("did not end" on heap limit, timer, non-zero exit or no message) and the count per outcome. Five of six mutants die on the rows that should catch them (`mutants.txt`). m1 (the code before the bound) reproduces the solver's RED here, 7 rows "stopped by the heap limit of 256 MB" in 4.1 to 4.7 s. m2 and m4 (14 months) fail the 7 far rows. m3 (12 months) fails the 3 valid rows and two older `@R20` tests. m6 (a throwing guard) fails the 7 far rows. The survivor is RC-9A-1.
- **It cannot hang or flake on today's code.** One worker per row, run one after another. The timer is cleared on `exit`, and `terminate` stops a busy loop, so a stopped worker still reaches `exit` and resolves the promise. An uncaught error in the worker, the failed `import()` included, reaches the `error` handler and fails the row. On the bounded code a single-key row takes about 20 to 30 ms and the 920-key row 247 ms (solver) and 285 ms (this review) against a 5 s timer, so the comment "many times what the 920-key row needs" holds (about 17 to 20 times). On the unbounded code the whole file ended by itself in 31 s with exit 1.
- **Comments.** The doc comment of `yearMonths` gives the why in two sentences (a key from a clock past 9999, a month the walk never writes) and cites R20 and SEC-R01, no line number. Its `@returns` says what the Contracts row says. The test's comment block says why a worker, why a heap limit and a timer, and why an eval source, and cites no line number.
- **RED capture** `docs/modules/habit-logic/qa/red-first/20261015-223234-task9a-node/` was taken on `a6f7e18` with only `tests/habits.test.js` modified (`run.json`, `tree_status_at_start`), 7 rows "did not end" and the 3 valid-key rows and the 3 "or threw" rows green in the same run, as qa.md asks.

## BLOCKER

None.

## WARNING

None.

## INFO

### RC-9A-1. The scenario admits an empty result, so the non-goal "no `isDateKey` call in `yearMonths`" is held by review only (test strength, R20)
- **R#.** R20 (the bound), and the H-06 Non-goals line ("Do NOT make the module validate `todayKey` (no `isDateKey` call in `yearMonths`)").
- **Symbol.** `OUTCOMES` in `tests/habits.test.js`, the outcome "it returned at most 13 months" (`months <= 13`), and `yearMonths` in `src/habits.js`.
- **What is wrong.** A guard `if (!isDateKey(todayKey)) return [];` at the top of `yearMonths` returns 0 months for every far key, which is "at most 13". It passes all 57 tests of `tests/habits.test.js` and all 151 Node tests. It would also change what the app shows at those clocks (a year view with no months instead of the re-accepted SEC-05 residual), which the owner did not rule. The test asserts exactly what the contract says, so the code and the test are not at fault. The gap is in the contract's wording.
- **Evidence.** `mutants.txt`, m5-guard-empty, 57 of 57 and then 151 of 151, exit 0. The throwing form of the same guard (m6) is killed.
- **Direction.** For the planner, not the solver. If the non-goal should be pinned by a test, the far rows' outcome could read "it returned between 1 and 13 months". The bounded code returns 1 to 13 months there, because the loop always pushes once before it checks. Otherwise leave it, and it stays a review-time check.

### RC-9A-2. The contract's differential has no capture in the project (records, R20)
- **R#.** R20 (the bound), task 9a, Node proofs ("A one-off differential ... Proofs go to `docs/modules/habit-logic/qa/solver/<datetimestamp>/`").
- **Symbol.** `docs/modules/habit-logic/BUILD.md`, section "v1.1.0 task 9a", "Green and the differential".
- **What is wrong.** The section says the differential "ran in the session scratchpad and not committed", and gives its numbers in prose. No folder under `docs/modules/habit-logic/qa/solver/` holds its script or its output (the listed folders hold the suites and the probes only). The task says the differential is not a committed test, which it is not, but its result is one of the task's proofs and has no file behind it.
- **Evidence.** `ls docs/modules/habit-logic/qa/solver/` shows `20261015-223406-precommit-node`, `-224014-node`, `-224041-chromium`, `-224353-webkit`, `-224907-probes-chromium`, `-225045-probes-webkit`, none with a differential. This review's own differential, on other keys, is captured in `differential.txt` and agrees (0 differences), so the claim now has a file behind it.
- **Direction.** For the orchestrator's records. Point the BUILD.md line at `differential.txt` of this folder, or have the solver keep the script and output of such a run in its proof folder next time. No code change.

## Known and owed elsewhere (named once, not findings)

The README's Known limits row on the year 10000 still says a year view "freezes the tab, open with the owner (ledger H-06)", and several "contracted and not built" lines in the habit-logic and app specs predate the build. Both are owed by the orchestrator and a doc pass.

## Not covered

The browser suites and the security finder's probes were not re-run here. The solver ran them on `40848ce` (`docs/modules/habit-logic/qa/solver/20261015-224041-chromium/`, `-224353-webkit/`, `-224907-probes-chromium/`, `-225045-probes-webkit/`). What a year view shows at the far clocks after the bound is left to the security re-check.

## PROCESSES

PROCESSES: none alive. Every process ran from the session scratchpad folder `streaks-rc-9a/`, under `timeout`. Seven foreground `node --test tests/habits.test.js` runs (one per tree), two foreground `node --test "tests/**/*.test.js"` runs on m5, one foreground `node fuzz.mjs`, one foreground `node differential.mjs` (run 2), and one background `node differential.mjs` (run 1, shell job PID 1602, node PID 1603, bounded at 560 s), which ended by itself with exit 1 (`differential.txt`). No server and no browser was started. Checked with `ps -ef | grep node` after the background job ended, no node process left.
