# Module: habit-logic

> Build contract. Read by the Senior Dev agent. Build ONLY what is here.
> Stack: LOCKED to project stack (vanilla JavaScript ES modules, zero dependencies, Node 24 built-in test runner). Depends on: none.
> Nature: logic only. No UI, no DOM, no storage, no clock. Consumed by `app` through the Contracts below and nothing else.
> Written by: the solutions architect (sdlc planner), 2026-10-08. Clarify-gate item that touches this module: CG-8, ruled 2026-10-08, ORCH: accepted as recommended, length counts Unicode code points (see `../ROADMAP.md`). CG-1 (the unit-test command) was resolved on 2026-10-08 when CLAUDE.md adopted `node --test "tests/**/*.test.js"`.
> v1.1.0 delta written by the planner (solutions architect role), 2026-10-13. 1.0's text stays in git tag `v1.0.0`. The one clarify item that touches this module is CG-13 (the same date last year on 29 February). The owner ruled it on 2026-10-13 with the recommended answer (ledger S1 row 4, `../ROADMAP.md`). Changed 2026-10-13 after the plan check (F1), this line first named CG-13 as open.
> Changed 2026-10-15 in the v1.1.0 regression (planner, solutions architect role, ledger H-06, owner ruling USER 2026-10-15 21:03 "1", option 1). R20 gains the bound on `yearMonths`, the Contracts row and the Threat model say so, and a new task 9a builds it, placed after task 9 with no task renumbered. This is a contract. Nothing is built yet, and no source or test has changed. Each change carries its own dated note.

## v1.1.0 delta
| R# | Status | Ledger scope | What changes |
|---|---|---|---|
| R5 | Retired in v1.1.0, replaced by R18 | S1, S7 | The 7-day strip is gone (brainstorm Round 1 rulings), so the week window has no user. The editable reach is the year of R18 |
| R8 | Retired in v1.1.0, replaced by app R34 | S7 | The run flag drew the strip's thread. The year view strings its beads by its own rule (app R34) |
| R9 | Changed | S1 | `toggleDay` accepts any day from `yearStart(today)` to today, not only the last 7 |
| R10 | Changed | S7 | A cell carries each habit's done flag (R19) for the rings. `level` is gone |
| R11 | Retired in v1.1.0, replaced by R19 | S7 | The overview draws one ring segment per habit (system.md, Ring), so no level is drawn |
| R17 | New | S1, S7 | `yearDate` and `monthTitle`, the labels of the year views |
| R18 | New | S1 | `yearStart`, the same date last year |
| R19 | New | S1, S7 | `doneFlags`, which habits are done on a day |
| R20 | New | S1, S7 | `yearMonths`, the 12-month calendar of both year views. Changed 2026-10-15 (ledger H-06), the call also always ends and returns at most 13 months, see R20, the bound |
| (test data) | Changed | S7 | `docs/design/sample-history.json` was replaced at the v1.1.0 finalize (366-character done strings, no `heatmapLevels`). The 1.0 worked examples move to a test fixture, see Contracts, Tests |

## Sources
| Source | What it fixes here |
|---|---|
| `docs/brainstorm/brainstorm.md`, "Rules the build must follow" | local days, week strip, current streak, best streak, heatmap levels, habit name, 12 habits, order |
| `docs/design/system.md`, "The bead and the thread", "Heatmap", "Accessible names" | run carried in (`data-run-continues`), heatmap grid and month axis, date label formats |
| `docs/design/today.md` | the sample values on the key screen |
| `docs/design/sample-history.json` | verified test data (read-only) |
| `docs/design/RULINGS.md`, rule 3 | trim, then check empty, too long, duplicate, in that order |
| v1.1.0. `docs/brainstorm/brainstorm.md`, "v1.1.0 delta" with the Round 1 and Round 2 rulings | the reach (today back to the same date last year), days after today closed, a day before a habit was added can be ticked, the strip gone |
| v1.1.0. `docs/design/system.md` (Ring, Bead, Accessible names), `year-view.md`, `overview-year.md`, `today.md` | one ring segment per habit, the 366-day year newest month first, the labels with a year, the band's 12 weeks |
| v1.1.0. `docs/design/sample-history.json` (today 2026-10-10) | the v1.1.0 test data. The 1.0 file is kept as a test fixture (Contracts, Tests) |

Note (v1.1.0). The 1.0 rows above name `system.md` sections and `today.md` values of the 1.0 goldens, which stay in tag `v1.0.0`.

Phase skills: the registry assigns none to plan, and this module has no UI work, so the design row does not apply to its builder.

## Invariants & assumptions
- A day is a date key, a string `YYYY-MM-DD` naming a local calendar day (brainstorm: "Days are local calendar days"). No `Date` object crosses the module boundary except the one argument of `localDateKey`.
- The current day is always passed in as `todayKey`. No function in this module reads the clock.
- Habit data passed to these functions is already valid: names trimmed, 1 to 40 code points, unique ignoring case, `done` arrays of valid date keys. Data enters the app only through `addHabit` and the app's storage decoder (which uses `validateName` and `isDateKey` from here). Changed 2026-10-15 in the v1.1.0 regression (consistency sweep CS-05). `done` ascending without duplicates (the `Habit` type) is enforced in two places with one expression, `toggledHabit` in `src/habits.js` and `readHabit` in `src/storage.js` (the app's decoder). It is a known pair, kept on purpose. Both change for one reason, the `Habit` type, so a change to the type changes both. A shared helper would be a new export for one line, and decoding belongs to the app (Non-goals).
- Functions never mutate their arguments. Every array or object returned is new.
- Weeks start on Monday (brainstorm, Heatmap).
- English only. Weekday and month names come from fixed tables in this module.
- The Gregorian calendar applies to every year.
- Date-key arithmetic is calendar arithmetic (for example through `Date.UTC` and the `getUTC*` getters, or plain integer day counts). It never adds multiples of 86,400,000 ms to a local time, so a 23 or 25 hour day (a DST change) cannot skip or repeat a day.

## Requirements

### Dates

- **R1.** `localDateKey(date)` returns the local calendar day of the given instant as `YYYY-MM-DD`, built from `getFullYear()`, `getMonth() + 1` and `getDate()` (local, never the UTC getters), year as 4 digits, month and day zero-padded to 2 digits.
  Examples: `new Date(2026, 9, 8, 0, 0, 0, 0)` gives `"2026-10-08"`. `new Date(2026, 9, 8, 23, 59, 59, 999)` gives `"2026-10-08"`. `new Date(2027, 0, 1)` gives `"2027-01-01"`. With the process time zone `Asia/Kuala_Lumpur` (UTC+8), `new Date("2026-10-07T16:30:00Z")` gives `"2026-10-08"` although the UTC date is 7 October.

- **R2.** `isDateKey(value)` returns `true` only when `value` is a string matching `^\d{4}-\d{2}-\d{2}$` whose year is 0001 or later, whose month is 01 to 12 and whose day is 01 to the last day of that month. February has 29 days when the year is divisible by 4 and not by 100, or divisible by 400. Every other value returns `false`.
  True: `"2026-10-08"`, `"2028-02-29"`, `"2000-02-29"`, `"2026-12-31"`. False: `"2026-02-29"`, `"2100-02-29"`, `"2026-13-01"`, `"2026-00-10"`, `"2026-04-31"`, `"2026-1-1"`, `"2026-10-08T00:00"`, `" 2026-10-08"`, `"0000-01-01"`, the number `20261008`, `null`, `undefined`, `{}`.

