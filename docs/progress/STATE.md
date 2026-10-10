# STATE: streaks

- **project:** Streaks, a daily habit tracker
- **design-phase:** sdlc:design
- **version:** 1.1.0 (1.0.0 sealed 2026-10-10, tag v1.0.0)
- **mode:** greenfield
- **phase:** v1.1.0 design, steps 5, 6 and 8 composed (final/ committed), step 7 wire and verify next
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
Composer done: `docs/design-explore/v1.1.0/final/` (system.md, system.css, 9 goldens with .md: today, day-editor, year-view, overview, overview-year, delete-dialog, today-empty, today-full, states; sample-history.json, MANIFEST.md, LINKS.json, SELF-CRITIQUE.md, checks). **Before step 7, fix the composer's two shortcuts** (overview.html and overview-year.html draw K1 underneath without its band, 5 px slivers at 1280; states.html style block is a subset of system.css). Then run `flowcheck_v.py streaks v1.1.0`, put SELF-CRITIQUE's copy list and seven interaction rules to the owner, plus three for his ruling (horizontal ink of numbers with a "1" up to 1.05 px left, desktop day cells under 44 px inherited from f2, the phone header top at 8 px without the tab). Then logo redraw, then the finalize gate (his approval AND his word to replace 1.0's goldens).

## Notes
Goldens (immutable): docs/design/today.html (key), today-empty.html, delete-dialog.html, states.html (specimen sheet), system.md, system.css, sample-history.json, RULINGS.md.
