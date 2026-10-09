# STATE: streaks

- **project:** Streaks, a daily habit tracker
- **design-phase:** sdlc:design
- **version:** 1.0.0
- **mode:** greenfield
- **phase:** execute (app: build)
- **next:** execute

## Modules
| module | nature | depends on | status | last green |
|---|---|---|---|---|
| habit-logic | logic | none | CLOSED 2026-10-09: code review PASS, security PASS, QA PASS (32 scenarios), 66 tests, credential gate clean | `de0156a` |
| app | FE + live composition | habit-logic | builder next | |

## Blockers
none

## Next action
Build the app module with sdlc-frontend-dev (sonnet) from docs/modules/app/spec.md, 1-to-1 with the goldens. Then finders (QA, code review, security, fidelity), solvers, cold-boot live gate, README, module close. Then regression --full, review, UAT pre-run.

## Notes
Goldens (immutable): docs/design/today.html (key), today-empty.html, delete-dialog.html, states.html (specimen sheet), system.md, system.css, sample-history.json, RULINGS.md.
