# Build record: app

> Written by: the frontend builder (senior frontend dev agent), 2026-10-09. Source of truth: `spec.md` in this folder. Test contract: `qa.md`. Version v1.0.0.

## Phase skills loaded (docs/phase-skills.md, design row)
Both rows were readable on disk and were read before any UI code: `taste-skill` (`taste-skill/1.0.0/skills/taste-skill/SKILL.md`) and `frontend-design` (`claude-plugins-official/frontend-design`). They were not invoked as slash skills (the builder has no Skill tool), so they were applied by reading.
- **What changed because of them:** nothing in the look. The goldens in `docs/design/` already applied both skills (see `docs/design/system.md`), and this module copies them 1-to-1.
- **Transferred (checked against the build):** zero em or en dashes in every file; Phosphor icons only, never hand-drawn (the three paths are copied from the goldens); label above the input, error below it, no placeholder as label; focus rings on `:focus-visible` only; press feedback and reduced motion come from the copied CSS; one radius rule and one accent (untouched); a copy self-audit (every visible string is a spec Copy row, none invented); no `window.addEventListener('scroll')`, no version labels, no decorative dots.
- **Not transferred, and why:** React, Tailwind, Motion, web fonts, image generation and dark mode (the locked stack is vanilla, zero-dependency, one light theme); hero, landing and bento rules (a one-screen tool); the "Design Read" and dial exercise (the design phase did it).

## Tasks to commits

| # | Task | Requirements | Commit |
|---|---|---|---|
| 1 | `index.html`, `src/styles.css`, `tests/browser/conftest.py`, static checks in `test_entry.py` | R1, R2 | `b6e5069` |
| 2 | `src/storage.js`, `src/view.js`, `src/app.js` boot path, `test_render.py` | R3, R4, R5, R6, R7, R9, R12, R16 | `b7b9c1e` |
| 3 | Tick in place, `test_tick.py` | R8, R16 | `dc9ccd1` |
| 4 | Add form, `test_add.py`, the R1 sub-path scenario | R10, R11, R12 | `134d5b9` |
| 5 | Delete dialog, `test_delete.py` | R13, R14, R15 | `2f8f8a6` |
| 6 | Unreadable data note, storage failures, reload persistence | R16, R17, R18 | pending |
| 7 | Rollover | R19, R20 | pending |
| 8 | Platform checks | R21 to R26 | pending |
| 9 | Fidelity state scripts | R28 | pending |
| 10 | Cold-boot live-e2e script | R27 | pending |

## How to run
From the project root. The suite needs a served app (`STREAKS_BASE_URL`, and `STREAKS_SUBPATH_URL` for the sub-path scenario). `harness/_scratch/run_browser_tests.py` (git-ignored scratch helper, not shipped) starts both servers on free loopback ports, runs `python -m pytest tests/browser -q`, stops the servers by PID and prints that the ports refuse. Unit tests: `node --test "tests/**/*.test.js"` (66, untouched).

## Handoff notes (for a fresh frontend-dev)
- `src/view.js` holds every DOM lookup and builder; `src/app.js` holds state, events and focus rules; `src/storage.js` is the codec. A task adds its view functions in its own commit, so a view function exists only when a test proves it.
- The delete flow runs in the dialog's `close` event, which the browser queues as a task. A test must wait on the result (`expect(...).to_have_count`, `to_be_focused`) and not read it straight after the click.
- `conftest.py` helpers already there: `open_app` (with `base_url`), the `app` fixture (closes contexts), `record`, `hide_tab`, `show_tab`, `stored`, `row`, `day`, `cell`, `pattern`, `streak`, `trash`, `open_delete_dialog`, `add_habit`, `type_name`, `tab_until`, `is_focused`, `center`, `short_date`, `long_date`, `add_days`, `canonical_pair`, `shot`, `plain_state`, `state_text`.
- Write files with the Write and Edit tools only. Do not use `\u` escape text in an Edit (use `chr(0x...)` in Python and `\u{...}` in JS).
