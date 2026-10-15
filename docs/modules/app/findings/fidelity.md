---
module: app
kind: fidelity
version: v1.1.0
task: 28 (first half, the fidelity gate in Chromium)
status: one-to-one
counts: { critical: 0, high: 0, medium: 0, low: 0, observations: 12 }
mismatch_pct: 0
mismatch_pixels: { captures_run: 23, captures_at_0: 23, total: 0 }
checklist: { rows: 139, pass: 139, fail: 0, not_run: 0 }
artifacts: ./docs/modules/app/qa/fidelity-<screen>-<WxH>/<datetimestamp>/ (23 runs, listed below), ./docs/modules/app/qa/fidelity-controls/20261015-180740/, ./docs/modules/app/qa/fidelity-checklist/20261015-181111/
---
# Fidelity gate, app, v1.1.0 (goldens ./docs/design/today.html, day-editor.html, year-view.html, overview.html, overview-year.html, delete-dialog.html, today-empty.html, today-full.html, states.html)

> Written by the fidelity finder (read-only on the product), 2026-10-15, task 28 first half. HEAD `56e3c7b` on `main`. It replaces the 1.0 verdict of 2026-10-09, whose form and gate-conditions table it follows. Every verdict below comes from a run I made today and a capture I listed on disk. No file under `src/`, `tests/`, `index.html` or `docs/design/` changed (checked before and after every batch). Nothing was committed.

## Verdict

**1-to-1. status one-to-one. 0 findings (0 critical, 0 high, 0 medium, 0 low), 12 observations.**

- All 23 captures give **0 mismatched pixels and `dimensions_match` true** at threshold 0.1, the budget of qa.md. In every one the candidate PNG is **byte-identical** to the golden PNG (0 pixels differ at any level, same SHA-256).
- The control holds and the gate can fail. Every golden against itself, at each viewport the gate uses for it, gives 0 (23 of 23, byte-identical). The negative control, today.html against the app with no state flag (S1), gives 15843, 16524 and 46874 mismatched pixels at 360, 390 and 1280. A gate that reported 0 there could not fail.
- The per-element check finds no addition, subtraction or modification outside the ruled and specified set (static stand-ins of the goldens, native modal effects, spec R2, R29, R36, SEC-02). A whole-page DOM comparison of golden and app paired 402 to 2161 elements per capture with 0 rectangle, 0 text and 0 computed-style differences outside that set.
- **All 139 FE checklist rows pass**, the six states.html rows at 360 x 780 and at 1280 x 800 included.
- Functional QA was green before this run (precondition read from primary files, see Gate conditions).

