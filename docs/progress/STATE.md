# STATE: streaks

- **project:** Streaks, a daily habit tracker
- **design-phase:** sdlc:design
- **version:** 0.1.0
- **mode:** greenfield
- **phase:** execute (habit-logic: code-review re-check)
- **next:** execute

## Modules
| module | nature | depends on | status | last green |
|---|---|---|---|---|
| habit-logic | logic | none | security solver done (SEC-01 to SEC-03, 64 tests pass at `eb2003b`); spec and BUILD dated notes, then security re-check, QA finder, code-review re-check | |
| app | FE + live composition | habit-logic | not started | |

## Blockers
none

## Next action
Solver adds the dated spec, qa and BUILD notes. Then security re-check (resume the auditor), QA finder, scoped code-review re-check. Then README reconcile, ledger, credential gate, record last green. Version relabel to v1.0.0 once no agent is writing.

## Notes
Goldens (immutable): docs/design/today.html (key), today-empty.html, delete-dialog.html, states.html (specimen sheet), system.md, system.css, sample-history.json, RULINGS.md.
