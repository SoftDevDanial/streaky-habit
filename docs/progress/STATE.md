# STATE: streaks

- **project:** Streaks, a daily habit tracker
- **design-phase:** sdlc:design
- **version:** 1.0.0
- **mode:** greenfield
- **phase:** uat: owner verdicts recorded, 7 of 7 PASS; seal waits for his word
- **next:** seal on his word, then v1.1.0
- **last-regression:** PASS @ 2026-10-10 12:25 (docs/regression/REGRESSION.md)

## Modules
| module | nature | depends on | status | last green |
|---|---|---|---|---|
| habit-logic | logic | none | CLOSED 2026-10-09 | `de0156a` |
| app | FE + live composition | habit-logic | CLOSED 2026-10-09: QA PASS, code review solved, security clean, fidelity 6 of 6 at 0 px and 71 of 71 rows, live gate 11 of 11, 176 browser + 99 unit, README, credential gate clean | `9ebc54e` |

## Blockers
none

## Next action
Waiting on the owner: the seal of v1.0.0, his yes on UAT-F2 (edit past days) and UAT-F4 (label Current and Best) for 1.1.0, his confirmation of the name "Streaky Habit" after the name check, H-01, D-01, the UAT-06 pause question, and what the five designs cover. v1.1.0 candidates: the time-free trash guard, UAT-F2, UAT-F4, the rename, the logo in the app, a livelier design in a design round with him. Server pid 12828 on 8731 still up until he is done.

## Notes
Goldens (immutable): docs/design/today.html (key), today-empty.html, delete-dialog.html, states.html (specimen sheet), system.md, system.css, sample-history.json, RULINGS.md.
