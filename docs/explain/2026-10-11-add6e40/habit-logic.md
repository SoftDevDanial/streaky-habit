# habit-logic, code walkthrough

Written by the codebase explainer (read-only), 2026-10-11.

| | |
|---|---|
| Module | `habit-logic`, the files `src/dates.js` and `src/habits.js` |
| Snapshot | git HEAD `d786d25` as the brief names it, the v1.0.0 build. `docs/regression/REGRESSION.md` records habit-logic's `src/` as unchanged since `de0156a` |
| Read for this | both source files, `tests/dates.test.js`, `tests/habits.test.js`, `tests/purity.test.js`, `tests/sample-history.test.js`, `tests/storage.test.js`, the module's `spec.md`, `qa.md`, `BUILD.md` and its three findings files, and the imports and call sites in `src/app.js`, `src/view.js` and `src/storage.js` |
| Not done | I had no shell, so I did not run the suite or check git. Every pass count below is quoted from a recorded run, and says which |

This is a dated snapshot. Every citation is a symbol, so it can be checked with grep.

## 1. What it does

habit-logic is the rule book of Streaks. Give it a habit's ticked days and today's date, and it says which seven days the week strip shows, how long the current and best streaks are, whether a run comes in from before the strip, how full each of the 84 heatmap days is, and which months label the heatmap. It also decides whether a habit name is allowed, and it builds the new list after an add, a tick or a delete. It draws nothing, stores nothing and never reads the clock. The page passes "today" in and gets new values back.

## 2. Where it starts

The module has no entry point of its own. It is two ES module files that the app imports.

- `src/dates.js` imports nothing. It owns the day key and all calendar arithmetic.
- `src/habits.js` imports `addDays`, `dayParts`, `isDateKey` and `weekdayIndex` from `./dates.js`, and nothing else. It owns the habit rules.

Two tests in `tests/purity.test.js` pin this shape, `@R16 habits.js imports only ./dates.js and dates.js imports nothing` and `@R16 only the contracted names are exported`.

| Export | File | What it answers | R# | Shipped callers outside the module |
|---|---|---|---|---|
| `localDateKey(date)` | dates.js | The local calendar day of an instant | R1 | `src/app.js` `readToday` |
| `isDateKey(value)` | dates.js | Is this value a real `YYYY-MM-DD` day | R2 | `src/storage.js` `readHabit` |
| `addDays(key, days)` | dates.js | The day `days` after `key` | R3 | none |
| `weekdayIndex(key)` | dates.js | 0 for Monday to 6 for Sunday | R4 | none |
| `dayParts(key)` | dates.js | `{ weekday: "Tue", day: 6, month: "Oct" }` | R4 | `src/view.js` `syncDay` |
| `shortDate(key)` | dates.js | "Tue 6 Oct" | R4 | `src/view.js` `syncDay`, `fillCell` |
| `longDate(key)` | dates.js | "Thursday 8 October" | R4 | `src/view.js` `renderHeader` |
| `MAX_HABITS` | habits.js | 12 | R14 | `src/app.js` `renderHabits`, `src/storage.js` `readHabits` |
| `MAX_NAME_LENGTH` | habits.js | 40 | R13 | none |
| `weekWindow(todayKey)` | habits.js | The 7 strip days, oldest first | R5 | `src/view.js` `createRow`, `syncStrip` |
| `currentStreak(done, todayKey)` | habits.js | The run that is still alive | R6 | `src/view.js` `syncStreak` |
| `bestStreak(done)` | habits.js | The longest run ever | R7 | `src/view.js` `syncStreak` |
| `runContinues(done, todayKey)` | habits.js | Does a run enter the strip from the left | R8 | `src/view.js` `syncStrip` |
| `toggleDay(habits, index, dateKey, todayKey)` | habits.js | The list with one day ticked or unticked | R9 | `src/app.js` `tick` |
| `heatLevel(count, total)` | habits.js | 0 to 4 for one day's share of habits done | R11 | none |
| `heatmapCells(habits, todayKey)` | habits.js | 84 cells for the 12-week grid | R10 | `src/view.js` `renderHeatmap` |
| `monthLabels(todayKey)` | habits.js | Month names over the grid columns | R12 | `src/view.js` `renderMonths` |
| `validateName(raw, existingNames)` | habits.js | Is this name allowed, and its trimmed form | R13 | `src/storage.js` `readHabit` |
| `addHabit(habits, raw)` | habits.js | The list with one new habit, or why not | R14 | `src/app.js` `submitName` |
| `deleteHabit(habits, index)` | habits.js | The list without one habit | R15 | `src/app.js` `removeHabit` |

