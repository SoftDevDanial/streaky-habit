---
module: app
kind: qa
ran_against: running-app
status: green
counts: { pass: 68, fail: 0, blocked: 0, untested: 2 }
---
# QA findings: app

**Verdict: PASS.** No failures. Project HEAD `f4563ab`, branch main, nothing under `src/`, `tests/`, `index.html` or `docs/design/` was changed (`git status` shows only the new evidence folder).

Evidence folder: `{workspace}/examples/streaks/docs/modules/app/qa/qa/20261009-144515/`

Run: headless Chromium 149.0.7827.55, `python -m http.server` on 127.0.0.1:52222 (app root) and 52223 (`--directory ..`, for the sub-path scenario), both stopped afterwards.

## Suites run (step 1)
| Suite | Command | Result | Evidence |
|---|---|---|---|
| Browser | `python -m pytest tests/browser -v -rA --junitxml=...` with `STREAKS_BASE_URL` and `STREAKS_SUBPATH_URL` set | **115 passed, 0 failed, 0 skipped** (24.7 s). Matches the builder's 115. The sub-path test ran (not skipped). | `pytest-output.txt`, `pytest-junit.xml` |
| Unit | `node --test "tests/**/*.test.js"` | **66 pass, 0 fail** (Node v24.11.1). Matches the builder's 66. | `node-test-output.txt` |

## Counts
- qa.md scenarios: 70 (66 functional, 1 `@R27`, 3 `@R28`).
- **Passed 68**: all 66 functional scenarios (each has at least one passing pytest test, and most also my independent probe), `@R27` (run by me, 11 of 11 steps), `@R28` "The fidelity state scripts are right".
- **Failed 0. Blocked 0.**
- **Untested 2** (by contract, not mine to run): `@R28` "Each screen is 1-to-1 with its golden" (6 pixel-diff captures) and `@R28` "Every specimen on the states sheet matches the live state". Both belong to the fidelity finder after functional green (qa.md, Fidelity gate).
- My independent probe: **118 checks pass, 0 fail, 0 error** (`probe.py`, `results.json`), plus 4 follow-up checks that pass (`probe2.py`, `probe2-results.json`).

## Scenario table (step 2)
Test names are in `tests/browser/`. "Read vs Then" is my reading of the test against its scenario's Then lines. Every test was judged at least as strong as its Then lines except where a note says otherwise (see "Test strength notes").

