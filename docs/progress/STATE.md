# STATE: streaks

- **project:** Streaks, a daily habit tracker
- **design-phase:** sdlc:design
- **version:** 1.1.0 (1.0.0 sealed 2026-10-10, tag v1.0.0)
- **mode:** greenfield
- **phase:** v1.1.0 design, round 2 (sdlc:design step 4): F2 built and verified, compare page written, waiting for the owner
- **next:** owner reviews round-2/compare.html (pick F2 or more notes), then lock, compose, wire, goldens
- **last-regression:** PASS @ 2026-10-10 12:25 (docs/regression/REGRESSION.md)

## Modules
| module | nature | depends on | status | last green |
|---|---|---|---|---|
| habit-logic | logic | none | CLOSED 2026-10-09 | `de0156a` |
| app | FE + live composition | habit-logic | CLOSED 2026-10-09: QA PASS, code review solved, security clean, fidelity 6 of 6 at 0 px and 71 of 71 rows, live gate 11 of 11, 176 browser + 99 unit, README, credential gate clean | `9ebc54e` |

## Blockers
none

## Next action
Waiting for the owner's review of `docs/design-explore/v1.1.0/round-2/compare.html` (round 1 D, F, F2 with every reading flagged, orchestrator's pick F2, ledger S7 row 5, H-02 round 2 recommendation). If he accepts F2, run sdlc:design steps 5 to 9 (lock the system with AA ratios, decide the 2.97 pair, compose every screen and state, wire and verify, self-critique, finalize goldens), then the logo with the name "Streaky Habit", then plan on sdlc 2.4.0.

## Notes
Goldens (immutable): docs/design/today.html (key), today-empty.html, delete-dialog.html, states.html (specimen sheet), system.md, system.css, sample-history.json, RULINGS.md.
