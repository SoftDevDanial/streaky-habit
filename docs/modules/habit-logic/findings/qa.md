---
module: habit-logic
kind: qa
ran_against: running-app
status: green
counts: { pass: 42, fail: 0, blocked: 0 }
---
# QA findings: habit-logic (v1.1.0, step 5)

**Verdict. PASS.** 42 of 42 live scenarios in `docs/modules/habit-logic/qa.md` are held by a test that ran green in my own run. Fail 0. Untested 0. Blocked 0. The 3 retired scenarios (one `@R5`, two `@R11`) are text only and are not counted.

Role. QA finder (read-only), written 2026-10-15. This module has no UI, so the running app is the module code under Node. It replaces the 1.0 verdict of 2026-10-09 (HEAD `7b79ea1`).

## Run

| Item | Value |
|---|---|
| Git HEAD | `4e860ff5c84b18c2777ebce8c203b963bd7c3610`. `git status` shows no change under `src/`, `tests/`, `index.html` or `docs/design/` before and after my runs |
| Node | v24.11.1 on Windows 11, no server, no browser, no process left behind |
| Command | `timeout 120 node --test --test-reporter=spec "tests/**/*.test.js"`, run once, foreground, exit 0 |
| Capture | `docs/modules/habit-logic/qa/qa-node/20261015-081009/node-test.txt` (listed on disk, written with the Write tool from the runner's stdout) |
| Counts read from the capture | tests 137, pass 137, fail 0, cancelled 0, skipped 0, todo 0, 609.7 ms |

The 137 tests are 81 habit-logic tests, 16 in `tests/ring.test.js` (`@R42`, the app's) and 40 in `tests/storage.test.js` (the app's `@R16`, `@R17`, `@R41`, `@T2`). The `@R#` tags of those 56 mean the app's requirements, not this module's. They are mapped in `docs/modules/app/findings/qa.md`. The split comes from the titles in the capture (the storage tests are the last 40 test lines).

## How I judged
- Mapped each of the 42 live scenarios to the test title that starts with its tag, by reading the titles in the capture against `qa.md`.
- Spot-read the v1.1.0 tests against their Examples tables, row by row. They are `toggleDay` (the 6, 6 and 3 rows), `yearStart` (5 rows), `doneFlags`, `yearMonths` (the goldens' year and the 4 other days), `monthTitle` and `yearDate`, and the 12-habit Current and Best table. I also grepped further literals of other tables (`2026-03-31`, `2027-01-07`, `Thursday 15 October`, `Tuesday 15 December`, `2100-02-29`, `FAR_START`, `America/New_York`) in the test files. All were present.
- I did not re-derive every row of the 1.0 Outlines (R1 to R4, R6, R7, R12 to R16) with an independent probe this run. Those tests carry rows that the earlier finder cross-checked with a probe, and they pass. Treat their row-level strength as inherited from the 1.0 verdict, not re-proved here.

## Scenario map

| # | Scenario | R# | Test(s) in the capture | Verdict |
|---|---|---|---|---|
| 1 | The local calendar day of an instant (6 rows) | R1 | `@R1 the local calendar day of an instant`, `@R1 @R3 the zone switch is real`, `@R1 the UTC date is not used`, `@R1 month and day are zero padded` | PASS |
| 2 | Valid date keys (17 rows) | R2 | `@R2 valid and invalid date keys`, `@R2 agrees with a calendar reference ... 1900 to 2100`, `@R2 a long hostile string is rejected quickly` | PASS |
| 3 | Calendar arithmetic that ignores the time zone (11 rows) | R3 | `@R3 calendar arithmetic that ignores the time zone`, `@R3 century and year edges`, `@R3 agrees with UTC reference maths ... both zones` | PASS |
| 4 | Short weekday, day and month (9 rows) | R4 | `@R4 short weekday, day and month for every weekday` | PASS |
| 5 | Short and long month names (14 rows) | R4 | `@R4 short and long month names for every month` | PASS |
| 6 | The weekday index, Monday first (9 rows) | R4 | `@R4 weekdayIndex counts Monday as 0 to Sunday as 6`, `@R4 weekday names and indexes agree with a UTC reference ...` | PASS |
| 7 | Labels do not follow the runtime locale | R4 | `@R4 labels do not follow the runtime locale` | PASS |
| 8 | The sample's streaks on the 1.0 key screen (3 rows) | R6 R7 | `@R6 @R7 the sample's streaks on the 1.0 key screen` | PASS |
| 9 | The same sample one day later (3 rows) | R6 | `@R6 the same sample one day later` | PASS |
| 10 | A streak does not break until today is over (8 rows) | R6 | `@R6 a streak does not break until today is over`, `@R6 a streak runs across a month, a year and a leap day` | PASS |
| 11 | A streak that crosses a DST change | R6 | `@R6 a streak that crosses a DST change` | PASS |
| 12 | The longest run in the whole history (7 rows) | R7 | `@R7 the longest run in the whole history`, `@R7 the best run may be old ...` | PASS |
| 13 | Keys that fail isDateKey are ignored (4 rows) | R6 R7 | `@R6 @R7 keys that fail isDateKey do not count ...`, `@R7 many spellings of one far-out date ...`, `@R7 the best-run walk ends on keys outside the valid range ...`, `@R6 the current-run walk ends on the cycle below year 0001` | PASS |
| 14 | Ticking a day inside the window (6 rows) | R9 | `@R9 ticking a day in the last week of the year` | PASS |
| 15 | Days outside the year and bad indexes change nothing (6 rows) | R9 | `@R9 days outside the year, bad dates and bad indexes change nothing` | PASS |
| 16 | Any day of the last 12 months can be ticked (3 rows) | R9 | `@R9 any day of the last 12 months can be ticked ...`, `@R9 both ends of the year are editable ...` | PASS |
| 17 | Ticks on the v1.1.0 sample move Current and Best (5 rows) | R9 R6 R7 | `@R9 @R6 @R7 ticks on the v1.1.0 sample move Current and Best` | PASS |
| 18 | The edges of the v1.1.0 year (2 rows) | R9 | `@R9 the edges of the v1.1.0 year ...`, `@R9 @R18 on 29 February the year starts on 28 February ...` | PASS |
| 19 | The 12-week grid around today (5 rows) | R10 | `@R10 the 12-week grid around today`, `@R10 a cell carries exactly the contract fields ...` | PASS |
| 20 | The 1.0 sample's 12 weeks | R10 | `@R10 the 1.0 sample's 12 weeks` | PASS |
| 21 | The v1.1.0 sample's band | R10 R19 | `@R10 @R19 the v1.1.0 sample's band of 12 weeks`, `@R10 @R19 a cell's done is doneFlags of its day` | PASS |
| 22 | A fourth habit counts in total and done | R10 | `@R10 a fourth habit counts in total and in done` | PASS |
| 23 | Month labels over the first column whose Monday is in the month (4 rows) | R12 | `@R12 month labels over the first column ...`, `@R12 each label sits on the first column ...` | PASS |
| 24 | Labels with the year (5 rows) | R17 | `@R17 labels with the year`, `@R17 the year is four digits, also before the year 1000` | PASS |
| 25 | The year labels do not follow the runtime locale | R17 | `@R17 year labels do not follow the runtime locale` | PASS |
| 26 | The same date last year (5 rows) | R18 | `@R18 the same date last year, and the year's day count` | PASS |
| 27 | Which habits are done on a day (4 rows) | R19 | `@R19 which habits are done on a day, one boolean per habit in list order`, `@R19 which habits are done on a day, for the v1.1.0 sample's first three habits` | PASS |
| 28 | No habits gives an empty list, twelve give the golden's count | R19 | `@R19 no habits gives an empty list, and every call returns a new array`, `@R19 all twelve habits on 2026-10-10 give the golden's 7 done, and none on an empty list` | PASS |
| 29 | The goldens' Current and Best (12 rows) | R19 R6 R7 | `@R19 @R6 @R7 the goldens' Current and Best come from the v1.1.0 sample` | PASS |
| 30 | The year of the goldens | R20 | `@R20 the year of the goldens`, `@R20 @R19 the v1.1.0 sample's year has 366 open days ...` | PASS |
| 31 | The year on other days (4 rows) | R20 | `@R20 the year on other days`, `@R20 every call returns new objects` | PASS |
| 32 | yearMonths reads no clock | R20 R16 | `@R20 @R16 yearMonths reads no clock, so two calls with one key give equal results` | PASS |
| 33 | Name checks in the order empty, too long, duplicate (8 rows) | R13 | `@R13 name checks in the order empty, too long, duplicate`, `@R13 the length rule counts the trimmed name ...` | PASS |
| 34 | Too long is checked before duplicate | R13 | `@R13 too long is checked before duplicate` | PASS |
| 35 | Length counts code points, not UTF-16 units | R13 | `@R13 length counts code points, not UTF-16 units`, `@R13 the length check reads at most 41 code points ...` | PASS |
| 36 | The limits are exported | R13 | `@R13 @R14 the limits are exported` | PASS |
| 37 | A new habit goes to the bottom | R14 | `@R14 a new habit goes to the bottom` | PASS |
| 38 | A rejected name returns its error | R14 | `@R14 a rejected name returns its error` | PASS |
| 39 | The limit of 12 habits (3 rows) | R14 | `@R14 the limit of 12 habits is checked before the name`, `@R14 adding to an empty list works` | PASS |
| 40 | Deleting a habit (4 rows) | R15 | `@R15 deleting a habit`, `@R15 deleting from an empty list returns an empty list` | PASS |
| 41 | No clock, DOM, storage or locale access in the source | R16 | `@R16 the source has no clock or random read, even in a comment`, `@R16 the code has no DOM, storage, network, timer, global or locale access ...`, `@R16 habits.js imports only ./dates.js and dates.js imports nothing`, `@R16 only the contracted names are exported` | PASS |
| 42 | No exported function writes to its arguments | R16 | `@R16 no exported function writes to its arguments or returns one of them` | PASS |

The count of 42 live and 3 retired comes from a script over the Gherkin block of `qa.md`. No live scenario carries R5 or R11.

## Fails, untested, blocked
None.

## Process-rule slips by me, disclosed
- One read-only Python count of the scenarios in `qa.md` was fed through a shell heredoc. It wrote nothing.
- One pytest repro line used `2>&1` inside a pipe to `grep`. It wrote no file.
Both are repeated in the app findings.

## PROCESSES
`node --test` ran in the foreground, exited 0 and left nothing. No server, no browser. The closing sweep for the whole session is in `docs/modules/app/findings/qa.md`.

## Re-check 2026-10-15
Written by the QA finder (read-only), the one re-check after the dev solver round (constitution stop rule). The round-1 text above is unchanged. The front matter counts and status are the same as before, because nothing changed in them (42 pass, 0 fail, 0 blocked, green).

**Verdict. PASS.** 42 of 42 live scenarios in `docs/modules/habit-logic/qa.md` are held by a test that ran green in my own run today. Fail 0. Untested 0. Blocked 0. Failing test ids, Node: none. This module has no UI, so the running app is the module code under Node, and it has no browser engine.

### Run

| Item | Value |
|---|---|
| Git HEAD | `c271938d5dd1d6ec6059b31eee9dc578f4825c7f` (`git rev-parse --short HEAD` gave `c271938`, checked first) |
| Folder (listed on disk) | `docs/modules/habit-logic/qa/qa-node/20261015-153148/` holding `node-test.txt` and `run-meta.txt` |
| Command | `node --test --test-reporter=spec "tests/**/*.test.js"`, run once in the foreground by a scratch runner (no shell, no redirection), capped at 120 s with a "gave up" branch, exit 0 in 0.7 s, the cap was not hit |
| Counts read from the capture's own summary lines | tests 137, pass 137, fail 0, cancelled 0, skipped 0, todo 0 (Node writes no junit file) |
| Node | v24.11.1 on Windows 11, no server, no browser, no process left behind |

The 137 tests are the same split as in round 1 (81 habit-logic tests, 16 in `tests/ring.test.js` and 40 in `tests/storage.test.js`, the last two the app's, tagged with the app's `@R#`).

### Did the round-1 map hold
By script over the two captures (round 1 `qa-node/20261015-081009/node-test.txt` against today's). 137 test lines in each, 0 failing marks in either, the set of test titles is identical (no title only in round 1, none only in today's). `docs/modules/habit-logic/qa.md` is unchanged since round 1 (`git diff 4e860ff c271938` lists no change to it), so the scenario map table above stands row for row, all 42 PASS.

The solver round changed `tests/purity.test.js` (WR-02, commit `9fe4a70`), so scenario 32, "yearMonths reads no clock" (`@R20 @R16 yearMonths reads no clock, so two calls with one key give equal results`), is now held by a stronger test. It calls `yearMonths` while `globalThis.Date` throws on a clock read. The title is the same as in round 1 and it passes. The solver's `RED` runs under the aliased-clock mutants are its own evidence (`docs/modules/habit-logic/qa/solver/20261015-142752-wr02-node/`). I did not re-run the mutants, I judge only that the test is green on the code. The `spec.md` of this module also changed (tasks 6 to 9 ticked, WR-01), which does not touch a scenario.

### New tests
None this round in this module. The suite stays at 137 tests. The 7 new tests of the solver round are all browser tests of the `app` module and are traced in `docs/modules/app/findings/qa.md`, section "Re-check 2026-10-15".

### Process-rule slips by me, disclosed
- Read-only listings with `2>/dev/null` and read-only pipes after `ls`, `grep` and `sed`, never after the test runner or git, are disclosed in the app findings.
- The Edit tool was not available, so the section was appended by a scratch Python script with a relative path under the project root. It changed nothing else.
- Nothing was written outside the two verdict files and my own new run folders. `git status` on `src/`, `tests/`, `index.html` and `docs/design/` is empty after my runs.

### PROCESSES
`node --test` ran in the foreground through a scratch runner, exited 0 and left nothing, no server, no browser. The sweeps (baseline 15:31:19, final 15:41:58, method and result) are in `docs/modules/app/findings/qa.md`, section "Re-check 2026-10-15", and covered this run too.
