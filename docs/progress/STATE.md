# STATE: streaks

- **project:** Streaks, a daily habit tracker
- **design-phase:** sdlc:design
- **version:** 0.1.0
- **mode:** greenfield
- **phase:** execute (habit-logic: finders wave 1)
- **next:** execute

## Modules
| module | nature | depends on | status | last green |
|---|---|---|---|---|
| habit-logic | logic | none | built (5/5 tasks, 60 tests pass), finders running | |
| app | FE + live composition | habit-logic | not started | |

## Blockers
none

## Next action
Collect code-review, then QA and security finders for habit-logic. Route findings to solvers. Then README, ledger, credential gate.

## Notes
Goldens (immutable): docs/design/today.html (key), today-empty.html, delete-dialog.html, states.html (specimen sheet), system.md, system.css, sample-history.json, RULINGS.md.
