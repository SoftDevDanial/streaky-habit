# Lifecycle, Streaks (Danial's Streaky Habit)

## v1.0.0 (sealed 2026-10-10, tag `v1.0.0`)

How this version went from an idea to a reviewed build, phase by phase. Written at review on 2026-10-10 from
`docs/progress/STATE-LOG.md`, the CHANGE-LEDGER and the findings files. The owner delegated the run on
2026-10-08 ("Auto create with lifecycles for 2 projects"), so decisions inside it are tagged ORCH and stay
reversible. The human test column and the seal are the owner's.

| Phase | When | What happened | Key decisions |
|---|---|---|---|
| Init | 2026-10-08 10:45 | Greenfield project, track `sdlc`, working version 0.1.0. Constitution, phase-skills registry, context hooks and `.gitignore` installed | One of two showcase examples |
| Brainstorm | 2026-10-08 10:50 | 11 questions walked, 7 capabilities (C1 to C7), 4 key flows, the rules and 9 non-goals written down | A habit tracker over a plain todo list, because its date and streak rules give the reviewers real edge cases (ORCH) |
| Design | 2026-10-08 10:50 to 15:52 | Three directions (Wall calendar, Quiet beads, Scoreboard), each checked at 360, 390 and 1280 px. "Quiet beads" chosen. A composer agent built the system, 3 screens and a states sheet from one sample history (81 of 81 heatmap cells match it) | The thread is the streak: a run of done days is drawn as one thick thread (ORCH). A mid-run plugin upgrade changed two constitution lines, none this run relies on |
| Plan | 2026-10-08 15:53 to 23:02 | Two modules: `habit-logic` (16 requirements) and `app` (28). Clarify gate CG-1 to CG-9 ruled, plan check PASS with 7 flags fixed. The change ledger opened with 7 scopes | The backdrop acts as Cancel (CG-6). Time is controlled in tests with Playwright's clock, never a hook in the app |
| Execute, habit-logic | 2026-10-09 11:26 to 14:14 | Built (60 tests). Security: 3 medium findings, then a re-check reopened one and found one more, two solver rounds, PASS. Code review: 10 warnings fixed. Closed at `de0156a` with 66 tests | The owner set the target to a stable 1.0, so the version label moved from 0.1.0 to 1.0.0 (USER) |
| Execute, app | 2026-10-09 14:45 to 22:05 | Built, QA PASS. Code review: 13 warnings, solved (127 browser tests). Security: findings including one high, solved, re-checked, then SEC-06 (direction characters in a name could reorder the delete question) fixed with a title strip. Fidelity 6 of 6 captures at 0 px and 71 of 71 element checks. Live gate 11 of 11. Closed at `9ebc54e` | Two 500 ms guards so a double click cannot open and confirm the delete dialog in one gesture (ORCH, from the security review). A slow double click past 500 ms stays a known limit for v1.1.0 |
| Regression | 2026-10-09 22:05 to 2026-10-10 12:26 | `--full` under an economy ruling: finders re-ran on code no finder had seen. Code review of the delta found 2 warnings and 4 notes, solved (tests and docs only), re-checked PASS. QA 120 of 120 scenarios. Cold boot 11 of 11. 179 browser and 99 unit tests | Verdicts on byte-identical code stand (ORCH). The owner chose a second version per app to show versioning, v1.1.0 fixes the v1.0 limits (USER) |
| Brand | 2026-10-10 | Logo, README redesign, static badges, a showcase image from real pixel-gate captures. Docs only, no app change | Logo in the repo now, the favicon in v1.1.0 through the design phase (USER) |
| Review | 2026-10-10 | Drove every brainstorm flow and rule on a cold boot with real gestures: 32 of 32 checks pass. See the verdict below | Shippable for the owner's test |

### v1.0.0 review verdict (stakeholder seat, 2026-10-10)

**Shippable for UAT.** Every capability C1 to C7 works on a cold boot with no seed. The four key flows, the name
rules, the 12-habit limit, the week strip, both streak rules, the heatmap levels and names, the midnight rollover,
the reset note, keyboard use, 360 px, reduced motion and the no-network rule all hold (`docs/review/20261010-130904/results.json`).
The design matches its goldens to the pixel.

