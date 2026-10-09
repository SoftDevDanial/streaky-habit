---
module: habit-logic
kind: code-review
status: issues_found
counts: { blocker: 0, warning: 10 }
---
# Code review, habit-logic

> Written by the code-review finder (read-only), 2026-10-09. Scope is `git diff 8c7b965..HEAD` (commits `6296a9d`, `d26cbcc`, `56ab40e`, `a25431f`, `eaf8f9f`, `09c5047`), which covers `src/dates.js`, `src/habits.js`, the four test files and `BUILD.md`. Judged against `spec.md` (R1 to R16, Contracts, Non-goals), `qa.md`, `docs/constitution.md` and `CLAUDE.md`.

## Verdict

**PASS with warnings. 0 BLOCKER, 10 WARNING.** The logic is correct. No hallucinated code, no non-goal built, no contract drift. Every warning is a test control that cannot fail, a false or duplicated claim in a comment or document, or a coupling smell.

## Evidence

All files named here are in `docs/modules/habit-logic/qa/code-review/20261009T112920/`.

- `node --test "tests/**/*.test.js"` from the project root, Node v24.11.1 on win32, gives 60 tests, 60 pass, 0 fail, 0 skipped, exit 0, about 0.45 s, nothing on stderr (`full-run.txt`). Per file 14, 34, 7 and 5, as BUILD.md records.
- Each of the five code commits, extracted with `git archive` and run alone, is green with 14, 28, 36, 48 and 60 tests. BUILD.md's "every commit was made with the full suite green" holds (`per-commit-runs.txt`).
- Differential check against independent UTC-millisecond reference implementations of `currentStreak`, `bestStreak`, `runContinues`, `heatmapCells` (every field of every cell), `monthLabels` and `heatLevel`. It covers every todayKey from 2023-01-01 to 2030-12-31 with seeded random histories of 1 to 12 habits, under TZ `Asia/Kuala_Lumpur`, `America/New_York` and `Pacific/Apia`. Result is 2922 days per zone and 0 mismatches (`probe-differential.mjs`, `probe-differential.txt`). Together with the builder's 1900 to 2100 sweeps of `isDateKey`, `addDays` and weekdays, the date arithmetic across months, years, leap days and DST changes is sound.
- Mutation of inputs was read by hand for every export and is confirmed by the frozen-input test for every array and object argument. The one gap is the Date argument (WR-02).
- Edge probes (`probe-edges.txt`) found nothing reachable. `addDays` returns a malformed key for a string or fractional `days`, but its only callers are inside `habits.js` with integer constants, and `app` does not import it (app/spec.md, "Uses from habit-logic").
- The evidence folder holds two deliberate mutants, `mutant-locale-dates.mjs` and `mirror-localDateKey-mutates/src/dates.js`. A repo-wide grep for `toLocale` or `setHours` will hit them. They are review evidence, not shipped code, and the CLAUDE.md test glob (`tests/**`) does not reach them.

## Reverse audit (every non-trivial symbol to an R#)

| Symbol | R# |
|---|---|
| `localDateKey` | R1 |
| `isDateKey`, `KEY_PATTERN`, `isLeapYear`, `daysInMonth`, `DAYS_IN_MONTH`, `parseKey` | R2 |
| `addDays`, `daysFromCivil`, `civilFromDays`, `formatKey`, `pad` | R3 and the Invariants (calendar arithmetic) |
| `dayParts`, `shortDate`, `longDate`, `namesOf`, `joinLabel`, `WEEKDAYS`, `MONTHS`, `ABBREVIATION_LENGTH`, `THURSDAY_INDEX` | R4 |
| `weekWindow` | R5, R9 |
| `currentStreak`, `bestStreak`, `runLength` | R6, R7 |
| `runContinues` | R8 |
| `toggleDay`, `toggledHabit`, `copyHabit` | R9, R14, R15, Threat model (object integrity) |
| `heatmapCells`, `columnMondays`, `doneCountsByDay` | R10 |
| `heatLevel` | R11 |
| `monthLabels` | R12 |
| `validateName`, `MAX_NAME_LENGTH` | R13 |
| `addHabit`, `MAX_HABITS` | R14 |
| `deleteHabit` | R15 |

