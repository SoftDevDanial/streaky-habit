# QA: habit-logic

> Test contract. Every scenario is tagged `@R#` and maps to a requirement in `spec.md`.
> Written by: the solutions architect (sdlc planner), 2026-10-08.
> v1.1.0 delta by the planner (solutions architect role), 2026-10-13. Scenarios marked `(v1.1.0 changed)` replace their 1.0 form (kept in tag `v1.0.0`). Scenarios of retired requirements (R5, R11) are kept as text only under "Feature: Retired in v1.1.0" at the end of the Gherkin, each with a `# Retired in v1.1.0` comment, and their tests are removed. New scenarios carry `(v1.1.0 new)`. Every new or changed R# (R9, R10, R17, R18, R19, R20) has at least one scenario. Changed 2026-10-13 after the plan check (F10). The three retired scenarios first sat inside the live Features "Week strip and streaks" and "Heatmap", and one comment covered both `@R11` scenarios, so a tag count read `No habits means level 0` as live.

## How these scenarios run
- This module has no UI. Its "running app" is the module code itself, exercised by Node's built-in test runner.
- The builder implements every scenario below as a `test()` in `tests/*.test.js`, with a title that starts with the scenario's tag or tags (for example `@R6 Stretch holds at 3 days while today is open`). Scenario Outlines may be one `test()` per Examples row or one `test()` that loops over all rows; either way each row is asserted.
- The QA finder runs, from the project root, in the foreground, capped at 120 seconds:
  `node --test "tests/**/*.test.js"`
  (the CLAUDE.md command. The earlier form `node --test tests/` exits 1 on Node 24.11.1, measured 2026-10-08.)
- The QA finder reports PASS or FAIL per `@R#` from the test titles, and also reads each test against its scenario here. A test whose assertions are weaker than the scenario's `Then` lines (a missing row, a looser comparison) is a FAIL of that scenario, even when it is green.
- The runner starts no server and no browser. It leaves no process behind. If a run is cut off by the 120 second cap, the finder reports which process it killed (PID) in its `PROCESSES` block.
- Test data: `docs/design/sample-history.json`, read-only. Any captured output goes to `docs/modules/habit-logic/qa/unit/<datetimestamp>/`.
- Named data used below:
  - **the sample**: the three habits of `sample-history.json` in file order ("Read 20 pages", "Stretch 10 minutes", "No phone after 11pm"). v1.1.0 changed, read from `tests/fixtures/sample-history-v1.0.0.json`, the 1.0 file byte for byte (spec, Contracts, Tests), because `docs/design/sample-history.json` was replaced at the v1.1.0 finalize.
  - **sample today**: `"2026-10-08"`.
  - **the v1.1.0 sample** (v1.1.0 new). The habits of `docs/design/sample-history.json` (read-only), converted by `sampleHabits` in `tests/fixtures/sample.js` (each `"1"` at position i becomes `addDays(from, i)`). "Its first three habits" are "Read 20 pages", "Stretch 10 minutes" and "No phone after 11pm". **v1.1.0 today** is `"2026-10-10"`.
  - A control is watched failing first (constitution, Gates and evidence). Each new scenario's test is run once against the tree before its task's code lands and recorded RED against the asserted property, never against a missing export alone. The RED capture goes to `docs/modules/habit-logic/qa/red-first/<datetimestamp>/`.
  - **The RED-first method for a new export** (stated here once, `../app/qa.md` points here). A named ES module import of an export that does not exist fails when the module links, before any test body runs, which is exactly the import error the line above forbids. So for each new export (`yearDate`, `monthTitle`, `yearStart`, `doneFlags`, `yearMonths`, and in `app` the `src/ring.js` exports `arcPath` and `legendCounts`) the builder first adds a throwaway stub that returns a value of the right type that is wrong (`""` for a label or a date key, `[]` for a list), runs the new tests once, keeps the RED capture, then replaces the stub with the real function. The stub is never committed. Where a scenario's property is an absence (the `@R20 @R16` purity scenario, and the app's "ring.js is pure"), the stub reads the clock with `new Date()`, so the scan is seen RED on that property. A changed export (`toggleDay`, `heatmapCells`) needs no stub, because its 1.0 form fails the new assertion. Added 2026-10-13 after the plan check (F6), the rule first named no method. The same method covers any test whose subject is a name or a file that its own task creates and that would otherwise fail at import, on a missing fixture or on a missing file, in Python as in JavaScript. The app's cases (task 11's `conftest.py` names, task 12's `src/icon.svg`, task 26's new state scripts) are listed with their stubs in `../app/qa.md`, "Controls are watched failing first". Added 2026-10-13 after the plan re-check (F13), the method first reached ES module exports only.

## Functional test cases (Gherkin)