- **R3.** `addDays(key, days)` returns the date key `days` calendar days after `key` (a negative number goes back). The result does not depend on the process time zone.
  Examples: `("2026-10-08", -6)` gives `"2026-10-02"`. `("2026-12-31", 1)` gives `"2027-01-01"`. `("2028-02-28", 1)` gives `"2028-02-29"`. `("2026-02-28", 1)` gives `"2026-03-01"`. `("2026-07-20", 83)` gives `"2026-10-11"`. `("2026-10-05", -77)` gives `"2026-07-20"`. With the process time zone `America/New_York` (DST starts 2026-03-08, ends 2026-11-01): `("2026-03-07", 1)` gives `"2026-03-08"`, `("2026-03-08", 1)` gives `"2026-03-09"`, `("2026-11-01", 1)` gives `"2026-11-02"`, `("2026-11-02", -1)` gives `"2026-11-01"`.

- **R4.** English date labels from fixed tables, the same under every runtime locale (no `Intl`, no `toLocale*`):
  - `dayParts(key)` returns `{ weekday, day, month }`. `weekday` is one of `Mon Tue Wed Thu Fri Sat Sun`. `day` is the day of the month as a number. `month` is one of `Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec`.
  - `shortDate(key)` returns `"<weekday> <day> <month>"` with no zero padding, for example `"Tue 6 Oct"`, `"Mon 20 Jul"`, `"Sat 1 Aug"`.
  - `longDate(key)` returns `"<weekday> <day> <month>"` with the full names `Monday` to `Sunday` and `January` to `December`, for example `"2026-10-08"` gives `"Thursday 8 October"` and `"2027-01-01"` gives `"Friday 1 January"`.
  The week 2026-10-05 (Monday) to 2026-10-11 (Sunday) covers every weekday name. The 15th of each month of 2026 covers every month name.
  Changed 2026-10-09 (code review WR-04, ORCH): `weekdayIndex(key)` is added. It returns the day's place in a Monday-first week, 0 for Monday to 6 for Sunday, from the same calendar count as the weekday names. The heatmap (R10, R12) finds each column's Monday through it, instead of matching the label "Mon" inside the 7-day strip, so the strip's width and a display label no longer decide the heatmap's weeks. Examples: `"2026-10-05"` gives 0, `"2026-10-08"` gives 3, `"2026-10-11"` gives 6, `"2026-07-20"` gives 0, `"2026-08-01"` gives 5. R4 first covered the three label functions only.

### Week strip and streaks

- **R5.** Retired in v1.1.0, replaced by R18. The export `weekWindow` and its tests are removed. (1.0 text) `weekWindow(todayKey)` returns 7 date keys, from `todayKey` minus 6 days to `todayKey`, oldest first (brainstorm: "7 cells, oldest on the left, today on the right").
  Examples: `"2026-10-08"` gives `["2026-10-02", "2026-10-03", "2026-10-04", "2026-10-05", "2026-10-06", "2026-10-07", "2026-10-08"]`. `"2027-01-03"` gives `["2026-12-28", "2026-12-29", "2026-12-30", "2026-12-31", "2027-01-01", "2027-01-02", "2027-01-03"]`.

- **R6.** `currentStreak(done, todayKey)` (brainstorm C3, "counted so it does not break until today is over"). If `todayKey` is in `done`, count consecutive done days going back from `todayKey`. Otherwise count consecutive done days going back from the day before `todayKey`. Return that count, which is 0 when the starting day is not done. Order and duplicates in `done` do not change the result. Days after `todayKey` never count.
  Worked examples from `sample-history.json`, today `2026-10-08` (noted v1.1.0, the 1.0 sample, now the fixture `tests/fixtures/sample-history-v1.0.0.json`, see Contracts, Tests. The v1.1.0 sample's values are in R19's examples).
  - "Read 20 pages" gives 6: 8, 7, 6, 5, 4 and 3 Oct are done, 2 Oct is not.
  - "Stretch 10 minutes" gives 3: today is not done, so counting starts at 7 Oct. 7, 6 and 5 Oct are done, 4 Oct is not.
  - "No phone after 11pm" gives 1: 8 Oct is done, 7 Oct is not.
  Same data, today `2026-10-09`: Read gives 6 (it still holds), Stretch gives 0, No phone gives 1.
  Small cases, today `2026-10-08`: `[]` gives 0. `["2026-10-07"]` gives 1. `["2026-10-06"]` gives 0. `["2026-10-09"]` gives 0. `["2026-10-08", "2026-10-08"]` gives 1. `["2026-09-30", "2026-10-01"]` gives 0.
  Changed 2026-10-09 (security re-check SEC-01 and code review WR-12, ORCH): `currentStreak` counts only keys that pass `isDateKey` (`streakDays`). A key that fails it is outside the Invariants and is ignored, wherever it sits in `done`: it neither starts nor extends a run. Example: today `"0001-01-10"` and 400 keys counting back from it, of which the first 10 are valid days and the rest fail `isDateKey`, give 10. R6 first said nothing about such keys.

- **R7.** `bestStreak(done)` (brainstorm C4) returns the length of the longest run of consecutive calendar days in `done`, over every entry, including entries older than the strip or the heatmap and entries after today. It returns 0 when `done` is empty. Duplicates do not lengthen a run.
  Worked examples: sample "Read 20 pages" gives 14 (2026-09-07 to 2026-09-20). "Stretch 10 minutes" gives 9 (2026-08-18 to 2026-08-26). "No phone after 11pm" gives 4 (2026-08-22 to 2026-08-25). `["2026-12-30", "2026-12-31", "2027-01-01"]` gives 3. `["2028-02-28", "2028-02-29", "2028-03-01"]` gives 3. `["2026-02-28", "2026-03-01"]` gives 2. `["2026-10-08", "2026-10-08"]` gives 1. `["2026-10-01", "2026-10-03"]` gives 1. `[]` gives 0.
  Changed 2026-10-09 (security re-check SEC-01 and code review WR-12, ORCH): "over every entry" means every entry that passes `isDateKey`. `bestStreak` ignores a key that fails it (`streakDays`), so such a key neither starts nor extends a run. Examples: `["2026-10-06", "2026-10-07", "2026-10-08", "24660873954866-12-02", "24660873954866-12-04"]` gives 3, and a `done` that holds only keys failing `isDateKey` gives 0. R7 first said "over every entry" and nothing about such keys.

- **R8.** Retired in v1.1.0, replaced by app R34. The export `runContinues` and its tests are removed. (1.0 text) `runContinues(done, todayKey)` returns `true` exactly when both the first day of the week window (`todayKey` minus 6) and the day before it (`todayKey` minus 7) are in `done` (system.md, "Run carried in"). The app writes it as the `data-run-continues` attribute.
  Worked examples, today 2026-10-08: Stretch gives true (1 and 2 Oct are done). Read gives false (2 Oct is not done, although 1 Oct is). No phone gives false. Today 2026-10-09: Read false, Stretch true (2 and 3 Oct done), No phone false.

