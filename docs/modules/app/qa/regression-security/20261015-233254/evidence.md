# Evidence, security re-check of habit-logic task 9a (the bound on `yearMonths`)

Security finder (read-only), 2026-10-15, 23:13 to 23:44. HEAD `c00bc8c` at the start (`23cd4cf` by the end, records
only). `git diff 40848ce HEAD -- src tests index.html` is empty, so every run measured the tree of `40848ce`. Engines
Chromium 149.0.7827.55 and WebKit 26.5 (Playwright, headless), Node v24.11.1, Python 3.14.0. Every browser context
got the suite's clipboard stand-in first (`lib.Session`, `standIn: true` in every boot line). The clock was set only
with Playwright's clock API (`set_fixed_time` for one day, `install` for a midnight), never a hook in the app. The
app was served from the project root by `python -m http.server` on 127.0.0.1. The verdict is in
`docs/modules/app/findings/regression-security.md`, section "Re-check 2026-10-15, task 9a".

Instruments were run from the finder's scratch folder. Their copies here have the same text (checked with
`diff --strip-trailing-cr`).

| File | What it is |
|---|---|
| `lib.py` | The first audit's helper, one line changed, `ROOT`, as the solver did |
| `rs9a_views.py` | 19 desktop dates and 3 phone dates, each in its own browser. Boot, Done today, P2 with every open bead pressed, P4 with its first open day and P1's tick, P4 a second time. Every read has a 3 s timeout |
| `compact_views.py` | Derives the compact view captures from the raw stdout (what it keeps is in its docstring) |
| `rs9a_views_chromium.txt`, `rs9a_views_webkit.txt` | The view captures, compact, with the raw stdout's sha256 |
| `rs9a_memory.py`, `rs9a_memory.txt` | Working set of the probe's own process tree at 9999-10-15 and 10000-10-15, P2 and P4 each sampled for 12 s, then 40 opens |
| `rs9a_memory_run1_note.txt` | Run 1, an instrument fault (unrelated processes counted through a reused parent PID), kept as a record |
| `rs9a_rollover.py`, `rs9a_rollover.txt` | Nine midnights with no press, P2 or P4 open, into 10000-10-01, 10000-11-01, 10001-01-01, 10009-10-01, 10010-10-01 and the 9999-12-31 control |
| `probe_11_hang_and_probe_14.txt` | The first audit's `probe_11` group `hang` and `probe_14`, unchanged, both engines |
| `rs9a_node.mjs`, `rs9a_node.txt` | The far-key sweep to the year 275760, the valid-key differential against `a6f7e18`, the unit suite and the `@R20` bound rows |
| `processes.txt` | Every server PID and port, the closing sweep |

The control for the freeze is the first audit's folder, `../20261015-192841/` (`probe_11_chromium_hang.txt`,
`probe_11_webkit_hang.txt`, `probe_12_hang_memory.txt`, `probe_14_rollover_hang.txt`). It was not run again.
