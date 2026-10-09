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

`node --test "tests/**/*.test.js"` gives 60 tests, 60 pass, 0 fail, exit 0 (about 0.5 s).
Per file: `dates.test.js` 14, `habits.test.js` 34, `sample-history.test.js` 7, `purity.test.js` 5.
After the code-review fixes of 2026-10-09: 61 tests, 61 pass, 0 fail. The one added test is the `weekdayIndex` scenario in `dates.test.js` (WR-04).
Every `test()` title starts with its `@R#` tag.

## Deviations

None from the spec's Requirements or Contracts. Decisions inside the spec's room, for the reviewer:

- **`weekdayIndex` is a seventh export of `dates.js`**, added by ORCH ruling on 2026-10-09 (code review WR-04). The first build had no weekday index in the Contracts, so it found the current Monday by its `"Mon"` label inside the 7-day strip, which tied the heatmap's weeks to the strip's width and to a display label. How the Monday is found now, see the comment on `columnMondays`.
- **Day arithmetic uses integer day counts** (`daysFromCivil`, `civilFromDays` in `dates.js`), the second option R3 and the Invariants allow. `Date.UTC` maps years 0 to 99 into the 1900s, which would break `0001-01-01`, a key `isDateKey` accepts. The result is checked against UTC reference maths for every day from 1900 to 2100 in both zones (`tests/dates.test.js`).
- **`dayParts` abbreviates by slicing the first three letters** of the full-name tables (every English weekday and month here abbreviates that way), so there is one table per kind, not two.
- **Tests beyond the qa.md rows** (each tagged to its R#): zone-switch proof, exhaustive `isDateKey` and `addDays` and weekday agreement with a UTC reference, hostile long strings, R8 rows built from synthetic data (qa.md has only the sample rows for R8), unsorted or duplicated `done` input to `toggleDay`, copy-not-alias checks, code-point and white-space edge cases for `validateName`, and an exact export list in `purity.test.js` that doubles as the guard that the frozen-input test calls every export.
- **The R4 locale scenario runs in a child process** with `LANG` and `LC_ALL` set to `de_DE.UTF-8`, German made the default of the date locale APIs, and a precondition that the default really is German. Why, see the comment in the test `@R4 labels do not follow the runtime locale`. The child exits at once (15 s timeout). Corrected 2026-10-09 (code review WR-01): the first version relied on `LANG` alone, which Node ignores on Windows.
- **Process note.** The R10 to R12 test block was appended to `tests/habits.test.js` with a shell heredoc to a relative in-project path (no backslashes in the payload, content confirmed by the following run). Later edits used the Edit and Write tools. Scratch scripts in `harness/_scratch/` (git-ignored) were created the same way.

Unspecified edges, noted and not built (outside every R#):

- `addDays` past year 9999 or before year 0001 returns a key that `isDateKey` rejects. The app never goes near these.
- `validateName` expects a string. A non-string `raw` throws a `TypeError`. The storage decoder in `app` must type-check before calling it.

## Non-goals honoured

No DOM, rendering, storage or decoding. No clock read and no timer (`todayKey` is always an argument; `purity.test.js` scans for it). No `Intl`, no locale, English tables only. No stored time zones and no UTC day keys. No user-facing copy beyond the R4 labels. No cache or memoisation. No weekly targets, no rename or reorder function, `toggleDay` refuses days older than 7 and any day outside the strip, `done` is a set of days, no stats beyond current streak, best streak and the heatmap, no export or import. Habit objects are rebuilt as `{ name, done }` literals (Threat model, row Object integrity. Why, see the comment on `copyHabit`), and the only regular expression on stored data is `^\d{4}-\d{2}-\d{2}$`.

## Exports (for the README reconcile)

`src/dates.js`: `localDateKey`, `isDateKey`, `addDays`, `dayParts`, `shortDate`, `longDate`, `weekdayIndex`. Imports nothing.
`src/habits.js`: `MAX_HABITS` (12), `MAX_NAME_LENGTH` (40), `weekWindow`, `currentStreak`, `bestStreak`, `runContinues`, `toggleDay`, `heatmapCells`, `heatLevel`, `monthLabels`, `validateName`, `addHabit`, `deleteHabit`. Imports only `./dates.js`.
Internal (not exported): `copyHabit`, `runLength`, `toggledHabit`, `columnMondays`, `doneCountsByDay` in `habits.js`; `formatKey`, `parseKey`, `daysFromCivil`, `civilFromDays`, `namesOf` and the label tables in `dates.js`.

## How to run

From the project root, in the foreground:

```
node --test "tests/**/*.test.js"
```

No install, no `package.json`, no server, no browser. Node 24 (built on 24.11.1). The tests read `docs/design/sample-history.json` and write nothing under `docs/`.
