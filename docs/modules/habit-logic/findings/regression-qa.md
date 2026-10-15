---
module: habit-logic
kind: qa
run: regression
ran_against: running-app
status: green
counts: { pass: 42, fail: 0, blocked: 0, untested: 0 }
---
# Regression QA findings: habit-logic (v1.1.0, full regression)

## Verdict

GREEN. 42 of 42 live scenarios in `docs/modules/habit-logic/qa.md` are held by a test that passed in this run. FAIL 0, BLOCKED 0, UNTESTED 0. The 3 retired scenarios (one `@R5`, two `@R11`) are text only and are not counted.

Role. QA finder (read-only), the full regression at the tail of execute, written 2026-10-15. This module has no UI, so the running app is the module code under Node. Git HEAD `ddf43f6`, code equal to `4af5d75`. `docs/modules/habit-logic/qa.md` is unchanged in that range.

## Run

| Item | Value |
|---|---|
| Folder, listed on disk | `docs/modules/app/qa/regression-qa/20261015-184158-node/` (`junit.xml`, `node-test.txt`, `run-meta.txt`). The Node suite covers both modules, and the brief sets this folder for it, so the same run is the evidence for this file and for the app file |
| Command | `node --test --test-reporter=spec --test-reporter-destination=stdout --test-reporter=junit --test-reporter-destination=<folder>/junit.xml "tests/**/*.test.js"`, foreground, from the project root, capped at 120 s. Exit 0 in 0.7 s |
| Counts, read from the run's own files | `node-test.txt` has `tests 137`, `pass 137`, `fail 0`. `junit.xml` has 137 testcases, all PASS. By the `file` attribute, 81 are this module's (`dates.test.js` 18, `habits.test.js` 43, `purity.test.js` 6, `sample-history.test.js` 14). The other 56 are the app's (`ring.test.js` 16, `storage.test.js` 40) |
| Baseline | The 137 ids equal those of `docs/modules/app/qa/functional/20261015-174935-node/junit.xml`. No verdict changed |
| Node | v24.11.1, Windows 11. No server and no browser was started |

## How I judged

- Each live scenario is held by the junit titles that start with its tag and carry its title words. A script matched them, and the non-obvious matches were checked by hand against the junit names. The 4 rows of L226 and the 2 of L434 were confirmed by their exact titles.
- Row-level strength was not re-derived in this run. The test files are the same as in `4af5d75`.

## The R# table (42 live scenarios, qa.md line numbers)

