---
module: habit-logic
kind: code-review
status: issues_found
counts: { blocker: 0, warning: 6 }
# Re-check 2026-10-09 at 14d59b7: the front matter reads the re-check (0 BLOCKER, 6 WARNING, WR-11 to WR-16). Round 1 read status issues_found, counts { blocker: 0, warning: 10 }, and all ten are resolved (see "Round 1 warnings, re-checked").
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

## Re-check (2026-10-09)

> Written by the code-review finder (read-only), 2026-10-09, against `14d59b7` on `main`. Scope is `git diff 09c5047..HEAD -- src tests`, 6 files, +314 -49, 13 commits: the WR-01 to WR-10 solver round (`73fb59b`, `7257e40`, `61761c6`, `6275858`, `bbd7666`, `c0099bb`, `da6586f`) and the security fixes (`add5043`, `e83acb4`, `3750d67`, `eb2003b`, `b48d716`, `a6e209d`). Everything above this section is unchanged. The front matter was updated in place to this re-check, and a dated YAML comment there keeps the round 1 values. Judged against `spec.md` with its dated notes, `qa.md`, `BUILD.md`, `docs/constitution.md` and `CLAUDE.md`. Line numbers are as of `14d59b7`, and each finding also names a symbol. Evidence is in `docs/modules/habit-logic/qa/code-review/20261009-131935/`. `run-log.txt` there has every command, pid and result, and the `.mjs` files reproduce them. Mutants are applied in memory (`preload.mjs`), so `src/` and `tests/` were not touched.

### Verdict

**PASS with warnings. 0 BLOCKER, 6 WARNING (WR-11 to WR-16).**

- All ten round 1 warnings are resolved. WR-02's fix has a blind spot (WR-14), and the patterns behind WR-06 and WR-10 each came back once (WR-16, WR-13).
- The security fixes are correct and change nothing for valid input. No hallucinated code, no non-goal built, no contract drift.
- The six warnings are two holes in test controls (WR-11, WR-14), a spec that does not say what the code does (WR-12), unreadable test data (WR-13), a guard that nothing can reach (WR-15) and a derivation stated twice (WR-16).
- The security auditor's three observations are all WARNINGs: (a) is WR-11, (b) is WR-12, (c) is WR-13.

### Evidence

- `node --test "tests/**/*.test.js"` gives 66 tests, 66 pass, 0 fail, exit 0. Per file 15, 39, 7 and 5, as BUILD.md says. Every `test()` title starts with its `@R` tag.
- Differential on valid input, HEAD against `09c5047`, `59c6ee5` and `eb2003b` (old sources read with `git show` and loaded in memory): 346,950 cases, each compared with all three revisions, 0 mismatches. It covers `currentStreak`, `bestStreak`, `runContinues`, `toggleDay`, `weekWindow`, `heatmapCells` and `monthLabels` (every day from 1995 to 2035 and 4,000 random days over 0001 to 9999), `heatLevel`, `addDays`, the three labels, `isDateKey`, `validateName` (40,000 names with lone surrogates, astral characters, white space, combining marks and the 38 to 45 code point edge), `addHabit` and `deleteHabit`. `weekdayIndex` agrees with the UTC weekday on all 3,652,059 days from 0001-01-01 to 9999-12-31. Control 1: 201 of 201 histories holding two keys that fail `isDateKey` differ from `eb2003b`, as `streakDays` intends. Control 2: a `bestStreak` raised by 1 is seen in 232 of 3,000 cases.
- Mutation matrix, 25 mutants run in memory over the suite or over one test file: 16 killed, 9 survived. The survivors are WR-11 (six scan mutants), WR-14, WR-15 and `locale-number-toLocaleString`, which is not a defect (see the WR-01 row below).
- `addDays` is exact over the whole valid range (3,652,058 steps, 0 wrong forward, 0 wrong back), and the first step outside it gives a key that fails `isDateKey`. That is the claim `streakDays` rests on.

