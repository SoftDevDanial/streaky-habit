---
module: app
kind: code-review
status: issues_found
counts: { blocker: 0, warning: 13 }
---
# Code review: app

Written by the code-review finder (read-only). Project HEAD `0590636`, branch main. Scope: `git diff 127104a..HEAD -- index.html src tests` (habit-logic files read only as the contract). Evidence: `docs/modules/app/qa/code-review/20261009-154715/` (`evidence.md` first).

**Verdict: no BLOCKER, 13 WARNING.** The shipped code is correct against the spec. I found no bug in focus handling, the dialog close path, the rollover (30 s interval and `visibilitychange`), the storage error paths or the strict decoder, and no spec-less code that is not a recorded judgment call. What is wrong is the strength of the gates: I planted 34 mutants in a throwaway copy (served from memory, the repo was never written) and ran the unchanged suite against each. 5 were killed (3 of them controls), 29 survived. 5 survivors are equivalent or an invalid control of mine, **24 are real holes in the tests**, among them one that deletes every icon from the page while 114 tests stay green. Plus the missing README, one comment the code refutes, and some small smells.

## Rulings on the QA notes

| QA note | Ruling |
|---|---|
| N1 source scans skip `styles.css` | Confirmed and proven. Not "low": the test is weaker than its scenario, which qa.md says fails the scenario. WR-07 |
| N2 "stored equals S" cannot tell "no write" from "same write" | Confirmed and proven by four mutants (keep path, rejected name, Dismiss, rollover). WR-02, high |
| N3 load-time sort and de-dupe untested | Confirmed and proven, and wider: the decoder's per-date and per-name strictness has the same hole. WR-03, high |
| N4 M02 and M11 equivalent on Chromium | Agree. I re-measured on Chromium 149: `returnValue` does persist across a reopen (the comment in `view.openDeleteDialog` is true), but Esc closes with `''`, so the reset cannot be seen here. No finding |
| N5 smaller gaps | A5 (focus after clicking Add) and the backdrop press/release pair are real, in WR-06. The cadence at 23:59:59.9 belongs to WR-04. "Rollover while the dialog is open" needs no test: rows are updated in place, so the index lookup is stable by construction |

## BLOCKER

None. Checked for BLOCKER class: every function of `app.js`, `view.js`, `storage.js` traced to an R# or to a BUILD judgment call (JC1 to JC9); none of the spec's Non-goals is built (no shortcuts, timers other than the one `setInterval`, network, `inert`, `.scrim`, migration, extra motion or icon); names reach the DOM only through `textContent` and `setAttribute`; the stylesheet differs from the golden by exactly the four edits R2 allows (my own token diff, `css_diff.py`; the style block is byte-identical in the four goldens, so the spec's "measured" holds); `index.html` matches the Contracts skeleton and head order; the Copy table matches every string; no contract drift.

## WARNING

### WR-01: Nothing in the functional suite guards the SVG namespace, the sprite or the dialog markup   (test-strength, high)
- **File:** `tests/browser/conftest.py:305-324` (`_CANONICAL_PAIR_JS`, `canonical_pair`), `tests/browser/test_render.py:248-256`, `src/view.js:36-41`.
- **Issue:** the spec warns that an `svg` made with `createElement` "does not render". Mutant V1 (both `svg` and `use` made with `createElement`) passes all 114 tests. `canon()` compares `node.localName` and attributes, never `namespaceURI`, and the R5 test only reads the `use` href. Probe: namespace `http://www.w3.org/1999/xhtml` instead of `.../2000/svg`, and the 44 x 44 trash button has **0 glyph pixels instead of 140**, so every icon disappears. The same blind spot: the DOM equality runs on `.page` only (`test_render.py:251,255`), so the sprite (`body > svg`) and `dialog.dialog` are unguarded. Three more mutants survive: H4 (`h2.dialog-title` loses its class, title 18px becomes 24px), H5 (sprite loses `position:absolute`, the whole page moves down 24px: `h1.brand` top 24px becomes 48px), H8 (Delete habit gets `btn-primary`, colour `rgb(162, 59, 50)` becomes `rgb(59, 107, 96)`). Only the fidelity pixel diff, not yet run, would catch them.
- **Fix:** (1) add `node.namespaceURI` to `canon()`. (2) A test that every `svg` and `use` in the document has namespace `http://www.w3.org/2000/svg` and that each `use` has `getBBox().width > 0` (an unknown HTML element has no `getBBox`, so a wrong-namespace `use` throws). (3) `canonical_pair` for `body > svg` (compare the i-check and i-trash symbols with today.html) and for `dialog.dialog` after opening "Delete Read 20 pages", against delete-dialog.html. Re-run V1, H4, H5, H8 from the evidence folder to see them go red.

