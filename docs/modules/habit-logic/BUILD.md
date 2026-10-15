# Build record: habit-logic

> Written by: the backend builder (senior dev agent), 2026-10-08 and 2026-10-09. Source of truth: `spec.md` in this folder. Test contract: `qa.md`.

## Tasks to commits

| # | Task | Requirements | Commit |
|---|---|---|---|
| 1 | `src/dates.js` and `tests/dates.test.js` | R1, R2, R3, R4 | `6296a9d` |
| 2 | `src/habits.js` part 1 (constants, `weekWindow`, `currentStreak`, `bestStreak`, `runContinues`, `toggleDay`) and its scenarios in `tests/habits.test.js` | R5, R6, R7, R8, R9 | `d26cbcc` |
| 3 | `src/habits.js` part 2 (`heatLevel`, `heatmapCells`, `monthLabels`) and its scenarios | R10, R11, R12 | `56ab40e` |
| 4 | `src/habits.js` part 3 (`validateName`, `addHabit`, `deleteHabit`) and its scenarios | R13, R14, R15 | `a25431f` |
| 5 | `tests/sample-history.test.js` and `tests/purity.test.js` | R5, R6, R7, R8, R10, R11, R12, R16 | `eaf8f9f` |
| 6 | v1.1.0. The test data fix, the 1.0 sample as a fixture and the 1.0 suites pointed at it | R6, R7, R10, R12, R16 | `6188e66` |
| 7 | v1.1.0. `src/dates.js` gains `yearDate` and `monthTitle` | R17 | `964678b` |
| 8 | v1.1.0. The year in `src/habits.js` (`yearStart`, `doneFlags`, `yearMonths`, `toggleDay` on the year, `heatmapCells` with `done`), the strip and the level removed | R9, R10, R16, R18, R19, R20 | `9a79991` |
| 9 | v1.1.0. The v1.1.0 sample checks in `tests/sample-history.test.js` | R10, R19, R20 | `3676fe5` |
| 9a | v1.1.0 regression (ledger H-06). The bound on `yearMonths`, so it ends for every key and returns at most 13 months, and its `@R20` test in `tests/habits.test.js` | R20, R16 | `eafc9e5` |

5 of 5 tasks done. Every commit was made with the full suite green.
Changed 2026-10-15 (code-review WR-01, solver). The line above is 1.0's count. Rows 6 to 9 are the v1.1.0 tasks, each built and committed, so 9 of 9 tasks are done. The task sections below give each one's proof.
Changed 2026-10-15 in the v1.1.0 regression (task 9a, dev solver). Row 9a is built and committed too, so 10 of 10 tasks are done.

## Final test run

~~`node --test "tests/**/*.test.js"` gives 60 tests, 60 pass, 0 fail, exit 0 (about 0.5 s).~~
~~Per file: `dates.test.js` 14, `habits.test.js` 34, `sample-history.test.js` 7, `purity.test.js` 5.~~
After the code-review fixes of 2026-10-09: 61 tests, 61 pass, 0 fail. The one added test is the `weekdayIndex` scenario in `dates.test.js` (WR-04).
Changed 2026-10-09 (security SEC-01 to SEC-03, ORCH): the two struck lines were the first build's counts and no longer hold. `node --test "tests/**/*.test.js"` now gives 64 tests, 64 pass, 0 fail, exit 0 (about 0.6 s, `eb2003b`). Per file: `dates.test.js` 15, `habits.test.js` 37, `sample-history.test.js` 7, `purity.test.js` 5. The three added tests are in `habits.test.js`: two streak-walk tests (SEC-01) and the name-length read count (SEC-02). SEC-03 widened two `purity.test.js` tests in place.
Changed 2026-10-09 (security re-check SEC-01, ORCH): the 64 above held at `eb2003b`. After the re-check's SEC-01 fix the suite gives 66 tests, 66 pass, 0 fail, exit 0. Per file: `dates.test.js` 15, `habits.test.js` 39, `sample-history.test.js` 7, `purity.test.js` 5. The two added tests are in `habits.test.js`: 20,000 spellings of one far-out date in one pass, and invalid keys not counted.
Every `test()` title starts with its `@R#` tag.
Changed 2026-10-15 (code-review re-check WR-04). The counts above are 1.0's and no longer hold. Each v1.1.0 task section below gives its own run.

