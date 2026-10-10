# STATE: streaks

- **project:** Streaks, a daily habit tracker
- **design-phase:** sdlc:design
- **version:** 1.1.0 (1.0.0 sealed 2026-10-10, tag v1.0.0)
- **mode:** greenfield
- **phase:** v1.1.0 design, round 2 (sdlc:design step 4): one new direction F Orbit List from the owner's pick
- **next:** designer builds round-2/f.html, orchestrator writes round-2/compare.html, owner reviews, then lock, compose, wire, goldens
- **last-regression:** PASS @ 2026-10-10 12:25 (docs/regression/REGRESSION.md)

## Modules
| module | nature | depends on | status | last green |
|---|---|---|---|---|
| habit-logic | logic | none | CLOSED 2026-10-09 | `de0156a` |
| app | FE + live composition | habit-logic | CLOSED 2026-10-09: QA PASS, code review solved, security clean, fidelity 6 of 6 at 0 px and 71 of 71 rows, live gate 11 of 11, 176 browser + 99 unit, README, credential gate clean | `9ebc54e` |

## Blockers
none

## Next action
Round 2 is running: one designer builds `docs/design-explore/v1.1.0/round-2/f.html` (F Orbit List) from `round-2/BRIEF.md`. The owner picked D Orbit Rings' look with his own list layout (ledger H-02 ruling, brainstorm "Round 1 rulings"). Then the orchestrator writes `round-2/compare.html` with the ORCH readings flagged, the owner reviews, then sdlc:design steps 5 to 9, the logo with the name "Streaky Habit", then plan. **Start a new Claude session before plan** so sdlc 2.4.0 is loaded (this session runs 2.2.0, the design steps are the same).

## Notes
Goldens (immutable): docs/design/today.html (key), today-empty.html, delete-dialog.html, states.html (specimen sheet), system.md, system.css, sample-history.json, RULINGS.md.