### Round 1 warnings, re-checked

| Finding | Result | What was checked |
|---|---|---|
| WR-01 | RESOLVED | Mutants `locale-weekday-toLocaleDateString` and `locale-weekday-Intl` change only the weekday name, and only on a non-English default locale. Each turns the R4 locale test red and nothing else in `dates.test.js` (14 of 15 pass). The test asserts the German default before it reads a label. One residual, not a defect: the child does not patch `Number.prototype.toLocaleString`, and German leaves a day number alone, so `day.toLocaleString()` survives that test. The R16 text scan bans `toLocale*`. |
| WR-02 | PARTLY RESOLVED | The check works for `setHours(0, 0, 0, 0)` (red). It cannot see a write that leaves 12:00:00.000 alone. See WR-14. |
| WR-03 | RESOLVED | The `copyHabit` comment (`src/habits.js:31`) states the true reason, and the spec threat-model row carries the dated correction. |
| WR-04 | RESOLVED | `weekdayIndex` is right on every day of the valid range. A 5-day strip (`strip-5`) turns only strip tests red (R5, R8, R9 and the sample strips), none of R10 to R12. `sunday-first` and `month-year-only` mutants are red in R10 and R12. The differential finds 0 mismatches for `heatmapCells` and `monthLabels`. |
| WR-05 | RESOLVED | `runcontinues-second-day` is red in two tests, and `runContinues` has 0 mismatches in 20,000 cases. |
| WR-06 | RESOLVED, repeated once | The four pairs now point to symbols (`BUILD.md:30`, `:31`, `:34`, `:44`). The same kind of pair came back with the security fixes (WR-16). |
| WR-07 | RESOLVED | The app spec lists 16 names, the module exports 20, and the four missing are `addDays`, `weekdayIndex`, `heatLevel` and `MAX_NAME_LENGTH`, as `spec.md:228` says. |
| WR-08 | RESOLVED | `BUILD.md:50` says private helpers stay out of the README. |
| WR-09 | RESOLVED | The header, the `toggledHabit` comment and the sample-history comment match the code. |
| WR-10 | RESOLVED, repeated once | (a) The trim test uses escapes (`tests/habits.test.js:473`), and a trim that handles plain spaces only turns it red. (b) The fixture check says so in its title. (c) The strip test asserts both `shortDate` labels (`tests/sample-history.test.js:53`). Pattern (a) came back at `tests/habits.test.js:170` (WR-13). |

### The security fixes

- **`runLength` bound** (`src/habits.js:50-54`). Correct, because a run never holds more days than the set. One comparison, readable. Behind `streakDays` it is unreachable and nothing pins it (WR-15).
- **`streakDays`** (`src/habits.js:41-43`). Correct and minimal: one line, and the comment gives the true reason. Mutants that drop the filter from `currentStreak`, from `bestStreak`, or make it `filter(Boolean)` are all red, the last two by the 5 s cap on the 20,000-spelling test. It needs `done` to be an array, which the JSDoc says. The behaviour it adds is not in R6 or R7 (WR-12).
- **`longerThan`** (`src/habits.js:222-226`). Correct. It matches `Array.from(name).length > 40` on 40,000 random names, including lone surrogates and the 40 and 41 edge. `++count >= limit` and a return to `Array.from` are both red. The comment is accurate. The unused loop variable `_` is the usual spelling.
- **Purity tables** (`tests/purity.test.js:27-47`). They equal the lists in spec R16 word for word, including `Temporal.Now`, `eval` and `Function(`. Of 22 accidental spellings (`new Date;`, `Date()`, `Date.now`, `fetch`, `localStorage`, `eval` and the rest) all 22 are caught, and 5 of 5 allowed lines pass (`new Date(y, m, d)`, `Date.UTC`, `Temporal.PlainDate`, a comment saying "week window"). No pattern has a `g` flag, so none keeps state. Each failure names its rule. The hole is the stripper that feeds `BANNED_IN_CODE` and the import rule (WR-11). Two entries are hard to read (Observation 2).