Four of the twenty exports have no shipped caller outside the module. `addDays`, `weekdayIndex` and `heatLevel` run only inside the module, and `MAX_NAME_LENGTH` is read only by `validateName`. Only the tests import them directly. They are in the spec's Contracts table, so they are public on purpose, and the spec's Roadmap note (dated 2026-10-09, code review WR-07) says the same thing. Nothing in the page depends on them as exports.

## 3. The flow, in call order

### 3.1 The main path, as the page drives it

The clock is read in one place, `src/app.js` `readToday`, which returns `localDateKey(new Date())`. Every other call receives that key as `todayKey`.

1. **Boot** (`src/app.js` `boot`). `loadHabits` in `src/storage.js` decodes the saved list. Its `readHabits` refuses more than `MAX_HABITS` entries. Its `readHabit` runs `validateName(entry.name, earlierNames)` and requires the result to equal the stored name exactly, so a stored name must already be trimmed and unique. Then it requires every `done` value to pass `isDateKey`, and rebuilds `done` sorted and without duplicates. Any failure makes the whole saved state unreadable and the list starts empty. So by the time a habit reaches the other functions here, the `Habit` invariant holds.
2. **First render** (`src/view.js`). `renderHeader` shows `longDate(todayKey)`. `renderMonths` lays out `monthLabels(todayKey)`. `renderList` builds one row per habit. `createRow` takes the number of day buttons from `weekWindow(todayKey)`, then `syncProgress` calls `syncStreak` (`currentStreak` and `bestStreak`) and `syncStrip` (`weekWindow`, `dayParts` and `shortDate` through `syncDay`, then `runContinues`). `renderHeatmap` draws `heatmapCells(habits, todayKey)`, and `fillCell` puts `shortDate` into each cell's accessible name.
3. **Tick** (`src/app.js` `tick`). The pressed button's `data-date` and the row index go to `toggleDay`. The new list is saved, that row is synced again (both streaks, the strip and the run flag), and the heatmap is redrawn.
4. **Add** (`src/app.js` `submitName`). `addHabit(state.habits, view.nameFieldValue())`. On `{ ok: false }` the view shows the message for that error code. On `{ ok: true }` the new list is saved and rendered.
5. **Delete** (`src/app.js` `removeHabit`). `deleteHabit(state.habits, index)`, then save and render.
6. **New day** (`src/app.js` `checkDay`, every 30 seconds and when the tab is shown again, per the README). When `readToday` returns a different key, the header, the month labels, every row and the heatmap are computed again with the new `todayKey`. Nothing in habit-logic knows that a day changed. It simply receives a new key.

### 3.2 `src/dates.js`, the day key

The whole app speaks in one format, the `DateKey`. It is a string `YYYY-MM-DD` that names a local calendar day, for example `"2026-10-08"`. Three things make that choice work. A string is what `localStorage` holds. A fixed-width key sorts as text in calendar order, which `toggledHabit` (`.sort()`) and `heatmapCells` (`key > todayKey`) rely on. And a calendar day has no time of day, so a daylight saving change cannot touch it.

**The private helpers.**
- `pad(number, width)` and `formatKey(year, month, day)` write a key. `formatKey` pads the year to at least 4 digits and the month and day to 2.
- `parseKey(key)` splits on `"-"` and reads each part with `Number()`. It does not validate. On a valid key it is exact. On other text it can return surprising numbers, because `Number()` ignores white space around digits and `pad` writes year -1 as `"00-1"`. The security rounds turned on exactly this (section 3.4).
- `isLeapYear(year)` and `daysInMonth(year, month)` are the Gregorian rules, with `DAYS_IN_MONTH` as the table.

**`localDateKey(date)` (R1).** Takes a `Date` and returns its local calendar day as a key, built from `getFullYear()`, `getMonth() + 1` and `getDate()`. These are the local getters on purpose. The UTC getters give the wrong day for anyone whose offset moves the instant across midnight. In Kuala Lumpur, 00:30 local time is still the previous day in UTC. This is the only function in the module that depends on the device's time zone, and it is meant to. It never changes its argument.

**`isDateKey(value)` (R2).** The gatekeeper for text that comes from storage. It returns `true` only for a string that matches `KEY_PATTERN` (`/^\d{4}-\d{2}-\d{2}$/`) and names a real day. The year must be 0001 or later, the month 01 to 12, and the day within that month under the leap-year rule. The pattern is anchored, has no flags and no nested quantifier, so a hostile string fails within its first characters and cannot cause backtracking. Without the `u` flag, `\d` matches only ASCII digits, so full-width digits fail (tested). The pattern also caps the year at 9999.