## Gate conditions
| Item | Value |
|---|---|
| Harness | `{sdlc}/harness/fidelity.py`, plugin version **2.6.0** (`.claude-plugin/plugin.json` beside it), file SHA-256 `630d10b41c350ba88fe6aaf21ef45382b87d3963ae5d119750a362c3d2dd71a3`, frozen mode. Its own `bypass_csp`, `reduced_motion=reduce`, launch flags `--force-color-profile=srgb --hide-scrollbars`, screenshots with animations disabled. The 1.0 path `{plugins}/...` is gone. No harness venv exists on this machine, the run used the user site packages of Python 3.14.0 |
| Browser and tools | headless Chromium 149.0.7827.55, Playwright 1.61.0, Pillow 12.3.0, numpy 2.4.6, Python 3.14.0, Windows 11 |
| Flags (every run) | `--dpr 1 --color-scheme dark --fixed-time 2026-10-10T09:00:00`, full page, threshold 0.1 (the default), no `--browser-arg` |
| State flags | as qa.md "Captures" table. K1 `seed-sample.js`. P1 to P4 and M1 `seed-sample.js` plus `open-day-editor.js`, `open-year-view.js`, `open-overview.js`, `open-overview-year.js`, `open-delete-dialog.js`. S1 none. S3 `seed-twelve.js`. Every capture that presses got the clipboard stand-in through its seed script, and each after-load script refuses to click without it. All 23 harness runs exited 0, so every after-load script reached its state (each throws otherwise) |
| Clock and zone | both sides saw `Sat Oct 10 2026 09:00:00 GMT+0800 (Malaysia Time)`, zone Asia/Kuala_Lumpur (the machine's) |
| Budget | 0 mismatched pixels at 0.1 and `dimensions_match` true per capture (qa.md). Not widened |
| Control (same harness, same session) | each golden as both golden and candidate, the candidate served read-only by the app's server at `/docs/design/<screen>.html`, at each viewport of the gate (23 runs). Expected 0 |
| Negative control | today.html against the app with no state flag (S1), 360, 390 and 1280. Expected above 0 |
| Baseline, the gate's own prior self | the 1.0 gate (harness 2.1.3, 2026-10-09, 6 captures of the 1.0 goldens, all 0). The v1.1.0 goldens and app are new, so no 1.0 capture is a pixel baseline. This run is the first v1.1.0 run on 2.6.0 and sets the baseline, anchored by the 23 golden-self controls |
| Code under test | HEAD `56e3c7b`, a docs-only commit over the brief's `e5767e5` (`git diff --stat e5767e5 56e3c7b -- src tests index.html docs/design` is empty). `git status --porcelain -- src tests index.html docs/design` empty before and after every batch |
| Functional precondition | QA finder's re-check, `findings/qa.md` "Re-check 2026-10-15", verdict PASS. Task 27a's builder runs on `4af5d75`, read from their own `junit.xml`. `docs/modules/app/qa/functional/20261015-174940-chromium/` tests 358, failures 0, errors 0, skipped 0. `docs/modules/app/qa/functional/20261015-175213-webkit/` tests 358, failures 0, errors 0, skipped 1 (CO-1) |
| Servers | one `python -m http.server <port> --bind 127.0.0.1` from the project root per batch, started and stopped by my runner, port checked refusing (Processes) |
| Phase skills | the registry assigns none to verification work. None loaded |

## The 23 captures
Each folder holds `golden.png`, `candidate.png`, `diff.png`, `styles.json`, `report.json` (the harness's) and `run-meta.json` (mine, the command, exit code, seconds, HEAD, server, and an independent re-count of the PNGs). Under `docs/modules/app/qa/`.

| # | Capture | Mismatched pixels (0.1) | `dimensions_match` | Size golden and candidate | Pixels differing at any level | Folder |
|---|---|---|---|---|---|---|
| 1 | K1 today.html 360x780 | **0** | true | 360x780 | 0 (byte-identical) | `fidelity-today-360x780/20261015-180906/` |
| 2 | K1 today.html 390x844 | **0** | true | 390x844 | 0 (byte-identical) | `fidelity-today-390x844/20261015-180910/` |
| 3 | K1 today.html 1280x800 | **0** | true | 1280x800 | 0 (byte-identical) | `fidelity-today-1280x800/20261015-180913/` |
| 4 | P1 day-editor.html 360x780 | **0** | true | 360x780 | 0 (byte-identical) | `fidelity-day-editor-360x780/20261015-180918/` |
| 5 | P1 day-editor.html 390x844 | **0** | true | 390x844 | 0 (byte-identical) | `fidelity-day-editor-390x844/20261015-180921/` |
| 6 | P1 day-editor.html 1280x800 | **0** | true | 1280x800 | 0 (byte-identical) | `fidelity-day-editor-1280x800/20261015-180925/` |
| 7 | P2 year-view.html 360x780 | **0** | true | 360x780 | 0 (byte-identical) | `fidelity-year-view-360x780/20261015-180929/` |
| 8 | P2 year-view.html 390x844 | **0** | true | 390x844 | 0 (byte-identical) | `fidelity-year-view-390x844/20261015-180933/` |
| 9 | P2 year-view.html 1280x800 | **0** | true | 1280x800 | 0 (byte-identical) | `fidelity-year-view-1280x800/20261015-180937/` |
| 10 | P3 overview.html 360x780 | **0** | true | 360x780 | 0 (byte-identical) | `fidelity-overview-360x780/20261015-180941/` |
| 11 | P3 overview.html 390x844 | **0** | true | 390x844 | 0 (byte-identical) | `fidelity-overview-390x844/20261015-180945/` |
| 12 | P4 overview-year.html 360x780 | **0** | true | 360x780 | 0 (byte-identical) | `fidelity-overview-year-360x780/20261015-180949/` |
| 13 | P4 overview-year.html 390x844 | **0** | true | 390x844 | 0 (byte-identical) | `fidelity-overview-year-390x844/20261015-180953/` |
| 14 | P4 overview-year.html 1280x800 | **0** | true | 1280x800 | 0 (byte-identical) | `fidelity-overview-year-1280x800/20261015-180957/` |
| 15 | M1 delete-dialog.html 360x780 | **0** | true | 360x780 | 0 (byte-identical) | `fidelity-delete-dialog-360x780/20261015-181001/` |
| 16 | M1 delete-dialog.html 390x844 | **0** | true | 390x844 | 0 (byte-identical) | `fidelity-delete-dialog-390x844/20261015-181005/` |
| 17 | M1 delete-dialog.html 1280x800 | **0** | true | 1280x800 | 0 (byte-identical) | `fidelity-delete-dialog-1280x800/20261015-181008/` |
| 18 | S1 today-empty.html 360x780 | **0** | true | 360x780 | 0 (byte-identical) | `fidelity-today-empty-360x780/20261015-181012/` |
| 19 | S1 today-empty.html 390x844 | **0** | true | 390x844 | 0 (byte-identical) | `fidelity-today-empty-390x844/20261015-181016/` |
| 20 | S1 today-empty.html 1280x800 | **0** | true | 1280x800 | 0 (byte-identical) | `fidelity-today-empty-1280x800/20261015-181020/` |
| 21 | S3 today-full.html 360x780 | **0** | true | 360x780 | 0 (byte-identical) | `fidelity-today-full-360x780/20261015-181023/` |
| 22 | S3 today-full.html 390x844 | **0** | true | 390x844 | 0 (byte-identical) | `fidelity-today-full-390x844/20261015-181027/` |
| 23 | S3 today-full.html 1280x800 | **0** | true | 1280x800 | 0 (byte-identical) | `fidelity-today-full-1280x800/20261015-181031/` |

P3's 1280 render is reference only (MANIFEST) and is not a capture. Every page is one viewport tall, so each full-page capture is the viewport. I opened `candidate.png` of P1 at 390, M1 at 360 and P4 at 1280, and the negative control's `diff.png` at 390. Each shows the expected state, and the negative diff is red exactly where S1's empty list differs from K1's rows.

## Controls, `docs/modules/app/qa/fidelity-controls/20261015-180740/`
| Control | Result | Folders |
|---|---|---|
| Positive, each golden against itself, 23 runs (the 23 screen and viewport pairs above) | 23 of 23 at **0**, `dimensions_match` true, PNGs byte-identical | `positive-<screen>-<WxH>/` |
| Negative, today.html against the app with no state flag (S1) | **15843** at 360x780, **16524** at 390x844, **46874** at 1280x800, dimensions match, max channel delta 231, 231, 223 | `negative-today-360x780/`, `negative-today-390x844/`, `negative-today-1280x800/` |

`batch-summary.json` in the same folder holds every row, the server PID and port, and the tree check.

## Per-element check behind the pixel counts
Pixels are one lens. qa.md's method adds the per-element computed-style check from `styles.json`.

1. **`styles.json` as the harness writes it** (`fidelity-checklist/20261015-181111/styles-json-check.json`). S1 matches entry for entry at all three widths (33, 33 and 394 entries, 0 rectangle and 0 style differences, only whitespace inside text strings). For the other screens a match by path and occurrence is not sound (O-04), so I added a tree comparison.
2. **Whole-page tree comparison** (`fidelity-checklist/20261015-181111/dom-compare/<capture>.json`, `dom-compare-summary.json`). Each golden and each candidate rendered exactly as the harness renders them (its own freeze script and stylesheet imported from `fidelity.py`, the same flags, context and state scripts). Every element of `body` on both sides was paired by tag, id and `data-key`, then by class overlap in order, and compared on classes, attributes, own text, rectangle, every computed property, `::before`, `::after`, and for dialogs `:modal` and `::backdrop`.

| Screen (all its gate widths) | Elements golden / app | Paired | Rectangle diffs | Text diffs (not whitespace) | Computed-style diffs outside the ruled set | What differs, all ruled or specified (O-05) |
|---|---|---|---|---|---|---|
| K1 | 682 / 737 | 402 | 0 | 0 | 0 | 264 ring arcs `<use>` against `<path>` (same geometry, class, box), golden `defs`, 5 closed app dialogs |
| P1 phone | 1297 / 1325 | 751 | 0 | 0 | 0 | arcs, scrim and static dialogs against native modals, `.below-desktop`, R36 room `padding-bottom` 293px on P3's body |
| P1 1280 | 1297 / 768 | 455 | 0 | 0 | 0 | as above, plus the golden's hidden P3 with content against the app's closed, empty P3 |
| P2 | 2442 / 2472 | 2161 | 0 | 0 | 0 | arcs, scrim and static dialog against native modal |
| P3 | 1242 / 1294 | 712 | 0 | 0 | 0 | arcs, scrim and static dialog against native modal |
| P4 | 3242 / 3850 phone, 3293 desktop | 1863 | 0 | 0 | 0 | arcs, scrim and static dialog against native modal, P3 open under P4 on a phone (P4-01) |
| M1 | 678 / 737 | 409 | 0 | 1, the title's isolate marks (SEC-02) | 0 | arcs, scrim and static dialog against native modal |
| S1 | 405 / 482 | 405 | 0 | 0 | 0 | 3 extra sprite symbols (K1-02 holds in S1, S1-01), 5 closed app dialogs |
| S3 | 1640 / 1700 | 571 | 0 | 0 | 0 | 1056 arcs, extra `symbol#i-x`, 5 closed app dialogs |

For every `<use>` to `<path>` pair the referenced path data equals the app's `d`, the classes and box are equal, and the only computed differences are the CSS `d` property itself and the modal-only `interactivity` and `user-select`. The tab title is "Danial's Streaky Habit" on both sides, and the app's icon link is `src/icon.svg` against the golden's data URL (R29, K1-03).

## FE element checklist (139 rows, 139 PASS)
A row passes when its element is present on the app with the values the row gives and equal to the golden's. Evidence for every row, the capture's 0-pixel diff at each gate width, the tree comparison above (0 rectangle, attribute, text and style differences outside the ruled set), and 297 explicit row values read on both the golden and the app in the capture states (`fidelity-checklist/20261015-181111/row-probe.json`). In that probe the app equals the golden on every check except the ruled ones, and the app meets the row's stated value on 288 of 297. The 9 others are my probe's reading, not the app (O-08).

| Screen | Rows | Result | Notes |
|---|---|---|---|
| K1 today.html | K1-01 to K1-44 | 44 PASS | 0 px at 360, 390, 1280. Names, labels, axis texts, 83 band days ("Mon 20 Jul, 2 of 3 habits" to "Sat 10 Oct, 1 of 3 habits"), numbers 4, 2, "No streak yet", 9, 5, 14, pressed states, field attributes read and equal. K1-03 title and `src/icon.svg`. K1-44 no dialog open, the app-only elements are five closed dialogs of zero size |
| P1 day-editor.html | P1-01 to P1-17 | 17 PASS | title, subtitle, ticks pressed false, false, true, numbers, open cell 2026-09-22 only, `:modal` true. P1-17 by the blur (O-03) |
| P2 year-view.html | P2-01 to P2-21 | 21 PASS | 13 month titles October 2026 to October 2025, 39 lead cells, 366 day buttons (250 pressed, 116 not), today "Mark Sat 10 Oct 2026 as done", names spanning 10 Oct 2025 to 10 Oct 2026 |
| P3 overview.html | P3-01 to P3-11 | 11 PASS | 360 and 390. Month column, 83 cells 2026-10-05 first to 2026-07-26 last, one empty cell |
| P4 overview-year.html | P4-01 to P4-11 | 11 PASS | 366 rings, 21 closed, 9 blank, names spanning 10 Oct 2025 to 10 Oct 2026 |
| M1 delete-dialog.html | M1-01 to M1-10 | 10 PASS | role, labels, `:modal` true, widths 328, 358 and 400, buttons, title with U+2068 and U+2069. M1-01 a page button cannot take focus. M1-10 by the blur (O-03) |
| S1 today-empty.html | S1-01 to S1-09 | 9 PASS | lead and line, 83 band days "..., 0 of 0 habits", Overview "Overview, today 0 of 0 habits done", composer enabled |
| S3 today-full.html | S3-01 to S3-10 | 10 PASS | 12 rows, frame scrolls at its top with `more-below`, `composer is-full`, field and Add disabled, the note text, "Overview, today 7 of 12 habits done", first band day "Mon 20 Jul, 7 of 12 habits", page one viewport tall. S3-08 the field box equals K1's at all three widths, on the goldens and on the app |
| States sheet | ST-01 to ST-06 | 6 PASS at 360x780, 6 PASS at 1280x800 | below |

### States sheet, computed-style method (`fidelity-checklist/20261015-181111/states/`)
`states.html` opened from its file path against the running app reached with real gestures (`conftest.open_app`, the stand-in first in every context, the sample day's clock). S2 by an empty submit, then "Read twenty pages of a novel before bed each night", then "read 20 pages", each with a click on Add. S4 by driver D-a and one click on "Done today, Stretch 10 minutes". S5 by storage "{". The pointer was parked off every control and animations had ended before each read. 36 element pairs per width, 2232 property comparisons in all (colour, background, four border colours, styles and widths, four radii, padding, margin, font size, weight and line height, and width and height for buttons, plus fill and stroke for the empty state's svg), and 32 attribute, text and position checks per width.

| # | 360x780 | 1280x800 | What was compared |
|---|---|---|---|
| ST-01 | PASS | PASS | message "Name the habit first." `field-msg err`, aria-live polite, margin 0 0 8 2, `--danger`. Field aria-invalid true, against K1's field only the four edge colours changed, to rgb(255, 107, 102). The field did not move (25, 707 at 360, 246.23, 727 at 1280, before and after). Label, Add and its icon, `div.add-ctl` equal the specimen. See O-06 for the composer's margin-top |
| ST-02 | PASS | PASS | the 50-character name stays in the field, message "Keep it to 40 characters or fewer.", styled as ST-01 |
| ST-03 | PASS | PASS | "read 20 pages" stays, message "You already track this habit.", styled as ST-01 |
| ST-04 | PASS | PASS | `div.banner.warn` role status holding only its `p`, every compared property equal, text equal. In `div.banners` between the header (phone, 82 to 94) or the band (desktop, 410 to 422) and the list. Both specimen and app draw the fill #2C261C (O-07) |
| ST-05 | PASS | PASS | `div.banner.note` role status, its `p`, the 44 by 44 "Dismiss note" button, its icon, `li.empty`, its svg, orbit and core circles, `p.lead`, `p.line`, `ul.rows` all equal. 12 between the banner and the list, as the specimen |
| ST-06 | PASS | PASS | none of `main.sheet`, `.spec`, `.stack`, `#n1` to `#n3`, `#m1` to `#m3`, the sheet title or the five frame headings exists in the live DOM in five states (sample, fresh, twelve, unreadable, save failing), and `src/styles.css` has no `.sheet`, `.spec` or `.stack` selector |

Screenshots of the sheet and of each live state at both widths are in the same folder.

## Findings
None. No addition, subtraction or modification of the design was found in any capture, checklist row or state.

## Observations
- **O-01 First run on harness 2.6.0.** The 1.0 baseline ran on 2.1.3 at a path that no longer exists. 2.6.0 reproduced the 0-pixel result here on the same Chromium 149.0.7827.55, and the 23 golden-self controls are byte-identical, so the harness renders deterministically on this machine. qa.md already names 2.6.0, so no document is stale on this point.
- **O-02 M1 is now exact.** In 1.0 the native modal against the static golden left 149 and 88 pixels below the threshold on Cancel's edge. In v1.1.0 all three M1 captures, and every popup capture, are byte-identical.
- **O-03 What the blur hides** (`fidelity-checklist/20261015-181111/noblur/`, an extra run, not the gate). With the last line of each after-load script removed, P1 gives 1663 (390) and 1831 (1280), P2, P3 and P4 give 347 each at 390, and M1 gives 878 at 390 mismatched pixels. Each mismatch box is exactly one control, P1's first tick (356 by 60 at 390, 398 by 60 at 1280), M1's Cancel with its ring (162 by 58) and the 44 by 44 Close at x 336, y 12. So the blur removes only the focus ring that the goldens do not draw, and it also shows that focus lands where R40 puts it.
- **O-04 `styles.json` alone cannot carry the per-element check here.** The harness keys elements by tag and class only and caps the dump at 600 visible elements. The goldens draw ring arcs as `<use>` and the app as `<path>` (MANIFEST, static stand-ins), so occurrence keys drift and a naive pairing reports style deltas between different elements. The cap also cuts 14 of the 23 dumps (every P1, P2, P3 and P4 capture, and K1, M1 and S3 at 1280), for example the field at 1280. The tree comparison above replaces it. A note in qa.md's Method would save the next finder the detour.
- **O-05 The ruled and specified differences the tree comparison shows**, none visible. (a) The goldens' static stand-ins (MANIFEST), `div.scrim`, `inert` on the page, `<dialog open>` with `z-index` 10 and `overlay` none, `.below-desktop` on P1's P3, ring arcs as `<use>` of shared `defs`. (b) The app's native modals, `:modal` true, `overlay` auto, `::backdrop` fixed, `interactivity` auto under the modal where the golden's `inert` gives inert, and `user-select` text inside the dialog. (c) The app's closed dialogs in the DOM at zero size. (d) The sprite of `index.html` holds all four symbols, where today-empty.html holds only `i-plus` and today-full.html lacks `i-x` (S1-01 and S3-01 keep K1-02). (e) P3's sheet body carries `padding-bottom: 293px` while P1 is open over it on a phone (spec R36, owner ruling H-03), below P3's legend behind P1, as R36 predicts. (f) The title's U+2068 and U+2069 (SEC-02). (g) The icon link `src/icon.svg` (R29). (h) Whitespace text nodes in the goldens' source. (i) On a phone the app opens P4 from P3's Year, so P3 is open under the full-sheet P4 (P4-01, `open-overview-year.js`), where the golden draws P4 alone. At 1280 the golden keeps a hidden P3 with its content and the app's P3 is closed and empty.
- **O-06 ST-01 to ST-03, the composer's margin-top.** My script compared `form.composer` too and flagged one property, computed `margin-top` 0px on the sheet against 188px (360) and 42px (1280) live. The probe (`states-composer-margin-rerun/probe.json`) shows both come from the same declared `.composer { margin-top: auto }`, resolved by the container, the sheet's `.spec` grid (specimen-only styling, which the method leaves out) against the app's `main.main` flex column that pins the composer to the bottom. Live it falls from 216 to 188 and from 70 to 42 when the message shows, 28 px, the message's 20 plus its 8 margin, so the message grows the composer upward as ST-01 says. Not a difference. The script's raw FAIL is kept in `states-check.json`. My first probe (`states-composer-margin/probe.json`) listed no declared rules because of a mistake in my CSSOM walk and is kept as history.
- **O-07 ST-04's "#2D271C over the page".** The specimen and the app both draw #2C261C (sampled inside both banners at both widths), from the same computed `rgba(255, 176, 32, 0.09)` over rgb(24, 25, 28). The row's hex is the arithmetic rounding, Chromium quantises the alpha to 23/255. A wording matter for qa.md, owner's edit.
- **O-08 The 9 probe values that differ from my reading of a row.** P1-16, my probe joined the spans' text with no space ("Current 4 daysBest 9"), the app equals the golden. P2-21 and P4-08 give a date range, while the DOM order starts at Thu 1 Oct 2026 and ends at Fri 31 Oct 2025. The goldens' 366 labels span 2025-10-10 to 2026-10-10 and include both named labels, and the app's attributes equal the golden's. None is an app difference.
- **O-09 What this gate cannot see.** The harness forces reduced motion, bypasses the CSP, photographs no hover, focus or press, and records no console, so a `test:clipboard:` marker could not show through it. The stand-in was in place for every capture that presses (the after-load scripts refuse otherwise, and all exited 0), the app has no copy feature, and the system clipboard was never touched. Hover, focus, press and motion stay with the functional suites.
- **O-10 HEAD.** The brief named `e5767e5`. HEAD is `56e3c7b`, a records commit with no change under `src/`, `tests/`, `index.html` or `docs/design/`.
- **O-11 A second agent ran browsers at the same time.** From 18.16 the `examples/split` agent ran a WebKit pytest with its own `http.server` on 58431. My runs are Chromium on their own ports, and each of my captures is byte-identical to its golden, so the overlap did not touch this evidence.
- **O-12 My process slips.** One read-only check ended with `2>/dev/null` (`ls "$HOME/.sdlc-harness"`), a redirection of stderr that wrote no file. I edited my own scratch script once through a small Python patch file, because no edit tool was available. Before the run I replaced a placeholder check in `states_check.py` that always passed with a real one (against K1's field only the edge colours may change), so no evidence came from it.

## Evidence
All under `{workspace}/examples/streaks/docs/modules/app/qa/`.
- The 23 capture folders of the table above.
- Controls `fidelity-controls/20261015-180740/` (23 `positive-*`, 3 `negative-*`, `batch-summary.json`).
- Checklist and honesty evidence `fidelity-checklist/20261015-181111/`. `gate-summary.json` (every capture and control from its own `report.json` and `run-meta.json`), `styles-json-check.json`, `dom-compare-summary.json` and `dom-compare/` (23 files), `row-probe.json`, `states/` (`states-check.json`, `states-sheet-<WxH>.png`, `live-ST-0<n>-<WxH>.png`), `states-composer-margin/` and `states-composer-margin-rerun/` (`probe.json`), `noblur/` (6 runs and `batch-summary.json`), and `scripts/` (the scripts that produced all of it, with `SHA256.json`).

## Processes
Every process I started is stopped. Each batch ran in the foreground under my runner, which started one server, bounded each wait (server ready in 10 s, each harness run 240 s, each batch 540 s, a "gave up" branch for each), stopped the server by PID and checked its port refusing.

| What | PID | Why | State | How it was stopped |
|---|---|---|---|---|
| `python -m http.server 2721 --bind 127.0.0.1` | 2940 | controls batch | STOPPED | `terminate()` by my runner, port refused |
| `python -m http.server 65295 --bind 127.0.0.1` | 6492 | the 23 captures | STOPPED | same |
| `python -m http.server 6314 --bind 127.0.0.1` | 10152 | tree comparison | STOPPED | same |
| `python -m http.server 5408 --bind 127.0.0.1` | 12832 | states check | STOPPED | same |
| `python -m http.server 43947 --bind 127.0.0.1` | 24464 | composer margin probe | STOPPED | same |
| `python -m http.server 27560 --bind 127.0.0.1` | 22964 | composer margin probe, rerun | STOPPED | same |
| `python -m http.server 51422 --bind 127.0.0.1` | 9440 | no-blur extra | STOPPED | same |
| `python -m http.server 36271 --bind 127.0.0.1` | 2708 | row probe | STOPPED | same |
| 23 + 26 + 6 harness runs, each `python -B fidelity.py` with two headless Chromium | in each `run-meta.json` | the captures, controls and no-blur runs | STOPPED | each exited 0 within its bound |
| headless Chromium of my scripts (tree comparison, states check, probes, one inline read of the two goldens' field box) | not recorded | the checklist | STOPPED | closed by each script |

Teardown verified at 18.22 by a sweep by name (python, node, Playwright, chrome, chromium, headless_shell, WebKit, bash, sh, cmd, powershell, conhost), age, command line (streaks, http.server, pytest, playwright, scratchpad, fidelity, harness, examples split) and listening ports. None of my PIDs was alive, no Chromium was alive, and the eight ports above returned no connection (`curl` HTTP 000). Alive and not mine, left untouched, were the `examples/split` agent's WebKit pytest (runner 20564, pytest 6488, `http.server` 7972 on 58431, Playwright driver 10044 and 14036 with its WebKit children, `wait_for_run.py` 6204, and their bash parents 23744, 22652, 25532, 1800, 25036, 25540, all created 18.16 from its scratch folder `split-a21`), five PowerShell processes from before my session (18192, 22096, 11932, 12048, 22668), and my sweep's own shell chain. No `http.server 4610` was running. Nothing was killed.
