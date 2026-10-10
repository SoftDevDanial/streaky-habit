# SEAL: Streaks v1.0.0

**Sealed:** 2026-10-10 16:40, on the owner's word: "1. Seal both apps".
**Tag:** `v1.0.0` (local, on the commit that adds this file). This folder is read-only from here on.
**Next working version:** 1.1.0 (`docs/v1.1.0/CHANGE-LEDGER.md`).

## Checks at the seal
- Staleness: the newest ledger entry is the seal row, `docs/progress/handoff/` is empty, so the ledger is current.
- Credential gate: clean over the whole tree, exit 0.
- Last green code: `src/` and `index.html` last changed at `e42eb2f` (2026-10-09 21:10). `sdlc:regression --full`
  passed on it at `825e005` (2026-10-10 12:25): cold boot 11 of 11, 99 unit and 179 browser tests, fidelity 6 of 6
  captures at 0 px and 71 of 71 element checks. The review drive (32 of 32) and UAT ran on the same code.

## What shipped (from the ledger)

| scope | title | status |
|---|---|---|
| C1 | Add a habit | SHIPPED |
| C2 | Tick the week | SHIPPED |
| C3 | Current streak | SHIPPED |
| C4 | Best streak | SHIPPED |
| C5 | 12-week heatmap | SHIPPED |
| C6 | Delete a habit | SHIPPED, with the guard limits below |
| C7 | Kept on the device | SHIPPED |

## UAT (2026-10-10, sitting 1 of 1)

| case | scope | tester | owner |
|---|---|---|---|
| UAT-01 | C1 Add a habit | BLOCKED (script), fixed before handover, then steps matched | PASS |
| UAT-02 | C2 Tick the week | PASS | PASS, with a request (edit past days) |
| UAT-03 | C3 Current streak | PASS | PASS, with a request (label Current and Best) |
| UAT-04 | C4 Best streak | PASS | PASS |
| UAT-05 | C5 12-week heatmap | PASS | PASS |
| UAT-06 | C6 Delete a habit | PASS | PASS, the half-second pauses kept |
| UAT-07 | C7 Kept on the device | PASS | PASS |

Script, verdicts in his words, and findings: `user-test-2026-10-10/`.

## Known residuals, as ruled
| residual | ruling |
|---|---|
| A slow double click (over half a second) on the bin can reach Delete habit | Fixed in 1.1.0 with a guard that does not depend on time |
| The half-second pauses in the delete box | Kept (owner, UAT-06). The 1.1.0 guard replaces the Delete habit pause |
| Habits that cannot be saved (storage blocked or full) give no message | Fixed in 1.1.0 (owner, D-01, as for Split) |
| Only Chromium was tested | Safari's engine joins the test runs in 1.1.0 (owner, D-01, as for Split) |
| Another page on the same github.io address can read the saved names | Kept (owner, D-01, as for Split) |
| Two tabs, the last save wins | Kept (owner, D-01, as for Split) |
| A name of many stacked accent marks draws over its neighbours | Kept, minor |
| With the computer's clock past the year 9999, the next load resets every habit | Kept, minor |

## Going into 1.1.0
The owner's UAT requests: edit past days, label Current and Best, the logo in the app, a livelier look from a design
round with him (five directions), the test-case layout, and a new name ("Streaky" is taken by three habit trackers,
chosen in the design round).
