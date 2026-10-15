---
module: habit-logic
kind: code-review
status: issues_found
counts: { blocker: 0, warning: 2 }
---
# Code review, habit-logic (v1.1.0, step 5)

Written by the code-review finder (read-only), 2026-10-15. HEAD `4e860ff`. It replaces the 1.0 verdict of this file (2026-10-09, re-checked at `14d59b7`, kept in git history). Scope is `git diff v1.0.0..HEAD -- src/dates.js src/habits.js tests/dates.test.js tests/habits.test.js tests/sample-history.test.js tests/purity.test.js tests/fixtures/` (tasks 6 to 9, commits `6188e66`, `964678b`, `9a79991`, `3676fe5`), judged against `spec.md` (R1 to R20, the v1.1.0 delta, Contracts, Invariants, Non-goals, Tasks), `qa.md`, `BUILD.md`, the README's habit-logic paragraph, `docs/constitution.md` and `CLAUDE.md`. Evidence is `docs/modules/habit-logic/qa/code-review/20261015-125001/` (`evidence.md` first).

## Verdict

**0 BLOCKER, 3 WARNING.** The code is correct against the spec, small and well named, and the tests are strong. I ran 11 mutants of the v1.1.0 code (`yearStart`, `toggleDay`'s range, `doneFlags` in `heatmapCells`, `yearMonths`, `yearDate`, `monthTitle`) through an in-memory load hook on a throwaway copy, and the unchanged suite killed all 11, each with a test of the R# it breaks (R9, R10, R17, R18, R20). The control run was 137 of 137 green and the hook's own control mutant was killed. The warnings are records that say the work is not done, one test whose title claims more than it can show, and the stale README paragraph.

## BLOCKER

None. Checked for this class. Every export traces to its R# (R1 to R4, R6, R7, R9, R10, R12 to R15, R17 to R20) and every private helper serves one of them. None of the retired exports remains (`weekWindow`, `runContinues`, `heatLevel`, and the private `doneCountsByDay`). The Contracts match (`HeatCell` with `done` and without `level`, `YearDay`, `YearMonth`, the export list that `tests/purity.test.js` pins). No Non-goal is built (no clock read, no `Intl`, no cache, no DOM or storage, no start date field, no ring geometry). `doneFlags` reads each habit's `done` once per call with one `includes`, as the threat model's responsiveness row requires.

## WARNING

### WR-01. The spec and BUILD.md still say the v1.1.0 tasks are not done (doc rot)
- **Symbol.** `spec.md` Tasks 6 to 9, `BUILD.md` "Tasks to commits" and "Non-goals honoured".
- **Failure.** Tasks 6, 7, 8 and 9 read `[ ]`, although each is built and committed (`6188e66`, `964678b`, `9a79991`, `3676fe5`) and the app spec ticks its tasks 11 to 27. The 1.0 round fixed the same gap with a dated "module close housekeeping" note. `BUILD.md`'s "Tasks to commits" table lists only tasks 1 to 5, and the task 6, 7 and 9 sections name no commit (task 8 names `9a79991`). Its 1.0 section "Non-goals honoured" says "`toggleDay` refuses days older than 7 and any day outside the strip", which v1.1.0's R9 made false, in a file whose "Exports" section is kept current, so a reader cannot tell which parts still hold.
- **Fix.** Tick tasks 6 to 9 with a dated note, add rows 6 to 9 to the table with their commits, and give the 1.0 "Non-goals honoured" paragraph a dated line that it is 1.0's, with v1.1.0's in the task sections.

### WR-02. `@R20 @R16 yearMonths reads no clock` cannot fail on a clock read (test strength, low)
- **Symbol.** `tests/purity.test.js`, the test `@R20 @R16 yearMonths reads no clock, so two calls with one key give equal results`.
- **Failure.** Its first line, `assertNoClockRead("habits.js", ...)`, repeats `@R16 the source has no clock or random read, even in a comment` on the same file. Its second line, two calls of `yearMonths(TODAY)` compared for equality, cannot see a clock read, because both calls run in the same millisecond. Mutant H13 makes `yearMonths` start from the device's month through `const Clock = Date; new Clock()`, and the test passes. Mutant H12 (an aliased read with no effect) passes the whole unit suite, 137 of 137. R16 itself names aliased reads as a residual left to review, so the scan is not the gap. The gap is a title that promises the property.
- **Fix.** Make the equality able to fail. Call `yearMonths(TODAY)` while `globalThis.Date` is a subclass whose constructor throws when called with no argument and whose `now` throws, then restore it in a `finally`. A read through an alias inside the function body then throws, and H12 and H13 go red. Or drop the test and map the qa scenario to the R16 scan by name.

### WR-03. The README's habit-logic paragraph lists removed exports (doc rot, fallback owner)
- **Symbol.** `README.md`, "How it is built", the `habit-logic` paragraph.
- **Failure.** It says "`weekWindow`, `toggleDay`, `currentStreak` and `bestStreak` drive the week strip and the streak line" and "`heatmapCells`, `heatLevel` and `monthLabels` build the 12-week heatmap". `weekWindow` and `heatLevel` no longer exist (grep of `src/`, no file). `yearStart`, `doneFlags`, `yearMonths`, `yearDate` and `monthTitle` are not named. The same file's other stale parts are the app's WR-09, so one reconcile fixes both.
- **Fix.** The orchestrator rewrites the paragraph from `BUILD.md` "Exports (for the README reconcile)", which is current, citing symbols.

## Notes (not findings)
- `yearMonths("10000-01-05")` throws a `TypeError` in `dayParts`, because `yearStart` and `calendarMonth` slice a four-digit year. A device clock in the year 10000 gives such a key through `localDateKey`. That is the accepted 1.0 residual SEC-05. The new symptom (P2 and P4 do not open) is in the app's README finding, so the README's limit says it.
- `yearMonths` stops on a string comparison inside `for (;;)`. For every four-digit key it ends after 13 months (tested on six dates, and on 0001 and 9999 by probe). A 13-step bound would read simpler. Left as is, the count follows from the rule as `BUILD.md` task 8 says.
- `yearMonth` and `yearMonths` step with literal `1` and `-1` where the file names `NEXT_DAY` and `PREVIOUS_DAY`. Cosmetic.
- `tests/habits.test.js` `tally` and the inline reduce in `tests/sample-history.test.js` count day kinds the same way. Test code, cosmetic.
- Every comment is a why, the load-bearing ones are kept (`streakDays`, `daysFromCivil`, `heatmapCells`' sort note), and no comment cites a line number.

## PROCESSES
The Node runs were foreground children of the runner (PIDs in `runs.txt`), each exited before the next started. Nothing of this module's review is left running. The closing sweep is in the return.

## Solver round 2026-10-15
Written by the dev solver (solver role). The finder's text above is unchanged.

| Finding | Verdict | Commit | Proof |
|---|---|---|---|
| WR-01 | RESOLVED. Tasks 6 to 9 ticked in `spec.md` with a dated note, rows 6 to 9 with their commits in `BUILD.md`, the 1.0 count and the 1.0 "Non-goals honoured" paragraph each with a dated line | `0f7f68b` | records only |
| WR-02 | RESOLVED. The test calls `yearMonths` while `globalThis.Date` throws on a clock read, restored in a `finally` | `9fe4a70` | RED under H12 and H13 (only this test fails), control 6 of 6, `docs/modules/habit-logic/qa/solver/20261015-142752-wr02-node/`. The earlier `20261015-142734-wr02-node/` is void, its hook did not apply on the CRLF checkout |
| WR-03 | NOT the solver's. The README is the orchestrator's | | |

Node suite after the round, `docs/modules/app/qa/functional/20261015-142907-node/`, 137 of 137. The qa.md wording for WR-02 is in `BUILD.md` "For the planner". To re-run: this code review.

## Re-check 2026-10-15
Written by the code-review finder (read-only), 2026-10-15, the one re-check after the one solver round (stop rule). HEAD `c271938`, the round's habit-logic commits `9fe4a70` and `0f7f68b`, judged with the solver's section above. Evidence is `docs/modules/habit-logic/qa/code-review/20261015-144606/` (`evidence.md` first). Mutants were applied in memory by round 1's load hook to a throwaway `git archive` copy of `c271938` in the session scratchpad. The round-1 text above is unchanged except the front matter, which now gives the re-check's count.

### Verdict
**0 BLOCKER, 2 WARNING open.** WR-03 is still open with the orchestrator, and WR-04 is new, a stale count of the same kind as WR-01 that my round 1 missed. WR-01 and WR-02 hold. The control run is 137 of 137 and the hook's own control mutant is killed.

### Round-1 findings
| Finding | Re-check | Evidence at `c271938` |
|---|---|---|
| WR-01 | HOLDS | Tasks 6 to 9 read `[x]` under a dated note in `spec.md`. "Tasks to commits" rows 6 to 9 carry `6188e66`, `964678b`, `9a79991` and `3676fe5`, the subject of each commit names its task, and each row's R# list is its spec task line's. The 1.0 count line and the 1.0 "Non-goals honoured" paragraph each carry a dated line that says what holds now |
| WR-02 | HOLDS. The test can now fail on a clock read | H12 KILLED on the whole unit suite, 136 of 137, only this test, "a clock read, new Date() with no argument". H13 KILLED. Two more aliased reads, `Date()` called as a function (H15) and `now()` (H16), KILLED by the same test. H14, the alias taken at module scope, SURVIVED, because the module is imported before the stand-in is in place. That is the residual R16 names, and the test's comment says "inside a function body", so it claims no more than it does |
| WR-03 | OPEN, the orchestrator's (the README) | |

### New WARNING

### WR-04. `BUILD.md`'s "Final test run" still gives 1.0's count as the last one (doc rot)
- **Symbol.** `BUILD.md`, section "Final test run".
- **Failure.** Its last line (2026-10-09) says the suite "gives 66 tests", with `dates.test.js` 15, `habits.test.js` 39, `sample-history.test.js` 7 and `purity.test.js` 5. At `c271938` the unit run gives 137, and this module's four files hold 18, 43, 14 and 6 (my per-file count, and the proof line of the task 9 section). The heading says final, and the round dated the count line just above this section but not the section itself. It is the same kind of record as WR-01, which my round 1 should have named with it. It predates the round.
- **Fix.** A dated line under the section that states the stable effect, not a new number, for example "Changed 2026-10-15 (code-review re-check WR-04). The counts above are 1.0's and no longer hold. Each v1.1.0 task section below gives its own run."

### On the "For the planner" line (`BUILD.md`, solver round)
The recommended Then ends "and Date is the real one again after the test". The test restores `Date` in a `finally` and asserts nothing about it, so that clause would be a Then that no check backs. Drop it, because putting `Date` back is the test's own hygiene and not a property of `yearMonths`, and keep "yearMonths called twice with the same key gives equal results and throws nothing".

### Notes (not findings)
- The solver's `docs/modules/habit-logic/qa/solver/20261015-142752-wr02-node/runs.jsonl` lists all six titles of `purity.test.js` under `failing` for H12 and H13, beside `"fail": 1`. Its `.txt` captures, its line above ("only this test fails") and my runs show one failing title. The verdict stands. The list is a parser slip in that record.

### PROCESSES
The Node runs were foreground children of the runner (PIDs in `runs.txt`), each exited before the next started. Nothing of this re-check is left running. The closing sweep is in the return.

### Targeted pass 2026-10-15 (solver)
Written by the dev solver (solver role), the one pass the orchestrator ruled under the stop rule. The finder's text above is unchanged.
- WR-04. RESOLVED by the solver, commit `a61cfc0`. One dated line under "Final test run" in `BUILD.md`, "Changed 2026-10-15 (code-review re-check WR-04). The counts above are 1.0's and no longer hold. Each v1.1.0 task section below gives its own run." The old lines are untouched. A record, nothing to run.
