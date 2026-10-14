# WebKit baseline of the 1.0 suite and the 1.0 live gate (app task 11, R30)

Recorded 2026-10-14 by the frontend builder (app task 11). The tree is commit `6188e66` plus task 11's test-side changes, with `src/` and `index.html` unchanged. WebKit 26.5 (Playwright 1.61.0, build webkit-2311), headless, Windows. Chromium 149.0.7827.55 for the comparison.

## The 1.0 suite (the nine 1.0 test files, run by name)
The command, from the project root, capped at 20 minutes.
`STREAKS_EVIDENCE_DIR=docs/modules/app/qa/webkit-baseline/20261014-125500-webkit timeout 1200 python -B -m pytest tests/browser/test_add.py tests/browser/test_delete.py tests/browser/test_entry.py tests/browser/test_fidelity_inputs.py tests/browser/test_platform.py tests/browser/test_render.py tests/browser/test_rollover.py tests/browser/test_storage.py tests/browser/test_tick.py -q -rA -p no:cacheprovider --engine webkit --junitxml=docs/modules/app/qa/webkit-baseline/20261014-125500-webkit/junit.xml`

| Engine | Passed | Failed | Skipped | pytest time | Wall time | Evidence |
|---|---|---|---|---|---|---|
| WebKit | 174 | 5 | 0 | 74.17 s | 77 s | `junit.xml` and the suite's screenshots `01-first-visit.png` to `08-note.png` in this folder |
| Chromium | 179 | 0 | 0 | 42.18 s | 45 s | `../../chromium-baseline/20261014-125323-chromium/junit.xml` |

The WebKit run ended 18 minutes before the 20-minute cap. 0 chromium_only skips (no test carries the marker at task 11).

### Each WebKit failure and its class
Classes of spec task 11. (a) an app defect Safari would show. (b) an engine difference, written into qa.md with its measurement. (c) Chromium-only tooling, marked `chromium_only`.

| Test | What failed | Measurement | Class |
|---|---|---|---|
| `test_add.py::test_R10_the_first_habit_on_a_fresh_day` | `is_focused(add_button(page))` after a mouse click on Add is false | `document.activeElement` is `body` after a mouse click on a button in WebKit, the button in Chromium (probes.json, `focus_after_click_and_keys`, also on the 1.0 app) | (b). The app does not move focus (R10), WebKit clears focus on a mouse click on a button as Safari does. Already in qa.md, Engine differences by design, row 1, now marked confirmed |
| `test_platform.py::test_R22_focus_rings_on_keyboard_focus[a day button]` | the computed `outline` string | `2px solid rgb(28, 37, 35)` in WebKit, `rgb(28, 37, 35) solid 2px` in Chromium. Width, style, colour and offset (`0px`) equal in both | (b). The same ring, serialised in another order. Written into qa.md (new table row and Task 11 measurements) |
| `test_platform.py::test_R22_focus_rings_on_keyboard_focus[an icon button]` | the same, offset `-2px` | as above | (b) |
| `test_platform.py::test_R22_focus_rings_on_keyboard_focus[the input]` | the same, offset `2px` | as above | (b) |
| `test_platform.py::test_R22_focus_rings_on_keyboard_focus[the Add button]` | the same, offset `3px` | as above | (b) |

No failure is class (a) or (c). No 1.0 assertion was changed and no marker was added. These 1.0 files are removed at task 12, and their v1.1.0 successors assert each engine's own sentence (qa.md).

## The 1.0 live gate
Run through a scratchpad runner that served the project root on a free 127.0.0.1 port, ran `python -B tests/browser/live_e2e.py --engine <engine> --base-url http://127.0.0.1:<port>/ --out <folder>` (600 s cap) and stopped the server, checking the port refused connections.

| Engine | Steps passed | Requests outside the rule | Console errors | Page errors | Pass | Evidence |
|---|---|---|---|---|---|---|
| WebKit 26.5 | 11 of 11 | 0 | 0 | 0 | true | `live-e2e-webkit/` (11 screenshots, steps, console, network, summary) |
| Chromium 149.0.7827.55 | 11 of 11 | 0 | 0 | 0 | true | `../../chromium-baseline/20261014-125323-chromium/live-e2e-chromium/` |

Each `summary.json` records `engine` and `browser_version`. The real clock was used, start and end date 2026-10-14.

## Probes
`probes.json` in this folder, both engines. P1 (the D-b redefinition of `window.localStorage`, honoured by both), P2 (quota fill, 5242672 characters in both, 10 ms and 3 ms), P3 (`image/svg+xml`), two quick taps (`detail` 2 in Chromium, 1 in WebKit), focus after a click, `getComputedStyle(dialog, "::backdrop")` (the same in both), the CSP console text, the computed `outline`, CO-1 (WebKit draws the light colour in both schemes, information only) and the clipboard on 127.0.0.1 (a secure context in both, the stand-in replaces `writeText`). The values and what they settle are in qa.md, "Task 11 measurements (2026-10-14)".
