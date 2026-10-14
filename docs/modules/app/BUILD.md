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

---

## v1.1.0 task 12, the entry point, the stylesheet and the tab icon (2026-10-14)
> Written by the frontend builder (senior frontend dev agent), 2026-10-14. Requirements R1, R2, R29. The commit is the one whose message starts `feat(app): v1.1.0 entry point, stylesheet and tab icon (task 12, R1, R2, R29)`.

### Phase skills (design row of `docs/phase-skills.md`)
Both were read on disk before any UI file was written (the builder has no Skill tool). `taste-skill` from `taste-skill/1.0.0/skills/taste-skill/SKILL.md` and `frontend-design` from the newest copy, `claude-plugins-official/frontend-design/8d392c816966/skills/frontend-design/SKILL.md` (four of the six cached copies have the same bytes).
- **What they changed.** Nothing in the look. The goldens already apply both skills (`docs/design/system.md`, "Skills loaded"), and this task copies them 1-to-1 (spec, Phase skills).
- **Transferred and checked.** No em or en dash in any file written. Phosphor icons only, four paths copied from `today.html`, no hand-drawn icon (the mark is the owner's, copied). Label above the field, no placeholder as a label (markup copied). Focus rings on `:focus-visible` only, reduced motion and press feedback, one radius scale and one accent all come from the copied CSS, untouched. Copy self-audit, every visible string in `index.html` is a row of the spec's Copy table.
- **Not transferred, and why.** React, Tailwind, Motion, web fonts, image generation and the light theme (locked stack, one dark theme by the brainstorm). Hero, landing, bento and logo-wall rules (a one-screen tool). The design read and the dials (the design phase did them).

### What changed
- `index.html` written again. The head of R1 in the spec's order with the icon credit comment, then the body skeleton of the Contracts (sprite, `div.app`, the five dialogs), every part copied from the goldens (`today.html` for the sprite, the mark, the header, the band, the frame and the composer, `overview.html`, `overview-year.html`, `year-view.html`, `day-editor.html` and `delete-dialog.html` for the dialogs, without `open`, `.scrim`, `.below-desktop` or `inert`). The parts the spec marks "filled" are left empty for the view modules. `button.ov-btn` has no `aria-label` and `time.date` no `datetime` until the view sets them (an empty `aria-label` would name nothing). `div.banners` holds no whitespace, so `.banners:empty` hides it.
- `src/styles.css` written again. `docs/design/system.css` from `:root{` to the stand-ins comment, byte for byte with its comments, and only the three R2 changes. A line diff against the golden slice shows exactly those three lines and the header comment.
- `src/icon.svg` (new). 458 bytes, the percent-decoded payload of the goldens' icon href, no newline.
- `tests/browser/test_entry.py` written again with the seven `@R1`, `@R2` and `@R29` scenarios of qa.md. `test_R1_R29_the_app_works_from_a_sub_path` carries `xfail(strict=True, reason="task 21")` (W2) and `test_R29_R25_the_page_links_the_icon_and_the_policy_lets_it_load` carries `xfail(strict=True, reason="task 15")` (W1). `test_R29_the_icon_is_amber_in_a_dark_theme_and_dark_amber_in_a_light_theme` carries `chromium_only` with the CO-1 reason. It reads one pixel from a screenshot with Pillow, which the plugin fidelity harness uses too.
- `tests/browser/conftest.py`. `SAMPLE_HABITS` (the first three) and `TWELVE` (all twelve) come from `docs/design/sample-history.json` converted from its done strings, `sample_state()` and the new `twelve_state()` write them with `encode` (the qa.md table's name, `ensure_ascii=False`, replacing `state_text`). `TODAY`, `NOON` and `PAUSE_AT` move to 2026-10-10. `open_app` uses `color_scheme="dark"` (qa.md, open_app). `type_name` types into `#nh`. Gone with their readers are `DESIGN_V10_DIR`, `SAMPLE_V10_FILE`, `SAMPLE`, `SAMPLE_LEVELS`, `SAMPLE_NAMES`, `pretty_sample_state`, `plain_state`, `row`, `day`, `cell`, `level_classes`, `heat_cells`, `is_focused`, `trash`, `open_delete_dialog`, `confirm_delete` (1.0 form), `center`, `tab_until`, `pattern`, `streak`, `long_date`, `add_days`, `canonical_pair` and `shot`.
- Removed with `git rm` as the owner ruled (ledger off-scope row 11). `test_render.py`, `test_add.py`, `test_delete.py`, `test_storage.py`, `test_rollover.py`, `test_platform.py`, `test_fidelity_inputs.py`, `test_tick.py` (each recoverable with `git checkout v1.0.0 -- tests/browser/<file>`) and `tests/fixtures/design-v1.0.0/` (recoverable with `git checkout 42b64c3 -- tests/fixtures/design-v1.0.0/`). `tests/fixtures/sample-history-v1.0.0.json` stays for habit-logic's unit tests. `live_e2e.py` and the two 1.0 fidelity scripts stay, unrun, until tasks 27 and 26.
- `spec.md` task 12 ticked.

### RED first (qa.md, "Controls are watched failing first")
`test_entry.py` and the conftest changes were written first, with the qa.md stub for task 12 (an empty `src/icon.svg`), on the 1.0 `index.html` and `styles.css`. One Chromium run with `--runxfail` gave 7 failed, each on its property (`docs/modules/app/qa/red-first/20261014-131821-chromium/junit.xml`). The head list differed at the viewport meta and had no icon link, the body children read `div.page`, the stylesheet text differed from the golden slice, the icon bytes were empty, the sub-path page had no `li.empty`, the page had no icon link, and the colour test failed because the empty icon did not load. That last one is not the colour property, so a second throwaway stub (a valid SVG with a black fill) ran the colour and bytes tests once more, and the colour test failed on its assertion, `(0, 0, 0)` in both schemes (`.../red-first/20261014-131845-chromium/junit.xml`). Both stubs were replaced by the real file before any commit.

### Proof
- Chromium, `python -m pytest tests/browser -q -rA`, **8 passed, 2 xfailed** (W1 task 15, W2 task 21), 8.6 s (`docs/modules/app/qa/functional/20261014-132138-chromium/junit.xml`).
- WebKit, the same with `--engine webkit`, **7 passed, 1 skipped (CO-1, chromium_only, counted with its reason), 2 xfailed**, 8.7 s (`.../functional/20261014-132156-webkit/junit.xml`). No WebKit failure, so nothing to class.
- With `--runxfail`, W1 fails in both engines only on the page error of the 1.0 app (`view.renderHeader` finds no `.date time`), its icon link, load and policy assertions already pass. W2 fails on `ul.rows` being empty. Both are the reasons their marks name.
- Node, `node --test "tests/**/*.test.js"`, 102 of 102 (unchanged).
- A headless look at 390 x 844 and 1280 x 800 (scratch, not evidence) shows the header, mark, Overview button, band frame and composer drawn as in `today-empty.html`, with the filled parts empty, which is what the spec expects until task 15.

### Judgment calls (named, for the orchestrator)
1. **Which conftest helpers went.** The spec says every helper that only a removed file used goes, and qa.md's conftest table names helpers the v1.1.0 suite keeps "as 1.0". Read together, a helper the table names stays (`stored`, `record`, `write_count`, `hide_tab`, `show_tab`, `let_guard_pass`, `dialog_title`, `GUARD_WINDOW_MS`), and every other helper with no reader left went. `add_habit`, `type_name` and `add_button` stay because W2 uses them, `short_date` because `live_e2e.py` imports it.
2. **`state_text` became `encode`**, the qa.md table's name and form (`ensure_ascii=False`, as `JSON.stringify` writes). Its only other reader was a removed file.
3. **`color_scheme="dark"` in `open_app` now**, the qa.md table's v1.1.0 value. The 1.0 reason for "light" (the 1.0 goldens) left with the 1.0 tests.
4. **The head comment names the tab icon too** ("drawn in one inline svg in the header and as the tab icon src/icon.svg"), so the comment covers both places the mark lives.
5. **No sprite comment.** The goldens credit the icons once in the head and once inside the sprite. The spec puts the credit in the head, so the sprite holds only the four symbols as the Contracts draw it.

### Non-goals honoured
No `.scrim`, `inert`, `<dialog open>` or `.below-desktop`. No apple-touch-icon, manifest or `data:` URL. No CSP change. No habit data in `index.html` or `src/`. No change in `src/app.js`, `src/view.js` or `src/storage.js` (task 15 and later build the rendering, task 14 the storage results).

### FE element checklist status vs the goldens
The static parts of K1, S1 and the five dialogs are in the DOM with the goldens' classes, ids, attributes and copy, checked by `test_R1_static_skeleton_and_the_five_dialogs` and by hand against each golden. Every row that depends on data (dates, rings, rows, stats, grids) waits for tasks 15 to 22. The fidelity gate is task 28.

### How to run and view
- `python -m pytest tests/browser -q` (Chromium) and `python -m pytest tests/browser -q --engine webkit`.
- Serve the root with `python -m http.server <port> --bind 127.0.0.1` and open `http://127.0.0.1:<port>/` (route `/`). Until task 15 it shows the skeleton with no data and logs one page error from the 1.0 view code.

### For the README reconcile
- `index.html` is the v1.1.0 skeleton (title "Danial's Streaky Habit", viewport with `viewport-fit=cover`, the tab icon link, the sprite with four icons, `div.app`, five dialogs). `src/styles.css` is `system.css` without its stand-ins and with three marked changes. `src/icon.svg` is the tab icon.
- The browser suite now holds `test_engines.py` and `test_entry.py` only. `conftest.py` exports `SAMPLE_HABITS`, `TWELVE`, `sample_state`, `twelve_state`, `encode`, `TODAY`, `NOON` and `PAUSE_AT` on the v1.1.0 sample.

---

## v1.1.0 task 13, ring geometry (2026-10-14)
> Written by the frontend builder (senior frontend dev agent), 2026-10-14. Requirement R42. The commit is the one whose message starts `feat(app): ring geometry, arcPath and legendCounts (task 13, R42)`.

### Phase skills
The design row loaded for task 12 (same session, same files) covers this task, which the spec counts as UI work. Nothing in it changed `ring.js`, a pure module whose output is fixed by the goldens' path data. Transferred, no em or en dash, names over comments.

### What changed
- `src/ring.js` (new). `arcPath(i, n)` draws R42's arc rule (step 360/n, gap `min(22, 0.3 x step)`, points on radius 15 round (20, 20) rounded to 2 decimals, the large-arc flag when `step - gap` is above 180). `legendCounts(n)` is the distinct values of `[0, ceil(n/3), ceil(2n/3), n]`. Nothing else is exported, no import, no page or clock access.
- `tests/ring.test.js` (new). The four Node scenarios of qa.md, 16 tests. The shared arcs `a3-0` to `a3-2` read from `today.html` and `a12-0` to `a12-11` from `today-full.html`, the seven other arcs, the seven legend rows, and the purity scan (no import statement, none of the five words, exports exactly the two names).
- `spec.md` task 13 ticked.

### RED first
The stub of habit-logic qa.md (`arcPath` returning `""` after a `new Date()`, `legendCounts` returning `[]`) gave 16 of 16 failing on their values and the purity scan failing on "Date" (`docs/modules/app/qa/red-first/20261014-132600-node/`, `junit.xml` written by the run and `red.txt`). The folder's name was chosen just before the run, which happened at 13:25. The stub was replaced before the commit.

### Proof
- Node, `node --test "tests/**/*.test.js"`, 118 of 118 (102 before, 16 new).
- Chromium 8 passed, 2 xfailed (`docs/modules/app/qa/functional/20261014-132537-chromium/junit.xml`). WebKit 7 passed, 1 skipped (CO-1), 2 xfailed (`.../functional/20261014-132549-webkit/junit.xml`). Unchanged from task 12, as expected, since no page code uses `ring.js` until task 15. No WebKit failure.

### Deviations
None. `arcPath` has no guard for `n` below 2, because the spec defines it for 2 or more and the view draws a circle for 0 and 1 (R42).

### For the README reconcile
- `src/ring.js` exports `arcPath` and `legendCounts` (pure, the Ring contract). `tests/ring.test.js` is new.

---

## v1.1.0 task 14, storage results (2026-10-14)
> Written by the frontend builder (senior frontend dev agent), 2026-10-14. Requirements R16, R41. The commit is the one whose message starts `feat(app): saveHabits and loadHabits report whether storage worked (task 14, R16, R41)`.

### Phase skills
None. The spec names task 14 as not UI work ("12 and up except 14, 27 and 28").

### What changed
- `src/storage.js`. `saveHabits(habits)` returns `true` when `setItem` returned and `false` when reading `localStorage` or `setItem` threw, and never reads what was thrown. `encodeState` runs before the guard, so only the storage access is guarded, the same rule `loadHabits` already followed. `loadHabits()` returns `{ habits, reset, saveFailed }`. A failed read gives `saveFailed: true`, absent and readable give `false`, and unreadable gives `reset: true` with `saveFailed` set from the reset save's result. The module comment no longer says a failed save is ignored (R18 is retired). `decodeState` and `encodeState` are unchanged.
- `tests/storage.test.js`. Seven `@R16 @R41` tests for the qa.md scenario "saveHabits reports whether the write worked, and loadHabits whether the read did", one per Given and Then pair, with a stand-in `localStorage` on `globalThis` that each case removes again (Node 24 has none of its own). The "not an Error" case throws an object whose `name`, `code` and `message` getters record any read, and the test asserts none happened. The sample case uses the v1.1.0 sample's first three habits through `tests/fixtures/sample.js`.
- `spec.md` task 14 ticked.
- `src/app.js` is not changed. It still reads `{ habits, reset }` and ignores the boolean, and the warning itself is task 23's.

### RED first
No stub, as qa.md says, because the 1.0 forms fail the new assertions. Run on the 1.0 `storage.js`, 7 of 7 failed on their property. `saveHabits` returned `undefined` where `true` or `false` was expected, and `loadHabits` returned no `saveFailed` (`docs/modules/app/qa/red-first/20261014-132730-node/`, `junit.xml` from the run and `red.txt`, the folder named a few seconds before the run at 13:27:25).

### Proof
- Node, `node --test "tests/**/*.test.js"`, 125 of 125 (118 before, 7 new).
- Chromium 8 passed, 2 xfailed (`docs/modules/app/qa/functional/20261014-132801-chromium/junit.xml`). WebKit 7 passed, 1 skipped (CO-1), 2 xfailed (`.../functional/20261014-132813-webkit/junit.xml`). No WebKit failure.

### Deviations
None.

### For the README reconcile
- `saveHabits` now returns a boolean and `loadHabits` returns `saveFailed` beside `habits` and `reset` (Storage contract, v1.1.0). A failed save is no longer silent at the storage level. The banner that shows it comes with task 23.

---

## v1.1.0 task 15, the boot render (2026-10-14)
> Written by the frontend builder (senior frontend dev agent), 2026-10-14. Requirements R3, R4, R5, R6, R12, R35, R42. The commit is the one whose message starts `feat(app): boot render, header, band, rows and the list frame (task 15`.

### Phase skills (design row of `docs/phase-skills.md`)
Both read on disk before any UI code (no Skill tool). `taste-skill` (`taste-skill/1.0.0/skills/taste-skill/SKILL.md`) and `frontend-design` (`claude-plugins-official/frontend-design/8d392c816966/skills/frontend-design/SKILL.md`).
- **Design read.** A one-screen daily tool for one owner, the locked v1.1.0 Streaky Habit system, copied 1-to-1 from the goldens. Nothing re-decided, no dials set (the design phase did that).
- **What they changed.** Nothing in the look. The markup is the goldens' and the CSS is task 12's copy of `system.css`.
- **Transferred and checked.** No em or en dash in any file written. Phosphor glyphs only through the sprite (`use href`), no hand-drawn icon. Every visible string is a row of the spec's Copy table (copy self-audit). Ring and bead numbers as SVG text, as the goldens do. Motion only answers an action (the `pop` and `bump` plumbing exists, and boot passes `animate` false, so nothing moves on load). Empty state composed as the golden draws it.
- **Not transferred, and why.** React, Tailwind, Motion, web fonts and image rules (locked stack). Taste-skill's ban on scroll listeners (spec R5 asks for a `scroll` handler on `div.frame`, and it only toggles two classes, no scroll-linked animation). Hero, landing and bento rules (not a landing page).

### What changed
- `src/calendar.js` (new). `element` and `svgElement` (the element factories every view module shares), `ringSvg`, `drawRing` (R42, returns whether it redrew a ring drawn before, so callers can pop it), `flagChange` (adds a class only to what changed, and restarts it when the same element changes twice), `drawLegend` (R42, redrawn only when the number of habits changes) and `drawOverview` (the band's columns or P3's rows from `heatmapCells`, laid out once per day and renamed and redrawn in place after that). Month labels come from habit-logic `monthLabels`, and P3 also labels its newest week (CG-16).
- `src/view.js` written again for K1. `renderDate`, `renderOverviewButton`, `renderBand`, `renderRows` (rows built again only when the habits change, otherwise updated in place), `renderStats` (exported for P2 at task 19), `renderComposerLimit` (R12 at load), `renderFrameFades` (R5) and `containers`. The 1.0 strip, heatmap, dialog and add-form code went with it.
- `src/app.js` written again. `readToday`, `state`, `render(animate)` and `boot` (load, date, first render with `animate` false, the frame's `scroll` handler and window `resize`). The 1.0 handlers (tick, add, delete, dismiss, rollover) went, each comes back with its task (16, 21, 22, 23, 24).
- `tests/browser/test_render.py` (new). The task 15 scenarios of qa.md, 37 tests (corrected 2026-10-14 at task 17 by the frontend builder, this line and the commit message of `b5a2d0d` said 38, a miscount. The RED run's 38 failures were 36 of `test_render.py` and W1 and W2 of `test_entry.py`). W3 (`reason="task 19"`), W4 and W5 (`"task 21"`) and W6 (`"task 18"`) carry strict xfail marks.
- `tests/browser/test_entry.py`. W1's mark removed, it passes (the page boots with no page error, the icon loads under the CSP). Its module text now names W2 only.
- `tests/browser/conftest.py`. Locators `row`, `bin_btn`, `year_btn`, `done_btn`, `band_day`, `p3_day` and `focused` (qa.md conftest table).
- `spec.md` task 15 ticked.

### RED first
The tests were written before any `src/` change and run once in Chromium with `--runxfail` on the task 14 tree, whose page renders the bare skeleton (the 1.0 `view.js` fails to link). 38 failed and 6 passed (`docs/modules/app/qa/red-first/20261014-141807-chromium/junit.xml`). Each failure was on its property, a missing `li.empty`, row, band button, date attribute or dialog, the header's `display` value, or W1's page error. The one task 15 test that passed was `test_R4_R38_the_header_on_a_phone_and_on_a_desktop[1280x800]`, whose property (the Overview button hidden and the date at the right end) is CSS that task 12 already shipped.

### Proof
- Chromium, `python -m pytest tests/browser -q -rA`, **42 passed, 5 xfailed** (W2, W3, W4, W5, W6), 34.8 s (`docs/modules/app/qa/functional/20261014-142530-chromium/junit.xml`).
- WebKit, the same with `--engine webkit`, **41 passed, 1 skipped (CO-1, counted with its reason), 5 xfailed**, 41.3 s (`.../functional/20261014-142607-webkit/junit.xml`). No WebKit failure, so nothing to class.
- With `--runxfail` each marked test fails at its named feature and passes every step before it. W3 at P2's first month title, W4 and W5 at the add (W5's resize steps pass), W6 at P3's day button, W2 at the add.
- Node, `node --test "tests/**/*.test.js"`, 137 of 137 (no change).
- A builder self-check (scratch, not the fidelity gate, no file written). K1, S1 and S3 against `today.html`, `today-empty.html` and `today-full.html` at 360 x 780, 390 x 844 and 1280 x 800 in headless Chromium, both sides at 09:00 with reduced motion, give 0 pixels differing by more than 25 in any channel in all nine pairs. Its control, `today.html` against the app with no habits at 390 x 844, gives 16815.

### Deviations and open questions (named, for the orchestrator)
1. **Q1, the composer box with twelve habits (qa.md `@R5 @R21` "The page never scrolls and the composer stays put", rows "twelve habits").** The scenario says the bounding box of `form.composer` equals its box on a fresh day. In the goldens it does not. The 12-habit note grows the composer upward (`today-full.html`, checklist S3-07 and S3-08), measured in Chromium on the goldens themselves, top 622 against 670 at 360 x 780, 686 against 734 at 390 x 844 and 686 against 714 at 1280 x 800, while the field's box is equal at every width. The build follows the golden. The test asserts the page height, the width, the field's box at every row and the composer's box at the six rows without the note. The three twelve rows do not assert the composer's box. qa.md needs the orchestrator's ruling (likely "the field's box" for those rows, as S3-08 says). Until then the QA finder will read those rows as weaker than the scenario.
2. **Q2, the Overview button's `display` (qa.md `@R4 @R38` "The header on a phone and on a desktop").** The scenario expects `inline-flex` below 1024 px. `system.css` writes `inline-flex`, but the button is a grid item of `header.top`, so the browser blockifies it, and `today.html` itself computes `flex` at 360 and 390 in Chromium and in WebKit (measured). The test asserts `flex`, with a comment. qa.md needs the orchestrator's ruling to read `flex`.
3. **Element factories in `calendar.js`.** The spec's Files table has no shared DOM helper file, and `view.js` and the future `popups.js` both draw rings, so the factories and the ring live in `calendar.js`, the lowest DOM module, and the others import from it (no cycle). No new file.
4. **Built only for this task.** No banner (R17, R41 at task 23), no Done today handler (16), no popups (17 on), no add or delete (21, 22), no rollover (24). A submit of the composer at this commit navigates and is refused by the CSP `form-action 'none'`, until task 21 adds the submit handler (W2, W4 and W5 wait on it).
5. **R12 at load is built, its test is task 21's** (`@R12` "Twelve habits at load" lives in `test_add.py`). `test_R6_R31_twelve_habits_show_the_goldens_numbers` and the S3 self-check above cover the full composer's look meanwhile.

### Non-goals honoured
No stand-ins, no `inert`, no seed or hook, `window` gets no property. No observer callback and no deferred render (the fades are set in the `scroll` and `resize` handlers and after each render). No `innerHTML` or the like in `src/`.

### How to run and view
- `python -m pytest tests/browser -q` (Chromium) and `python -m pytest tests/browser -q --engine webkit`.
- Serve the root with `python -m http.server <port> --bind 127.0.0.1` and open `http://127.0.0.1:<port>/` (route `/`). It shows K1 or S1 from the saved habits. Nothing can be pressed yet.

### For the README reconcile
- `src/calendar.js` is new (rings, legends, the overview grids, the shared element factories). `src/view.js` exports `renderDate`, `renderOverviewButton`, `renderBand`, `renderRows`, `renderStats`, `renderComposerLimit`, `renderFrameFades`, `containers`. `src/app.js` holds `readToday`, `state`, `render`, `boot`.
- The browser suite gains `test_render.py`. `conftest.py` gains `row`, `bin_btn`, `year_btn`, `done_btn`, `band_day`, `p3_day`, `focused`.

---

## v1.1.0 task 16, Done today and the every-view update (2026-10-14)
> Written by the frontend builder (senior frontend dev agent), 2026-10-14. Requirements R31, R32, R23. The commit is the one whose message starts `feat(app): Done today, one save and every view at once (task 16`.

### Phase skills
The design row loaded for task 15 (same session, same files) covers this task. Transferred, motion only answers an action and shows what changed (frontend-design, "Motion that answers a person's action"), reduced motion from the copied CSS, no new copy. No look changed.

### What changed
- `src/app.js`. `edit(habits)` (state, one `saveHabits`, then `render(true)`), the one path every edit takes, and `onPageClick`, a delegated `click` on `div.app` that ticks or unticks today with `toggleDay(habits, index, today, today)` (R31). Focus is never moved. The boolean `saveHabits` returns is not read yet, the warning is task 23's.
- `src/view.js`. `doneTodayIndexOf(target)` (a row's habit is its place in the list) and `containers()` returns `page` too. The in-place row update, `renderStats` with `bump`, the Done today `pop`, the band ring `pop` and the Overview ring `pop` were built at task 15 and run with `animate` true from here on.
- `tests/browser/test_today.py` (new). The ten scenarios of qa.md, 15 tests. W7 and the P2 rows of W12 and W13 carry `xfail(strict=True, reason="task 19")`, W8 and the P1 rows of W12 and W13 `"task 18"`, W9 `"task 20"`, W10 `"task 19"`, W11 `"task 22"`. The Done today row of W12 is green.
- `tests/browser/conftest.py`. `p4_day`, `bead`, `tick`, `confirm_delete` (the v1.1.0 form of the qa.md table, used by W11), `stats_tree` with `current_block` and `best_block`, and `row_numbers`. `stats_tree` leaves the motion class `bump` out of the tree, so a value reads the same while it rises.
- `tests/browser/test_render.py`. Its own stats reader and the twelve-row reader were replaced by the conftest ones (DRY). The R6 tests were run before and after the move, 5 passed and 1 xfailed both times.
- `spec.md` task 16 ticked.

### RED first
`test_today.py` was written first and run once with `--runxfail` on the task 15 tree, which has no Done today handler. 15 of 15 failed on their property (`docs/modules/app/qa/red-first/20261014-143109-chromium/junit.xml`). `aria-pressed` did not flip, no write was counted, and each popup scenario failed at its popup.

### Proof
- Chromium, **48 passed, 14 xfailed**, 83.5 s (`docs/modules/app/qa/functional/20261014-143742-chromium/junit.xml`).
- WebKit, **47 passed, 1 skipped (CO-1, counted with its reason), 14 xfailed**, 94.3 s (`.../functional/20261014-143909-webkit/junit.xml`). No WebKit failure. The engine difference of a mouse click (Chromium focuses the button, WebKit leaves `body`) is asserted per engine in `test_R31_R16_done_today_presses_and_unpresses`, as qa.md says.
- Node 137 of 137.
- With `--runxfail` W7 passes all of its Done today checks (one write, `bump` on Stretch's Current only, `pop` on Stretch's button only, today's band ring the only band `pop`, the Overview ring's `pop` and name) and fails only at P2's bead. Every other marked test fails at the popup it waits for.
- A builder probe (scratch, nothing written) logged `animationstart` over two presses of Done today in both engines at 1280 x 800. Each press started `pop` on the band cell's svg, `pop` on the Done today dot and `bump` on the Current value, the second press as well as the first (R23, "replays"). The Overview ring has no animation at 1280 because the button is not displayed there.

### Deviations
None. The R23 scenarios themselves are task 25's (`test_platform.py`).

### For the README reconcile
- `src/app.js` gains `edit` and `onPageClick`. `src/view.js` gains `doneTodayIndexOf`, `containers()` returns `page` and `frame`.
- The browser suite gains `test_today.py`. `conftest.py` gains `p4_day`, `bead`, `tick`, `confirm_delete`, `stats_tree`, `current_block`, `best_block`, `row_numbers`.

---

## v1.1.0 task 17, popup plumbing and P3 (2026-10-14)
> Written by the frontend builder (senior frontend dev agent), 2026-10-14. Requirements R40, R38. The commit is the one whose message starts `feat(app): popup plumbing and the overview popup P3 (task 17`.

### Phase skills
The design row loaded for task 15 covers this task. Transferred, the popup's copy and markup are the golden's (copy self-audit, no new string), motion is the copied `rise` and `fade`, focus is set where rule 1 says. No look changed.

### What changed
- `src/popups.js` (new). `dialogs()` (the five dialogs by what each shows, their selectors live here only), `closeButtonOf`, `showPopup(dialog, focusTarget)` (`showModal`, the sheet body to its top, focus on the rule 1 target), `onBackdrop(dialog, event)` (the point lies outside `div.dlg-box`, since a backdrop press is dispatched to the dialog element) and `renderOverviewPopup` (P3's weeks newest first and its legend, drawn by `calendar.drawOverview` and `drawLegend` as the band is).
- `src/app.js`. `openers` (each open popup and the control that opened it), `pressStartedOnBackdrop`, `openPopup`, `openOverview`, and the generic listeners on all five dialogs, `onPopupPointerDown`, `onPopupClick` (Close, or a press and release both on the backdrop, closes that popup only) and `onPopupClose` (every way out, Esc included, puts focus back on the opener by hand). `onPageClick` also opens P3 from the Overview button. `render` redraws P3 while it is open (R32). Esc is the native `cancel`.
- `src/view.js`. `overviewButtonOf(target)`.
- `tests/browser/test_popups.py` (new). The five `@R40` scenarios of qa.md, 21 tests. Green at task 17 are the "800x900 P3" row of the backdrop outline (W15) and the P3 row of the modal outline (W18). Every other row carries a strict xfail mark with its task, W14 `"task 20"`, the W15 rows 18, 18, 19, 20, 22, 22 and 22, the W16 rows 22, 18, 19 and 20, the W17 rows 18, 19 and 22, the W18 rows 20, 19, 18 and 22.
- `tests/browser/test_overview.py` (new). The three P3 scenarios of qa.md, 4 tests, all green. Task 20 adds P4's.
- `tests/browser/conftest.py`. The ring and grid readers moved here from `test_render.py` (`grid_children`, `legend_parts`, `ring_parts`, `golden_arcs`, `ARCS3`, `ARCS12`, the part strings and `seg`, `number`, `ring_of`), because `test_overview.py` compares P3's rings with the band's (DRY). `test_render.py` imports them. It gave 33 passed and 4 xfailed before and after the move.
- `spec.md` task 17 ticked.

### RED first
The two files were written first and run once with `--runxfail` on the task 16 tree, which opens no popup. 24 failed on their property (no dialog opened) and 1 passed (`docs/modules/app/qa/red-first/20261014-144543-chromium/junit.xml`). The one that passed is `test_R38_R22_p3_cannot_be_reached_on_a_desktop`, whose property (Tab never lands on the Overview button at 1280) is task 12's CSS, which does not display the button from 1024 px.

### Proof
- Chromium, **54 passed, 33 xfailed**, 185.7 s (`docs/modules/app/qa/functional/20261014-145825-chromium/junit.xml`). The run is slower than before because each xfail test waits up to 5 s for its missing popup.
- WebKit, **53 passed, 1 skipped (CO-1, counted with its reason), 33 xfailed**, 203.7 s (`.../functional/20261014-150134-webkit/junit.xml`). No WebKit failure.
- Node 137 of 137.
- With `--runxfail` all 33 marked tests fail, each at the popup its task lands (P1, P2, P4 or M1 not opening, or a P4 or P2 control not drawn), and none fails in a P3 step.
- Builder self-check (scratch, nothing written). P3 opened with `element.click()` against `overview.html` at 360 x 780 and 390 x 844 gives 0 differing pixels in both. Its control, `today.html` against the app with P3 open at 390 x 844, gives 73783.

### Judgment calls (named, for the orchestrator)
1. **One set of popup listeners for all five dialogs now.** Close, the backdrop and the focus return are the same rule for every popup (R40), so they are wired at boot on every dialog. Only P3 can open at this commit. Each later task adds its own opener and contents, not its own closing.
2. **The tap-through guard (R14, CG-11) is not built.** It is task 22's. No green scenario of task 17 clicks the page within 500 ms of a click in a popup.
3. **Focus on opening** is set by hand on Close, since the native first focus of `showModal` differs by engine and would land on P3's Year.

### Deviations
None.

### For the README reconcile
- `src/popups.js` is new, exporting `dialogs`, `closeButtonOf`, `showPopup`, `onBackdrop`, `renderOverviewPopup`. `src/app.js` gains `openers`, `pressStartedOnBackdrop`, `openPopup`, `openOverview`, `onPopupPointerDown`, `onPopupClick`, `onPopupClose`. `src/view.js` gains `overviewButtonOf`.
- The browser suite gains `test_popups.py` and `test_overview.py`. `conftest.py` now holds the ring and grid readers.

---

## v1.1.0 task 18, the day editor P1 (2026-10-14)
> Written by the frontend builder (senior frontend dev agent), 2026-10-14. Requirements R36, R37, R32. The commit is the one whose message starts `feat(app): the day editor P1, opening a day and ticking it (task 18`.

### Phase skills (design row of `docs/phase-skills.md`)
Both read on disk before any UI code in this session (no Skill tool). `taste-skill` (`taste-skill/1.0.0/skills/taste-skill/SKILL.md`) and `frontend-design` (`claude-plugins-official/frontend-design/8d392c816966/skills/frontend-design/SKILL.md`).
- **What they changed.** Nothing in the look. P1's markup, copy and CSS are the golden's (`day-editor.html`, `system.css`).
- **Transferred and checked.** No em or en dash in any file written. The check glyph through the sprite only (`use href="#i-check"`), no hand-drawn icon. Copy self-audit, every P1 string is a row of the spec's Copy table ("N of T habits", "Current N days", "Current 1 day", "No streak yet", "Best N", "No habits yet."). Motion only answers an action (the tick box `pop` on a tick, nothing on opening beyond the copied `sheet`, `rise` and `fade`). The empty state (CG-12) is the line `system.css` styles.
- **Not transferred, and why.** React, Tailwind, Motion, fonts and image rules (locked stack). Landing and hero rules (a tool, not a landing page).

### What changed
- `src/popups.js`. `buildDayList(habits)` (one tick per habit, or `li.day-empty` "No habits yet." for CG-12, built as P1 opens because no habit can be added or deleted while it is open), `renderDayEditor(dayKey, habits, todayKey, animate)` (the mini ring, `longDate`, "<count> of <total> habits", and each tick's `aria-pressed`, `on`, `pop` and numbers for today, in place), `dayEditorFocus()` (the first tick, else Close), `tickIndexOf(target)`, `markOpenDay(dayKey)` (`is-open` on every day button for that date, null clears) and `keepDayInSight(dayButton)` (rule 4, below 768 px). The module comment names P1.
- `src/app.js`. `state.day` (the date P1 is open for), `openDay(dayButton)`, a band day in `onPageClick` and a P3 day or a P1 tick in `onPopupClick` (after Close and the backdrop), and `onPopupClose` clears `state.day` and the marks when P1 closes. `render` redraws P1 while it is open (R32).
- `src/calendar.js`. `DAY_BUTTON` (the day cell's selector, now one home), `dayButtonOf(target)`, `dayUnit(count)` ("day" or "days", shared by the row stats and the tick stats) and `icon` (moved from `view.js`, because P1's tick draws the check glyph too).
- `src/view.js`. Imports `icon` and `dayUnit` from `calendar.js`, no other change.
- `tests/browser/test_day_editor.py` (new). The P1 scenarios of qa.md that task 18 lands, 12 tests. The scenario "A P4 day opens P1 over P4 on a desktop" and the two P4 rows of W22 are task 20's, as qa.md says.
- Marks removed (each test read against its scenario first, and every feature it uses now exists). W6 `test_R42_small_rings_carry_no_number_and_no_today_circle`, W8 `test_R32_R37_a_tick_in_p1_over_p3_...`, the P1 rows of W12 and W13, and in `test_popups.py` the W15 rows "390x844 P3 then P1" and "1280x800 P1", the W16 row "1280x800 P1", the W17 row "390x844 P3 then P1" and the W18 row "1280x800 P1". Nine marks in all.
- Marks added. Two, `BLOCKED_B1` on the rows "390x844 P3 2026-07-20" and "360x780 P3 2026-07-20" of W22, see Blocker B1.
- `docs/modules/app/qa.md`. One dated row in "Engine differences by design", the WebKit focus after a click inside a popup (see Judgment call 2).
- `spec.md` task 18 ticked.

### RED first
`test_day_editor.py` was written first and run once in Chromium on the task 17 tree, which opens no P1. 12 of 12 failed on their property, `dialog.dlg-day` never opened (`docs/modules/app/qa/red-first/20261014-151839-chromium/junit.xml`). The nine unmarked tests were recorded RED at the tasks that wrote them (15, 16, 17).

### Proof
- Chromium, **73 passed, 26 xfailed**, 148.1 s (`docs/modules/app/qa/functional/20261014-153509-chromium/junit.xml`). An earlier run of the same tree before the WebKit measurement change gave the same counts (`.../functional/20261014-152547-chromium/junit.xml`).
- WebKit, **72 passed, 1 skipped (CO-1, counted with its reason), 26 xfailed**, 168.6 s (`.../functional/20261014-153212-webkit/junit.xml`). The first WebKit run failed one test, `test_day_editor.py::test_R37_R32_ticking_a_past_day_in_p1`, on its focus line (`.../functional/20261014-152824-webkit/junit.xml`, kept). Classed (b), an engine difference, see Judgment call 2.
- The 26 xfails are the 33 of task 17 less the nine removed, plus the two B1 rows.
- Node, `node --test "tests/**/*.test.js"`, 137 of 137.
- B1 measured, the two blocked rows run with `--runxfail` fail on their property, the day's box (top 642, bottom 690 at 390x844, top 620, bottom 666 at 360x780) lies below P1's top edge (551 and 487) with P3's body at `scrollTop` 0 (`docs/modules/app/qa/day-editor-b1/20261014-153746-chromium/junit.xml`).
- Builder self-check (scratch, not the fidelity gate, nothing written). P1 opened on 22 September (from P3 below 1024 px, from the band at 1280) against `day-editor.html` in headless Chromium with reduced motion gives 0 pixels differing by more than 25 in any channel at 360 x 780, 390 x 844 and 1280 x 800. Its control, the app with nothing open against the same golden, gives 60001, 66447 and 70493.

### Blocker B1 (for the orchestrator, R36 rule 4 against the golden)
R36 says that below 768 px, when P1 opens over P3, P3's `div.sheet-body` scrolls so the chosen day lies fully between P3's head and P1's top edge, and W22's rows "2026-07-20" expect `scrollTop` above 0. In the golden layout P3 never scrolls on a phone. `.dlg-full` is 100dvh and the 12 week rows fit, so the body's `scrollHeight` equals its `clientHeight` (698 at 360 x 780, 762 at 390 x 844, measured). P1's sheet covers the bottom of the screen (its top at 487 and 551), so the lower weeks of P3, about 20 July to 16 August, lie under it and no scroll can lift them. `f2.html` has the same gap (its scroll is clamped). `keepDayInSight` is written to R36's rule and scrolls whenever the host has room (P4 at task 20 has room). The two rows carry `xfail(strict=True, reason="blocked B1, ...")`, a mark that names no later task, so the gap shows in every run. Recommended answer. Rule 4 is an owner-approved interaction rule, so give P3 the room through the design phase (for example P3's body gains bottom padding equal to P1's height while P1 is open over it), and then the two rows hold as written. The other way is to accept it as a residual, drop the two rows from W22 and add a UAT note that on a phone the lower weeks of P3 sit under P1.

### Judgment calls (named, for the orchestrator)
1. **`pop` on `div.day-mini`.** R32 says a ring whose drawn state changed carries `pop`. P1's mini ring is a ring, so its holder gets `pop` after a tick that changes it, as `span.ov-ring` does. `system.css` has no rule for `.day-mini.pop`, so nothing moves (system.md Motion is not extended). Recommended, keep it, it is the spec's letter and has no look.
2. **WebKit focus after a click inside a popup (Q3 for qa.md).** Measured with a scratch probe in both engines. After a mouse click on a tick, Chromium focuses the tick and WebKit focuses `dialog.dlg-day`, not `body`. A click on P1's title (no control) focuses the dialog in both. The app moves no focus on a tick. qa.md's scenario "Ticking a past day in P1" reads "In WebKit document.activeElement is body". The spec's engine note says a different measurement is written into qa.md with its value, so qa.md's engine table has a new dated row and the test asserts the dialog in WebKit. The scenario line needs the planner's wording. The same will hold for P2's beads (qa.md "Ticking a day in the year view", task 19).
3. **Ticks are built as P1 opens and updated in place after that.** No habit can be added or deleted while P1 is open (it is modal), so `openDay` builds the list and `render` only updates it, which keeps a ticked button the same element with its focus.
4. **P1's top edge for rule 4 is the dialog element's box**, not `div.dlg-box`, because the box is still moved by its `sheet` animation when P1 has just opened (the code comment in `keepDayInSight` says so). The scroll amount is rounded up so a fractional box never leaves a part of the day under the sheet.

### Deviations
- The two `BLOCKED_B1` marks name a blocker, not a later task (spec Tasks, "A test that waits on a later task", allows only later tasks). Named here and in the return. They go when B1 is ruled.
- qa.md edited by the builder (one engine-table row), which the spec's engine note asks for.

### Non-goals honoured
No `inert`, no `.scrim`, no `<dialog open>`. No observer callback, no deferred render (rule 4's scroll runs in the click handler after `showModal`). No tap-through guard (R14, CG-11, task 22). No rollover work (task 24). No new copy, icon, motion or shadow.

### How to run and view
- `python -m pytest tests/browser -q` (Chromium) and `python -m pytest tests/browser -q --engine webkit`.
- Serve the root with `python -m http.server <port> --bind 127.0.0.1` and open `http://127.0.0.1:<port>/`. At 1280 px a band day opens P1. Below 1024 px open Overview, then a day.

### For the README reconcile
- `src/popups.js` exports `dialogs`, `closeButtonOf`, `showPopup`, `onBackdrop`, `renderOverviewPopup`, `buildDayList`, `renderDayEditor`, `dayEditorFocus`, `tickIndexOf`, `markOpenDay`, `keepDayInSight`.
- `src/calendar.js` gains `DAY_BUTTON`, `dayButtonOf`, `dayUnit` and `icon` (moved from `view.js`).
- `src/app.js` gains `state.day` and `openDay`. `onPageClick` opens P1 from a band day, `onPopupClick` from a P3 day and ticks in P1, `onPopupClose` clears P1's day and marks.
- The browser suite gains `test_day_editor.py`. qa.md's engine table has a row for focus after a click inside a popup.
