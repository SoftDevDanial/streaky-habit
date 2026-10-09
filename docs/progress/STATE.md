# STATE: streaks

- **project:** Streaks, a daily habit tracker
- **design-phase:** sdlc:design
- **version:** 1.0.0
- **mode:** greenfield
- **phase:** execute (app: code review)
- **next:** execute

## Modules
| module | nature | depends on | status | last green |
|---|---|---|---|---|
| habit-logic | logic | none | CLOSED 2026-10-09 | `de0156a` |
| app | FE + live composition | habit-logic | built (10/10 tasks, 115 browser + 66 unit tests, f4563ab); QA finder running, then code review, security, fidelity, live gate | |

## Blockers
none

## Next action
Collect the QA finder. Then code review, security and fidelity finders (two agents at a time), solvers, the official cold-boot live gate (tests/browser/live_e2e.py into docs/modules/app/qa/live-e2e/<ts>/), README, module close.

## Notes
Goldens (immutable): docs/design/today.html (key), today-empty.html, delete-dialog.html, states.html (specimen sheet), system.md, system.css, sample-history.json, RULINGS.md.
