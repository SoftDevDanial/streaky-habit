# Live gate verdict, regression 20261015-185800 (v1.1.0 full)

Role: QA finder (read-only), cold-boot live-e2e gate, 2026-10-15 23:55 to 23:56 local. Code at `40848ce`, HEAD `5566e47`, plus the orchestrator's uncommitted ledger and STATE edit. Verdict: GREEN in both engines, each with its control seen red first.

## Method
- One engine at a time, Chromium then WebKit. Each engine had its own `python -m http.server <port> --bind 127.0.0.1` from the project root (Chromium on 4761, WebKit on 4762), started by this finder, stopped by exact PID, port checked refusing afterwards.
- Per engine, the control first (`--control seeded`), then the green run against the same server (no `--control`).
- Headless only. The gate loads its own clipboard stand-in. No clock hook. The browser date was 2026-10-15 at the start and the end of all four runs (`date_unchanged` true), although the runs sat 4 to 5 minutes before local midnight.

## Control, per engine (RED on its own property)
| engine | folder | stopped at | summary |
|--------|--------|------------|---------|
| Chromium 149.0.7827.55 | `live-e2e-20261015-235513-chromium-control/` | step 01 "first visit" (1 of 21 run, 0 passed) | `control` "seeded", `pass` false, `control_red_on_its_property` true |
| WebKit 26.5 | `live-e2e-20261015-235556-webkit-control/` | step 01 "first visit" (1 of 21 run, 0 passed) | `control` "seeded", `pass` false, `control_red_on_its_property` true |

The failing property in both engines, read from the run's own output. `stored(page)` was a 10646 character saved state where null was expected. `ul.rows` held no `li.empty` "No habits yet." and 3 `li.row` where 0 were expected. The Overview button read "Overview, today 0 of 3 habits done" where "0 of 0" was expected. The 81 band day buttons read, for example, "Mon 27 Jul, 2 of 3 habits" where "0 of 0 habits" was expected. 5 files each (screenshot, console, network, steps, summary).

## Green run, per engine
| engine | folder | steps | console errors | page errors | CSP violations | requests outside the @R25 rule | clipboard marks |
|--------|--------|-------|----------------|-------------|----------------|--------------------------------|-----------------|
| Chromium 149.0.7827.55 | `live-e2e-20261015-235524-chromium/` | 21 of 21 passed | 0 | 0 | 0 | 0 of 30 | 0 |
| WebKit 26.5 | `live-e2e-20261015-235607-webkit/` | 21 of 21 passed | 0 | 0 | 0 | 0 of 30 | 0 |

- `control` is null in both green summaries, `pass` true, `first_failing_step` null, 21 screenshots plus `console.json`, `network.json`, `steps.json`, `summary.json` (25 files each).
- Requests per green run, all GET to the base URL origin with no query string or fragment, for `/` and the nine files `src/styles.css`, `app.js`, `calendar.js`, `dates.js`, `habits.js`, `popups.js`, `ring.js`, `storage.js`, `view.js`. No POST, no other origin.
- CSP method. The gate has no separate CSP listener. A violation would surface as a console message, and `console.json` holds no message in any of the four runs. A text search of the four folders for "content security", "refused to" and "csp" found nothing.
- Screenshots read by this finder: `live-e2e-20261015-235524-chromium/01-first-visit.png` (empty state, "No habits yet.", 390 wide) and `live-e2e-20261015-235607-webkit/21-year-of-all-habits-closed.png` (1280 wide band, one row "Read 20 pages", Current 2 days, Best 2, Done today pressed, focus ring on the band's Year).

## Comparison with task 28 (`docs/modules/app/qa/live-e2e/`, folders `20261015-182937-chromium-control`, `20261015-183002-chromium`, `20261015-183044-webkit-control`, `20261015-183102-webkit`)
- No difference. Green 21 of 21 then and now, in both engines. Controls 1 of 21 run, red at "first visit", in both engines, both then and now.
- The 21 step names, the `expected` text of every step, the distinct request lists (10 distinct URLs counting `/`, 30 requests green, 10 requests control) and the screenshot counts (21 green, 1 control) are equal to task 28's. Browser versions are the same (Chromium 149.0.7827.55, WebKit 26.5). Console, page error, CSP and clipboard counts were 0 then and are 0 now.
- Only the ports (4731 then, 4761 and 4762 now) and the timestamps differ.

## Not covered by this verdict
- Nothing beyond the gate's own 21 steps and its control. Functional, fidelity, code-review and security verdicts are other finders' records.
