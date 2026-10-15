# Evidence index, regression security audit of app v1.1.0 (2026-10-15)

Security finder (read-only), the v1.1.0 full regression at the tail of execute. HEAD `ddf43f6`. Engines Chromium
149.0.7827.55 and WebKit 26.5 (Playwright 1.61.0, Python 3.14.0, Node v24.11.1), headless, Windows 11, clock zone
Asia/Kuala_Lumpur. Every browser context had the clipboard stand-in of `tests/browser/conftest.py` as its first
init script. Every server was started from the project root. Nothing was written to `src/`, `tests/`, `index.html`,
`docs/design/` or the project root. Each `.txt` is the stdout of its probe, saved with the Write tool, with a header
line naming the command and its time. Verdict file `docs/modules/app/findings/regression-security.md`.

The probes `lib.py`, `probe_00` to `probe_07`, `run_04.py` and `run_07.py` are the 4e860ff audit's instruments
(`docs/modules/app/qa/security/20261015-131500/`), copied unchanged and run again against HEAD. `probe_10` to
`probe_14` are new in this run.

| File | What it shows |
|---|---|
| `probe_00_static.txt` | CSP equal to R1 and D2, head order, no inline script or handler, the banned-API scan of `src/` (no HTML sink, no selector from data, no network, no window write), icon bytes equal to the goldens (sha256 unchanged), no sample names, the publish set |
| `probe_01_names.txt` | 12 hostile names, planted and typed, through every name sink, both engines |
| `probe_02_tamper.txt` | 29 unreadable values reset with the note, 7 readable ones load clean, prototypes clean, DOM `data-key` edits refused |
| `probe_02b_surrogate_write.txt` | Loading writes nothing, compared inside the page |
| `probe_03_planted_size.txt` | T8 timings at the quota and for five years of real use, both engines |
| `probe_04_csp_network.txt` | 25 egress and code attempts reach a canary 0 times, every flow same-origin GET only, failing storage, query strings, no globals, the icon under the CSP |
| `probe_05_bidi_layout.txt` | Bidi and control characters in P1, P2, rows and M1, layout at 360 x 780 |
| `probe_06_close_race.txt` | Reopening a popup before its close event ran, 72 trials, fails safe |
| `probe_07_delete_guard.txt` | The time-free Delete habit guard at 8 viewports, mouse, touch, slow and triple clicks |
| `probe_10_yearmonths.mjs`, `.txt` | The real `yearMonths`, `yearStart`, `toggleDay` at far clocks in bounded workers. October to December of 10000 to 10009 never returns and hits a 256 MB heap cap |
| `probe_11_year10000.py` | CS-01 driven through the app, cases control, A, A2, E, C, C2, B-control, B-P2, B-P4 |
| `probe_11_run1_note.txt` | Run 1 of probe_11, an instrument fault (the probe's pace tripped the R14 guard, the fake clock rethrew a timer error) |
| `probe_11_chromium_basic_phone.txt`, `probe_11_webkit_basic_phone.txt` | CS-01's date 10000-01-05 at 1280 and 390, with the 2026 control |
| `probe_11_chromium_far_rollover_bcontrol.txt`, `probe_11_webkit_far_rollover_bcontrol.txt` | 10015-11-20, the rollover into 10000-01-01 with P2 or P4 open, the 9999-10-15 control |
| `probe_11_chromium_hang.txt`, `probe_11_webkit_hang.txt` | 10000-10-15, the row's Year and the band's Year freeze the page, data intact, a second tab boots |
| `probe_12_hang_memory.py`, `.txt` | Chromium renderer during the freeze, one core busy, working set 107 to 1,301 MiB in 12 s |
| `probe_12b_pid_check.py`, `.txt` | Instrument check, CDP process ids are OS PIDs (probe_12 measured its own renderer) |
| `probe_13_delta.py`, `.txt` | The step 5 and 27a delta. Done today state equals stored data under hostile values, Dismiss with the field disabled saves nothing and never leaves focus on body |
| `probe_13_run1.txt` | Run 1 of probe_13, an instrument fault in WebKit (Escape pressed before a close settled) |
| `probe_14_rollover_hang.py`, `.txt` | The freeze arrives with no press at the midnight into 10000-10-01 with P4 open, both engines, control answers |
| `processes.txt` | Every process started, how each was stopped, the closing sweep, and two lapses |