**`daysFromCivil` and `civilFromDays`.** These convert between a calendar date and a whole number of days since 1970-01-01. They are Howard Hinnant's `days_from_civil` and `civil_from_days`, as the comment names them, and the constants (719468, 146097, 153 and the rest) come from that algorithm. The comment on `daysFromCivil` gives the reason for not using `Date`. `Date.UTC` maps years 0 to 99 into the 1900s, and local `Date` maths turns a DST change into a 23 or 25 hour day. With integers there is no time of day and no time zone at all.

**`addDays(key, days)` (R3).** Parse, convert to a day count, add `days`, convert back, format. A negative `days` goes back. The result is the same in every time zone, because no `Date` is involved. This is the one primitive that every window, streak and heatmap function walks with. It trusts its input. `days` must be an integer and `key` must be a valid key. Every caller in the module passes integer offsets and keys built from `todayKey`.

**`weekdayIndex(key)` (R4, added by code review WR-04).** Returns 0 for Monday to 6 for Sunday. It takes the day count, adds `THURSDAY_INDEX` (3, because 1970-01-01 was a Thursday and Thursday is index 3 in a Monday-first week), and reduces modulo 7 twice so that days before 1970 still give 0 to 6. Weeks start on Monday everywhere in the app (spec Invariants). Before WR-04 the heatmap found Monday by looking for the label `"Mon"` inside the 7-day strip, which tied the heatmap to the strip's width and to a display string.

**The labels (R4).** `WEEKDAYS` and `MONTHS` hold the full English names. `namesOf(key)` returns `{ weekday, day, month }` with full names. `dayParts(key)` cuts both names to their first three letters (`ABBREVIATION_LENGTH`), which works because every English weekday and month abbreviates that way, so one table per kind is enough. `shortDate` gives `"Tue 6 Oct"` and `longDate` gives `"Thursday 8 October"`, both through `joinLabel`. The day number has no padding. There is no `Intl` and no `toLocale*`, so a German device still reads English.

### 3.3 `src/habits.js`, the habit rules

**Constants.** `MAX_HABITS` (12) and `MAX_NAME_LENGTH` (40) are exported. The private ones are `STRIP_DAYS` (7), `DAYS_PER_WEEK` (7), `HEATMAP_WEEKS` (12), `PREVIOUS_DAY` (-1) and `NEXT_DAY` (1). The two sevens are separate on purpose, and the comment above them says why. The strip's width is a design choice, while the week's length is a calendar fact. A 5-day strip would change `STRIP_DAYS` and leave the heatmap alone, which the code reviewer's mutant `strip-5` confirmed.

**`copyHabit(habit)`.** Returns `{ name, done: [...done] }`. It builds a fresh literal from the two known fields, so an extra key from stored data (`__proto__`, `constructor` or anything else) is never carried into new state. Every list operation uses it for the habits it does not change.

#### The week strip

**`weekWindow(todayKey)` (R5).** Seven keys, from `todayKey` minus 6 days to `todayKey`, oldest first. It is the one definition of the strip's span. `toggleDay` uses it as the editable range, `runContinues` reads its first day, and `src/view.js` builds and labels the beads from it. Change the strip here and all three follow.

#### Streaks

The two streak functions share two private helpers, so they count a run the same way.

**`streakDays(done)`.** `new Set(done.filter(isDateKey))`. The Set drops duplicates and gives constant-time lookups. The filter keeps only real days. On the app's data it removes nothing, because the decoder already rejected any saved state that held a bad key. It exists because of security finding SEC-01. Outside the valid range `addDays` can return a key it already returned, so a walk could loop forever, and many spellings of one far-out date could each start such a walk. Inside the valid range each day has one spelling and `addDays` never repeats a key, so every walk ends at the first day not in the set. The comment on `streakDays` is the one home of this reasoning. The spec's threat model and `BUILD.md` point to it.

**`runLength(days, from, step)`.** Counts consecutive keys in `days`, starting at `from` and stepping by `step` (1 or -1) with `addDays`. It stops at the first key that is not in the set. It has no bound of its own, and its comment says `days` must come from `streakDays` for that reason. A size bound used to sit here. Code review WR-15 showed it could never decide a result behind the filter, and it was removed.

