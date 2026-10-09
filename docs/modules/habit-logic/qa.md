# QA: habit-logic

> Test contract. Every scenario is tagged `@R#` and maps to a requirement in `spec.md`.
> Written by: the solutions architect (sdlc planner), 2026-10-08.

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
  - **the sample**: the three habits of `sample-history.json` in file order ("Read 20 pages", "Stretch 10 minutes", "No phone after 11pm").
  - **sample today**: `"2026-10-08"`.

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

  @R5
  Scenario Outline: The seven days of the strip
    When weekWindow is called with "<today>"
    Then the result is <days>

    Examples:
      | today      | days                                                                                              |
      | 2026-10-08 | ["2026-10-02","2026-10-03","2026-10-04","2026-10-05","2026-10-06","2026-10-07","2026-10-08"]      |
      | 2027-01-03 | ["2026-12-28","2026-12-29","2026-12-30","2026-12-31","2027-01-01","2027-01-02","2027-01-03"]      |
      | 2028-03-02 | ["2028-02-25","2028-02-26","2028-02-27","2028-02-28","2028-02-29","2028-03-01","2028-03-02"]      |

  @R5 @R6 @R7 @R8
  Scenario Outline: The sample's strips and streaks on the key screen
    Given the sample and today "2026-10-08"
    When the strip, current streak, best streak and run flag of "<habit>" are computed
    Then the strip from Fri 2 to Thu 8 reads "<strip>" (D done, . not done)
    And currentStreak is <current>
    And bestStreak is <best>
    And runContinues is <run>

    Examples:
      | habit               | strip         | current | best | run   |
      | Read 20 pages       | . D D D D D D | 6       | 14   | false |
      | Stretch 10 minutes  | D D . D D D . | 3       | 9    | true  |
      | No phone after 11pm | . D . . D . D | 1       | 4    | false |

  @R6 @R8
  Scenario Outline: The same sample one day later
    Given the sample and today "2026-10-09"
    Then currentStreak of "<habit>" is <current>
    And runContinues of "<habit>" is <run>

    Examples:
      | habit               | current | run   |
      | Read 20 pages       | 6       | false |
      | Stretch 10 minutes  | 0       | true  |
      | No phone after 11pm | 1       | false |

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

  @R9
  Scenario Outline: Days outside the window and bad indexes change nothing
    Given the sample and today "2026-10-08"
    When toggleDay is called with index <index> and date "<date>"
    Then the result is a new array equal in content to the sample

    Examples:
      | index | date       |
      | 0     | 2026-10-01 |
      | 1     | 2026-10-09 |
      | 2     | 2026-07-20 |
      | 3     | 2026-10-08 |
      | -1    | 2026-10-08 |
      | 0.5   | 2026-10-08 |

Feature: Heatmap

  @R10
  Scenario Outline: The 12-week grid around today
    Given no habits
    When heatmapCells is called with today "<today>"
    Then there are 84 cells in column-major order with rows Monday (1) to Sunday (7)
    And the first cell is "<first>" at column 1 row 1 and the last cell is "<last>" at column 12 row 7
    And exactly <future> cells are future, all of them after "<today>", each with count null and level null
    And exactly one cell has today true, the one for "<today>"
    And every cell that is not future has count 0, total 0 and level 0

    Examples:
      | today      | first      | last       | future |
      | 2026-10-08 | 2026-07-20 | 2026-10-11 | 3      |
      | 2026-10-11 | 2026-07-20 | 2026-10-11 | 0      |
      | 2026-10-05 | 2026-07-20 | 2026-10-11 | 6      |
      | 2026-10-12 | 2026-07-27 | 2026-10-18 | 6      |
      | 2027-01-07 | 2026-10-19 | 2027-01-10 | 3      |

  @R10 @R11
  Scenario: The sample's heatmap equals the golden
    Given the sample and today "2026-10-08"
    When heatmapCells is called
    Then the cell for "2026-10-08" is at column 12 row 4 with today true
    And for every one of the 81 keys in heatmapLevels the cell's level equals the file's value
    And each of those cells has total 3 and count equal to the number of sample habits whose done contains the key
    And the levels count 3 at 0, 30 at 1, 28 at 2, 0 at 3 and 20 at 4
    And the cells for "2026-10-09", "2026-10-10" and "2026-10-11" are future

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

  @R11
  Scenario: No habits means level 0
    When heatLevel is called with count 0 and total 0
    Then the level is 0

  @R10 @R11
  Scenario: A fourth habit makes level 3 appear
    Given the sample plus a fourth habit "Drink water" with no done days, and today "2026-10-08"
    When heatmapCells is called
    Then "2026-07-20" has count 3, total 4, level 3
    And "2026-10-06" has count 3, total 4, level 3
    And "2026-10-08" has count 2, total 4, level 2
    And "2026-07-21" has count 1, total 4, level 1
    And "2026-08-12" has count 0, total 4, level 0

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
    Given the text of src/dates.js and src/habits.js
    Then neither contains "Date.now(" or a match of /new\s+Date\s*\(\s*\)/, checked on the file text as it is, comments included
    And, with every /* ... */ block and every // comment up to the end of its line removed first, neither contains a match of /\b(document|window|localStorage|globalThis|Intl)\b/ or of /\btoLocale\w*/
    And the only import in src/habits.js is from "./dates.js" and src/dates.js has no import
    # The comment strip is two plain regular expressions. These two files hold only English label tables and date logic, with no string or regular expression literal that contains // or /*. A test author who meets one tokenises the source instead of guessing.

  @R16
  Scenario: No exported function writes to its arguments
    # Changed 2026-10-09 (code review WR-02, ORCH): a freeze does not protect a Date's internal time value, so a write to the Date of localDateKey went unnoticed. The added last line checks that Date by value. The other lines are unchanged.
    Given the sample deep-frozen (every array and object frozen) and today "2026-10-08"
    When every exported function of src/dates.js and src/habits.js is called with frozen arguments
    Then no call throws
    And the frozen sample still equals the file's habits
    And the Date passed to localDateKey has the same getTime() after the call as before it
```

## FE element checklist
Not applicable. `habit-logic` renders nothing. Every value it computes reaches the screen through `app`, whose FE element checklist and fidelity gate cover it (`../app/qa.md`).

## Fidelity gate
Not applicable (no UI).

## Regression
- Re-run `node --test "tests/**/*.test.js"` in the final parallel all-modules pass.
