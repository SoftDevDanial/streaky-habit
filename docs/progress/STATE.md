# STATE: streaks

- **project:** Streaks, a daily habit tracker
- **design-phase:** sdlc:design
- **version:** 1.0.0
- **mode:** greenfield
- **phase:** v1.0.0 SEALED 2026-10-10 on the owner's word; v1.1.0 opening
- **next:** v1.1.0: brainstorm delta, then the design round with the owner
- **last-regression:** PASS @ 2026-10-10 12:25 (docs/regression/REGRESSION.md)

## Modules
| module | nature | depends on | status | last green |
|---|---|---|---|---|
| habit-logic | logic | none | CLOSED 2026-10-09 | `de0156a` |
| app | FE + live composition | habit-logic | CLOSED 2026-10-09: QA PASS, code review solved, security clean, fidelity 6 of 6 at 0 px and 71 of 71 rows, live gate 11 of 11, 176 browser + 99 unit, README, credential gate clean | `9ebc54e` |

## Blockers
none

## Next action
Open docs/v1.1.0/CHANGE-LEDGER.md with the scopes the owner approved at UAT. Then the brainstorm delta (new rows, future-implementation note), then the design round with him: list the designer's job first, five clickable static directions per app, the name and wordmark, the logo in the app, the test-case layout.

## Notes
Goldens (immutable): docs/design/today.html (key), today-empty.html, delete-dialog.html, states.html (specimen sheet), system.md, system.css, sample-history.json, RULINGS.md.