| # | Scenario | R# | Test or probe | Result |
|---|---|---|---|---|
| 1 | Head, CSP and relative URLs | R1 | `test_entry::test_R1_head_csp_and_relative_urls`; probes S1.imports, S1.template | PASS |
| 2 | The app works from a sub-path | R1 | `test_entry::test_R1_the_app_works_from_a_sub_path` (served on :52223, ran) | PASS |
| 3 | The static skeleton | R1 | `test_entry::test_R1_static_skeleton` | PASS |
| 4 | Stylesheet is the golden CSS with the three changes | R2 | `test_entry::test_R2_stylesheet_is_the_golden_css_with_the_listed_changes`, `test_R2_golden_style_block_is_the_same_in_every_golden`; probe F15 (backdrop colour) | PASS |
| 5 | No sample data in the shipped files | R26 | `test_platform::test_R26_no_sample_data_in_the_shipped_files`; probe S1.sample (also scans `styles.css`) | PASS |
| 6 | Query strings and fragments do not seed (3 rows) | R26 | `test_platform::test_R26_query_strings_and_fragments_do_not_seed[?demo=1, ?seed, #sample]` | PASS |
| 7 | No globals and no hooks | R26 | `test_platform::test_R26_no_globals_and_no_hooks`; probe S1.globals | PASS |
| 8 | The empty first screen | R3 | `test_render::test_R3_the_empty_first_screen`; probes F1.model, F1.nowrite, F1.form | PASS |
| 9 | Brand and date | R4 | `test_render::test_R4_brand_and_date` | PASS |
| 10 | The date follows the device clock (3 rows) | R4 | `test_render::test_R4_the_date_follows_the_device_clock[3]`; probe F10.tz (17 days in 6 time zones incl. DST, leap day, year boundary) | PASS |
| 11 | English under a German browser locale | R4 | `test_render::test_R4_english_under_a_german_browser_locale`; probe F16.de | PASS |
| 12 | Rows in stored order | R5 | `test_render::test_R5_rows_in_stored_order`; model runs F14 | PASS |
| 13 | The sample's streak lines (3 rows) | R6 | `test_render::test_R6_the_samples_streak_lines[3]` | PASS |
| 14 | No streak yet, with and without a best | R6 | `test_render::test_R6_no_streak_yet_with_a_best` plus `test_add::test_R6_a_habit_just_added_has_no_streak_and_no_best` | PASS |
| 15 | The sample's week strips (3 rows) | R7 | `test_render::test_R7_the_samples_week_strips[3]` | PASS |
| 16 | Day names, today, and nothing outside the window | R7 | `test_render::test_R7_day_names_today_and_nothing_outside_the_window` | PASS |
| 17 | The name does not change with the state | R7 R8 | `test_tick::test_R8_the_name_does_not_change_with_the_state` (killed mutation M18) | PASS |
| 18 | Toggling a day updates bead, streak, heatmap, storage (6 rows) | R8 R16 | `test_tick::test_R8_toggling_a_day_updates_the_bead_in_place[6]`; probe F2.cell-inplace | PASS |
| 19 | Keyboard toggling keeps focus | R8 | `test_tick::test_R8_keyboard_toggling_keeps_focus`; probe F4.space, F4.enter | PASS |
| 20 | Ticking twice restores the saved value | R8 | `test_tick::test_R8_ticking_twice_restores_the_saved_value` | PASS |
| 21 | The sample's heatmap | R9 | `test_render::test_R9_the_samples_heatmap` | PASS |
| 22 | A Monday shows six future cells and a shifted grid | R9 | `test_render::test_R9_a_monday_shows_six_future_cells_and_a_shifted_grid` | PASS |
| 23 | First habit on a fresh day | R10 R16 | `test_add::test_R10_the_first_habit_on_a_fresh_day`; probe F2.add1 | PASS |
| 24 | Enter adds at the bottom, trimmed, heatmap recounts | R10 | `test_add::test_R10_enter_adds_at_the_bottom_trimmed_and_the_heatmap_recounts`; probe F2.add2 | PASS |
| 25 | Rejected names keep the text and show one message (6 rows) | R11 | `test_add::test_R11_rejected_names_keep_the_text_and_show_one_message[6]`; probe F5.errors (7 names) | PASS |
| 26 | Exactly 40 characters is accepted | R11 | `test_add::test_R11_exactly_40_characters_is_accepted` (plus code-point test) | PASS |
| 27 | No message while typing | R11 | `test_add::test_R11_no_message_while_typing`; probe F5.typing | PASS |
| 28 | One message at a time, replaced, then cleared | R11 | `test_add::test_R11_one_message_at_a_time_replaced_then_cleared_on_success` | PASS |
| 29 | The twelfth habit disables the form | R12 | `test_add::test_R12_the_twelfth_habit_disables_the_form`; probe F13.12th | PASS |
| 30 | Twelve habits at load | R12 | `test_render::test_R12_twelve_habits_at_load` | PASS |
| 31 | Deleting one of twelve enables the form again | R12 R15 | `test_delete::test_R12_deleting_one_of_twelve_enables_the_form_again`; probe F13.delete12 | PASS |
| 32 | Confirmation opens as a modal with focus on Cancel | R13 | `test_delete::test_R13_the_confirmation_opens_as_a_modal_with_focus_on_cancel`; probes F3.open, F15.inert | PASS |
| 33 | Tab never leaves the dialog for the page | R13 | `test_delete::test_R13_tab_never_leaves_the_dialog_for_the_page`; probe F4.tab-dialog, F4.tab-wrap | PASS |
| 34 | A long name wraps in the title, box keeps its width | R13 | `test_delete::test_R13_a_long_name_wraps_in_the_title_and_the_box_keeps_its_width`; probe F7.dialog-box (360 px) | PASS |
| 35 | Cancel, Esc and a backdrop click keep the habit (3 rows) | R14 | `test_delete::test_R14_cancel_esc_and_a_backdrop_click_keep_the_habit[3]`; probes F3.cancel, F3.esc, F3.backdrop, F3.backdrop2 | PASS |
| 36 | Clicks inside the box, and drags out of it, keep it open | R14 | `test_delete::test_R14_clicks_inside_the_box_and_drags_out_of_it_keep_the_dialog_open` (killed mutation M17); probe F3.inside | PASS |
| 37 | Esc after an earlier delete still keeps the habit | R14 | `test_delete::test_R14_esc_after_an_earlier_delete_still_keeps_the_habit` | PASS (note N4) |
| 38 | Deleting moves focus to the next one and recounts | R15 R16 | `test_delete::test_R15_deleting_a_habit_moves_focus_to_the_next_one_and_recounts`; probe F3.confirm-middle, F3.confirm-focus | PASS |
| 39 | Deleting the bottom habit moves focus to the field | R15 | `test_delete::test_R15_deleting_the_bottom_habit_moves_focus_to_the_field`; probe F3.confirm-last | PASS |
| 40 | Deleting the only habit shows the empty message | R15 | `test_delete::test_R15_deleting_the_only_habit_shows_the_empty_message`; probe F3.confirm-only | PASS |
| 41 | History goes with the habit | R15 | `test_delete::test_R15_history_goes_with_the_habit`; probe F3.readd | PASS |
| 42 | Changes survive a reload and a closed tab | R16 | `test_storage::test_R16_changes_survive_a_reload_and_a_closed_tab`; probes F2.reload, F2.newtab | PASS |
| 43 | Loading writes nothing | R16 | `test_render::test_R16_loading_writes_nothing` (pretty-printed seed, so it can tell a re-save); probe F2.reload.nowrite | PASS |
| 44 | Unreadable saved data resets and shows the note (16 rows) | R17 | `test_storage::test_R17_unreadable_saved_data_resets_the_list_and_shows_the_note[16]`; probe F6.variants (15 more raw values) | PASS |
| 45 | Readable edge cases load without a note (5 rows) | R17 | `test_storage::test_R17_readable_edge_cases_load_without_a_note[5]`; probe P2.* | PASS (note N3) |
| 46 | Dismiss removes the note, moves focus, does not come back | R17 R22 | `test_storage::test_R17_dismiss_removes_the_note_moves_focus_to_the_field_and_it_does_not_come_back`; probe F6.dismiss, F6.reload | PASS |
| 47 | On desktop the note sits in the left column | R17 | `test_storage::test_R17_on_desktop_the_note_sits_in_the_left_column`; screenshot `shots/F6-note-1280.png` | PASS |
| 48 | Storage that cannot be used at all | R18 | `test_storage::test_R18_storage_that_cannot_be_used_at_all`; probe F12.getitem (getItem throws) | PASS |
| 49 | A save that fails | R18 | `test_storage::test_R18_a_save_that_fails`; probes F12.reset-save-fails, F12.plain-error | PASS |
| 50 | View moves to the new day within a minute while visible | R19 | `test_rollover::test_R19_the_view_moves_to_the_new_day_within_a_minute_while_visible`; probes F9.early (23:59:59.9 still Thursday), F9.late | PASS |
| 51 | The heatmap shifts when a new week starts | R19 | `test_rollover::test_R19_the_heatmap_shifts_when_a_new_week_starts` | PASS |
| 52 | The add form and its focus survive the rollover | R19 | `test_rollover::test_R19_the_add_form_and_its_focus_survive_the_rollover` | PASS |
| 53 | An error message survives the rollover | R19 | `test_rollover::test_R19_an_error_message_survives_the_rollover` | PASS |
| 54 | Focus on today's bead stays on today's bead | R19 R22 | `test_rollover::test_R19_focus_on_todays_bead_stays_on_todays_bead` | PASS |
| 55 | The view moves at once when the tab is shown again | R20 | `test_rollover::test_R20_the_view_moves_at_once_when_the_tab_is_shown_again`; probe F9.vis-same | PASS |
| 56 | Phone width 360 | R21 | `test_platform::test_R21_phone_width_360`; probes F7.* (12 habits with 40-char unbroken names, dialog, note, error, 320 px extra) | PASS |
| 57 | Tab order | R22 | `test_platform::test_R22_tab_order`; probes F4, F13.skip-disabled | PASS |
| 58 | Tab order with the note | R22 | `test_platform::test_R22_tab_order_with_the_note` | PASS |
| 59 | Focus rings on keyboard focus only (4 rows) | R22 | `test_platform::test_R22_focus_rings_on_keyboard_focus[4]`; `shots/F4-focus-ring-390.png` | PASS |
| 60 | A mouse click draws no ring | R22 | `test_platform::test_R22_a_mouse_click_draws_no_ring` | PASS |
| 61 | Motion without reduced motion | R23 | `test_platform::test_R23_motion_without_reduced_motion` | PASS |
| 62 | Everything appears at once under reduced motion | R23 | `test_platform::test_R23_everything_appears_at_once_under_reduced_motion`; probe F15 | PASS |
| 63 | Markup in a name stays text | R24 | `test_platform::test_R24_markup_in_a_name_stays_text`; probe F11.* (10 hostile names, `__proto__`, reload) | PASS |
| 64 | No HTML sinks in the source | R24 | `test_platform::test_R24_no_html_sinks_in_the_source`; probe S1.sinks (adds `styles.css`) | PASS (note N1) |
| 65 | Every request stays on the device's own files | R25 | `test_platform::test_R25_every_request_stays_on_the_devices_own_files`; every probe flow logged requests and console | PASS |
| 66 | The CSP is in force | R25 | `test_platform::test_R25_the_csp_is_in_force` (killed mutation M12) | PASS |
| 67 | The headline flows on a cold start | R27 | `python tests/browser/live_e2e.py` run by me against :52222, 11 of 11 steps, 0 console errors, 0 page errors, 0 requests outside the rule, date unchanged (2026-10-09). Output in `live-e2e-run/` | PASS (note N6) |
| 68 | Each screen is 1-to-1 with its golden | R28 | fidelity finder (pixel diff) | NOT RUN here |
| 69 | The fidelity state scripts are right | R28 | `test_fidelity_inputs::test_R28_the_seed_script_writes_the_sample_and_nothing_else`, `test_R28_the_after_load_script_leaves_the_dialog_open_with_nothing_focused`; extra `test_render::test_R28_the_rendered_page_has_the_markup_of_the_goldens`; probe F8 (1280 layout and dialog at the golden positions) | PASS |
| 70 | Every specimen on the states sheet matches | R28 | fidelity finder (computed style) | NOT RUN here |