### WR-02: N2 is not low: the "saves nothing" and "at no other time" requirements cannot fail   (test-strength, high)
- **File:** `tests/browser/test_delete.py:84,99`, `tests/browser/test_add.py:91,103`, `tests/browser/test_storage.py:127-140`, `tests/browser/test_rollover.py` (no write check), `tests/browser/conftest.py:42-43`.
- **Issue:** `sample_state()` is compact `json.dumps(..., separators=(",", ":"))`, byte-identical to what `encodeState` writes, so `stored(page) == before` stays true after a re-save. Four mutants survive: A1 (Cancel, Esc and backdrop save, R14), A2 (a rejected name saves, R11), A3 (the rollover saves, R16, QA M22), A4 (Dismiss saves, R17). Probe with a `setItem` counter: pristine 0 writes on every path, each mutant 1 write per occurrence. R16 says saves happen "at no other time" except the reset.
- **Fix:** seed the R11 and R14 tests with the same habits as indented JSON (`json.dumps({"version": 1, "habits": SAMPLE_HABITS}, indent=1)`, as `test_R16_loading_writes_nothing` already does), so any save changes the text. For Dismiss and the rollover add a write counter option to `open_app` (init script wrapping `Storage.prototype.setItem` and reporting by `console.log`, as `probe.py` does, and not a window property because of R26) and assert 0.

### WR-03: N3 ruling: load-time sort, de-duplication and strictness are untested; three more decoder holes   (test-strength, high)
- **File:** `src/storage.js:27,28,35`, `tests/browser/test_storage.py:55-72,93-123`.
- **Issue:** S1 (no sort, no de-dupe, QA M10), S2 (de-dupe only) and S3 (sort only) all survive. The scenario row "unsorted and duplicated days" reads only the streak line (`test_storage.py:115-117`), which ignores order and duplicates by design. Probe: seed `A.done = [10-08, 10-07, 10-08]` plus a habit B, tick B, read storage: pristine A is `['2026-10-07','2026-10-08']`, S1 keeps the original three. New holes: S5 (only `done[0]` is validated) accepts `["2026-10-08","2026-02-30"]` and keeps the impossible date in storage, S6 (a duplicate name is checked against the previous entry only) loads `A, B, a` as three rows. Every UNREADABLE case has a one-element `done` and adjacent duplicates. S4 (decode returns the parsed object, T2 says never) cannot be seen from a browser at all.
- **Fix:** add UNREADABLE rows `done: ["2026-10-08","2026-02-30"]` and `A, B, a`; add the tick-another-habit test above (stored `A.done` sorted and unique). `decodeState` and `encodeState` are pure and import under Node (`decode-unit.mjs`), so a `tests/storage.test.js` can also pin "the result is not the parsed object". The spec's Files table does not list a storage unit test, so the orchestrator should rule on that file first.

### WR-04: The rollover cadence is not pinned: 60 s and 85 s intervals pass every test   (test-strength, medium)
- **File:** `tests/browser/test_rollover.py:65-75,78-96,99-117`, `src/app.js:19,156`.
- **Issue:** R19 says every 30 seconds and at most 60 s after midnight. Each test boots the page so that a tick lands inside its window by phase (install 23:59:00 or 23:59:30, then 00:01:00 or 90 s later). A6-60s and A6-85s survive. Probe, page booted at about 23:59:58: 31 s after 23:59:59 pristine reads Friday, the 60 s mutant Thursday; the 85 s mutant is still Thursday 61 s later, which is 60 s after midnight, so the stated promise is broken and nothing is red. QA N5 (23:59:59 versus .9) is the same family.
- **Fix:** install at 23:59:50, `pause_at` 23:59:59 once the page is open, `run_for(900)` and expect Thursday, then `run_for(30100)` and expect Friday. A 30 s cadence flips by about 00:00:20; 45 s, 60 s and 85 s do not.

