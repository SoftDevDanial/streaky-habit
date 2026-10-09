# Evidence, regression solver round: app (2026-10-09)

Written by the dev solver for the regression code-review findings (`docs/modules/app/findings/regression-code-review.md`). Test and doc work only: `git diff a3d3ed1 HEAD --stat -- src index.html docs/design README.md docs/progress docs/v1.0.0` is empty. The fidelity and live-gate verdicts stand because `src/` and `index.html` are byte-identical to the tree they ran on.

## Files in this folder

| File | What it is |
|---|---|
| `mutants_output.txt` | The runner's own output: the mutants against the finder's tests (before), against the tests after RG-CR-01 and after RG-CR-02 (the red proofs), and all 21 mutants against the final tests (after) |
| `mutants_solver.py`, `run_mutants_solver.py` | Two extra mutants (`G-499`, `G-501`) and a runner that feeds them to the same earlier `mut.py` as the finder's `run_mutants.py` |
| `evidence.md` | This file |

The finder's runner (`../../regression-code-review/20261009T221155/run_mutants.py`, with its `mutants_regression.py`) was used as it is. Every mutant is served from memory and no project file was written. The "before" runs used a scratch copy of HEAD `a3d3ed1` (`git archive HEAD index.html src tests docs/design`, unpacked in the session scratchpad) because the working tree already held the new tests; its `src/` equals the working tree's (compared ignoring line ends).

## RG-CR-01, the 500 ms edge (WARNING): RESOLVED

Commits: `3c9afdf` test, `e26edaa` qa.md.

