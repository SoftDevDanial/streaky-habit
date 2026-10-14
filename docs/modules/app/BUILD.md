# Build record: app

> Written by: the frontend builder (senior frontend dev agent), 2026-10-09. Source of truth: `spec.md` in this folder. Test contract: `qa.md`. Version v1.0.0.
> Status: all 10 tasks done and committed. The finders (QA, code review, security, fidelity) and the official cold-boot gate run are not part of this build.

## Phase skills loaded (docs/phase-skills.md, design row)
Both rows were readable on disk and were read before any UI code: `taste-skill` (`taste-skill/1.0.0/skills/taste-skill/SKILL.md`) and `frontend-design` (`claude-plugins-official/frontend-design`). The builder has no Skill tool, so they were applied by reading, not invoked as slash skills.
- **What changed because of them:** nothing in the look. The goldens in `docs/design/` already applied both skills (see `docs/design/system.md`) and this module copies them 1-to-1.
- **Transferred (checked against the build):** no em or en dashes in any file; Phosphor icons only and never hand-drawn (the three paths are copied from the goldens); label above the input, message below, no placeholder as a label; focus rings on `:focus-visible` only; press feedback and reduced motion come from the copied CSS; one radius rule and one accent (untouched); a copy self-audit (every visible string is a `spec.md` Copy row, none invented); no scroll listener, no version labels, no decorative dots.
- **Not transferred, and why:** React, Tailwind, Motion, web fonts, image generation and dark mode (locked stack: vanilla, zero dependencies, one light theme); hero, landing and bento rules (a one-screen tool); the "Design Read" and dial exercise (the design phase did it).

## Tasks to commits

| # | Task | Requirements | Commit |
|---|---|---|---|
| 1 | `index.html`, `src/styles.css`, `tests/browser/conftest.py`, static checks in `test_entry.py` | R1, R2 | `b6e5069` |
| 2 | `src/storage.js`, `src/view.js`, `src/app.js` boot path, `test_render.py` | R3, R4, R5, R6, R7, R9, R12, R16 | `b7b9c1e` |
| 3 | Tick in place, `test_tick.py` | R8, R16 | `dc9ccd1` |
| 4 | Add form, `test_add.py`, the R1 sub-path scenario | R10, R11, R12 | `134d5b9` |
| 5 | Delete dialog, `test_delete.py` | R13, R14, R15 | `2f8f8a6` |
| 6 | Unreadable data note, storage failures, reload persistence, `test_storage.py` | R16, R17, R18 | `2ffe0a9` |
| 7 | Rollover, `test_rollover.py` | R19, R20 | `e835e96` |
| 8 | Platform checks, `test_platform.py` | R21 to R26 | `47b7584` |
| 9 | Fidelity state scripts and `test_fidelity_inputs.py` | R28 | `30f0f33` |
| 10 | `tests/browser/live_e2e.py` | R27 | `ed9ff9d` |

Each commit carries the code and the tests that prove it, and ticks its box in `spec.md`. Every commit was made with the credential gate clean (exit 0) and the unit suite green.

## Test counts
- Unit: `node --test "tests/**/*.test.js"` gives 66 tests, 66 pass, 0 fail (unchanged, habit-logic untouched).
- Browser: `python -m pytest tests/browser -q` gives 115 passed, 0 failed, 0 skipped (about 24 s). Per file: `test_entry.py` 5, `test_render.py` 20, `test_tick.py` 9, `test_add.py` 14, `test_delete.py` 13, `test_storage.py` 26, `test_rollover.py` 7, `test_platform.py` 19, `test_fidelity_inputs.py` 2.
- Negative controls run: a 300000 ms rollover interval fails six of the seven rollover tests; the DOM equality helper reports a difference for a different golden and for one changed attribute.

