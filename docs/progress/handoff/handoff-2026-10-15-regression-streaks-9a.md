# Handoff, Streaks v1.1.0 regression, the targeted pass (habit-logic task 9a, app task 28a)

Written 2026-10-15 by the dev solver (solver role), at the end of the pass. It is for the code-review and security re-checks scoped to this pass's delta, which come next (ledger S1 row 27, H-06), then the cold boot and the close.

## Where it stands
- `eafc9e5` `fix(habit-logic): yearMonths stops after 13 months, so it ends for every key (task 9a, R20, SEC-R01)`. `src/habits.js` and `tests/habits.test.js`.
- `40848ce` `docs(app): the comment of firstControl names what it returns and no caller (task 28a, code review RG-CR-I1)`. `src/view.js`, comment only.
- The docs commit on top holds the proof folders, the ticks of tasks 9a and 28a, a section per task in each module's `BUILD.md`, a solver section under the finder's text in `docs/modules/app/findings/regression-security.md` (SEC-R01) and `regression-code-review.md` (RG-CR-I1), and this handoff.
- The delta to re-check is `git diff a6f7e18 40848ce -- src tests`, three files.
- Detail, method and judgment calls are in `docs/modules/habit-logic/BUILD.md`, "v1.1.0 task 9a, the bound on `yearMonths`", and `docs/modules/app/BUILD.md`, "v1.1.0 task 28a". This file does not repeat them.

## Proof, counts from each folder's own files
| Run | Folder | Result |
|---|---|---|
| RED | `docs/modules/habit-logic/qa/red-first/20261015-223234-task9a-node/` | 143 pass, 8 fail. The six far rows and the 920-key row "did not end", the valid-key rows pass. `-223128-` before it is the same RED with quoted row titles |
| Node | `docs/modules/habit-logic/qa/solver/20261015-224014-node/` | 151 of 151, the 137 ids of the last green run unchanged |
| Chromium | `docs/modules/habit-logic/qa/solver/20261015-224041-chromium/` | 358 passed, the same ids as `regression-qa/20261015-184210-chromium/` |
| WebKit | `docs/modules/habit-logic/qa/solver/20261015-224353-webkit/` | 357 passed, CO-1 skipped, the same ids and outcomes as `regression-qa/20261015-184449-webkit/` |
| Probes | `docs/modules/habit-logic/qa/solver/20261015-224907-probes-chromium/`, `-225045-probes-webkit/` | at 10000-10-15 both presses return and the page answers, at the midnight into 10000-10-01 with P4 open the page answers |
| 28a | `docs/modules/app/qa/solver/20261015-224448-task28a-diff/git-show-U0.txt` | comment lines of `firstControl` only |

The differential of the contract ran in the scratchpad and is not committed. 0 differences over 37,620 days and 119,988 month starts.

## For the code-review re-check
1. The bound is `months.length === YEAR_VIEW_MONTHS`, joined with `||` to the month check after the push. Removing it reds the seven far rows of the new test, which is what the RED captures show.
2. The doc comment of `yearMonths` no longer says "always 13". It gives 13 for a key that passes `isDateKey` and the reason for the bound.
3. The test's worker, its 256 MB heap limit and its 5 s timer are explained in the test's comment, and the timer's margin in `BUILD.md`.
4. `firstControl`'s comment names no caller. `firstFocusOfTopLayer` and `dismissNote` keep the why, unchanged.

## For the security re-check
1. The probes show the freeze gone at the two places the finder measured it, in both engines. They do not show what P2 and P4 hold at 10000-10-15, because the hang group prints only whether the page answers. That measurement is the re-check's.
2. The re-accepted residual was not touched. January to September of every year from 10000, and six digit years, still throw. October to December from 10010 still give 11 one-day months (the new test's last three rows pin only that those calls end).

## For the orchestrator (records it owns)
- `README.md`, the Known limits row on the year 10000 still says a year view freezes the tab from October to December of those years.
- Lines that still say task 9a or 28a is contracted and not built, each for a dated line. `habit-logic/spec.md`, the top note of 2026-10-15, R20's paragraph "the bound", the Contracts row of `yearMonths`, the note under task 9a, the Threat model row on termination ("not built at this writing"). `habit-logic/qa.md`, the top note and the comment of the new Scenario Outline. `app/spec.md`, the top note, the note under task 28a, the Threat model line "SEC-05, the year views freeze". `ROADMAP.md`, the top note, the Test contracts paragraph, line 7 of the build-order block, step 7, and the rows 9a and 28a.
- The Node suite count is now 151, not 137.
- The ledger rows for this pass. PROCESSES at the hand-back: none alive.

## Resume point
Next is the code-review re-check and the security re-check on the delta above, then the cold boot and the close in the ledger's order.
