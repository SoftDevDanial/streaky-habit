# Evidence index, security audit of app v1.1.0 (2026-10-15)

Security finder, read-only. HEAD `4e860ff`. Every probe was run from this folder with `python -u -B` (or `python -B`), so no bytecode was written under `tests/browser/`. Each probe printed its result to stdout, and the `.txt` beside it holds that stdout, written with the Write tool. Servers were `python -m http.server <port> --bind 127.0.0.1` from the project root, started and stopped inside each probe (`lib.py`), and each stop printed that the port refuses connections. Every browser context was fresh and headless, and the clipboard stand-in of `tests/browser/conftest.py` was its first init script. Planted values were built inside the throwaway context and never written to disk. The probe sources hold the hostile names as string literals, and no planted state file exists.

| File | What it shows |
|---|---|
| `lib.py` | Server start and stop with the port check, the session with the stand-in, CSP violation logging, request logging |
| `probe_00_static.py`, `.txt` | CSP string, head order, no inline script or handler, banned API scan of `src/`, non-ASCII bytes, icon bytes equal to the goldens, no sample names, the publish set, credential-shaped names (none) |
| `probe_01_names.py`, `.txt` | 12 hostile names, planted and typed, through every v1.1.0 sink in Chromium and WebKit |
| `probe_01_names_run1.txt` | The first version of probe_01, driven faster than the app's close events, kept as the first sight of the close race |
| `probe_02_tamper.py`, `.txt` | 29 unreadable and 7 readable stored values, prototype checks, no control outside the year, DOM `data-key` edits |
| `probe_02b_surrogate_write.py`, `.txt` | Loading writes nothing for lone-surrogate and control-character names, compared inside the page |
| `probe_03a_quota.py` | The localStorage quota per engine (output in `probe_03_planted_size.txt`) |
| `probe_03_planted_size.py`, `.txt` | Boot, ticks, P4, P1 over P4 and P2 timed with planted values up to the quota, both engines |
| `probe_04_csp_network.py`, `run_04.py`, `.txt` | 25 egress and code attempts against a canary origin, every v1.1.0 flow with its request log, failing storage, rollover, query strings, the icon under the CSP |
| `probe_05_bidi_layout.py`, `.txt` | Bidi and control characters in P1, P2, rows and M1, and layout at 360 x 780 |
| `probe_06_close_race.py`, `.txt` | Reopening a popup before its previous close event ran, 72 trials, effect against what the popup shows |
| `probe_07_delete_guard.py`, `run_07.py`, `.txt` | The time-free guard of Delete habit at 8 viewports, mouse, touch, slow and triple clicks, with controls |
