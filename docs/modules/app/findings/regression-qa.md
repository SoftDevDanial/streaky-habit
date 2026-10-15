---
module: app
kind: qa
run: regression
ran_against: running-app
status: green
counts: { pass: 170, fail: 0, blocked: 0, untested: 6 }
---
# Regression QA findings: app (v1.1.0, full regression)

## Verdict

GREEN on every functional scenario that a test holds. 170 of 176 live scenarios PASS, 0 FAIL, 0 BLOCKED. Of the 170, 169 are held by a test that passed and 1 is a finder check read from this run's own `-rA` output. The 6 UNTESTED are the live gate, its control, the fidelity gate, its controls and the states check, which this regression does not run. Failing test ids in any suite: none.

Role. QA finder (read-only), the full regression at the tail of execute, written 2026-10-15. Git HEAD `ddf43f6` (the code is equal to `4af5d75`, `git diff 4af5d75 ddf43f6 -- src tests index.html` is empty). The only change to `docs/modules/app/qa.md` in that range is a wording pass (ST-04 colour and the fidelity method text), so no functional scenario text moved. Each verdict below comes from a run made today and a folder listed on disk.

## Runs (folders listed on disk)

| Suite | Folder | Counts, read from the run's own files |
|---|---|---|
| Node | `docs/modules/app/qa/regression-qa/20261015-184158-node/` (`junit.xml`, `node-test.txt`, `run-meta.txt`) | `node-test.txt` has `tests 137`, `pass 137`, `fail 0`. `junit.xml` has 137 testcases, all PASS, 0 FAIL, 0 SKIP. Its root carries no counts. Exit 0 in 0.7 s |
| Chromium | `docs/modules/app/qa/regression-qa/20261015-184210-chromium/` (`junit.xml`, `pytest-rA.txt`, `run-meta.txt`, evidence json) | `junit.xml` root: tests 358, failures 0, errors 0, skipped 0. `pytest-rA.txt` ends `358 passed in 144.80s`. Exit 0 in 148.1 s |
| WebKit | `docs/modules/app/qa/regression-qa/20261015-184449-webkit/` (`junit.xml`, `pytest-rA.txt`, `run-meta.txt`, evidence json) | `junit.xml` root: tests 358, failures 0, errors 0, skipped 1. `pytest-rA.txt` ends `357 passed, 1 skipped in 234.17s`. Exit 0 in 237.6 s |

Commands. All foreground, from the project root, each bounded by a runner cap (120, 400 and 480 s). No cap was hit.
- Node. `node --test --test-reporter=spec --test-reporter-destination=stdout --test-reporter=junit --test-reporter-destination=<folder>/junit.xml "tests/**/*.test.js"`.
- Chromium. `python -m pytest tests/browser -q -rA -p no:cacheprovider --junitxml=<folder>/junit.xml`, with `STREAKS_EVIDENCE_DIR=<folder>` and `PYTHONDONTWRITEBYTECODE=1`. The conftest started and stopped its own two `http.server` processes.
- WebKit. The same command with `--engine webkit`.
- `-p no:cacheprovider` keeps `.pytest_cache` out of the project root. The CLAUDE.md command without it writes there. The scratch runner `runner.py` is in the session scratchpad, outside the project.

## Baselines, compared by test id

- Node. The 137 ids equal the ids of `docs/modules/app/qa/functional/20261015-174935-node/junit.xml`. No verdict changed.
- Chromium. The 358 ids equal the ids of `docs/modules/app/qa/functional/20261015-174940-chromium/junit.xml`. No verdict changed.
- WebKit. The 358 ids equal the ids of `docs/modules/app/qa/functional/20261015-175213-webkit/junit.xml`. No verdict changed. The one skip is the same in both.

## Failing ids

None, in Node, Chromium or WebKit.

## Skips (counted, never a pass)

- WebKit, `tests/browser/test_entry.py::test_R29_the_icon_is_amber_in_a_dark_theme_and_dark_amber_in_a_light_theme`. Reason in the run: `chromium_only: CO-1, WebKit draws the colour scheme of SVG images by its own rules`. The same test PASSES in Chromium.

## UNTESTED (6)

| qa.md line | Scenario | R# | Why UNTESTED, and where the evidence is |
|---|---|---|---|
| 331 | The live gate records its engine (2 rows) | R30 | Finder check on the live gate evidence, not run in this regression. Task 28 evidence on disk, not read here: `docs/modules/app/qa/live-e2e/20261015-183002-chromium/` and `docs/modules/app/qa/live-e2e/20261015-183102-webkit/` |
| 2426 | The headline flows on a cold start (2 rows) | R27, R30 | Live gate. No test holds it. Same live-e2e folders as line 331 |
| 2483 | The gate fails when the app starts from saved habits (control, 2 rows) | R27 | Live gate control. No test holds it. `docs/modules/app/qa/live-e2e/20261015-182937-chromium-control/` and `docs/modules/app/qa/live-e2e/20261015-183044-webkit-control/` |
| 2508 | Each screen is 1-to-1 with its golden (23 rows) | R28 | Fidelity gate, Chromium only. Not run in this regression. Task 28 captures under `docs/modules/app/qa/fidelity-*/`, verdict in `docs/modules/app/findings/fidelity.md` |
| 2540 | The gate can pass and can fail | R28 | Fidelity controls. Not run here. `docs/modules/app/qa/fidelity-controls/20261015-180740/` |
| 2573 | Every frame on the states sheet matches the live state | R28 | States check, task 28. Not run here |

## The R# table (176 live scenarios)

Line numbers are the scenario's line in `docs/modules/app/qa.md`. C is Chromium and W is WebKit. Browser test files are under `tests/browser/`. A Node row has no W column, because it is not a browser test. A parametrised scenario is held by all of its rows, shown as "n rows".