**`currentStreak(done, todayKey)` (R6).** This is the rule users notice most. If today is ticked, count back from today. If not, count back from yesterday. So a streak does not break while today is still open. At 10 in the morning, before you tick today, yesterday's 5-day streak still shows 5. It drops to 0 only on the next day, and only if today was never ticked. Because the walk moves only backwards from today or yesterday, days after `todayKey` never count. With the sample on 2026-10-08, "Stretch 10 minutes" is not ticked today, so counting starts on 7 October and gives 3.

**`bestStreak(done)` (R7).** The longest run anywhere in the history, days after today included. It walks each run once. For every day whose previous day is absent (a run start), it measures forward with `runLength` and keeps the longest. Total work is linear in the number of days. An empty `done`, or one with no valid key, gives 0.

**`runContinues(done, todayKey)` (R8).** True when the strip's first day and the day before it are both ticked. The view writes it as the `data-run-continues` attribute and draws the thread running off the strip's left edge. It takes the first day from `weekWindow(todayKey)[0]` (code review WR-05 removed a second copy of that rule). It builds `new Set(done)` rather than using `streakDays`. That is harmless, because it only looks up two keys derived from a valid `todayKey`, but a reader comparing it with the streak functions may wonder why.

#### Ticking a day

**`toggledHabit(habit, dateKey)`.** Puts `done` into a Set, adds the key if it is absent or removes it if it is present, and returns `{ name, done: [...days].sort() }`. The Set removes duplicates and the default `.sort()` restores ascending order, which is calendar order for fixed-width keys. So the `Habit` invariant holds after any toggle, even when the input was unsorted.

**`toggleDay(habits, index, dateKey, todayKey)` (R9).** The rule "only the last 7 days can be changed" lives here, where the data changes, and not only in the screen. `editable` is `weekWindow(todayKey).includes(dateKey)`. The function maps the list. The habit at `index` is toggled when the day is editable, and every other habit is copied. A day outside the strip, or an index that is not a real position (3, -1, 0.5, `NaN`, the string `"0"`), matches nothing, so the result is a new array equal in content to the input. It never throws on a bad index and never mutates.

#### The heatmap

**`heatLevel(count, total)` (R11).** Maps the share of habits done on one day to a level from 0 to 4. It uses integer comparisons only, so a boundary such as 1 of 3 cannot flip on floating-point rounding.
- 0 when `count` or `total` is 0.
- 4 when every habit was done.
- 1 when `3 * count <= total`, up to a third.
- 2 when `3 * count <= 2 * total`, up to two thirds.
- 3 otherwise, more than two thirds but not all.

Both thirds are inclusive, as the golden screens show (1 of 3 is level 1, 2 of 3 is level 2). With the sample's three habits, level 3 never appears, because 2 of 3 is level 2 and 3 of 3 is level 4. The view turns the level into the CSS class `l0` to `l4` in `fillCell`.

**`columnMondays(todayKey)`.** The Monday that starts each of the 12 columns, oldest first. The current week's Monday is `todayKey` minus `weekdayIndex(todayKey)` days, and the first column starts 11 weeks before it.

**`calendarMonth(key)`.** The `"YYYY-MM"` prefix of a key, taken by slicing the first 7 characters. It relies on the fixed width.

**`doneCountsByDay(habits)`.** One pass over every habit's days, into a `Map` from key to the number of habits done that day. A habit counts once per day, because it iterates `new Set(habit.done)`. It is built once per call so the 84 cells do not each scan every habit. Nothing is kept between calls, so the "no caching" non-goal holds.

**`heatmapCells(habits, todayKey)` (R10).** 84 cells in column-major order, column 1 from Monday to Sunday, then column 2, and so on. Row 1 is Monday. Each cell is `{ key, column, row, today, future, count, total, level }`. `future` is `key > todayKey`, a text comparison that is safe because keys are fixed width, and an end-of-line comment says so. Future cells carry `count: null` and `level: null`, so the screen leaves them blank instead of drawing a 0 that never happened. `total` is the current number of habits, for every day including past days. That is the spec ("the share of the current habits done that day"), and it has a visible effect. Adding a habit makes every past day look lighter, and deleting one removes its history from the grid.

**`monthLabels(todayKey)` (R12).** Column 1 is labelled with its Monday's short month, and every later column is labelled when its Monday is in a different calendar month from the previous column's Monday. A month whose days appear only after the last Monday gets no label. For 2026-03-31 there is no "Apr", although 1 to 5 April sit in column 12. It compares `calendarMonth` prefixes rather than label strings (WR-04), and takes the label text from `dayParts(monday).month`.

#### Names and the list