| R# | Scenario (qa.md line) | Verdict | Observed, held by (Node titles) |
|---|---|---|---|
| R1 | The local calendar day of an instant (6 rows, 30) | PASS | `@R1 the local calendar day of an instant`; `@R1 @R3 the zone switch is real, so the zone cases are not vacuous` |
| R2 | Valid date keys (17 rows, 45) | PASS | `@R2 valid and invalid date keys` |
| R3 | Calendar arithmetic that ignores the time zone (11 rows, 70) | PASS | `@R3 calendar arithmetic that ignores the time zone` |
| R4 | Short weekday, day and month for every weekday (9 rows, 90) | PASS | `@R4 short weekday, day and month for every weekday` |
| R4 | Short and long month names for every month (14 rows, 108) | PASS | `@R4 short and long month names for every month` |
| R4 | The weekday index, Monday first (9 rows, 131) | PASS | `@R4 weekdayIndex counts Monday as 0 to Sunday as 6` |
| R4 | Labels do not follow the runtime locale (149) | PASS | `@R4 labels do not follow the runtime locale` |
| R6 R7 | The sample's streaks on the 1.0 key screen (3 rows, 162) | PASS | `@R6 @R7 the sample's streaks on the 1.0 key screen` |
| R6 | The same sample one day later (3 rows, 176) | PASS | `@R6 the same sample one day later` |
| R6 | A streak does not break until today is over (8 rows, 187) | PASS | `@R6 a streak does not break until today is over` |
| R6 | A streak that crosses a DST change (204) | PASS | `@R6 a streak that crosses a DST change` |
| R7 | The longest run in the whole history (7 rows, 211) | PASS | `@R7 the longest run in the whole history` |
| R6 R7 | Keys that fail isDateKey are ignored (4 rows, 226) | PASS | `@R6 @R7 keys that fail isDateKey do not count, so a streak counts only valid days`; `@R7 many spellings of one far-out date that all run into the stuck key cost one pass, not one walk each`; `@R7 the best-run walk ends on keys outside the valid range, where the next day repeats itself`; `@R6 the current-run walk ends on the cycle below year 0001` |
| R9 | Ticking a day inside the window (6 rows, 240) | PASS | `@R9 ticking a day in the last week of the year` |
| R9 | Days outside the year and bad indexes change nothing (6 rows, 261) | PASS | `@R9 days outside the year, bad dates and bad indexes change nothing` |
| R9 | Any day of the last 12 months can be ticked (3 rows, 276) | PASS | `@R9 any day of the last 12 months can be ticked, even before the habit's history` |
| R9 R6 R7 | Ticks on the v1.1.0 sample move Current and Best (5 rows, 290) | PASS | `@R9 @R6 @R7 ticks on the v1.1.0 sample move Current and Best` |
| R9 | The edges of the v1.1.0 year (2 rows, 305) | PASS | `@R9 the edges of the v1.1.0 year: the day before the start and the day after today change nothing` |
| R10 | The 12-week grid around today (5 rows, 319) | PASS | `@R10 the 12-week grid around today`; `@R10 a cell carries exactly the contract fields, and a habit counts once per day` |
| R10 | The 1.0 sample's 12 weeks (342) | PASS | `@R10 the 1.0 sample's 12 weeks` |
| R10 R19 | The v1.1.0 sample's band (351) | PASS | `@R10 @R19 the v1.1.0 sample's band of 12 weeks` |
| R10 | A fourth habit counts in total and in done (362) | PASS | `@R10 a fourth habit counts in total and in done` |
| R12 | Month labels over the first column whose Monday is in the month (4 rows, 372) | PASS | `@R12 month labels over the first column whose Monday is in the month` |
| R17 | Labels with the year (5 rows, 386) | PASS | `@R17 labels with the year`; `@R17 the year is four digits, also before the year 1000` |
| R17 | The year labels do not follow the runtime locale (399) | PASS | `@R17 year labels do not follow the runtime locale` |
| R18 | The same date last year (5 rows, 405) | PASS | `@R18 the same date last year, and the year's day count` |
| R19 | Which habits are done on a day (4 rows, 421) | PASS | `@R19 which habits are done on a day, for the v1.1.0 sample's first three habits` |
| R19 | No habits gives an empty list, and twelve habits give the golden's count (434) | PASS | `@R19 no habits gives an empty list, and every call returns a new array`; `@R19 all twelve habits on 2026-10-10 give the golden's 7 done, and none on an empty list` |
| R19 R6 R7 | The goldens' Current and Best come from the v1.1.0 sample (12 rows, 441) | PASS | `@R19 @R6 @R7 the goldens' Current and Best come from the v1.1.0 sample` |
| R20 | The year of the goldens (462) | PASS | `@R20 the year of the goldens` |
| R20 | The year on other days (4 rows, 472) | PASS | `@R20 the year on other days`; `@R20 every call returns new objects` |
| R20 R16 | yearMonths reads no clock (485) | PASS | `@R20 @R16 yearMonths reads no clock, so two calls with one key give equal results` |
| R13 | Name checks in the order empty, too long, duplicate (8 rows, 498) | PASS | `@R13 name checks in the order empty, too long, duplicate` |
| R13 | Too long is checked before duplicate (515) | PASS | `@R13 too long is checked before duplicate` |
| R13 | Length counts code points, not UTF-16 units (521) | PASS | `@R13 length counts code points, not UTF-16 units` |
| R13 R14 | The limits are exported (528) | PASS | `@R13 @R14 the limits are exported` |
| R14 | A new habit goes to the bottom (532) | PASS | `@R14 a new habit goes to the bottom` |
| R14 | A rejected name returns its error (540) | PASS | `@R14 a rejected name returns its error` |
| R14 | The limit of 12 habits (3 rows, 546) | PASS | `@R14 the limit of 12 habits is checked before the name`; `@R14 adding to an empty list works` |
| R15 | Deleting a habit (4 rows, 558) | PASS | `@R15 deleting a habit` |
| R16 | No clock, DOM, storage or locale access in the source (574) | PASS | `@R16 the source has no clock or random read, even in a comment`; `@R16 the code has no DOM, storage, network, timer, global or locale access and builds no code from strings`; `@R16 habits.js imports only ./dates.js and dates.js imports nothing` |
| R16 | No exported function writes to its arguments (585) | PASS | `@R16 no exported function writes to its arguments or returns one of them` |

## Notes

- The 42 PASS verdicts are "the held test passed in this run". Both judgements, the held test and its pass, come from the run's own `junit.xml`.
- The Node run also holds the app's 56 Node tests (`ring.test.js` and `storage.test.js`). Those are in `docs/modules/app/findings/regression-qa.md`.
- Process-rule slips and the full PROCESSES block are in the app file. The Node run was foreground, exited 0, and left nothing running. Nothing of this module's files was written by the run.

## PROCESSES

`runner.py node 120` and its `node --test` child (PID 14340) ran in the foreground, exited 0 in 0.7 s, and are STOPPED. The final sweep at 18:54:29 found no node process of mine and no server or browser. The other lanes' processes are listed in the app file, and I did not touch them.