Changed 2026-10-09 (code-review solver round, ORCH): the three lines above are the counts at the build. The round added tests, so they are no longer a current claim. The counts after it and the mutants each new test kills are in `findings/code-review.md`, section "Solver (2026-10-09)".
- Builder self-checks (scratch output, git-ignored, not the gates' evidence): the plugin harness at `{sdlc}/harness/fidelity.py` (plugin 2.1.3) with `--fixed-time 2026-10-08T09:00:00`, the two state scripts and the qa.md command gave `dimensions_match` true and 0 mismatched pixels on all six captures (S1, S2 and M1 at 390 x 844 and 1280 x 800; sizes 390 x 1136 and 1280 x 837 for S1 and M1). `live_e2e.py` run against a served copy wrote to a scratch folder and passed 11 of 11 steps with 0 console errors, 0 page errors and 0 requests outside the rule. The official gate run and its evidence folder (`docs/modules/app/qa/live-e2e/<datetimestamp>/`) are left to the orchestrator.

## How to run
From the project root, with nothing outside the repository.
1. Browser tests: `python -m pytest tests/browser -q`. With no environment set, `tests/browser/conftest.py` starts its own two servers (the project root, and its parent folder for the sub-path scenario) on free `127.0.0.1` ports and stops them at the end, checking that both ports refuse connections. `STREAKS_BASE_URL` (ends with `/`) and `STREAKS_SUBPATH_URL` replace them with servers you run yourself; with the first and not the second the sub-path test skips (BLOCKED, never PASS).
2. Unit tests: `node --test "tests/**/*.test.js"`.
3. Cold-boot gate, which needs a served app: start `python -m http.server <port> --bind 127.0.0.1` from the project root, run `python tests/browser/live_e2e.py --base-url http://127.0.0.1:<port>/ --out docs/modules/app/qa/live-e2e/<datetimestamp>/`, then stop the server.
4. Fidelity: the commands in qa.md, with `--candidate-init-script tests/browser/fidelity/seed-sample.js` (S1 and M1) and `--candidate-after-load tests/browser/fidelity/open-delete-dialog.js` (M1).
To look at the screen: serve the root and open `http://127.0.0.1:<port>/` (route `/`).

Changed 2026-10-09 (code-review WR-10, ORCH): this section first needed two servers started by hand and a git-ignored helper under `harness/_scratch/`, so a fresh clone could not run the suite. The conftest now serves the app itself.

## Judgment calls (where the spec is silent or leaves room)
1. **Rows are rebuilt on add and delete and updated in place on a tick and on a new day.** Rebuilding keeps the `h<N>-name` ids and the strip's `aria-labelledby` right after a delete. In-place updates keep the focused button and let the bead transitions run (R8, R19).
2. **Heat cells are created once and set in place**, also at rollover. The why is the comment above `view.renderHeatmap`.
3. **`setText` writes a text only when it changed.** The why is the comment above `view.setText`; `test_JC3_a_tick_writes_only_the_text_that_changed` watches it.
4. **`rejectName` had a branch for `addHabit`'s `"limit"` error** that no real submit reaches (the field and Add are disabled at 12).
   Deleted 2026-10-09 (code-review WR-11, ORCH ruling on this call): an untestable branch has no owner, and tab state is per tab, so it cannot be reached. `rejectName` now takes only the three name errors; the comment above it says why `"limit"` is absent. `syncDay` lost its `else` branch the same day (WR-11): the strip window always ends today, so `aria-current` is only ever set and removing it changed nothing.
5. **`view.js` owns every DOM lookup**, including `containers()` for the elements `app.js` listens on and `dayButtonOf`, `deleteButtonOf` and `dismissButtonOf` for what a click landed on, so a selector lives in one file. Changed 2026-10-09 (code-review WR-12, ORCH): `app.js` used to call `closest(...)` with three selectors itself; it now holds none.
6. **The delete is decided in the dialog's `close` event** (`app.onDialogClose`), as the Contracts say. `pendingDelete` and `pressedOutside` are module-level variables in `app.js` beyond `habits` and `todayKey`; the comment above `pendingDelete` says why. Changed 2026-10-09 (security SEC-01, ORCH): `dialogOpenedAt` and `dialogPressedAt` are two more (the event times the dialog's two guards count from), with `DIALOG_GUARD_MS`, `withinGuard`, `guardDialogClick` and `swallowTapThrough`; the comment above `DIALOG_GUARD_MS` says why. `view.containers()` also returns `page`, and `view.confirmButtonOf` is new.
7. **`loadHabits().reset` drives the note; `showNote` runs after the first render**, so the empty message exists under it.
8. **Test scaffolding beyond qa.md** (each tagged to its R#): `test_R28_the_rendered_page_has_the_markup_of_the_goldens` (the S1 and S2 `.page` DOM equals the goldens attribute for attribute), `test_R2_golden_style_block_is_the_same_in_every_golden`, `test_R11_length_counts_code_points_not_utf16_units` (CG-8), `test_R19_a_habit_added_before_the_rollover_rolls_over_too`, `test_R6_a_habit_just_added_has_no_streak_and_no_best` (the add half of the R6 scenario, in `test_add.py`), `test_R22_tab_order_with_the_note` (in `test_platform.py`, with its R22 siblings). `conftest.py` changes: `open_app` has an extra optional `base_url` (for the sub-path scenario); the `app` fixture closes contexts at teardown; `shot()` saves a screenshot only when `STREAKS_EVIDENCE_DIR` is set. Changed 2026-10-09 (code-review solver round, ORCH): `conftest.py` gained `pytest_configure` (serves the app when no server is named), the `count_writes` option of `open_app` with `write_count`, `pretty_sample_state`, `heat_cells`, `level_classes`, `SAMPLE_NAMES` and an `ignore` option of `canonical_pair`; `tests/storage.test.js` is new (spec Files table); and `live_e2e.py` runs its 11 steps as the named methods of one `Scenario` class, with the `gesture` and `expected` fields of `steps.json` now holding what their names say (they were exchanged before).
9. **The 404 `__seed__` page** is used as qa.md says. No test writes app state except by seeding `localStorage` before load.
10. **The delete dialog's title is built from a reduced copy of the name.** Changed 2026-10-09 (security SEC-02 and SEC-06, ORCH): `view.openDeleteDialog` writes `Delete "`, U+2068, the name, U+2069, `"?` (SEC-02), and the name in it has `TITLE_STRIPPED` (a module constant of `view.js`, not exported) taken out first (SEC-06): the bidi embeddings, overrides and isolates (U+202A to U+202E, U+2066 to U+2069) and the paragraph separators (U+0085, U+001C to U+001E, U+2029). The isolate alone does not hold when the name can close it or leave one open; the comment above `TITLE_STRIPPED` says why. Only the title changes: the stored name, the list row (`fillRow`) and the trash button's label keep the name as typed, and `habit-logic` is untouched. The title line and `TITLE_STRIPPED` are written as `\u{...}` escapes so the file holds no invisible character (`src/view.js` is pure ASCII, checked by byte count after each edit, because the writing tool has turned escape text into the raw character in earlier rounds; it did not in this one). The tests build their characters with `chr()` for the same reason (`test_delete.py`, `conftest.py`).

## Deviations
None from the spec's Requirements or Contracts. No dependency, routing, state library or contract change. No habit-logic defect found (`src/dates.js`, `src/habits.js` and their tests are untouched).
Process notes for the orchestrator: two small file edits (a test import tidy and one `spec.md` tick) were made with a short Python write, not the Edit tool (content checked with `git diff`), and one read-only Python call used a heredoc. Nothing else was written outside the Write and Edit tools.

## FE element checklist status vs the goldens
- **S1 (`today.html`), S2 (`today-empty.html`), M1 (`delete-dialog.html`):** the rendered `.page` DOM equals the golden's, attribute for attribute (S1, S2: `test_R28_...`), the CSS is the golden block with the three R2 changes (`test_R2_...`), and the plugin harness gave 0 mismatched pixels at both viewports. The M1 dialog markup is the golden's `dialog` with the native `::backdrop` in place of `.scrim`.
- **States sheet:** the S5 note markup equals the sheet's `.note`; the just-added row equals the sheet's apart from the sheet's own `new-name` id (the app uses `h<N>-name`). The remaining ST rows hold by construction (same CSS, same classes) and were not measured here: the computed-style comparison is the fidelity finder's.

## Non-goals honoured
No reminders, accounts, sync, targets, rename or reorder, export or import, older-day editing, notes or amounts, extra stats, theme switcher. No extra motion, icon or shadow. No undo, toast or banner beyond the S3, S4 and S5 messages. No interaction on heat cells. No service worker, manifest, offline cache, migration code, cross-tab sync, URL parameters, shortcuts, analytics or network request. No seed, fixture or test hook in `index.html` or `src/`: `window` gets no property, the CSP is the spec's, and `src/` has no `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, `eval` or `new Function` (R24, tested). No `inert` and no `.scrim`.

## For the README reconcile (comments are the builder's, the README is the orchestrator's)
- `index.html`: the one entry point (head, CSP, sprite, skeleton, dialog). `src/styles.css`: the golden CSS with three marked changes.
- `src/app.js` (exports nothing): `readToday` (the only clock read), `renderHabits`, `tick`, `askToDelete`, `removeHabit`, `onDialogClose`, `onDialogPointerDown`, `onDialogClick` (backdrop click, CG-6), `guardDialogClick` and `swallowTapThrough` (the two SEC-01 guards; added 2026-10-09, security SEC-01) with `withinGuard` (the test of event time they share) and `DIALOG_GUARD_MS` (the 500 ms window), `submitName`, `rejectName`, `checkDay` (rollover every 30 s and on `visibilitychange`), `onMainColumnClick` (dismiss), `boot`.
- `src/view.js` exports: `renderHeader`, `renderMonths`, `renderList`, `syncHabit`, `syncHabits`, `habitIndexOf`, `renderHeatmap`, `showNameError`, `resetMessage`, `nameFieldValue`, `clearNameField`, `focusNameField`, `setAddLimit`, `showNote`, `removeNote`, `openDeleteDialog`, `focusDeleteButton`, `containers`, `dayButtonOf`, `deleteButtonOf`, `confirmButtonOf`, `dismissButtonOf`. Changed 2026-10-09 (security SEC-01, ORCH): `confirmButtonOf` is new (what the Delete habit guard asks about the click's target) and `containers()` also returns `page`. Changed 2026-10-09 (code-review WR-12, ORCH): `renderMonths` is new (the month axis is drawn at boot and on a new day, no longer inside `renderHeatmap` on every change), `resetMessage` replaces `clearNameError`, and the three `...Of` functions replace the selectors that were in `app.js`. Changed 2026-10-09 (security SEC-06, ORCH): `TITLE_STRIPPED` is new in `view.js` (a module constant, not an export); `openDeleteDialog` takes it out of the title's copy of the name, and that change adds no export.
- `src/storage.js` exports: `STORAGE_KEY`, `decodeState`, `encodeState`, `loadHabits`, `saveHabits` (the Storage contract of `spec.md`).
- `tests/browser/`: `conftest.py` (fixtures and helpers), nine `test_*.py` files, `live_e2e.py` (not collected by pytest), `fidelity/seed-sample.js` and `fidelity/open-delete-dialog.js` (test-side only).

## Handoff
Nothing is open. A fresh agent only needs the finders' findings to start a solver round. Gotchas for a solver: the delete result arrives in a queued `close` task (wait with `expect`); write files with the Write and Edit tools and avoid `\u` escape text in an Edit (use `chr(0x...)` in Python and `\u{...}` in JS); the harness's `--candidate-after-load` text is inserted raw into an async function body, so the script must end its comment lines with a newline.

---

## v1.1.0 task 11, the engine switch and the WebKit baseline (2026-10-14)
> Written by the frontend builder (senior frontend dev agent), 2026-10-14. Requirement R30. The commit is the one whose message starts `test(app): engine switch, 1.0 golden fixtures and the WebKit baseline (task 11, R30)` (its hash is in the builder's return and `git log`).

### Phase skills
None loaded. Task 11 writes no UI (test code, test fixtures and records only, `src/` and `index.html` unchanged), so the design row of `docs/phase-skills.md` does not apply (spec, Tasks, "Every UI task (12 and up except 14, 27 and 28)").

### What changed
- `tests/fixtures/design-v1.0.0/` (new). `today.html`, `today-empty.html`, `delete-dialog.html`, `states.html`, each the bytes of `git show v1.0.0:docs/design/<file>`, written with the Write tool. Proof with `git hash-object --no-filters` (core.autocrlf is true here) against `git rev-parse v1.0.0:docs/design/<file>`. All four equal, `40a3fdb648053a9902c4a6cc64592b73cf376c29`, `9439584b7004012a6fbe56ec0f8ede496bba2298`, `1d9fb01f28bfc0de9739ed0c33a748a76b12f7ed`, `9258f8f3d079bb7c284b2745131d3804360be3fc`, the spec's table. `docs/design/` was only read (`git status docs/design` empty).
- `tests/browser/conftest.py`. `DESIGN_V10_DIR` and `SAMPLE_V10_FILE`. `SAMPLE` (so `SAMPLE_HABITS`, `SAMPLE_LEVELS` and the state helpers, same names) reads `tests/fixtures/sample-history-v1.0.0.json`. `canonical_pair` reads `DESIGN_V10_DIR`. `DESIGN_DIR` still names `docs/design/` (no reader left at task 11). The engine switch is `ENGINES`, `LAUNCH_ARGS`, `pytest_addoption` (`--engine`, choices `chromium` and `webkit`, default `chromium`), the session fixture `engine`, `launch(playwright, engine)` (the only `.launch` call in `tests/browser/`, `ValueError` for any other engine), the session fixture `playwright` (the run's one driver), `browser` from `launch`, the `chromium_only(reason=...)` marker registered in `pytest_configure` and turned into a skip by `pytest_collection_modifyitems` (a marker without a reason stops the run), `pytest_terminal_summary` (prints the engine and the count and list of chromium_only skips), `with_engine` (makes the last part of `STREAKS_EVIDENCE_DIR` end with `-<engine>`), and `CLIPBOARD_STANDIN`, added first to every `open_app` context.
- `tests/browser/test_entry.py`. `golden_icon_paths` and `golden_style` read `DESIGN_V10_DIR`. No assertion changed.
- `tests/browser/live_e2e.py`. `--engine` (choices `ENGINES`, default the first, so the file names no engine), the browser from `conftest.launch`, `CLIPBOARD_STANDIN` first in its context, `--out` passed through `with_engine`, and `summary.json` records `engine` and `browser_version` in place of the hard-coded "Chromium ...". The 11 steps are still 1.0's (task 27 writes them again).
- `tests/browser/test_engines.py` (new). The three `@R30` scenarios of task 11, `test_R30_the_run_uses_the_engine_it_was_asked_for`, `test_R30_an_unknown_engine_is_refused_before_any_browser_starts` and `test_R30_one_helper_launches_every_browser`. Each gathers every broken property before it fails, so one RED run shows all of them.
- `docs/modules/app/qa.md`. The Engine differences table gains the measured values and one row (the `outline` shorthand), and a dated "Task 11 measurements (2026-10-14)" list (spec task 11 asks for class (b) and the probe values there).

### RED first (qa.md, "Controls are watched failing first")
`test_engines.py` was written first, then `conftest.py` held the stubs of the qa.md table (`--engine` with no choices, `engine` returning the option, `launch` launching Chromium for any engine and never raising, `LAUNCH_ARGS` `{"chromium": [], "webkit": []}`, `EVIDENCE_DIR` as in 1.0, the 1.0 browser fixture's launch line unchanged), and `live_e2e.py` was still 1.0's. One run with `--engine webkit` and `STREAKS_EVIDENCE_DIR=.../evidence` gave 3 failed, each on its property. The browser type was chromium, the folder `evidence` did not end with `-webkit`, `--engine firefox --collect-only` exited 0 with empty error output, `launch(playwright, "firefox")` raised nothing, `.launch(` sat in `conftest.py` outside `launch` and in `live_e2e.py`, `live_e2e.py` did not import `launch`, and `LAUNCH_ARGS["chromium"]` was `[]`. The capture is `docs/modules/app/qa/red-first/20261014-125102-webkit/junit.xml`. The stubs were replaced before any commit. One plumbing difference from "the 1.0 browser fixture left as it is". Its `with sync_playwright()` moved into the shared `playwright` fixture (two drivers cannot run in one thread), and its launch line stayed the 1.0 one.

### Proof (Chromium, `src/` unchanged)
1. The four blob ids above.
2. The nine 1.0 test files run by name give **179 passed, 0 failed, 0 skipped** (42.18 s), the sealed count. Capture `docs/modules/app/qa/chromium-baseline/20261014-125323-chromium/junit.xml` with the suite's screenshots.
3. `test_engines.py` gives 3 passed in Chromium and 3 passed in WebKit. The bare `python -m pytest tests/browser -q` gives 182 passed (179 + 3) in Chromium. `node --test "tests/**/*.test.js"` 99 of 99.

### WebKit baseline
Folder `docs/modules/app/qa/webkit-baseline/20261014-125500-webkit/` (`baseline.md` is the record, with `junit.xml`, `probes.json`, the suite's screenshots and `live-e2e-webkit/`).
- The nine 1.0 files give **174 passed, 5 failed, 0 skipped**, 74.17 s (77 s wall, 20-minute cap). `test_R10_the_first_habit_on_a_fresh_day` (a mouse-clicked button takes no focus in WebKit, `body`) and the four rows of `test_R22_focus_rings_on_keyboard_focus` (the computed `outline` shorthand reads `2px solid rgb(28, 37, 35)` in WebKit, the longhands are equal). All five are class (b), written into qa.md with the measurement. No class (a), no class (c), so no test is marked `chromium_only` at task 11, and no 1.0 assertion changed.
- The 1.0 live gate gives 11 of 11 steps, 0 requests outside the rule, 0 console errors, 0 page errors, pass, in WebKit 26.5 (`live-e2e-webkit/`) and in Chromium 149 (`chromium-baseline/.../live-e2e-chromium/`).
- Probes in both engines. P1 honoured by both (no Chromium-only row needed for D-b), P2 5242672 characters in 18 keys in both (10 ms and 3 ms), P3 `image/svg+xml`, two quick taps give `detail` 2 in Chromium and 1 in WebKit, `getComputedStyle(dialog, "::backdrop")` the same in both, the CSP text per engine, the `outline` serialisation, CO-1 (WebKit draws the light colour in both schemes, information only), the clipboard (127.0.0.1 is a secure context in both, the stand-in replaces `writeText`).

### Judgment calls and deviations (named, for the orchestrator)
1. **`CLIPBOARD_STANDIN` lands at task 11.** qa.md's conftest table lists it as a v1.1.0 change of `open_app` without naming a task. The constitution (Browser gates) and the build brief require a stand-in in every context that clicks, and the 1.0 suite and live gate click, so it went in before the first WebKit run. It adds no property to `window` (the 1.0 `test_R26_no_globals_and_no_hooks` stays green in both engines) and changes no assertion. Its scenario (W21) is still written at task 19.
2. **`playwright` session fixture.** Not in the qa.md table. It is plumbing. The browser fixture and `test_R30_an_unknown_engine_is_refused_before_any_browser_starts` share one driver, because a second `sync_playwright()` cannot start while the session's driver runs.
3. **How `EVIDENCE_DIR` ends with `-<engine>`.** A folder whose last part already ends with it is kept, any other gets `-<engine>` appended (`with_engine`), so two engines can never write into one folder. `live_e2e.py --out` goes through the same helper (DRY, one rule for both).
4. **`pytest_terminal_summary`** prints the chromium_only skip count and list, so "is listed and counted" is in every run's output beside `-rA` and junit.
5. **Generated folders skipped by the scan** of `test_R30_one_helper_launches_every_browser`. `__pycache__` and `.pytest_cache` are written by Python and pytest, not source. The test builds its search words from parts so it does not match itself.
6. **The spec's proof (1) says `git hash-object`.** It was run with `--no-filters`, as the spec's own reason (core.autocrlf) and the brief require.
7. **Process notes.** One `mkdir -p` made the empty WebKit evidence folder before its run (pytest's junit writer makes it too). `probes.json` is the probe script's stdout, laid out compactly with the same values and written with the Write tool. Every other write went through the Write and Edit tools or was output the tests and gates produce themselves.
8. **Not done here, on purpose.** No test is marked `chromium_only` (CO-1's marker comes with task 12's `test_entry.py`). The README and `CLAUDE.md` are the orchestrator's.

### Non-goals honoured
No change in `src/` or `index.html`, no UI, no install, nothing written under `docs/design/`, no network beyond 127.0.0.1, browsers headless, no clipboard touched (stand-in in every context that clicks).

### How to run
- Chromium (the default) `python -m pytest tests/browser -q`. WebKit `python -m pytest tests/browser -q --engine webkit`. With evidence `STREAKS_EVIDENCE_DIR=docs/modules/app/qa/functional/<datetimestamp>-<engine>/ timeout 1200 python -m pytest tests/browser -q -rA --engine <engine>`.
- Live gate, on a served app, `python tests/browser/live_e2e.py --engine <engine> --base-url http://127.0.0.1:<port>/ --out docs/modules/app/qa/live-e2e/<datetimestamp>-<engine>/`.

### For the README reconcile
- `tests/browser/conftest.py` new names are `ENGINES`, `LAUNCH_ARGS`, `launch`, `with_engine`, `CLIPBOARD_STANDIN`, `DESIGN_V10_DIR`, `SAMPLE_V10_FILE`, the fixtures `engine` and `playwright`, the hooks `pytest_addoption`, `pytest_collection_modifyitems`, `pytest_terminal_summary`, and the `chromium_only` marker. `browser` now comes from `launch`.
- `tests/browser/live_e2e.py` takes `--engine` and its `summary.json` has `engine` and `browser_version` (no `browser` key).
- `tests/browser/test_engines.py` is new. `tests/fixtures/design-v1.0.0/` holds the four 1.0 goldens until task 12 removes them.
- The test command gains `--engine webkit`.
