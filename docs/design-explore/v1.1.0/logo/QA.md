# Logo round 1, QA record, Streaky Habit

Each sheet was rendered by the orchestrator in headless Chromium at 1440 x 900 (console, network, overflow, the production mark alone at 16, 28 and 96 px), then reviewed by a separate `logo-qa` agent against the canon's rubric and the brief's hard constraints. Only a PASS reaches the board.

| Id | Idea | Verdict | Score | Weakest criterion | Risks for the owner |
|---|---|---|---|---|---|
| T1 | The full day | PASS, first review | 22 of 24 | Distinctiveness 1, ownability low (ring and dot is close to a bullseye, a selected radio button, a progress donut) | On a full day the 28 px header mark sits beside the live Overview ring, which draws almost the same picture. Never use it dark on an amber tile (radiation sign orientation) |
| T2 | Another lap | FAIL, RETIRED, first review | 21 of 24 | Scalability 0 (constraint 7). The proof is an over-under crossing, end, gap, over band, gap, under tail, about 10 to 11 px of a 14 px tile at 2 px each. The knockout is 1.05 px at 28 and every favicon gap is 1 px. At 28, 18 and 16 px it reads as a letter O with accents ("ő"), a letter the brief rules out. Structural, the 16 px favicon cannot hold it. Also Apple's Activity rings already own "the end laps the start", and the sources drew below the sheet (3788 px tall) | Not shown on the board. Replaced by T5 |

**T1 production fix, 2026-10-11.** T2's reviewer found T1's two sources also used the `hidden` attribute (3788 px sheet). The orchestrator changed both to `style="display:none"`, nothing else. Re-rendered at 1440 x 900, no console errors, no network.
