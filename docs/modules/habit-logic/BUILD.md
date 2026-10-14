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

5 of 5 tasks done. Every commit was made with the full suite green.

## Final test run

~~`node --test "tests/**/*.test.js"` gives 60 tests, 60 pass, 0 fail, exit 0 (about 0.5 s).~~
~~Per file: `dates.test.js` 14, `habits.test.js` 34, `sample-history.test.js` 7, `purity.test.js` 5.~~
After the code-review fixes of 2026-10-09: 61 tests, 61 pass, 0 fail. The one added test is the `weekdayIndex` scenario in `dates.test.js` (WR-04).
Changed 2026-10-09 (security SEC-01 to SEC-03, ORCH): the two struck lines were the first build's counts and no longer hold. `node --test "tests/**/*.test.js"` now gives 64 tests, 64 pass, 0 fail, exit 0 (about 0.6 s, `eb2003b`). Per file: `dates.test.js` 15, `habits.test.js` 37, `sample-history.test.js` 7, `purity.test.js` 5. The three added tests are in `habits.test.js`: two streak-walk tests (SEC-01) and the name-length read count (SEC-02). SEC-03 widened two `purity.test.js` tests in place.
Changed 2026-10-09 (security re-check SEC-01, ORCH): the 64 above held at `eb2003b`. After the re-check's SEC-01 fix the suite gives 66 tests, 66 pass, 0 fail, exit 0. Per file: `dates.test.js` 15, `habits.test.js` 39, `sample-history.test.js` 7, `purity.test.js` 5. The two added tests are in `habits.test.js`: 20,000 spellings of one far-out date in one pass, and invalid keys not counted.
Every `test()` title starts with its `@R#` tag.

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
- `doneFlags` is one `includes` per habit. `heatmapCells` calls it once per non-future cell, at most 84 calls (Threat model, responsiveness row).
- Tests. `tests/habits.test.js`: the `@R5`, `@R8` and `@R11` tests are removed, the `@R9` and `@R10` tests changed, new `@R18`, `@R19`, `@R20` tests. `tests/purity.test.js`: the export list and the frozen-input calls follow the new exports, plus `@R20 @R16 yearMonths reads no clock` (the clock scan became the shared helper `assertNoClockRead`). `tests/sample-history.test.js`: the 1.0 sample checks lose the strip, run flag and level lines and gain the done-flag and count checks (counts 3, 30, 28, 20 for 0 to 3 habits). The qa rows that read the v1.1.0 sample are task 9.

RED first. The tests were written before the code. `src/habits.js` kept its 1.0 form plus a throwaway stub (`yearStart` gave `""`, `doneFlags` gave `[]`, `yearMonths` read `new Date()` and gave `[]`), never committed. 129 tests, 112 pass, 17 fail, each on the asserted property (the absence property of `@R20 @R16` failed on the stub's clock read). Capture: `docs/modules/habit-logic/qa/red-first/20261014T140319-task8/red.txt`.

Proof. `node --test "tests/**/*.test.js"` gives 129 tests, 129 pass (dates 18, habits 43, sample-history 6, purity 6, ring 16, storage 40). Chromium browser suite (`python -m pytest tests/browser -q`), 8 passed, 2 xfailed (strict), nothing red. The 1.0 `src/view.js` still imports `weekWindow` and `runContinues`, so the page's module graph no longer links until app task 15 replaces it (expected, ordered by the orchestrator). The 8 passing browser tests do not depend on it.

Deviations: none. Non-goals honored: no clock, no `Intl`, no start date per habit, no caching, no ring geometry.