### WR-05: Heat-cell recycling at the rollover is unchecked beyond class and label   (test-strength, medium)
- **File:** `tests/browser/test_rollover.py:55-62,78-96`, `tests/browser/test_tick.py:23-28`, `src/view.js:202-216`.
- **Issue:** JC2 recycles the 84 cells, so a cell must drop every attribute of its old role. Survivors: V3 (a cell that becomes future keeps role, label and `aria-current`: after Sun to Mon, 6 future cells carry a role and two cells have `aria-current`), V4 (a cell that stops being future keeps `aria-hidden="true"`: after Thu to Fri today's cell is hidden from assistive tech until a reload), V5 (the old today cell keeps `aria-current`: two cells say "current date"). `CELL_FIELDS` and `assert_the_sample_on_friday` read class, date and label only. E6 (all cells replaced on every render instead of set in place, R8 "in place", JC2) also survives, because nothing holds a handle to a heat cell as `test_tick.py` does for the bead.
- **Fix:** in `assert_the_sample_on_friday` assert that the `[aria-current]` cells are exactly the Friday cell and that it has no `aria-hidden`; in the week-shift test assert that no `hc future` cell has `role`, `aria-label` or `aria-current`; add a handle test that a heat cell stays connected after a tick.

### WR-06: Five specified behaviours have no test, each shown by a surviving mutant   (test-strength, medium-low)
- **File and fix:**
  - **R6, best back to 0 on the in-place path** (V2, `src/view.js:108`). `test_tick.py:10-17` never returns best to 0. Probe after tick then untick of a new habit: pristine shows only `cur none`, the mutant keeps "Best 1". Add that case and assert `{"cur": "No streak yet", "cur_class": "cur none", "best": None, "children": 1}`.
  - **R11, the message stays until the next submit, across a delete** (V7, `src/view.js:271`). Duplicate error, then delete another habit: pristine keeps message and `aria-invalid`, the mutant clears both. One test.
  - **R10, no focus move after a successful add, by clicking Add** (A5, `src/app.js:118`, QA N5). `test_add.py:53-70` checks focus only after Enter, where the input already had it. Probe: pristine focus stays on the Add button, the mutant moves it to the input. After `add_habit(page, "Drink water")` assert `is_focused(add_button(page))`.
  - **R14, "pressed and released outside"** (A7, `src/app.js:85`). `test_delete.py:103-117` covers a drag from inside to the backdrop, not the reverse. Probe: press at (5, 5), release on the title: pristine stays open, the mutant closes. Add the reverse drag.
  - **BUILD JC3, `setText` writes only a changed text** (V6, `src/view.js:49-51`). A behaviour with no R# and no test, so the claim "a tick leaves unchanged streak lines alone" is unverified. Add a MutationObserver test (tick a day where only `.cur` changes, expect no record on `.best`), or drop the helper.

### WR-07: N1 ruling: the "every file under src/" scans skip every file that is not JavaScript   (test-strength, medium-low; test weaker than its scenario)
- **File:** `tests/browser/test_platform.py:28-29` (`src_text`, used at 150, 170 and 194).
- **Issue:** proven. In a throwaway copy with a `src/planted.css` holding all three sample names, `sample-history` and every banned sink, the R24 sinks test, the R26 sample-data test and the R1 and R2 tests all pass (`4 passed`). qa.md says "every file under src/" for both scenarios, and its own rule says a test weaker than its scenario fails that scenario even when green, so QA table rows 5 and 64 should not read PASS. The shipped tree is clean (grep, and the QA probe), so there is no product defect.
- **Fix:** `src_text()` reads every regular file in `SRC_DIR`. The R25 allowed set (`test_platform.py:170`) then lists `styles.css` by itself, so nothing else changes.

### WR-08: A comment the code refutes   (doc rot)
- **File:** `src/app.js:3-4`.
- **Issue:** "so none of those three knows about the others". `storage.js` imports `dates.js` and `habits.js` (`storage.js:8-9`) and `view.js` imports both (`view.js:8-9`), so both depend on habit-logic. What is true is that `storage.js` and `view.js` do not import each other.
- **Fix:** say that, or drop the clause.

### WR-09: The same derivation sits in BUILD.md and in the source comments   (doc rot, DRY across the code/docs boundary)
- **File:** `docs/modules/app/BUILD.md:46-48,50` against `src/view.js:45-48` (`setText`), `src/view.js:218-221` (cells set in place), `src/app.js:97-98` (`limit` branch), `src/app.js:23` (`pendingDelete`).
- **Issue:** judgment calls 2, 3, 4 and 6 restate the why that the comments already hold. Constitution: one home, referenced from the other, or they diverge.
- **Fix:** BUILD.md keeps the decision and points at the symbol (`view.setText`, `view.renderHeatmap`, `app.rejectName`, `pendingDelete`); the comment keeps the why.

### WR-10: No README, and the run instructions live in a git-ignored scratch file   (doc, fallback ownership, a close gate)
- **File:** repo root (`git ls-files` lists no README), `docs/modules/app/BUILD.md:35-42`, `CLAUDE.md:21`, `tests/browser/conftest.py:51-56`, `tests/browser/test_entry.py:102-103`.
- **Issue:** the constitution gives the README to the orchestrator and the reviewer is the fallback, so I raise it. STATE schedules it after the solver round, so it is open rather than stale, but it is a Definition-of-done item. BUILD.md's "How to run" depends on `harness/_scratch/run_browser_tests.py`, which `.gitignore:9` excludes, so a fresh clone cannot start the servers. `CLAUDE.md:21` gives `python -m pytest tests/browser -q`, which fails every app test without `STREAKS_BASE_URL` and skips the sub-path test (BLOCKED) without `STREAKS_SUBPATH_URL`.
- **Fix:** the orchestrator writes `README.md` from the "For the README reconcile" list of BUILD.md, citing symbols and not lines, with the serve commands, both environment variables and the two servers, the cold-boot gate command, the fidelity commands, and the storage key and format. Add the two variables to the CLAUDE.md Commands line. Re-check it against the code after the solver round.

### WR-11: Dead code   (quality)
- **File:** `src/app.js:96-105` (`rejectName`, `"limit"` branch), `src/view.js:127-128` (`syncDay`, `else` branch).
- **Issue:** (a) `addHabit` answers `"limit"` only at 12 habits, where `setAddLimit` has already disabled the input and Add, so no gesture reaches it and no test can. It is named in JC4 and a comment, so it is not a hallucination, but an untestable branch needs an owner. (b) the strip window always ends today, so only the 7th button is ever today and `else button.removeAttribute("aria-current")` can never change anything (my control mutant C3 survived as equivalent for this reason).
- **Fix:** (a) ask the orchestrator for a ruling: delete it, or keep it with the justification in one place. (b) delete the `else`, or leave a one-line note that the last button is always today.

### WR-12: Smaller source smells   (quality)
- **File and fix:**
  - **Coupling.** `src/app.js:90,92,137` hold three selectors for the view's markup, against the stated purpose of JC5 ("a selector lives in one file"). Export `dayButtonOf(node)`, `deleteButtonOf(node)` and `dismissButtonOf(node)` from `view.js`.
  - **Repetition.** `src/view.js:175,185,305` repeat `$$(".habits > .habit")`, and `src/view.js:157,312` repeat the list section selector. One `rows()` helper and one constant.
  - **Pass-through.** `src/view.js:247-249` `clearNameError` only calls `resetMessage`. Keep one name.
  - **Work on every tick.** `src/app.js:40` calls `renderHeatmap`, whose first line (`src/view.js:223`) rebuilds the month axis with `replaceChildren` although the months depend on `todayKey` only. This contradicts the docblock at `view.js:218-221` ("an unchanged cell is left alone"). Call `renderMonths` from boot and the rollover only.
  - **Wide try.** `src/storage.js:74-78` runs `decodeState` inside the `try` meant for storage access. A future throw in the decoder would read as "storage unusable" (empty, no note, no reset), and the next save would overwrite the stored data. Wrap `getItem` alone.

### WR-13: Test code duplication and one long function   (quality)
- **File:** `tests/browser/test_add.py:28` and `tests/browser/test_delete.py:38` (the same `level_classes`), `SAMPLE_NAMES` in `test_render.py:27`, `test_rollover.py:22` and `test_platform.py:23`, `tests/browser/live_e2e.py:19,94-176`.
- **Issue:** duplicated helpers will drift. `drive` is an 80 line function of nested closures, and the gate script imports a pytest `conftest` (which also reads the golden sample at import).
- **Fix:** move the shared helper and constant to `conftest.py` (qa.md names it for shared helpers); split `drive` by step.

## Notes (not findings)

- **Equivalent or invalid survivors:** C3 (my wrong control, see WR-11), E1 and E2 (QA M11 and M02, N4), E3 (checking the day while the tab is hidden is harmless), S4 (browser-equivalent, WR-03).
- **Killed, good:** C1 (interval 300 s), C2 (a hook on `window`), A8 (close on release alone), E4 (the add form's `preventDefault()` dropped, so the CSP is not the only guard), E5 (rollover rebuilds rows, loses focus).
- **Not covered by this review:** the fidelity pixel diff and the states.html specimens, the security audit, and the official R27 run (QA N6). WR-01 means a pixel regression would currently be caught by fidelity only.
- **Hygiene:** no em or en dash in any changed file, no file:line citation in any comment, no unused import in `src/`, `node --check` passes, and `node --test` is 66 of 66.