**`longerThan(text, limit)`.** True when `text` has more than `limit` code points. It walks the string iterator and returns as soon as it reaches code point 41, so a name planted in storage at quota size costs no more than a short one. Before security finding SEC-02 the check was `Array.from(name).length`, which first copied the whole name into an array with one string per code point. The results are the same for every string.

**`validateName(raw, existingNames)` (R13).** Trims with `String.prototype.trim`, then checks in this order and returns the first failure.
1. Empty gives `{ ok: false, error: "empty" }`.
2. More than 40 code points gives `"too-long"`.
3. Equal to an existing name, with `toLowerCase()` on both sides, gives `"duplicate"`.

Otherwise it returns `{ ok: true, name }` with the trimmed name. The order is part of the rule (design RULINGS rule 3). A name of only spaces is "empty", and an over-long copy of an existing name is "too-long". Length counts Unicode code points (clarify gate CG-8). The book emoji U+1F4DA counts as 1 code point, where UTF-16 would count 2. A family emoji joined with zero-width joiners counts as several, because counting what a person sees as one character would need `Intl.Segmenter`, which the module may not use. The view's message still says "40 characters". A non-string `raw` throws a `TypeError`, and both callers pass strings.

**`addHabit(habits, raw)` (R14).** The limit comes first. At 12 or more habits it returns `{ ok: false, error: "limit" }` without looking at the name. Otherwise it returns the failure from `validateName` unchanged, or `{ ok: true, habits }` with copies of the old habits and `{ name, done: [] }` at the bottom. In the shipped page "limit" never arrives, because `src/app.js` disables the form at 12 (`setAddLimit`, as the comment on `rejectName` says).

**`deleteHabit(habits, index)` (R15).** Filters out the position equal to `index`, then copies the rest. An index that is not a position removes nothing.

### 3.4 Side paths, empty states and edge cases

- **Empty list.** `heatmapCells([], todayKey)` still returns 84 cells, with `count` 0, `total` 0 and `level` 0 up to today. `toggleDay([], ...)` and `deleteHabit([], 0)` return `[]`. `addHabit([], " Run ")` returns one habit named "Run".
- **No ticks.** `currentStreak` and `bestStreak` give 0. The view then shows "No streak yet" and removes the "Best" text (`src/view.js` `syncStreak`).
- **Order and duplicates.** Every streak and heatmap function accepts `done` in any order and with duplicates. `toggleDay` hands it back sorted and unique.
- **Days after today.** They can exist if the device clock or time zone moved back. They never count for `currentStreak` and show as future cells in the heatmap, but they do count for `bestStreak`, as R7 says.
- **Midnight and DST.** The module has no time of day. A day changes only when the app passes a new `todayKey`. A DST change cannot skip or repeat a day, because `addDays` works in integer days. The tests show this under `America/New_York` across both 2026 changes.
- **Keys outside the valid range.** The app's decoder never lets one through. If one did, `streakDays` drops it, so streaks count only valid days and every walk ends. Three quirks made such keys dangerous before that filter. `Number()` ignores white space, so one far-out date has thousands of spellings. Below year 0001, `pad` writes `"00-1"`, which reads back as a different date, and the walk back from 0000-01-03 forms a 12-day cycle. Near 2^53 days, floating-point rounding makes `addDays(key, 1)` return the same key. The tests that use `streakInChild` cover all three.
- **Year 10000.** `localDateKey` would write a five-digit year, which `isDateKey` rejects. The README lists the effect as a known limit. The app would save a day it cannot read back, and the next load would reset every habit.

## 4. The data

| Shape | Defined in | What it is |
|---|---|---|
| `DateKey` | `src/dates.js` typedef | `"YYYY-MM-DD"`, a local calendar day. Fixed width, so text order is calendar order |
| `Habit` | `src/habits.js` typedef | `{ name, done }`. The name is trimmed, 1 to 40 code points, unique ignoring case. `done` is ascending, without duplicates, valid keys only |
| `HeatCell` | `src/habits.js` typedef | `{ key, column, row, today, future, count, total, level }`, with `count` and `level` null on future days |
| `MonthLabel` | `src/habits.js` typedef | `{ column, month }`, the month as a three-letter name |
| `NameCheck` | `src/habits.js` typedef | `{ ok: true, name }`, or `{ ok: false, error }` with error `empty`, `too-long` or `duplicate` |
| `AddResult` | `src/habits.js` typedef | `{ ok: true, habits }`, or `{ ok: false, error }` with `limit` added to the three name errors |

