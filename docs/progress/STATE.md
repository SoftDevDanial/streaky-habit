# STATE: streaks

- **project:** Streaks, a daily habit tracker
- **design-phase:** sdlc:design
- **version:** 1.1.0 (1.0.0 sealed 2026-10-10, tag v1.0.0)
- **mode:** greenfield
- **phase:** v1.1.0 plan DONE 2026-10-13 23:00. PLAN-CHECK PASS (re-check 22:16, then a touch-up closed its four FLAGs and two NOTEs). Clarify gates parts 1 and 2 all ruled (USER). Ledger scopes S1 to S8 name their module R#s
- **next:** sdlc:execute v1.1.0. Step 0, the orchestrator installs WebKit (python -m playwright install webkit, owner approved 2026-10-13, ledger S5 row 2) and records it in process-ledger.md. Then the ROADMAP v1.1.0 build order, habit-logic tasks 6 to 9 (task 6 restores the 1.0 sample fixture), app task 11 (1.0 golden fixtures, engine switch, WebKit baseline, 179 passed in Chromium on unchanged src), then tasks 12 to 28. UI tasks load taste-skill and frontend-design. Weekly usage was 76% at plan close, the owner decides when the build waves start
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