### Rulings on the security auditor's three observations

- **(a) `withoutComments` strips `//` and `/*` inside strings: WARNING, WR-11.** The hole is real and proven (scan mutants `scan-s1` and `scan-s2` pass the real purity test). It is wider than the observation says. It also hides code after a `/*` inside a `//` comment, and it blinds the import rule as well as the banned-word table. The auditor's guard regex catches the string shapes only, so it is not the right fix. A one-pass stripper is, and it changes nothing on the real sources.
- **(b) R6 and R7 do not say that keys failing `isDateKey` are ignored: WARNING, WR-12.** The code traces to the SEC-01 threat-model row, so it is not a hallucination. But the project puts a dated note on the R# whose behaviour changed (R13 for SEC-02, R16 for SEC-03 and SEC-04), and two tests are tagged `@R6 @R7` for behaviour neither R states. R7 says "over every entry". Low priority, one dated note and one qa.md scenario close it.
- **(c) `WHITE_SPACE` writes four characters raw: WARNING, WR-13.** WR-10(a) fixed the same pattern in the trim test two commits earlier, so it is a repeat, and 6 of the 7 entries read as empty or as a plain space. It is not worse than a WARNING, because the test would not fail silently: if the set collapsed, the "20,000 distinct keys" precondition at `tests/habits.test.js:185` goes red.

### Reverse audit of the changed code

| Symbol | R# |
|---|---|
| `weekdayIndex` | R4 (dated note), Contracts row |
| `STRIP_DAYS`, `DAYS_PER_WEEK` | R5, R10 |
| `calendarMonth` | R12 |
| `longerThan` | R13 (dated note) |
| `streakDays` | Threat model row "Responsiveness with date keys outside the valid range". No R# states it (WR-12) |
| the size bound in `runLength` | the same row (WR-15) |
| `CLOCK_AND_RANDOM_READS`, `BANNED_IN_CODE` | R16 (dated notes), Threat model rows "Deterministic" and "No network or storage call" |
| `streakInChild`, `FAR_START`, `FAR_STUCK`, `spellingsOfFarStart`, `iteratorSteps` | regression tests for SEC-01 and SEC-02, tagged `@R6`, `@R7`, `@R13` |

No symbol maps to nothing, and no non-goal was built (`streakDays` builds a Set per call and keeps nothing between calls, so the "no caching" non-goal holds).

### BLOCKER (re-check)

None.

### WARNING (re-check)

#### WR-11: `withoutComments` hides code from the banned-word table and the import rule   (control that can be evaded; security observation (a))
- **File:** `tests/purity.test.js:10-12` (the comment and `withoutComments`), used at `:61` (`BANNED_IN_CODE`) and `:69-70` (the import rule). `qa.md:422` states the same assumption.
- **Issue:** The stripper removes block comments first and `//` comments second, and it knows nothing about strings. A `//` inside a string removes the rest of that line. A `/*` inside a string, or inside a `//` comment, opens a block that runs to the next `*/` anywhere later, which here is the end of the next JSDoc, so whole lines vanish from `code`. The clock table is not affected, because `CLOCK_AND_RANDOM_READS` is also matched on the whole text (`:51`). Proof, with in-memory scan mutants and `tests/purity.test.js` alone (`run-log.txt`, sections 2, 3 and 10):
  - The auditor's two mutants pass 5 of 5: `const ENDPOINT = "https://collector.invalid/streaks"; fetch(ENDPOINT);` and `const MIME = "*/*"; sessionStorage.setItem("k", MIME);`.
  - Three mutants of mine pass 5 of 5 and hold no quote that contains a marker: the line comment `// every file under src/*` followed by `localStorage.setItem("streaks", "x");`, or by `navigator.sendBeacon(endpoint, body);`, or by `import { send } from "./net.js";`. The same import line in plain sight turns the import test red, so the rule "habits.js imports only ./dates.js" is evadable too (the stripped text counts 1 `import` word where the file has 2).
  - The auditor's guard regex matches the string shapes and does not match the two comment shapes (`guard matches false`). So it fixes two of three.
  - The assumption is written twice (`tests/purity.test.js:10-11` and `qa.md:422`, which says a test author who meets such a literal "tokenises the source instead of guessing"), and nothing enforces it. The wording "these files hold only label tables and date logic" is also stale, because `habits.js` holds streaks, the heatmap and the name rules.
  - No live defect: the module holds no such line, and a reviewer or the runtime traps would see a network call. So WARNING.
