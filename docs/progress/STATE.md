# STATE: streaks

- **project:** Streaks, a daily habit tracker
- **design-phase:** sdlc:design
- **version:** 1.1.0 (1.0.0 sealed 2026-10-10, tag v1.0.0)
- **mode:** greenfield
- **phase:** v1.1.0 plan, step 3 plan re-check running after the fix pass (first check BLOCK, B1 and F1 to F11 fixed by the planner 2026-10-13 21:55). Clarify gate part 2 ruled 2026-10-13 21:15 (CG-10 to CG-19, all USER)
- **next:** PLAN-CHECK.md verdict, then a planner pass flips the specs' pending CG-12 to CG-19 markers to ruled and fixes any BLOCK, then the ledger scope map and commit. The orchestrator installs WebKit (owner approved 2026-10-13) before app task 11 and amends the CLAUDE.md stack line
- **last-regression:** PASS @ 2026-10-10 12:25 (docs/regression/REGRESSION.md)

## Modules
| module | nature | depends on | status | last green |
|---|---|---|---|---|
| habit-logic | logic | none | CLOSED 2026-10-09 | `de0156a` |
| app | FE + live composition | habit-logic | CLOSED 2026-10-09: QA PASS, code review solved, security clean, fidelity 6 of 6 at 0 px and 71 of 71 rows, live gate 11 of 11, 176 browser + 99 unit, README, credential gate clean | `9ebc54e` |

## Blockers
none

## Next action
Design v1.1.0 closed. The owner approved the final set and the replacement of 1.0's goldens on 2026-10-11 23:45 ("Yes, but later"). On 2026-10-13 final/ was copied into docs/design/ (23 files, SHA-256 equal), the v1.1.0 rulings sit beside 1.0's as RULINGS-v1.1.0.md, and check.py rerun against docs/design/ gave 97 of 97 with every section equal to the final/ run (design-explore/v1.1.0/finalize/). Ledger S7 row 11. Next is sdlc:plan. Its inputs are the goldens below, both RULINGS files, design-explore/v1.1.0/final/SELF-CRITIQUE.md (the approved copy list and interaction rules the rulings point to) and the brainstorm delta.

## Notes
Goldens (immutable, v1.1.0, 1.0's in tag v1.0.0): docs/design/today.html (key), day-editor.html, year-view.html, overview.html, overview-year.html, delete-dialog.html, today-empty.html, today-full.html, states.html (specimen sheet), each with its .md, plus system.md, system.css, sample-history.json, LINKS.json, MANIFEST.md, RULINGS.md (1.0), RULINGS-v1.1.0.md.
