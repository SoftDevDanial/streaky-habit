# Code review evidence: app

Run 20261009-154715. Written by the code-review finder (read-only). Project HEAD `0590636`, branch main. Nothing under `src/`, `tests/`, `index.html` or `docs/design/` was changed (`git status` was clean before and after). The verdict is `../../../findings/code-review.md`.

## Method

1. Read the spec (R1 to R28, Contracts, threat model, non-goals), `qa.md`, `BUILD.md`, the QA verdict and every changed file of `git diff 127104a..HEAD -- index.html src tests`.
2. Reverse audit of every function in `src/app.js`, `src/view.js`, `src/storage.js` against an R# or a recorded BUILD judgment call (JC).
3. CSS fidelity check, independent of the test (`css_diff.py`, `byteid.py`).
4. Mutation testing. A throwaway copy of `index.html`, `src/`, `tests/` and `docs/design/` was made in the session scratchpad (`cp -r`). Mutants are applied **in memory** by a small static server (`mut.py`, port 0 on 127.0.0.1, a thread of the runner), so no file of the copy or of the repo is written. The unchanged suite (`python -m pytest tests/browser`) runs against the served mutant, one pytest child per mutant. A mutant whose patch text does not occur exactly once stops the runner (no fake survivors).
5. Behaviour probes (`probe.py`) on the pristine app and on each surviving mutant, to prove that a survivor is a real behaviour change and not an equivalent mutant.

Commands (scratch layout: `<sp>/work` is the copy, scripts are in `<sp>`):

```
python mut.py <sp>/work baseline 1000
python mut.py <sp>/work <id,id,...> 4            # mutants.py
python -c "<point mutants.MUTANTS at mutants_extra.MUTANTS, then run mut.py>"   # mutants_extra.py
python probe.py <sp>/work pristine,<id,id,...>
node decode-unit.mjs <project root>
```

The copies in this folder are the code that ran, with these differences only: `probe.py` has the two later probes merged in place, `css_diff.py` leaves out a comparison with `system.css` (which holds tokens only and was not needed), `mutants_extra.py` and `dialog_rv.py` have a longer docstring.

## Baseline

`pristine copy: 114 passed, 1 skipped in 24.06s` (the skip is the sub-path test, no second server, so 114 plus 1 equals the 115 of BUILD.md and QA). `node --test "tests/**/*.test.js"`: 66 pass, 0 fail.

## Mutation results

34 mutants run. 5 killed, 29 survived. Of the survivors, 5 are equivalent or an invalid control of mine (C3, E1, E2, E3, and S4 in the browser). The other 24 are real holes in the tests.

Killed.

