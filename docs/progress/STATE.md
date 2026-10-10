# STATE: streaks

- **project:** Streaks, a daily habit tracker
- **design-phase:** sdlc:design
- **version:** 1.1.0 (1.0.0 sealed 2026-10-10, tag v1.0.0)
- **mode:** greenfield
- **phase:** v1.1.0 design, steps 5 to 8 (lock, compose, wire, self-critique) from the accepted F2
- **next:** composer builds docs/design-explore/v1.1.0/final/ (system, goldens, manifest, links, self-critique), orchestrator wires and drives the flow (step 7), owner approves the set and the replacement of 1.0's goldens, logo redraw swapped in, finalize, then plan
- **last-regression:** PASS @ 2026-10-10 12:25 (docs/regression/REGRESSION.md)

## Modules
| module | nature | depends on | status | last green |
|---|---|---|---|---|
| habit-logic | logic | none | CLOSED 2026-10-09 | `de0156a` |
| app | FE + live composition | habit-logic | CLOSED 2026-10-09: QA PASS, code review solved, security clean, fidelity 6 of 6 at 0 px and 71 of 71 rows, live gate 11 of 11, 176 browser + 99 unit, README, credential gate clean | `9ebc54e` |

## Blockers
none

## Next action
One composer agent builds `docs/design-explore/v1.1.0/final/` from `v1.1.0/COMPOSE-BRIEF.md` (F2 accepted, ledger S7 row 6, H-02 final ruling). Rulings for the step: the 2.97 pair lifted, every number centred by its ink (rings done in f2, P2 beads still about 0.7 px low on a phone), the header mark kept swappable for the logo redraw. Then the orchestrator wires `final/` into `v1.1.0/prototype/` and drives `final/LINKS.json` (flowcheck adapted to v1.1.0 paths), writes `v1.1.0/FLOW-CHECK.md`, and puts the set to the owner. **Finalize writes `docs/design/`, which holds 1.0's immutable goldens. Replacing them needs the owner's explicit word** (1.0's stay in tag v1.0.0). Logo redraw with "Streaky Habit" before finalize so the goldens carry the new mark.

## Notes
Goldens (immutable): docs/design/today.html (key), today-empty.html, delete-dialog.html, states.html (specimen sheet), system.md, system.css, sample-history.json, RULINGS.md.