## R# coverage (step 4)
Every R1 to R28 has at least one passing scenario. No R# is without coverage.

| R# | Passing scenario rows | R# | Passing scenario rows |
|---|---|---|---|
| R1 | 1, 2, 3 | R15 | 31, 38, 39, 40, 41 |
| R2 | 4 | R16 | 18, 23, 38, 42, 43 |
| R3 | 8 | R17 | 44, 45, 46, 47, 49 |
| R4 | 9, 10, 11 | R18 | 48, 49 |
| R5 | 12 | R19 | 50, 51, 52, 53, 54 |
| R6 | 13, 14 | R20 | 55 |
| R7 | 15, 16, 17 | R21 | 56 |
| R8 | 17, 18, 19, 20 | R22 | 46, 54, 57, 58, 59, 60 |
| R9 | 21, 22 | R23 | 61, 62 |
| R10 | 23, 24 | R24 | 63, 64 |
| R11 | 25, 26, 27, 28 | R25 | 65, 66 |
| R12 | 29, 30, 31 | R26 | 5, 6, 7 |
| R13 | 32, 33, 34 | R27 | 67 |
| R14 | 35, 36, 37 | R28 | 69 (rows 68 and 70 are the fidelity finder's) |

## Independent cross-check (step 3)
`probe.py` (own Playwright script, real gestures only, `page.clock` / context clock for every date, own helpers, no import of `conftest.py`) holds a Python oracle of the habit-logic rules written from `docs/modules/habit-logic/spec.md` and compares the whole DOM, `localStorage` text and write count to it. It also counts every `setItem` call through an init-script wrapper that only logs to the console (no `window` property). Results (all PASS):

| Flow | What it drove | Result |
|---|---|---|
| F1 first visit | empty screen, 84 cells, no write, console clean, Tab order | PASS |
| F2 add, tick today and yesterday, reload, new tab | model equal after each step, one write per change, focus rules, heat cell updated in place | PASS |
| F3 delete: Cancel, Esc, backdrop (5,5), backdrop 3 px outside the corner, clicks inside, open A / Cancel / open B / delete, last, only, re-add | zero writes on every keep path, correct habit removed, ids renumbered, focus targets | PASS |
| F4 keyboard only | Tab, type, Enter, Shift+Tab to beads, Space and Enter, stray Enter on Cancel keeps the habit (T7), Tab trapped in the dialog, keyboard delete | PASS |
| F5 name errors | 7 rejected names (empty, spaces, 2 too long, 3 duplicates by case), no write, message replaced then cleared | PASS |
| F6 unreadable data | 15 raw values (incl. empty string, NUL, bare `true`, `{"habits":[]}`), exactly one reset write, note, Dismiss, reload | PASS |
| F7 360 x 780 (and 320) | no horizontal scroll and nothing past the right edge with 12 habits of 40-char unbroken names, the 12-note, the unreadable note, an error message, and the dialog with a long name | PASS |
| F8 1280 x 800 | column x168 w500, heatmap x732 w380, dialog 400 wide at x440 | PASS |
| F9 rollover | dialog open across midnight then Cancel, Esc, Delete (right habit, Friday model equal), never early (23:59:59.9), rollover writes nothing, tick and add after rollover | PASS |
| F10 time zones | 17 local days in LA, Auckland, London (both DST changes), Kiritimati, KL: leap day, year boundary, the habit-logic R12 month-label examples (2027-01-07, 2026-03-31) | PASS |
| F11 names as text | `__proto__`, `constructor`, `toString`, `<b>`, `<script>`, quotes, entities, emoji; literal everywhere, survives reload, `Object.prototype` untouched | PASS |
| F12 storage failures | `getItem` throws, reset save throws, plain `Error` on save: no console or page error | PASS |
| F13 twelve habits | disabled controls skipped by Tab, delete re-enables, focus on input | PASS |
| F14 model-based random runs | 3 seeds x 90 operations (tick, double click, add valid and invalid, delete, keep by 3 ways, reload): DOM, stored text, write count and focus equal the oracle after every operation | PASS |
| S1 static scans | no HTML sink, no sample name, no network API or absolute URL, no async or timers, one clock read (`app.js`), relative imports, no window assignment, no `<template>` or inline script (all over `src/` including `styles.css`) | PASS |
| P2 follow-ups | saved days sorted and de-duplicated at the next save, a saved future day kept, extra properties dropped | PASS |

Negative controls (`negctl.py`): the oracle reports a difference for an un-modelled tick, an un-modelled delete and a wrong day, so the probe can fail. The builder's own negative controls plus my mutation spot-check (below) show the pytest tests can fail.

Screenshots (390, 360, 1280): `shots/` (first visit, ticked, dialog, error, note, 12 habits at 360 with long names, long-name dialog at 360, odd names, 1280 sample and dialog, 3 end states of the random runs). I looked at the 12-habit 360 view, the 390 dialog and the 1280 note view: no overlap, clipping or horizontal scroll visible.

## Mutation spot-check of the tests (can each test fail?)
`mutate.py` applies one bug at a time to a scratch copy of the project (the original was not touched), serves the copy and runs the whole suite. Baseline of the copy: 114 passed, 1 skipped (the sub-path test, no second server). 24 mutations: **20 killed, 4 survived**.
- Killed (each by the named R# tests): backdrop click does not close (R13, R14), rollover skips heatmap (R19, R20), unreadable data not reset in storage (17 R17 tests), delete always focuses input (R15), no `aria-invalid` (R11), tick not saved (R8), today cell loses `aria-current` (R3, R9, R28), `visibilitychange` ignored (R20), CSP loses `connect-src` (R1), no focus to input after a rejected name (R11), add/delete skip the heatmap recount (27 tests), Add not disabled at 12 (R12), tick skips the heat cell (R8), drag from inside closes the dialog (R14), day name changes with state (R7, R8, R22, R28), note not first child (R17, R22), no 30 s check (R19), read failure not caught (R18), empty `ul.habits` rendered (R3, R15, R17, R28), heat level 4 capped at 3 (R8, R9, R15, R28).
- Survived, see N3, N4, N5: M02 (no explicit focus return after keep), M10 (days not sorted and de-duplicated at load), M11 (dialog `returnValue` not reset), M22 (rollover writes storage).

## Test strength notes (none fails a scenario)
These are weaknesses against the scenario text. In each case the real app is correct, shown by my probes. Severity is for the tests, not the app.
- **N1 (low).** `test_R24_no_html_sinks_in_the_source` and `test_R26_no_sample_data_in_the_shipped_files` glob `src/*.js` only, while the scenarios say every file under `src/`. `src/styles.css` is not scanned. My scan covers it and is clean.
- **N2 (low).** The R11, R14 and R17 "stored(page) equals S" assertions use a seed that is byte-identical to what the app writes, so they cannot tell "saved nothing" from "re-saved the same text". My `setItem` counter shows zero writes on every rejected name, Cancel, Esc, backdrop click, Dismiss and reload. R16 "at no other time" has no scenario for the rollover (mutation M22 survived); my probe F9 confirms the rollover writes nothing.
- **N3 (low).** Scenario 45 row "unsorted and duplicated days" asserts only the streak line, which ignores order and duplicates by design, so decode's sort and de-duplication (M10) is untested. The Contracts say the next save is ascending without duplicates. My probe P2 confirms it.
- **N4 (info, equivalent mutants on Chromium 149).** M02 and M11 survive because Chromium already returns focus to the opener on close and already resets `returnValue` on a later Esc (measured on a plain dialog: `'delete'` after submit, `''` after reopen plus Esc). The explicit code exists for Safari and Firefox, which this plan does not run (spec browser floor). So `test_R14_esc_after_an_earlier_delete_still_keeps_the_habit` and the focus-return half of R14 cannot fail on Chromium for those two lines.
- **N5 (low).** Smaller gaps, all covered by my probes: scenario 32's "no dialog for Stretch ever opens" is inferred from the closed dialog; R10 "no focus move after a successful add" is tested for Enter only (my F2.add1.focus covers the Add click); R14's "looked up after a rollover while the dialog was open" has no test (my F9 cancel, Esc and Delete cases pass); scenario 50 checks "still Thursday" only at 23:59:59 (my F9.early at 23:59:59.9).
- **N6 (process).** The official `@R27` gate artifact (`docs/modules/app/qa/live-e2e/<datetimestamp>/`) is not produced here. I ran the same script into `qa/qa/20261009-144515/live-e2e-run/` (01-first-visit.png to 11-reloaded-again.png, `steps.json`, `console.json`, `network.json`, `summary.json`), which passed. The orchestrator's official run is still owed.

## Failures
None. No reproduction steps are needed. No severity above "low" applies, and the only items are the test-strength notes above.

## Files in the evidence folder
`pytest-output.txt`, `pytest-junit.xml`, `node-test-output.txt`, `functional/` (8 screenshots the suite saved), `probe.py`, `results.json`, `probe2.py`, `probe2-results.json`, `negctl.py`, `mutate.py`, `mutation-results.json`, `live-e2e-run/`, `shots/` (18 screenshots).

## Process notes (declared deviations)
- I used one Bash heredoc (a `python - <<EOF` patch of my own `probe.py`). It raised an error before writing, so nothing was modified; I then rewrote the file with the Write tool.
- `tee` was used to keep `pytest-output.txt` and `node-test-output.txt`. No `>` redirects were used.
- A scratch copy of the project was made in the session scratchpad for the mutation check and removed by the script. The original project files were never written.
