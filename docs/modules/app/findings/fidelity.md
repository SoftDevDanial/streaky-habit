---
module: app
kind: fidelity
status: clean
counts: { critical: 0, high: 0, medium: 0, low: 0 }
mismatch_pct: 0
mismatch_pixels: { S1_390: 0, S1_1280: 0, S2_390: 0, S2_1280: 0, M1_390: 0, M1_1280: 0 }
artifacts: ./docs/modules/app/qa/fidelity-<screen>-<viewport>/<datetimestamp>/ (six runs, listed below) and ./docs/modules/app/qa/fidelity-checklist/20261009-213300/
---
# Fidelity gate, app

> Written by the fidelity finder (read-only on the product), 2026-10-09, against `321329c` on `main`. Goldens: `docs/design/today.html` (S1), `today-empty.html` (S2), `delete-dialog.html` (M1), `states.html` (specimen sheet). The working tree was clean before the run and `git status --short` afterwards lists only my new evidence folders.

## Verdict

**1-to-1. status: clean. 0 findings (0 critical, 0 high, 0 medium, 0 low), 10 observations.**

- All six captures give **0 mismatched pixels and `dimensions_match` true** at threshold 0.1, the budget in qa.md. The S1 and S2 candidate screenshots are **byte-identical** to their golden screenshots (same SHA-256 prefix and 0 differing pixels at any level), so for those four captures not even one pixel differs.
- All **71 FE checklist rows pass** (S1 37 of 37, S2 6 of 6, M1 11 of 11, states sheet 17 of 17), measured on the running app with `getBoundingClientRect` and computed styles at both viewports (states sheet at 360x780), 0 FAIL.
- The 0-pixel baseline measured on harness 2.1.1 **holds on harness 2.1.3**, the check qa.md asks of the first run on a later harness.
- The gate is honest. I reproduced what the M1 blur hides (the Cancel focus ring only), proved the title check rejects wrong titles, repeated M1, and explained the only pixels that differ below the threshold (see Observations).

Functional QA was taken as green from the task brief (176 browser, 99 unit). I did not re-run the full suites. I re-ran the two `@R28` state-script tests (`tests/browser/test_fidelity_inputs.py`, 2 passed) because the gate depends on them.