No symbol maps to no R#. The export lists equal the Contracts exactly, and `purity.test.js` ("only the contracted names are exported") guards that. No non-goal was built. `doneCountsByDay` is a per-call precomputation, not a cache kept between calls, so the "no caching or memoisation" non-goal holds. Every qa.md scenario row has a matching assertion, and every `test()` title starts with its `@R` tag.

## BLOCKER

None.

## WARNING

### WR-01: The R4 locale test cannot fail on the build platform   (control that cannot fail)
- **File:** `tests/dates.test.js:212` (test "@R4 labels do not follow the runtime locale"), its comment at `tests/dates.test.js:213`, `BUILD.md:31`, `qa.md:126`
- **Issue:** On this Windows machine, where the module was built and tested, Node's ICU ignores `LANG` and `LC_ALL`. A child started with `LANG=de_DE.UTF-8 LC_ALL=de_DE.UTF-8` still resolves its default locale to `en-MY`. A mutant whose `longDate` and `shortDate` call `toLocaleDateString(undefined, ...)` returns "Thursday 8 October" and "Tue 6 Oct" in that child, so the test's assertion passes on code that a German device renders as "Donnerstag" (`probe-locale-test-vacuous.txt`). The qa.md Given ("the process environment has LANG de_DE.UTF-8") is set but never takes effect, so the scenario reports PASS without having run. BUILD.md:31 and the comment at :213 say the child process is what makes the check real. That holds on Linux and is false here. Today the real guard against this risk is the R16 source scan for `Intl` and `toLocale`. The zone-switch test in the same file ("@R1 @R3 the zone switch is real") already shows the right pattern, which is to assert the precondition before trusting the environment.
- **Fix:** Make the child prove the precondition, and report a skip rather than a pass when the platform cannot provide it. In the child program, also emit `new Date(2026, 9, 8).toLocaleDateString(undefined, { weekday: "long" })`, then in the test (taking `t`):
  ```js
  const [long, short, probe] = JSON.parse(output);
  if (probe !== "Donnerstag") return t.skip(`runtime ignores LANG (default weekday "${probe}")`);
  assert.deepEqual([long, short], ["Thursday 8 October", "Tue 6 Oct"]);
  ```
  To make it run on every platform instead, give the child a `--import` preload that wraps `Intl.DateTimeFormat` and `Date.prototype.toLocale*String` so their default locale is `de-DE`, and assert that default before importing `dates.js`. For the orchestrator, add a matching precondition line to qa.md:126 ("And the child's default locale resolves to German") and correct BUILD.md:31.

### WR-02: The frozen-input check cannot catch a write to the Date argument of `localDateKey`   (control that cannot fail, spec claim false)
- **File:** `tests/purity.test.js:77` (the `localDateKey` entry of `callsWith`), `spec.md:115` (R16), `qa.md:404`
- **Issue:** `Object.freeze` does not protect a Date's internal time value. On a frozen Date, `setDate`, `setHours` and the other setters succeed silently in strict mode (`probe-freeze-and-spread.txt`). A mirror whose `localDateKey` starts with `date.setHours(0, 0, 0, 0)` passes all 5 purity tests and the full suite, 60 of 60 (`probe-localDateKey-mutates.txt`, `probe-localDateKey-mutates-full-suite.txt`). Nothing in the suite would go red if `localDateKey` changed the caller's Date. The current code does not write to it (read by hand), so behaviour is correct, but R16's "no exported function changes its arguments" is unguarded for this export. The spec sentence "deep-frozen inputs, which throw on any write in strict-mode ES modules" is false for a Date, and the test was built to it.
- **Fix:** Check the Date's value before and after the call instead of trusting the freeze:
  ```js
  localDateKey: () => {
    const date = new Date(2026, 9, 8, 12);
    const before = date.getTime();
    const key = dates.localDateKey(date);
    assert.equal(date.getTime(), before, "localDateKey left its Date unchanged");
    return key;
  },
  ```
  For the orchestrator, correct spec.md:115 and qa.md:404 to say frozen inputs for arrays and objects, plus a before-and-after value check for the Date of `localDateKey`, whose internal time a freeze does not protect.

