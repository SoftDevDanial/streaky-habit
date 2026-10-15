# Regression, v1.1.0

| | |
|---|---|
| Project | Streaks |
| Mode | full, under the ORCH economy ruling of v1.0.0 (1.0 ledger row 44) |
| Opened | 2026-10-15 18:34, at the tail of execute (ledger S1 row 27) |
| Closed | 2026-10-15 23:58 |
| Run by | the orchestrator, with finder, solver and planner agents |
| Verdict | **PASS** |

The v1.0.0 report is in git history (`git show v1.0.0:docs/regression/REGRESSION.md`).

## Scope per module
`--full` asks for every finder on every module. The economy ruling keeps a finder's verdict when the code it judged has not changed
since, and re-runs every finder whose code no agent has seen. The QA finder and the cold boot ran on everything.

| Module | Code at the start | What re-ran | Why the rest stands |
|---|---|---|---|
| habit-logic | `src/` unchanged since `4e860ff` until task 9a | QA finder, unit suite, then a code-review and a security re-check of task 9a | its step 5 code review and security judged the same code until 9a, and the re-checks judged 9a |
| app | `c271938..HEAD` for code review, `4e860ff..HEAD` for security | QA finder, code review of the delta and a consistency sweep, security of the delta, then the re-checks of 28a and 9a | fidelity stands on today's code, task 28's one-to-one run (ledger S1 row 24) |

## Finder verdicts
| Finder | Model | Verdict | Report |
|---|---|---|---|
| QA, both modules | haiku | PASS. Node 137 of 137, Chromium 358 tests 0 failures, WebKit 358 tests 0 failures 1 skip (CO-1). App 170 of 176 scenarios, the 6 gate scenarios from S1 rows 24 and 25 and the cold boot. habit-logic 42 of 42 | `docs/modules/*/findings/regression-qa.md` |
| Code review, app delta | opus | CLEAN, 3 INFO (RG-CR-I1 to I3) | `docs/modules/app/findings/regression-code-review.md` |
| Consistency sweep | opus | 0 BLOCKER, 3 WARNING, 10 INFO | `docs/regression/20261015-185800/consistency.md` |
| Security, app delta | opus | 1 LOW, SEC-R01 (the year views freeze from October to December of 10000 to 10009). Every T1 to T13 mitigation holds | `docs/modules/app/findings/regression-security.md` |
| Fidelity, app | | stands, task 28 one-to-one, 23 of 23 at 0 px and 139 rows | `docs/modules/app/findings/fidelity.md` |
| Code review re-check, 9a and 28a | opus | CLEAN, 2 INFO (RC-9A-1, RC-9A-2), both ruled | `docs/modules/habit-logic/findings/regression-code-review.md`, the re-check section in the app's |
| Security re-check, 9a | opus | SEC-R01 closed in both engines, 3 INFO, all about the written residual | the re-check section of `docs/modules/app/findings/regression-security.md` |

## Owner ruling
H-06 (SEC-R01). Asked 2026-10-15 20:06, ruled USER "1" at 21:03. `yearMonths` stops after the 13 months its doc comment promises.
The rest of SEC-05 is re-accepted in its v1.1.0 form.

## Solver and doc rounds
- Doc pass `b372666` (planner) on the sweep and code review wording, CS-01, CS-02, CS-03, CS-05, CS-09, RG-CR-I3.
- Planner line `b3183c0`, habit-logic task 9a and app task 28a.
- Targeted pass (dev solver). `eafc9e5` the bound, RED first in Node in a worker thread with a heap limit and a timer (8 of 151 failed
  on termination, the control rows passed). `40848ce` the `firstControl` comment, RG-CR-I1. `3e79c85` the proofs.
- Doc pass `5566e47` (planner), every "contracted and not built" line, the measured SEC-05 form in place of "a prediction".
- README reconciled by the orchestrator twice, RM-01 to RM-04 in row 27, and the Known limits row from the security re-check.

One solver round for code, one re-check per finder kind, under the stop rule.

## Cold boot
Evidence `docs/regression/20261015-185800/` (`live-gate.md` and four run folders). The shipped `index.html` on a plain static server,
no seed, real `localStorage`, real clicks and keys, one server per engine, the control first.

| Engine | Control | Green run |
|---|---|---|
| Chromium 149 | red at step 01 "first visit" on its property, a stored state where null was expected (`live-e2e-20261015-235513-chromium-control/`) | 21 of 21, 0 console errors, 0 page errors, 0 CSP lines, 30 requests all to the app's own address (`live-e2e-20261015-235524-chromium/`) |
| WebKit 26.5 | red at step 01 on the same property (`live-e2e-20261015-235556-webkit-control/`) | 21 of 21, the same zero counts, 30 requests (`live-e2e-20261015-235607-webkit/`) |

Step names, expected text, request lists and screenshot counts equal task 28's gate runs. `date_unchanged` true in all four runs.
Servers 28620 on 4761 and 27696 on 4762, stopped by PID, both ports refuse.

## Suites on the final code
The code is `40848ce`. Every later commit is docs only. Run by the dev solver on the committed tree.

| Suite | Result | Evidence |
|---|---|---|
| Unit, `node --test "tests/**/*.test.js"` | 151 of 151 (137 before, plus the `@R20` test and its 13 rows) | `docs/modules/habit-logic/qa/solver/20261015-224014-node/` |
| Browser, Chromium | 358 passed, by id equal to the QA finder's run | `docs/modules/habit-logic/qa/solver/20261015-224041-chromium/` |
| Browser, WebKit | 357 passed, 1 skipped (CO-1), by id equal | `docs/modules/habit-logic/qa/solver/20261015-224353-webkit/` |

## Accepted or deferred by this run
- SEC-05 in its v1.1.0 form, re-accepted by the owner with H-06. Measured in the app spec's threat model and the README's Known limits.
- RS-9A-2, a second press of the band's Year opens an empty P4 at January to September clocks of 10000 on (ORCH, part of SEC-05).
- RC-9A-1, "at most 13 months" also accepts an empty result (ORCH residual, the wording "between 1 and 13 months" goes to the v1.2.0 plan).
- RG-CR-I2 accepted as documentation. CS-06 accepted. CS-04, CS-07 and CS-08 deferred to the v1.2.0 plan, blocking item none.

The rest of the known limits are in the README.

## Close
- CHANGE-LEDGER. S1 rows 27 to 33, H-06 closed.
- README. Reconciled after the code settled (row 27 and row 31).
- Process ledger. Rows 69 to 75, every process stopped and verified.
- Credential gate. Full sweep from the project root 2026-10-15 23:57, 3616 files, exit 0.

## Verdict
**PASS.** Every in-scope finder is green, re-checked or stands on unchanged code, the one LOW is fixed and re-checked in both engines,
both suites and the unit suite pass, and the app works live from a cold boot in Chromium and WebKit.
