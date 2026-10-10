# STATE: streaks

- **project:** Streaks, a daily habit tracker
- **design-phase:** sdlc:design
- **version:** 1.1.0 (1.0.0 sealed 2026-10-10, tag v1.0.0)
- **mode:** greenfield
- **phase:** v1.1.0 design, round 1 done (sdlc:design step 3), waiting for the owner's pick
- **next:** owner picks from docs/design-explore/v1.1.0/round-1/compare.html, then converge, lock, compose, wire, goldens
- **last-regression:** PASS @ 2026-10-10 12:25 (docs/regression/REGRESSION.md)

## Modules
| module | nature | depends on | status | last green |
|---|---|---|---|---|
| habit-logic | logic | none | CLOSED 2026-10-09 | `de0156a` |
| app | FE + live composition | habit-logic | CLOSED 2026-10-09: QA PASS, code review solved, security clean, fidelity 6 of 6 at 0 px and 71 of 71 rows, live gate 11 of 11, 176 browser + 99 unit, README, credential gate clean | `9ebc54e` |

## Blockers
none

## Next action
Owner rules on round 1 (`docs/design-explore/v1.1.0/round-1/compare.html`): which direction (orchestrator's pick A Night Console, runner-up B Neon Thread) and whether the 12-week heatmap may turn on its side (all five do, a 1.0 rule change). Then sdlc:design steps 4 to 9 (converge, lock system, compose every screen and state, wire, self-critique, finalize goldens), the logo redraw with the name "Streaky Habit", then plan. **Start a new Claude session before plan** so the 2.2.0 plugin (UAT test sheet, plan-checker with Write) is loaded; the session that ran round 1 still ran plugin 1.0.0. UAT sheet layout already ruled (ledger off-scope row 5, sdlc 2.2.0 template).

## Notes
Goldens (immutable): docs/design/today.html (key), today-empty.html, delete-dialog.html, states.html (specimen sheet), system.md, system.css, sample-history.json, RULINGS.md.