- **Fix:** Replace the two-pass stripper with one pass that consumes strings and comments in source order:
  ```js
  const STRING_OR_COMMENT = /("(?:\\.|[^"\\\n])*"|'(?:\\.|[^'\\\n])*'|`(?:\\.|[^`\\])*`)|\/\*[\s\S]*?\*\/|\/\/.*$/gm;
  const withoutComments = (text) => text.replace(STRING_OR_COMMENT, (match, quoted) => quoted ?? "");
  ```
  On `src/dates.js` and `src/habits.js` its output equals the current output exactly. It passes eight small checks and finds the planted line in each of the four hiding mutants of `probe-stripper.mjs`, and it counts the hidden second import (`probe-stripper-import.mjs`: 2 `import` words where the current stripper counts 1). Then delete the comment at `:10-11`. Its one remaining limit, a quote inside a regular expression literal on a line with another quote, does not occur in the source. For the orchestrator, reword `qa.md:422` (the scan no longer assumes anything about literals).

#### WR-12: R6 and R7 do not say that keys failing `isDateKey` are ignored   (spec does not state the behaviour; security observation (b))
- **File:** `spec.md:54` (R6) and `:62` (R7), `qa.md` (no scenario), `tests/habits.test.js:182` and `:194`, `src/habits.js:41-43` (`streakDays`)
- **Issue:** `currentStreak` and `bestStreak` count only keys that pass `isDateKey`. That is said in the threat-model row (`spec.md:205`), in `BUILD.md:39` and in the JSDoc of `streakDays`, `currentStreak` and `bestStreak`. R6 and R7 do not say it, R7 says "over every entry", and the Invariants (`spec.md:22`) say the input is already valid, so a reader of R6 or R7 does not learn what a stray key does. The two tests at `:182` and `:194` are tagged `@R6 @R7` but assert behaviour that neither requirement states, and qa.md has no scenario for them. The code does map to a spec section, so it is not a hallucination.
- **Fix:** For the orchestrator. Add a dated note under R6 and under R7, for example "Changed 2026-10-09 (security re-check SEC-01, ORCH): keys that fail `isDateKey` are outside the Invariants and are ignored, so the count is of valid days only." Add one qa.md scenario with a stuck key. Then shorten the threat-model row to point at R6 and R7, so the rule has one home.

#### WR-13: `WHITE_SPACE` writes four characters as raw invisible text   (readability; security observation (c))
- **File:** `tests/habits.test.js:170`
- **Issue:** The line holds U+00A0, U+2003, U+3000 and U+FEFF as raw characters. It is the only line in `src/` and `tests/` that does (`probe-whitespace.mjs`). Six of the seven entries read as empty or as a plain space without a hex view. This is the pattern WR-10(a) fixed in the trim test at `:473`, repeated two commits later. The comment above (`:168-169`) does not name the characters either. The test would not pass silently if the set collapsed, because the precondition at `:185` (20,000 distinct keys) goes red, so this costs review time and not correctness.
- **Fix:** `const WHITE_SPACE = ["", " ", "\t", " ", " ", "　", "﻿"];` All seven are accepted as white space by `Number()` (checked). Name them in the comment: no-break space, em space, ideographic space and BOM.

#### WR-14: The Date check added for WR-02 uses a round time, so a partial write goes unseen   (control that can be evaded)
- **File:** `tests/purity.test.js:116` (`new Date(2026, 9, 8, 12)` in the `localDateKey` entry of `callsWith`)
- **Issue:** The test compares `getTime()` before and after the call, which is the right idea. But the Date is exactly 12:00:00.000, so `setMinutes(0)`, `setSeconds(0)` and `setMilliseconds(0)` change nothing on it. Mutant `date-arg-partial`, which runs those three setters on the argument at the start of `localDateKey`, passes 66 of 66. `setHours(0, 0, 0, 0)` is red. On `new Date(2026, 9, 8, 12, 34, 56, 789)` the same mutant changes `getTime()` (`probe-date-arg.mjs`). The criterion at `qa.md:431` ("the same `getTime()` after the call as before it") stays met on that Date, so the control passes over a write it exists to catch.
- **Fix:** Use a Date with non-zero minutes, seconds and milliseconds: `const date = Object.freeze(new Date(2026, 9, 8, 12, 34, 56, 789));`. The key stays `2026-10-08`.

#### WR-15: The size bound in `runLength` cannot be reached and no test pins it   (dead guard)
- **File:** `src/habits.js:45-54` (`runLength` and its comment), `spec.md:205` ("The size bound stays as a second guard"), `BUILD.md:39`
- **Issue:** Behind `streakDays` the set holds only valid keys. Inside the valid range `addDays` is exact (3,652,058 steps checked, `probe-adddays-range.mjs`), and the first step outside it gives a key that is not in the set. So a walk cannot cycle and `length < days.size` never decides anything. Measured: with the bound turned into a counter it fired 0 times in 6,014 calls, 428 of whose keys failed `isDateKey`; with the filter off it fired 25 times (`probe-bound.mjs`). Removing the bound leaves 66 of 66 green (`bound-removed`), while setting it to 0 turns 10 tests red, so the line is live code and no test sees what it does. The solver says it "stays untested, as defence in depth" (`findings/security.md`, Solver round 2, Residuals). Unreachable code that nothing can test is the dead-code smell (constitution principle 6), and the comment's word "guard" is a claim no control can falsify. The two tests from `add5043` (`tests/habits.test.js:144` and `:153`) now pass through the filter and say nothing about the bound.
- **Fix:** Remove `length < days.size && ` from the loop (`for (let key = from; days.has(key); key = addDays(key, step)) length++;`) and the second sentence of the comment, and strike the spec sentence and the `BUILD.md:39` clause with a dated note. A walk over distinct valid days still ends. If the orchestrator keeps its ruling, say in the `runLength` comment that no export reaches the bound and nothing tests it, instead of calling it a guard. Rulings by ORCH are reversible.

#### WR-16: `BUILD.md:39` states the SEC-01 derivation that the source comments and the spec already carry   (DRY across the code/docs boundary, WR-06 again)
- **File:** `BUILD.md:39`, against `src/habits.js:36-40` (`streakDays` comment), `src/habits.js:45-49` (`runLength` comment) and `spec.md:205`
- **Issue:** WR-06 asked for one home per piece of reasoning and BUILD.md was cut back to decisions and pointers. `BUILD.md:39` again gives the reason ("the bound alone was not enough, because many spellings of one such key each start a walk") and the status of the bound ("the bound stays as a second guard"). The `streakDays` and `runLength` comments and the threat-model row say the same. When WR-15 is acted on, three places need the same edit.
- **Fix:** In `BUILD.md:39` keep the decision and point to the symbols: "Streaks count only keys that pass `isDateKey`, see `streakDays`. See `runLength` for the size bound." The comment at `tests/habits.test.js:168-169` explains why the white-space table exists, which is test-data construction, and may stay.

### Observations (not filed)

1. **Spellings that pass both scan tables and are not in the R16 list of forms left to review** (`probe-scan-forms.mjs`): `Date["now"]()`, `Date?.now()`, `Date.call()`, `const { now } = Date`, `new Date(...[])`, `new Image().src = url` and `location.href = url`. They are deliberate evasions of the kind R16's note already accepts, and a denylist cannot be complete. Cheap options: name them in that note, or widen the `Date.now` entry to `/Date\s*(?:\?\.|\.|\[\s*["'`])\s*now\b/`, which matches the first two spellings and `Date['now']()` and not `Date.nowhere`, `Date.UTC` or `new Date(key)` (`probe-stripper-import.mjs`).
2. **Readability of the scan tables.** `(?<![.\w$]|\bnew\s+)Date\s*\(` and `new\s+Date\b(?!\s*\(\s*[^\s)])` need a one-line comment each. The failure message names the rule, which helps, but not the reader of the pattern.
3. **No README exists** for the module or the project, and `BUILD.md:46` ("Exports (for the README reconcile)") has nothing to reconcile into. `spec.md:187-191` still shows all five tasks unticked, while `BUILD.md:15` says 5 of 5 are done. Neither was in scope of the changes reviewed here. They are the orchestrator's.
4. **`calendarMonth`** (`src/habits.js:160-162`) reads the length of the format string `"YYYY-MM"` as a number. A named constant, like `ABBREVIATION_LENGTH` in `dates.js`, would read better. Not filed.
5. **Numbers in docs were checked.** `BUILD.md`'s 66 tests (15, 39, 7, 5) match the run. The 81,706 and 51,202 differential cases in `spec.md` appear in the solver's evidence (`qa/security-solver/20261009T123108/sec01-runs.txt`, `sec02-runs.txt`). No `file:line` citation exists in `spec.md`, `qa.md`, `BUILD.md` or `src/`. No em or en dash exists in `src/`, `tests/`, the module docs or the evidence. No commit in the range carries a vendor attribution line.

### Processes (re-check)

PROCESSES: none alive. Every command ran in the foreground under a shell `timeout` or a `spawnSync` timeout with SIGKILL. No server, browser, watcher or background shell was started.

- Child pids, all exited by themselves: 29828, 39908, 45256, 25336, 35200, 28044, 39476, 18304, 4024, 33472, 6360, 22672, 43712, 46012, 29012, 25920, 45612, 42644, 45592, 45672, 37064, 45952, 44884, 34700, 7288, 32676, 41796, 32764, 35808, 21376, 22512, 13080, 39864, 43696, 27700, 44140, 27608, 42184, 36324, 2692, 44972, 38076, 25632, 4148, 20324, 45644, 25524, 38696 and 39988, plus the 26 children of `run-matrix.mjs` (pids in `run-log.txt`, section 2). Windows reuses pids, so a few numbers repeat. The first suite run was made directly under a shell `timeout 120` and its pid was not captured.
- Children killed at a cap: the two spelling tests under the `best-unfiltered` and `filter-useless` mutants hit their own 5 s cap, and the suite killed those children. They were not started by hand.
- Sweep after the last run: `tasklist` for `node.exe` and `python.exe` found none. `Get-CimInstance Win32_Process` for `node`, `bash`, `sh`, `cmd`, `python`, `pwsh` and `powershell` found no `node` or `python` process, and a command-line match on this folder's name, `preload.mjs`, `run-capped`, `run-matrix` and `--import` found only the sweep's own `bash` and `powershell`. Three `powershell.exe` processes (39064, 37820, 25804) have `claude.exe` (41972) as parent and were started before this review. They are not this review's and were left alone.
- **How this file was written.** This session had no Edit tool, so the file was replaced with the Write tool. The Write tool cannot carry U+00A0 and U+2003, which round 1's text holds raw on the WR-10 "Fix" line and in the WR-10 row of the solver table. After the Write, those two lines were restored byte for byte from `HEAD` with `git diff -U0 -- <file> | awk <keep the two hunks> | git apply -R --unidiff-zero -`. No shell redirect and no heredoc was used. `git diff` of this file now shows two hunks: the front matter and this appended section.

## Solver (re-check, 2026-10-09)

> Written by the dev solver, under the orchestrator rulings of 2026-10-09 (ORCH). The reviewer's text above, its front matter and its evidence folder are unchanged. Solver evidence is in `docs/modules/habit-logic/qa/solver/20261009T135035/`. Phase skills: the registry assigns none to a non-UI fix batch, so none were loaded. Stop rule (ORCH): no further code-review round after this batch. The QA finder runs next and checks the suite.

**Result: 6 of 6 RESOLVED, 0 STILL-OPEN.**

- Final run, `node --test "tests/**/*.test.js"` from the project root, Node v24.11.1 on win32: 66 tests, 66 pass, 0 fail, 0 skipped, exit 0 (`final-run.txt`). Per file: `dates.test.js` 15, `habits.test.js` 39, `sample-history.test.js` 7, `purity.test.js` 5. No test was added or removed, so the counts in BUILD.md hold.
- Each commit of the batch was extracted with `git archive` and run alone. All are green (`per-commit-runs.txt`).
- The mutants are the reviewer's, applied in memory by the reviewer's loader hook, plus three of mine (`mutants.mjs`, run by this folder's `run-capped.mjs`). A mutant run never writes `src/` or `tests/`. `mutants.mjs` holds the Date setter calls as text, so a repo-wide grep for `setMinutes` will hit it. It sits outside `src/` and outside the test glob. Where a row says "before", the same mutant also ran against the code as it stood before the fix, to show that it survived there (`before-runs.txt`).
- The credential gate was green before the batch and before each commit (`final-run.txt`).

| Finding | Status | Commit | How it was verified |
|---|---|---|---|
| WR-11 | RESOLVED | `adb1a99` | `withoutComments` in `tests/purity.test.js` is now one pass (`STRING_OR_COMMENT`, the reviewer's regex) that keeps string and template literals and drops comments. The stale comment is replaced by three lines that give the reason and the one limit. On `src/dates.js` and `src/habits.js` its output equals the old stripper's exactly (`stripper-equality.mjs`). The reviewer's five hiding mutants (`scan-s1`, `scan-s2`, `scan-s3b`, `scan-s3c`, `scan-s5-second-import-hidden`) passed 5 of 5 before and are each red now, with the real source green and both controls still red (`wr11-runs.txt`). The qa.md R16 note that assumed no `//` or `/*` inside a literal has a dated correction. |
| WR-12 | RESOLVED | `160ba9c` | spec.md R6 and R7 each carry a dated note that keys failing `isDateKey` are ignored, with an example that a test pins. qa.md has one new outline, `@R6 @R7 Keys that fail isDateKey are ignored`, with four rows, each mapped to an existing test by title. Those tests pass. The numbers in the notes were recomputed by calling the exports (`wr12-wr16-runs.txt`). The SEC-01 threat-model row now points to the R6 and R7 notes and to the `streakDays` comment. |
| WR-13 | RESOLVED | `ae52deb` | `WHITE_SPACE` is written `"\u{A0}", "\u{2003}", "\u{3000}", "\u{FEFF}"` after the empty string, a space and a tab, and its comment names the four characters. The line is printable ASCII (`od -c`). The array equals the old one entry for entry (`whitespace-equality.mjs`), and the reviewer's `probe-whitespace.mjs`, unchanged, lists no invisible character in `src/` or `tests/` any more (`wr13-runs.txt`). The Edit tool matched the old raw line only when the old text spelled the characters as `\uXXXX` escapes, and it trimmed a trailing space from new text, so the bytes were checked after each edit. |
| WR-14 | RESOLVED | `32edd0f` | The Date is `Object.freeze(new Date(2026, 9, 8, 12, 34, 56, 789))`. The reviewer's `date-arg-partial` mutant passed 5 of 5 before and is red now. Each of its three setters alone (`date-arg-minutes-only`, `date-arg-seconds-only`, `date-arg-milliseconds-only`) was green before and is red now, and `date-arg-sethours` stays red. The key stays `2026-10-08` under four time zones (`wr14-runs.txt`). |
| WR-15 | RESOLVED | `7ea311d` | `length < days.size && ` is gone from `runLength`. Its comment now says `days` must come from `streakDays`, and the `streakDays` comment says the filter is the only guard and why. The suite stays 66 of 66. The working tree against `fa7838d` differs in 0 of 62,010 cases (valid random input, the edges of the valid range, and input holding keys that fail `isDateKey`), while a control with the bound set to `length < 1` differs in most rows (`bound-differential.mjs`). The reviewer's `probe-differential.mjs`, unchanged, gives 0 mismatches in all 346,950 cases against three older revisions. With the filter removed in memory (`current-unfiltered`, `best-unfiltered`, `filter-useless`) the termination tests go red at their own 5 s cap, 2, 3 and 4 tests (1, 2 and 2 before), so the filter alone is now pinned (`wr15-runs.txt`). spec.md (the SEC-01 row) and BUILD.md strike the sentences that named the bound, with dated notes, and the old text stays visible. |
| WR-16 | RESOLVED | `160ba9c` | The BUILD.md bullet on `addDays` past year 9999 keeps the decision and points to `streakDays` (why every walk ends) and `runLength` (how a run is counted). The derivation is gone from it and lives in the `streakDays` comment only. The two clauses that named the size bound stay visible, struck (`wr12-wr16-runs.txt`). |

Also done as the rulings asked: the qa.md R16 note (`adb1a99`), the five task boxes in spec.md ticked with a dated note (`6088b1d`). No README was created.

### What changed, for the README reconcile

- No export, signature or Contract changed. `runLength`, the stripper and the test constants are private.
- Behaviour is the same on valid input and on input holding keys that fail `isDateKey`. The only code change is the deleted comparison in `runLength`.
- Comments touched: `runLength` and `streakDays` in `src/habits.js`, the stripper and the Date comment in `tests/purity.test.js`, the `WHITE_SPACE` comment in `tests/habits.test.js`.
- Documents touched: spec.md (R6, R7, the SEC-01 row, the task boxes), qa.md (the R16 scenario note and one new scenario), BUILD.md (one bullet).
- When the project README is written at the app module close, it should describe the streak rule as R6 and R7 now state it (keys that fail `isDateKey` are ignored) and should not mention a size bound.

### Residuals (not defects)

1. The new stripper has no test of its own. The mutants above prove the current one, but a revert to the two-regex stripper would stay green on the real sources. A two-line self-check (a string holding `//`, a comment holding a quote) would pin it. Not added, because it is outside the six findings.
2. The stripper reads a quote inside a regular expression literal as the start of a string. It says so in its comment and in the qa.md note.
3. Observation 1 of the re-check (`Date["now"]`, `Date?.now()` and the other spellings) was ruled an accepted residual by ORCH and was not touched.
4. The R6 and R7 example values are pinned by two tests in `tests/habits.test.js`. If those tests change, the notes need the same edit.

### Processes (solver)

PROCESSES: none alive. Every command ran in the foreground and exited by itself, and nothing was started in the background. The only kills were the tests' own 5 s caps on walk children under the three filter mutants, which loop by design. Method and result of the sweep by name, by command line and by parent are in `process-sweep.txt`. Three `powershell.exe` processes (39064, 37820, 25804) with parent `claude.exe` (41972) predate the batch and were left alone. Six scratch directories `pc-<commit>` remain in the session scratchpad, outside the project, and were not deleted.
