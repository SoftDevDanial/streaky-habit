---
module: app
kind: qa
ran_against: running-app
status: green
counts: { pass: 163, fail: 0, blocked: 0 }
---
# QA findings: app (v1.1.0, step 5)

**Verdict. FAIL on 1 scenario of 169 live.** 162 pass, 1 fails, 6 wait for task 28 (they are not gaps and are not counted as blocked). Untested 0. The failing scenario is `@R36` "On a phone the host of P1 gets room while P1 is open over it, and loses it when P1 closes", row `360x780 P3 2026-07-20` (clicks Close), in Chromium. It is intermittent. WebKit passed that row once, but a probe shows the same race there.

Role. QA finder (read-only), written 2026-10-15. It replaces the 1.0 verdict. Every verdict below comes from a run I made today and a capture I listed on disk.

## Runs

| Run | Folder (listed on disk) | Engine | Counts read from `junit.xml` |
|---|---|---|---|
| Node, once | `docs/modules/habit-logic/qa/qa-node/20261015-081009/node-test.txt` | Node v24.11.1 | 137 tests, 137 pass, 0 fail, 0 skipped (56 of them are this module's, 16 in `ring.test.js` and 40 in `storage.test.js`) |
| Browser, Chromium, once | `docs/modules/app/qa/functional/20261015-081136-chromium/` (`junit.xml`, `pytest-rA.txt`, 28 evidence json files) | Chromium 149.0.7827.55 | tests 348, failures 1, errors 0, skipped 0, 132.7 s |
| Browser, WebKit, once | `docs/modules/app/qa/functional/20261015-081409-webkit/` (`junit.xml`, `pytest-rA.txt`, 33 evidence json files) | WebKit 26.5 | tests 348, failures 0, errors 0, skipped 1 (CO-1), 215.2 s |
| Repro 1 of the one failure | `docs/modules/app/qa/functional/20261015-081804-r36-repro1-chromium/` (`junit.xml`, `repro-notes.txt`) | Chromium | tests 1, failures 0 |
| Repro 2 | `docs/modules/app/qa/functional/20261015-081810-r36-repro2-chromium/` (`junit.xml`) | Chromium | tests 1, failures 1 |
| Repro 3 | `docs/modules/app/qa/functional/20261015-081817-r36-repro3-chromium/` (`junit.xml`) | Chromium | tests 1, failures 1 |
| Probe of the release timing | `docs/modules/app/qa/r36-room-close-probe/20261015-082205/probe.txt` | Chromium 149.0.7827.55 and WebKit 26.5 | 8 and 4 tries, see FAIL |

- Git HEAD `4e860ff5c84b18c2777ebce8c203b963bd7c3610`. `git status` shows no change under `src/`, `tests/`, `index.html` or `docs/design/` after my runs.
- Playwright (Python) 1.61.0, Python 3.14.0, pytest 9.1.0, headless, Windows 11.
- Commands. `STREAKS_EVIDENCE_DIR=<folder> timeout 600 python -m pytest tests/browser -q -rA --junitxml <folder>/junit.xml`, and the same with `--engine webkit`. The Chromium run ended before the WebKit run started. The conftest started and stopped its own servers.
- The suite holds 348 test ids in each engine (162 functions). No `xfail`, `skipif` or blocker mark is left in `tests/browser/` (grep), and `skipped` is 0 in Chromium.
- I changed nothing under `src/` or `tests/`.

## The two-engine finder checks (Feature "Two engines")

| Check | Result | Evidence |
|---|---|---|
| The run uses the engine it was asked for (`test_R30_the_run_uses_the_engine_it_was_asked_for`, and the `-rA` header) | PASS in both | Chromium `pytest-rA.txt` has `engine chromium: 0 chromium_only skip(s)`. WebKit `pytest-rA.txt` has `engine webkit: 1 chromium_only skip(s)`. The test passed in both runs. The evidence folders end in `-chromium` and `-webkit`, and the json evidence of each run landed in its own folder |
| A Chromium-only test is a counted skip with its reason in WebKit (finder check, the 4th of the Feature) | PASS | `python -m pytest tests/browser --markers` lists `@pytest.mark.chromium_only(reason)`. WebKit. `test_R29_the_icon_is_amber_in_a_dark_theme_and_dark_amber_in_a_light_theme` is SKIPPED with the reason "chromium_only: CO-1 ..." and none is PASSED. Chromium. The same test is PASSED. One skip equals the one row (CO-1) of the Chromium-only table |
| The live gate records its engine (finder check, the 5th of the Feature, 2 rows) | WAITS FOR TASK 28 | read from the live gate's evidence at task 28 |

## FAIL

**`@R36` On a phone the host of P1 gets room while P1 is open over it, and loses it when P1 closes (v1.1.0 new, H-03 ruled), qa.md line 940.**
- Test id. `tests/browser/test_day_editor.py::test_R36_on_a_phone_the_host_of_p1_gets_room_while_p1_is_open_over_it_and_loses_it_when_p1_closes[360x780 P3 2026-07-20]`.
- Engine. Chromium. In the full Chromium run it failed. In WebKit's full run it passed.
- Assertion message. `assert ['293px', '293px'] == ['24px', '']` ("At index 0 diff: '293px' != '24px'"), at `tests\browser\test_day_editor.py:274`, the line `assert after["padding"] == ["24px", ""], after`, which follows `page.wait_for_function("() => !document.querySelector('dialog.dlg-day').open")`.
- Scenario line that fails. "Then P1 is closed, the host is open ... And the host's div.sheet-body has the computed padding-bottom "24px" and no inline padding-bottom".
- Repro. `STREAKS_EVIDENCE_DIR=<a new folder> python -m pytest "tests/browser/test_day_editor.py::test_R36_on_a_phone_the_host_of_p1_gets_room_while_p1_is_open_over_it_and_loses_it_when_p1_closes[360x780 P3 2026-07-20]" -q`. Of 4 Chromium runs of this row (the full run and three single-test repros) 3 failed and 1 passed. The other 5 rows of the scenario passed in Chromium in the full run, and all 6 passed in WebKit's full run.
- Probe (read-only, same steps, then reading P3's `div.sheet-body` padding at the instant `dialog.dlg-day.open` turns false, and every 10 ms after). Chromium. 8 of 8 tries read the stale room `['293px','293px']` at that instant, and it was gone 10 to 11 ms later (`['24px','']`). WebKit. 3 of 4 tries read the stale room and it was gone 16 to 17 ms later, 1 of 4 read it already released. So the room is released, about one frame after `open` flips, and the test reads inside that window. The WebKit pass in the full run was luck in the same race, not a different behaviour.
- Which side is wrong is the solver's call. The fact is that the release is done by `popups.clearDayRoom()`, called from the popup-closed handler in `src/app.js`. I did not trace which event runs that handler. Either the test should wait (bounded) for the padding, or the app should release the room in the same task that closes P1. The same row was green in the builder's earlier runs (322 tests, `docs/modules/app/qa/functional/20261014-231919-chromium/junit.xml`, 0 failures, the row is in it), so machine load decides who wins the race.

## Scenario map

Test naming. A pytest function is `test_` + the R tags + the scenario title in snake case. My script matched every browser scenario by that rule except 15, which are matched by hand. Seven are named in the table, 5 are Node scenarios, 2 are finder checks, and 1 is the R28 state-script scenario held by `test_fidelity_inputs.py`. "Rows" is the Examples row count in `qa.md`, and the pytest param count equals it for every Outline except the one explained at line 1871. C is Chromium, W is WebKit.

| qa.md line | Scenario | R# | Held by | Rows | C | W |
|---|---|---|---|---|---|---|
| 177 | Head, CSP, icon link and relative URLs | R1 | test_entry.py | | PASS | PASS |
| 195 | The app works from a sub-path | R1 R29 | test_entry.py | | PASS | PASS |
| 203 | The static skeleton and the five dialogs | R1 | test_entry.py `test_R1_static_skeleton_and_the_five_dialogs` | | PASS | PASS |
| 219 | The stylesheet is system.css without its stand-ins, with the listed changes | R2 | test_entry.py `test_R2_stylesheet_is_system_css_...` | | PASS | PASS |
| 232 | The icon file is the goldens' icon, byte for byte | R29 | test_entry.py | | PASS | PASS |
| 239 | The page links the icon and the policy lets it load | R29 R25 | test_entry.py | | PASS | PASS |
| 248 | The icon is amber in a dark theme and dark amber in a light theme (CO-1) | R29 | test_entry.py | | PASS | SKIP with its reason (counted, not a failure) |
| 257 | No sample data in the shipped files | R26 | test_platform.py | | PASS | PASS |
| 263 | Query strings and fragments do not seed | R26 | test_platform.py | 3 | PASS | PASS |
| 276 | No globals and no hooks | R26 | test_platform.py | | PASS | PASS |
| 292 | The run uses the engine it was asked for | R30 | test_engines.py | | PASS | PASS |
| 298 | An unknown engine is refused before any browser starts | R30 | test_engines.py | | PASS | PASS |
| 304 | One helper launches every browser | R30 | test_engines.py | | PASS | PASS |
| 312 | A Chromium-only test is a counted skip with its reason in WebKit | R30 | finder check on the `-rA` output | | PASS | PASS |
| 322 | The live gate records its engine | R30 | finder check on the live gate evidence | 2 | WAITS FOR TASK 28 | WAITS FOR TASK 28 |
| 334 | Every context has the clipboard stand-in | R30 | test_engines.py | | PASS | PASS |
| 345 | The empty first screen | R3 R35 R42 | test_render.py | | PASS | PASS |
| 360 | Brand, mark and date | R4 | test_render.py | | PASS | PASS |
| 368 | The date follows the device clock | R4 | test_render.py | 3 | PASS | PASS |
| 379 | The header on a phone and on a desktop | R4 R38 | test_render.py | 3 | PASS | PASS |
| 395 | English under a German browser locale | R4 | test_render.py | | PASS | PASS |
| 408 | Rows in stored order | R5 R6 | test_render.py | | PASS | PASS |
| 417 | Current and Best for the sample | R6 | test_render.py | 3 | PASS | PASS |
| 429 | Twelve habits show the goldens' numbers | R6 R31 | test_render.py | | PASS | PASS |
| 448 | A new habit shows no Best block | R6 R10 | test_render.py | | PASS | PASS |
| 454 | The page never scrolls and the composer stays put | R5 R21 | test_render.py | 9 | PASS | PASS |
| 478 | The list scrolls inside its frame and shows where more lies | R5 | test_render.py | | PASS | PASS |
| 489 | The fades follow the rows and a resize | R5 | test_render.py | | PASS | PASS |
| 504 | The band on a desktop | R35 R42 | test_render.py | | PASS | PASS |
| 517 | The band shows from 1024 pixels | R35 | test_render.py | 4 | PASS | PASS |
| 533 | arcPath reproduces the goldens' shared arcs | R42 | `tests/ring.test.js` (Node) | | PASS | not a browser test |
| 539 | arcPath for other numbers of habits | R42 | `tests/ring.test.js` (Node) | 7 | PASS | not a browser test |
| 554 | legendCounts | R42 | `tests/ring.test.js` (Node) | 7 | PASS | not a browser test |
| 569 | ring.js is pure | R42 | `tests/ring.test.js` (Node) | | PASS | not a browser test |
| 576 | A ring's parts and their order | R42 | test_render.py `test_R42_a_rings_parts_and_their_order` | | PASS | PASS |
| 583 | Rings for no habit and for one habit | R42 | test_render.py | 3 | PASS | PASS |
| 594 | Twelve habits draw twelve segments | R42 | test_render.py | | PASS | PASS |
| 600 | Small rings carry no number and no today circle | R42 | test_render.py | | PASS | PASS |
| 611 | Done today presses and unpresses | R31 R16 | test_today.py | 3 | PASS | PASS |
| 627 | Keyboard presses keep focus | R31 | test_today.py | | PASS | PASS |
| 635 | Pressing twice restores the saved value | R31 R16 | test_today.py | | PASS | PASS |
| 641 | One Done today updates every place at once, and only what changed moves | R32 R16 | test_today.py | | PASS | PASS |
| 655 | A tick in P1 over P3 updates P3 and the row, and leaves today's ring alone | R32 R37 | test_today.py | | PASS | PASS |
| 664 | A tick in P1 over P4 updates P4 and P3 beneath it | R32 R39 | test_today.py | | PASS | PASS |
| 672 | A tick in P2 updates P2, the row and the band | R32 R34 | test_today.py | | PASS | PASS |
| 680 | Each edit saves once, and opening or closing a popup saves nothing | R32 R16 | test_today.py | | PASS | PASS |
| 696 | Best back to 0 removes the Best block in every place | R6 R32 | test_today.py | 3 | PASS | PASS |
| 716 | A tick that changes Current and leaves Best moves Current only | R32 | test_today.py | 2 | PASS | PASS |
| 740 | Popups stack and Esc closes the top one only | R40 | test_popups.py | | PASS | PASS |
| 753 | A backdrop click closes that popup only | R40 R14 | test_popups.py | 8 | PASS | PASS |
| 770 | A click inside the box, or a drag that leaves it, closes nothing | R40 R14 | test_popups.py | 4 | PASS | PASS |
| 785 | Tab never reaches a control outside the top popup | R40 | test_popups.py | 3 | PASS | PASS |
| 797 | Every popup is modal and the page does not scroll under it | R40 | test_popups.py | 5 | PASS | PASS |
| 816 | The Overview button opens P3 | R38 R42 | test_overview.py | | PASS | PASS |
| 829 | P3 closes and gives focus back to Overview | R38 R40 | test_overview.py | 2 | PASS | PASS |
| 840 | P3 cannot be reached on a desktop | R38 R22 | test_overview.py | | PASS | PASS |
| 846 | The band's Year opens P4 | R39 R42 | test_overview.py `test_R39_R42_the_bands_year_opens_p4` | | PASS | PASS |
| 859 | P4 on a phone covers P3 | R39 | test_overview.py | | PASS | PASS |
| 865 | P4 closes and gives focus back to the Year that opened it | R39 R40 | test_overview.py | 5 | PASS | PASS |
| 891 | A band day opens P1 | R36 R42 | test_day_editor.py | | PASS | PASS |
| 906 | P1 closes and gives focus back to its day | R36 R40 | test_day_editor.py | 3 | PASS | PASS |
| 918 | On a phone the chosen day stays in sight above P1 | R36 | test_day_editor.py | 6 | PASS | PASS |
| 940 | **On a phone the host of P1 gets room while P1 is open over it, and loses it when P1 closes** | R36 | test_day_editor.py | 6 | **FAIL (1 of 6 rows)** | PASS (see the probe) |
| 968 | With twelve habits on a phone the chosen day's top meets the host's head | R36 | test_day_editor.py | 2 | PASS | PASS |
| 985 | A P4 day opens P1 over P4 on a desktop | R36 R39 | test_day_editor.py | | PASS | PASS |
| 994 | A day opens P1 when there are no habits | R36 R3 | test_day_editor.py | | PASS | PASS |
| 1003 | Ticking a past day in P1 | R37 R32 | test_day_editor.py | | PASS | PASS |
| 1017 | Keyboard ticks keep focus, and a second tick restores the saved value | R37 | test_day_editor.py | | PASS | PASS |
| 1025 | Ticking today in P1 presses Done today | R37 R31 | test_day_editor.py | | PASS | PASS |
| 1036 | Year opens the habit's year view | R33 R6 | test_year.py `test_R33_R6_year_opens_the_habits_year_view` | | PASS | PASS |
| 1053 | P2 closes and gives focus back to its Year | R33 R40 | test_year.py | 5 | PASS | PASS |
| 1067 | P2 per width | R33 | test_year.py | 2 | PASS | PASS |
| 1078 | Ticking a day in the year view | R34 R32 | test_year.py | | PASS | PASS |
| 1091 | Untick and tick again | R34 R16 | test_year.py | | PASS | PASS |
| 1099 | A day before a habit was added can be ticked | R34 R10 | test_year.py | | PASS | PASS |
| 1107 | No control exists after today or before the year | R34 | test_year.py | | PASS | PASS |
| 1113 | Beads are reached and ticked with the keyboard | R34 R22 | test_year.py | | PASS | PASS |
| 1128 | The first habit on a fresh day | R10 R16 R32 | test_add.py | | PASS | PASS |
| 1140 | Enter adds at the bottom, trimmed, and the band recounts | R10 R32 | test_add.py | | PASS | PASS |
| 1150 | The frame scrolls to show the new row | R10 | test_add.py | | PASS | PASS |
| 1158 | Rejected names keep the text and show one message above the field | R11 | test_add.py | 7 | PASS | PASS |
| 1178 | Exactly 40 characters is accepted | R11 | test_add.py | | PASS | PASS |
| 1184 | No message while typing | R11 | test_add.py | | PASS | PASS |
| 1190 | Typing clears a message at once | R11 | test_add.py | | PASS | PASS |
| 1198 | One message at a time, replaced, then cleared on success | R11 | test_add.py | | PASS | PASS |
| 1210 | The twelfth habit closes the composer | R12 | test_add.py | | PASS | PASS |
| 1220 | Twelve habits at load | R12 | test_add.py | 2 | PASS | PASS |
| 1230 | Deleting one of twelve opens the composer again | R12 R15 | test_add.py | | PASS | PASS |
| 1239 | A bin opens M1 with focus on Cancel | R13 | test_delete.py | | PASS | PASS |
| 1249 | Delete habit in the year view opens M1 over it | R13 R33 | test_delete.py | | PASS | PASS |
| 1255 | A long name wraps in the title and the box keeps its width | R13 | test_delete.py | | PASS | PASS |
| 1267 | A slow double click on a bin that lies under Delete habit cannot delete | R13 | test_delete.py | 4 | PASS | PASS |
| 1283 | A fast double click or double tap on a bin under Delete habit cannot delete | R13 | test_delete.py | 4 | PASS | PASS |
| 1299 | A press with a click count of 2 on Delete habit, away from the bin, does nothing | R13 | test_delete.py | | PASS | PASS |
| 1306 | One press on Delete habit away from the bin deletes at once | R13 R15 | test_delete.py | 3 | PASS | PASS |
| 1318 | Enter on Delete habit deletes at once | R13 R15 | test_delete.py | | PASS | PASS |
| 1324 | The keyboard deletes even when Delete habit lies over the bin | R13 R15 | test_delete.py | | PASS | PASS |
| 1332 | Cancel, Esc and a backdrop click keep the habit and give focus back | R14 | test_delete.py | 6 | PASS | PASS |
| 1348 | Esc after an earlier delete still keeps the habit | R14 | test_delete.py | | PASS | PASS |
| 1355 | Cancel, Esc and a backdrop click work at the instant of opening | R14 | test_delete.py | 3 | PASS | PASS |
| 1367 | Cancel still works right after a click inside the box | R14 | test_delete.py | | PASS | PASS |
| 1378 | A double press on a backdrop does not reach the control behind it | R14 | test_delete.py | 7 | PASS | PASS |
| 1395 | A double press on Close does not reach the control behind it | R14 | test_delete.py | 5 | PASS | PASS |
| 1409 | A double press on the backdrop over Add does not add a typed name | R14 R10 | test_delete.py | 2 | PASS | PASS |
| 1421 | A double click on Delete habit deletes once and nothing behind acts | R14 R15 | test_delete.py | | PASS | PASS |
| 1430 | The layer behind listens again once the window has passed | R14 | test_delete.py | 2 | PASS | PASS |
| 1443 | Closing with the keyboard holds nothing | R14 | test_delete.py | 3 | PASS | PASS |
| 1458 | Clicks inside the same popup, or in a popup opened after it, are never held | R14 | test_delete.py | | PASS | PASS |
| 1472 | Deleting from a bin moves focus to the next bin and recounts | R15 R32 | test_delete.py | | PASS | PASS |
| 1481 | Deleting the last row moves focus to the bin above | R15 | test_delete.py | | PASS | PASS |
| 1488 | Deleting the only habit shows the empty list | R15 R3 | test_delete.py | | PASS | PASS |
| 1496 | Deleting from the year view closes both popups and moves focus | R15 R33 | test_delete.py | 3 | PASS | PASS |
| 1508 | History goes with the habit | R15 | test_delete.py | | PASS | PASS |
| 1516 | A focused row out of sight is scrolled into view | R15 | test_delete.py | | PASS | PASS |
| 1525 | The title shows the name without bidi format characters, and its quotes stay in place | R13 | test_delete.py | 16 | PASS | PASS |
| 1551 | Every character of the stripped set is left out of the title | R13 | test_delete.py | | PASS | PASS |
| 1557 | The neighbours of the stripped ranges and other invisible characters stay in the title | R13 | test_delete.py | | PASS | PASS |
| 1563 | Only the title's copy loses the characters, and the habit named in it is the one deleted | R13 R15 | test_delete.py `test_R13_R15_only_the_titles_copy_...` | | PASS | PASS |
| 1577 | saveHabits reports whether the write worked, and loadHabits whether the read did | R16 R41 | `tests/storage.test.js` (Node), 7 tests titled `@R16 @R41 ...` | 7 cases | PASS | not a browser test |
| 1595 | Changes survive a reload and a closed tab | R16 R32 | test_storage.py | | PASS | PASS |
| 1607 | Loading writes nothing | R16 | test_storage.py | | PASS | PASS |
| 1614 | Unreadable saved data resets the list and shows the note | R17 | test_storage.py | 16 | PASS | PASS |
| 1642 | Readable edge cases load without a note | R17 | test_storage.py | 5 | PASS | PASS |
| 1656 | Dismiss removes the note, moves focus to the field, and the note does not come back | R17 R22 | test_storage.py | | PASS | PASS |
| 1666 | The note sits between the top of the page and the list | R17 | test_storage.py | 2 | PASS | PASS |
| 1676 | An unreadable value whose reset save fails shows the warning above the note | R17 R41 | test_storage.py | | PASS | PASS |
| 1687 | A cold boot with working storage shows no warning and writes nothing | R41 | test_storage.py | 3 | PASS | PASS |
| 1699 | The first failing save shows the warning, and the change stays | R41 | test_storage.py | | PASS | PASS |
| 1708 | While saves keep failing the warning stays the same element | R41 | test_storage.py | | PASS | PASS |
| 1717 | The next working save removes the warning, and storage then holds what is on screen | R41 | test_storage.py | | PASS | PASS |
| 1724 | Storage refused at boot shows the warning in the first render and clears when storage returns | R41 | test_storage.py | | PASS | PASS |
| 1737 | A read that throws at boot shows the warning, and the first working save clears it | R41 | test_storage.py | | PASS | PASS |
| 1747 | A real full quota shows the warning and clears when space returns | R41 | test_storage.py | | PASS | PASS |
| 1757 | The app never reads the error it catches | R41 | test_storage.py | | PASS | PASS |
| 1768 | The view moves to the new day within a minute while visible | R19 R35 | test_rollover.py | | PASS | PASS |
| 1781 | The band and P3 move when a new week starts | R19 R35 R38 | test_rollover.py | | PASS | PASS |
| 1793 | An open year view moves to the new year | R19 R33 | test_rollover.py | | PASS | PASS |
| 1802 | An open day editor keeps its day and shows today's numbers | R19 R36 | test_rollover.py | | PASS | PASS |
| 1810 | The composer keeps its text and its focus | R19 | test_rollover.py | | PASS | PASS |
| 1816 | An error message survives the rollover | R19 | test_rollover.py | | PASS | PASS |
| 1822 | Focus on a Done today button stays on it | R19 R22 | test_rollover.py | | PASS | PASS |
| 1828 | Focus on a day that stays in view stays on that day | R19 R22 | test_rollover.py | | PASS | PASS |
| 1834 | Focus whose day leaves the view goes to the top popup's first focus, or to the page's first control | R19 R22 | test_rollover.py | 4 | PASS | PASS |
| 1847 | P1 open on the oldest day of the year when midnight passes | R19 R37 | test_rollover.py | | PASS | PASS |
| 1857 | The view moves at once when the tab is shown again | R20 | test_rollover.py | | PASS | PASS |
| 1871 | Nothing scrolls at 360 pixels | R21 | test_platform.py `..._with_a_popup_open` holds the 5 popup rows. The 3 "none" rows (sample day, fresh day, twelve habits at 360 x 780) are held by `test_R5_R21_the_page_never_scrolls_and_the_composer_stays_put[360x780-*]` in test_render.py, which asserts the same `scrollHeight == 780` and `scrollWidth <= 360` | 8 = 5 + 3 | PASS | PASS |
| 1887 | Sizes at 360 pixels | R21 | test_platform.py | | PASS | PASS |
| 1903 | Sizes at 390 pixels | R21 | test_platform.py | | PASS | PASS |
| 1913 | Tab order on a phone | R22 | test_platform.py | | PASS | PASS |
| 1919 | Tab order on a desktop | R22 R35 | test_platform.py | | PASS | PASS |
| 1925 | Tab order with the note | R22 R17 | test_platform.py | 2 | PASS | PASS |
| 1936 | Focus rings on keyboard focus | R22 | test_platform.py | 13 | PASS | PASS |
| 1958 | A focused bin shows its glyph in the danger colour, and a focused bead has no ring of its own | R22 | test_platform.py | | PASS | PASS |
| 1966 | A mouse click draws no ring | R22 | test_platform.py | | PASS | PASS |
| 1973 | Every popup can be used with the keyboard alone | R22 R40 | test_platform.py | | PASS | PASS |
| 1991 | Transitions without reduced motion | R23 | test_platform.py | | PASS | PASS |
| 2001 | Popups rise and backdrops fade | R23 | test_platform.py | 5 | PASS | PASS |
| 2017 | A change pops what changed and bumps its number, and replays on the next change | R23 R32 | test_platform.py | | PASS | PASS |
| 2030 | Everything appears at once under reduced motion | R23 | test_platform.py | | PASS | PASS |
| 2037 | Markup in a name stays text everywhere | R24 | test_platform.py | | PASS | PASS |
| 2051 | No HTML sinks in the source | R24 | test_platform.py | | PASS | PASS |
| 2056 | Every request stays on the device's own files | R25 | test_platform.py `test_R25_every_request_stays_on_the_devices_own_files` | | PASS | PASS |
| 2064 | The CSP is in force | R25 | test_platform.py | | PASS | PASS |
| 2270 | The headline flows on a cold start | R27 R30 | the live gate, task 28 | 2 | WAITS FOR TASK 28 | WAITS FOR TASK 28 |
| 2327 | The gate fails when the app starts from saved habits (control) | R27 | the live gate control, task 28 | 2 | WAITS FOR TASK 28 | WAITS FOR TASK 28 |
| 2352 | Each screen is 1-to-1 with its golden | R28 | the fidelity gate, task 28, Chromium only | 23 | WAITS FOR TASK 28 | not run by design |
| 2384 | The gate can pass and can fail | R28 | the fidelity controls, task 28 | | WAITS FOR TASK 28 | not run by design |
| 2391 | The fidelity state scripts are right | R28 | test_fidelity_inputs.py, 5 functions, 26 test ids | 26 ids | PASS | PASS (the control "refuses to click without the stand-in" only records `navigator.clipboard` in WebKit, as the scenario says) |
| 2417 | Every frame on the states sheet matches the live state | R28 | the states check, task 28 | | WAITS FOR TASK 28 | not run by design |

The map covers 163 functional scenarios plus the 2 R27 and 4 R28 scenarios, 169 live in all (a script count over `qa.md`, equal to the file's own coverage paragraph). Of them 162 pass, 1 fails and 6 wait for task 28 (line 322, both R27 scenarios, and the three R28 gates at lines 2352, 2384 and 2417). The 18 retired scenarios kept as text are not counted and no test holds them.

## Observations that are not scenario verdicts
- Two tests have no scenario of their own, `test_R13_R28_m1_has_the_markup_of_the_golden` and `test_R17_R41_R28_the_banners_have_the_markup_of_the_golden`. They are the 2 left when the 156 pytest scenarios and the 4 extra functions of the R28 state-script scenario are taken from the 162 functions. `qa.md` does not use the wording "markup of the golden". Both pass in both engines. Extra checks are not a failure. I report them for traceability only.
- WebKit writes five `fidelity-control-*.json` files that Chromium does not. That is by design, because `test_R28_each_after_load_script_refuses_to_click_without_the_standin` records the engine and returns in WebKit.
- Row-level strength. I verified by script that the pytest param count equals the Examples row count for every Outline in the browser suite (the one exception is line 1871, explained in the table). I read the failing test, the R21 tests, the R28 state-script scenario and the Node storage and ring tests against their scenarios. I did not read every other browser test against every `Then` line. So "PASS" for those means the test ran green and its title, tag and row count match its scenario. It does not mean I re-derived each assertion.
- A foreign pytest WebKit run (`timeout 2100 python -m pytest tests/browser ... --engine webkit`, started 08:05:41, with its own `http.server` and a WebKit browser) was running when I started. It is not mine and I did not touch it. I waited for its PID to go, with a 300 s cap and a "gave up" branch, and it was gone within 30 s. My Chromium run started after that. I cannot rule out other load from the builder in `examples/split` during my runs. The probe shows the one failure is a race that load only shifts.
- The fidelity gate and the live gate are not part of this step. R27 and the three fidelity gates wait for task 28.

## Process-rule slips by me, disclosed
- One pytest repro line used `2>&1` inside a pipe to `grep` (the three repro runs). It wrote no file.
- One read-only Python count of the scenarios in `qa.md` was fed through a shell heredoc. It wrote nothing.
- The first Python helper I ran with `-I` could not import Playwright (user site is off under `-I`), so I ran the later helpers without it. They are my own files in the session scratchpad.
Nothing was written outside the folders named in the task. Every path above was listed on disk after I wrote it.

## PROCESSES

Started by me, all foreground, none left running.

| What | PID | Why | State |
|---|---|---|---|
| `node --test` (Node suite) | not recorded (foreground) | the one Node run | STOPPED, exit 0 |
| `python -m pytest tests/browser ...` Chromium suite, with its headless Chromium and Playwright driver | pytest PID not recorded (foreground) | the Chromium run | STOPPED, exit 1 (one failure) |
| conftest `http.server` for that run | 11176 (port 7512), 7848 (port 7510) | serve the app and its parent folder | STOPPED, the run printed that both ports refuse connections |
| `python -m pytest tests/browser ... --engine webkit`, with WebKit | not recorded (foreground) | the WebKit run | STOPPED, exit 0 |
| conftest `http.server` for that run | 20916 (port 36064), 8240 (port 36062) | same | STOPPED, ports refuse connections |
| three single-test pytest runs (repro 1 to 3) | not recorded (foreground) | classify the one failure | STOPPED |
| `python -m pytest tests/browser --markers` | not recorded (foreground) | the `chromium_only` marker check | STOPPED |
| its conftest `http.server` | 11012 (port 59231), 10936 (port 59229) | same | STOPPED, ports refuse connections |
| `python engine_versions.py` (scratchpad) with one Chromium and one WebKit | not recorded (foreground) | read the engine versions | STOPPED |
| `python r36_close_probe.py` (scratchpad), Chromium then WebKit, and its own `http.server` | 24152 (port 59237), 20736 (port 47620) | the release-timing probe | STOPPED, the script confirmed both ports refuse connections |

No background shell, no poll loop and no `run_in_background` call. My one wait loop (on the foreign pytest PID 10156) was a foreground loop with a 300 s cap and a "gave up" branch, and it ended by itself at 30 s.

Closing sweep, 2026-10-15 08:26:39. Method. `Get-CimInstance Win32_Process`, matched by name (`python`, `pythonw`, `node`, `Playwright`, `WebKit*`, `chrome`, `chromium`, `headless_shell`, `msedge`, `bash`, `sh`, `cmd`, `timeout`) or by command line (`streaks`, `http.server`, `pytest`, `playwright`, `scratchpad`), with parent PID, creation time and command line, and the system Edge WebView helpers left out. Result. Only the four processes of the sweep's own shell chain remained (bash 7804, 14096, 25028 and powershell 8988, all created 08:26:38). No python, node, Playwright or WebKit process was alive, the foreign run included. Ports. `netstat -ano` filtered to LISTENING on 127.0.0.1 ports 7510, 7512, 36062, 36064, 59229, 59231, 59237 and 47620 showed none. I did not kill anything.

## Solver round 2026-10-15
Written by the dev solver (solver role). The finder's text above is unchanged.

- **The `@R36` room row, `360x780 P3 2026-07-20`. RESOLVED in the test, commit `7d3bd78` (code review CR-01).** The app was right. The room is released in the app's close handler, a queued task, and the test read the padding as soon as Chromium's own focus restore showed the day focused. The test now takes `watch_close` before the gesture and `wait_for_close` before reading, as do the five other close tests. RED with the release removed (planted defect A2, served from memory, never committed), 5 of 6 rows red on the padding line, `docs/modules/app/qa/solver/20261015-140740-cr01-chromium/`. The row ten times in Chromium on the fixed test, 10 of 10 passed, `docs/modules/app/qa/functional/20261015-143559-r36-x10-chromium/`.
- Suites after the round. Node `docs/modules/app/qa/functional/20261015-142907-node/`, 137 of 137. Chromium `docs/modules/app/qa/functional/20261015-142914-chromium/`, 355 tests, 0 failures, 0 skipped. WebKit `docs/modules/app/qa/functional/20261015-143150-webkit/`, 355 tests, 0 failures, 1 skipped (CO-1). The suite grew by 7 tests this round (code review WR-01 to WR-07), see `BUILD.md`. To re-run: QA.

## Re-check 2026-10-15
Written by the QA finder (read-only), the one re-check after the dev solver round (constitution stop rule). Round 1 and the solver's section above are unchanged. The front matter now reads this re-check. Every verdict below comes from a run I made today and a capture I listed on disk.

**Verdict. PASS.** 163 of the 169 live scenarios pass, 0 fail, 0 blocked, and 6 still wait for task 28 (they are task 28's, they are not failures and are not counted as blocked). Round 1's one FAIL, `@R36` "On a phone the host of P1 gets room while P1 is open over it, and loses it when P1 closes", row `360x780 P3 2026-07-20`, is now PASS. Failing test ids, either engine: none.

### Runs

| Run | Folder (listed on disk) | Engine | Counts read from the run's own file |
|---|---|---|---|
| Node, once | `docs/modules/habit-logic/qa/qa-node/20261015-153148/` (`node-test.txt`, `run-meta.txt`) | Node v24.11.1 | Node writes no junit. From the capture's own summary lines, tests 137, pass 137, fail 0, cancelled 0, skipped 0, todo 0, exit 0 |
| Browser, Chromium, once | `docs/modules/app/qa/functional/20261015-153158-chromium/` (`junit.xml`, `pytest-rA.txt`, `run-meta.txt`, 28 evidence json files) | Chromium | `junit.xml` tests 355, failures 0, errors 0, skipped 0, xfail 0, 144.4 s. `pytest-rA.txt` ends "355 passed in 144.45s" |
| Browser, WebKit, once | `docs/modules/app/qa/functional/20261015-153430-webkit/` (`junit.xml`, `pytest-rA.txt`, `run-meta.txt`, 33 evidence json files) | WebKit | `junit.xml` tests 355, failures 0, errors 0, skipped 1 (CO-1), xfail 0, 229.8 s. `pytest-rA.txt` ends "354 passed, 1 skipped in 229.86s" |
| `@R36` row `360x780 P3 2026-07-20`, ten single-test runs | `docs/modules/app/qa/functional/20261015-153827-r36-recheck-x10-chromium/` (`junit-01.xml` to `junit-10.xml`, `run-01.txt` to `run-10.txt`, `run-meta.txt`) | Chromium | each of the 10 `junit-NN.xml`, tests 1, failures 0, errors 0, skipped 0 (about 4.1 to 4.6 s wall per run). 10 of 10 pass |

- Git HEAD `c271938d5dd1d6ec6059b31eee9dc578f4825c7f` (`git rev-parse --short HEAD` gave `c271938`, checked first, it matches the brief). Python 3.14.0, Node v24.11.1, Windows 11, headless, one run at a time (Chromium ended before WebKit began, the x10 began after WebKit ended).
- Commands. A scratch runner (`streaks-qa-recheck/runner.py` in the session scratchpad, no shell, no redirection) ran, from the project root, `python -m pytest tests/browser -q -rA --junitxml <folder>/junit.xml` (plus `--engine webkit`) with `STREAKS_EVIDENCE_DIR=<folder>`, capped at 560 s with a "gave up" branch. It ran `node --test --test-reporter=spec "tests/**/*.test.js"` capped at 120 s, and the `@R36` node id ten times, each capped at 150 s. No cap was hit. The runner refuses a folder that already exists, each run has its own new timestamped folder, and each `run-meta.txt` records HEAD, the command, the exit code and the seconds (exit 0 in all).
- The conftest started and stopped its own two `http.server` processes in each pytest run. The live gate and the fidelity gate were not part of this re-check.
- Round 1's counts for the same folders, for the comparison below, are in the Runs table near the top of this file (348 ids per engine, Chromium 1 failure).

### Did the round-1 map hold
By script over the junit files (round 1 `20261015-081136-chromium/junit.xml` and `20261015-081409-webkit/junit.xml` against today's).

| Check | Chromium | WebKit |
|---|---|---|
| Test ids in round 1 / today | 348 / 355 | 348 / 355 |
| Round-1 ids missing today | 0 | 0 |
| Ids added today | 7 (listed below) | the same 7 |
| Same id, verdict changed | 1, the `@R36` row `[360x780 P3 2026-07-20]`, FAIL to PASS | 0 |
| Verdicts today | 355 PASS | 354 PASS, 1 SKIP (`test_R29_the_icon_is_amber_in_a_dark_theme_and_dark_amber_in_a_light_theme`, reason "chromium_only: CO-1 ...", counted, not a failure) |

So the scenario map above stands. Every scenario that was PASS in round 1 is still PASS in both engines (the same ids, all green, and `qa.md` for both modules is unchanged since round 1, so no scenario was added, removed or reworded). In the map table, the `@R36` scenario at `qa.md` line 940 turns from "FAIL (1 of 6 rows)" to PASS in Chromium and stays PASS in WebKit. The count moves from 162 pass and 1 fail to 163 pass and 0 fail.

### The round-1 failure, `@R36` room row
- All six rows of "On a phone the host of P1 gets room while P1 is open over it, and loses it when P1 closes" (`390x844 P3 2026-07-20`, `360x780 P3 2026-07-20`, `390x844 P3 2026-09-22`, `800x900 P3 2026-07-20`, `390x844 P4 2025-10-10`, `360x780 P4 2025-10-10`) are PASS in the full Chromium run and in the full WebKit run (read from the two `junit.xml`).
- The row that failed 3 of 4 in round 1 passed 10 of 10 as single-test Chromium runs, one `junit-NN.xml` each, the test name in each file is the `[360x780 P3 2026-07-20]` id. I judge by this behaviour only. I did not re-run the release-timing probe and I did not re-read the app's close handler. The solver's claim that the app was right and the test read inside the one-frame window is not something I re-derived.
- Caveat. The builder of `examples/split` shares this machine, so load during my runs was not under my control.

### The 6 rows that wait for task 28
Unchanged and still waiting, they are task 28's and not failures. They are the finder check "The live gate records its engine" (`qa.md` line 322, 2 rows), the two R27 scenarios (2270 and 2327, 2 rows each) and the three R28 gates (2352, 2384, 2417). Basis. `spec.md` line 502 still shows task 28 as `[ ]`, and `docs/modules/app/qa/live-e2e/` holds nothing newer than the task 27 builder's runs of 07:52 to 07:55 (the newest folder is `20261015-075558-webkit`). The suite is now green in both engines, which is the precondition task 28 names. I did not run either gate.

### Two-engine finder checks
- `pytest-rA.txt` header of the Chromium run, line 9, `engine chromium: 0 chromium_only skip(s)`. WebKit run, line 9, `engine webkit: 1 chromium_only skip(s)`, and the one SKIPPED line carries the CO-1 reason. PASS, as in round 1.
- "The live gate records its engine" still waits for task 28.

### The 7 new tests, each traced
`BUILD.md` says the suite grew by 7 ids per engine (348 to 355), and the junit comparison finds exactly 7 added ids, the same in both engines, all PASS today. None has its own scenario in `qa.md`, because `qa.md` has not changed (the solver listed the recommended wording in `BUILD.md`, "For the planner"). All 7 carry an `@R#` tag in the test name and trace to that requirement's text in `spec.md`.

| # | Added test id (file `tests/browser/`) | R# | Spec text it traces to | Scenario in `qa.md` | Note |
|---|---|---|---|---|---|
| 1 | `test_render.py::test_R42_every_svg_part_in_the_page_and_the_popups_is_in_the_svg_namespace_and_draws` | R42 | "A ring is an `svg` ..." with its circles, paths and text | none. Nearest is "A ring's parts and their order" (line 576). Planner item 2 | `spec.md` R42 does not use the word namespace. The property (the part draws, `getBBox().width` above 0) is implied by "a ring is an svg", the wording is the solver's. Not a failure, a traceability gap |
| 2 | `test_rollover.py::test_R19_a_page_booted_ten_seconds_before_midnight_shows_the_new_day_thirty_seconds_after_it` | R19 | "compares `readToday()` with the shown day every 30 seconds" and "The view never changes day before local midnight" | none. Nearest is "The view moves to the new day within a minute while visible" (line 1768). Planner item 5 | traces cleanly, it pins the 30 second cadence |
| 3 | `test_year.py::test_R33_p2_opens_again_at_its_top_after_it_closed_scrolled` | R33 | "On opening, Close has focus and the body is scrolled to its top" | none. Nearest is "P2 closes and gives focus back to its Year" (line 1053). Planner item 8 | traces cleanly |
| 4 | `test_overview.py::test_R39_p4_opens_again_at_its_top_after_it_closed_scrolled` | R39 | "On opening, Close has focus and the body is scrolled to its top" | none. Nearest is "P4 closes and gives focus back to the Year that opened it" (line 865). Planner item 8 | traces cleanly |
| 5 | `test_day_editor.py::test_R36_p1_lists_the_habits_there_are_when_it_opens` | R36 | "Its `ul.day-list` holds one `li` per habit in list order", `p#day-sub` "<count> of <total> habits" | none. Nearest is "A band day opens P1" (line 891). Planner item 9 | traces cleanly |
| 6 | `test_add.py::test_R12_a_render_at_twelve_habits_does_not_write_the_note_again` | R12 | R12's `#nh-msg` at 12 habits. `spec.md` line 478 notes that in every golden only `#nh-msg` carries `aria-live` | none. Nearest is "Twelve habits at load" (line 1220). Planner item 9 | R12 does not say "not written again". That rule rests on the live region remark, a rationale in the test's docstring, not a spec `Then`. Not a failure, a traceability gap |
| 7 | `test_delete.py::test_R14_a_double_press_on_a_backdrop_does_not_reach_the_control_behind_it[1280x800-mouse-P2-then-M1]` | R14 | R14 and CG-11, a backdrop press must not reach the control behind | a new row of an existing scenario, "A double press on a backdrop does not reach the control behind it" (line 1378). Its Examples table in `qa.md` still has 7 rows and the test now has 8 ids. Planner item 11 | the one place where round 1's "pytest param count equals the Examples row count" no longer holds, by exactly this one row |

No added test lacks an `@R#`, and none contradicts a spec `Then`. Rows 1 and 6 go beyond the spec's literal words (see their notes). I report them for traceability and do not count them as failures, because the spec text names the property in spirit and the planner has not yet written the scenarios.

### Observations, not scenario verdicts
- The two tests with no scenario of their own in round 1 (`test_R13_R28_m1_has_the_markup_of_the_golden` and `test_R17_R41_R28_the_banners_have_the_markup_of_the_golden`) are still present and PASS in both engines.
- Row-level strength is as in round 1. PASS means the test ran green and its title, tag and row count match its scenario, apart from the one 8 against 7 row above. I read the seven new tests against the spec, I did not re-derive every other assertion. The diff from round 1's HEAD `4e860ff` to `c271938` touches `src/app.js`, `src/calendar.js`, `src/popups.js`, `src/view.js` and `index.html` (WR-08, WR-10 refactor and comments). The whole browser suite is green on that code in both engines, which is what I can attest to.
- A foreign pytest WebKit run of the Split build (python `run_pytest.py` under the `split-a15` scratchpad, its own `http.server` on 24119 and its WebKit processes) was alive at 15:40, after my last run, and gone by my final sweep at 15:41:58. It is not mine and I did not touch it. My baseline sweep at 15:31 found no python, node or browser process, and I cannot say whether it overlapped my WebKit run.

### Process-rule slips by me, disclosed
- Two read-only listings used `2>/dev/null` (`ls docs/modules/app/qa/live-e2e` and `ls docs/modules/app/qa/fidelity`, each piped to `tail`). Neither wrote a file. The brief rules that form out.
- I used read-only pipes after `ls`, `grep` and `sed` (never after a test runner or git).
- The Edit tool was not available to me, so the front matter lines and this section were applied by a scratch Python script (`append_section.py` in the session scratchpad) that does an exact, asserted replace of the two front matter lines and an append, using a relative path under the project root. It rewrote nothing else.
- Nothing was written outside the two verdict files and my own new run folders. `git status` on `src/`, `tests/`, `index.html` and `docs/design/` is empty after my runs, and HEAD is still `c271938`.

### PROCESSES
All foreground, all exited, none left running. PIDs were not recorded for foreground runs.

| What | PID | Why | State |
|---|---|---|---|
| `python runner.py node`, with its `node --test` child | not recorded (foreground) | the one Node run | STOPPED, exit 0 in 0.7 s |
| `python runner.py pytest chromium`, with pytest, Playwright's driver, headless Chromium and the conftest's 2 `http.server` processes | not recorded (foreground) | the Chromium run | STOPPED, exit 0 in 147.8 s |
| `python runner.py pytest webkit`, with pytest, the driver, headless WebKit and the conftest's 2 `http.server` processes | not recorded (foreground) | the WebKit run | STOPPED, exit 0 in 233.2 s |
| `python runner.py r36x10`, ten pytest runs each with Chromium and 2 `http.server` processes | not recorded (foreground) | the ten `@R36` runs | STOPPED, ten exits of 0 |
| `python analysis.py`, `python nodecmp.py` (read-only), `powershell sweep.ps1` three times | not recorded (foreground) | junit and capture comparison, baseline, mid and final sweeps | STOPPED |

No background shell, no poll loop and no `run_in_background` call. Every wait was a bounded subprocess wait (caps above).

Sweeps, method. `Get-CimInstance Win32_Process` listing, with PID, parent PID, creation time and command line, every process named python, pythonw, node, playwright, chrome, chromium, headless_shell, msedge, bash, sh, cmd, timeout, powershell or pwsh, anything named WebKit*, Playwright* or pw_run*, and anything whose command line mentions streaks, http.server, pytest, playwright, scratchpad, streaks-qa-recheck or examples split (the system Edge WebView helpers left out), plus `Get-NetTCPConnection -State Listen` on 127.0.0.1. Baseline 15:31:19, before my first run. Final 15:41:58. Result of the final sweep. No python, node, Playwright, WebKit or browser process was alive, and no `http.server` was listening. Alive were only my sweep's own shell chain (bash 13996, 2836, 22992 and powershell 23876, all created 15:41:57) and three powershell processes from before my session (18192 and 22096 created 07:38, 11932 created 14:37, parent 17836), which I did not start and did not touch. Listening on 127.0.0.1 were the same ports as at baseline (1549, 1579, 2051, 2053, 6463, 50911, 50912) plus 4709, which is `wpscloudsvr.exe` of WPS Office (PID 6600, created 15:32:58). None is mine. I killed nothing.