Inside the module two more shapes move. `parseKey` returns `{ year, month, day }` as numbers, and `daysFromCivil` returns a plain integer day count. The streak functions work on a `Set` of keys and the heatmap on a `Map` from key to count. All of them are built per call and dropped.

**State.** None. No module-level variable ever changes. Every function returns new arrays and objects, and none writes to its arguments. `tests/purity.test.js` proves this by calling every export with frozen inputs.

**Persistence.** None in this module. The app saves the `Habit[]` array as it is, inside `{ "version": 1, "habits": [...] }` under the key `streaks.state` (`src/storage.js`). That is why `copyHabit` and `toggledHabit` keep exactly `name` and `done`, and why the decoder uses `validateName` and `isDateKey` from here.

## 5. Boundaries

- **Depends on.** Nothing outside its two files. No browser API, no `Intl`, no network, no storage, no timers.
- **Depended on by.** `src/app.js`, `src/view.js` and `src/storage.js`, as listed in section 2. The view also relies on facts a signature does not show. The strip has exactly 7 days, the heatmap has exactly 84 cells in column-major order to fill the CSS grid, and the levels are 0 to 4 to match the stylesheet's `l0` to `l4` classes.
- **External.** One thing. `localDateKey` reads the host's time zone through the local `Date` getters. The clock read itself (`new Date()`) sits in `src/app.js` `readToday`, outside the module. Browser tests move time with Playwright's clock, never with a hook in the app.
- **Test data.** `docs/design/sample-history.json` is golden data, read-only, imported by the tests with `with { type: "json" }`. No test writes under `docs/`.

## 6. How the tests prove it

I counted 66 `test()` calls across the four module files (15 in `tests/dates.test.js`, 39 in `tests/habits.test.js`, 7 in `tests/sample-history.test.js`, 5 in `tests/purity.test.js`). I did not run them. The QA finder recorded 66 of 66 passing at `7b79ea1` (`docs/modules/habit-logic/findings/qa.md`). The v1.0.0 regression recorded 99 unit tests passing, which is these 66 plus the 33 in `tests/storage.test.js` (`docs/regression/REGRESSION.md`). Every title starts with its `@R#` tag, and that is how the QA finder maps results to requirements.

**`tests/dates.test.js`** (R1 to R4).
- `inZone` sets `process.env.TZ` around a test body. The first test proves the zone switch takes effect (offsets of -480, 240 and 300 minutes), so the zone cases cannot pass by accident.
- R1 rows in Kuala Lumpur and New York, and one case where the UTC date and the local date differ.
- R2's table, then every year, month and day 0 to 32 from 1900 to 2100 against `Date.UTC`, then strings of a million characters rejected in under a second.
- R3's table in both zones, century and leap edges, then every day from 1900 to 2100 stepped by +1, -1 and +400 in both zones against UTC millisecond maths.
- R4's label rows, the `weekdayIndex` rows, and every day from 1900 to 2100 against `getUTCDay`.
- `@R4 labels do not follow the runtime locale` starts a child Node process that makes German the default of `Intl.DateTimeFormat` and of the `Date` `toLocale*` methods. It proves the default is German ("Donnerstag") and only then checks that the labels are English. On Windows, ICU ignores `LANG`, so the first version of this test could not fail (code review WR-01).

**`tests/habits.test.js`** (R5 to R15).
- Table tests for every qa.md scenario, plus streaks across a month, a year, a leap day and both DST changes.
- `toggleDay` tests check that the input is unchanged, that every habit in the result is a new object, that `done` stays ascending and unique, and that bad indexes (3, -1, 0.5, `NaN`, `undefined`) change nothing.
- The heatmap test checks all 84 cells (column, row, key and weekday) for five different todays. A second test checks `monthLabels` against the grid for five start days.
- Name tests cover the order of checks, code points (40 book emoji are 80 UTF-16 units and pass), Unicode white space, and `iteratorSteps`, which counts string-iterator steps to prove that `longerThan` stops at 41 on a 5,000,000-unit name.
- `streakInChild` runs a streak call in a child process that is killed at 5 seconds, so a walk that never ends fails its test instead of hanging the suite. Four tests use it, with the stuck far-out keys, the cycle below year 0001, 20,000 spellings of one date, and a history that leaves the valid range.

**`tests/sample-history.test.js`** (the golden values). The sample's strips, streaks and run flags on 2026-10-08 and 2026-10-09, its best runs, all 81 heatmap levels against the file's `heatmapLevels` (3 at level 0, 30 at 1, 28 at 2, none at 3, 20 at 4), and the month axis Jul 1, Aug 3, Sep 8, Oct 12.