```gherkin
Feature: Local date keys and English labels

  @R1
  Scenario Outline: The local calendar day of an instant
    Given the process time zone is "<tz>"
    When localDateKey is called with <instant>
    Then the result is "<key>"

    Examples:
      | tz                | instant                                  | key        |
      | Asia/Kuala_Lumpur | new Date(2026, 9, 8, 0, 0, 0, 0)         | 2026-10-08 |
      | Asia/Kuala_Lumpur | new Date(2026, 9, 8, 23, 59, 59, 999)    | 2026-10-08 |
      | Asia/Kuala_Lumpur | new Date(2027, 0, 1)                     | 2027-01-01 |
      | Asia/Kuala_Lumpur | new Date("2026-10-07T16:30:00Z")         | 2026-10-08 |
      | America/New_York  | new Date(2026, 2, 8, 3, 30)              | 2026-03-08 |
      | America/New_York  | new Date(2026, 10, 1, 1, 30)             | 2026-11-01 |

  @R2
  Scenario Outline: Valid date keys
    When isDateKey is called with <value>
    Then the result is <result>

    Examples:
      | value                | result |
      | "2026-10-08"         | true   |
      | "2028-02-29"         | true   |
      | "2000-02-29"         | true   |
      | "2026-12-31"         | true   |
      | "2026-02-29"         | false  |
      | "2100-02-29"         | false  |
      | "2026-13-01"         | false  |
      | "2026-00-10"         | false  |
      | "2026-04-31"         | false  |
      | "2026-1-1"           | false  |
      | "2026-10-08T00:00"   | false  |
      | " 2026-10-08"        | false  |
      | "0000-01-01"         | false  |
      | 20261008             | false  |
      | null                 | false  |
      | undefined            | false  |
      | {}                   | false  |

  @R3
  Scenario Outline: Calendar arithmetic that ignores the time zone
    Given the process time zone is "<tz>"
    When addDays is called with "<key>" and <days>
    Then the result is "<result>"

    Examples:
      | tz                | key        | days | result     |
      | Asia/Kuala_Lumpur | 2026-10-08 | -6   | 2026-10-02 |
      | Asia/Kuala_Lumpur | 2026-12-31 | 1    | 2027-01-01 |
      | Asia/Kuala_Lumpur | 2028-02-28 | 1    | 2028-02-29 |
      | Asia/Kuala_Lumpur | 2026-02-28 | 1    | 2026-03-01 |
      | Asia/Kuala_Lumpur | 2026-07-20 | 83   | 2026-10-11 |
      | Asia/Kuala_Lumpur | 2026-10-05 | -77  | 2026-07-20 |
      | America/New_York  | 2026-03-07 | 1    | 2026-03-08 |
      | America/New_York  | 2026-03-08 | 1    | 2026-03-09 |
      | America/New_York  | 2026-11-01 | 1    | 2026-11-02 |
      | America/New_York  | 2026-11-02 | -1   | 2026-11-01 |
      | America/New_York  | 2026-03-09 | -2   | 2026-03-07 |

  @R4
  Scenario Outline: Short weekday, day and month for every weekday
    When dayParts and shortDate are called with "<key>"
    Then dayParts gives weekday "<weekday>", day <day> and month "<month>"
    And shortDate gives "<short>"

    Examples:
      | key        | weekday | day | month | short      |
      | 2026-10-05 | Mon     | 5   | Oct   | Mon 5 Oct  |
      | 2026-10-06 | Tue     | 6   | Oct   | Tue 6 Oct  |
      | 2026-10-07 | Wed     | 7   | Oct   | Wed 7 Oct  |
      | 2026-10-08 | Thu     | 8   | Oct   | Thu 8 Oct  |
      | 2026-10-09 | Fri     | 9   | Oct   | Fri 9 Oct  |
      | 2026-10-10 | Sat     | 10  | Oct   | Sat 10 Oct |
      | 2026-10-11 | Sun     | 11  | Oct   | Sun 11 Oct |
      | 2026-07-20 | Mon     | 20  | Jul   | Mon 20 Jul |
      | 2026-08-01 | Sat     | 1   | Aug   | Sat 1 Aug  |

  @R4
  Scenario Outline: Short and long month names for every month
    When dayParts and longDate are called with "<key>"
    Then dayParts gives month "<month>"
    And longDate gives "<long>"

    Examples:
      | key        | month | long                 |
      | 2026-01-15 | Jan   | Thursday 15 January  |
      | 2026-02-15 | Feb   | Sunday 15 February   |
      | 2026-03-15 | Mar   | Sunday 15 March      |
      | 2026-04-15 | Apr   | Wednesday 15 April   |
      | 2026-05-15 | May   | Friday 15 May        |
      | 2026-06-15 | Jun   | Monday 15 June       |
      | 2026-07-15 | Jul   | Wednesday 15 July    |
      | 2026-08-15 | Aug   | Saturday 15 August   |
      | 2026-09-15 | Sep   | Tuesday 15 September |
      | 2026-10-15 | Oct   | Thursday 15 October  |
      | 2026-11-15 | Nov   | Sunday 15 November   |
      | 2026-12-15 | Dec   | Tuesday 15 December  |
      | 2026-10-08 | Oct   | Thursday 8 October   |
      | 2027-01-01 | Jan   | Friday 1 January     |

  @R4
  Scenario Outline: The weekday index, Monday first
    # Changed 2026-10-09 (code review WR-04, ORCH): scenario added with the weekdayIndex export.
    When weekdayIndex is called with "<key>"
    Then the result is <index>

    Examples:
      | key        | index |
      | 2026-10-05 | 0     |
      | 2026-10-06 | 1     |
      | 2026-10-07 | 2     |
      | 2026-10-08 | 3     |
      | 2026-10-09 | 4     |
      | 2026-10-10 | 5     |
      | 2026-10-11 | 6     |
      | 2026-07-20 | 0     |
      | 2026-08-01 | 5     |

  @R4
  Scenario: Labels do not follow the runtime locale
    # Changed 2026-10-09 (code review WR-01, ORCH): on Windows, Node's ICU ignores LANG and LC_ALL, so the old Given was set but never took effect and the scenario passed without having run. The old Given read: the process environment has LANG "de_DE.UTF-8" and LC_ALL "de_DE.UTF-8". German is now also made the default of the date locale APIs, and the second line proves it before the labels are read.
    Given a child process with LANG "de_DE.UTF-8" and LC_ALL "de_DE.UTF-8", in which Intl.DateTimeFormat and Date's toLocaleString, toLocaleDateString and toLocaleTimeString use "de-DE" when given no locale, set up before src/dates.js is imported
    And the child's default locale resolves to German: the long weekday of 8 October 2026 from toLocaleDateString and from Intl.DateTimeFormat, each given no locale, is "Donnerstag"
    When longDate is called with "2026-10-08" and shortDate with "2026-10-06"
    Then the results are "Thursday 8 October" and "Tue 6 Oct"

Feature: Week strip and streaks
  # The retired R5 scenario moved to "Feature: Retired in v1.1.0" at the end (2026-10-13, plan check F10).

  # v1.1.0 changed. The strip and run columns are retired with R5 and R8. The 1.0 form (tags @R5 @R6 @R7 @R8, with the
  # strip ". D D D D D D", "D D . D D D .", ". D . . D . D" and run false, true, false) is in tag v1.0.0.
  @R6 @R7
  Scenario Outline: The sample's streaks on the 1.0 key screen (v1.1.0 changed)
    Given the sample and today "2026-10-08"
    When the current streak and best streak of "<habit>" are computed
    Then currentStreak is <current>
    And bestStreak is <best>

    Examples:
      | habit               | current | best |
      | Read 20 pages       | 6       | 14   |
      | Stretch 10 minutes  | 3       | 9    |
      | No phone after 11pm | 1       | 4    |

  # v1.1.0 changed. The run column is retired with R8 (1.0 tags @R6 @R8, runs false, true, false).
  @R6
  Scenario Outline: The same sample one day later (v1.1.0 changed)
    Given the sample and today "2026-10-09"
    Then currentStreak of "<habit>" is <current>

    Examples:
      | habit               | current |
      | Read 20 pages       | 6       |
      | Stretch 10 minutes  | 0       |
      | No phone after 11pm | 1       |

  @R6
  Scenario Outline: A streak does not break until today is over
    Given today is "2026-10-08"
    When currentStreak is called with <done>
    Then the result is <current>

    Examples:
      | done                                   | current |
      | []                                     | 0       |
      | ["2026-10-07"]                         | 1       |
      | ["2026-10-06"]                         | 0       |
      | ["2026-10-09"]                         | 0       |
      | ["2026-10-08", "2026-10-08"]           | 1       |
      | ["2026-09-30", "2026-10-01"]           | 0       |
      | ["2026-10-08", "2026-10-06", "2026-10-07"] | 3   |
      | ["2026-10-07", "2026-10-08", "2026-10-09"] | 2   |

  @R6
  Scenario: A streak that crosses a DST change
    Given the process time zone is "America/New_York"
    And today is "2026-03-09"
    When currentStreak is called with ["2026-03-07", "2026-03-08", "2026-03-09"]
    Then the result is 3

  @R7
  Scenario Outline: The longest run in the whole history
    When bestStreak is called with <done>
    Then the result is <best>

    Examples:
      | done                                         | best |
      | []                                           | 0    |
      | ["2026-12-30", "2026-12-31", "2027-01-01"]   | 3    |
      | ["2028-02-28", "2028-02-29", "2028-03-01"]   | 3    |
      | ["2026-02-28", "2026-03-01"]                 | 2    |
      | ["2026-10-08", "2026-10-08"]                 | 1    |
      | ["2026-10-01", "2026-10-03"]                 | 1    |
      | ["2026-10-09", "2026-10-08", "2026-10-07"]   | 3    |

  @R6 @R7
  Scenario Outline: Keys that fail isDateKey are ignored
    # Changed 2026-10-09 (code review WR-12, ORCH): scenario added for the behaviour that the notes under R6 and R7 state. Rows 1, 3 and 4 are the test "@R6 @R7 keys that fail isDateKey do not count, so a streak counts only valid days". Row 2 is "@R7 many spellings of one far-out date ...". Each call runs in a child process with a 5 second cap, so a walk that never ends fails the test and does not hang the suite.
    Given FAR_START "24660873954866-12-02" and FAR_STUCK "24660873954866-12-04", two keys that fail isDateKey, where the day after FAR_START is FAR_STUCK and the day after FAR_STUCK is FAR_STUCK again
    When <call> is called with <done>
    Then the result is <result> within 5 seconds

    Examples:
      | call          | done                                                                                              | result |
      | bestStreak    | ["2026-10-06", "2026-10-07", "2026-10-08", FAR_START, FAR_STUCK]                                  | 3      |
      | bestStreak    | 20,000 distinct spellings of FAR_START with white space around its parts, and FAR_STUCK            | 0      |
      | currentStreak | 400 keys, "0001-01-10" and the days before it as addDays gives them, 10 of them valid, today "0001-01-10" | 10     |
      | bestStreak    | the same 400 keys                                                                                 | 10     |

  @R9
  Scenario Outline: Ticking a day inside the window
    Given the sample and today "2026-10-08"
    When toggleDay is called with index <index> and date "<date>"
    Then the habit at <index> <change> "<date>" and its done array stays ascending without duplicates
    And currentStreak of that habit for today "2026-10-08" is <current>
    And the other two habits are equal in content to the input
    And the input array and its habits are unchanged

    Examples:
      | index | date       | change               | current |
      | 1     | 2026-10-08 | now contains         | 4       |
      | 0     | 2026-10-08 | no longer contains   | 5       |
      | 2     | 2026-10-07 | now contains         | 3       |
      | 1     | 2026-10-04 | now contains         | 7       |
      | 1     | 2026-10-02 | no longer contains   | 3       |
      | 0     | 2026-10-02 | now contains         | 10      |

  # v1.1.0 changed. The range is yearStart(today) to today (R9). 1.0 rows (0, 2026-10-01) and (2, 2026-07-20) are now
  # inside the range and moved to the scenario below. They are replaced here by a day before the year start and a date
  # that is not a real day.
  @R9
  Scenario Outline: Days outside the year and bad indexes change nothing (v1.1.0 changed)
    Given the sample and today "2026-10-08"
    When toggleDay is called with index <index> and date "<date>"
    Then the result is a new array equal in content to the sample

    Examples:
      | index | date       |
      | 0     | 2025-10-07 |
      | 1     | 2026-10-09 |
      | 2     | 2026-02-30 |
      | 3     | 2026-10-08 |
      | -1    | 2026-10-08 |
      | 0.5   | 2026-10-08 |

  @R9
  Scenario Outline: Any day of the last 12 months can be ticked (v1.1.0 new)
    Given the sample and today "2026-10-08"
    When toggleDay is called with index <index> and date "<date>"
    Then the habit at <index> <change> "<date>", its done array stays ascending without duplicates, and the other habits are equal in content to the input

    Examples:
      | index | date       | change             |
      | 0     | 2026-10-01 | no longer contains |
      | 1     | 2025-10-08 | now contains       |
      | 2     | 2026-01-15 | now contains       |
    # 2025-10-08 is yearStart("2026-10-08"), the first editable day. 2026-01-15 is long before any day in the 1.0 sample,
    # so a day before the habit's history (and before it was added) can be ticked.

  @R9 @R6 @R7
  Scenario Outline: Ticks on the v1.1.0 sample move Current and Best (v1.1.0 new)
    Given the v1.1.0 sample's first three habits and today "2026-10-10"
    When toggleDay is called with index <index> and date "<date>"
    Then the habit at <index> <change> "<date>"
    And currentStreak of that habit for today is <current> and bestStreak is <best>

    Examples:
      | index | date       | change             | current | best |
      | 1     | 2026-10-10 | now contains       | 3       | 5    |
      | 0     | 2026-10-10 | no longer contains | 3       | 9    |
      | 0     | 2026-09-22 | now contains       | 4       | 13   |
      | 2     | 2026-10-09 | now contains       | 8       | 14   |
      | 0     | 2025-10-10 | no longer contains | 4       | 9    |

  @R9
  Scenario Outline: The edges of the v1.1.0 year (v1.1.0 new)
    Given the v1.1.0 sample's first three habits and today "2026-10-10"
    When toggleDay is called with index 0 and date "<date>"
    Then the result is a new array equal in content to the input

    Examples:
      | date       |
      | 2025-10-09 |
      | 2026-10-11 |

Feature: Heatmap

  # v1.1.0 changed. "level null" and "level 0" read "done null" and "done []" (R10 changed, level removed).
  @R10
  Scenario Outline: The 12-week grid around today (v1.1.0 changed)
    Given no habits
    When heatmapCells is called with today "<today>"
    Then there are 84 cells in column-major order with rows Monday (1) to Sunday (7)
    And the first cell is "<first>" at column 1 row 1 and the last cell is "<last>" at column 12 row 7
    And exactly <future> cells are future, all of them after "<today>", each with done null and count null
    And exactly one cell has today true, the one for "<today>"
    And every cell that is not future has done [], count 0 and total 0
    And no cell has a property named level

    Examples:
      | today      | first      | last       | future |
      | 2026-10-08 | 2026-07-20 | 2026-10-11 | 3      |
      | 2026-10-11 | 2026-07-20 | 2026-10-11 | 0      |
      | 2026-10-05 | 2026-07-20 | 2026-10-11 | 6      |
      | 2026-10-12 | 2026-07-27 | 2026-10-18 | 6      |
      | 2027-01-07 | 2026-10-19 | 2027-01-10 | 3      |

  # v1.1.0 changed. The level lines are retired with R11. The 1.0 form (@R10 @R11, "for every one of the 81 keys in
  # heatmapLevels the cell's level equals the file's value", "the levels count 3 at 0, 30 at 1, 28 at 2, 0 at 3 and 20
  # at 4") is in tag v1.0.0. The counts below are the same 81 days counted as 3 at 0, 30 at 1, 28 at 2 and 20 at 3,
  # read from the fixture's own heatmapLevels (level 4 is 3 of 3 for three habits, level 1 is 1 of 3, level 2 is 2 of 3).
  @R10
  Scenario: The 1.0 sample's 12 weeks (v1.1.0 changed)
    Given the sample and today "2026-10-08"
    When heatmapCells is called
    Then the cell for "2026-10-08" is at column 12 row 4 with today true
    And each of the 81 cells up to today has total 3, a done array of three booleans equal to whether each sample habit's done contains the key, and count equal to the number of true values
    And the counts are 3 cells at 0, 30 at 1, 28 at 2 and 20 at 3
    And the cells for "2026-10-09", "2026-10-10" and "2026-10-11" are future

  @R10 @R19
  Scenario: The v1.1.0 sample's band (v1.1.0 new)
    Given the v1.1.0 sample's first three habits and today "2026-10-10"
    When heatmapCells is called
    Then the cells run from "2026-07-20" to "2026-10-11", the cell for "2026-10-10" is at column 12 row 6 with today true and the cell for "2026-10-11" is the only future cell
    And the cell for "2026-09-22" has done [false, false, true] and count 1, the cell for "2026-07-21" has done [true, true, true] and count 3, the cell for "2026-10-10" has done [true, false, false] and count 1
    And of the 83 cells up to today, 2 have count 0, 16 count 1, 47 count 2 and 18 count 3

  # The two retired R11 scenarios moved to "Feature: Retired in v1.1.0" at the end (2026-10-13, plan check F10).

  # v1.1.0 changed. The level values are retired with R11 (1.0 tags @R10 @R11, levels 3, 3, 2, 1, 0).
  @R10
  Scenario: A fourth habit counts in total and done (v1.1.0 changed)
    Given the sample plus a fourth habit "Drink water" with no done days, and today "2026-10-08"
    When heatmapCells is called
    Then "2026-07-20" has count 3, total 4 and a done array of four values ending with false
    And "2026-10-06" has count 3, total 4
    And "2026-10-08" has count 2, total 4
    And "2026-07-21" has count 1, total 4
    And "2026-08-12" has count 0, total 4

  @R12
  Scenario Outline: Month labels over the first column whose Monday is in the month
    When monthLabels is called with "<today>"
    Then the result is <labels>

    Examples:
      | today      | labels                                                                             |
      | 2026-10-08 | [{column:1,month:"Jul"},{column:3,month:"Aug"},{column:8,month:"Sep"},{column:12,month:"Oct"}] |
      | 2026-10-12 | [{column:1,month:"Jul"},{column:2,month:"Aug"},{column:7,month:"Sep"},{column:11,month:"Oct"}] |
      | 2027-01-07 | [{column:1,month:"Oct"},{column:3,month:"Nov"},{column:8,month:"Dec"},{column:12,month:"Jan"}] |
      | 2026-03-31 | [{column:1,month:"Jan"},{column:4,month:"Feb"},{column:8,month:"Mar"}]                         |

Feature: The year (v1.1.0 new)

  @R17
  Scenario Outline: Labels with the year (v1.1.0 new)
    When yearDate and monthTitle are called with "<key>"
    Then yearDate gives "<year date>" and monthTitle gives "<title>"

    Examples:
      | key        | year date        | title          |
      | 2025-10-10 | Fri 10 Oct 2025  | October 2025   |
      | 2026-10-10 | Sat 10 Oct 2026  | October 2026   |
      | 2026-09-22 | Tue 22 Sep 2026  | September 2026 |
      | 2025-12-01 | Mon 1 Dec 2025   | December 2025  |
      | 2028-02-29 | Tue 29 Feb 2028  | February 2028  |

  @R17
  Scenario: The year labels do not follow the runtime locale (v1.1.0 new)
    Given the child process of the @R4 locale scenario, with German proven as the default locale
    When yearDate is called with "2026-10-10" and monthTitle with "2026-10-10"
    Then the results are "Sat 10 Oct 2026" and "October 2026"

  @R18
  Scenario Outline: The same date last year (v1.1.0 new)
    When yearStart is called with "<today>"
    Then the result is "<start>"
    And the range from "<start>" to "<today>", both included, holds <days> days

    Examples:
      | today      | start      | days |
      | 2026-10-10 | 2025-10-10 | 366  |
      | 2026-01-01 | 2025-01-01 | 366  |
      | 2027-03-01 | 2026-03-01 | 366  |
      | 2028-03-01 | 2027-03-01 | 367  |
      | 2028-02-29 | 2027-02-28 | 367  |
    # The last row is CG-13, ruled 2026-10-13 by the owner with this answer (ledger S1 row 4). Changed 2026-10-13
    # after the plan check (F1), this note first called CG-13 pending.

  @R19
  Scenario Outline: Which habits are done on a day (v1.1.0 new)
    Given the v1.1.0 sample's first three habits
    When doneFlags is called with "<key>"
    Then the result is <flags>

    Examples:
      | key        | flags                |
      | 2026-10-10 | [true, false, false] |
      | 2026-09-22 | [false, false, true] |
      | 2026-07-21 | [true, true, true]   |
      | 2026-10-11 | [false, false, false]|

  @R19
  Scenario: No habits gives an empty list, and twelve habits give the golden's count (v1.1.0 new)
    When doneFlags is called with no habits and "2026-10-10"
    Then the result is []
    When doneFlags is called with all twelve habits of the v1.1.0 sample and "2026-10-10"
    Then the result holds 12 booleans, 7 of them true, in the order [true, false, false, true, false, true, true, true, false, true, true, false]

  @R19 @R6 @R7
  Scenario Outline: The goldens' Current and Best come from the v1.1.0 sample (v1.1.0 new)
    Given all twelve habits of the v1.1.0 sample and today "2026-10-10"
    Then currentStreak of "<habit>" is <current> and bestStreak is <best>

    Examples:
      | habit                   | current | best |
      | Read 20 pages           | 4       | 9    |
      | Stretch 10 minutes      | 2       | 5    |
      | No phone after 11pm     | 0       | 14   |
      | Drink 2 litres of water | 1       | 11   |
      | Walk 8,000 steps        | 1       | 11   |
      | Journal one page        | 8       | 11   |
      | Practise guitar         | 1       | 11   |
      | Cook dinner at home     | 5       | 11   |
      | Lights out by midnight  | 2       | 11   |
      | Meditate 5 minutes      | 2       | 11   |
      | Floss                   | 1       | 11   |
      | Learn 10 Malay words    | 1       | 11   |
    # today.md and today-full.md show these numbers. Current 0 shows as "No streak yet" in the app.

  @R20
  Scenario: The year of the goldens (v1.1.0 new)
    When yearMonths is called with "2026-10-10"
    Then it returns 13 months, the first with key "2026-10-01", title "October 2026" and lead 3, the last with key "2025-10-01", title "October 2025" and lead 2
    And the months in between are September 2026 (lead 1), August 2026 (lead 5), July 2026 (lead 2), and so on back to November 2025, each title equal to monthTitle of its key
    And October 2026 has days 1 to 10 open and 11 to 31 closed, and October 2025 has days 1 to 9 empty and 10 to 31 open
    And every day of the other 11 months is open
    And over all 13 months 366 days are open, 21 closed and 9 empty, and the leads add up to 39
    And each day's key is its month's key with the day of the month, and each month holds as many days as the calendar month

  @R20
  Scenario Outline: The year on other days (v1.1.0 new)
    When yearMonths is called with "<today>"
    Then it returns 13 months, the first "<first>", the last "<last>"
    And <open> days are open, <closed> closed and <empty> empty

    Examples:
      | today      | first         | last          | open | closed | empty |
      | 2026-11-01 | November 2026 | November 2025 | 366  | 29     | 0     |
      | 2026-10-31 | October 2026  | October 2025  | 366  | 0      | 30    |
      | 2028-02-29 | February 2028 | February 2027 | 367  | 0      | 27    |
      | 2027-01-01 | January 2027  | January 2026  | 366  | 30     | 0     |

  @R20 @R16
  Scenario: yearMonths reads no clock (v1.1.0 new)
    Given the purity scan of @R16 over src/habits.js with the new exports
    Then it passes, and yearMonths called twice with the same key gives equal results

Feature: Names and the habit list

  @R13
  Scenario Outline: Name checks in the order empty, too long, duplicate
    Given the existing names "Read 20 pages", "Stretch 10 minutes" and "No phone after 11pm"
    When validateName is called with <raw>
    Then the result is <result>

    Examples:
      | raw                                                     | result                                  |
      | ""                                                      | { ok: false, error: "empty" }           |
      | "   "                                                   | { ok: false, error: "empty" }           |
      | "Walk to the end of the street and back after dinner"   | { ok: false, error: "too-long" }        |
      | "Read twenty pages before bed every night"              | { ok: true, name: "Read twenty pages before bed every night" } |
      | "Read twenty pages before bed every night."             | { ok: false, error: "too-long" }        |
      | "  Drink water  "                                       | { ok: true, name: "Drink water" }       |
      | "read 20 pages"                                         | { ok: false, error: "duplicate" }       |
      | " STRETCH 10 MINUTES "                                  | { ok: false, error: "duplicate" }       |

  @R13
  Scenario: Too long is checked before duplicate
    Given the existing name "Read twenty pages before bed every night."
    When validateName is called with "Read twenty pages before bed every night."
    Then the result is { ok: false, error: "too-long" }

  @R13
  Scenario: Length counts code points, not UTF-16 units
    Given no existing names
    When validateName is called with a string of 40 "📚" characters (80 UTF-16 units)
    Then the result is ok with that string as the name
    And with 41 of them the result is { ok: false, error: "too-long" }

  @R13
  Scenario: The limits are exported
    Then MAX_NAME_LENGTH is 40 and MAX_HABITS is 12

  @R14
  Scenario: A new habit goes to the bottom
    Given the sample
    When addHabit is called with "  Drink water  "
    Then the result is ok with 4 habits named "Read 20 pages", "Stretch 10 minutes", "No phone after 11pm", "Drink water"
    And the fourth habit is { name: "Drink water", done: [] }
    And the first three are equal in content to the sample, and the sample array is unchanged

  @R14
  Scenario: A rejected name returns its error
    Given the sample
    When addHabit is called with "read 20 pages"
    Then the result is { ok: false, error: "duplicate" }

  @R14
  Scenario Outline: The limit of 12 habits
    Given <count> habits named "Habit 1" to "Habit <count>" with no done days
    When addHabit is called with "<raw>"
    Then the result is <result>

    Examples:
      | count | raw      | result                                    |
      | 11    | Habit 12 | ok with 12 habits, "Habit 12" last        |
      | 12    | Habit 13 | { ok: false, error: "limit" }             |
      | 12    |          | { ok: false, error: "limit" }             |

  @R15
  Scenario Outline: Deleting a habit
    Given the sample
    When deleteHabit is called with index <index>
    Then the result holds <names> in that order with their done arrays unchanged
    And the sample array is unchanged

    Examples:
      | index | names                                         |
      | 0     | "Stretch 10 minutes", "No phone after 11pm"   |
      | 2     | "Read 20 pages", "Stretch 10 minutes"         |
      | 3     | all three sample habits                       |
      | -1    | all three sample habits                       |

Feature: Purity

  @R16
  Scenario: No clock, DOM, storage or locale access in the source
    # Changed 2026-10-08 (plan-check flag, ORCH): the word scan first ran over the whole file text, comments included, so a function comment such as "the week window" or "outside the window" failed it. The old Then line read: neither contains "Date.now(", a match of /new\s+Date\s*\(\s*\)/, or any of "document", "window", "localStorage", "globalThis", "Intl", "toLocale". The word scan now runs on code only.
    # Changed 2026-10-09 (security SEC-03, ORCH): the test checks more than the Then lines below, which still hold. Its clock check is the table CLOCK_AND_RANDOM_READS (Date.now with or without a call, new Date with no argument with or without parentheses, Date called as a function, performance.now, Math.random), matched on the file text as it is and again with comments removed. Its word check is the table BANNED_IN_CODE (DOM and global objects, storage, network, dynamic import(, timers, crypto, Intl and toLocale*), matched on code only, as whole words. The full lists are in spec.md R16, dated 2026-10-09. new Date with an argument and Date.UTC stay allowed.
    # Changed 2026-10-09 (security re-check SEC-04, ORCH): the two lists in the line above are incomplete. CLOCK_AND_RANDOM_READS also holds Temporal.Now, and Temporal.PlainDate arithmetic stays allowed. BANNED_IN_CODE also bans code built from a string (eval, Function( and new Function(). See spec.md R16.
    Given the text of src/dates.js and src/habits.js
    Then neither contains "Date.now(" or a match of /new\s+Date\s*\(\s*\)/, checked on the file text as it is, comments included
    And, with every /* ... */ block and every // comment up to the end of its line removed first, neither contains a match of /\b(document|window|localStorage|globalThis|Intl)\b/ or of /\btoLocale\w*/
    And the only import in src/habits.js is from "./dates.js" and src/dates.js has no import
    # Changed 2026-10-09 (code review WR-11, ORCH): the comment strip is one pass that reads string literals and comments in source order. A // or /* inside a string is not a comment, and a quote inside a comment does not open a string. The strip it replaces was two plain regular expressions that knew nothing about strings: a // inside a string removed the rest of its line, and a /* inside a string or inside a // comment opened a block that ran to the next */, so the code after it vanished from the word scan and from the import count. The old note read: "The comment strip is two plain regular expressions. These two files hold only English label tables and date logic, with no string or regular expression literal that contains // or /*. A test author who meets one tokenises the source instead of guessing." One limit remains: a quote inside a regular expression literal is read as the start of a string.

  @R16
  Scenario: No exported function writes to its arguments
    # Changed 2026-10-09 (code review WR-02, ORCH): a freeze does not protect a Date's internal time value, so a write to the Date of localDateKey went unnoticed. The added last line checks that Date by value. The other lines are unchanged.
    Given the sample deep-frozen (every array and object frozen) and today "2026-10-08"
    When every exported function of src/dates.js and src/habits.js is called with frozen arguments
    Then no call throws
    And the frozen sample still equals the file's habits
    And the Date passed to localDateKey has the same getTime() after the call as before it

Feature: Retired in v1.1.0
  # Text only. No test implements a scenario of this Feature, and a tag count reads none of them as live.
  # Moved here 2026-10-13 after the plan check (F10) from "Week strip and streaks" (R5) and "Heatmap" (R11).

  # Retired in v1.1.0 (R5 retired, replaced by R18). Text kept, test removed.
  @R5
  Scenario Outline: The seven days of the strip
    When weekWindow is called with "<today>"
    Then the result is <days>

    Examples:
      | today      | days                                                                                              |
      | 2026-10-08 | ["2026-10-02","2026-10-03","2026-10-04","2026-10-05","2026-10-06","2026-10-07","2026-10-08"]      |
      | 2027-01-03 | ["2026-12-28","2026-12-29","2026-12-30","2026-12-31","2027-01-01","2027-01-02","2027-01-03"]      |
      | 2028-03-02 | ["2028-02-25","2028-02-26","2028-02-27","2028-02-28","2028-02-29","2028-03-01","2028-03-02"]      |

  # Retired in v1.1.0 (R11 retired, replaced by R19). Text kept, test removed.
  @R11
  Scenario Outline: Levels from the share of habits done
    When heatLevel is called with count 0 up to <total> and total <total>
    Then the levels are <levels>

    Examples:
      | total | levels                     |
      | 1     | 0 4                        |
      | 2     | 0 2 4                      |
      | 3     | 0 1 2 4                    |
      | 4     | 0 1 2 3 4                  |
      | 5     | 0 1 2 2 3 4                |
      | 6     | 0 1 1 2 2 3 4              |
      | 12    | 0 1 1 1 1 2 2 2 2 3 3 3 4  |

  # Retired in v1.1.0 (R11 retired, replaced by R19). Text kept, test removed.
  @R11
  Scenario: No habits means level 0
    When heatLevel is called with count 0 and total 0
    Then the level is 0
```

## FE element checklist
Not applicable. `habit-logic` renders nothing. Every value it computes reaches the screen through `app`, whose FE element checklist and fidelity gate cover it (`../app/qa.md`).

## Fidelity gate
Not applicable (no UI).

## Regression
- Re-run `node --test "tests/**/*.test.js"` in the final parallel all-modules pass.
