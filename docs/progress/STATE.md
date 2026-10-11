# STATE: streaks

- **project:** Streaks, a daily habit tracker
- **design-phase:** sdlc:design
- **version:** 1.1.0 (1.0.0 sealed 2026-10-10, tag v1.0.0)
- **mode:** greenfield
- **phase:** v1.1.0 design, step 7 wired and verified (FLOW-CHECK 49 of 49), owner's rulings next
- **next:** owner rules on the composer's copy list, seven interaction rules and three open points (v1.1.0/RULINGS.md), logo redraw swapped in, finalize gate (his approval AND his word to replace 1.0's goldens), then plan
- **last-regression:** PASS @ 2026-10-10 12:25 (docs/regression/REGRESSION.md)

## Modules
| module | nature | depends on | status | last green |
|---|---|---|---|---|
| habit-logic | logic | none | CLOSED 2026-10-09 | `de0156a` |
| app | FE + live composition | habit-logic | CLOSED 2026-10-09: QA PASS, code review solved, security clean, fidelity 6 of 6 at 0 px and 71 of 71 rows, live gate 11 of 11, 176 browser + 99 unit, README, credential gate clean | `9ebc54e` |

## Blockers
none

## Next action
Step 7 done. `docs/design-explore/v1.1.0/FLOW-CHECK.md` 49 of 49 links, zero errors, prototype in `v1.1.0/prototype/`. Orchestrator fixes in final/ (ledger S7 rows 7 and 8). K1 under P3 and P4 is today.html's K1 with its band, states.html inlines system.css, the Overview button's name is an aria-label (Chromium read "Overview , today ..."). check.py 97 of 97. Next, put SELF-CRITIQUE's copy list, its seven interaction rules and three open points (horizontal ink of numbers with a "1" up to 1.05 px left, desktop day cells under 44 px inherited from f2, the phone header top at 8 px) to the owner and record his answers in `docs/design-explore/v1.1.0/RULINGS.md`. Then logo redraw ("Streaky Habit", swap the one inline mark svg and the favicon), then the finalize gate.

## Notes
Goldens (immutable): docs/design/today.html (key), today-empty.html, delete-dialog.html, states.html (specimen sheet), system.md, system.css, sample-history.json, RULINGS.md.
