# Roadmap: Streaks

> v1.1.0 section written by the planner (solutions architect role), 2026-10-13. The 1.0 section below it is sealed (git tag `v1.0.0`) and kept as written, with its headings moved down one level.
> Changed 2026-10-13 after the plan check (`PLAN-CHECK.md`, B1, F1 to F11, N1 to N3, N7). The four contracts and this section carry a dated note at each change a reader needs. N4 was in the ledger (the orchestrator's), N5 and N6 needed nothing.
> Changed 2026-10-13 after the plan re-check (`PLAN-CHECK.md`, F12 to F15, N8, N9). A test that waits on a later task is marked `xfail(strict=True)` until that task (F12). The stub method reaches the conftest names and new files under test (F13). Two `test_today.py` scenarios succeed two `test_tick.py` tests (F14). Task 12's removals carry the owner's ruling (F15). The year views' threat rows name planted data (N8). Two `@R30` scenarios are finder checks (N9). Each change carries its own dated note.
> Changed 2026-10-14 in execute (planner touch-up, ledger H-03, S1 row 8, S7 row 15). App task 20 also builds P3's room for rule 4 on a phone (app R36, owner ruling H-03), and app qa.md gains one `@R36` scenario for it. The qa wording of Q1, Q2 and Q3 follows the goldens and the task 18 measurement, with no task change. Each change carries its own dated note.
> Changed 2026-10-14 in execute (planner follow-up, ledger H-03, owner ruling 2026-10-14 16:32 "Same fix for P4 (Recommended)"). App task 20 builds the same room for P4, measures P4's oldest month and the twelve-habit gap first, and gains one `@R36` scenario for a gap smaller than a day (ruled ORCH). App task 26 measures WebKit's focus after a scripted blur before asserting it (ruled ORCH).
> Changed 2026-10-15 in the v1.1.0 regression (consistency sweep CS-03, doc pass only). The scenario count of `app/qa.md` points to its Coverage line instead of a number, and task 27a joins the UI-task list and the build order. Each change carries its own dated note.

## v1.1.0 (Danial's Streaky Habit)

> Inputs. `docs/brainstorm/brainstorm.md` (the v1.1.0 delta with its Round 1 and Round 2 rulings), `docs/v1.1.0/CHANGE-LEDGER.md` (S1 to S8, clarify gate part 1), the nine goldens in `docs/design/` with their `.md`, `system.md`, `system.css`, `sample-history.json`, `LINKS.json`, `MANIFEST.md`, `RULINGS.md` and `RULINGS-v1.1.0.md`, `docs/design-explore/v1.1.0/final/SELF-CRITIQUE.md`, the research `docs/brainstorm/research/webkit-testing.md` and `save-warning-and-tab-icon.md`, `CLAUDE.md` and `docs/constitution.md` (sdlc 2.6.0).
> Phase skills. The registry assigns none to plan. In execute, every UI task loads the design row of `docs/phase-skills.md` (`taste-skill`, `frontend-design`) before it writes UI, and declares it in `BUILD.md`. ~~Those are app tasks 12, 13 and 15 to 26 (app spec, Tasks).~~ Those are app tasks 12, 13, 15 to 26 and 27a (app spec, Tasks). Changed 2026-10-15 in the v1.1.0 regression (consistency sweep CS-03). The list stopped at 26, before task 27a (owner ruling H-05) was added. The app spec's Tasks header counts 27a as UI work, and its builder loaded the design row (`BUILD.md`, task 27a). habit-logic has no UI task.

### Modules
| # | Module | Nature | Depends on | Requirements | Owns (v1.1.0 additions in bold) |
|---|---|---|---|---|---|
| 1 | `habit-logic` | logic (no UI, no I/O) | none | R1 to R20, 17 live | `src/dates.js`, `src/habits.js`, `tests/*.test.js` except the app's two, **`tests/fixtures/sample-history-v1.0.0.json`**, **`tests/fixtures/sample.js`** |
| 2 | `app` | FE, live-composition module | `habit-logic` (Contracts only) | R1 to R42, 38 live | `index.html`, `src/styles.css`, **`src/icon.svg`**, `src/app.js`, `src/view.js`, **`src/calendar.js`**, **`src/popups.js`**, **`src/ring.js`**, `src/storage.js`, `tests/browser/`, `tests/storage.test.js`, **`tests/ring.test.js`**, **`tests/fixtures/design-v1.0.0/`** (tasks 11 and 12 only) |

Changed 2026-10-13 after the plan check (B1). `tests/fixtures/` was habit-logic's alone. The four 1.0 goldens that app task 11 restores there are read only by the app's 1.0 browser tests, so the folder that holds them is the app's.

**Why still two modules.** Nothing in v1.1.0 argues for a change. The new day rules (the year's reach, which habits are done on a day, the 13-month calendar, the labels with a year) are pure functions of data and a passed-in day, so they join `habit-logic`. The new ring geometry is drawing, not a rule about days, so it is a pure file inside `app` (`src/ring.js`), proven by unit tests against the goldens' arcs. Everything that touches the browser (five popups, four day grids, the save warning, the engines) still changes for the same reasons and is wired from the one entry point, so it stays in `app`, which keeps the cold-boot gate. Inside `app` the files are cut along cohesion lines (app spec, Contracts, Files). No seam is added where nothing varies.

### Requirement counts (recounted from both specs on 2026-10-13)
| Module | New | Changed | Retired | Unchanged | In all | Live |
|---|---|---|---|---|---|---|
| `habit-logic` | 4 (R17 to R20) | 2 (R9, R10) | 3 (R5, R8, R11) | 11 (R1 to R4, R6, R7, R12 to R16) | 20 | 17 |
| `app` | 14 (R29 to R42) | 22 (R1 to R6, R10 to R17, R19, R21 to R25, R27, R28) | 4 (R7, R8, R9, R18) | 2 (R20, R26) | 42 | 38 |
| Both | 18 | 24 | 7 | 13 | 62 | 55 |

Test contracts. `habit-logic/qa.md` covers every new and changed R# (written in the first planner run). `app/qa.md` has ~~167~~ ~~168~~ ~~169~~ as many live scenarios as its Coverage line counts (changed 2026-10-14, H-03 and the ORCH ruling on a gap smaller than a day, made it 169), every live R# with at least one, 18 retired scenarios kept as text, 1 Chromium-only scenario, and 139 FE element checklist rows over the nine goldens (its Coverage section). `habit-logic/qa.md` has 42 live scenarios and 3 retired ones, now kept under its own "Feature: Retired in v1.1.0". Recounted by script on 2026-10-13 after the plan check (the live gate's control scenario, F5, made 164 into 165). Recounted by script on 2026-10-13 after the plan re-check (the two successors of the `test_tick.py` tests, F14, made 165 into 167). Recounted by script on 2026-10-14 in execute (planner touch-up, ledger H-03), the `@R36` scenario of P3's room made ~~167~~ 168 live scenarios. Recounted by script on 2026-10-14 in execute (planner follow-up), the `@R36` scenario of a gap smaller than a day made 169. Changed 2026-10-15 in the v1.1.0 regression (consistency sweep CS-03). The number no longer stands here. 169 was stale. Six scenarios for the step 5 solver round and one for task 27a (R17) came after it, and `app/qa.md`'s Coverage line read 176 live scenarios on 2026-10-15. The count now has one home, that Coverage line (the first paragraph of "Coverage by R#"), and this paragraph points to it so the number cannot rot a second time.

### Scope trace (for the ledger's scope map)
Built from the delta tables of both specs.

| Scope | `habit-logic` | `app` |
|---|---|---|
| S1 Edit any past day | R9, R17, R18, R19, R20 (R5 retired) | R16, R19, R27, R31, R32, R33, R34, R36, R37, R39 (R7, R8 retired) |
| S2 Current and Best named | | R6, R27, R32, R33 |
| S3 A delete guard that does not depend on time | | R13, R14, R15, R27, R33 |
| S4 Habits that cannot be saved say so | | R16, R17, R27, R41 (R18 retired) |
| S5 Tested in Safari's engine too | | R27, R30, and every functional scenario runs in both engines |
| S6 The logo in the app | | R1, R4, R25, R27, R29 |
| S7 A livelier look | R10, R17, R19, R20 (R5, R8, R11 retired) | R1 to R5, R10 to R15, R17, R19, R21 to R24, R27, R28, R31, R33, R35, R36, R38 to R40, R42 (R7, R9 retired) |
| S8 A name that is free to use | | R1, R4, R27 |

### Build order
```
0  orchestrator, CLAUDE.md stack line, install WebKit
1  habit-logic task 6 (the 1.0 sample restored) --> app task 11 (the four 1.0 goldens restored, engine switch, WebKit baseline)
2  habit-logic tasks 7, 8, 9            app tasks 12, 13, 14 may run beside them (task 12 removes the 1.0 browser files)
3  app tasks 15 to 25, in order
4  app tasks 26 and 27 (fidelity state scripts, the live gate script with its control mode)
5  finders on both modules (QA in Chromium and in WebKit, code review, security)
6  last, app task 28, fidelity in Chromium, then the cold-boot live gate and its control in Chromium and in WebKit
```
1. **Step 0, the orchestrator (before any code).** Amend the `CLAUDE.md` stack line and install WebKit (Orchestrator actions 1 and 2 below).
2. **Step 1, the test data and the engines.** habit-logic task 6 first. The design finalize of 2026-10-13 replaced `docs/design/sample-history.json` (366-character done strings, no `heatmapLevels`, today 2026-10-10), so today's suites are red before any v1.1.0 work. `tests/browser/conftest.py` reads `SAMPLE["heatmapLevels"]` at import (a KeyError, so the whole browser suite fails to collect), and `tests/habits.test.js`, `tests/purity.test.js` and `tests/sample-history.test.js` read the replaced file. Task 6 restores the 1.0 file as `tests/fixtures/sample-history-v1.0.0.json`, byte for byte from `git show v1.0.0:docs/design/sample-history.json`, and points the three unit files at it. Proof, 99 unit tests green on the unchanged `src/`, and the fixture's blob id equals the tag's. The browser suite has a second cause. Four 1.0 browser tests read 1.0 goldens that the finalize also replaced (`test_R2_golden_style_block_is_the_same_in_every_golden`, `test_R2_stylesheet_is_the_golden_css_with_the_listed_changes`, `test_R28_the_rendered_page_has_the_markup_of_the_goldens`, `test_R28_the_open_dialog_has_the_markup_of_the_golden`). Then app task 11 points `conftest.py`'s sample at the same fixture, restores `today.html`, `today-empty.html`, `delete-dialog.html` and `states.html` byte for byte from tag `v1.0.0` into `tests/fixtures/design-v1.0.0/` and points the 1.0 golden reads at them, adds the engine switch, shows the sealed Chromium count (179 passed, the nine 1.0 test files run by name) on the unchanged `src/`, and records one WebKit run of the 1.0 suite and of the 1.0 live gate with its probes. Changed 2026-10-13 after the plan check (B1). This step first named only the sample, so 179 could not be reached. The golden fixtures are the orchestrator's choice (ORCH, reversible, ledger off-scope row 9).
3. **Step 2, the new day rules, and the 1.0 browser files go.** habit-logic tasks 7, 8 and 9. App tasks 12, 13 and 14 use none of the new exports and may run beside them. App task 15 waits for habit-logic tasks 7 to 9. Task 12's new skeleton breaks every 1.0 locator, so task 12 removes the 1.0 browser test files (each written again by a later task, except `test_tick.py`, which Done today, the day editor and the year view replace), the golden fixtures with their readers, and switches the conftest's sample to v1.1.0. `live_e2e.py` and the two 1.0 fidelity scripts stay unrun until tasks 27 and 26 write them again (app spec, task 12, F3).

   | 1.0 file in `tests/browser/` | At task 11 | At task 12 | Written again by |
   |---|---|---|---|
   | `conftest.py` | engine switch, the 1.0 sample fixture, `DESIGN_V10_DIR` | sample switched to v1.1.0, 1.0-only helpers and `DESIGN_V10_DIR` go | every task adds what it needs |
   | `test_entry.py` | its golden reads point at the fixtures | written again (R1, R2, R29) | task 12 |
   | `test_render.py` | its golden read points at the fixtures | removed | task 15 |
   | `test_tick.py` | unchanged | removed | none (R8 retired, replaced by `test_today.py` 16, `test_day_editor.py` 18, `test_year.py` 19). Its R6 check and JC3 have two successor scenarios in `test_today.py` at 16 (F14) |
   | `test_add.py` | unchanged | removed | task 21 |
   | `test_delete.py` | its golden read points at the fixtures | removed | task 22 |
   | `test_storage.py` | unchanged | removed | task 23 |
   | `test_rollover.py` | unchanged | removed | task 24 |
   | `test_platform.py` | unchanged | removed | task 25 |
   | `test_fidelity_inputs.py` | unchanged | removed | task 26 |
   | `fidelity/seed-sample.js`, `fidelity/open-delete-dialog.js` | unchanged | kept, read by no test | task 26 |
   | `live_e2e.py` | `--engine`, `launch` | kept, not collected | task 27 |
   | `test_engines.py` (new) | three `@R30` scenarios (two more are finder checks with no test, N9) | kept | task 19 adds the clipboard scenario |

   The removals of this step are ruled. The owner answered "git rm, kept in tag v1.0.0 (Recommended)" on 2026-10-13 at 22:20 (ledger off-scope row 11). Task 12's commit removes the eight files marked "removed" above and the folder `tests/fixtures/design-v1.0.0/` with `git rm`, and makes no archive copy. Each of the eight test files is recoverable with `git checkout v1.0.0 -- tests/browser/<file>`. The four golden fixtures never sat at that path in tag `v1.0.0`, so they come back with `git checkout <task 11's commit> -- tests/fixtures/design-v1.0.0/`, or each from `git show v1.0.0:docs/design/<file>` checked against its blob id (app spec, task 11), and never with `git checkout v1.0.0 -- docs/design/<file>`, which would overwrite a v1.1.0 golden. Added 2026-10-13 after the plan re-check (F15).

4. **Step 3, the app.** Tasks 15 to 25 in order. Changed 2026-10-13 after the plan check (F1). This step first held each task until its clarify items were ruled. The owner ruled all ten on 2026-10-13, so nothing waits on them. A test that uses a feature of a later task is committed with `xfail(strict=True, reason="task N")` and that task removes the mark, so every commit ends green and no mark is left after task 22 (app spec, Tasks, and app qa, "Scenarios that wait on a later task", W1 to W22). A mark does not make a task wait. Added 2026-10-13 after the plan re-check (F12).
5. **Step 4.** Tasks 26 and 27. Changed 2026-10-15 in the v1.1.0 regression (consistency sweep CS-03). Task 27a belongs to this step too, and line 4 of the block above gains it. The app spec places it between 27 and 28 with no task renumbered (owner ruling H-05), so its build order is 27, then 27a, then 28. In time it was built after the step 5 solver round (`BUILD.md`, task 27a, Proof, which counts its tests against that round's run).
6. **Step 5, the finders.** QA runs the Node suite once and the browser suite once per engine, then code review and security, on both modules.
7. **Step 6, the gates, last.** App task 28. The fidelity gate in Chromium (23 captures, their controls and the states sheet), then the cold-boot live gate in Chromium and in WebKit, each engine's green run with its control run, which must fail at the first-visit step (app R27, F5). A WebKit failure in the suite or the live gate blocks the seal (ledger S5 row 2).

No dependency deadlock. `app` uses `habit-logic`, never the reverse.

### Tasks
`habit-logic` (spec, Tasks)
| Task | What | R# | Waits on |
|---|---|---|---|
| 6 | The test data fix. `tests/fixtures/sample-history-v1.0.0.json` (the 1.0 sample restored byte for byte from tag `v1.0.0`) and `tests/fixtures/sample.js` (`sampleHabits`), the three unit test files pointed at the fixture, no change in `src/`. Proof, 99 tests green and the fixture's blob id equal to the tag's | R6, R7, R10, R12, R16 (test data only) | none |
| 7 | `src/dates.js` `yearDate`, `monthTitle` | R17 | none |
| 8 | `src/habits.js` `yearStart`, `doneFlags`, `yearMonths`, `toggleDay` on the year, `heatmapCells` with `done` and no `level`. `weekWindow`, `runContinues` and `heatLevel` removed with their tests | R9, R10, R18, R19, R20, R16 | none (CG-13 ruled 2026-10-13) |
| 9 | `tests/sample-history.test.js` v1.1.0 checks | R10, R19, R20 | none |

`app` (spec, Tasks)
| Task | What | R# | Waits on |
|---|---|---|---|
| 11 | The engine switch and the WebKit baseline. `--engine`, `launch`, the `chromium_only` marker, the engine in evidence names, `live_e2e.py --engine`, three `@R30` scenarios in the new `test_engines.py` seen RED through conftest stubs (two more are finder checks, N9, F13), `conftest.py` on the 1.0 sample fixture, the four 1.0 goldens restored byte for byte into `tests/fixtures/design-v1.0.0/` with the 1.0 golden reads pointed at them. Chromium 179 passed for the nine 1.0 test files on the unchanged `src/`, one WebKit run of the 1.0 suite and the 1.0 live gate recorded in `docs/modules/app/qa/webkit-baseline/<datetimestamp>-webkit/`, probes P1 to P3 and the tap, `::backdrop`, CSP and outline probes, each failure classed (a), (b) or (c) | R30 | WebKit installed (step 0), habit-logic task 6 |
| 12 | `index.html`, `src/styles.css`, `src/icon.svg`, `test_entry.py` written again. The 1.0 browser test files, the golden fixtures and the 1.0 sample in `conftest.py` go, the files with `git rm` as the owner ruled (Build order, step 2, F15) | R1, R2, R29 | none |
| 13 | `src/ring.js` (`arcPath`, `legendCounts`) and `tests/ring.test.js` | R42 | none |
| 14 | `src/storage.js` results and `tests/storage.test.js` | R16, R41 | none |
| 15 | The boot render, `test_render.py`, and task 12's icon load scenario turns green | R3, R4, R5, R6, R12, R35, R42 | habit-logic tasks 7 to 9 |
| 16 | Done today and the every-view update, `test_today.py` | R31, R32, R23 | none |
| 17 | Popup plumbing and P3, `test_popups.py`, `test_overview.py` | R40, R38 | none |
| 18 | P1, opening and ticking, `test_day_editor.py` | R36, R37, R32 | none |
| 19 | P2, opening and ticking, `test_year.py`, and the `@R30` clipboard scenario in `test_engines.py` | R33, R34, R32, R30 | none |
| 20 | P4, and P1 over P4. P3's room for rule 4 on a phone (owner ruling H-03), with W22's two P3 rows "2026-07-20" and the new `@R36` room scenario. Added 2026-10-14 in execute (planner touch-up, ledger H-03). P4's room by the same code (owner ruling H-03 of 16:32), measured first on P4's oldest month (2025-10-10 at 390x844 and 360x780) with the RED kept, so W22's row "390x844 P4 2025-10-10" holds. A gap smaller than a day with twelve habits, measured first, and its `@R36` scenario (ruled ORCH). Added 2026-10-14 in execute (planner follow-up) | R39, R36 | none |
| 21 | The composer, `test_add.py`, and task 12's sub-path scenario turns green | R10, R11, R12 | none |
| 22 | Delete from a row and from P2, the time-free guard, the tap-through guard, focus, `test_delete.py` | R13, R14, R15 | none |
| 23 | Persistence, the unreadable note, the save warning, `test_storage.py` | R16, R17, R41 | none |
| 24 | Rollover with popups open, `test_rollover.py` | R19, R20 | none |
| 25 | Platform checks, `test_platform.py` | R21, R22, R23, R24, R25, R26 | none |
| 26 | The fidelity state scripts, each seed script starting with the clipboard stand-in, and `test_fidelity_inputs.py` | R28 | none |
| 27 | `live_e2e.py`, the v1.1.0 cold-boot gate in both engines, with its control mode `--control seeded` | R27, R30 | none |
| 27a | Dismiss with the field disabled sends focus to the page's first control, `dismissNote` (owner ruling H-05). Row added 2026-10-15 by the orchestrator to mirror `app/spec.md` task 27a (commit `bd07675`) | R17 | none |
| 28 | The gates, after the finders are green in both engines. Fidelity in Chromium, then the live gate in Chromium and WebKit, each with its control run | R28, R27 | every task above |

Changed 2026-10-13 after the plan check (B1, F1, F3, F4, F5). The "Waits on" column first held CG-10 to CG-19 for tasks 8, 17, 18, 21, 22, 23, 24 and 27. The owner ruled all ten on 2026-10-13 (Clarify gate, part 2), so no task waits on any of them. Rows 11, 12, 15, 19, 21, 26, 27 and 28 follow the app spec's tasks.

### Orchestrator actions (not builder tasks)
1. **Amend the `CLAUDE.md` stack line** before step 1 (ledger S5 row 2, owner "Keep it, install WebKit"). It reads "Browser tests and gates: Python Playwright, headless Chromium only." It becomes Chromium and WebKit for the functional suite and the cold-boot live gate, with the fidelity pixel gate in Chromium only, and the browser test command gains `--engine webkit` as the second run. The app spec's R30 already replaces the 1.0 spec lines. Stack line done 2026-10-13 22:20 by the orchestrator. The WebKit commands join CLAUDE.md when the engine option lands (A0 for Split, task 11 for Streaks), so CLAUDE.md never names a flag that does not exist yet.
2. **Install WebKit before app task 11.** `python -m playwright install webkit` (owner approved 2026-10-13, about 62 MB from Playwright's download server into `{home}\AppData\Local\ms-playwright\webkit-2311`). Then a listing shows `webkit-2311`, one headless launch prints `browser.version` and closes, and no `Playwright.exe` is left. Record it in `docs/progress/process-ledger.md`.
3. **Clarify gate part 2.** Done. The owner ruled CG-10 to CG-19 on 2026-10-13 with the recommended answers (ledger S1 row 4, S3 row 2, S4 row 3, S7 row 12, table below). Changed 2026-10-13 after the plan check (F1), this action first asked for the rulings.
4. **README changes** (the orchestrator owns the README). Changed 2026-10-13 after the plan check (F7). This action first held the limits only, and the two items below it were missing.
   - The name. The README uses the full name "Danial's Streaky Habit" (brainstorm v1.1.0, Name, "The page title and the READMEs use the full name").
   - The engines. The README's row "Only Chromium is tested. Safari and Firefox are not verified" and its test section ("headless Chromium") become two engines. The functional suite and the cold-boot live gate run in headless Chromium and headless WebKit, the fidelity pixel gate runs in Chromium only, and Firefox is not tested (app R30, ledger S5 row 2). WebKit on Windows is Safari's engine, not Safari on an iPhone, so the owner's iPhone cases in UAT cover touch, the on-screen keyboard and Safari's storage expiry (app spec, Invariants).
   - Private browsing and Safari's 7-day clean-up lose saved habits with no failure the page can see, so no warning shows. The README states the limit and its reason, not "not built", since no reliable detection exists (part 1 CG-2, ledger S4 row 2, ORCH wording).
   - Safari 26 shows the tab icon in one colour in both themes (WebKit bug 309949). Accepted as Safari's bug (ledger S6 row 2).
   - The hub constraint (app spec, Invariants). The showcase hub frames the app from the same origin without `sandbox`, never writes `streaks.state` and never calls `localStorage.clear()`.
5. **UAT cases on the owner's iPhone** (ledger S5 row 2, research webkit-testing item 6, save-warning research D-h and B8 item 6). A double tap on a bin and then on Delete habit. A look at each screen. The save warning with Safari "Block All Cookies" (or Chrome's "Don't allow sites to save data on your device"), never a private window. The tab icon in light and dark on Chrome, Firefox, Safari on macOS and Safari on the iPhone. What iOS 26 draws from the tab icon on the home screen, as information only (ledger off-scope row 7, deferred).
6. **The ledger.** The scope map above, the four contract corrections of this plan (Contradictions, items 7 to 10) and the new item CG-19 (now recorded, ledger S1 row 4). Added 2026-10-13 after the plan check, the fixes of the plan-check pass (B1, F1 to F11, N1 to N3, N7), with B1's golden fixtures as an ORCH choice (ledger off-scope row 9). Added 2026-10-13 after the plan re-check, the touch-up of F12 to F14, N8 and N9, and F15 as applied from the owner's ruling (ledger off-scope row 11).
7. **Processes.** Every WebKit run (the baseline, the suites, the live gate) starts `Playwright.exe`. The agent that runs it declares it in `PROCESSES`, and the orchestrator reconciles the process ledger.

### Clarify gate, part 2 (all ruled 2026-10-13)
The owner ruled all ten items on 2026-10-13 and took the recommended answer each time (USER). The specs apply each answer and name its item ("CG-n, ruled 2026-10-13" with its ledger row), and the qa scenarios that assert one say "CG-n ruled" in their titles. No task waits on any of them. 1.0's CG-1 to CG-9 stay ruled (sealed section below). Part 1 of v1.1.0 (the ledger's CG-1 to CG-4, S4, S5 and S6 row 2) is ruled. Changed 2026-10-13 after the plan check (F1). This heading first read "(all open)", the table's last column held the tasks that waited, and the specs marked each item "pending CG-n, recommended".

| # | Question | Ruling (the recommended answer, owner, 2026-10-13) | Why it was recommended | Ledger row | Applied in |
|---|---|---|---|---|---|
| CG-10 | What exactly is the time-free Delete habit guard (S3)? | Delete habit ignores a mouse or touch click (`detail` above 0) whose point lies inside the box of the control that opened M1 (the bin or P2's Delete habit, measured when M1 opens), or whose `detail` is above 1. A keyboard activation (`detail` 0) always acts. No time window | The second click of a double click, slow or fast, lands at the point of the first. `detail` alone fails a pair slower than the system's double-click time and is unproven for taps in WebKit. Residual, a deliberate click on the part of Delete habit that lies over the opener does nothing. The 1.0 ledger row 37 noted the spatial idea | S3 row 2 | app R13, task 22 |
| CG-11 | Does the 1.0 page guard (500 ms after a pointer click in the dialog) stay, and does it cover the four new popups? | Keep it (the owner kept the pauses at UAT-06) and extend it to every popup. It holds clicks on the page and on popups already open beneath, never inside the clicked popup or popups opened after it | The new popups' Close buttons and backdrops lie over Done today buttons, band days and the Overview button, so the second click of a double click would act behind (1.0 T7 b) | S3 row 2 | app R14, tasks 22 and 27 |
| CG-12 | What does P1 show when a day is opened with no habits (S1 band days are buttons)? | The title, "0 of 0 habits", one thin mini ring, Close focused, and `li.day-empty` "No habits yet." | F2 does it, `system.css` styles `.day-empty`, and no golden draws it | S1 row 4 | app R36, task 18 |
| CG-13 | "The same date last year" on 29 February | 28 February of the year before (a 367-day year) | Common date arithmetic, and it keeps today's month | S1 row 4 | habit-logic R18, task 8 |
| CG-14 | Where does focus go when a rollover removes the focused control? | To the top popup's open-focus target (rule 1), or with no popup open to the page's first focusable control | No rule covers it, and 1.0's position rule has no v1.1.0 equivalent | S7 row 12 | app R19, task 24 |
| CG-15 | After an add, does the list frame scroll to show the new row? | Yes, so the new row lies fully inside the frame's visible part | F2 does it ("keep it in sight"). The approved rules are silent, and without it a 7th habit at 390 px is added out of sight | S7 row 12 | app R10, task 21 |
| CG-16 | Which rows of P3 carry a month label? | F2's rule. The newest row, the oldest row, and any row whose Monday is day 1 to 7 of its month | It matches the golden. It differs from the band's `monthLabels` only when the newest week's Monday is after the 7th, and then "Oct" shows on two rows (the qa's rollover scenario shows it for Monday 12 October) | S7 row 12 | app R38, task 17 |
| CG-17 | Which comes first when the S4 warning and the S5 note both show? | The warning, then the note | The research's ORCH reading (as in Split, where the warning bar sits above the note). No golden draws both | S4 row 3 | app R17 and R41, task 23 |
| CG-18 | Where does focus go after a delete from P2 when the last row went? | To the Year of the row above, or to the field when the list is empty | F2's code (`years[Math.min(idx, len - 1)]`). Rule 3 says only "the next row's Year" | S7 row 12 | app R15, task 22 |
| CG-19 (new) | P1 is open on the oldest day of the year when midnight passes, so that day leaves the editable year. And P1 closes after a rollover removed the day button that opened it. What happens? | P1 stays open on its day (R19), its ticks change nothing (`toggleDay` refuses the day, and the app draws each tick from the data, so no tick flips and nothing is saved). When P1 closes and its opener is gone, focus goes as CG-14 says | No rule or golden covers it. Closing P1 under the user's pointer would surprise. A tick that flips while the data does not would show a state that was never saved | S1 row 4 | app R19, task 24 |

Also flagged, not a new item. CG-3 of 1.0 (the backdrop colour fallbacks) is carried into the v1.1.0 stylesheet (app R2, change 3), because the 1.0 browser floor still stands.

### Contradictions found while planning
1. `docs/design/sample-history.json` was replaced at the finalize, and the sealed 1.0 suites still read it (Build order, step 1). So were `today.html`, `today-empty.html`, `delete-dialog.html` and `states.html`, which four 1.0 browser tests read (the two `test_R2` style tests in `test_entry.py`, `test_R28_the_rendered_page_has_the_markup_of_the_goldens` and `test_R28_the_open_dialog_has_the_markup_of_the_golden`). The research's "the Chromium run must stay green with the same counts" cannot hold until habit-logic task 6 restores the sample and app task 11 restores the four goldens, each byte for byte from tag `v1.0.0` into `tests/fixtures/`. Changed 2026-10-13 after the plan check (B1), this item first named the sample only.
2. `docs/design/today.md` names a save warning golden `today-warning.html`. None exists. The warning is the S4 frame of `states.html` (MANIFEST).
3. `docs/design/today.md` says hover, focus and press are shown in `states.html`. They are not. `states.html` holds only S2 (three frames), S4 and S5. The component states live in `system.css`.
4. SELF-CRITIQUE rule 3 sends focus after a delete from P2 to "the next row's Year" and says nothing for the last row. f.md reading 18 adds "or the field when the list is empty". F2's code uses the previous row's Year (CG-18).
5. 1.0 RULINGS rule 1 (focus to the next trash button or the field after a delete) is replaced by v1.1.0 rule 3 (the bin above when the last row went). RULINGS-v1.1.0 says the 1.0 rulings stand "unless a ruling here replaces one", and rule 3 does.
6. The brainstorm's 1.0 C2 says the strip "stays", while Round 1 says "The per-habit 7-day strip is gone". Round 1 wins (it says it changes the rows above).
7. `docs/design/today.md`'s layout table gives the phone app column 8 px at the top. RULINGS-v1.1.0 small point 1 and `system.css` set 12. The golden CSS wins (checklist row K1-04).
8. The app spec's engine note said WebKit leaves `document.activeElement` unchanged after a mouse click on a button. The research (WebKit's `EventHandler`, a mouse-down with no mouse-focusable element clears focus) gives `body`, whatever had focus. Corrected in the spec on 2026-10-13 with a dated note, and task 11's probe confirms it.
9. The habit-logic spec pointed at "app task 1" and "app task 3", which do not exist in v1.1.0 (the app's tasks are 11 to 28). Corrected to tasks 11 and 15 with a dated note.
10. The app spec named `src/ring.js` with no export names or signatures, and its design-row line began at task 13, leaving out task 12 (markup, stylesheet, icon). Both corrected with dated notes (the Ring contract table, "12 and up").
11. The first planner's handoff had two slips the qa does not follow. Its live gate step put focus on the field after deleting the second of two habits (rule 3 gives the bin above), and its guard step used a Playwright click with a click count of 2 (which sends a first click of `detail` 1 that would delete). The qa uses one press with a click count of 2.
12. Found while fixing F3 of the plan check (2026-10-13). The plan put the `@R30` scenarios in `test_platform.py` at task 11, a 1.0 file that task 12 now removes, and one of them ("Every context has the clipboard stand-in") presses Done today and Year, which the unchanged 1.0 `src/` of task 11 does not have. The Feature moves to the new `test_engines.py`, and that scenario is written at task 19. Two `test_entry.py` scenarios of task 12 also need a page that boots and adds, so the app spec says they stay RED until task 15 and task 21 (app spec, task 12). Changed 2026-10-13 after the plan re-check (F12). The two are now marked `xfail(strict=True)` until task 15 and task 21, under the one rule that covers W1 to W22.

### Measurements taken while planning (read-only scratch scripts in the session scratchpad)
- The arc rule of app R42 reproduces every shared arc in every golden (`#a3-0` to `#a3-2` in six goldens, `#a12-0` to `#a12-11` in four, 66 arcs in all), and gives the N 2 and N 5 values in the qa. Changed 2026-10-13 after the plan check (N2), this line first said seven goldens for `#a3-*`. Recounted, they are `day-editor`, `delete-dialog`, `overview-year`, `overview`, `today` and `year-view`.
- The v1.1.0 sample, today 2026-10-10. Read 4 and 9, Stretch 2 and 5, No phone 0 and 14. Twelve habits, seven done today (Read, Drink 2 litres of water, Journal one page, Practise guitar, Cook dinner at home, Meditate 5 minutes, Floss). Band 83 days, 2, 16, 47 and 18 days with 0 to 3 done. Year 366 days, 18, 96, 153 and 99. No band day has all twelve done. Every Current and Best after an edit that the qa quotes was recomputed.
- `year-view.html` bead classes, 127 with `on l r`, 56 with `on l` (today among them), 56 with `on r`, 11 with `on`, 116 not done, 21 closed, 9 blank, 39 lead. Month ids without a leading zero (`mo-2026-9`, `amo-2026-9`).
- The plugin harness at sdlc 2.6.0 has `--candidate-init-script`, `--candidate-after-load` and `--fixed-time`, its `--color-scheme` defaults to dark, and it renders with `--force-color-profile=srgb` and `--hide-scrollbars` and screenshots with animations disabled.

---

## v0.1.0 (1.0, sealed 2026-10-10, git tag `v1.0.0`)

> Sealed. The text below is the 1.0 roadmap as written, with its headings moved down one level. Its rulings CG-1 to CG-9 still stand where v1.1.0 does not replace them.

> Written by: the solutions architect (sdlc planner), 2026-10-08. Inputs: `docs/brainstorm/brainstorm.md`, `docs/design/` (goldens, `.md` docs, `RULINGS.md`, `sample-history.json`), `CLAUDE.md`, `docs/constitution.md`. No research folder and no repo summary (greenfield).
> Phase skills: the registry assigns none to plan. The `app` builder loads the design row (`taste-skill`, `frontend-design`) because its work is UI.

### Modules

| # | Module | Nature | Depends on | Requirements | Owns |
|---|---|---|---|---|---|
| 1 | `habit-logic` | logic (no UI, no I/O) | none | R1 to R16 | `src/dates.js`, `src/habits.js`, `tests/*.test.js` |
| 2 | `app` | FE, live-composition module | `habit-logic` (Contracts only) | R1 to R28 | `index.html`, `src/styles.css`, `src/app.js`, `src/view.js`, `src/storage.js`, `tests/browser/` |

**Why two modules.** The brief's expected shape holds and nothing argued for changing it. The rules (days, streaks, heatmap levels, name checks, list changes) are pure functions of data and a passed-in day, with no DOM and no clock, so they form one cohesive module that `node --test` can prove exhaustively, including DST and the golden sample. Everything that touches the browser (DOM, storage, clock, dialog, rollover) changes for the same reasons and is wired from the one entry point, so it stays together in `app`, which is also the mandatory live-composition module carrying the cold-boot gate. Splitting `app` further (for example a separate storage module) would put a seam where nothing varies: `localStorage` and `Date` are the only implementations the locked stack allows. The storage codec stays in `app` because the stored format is the app's persistence contract; it reuses `validateName` and `isDateKey` from `habit-logic` rather than restating the rules.

### Build order
1. **`habit-logic`**: independent, so first. Done when `node --test "tests/**/*.test.js"` is green for every `@R` scenario, code review passes and security passes. No fidelity gate (no UI).
2. **`app`**: after `habit-logic`. Done when the browser suite (`python -m pytest tests/browser -q` against the running app) is green, code review and security pass, the fidelity gate is 1-to-1 (6 captures plus the states sheet), and the cold-boot live-e2e gate (`@R27`) passes with its evidence artifact in `docs/modules/app/qa/live-e2e/<datetimestamp>/`.

No dependency deadlock: `app` uses `habit-logic`, never the reverse.

```
habit-logic  -->  app (index.html, composition root, cold-boot gate)
```

### Capability trace
| Brainstorm item | habit-logic | app |
|---|---|---|
| C1 Add a habit (name rules, 12 limit, order) | R13, R14 | R10, R11, R12 |
| C2 Tick the week (7 days, only these editable) | R5, R9 | R7, R8 |
| C3 Current streak (does not break until today ends) | R6 | R6, R8 |
| C4 Best streak | R7 | R6 |
| C5 12-week heatmap (levels, Monday weeks, blanks) | R10, R11, R12 | R9 |
| C6 Delete a habit (confirmation, history gone) | R15 | R13, R14, R15 |
| C7 Kept on the device (saved, unreadable reset) | | R16, R17, R18 |
| Days are local calendar days | R1, R2, R3 | R19, R20 |
| Rolling over midnight | | R19, R20 |
| Platform: phone 360+, keyboard, focus, reduced motion, English | R4 | R4, R21, R22, R23 |
| Nothing leaves the device, no accounts | | R24, R25 |
| Live composition, no seed, cold boot | | R1, R26, R27 |
| 1-to-1 with the goldens | | R2, R28 |

Golden coverage: `today.html` (S1 rows), `today-empty.html` (S2 rows), `delete-dialog.html` (M1 rows) and `states.html` (ST rows) are all in `app/qa.md`'s FE element checklist. `states.html` is a specimen sheet, checked by computed style and Gherkin, never by a pixel diff.

### Clarify gate
All items are closed. CG-1 was resolved by a CLAUDE.md change during planning. CG-2 to CG-9 were ruled on 2026-10-08 by the orchestrator under the owner's delegation (ORCH: reversible, the owner may overturn any of them). The specs follow the rulings and mark each affected place with the item's number. The planning-time recommendation is kept beside each ruling as the record.

| # | Status | Question | Recommended at planning | Ruling |
|---|---|---|---|---|
| CG-1 | Resolved 2026-10-08 | The unit-test command `node --test tests/` in CLAUDE.md exits 1 on Node 24.11.1 ("Cannot find module ...\tests", measured in a scratch copy). | CLAUDE.md now reads `node --test "tests/**/*.test.js"` (changed on disk during planning). Both specs use it. | CLAUDE.md now reads `node --test "tests/**/*.test.js"` (changed on disk during planning). Both specs use it. |
| CG-2 | Ruled 2026-10-08, ORCH | The stock `harness/fidelity.py` cannot reach S1 or M1: it has no clock control, no storage seeding and no gesture step, and its frozen init script pins `Date.now` to 1700000000000 (14 Nov 2023), which conflicts with a clock fixed to 8 Oct 2026. Only S2 on the real date 8 Oct 2026 would be reachable, by coincidence. **Correction (2026-10-08, orchestrator, measured):** this row first also said the 2.1.0 frozen init script pinned `Date.now` to 1700000000000 (14 Nov 2023). That was wrong: the script was an uninvoked arrow function and pinned nothing. | The `app` builder writes `tests/browser/fidelity_capture.py`: the golden through the harness's own `render()`, the candidate with the same launch flags and context plus `page.clock`, the Asia/Kuala_Lumpur zone, seeding from `sample-history.json` and a real click for M1, then the harness's own `diff_images()` and `STYLE_DUMP_JS`, writing the same five files. The fidelity tester runs this driver instead of `fidelity.py` directly. | **Resolved in the plugin instead.** sdlc 2.1.1 `harness/fidelity.py` adds `--candidate-init-script <file.js>` (runs before the app's scripts; seeds storage), `--candidate-after-load <file.js>` (runs after load, may await; opens the dialog), `--fixed-time <ISO local datetime>` (Playwright clock for both renders, covering `Date.now()` and `new Date()`) and repeatable `--browser-arg`. The custom capture driver is dropped. The fidelity tester runs the plugin harness; the two state scripts stay test-side in `tests/browser/fidelity/`. Every Streaks run passes `--fixed-time 2026-10-08T09:00:00`, because 2.1.1 always pins time (default 2023-11-14T22:13:20Z). The measured 0-pixel budget is kept, re-measured with 2.1.1 (D8). Changed 2026-10-08 (plan-check flag, ORCH): this ruling first credited the four state flags to "sdlc 2.1.1" ("sdlc 2.1.1 `harness/fidelity.py` adds ..." above). Corrected from the plugin CHANGELOG, see the version history under Measurements: 2.1.0 added the four flags, 2.1.1 fixed the freeze (time is always pinned through Playwright's clock), 2.1.2 added `bypass_csp`. The minimum stays "2.1.1 or later" and `--fixed-time 2026-10-08T09:00:00` stays on every run. The first fidelity run on 2.1.2 must confirm the 0-pixel baseline measured on 2.1.1 (D8). |
| CG-3 | Ruled 2026-10-08, ORCH | Moving the golden's `.scrim` element to the app's native `::backdrop` (as delete-dialog.md requires) breaks two things in the golden CSS: (a) `background: var(--scrim)` on `::backdrop` is transparent in Chrome and Edge before 122 and Safari before 17.4, which the approved floor includes (Chrome 105+, Safari 15.4+), so the dialog opens with no dim and its edge loses the 3:1 contrast the scrim gives; (b) the reduced-motion rule `*, *::before, *::after` does not reach `::backdrop`, so the backdrop still fades for 180ms under reduced motion (measured), against system.md "both appear at once". | Two additions to the copied CSS, recorded in `app` R2: `background: var(--scrim, rgb(28 37 35 / 0.5))` (same colour, renders identically on current browsers) and `::backdrop` added to the reduced-motion selector list. | Accepted as recommended: the `var(--scrim, rgb(28 37 35 / 0.5))` fallback and `::backdrop` in the reduced-motion selector (`app` R2). |
| CG-4 | Ruled 2026-10-08, ORCH | The brainstorm says the app resets when saved data "cannot be read" but does not say which values count. This decides when a user loses data. | Unreadable = not JSON; not an object; `version` not 1; `habits` not an array of 0 to 12; a name that breaks the name rules (untrimmed, empty, over 40, duplicate ignoring case); a `done` that is not an array of real dates. Lossless oddities are repaired, not reset: unknown extra properties are ignored, `done` is sorted and de-duplicated, dates after today are kept (a clock or time-zone change can create them). On a reset the empty state is saved at once, so "the list was reset" is true and the note shows once, returning only when a later load fails again. Full rule in `app` spec, Storage contract. | Accepted as recommended, including saving the empty state at once after a reset (`app` R17 and the Storage contract). |
| CG-5 | Ruled 2026-10-08, ORCH | No design or copy covers storage being unusable (blocked by the browser) or a failed save (quota or security error). | Never crash. If storage cannot be used at load, start empty without the S5 note (nothing was reset). If a save fails, keep the change on screen for the session and show nothing. Residual: in such a browser the habits are lost on reload without a warning. | Accepted as recommended: keep working in memory, never crash (`app` R18). Recorded as an accepted residual. |
| CG-6 | Ruled 2026-10-08, ORCH | `docs/design-explore/FLOW-CHECK.md` exercised a backdrop click as a dialog exit (PASS), but that came from the flow-check wiring script. `delete-dialog.md`, `system.md` and `RULINGS.md` name only Cancel and Esc. | A backdrop click does nothing (the native `showModal()` behaviour, nothing added). | **Ruled against the recommendation: a backdrop click acts as Cancel** (same result as Cancel, including focus return to the trash button). This matches the design flow check and the Split app. `app` R14, its Contracts (press and release both outside the dialog box) and the `@R13`/`@R14` scenarios follow it. |
| CG-7 | Ruled 2026-10-08, ORCH | Two actions remove or disable the focused control and no approved rule says where focus goes: (a) Dismiss on the S5 note (the button disappears); (b) the 12th add (the input and Add become disabled). | (a) Focus moves to the "New habit" input when it is enabled. (b) The app does not move focus (the browser returns it to the document); the S4 note is announced through the existing live message line. | Accepted as recommended (`app` R12 and R17). |
| CG-8 | Ruled 2026-10-08, ORCH | "1 to 40 characters" does not say what a character is. | Unicode code points (`Array.from(name).length`). Counting graphemes needs `Intl.Segmenter`, which Firefox 121 to 124 (inside the floor) lack, and counting UTF-16 units would make one emoji count as 2. The duplicate check compares `toLowerCase()` of both trimmed names. | Accepted: Unicode code points (`habit-logic` R13). |
| CG-9 | Ruled 2026-10-08, ORCH | The brainstorm does not cover two open tabs. | No cross-tab sync in v0.1.0. Each tab keeps its own state and the last save wins, so a stale tab can overwrite ticks made in another. Recorded as an accepted residual. | Accepted: no sync, last save wins. Recorded as an accepted residual. |

### Architect decisions (within the plan's remit, reversible)
| # | Decision | Why |
|---|---|---|
| D1 | Storage key `streaks.state`, value `{"version":1,"habits":[{"name","done"}]}` | Mirrors the habit shape of `sample-history.json`, so tests seed the sample directly. A specific key because all of one user's GitHub Pages sites share an origin. |
| D2 | A meta Content Security Policy: `default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'` | Enforces "nothing leaves the device" and backs up text-only rendering of names. `'unsafe-inline'` for styles keeps the goldens' inline `style` attributes. Measured: `form-action 'none'` does not block the dialog's `method="dialog"` form; `connect-src 'none'` refuses `fetch`. |
| D3 | Renders are synchronous; a tick updates the existing day button and heat cell in place | The system.md bead and dot transitions can only run on an element that persists, focus stays put, and Playwright's paused clock cannot stall a render. |
| D4 | Rollover check every 30 seconds plus `visibilitychange` | Meets "within a minute" with margin for timer jitter. The header date and streak lines roll over with the strips because they derive from the same day. |
| D5 | Tests use the `Asia/Kuala_Lumpur` zone (UTC+8, no DST) and instants with an explicit `+08:00` | Results do not depend on the test machine's zone. DST is proven in the `habit-logic` unit tests under `America/New_York`. |
| D6 | Functional tests seed through a same-origin 404 page (`<base>__seed__`) before the app loads; the fidelity gate seeds through the harness's `--candidate-init-script` | No app code runs before the seed, and nothing in the shipped app knows about seeding. |
| D7 | The hidden tab is simulated test-side (`visibilityState` getter plus a `visibilitychange` event) | Measured: headless Chromium keeps `visibilityState` "visible" when another tab is brought to the front and when the window is minimised through CDP. |
| D8 | Fidelity budget 0 mismatched pixels at per-pixel threshold 0.1 | Measured, first with a planning probe and again with harness 2.1.1 and `--fixed-time 2026-10-08T09:00:00`: the S1 golden against itself gives 0 pixels; a native modal with `::backdrop` against the M1 golden gives 0 pixels at 390 and 1280 once the after-load script blurs the script-focused Cancel (D12). Added 2026-10-08: these zeros were measured on 2.1.1 and the installed harness is 2.1.2 (which adds `bypass_csp` only). The first fidelity run on 2.1.2 must confirm the 0-pixel baseline before the budget is trusted. A non-zero count on 2.1.2 that was 0 on 2.1.1 is reported to the owner and is not absorbed into the budget. |
| D12 | The M1 after-load script ends with `document.activeElement.blur()` | The golden draws no focus. Script focus without a prior pointer gesture matches `:focus-visible` in Chromium, and that Cancel ring was the whole diff (877 pixels at 390, 977 at 1280, measured with 2.1.1). Focus on Cancel is proven by `@R13`. |
| D13 | A backdrop click (CG-6) counts only when both the press and the release land outside the dialog box | Clicks on `::backdrop` and on the dialog's padding both target the dialog element, so the box test is needed; the press test keeps a text-selection drag from the title from closing the dialog. |
| D9 | After Delete habit, "the next habit" is the one directly below; deleting the bottom habit focuses the input | RULINGS rule 1 read literally ("the next habit's trash button or "New habit""). |
| D10 | After a rejected submit the input has focus, also after a click on Add | states.md "Focus stays in the input" and "so the user can fix it". |
| D11 | Heat cell names always say "habits" ("1 of 1 habits") | The approved formula in system.md, applied literally as RULINGS did for "0 of 0 habits". |

### Measurements taken while planning (scratch scripts outside the project)
- `sample-history.json` independently re-derived: strips, current streaks 6, 3, 1, best streaks 14, 9, 4, `data-run-continues` only on Stretch, all 81 heat levels, month columns 1, 3, 8, 12. All match the goldens.
- The component CSS block is byte-identical in all four goldens; the M1 page body equals the S1 body apart from `inert`.
- Node 24.11.1: `node --test tests/` fails, the quoted glob and bare `node --test` pass; ES module syntax is detected without `package.json`; a runtime `process.env.TZ` change takes effect at once.
- Python 3.14: `http.server` serves `.js` as `text/javascript`; Playwright 1.61 with Chromium 149; pytest available.
- Playwright clock: `run_for` fires interval timers deterministically across midnight, `set_system_time` fires none, an installed clock otherwise follows wall time.
- Golden full-page sizes: S1 and M1 are 390 x 1136 and 1280 x 837.
- Harness 2.1.1 (after the rulings): `--fixed-time 2026-10-08T09:00:00` with an after-load script on a native-dialog copy of M1 gives 877 pixels at 390 and 977 at 1280, all of them the Cancel focus ring; `--disable-lcd-text` leaves both counts unchanged; ending the script with a blur gives 0 and 0.
- Harness version history (corrected 2026-10-08 from the plugin CHANGELOG; earlier text in the CG-2 row and in the `app/spec.md` header credited the four state flags to 2.1.1): 2.1.0 added `--candidate-init-script`, `--candidate-after-load`, `--fixed-time` and repeatable `--browser-arg`; 2.1.1 fixed the freeze so time is always pinned through Playwright's clock (default 2023-11-14T22:13:20Z); 2.1.2 added `bypass_csp` and nothing else. Minimum for Streaks is 2.1.1 or later. The installed harness is 2.1.2. Streaks should render the same on 2.1.2 because its CSP already allows inline styles (D2), but that stays unmeasured until the first fidelity run on 2.1.2 confirms the 0-pixel baseline of D8.

### Residuals to carry into the change ledger
- Safari and Firefox are inside the browser floor but are not tested (CLAUDE.md allows headless Chromium only).
- Clickjacking cannot be blocked from a meta CSP on GitHub Pages; storage partitioning limits the impact.
- CG-5, accepted residual (ruled 2026-10-08, ORCH): where storage is blocked or a save fails, the app works for the session but changes are lost on reload, without a warning.
- CG-9, accepted residual (ruled 2026-10-08, ORCH): two open tabs do not sync and the last save wins, so a stale tab can overwrite ticks made in another.
