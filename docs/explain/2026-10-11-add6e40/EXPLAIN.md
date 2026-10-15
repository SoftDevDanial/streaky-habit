# Streaks, code walkthrough (habit-logic)

Written by the sdlc:explain orchestrator, 2026-10-11. Read-only. This is a dated snapshot and not a gate.

| | |
|---|---|
| Scope | `/sdlc:explain habit-logic`, one module |
| Snapshot | git HEAD `d786d25`, tree clean when the run started. The code is the v1.0.0 build (sealed 2026-10-10, tag `v1.0.0`). The last commit that touched `src/` is `e42eb2f` |
| Walkthroughs | [habit-logic.md](habit-logic.md), written by the codebase explainer (read-only) |

## The product

Streaks is a daily habit tracker on one static web page. You add up to 12 habits, tick any of the last 7 days, and see each habit's current and best streak and one 12-week heatmap for all habits. Everything stays in the browser's `localStorage`. There is no account, no server, no network call, no dependency and no build step. v1.1.0 is in its design phase, so no v1.1.0 code exists yet.

How to run it, from the project root (commands from `CLAUDE.md`).

| What | Command |
|---|---|
| Serve | `python -m http.server <port> --bind 127.0.0.1`, then open `http://127.0.0.1:<port>/` |
| Unit tests | `node --test "tests/**/*.test.js"` |
| Browser tests | `python -m pytest tests/browser -q` |

## The map

`index.html` is the shipped entry point. It loads `src/app.js`, the composition root. Two modules, per `docs/modules/ROADMAP.md`.

| Module | Files | Job |
|---|---|---|
| `habit-logic` | `src/dates.js`, `src/habits.js` | Every rule about days, streaks, the heatmap and names, as pure functions. No DOM, no storage, no clock |
| `app` | `index.html`, `src/app.js`, `src/view.js`, `src/storage.js`, `src/styles.css` | Boot, gestures, the clock, rendering, saving. The live-composition module |

How calls move.

```
index.html
  -> src/app.js      readToday (the one clock read), boot, tick, submitName, removeHabit, checkDay
       -> src/storage.js   loadHabits / saveHabits   (uses isDateKey, validateName, MAX_HABITS)
       -> src/view.js      render*, sync*            (uses weekWindow, currentStreak, bestStreak,
                                                       runContinues, heatmapCells, monthLabels,
                                                       dayParts, shortDate, longDate)
       -> src/habits.js    toggleDay, addHabit, deleteHabit, MAX_HABITS
       -> src/dates.js     localDateKey
src/habits.js -> src/dates.js   (addDays, dayParts, isDateKey, weekdayIndex)
src/dates.js imports nothing
```

Data flow in one line. `app.js` reads the clock once into a `YYYY-MM-DD` key, passes that key and the habit list into habit-logic, gets new values back, saves them through `storage.js` and draws them through `view.js`. habit-logic never knows a day changed. It just receives a new key.

Four habit-logic exports have no shipped caller (`addDays`, `weekdayIndex`, `heatLevel`, `MAX_NAME_LENGTH`). They run inside the module and the tests import them. Checked against the imports in `src/app.js`, `src/view.js` and `src/storage.js`.

## Reading order for a new developer

1. This page, for the map.
2. [habit-logic.md](habit-logic.md) sections 1 and 2, what the module answers and its twenty exports.
3. [habit-logic.md](habit-logic.md) section 3.2 with `src/dates.js` open beside it. The day key is the idea everything else stands on.
4. [habit-logic.md](habit-logic.md) section 3.3 with `src/habits.js` open. Streaks, then the heatmap, then names.
5. [habit-logic.md](habit-logic.md) sections 3.4 to 6, edge cases, data shapes and how the tests prove each rule.
6. [habit-logic.md](habit-logic.md) sections 7 and 8, the quality read and how to change the module safely.

The `app` module has no walkthrough in this run (see the last section). A reader who needs it next would start at `src/app.js` `boot`.

## Quality read, rolled up

The module came through 16 code-review warnings and 4 security findings in v1.0.0, all resolved. What is left is small.

| Area | NOTE | WORTH FIXING |
|---|---|---|
| duplication | 1 | 0 |
| coupling | 1 | 0 |
| exports with no shipped caller | 1 | 0 |
| over-engineering | 2 | 0 |
| fragile patterns | 3 | 0 |
| naming | 1 | 0 |
| comments | 1 | 0 |
| tests | 4 | 0 |
| **Total** | **14** | **0** |

### WORTH FIXING

None. No item in this module was rated WORTH FIXING.

| Module | Symbol | Issue |
|---|---|---|
| | | (none) |

### The NOTE items most worth a look

These are opinions, not defects. The full list with reasons is in [habit-logic.md](habit-logic.md) section 7.

| Module | Symbol | Note |
|---|---|---|
| habit-logic | `toggledHabit`, and `readHabit` in `src/storage.js` | The sort and de-duplicate rule for `done` lives in two modules |
| habit-logic | `MAX_NAME_LENGTH`, `MAX_HABITS` | `src/view.js` writes "40 characters" and "12 habits" as text, so a constant change leaves the copy stale with no test going red |
| habit-logic | the `src/dates.js` module header | Says the file is free of time zones, but `localDateKey` depends on the device time zone by design |
| habit-logic | `withoutComments` in `tests/purity.test.js` | The comment stripper that guards purity has no test of its own and was wrong once before (WR-11) |
| habit-logic | two `@R6` and `@R7` walk tests | Loose `<= 2` and `<= 12` asserts left from a removed size bound, where the code now returns 0 |

### What the orchestrator checked

The explainer had no shell. So the orchestrator checked these points against the code at `d786d25`.

| Check | Result |
|---|---|
| Unit tests, `node --test "tests/**/*.test.js"` | 99 of 99 pass, 0 fail, 545 ms (66 habit-logic tests plus 33 storage codec tests) |
| The four exports with no shipped caller | Confirmed from the import lines of `src/app.js`, `src/view.js` and `src/storage.js` |
| `done` rebuilt as `[...new Set(x)].sort()` in two modules | Confirmed in `toggledHabit` and `readHabit` |
| "40 characters" and "12 habits" written as text | Confirmed in `NAME_ERRORS` and `LIMIT_NOTE` in `src/view.js` |
| The `src/dates.js` header wording | Confirmed, it reads "free of clocks, time zones and locales" |
| The loose walk asserts | Confirmed, `best <= 2` and `current <= 12` in `tests/habits.test.js` |
| `git status --short` after the run | Only `?? docs/explain/` |

## What this walkthrough did not cover

- The `app` module (`index.html`, `src/app.js`, `src/view.js`, `src/storage.js`, `src/styles.css`, `tests/browser/`). It appears here only as habit-logic's caller. Run `/sdlc:explain app` for it.
- The runtime and deployment view (serving, the publish copy, the gates). That is `/sdlc:explain --infra`.
- The browser tests, the fidelity gate and the cold-boot live gate. None were run. Only the unit tests were.
- Correctness beyond what the tests and the spec show. The explainer read the code against `docs/modules/habit-logic/spec.md` and its findings, and did not re-derive every rule by hand.
- v1.1.0. It has no code yet, and `docs/design-explore/` was out of scope.

## Processes

| Owner | Process | State |
|---|---|---|
| codebase explainer | none (Read, Grep, Glob and Write only) | none started |
| orchestrator | one foreground `node --test` run, with its child Node processes from the tests | exited before this page was written |

Nothing is left running. This run wrote only `habit-logic.md` and this page.