- **R9.** (v1.1.0 changed, S1) `toggleDay(habits, index, dateKey, todayKey)` returns a new habits array in which the habit at `index` has `dateKey` added to its `done` when absent, or removed when present, with `done` kept in ascending order without duplicates. Only the days from `yearStart(todayKey)` (R18) to `todayKey`, both included, can change (brainstorm v1.1.0, Round 1 rulings, "any day in the last 12 months, today included (today back to the same date last year). Days after today stay closed"). A day before the habit's first done day, or before the habit was added, can change like any other, since no start date is stored (brainstorm v1.1.0, Rules). When `dateKey` is outside that range, is not a valid date key (R2), or `index` is not an integer index of `habits`, the function returns a new array equal in content to `habits`. The other habits keep their content and order.
  Examples with the 1.0 sample fixture and today 2026-10-08. Toggling 2026-10-08 on Stretch (index 1) adds it, and Stretch's current streak becomes 4. Toggling 2026-10-08 on Read (index 0) removes it, and Read's current streak becomes 5. Toggling 2026-10-09 on any habit changes nothing (after today). Index 3 or -1 changes nothing. Toggling 2026-10-01 on Read now removes it (1.0 refused it), and toggling 2025-10-08 (the year start) on Stretch adds it, while 2025-10-07 changes nothing.
  Changed 2026-10-13 after the plan check (F2). The 2026-10-01 example first said the toggle adds the day. Read already holds 2026-10-01 in the 1.0 fixture, so the toggle removes it, as the qa row (index 0, 2026-10-01, "no longer contains") says.
  Examples with the v1.1.0 sample and today 2026-10-10. Toggling 2026-09-22 on Read adds it and Read's best streak becomes 13 (current stays 4). Toggling 2026-10-09 on "No phone after 11pm" adds it and its current streak becomes 8 (best stays 14). Toggling 2025-10-10 (the year start) on Read removes it. Toggling 2025-10-09 or 2026-10-11 changes nothing.
  (1.0 text) Only the 7 days of `weekWindow(todayKey)` can change (brainstorm: "Only these 7 days can be changed"). When `dateKey` is outside the window, or `index` is not an integer index of `habits`, the function returns a new array equal in content to `habits`.

### Heatmap

- **R10.** (v1.1.0 changed, S7) `heatmapCells(habits, todayKey)` returns 84 cells covering 12 weeks (brainstorm C5, and v1.1.0 C5 "The overview stays the last 12 weeks"). Column 12 is the Monday to Sunday week that contains `todayKey`. Column 1 starts on the Monday 11 weeks before that week's Monday. Cells come in column-major order (column 1 from Monday to Sunday, then column 2, and so on). Row 1 is Monday, row 7 is Sunday. For each cell:
  - `future` is true when the key is after `todayKey`. A future cell has `done` and `count` set to `null`.
  - `today` is true only for `todayKey`.
  - `total` is `habits.length`.
  - `done` is `doneFlags(habits, key)` (R19), one boolean per habit in list order.
  - `count` is the number of `true` values in `done`.
  The cell has no `level` (R11 retired). v1.1.0 example with the v1.1.0 sample and today 2026-10-10. Cells 2026-07-20 to 2026-10-11, 83 not future and 1 future (2026-10-11). 2026-09-22 has `done` [false, false, true] and `count` 1. 2026-10-10 has `today` true, `done` [true, false, false], `count` 1. Of the 83 days, 2 have count 0, 16 count 1, 47 count 2 and 18 count 3.
  (1.0 text) a future cell has `count` and `level` set to `null`, and `level` is `heatLevel(count, total)`. 1.0 worked examples below still hold for the grid, the future cells and `count`. Read "level 0" in the last one as "count 0".
  Worked examples: today 2026-10-08 (a Thursday) gives a first cell 2026-07-20 (column 1, row 1), a last cell 2026-10-11 (column 12, row 7), today at column 12 row 4, 81 cells up to today and 3 future cells (2026-10-09 to 2026-10-11). Today 2026-10-11 (Sunday) gives the same range with 0 future cells. Today 2026-10-05 (Monday) gives the same range with 6 future cells. Today 2026-10-12 (Monday) gives 2026-07-27 to 2026-10-18 with 6 future cells. Today 2027-01-07 gives 2026-10-19 to 2027-01-10. With no habits every cell up to today has `count` 0, `total` 0 and `level` 0.

