# UAT findings, Streaks v1.1.0, user test 2026-10-16

Keyed by case id. Written by the orchestrator. Each finding is routed by the post-review rule (LITE or FULL) only after the owner decides. Nothing here is closed until the CHANGE LEDGER names it.

| id | case | found | what | evidence | routing |
|---|---|---|---|---|---|
| P1 | UAT-07, UAT-11 | 2026-10-16, pre-run (orchestrator probe P1, not a case) | Saved habits are overwritten when storage comes back while the page is open. With storage blocked when the page opened, the page started empty with the save warning. Storage was allowed again with no reload, one Done today tick on the new habit "Water" saved, and after a reload only Water was left. The three habits saved before were gone. Measured under a test stand-in that blocks and frees `localStorage`, so it shows the app's own logic, not whether Chrome or Safari let an open page save again | `pre-run/20261016-0217/probe-P1-H08/`, `PRE-RUN.md` section "Re-run 2026-10-16" | Owner decision H-08 in the ledger's Needs the human and in handover (a). Options (1) save nothing after a failed start until a reload, recommended, (2) re-read before the first save and refuse to overwrite, (3) keep it as a README limit. Options (1) and (2) change logic, so the FULL route (a planner line, a build, the finder loop, the live gate). Version 1.1.0 or 1.2.0 is his call |

Owner verdicts on the cases are recorded in `TEST-CASES.md` and the sheet when he pastes them. A case he fails gets its row here with his words.