### WR-03: `copyHabit`'s comment gives a false reason, copied from the spec's threat model   (doc rot, false claim)
- **File:** `src/habits.js:30`, `spec.md:193` (Threat model, row "Object integrity"), `BUILD.md:41`
- **Issue:** The comment says habits are "never spread, so a key from stored data cannot reach the prototype". Object spread defines own properties and never calls the `__proto__` setter. `{ ...JSON.parse('{"__proto__":{"polluted":true}}') }` keeps `Object.prototype` as its prototype and only carries an own key named `__proto__` (`probe-freeze-and-spread.txt`). It is `Object.assign` that runs the setter and swaps the target's prototype. The code is right, and rebuilding from the two known fields is a good choice. Its real effect is that no extra key from stored data (`__proto__`, `constructor` or anything else) travels into new state. The false reason came from spec.md:193, which groups spread with `Object.assign`, and BUILD.md:41 repeats it.
- **Fix:** Reword the comment to the true reason, for example `/** Rebuilt from the two known fields, so no extra key from stored data is carried into new state. */`. For the orchestrator, correct the spec.md:193 mitigation, for example "`Object.assign` runs the `__proto__` setter and spread carries unknown keys along. Both are avoided by building `{ name, done }` literals."

### WR-04: The heatmap's week logic depends on the strip's width and on a display label   (coupling, false DRY)
- **File:** `src/habits.js:24` (`WEEK_LENGTH`), `src/habits.js:26` (`MONDAY = "Mon"`), `src/habits.js:135` (`columnMondays`), `src/habits.js:187` (`monthLabels`)
- **Issue:** One constant, `WEEK_LENGTH`, carries two facts that change for different reasons. One is the strip's width (R5, a design choice of 7 cells). The other is the number of days in a heatmap column (R10, a calendar fact). `columnMondays` then finds the current Monday by searching the strip (`weekWindow(todayKey)`) for the day whose display label is "Mon". If the design changed the strip to 5 cells, every heatmap column would also shrink to 5 rows, and `columnMondays` would find no Monday on Saturdays and Sundays, so `heatmapCells` would throw a TypeError inside `addDays`. A change to the label table would break the heatmap the same way. `monthLabels` also compares month labels rather than month numbers. This is constitution refinement (8), look-alike values that change for different reasons stay separate. BUILD.md:27 names the root cause correctly (the dates.js Contracts give no weekday index), and the builder was right not to change the Contracts alone. That makes it a spec gap for the orchestrator to rule on, not a permanent workaround.
- **Fix:** Without a contract change, split the constant into `STRIP_DAYS = 7` (for `weekWindow` and `runContinues`) and `DAYS_PER_WEEK = 7` (for `heatmapCells` and `columnMondays`), and search for the Monday in `Array.from({ length: DAYS_PER_WEEK }, (_, back) => addDays(todayKey, -back))` rather than in the strip. Then raise a clarify-gate item to add a weekday index to the dates.js Contracts (for example `weekdayIndex(key)` giving 0 to 6 with Monday as 0, from the same `daysFromCivil` that `namesOf` already uses), so `columnMondays` and `monthLabels` stop comparing display strings.