**`tests/purity.test.js`** (R16).
- `CLOCK_AND_RANDOM_READS` (`Date.now`, `new Date` with no argument, `Date` called as a function, `Temporal.Now`, `performance.now`, `Math.random`) must not match the file text, comments included, or the code. `BANNED_IN_CODE` (DOM and global objects, storage, network, dynamic import, `eval` and `Function`, timers, `crypto`, `Intl` and `toLocale*`) must not match the code once `withoutComments` has removed the comments.
- An import rule and an exact list of exports.
- Every exported function is called with deep-frozen inputs. The test fails when an export has no entry in `callsWith`, when a call throws, or when a result holds a frozen object (an input handed back). The `Date` given to `localDateKey` is checked by `getTime()` before and after, because a freeze does not stop a `Date`'s setters.

**`tests/storage.test.js`** belongs to the app module. It reaches habit-logic only through `decodeState`. Rows such as "an untrimmed name", "41 characters", "an impossible date" and "a duplicate name that is not next to its twin" exercise `validateName` and `isDateKey` as the decoder uses them.

## 7. Quality read

Judged against constitution §Engineering principles and the comment rule in §Documentation ownership. These are opinions for the owner, not gate findings. The module came through 16 code-review warnings (WR-01 to WR-16) and 4 security findings (SEC-01 to SEC-04), all resolved, and it shows. What follows is what is left. **Result: 0 WORTH FIXING, 14 NOTE.**

| Area | Symbol | What | Why it matters | Weight |
|---|---|---|---|---|
| duplication | `toggledHabit`, and `readHabit` in `src/storage.js` | Both rebuild `done` as `[...new Set(x)].sort()`. | The `Habit` invariant (ascending, no duplicates) has two homes in two modules, while `docs/modules/app/spec.md` says the app "re-implements none of these rules". A change to the rule must be made twice. It is one line, and the Contracts offer no normalise export to call instead. | NOTE |
| coupling | `MAX_NAME_LENGTH`, `MAX_HABITS` | `src/view.js` writes both limits as text, "40 characters" in `NAME_ERRORS` and "12 habits" in `LIMIT_NOTE`. No shipped file imports `MAX_NAME_LENGTH`. | Change a constant and the user copy goes stale with no test going red. The copy is fixed by the golden design, so this is a drift risk, not a bug today. | NOTE |
| dead code | exports `addDays`, `weekdayIndex`, `heatLevel`, `MAX_NAME_LENGTH` | Exported and in the Contracts, used inside the module, imported directly only by tests. | Not dead code. It is public surface with no shipped caller, kept stable for the tests alone. Worth knowing before a refactor. | NOTE |
| over-engineering | `streakDays` | Filters `done` with `isDateKey` on every streak call. | In the shipped app it never removes anything, because `readHabit` rejects any saved state with a bad key and `toggleDay` only adds strip days. The security rounds measured streaks about 30 to 70 percent slower on a quota-sized history because of it, and it carries a six-line comment. It was an orchestrator ruling (SEC-01) to protect future callers. Defensible, but it defends a path the app already closes. | NOTE |
| over-engineering | `daysFromCivil`, `civilFromDays` | About 20 lines of published integer calendar maths with bare constants, where `Date.UTC` and the `getUTC*` getters would take a handful. | The stated reason (years 0 to 99, and no `Date` at all) covers dates the app never meets. The code is correct, and the code review checked `addDays` and `weekdayIndex` over every day from 0001 to 9999, so the only cost is that a reader must trust the cited algorithm. | NOTE |
| fragile pattern (unchecked input) | `addDays`, `parseKey` | No input guard. A fractional or string `days`, or a key that fails `isDateKey`, returns a malformed key with no error (code-review probe `probe-edges.txt`). | Every current caller passes integer offsets and keys built from a valid `todayKey`, and the app does not import `addDays`. A future caller that passes a DOM attribute or a float would get silent garbage. | NOTE |
| fragile pattern (time and date) | `localDateKey` | From year 10000, `pad` writes five digits, against R1's "year as 4 digits", and `isDateKey` rejects the key. | Needs the device clock set to year 10000. The README lists the effect as an accepted limit (the next load resets every habit). | NOTE |
| fragile pattern (unchecked input) | `validateName` | The duplicate check is `toLowerCase()` only, and `trim` does not remove U+200B. NFC and NFD forms, zero-width variants and look-alike letters pass as different names, and a name made only of U+200B is not "empty". | Matches the spec exactly, and the security finder filed it as a product decision, not a defect. A user can create two rows that look the same. | NOTE |
| naming | `THURSDAY_INDEX` | Reads as "the index of Thursday". Its role is the weekday of day 0 (1970-01-01). | The comment on `weekdayIndex` explains it. A name such as `EPOCH_WEEKDAY_INDEX` would carry the reason by itself. | NOTE |
| comments | the `src/dates.js` module header | Says the file is "free of clocks, time zones and locales" and that its input is date keys. | `localDateKey` takes a `Date` and depends on the device time zone through the local getters, by design (R1). The header overstates, and it is the first thing a reader sees. | NOTE |
| tests | `@R7 the best-run walk ends on keys outside the valid range, where the next day repeats itself` and `@R6 the current-run walk ends on the cycle below year 0001` | Written for the removed size bound. They assert `best <= 2` and `current <= 12`, where the code now returns 0. | They prove only that the walk ends. `@R6 @R7 keys that fail isDateKey do not count, so a streak counts only valid days` pins exact values. These two are loose and largely redundant. | NOTE |
| tests | `withoutComments` and `STRING_OR_COMMENT` in `tests/purity.test.js` | The comment stripper that feeds `BANNED_IN_CODE` and the import rule has no test of its own. | It was wrong once already (WR-11, a `//` inside a string hid the code after it). A revert would stay green on the real sources. The solver listed it as a residual. A two-line self-check would pin it. | NOTE |
| tests | `@R1 month and day are zero padded and the year has 4 digits` | The title promises a 4-digit year, but both rows are in 2026. | A `localDateKey` that stopped padding the year would pass it. `addDays("0001-01-01", 1)` in `@R3 century and year edges` covers the shared `formatKey`, not `localDateKey` alone. Real devices never show a year below 1000, so the gap is mostly in the title. | NOTE |
| tests | `@R2 a long hostile string is rejected quickly`, `@R13 a very long name is rejected without hanging` | Wall-clock asserts, `performance.now()` under 1000 ms. | Timing asserts can flake on a slow or busy machine. The margin is wide here, and `@R13 the length check reads at most 41 code points, so a huge stored name costs no more than a short one` already proves the name case by step count. | NOTE |

