---
module: habit-logic
kind: security
status: pass
counts: { critical: 0, high: 0, medium: 0, low: 0 }
---
# Security audit, habit-logic (v1.1.0, step 5)

> Written by the security finder (read-only), 2026-10-15, against HEAD `4e860ff` on `main`. It replaces the 1.0 verdict of this file (2026-10-09, the first audit, its solver rounds and two re-checks with their unfiled observations, all in git history). Scope is `git diff v1.0.0..HEAD -- src/dates.js src/habits.js` and the tests that hold them, judged against the module's Threat model (with its dated notes and the v1.1.0 row "Responsiveness of the year views"), its Invariants and R1 to R20, with the app's storage contract as the context for stored input. This round's QA and code-review verdicts were read as context only. Node v24.11.1 on win32. Evidence is `docs/modules/habit-logic/qa/security/20261015-131500/` (`probe-v110.mjs` with its output `probe-v110.txt`, and `unit-suite-tail.txt`). Line numbers are as of `4e860ff`.

## Verdict

**PASS. 0 CRITICAL, 0 HIGH, 0 MEDIUM, 0 LOW.**

Every mitigation of the threat model is in the code and held under my own probe. The v1.1.0 exports (`yearDate`, `monthTitle`, `yearStart`, `doneFlags`, `yearMonths`) and the widened `toggleDay` read no clock, touch no global, write none of their arguments and copy no object key from data. `toggleDay` agreed with an independently written range rule on 42,000 calls. `doneFlags` makes one `includes` per habit per call, so a year view is linear in the stored history. Two observations on a device clock in the year 10000 belong to the accepted 1.0 residual SEC-05.

## CRITICAL

None.

## HIGH

None.

## MEDIUM

None.

## LOW

None.

## Threat model, row by row (what I ran and what it showed)

| Row | Control found (file:line) | Driven | Verdict |
|---|---|---|---|
| The day the user sees as "today" | `localDateKey` uses the local getters (`src/dates.js:76`), `addDays` integer day counts (`daysFromCivil`, `civilFromDays`) | `node --test "tests/**/*.test.js"` 137 of 137 pass, the `Asia/Kuala_Lumpur` and `America/New_York` cases among them (`unit-suite-tail.txt`) | PASS |
| Deterministic, testable results | `todayKey` is an argument of every function. The R16 tables in `tests/purity.test.js` | `probe-v110.txt` part 1, no clock or random read (`Date.now`, `new Date` without an argument, `Date()`, `performance.now`, `Math.random`, `Temporal.Now`) in either file, comments included. Part 2, 0 such calls at run time while all 22 exports ran three times | PASS |
| English copy | Fixed `WEEKDAYS` and `MONTHS` tables. The new `yearDate` and `monthTitle` reuse them with `pad` | Part 1, no `Intl` or `toLocale` in the code | PASS |
| Responsiveness with tampered stored data | Only the anchored `KEY_PATTERN` (`src/dates.js:10`), the early-exit `longerThan` | Part 1, the one regular expression of both files is `KEY_PATTERN`. v1.1.0 added none | PASS |
| The app's in-memory state | Pure functions returning new arrays | Part 3, frozen and proxied arguments to every export, the new ones included, 0 writes, 0 throws, no result shares an object with an input | PASS |
| The app's invariants, v1.1.0 range | `toggleDay` checks `isDateKey` and `yearStart(today) <= key <= today` (`src/habits.js:124`), `addHabit` the limit first | Part 4, 42,000 calls over 7 todays (29 February, year ends, year 0002, year 9999) with random, edge and malformed keys, 0 disagreements with the rule written in the probe, the other habit never changed. Part 5, indexes `"0"`, 0.5, NaN, -1, 2, 1e300, true, null, undefined and `[0]` change nothing | PASS |
| Responsiveness of the year views (v1.1.0) | `doneFlags` is one `includes` per habit (`src/habits.js:138`), `heatmapCells` builds each cell from it | Part 6, one call over 12 habits made 12 `includes`, the band 83 x 12, no nested scan. Part 9, a planted 395,000-day list costs 64 to 89 ms for the band and 307 to 400 ms for one P4 draw, and the streaks of every habit cost more (642 to 985 ms). The app's browser timings at the quota are in the app's evidence (`probe_03_planted_size.txt`), at most about 1.9 s per tick | PASS, residual as stated |
| Object integrity | `{ name, done }` literals in `copyHabit` (`:36`) and `toggledHabit` (`:106`), no `Object.assign`, no object spread (part 1) | Part 8, parsed `__proto__`, `constructor.prototype` and extra keys never reach a result, own keys exactly `done,name`, plain prototypes, `({}).polluted` undefined | PASS |
| Date keys outside the valid range | `streakDays` filters with `isDateKey` (`:47`), unchanged since 1.0 | The unit suite's SEC-01 tests pass (`unit-suite-tail.txt`). Part 9 shows the streaks linear at the quota | PASS |
| No network or storage call | The R16 `BANNED_IN_CODE` table | Part 1, none of the banned words (also `Reflect`, `Proxy`, `postMessage`) in the code. Part 2, 0 network or timer calls and 0 globals added. `habits.js` imports only `./dates.js`, `dates.js` nothing | PASS |

## Observations (not filed)

- **O1. A five-digit `todayKey` (device clock in the year 10000, the app's accepted SEC-05).** `yearStart` and `toggleDay` compare keys as text, so for today `10000-01-05` the range starts at `09990-01-05` and `toggleDay` adds `1000-06-01` (part 7). `yearMonths` throws `TypeError` at once for `10000-01-05` and returns 11 months for `99999-12-31`. No control of the app offers a day in year 1000, Done today's key fails `isDateKey`, and P2 and P4 do not open, so nothing wrong can be saved. The code review gave the P2 and P4 symptom to the README. A guard in `toggleDay` that also checks `isDateKey(todayKey)` would close the text comparison if the residual is ever revisited.
- **O2. A `todayKey` in the year 0001.** `yearMonths("0001-01-01")` lays out year 0000 days as open (367 of them), keys that `isDateKey` rejects, so `toggleDay` refuses every one of them. Same family as O1, not realistic.
- **O3. Index -0** acts as 0 in `toggleDay` and `deleteHabit` (part 5). It is the same integer index, so this is no defect.

## Not audited

Nothing in this module's scope was left out. The app's use of these exports in the browser is in `docs/modules/app/findings/security.md`.

## Processes

PROCESSES: none alive. Two foreground Node runs, both exited by themselves. `timeout 300 node probe-v110.mjs` started no child process. `timeout 120 node --test "tests/**/*.test.js"` started its per-file test children, which exited with it. One lapse against the brief, that second command merged stderr with `2>&1` into a pipe, wrote no file, and is recorded in `unit-suite-tail.txt`. The closing sweep at 13:52 (`Get-CimInstance Win32_Process` by name, parent, creation time and command line for python, node, chrome, headless, Playwright and WebKit) found no such process alive.
