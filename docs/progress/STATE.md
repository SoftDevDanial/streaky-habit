# STATE: streaks

- **project:** Streaks, a daily habit tracker
- **design-phase:** sdlc:design
- **version:** 1.1.0 (1.0.0 sealed 2026-10-10, tag v1.0.0)
- **mode:** greenfield
- **phase:** v1.1.0 design, round 2 (sdlc:design step 4): revision F2 Orbit List, revised, from the owner's review of F
- **next:** designer builds round-2/f2.html, orchestrator writes round-2/compare.html, owner reviews, then lock, compose, wire, goldens
- **last-regression:** PASS @ 2026-10-10 12:25 (docs/regression/REGRESSION.md)

## Modules
| module | nature | depends on | status | last green |
|---|---|---|---|---|
| habit-logic | logic | none | CLOSED 2026-10-09 | `de0156a` |
| app | FE + live composition | habit-logic | CLOSED 2026-10-09: QA PASS, code review solved, security clean, fidelity 6 of 6 at 0 px and 71 of 71 rows, live gate 11 of 11, 176 browser + 99 unit, README, credential gate clean | `9ebc54e` |

## Blockers
none

## Next action
Round 2 revision is running: one designer builds `docs/design-explore/v1.1.0/round-2/f2.html` (F2 Orbit List, revised) from `round-2/BRIEF-F2.md`. The owner reviewed F (ledger H-02 round 2 ruling, S7 row 4, S1 row 3, brainstorm "Round 2 rulings"): the overview stays 12 weeks with a Year button that opens P4, a year view of the last 12 months with every habit together (desktop and phone), and a delete button on every habit row. F `f.html` stays as the record. Then the orchestrator writes `round-2/compare.html` (round 1 D, F and F2, readings (a) to (h) flagged), the owner reviews, then sdlc:design steps 5 to 9, the logo with the name "Streaky Habit", then plan on sdlc 2.4.0.

## Notes
Goldens (immutable): docs/design/today.html (key), today-empty.html, delete-dialog.html, states.html (specimen sheet), system.md, system.css, sample-history.json, RULINGS.md.