## Gate conditions
| Item | Value |
|---|---|
| Harness | `{sdlc}/harness/fidelity.py`, plugin version **2.1.3** (`.claude-plugin/plugin.json`), frozen mode. `bypass_csp` and `reduced_motion=reduce` are the harness's own |
| Browser | headless Chromium 149.0.7827.55, Playwright 1.61.0, Pillow 12.3.0, numpy 2.4.6, Python 3.14.0 |
| Flags (every run) | `--dpr 1 --color-scheme light --fixed-time 2026-10-08T09:00:00`, full page, threshold 0.1 (default), no `--browser-arg` |
| State flags | S1 `--candidate-init-script tests/browser/fidelity/seed-sample.js`. S2 none. M1 that seed plus `--candidate-after-load tests/browser/fidelity/open-delete-dialog.js` |
| Server | `python -m http.server 52346 --bind 127.0.0.1` from the project root, stopped afterwards |
| Clock and zone | page saw `Thu Oct 08 2026 09:00:00 GMT+0800 (Malaysia Time)`, zone Asia/Kuala_Lumpur (the machine's) |

## The six captures
| Capture | Mismatched pixels (threshold 0.1) | `dimensions_match` | Golden / candidate size | Pixels that differ at any level | Evidence (under `docs/modules/app/qa/`) |
|---|---|---|---|---|---|
| S1 today.html 390x844 | **0** | true | 390x1136 / 390x1136 | 0 (files byte-identical) | `fidelity-today-390x844/20261009-213131/` |
| S1 today.html 1280x800 | **0** | true | 1280x837 / 1280x837 | 0 (files byte-identical) | `fidelity-today-1280x800/20261009-213136/` |
| S2 today-empty.html 390x844 | **0** | true | 390x844 / 390x844 | 0 (files byte-identical) | `fidelity-today-empty-390x844/20261009-213140/` |
| S2 today-empty.html 1280x800 | **0** | true | 1280x800 / 1280x800 | 0 (files byte-identical) | `fidelity-today-empty-1280x800/20261009-213144/` |
| M1 delete-dialog.html 390x844 | **0** | true | 390x1136 / 390x1136 | 149, max channel delta 4 of 255, box x 44 to 188, y 444 to 484 (inside the Cancel button, see O-02) | `fidelity-delete-dialog-390x844/20261009-213148/` |
| M1 delete-dialog.html 1280x800 | **0** | true | 1280x837 / 1280x837 | 88, max channel delta 4, box x 464 to 633, y 424 to 462 (inside the Cancel button) | `fidelity-delete-dialog-1280x800/20261009-213152/` |

Each folder holds `golden.png`, `candidate.png`, `diff.png`, `styles.json`, `report.json`. The expected sizes in qa.md (S1 and M1 390x1136 and 1280x837) are what was measured. `diff.png` of S1 at 1280 and the M1 candidate at 390 were opened and look right (dimmed golden with no red, dialog centred over the dimmed page).

## Whole-page comparison behind the pixel counts
Pixels are only one lens, so I walked the golden's and the app's DOM side by side (`generic_diff.py`): every element's attributes, own text, rectangle, all computed styles, and the `::before` and `::after` styles of the thread halves and heat cells. S1 has 329 golden elements, S2 127, M1 336.

| Screen | Rectangle differences | Computed style differences | `::before`/`::after` differences | Attribute, text and element differences |
|---|---|---|---|---|
| S1, both viewports | 0 | 0 | 0 | 4 `style` attribute spellings (`grid-column:1` against `grid-column:1;`), the app's extra hidden `symbol#i-x`, the app's closed `dialog.dialog` (display none) |
| S2, both viewports | 0 | 0 | 0 | the same, plus the app's 0x0 icon sprite that the S2 golden does not have |
| M1, both viewports | 0 | 9 properties, all native-modal only (O-05) | 2 properties, `interactivity` only | no `inert` attribute on `.page`, no `.scrim` element (the backdrop is the native `::backdrop`, computed `rgba(28, 37, 35, 0.5)`, fixed, inset 0), the title text holds U+2068 and U+2069 (SEC-02), the extra `symbol#i-x` |

Every one of these is a ruled or specified difference (spec R1, R2, R13, Non-goals, S1-02, S2-06). There is no reordering, no missing element, no changed copy, no changed spacing, colour or font anywhere. `src/styles.css` against the style block of each golden (`css_diff.py`): the four goldens' blocks are identical to each other and the app's stylesheet differs only by the four rule edits of spec R2 (`.scrim` rule removed, `.scrim, .dialog::backdrop` narrowed to `.dialog::backdrop`, backdrop colour fallback, `::backdrop` added to the reduced-motion selector).

## FE element checklist
Result column: PASS means the measured value equals the value qa.md gives and equals the golden's. Where two values are shown they are 390x844 then 1280x800. Colours are computed values. Source: `rows_s1.json`, `rows_s2.json`, `rows_m1.json`, `states_sheet.json`, `states_sheet_rerun.json` in the checklist evidence folder.

### S1 (37 rows, all PASS)
| # | Result | Measured (390 / 1280) |
|---|---|---|
| S1-01 | PASS | body bg rgb(242, 245, 243), ink rgb(28, 37, 35), 16px/24px weight 400, the system rounded stack (`ui-rounded, "SF Pro Rounded", system-ui, ... sans-serif`), margin 0 |
| S1-02 | PASS | sprite svg 0x0, position absolute, aria-hidden true, focusable false. `i-check` and `i-trash` path data equal the golden's. Third symbol `i-x` present and invisible (its path equals states.html's, ST-06) |
| S1-03 | PASS | page x 0, width 390, max-width 600, padding 24 20 48 / x 120, width 1040, max-width 1040, padding 40 48 48 |
| S1-04 | PASS | flex, align-items baseline, justify space-between, gap 12, padding-bottom 24 / 32 |
| S1-05 | PASS | H1 "Streaks" 22px/28px 700, letter-spacing -0.22px, rgb(46, 90, 80), left at x 20 / 168 |
| S1-06 | PASS | `time[datetime=2026-10-08]` "Thursday 8 October" 16/24 rgb(82, 96, 91), right edge 370 / 1112. Baseline from font metrics: brand 47, date 47.5 / 63, 63.5 (my estimate, half a pixel of rounding; the rectangles equal the golden's and `align-items: baseline` is in force) |
| S1-07 | PASS | 390: one column (main 350 wide, heatmap below it). 1280: grid `500px 380px`, gap 64, main x 168 w 500, heatmap x 732 w 380, both tops 101 |
| S1-08 | PASS | `h2#habits-title.sr-only` "Habits", 1x1, absolute, section `aria-labelledby=habits-title` |
| S1-09 | PASS | list-style none, padding 0, margin 0, row tops 77, 273, 469 / 101, 301, 501, gaps 32 |
| S1-10 | PASS | `h3#h1-name` "Read 20 pages" 18/28 600 rgb(28, 37, 35), padding-top 8, overflow-wrap anywhere, trash `aria-label` "Delete Read 20 pages" |
| S1-11 | PASS | `.cur` "6 days" 14/20 600 rgb(46, 90, 80), `.best` "Best 14" 14/20 400 rgb(82, 96, 91), 12.0 apart, tabular-nums, strip 8 below |
| S1-12 | PASS | `. D D D D D D`, no `data-run-continues`. Thread halves (before, after) per day: Fri 2 fade-thin, thin. Sat 3 thin, run. Sun 4 to Wed 7 run, run. Thu 8 run, none. Run is 4px rgb(59, 107, 96) from Sat 3 to Thu 8, every half centred on the bead. Thu 8 done with today ring |
| S1-13 | PASS | `h3#h2-name` "Stretch 10 minutes", trash "Delete Stretch 10 minutes" |
| S1-14 | PASS | "3 days", "Best 9", same sizes and colours as S1-11 |
| S1-15 | PASS | `D D . D D D .`, `data-run-continues` present. Fade-run at Fri 2's left, run Fri 2 to Sat 3, thin Sat 3 to Mon 5, run Mon 5 to Wed 7, dashed Wed 7 to Thu 8: 4px high, tile 7px (4 on, 3 off), repeat-x, Wed 7's right half anchored `100% 50%` and Thu 8's left half `0% 50%` so a dash starts at the boundary. Thu 8 hollow with today ring |
| S1-16 | PASS | `h3#h3-name` "No phone after 11pm", trash "Delete No phone after 11pm" |
| S1-17 | PASS | "1 day", "Best 4" |
| S1-18 | PASS | `. D . . D . D`, all 13 drawn halves thin (2px) or the thin fade, no 4px and no dashed half anywhere, Thu 8 done with today ring |
| S1-19 | PASS | 44x44, radius 50%, transparent, glyph 20x20 rgb(82, 96, 91), glyph right edge 370 / 668 equals the content edge, name's first-line centre equals the button centre (99, 295, 491 / 123, 323, 523) |
| S1-20 | PASS | all 21 cells 50x92 / 71.42x96, padding 4 0 8, gap 8, radius 999, weekday 12/16 rgb(82, 96, 91), number 16/20 500 tabular, today's weekday and number rgb(28, 37, 35) 700 |
| S1-21 | PASS | bead 36 / 40. Not done: 2px solid rgb(126, 142, 136), fill rgb(242, 245, 243), check opacity 0. Done: fill and stroke rgb(59, 107, 96), check rgb(247, 250, 249) opacity 1, 17.91 / 20.16 wide (56%). Today: `0 0 0 3px rgb(242, 245, 243), 0 0 0 4.5px rgb(126, 142, 136)` |
| S1-22 | PASS | 20 thin halves across the three strips, all 2px, margin-top -1px, rgb(198, 208, 204), centred on the bead centre, before half `left 0 / right 50%`, after half `left 50% / right 0`. The last cell's right half is display none in all 3 rows |
| S1-23 | PASS | `form.add[novalidate]` top 673 / 709, 40 below the list |
| S1-24 | PASS | `label[for=new-habit]` "New habit" 16/24 600 rgb(28, 37, 35), block, 8 above the input |
| S1-25 | PASS | `#new-habit` 255.97x48 / 405.97x48 (qa.md rounds to 256 and 406; the Add button is 82.03 wide), radius 999, border 2px solid rgb(126, 142, 136), fill rgb(253, 254, 254), padding 0 20, attributes only `aria-describedby=new-habit-msg autocomplete=off class id name type`, no placeholder, no maxlength |
| S1-26 | PASS | "Add" 82.03x48, rgb(59, 107, 96), text rgb(247, 250, 249) 16px 600, 12.0 right of the input |
| S1-27 | PASS | `p#new-habit-msg.field-msg.field-error`, `aria-live=polite`, empty, display none |
| S1-28 | PASS | 390: top 793, 40 below the form, 350 wide, padding 20 16. 1280: top 101 (equals the first habit's top), 380 wide, padding 24, sticky top 32. Both: bg rgb(250, 252, 251), radius 20. Sticky is live: scrolled at 1280x500 the panel's top goes 101, 61, 32, 32, 32, identical to the golden (`extras.json`) |
| S1-29 | PASS | `h2.heat-title` "Last 12 weeks" 16/24 600, 12 above the grid |
| S1-30 | PASS | Jul col 1, Aug col 3, Sep col 8, Oct col 12 (x 68.61, 116.17, 235.08, 330.2 / 788.61, 838.5, 963.25, 1063.05, each on its column start), 12/16 rgb(82, 96, 91), `aria-hidden=true` |
| S1-31 | PASS | Mon, blank, Wed, blank, Fri, blank, Sun, 8.0 from the cells, 12px rgb(82, 96, 91), each centred on its row (largest offset 0.01), `aria-hidden=true` |
| S1-32 | PASS | 84 cells, column-major, 23.78 / 24.94 square (qa.md 23.8 / 24.9), the 81 levels equal `heatmapLevels` of sample-history.json, names "Mon 20 Jul, 3 of 3 habits" to "Thu 8 Oct, 2 of 3 habits", `role=img` |
| S1-33 | PASS | l0 6px, transparent fill, inset ring 1.5px rgb(126, 142, 136). l1 7px rgb(120, 150, 139). l2 11px rgb(79, 124, 112). l3 14px rgb(59, 107, 96). l4 17px rgb(46, 90, 80). All radius 50%. Grid cells of l0, l1, l2 and l4 have the same dot sizes as the legend's |
| S1-34 | PASS | Thu 8 Oct: class `hc l2 today`, `aria-current=date`, `::after` 22x22, ring rgb(126, 142, 136), inner dot 11px. The token is 1.5px and Chrome draws that border as 1px at 1x (O-07), identical in the golden |
| S1-35 | PASS | Fri 9, Sat 10, Sun 11: class `hc future`, `aria-hidden=true`, no role, no name, dot background transparent, no shadow, ring border 0 |
| S1-36 | PASS | `aria-hidden=true`, flex-end, 12.0 below the grid, "None", five dots in 20x20 cells, "All", gap 4, 12/16 rgb(82, 96, 91), right edge on the panel's content edge |
| S1-37 | PASS | visible controls 3 trash + 21 day + 1 input + 1 Add, nothing else focusable; no note; dialog closed and display none; no image, canvas or iframe; visible text equals the golden's; 24 visible svgs (3 trash, 21 check glyphs) as in the golden |

### S2 (6 rows, all PASS)
| # | Result | Measured (390 / 1280) |
|---|---|---|
| S2-01 | PASS | S1-01, S1-03 to S1-08, S1-24 to S1-31 and S1-36 re-measured on S2: 16 shared checks, none failing. S1-28's top is 293 / 101 here, not 793 |
| S2-02 | PASS | `p.empty` top 77 / 101, 56 tall, x 20 / 168. `strong` "No habits yet." block 18/28 600 rgb(28, 37, 35), margin-bottom 4. Text "Add one you want to do every day." 16/24 rgb(82, 96, 91). `innerHTML` is `<strong>No habits yet.</strong> Add one you want to do every day.`. No `ul.habits` |
| S2-03 | PASS | form top 173 / 197, 40 below the message. Input and Add enabled, field empty, message empty and display none |
| S2-04 | PASS | 390: panel top 293, bottom 587.58 (qa.md 588), page 390x844 with no scroll. 1280: top 101 at x 732, left column 176 tall = 56 + 40 + 80, no filler |
| S2-05 | PASS | 81 hollow l0 rings (6px, ring rgb(126, 142, 136)) named "Mon 20 Jul, 0 of 0 habits" to "Thu 8 Oct, 0 of 0 habits". Thu 8 Oct class `hc l0 today`, ring 22px. Fri 9 to Sun 11 `hc future` |
| S2-06 | PASS | 0 visible svgs. Sprite present at 0x0 |

Extra: with empty storage nothing is written on load (`localStorage` item is null), as spec R3 says.

### M1 (11 rows, all PASS)
Opened with a real mouse click on "Delete Read 20 pages", measured after the 200ms entrance. Values 390 / 1280.
| # | Result | Measured |
|---|---|---|
| M1-01 | PASS | page measurement with the dialog open equals the closed one (0 differences). Hit test at 6 page targets (day bead, trash, input, Add, heat cell, brand) never reaches the page. `focus()` on them does not move focus. 10 Tab presses never land on a page control (focus cycles Delete habit, out of the document, Cancel) |
| M1-02 | PASS | `::backdrop` rgba(28, 37, 35, 0.5), fixed, inset 0. In the harness's `candidate.png` the four viewport corners are (135, 141, 139), which is rgb(242, 245, 243) under the scrim |
| M1-03 | PASS | open, `:modal` true, `role=alertdialog`, `aria-modal=true`, `aria-labelledby=del-title`, `aria-describedby=del-body`. 350x180 at x 20, y 332 / 400x180 at x 440, y 310, centred both ways. bg rgb(250, 252, 251), radius 20, padding 24, shadow `rgba(28, 37, 35, 0.18) 0px 16px 48px 0px, rgba(28, 37, 35, 0.08) 0px 2px 6px 0px`, transform none |
| M1-04 | PASS | `h2#del-title` text `Delete "` U+2068 `Read 20 pages` U+2069 `"?`, shown as Delete "Read 20 pages"? with straight quotes, 18/28 600 rgb(28, 37, 35), 28 tall (one line), 24 from the box top. A 40-character name wraps to 4 lines, the box grows 180 to 264 high, width stays 350 / 400, still centred |
| M1-05 | PASS | `p#del-body` "Its history is deleted too." 16/24 rgb(82, 96, 91), 8 below the title |
| M1-06 | PASS | `form.dialog-actions[method=dialog]` 24 below the body, columns 145 145 / 170 170, gap 12, buttons 48 tall |
| M1-07 | PASS | `.btn.btn-secondary[type=submit][value=cancel]` "Cancel", transparent, 2px solid rgb(126, 142, 136), rgb(28, 37, 35) 16px 600, left (x 44 / 464) |
| M1-08 | PASS | `.btn.btn-danger[type=submit][value=delete]` "Delete habit", fill rgb(162, 59, 50), text rgb(247, 250, 249), right (x 201 / 646). Cancel is transparent, so it is the only filled button |
| M1-09 | PASS | mouse open: focus on Cancel, `:focus-visible` false, outline none. Keyboard open (Tab to the trash button, Enter): focus on Cancel, `:focus-visible` true, outline 2px solid rgb(28, 37, 35), offset 3px |
| M1-10 | PASS | open: html and body height 844px / 800px (100%), overflow hidden. After Esc both overflow visible again |
| M1-11 | PASS | normal motion: `::backdrop` animation `scrim-in` 180ms (opacity 0 to 1), dialog `dialog-in` 200ms from opacity 0 and `translateY(8px)`. Reduced motion: 0 running animations, animation-name none on both |

### States sheet, computed-style method (17 rows, all PASS)
At 360x780, `states.html` opened from its file path against the running app in the same state, reached with real gestures. 78 specimen-to-live comparisons, 4995 property comparisons (colour, background, four border colours and widths, outline colour, style, width and offset, box-shadow, radius, font size, weight, line height, transform, opacity, cursor, fill, display, margin, padding; bead and icon-button width and height), 0 differences. Specimen-only styling was excluded as qa.md says.
| # | Result | Cases and what was compared |
|---|---|---|
| ST-01 | PASS | 7 cases. Empty submit gives "Name the habit first.", classes `field-msg field-error`, `aria-invalid=true`, `--danger` border. The form grew 80 to 108 (+28), input x 20 and width 225.97 and Add x 257.97 unchanged. Focus returns to the input with the 2px offset-2 ring (the sheet's specimen is unfocused, so I compared with the pointer parked and the input blurred) |
| ST-02 | PASS | 2 cases. 51-character text gives "Keep it to 40 characters or fewer." and the text stays in the field |
| ST-03 | PASS | 2 cases. "read 20 pages" on the sample gives "You already track this habit." and the text stays |
| ST-04 | PASS | 4 cases. 12 habits: input and Add `disabled`, `--wash` fill and `--thread` border on the input, not-allowed cursor, Add `--thread` fill. Label and note `--ink-soft`, note 14/20 `field-note`, 40 tall (two lines) live and in the sheet. Hover on the disabled Add keeps rgb(198, 208, 204), press keeps transform none |
| ST-05 | PASS | whole row, 65 elements in order, 2210 comparisons. "Read 20 pages", `span.cur.none` "No streak yet", 0 `.best` elements, 7 beads none pressed, today ringed, thin thread only |
| ST-06 | PASS | 7 cases. `{` seeded gives the note as first child of `.col-main`. Banner, text, Dismiss button (44x44, 8 from the top and the right, `aria-label` "Dismiss note", `use href=#i-x`, path equal to states.html's), 32 above the empty message in both. Brand: live `H1.brand` against the sheet's `P.brand`, equal computed styles. On 1280 the note sits in the left column (x 168, width 500, heatmap still at x 732) |
| ST-07 | PASS | 4 cases. Default, hover (rgb(46, 90, 80)), keyboard focus (2px solid rgb(28, 37, 35), offset 3px), disabled all equal the sheet. Press: `matrix(0.98, 0, 0, 0.98, 0, 0)` under normal and reduced motion |
| ST-08 | PASS | 2 cases. Cancel default and hover (`--wash`) equal the sheet (outline excluded while the dialog holds focus on Cancel) |
| ST-09 | PASS | 2 cases. Delete habit default and hover equal the sheet, hover rgb(132, 48, 42) |
| ST-10 | PASS | 4 cases. Default, keyboard focus (2px offset 2, border unchanged), error, disabled equal the sheet |
| ST-11 | PASS | 20 cases. Not done, done, today, today done: bead, check glyph, day cell, weekday and number, all equal |
| ST-12 | PASS | 4 cases. Real hover: not-done stroke turns rgb(59, 107, 96), done fill and stroke turn rgb(46, 90, 80) |
| ST-13 | PASS | 2 cases. Keyboard focus on Thu 8 (today, not done): cell outline 2px solid rgb(28, 37, 35), offset 0, radius 999px (cell 45.72x88, a vertical capsule), the bead has no outline and keeps the today ring |
| ST-14 | PASS | `mouse.down` under reduced motion: bead `matrix(0.94, 0, 0, 0.94, 0, 0)`; released off the cell, no tick |
| ST-15 | PASS | 5 cases. Trash at rest (transparent, rgb(82, 96, 91) glyph), hover (`--wash`, rgb(28, 37, 35) glyph), keyboard focus (2px offset -2) equal the sheet |
| ST-16 | PASS | 12 cases. l0, l1, l2, l4 on the sample, today ring, future blank equal the sheet. Level 3 live on the sample plus "Drink water": Mon 20 Jul `hc l3` "Mon 20 Jul, 3 of 4 habits" with a 14px dot equal to the sheet's. The R10 worked-example cells match too (Tue 6 Oct 3 of 4 l3, Thu 8 Oct 2 of 4 l2, Tue 21 Jul 1 of 4 l1, Wed 12 Aug 0 of 4 l0) |
| ST-17 | PASS | none of 26 sheet-only strings (title, subtitle, group headings, captions, specimen names such as "Level 0, none of the habits") and none of 19 sheet-only classes in the live DOM in 5 states (sample, fresh with an error, 12 habits, unreadable data, sample plus an added habit). No sheet-only rule in `src/styles.css` |

First-pass flags, for the record. Three groups of my own checks failed on the first run and were corrected, none by the app. (1) The S1 script, 15 of its 82 results: it expected a different serialisation of the dashed gradient, an unscaled not-done check glyph (it is scaled to 0.6 and hidden), an exact 256 and 82 (content widths give 255.97 and 82.03), tighter heat-cell positions than Chrome's layout units hold, a computed 1.5px ring (Chrome returns 1px), and 3 visible svgs instead of 24. (2) M1-01 compared `body.innerText`, which includes the open dialog's own text, and expected Tab to stay inside the dialog when Chrome moves it out of the document. (3) ST-01 (the Add button) and ST-05 (one bead) were measured while the pointer still sat on the Add button or on a new bead, which drew the hover fill. Each was re-run with the expectation or the pointer fixed (`states_sheet_rerun.json` for the last group). None of these adjustments can hide an app difference, because the whole-page comparison above found 0 style and 0 rectangle differences against the golden independently of them.

## Findings
None. No addition, subtraction or modification of the design was found.

Candidates I considered and did not raise: the U+2068 and U+2069 marks in the dialog title (specified, invisible, O-04); the native modal's UA `max-height` and `overflow` (O-05); the 1.5px ring that draws as 1px (O-07); the stale harness version in qa.md (O-08). Each is ruled, specified or a documentation matter and none changes what the user sees against the golden.

## Observations
- **O-01 Baseline on 2.1.3.** qa.md asked that the first captures on a later harness show 0 and `dimensions_match` true. They do, for all six, so the 2.1.1 baseline stands and the budget needed no widening. I also ran the three screens at 360x780 and at 390x844 with `--dpr 2` (not part of the gate): all 0 mismatched pixels, dimensions match (`extra-360x780/`, `extra-dpr2/` in the checklist folder). The design notes' 360 values (habit tops 77, 269, 461, panel top 781, dialog 320x180 at x 20, y 300) are therefore met too.
- **O-02 M1 differs at a level below the threshold, and the app is not the cause.** At any level 149 pixels (390) and 88 pixels (1280) differ from the golden, at most 4 of 255 on a channel, all on the rounded border of the Cancel button. The same count appears when the golden's own DOM is turned into a native `showModal()` dialog (`.scrim` and `inert` removed) and compared with the static golden. Compared with the app's `candidate.png`, that native copy gives **0 differing pixels at any level** at both widths. So the app equals the golden rendered as a native modal exactly, and the noise is the engine drawing a static open dialog and a top-layer one a hair apart. The 0.1 threshold is far above it (largest delta 4 against about 44 needed).
- **O-03 What the blur hides.** With the last line of `open-delete-dialog.js` removed, M1 gives **877 mismatched pixels at 390 and 977 at 1280**, the numbers qa.md cites for 2.1.1, all inside x 39 to 193, y 435 to 492 (390) and x 459 to 638, y 413 to 470 (1280), which is the Cancel button's 2px ring plus its 3px offset. Before the blur, focus is on the Cancel `BUTTON`, `:focus-visible` true, outline 2px solid rgb(28, 37, 35), offset 3px. After it, focus is on `body` with the dialog open and modal. So the blur removes exactly the Cancel focus ring, which the golden does not draw, and nothing else. The ring itself is proven by M1-09 above and by `@R13`. M1 run again with the blur: 0 and 0.
- **O-04 The title marks are invisible to the pixel gate.** U+2068 and U+2069 draw nothing, so only the script's string check guards them. I ran the script against the live app with the shipped title (accepted) and with three wrong expectations, the pre-SEC-02 title, the marks swapped, and the closing mark missing: all three throw "unexpected dialog title". The page's `#del-title` is `Delete "`, U+2068, `Read 20 pages`, U+2069, `"?`, so the SEC-06 strip leaves that name unchanged and the check matches the shipped title. This is a ruled difference from the golden's literal title text (the golden has no marks): invisible, and the accessible name carries two characters that screen readers ignore.
- **O-05 Native modal against the golden's static dialog.** The M1 computed-style differences are `interactivity` (the golden's `inert` page against the app's modal-made inertness, 323 elements), `overlay`, `user-select` on the dialog subtree, and the UA rules for a modal dialog, `max-height: calc(100% - 38px)` with `overflow: auto`. None changes a pixel at the golden's content. The `max-height` only matters if a dialog is ever taller than the viewport minus 38px, which a 40-character name does not reach even at 320 wide (264 high).
- **O-06 There is no "Allowed differences" section.** The brief named one, but spec.md, qa.md and BUILD.md have none. I judged against the set that is stated across spec R1, R2, R13, the Non-goals and the checklist rows (S1-02's extra `i-x`, S2-06's sprite, M1's native backdrop and no `inert`, the title marks). The whole-page comparison found nothing outside that set. A short list in qa.md would save the next tester the search.
- **O-07 Declared 1.5px, drawn 1px.** S1-34 and S1-21 give the ring as 1.5px (tokens `--today-ring` and `--dot-ring`). Chrome's computed `border-width` is 1px at 1x for the `::after` ring (the heat-cell hollow ring is an inset shadow and keeps 1.5px). The golden is identical, so this is not a difference, only a reading note for the row.
- **O-08 qa.md is stale on the harness.** The Fidelity gate says "The installed harness is 2.1.2" and that the first run on 2.1.2 must confirm the baseline. The installed harness is 2.1.3 and that confirmation is now this report. The `open-delete-dialog.js` bullet already records a 2.1.3 measurement, so the document disagrees with itself. Owner's edit, not mine.
- **O-09 What the gate cannot see.** The harness forces `reduced_motion=reduce` for both renders and `bypass_csp`, photographs no hover, focus or press state, and uses the machine's system font for both sides. So the entrance animation (M1-11), hover, focus and press (ST rows) and the CSP are checked by computed style and by the functional suites, not by the diff. My own row measurements ran with the CSP in force and normal motion (the whole-page comparison used reduced motion like the harness), and the app rendered and measured the same, so the CSP does not change what is drawn. The 0 budget is as strong as the same-machine, same-fonts rule that qa.md already states.
- **O-10 Process slips of mine.** See Processes. None touched the product, and none affects the validity of the evidence.

## Evidence
All under `{workspace}/examples/streaks/docs/modules/app/qa/`.
- Six gate runs: `fidelity-today-390x844/20261009-213131/`, `fidelity-today-1280x800/20261009-213136/`, `fidelity-today-empty-390x844/20261009-213140/`, `fidelity-today-empty-1280x800/20261009-213144/`, `fidelity-delete-dialog-390x844/20261009-213148/`, `fidelity-delete-dialog-1280x800/20261009-213152/` (each `golden.png`, `candidate.png`, `diff.png`, `styles.json`, `report.json`).
- Checklist and honesty evidence: `fidelity-checklist/20261009-213300/` holding `exact_diff.json` (any-level pixel counts and hashes), `generic_diff.json` (whole-page comparison), `rows_s1.json`, `rows_s2.json`, `rows_m1.json`, `states_sheet.json` and `states_sheet_rerun.json`, `gate_honesty.json` and `honesty/` (the no-blur, repeat and native-modal-control PNGs), `css_diff.json`, `extras.json`, `measure_s1_*` and `measure_s2_*` (the raw measurements of golden and app), `extra-360x780/`, `extra-dpr2/`, and the Python scripts that produced them (`common.py`, `measure.py`, `generic_diff.py`, `rows_*.py`, `states_sheet*.py`, `gate_honesty.py`, `css_diff.py`, `extras.py`, `exact_diff.py`).

## Processes
- Started: one `python -m http.server 52346 --bind 127.0.0.1` from the project root, listener PID 49448 (under the tool shell's bash wrapper 39860). Stopped by exact PID with `Stop-Process -Id 49448`. Afterwards `curl http://127.0.0.1:52346/` returns no response (HTTP 000, connection refused).
- Browsers: every harness run and every measurement script launched its own headless Chromium 149 through Playwright and closed it. A process listing after the last run shows no python, chrome or http.server process of mine. Nothing was started with a visible window and the clipboard was never touched.
- One stray process: an accidentally empty `python -` heredoc in a command hung. I checked its creation time and parent against my command, then stopped it by exact PID 46636. No other process was stopped.
- The state-script tests ran against my server through `STREAKS_BASE_URL`, with `PYTHONDONTWRITEBYTECODE=1` and `-p no:cacheprovider`, so pytest started no server and left no cache.
- Rule slips of mine, stated plainly: I patched my own scratch script `rows_s1.py` once with a Python heredoc instead of the Write tool (the fixes listed under the first-pass note), I sent the harness's stdout to `/dev/null` on one loop (the dpr 2 extras), and I ran the empty heredoc above. All other files were created with the Write tool. I removed my own `__pycache__` from the checklist folder.
- Untouched, checked with `git status --short` (only `docs/modules/app/qa/fidelity-*` and `fidelity-checklist/` are new): `src/`, `tests/`, `index.html`, `docs/design/`, `spec.md`, `qa.md`, `BUILD.md`. Nothing was committed.