| R# | Scenario (qa.md line) | Verdict | Observed, held by |
|---|---|---|---|
| R1 | Head, CSP, icon link and relative URLs (186) | PASS | C PASS, W PASS. test_entry.py `test_R1_head_csp_icon_link_and_relative_urls` |
| R1 R29 | The app works from a sub-path (204) | PASS | C PASS, W PASS. test_entry.py `test_R1_R29_the_app_works_from_a_sub_path` |
| R1 | The static skeleton and the five dialogs (212) | PASS | C PASS, W PASS. test_entry.py `test_R1_static_skeleton_and_the_five_dialogs` |
| R2 | The stylesheet is system.css without its stand-ins (228) | PASS | C PASS, W PASS. test_entry.py `test_R2_stylesheet_is_system_css_without_its_stand_ins_with_the_listed_changes` |
| R29 | The icon file is the goldens' icon, byte for byte (241) | PASS | C PASS, W PASS. test_entry.py `test_R29_the_icon_file_is_the_goldens_icon_byte_for_byte` |
| R29 R25 | The page links the icon and the policy lets it load (248) | PASS | C PASS, W PASS. test_entry.py `test_R29_R25_the_page_links_the_icon_and_the_policy_lets_it_load` |
| R29 (CO-1) | The icon is amber in a dark theme and dark amber in a light theme (257) | PASS | C PASS. W counted SKIP with its CO-1 reason, never a pass. test_entry.py `test_R29_the_icon_is_amber_in_a_dark_theme_and_dark_amber_in_a_light_theme` |
| R26 | No sample data in the shipped files (266) | PASS | C PASS, W PASS. test_platform.py `test_R26_no_sample_data_in_the_shipped_files` |
| R26 | Query strings and fragments do not seed (3 rows, 272) | PASS | C PASS, W PASS. test_platform.py `test_R26_query_strings_and_fragments_do_not_seed` |
| R26 | No globals and no hooks (285) | PASS | C PASS, W PASS. test_platform.py `test_R26_no_globals_and_no_hooks` |
| R30 | The run uses the engine it was asked for (301) | PASS | C PASS, W PASS. test_engines.py `test_R30_the_run_uses_the_engine_it_was_asked_for` |
| R30 | An unknown engine is refused before any browser starts (307) | PASS | C PASS, W PASS. test_engines.py `test_R30_an_unknown_engine_is_refused_before_any_browser_starts` |
| R30 | One helper launches every browser (313) | PASS | C PASS, W PASS. test_engines.py `test_R30_one_helper_launches_every_browser` |
| R30 | A Chromium-only test is a counted skip with its reason in WebKit (321) | PASS | Finder check, read from this run's `-rA` output. Chromium `pytest-rA.txt` line 9 `engine chromium: 0 chromium_only skip(s)`. WebKit `pytest-rA.txt` line 9 `engine webkit: 1 chromium_only skip(s)` and line 369, the SKIPPED line with the CO-1 reason. One skip, equal to the one row of the Chromium-only table. The same test PASSES in Chromium |
| R30 | The live gate records its engine (2 rows, 331) | UNTESTED | Finder check on the live gate evidence, not run here. See the UNTESTED table |
| R30 | Every context has the clipboard stand-in (343) | PASS | C PASS, W PASS. test_engines.py `test_R30_every_context_has_the_clipboard_stand_in` |
| R3 R35 R42 | The empty first screen (354) | PASS | C PASS, W PASS. test_render.py `test_R3_R35_R42_the_empty_first_screen` |
| R4 | Brand, mark and date (369) | PASS | C PASS, W PASS. test_render.py `test_R4_brand_mark_and_date` |
| R4 | The date follows the device clock (3 rows, 377) | PASS | C PASS, W PASS. test_render.py `test_R4_the_date_follows_the_device_clock`, 3 rows |
| R4 R38 | The header on a phone and on a desktop (3 rows, 388) | PASS | C PASS, W PASS. test_render.py `test_R4_R38_the_header_on_a_phone_and_on_a_desktop`, 3 rows |
| R4 | English under a German browser locale (404) | PASS | C PASS, W PASS. test_render.py `test_R4_english_under_a_german_browser_locale` |
| R5 R6 | Rows in stored order (417) | PASS | C PASS, W PASS. test_render.py `test_R5_R6_rows_in_stored_order` |
| R6 | Current and Best for the sample (3 rows, 426) | PASS | C PASS, W PASS. test_render.py `test_R6_current_and_best_for_the_sample`, 3 rows |
| R6 R31 | Twelve habits show the goldens' numbers (438) | PASS | C PASS, W PASS. test_render.py `test_R6_R31_twelve_habits_show_the_goldens_numbers` |
| R6 R10 | A new habit shows no Best block (457) | PASS | C PASS, W PASS. test_render.py `test_R6_R10_a_new_habit_shows_no_best_block` |
| R5 R21 | The page never scrolls and the composer stays put (9 rows, 463) | PASS | C PASS, W PASS. test_render.py `test_R5_R21_the_page_never_scrolls_and_the_composer_stays_put`, 9 rows |
| R5 | The list scrolls inside its frame and shows where more lies (487) | PASS | C PASS, W PASS. test_render.py `test_R5_the_list_scrolls_inside_its_frame_and_shows_where_more_lies` |
| R5 | The fades follow the rows and a resize (498) | PASS | C PASS, W PASS. test_render.py `test_R5_the_fades_follow_the_rows_and_a_resize` |
| R35 R42 | The band on a desktop (513) | PASS | C PASS, W PASS. test_render.py `test_R35_R42_the_band_on_a_desktop` |
| R35 | The band shows from 1024 pixels (4 rows, 526) | PASS | C PASS, W PASS. test_render.py `test_R35_the_band_shows_from_1024_pixels`, 4 rows |
| R42 | arcPath reproduces the goldens' shared arcs (542) | PASS | Node PASS. ring.test.js `@R42 arcPath reproduces the goldens' shared arcs` |
| R42 | arcPath for other numbers of habits (7 rows, 548) | PASS | Node PASS. ring.test.js `@R42 arcPath(0, 2)` to `@R42 arcPath(4, 5)`, 7 tests |
| R42 | legendCounts (7 rows, 563) | PASS | Node PASS. ring.test.js `@R42 legendCounts(0)`, `(1)`, `(2)`, `(3)`, `(4)`, `(5)` and `(12)`, 7 tests |
| R42 | ring.js is pure (578) | PASS | Node PASS. ring.test.js `@R42 ring.js is pure` |
| R42 | A ring's parts and their order (585) | PASS | C PASS, W PASS. test_render.py `test_R42_a_rings_parts_and_their_order` |
| R42 | Rings for no habit and for one habit (3 rows, 592) | PASS | C PASS, W PASS. test_render.py `test_R42_rings_for_no_habit_and_for_one_habit`, 3 rows |
| R42 | Twelve habits draw twelve segments (603) | PASS | C PASS, W PASS. test_render.py `test_R42_twelve_habits_draw_twelve_segments` |
| R42 | Small rings carry no number and no today circle (609) | PASS | C PASS, W PASS. test_render.py `test_R42_small_rings_carry_no_number_and_no_today_circle` |
| R42 | Every svg part in the page and the popups is in the SVG namespace and draws (616) | PASS | C PASS, W PASS. test_render.py `test_R42_every_svg_part_in_the_page_and_the_popups_is_in_the_svg_namespace_and_draws` |
| R31 R16 | Done today presses and unpresses (3 rows, 640) | PASS | C PASS, W PASS. test_today.py `test_R31_R16_done_today_presses_and_unpresses`, 3 rows |
| R31 | Keyboard presses keep focus (656) | PASS | C PASS, W PASS. test_today.py `test_R31_keyboard_presses_keep_focus` |
| R31 R16 | Pressing twice restores the saved value (664) | PASS | C PASS, W PASS. test_today.py `test_R31_R16_pressing_twice_restores_the_saved_value` |
| R32 R16 | One Done today updates every place at once, and only what changed moves (670) | PASS | C PASS, W PASS. test_today.py `test_R32_R16_one_done_today_updates_every_place_at_once_and_only_what_changed_moves` |
| R32 R37 | A tick in P1 over P3 updates P3 and the row, and leaves today's ring alone (684) | PASS | C PASS, W PASS. test_today.py `test_R32_R37_a_tick_in_p1_over_p3_updates_p3_and_the_row_and_leaves_todays_ring_alone` |
| R32 R39 | A tick in P1 over P4 updates P4 and P3 beneath it (693) | PASS | C PASS, W PASS. test_today.py `test_R32_R39_a_tick_in_p1_over_p4_updates_p4_and_p3_beneath_it` |
| R32 R34 | A tick in P2 updates P2, the row and the band (701) | PASS | C PASS, W PASS. test_today.py `test_R32_R34_a_tick_in_p2_updates_p2_the_row_and_the_band` |
| R32 R16 | Each edit saves once, and opening or closing a popup saves nothing (709) | PASS | C PASS, W PASS. test_today.py `test_R32_R16_each_edit_saves_once_and_opening_or_closing_a_popup_saves_nothing` |
| R6 R32 | Best back to 0 removes the Best block in every place (3 rows, 725) | PASS | C PASS, W PASS. test_today.py `test_R6_R32_best_back_to_0_removes_the_best_block_in_every_place`, 3 rows |
| R32 | A tick that changes Current and leaves Best moves Current only (2 rows, 745) | PASS | C PASS, W PASS. test_today.py `test_R32_a_tick_that_changes_current_and_leaves_best_moves_current_only`, 2 rows |
| R40 | Popups stack and Esc closes the top one only (769) | PASS | C PASS, W PASS. test_popups.py `test_R40_popups_stack_and_esc_closes_the_top_one_only` |
| R40 R14 | A backdrop click closes that popup only (8 rows, 782) | PASS | C PASS, W PASS. test_popups.py `test_R40_R14_a_backdrop_click_closes_that_popup_only`, 8 rows |
| R40 R14 | A click inside the box, or a drag that leaves it, closes nothing (4 rows, 799) | PASS | C PASS, W PASS. test_popups.py `test_R40_R14_a_click_inside_the_box_or_a_drag_that_leaves_it_closes_nothing`, 4 rows |
| R40 | Tab never reaches a control outside the top popup (3 rows, 814) | PASS | C PASS, W PASS. test_popups.py `test_R40_tab_never_reaches_a_control_outside_the_top_popup`, 3 rows |
| R40 | Every popup is modal and the page does not scroll under it (5 rows, 826) | PASS | C PASS, W PASS. test_popups.py `test_R40_every_popup_is_modal_and_the_page_does_not_scroll_under_it`, 5 rows |
| R38 R42 | The Overview button opens P3 (845) | PASS | C PASS, W PASS. test_overview.py `test_R38_R42_the_overview_button_opens_p3` |
| R38 R40 | P3 closes and gives focus back to Overview (2 rows, 858) | PASS | C PASS, W PASS. test_overview.py `test_R38_R40_p3_closes_and_gives_focus_back_to_overview`, 2 rows |
| R38 R22 | P3 cannot be reached on a desktop (869) | PASS | C PASS, W PASS. test_overview.py `test_R38_R22_p3_cannot_be_reached_on_a_desktop` |
| R39 R42 | The band's Year opens P4 (875) | PASS | C PASS, W PASS. test_overview.py `test_R39_R42_the_bands_year_opens_p4` |
| R39 | P4 on a phone covers P3 (888) | PASS | C PASS, W PASS. test_overview.py `test_R39_p4_on_a_phone_covers_p3` |
| R39 R40 | P4 closes and gives focus back to the Year that opened it (5 rows, 894) | PASS | C PASS, W PASS. test_overview.py `test_R39_R40_p4_closes_and_gives_focus_back_to_the_year_that_opened_it`, 5 rows |
| R39 | P4 opens again at its top after it closed scrolled (908) | PASS | C PASS, W PASS. test_overview.py `test_R39_p4_opens_again_at_its_top_after_it_closed_scrolled` |
| R36 R42 | A band day opens P1 (931) | PASS | C PASS, W PASS. test_day_editor.py `test_R36_R42_a_band_day_opens_p1` |
| R36 R40 | P1 closes and gives focus back to its day (3 rows, 946) | PASS | C PASS, W PASS. test_day_editor.py `test_R36_R40_p1_closes_and_gives_focus_back_to_its_day`, 3 rows |
| R36 | P1 lists the habits there are when it opens (958) | PASS | C PASS, W PASS. test_day_editor.py `test_R36_p1_lists_the_habits_there_are_when_it_opens` |
| R36 | On a phone the chosen day stays in sight above P1 (6 rows, 971) | PASS | C PASS, W PASS. test_day_editor.py `test_R36_on_a_phone_the_chosen_day_stays_in_sight_above_p1`, 6 rows |
| R36 | On a phone the host of P1 gets room while P1 is open over it, and loses it when P1 closes (6 rows, 993) | PASS | C PASS (all 6 rows in the full run), W PASS. test_day_editor.py `test_R36_on_a_phone_the_host_of_p1_gets_room_while_p1_is_open_over_it_and_loses_it_when_p1_closes`, 6 rows. This row failed once in an earlier round (the `360x780 P3 2026-07-20` row). It passes here |
| R36 | With twelve habits on a phone the chosen day's top meets the host's head (2 rows, 1021) | PASS | C PASS, W PASS. test_day_editor.py `test_R36_with_twelve_habits_on_a_phone_the_chosen_days_top_meets_the_hosts_head`, 2 rows |
| R36 R39 | A P4 day opens P1 over P4 on a desktop (1038) | PASS | C PASS, W PASS. test_day_editor.py `test_R36_R39_a_p4_day_opens_p1_over_p4_on_a_desktop` |
| R36 R3 | A day opens P1 when there are no habits (1047) | PASS | C PASS, W PASS. test_day_editor.py `test_R36_R3_a_day_opens_p1_when_there_are_no_habits` |
| R37 R32 | Ticking a past day in P1 (1056) | PASS | C PASS, W PASS. test_day_editor.py `test_R37_R32_ticking_a_past_day_in_p1` |
| R37 | Keyboard ticks keep focus, and a second tick restores the saved value (1072) | PASS | C PASS, W PASS. test_day_editor.py `test_R37_keyboard_ticks_keep_focus_and_a_second_tick_restores_the_saved_value` |
| R37 R31 | Ticking today in P1 presses Done today (1080) | PASS | C PASS, W PASS. test_day_editor.py `test_R37_R31_ticking_today_in_p1_presses_done_today` |
| R33 R6 | Year opens the habit's year view (1091) | PASS | C PASS, W PASS. test_year.py `test_R33_R6_year_opens_the_habits_year_view` |
| R33 R40 | P2 closes and gives focus back to its Year (5 rows, 1108) | PASS | C PASS, W PASS. test_year.py `test_R33_R40_p2_closes_and_gives_focus_back_to_its_year`, 5 rows |
| R33 | P2 opens again at its top after it closed scrolled (1122) | PASS | C PASS, W PASS. test_year.py `test_R33_p2_opens_again_at_its_top_after_it_closed_scrolled` |
| R33 | P2 per width (2 rows, 1132) | PASS | C PASS, W PASS. test_year.py `test_R33_p2_per_width`, 2 rows |
| R34 R32 | Ticking a day in the year view (1143) | PASS | C PASS, W PASS. test_year.py `test_R34_R32_ticking_a_day_in_the_year_view` |
| R34 R16 | Untick and tick again (1158) | PASS | C PASS, W PASS. test_year.py `test_R34_R16_untick_and_tick_again` |
| R34 R10 | A day before a habit was added can be ticked (1166) | PASS | C PASS, W PASS. test_year.py `test_R34_R10_a_day_before_a_habit_was_added_can_be_ticked` |
| R34 | No control exists after today or before the year (1174) | PASS | C PASS, W PASS. test_year.py `test_R34_no_control_exists_after_today_or_before_the_year` |
| R34 R22 | Beads are reached and ticked with the keyboard (1180) | PASS | C PASS, W PASS. test_year.py `test_R34_R22_beads_are_reached_and_ticked_with_the_keyboard` |
| R10 R16 R32 | The first habit on a fresh day (1195) | PASS | C PASS, W PASS. test_add.py `test_R10_R16_R32_the_first_habit_on_a_fresh_day` |
| R10 R32 | Enter adds at the bottom, trimmed, and the band recounts (1207) | PASS | C PASS, W PASS. test_add.py `test_R10_R32_enter_adds_at_the_bottom_trimmed_and_the_band_recounts` |
| R10 | The frame scrolls to show the new row (1220) | PASS | C PASS, W PASS. test_add.py `test_R10_the_frame_scrolls_to_show_the_new_row_cg15` |
| R11 | Rejected names keep the text and show one message above the field (7 rows, 1228) | PASS | C PASS, W PASS. test_add.py `test_R11_rejected_names_keep_the_text_and_show_one_message_above_the_field`, 7 rows |
| R11 | Exactly 40 characters is accepted (1251) | PASS | C PASS, W PASS. test_add.py `test_R11_exactly_40_characters_is_accepted` |
| R11 | No message while typing (1257) | PASS | C PASS, W PASS. test_add.py `test_R11_no_message_while_typing` |
| R11 | Typing clears a message at once (1263) | PASS | C PASS, W PASS. test_add.py `test_R11_typing_clears_a_message_at_once` |
| R11 | One message at a time, replaced, then cleared on success (1271) | PASS | C PASS, W PASS. test_add.py `test_R11_one_message_at_a_time_replaced_then_cleared_on_success` |
| R12 | The twelfth habit closes the composer (1283) | PASS | C PASS, W PASS. test_add.py `test_R12_the_twelfth_habit_closes_the_composer` |
| R12 | A render at twelve habits does not write the note again (1293) | PASS | C PASS, W PASS. test_add.py `test_R12_a_render_at_twelve_habits_does_not_write_the_note_again` |
| R12 | Twelve habits at load (2 rows, 1302) | PASS | C PASS, W PASS. test_add.py `test_R12_twelve_habits_at_load`, 2 rows |
| R12 R15 | Deleting one of twelve opens the composer again (1312) | PASS | C PASS, W PASS. test_add.py `test_R12_R15_deleting_one_of_twelve_opens_the_composer_again` |
| R13 | A bin opens M1 with focus on Cancel (1321) | PASS | C PASS, W PASS. test_delete.py `test_R13_a_bin_opens_m1_with_focus_on_cancel` |
| R13 R33 | Delete habit in the year view opens M1 over it (1331) | PASS | C PASS, W PASS. test_delete.py `test_R13_R33_delete_habit_in_the_year_view_opens_m1_over_it` |
| R13 | A long name wraps in the title and the box keeps its width (1337) | PASS | C PASS, W PASS. test_delete.py `test_R13_a_long_name_wraps_in_the_title_and_the_box_keeps_its_width` |
| R13 | A slow double click on a bin that lies under Delete habit cannot delete (4 rows, 1349) | PASS | C PASS, W PASS. test_delete.py `test_R13_a_slow_double_click_on_a_bin_that_lies_under_delete_habit_cannot_delete`, 4 rows |
| R13 | A fast double click or double tap on a bin under Delete habit cannot delete (4 rows, 1365) | PASS | C PASS, W PASS. test_delete.py `test_R13_a_fast_double_click_or_double_tap_on_a_bin_under_delete_habit_cannot_delete`, 4 rows |
| R13 | A press with a click count of 2 on Delete habit, away from the bin, does nothing (1381) | PASS | C PASS, W PASS. test_delete.py `test_R13_a_press_with_a_click_count_of_2_on_delete_habit_away_from_the_bin_does_nothing` |
| R13 R15 | One press on Delete habit away from the bin deletes at once (3 rows, 1388) | PASS | C PASS, W PASS. test_delete.py `test_R13_R15_one_press_on_delete_habit_away_from_the_bin_deletes_at_once`, 3 rows |
| R13 R15 | Enter on Delete habit deletes at once (1400) | PASS | C PASS, W PASS. test_delete.py `test_R13_R15_enter_on_delete_habit_deletes_at_once` |
| R13 R15 | The keyboard deletes even when Delete habit lies over the bin (1406) | PASS | C PASS, W PASS. test_delete.py `test_R13_R15_the_keyboard_deletes_even_when_delete_habit_lies_over_the_bin` |
| R14 | Cancel, Esc and a backdrop click keep the habit and give focus back (6 rows, 1414) | PASS | C PASS, W PASS. test_delete.py `test_R14_cancel_esc_and_a_backdrop_click_keep_the_habit_and_give_focus_back`, 6 rows |
| R14 | Esc after an earlier delete still keeps the habit (1430) | PASS | C PASS, W PASS. test_delete.py `test_R14_esc_after_an_earlier_delete_still_keeps_the_habit` |
| R14 | Cancel, Esc and a backdrop click work at the instant of opening (3 rows, 1441) | PASS | C PASS, W PASS. test_delete.py `test_R14_cancel_esc_and_a_backdrop_click_work_at_the_instant_of_opening`, 3 rows |
| R14 | Cancel still works right after a click inside the box (1453) | PASS | C PASS, W PASS. test_delete.py `test_R14_cancel_still_works_right_after_a_click_inside_the_box` |
| R14 | A double press on a backdrop does not reach the control behind it (8 rows, 1464) | PASS | C PASS, W PASS. test_delete.py `test_R14_a_double_press_on_a_backdrop_does_not_reach_the_control_behind_it`, 8 rows |
| R14 | A double press on Close does not reach the control behind it (5 rows, 1486) | PASS | C PASS, W PASS. test_delete.py `test_R14_a_double_press_on_close_does_not_reach_the_control_behind_it`, 5 rows |
| R14 R10 | A double press on the backdrop over Add does not add a typed name (2 rows, 1500) | PASS | C PASS, W PASS. test_delete.py `test_R14_R10_a_double_press_on_the_backdrop_over_add_does_not_add_a_typed_name`, 2 rows |
| R14 R15 | A double click on Delete habit deletes once and nothing behind acts (1512) | PASS | C PASS, W PASS. test_delete.py `test_R14_R15_a_double_click_on_delete_habit_deletes_once_and_nothing_behind_acts` |
| R14 | The layer behind listens again once the window has passed (2 rows, 1521) | PASS | C PASS, W PASS. test_delete.py `test_R14_the_layer_behind_listens_again_once_the_window_has_passed`, 2 rows |
| R14 | Closing with the keyboard holds nothing (3 rows, 1534) | PASS | C PASS, W PASS. test_delete.py `test_R14_closing_with_the_keyboard_holds_nothing`, rows Enter, Space, Escape |
| R14 | Clicks inside the same popup, or in a popup opened after it, are never held (1549) | PASS | C PASS, W PASS. test_delete.py `test_R14_clicks_inside_the_same_popup_or_in_a_popup_opened_after_it_are_never_held` |
| R15 R32 | Deleting from a bin moves focus to the next bin and recounts (1563) | PASS | C PASS, W PASS. test_delete.py `test_R15_R32_deleting_from_a_bin_moves_focus_to_the_next_bin_and_recounts` |
| R15 | Deleting the last row moves focus to the bin above (1575) | PASS | C PASS, W PASS. test_delete.py `test_R15_deleting_the_last_row_moves_focus_to_the_bin_above` |
| R15 R3 | Deleting the only habit shows the empty list (1582) | PASS | C PASS, W PASS. test_delete.py `test_R15_R3_deleting_the_only_habit_shows_the_empty_list` |
| R15 R33 | Deleting from the year view closes both popups and moves focus (3 rows, 1592) | PASS | C PASS, W PASS. test_delete.py `test_R15_R33_deleting_from_the_year_view_closes_both_popups_and_moves_focus`, 3 rows |
| R15 | History goes with the habit (1604) | PASS | C PASS, W PASS. test_delete.py `test_R15_history_goes_with_the_habit` |
| R15 | A focused row out of sight is scrolled into view (1612) | PASS | C PASS, W PASS. test_delete.py `test_R15_a_focused_row_out_of_sight_is_scrolled_into_view` |
| R13 | The title shows the name without bidi format characters, and its quotes stay in place (16 rows, 1621) | PASS | C PASS, W PASS. test_delete.py `test_R13_the_title_shows_the_name_without_bidi_format_characters_and_its_quotes_stay_in_place`, 16 rows |
| R13 | Every character of the stripped set is left out of the title (1647) | PASS | C PASS, W PASS. test_delete.py `test_R13_every_character_of_the_stripped_set_is_left_out_of_the_title` |
| R13 | The neighbours of the stripped ranges and other invisible characters stay in the title (1653) | PASS | C PASS, W PASS. test_delete.py `test_R13_the_neighbours_of_the_stripped_ranges_and_other_invisible_characters_stay_in_the_title` |
| R13 R15 | Only the title's copy loses the characters, and the habit named in it is the one deleted (1659) | PASS | C PASS, W PASS. test_delete.py `test_R13_R15_only_the_titles_copy_loses_the_characters_and_the_habit_named_in_it_is_the_one_deleted` |
| R16 R41 | saveHabits reports whether the write worked, and loadHabits whether the read did (1674) | PASS | Node PASS. storage.test.js, the 7 tests titled `@R16 @R41 ...` |
| R16 R32 | Changes survive a reload and a closed tab (1692) | PASS | C PASS, W PASS. test_storage.py `test_R16_R32_changes_survive_a_reload_and_a_closed_tab` |
| R16 | Loading writes nothing (1704) | PASS | C PASS, W PASS. test_storage.py `test_R16_loading_writes_nothing` |
| R17 | Unreadable saved data resets the list and shows the note (16 rows, 1711) | PASS | C PASS, W PASS. test_storage.py `test_R17_unreadable_saved_data_resets_the_list_and_shows_the_note`, 16 rows |
| R17 | Readable edge cases load without a note (5 rows, 1739) | PASS | C PASS, W PASS. test_storage.py `test_R17_readable_edge_cases_load_without_a_note`, 5 rows |
| R17 R22 | Dismiss removes the note, moves focus to the field, and the note does not come back (1753) | PASS | C PASS, W PASS. test_storage.py `test_R17_R22_dismiss_removes_the_note_moves_focus_to_the_field_and_the_note_does_not_come_back` |
| R17 | Dismiss with the field disabled moves focus to the page's first control, never to body (3 rows, 1768) | PASS | C PASS, W PASS. test_storage.py `test_R17_dismiss_with_the_field_disabled_moves_focus_to_the_pages_first_control_never_to_body`, 3 rows |
| R17 | The note sits between the top of the page and the list (2 rows, 1795) | PASS | C PASS, W PASS. test_storage.py `test_R17_the_note_sits_between_the_top_of_the_page_and_the_list`, 2 rows |
| R17 R41 | An unreadable value whose reset save fails shows the warning above the note (1805) | PASS | C PASS, W PASS. test_storage.py `test_R17_R41_an_unreadable_value_whose_reset_save_fails_shows_the_warning_above_the_note` |
| R41 | A cold boot with working storage shows no warning and writes nothing (3 rows, 1816) | PASS | C PASS, W PASS. test_storage.py `test_R41_a_cold_boot_with_working_storage_shows_no_warning_and_writes_nothing`, 3 rows |
| R41 | The first failing save shows the warning, and the change stays (1828) | PASS | C PASS, W PASS. test_storage.py `test_R41_the_first_failing_save_shows_the_warning_and_the_change_stays` |
| R41 | While saves keep failing the warning stays the same element (1837) | PASS | C PASS, W PASS. test_storage.py `test_R41_while_saves_keep_failing_the_warning_stays_the_same_element` |
| R41 | The next working save removes the warning, and storage then holds what is on screen (1846) | PASS | C PASS, W PASS. test_storage.py `test_R41_the_next_working_save_removes_the_warning_and_storage_then_holds_what_is_on_screen` |
| R41 | Storage refused at boot shows the warning in the first render and clears when storage returns (1853) | PASS | C PASS, W PASS. test_storage.py `test_R41_storage_refused_at_boot_shows_the_warning_in_the_first_render_and_clears_when_storage_returns` |
| R41 | A read that throws at boot shows the warning, and the first working save clears it (1866) | PASS | C PASS, W PASS. test_storage.py `test_R41_a_read_that_throws_at_boot_shows_the_warning_and_the_first_working_save_clears_it` |
| R41 | A real full quota shows the warning and clears when space returns (1876) | PASS | C PASS, W PASS. test_storage.py `test_R41_a_real_full_quota_shows_the_warning_and_clears_when_space_returns` |
| R41 | The app never reads the error it catches (1886) | PASS | C PASS, W PASS. test_storage.py `test_R41_the_app_never_reads_the_error_it_catches` |
| R19 R35 | The view moves to the new day within a minute while visible (1899) | PASS | C PASS, W PASS. test_rollover.py `test_R19_R35_the_view_moves_to_the_new_day_within_a_minute_while_visible` |
| R19 | A page booted ten seconds before midnight shows the new day thirty seconds after it (1912) | PASS | C PASS, W PASS. test_rollover.py `test_R19_a_page_booted_ten_seconds_before_midnight_shows_the_new_day_thirty_seconds_after_it` |
| R19 R35 R38 | The band and P3 move when a new week starts (1925) | PASS | C PASS, W PASS. test_rollover.py `test_R19_R35_R38_the_band_and_p3_move_when_a_new_week_starts` |
| R19 R33 | An open year view moves to the new year (1937) | PASS | C PASS, W PASS. test_rollover.py `test_R19_R33_an_open_year_view_moves_to_the_new_year` |
| R19 R36 | An open day editor keeps its day and shows today's numbers (1946) | PASS | C PASS, W PASS. test_rollover.py `test_R19_R36_an_open_day_editor_keeps_its_day_and_shows_todays_numbers` |
| R19 | The composer keeps its text and its focus (1954) | PASS | C PASS, W PASS. test_rollover.py `test_R19_the_composer_keeps_its_text_and_its_focus` |
| R19 | An error message survives the rollover (1960) | PASS | C PASS, W PASS. test_rollover.py `test_R19_an_error_message_survives_the_rollover` |
| R19 R22 | Focus on a Done today button stays on it (1966) | PASS | C PASS, W PASS. test_rollover.py `test_R19_R22_focus_on_a_done_today_button_stays_on_it` |
| R19 R22 | Focus on a day that stays in view stays on that day (1972) | PASS | C PASS, W PASS. test_rollover.py `test_R19_R22_focus_on_a_day_that_stays_in_view_stays_on_that_day` |
| R19 R22 | Focus whose day leaves the view goes to the top popup's first focus, or to the page's first control (4 rows, 1978) | PASS | C PASS, W PASS. test_rollover.py `test_R19_R22_focus_whose_day_leaves_the_view_goes_to_the_top_popups_first_focus_or_the_pages_first_control`, 4 rows |
| R19 R37 | P1 open on the oldest day of the year when midnight passes (1991) | PASS | C PASS, W PASS. test_rollover.py `test_R19_R37_p1_open_on_the_oldest_day_of_the_year_when_midnight_passes` |
| R20 | The view moves at once when the tab is shown again (2001) | PASS | C PASS, W PASS. test_rollover.py `test_R20_the_view_moves_at_once_when_the_tab_is_shown_again` |
| R21 | Nothing scrolls at 360 pixels (8 rows, 2015) | PASS | C PASS, W PASS. The 5 popup rows are test_platform.py `test_R21_nothing_scrolls_at_360_pixels_with_a_popup_open`. The 3 rows with no popup are test_render.py `test_R5_R21_the_page_never_scrolls_and_the_composer_stays_put[360x780-...]` |
| R21 | Sizes at 360 pixels (2031) | PASS | C PASS, W PASS. test_platform.py `test_R21_sizes_at_360_pixels` |
| R21 | Sizes at 390 pixels (2047) | PASS | C PASS, W PASS. test_platform.py `test_R21_sizes_at_390_pixels` |
| R22 | Tab order on a phone (2057) | PASS | C PASS, W PASS. test_platform.py `test_R22_tab_order_on_a_phone` |
| R22 R35 | Tab order on a desktop (2063) | PASS | C PASS, W PASS. test_platform.py `test_R22_R35_tab_order_on_a_desktop` |
| R22 R17 | Tab order with the note (2 rows, 2069) | PASS | C PASS, W PASS. test_platform.py `test_R22_R17_tab_order_with_the_note`, 2 rows |
| R22 | Focus rings on keyboard focus (13 rows, 2080) | PASS | C PASS, W PASS. test_platform.py `test_R22_focus_rings_on_keyboard_focus`, 13 rows |
| R22 | A focused bin shows its glyph in the danger colour, and a focused bead has no ring of its own (2102) | PASS | C PASS, W PASS. test_platform.py `test_R22_a_focused_bin_shows_its_glyph_in_the_danger_colour_and_a_focused_bead_has_no_ring_of_its_own` |
| R22 | A mouse click draws no ring (2110) | PASS | C PASS, W PASS. test_platform.py `test_R22_a_mouse_click_draws_no_ring` |
| R22 R40 | Every popup can be used with the keyboard alone (2117) | PASS | C PASS, W PASS. test_platform.py `test_R22_R40_every_popup_can_be_used_with_the_keyboard_alone` |
| R23 | Transitions without reduced motion (2135) | PASS | C PASS, W PASS. test_platform.py `test_R23_transitions_without_reduced_motion` |
| R23 | Popups rise and backdrops fade (5 rows, 2145) | PASS | C PASS, W PASS. test_platform.py `test_R23_popups_rise_and_backdrops_fade`, 5 rows |
| R23 R32 | A change pops what changed and bumps its number, and replays on the next change (2161) | PASS | C PASS, W PASS. test_platform.py `test_R23_R32_a_change_pops_what_changed_and_bumps_its_number_and_replays_on_the_next_change` |
| R23 | Everything appears at once under reduced motion (2186) | PASS | C PASS, W PASS. test_platform.py `test_R23_everything_appears_at_once_under_reduced_motion` |
| R24 | Markup in a name stays text everywhere (2193) | PASS | C PASS, W PASS. test_platform.py `test_R24_markup_in_a_name_stays_text_everywhere` |
| R24 | No HTML sinks in the source (2207) | PASS | C PASS, W PASS. test_platform.py `test_R24_no_html_sinks_in_the_source` |
| R25 | Every request stays on the device's own files (2212) | PASS | C PASS, W PASS. test_platform.py `test_R25_every_request_stays_on_the_devices_own_files` |
| R25 | The CSP is in force (2220) | PASS | C PASS, W PASS. test_platform.py `test_R25_the_csp_is_in_force` |
| R27 R30 | The headline flows on a cold start (2 rows, 2426) | UNTESTED | Live gate. No test holds it. See the UNTESTED table |
| R27 | The gate fails when the app starts from saved habits (control, 2 rows, 2483) | UNTESTED | Live gate control. No test holds it. See the UNTESTED table |
| R28 | Each screen is 1-to-1 with its golden (23 rows, 2508) | UNTESTED | Fidelity gate, not run in this regression. See the UNTESTED table |
| R28 | The gate can pass and can fail (2540) | UNTESTED | Fidelity controls, not run in this regression. See the UNTESTED table |
| R28 | The fidelity state scripts are right (2547) | PASS | C PASS, W PASS. test_fidelity_inputs.py, 26 test ids |
| R28 | Every frame on the states sheet matches the live state (2573) | UNTESTED | States check, task 28, not run in this regression. See the UNTESTED table |

## Notes on the table

- PASS means the held test ran green in this run. The scenario titles and their row counts were matched to the junit names by a script (the tag and the title words). The matches that were not clean were read by hand against the junit names. Row-level strength was not re-derived here. The test files are the same as in `4af5d75`.
- The 7 tests that the earlier re-check listed without a scenario each have one in `qa.md` now. They are L616 (svg namespace), L908 (P4 opens at its top), L958 (P1 lists the habits), L1122 (P2 opens at its top), L1293 (a render at twelve habits), L1912 (booted ten seconds before midnight) and the 8th row of L1464 (double press on a backdrop).
- The two tests with no scenario of their own are still present and pass in both engines: `test_R13_R28_m1_has_the_markup_of_the_golden` and `test_R17_R41_R28_the_banners_have_the_markup_of_the_golden`.
- Outline row counts were compared with the junit parameter counts by script. This run did not check every row of every Outline by hand.

## Process-rule slips (disclosed by me)

- The WebKit runner's stdout went through `cut -c1-260` for display. That is a pipe after a test runner. The runner's own files are complete, and `run-meta.txt` records exit 0.
- One read-only mapping output was saved with a shell `>` into the session scratchpad (`streaks-reg-qa/app-map.txt`, outside the project). Nothing was written into the project by it.
- Two read-only `ls` calls used `2>/dev/null`, and one read-only `python -c` call used `2>&1`. None of them wrote a file.
- Read-only pipes after `git`, `ls`, `grep` and `python -c` (`head`, `tail`, `cut`).
- Nothing under `src/`, `tests/`, `index.html`, `docs/design/`, the specs, either `qa.md` or the ledger changed. `git status` on those paths is empty. The new paths are the three run folders.

## PROCESSES

Started by me, all foreground, all exited. Each runner was bounded by a cap, and no cap was hit, so no kill was issued.

| What | PID | Why | State |
|---|---|---|---|
| `runner.py node 120` and its `node --test` child | runner not recorded, node 14340 | the Node run | STOPPED, exit 0, 0.7 s |
| `runner.py chromium 400`, with pytest 23400, Playwright's driver, headless Chromium and the conftest's two `http.server` processes | runner not recorded, pytest 23400 | the Chromium run | STOPPED, exit 0, 148.1 s. The conftest stopped its own servers (their PIDs were not recorded) |
| `runner.py webkit 480`, with pytest 20580, Playwright's driver, headless WebKit and the conftest's two `http.server` processes | runner not recorded, pytest 20580 | the WebKit run | STOPPED, exit 0, 237.6 s. The conftest stopped its own servers (their PIDs were not recorded) |
| `mapr.py` and `compare.py` (read-only, scratchpad), `python -c` checks | not recorded | the scenario map, the junit comparisons, the name checks | STOPPED |

Verified teardown. The sweep before my first run found no python, node, Playwright, WebKit or browser process, and no `http.server`. The final sweep at 18:54:29 found none either. The method was `Get-CimInstance Win32_Process` by name (python, node, chrome, chrome-headless-shell, Playwright, WebKit, pw_run, MiniBrowser) and by command line (http.server, pytest, playwright, streaks, scratchpad), plus `Get-NetTCPConnection -State Listen` on 127.0.0.1. PIDs 14340, 23400 and 20580 were re-queried by PID and are gone.

Processes of other lanes, observed and not touched:
- A Chromium chain created 18:48:41 to 18:48:47, during the last seconds of my WebKit run. It was python 9184 (parent 11276), python 21416, python 10476, node 10724, chrome-headless-shell 21432 and its children 15488, 14192 and 25476. It was gone by 18:49:06. The WebKit suite starts no Chromium and no node. A grep of `tests/browser` shows the only subprocesses are the conftest's `http.server` pair, `taskkill`, and the `--collect-only` pytest call in `test_engines.py`. I did not kill it. Its owner is not proven. The brief names `examples/split` as the other lane with its own browser jobs.
- A WebKit lane created 18:49:01 to 18:49:27, after my last runner exited. It was python 7244 (parent 23420), python 5292, `python -m http.server 22171 --bind 127.0.0.1` (PID 13256), node 14116, Playwright.exe 24732 and its WebKit processes 5496, 11884 and 24980. It was gone by the final sweep. Its owner is not proven.
