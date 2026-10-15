---
kind: consistency-sweep
version: v1.1.0
run: regression --full
status: issues_found
counts: { blocker: 0, warning: 3, info: 10 }
---
# Consistency sweep

Written by the code-review finder (read-only), sweep mode, 2026-10-15. HEAD `ddf43f6`. Once for the whole codebase (`index.html`, `src/`, `tests/`) and its living docs (`README.md`, `CLAUDE.md`, both `spec.md`, `docs/modules/ROADMAP.md`, both `BUILD.md`, both `qa.md` where they make claims about the code, the ledger's "At a glance"). It looks only for what a per-module review cannot see, the same logic in two modules, docs that contradict the code or each other, dead code across the module boundary, one concept with two names, and leftovers. The app's delta review is a separate verdict, `docs/modules/app/findings/regression-code-review.md`.

Evidence, under `docs/modules/app/qa/regression-code-review/`.
- `20261015-191629-sweep-census/`, fifteen read-only checks, one `.txt` each, cited below as "census 01" to "census 15". The doc identifier census, unread names, unused imports, comment citations, the export and import lists, and the greps each finding cites.
- `20261015-191229-chromium-year10000/probe.json`, the probe behind CS-01. Headless Chromium 149.0.7827.55, the suite's clipboard stand-in in each context, a throwaway `git archive` copy of `ddf43f6` served from the session scratchpad.

Doc rot goes to the orchestrator (README, ledger, records) and the planner (specs, ROADMAP). No finding asks for a code change.

## Verdict

**issues_found. 0 BLOCKER, 3 WARNING, 10 INFO.** No code defect, no unrequested code and no cross-module security gap. The habit-logic exports the app imports are exactly the app spec's "Uses from habit-logic" list. The three WARNINGs are docs the code refutes. The spec and README describe the year-10000 residual as 1.0 had it, and a probe shows v1.1.0 no longer loses data that way (CS-01). The app spec gives `popups.js` the closing of popups and omits a listener and three pieces of state (CS-02). The ROADMAP's scenario count and task lists predate step 5 and task 27a (CS-03). The INFOs are dead contract surface, two real duplicates that are cheaper left in place, naming drift, a dead test constant, two records and three loose README lines.

## BLOCKER

None.

## WARNING

### CS-01. The year-10000 residual (SEC-05) is described as 1.0 had it, and v1.1.0 behaves differently (docs contradict code)
- **Symbols.** The closing line of the app spec's Threat model ("The 1.0 notes SEC-02, SEC-05 and SEC-06 ... still hold as written at tag `v1.0.0`"). The README's "Known limits" row that starts "With the device clock set to the year 10000 or later" (RM-01 below). In the code, `toggleDay` (habit-logic R9, changed in v1.1.0 to refuse a key that fails `isDateKey`), `localDateKey`, `heatmapCells` and `yearMonths`.
- **What the docs say.** SEC-05 at tag `v1.0.0` says the app "saves a state that its own `decodeState` calls unreadable, and the next load resets every habit with the S5 note", measured by "adding a habit and ticking today". The README row says the same and adds "In 1.1.0 the year views also do not open".
- **What the code does (observed, `probe.json`).** The clock at 10000-01-05 12:00 (+08:00), empty storage, 1280 x 800, then the same steps at 2026-10-10 12:00 as the control.

  | Step | Control, 2026 | Year 10000 |
  |---|---|---|
  | Boot | header `2026-10-10`, 83 band day buttons, 0 page errors | header `10000-01-05`, 5 band day buttons, 0 page errors |
  | Add "Read" with Enter | saved `{"version":1,"habits":[{"name":"Read","done":[]}]}` | the same |
  | Done today | pressed, saved with `2026-10-10` | stays unpressed, nothing saved |
  | The row's Year | P2 opens | nothing opens, page error "Cannot read properties of undefined (reading 'slice')" |
  | Reload | the habit, Done today pressed, no banner | the habit, no banner, no reset |

  Done today saves nothing because v1.1.0's `toggleDay` checks `isDateKey` on the day first, and a five-digit year fails it. So no unreadable state is ever written, and the next load does not reset.
- **Failure scenario.** A reader of the spec or the README believes this residual loses every habit. The real v1.1.0 shape is different. Done today silently does nothing, the band offers 5 days instead of 83, and P2 and P4 throw on opening. A later security or planning pass that starts from the spec reasons about the wrong failure.
- **Fix direction.** The planner adds a dated note under the Threat model line that gives SEC-05's v1.1.0 form. The orchestrator rewrites the README row (RM-01). The residual stays accepted unless the owner rules again, since it needs a device clock in the year 10000. No code change is asked.

### CS-02. The app spec's Contracts and Invariants describe `app.js`'s wiring in ways the code refutes (contract drift, docs)
- **(a) Who closes a popup.** The Files table gives `src/popups.js` "`showModal`, `close`". `popups.js` opens (`showPopup` calls `showModal()`) and never closes a dialog. Both closes are in `src/app.js`, in `closeWithoutReturn` and `onPopupClick` (census 08). The `app.js` row of the same table lists the Close, Cancel, backdrop and Esc handlers, which is where the code has them.
- **(b) The listener list.** "Events and focus" lists the listeners ("Delegated `click` listeners ..., a `submit` listener ..., an `input` listener ..., a `close` listener on each dialog, and a `scroll` listener"). It leaves out the `pointerdown` listener on each dialog (`onPopupPointerDown`), which R40's "press and release both land outside a popup's box" needs. (`resize` and `visibilitychange` are named in R5 and in the Rollover line.)
- **(c) The state.** Invariants say "All state is one in-memory array of `Habit` ... plus the shown `todayKey` and which popups are open for what". `app.js` also holds `state.saveFailed` (R41), `lastPopupPress` (R14's window) and `pressStartedOnBackdrop` (R40). The `app.js` module comment lists "whether the latest save failed" as state, so the code comment and the contract disagree.
- **Failure scenario.** A reader changing how popups close looks in `popups.js` and finds nothing. The next planner touch copies the Files row into a task as a rule, and a builder adds a close wrapper to satisfy it. A reader trusting the state line misses the guard state when changing R14 or R40.
- **Fix direction.** A dated planner amendment, no code change. `popups.js` opens popups and `app.js` closes them. A `close` wrapper over one native call would be YAGNI. Add `pointerdown` to "Events and focus". Name the state as the module comment does (habits, `todayKey`, `saveFailed`, the open popups with their openers, and the two guard values).

### CS-03. The ROADMAP's v1.1.0 section was not reconciled after step 5 and task 27a (docs contradict each other)
- **Symbols.** `docs/modules/ROADMAP.md`, v1.1.0, "Test contracts", the phase-skills note at the top of the section, and "Build order" (census 14).
- **Failures.**
  - "`app/qa.md` has ~~167~~ ~~168~~ 169 live scenarios". `app/qa.md`'s own Coverage line says 176 (101 new, 71 changed, 4 unchanged, census 15), and a count of its Gherkin gives 176 live and 18 retired.
  - "every UI task loads the design row ... Those are app tasks 12, 13 and 15 to 26". The app spec's Tasks header makes 27a UI work too, and its builder loaded the row (`BUILD.md` task 27a).
  - Build order steps 3 to 6 place tasks 15 to 28 and leave 27a out. Only the Tasks table row the orchestrator added carries it.
- **Failure scenario.** A reader of the ROADMAP, or the next planner, takes 169 as current and copies it, and the count rots again. A brief built from the ROADMAP's UI list would leave the design row off a task like 27a.
- **Fix direction.** Replace the count with a pointer to `app/qa.md`'s Coverage line, so the number has one home (DRY across docs, and the constitution's "state the stable effect"). Add 27a to the UI list and to step 4 of the build order, each with a dated note.

## INFO

### CS-04. `HeatCell` carries fields no consumer reads, under 1.0 names (dead across the boundary, naming)
- **Dead fields.** `heatmapCells` builds `count`, `total`, `column` and `row` for each cell, and habit-logic's tests pin them. Since app task 20 (judgment call 1, accepted ORCH) no app file reads any of the four. The app reads `key`, `done`, `today` and `future` (census 09) and derives "N of T" from the flags itself, in `syncDayButton` (`src/calendar.js`), `renderDayEditor` (`src/popups.js`) and `renderOverviewButton` (`src/view.js`), each `flags.filter(Boolean).length`. So the count rule lives once in habit-logic and three times in the app, and habit-logic's copy is read only by its own tests.
- **Names.** v1.1.0 has no heatmap (levels retired with R11), yet the contract keeps `heatmapCells`, `HeatCell` and `HEATMAP_WEEKS`, which habit-logic's Non-goals gloss ("the heatmap" now reads "the overview and the two year views"). And `done` means two things across the boundary, a habit's `DateKey[]` (`Habit`) and a day's `boolean[]` per habit (`HeatCell`, added in v1.1.0). The app keeps them apart by calling the second `flags`.
- **Why INFO.** Nothing is wrong today, the count is one expression, and any fix is a contract change.
- **Fix direction, for the next version's plan.** The planner rules whether `HeatCell` drops the four unread fields (their tests move to `done`) or the band and P3 read `count` and `total`. P4, P1 and the Overview button have no cell, so the first keeps one home for the count, in the app. A rename of `HeatCell.done` or `heatmapCells` belongs to the same ruling.

### CS-05. The Habit invariant "done ascending, no duplicates" is enforced in two modules with one expression (DRY, a real pair)
- **Symbols.** `toggledHabit` in `src/habits.js` (a `Set`, then `sort`) and `readHabit` in `src/storage.js` (`[...new Set(entry.done)].sort()`) (census 13).
- **Classification.** Both change for one reason, habit-logic's `Habit` type ("done ascending, no duplicates"), so this is not false DRY.
- **Why not merge.** A shared helper would be a new habit-logic export for a one-line expression, and habit-logic's Non-goals give decoding to the app.
- **Fix direction.** Name it where the contract already speaks. habit-logic's Invariants say data enters through `addHabit` and the app's decoder "which uses `validateName` and `isDateKey` from here". One dated clause, "and keeps `done` ascending without duplicates", lets a change to the invariant find both sites from the contract.

### CS-06. The sample conversion exists twice, across the JavaScript and Python boundary (a real pair that cannot merge)
- **Symbols.** `sampleHabits` in `tests/fixtures/sample.js` (habit-logic's test helper, also imported by the app's `tests/storage.test.js`) and `_sample_habits` in `tests/browser/conftest.py`. Both turn the 366-character `done` strings of `docs/design/sample-history.json` into `Habit` objects.
- **Classification.** One reason to change (the sample's format), so a real pair. One is JavaScript and one Python, so no shared code is possible.
- **Why it is safe.** Each is held against the file on its own. `tests/sample-history.test.js` compares `doneFlags` with the file's raw characters, and the browser suite's golden numbers (Current and Best, the band's counts) fail on a wrong Python conversion.
- **Fix direction.** None needed. Recorded so a change to the sample's format updates both.

### CS-07. One guard, two names (one concept, two names)
- **Symbols.** R14's guard is "the tap-through guard" with `TAP_THROUGH_MS` in `src/app.js` (`guardTapThrough`), in the README, in `tests/browser/test_delete.py` and in spec R14's heading. It is "the page guard" with `GUARD_WINDOW_MS` and `let_guard_pass` in `tests/browser/conftest.py`, and in the comment on `PAUSE_MS` in `tests/browser/live_e2e.py`, 1.0's name (census 11). Spec R14 uses both.
- **Why INFO.** The test constant is written out on purpose so it does not read `src/`, which is right. Only the name differs.
- **Fix direction.** The next edit of `conftest.py` calls it the tap-through guard (for example `TAP_THROUGH_MS` and `let_tap_through_pass`). The number stays written out.

### CS-08. `STORAGE_KEY` in `tests/browser/conftest.py` is read by nothing (dead code, DRY)
- **Symbols.** `STORAGE_KEY` in `tests/browser/conftest.py`, defined at 1.0 task 1 (`b6e5069`) and never read (census 02). The literal `streaks.state` is written out instead, in `open_app` and `stored` (`conftest.py`), twice in `live_e2e.py` (`SNAPSHOT_JS` and the control's `seed`), in `test_fidelity_inputs.py` and in `test_storage.py` (census 10).
- **Fix direction.** Pass `STORAGE_KEY` as the `evaluate` argument at those Python sites, or delete it. Test code only.

### CS-09. The head of app `BUILD.md` is 1.0's record with no dated line, where habit-logic's got one (one kind of record, two treatments)
- **Symbols.** `docs/modules/app/BUILD.md`, the header ("Version v1.0.0", "Status: all 10 tasks done and committed"), "Tasks to commits" (tasks 1 to 10), "How to run" (1.0's gate command and fidelity scripts) and "For the README reconcile", which names 31 symbols that no longer exist (13 of `app.js`, such as `renderHabits`, `onDialogClose` and `DIALOG_GUARD_MS`, and 18 of `view.js`, such as `renderHeatmap`, `showNote` and `openDeleteDialog`, census 01).
- **Failure scenario.** None of these carries a line saying it is 1.0's. habit-logic's `BUILD.md` got exactly such lines for the same kind of record (its code review WR-01 and WR-04, 2026-10-15). The v1.1.0 task sections after them are dated and current, so the risk is a reader who stops at the head, or a README reconcile that starts from the first "For the README reconcile" list.
- **Fix direction.** One dated line under the header, saying the sections down to "Handoff" are 1.0's and each v1.1.0 task section gives its own commit, proof and README list. Records only.

### CS-10. The ledger's "At a glance" still reads "plan next" for S7 (records)
- **Symbol.** `docs/v1.1.0/CHANGE-LEDGER.md`, "At a glance", row S7, "OPEN, goldens final in docs/design (2026-10-13), plan next". Execute began on 2026-10-14 and closed on 2026-10-15 (S1 row 25). The scope sections' Status lines are right (OPEN until the seal).
- **Fix direction.** A dated, additive correction of the S7 cell. The orchestrator owns the ledger.

## Stale README lines (the orchestrator's reconcile)

### RM-01 (WARNING, the README half of CS-01). Known limits, the year 10000 row
"the app saves a day it cannot read back, and the next load resets every habit" no longer holds. Observed at HEAD (CS-01, `probe.json`), Done today does nothing, nothing unreadable is saved, a reload keeps the habits with no note, the band offers 5 days, and the year views do not open (a page error).

### RM-02 (INFO). How it is built, "`src/view.js` owns the page's selectors"
The dialogs' selectors live in `src/popups.js` (`dialogs`, whose comment says "Their selectors live here only"), and the day grids' in `src/calendar.js` (`DAY_BUTTON`, `BEAD`, `DAY_GRID`). `view.js` owns the main screen's, as its own header comment says. Fix, "owns the main screen's markup and selectors".

### RM-03 (INFO). How it is built, "when the day editor opens over the overview, `keepDayInSight` gives that popup room"
Since the owner's ruling H-03 of 2026-10-14 16:32 the host is the overview or the year of all habits (P4), and `clearDayRoom` clears both. Fix, "over the overview or the year of all habits".

### RM-04 (INFO). What it does, "A name error shows above the field when you press Add"
Enter in the field submits too (R11, `onComposerSubmit`). Fix, "when you press Add or Enter".

Not stale yet. "Where the record lives" calls `docs/regression/REGRESSION.md` "the last full re-check of the whole app". It is 1.0's and stays true until this regression's record lands.

## Checked and consistent (no finding)

- **The export census agrees with both contracts** (census 06 and 07). The app spec's "Uses from habit-logic" lists exactly what the app imports from `dates.js` and `habits.js`. The habit-logic exports no app file imports (`addDays`, `weekdayIndex`, `monthTitle`, `yearStart`, `MAX_NAME_LENGTH`) are the ones habit-logic's Roadmap notes name. Every export of the app's own modules is imported by another app module, except `STORAGE_KEY`, `decodeState` and `encodeState` of `storage.js`, which the Storage contract names and `tests/storage.test.js` tests.
- **P3's month labels reuse `monthLabels`** (`weekMonths` in `src/calendar.js`) and add the newest row. That equals R38's CG-16 rule, because a Monday on day 1 to 7 of its month is exactly a Monday in another month than the Monday before. A correct reuse, not a second copy.
- **The Python test oracles** that re-derive habit-logic and `ring.js` (`short_date`, `long_date`, `year_date`, `month_title`, `arc_path`, `legend_of` in `conftest.py`) are deliberate, since an oracle must not share code with what it checks. False DRY, keep them.
- **README and CLAUDE.md.** Every backticked symbol in the README is in the code (census 01, none missing). CLAUDE.md's commands match `conftest.py` (`--engine`, `STREAKS_BASE_URL`, `STREAKS_SUBPATH_URL`, the two servers) and `live_e2e.py` (`--engine`, `--base-url`, `--out` that refuses a folder holding files, `--control seeded`). Node 24.11.1 and pytest 9.1.0 are installed, as CLAUDE.md says.
- **No leftovers in the tracked tree.** No `STUB`, `TODO` or `FIXME`, no debug output, no 1.0 name (`weekWindow`, `runContinues`, `heatLevel`, the strip) in `src/`, `index.html` or `tests/`. No `xfail` or `BLOCKED_B1` mark left. Every fidelity script and fixture is read by a test. No unused import in any test or `src/` file (census 03 and 04). Every backticked name in a code comment exists in the code (census 05).
- **Cross-module security.** Every value from the DOM that reaches habit-logic (`data-key` into `toggleDay`) is checked there by `isDateKey`. Names reach the DOM only through `textContent` and `setAttribute`, and M1's title strips bidi controls from its one copy. No path skips a check that another path makes.
- **Leftovers outside git.** `harness/_scratch/` holds 175 files from the 1.0 design phase, and `.pytest_cache/` sits at the project root. Both are git-ignored and both are places the constitution allows. Named for the owner's cleanup, not a finding.

## Not covered

The qa.md scenario text against the tests (the QA regression finder's). The fidelity and live gates (task 28's, not run again here). The design records under `docs/design/` and `docs/design-explore/` (immutable, out of scope). Handoffs and `STATE.md` (situation, not living docs), except where a finding cites one.

## PROCESSES

The sweep's own processes, all foreground and ended before this file was written. `census_run.py` (git and Python children only, no server). `probe_year10000.py`, with its in-process `127.0.0.1` server on a free port (59991, `port_refuses_after` true in `probe.json`) and the headless Chromium it launched and closed. The app review's mutant runs are declared in `docs/modules/app/findings/regression-code-review.md`. A closing sweep at 19:20 by name, command line, port and loopback listeners found only the sweep's own shell.