| Id | Change | Failing tests |
|---|---|---|
| C1-interval-300s | rollover interval 300000 ms (the builder's own control) | 4 of test_rollover.py (R19), stopped at maxfail 4 |
| C2-hook-on-window | `window.__hook = boot` | test_R26_no_globals_and_no_hooks |
| A8-backdrop-release-only | close on the release point alone | test_R14_clicks_inside_the_box_and_drags_out_of_it_keep_the_dialog_open |
| E4-prevent-default-dropped | add form submit not `preventDefault()`ed | 4 of test_add.py (stopped at maxfail 4) |
| E5-rollover-rebuilds-rows | `checkDay` calls `renderHabits()` | test_R19_focus_on_todays_bead_stays_on_todays_bead |

Survived. "Probe" is what `probe.py` observed, pristine versus mutant.

| Id | Change | Verdict | Probe (pristine versus mutant) |
|---|---|---|---|
| A1-cancel-resaves | keep path (Cancel, Esc, backdrop) saves the unchanged habits | real hole (QA N2) | 0 writes pristine. Mutant 1 write per keep path (3 in total; counts lag one step because the dialog `close` event is queued) |
| A2-reject-resaves | a rejected name saves | real hole (N2) | pristine 0, mutant 1 |
| A3-rollover-saves | the day rollover saves | real hole (N2, QA M22) | pristine 0 after rollover, mutant 1 |
| A4-dismiss-saves | Dismiss saves | real hole (N2) | pristine 0, mutant 1 |
| S1-no-sort-no-dedupe | decode keeps `done` as stored | real hole (N3, QA M10) | after a tick on another habit, stored `A.done` pristine `['2026-10-07','2026-10-08']`, mutant `['2026-10-08','2026-10-07','2026-10-08']` |
| S2-dedupe-only | decode de-duplicates, no sort | real hole | mutant `['2026-10-08','2026-10-07']` |
| S3-sort-only | decode sorts, no de-duplication | real hole | mutant `['2026-10-07','2026-10-08','2026-10-08']` |
| S4-parsed-object-reused | decode returns the parsed object | equivalent in the browser | `encodeState` rebuilds `{name, done}` anyway. Only a unit test of `decodeState` can tell (`decode-unit.mjs`) |
| S5-first-date-only | only `done[0]` is validated | real hole | `done:["2026-10-08","2026-02-30"]`: pristine shows the note and resets, mutant loads one row and keeps the bad date in storage |
| S6-duplicate-vs-previous-only | duplicate name only checked against the previous entry | real hole | `A, B, a`: pristine unreadable and reset, mutant loads 3 rows |
| A5-add-moves-focus | a successful add focuses the input | real hole (N5, R10) | after clicking Add: pristine focus on the Add button, mutant on `#new-habit` |
| A7-backdrop-press-only | close if the press began on the backdrop, whatever the release point | real hole (R14) | press at (5,5), release on the title: pristine dialog stays open, mutant closes |
| A6-interval-60s | rollover cadence 60 s | real hole | page booted 23:59:58. 31 s after 23:59:59 pristine reads Friday 9 October, mutant still Thursday |
| A6-interval-85s | rollover cadence 85 s | real hole | mutant still Thursday 61 s after 23:59:59 (60 s after midnight), so the "within a minute" promise is broken and nothing is red |
| V1-svg-html-namespace | `icon()` makes `svg` and `use` with `createElement` | real hole, worst of the set | `namespaceURI` pristine `http://www.w3.org/2000/svg`, mutant `http://www.w3.org/1999/xhtml`. The 44 x 44 trash button has 140 glyph pixels pristine and 0 in the mutant: every icon disappears while 114 tests pass |
| V2-stale-best | `span.best` not removed when best drops to 0 | real hole (R6) | habit ticked then unticked: pristine `['cur none:No streak yet']`, mutant `['cur none:No streak yet','best:Best 1']` |
| V3-future-cell-keeps-role-label-current | a cell that becomes future keeps role, label and aria-current | real hole (R9, R19) | Sun to Mon: pristine 0 future cells with role or label, mutant 6, and two cells with aria-current (`2026-10-12`, `2026-10-18`) |
| V4-new-today-cell-keeps-aria-hidden | a cell that stops being future keeps `aria-hidden=true` | real hole (R9, R19) | Thu to Fri: today's cell `aria-hidden` pristine null, mutant `"true"` (hidden from assistive tech until reload) |
| V5-old-today-cell-keeps-aria-current | the old today cell keeps `aria-current` | real hole (R9, R19) | Thu to Fri: pristine aria-current cells `['2026-10-09']`, mutant `['2026-10-08','2026-10-09']` |
| V6-settext-always-writes | `setText` writes an unchanged text (BUILD JC3) | real hole (JC3 untested) | not observable without a MutationObserver |
| V7-error-cleared-by-render | any render below 12 clears the message line | real hole (R11) | duplicate error, then a delete: pristine keeps message and `aria-invalid`, mutant clears both |
| H4-dialog-title-class | `h2.dialog-title` loses its class | real hole (fidelity only) | title font pristine 18px, mutant 24px |
| H5-sprite-in-flow | sprite loses `position:absolute` | real hole (fidelity only) | `h1.brand` top pristine 24px, mutant 48px (the whole page moves down 24px) |
| H8-delete-button-class | Delete habit is `btn-primary` | real hole (fidelity only) | button colour pristine `rgb(162, 59, 50)`, mutant `rgb(59, 107, 96)` |
| E6-heat-cells-rebuilt | `renderHeatmap` replaces all 84 cells on every render | real hole (R8 "in place", JC2) | no probe needed: the change is the point (nothing holds a handle to a heat cell) |
| C3-strip-aria-current-stale | `syncDay` never removes `aria-current` (my intended control) | equivalent, my control was wrong | the strip window always ends today, so the today button is always the 7th and the `else removeAttribute` branch (`view.js` 128) never changes anything. Dead in effect |
| E1-returnvalue-not-reset | no `returnValue` reset | equivalent on Chromium (QA M11) | `dialog_rv.py`: Chromium 149 keeps `returnValue` `'delete'` across a reopen, but a later Esc closes with `''`. The reset only matters on other engines |
| E2-no-focus-return-after-keep | no explicit focus return | equivalent on Chromium (QA M02) | Chromium restores focus to the opener itself |
| E3-visibility-check-dropped | day check runs on any `visibilitychange` | equivalent | checking while hidden is harmless |

## Other evidence

- **N1 (source scans skip `styles.css`).** `work-static` copy with a planted `src/planted.css` holding all three sample names, `sample-history` and every banned sink. `pytest test_platform.py test_entry.py -k "no_html_sinks or no_sample_data or head_csp or stylesheet_is_the_golden"` gave `4 passed`. The files the tests scan are `['app.js','dates.js','habits.js','storage.js','view.js']`, the files under `src/` are those plus `planted.css` and `styles.css`. The shipped tree itself is clean (`grep`: no hit in `styles.css` except the CSS keyword `stretch`).
- **R2 stylesheet.** `css_diff.py` (token level diff of the golden block against `src/styles.css`) shows exactly the four edits R2 allows: `.scrim` rule removed, `.scrim,` removed from the `scrim-in` selector, backdrop colour with fallback, `::backdrop` in the reduced-motion list. Nothing else differs. `byteid.py`: the style block is byte-identical in the four goldens (15997 characters, one sha1), so the spec's "measured" claim holds.
- **`decode-unit.mjs`.** `storage.js` imports and runs under Node, so `decodeState` and `encodeState` can be unit tested without a browser. Output: unsorted and duplicate days come back sorted and unique, a mixed good and impossible date is `unreadable`, `A, B, a` is `unreadable`, a `__proto__` and extra key habit is rebuilt as `{name, done}` with no pollution, `encodeState` drops extra properties.
- **Static checks.** `node --check` passes for `app.js`, `view.js`, `storage.js`. No em or en dash in any changed file. No `console`, `fetch`, `window.`, timer other than the one `setInterval`, and no `innerHTML` family in `src/`.
- **Comment and number claims checked.** No comment in the changed code cites a file:line. The absolute counts in comments are "84 cells" (12 x 7, true) and the "60 second promise" (the spec's).

## Probe output (verbatim, shortened where marked)

```
[pristine] decoder_sort: after a tick on B, A.done in storage = ['2026-10-07', '2026-10-08']
[pristine] decoder_first_date: notes=1 rows=0 stored={"version":1,"habits":[]}
[pristine] decoder_dup: notes=1 rows=0
[pristine] add_focus: after clicking Add, focus is on BUTTON#.Add
[pristine] writes: at load=0, cumulative after Cancel=0, Esc=0, backdrop=0, rejected name=0 | unreadable load=1, after Dismiss=0 more | at load=0, after the rollover=0 more
[pristine] cadence: 31 s after 23:59:59 ... 'Friday 9 October'; 61 s ... 'Friday 9 October'
[pristine] cells: {"futureCount": 6, "futureWithRoleOrName": 0, "futureWithCurrent": 0, "todayDate": "2026-10-12", "todayAriaHidden": null, "ariaCurrentCells": ["2026-10-12"]}
[pristine] cells_weekday: {"fri9": {"cls": "hc l0 today", "ariaHidden": null, "current": "date"}, "thu8": {"cls": "hc l2", "current": null}, "ariaCurrentCells": ["2026-10-09"]}
[pristine] best_zero: after tick ['cur:1 day', 'best:Best 1']; after untick ['cur none:No streak yet']
[pristine] error_then_delete: ['You already track this habit.', 'field-msg field-error', 'true']
[pristine] svg: {"ns": "http://www.w3.org/2000/svg", "w": 20, "h": 20, "useNs": "http://www.w3.org/2000/svg"}
[pristine] svg_pixels: trash button 44x44: 140 glyph pixels differ from the background
[pristine] layout: brand top=24px; {"titleFont": "18px", "deleteBg": "rgb(162, 59, 50)"}
[pristine] backdrop_drag_in: press on the backdrop, release on the title: dialog open = True

[S1-no-sort-no-dedupe] decoder_sort: ['2026-10-08', '2026-10-07', '2026-10-08']
[S2-dedupe-only] decoder_sort: ['2026-10-08', '2026-10-07']
[S3-sort-only] decoder_sort: ['2026-10-07', '2026-10-08', '2026-10-08']
[S5-first-date-only] decoder_first_date: notes=0 rows=1 stored={"version":1,"habits":[{"name":"A","done":["2026-10-08","2026-02-30"]}]}
[S6-duplicate-vs-previous-only] decoder_dup: notes=0 rows=3
[A5-add-moves-focus] add_focus: after clicking Add, focus is on INPUT#new-habit.
[A1-cancel-resaves] writes: cumulative after Cancel=0, Esc=1, backdrop=2, rejected name=3 (every keep path wrote once)
[A2-reject-resaves] writes: rejected name=1
[A3-rollover-saves] writes: after the rollover=1 more
[A4-dismiss-saves] writes: after Dismiss=1 more
[A6-interval-60s] cadence: 31 s ... 'Thursday 8 October'; 61 s ... 'Friday 9 October'
[A6-interval-85s] cadence: 31 s ... 'Thursday 8 October'; 61 s ... 'Thursday 8 October'
[V3-future-cell-keeps-role-label-current] cells: futureWithRoleOrName 6, futureWithCurrent 1, ariaCurrentCells ["2026-10-12","2026-10-18"]
[V4-new-today-cell-keeps-aria-hidden] cells_weekday: fri9 ariaHidden "true"
[V5-old-today-cell-keeps-aria-current] cells_weekday: thu8 current "date", ariaCurrentCells ["2026-10-08","2026-10-09"]
[V2-stale-best] best_zero: after untick ['cur none:No streak yet', 'best:Best 1']
[V7-error-cleared-by-render] error_then_delete: ['', 'field-msg field-error', None]
[V1-svg-html-namespace] svg: {"ns": "http://www.w3.org/1999/xhtml", ...}; svg_pixels: trash button 44x44: 0 glyph pixels
[H5-sprite-in-flow] layout: brand top=48px
[H4-dialog-title-class] layout: titleFont 24px
[H8-delete-button-class] layout: deleteBg rgb(59, 107, 96)
[A7-backdrop-press-only] backdrop_drag_in: dialog open = False
```

## Files in this folder

`evidence.md` (this file), `mutants.py` (28 mutants) and `mutants_extra.py` (6 mutants), `mut.py` (in-memory serving runner), `probe.py` (behaviour probes), `decode-unit.mjs`, `css_diff.py`, `byteid.py`, `dialog_rv.py`. The scripts take the scratch work copy or the project root as an argument and write nothing.

## Process accounting

Everything started was a child of a runner or probe invocation and exited by itself. No background shell, watcher or poll loop was started.

| What | PID | Port | Purpose | At return |
|---|---|---|---|---|
| baseline runner / pytest | 44760 / 41012 | 47190 | pristine run | STOPPED (exited) |
| runner batch 1 | 44660 | 1350, 48289, 20222, 23238, 36100, 37886, 23512 | C1 to C3, A1 to A4 | STOPPED |
| runner batch 2 | 2900 | 49758, 24117, 18744, 25368, 28091, 16987, 19332 | S1 to S6, A5 | STOPPED |
| runner batch 3 | 21272 | 40433, 57900, 1214, 52746, 43353, 20100, 29766 | A7, A8, A6 x2, V3 to V5 | STOPPED |
| runner batch 4 | 32040 | 54044, 9147, 30030, 25263, 13095, 56657, 47607 | V2, V6, V7, V1, H4, H5, H8 | STOPPED |
| runner batch 5 | 46528 | 56560, 43757, 1884, 21172, 1716 | E1 to E5 | STOPPED |
| runner batch 6 | 14656 (pytest 46108) | 55540 | E6 | STOPPED |
| probe invocations, `dialog_rv.py`, `decode-unit.mjs`, `css_diff.py`, `byteid.py` | short lived | ephemeral | probes and checks | STOPPED |

Each pytest child (one per mutant) closed its own headless Chromium at session end. The sweep method, run before the first mutant and after the last: PowerShell `Get-CimInstance Win32_Process` filtered by name (`python|node|chrom|headless|playwright|pytest|http`) and by command line (`cr-app|pytest|playwright|http.server|mut.py|probe.py`), plus `Get-NetTCPConnection -State Listen` on 127.0.0.1. Before: only the shell I was running in. After the last mutant run: no python, node, Chromium or shell process of mine, and none of the ports above listening. The other loopback listeners on the machine (owners 33396, 6060, 6052, 21688, 14156, 16100, 19476, 2244, 45496, 23980) were not started by this run and were not touched.

## Declared deviations

- One heredoc was used to patch my own scratch `probe.py` (adding two probes) in the session scratchpad, not in the repo. The result was read back and is what was copied here.
- One `rm -rf` was issued against a scratch path (`work-static`) that did not exist, so it deleted nothing. No other delete was run.
- `cp -r` was used to copy the project files into the scratchpad throwaway copy. The only repo files written are the ones in this folder and `findings/code-review.md`, all with the Write tool.