### WR-05: `runContinues` derives the strip's first day a second time   (DRY)
- **File:** `src/habits.js:88`, against the `weekWindow` comment at `src/habits.js:43`
- **Issue:** R8 defines the run flag from "the first day of the week window". `runContinues` re-derives that day as `addDays(todayKey, 1 - WEEK_LENGTH)` instead of reading it from `weekWindow`. The `weekWindow` comment says it exists "so the strip and the editable range are one definition", but the run flag is a third consumer of the same edge and bypasses that definition. If the strip's span changed, `weekWindow` and `toggleDay` would move and `runContinues` would not. Unlike WR-04, these change for the same reason, so this is true duplication.
- **Fix:** `const firstDay = weekWindow(todayKey)[0];` in `runContinues`.

### WR-06: The same reasoning is written in a source or test comment and again in BUILD.md   (DRY across the code/docs boundary)
- **File:** `src/habits.js:131` with `BUILD.md:27` (finding the Monday in the strip), `src/dates.js:43` with `BUILD.md:28` (`Date.UTC` maps years 0 to 99 into the 1900s), `tests/dates.test.js:213` with `BUILD.md:31` (ICU reads the locale at start-up), `src/habits.js:30` with `BUILD.md:41` (literal rebuild against prototype pollution)
- **Issue:** The constitution (Documentation ownership) asks for one home, referenced from the other. Two of these four pairs already carry a false claim (WR-01, WR-03), so a fix to one copy will leave the other stale.
- **Fix:** Keep the reasoning in the source comment, next to the code it explains. In BUILD.md keep only the decision and point to the symbol, for example "Monday detection, see the comment on `columnMondays`".

### WR-07: The spec says `app`'s live gate uses every export, and it does not   (spec claim false)
- **File:** `spec.md:214` (Roadmap, "Done when"), against `docs/modules/app/spec.md:156` ("Uses from habit-logic")
- **Issue:** habit-logic exports 19 names and the app spec lists 16 of them. `addDays`, `heatLevel` and `MAX_NAME_LENGTH` are not consumed by `app`. They run only inside `toggleDay`, `heatmapCells` and `validateName`, so the cold-boot gate proves them only through those functions. The constitution holds the orchestrator's own prose to the same standard as code, and a false "every export" is the kind of claim that gets copied into a later gate. (Side note for the app review, not this module. app/spec.md:92 and :273 spell the limit as "40" in user copy while `MAX_NAME_LENGTH` exists.)
- **Fix:** For the orchestrator, reword spec.md:214 to "uses every export except `addDays`, `heatLevel` and `MAX_NAME_LENGTH`, which it reaches through `toggleDay`, `heatmapCells` and `validateName`", or drop the claim.

### WR-08: BUILD.md's list of internal symbols is incomplete, and it is marked for the README   (doc accuracy)
- **File:** `BUILD.md:47`
- **Issue:** The "Internal (not exported)" line, under the heading "for the README reconcile", leaves out `pad`, `isLeapYear`, `daysInMonth` and `joinLabel` in `dates.js`. A README built from it is wrong on day one, and an enumerated list of private helpers rots on every refactor.
- **Fix:** Drop the internal list from BUILD.md and keep it out of the README. The exports line and the source are the record. If a list must stay, make it complete and limit it to function names.

### WR-09: Three comments state things the code or the test setup contradicts   (doc rot)
- **File:** `src/habits.js:2`, `src/habits.js:92`, `tests/sample-history.test.js:14`
- **Issue:** The `habits.js` header ("Week strip, streak and habit-list rules.") leaves out the heatmap and the month axis (R10 to R12), a third of the file. The `toggledHabit` comment says toggling "through a Set" makes the array come out ascending, but the Set only removes duplicates and `.sort()` gives the order. The sample-history comment says the clone stops this file from altering "what other files import". Each test file runs in its own process (spec.md:170), so no other file shares this import. The clone only protects later tests in this file.
- **Fix:** Header, "Week strip, streaks, heatmap and habit-list rules." `toggledHabit`, "The Set drops duplicates and the sort restores ascending order, so the stored array keeps the Habit invariant." sample-history, "Tests use a clone so no test can change the sample a later test reads."

