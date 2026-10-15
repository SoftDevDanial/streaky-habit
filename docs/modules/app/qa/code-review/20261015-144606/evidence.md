# Code review re-check evidence, app, v1.1.0 step 5

Written by the code-review finder (read-only), 2026-10-15. HEAD `c271938`, the solver round `4e860ff..c271938`. The verdict is the section "Re-check 2026-10-15" of `docs/modules/app/findings/code-review.md`. This folder is the record of the runs behind it.

## What was run, and where
- A throwaway copy of `c271938`, made with `git -c core.autocrlf=false archive -o <scratchpad>/cr-recheck/streaks-c271938-lf.tar c271938` and extracted in the session scratchpad (`cr-recheck/copy-lf`). Nine files were checked equal to the commit's blobs with `git hash-object --no-filters` (`index.html`, `src/app.js`, `view.js`, `calendar.js`, `popups.js`, `habits.js`, `dates.js`, `tests/browser/conftest.py`, `tests/purity.test.js`).
- Each mutant was served from memory by round 1's runner (`docs/modules/app/qa/code-review/20261015-125001/tools/mutrun.py.txt`, unchanged) or by `tools/mutrun2.py.txt`, which wraps it and only reads pytest's failing lines whole. The copy's own pytest suite ran against the server through `STREAKS_BASE_URL`. No file of the repository and no file of the copy's `src/` was written.
- Two probe files were added to the copy only (`probes/*.py.txt`, kept with a `.txt` ending so no pytest run collects them). The full-suite runs left both out with `--ignore`.
- The copy's live gate ran once unmutated (round 1's `gaterun.py`) and once with the clipboard stand-in removed (`tools/gate_nostandin.py.txt`). Both wrote their evidence inside the copy.
- In `runs.txt` some command lines name a mutant by the short part of its id (B1 for `B1-svg-in-html-namespace`). The definitions are `mutants/recheck-browser.json` and `mutants/recheck-more.json`.

## Controls
- The 22 targeted test functions (58 rows) unmutated, green in Chromium and WebKit.
- The whole browser suite at `c271938`, Chromium 354 passed and 1 skipped (the sub-path test, the runner names a base URL), WebKit 353 passed and 2 skipped (that one and CO-1).
- The live gate unmutated, GATE PASS, 21 of 21 steps.
- The `@R36` room test 8 more times in Chromium, 48 of 48 rows green (10 runs in all with the control and the full suite).
- Unit suite at `c271938`, 137 of 137 (the habit-logic evidence of this re-check).

## Results at c271938 (Chromium unless named)
| Round-1 finding | Mutant | Result |
|---|---|---|
| CR-01 | A2 (room never released) | KILLED 5 of 6 rows in Chromium and in WebKit, each on `test_day_editor.py` line 285, `after["padding"] == ["24px", ""]`. The 800x900 row has no room by design |
| CR-01 | A16 (`is-open` kept) | KILLED 3 of 3 |
| WR-06, WR-12 | A1 (no app focus on a connected opener) | SURVIVED 30 of 30 rows of the 7 close-focus test functions in Chromium. KILLED 30 of 30 in WebKit, "Locator expected to be focused" |
| WR-01 (a) | B1 (every created svg part in the HTML namespace) | KILLED, 9 tests of `test_render.py`, the new test on "the band's ring for today draws nothing" |
| WR-01 (a) | B1b, new (only the sprite `use` of `icon` in the HTML namespace) | KILLED by the new test, 9 nodes out of the namespace |
| WR-01 (b) | B3 (Dismiss saves) | KILLED, "Dismiss saved" |
| WR-01 (b) | B4 (a rejected name saves) | KILLED 7 of 7 rows, `write_count(page) == 0` |
| WR-01 (c) | A51 at 45, 60, 85 and 115 s | KILLED all four, and 45 s in WebKit |
| WR-02 | A11 (every bead pops) | KILLED in both engines |
| WR-02 | A11g, new (a bead whose thread changed pops) | KILLED in both engines, `['2026-10-08', '2026-10-09']` |
| WR-02 | A11b (every tick pops) | KILLED in both engines |
| WR-03 | A65 (legend drawn once) | KILLED on the add and bin-delete rows, the only-habit row passes (its legend was drawn for 0 at boot) |
| WR-03 | A65c, new (legend never drawn again for fewer habits) | KILLED on the bin-delete row and the only-habit row |
| WR-04 | A17 (no scroll to top) | KILLED both new tests in both engines |
| WR-05 (a) | A60 (P1's list built once) | KILLED on the reopen after the add |
| WR-05 (b) | A9 (the note written on every render) | KILLED |
| WR-07 | P-G0 (nothing held) | KILLED 8 of 8 rows, the new row included |
| WR-07 | P-G1 (only the page held) | KILLED the two P3 rows and the new row, in both engines |
| WR-07 | A50 (`stopPropagation`) | SURVIVED 8 of 8, equivalent as ruled |
| WR-11 | the stand-in removed | `test_R30_every_context_has_the_clipboard_stand_in` red "navigator.clipboard is the browser's own", the gate red at step 01 first visit on its stand-in line |

## WR-11 probe
`STANDIN_IN_PLACE_JS` gives, in both engines, true with the stand-in, false without it, true with `writeText` removed (no TypeError, the ruled answer), true with `writeText` removed and the stand-in after it, and true with `navigator.clipboard` removed. `live_e2e.SNAPSHOT_JS` holds the text `standIn: (` + the same predicate + `)()`, so the gate and pytest give one answer.

## Static reads
- `src/` diff `4e860ff..c271938`. `calendar.js` loses `dayUnit` and `icon` (bodies unchanged in `view.js`), `popups.js` and `view.js` change one import line each, `app.js` computes `doneFlags(habits, todayKey)` once and passes it to `renderRows`, `syncRow` reads `String(doneToday)`. `doneFlags` is `habits.map((habit) => habit.done.includes(dateKey))`, so the value is the one `done.includes(todayKey)` gave. One comment changed in `guardTapThrough`, none of its code.
- `grep -rn "is the app's\|are the app's" tests/browser` gives five comments after `wait_for_close(watch)` (and one unrelated line in `test_entry.py`). `git log -S` puts two of the phrasings, four of the comments, in `7d3bd78`. The fifth, in `test_popups.py`, is older (WR-12).