## Deviations

None from the spec's Requirements or Contracts. Decisions inside the spec's room, for the reviewer:

- **`weekdayIndex` is a seventh export of `dates.js`**, added by ORCH ruling on 2026-10-09 (code review WR-04). The first build had no weekday index in the Contracts, so it found the current Monday by its `"Mon"` label inside the 7-day strip, which tied the heatmap's weeks to the strip's width and to a display label. How the Monday is found now, see the comment on `columnMondays`.
- **Day arithmetic uses integer day counts** (`daysFromCivil`, `civilFromDays` in `dates.js`), the second option R3 and the Invariants allow. Why, see the comment on `daysFromCivil`. The result is checked against UTC reference maths for every day from 1900 to 2100 in both zones (`tests/dates.test.js`).
- **`dayParts` abbreviates by slicing the first three letters** of the full-name tables (every English weekday and month here abbreviates that way), so there is one table per kind, not two.
- **Tests beyond the qa.md rows** (each tagged to its R#): zone-switch proof, exhaustive `isDateKey` and `addDays` and weekday agreement with a UTC reference, hostile long strings, R8 rows built from synthetic data (qa.md has only the sample rows for R8), unsorted or duplicated `done` input to `toggleDay`, copy-not-alias checks, code-point and white-space edge cases for `validateName`, and an exact export list in `purity.test.js` that doubles as the guard that the frozen-input test calls every export.
- **The R4 locale scenario runs in a child process** with `LANG` and `LC_ALL` set to `de_DE.UTF-8`, German made the default of the date locale APIs, and a precondition that the default really is German. Why, see the comment in the test `@R4 labels do not follow the runtime locale`. The child exits at once (15 s timeout). Corrected 2026-10-09 (code review WR-01): the first version relied on `LANG` alone, which Node ignores on Windows.
- **Process note.** The R10 to R12 test block was appended to `tests/habits.test.js` with a shell heredoc to a relative in-project path (no backslashes in the payload, content confirmed by the following run). Later edits used the Edit and Write tools. Scratch scripts in `harness/_scratch/` (git-ignored) were created the same way.

Unspecified edges, noted and not built (outside every R#):

- `addDays` past year 9999 or before year 0001 returns a key that `isDateKey` rejects. The app never goes near these. Decision (security SEC-01 and re-check, ORCH): `currentStreak` and `bestStreak` count only keys that pass `isDateKey`, ~~and the bound stays as a second guard~~. Why that ends every walk, see the comment on `streakDays`. How a run is counted, see `runLength`. ~~`runLength` now stops after as many days as the set holds, see its comment.~~ Changed 2026-10-09 (code review WR-15 and WR-16, ORCH): the two struck passages named the size bound, which is removed from `runLength`. The derivation this note once gave is in the `streakDays` comment only.
- `validateName` expects a string. A non-string `raw` throws a `TypeError`. The storage decoder in `app` must type-check before calling it.

## Non-goals honoured

Changed 2026-10-15 (code-review WR-01, solver). The paragraph below is 1.0's. Its sentence that `toggleDay` refuses days older than 7 and any day outside the strip is no longer true, because v1.1.0's R9 makes `toggleDay` accept any day of the year (`yearStart` to today). The v1.1.0 non-goals are in the task sections below.

No DOM, rendering, storage or decoding. No clock read and no timer (`todayKey` is always an argument; `purity.test.js` scans for it). No `Intl`, no locale, English tables only. No stored time zones and no UTC day keys. No user-facing copy beyond the R4 labels. No cache or memoisation. No weekly targets, no rename or reorder function, `toggleDay` refuses days older than 7 and any day outside the strip, `done` is a set of days, no stats beyond current streak, best streak and the heatmap, no export or import. Habit objects are rebuilt as `{ name, done }` literals (Threat model, row Object integrity. Why, see the comment on `copyHabit`), and the only regular expression on stored data is `^\d{4}-\d{2}-\d{2}$`.

## Exports (for the README reconcile)

`src/dates.js`: `localDateKey`, `isDateKey`, `addDays`, `dayParts`, `shortDate`, `longDate`, `weekdayIndex`, `yearDate`, `monthTitle`. Imports nothing.
`src/habits.js`: `MAX_HABITS` (12), `MAX_NAME_LENGTH` (40), `currentStreak`, `bestStreak`, `toggleDay`, `heatmapCells`, `monthLabels`, `yearStart`, `doneFlags`, `yearMonths`, `validateName`, `addHabit`, `deleteHabit`. Imports only `./dates.js`.
Changed v1.1.0 (tasks 7 and 8): `yearDate`, `monthTitle`, `yearStart`, `doneFlags` and `yearMonths` are new. `weekWindow`, `runContinues` and `heatLevel` are removed (R5, R8 and R11 retired). The 1.0 list above is in git tag `v1.0.0`.
Private helpers are not listed here and do not belong in the README. The source is their record. Changed 2026-10-09 (code review WR-08): an incomplete list of them was removed.

## How to run

From the project root, in the foreground:

```
node --test "tests/**/*.test.js"
```

No install, no `package.json`, no server, no browser. Node 24 (built on 24.11.1). The tests read `docs/design/sample-history.json` and write nothing under `docs/`. (Changed v1.1.0 task 6: the three 1.0 suites now read `tests/fixtures/sample-history-v1.0.0.json`, see below.)

## v1.1.0 task 6, the test data fix (2026-10-14)

The design finalize of 2026-10-13 replaced `docs/design/sample-history.json`, so the 1.0 suites that read it went red. Task 6 restores the 1.0 data as a test fixture. No change in `src/`.

- `tests/fixtures/sample-history-v1.0.0.json`: the 1.0 file, 5354 bytes, LF line ends.
- `tests/fixtures/sample.js`: `sampleHabits(file)`, which reads the v1.1.0 sample (a path or URL) and returns habits of the `Habit` shape, using the module's own `addDays`. No test calls it yet, tasks 8 and 9 do. Checked by hand against the current `docs/design/sample-history.json` (12 habits, first habit 250 days, 2025-10-10 to 2026-10-10).
- `tests/habits.test.js`, `tests/purity.test.js`, `tests/sample-history.test.js`: the JSON import points at the fixture. Nothing else changed in them.

Proof. `node --test "tests/**/*.test.js"` gives 99 tests, 99 pass, 0 fail on the unchanged `src/`. Blob id check, byte exact with `git hash-object --no-filters` (`core.autocrlf` is true here): the fixture gives `62620300113514b9712d0cbdfea2b15534e6d326`, and `git rev-parse v1.0.0:docs/design/sample-history.json` gives the same.

Deviations: none. Non-goals honored: `docs/design/` untouched, no `src/` change.

## v1.1.0 task 7, the year labels (2026-10-14)

`src/dates.js` gains `yearDate(key)` ("Fri 10 Oct 2025", the R4 `shortDate` plus a 4-digit year) and `monthTitle(key)` ("October 2026"), both from the existing tables, so they are the same in every locale (R17).

- `tests/dates.test.js`: three `@R17` tests (five qa rows, a year before 1000 to prove the 4-digit pad, and the German-default child). The child code of the `@R4` locale test moved into the helper `labelsInGermanChild(calls)` so both locale tests share it (DRY). The `@R4` test asserts the same values as before.
- `tests/purity.test.js`: the export list and the frozen-input calls gain the two names.

RED first. A throwaway stub (`() => ""`, never committed) made the three `@R17` tests fail on the label value, 99 pass, 3 fail of 102. Capture: `docs/modules/habit-logic/qa/red-first/20261014T130716-task7/red.txt`. One of my expected values was wrong (0999-01-01 is a Tuesday) and was corrected against Python's calendar, not against the code's output.

Proof. `node --test "tests/**/*.test.js"` gives 102 tests, 102 pass. Chromium browser suite (`python -m pytest tests/browser -q`), 182 passed.

Deviations: none. Non-goals honored: no clock, no `Intl`, no copy beyond the labels.

## v1.1.0 task 8, the year in `habits.js` (2026-10-14)

`src/habits.js` gains `yearStart` (R18), `doneFlags` (R19) and `yearMonths` (R20). `toggleDay` now accepts any valid day from `yearStart(todayKey)` to `todayKey` (R9). `heatmapCells` cells carry `done` (built by `doneFlags`) and `count`, and no `level` (R10). `weekWindow`, `runContinues` and `heatLevel` are removed, with the private `doneCountsByDay` (dead once `doneFlags` builds the cell).

- `yearStart` rebuilds the key from its text (year less one, same month and day). 29 February falls back to 28 February (CG-13). Why text and not date arithmetic, see the comment on `yearStart`.
- `yearMonths` walks from today's month back until it reaches the month of `yearStart`, so the 13 comes from the rule and not from a constant. Each month is walked day by day with `addDays`, no month-length table.
  Changed 2026-10-15 in the v1.1.0 regression (task 9a). The walk also stops after 13 months, the constant `YEAR_VIEW_MONTHS`, so it ends for every key. For a key that passes `isDateKey` both stops fall on the same month, so there the 13 still comes from the rule. See the section of task 9a.
- `doneFlags` is one `includes` per habit. `heatmapCells` calls it once per non-future cell, at most 84 calls (Threat model, responsiveness row).
- Tests. `tests/habits.test.js`: the `@R5`, `@R8` and `@R11` tests are removed, the `@R9` and `@R10` tests changed, new `@R18`, `@R19`, `@R20` tests. `tests/purity.test.js`: the export list and the frozen-input calls follow the new exports, plus `@R20 @R16 yearMonths reads no clock` (the clock scan became the shared helper `assertNoClockRead`). `tests/sample-history.test.js`: the 1.0 sample checks lose the strip, run flag and level lines and gain the done-flag and count checks (counts 3, 30, 28, 20 for 0 to 3 habits). The qa rows that read the v1.1.0 sample are task 9.

RED first. The tests were written before the code. `src/habits.js` kept its 1.0 form plus a throwaway stub (`yearStart` gave `""`, `doneFlags` gave `[]`, `yearMonths` read `new Date()` and gave `[]`), never committed. 129 tests, 112 pass, 17 fail, each on the asserted property (the absence property of `@R20 @R16` failed on the stub's clock read). Capture: `docs/modules/habit-logic/qa/red-first/20261014T140319-task8/red.txt`.

Proof. `node --test "tests/**/*.test.js"` gives 129 tests, 129 pass (dates 18, habits 43, sample-history 6, purity 6, ring 16, storage 40). Chromium browser suite (`python -m pytest tests/browser -q`), 8 passed, 2 xfailed (strict), nothing red. The 1.0 `src/view.js` still imports `weekWindow` and `runContinues`, so the page's module graph no longer links until app task 15 replaces it (expected, ordered by the orchestrator). The 8 passing browser tests do not depend on it.

Deviations: none. Non-goals honored: no clock, no `Intl`, no start date per habit, no caching, no ring geometry.
Commit: `9a79991`.

## v1.1.0 task 9, the v1.1.0 sample checks (2026-10-14)

`tests/sample-history.test.js` gains eight tests that read `docs/design/sample-history.json` (read-only) through `sampleHabits` from `tests/fixtures/sample.js`. No `src/` change.

- Fixture check: today 2026-10-10, 12 habits, 366 characters each, valid ascending unique days inside `from` to `to`.
- `@R19`: `doneFlags` for the first three habits on four days, and all twelve habits on 2026-10-10 (7 true, in the qa order).
- `@R19 @R6 @R7`: Current and Best for all twelve habits, the table of today-full.md.
- `@R10 @R19`: the band of 12 weeks for the first three habits, 2026-07-20 to 2026-10-11, today at column 12 row 6, the only future cell 2026-10-11, and over the 83 days 2 at count 0, 16 at 1, 47 at 2, 18 at 3.
- `@R9 @R6 @R7`: five ticks with the resulting Current and Best, and the two edges (2025-10-09, 2026-10-11) that change nothing.
- `@R20 @R19`: `yearMonths("2026-10-10")` has 366 open, 21 closed, 9 empty days, the open days are 366 in a row from `from` to `to`, and `doneFlags` of every open day equals the file's own character at that position. The file is read a second time raw for that, so the helper's conversion is checked against the data and not against itself.

RED first. The code under test landed in task 8, so a missing export could not be used. Three throwaway changes to `src/habits.js` (`doneFlags` all false, `yearStart` returning today, `currentStreak` always counting from yesterday) failed 8 of 14, and a fourth run with `yearStart` one day too early failed the edge test too (9 of 14). All restored, `git diff src/` empty. Capture: `docs/modules/habit-logic/qa/red-first/20261014T141400-task9/red.txt`.

Proof. `node --test "tests/**/*.test.js"` gives 137 tests, 137 pass (dates 18, habits 43, sample-history 14, purity 6, ring 16, storage 40). Chromium browser suite, 8 passed, 2 xfailed (strict).

Deviations: none. Non-goals honored: `docs/design/` read only, nothing written there.

## v1.1.0 solver round on the step 5 code review (2026-10-15)
> Written by the dev solver (solver role), 2026-10-15. The verdicts are in `findings/code-review.md`, section "Solver round 2026-10-15".

- WR-01 (`0f7f68b`). Tasks 6 to 9 ticked in `spec.md` with a dated note, rows 6 to 9 in "Tasks to commits" above, the 1.0 count and the 1.0 non-goals paragraph each with a dated line.
- WR-02 (`9fe4a70`). `tests/purity.test.js` calls `yearMonths` while `globalThis.Date` is `ClockReadDate`, which throws on `new Date()` with no argument and on `Date.now`, restored in a `finally`. The scan line the test repeated is gone, `@R16 the source has no clock or random read` holds it. RED under the aliased-clock mutants H12 and H13 (only this test fails, "a clock read, new Date() with no argument"), green on the code, `docs/modules/habit-logic/qa/solver/20261015-142752-wr02-node/`. The folder `20261015-142734-wr02-node/` before it is void, its load hook did not apply on the CRLF checkout.
- WR-03 is the orchestrator's (the README).
- Proof. `docs/modules/app/qa/functional/20261015-142907-node/`, 137 of 137.

For the planner. qa.md "yearMonths reads no clock" reads "Given the purity scan of @R16 over src/habits.js with the new exports / Then it passes, and yearMonths called twice with the same key gives equal results". Recommended. "Given globalThis.Date is a stand-in that throws when it is called with no argument and from Date.now / Then yearMonths called twice with the same key gives equal results and throws nothing, and Date is the real one again after the test".

## v1.1.0 task 9a, the bound on `yearMonths` (2026-10-15)
> Written by the dev solver (solver role), 2026-10-15, in the v1.1.0 regression's targeted pass (ledger H-06, owner ruling USER 2026-10-15 21:03, option 1, security finder SEC-R01). The code commit is `eafc9e5` `fix(habit-logic): yearMonths stops after 13 months, so it ends for every key (task 9a, R20, SEC-R01)`. App task 28a (`40848ce`, the comment of `firstControl`) was built in the same pass, after it. This section, the spec ticks, the proof folders and the handoff are the docs commit after both.

### Phase skills
None. Task 9a is logic in `src/habits.js` and task 28a changes a comment, so neither is UI work and the design row of `docs/phase-skills.md` does not apply (its "execute (non-UI)" row assigns none).

### What changed
- `src/habits.js` `yearMonths`. The walk returns at the month of `yearStart` or once it holds 13 months, whichever comes first. New module constant `YEAR_VIEW_MONTHS` (13), not exported. The doc comment says the 13 is exact for a key that passes `isDateKey`, and why the walk also stops after 13 months (a key from a clock past the year 9999 can give `yearStart` a month the walk never writes). Its `@returns` says "13 months for a key that passes `isDateKey`, never more than 13". No other function, export or import changed.
- `tests/habits.test.js`. New test `@R20 yearMonths ends for every key and returns at most 13 months`, the qa.md Scenario Outline of that name, its 13 Examples rows as subtests. Each row calls `yearMonths` in a worker thread (`node:worker_threads`, an `eval` source that reaches the module through `import()`) with a heap limit of 256 MB and a timer of 5 s. The worker posts the month count or the error for each key. A worker stopped by either, or one that posts nothing or exits non-zero, fails its row with "did not end". The 920-key row runs all its keys in one worker under one timer. Preconditions, 920 distinct keys and each fails `isDateKey`. New import `Worker`. No existing test changed.

### The timer (the solver's choice, qa.md)
5 s. On the bounded code a single-key row takes about 20 to 30 ms, worker start included, and the 920-key row about 250 ms (`node-test.txt` of the pre-commit and the Node proof run), so the timer is about 20 times the slowest row. On the unbounded code the workers reached the heap limit after about 3.7 to 4.6 s, so there the timer and the heap limit race and either stop is "did not end". If every row ran on, 13 rows of 5 s is 65 s, inside the finder's 120 s cap.

### RED first
Two runs of the whole Node suite on HEAD `a6f7e18`, `src/` equal to HEAD and the new test in the working tree, each in its own folder in `docs/modules/habit-logic/qa/red-first/` (`junit.xml`, `node-test.txt`, `run.json`).
1. `20261015-223128-task9a-node`. 151 tests, 143 pass, 8 fail, 30.8 s, exit 1. The rows 10000-10-01, 10000-10-15, 10000-12-31, 10005-11-20, 10009-10-01, 10009-12-31 and the 920-key row fail, each "did not end, stopped by the heap limit of 256 MB", and so does their parent test. The three valid-key rows (13 months) and the last three rows pass in the same run, the control that the worker harness works. The row titles of this run held the key in quotes, which Node's junit reporter escapes twice (`&amp;quot;`), so the quotes were dropped.
2. `20261015-223234-task9a-node`, the test as committed. The same 8 fail and 143 pass, 34.3 s. Five far rows were stopped by the timer and two by the heap limit, each "did not end".
Neither run hung or crashed, and both ended well inside the 120 s cap.

### Green and the differential
- Pre-commit, the working tree with the bound, `docs/modules/habit-logic/qa/solver/20261015-223406-precommit-node/`, 151 of 151 in 1.1 s. A check, not the proof.
- The contract's one-off differential, run in the session scratchpad and not committed. `yearMonths` before the bound (`git show ad40779:src/habits.js`, extracted with `git archive`, blob `cee86af` as in that commit) and after it returned deep-equal results (`util.isDeepStrictEqual`) for every day from 1999-01-01 to 2101-12-31 (37,620 keys, 37.7 s) and for the first day of every month of the years 0001 to 9999 (119,988 keys, 120.8 s). 0 differences, and every result held 13 months. Its control in the same run flagged a result cut to 12 months and one with one day's `kind` changed.

### Proof (the committed tree `40848ce`, after app task 28a)
Each run in its own folder under `docs/modules/habit-logic/qa/solver/`, made with a scratch runner (`streaks-9a/run_suite.py` in the session scratchpad). It bounds the run with a timeout, writes the run's output and `run.json` into a new folder it creates and refuses to reuse, and records `src/`, `tests/` and `index.html` equal to HEAD at the start and the end of every proof run.
- Node, `20261015-224014-node/`, 151 of 151 (137 before, plus the new test and its 13 rows). By id against `docs/modules/app/qa/regression-qa/20261015-184158-node/`, the 137 ids all pass, 13 rows are added, no outcome changed (`compare-ids.txt`).
- Chromium, `20261015-224041-chromium/`, 358 passed in 175.2 s. By id against `docs/modules/app/qa/regression-qa/20261015-184210-chromium/`, the same 358 ids and no outcome changed (`compare-ids.txt`).
- WebKit, `20261015-224353-webkit/`, 357 passed and 1 skipped (CO-1, `chromium_only` with its reason) in 291.0 s, a background job bounded at 1080 s with no other browser run at the same time. By id against `docs/modules/app/qa/regression-qa/20261015-184449-webkit/`, the same 358 ids and the same outcomes (`compare-ids.txt`).
- The security finder's probes `probe_11_year10000.py` (group `hang`) and `probe_14_rollover_hang.py` with `lib.py`, copied from `docs/modules/app/qa/regression-security/20261015-192841/` into the session scratchpad and run once per engine, captures in `20261015-224907-probes-chromium/` and `20261015-225045-probes-webkit/`. The two probes are byte for byte the finder's (sha256 in each `run.json`). `lib.py` differs in one line, `ROOT`, because the finder's `HERE.parents[5]` finds the project only from a folder at that depth, so the copy names the project root instead.
  - At 10000-10-15 the row's Year and the band's Year each returned in about 0.05 s and the page answered at once, with 0 page errors, in both engines. The finder's `probe_11_chromium_hang.txt` and `probe_11_webkit_hang.txt` show the same presses timing out after 3 s and the page not answering. They are the control, so the freeze was not run again.
  - At the midnight into 10000-10-01 with P4 open, after 35 s of real time the page answered, showed 10000-10-01 and still had P4 open, in both engines. Its one page error came before midnight, from the first press of the band's Year in September of a five digit year (`TypeError`, the re-accepted SEC-05 residual). The finder's `probe_14_rollover_hang.txt` shows this case not answering. The control case, nothing open, answered in both runs.
  - The hang group prints whether the page answers, not what P2 and P4 hold after the press. What a year view shows at those clocks is left to the security re-check.

### Judgment calls (named, for the orchestrator)
1. The rows are subtests of one `test()`, so the RED capture reports each row pass or fail on its own. Node counts the test and its rows, so the suite count moves from 137 to 151 (`junit.xml` holds 150 testcases, the parent being a testsuite).
2. The 13 is the named constant `YEAR_VIEW_MONTHS`, as `HEATMAP_WEEKS` names the 12. It is not exported, so the export and purity checks (R16) are unchanged and green.
3. The bound is checked after the push with `===`, so the walk ends at exactly 13 months, the count the rule gives for a valid key.
4. The worker runs an `eval` source rather than a second file, so the test lives in `tests/habits.test.js` alone, as the task names.

### Deviations
None in the code. No dependency, no contract change.
Process. The runner writes each run's console output and `run.json` with Python into the run's new folder, as the task 27a runner did. Every other file was written with the Write or Edit tool.
Process slip. Eight commands redirected stderr (`2>&1` or `2>/dev/null`), which the brief's ban on shell redirection covers. Seven were read-only listings or diffs, and one was the `git add` of the docs commit, its output filtered with `grep`. None wrote a file through the redirection.

### Non-goals honoured (spec, Non-goals, ledger H-06)
No `isDateKey` call in `yearMonths`. No guard for five digit years in `localDateKey`, `yearStart`, `heatmapCells` or `toggleDay`. The result for every key the differential covered is unchanged. No app guard on the year views. `docs/design/` read only and nothing written there.

### For the README reconcile
- `src/habits.js` `yearMonths` returns at most 13 months for any key and always ends, exactly 13 for a key that passes `isDateKey`. New private constant `YEAR_VIEW_MONTHS`.
- `tests/habits.test.js` gains `@R20 yearMonths ends for every key and returns at most 13 months` (13 rows). The Node suite is 151 tests.
- The README's Known limits row on the year 10000 still says that from October to December of those years opening a year view freezes the tab. After the bound the probes show the page answering at 10000-10-15 and at the midnight into 10000-10-01 with P4 open, in both engines.
