# Lifecycle: Streaks v1.0.0

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

## Review verdict (stakeholder seat, 2026-10-10)

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