- **R11.** Retired in v1.1.0, replaced by R19. The export `heatLevel` and its tests are removed (v1.1.0 C5, the overview's rings draw one segment per habit, so no level is drawn and the function would be dead code). (1.0 text) `heatLevel(count, total)` (brainstorm: "the share of the current habits done that day") uses integer arithmetic only. It returns 0 when `count` is 0 or `total` is 0, 4 when `count` equals `total`, else 1 when `3 * count <= total` (up to a third, inclusive), else 2 when `3 * count <= 2 * total` (up to two thirds, inclusive), else 3 (more than two thirds, not all). The goldens confirm both boundaries are inclusive: 1 of 3 is level 1 and 2 of 3 is level 2.
  Levels for count = 0 up to total:

  | total | levels |
  |---|---|
  | 1 | 0 4 |
  | 2 | 0 2 4 |
  | 3 | 0 1 2 4 |
  | 4 | 0 1 2 3 4 |
  | 5 | 0 1 2 2 3 4 |
  | 6 | 0 1 1 2 2 3 4 |
  | 12 | 0 1 1 1 1 2 2 2 2 3 3 3 4 |

  With `sample-history.json` and today 2026-10-08, the 81 levels equal `heatmapLevels` in that file (3 cells at level 0, 30 at 1, 28 at 2, none at 3, 20 at 4).

- **R12.** `monthLabels(todayKey)` returns `{ column, month }` entries for the heatmap's month axis (system.md, Axes: "Month labels sit over the first column whose Monday falls in that month"). Column 1 is always labelled with the short month of its Monday. A later column is labelled when its Monday is in a different month from the previous column's Monday. A month whose days appear only after a column's Monday gets no label.
  Worked examples: 2026-10-08 gives Jul 1, Aug 3, Sep 8, Oct 12 (the golden's axis). 2026-10-12 gives Jul 1, Aug 2, Sep 7, Oct 11. 2027-01-07 gives Oct 1, Nov 3, Dec 8, Jan 12. 2026-03-31 gives Jan 1, Feb 4, Mar 8 and no Apr label, although 1 to 5 April sit in column 12.

### Names and the habit list

- **R13.** `validateName(raw, existingNames)` (brainstorm, Habit name. RULINGS rule 3) trims `raw` with `String.prototype.trim`, then checks in this order and returns the first failure:
  1. empty gives `{ ok: false, error: "empty" }`;
  2. more than 40 Unicode code points (`Array.from(name).length > 40`, CG-8 ruled 2026-10-08, ORCH) gives `{ ok: false, error: "too-long" }`;
  3. equal to an existing name when both are lower-cased with `toLowerCase()` gives `{ ok: false, error: "duplicate" }`.
  Otherwise it returns `{ ok: true, name: <the trimmed name> }`.
  Examples with existing names `["Read 20 pages", "Stretch 10 minutes", "No phone after 11pm"]`: `""` is empty. `"   "` is empty. `"Walk to the end of the street and back after dinner"` (51 code points) is too long. `"Read twenty pages before bed every night"` (40) is ok. `"Read twenty pages before bed every night."` (41) is too long. `"  Drink water  "` is ok with name `"Drink water"`. `"read 20 pages"` is a duplicate. `" STRETCH 10 MINUTES "` is a duplicate. A 41 code point name that also matches an existing name is too long (order). A name of 40 emoji (40 code points, 80 UTF-16 units) is ok.
  Changed 2026-10-09 (security SEC-02, ORCH): the rule is unchanged, more than 40 code points as `Array.from(name).length` counts them, a lone surrogate counting as one. The code now counts with the private `longerThan`, which walks the same string iterator and stops at the 41st code point, so a name planted in storage at quota size is never copied into an array. The expression in rule 2 states the rule, not how the code counts. Results are the same for every string (51,202 differential cases, `../findings/security.md`, Solver section).

- **R14.** `addHabit(habits, raw)`. When `habits.length` is 12 or more it returns `{ ok: false, error: "limit" }` without checking the name (brainstorm: "At most 12 habits"). Otherwise it runs `validateName(raw, <names of habits>)` and returns its failure unchanged. On success it returns `{ ok: true, habits: <new array> }`: the old habits in their order followed by `{ name: <trimmed name>, done: [] }` (brainstorm: "New habits go to the bottom").
  Examples: adding `"Drink water"` to the 3 sample habits gives 4 habits with "Drink water" last. Adding to 11 habits gives 12. Adding to 12 habits gives `limit`. Adding `"read 20 pages"` to the sample gives `duplicate`.

- **R15.** `deleteHabit(habits, index)` returns a new array without the habit at `index`, the others in their order. When `index` is not an integer index of `habits` it returns a new array equal in content to `habits`.
  Example: deleting index 0 of the sample gives `["Stretch 10 minutes", "No phone after 11pm"]` with their `done` arrays unchanged.

### Purity

- **R16.** The module is pure and deterministic. `src/dates.js` and `src/habits.js` contain no `Date.now(`, no `new Date()` without arguments, and none of `document`, `window`, `localStorage`, `globalThis`, `Intl` or `toLocale`. `habits.js` imports only `./dates.js` and `dates.js` imports nothing. No exported function changes its arguments (checked by calling every function with deep-frozen inputs, which throw on any write in strict-mode ES modules).
  Changed 2026-10-08 (plan-check flag, ORCH): the ban on `document`, `window`, `localStorage`, `globalThis`, `Intl` and `toLocale` applies to code, as whole words, with comments removed first, so a function comment may say "the week window". `Date.now(` and `new Date()` without arguments stay banned anywhere in the file text, comments included, so a comment must not spell them. The sentence above first applied the word ban to the whole file text.
  Changed 2026-10-09 (code review WR-02, ORCH): the frozen-input check is true for arrays and objects only. `Object.freeze` does not protect a Date's internal time value, and `setHours` and the other setters still succeed on a frozen Date in strict mode. So arguments are checked by calling every function with deep-frozen arrays and objects, plus a before-and-after `getTime()` comparison for the Date passed to `localDateKey`. The first sentence of R16 said deep-frozen inputs "throw on any write in strict-mode ES modules", which is false for a Date.
  Changed 2026-10-09 (security SEC-03, ORCH): the source scan is widened. The bans above still hold and are now part of two named tables in `tests/purity.test.js`, and each new pattern matches everything the pattern it replaced matched.
  - `CLOCK_AND_RANDOM_READS`, matched on the whole file text, comments included, and again on the code with comments removed (which also finds a read that a comment splits, such as `new Date(/* today */)`): `Date.now` with or without a call, `new Date` with no argument with or without parentheses, `Date` called as a function, `performance.now` and `Math.random`. `new Date` with an argument and `Date.UTC` stay allowed, because they read no clock.
  - `BANNED_IN_CODE`, matched on the code only, as whole words, comments removed: `document`, `window`, `self`, `globalThis`, `navigator`, `process`, `localStorage`, `sessionStorage`, `indexedDB`, `caches`, `fetch`, `XMLHttpRequest`, `WebSocket`, `EventSource`, `sendBeacon`, dynamic `import(`, `setTimeout`, `setInterval`, `setImmediate`, `queueMicrotask`, `requestAnimationFrame`, `crypto`, `Intl` and `toLocale*`.
  Before this change the scan matched only the text `Date.now(`, the pattern `/new\s+Date\s*\(\s*\)/` and the words of the first sentence, so `new Date` without parentheses, `Date()` and every network and storage call passed it.
  Changed 2026-10-09 (security re-check SEC-04, ORCH): the two lists above are incomplete. `CLOCK_AND_RANDOM_READS` also holds `Temporal.Now` (`/\bTemporal\s*\.\s*Now\b/`), matched the same way, and `Temporal.PlainDate` arithmetic stays allowed. `BANNED_IN_CODE` also bans code built from a string at run time, `eval` and the `Function` constructor (`Function(` and `new Function(`), because a clock read spelled inside such a string passes every pattern. A text scan still cannot see a clock read reached through an alias, such as `Reflect.construct(Date, [])`, `const Clock = Date; new Clock()` or `new (Date)()`. Those are deliberate evasions, left to review.

### The year (v1.1.0)

- **R17.** (v1.1.0 new, S1 and S7) Two more English labels from the same fixed tables as R4, the same under every runtime locale (system.md, Accessible names, "P4 day ... with the year, because P4 holds two Octobers", and year-view.md, "Months").
  - `yearDate(key)` returns `"<weekday> <day> <month> <year>"`, the R4 `shortDate` followed by a space and the 4-digit year, for example `"2025-10-10"` gives `"Fri 10 Oct 2025"` and `"2026-10-10"` gives `"Sat 10 Oct 2026"`.
  - `monthTitle(key)` returns the full month name of the key's month, a space and the 4-digit year, for example `"2026-10-10"` gives `"October 2026"` and `"2025-12-01"` gives `"December 2025"`.

- **R18.** (v1.1.0 new, S1) `yearStart(todayKey)` returns the first day of the editable year, "today back to the same date last year" (brainstorm v1.1.0, Round 1 rulings). That is the date key with the year one less, the same month and the same day. When that day does not exist (`todayKey` is 29 February), it returns 28 February of the year before (CG-13, ruled 2026-10-13 by the owner with this answer, ledger S1 row 4). The range `yearStart(todayKey)` to `todayKey`, both included, holds 366 days, or 367 when it includes a 29 February.
  Examples. `"2026-10-10"` gives `"2025-10-10"` (366 days, year-view.md "Friday 10 October 2025 to Saturday 10 October 2026 (366 days)"). `"2026-01-01"` gives `"2025-01-01"`. `"2027-03-01"` gives `"2026-03-01"`. `"2028-03-01"` gives `"2027-03-01"` (367 days). `"2028-02-29"` gives `"2027-02-28"` (367 days, CG-13).

- **R19.** (v1.1.0 new, S1 and S7) `doneFlags(habits, dateKey)` returns one boolean per habit, in list order, `true` when that habit's `done` contains `dateKey` (system.md, Ring, "one segment per habit, clockwise from the top in list order"). With no habits it returns `[]`.
  Examples with the v1.1.0 sample (its first three habits, today 2026-10-10). `"2026-10-10"` gives `[true, false, false]`. `"2026-09-22"` gives `[false, false, true]`. `"2026-07-21"` gives `[true, true, true]`. `"2026-10-11"` gives `[false, false, false]`. With all twelve habits, `"2026-10-10"` gives 7 `true` values (today-full.md, "today 7 of 12 habits done").
  With the same sample and today, `currentStreak` and `bestStreak` give the goldens' numbers. Read 20 pages 4 and 9, Stretch 10 minutes 2 and 5, No phone after 11pm 0 and 14 (today.md), and for the twelve habits the values of the table in today-full.md.

- **R20.** (v1.1.0 new, S1 and S7) `yearMonths(todayKey)` returns the calendar of the two year views (year-view.md, overview-year.md), months newest first, from the month of `todayKey` back to the month of `yearStart(todayKey)`, both included (always 13 months, because the month of `yearStart(todayKey)` is the same month one year earlier). Each month is `{ key, title, lead, days }`.
  - `key` is the date key of its first day. `title` is `monthTitle(key)` (R17).
  - `lead` is `weekdayIndex(key)` (R4), the number of empty cells before day 1 in a Monday-first grid.
  - `days` holds one entry per day of the month, `{ key, day, kind }`, where `day` is the day of the month and `kind` is `"empty"` before `yearStart(todayKey)`, `"closed"` after `todayKey`, and `"open"` otherwise.
  Examples, today `"2026-10-10"`. 13 months, the first `{ key: "2026-10-01", title: "October 2026", lead: 3 }` with days 1 to 10 open and 11 to 31 closed, the last `{ key: "2025-10-01", title: "October 2025", lead: 2 }` with days 1 to 9 empty and 10 to 31 open. September 2026 has lead 1, August 2026 lead 5, July 2026 lead 2. In all 13 months, 366 days are open, 21 closed, 9 empty, and the leads add up to 39 (the golden `year-view.html` holds 366 day buttons, 21 closed cells, 9 blank cells and 39 lead cells). Today `"2026-11-01"` gives November 2026 first (day 1 open, 2 to 30 closed), November 2025 last (no empty day). Today `"2028-02-29"` gives February 2028 first, February 2027 last with days 1 to 27 empty, 367 open days.
  Changed 2026-10-15 in the v1.1.0 regression (planner, ledger H-06, owner ruling USER 2026-10-15 21:03, option 1, security finder SEC-R01). The bound. `yearMonths` always ends and never returns more than the 13 months this requirement promises. It is contracted here and built at task 9a, not built yet. What a test checks, by key.
  - Every `todayKey` that passes `isDateKey` (0001-01-01 to 9999-12-31). The call returns exactly the 13 months it returns before this change, entry for entry. The examples above hold, and so do `"0001-01-01"` and `"9999-12-31"`, which return 13 months.
  - Every day of October, November and December of the years 10000 to 10009 (920 keys, `"10000-10-01"` to `"10009-12-31"` in those three months). `localDateKey` writes these with a five digit year, so `isDateKey` rejects them, and the app passes them in from a device clock set that far ahead. The call returns, and returns at most 13 months. Before this change it never returned. The month prefix of `yearStart` for such a key is `0999d-1` (d is the last digit of the year), a prefix the month walk never writes, so the walk ran back past year 1 while its array grew about 90 MiB a second until the tab gave out (SEC-R01, `../app/findings/regression-security.md`).
  - Every other `todayKey`. The call returns at most 13 months or throws. It never runs on. That is the whole claim for those keys.
  What the bound leaves alone is the rest of SEC-05, re-accepted by the same ruling. The months returned for a key that fails `isDateKey` are not a calendar, and this requirement does not specify them beyond their number. January to September of every year from 10000 on, and every six digit year, still throw a `TypeError`. October to December of the years from 10010 on still return 11 one-day months (`../app/qa/regression-security/20261015-192841/probe_10_yearmonths.txt`).

## Contracts

### Files
`src/dates.js` and `src/habits.js`. Nothing else in `src/` belongs to this module.

### Types (JSDoc in the source)
```js
/** @typedef {string} DateKey  "YYYY-MM-DD", a local calendar day */
/** @typedef {{ name: string, done: DateKey[] }} Habit  done ascending, no duplicates */
/** @typedef {{ key: DateKey, column: number, row: number, today: boolean, future: boolean,
 *              done: boolean[] | null, count: number | null, total: number }} HeatCell   (v1.1.0 changed: done added, level removed) */
/** @typedef {{ column: number, month: string }} MonthLabel */
/** @typedef {{ key: DateKey, day: number, kind: "open" | "closed" | "empty" }} YearDay   (v1.1.0 new) */
/** @typedef {{ key: DateKey, title: string, lead: 0 | 1 | 2 | 3 | 4 | 5 | 6, days: YearDay[] }} YearMonth   (v1.1.0 new) */
/** @typedef {{ ok: true, name: string } | { ok: false, error: "empty" | "too-long" | "duplicate" }} NameCheck */
/** @typedef {{ ok: true, habits: Habit[] } | { ok: false, error: "limit" | "empty" | "too-long" | "duplicate" }} AddResult */
```
The `Habit` shape is the same as a habit in `sample-history.json` and in the app's stored state.

### `src/dates.js` exports
| Export | Signature | Requirement |
|---|---|---|
| `localDateKey` | `(date: Date) => DateKey` | R1 |
| `isDateKey` | `(value: unknown) => boolean` | R2 |
| `addDays` | `(key: DateKey, days: number) => DateKey` | R3 |
| `dayParts` | `(key: DateKey) => { weekday: string, day: number, month: string }` | R4 |
| `shortDate` | `(key: DateKey) => string` | R4 |
| `longDate` | `(key: DateKey) => string` | R4 |
| `weekdayIndex` | `(key: DateKey) => 0 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6` (Monday 0 to Sunday 6) | R4 |
| `yearDate` (v1.1.0 new) | `(key: DateKey) => string` | R17 |
| `monthTitle` (v1.1.0 new) | `(key: DateKey) => string` | R17 |

Changed 2026-10-09 (code review WR-04, ORCH): `weekdayIndex` added. The table first listed six exports.

### `src/habits.js` exports
| Export | Signature | Requirement |
|---|---|---|
| `MAX_HABITS` | `12` | R14 |
| `MAX_NAME_LENGTH` | `40` | R13 |
| ~~`weekWindow`~~ | removed in v1.1.0 (R5 retired) | R5 |
| `currentStreak` | `(done: readonly DateKey[], todayKey: DateKey) => number` | R6 |
| `bestStreak` | `(done: readonly DateKey[]) => number` | R7 |
| ~~`runContinues`~~ | removed in v1.1.0 (R8 retired) | R8 |
| `toggleDay` | `(habits: readonly Habit[], index: number, dateKey: DateKey, todayKey: DateKey) => Habit[]` (v1.1.0 changed range) | R9 |
| `heatmapCells` | `(habits: readonly Habit[], todayKey: DateKey) => HeatCell[]` (length 84, v1.1.0 changed cell) | R10 |
| ~~`heatLevel`~~ | removed in v1.1.0 (R11 retired) | R11 |
| `monthLabels` | `(todayKey: DateKey) => MonthLabel[]` | R12 |
| `yearStart` (v1.1.0 new) | `(todayKey: DateKey) => DateKey` | R18 |
| `doneFlags` (v1.1.0 new) | `(habits: readonly Habit[], dateKey: DateKey) => boolean[]` | R19 |
| `yearMonths` (v1.1.0 new) | `(todayKey: DateKey) => YearMonth[]` (length 13 for a key that passes `isDateKey`, never more than 13 for any key. Changed 2026-10-15, ledger H-06, contracted and not yet built) | R20 |
| `validateName` | `(raw: string, existingNames: readonly string[]) => NameCheck` | R13 |
| `addHabit` | `(habits: readonly Habit[], raw: string) => AddResult` | R14 |
| `deleteHabit` | `(habits: readonly Habit[], index: number) => Habit[]` | R15 |

Nothing else is exported. User-facing copy (streak text such as "6 days", error messages, accessible names such as "Mark Tue 6 Oct as done") belongs to `app`, which builds it from these values. The date labels of R4 are the one exception, because they are the date-key concern.
v1.1.0. The labels of R17 join that exception for the same reason. The ring's drawing (arcs, legend) is `app`'s (app R42), because it is geometry of the view and not a rule about days. `doneFlags` is the one place that answers "which habits are done on this day", so the band, the overview popup, the overview year view, the day editor and the Overview button all read it (DRY), and `heatmapCells` builds its `done` from it.

### Persistence / state
None. The module holds no state between calls.

### Tests
- Files: `tests/dates.test.js`, `tests/habits.test.js`, `tests/sample-history.test.js`, `tests/purity.test.js`. Node's `node:test` and `node:assert/strict` only.
- `tests/sample-history.test.js` reads `docs/design/sample-history.json` read-only (for example `import sample from "../docs/design/sample-history.json" with { type: "json" }`, which Node 24 supports). No test writes anywhere under `docs/`.
- Time-zone cases set `process.env.TZ` inside the test before they build any `Date`. Node 24 applies the new zone at once (measured 2026-10-08: noon 7 March to noon 8 March 2026 is 23 hours under `America/New_York`). Each test file runs in its own process, so a zone set in one file does not leak into another.
- Command, from the project root: `node --test "tests/**/*.test.js"` (the CLAUDE.md command. The earlier form `node --test tests/` exits 1 on Node 24.11.1, measured 2026-10-08). No `package.json` is needed: Node 24 detects ES module syntax in `.js` files (measured, no warning).
- Each `test()` title starts with the tag or tags of the qa.md scenario it implements, for example `@R6 Stretch holds at 3 days while today is open`, so the QA finder can map results to R numbers.
- v1.1.0 (changed test data). The design finalize of 2026-10-13 replaced `docs/design/sample-history.json`. The v1.1.0 file has `today` "2026-10-10", `from` "2025-10-10" and, per habit, `done` as a string of 366 characters, `"1"` done and `"0"` not, character 0 being `from` and character 365 being `to`. It has no `heatmapLevels`. So on the current tree `tests/habits.test.js`, `tests/purity.test.js` and `tests/sample-history.test.js` read a file they were not written for. Task 6 fixes it as follows.
  - `tests/fixtures/sample-history-v1.0.0.json` holds, byte for byte, `git show v1.0.0:docs/design/sample-history.json`. Every 1.0 scenario that names "the sample" or "the 1.0 sample" reads this fixture. It is test data under `tests/`, which is never published (CLAUDE.md, Publish).
  - "The v1.1.0 sample" is `docs/design/sample-history.json` read-only, converted by one shared test helper (`tests/fixtures/sample.js`, export `sampleHabits(file)`) into habits of the `Habit` shape. For each `"1"` at position i, the key `addDays(from, i)`. The helper is test code and uses the module's own `addDays`.

## Tasks
> Atomic, ordered, one commit each. Each commit carries the code and the tests that prove it.
> Changed 2026-10-09 (module close housekeeping, ORCH): the five boxes below are ticked. All five tasks are done, one commit each, see `BUILD.md`, "Tasks to commits". The boxes were never ticked when the tasks were built.
1. [x] `src/dates.js` with `localDateKey`, `isDateKey`, `addDays`, `dayParts`, `shortDate`, `longDate`, and `tests/dates.test.js` with every R1 to R4 scenario in qa.md. → R1, R2, R3, R4
2. [x] `src/habits.js`, part 1: the constants, `weekWindow`, `currentStreak`, `bestStreak`, `runContinues`, `toggleDay`, and their scenarios in `tests/habits.test.js`. → R5, R6, R7, R8, R9
3. [x] `src/habits.js`, part 2: `heatLevel`, `heatmapCells`, `monthLabels`, and their scenarios. → R10, R11, R12
4. [x] `src/habits.js`, part 3: `validateName`, `addHabit`, `deleteHabit`, and their scenarios. → R13, R14, R15
5. [x] `tests/sample-history.test.js` (every golden value from the sample) and `tests/purity.test.js` (source scan and deep-frozen inputs). → R5, R6, R7, R8, R10, R11, R12, R16

v1.1.0 tasks, in `../ROADMAP.md` build order. Task 6 runs first of all v1.1.0 code work, together with app task 11, because the unit baseline must be green before anything is measured. Changed 2026-10-13 (planner, solutions architect role). This line and the v1.1.0 roadmap note below first read "app task 1" and "app task 3". The app's v1.1.0 tasks are numbered 11 to 28, so they are app task 11 (the engine switch and the baseline) and app task 15 (the boot render, the first app task that uses tasks 7 to 9).
Changed 2026-10-13 after the plan check (B1). The sample is not the only cause of the red state. Four 1.0 browser tests also read 1.0 goldens that the finalize replaced in `docs/design/`. App task 11 restores those four goldens as fixtures in `tests/fixtures/design-v1.0.0/` the same way task 6 restores the sample (app spec, task 11). This module's unit suite reads no golden, so task 6 is unchanged.
Changed 2026-10-15 (code-review WR-01, solver). Tasks 6 to 9 below are ticked. Each is built and committed (`6188e66`, `964678b`, `9a79991`, `3676fe5`), see `BUILD.md`, "Tasks to commits". The boxes were never ticked when the tasks were built.

6. [x] The test data fix. `tests/fixtures/sample-history-v1.0.0.json` and `tests/fixtures/sample.js`, the three test files pointed at the fixture, no change in `src/`. Proof, `node --test "tests/**/*.test.js"` gives the sealed count (99 tests, `docs/v1.0.0/SEAL.md`) green on the unchanged `src/`, and `git hash-object tests/fixtures/sample-history-v1.0.0.json` prints `62620300113514b9712d0cbdfea2b15534e6d326`, the blob id of `v1.0.0:docs/design/sample-history.json` (`git rev-parse` gives it). The blob id is the check because `core.autocrlf` is true on this machine, so a later checkout may change the file's line ends while its blob stays equal. → R6, R7, R10, R12, R16 (test data only)
7. [x] `src/dates.js` gains `yearDate` and `monthTitle`, with their scenarios. → R17
8. [x] `src/habits.js` with `yearStart`, `doneFlags`, `yearMonths`, and `toggleDay` on the year range, `heatmapCells` with `done` and without `level`. `weekWindow`, `runContinues` and `heatLevel` removed with their tests, the retired scenarios kept as text in qa.md only. The purity scan and the frozen-input check cover the new exports. → R9, R10, R18, R19, R20, R16
9. [x] `tests/sample-history.test.js` gains the v1.1.0 sample checks (the goldens' Current and Best for all twelve habits, the band's 83 days, the year's 366 days). → R10, R19, R20
9a. [ ] The bound on `yearMonths` (owner ruling H-06, 2026-10-15 21:03, option 1). In `src/habits.js`, `yearMonths` stops after the 13 months its doc comment promises, so it ends for every `todayKey` (R20, the bound). Its doc comment says so in a line or two, with the reason. The test is the `@R20` Scenario Outline "yearMonths ends for every key and returns at most 13 months", written first into `tests/habits.test.js` with its title starting `@R20`. A call that may never end cannot be failed from its own thread, so each row calls `yearMonths` in a worker thread with a heap limit and a timer, and a worker stopped by either fails the row (qa.md names the method). RED before the bound lands, on the October to December rows of 10000 to 10009, with the valid-key rows green in the same run as the control that the worker harness works. The capture goes to `docs/modules/habit-logic/qa/red-first/<datetimestamp>/`. A hung or crashed runner is not a RED. Then the bound, and nothing else changes. No other function, no export and no import, and the purity scan (R16) stays green. Proofs go to `docs/modules/habit-logic/qa/solver/<datetimestamp>/`.
    - Node. The scenario green. `node --test "tests/**/*.test.js"` green with no existing test changed. A one-off differential that the function before and after the change returns deep-equal results for every day from 1999-01-01 to 2101-12-31 (37,620 keys) and for the first day of every month of the years 0001 to 9999 (119,988 keys), the earlier function taken from `git show ad40779:src/habits.js`. It is not a committed test, because it takes minutes. The planner ran the same differential on a throwaway copy with the loop capped at 13, in about 33 s and 104 s, with 0 differences.
    - Chromium and WebKit, run after task 28a of `app` is committed, so they cover the whole pass. `python -m pytest tests/browser -q` and the same with `--engine webkit`, both green, no browser test added or changed, with the counts of the last green runs (Chromium 358 passed, WebKit 357 passed and 1 skipped, CO-1). The security finder's probes `probe_11_year10000.py` (group `hang`) and `probe_14_rollover_hang.py` (which imports the first), with `lib.py`, copied from `docs/modules/app/qa/regression-security/20261015-192841/` into the task's own evidence folder and run once in each engine on the changed tree. They show the page still answers with the clock at 10000-10-15, and at the midnight into 10000-10-01 with P4 open. The finder's captures in the original folder froze the page and are the control, so the freeze is not run again. → R20, R16
    Added 2026-10-15 in the v1.1.0 regression, after the owner's ruling (ledger H-06). This task has the id 9a so that it sits after task 9 and no task is renumbered. It is built in one dev-solver pass with task 28a of `app` (the comment of `firstControl`, code review RG-CR-I1), which belongs to `app` because `src/view.js` is its file. Task 9a is committed first. Both are contracted here and not built.

## Threat model
> Feeds the security gate. This module has no I/O. Its risks are wrong values and broken invariants.

| Asset | Boundary | Threat | Required mitigation |
|---|---|---|---|
| The day the user sees as "today", and every streak built on it | `Date` instant into `localDateKey` | A UTC getter or millisecond arithmetic shifts the day near midnight or across a DST change, so streaks break or double count | R1 uses the local getters. R3 uses calendar arithmetic. Tests under `Asia/Kuala_Lumpur` and `America/New_York` (qa.md). |
| Deterministic, testable results | the whole module | A hidden clock read makes results depend on when they run, and the midnight rollover becomes untestable | `todayKey` is always an argument. R16 scans the source for clock reads. Changed 2026-10-09 (security SEC-03, ORCH): the scan now also finds `new Date` without parentheses, `Date()`, `Date.now` without a call, `performance.now` and `Math.random` (the table `CLOCK_AND_RANDOM_READS`, see R16). Before this change it found none of these five. Changed 2026-10-09 (security re-check SEC-04, ORCH): the table missed `Temporal.Now` and now holds it, and the code may not build code from a string (`eval`, `Function(`), which would hide any read from the scan. See R16. |
| English copy | label functions | `Intl` or `toLocale*` returns another language or other digits on a non-English device | Fixed tables (R4). R16 scans for `Intl` and `toLocale`. |
| Responsiveness with tampered stored data | strings from storage reach `isDateKey` and `validateName` through the app's decoder | A pathological string causes catastrophic regex backtracking | Only the anchored, linear pattern `^\d{4}-\d{2}-\d{2}$`. Name length is counted in one linear pass. No other regular expression runs on stored data. Changed 2026-10-09 (security SEC-02, ORCH): the threat also covers memory. The name is counted in one pass that stops after 41 code points (`longerThan`), so a stored name of any size costs no more than a short one. The first count was linear in time but copied the whole name into an array first, up to 153 MiB of heap for a name of 5,000,000 UTF-16 units. |
| The app's in-memory state | arrays passed in by the app | A function mutates its input and the screen, the saved data and the logic disagree | Pure functions returning new arrays (R16, frozen-input tests). |
| The app's invariants: at most 12 habits, valid unique names, only the last 7 days editable. v1.1.0 changed, only the days from `yearStart(today)` to today editable | `addHabit`, `toggleDay` | A caller bypasses the rules through the API | `addHabit` checks the limit, then the name (R14). `toggleDay` refuses dates outside the range and keys that fail `isDateKey` (R9, v1.1.0 changed), so a key after today, before the year start or not a real date never enters `done` through a tick. |
| Responsiveness of the year views. Added v1.1.0 | `doneFlags` takes one day, and the app calls it once per drawn day, up to 367 times for P4 and 84 for the band or P3 (app R39, R35, R38) | Each call reads every habit's `done`, so one draw of P4 costs about days x habits x history. A call that scans a `done` array more than once per habit, or nests scans, makes that worse | One `doneFlags` call reads each habit's `done` at most once (one lookup per habit, or one set built per habit), so no call is quadratic. `heatmapCells` builds each cell's `done` with `doneFlags` (R10), so one band costs at most 84 such calls. The cost of a P4 draw is then bounded by 367 x 12 habits (R14) x the stored history of one habit. Through ticks that history holds each day at most once (`done` is a set of days) and only days from `yearStart` of the first day of use up to today (R9). So one sitting can add up to 367 days to a habit, and Y years of use leave at most about 365 x Y + 367. Residual, accepted, that draw grows linearly with the years of history (no cache, Non-goals). Planted data is not bounded by use (app T8, T9). A planted `done` list can hold as many valid dates as the origin's storage quota allows, and one P4 draw then reads it up to about 367 times, the band or P3 up to about 84 times. App T8 carries that case and bounds it by the quota. Unit tests time nothing, the review checks that no call reads a `done` array more than once per habit. Changed 2026-10-13 after the plan re-check (N8). This cell said the stored history "grows by at most one day per habit per day of use", which stopped being true once the whole year became editable, and it did not name planted data. Changed 2026-10-13 after the plan check (F11). This row first said `doneFlags` answers from a set built once per call, so a call is linear in the history size. That holds per call, but `doneFlags` takes one day and P4 makes 367 calls, so the row now states the cost of the whole draw and its bound. |
| Object integrity | habit objects | Prototype pollution through copying objects key by key | New habits are built as literal `{ name, done }` objects. No `Object.assign` or spread of objects whose keys come from data. Changed 2026-10-09 (code review WR-03, ORCH): the two are avoided for different reasons. `Object.assign` runs the `__proto__` setter and can swap the target's prototype. Spread never runs that setter, but it carries every unknown key from stored data (`__proto__`, `constructor` or any other) into new state. Building `{ name, done }` literals avoids both. The row first grouped spread with `Object.assign` as a prototype risk. |
| Responsiveness with date keys outside the valid range. Added 2026-10-09 (security SEC-01, ORCH) | `done` arrays reach `currentStreak` and `bestStreak` | A key that fails `isDateKey` (near 2^53 days, or before year 0001) makes `addDays` return a key it already returned, so a streak walk never ends. The app computes `bestStreak` at boot, so the tab would hang on every load. Changed 2026-10-09 (security re-check SEC-01, ORCH): `parseKey` reads each part with `Number()`, which ignores white space, so one such date has thousands of spellings. In `bestStreak` each spelling starts its own walk into the stuck key, about n squared steps in all (20,000 keys gave no result in 60 s). | Keys that fail `isDateKey` are ignored by `currentStreak` and `bestStreak` (R6 and R7, notes dated 2026-10-09). Why that ends every walk is in the comment on `streakDays`. The app's readable rule 5 keeps such keys out today. ~~Each walk is bounded by the number of distinct days: `runLength` stops after as many days as the set holds.~~ ~~The bound holds if one gets through.~~ ~~The size bound stays as a second guard.~~ Changed 2026-10-09 (code review WR-12 and WR-15, ORCH): the three struck sentences named the size bound in `runLength`. The control is the filter in `streakDays`. The bound behind it is removed, because behind the filter a walk ends at the first day not in the set, so the bound never decided a result and no test could pin it (`../qa/code-review/20261009-131935/`, `probe-bound.mjs`, mutant `bound-removed`). Valid input gives the same results (`../qa/solver/20261009T135035/`, `bound-differential.mjs`). This cell also held the derivation and the differential counts. They are now in the `streakDays` comment and in `../findings/security.md`, and the earlier wording of this cell is in git history, commit `fa7838d`. |
| No network or storage call. Added 2026-10-09 (security SEC-03, ORCH) | the whole module | A network, storage, timer or global call added to the module sends data off the device, reads or writes state, or makes results depend on when they run | The module has no I/O. The R16 scan bans each such call in the code (the table `BANNED_IN_CODE`, see R16). |
| Termination of `yearMonths` with a today key outside the valid range. Added 2026-10-15 (security regression finder SEC-R01, ledger H-06) | the device clock through the app's `readToday` and `localDateKey` into `todayKey`, then into `yearMonths`. Only the device's own clock reaches it | A clock in October to December of the years 10000 to 10009 gives a key whose walk back never ends, so the call never returns and its array grows until the tab gives out. The data is untouched and a reload recovers, so the weight is LOW | `yearMonths` stops after 13 months for any input (R20, the bound). SEC-R01 is closed by the bound, task 9a. It is contracted 2026-10-15 and not built at this writing. Residual, re-accepted by the owner (ledger H-06). For a key that fails `isDateKey` the months are not a calendar, and `yearMonths` still throws in January to September of every year from 10000 on. `../app/spec.md`, Threat model, carries SEC-05 whole |

## Non-goals
> Explicit "do NOT build". Building any of these is a defect.
- No DOM access, rendering, CSS, event handling, storage access, storage format or decoding (all owned by `app`).
- No reading of the clock and no timers.
- No `Intl`, no locale support, no languages other than English.
- No time zones stored or converted, no UTC day keys.
- No user-facing copy other than the R4 date labels (v1.1.0, and the R17 labels).
- No caching or memoisation layer.
- From the brainstorm's non-goals, where they touch logic:
  - No weekly targets ("3 times a week") or any schedule other than daily.
  - No renaming or reordering habits: no rename or move function.
  - ~~No editing of days older than the last 7: `toggleDay` refuses them.~~ Removed in v1.1.0 (brainstorm v1.1.0, "The non-goal "Editing days older than the last 7" is removed", USER). Replaced by no editing of a day after today or before `yearStart(today)` (R9).
  - No more than one tick per day, no notes, no amounts: `done` is a set of days.
  - No stats beyond current streak, best streak and the heatmap: no totals, averages, rates or per-habit heatmaps. v1.1.0, "the heatmap" now reads "the overview and the two year views". No totals, averages, rates or done counts per habit (the year view shows days, not a count of them).
  - No export or import.
- v1.1.0. No start date per habit and no field other than `name` and `done` (brainstorm v1.1.0, "1.0 stores no start date").
- v1.1.0. No ring geometry, legend rule or any other drawing here (app R42).
- v1.1.0, ledger H-06 (2026-10-15). The bound is the whole change. Do NOT make the module validate `todayKey` (no `isDateKey` call in `yearMonths`), do NOT add a guard for five digit years to `localDateKey`, `yearStart`, `heatmapCells` or `toggleDay`, and do NOT change what `yearMonths` returns for a key that passes `isDateKey`. The finder's other option, an app that opens no year view while `isDateKey(todayKey)` is false, was not ruled and is not built. The rest of SEC-05 is re-accepted as it is.

## Roadmap
- **Build order:** 1 of 2. No dependencies, so it is built first.
- **Nature:** logic (no FE, no BE).
- **Done when:** functional QA green (`node --test "tests/**/*.test.js"`, every `@R` scenario passing), code review pass, security pass. No fidelity gate (it renders nothing). Its live behaviour is proven by `app`'s cold-boot live-e2e gate, which uses every export.
  Changed 2026-10-09 (code review WR-07, ORCH): the gate does not use every export. It uses the exports `app` consumes, listed in `../app/spec.md`, "Uses from habit-logic". `addDays`, `weekdayIndex`, `heatLevel` and `MAX_NAME_LENGTH` are not among them. The gate reaches them only inside `toggleDay`, `heatmapCells`, `monthLabels` and `validateName`, so their direct proof is the unit suite.
  Changed 2026-10-15 after execute, wording pass before the regression (ledger S1 rows 21 and 25). The list above also misses `monthTitle` and `yearStart`, two v1.1.0 exports that no app file imports (`../app/spec.md`, "Uses from habit-logic", struck both on 2026-10-15). `monthTitle` is in `src/dates.js` and the gate reaches it only inside `yearMonths`. `yearStart` is in `src/habits.js` and the gate reaches it only inside `yearMonths` and `toggleDay`. Their direct proof is the unit suite, like the four above. `heatLevel`, named above, was removed in v1.1.0 (the exports table, R11 retired), so it no longer belongs in the list and `heatmapCells` no longer reaches it.
- **Unblocks:** `app`.
- **v1.1.0.** Build order 1 of 2 again. Task 6 (test data) first, with app task 11, then tasks 7 to 9 before app task 15 (corrected 2026-10-13, see the note above Task 6). Done when the unit suite is green with every new and changed `@R` scenario, the retired scenarios are gone from `tests/` (kept as text in qa.md), code review and security pass. The app's cold-boot gate in both engines proves the live use. Nature unchanged (logic, no engine). No phase skill applies (no UI).
  Added 2026-10-15 in the v1.1.0 regression (ledger H-06). Task 9a (the bound on `yearMonths`) is built after `app` task 28, in one dev-solver pass with `app` task 28a. The roadmap names the order, `../ROADMAP.md`, Build order, step 7.