Clean areas, one line each.
- **Dead code.** Every private helper and constant in both files has a caller (checked by grep). The one unreachable guard, the size bound in `runLength`, was already removed.
- **Code with no R#.** None. `streakDays` traces to the dated notes under R6 and R7, `longerThan` to the note under R13, `copyHabit` to R9, R14, R15 and the Object integrity row, `doneCountsByDay` to R10 and `calendarMonth` to R12.
- **Risky patterns.** One regular expression on stored data (`KEY_PATTERN`), anchored and linear. No `innerHTML`, `eval`, `Function`, `Object.assign` or object spread of stored data. No floating-point maths in `heatLevel` and no millisecond date arithmetic anywhere.
- **Comments.** Apart from the module header above, every comment I read is true and explains why, not what. The longest, on `streakDays`, is six lines and load-bearing. No `file:line` citations.
- **Mutation.** Every export returns new values, proved by the frozen-input test and by the security audit's write-trapping proxies.

## 8. How to change it safely

1. **Keep the day key a fixed-width string, keep arithmetic in whole days, and keep the clock out.** Sorting (`toggledHabit`), the `future` flag (`heatmapCells`) and `calendarMonth` all compare or slice keys as text. Use `addDays` for every step. Adding 86,400,000 ms to a local time brings back the DST bug the spec names. Pass `todayKey` in, and never read the clock or use `Intl` here. `tests/purity.test.js` catches the usual spellings, but it is a text denylist, and an alias such as `Reflect.construct(Date, [])` passes it (spec R16 accepts that and leaves it to review).
2. **The view depends on more than the signatures.** The strip span comes from `weekWindow` alone, so change `STRIP_DAYS` and `toggleDay`, `runContinues` and the view follow. The heatmap must stay 84 cells in column-major order with levels 0 to 4, or the CSS grid and the `l0` to `l4` classes break. Adding or removing an export also means updating the exact list and the `callsWith` table in `tests/purity.test.js`, or that test fails.
3. **Read the spec's dated notes before trusting its first sentence.** `docs/modules/habit-logic/spec.md` carries each rule as its original text plus "Changed 2026-10-09" notes and struck sentences, and the note wins. For example, R6 and R7 now ignore keys that fail `isDateKey`, and the `Array.from` expression in R13 states the rule, not how the code counts. There is no module README. The root `README.md` has four bullets on habit-logic under "How it is built", and the reasoning lives in the source comments.
