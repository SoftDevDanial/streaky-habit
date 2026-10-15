---
module: app
kind: code-review
run: regression
status: clean
counts: { blocker: 0, warning: 0, info: 3 }
---
# Code review, regression pass, app (v1.1.0)

Written by the code-review finder (read-only), 2026-10-15, for `sdlc:regression --full` at the tail of execute. HEAD `ddf43f6`. It replaces the 1.0 regression verdict of this file (2026-10-09, kept in git history). The step 5 verdict and its re-check stay in `findings/code-review.md`, untouched.

Scope is `git diff c271938 HEAD -- src index.html tests`, the delta since the code-review re-check judged `c271938` (ledger S1 rows 14 and 17). It holds
- task 27a, `dismissNote` in `src/view.js` (R17, owner ruling H-05, `4af5d75`) and its test `test_R17_dismiss_with_the_field_disabled_moves_focus_to_the_pages_first_control_never_to_body` in `tests/browser/test_storage.py`,
- the targeted pass `a61cfc0` (WR-12, the `watch_close` docstring in `tests/browser/conftest.py` and five test comments, and habit-logic's WR-04 line in its `BUILD.md`),
- one comment in `test_R22_R40_every_popup_can_be_used_with_the_keyboard_alone` (`tests/browser/test_platform.py`).

habit-logic's `src/` is unchanged since `4e860ff`, so it has no delta here and its verdict stands. The cross-module sweep of the whole codebase is a separate verdict, `docs/regression/20261015-185800/consistency.md`.

Evidence is under `docs/modules/app/qa/regression-code-review/`. Every run served a throwaway `git archive` copy of `ddf43f6` from the session scratchpad, with each mutant held in memory by the test server and never written to disk. Every browser was headless and every context had the suite's clipboard stand-in (`open_app` adds `CLIPBOARD_STANDIN`).
- `20261015-190743-chromium/` and `20261015-190820-webkit/`, the mutant runs of the new test (`run.json` first, then each `<id>-pytest.txt` and `<id>-junit.xml`).
- `20261015-191629-sweep-census/`, the read-only static checks (exports, imports, unread names, comment citations).

## Verdict

**clean. 0 BLOCKER, 0 WARNING, 3 INFO.** The task 27a change is correct, maps to R17 and its H-05 paragraph, and builds nothing the spec does not ask for. Its test is a real control in both engines. Four mutants of `dismissNote` and `firstControl` each die on the row that should catch them and on no other, and the control passes. The targeted pass changed only comments and one docstring, and they now say what the code does. The three INFO items are a function comment that names one of its two uses, a test line that can never be the one that fails, and a record that names a file that does not exist.

### The mutant runs

The test has three rows, `390x844-12` (the field disabled, the Overview button expected), `1280x800-12` (the field disabled, the band's Year expected) and `390x844-11` (the field enabled, the field expected).

| Id | Mutant | Rows red, Chromium | Rows red, WebKit | Reading |
|---|---|---|---|---|
| C0 | none, HEAD as committed | none | none | the control passes |
| M1 | `dismissNote` as before 27a, `field.focus()` always | `390x844-12`, `1280x800-12` | the same | the H-05 defect, "document.activeElement is 'body'" |
| M2 | `firstControl().focus()` always | `390x844-11` | the same | the over-broad fix, focus on "Overview, today 0 of 11 habits done" |
| M3 | the Overview button written in place of `firstControl()` | `1280x800-12` | the same | from 1024 px the CSS hides the Overview button, so focus falls to `body` |
| M4 | `firstControl` without its filter `getClientRects().length > 0` | `1280x800-12` | the same | the same fall to `body` |

M1 and M2 repeat the builder's RED of task 27a. M3 and M4 are new and show what the desktop row is for. It is the only row of the outline that guards the "first shown control" half of R17's rule, so a later thinning of the Examples table must keep it.

## BLOCKER

None. Checked for this class.
- **Reverse audit.** The one changed function, `dismissNote`, maps to R17's paragraph of 2026-10-15 (H-05), the Events and focus line for R17, and task 27a. `firstControl` is unchanged and already maps to R19 (CG-14). The test maps to the `@R17` Scenario Outline "Dismiss with the field disabled moves focus to the page's first control, never to body". Nothing maps to no R#.
- **Non-goals.** No markup, style, copy, motion, storage, timer, listener or `window` property added. `git diff c271938 HEAD --stat -- src index.html` shows `src/view.js` only.
- **Behaviour traced.** The note is removed before `firstControl()` runs, so the Dismiss button cannot pick itself. With the field disabled there are twelve habits, so a shown, enabled control always exists (the Overview button below 1024 px, the band's Year from 1024 px), and `firstControl()` cannot return `undefined` on this path. A modal popup makes the page inert, so Dismiss cannot be pressed while one is open. Both widths agree with R22's tab order, whose first stop is the same control.

## WARNING

None.

## INFO

### RG-CR-I1. `firstControl`'s comment names only one of its two uses (doc rot, low)
- **Symbol.** The doc comment of `firstControl` in `src/view.js`.
- **Failure scenario.** It says the function is "where focus goes when a new day took away the day that held it and no popup is open (CG-14)". Since task 27a, `dismissNote` also sends focus there when the field is disabled (R17, H-05). A reader who changes `firstControl` for the rollover case reads nothing that warns them the Dismiss path depends on it too. M3 and M4 show the Dismiss path does depend on it.
- **Fix direction.** Say what the function returns, not who calls it. For example, "The page's first shown control that is not disabled, in page order. The Overview button below 1024 px, the band's Year from 1024 px, where the CSS hides the Overview button." The callers' own comments (`firstFocusOfTopLayer`, `dismissNote`) already say why they use it. Comment only.

### RG-CR-I2. One line of the new test can never be the line that fails (test strength, low)
- **Symbol.** `assert page.evaluate("() => document.activeElement !== document.body")` in `test_R17_dismiss_with_the_field_disabled_moves_focus_to_the_pages_first_control_never_to_body`.
- **Failure scenario.** The line before it asserts that the target element (`#nh`, `button.ov-btn` or `section.band button.btn-all`) is `document.activeElement`. None of those is `body`, so whenever focus is on `body` the line before fails first, and its message already says so through `focused` ("document.activeElement is 'body'", as M1, M3 and M4 show). The second line adds no check. It mirrors qa.md's Then "and document.activeElement is not body", which follows from the Then before it.
- **Fix direction.** Drop the line, or keep it as the visible form of the scenario's title. Either is fine. No behaviour is at stake.

### RG-CR-I3. The task 27a record names `src/system.css`, a file that does not exist (records)
- **Symbols.** `BUILD.md` section "v1.1.0 task 27a", "Non-goals honoured" ("`index.html`, `src/system.css` and `docs/design/` untouched"). The same name is in the ledger's S1 row 23 and in `docs/progress/handoff/handoff-2026-10-15-execute-streaks-app28b.md` (`12-src-system-css-mentions.txt` in the census folder).
- **Failure scenario.** The stylesheet is `src/styles.css`. `system.css` is the golden in `docs/design/`. A claim that a file which does not exist is untouched cannot fail, so the record does not show what it means to show. Nothing is hidden by it, because `git diff c271938 HEAD -- src/styles.css` is empty.
- **Fix direction.** A dated correction that names `src/styles.css`, additive in the ledger. The orchestrator owns the ledger and the handoff. The builder's record is `BUILD.md`.

## What I checked and found right

- **`dismissNote`'s comment** follows the comment rule. It gives what, why, input and output, cites R17, R12, rule 7, CG-14 and the WebKit engine note, and cites no line number.
- **The test.** The habits are added by gesture while the note shows, the only way to reach the state (a seeded twelve would load without the note), and the docstring says so. The precondition lines (`field.is_disabled()`, the stored twelve or eleven) fail on a wrong setup, not on the property. The focus line reads once after the sync point (the note gone and the rows counted), which holds because `dismissNote` removes the note and sets focus in one click handler. The trailing checks (the field still disabled or enabled, `stored(page)` equal to S) would fail on a Dismiss that enabled the field to focus it or that saved a different text.
- **"Nothing is saved" on the disabled path.** The outline compares the saved text, so a second save of the same text would pass it. The field-enabled Dismiss test counts writes (`count_writes`, code review WR-01 (b)), and both paths run the same branch of `onPageClick` and the same `dismissNote`. A save in the disabled branch alone would have to live in `view.js`, which imports no storage (spec Files). Not a gap.
- **The targeted pass.** The `watch_close` docstring is true. The test-side listener is added after the app's `close` listener, so it runs after `onPopupClose`, and it says it does not show who moved focus. The five comments and the `test_platform.py` comment point to it and claim nothing more. habit-logic's `BUILD.md` "Final test run" now carries the dated line that its counts are 1.0's.
- **Static checks** (census folder). No unused import in any browser test file or in `src/`. No backticked name in a comment of `src/` or `tests/` that the code lacks. The new imports `focused` and `plain_state` are used.

## Not covered

The whole suite, the fidelity gate and the live gate were not run here. The QA regression finder ran the suites (`docs/modules/app/qa/regression-qa/20261015-184158-node/`, `-184210-chromium/`, `-184449-webkit/`). This review ran the new test's three rows five times in each engine, as listed above.

## PROCESSES

Every process of this review ran in the foreground of its tool call and ended before this file was written. `mutrun.py` ran twice (Chromium, then WebKit), from the session scratchpad folder `streaks-reg-cr/`, each mutant with its own in-process `127.0.0.1` test server on a free port, stopped and recorded refusing (`port_refuses_after` true for all ten in the two `run.json`). Its pytest children (Chromium PIDs 22496, 10216, 11420, 24040, 24048, WebKit PIDs 5204, 18012, 5080, 18800, 8196) exited with each run, with the Playwright drivers and headless browsers they started. The sweep's two scripts are declared in `consistency.md`. A closing sweep at 19:20 by name (python, node, pytest, chrome, headless, webkit, Playwright, bash, sh, cmd), by command line (`streaks-reg-cr`, `mutrun`, `probe_year10000`, `census_run`, `regression-code-review`), by port (the eleven ports used, each refusing) and by the loopback listeners found only the sweep's own shell.