What changed:
- `tests/browser/test_delete.py::test_SEC01_R13_a_click_inside_the_window_is_ignored_and_one_after_it_deletes` and `::test_SEC01_R14_the_page_listens_again_once_the_window_has_passed` now run for a mouse and for a touch (the ruling named both). Under the paused clock they press at `GUARD_WINDOW_MS - 1` (ignored; the dialog stays open or the bead stays unticked; `write_count` is 0 and `stored` is the seed) and then after `run_for(1)` (acts; one write). The page-guard test gained `count_writes` and the stored-text check the delete test already had.
- Helpers in the same file: `press_once(page, point, touch)` and `open_by_press(page, name, touch)`; `open_by_mouse` calls the second with a mouse, so the other tests are untouched.
- `tests/browser/conftest.py`: the comment "Keep it equal to DIALOG_GUARD_MS in src/app.js" became the reason the number is written out and not read from `src/` (the finder's fix said it could go once the tests enforce it).
- `qa.md`: the two scenarios became outlines over `mouse` and `touch` at 499 and 1 ms more, and a dated paragraph says why `GUARD_WINDOW_MS` is the spec number.

Red (the finder's mutants, finder's runner, `-k test_delete`, `--maxfail 1000`), at `3c9afdf`:

| Mutant | Before (tests of `a3d3ed1`) | At `3c9afdf` |
|---|---|---|
| G-450 (window 450) | SURVIVED, 65 passed | KILLED, 4 failed (both edge tests, mouse and touch) |
| G-600 (window 600) | SURVIVED, 65 passed | KILLED, 4 failed |
| G-le (`<=`) | SURVIVED, 65 passed | KILLED, 4 failed |
| G-499 (window 499, mine) | SURVIVED, 65 passed | KILLED, 4 failed |
| G-501 (window 501, mine) | SURVIVED, 65 passed | KILLED, 4 failed |

G-499 and G-501 are the closest neighbours of 500. They back the sentence in the `conftest.py` comment that the edge tests fail for any other `DIALOG_GUARD_MS`.

Green: the shipped code passes all four edge tests; `pytest tests/browser` 178 passed at that commit.

The touch variants kill the same mutants as the mouse ones, which shows that the `event.timeStamp` of a touch tap follows Playwright's installed clock the way a mouse click's does. The old touch tests did not show it: they pressed twice at one frozen instant, and two taps made within 500 ms of real time would pass whichever clock the stamps used.

Stability: the four edge cases (two tests, each for a mouse and a touch) and the keyboard test of RG-CR-02 ran together six times in a row before the first commit (5 passed each time), the keyboard test alone ran five more times (passed each time), and the full suite ran seven times across the round (all passed).

## RG-CR-02, Enter on "Delete habit" inside the window (WARNING): RESOLVED for the Delete habit half

Commits: `dd86356` test, `b30c6c8` qa.md and spec.md.

What changed:
- New `tests/browser/test_delete.py::test_SEC01_R13_enter_on_delete_habit_inside_the_window_is_ignored_and_one_after_it_deletes`. Focus the trash button of "Stretch 10 minutes", pause the clock, Enter (the dialog opens, focus on Cancel), Tab (focus on "Delete habit"), Enter at the same instant: the dialog is open, focus is still on "Delete habit", 3 rows, `write_count` 0, `stored` equals the seed. Then `run_for(GUARD_WINDOW_MS)` and Enter: the dialog closes, the rows are "Read 20 pages" and "No phone after 11pm", one write.
- `qa.md`: the matching scenario next to "Enter on Delete habit after the window deletes".
- `spec.md`, the R13 note: one dated sentence (Noted 2026-10-09, RG-CR-02) saying that whether the page guard swallows a keyboard-made click inside its window is left unspecified and no test pins it, because v1.1.0 replaces the time window with a time-free guard. The page guard's keyboard half has no test and no scenario, as ruled.

Red, at `dd86356`:

| Mutant | Before | After |
|---|---|---|
| G-kbd-delete-open (Delete habit held only for `detail > 0`) | SURVIVED, 65 passed | KILLED, 1 failed (the new test) |
| P-kbd-click-passes (page swallows only `detail > 0`) | SURVIVED | SURVIVED, 68 passed: unpinned by ruling |
| G-bubble (capture flag) | SURVIVED | SURVIVED, 68 passed: equivalent today, RG-CR-06 accepted |

Green: the new test passes on the shipped code (five single runs, 0.7 s each, and the full suite, 179 passed at that commit). The new test also kills G-600 and G-le and the 700 ms window, as a side effect (see the table below).

## RG-CR-04, BUILD.md reconcile lists (INFO): RESOLVED

Commit `137e90c`. The `src/app.js` bullet of "For the README reconcile" names `guardDialogClick`, `swallowTapThrough`, `withinGuard` and `DIALOG_GUARD_MS`; the `src/view.js` exports bullet names `confirmButtonOf` (22 names, equal to `grep -n "^export" src/view.js`) and says `containers()` also returns `page`. The SEC-06 sentence "the export list is unchanged" now reads "that change adds no export", so it does not sit over a list that SEC-01 had already changed.

## RG-CR-05, qa.md helper descriptions (INFO): RESOLVED

Commit `1ed506c`. `let_guard_pass` is described as running the clock past the guard window, `GUARD_WINDOW_MS + 100` ms. The same bare 600 stood in the SEC-01 comment on `confirm_delete`, which describes the same helper; it now says the same. The `open_app` row lists `base_url=None, count_writes=False, touch=False` and a dated paragraph says in one sentence what `base_url` and `count_writes` do.

## Mutant table, before and after

Finder's 21 mutants, finder's runner, `-k test_delete`. "Before" is the finder's own run 1 against the tests of `a3d3ed1` (`regression-code-review/20261009T221155/mutants_output.txt`); I re-ran the six survivors and my two extra mutants against those tests myself and got the same verdicts (baseline 65 passed). "After" is my run against the final tests (HEAD `1ed506c`, 68 tests in `test_delete.py`).

| Mutant | Before | After |
|---|---|---|
| G-450 | lived (0 failed) | KILLED, 4 failed |
| G-600 | lived | KILLED, 5 failed |
| G-le | lived | KILLED, 5 failed |
| G-kbd-delete-open | lived | KILLED, 1 failed |
| P-kbd-click-passes | lived | lives (unspecified by ruling) |
| G-bubble | lived, equivalent | lives, equivalent (RG-CR-06 accepted) |
| G-300 | killed, 2 | killed, 4 |
| G-700 | killed, 7 | killed, 10 |
| G-no-open-stamp | killed, 6 | killed, 8 |
| G-open-stamp-once | killed, 5 | killed, 5 |
| P-no-stop | killed, 13 | killed, 14 |
| P-no-prevent | killed, 2 | killed, 2 |
| P-bubble | killed, 13 | killed, 14 |
| P-on-document | killed, 2 | killed, 3 |
| P-stamp-always | killed, 2 | killed, 2 |
| P-stamp-never-on-delete | killed, 2 | killed, 2 |
| P-stamp-only-backdrop | killed, 6 | killed, 6 |
| T-strip-whole | killed, 26 | killed, 26 |
| T-open-lri | killed, 27 | killed, 27 |
| T-close-missing | killed, 26 | killed, 26 |
| T-name-lowercased | killed, 11 | killed, 11 |
| G-499 (mine) | lived | KILLED, 4 failed (at `3c9afdf`) |
| G-501 (mine) | lived | KILLED, 4 failed (at `3c9afdf`) |

21 of the finder's mutants: 15 killed before, 19 killed after. The two that still live are the two the rulings leave alone. No mutant that died before lives now. The failure counts of the killed ones rose or stayed (the touch variants and the keyboard test add tests that notice).

## Suites

| When | `pytest tests/browser -q -p no:cacheprovider` | `node --test "tests/**/*.test.js"` |
|---|---|---|
| Start of the round (HEAD `a3d3ed1`) | 176 passed (the finder's figure, stated in the brief) | 99 pass |
| Before `3c9afdf` (edge tests) | 178 passed in 45.8 s | 99 pass, 0 fail |
| Before `e26edaa` (qa.md) | 178 passed in 45.6 s | 99 pass |
| Before `dd86356` (keyboard test) | 179 passed in 46.2 s | 99 pass |
| Before `b30c6c8` (qa.md, spec.md) | 179 passed in 46.1 s | 99 pass |
| Before `137e90c` (BUILD.md) | 179 passed in 45.9 s | 99 pass |
| Before `1ed506c` (qa.md) | 179 passed in 46.2 s | 99 pass |
| End of the round, HEAD `1ed506c` | 179 passed in 45.9 s, 0 skipped, both conftest servers stopped and refusing connections | 99 pass, 0 fail, 0 skipped |

176 + 2 (the two edge tests now run for touch as well) + 1 (the keyboard test) = 179. Unit tests are unchanged at 99 because `src/` and the habit-logic tests were not touched.

## Credential gate

`python -B {sdlc}/harness/credential_sweep.py --staged` ran from the project root, unpiped, before each of the commits and exited 0 each time (CLEAN, positive control True, negative control 0 false hits).

## Hygiene

- No em dash or en dash, and no non-ASCII byte at all, in anything I added (the diff of the round holds 0 non-ASCII bytes).
- No vendor line or Co-Authored-By in any commit message.
- `README.md`, `src/`, `index.html`, `docs/design/`, `docs/progress/`, `docs/v1.0.0/` and `docs/modules/ROADMAP.md` untouched.
- Files were written with the Write and Edit tools only. The one git operation outside commits was `git archive HEAD ... | tar -x` into the session scratchpad, to run the "before" mutants against the finder's tests.

## Processes

PROCESSES: started, all stopped.
- Every `python -m pytest tests/browser` run without a base URL (the seven full-suite runs and the repeat runs of single tests): each started conftest's two `http.server` children and stopped both at the end, printing that the ports refuse connections.
- Mutant runners: one foreground and three background shells (task ids `b39ebrl4k`, `b4jwx96aj` and a wait loop `bg3c3grgp`), each runner an in-process server thread plus one pytest child per mutant, waited for by the runner; all exited with code 0. The runner kills a hung child by the PID it started and none hung.
- `node --test` runs, all exited.
- Scratch: `git archive | tar` copy of HEAD in the session scratchpad (removed at the end of the round).
- A final sweep by command line at the end of the round is in the report.