Deviations from the brainstorm and the design, with their cause:

| Deviation | Cause |
|---|---|
| "Delete habit" does nothing for the first 500 ms after the dialog opens, and a page click within 500 ms after a press in the dialog is dropped | Claude (ORCH), fixing security finding SEC-01 so a double click cannot delete in one gesture. Visible behaviour the brainstorm did not ask for. Documented in the README and listed for UAT |
| `src/styles.css` differs from the golden CSS in three marked rules (the native `::backdrop` replaces the golden's `.scrim` element, a fallback colour for older browsers, and reduced motion reaching `::backdrop`) | Claude (ORCH), app spec R2. The pixel gate shows no visible difference |
| The dialog title isolates the name and leaves direction control characters out of its copy of it | Claude (ORCH), security SEC-02 and SEC-06. The stored name is unchanged |
| A slow double click (more than 500 ms between clicks) where the trash and "Delete habit" overlap can still delete | Known limit, accepted for v1.0 (ORCH), fixed in v1.1.0 (USER) |
| If storage is blocked or full, changes are not saved and no message says so | Known limit, accepted (ORCH). The brainstorm's reset note covers unreadable data, not a failed save |

No requirement was dropped and nothing was built that no spec asked for. Compliance review is skipped (personal direction).
No out-of-project artifacts are logged (`docs/progress/out-of-project-artifacts.md` does not exist).

---

## v1.1.0 (sealed 2026-10-16, tag `v1.1.0`)

Added at review on 2026-10-16 by the stakeholder reviewer (agent), from `docs/v1.1.0/CHANGE-LEDGER.md`, `docs/regression/REGRESSION.md` and the handoffs in `docs/progress/handoff/`. The v1.0 text above is unchanged. This version was not delegated. The owner ran the design round with him in it, so his decisions are tagged USER and the orchestrator's in between are ORCH and reversible. UAT and the seal are his. On 2026-10-22, after the seal, the page took one title with a heading per version, and the UAT and seal rows were added from `docs/v1.1.0/SEAL.md` and its ledger.

| Phase | When | What happened | Key decisions |
|---|---|---|---|
| Brainstorm delta | 2026-10-10 | Opened at the 1.0 seal from the owner's UAT. Scopes S1 to S8 (edit any past day, Current and Best labels, a time-free delete guard, a save warning, WebKit testing, the logo in the app, a livelier look, a free name). Appended to `docs/brainstorm/brainstorm.md` with grill rows 12 to 21 | The name Danial's Streaky Habit, "Streaky Habit" in the logo and header (USER). The non-goal on days older than 7 removed (USER). One dark theme allowed, still system fonts and no network (ORCH) |
| Design | 2026-10-10 to 2026-10-13 | Round 1, five clickable directions. The owner picked D Orbit Rings' look with his own layout (a list with Done today and a per-habit year view, an overview). Round 2 direction F, then revision F2 with a year view of all habits and a bin on every row. F2 accepted 2026-10-11 00:58 after the ring numbers were centred. Composer, flow check 49 of 49 links, rulings, a logo round (T6, the 1.0 mark with one outer arc, no tile). Finalize copied 23 files into `docs/design/` on 2026-10-13 | Reach is the last 12 months (USER). The overview stays 12 weeks with a Year button (USER). Delete from the row and from the year view (USER). Seven interaction rules and the copy approved as written (USER) |
| Plan | 2026-10-13 18:20 to 22:55 | The constitution replaced with sdlc 2.6.0. Two researchers (WebKit testing, save warning and tab icon). Clarify gate parts 1 and 2 ruled CG-1 to CG-19. Plan check BLOCK (the finalize had replaced goldens the 1.0 suites read), one fix pass, PASS. habit-logic gains R17 to R20 and retires R5, R8, R11. app gains R29 to R42 and retires R7, R8, R9, R18 | WebKit installed and gating the suites and live gate, the pixel gate stays Chromium only (USER). The tab icon as a file under a strict CSP (USER). 1.0 test files removed with `git rm`, kept in tag v1.0.0 (USER) |
| Execute | 2026-10-14 12:34 to 2026-10-15 18:34 | habit-logic tasks 6 to 9, app tasks 11 to 28 with 27a, each seen RED first. The owner halted the build at 13:50 on 2026-10-14 after seeing the 1.0 page in a baseline run, a check showed the goldens intact and he resumed it. Step 5, QA one failure (the test was wrong, CR-01), code review 1 BLOCKER and 11 WARNING in app and 3 in habit-logic, security PASS with 0 findings. One solver round resolved all 16, re-checks held. Fidelity 23 of 23 captures at 0 px and 139 of 139 rows. Cold-boot live gate 21 of 21 in both engines with red controls | Room under the day editor on a phone, for P3 then P4 (USER, H-03). The solver's skipped design row accepted (USER, H-04). Focus after Dismiss with the field disabled (USER, H-05). Records committed at every session end (ORCH, after the owner asked) |
| Regression | 2026-10-15 18:34 to 23:58 | `--full` under the 1.0 economy ruling. QA PASS (Node 137, Chromium 358, WebKit 358 with one counted skip). App code review CLEAN, consistency sweep 0 BLOCKER. Security found SEC-R01 (the year views froze the tab with the device clock in late 10000). Bound built as habit-logic task 9a with app task 28a, both re-checks CLEAN and SEC-R01 closed. Cold boot 21 of 21 in both engines | The 13-month bound in `yearMonths` (USER, H-06). Three sweep items deferred to the v1.2.0 plan (ORCH) |
| Review | 2026-10-16 00:13 | Drove every v1.1.0 capability on a cold boot with no seed and the real clock, real taps at 390 x 844 and clicks and keys at 1280 x 800, in Chromium and WebKit. 264 checks pass, 0 fail. See the verdict below | Shippable to UAT, one new item for the owner |
| UAT | 2026-10-16 01:23 to 19:38 | 12 cases in two sittings. The tester's pre-run, script repairs and a re-run. The owner's desk sitting passed UAT-01 to UAT-07, with one crossed line in UAT-01, the All habits window showing two months per row in Chrome on Windows (H-09). The phone sitting, UAT-08 to UAT-12, was not run on an iPhone and stays BLOCKED. A tester run in Android layouts is kept as evidence only. Script, verdicts in his words and findings in `docs/v1.1.0/user-test-2026-10-16/` | H-09 deferred to the next version and written up in `docs/future/bugs-found.md`. Phone cases stay recorded as not run, with the reason, and the release does not depend on them. H-07 and H-08 kept as built (USER) |
| Seal | 2026-10-16 19:50 | `docs/v1.1.0/SEAL.md`, tag `v1.1.0`, residuals listed as ruled | "seal both" (USER) |

### v1.1.0 review verdict (stakeholder seat, 2026-10-16)

**Shippable to UAT.** The full report is `docs/review/20261016-001319/review.md`. Every capability of the delta works in both engines, the first visit equals its golden to the pixel in each engine, and nothing leaves the device.

Deviations, with their cause.

| Deviation | Cause |
|---|---|
| In WebKit every popup opened by a tap or click draws the focus ring on the control the app focuses. The goldens and Chromium draw none | WebKit's focus heuristic with rule 1 (the app sets first focus, owner-approved). Unseen because the pixel gate is Chromium only (USER). New, for the owner's iPhone in UAT |
| The README header still shows the 1.0 name and captures | ORCH (ledger S1 row 18), changes at the seal |
| Room under the day editor on a phone, and its residuals (a partly shown day with many habits, a thin scrollbar in narrow desktop windows, a Monday midnight) | USER for the room (H-03), ORCH for the residuals (S1 rows 10 and 12) |
| Three marked CSS changes from the golden | Carried from 1.0 (app R2), no visible difference |
| Far device clocks (year 10000 and later) | The bound is USER (H-06), the residual SEC-05 ORCH |

No requirement was dropped and nothing visible was built that no spec asked for. Compliance review is skipped (personal direction). No out-of-project artifacts are logged.
