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
2. **Heat cells are created once and set in place** (class, `data-date`, role, name), also at rollover. A cell whose level changes plays the golden's dot transition (system.md Motion: "Heat dot size and tone change"). The first render of a page never animates, so the fidelity captures are unaffected.
3. **`setText` writes a text only when it changed.** Replacing a live-region text node with an identical one can make screen readers repeat it, so a tick leaves unchanged streak lines alone.
4. **`rejectName` had a branch for `addHabit`'s `"limit"` error** that no real submit reaches (the field and Add are disabled at 12).
   Deleted 2026-10-09 (code-review WR-11, ORCH ruling on this call): an untestable branch has no owner, and tab state is per tab, so it cannot be reached. `rejectName` now takes only the three name errors; the comment above it says why `"limit"` is absent. `syncDay` lost its `else` branch the same day (WR-11): the strip window always ends today, so `aria-current` is only ever set and removing it changed nothing.
5. **`view.js` owns every DOM lookup**, including `containers()` for the elements `app.js` listens on and `dayButtonOf`, `deleteButtonOf` and `dismissButtonOf` for what a click landed on, so a selector lives in one file. Changed 2026-10-09 (code-review WR-12, ORCH): `app.js` used to call `closest(...)` with three selectors itself; it now holds none.
6. **The delete is decided in the dialog's `close` event**, as the Contracts say. The browser queues that event as a task, so a test reads the result with an auto-waiting `expect` and not straight after the click. `pendingDelete` (the index the open dialog asks about) and `pressedOutside` are two module-level variables in `app.js` beyond `habits` and `todayKey`; there is one dialog element, so they cannot live on a row.
7. **`loadHabits().reset` drives the note; `showNote` runs after the first render**, so the empty message exists under it.
8. **Test scaffolding beyond qa.md** (each tagged to its R#): `test_R28_the_rendered_page_has_the_markup_of_the_goldens` (the S1 and S2 `.page` DOM equals the goldens attribute for attribute), `test_R2_golden_style_block_is_the_same_in_every_golden`, `test_R11_length_counts_code_points_not_utf16_units` (CG-8), `test_R19_a_habit_added_before_the_rollover_rolls_over_too`, `test_R6_a_habit_just_added_has_no_streak_and_no_best` (the add half of the R6 scenario, in `test_add.py`), `test_R22_tab_order_with_the_note` (in `test_platform.py`, with its R22 siblings). `conftest.py` changes: `open_app` has an extra optional `base_url` (for the sub-path scenario); the `app` fixture closes contexts at teardown; `shot()` saves a screenshot only when `STREAKS_EVIDENCE_DIR` is set.
9. **The 404 `__seed__` page** is used as qa.md says. No test writes app state except by seeding `localStorage` before load.

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
- `src/app.js` (exports nothing): `readToday` (the only clock read), `renderHabits`, `tick`, `askToDelete`, `removeHabit`, `onDialogClose`, `onDialogPointerDown`, `onDialogClick` (backdrop click, CG-6), `submitName`, `rejectName`, `checkDay` (rollover every 30 s and on `visibilitychange`), `onMainColumnClick` (dismiss), `boot`.
- `src/view.js` exports: `renderHeader`, `renderMonths`, `renderList`, `syncHabit`, `syncHabits`, `habitIndexOf`, `renderHeatmap`, `showNameError`, `resetMessage`, `nameFieldValue`, `clearNameField`, `focusNameField`, `setAddLimit`, `showNote`, `removeNote`, `openDeleteDialog`, `focusDeleteButton`, `containers`, `dayButtonOf`, `deleteButtonOf`, `dismissButtonOf`. Changed 2026-10-09 (code-review WR-12, ORCH): `renderMonths` is new (the month axis is drawn at boot and on a new day, no longer inside `renderHeatmap` on every change), `resetMessage` replaces `clearNameError`, and the three `...Of` functions replace the selectors that were in `app.js`.
- `src/storage.js` exports: `STORAGE_KEY`, `decodeState`, `encodeState`, `loadHabits`, `saveHabits` (the Storage contract of `spec.md`).
- `tests/browser/`: `conftest.py` (fixtures and helpers), nine `test_*.py` files, `live_e2e.py` (not collected by pytest), `fidelity/seed-sample.js` and `fidelity/open-delete-dialog.js` (test-side only).

## Handoff
Nothing is open. A fresh agent only needs the finders' findings to start a solver round. Gotchas for a solver: the delete result arrives in a queued `close` task (wait with `expect`); write files with the Write and Edit tools and avoid `\u` escape text in an Edit (use `chr(0x...)` in Python and `\u{...}` in JS); the harness's `--candidate-after-load` text is inserted raw into an async function body, so the script must end its comment lines with a newline.
