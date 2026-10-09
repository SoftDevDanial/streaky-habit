---
module: habit-logic
kind: qa
ran_against: running-app
status: green
counts: { pass: 32, fail: 0, blocked: 0 }
---
# QA findings: habit-logic

**Verdict: PASS.** All 32 scenarios in `docs/modules/habit-logic/qa.md` pass. That is 20 Scenario Outlines (137 example rows) and 12 standalone scenarios, 149 rows in all. Failed: 0. Untested: 0. Blocked: 0. Every R1 to R16 has at least one passing scenario.

Ran against: the module exports in `src/` under Node v24.11.1 on Windows 11. There is no UI, so the running app is the module itself. Git HEAD `7b79ea1`. `src/`, `tests/` and `docs/design/` have no diff against HEAD after the run.

Project root used: `{workspace}/examples/streaks`, as the task named. (The session's reported working directory was `examples\split`. It was not used.)

## 1. Unit suite

Command: `node --test --test-reporter=spec "tests/**/*.test.js"`

| Run | tests | pass | fail | cancelled | skipped | exit |
|---|---|---|---|---|---|---|
| 1 | 66 | 66 | 0 | 0 | 0 | 0 |
| 2 (repeat, timing check) | 66 | 66 | 0 | 0 | 0 | 0 |

Per-test spec output: `docs/modules/habit-logic/qa/qa/20261009-140635/unit-run-spec.txt`.

Of the 66 tests, 35 implement a qa.md scenario, matched by the `@R#` tag at the start of the title. The other 31 are extra checks (precondition, reference maths, edge cases). All 66 pass. I read every test file and checked each scenario's Given, When and Then lines and its Examples rows against the assertions. No test is weaker than its scenario's Then lines. The expected values in the tests match the qa.md tables row for row.

## 2. Scenario verdicts

The Test column names the `test()` title that implements the scenario. The Probe column is the independent cross-check, `probe-independent.mjs` (or `probe-locale.mjs` for scenario 7). The probe reads expected values from qa.md, not from the test files. Both agree on every row. Evidence: `docs/modules/habit-logic/qa/qa/20261009-140635/`.

| # | Scenario (qa.md) | R# | Test title that implements it | Probe rows pass/total | Result |
|---|---|---|---|---|---|
| 1 | The local calendar day of an instant (Outline, 6 rows) | R1 | `@R1 the local calendar day of an instant` | 6/6 | PASS |
| 2 | Valid date keys (Outline, 17 rows) | R2 | `@R2 valid and invalid date keys` | 17/17 | PASS |
| 3 | Calendar arithmetic that ignores the time zone (Outline, 11 rows) | R3 | `@R3 calendar arithmetic that ignores the time zone` | 11/11 | PASS |
| 4 | Short weekday, day and month for every weekday (Outline, 9 rows) | R4 | `@R4 short weekday, day and month for every weekday` | 9/9 | PASS |
| 5 | Short and long month names for every month (Outline, 14 rows) | R4 | `@R4 short and long month names for every month` | 14/14 | PASS |
| 6 | The weekday index, Monday first (Outline, 9 rows) | R4 | `@R4 weekdayIndex counts Monday as 0 to Sunday as 6` | 9/9 | PASS |
| 7 | Labels do not follow the runtime locale (1) | R4 | `@R4 labels do not follow the runtime locale` (child process, German default) | 2/2 in `probe-locale.mjs`, control child shows English | PASS |
| 8 | The seven days of the strip (Outline, 3 rows) | R5 | `@R5 the seven days of the strip` | 3/3 | PASS |
| 9 | The sample's strips and streaks on the key screen (Outline, 3 habits) | R5, R6, R7, R8 | `@R5 @R6 @R7 @R8 the sample's strips and streaks on the key screen` | 12/12 | PASS |
| 10 | The same sample one day later (Outline, 3 habits) | R6, R8 | `@R6 @R8 the same sample one day later` | 6/6 | PASS |
| 11 | A streak does not break until today is over (Outline, 8 rows) | R6 | `@R6 a streak does not break until today is over` | 8/8 | PASS |
| 12 | A streak that crosses a DST change (1) | R6 | `@R6 a streak that crosses a DST change` | 1/1 | PASS |
| 13 | The longest run in the whole history (Outline, 7 rows) | R7 | `@R7 the longest run in the whole history` | 7/7 | PASS |
| 14 | Keys that fail isDateKey are ignored (Outline, 4 rows) | R6, R7 | `@R6 @R7 keys that fail isDateKey do not count, so a streak counts only valid days` (rows 1, 3, 4) and `@R7 many spellings of one far-out date that all run into the stuck key cost one pass, not one walk each` (row 2). Both run the walk in a child capped at 5 s. | 6/6 | PASS |
| 15 | Ticking a day inside the window (Outline, 6 rows) | R9 | `@R9 ticking a day inside the window` | 6/6 | PASS |
| 16 | Days outside the window and bad indexes change nothing (Outline, 6 rows) | R9 | `@R9 days outside the window and bad indexes change nothing` | 6/6 | PASS |
| 17 | The 12-week grid around today (Outline, 5 rows) | R10 | `@R10 the 12-week grid around today` | 5/5 | PASS |
| 18 | The sample's heatmap equals the golden (1) | R10, R11 | `@R10 @R11 the sample's heatmap equals the golden` | 5/5 | PASS |
| 19 | Levels from the share of habits done (Outline, 7 rows) | R11 | `@R11 levels from the share of habits done` | 7/7 | PASS |
| 20 | No habits means level 0 (1) | R11 | `@R11 no habits means level 0` | 1/1 | PASS |
| 21 | A fourth habit makes level 3 appear (1) | R10, R11 | `@R10 @R11 a fourth habit makes level 3 appear` | 5/5 | PASS |
| 22 | Month labels over the first column whose Monday is in the month (Outline, 4 rows) | R12 | `@R12 month labels over the first column whose Monday is in the month` | 4/4 | PASS |
| 23 | Name checks in the order empty, too long, duplicate (Outline, 8 rows) | R13 | `@R13 name checks in the order empty, too long, duplicate` | 8/8 | PASS |
| 24 | Too long is checked before duplicate (1) | R13 | `@R13 too long is checked before duplicate` | 1/1 | PASS |
| 25 | Length counts code points, not UTF-16 units (1) | R13 | `@R13 length counts code points, not UTF-16 units` | 2/2 | PASS |
| 26 | The limits are exported (1) | R13, R14 | `@R13 @R14 the limits are exported` | 1/1 | PASS |
| 27 | A new habit goes to the bottom (1) | R14 | `@R14 a new habit goes to the bottom` | 1/1 | PASS |
| 28 | A rejected name returns its error (1) | R14 | `@R14 a rejected name returns its error` | 1/1 | PASS |
| 29 | The limit of 12 habits (Outline, 3 rows) | R14 | `@R14 the limit of 12 habits is checked before the name` | 3/3 | PASS |
| 30 | Deleting a habit (Outline, 4 rows) | R15 | `@R15 deleting a habit` | 4/4 | PASS |
| 31 | No clock, DOM, storage or locale access in the source (1) | R16 | `@R16 the source has no clock or random read, even in a comment`, `@R16 the code has no DOM, storage, network, timer, global or locale access and builds no code from strings`, `@R16 habits.js imports only ./dates.js and dates.js imports nothing` | 2/2 scan rows and 1/1 import row | PASS |
| 32 | No exported function writes to its arguments (1) | R16 | `@R16 no exported function writes to its arguments or returns one of them` | 4/4 | PASS |

Probe totals: 176 rows in `probe-independent.mjs` (summary `scenarios_pass=32 scenarios_fail=0 rows_pass=176 rows_total=176`) and 2 rows in `probe-locale.mjs`, all PASS. Scenario 31 lists the import check as its own probe row, but it is the third Then line of that scenario.

## 3. Untested scenarios

None. Every scenario in qa.md has a test with a matching `@R#` title. The gap probe in step 3 of the brief therefore had nothing to run. I still ran the independent probes on all 32 scenarios as a cross-check, and they agree with the tests.

## 4. Coverage by requirement

| R# | Passing scenarios (table #) | Covered |
|---|---|---|
| R1 | 1 | yes |
| R2 | 2 | yes |
| R3 | 3 | yes |
| R4 | 4, 5, 6, 7 | yes |
| R5 | 8, 9 | yes |
| R6 | 9, 10, 11, 12, 14 | yes |
| R7 | 9, 13, 14 | yes |
| R8 | 9, 10 | yes |
| R9 | 15, 16 | yes |
| R10 | 17, 18, 21 | yes |
| R11 | 18, 19, 20, 21 | yes |
| R12 | 22 | yes |
| R13 | 23, 24, 25, 26 | yes |
| R14 | 26, 27, 28, 29 | yes |
| R15 | 30 | yes |
| R16 | 31, 32 | yes |

No R# lacks a passing scenario.

## 5. Failures and reproduction

None. No FAIL row in the unit suite (run twice) or in either probe.

## 6. Notes on what the green result rests on

- R4 locale (scenario 7): ICU on Windows ignores `LANG` and `LC_ALL`. The test and the probe make German the default inside a child process, by patching `Intl.DateTimeFormat` and the `Date` `toLocale*` methods before importing `src/dates.js`. The probe's control child, with no patch, reports `["Thursday","Thursday"]`, and the patched child reports `["Donnerstag","Donnerstag"]`. So the German precondition is what makes the label check meaningful.
- Keys that fail isDateKey (scenario 14): the 20,000-spelling walk and the 400-key walk each run in a child with a 5 second cap, so a non-terminating walk would fail the test, not hang the suite. The two tests ran in about 120 ms and 104 ms.
- R16 scans (scenario 31): the test and the probe both match on the file text, comments included, and again on the code with comments removed, as qa.md states.
- Timing-based assertions (hostile-string checks under 1000 ms) passed on both runs with wide margins (durations in the spec output).

## PROCESSES

- Started by me: `node --test` (2 foreground runs), `probe-independent.mjs`, and `probe-locale.mjs`, which spawned 2 child node processes (the control and the patched child). Each ran as a foreground command under a `timeout` of 120 s or 90 s. Each returned exit 0 before the next step.
- PIDs: not recorded per process, since every one exited before its command returned.
- Post-run check: `tasklist //FI "IMAGENAME eq node.exe"` reports "No tasks are running", and PowerShell `Get-Process -Name node` counts 0. No process from this run is alive.
- No server, browser or background job was started. Nothing was written to the clipboard.