### WR-10: Three test details hide or overstate what is checked   (test quality)
- **File:** `tests/habits.test.js:376`, `tests/habits.test.js:377`, `tests/sample-history.test.js:21`, `tests/sample-history.test.js:49`
- **Issue:** (a) Line 377 types U+00A0, U+2003 and U+FEFF as raw invisible characters. A reader sees plain spaces (this review's first read of the file did), so the case cannot be checked by eye. The title at :376 claims "all kinds of white space", but four kinds are tested. (b) The test at sample-history.test.js:21 is tagged `@R2` but checks the golden fixture. `habit.done.every(isDateKey)` also passes with `isDateKey = () => true`, so it adds nothing to R2, yet the QA finder will count it toward R2. (c) The title at sample-history.test.js:49 names "Fri 2 Oct" and "Thu 8 Oct", but the body asserts only the two keys, not the weekdays.
- **Fix:** (a) Write `"  Drink water﻿ "` and title it "trim removes no-break, em-space and BOM white space". (b) Retag it under the R numbers whose goldens depend on the fixture (R5 to R12) and say "fixture check" in the title after the tags. (c) Add `assert.deepEqual([shortDate(days[0]), shortDate(days[6])], ["Fri 2 Oct", "Thu 8 Oct"])`, or drop the weekdays from the title.

## Processes

PROCESSES: none alive. Every command ran in the foreground with a `timeout` cap and exited, including the suite runs, the per-commit runs, the probes and the `execFileSync` children they started. `tasklist /FI "IMAGENAME eq node.exe"` after the last run listed no node process.

## Solver (2026-10-09)

> Written by the dev solver, under the orchestrator rulings of 2026-10-09 (ORCH). The reviewer's text above and its evidence folder are unchanged. Solver evidence is in `docs/modules/habit-logic/qa/solver/20261009T114157/`. Phase skills: the registry assigns none to a non-UI fix batch, so none were loaded.

**Result: 10 of 10 RESOLVED, 0 STILL-OPEN.**

- Final run, `node --test "tests/**/*.test.js"` from the project root, Node v24.11.1 on win32: 61 tests, 61 pass, 0 fail, 0 skipped, exit 0 (`full-run.txt`). Per file: `dates.test.js` 15, `habits.test.js` 34, `sample-history.test.js` 7, `purity.test.js` 5. The one added test is the `weekdayIndex` scenario (WR-04).
- Each solver commit was extracted with `git archive` (src, tests and the sample) and run alone. All are green (`per-commit-runs.txt`).
- Mutation proofs use `mutate.mjs` and `mutants.mjs` in the evidence folder. Each mutant runs in its own mirror under `mirrors/<name>/`. Where a control is named, the same mutant also runs against the tests before the fix, to show that the old test stayed green on it. The mirrors hold deliberate mutants that use `toLocaleDateString`, `Intl` and `setHours`, so a repo-wide grep will hit them. They sit outside `src/` and outside the test glob.

| Finding | Status | Commit | How it was verified |
|---|---|---|---|
| WR-01 | RESOLVED | `73fb59b` | The child now makes `de-DE` the default of `Intl.DateTimeFormat` and of Date's `toLocale*` methods before `dates.js` loads. It keeps `LANG` and `LC_ALL` for POSIX, and the test asserts the precondition (both probes give "Donnerstag") before the labels. A `toLocaleDateString(undefined, ...)` mutant turns the test red on win32, with "Donnerstag 8 Oktober" and "Di 6 Okt". The same mutant against the 09c5047 tests stays green, which reproduces the finding. A mutant that builds an `Intl.DateTimeFormat` when the module loads is also red (`wr01-locale-mutants.txt`, `wr01-locale-mutant-diff.txt`). The R16 source scan stays as a second guard. The qa.md scenario (Given and a new precondition line) and BUILD.md are corrected. |
| WR-02 | RESOLVED | `7257e40` | The `localDateKey` entry of `callsWith` compares `getTime()` before and after the call. A mutant that calls `setHours(0, 0, 0, 0)` on its argument turns the purity test red, and the 73fb59b tests stay green on it (`wr02-localDateKey-mutants.txt`). The spec R16 note and the qa.md purity scenario are corrected with dated notes. |
| WR-03 | RESOLVED | `61761c6` | The `copyHabit` comment now gives the true reason. The spec threat-model row has a dated correction, and BUILD.md points to `copyHabit`. A probe confirms that spread keeps `Object.prototype` and carries the unknown keys, `Object.assign` swaps the prototype, and the literal carries only `name` and `done` (`wr03-spread-vs-assign.txt`). |
| WR-04 | RESOLVED | `bbd7666` | `dates.js` exports `weekdayIndex(key)` (Monday 0 to Sunday 6). `columnMondays` steps back by it. `STRIP_DAYS` and `DAYS_PER_WEEK` replace `WEEK_LENGTH`, and `MONDAY` is gone. `monthLabels` compares the keys' calendar month (`calendarMonth`, the "YYYY-MM" prefix) instead of labels, because the finding's issue text names it too. With a 5-day strip, the code before the fix also turns the R10 and R12 tests red. After the fix only the R5, R8 and R9 tests go red, and R10 to R12 stay green (`wr04-strip-width-decoupling.txt`). The reviewer's differential probe, run read-only against the fixed code, finds 0 mismatches in Asia/Kuala_Lumpur, America/New_York and Pacific/Apia (`wr04-differential.txt`). The spec Contracts row and an R4 note, a qa.md scenario, the exact-export test, the frozen-input call table and BUILD.md are updated. |
| WR-05 | RESOLVED | `6275858` | `runContinues` reads `weekWindow(todayKey)[0]`. The differential probe finds 0 mismatches in all three zones (`wr05-differential.txt`). The WR-04 strip mutant shows the run-flag test moving with the strip. The `weekWindow` comment now states the rule instead of listing two of its three users. |
| WR-06 | RESOLVED | `bbd7666`, `c81ac1b`, `73fb59b`, `61761c6` | Each of the four pairs now has one home, the source or test comment, and BUILD.md keeps only the decision and points to the symbol. The pairs are `columnMondays` (bbd7666), `daysFromCivil` (c81ac1b), the test `@R4 labels do not follow the runtime locale` (73fb59b) and `copyHabit` (61761c6). Verified by reading BUILD.md against each comment. |
| WR-07 | RESOLVED | `c621137` | spec.md "Done when" has a dated correction that points to the app spec's "Uses from habit-logic" list, rather than copying it, and names the exports that `app` does not use. A computed check gives 20 exports, 16 in the app's list, and `addDays`, `weekdayIndex`, `MAX_NAME_LENGTH` and `heatLevel` not in it (`wr07-exports-used-by-app.txt`). |
| WR-08 | RESOLVED | `c81ac1b` | The incomplete "Internal (not exported)" line is removed from BUILD.md, with a dated note that private helpers stay out of the README. |
| WR-09 | RESOLVED | `c0099bb` | The `habits.js` header, the `toggledHabit` comment and the sample-history comment are reworded to what the code does. A mutant without the `.sort()` turns two R9 tests red, which confirms that the sort, not the Set, gives the order (`wr09-toggledHabit-sort.txt`). |
| WR-10 | RESOLVED | `da6586f` | (a) The trim case is now ASCII-only source (` `, ` `, `﻿` escapes), and its title names the four kinds. A mutant that trims plain spaces only turns it red. (b) The fixture check is tagged `@R5` to `@R12` with "fixture check" after the tags. R2 keeps its three tests in `dates.test.js`. (c) The strip test asserts `shortDate` of the first and last day. A mutant that shifts the weekday by one turns it red, and the c0099bb tests stay green on it (`wr10-mutants.txt`). |

Also corrected as the rulings asked: qa.md's locale scenario (`73fb59b`) and purity scenario (`7257e40`), each with a dated note that keeps the old wording.
