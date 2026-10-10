# Regression, v1.0.0

| | |
|---|---|
| Project | Streaks |
| Mode | full, under the ORCH economy ruling of 2026-10-09 (CHANGE-LEDGER row 44) |
| Opened | 2026-10-09, at the tail of execute |
| Closed | 2026-10-10 12:25 |
| Run by | the orchestrator, with finder and solver agents |
| Verdict | **PASS** |

## Scope per module
`--full` asks for every finder on every module. The economy ruling keeps a finder's verdict when the code it judged has not changed
since, and re-runs every finder whose code no agent has seen. Over-testing is cheap, so the QA finder and the cold boot ran on
everything.

| Module | Last green | Code since its finders ran | What re-ran | Why the rest stands |
|---|---|---|---|---|
| habit-logic | `de0156a` | none, `src/` byte for byte the same | QA finder (32 scenarios), unit suite, cold boot. The app's code review re-read the seam between the two modules | Code review and security were given on this exact code |
| app | `9ebc54e` | `fa58481..9ebc54e`, the SEC-01 guards and the SEC-02 and SEC-06 title changes, which no code reviewer had seen | Code review on that delta, with a security eye on SEC-06. QA finder (88 items). Cold boot | Fidelity ran on `321329c`, the same `src/` as `9ebc54e` (6 of 6 at 0 px, 71 of 71 rows). Security closed clean after SEC-06 under the stop rule |

## Finder verdicts
| Finder | Model | Verdict | Report |
|---|---|---|---|
| Code review, app delta | sonnet | 0 BLOCKER, 2 WARNING, 4 INFO. Solved, then a scoped re-check PASS once one spec sentence was reworded (RG-CR-07) | `docs/modules/app/findings/regression-code-review.md` |
| QA, both modules | haiku | PASS, 120 of 120 scenarios, 0 untested. Five everyday flows driven by hand at 390 x 844, 9 of 9 | `docs/modules/app/findings/regression-qa.md` |
| Fidelity, app | | stands, 6 of 6 captures at 0 px, 71 of 71 checklist rows | `docs/modules/app/findings/fidelity.md` |
| Security, both modules | | stands, clean | `docs/modules/*/findings/security.md` |

## Solver rounds
One round, tests and docs only, no change to `src/`.
- RG-CR-01. The 500 ms edge tests now press at 499 ms (ignored) and then 1 ms later (acts), with mouse and touch. Five guard mutants that lived before are killed.
- RG-CR-02. Enter on Delete habit inside the window is ignored, and after it the habit goes. The page guard's keyboard half stays unspecified and the spec says so.
- RG-CR-04 and RG-CR-05. BUILD.md and qa.md gaps closed.
- RG-CR-03. Four README lines, reconciled by the orchestrator after the tree settled.
- RG-CR-06. Long docblocks, accepted.

19 of 21 mutants killed. The two that live are ruled (one is unspecified behaviour, one is equivalent). Browser tests went from 176 to 179.
The scoped re-check found one INFO (RG-CR-07, a spec note gave the wrong reason). The orchestrator reworded it, and code review ended
for v1.0.0 under the stop rule.

## Cold boot
Evidence `docs/regression/20261010-122303/`. The shipped `index.html` on a plain static server, no seed, real `localStorage`, real
clicks and keys, Chromium 149. The run starts on an empty store and ends on what a person would see after a reload.

| # | Step | What it proves | Result |
|---|---|---|---|
| 1 | open the app | the empty first screen, today ringed, nothing stored | PASS |
| 2 | click the field, type a name, click Add | one row with 7 open beads ending on today | PASS |
| 3 | type a name, press Enter | a second row under the first | PASS |
| 4 | click today's bead on both rows | 1 day and Best 1 on both rows, today's heatmap cell at level 4 | PASS |
| 5 | click yesterday's bead on Read | 2 days and Best 2, yesterday's cell at level 2 | PASS |
| 6 | reload | both rows, beads and streak lines unchanged | PASS |
| 7 | click Delete Stretch 10 minutes | the dialog asks, Cancel has focus | PASS |
| 8 | click Cancel | 2 rows remain, focus back on the trash button | PASS |
| 9 | wait, click the trash button, wait, click Delete habit, wait | 1 row, focus on the field, today's cell counts 1 habit | PASS |
| 10 | type a duplicate name, press Enter | the duplicate message shows and the text stays | PASS |
| 11 | reload | exactly one row, 2 days and Best 2 | PASS |

21 requests, every one to the app's own address, 0 outside the rule. 0 console errors, 0 page errors. One screenshot per step
(`01-first-visit.png` to `11-reloaded-again.png`). Server pid 12816 on port 31368, stopped by PID, the port refuses connections after.

## Suites on the final tree
Run by the orchestrator on 2026-10-10 at 12:24, after the cold boot.

| Suite | Command | Result |
|---|---|---|
| Unit | `node --test "tests/**/*.test.js"` | 99 pass, 0 fail |
| Browser | `python -m pytest tests/browser -q -p no:cacheprovider` | 179 passed in 42.32 s. The suite's own servers (pid 9404 and 3964) stopped, ports refuse connections |

## Accepted for v1.0, unchanged by this run
- A click on the page within 500 ms of a mouse press in the delete dialog is dropped without a sign (row 52). Listed for the owner's test pass.
- A slow double click (519 ms or more) can still delete through the trash and Delete habit overlap (the T7 residual, row 37). v1.1.0 replaces the window with a time-free guard (row 40).

The rest of the known limits are in the README.

## Close
- CHANGE-LEDGER. A "re-verified, no regression" row in each of C1 to C7, with its proof, plus this run's row.
- README. Reconciled after the solver (row 48). Nothing a solver touched since.
- Process ledger. Reconciled 2026-10-10 (`docs/progress/process-ledger.md`).
- Credential gate. Full sweep from the project root, exit 0.

## Verdict
**PASS.** Every in-scope finder is green or stands on unchanged code, both suites pass, and the app works live from a cold boot.
