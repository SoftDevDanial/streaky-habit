# Evidence index, security audit of module app

Written by the security finder (read-only), 2026-10-09, against `6cfe05f`. Every probe is a Python script in this folder, run from the project root as `PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python docs/modules/app/qa/security/20261009T165000/<probe>.py` under a `timeout`. Each one starts its own `python -m http.server <free port> --bind 127.0.0.1`, prints the PID, and stops it by PID in a `finally` block (it then checks that the port refuses connections). `lib.py` holds the shared helpers. Probes print to stdout. The only files they write are the screenshots in `shots/`.

Outputs below are copied from the runs. Where a probe had a bug in my own script, a later probe replaced it, and the table says so.

## Probes

| Probe | What it checks | Result |
|---|---|---|
| `probe_01_static.py` | Sink and egress scan of `index.html` and `src/` | 0 HTML sinks, 0 code-from-string (2 hits are JSDoc `import("...")` type comments), 0 network, navigation, storage-other or dynamic-selector hits, 0 inline handlers, 0 non-ASCII characters. Every `habit.name` use is `view.js` `fillRow` (`textContent`, `setAttribute`) and `openDeleteDialog` (`textContent`). All imports are relative. |
| `probe_02_storage_hostile.py` | T1, T2, T3, T8 through the running app | 34 tamper cases, 10 stored-XSS names, 8 size cases, all as expected. Its last section had a selector bug (it waited on the first strip, not the clicked one). `probe_02b` and `probe_02c` repeat that section. |
| `probe_02b_resource.py`, `probe_02c_resource_rest.py` | Worst-case valid histories near the 5 MB quota | 02b stopped at an ambiguous locator after its first two measurements, 02c ran the rest. |
| `probe_03_csp.py` | The meta CSP in force, with a canary listener | See "CSP" below. Its form-action section was replaced (see 03e). |
| `probe_03b`, `03c`, `03d` | Native form submission with the script blocked | Superseded. They used `time.sleep`, which does not pump Playwright's sync event loop, so request and navigation logs were read before the events arrived. |
| `probe_03e_formaction.py`, `probe_03f_nojs.py` | The same, correctly waited | See "form-action" below. |
| `probe_04_storage_failure.py`, `probe_04b_reset_full.py` | T6 and R18 | See "Storage failure" below. |
| `probe_05_delete_safety.py` | T7 keyboard, returnValue, double click, geometry | Section D found the overlap. |
| `probe_05b_tap_through.py` | Per viewport overlap of a trash button with the dialog's Delete habit, end-to-end double tap | See SEC-01. Its part 5 had a duplicate-name bug in my script (it stored two equal names, so the state was unreadable). |
| `probe_05c_double_click_rows.py` | Double click on the centre of each sample row's trash | Centre clicks keep the habit on the sample. The deleting point is off centre. Part 2 timed the dialog: hit-testable at 4 ms with opacity 0. |
| `probe_05d_click_detail.py` | `event.detail` and gap of the second click | `detail` is 2, gap 166 to 189 ms. |
| `probe_05e_overlap_at_rest.py` | Overlap with the page not scrolled, 1 to 12 habits, 8 viewports | Row 3 overlaps at 390x844, 360x780, 412x915 and 1440x900. |
| `probe_05f_repro_sample.py`, `probe_05g_gap_sweep.py` | Reproduction on the three-habit sample, and the gap sweep | See SEC-01. |
| `probe_05h_second_click_lands.py` | Double click on Delete habit itself | 66 scroll positions, the second click had no side effect. |
| `probe_06_unicode_layout.py`, `probe_06b_dialog_shots.py` | Long, bidi and invisible names | See SEC-02. 06 shot the dialog's first frame (before the fade-in), so 06b repeats the dialog shots after 450 ms. |
| `probe_07_network_origin_frame.py` | R25 request log, R26, T9 sibling write | Parts 1 to 3 ran. Part 4 (framing) failed in my route handler. |
| `probe_07b`, `07c`, `07d` | Framing | 07b and 07c served the top page through `page.route`, which Chromium treats as a public page, so the loopback frame was blocked (`ERR_BLOCKED_BY_LOCAL_NETWORK_ACCESS_CHECKS`). 07d uses a real loopback listener. |
| `probe_07e_browser_flags.py` | Chromium command line | `--disable-features` names `ThirdPartyStoragePartitioning`. |
| `probe_07f_framing_partitioned.py` | Framing with partitioning on | The authoritative T10 result. |
| `probe_08_rollover_clobber_focus.py`, `probe_08b_clobber_focus_rest.py` | Rollover, clock extremes, clobbering, `data-date`, focus, T12 | 08 stopped at an input that is disabled at 12 habits (my script). 08b ran the rest. |
| `probe_09_selector_and_typed_xss.py` | T4 and typed T3 | All held. |
| `probe_10_fix_sketches.py` | Fix sketches applied in memory by route interception | Both sketches verified. `src/` was not touched. |
| `shots/` | Screenshots | `list-*.png` are the page with a hostile name, `dlg-*.png` the dialog after the fade-in, `fix-*.png` the bidi sketch. Files named `dialog-*.png` are the dialog's first frame, before it faded in, and show only the page. |

## Hostile storage matrix (probe_02)

Every row: no change to the shared prototypes, 0 console errors, 0 page errors, 0 JS dialogs.

- Readable, left byte for byte, no note: `__proto__` in a habit (3 shapes), `__proto__` beside real top-level keys, a habit named `__proto__`, seven habits named `constructor`, `toString`, `valueOf`, `hasOwnProperty`, `prototype`, `__defineGetter__`, `__proto__`, `version` as 1.0, 12 habits, dates `0001-01-01` and `9999-12-31`, a 40-emoji name, a lone surrogate, NUL in a name.
- Unreadable, reset to `{"version":1,"habits":[]}` with the note: `__proto__` at top level without a version, `habits` as an object with `__proto__`, `done` element `__proto__`, `done` as an object, array-like `habits`, a name that is an object with `toString` and `trim`, version `true`, version `[1]`, duplicate `version` key (last wins, 2), top-level string, empty string, whitespace, `NaN` token, BOM prefix, trailing garbage, 13 habits, dates with a leading space, Arabic-indic digits, a trailing newline, year 0000, a 41-emoji name, a non-breaking-space-padded name.
- Stored names (up to 40 code points): `<img src=x onerror=window.__pwned=1>`, `<svg onload=...>`, `javascript:...`, `<script>...</script>`, `"><svg/onload=...>`, `'><img src=x onerror=...>`, `<style>*{display:none}</style>`, `<details open ontoggle=...>`, `<base href=//127.0.0.1:1/>`, `<form action=//127.0.0.1:1/><button>x`. For each: `h3` text equals the name, no child elements, `aria-label` equals `Delete <name>`, 0 hostile elements in the body, 0 `on*` attributes, `window.__pwned` undefined, `document.baseURI` unchanged, head unchanged, dialog title `Delete "<name>"?` with 0 child elements. Seven further payloads were above 40 code points and were skipped because the decoder resets them (which is itself the mitigation).
- Size (T8): 4.9M characters of text, a 4.9M-character name, a 4.9M-character astral-emoji name, depth 1,000,000 arrays, a 4.9M-character ignored property, depth 400,000 inside an ignored property, 380k duplicate valid dates, 380k duplicates with one bad date at the end: each loaded in 190 to 601 ms and gave the expected note or rows.
- Valid but huge (desktop headless Chromium): 400,000 consecutive days in one habit (5.2 MB): boot 1162 ms, one tick 728 ms. 12 habits of 33,000 days (5.1 MB): boot 1098 to 1133 ms, tick 161 ms, delete 722 ms. 400,000 days rollover re-render 674 ms. 190,000 alternate days (2.5 MB): boot 578 ms. A heavy real user (12 habits, 5 years daily, 285 KB): boot 160 ms. R16: a readable pretty-printed value with extras was unchanged after load.

## CSP (probe_03)

The meta policy equals the spec R1 string exactly, and it comes before the `link` and `script` in `head`. A positive control showed the canary listener answers a CSP-free page (hit recorded). Attempts inside the app page, all created by CDP evaluate (which the CSP does not govern):

- Blocked, with a `securitypolicyviolation` event and no canary hit: inline `<script>` via DOM and via `insertAdjacentHTML` (`script-src-elem`), `<img onerror>`, `<svg onload>`, `onclick` attribute then click (`script-src-attr`), `javascript:` link, `eval`, `new Function`, `setTimeout('string')` (`script-src`), external `<script src>`, `data:` script, blob worker (`worker-src`), dynamic `import()` of another origin, `fetch` (cross-origin, no-cors, and same-origin `/index.html`), XHR, WebSocket, EventSource, `sendBeacon` (returns true, violation fired, no hit), `new Image`, stylesheet link, `@import` and `url()` in a style element, `<iframe>`, `<object>`, `<embed>`, `<audio>`, a form submit to another origin, `<base href>` (baseURI unchanged), the `ping` attribute.
- Allowed, as the policy says: a same-origin `<script type=module src=/src/storage.js>`; a JS function assigned to `onclick` (needs script already running).
- Not governed by CSP, and the only canary hit: `window.open(canary)` (`GET /open`). Navigation and `dns-prefetch` links are outside `connect-src`. This matters only after a script injection.
- 29 `securitypolicyviolation` events, 0 page errors.

### form-action (probe_03e, probe_03f)

- Control, copy of the page without the CSP and with `app.js` blocked: Enter in the field navigated to `control.html?name=No+alcohol+secret` (a native GET carrying the name).
- Real page, `app.js` blocked: Enter did not navigate, no request carried a query string, console: `Sending form data to 'http://127.0.0.1:.../?name=No+alcohol+secret' violates the following Content Security Policy directive: "form-action 'none'"`.
- Real page, JavaScript disabled: same result. (Clicking Add after a blocked submission hangs Playwright, which waits for a navigation that never commits. That is a tool effect.)

## Storage failure (probe_04, probe_04b)

- `window.localStorage` getter throws `SecurityError`: boots empty, no note, add, tick, add, delete all work in memory, 0 console errors, 0 page errors.
- `Storage.prototype.getItem` throws: same.
- `setItem` throws `QuotaExceededError`: the same flows work, the stored sample is unchanged, a reload shows the saved sample (changes lost, the CG-5 residual).
- A really full origin (filler key of 5,240,826 characters, a 100-character write throws `QuotaExceededError`): same result.
- Unreadable value with a full origin (written before the app first loads): the note shows, `stored` stays `{`, adding a habit works in memory, the next load shows the note again. 0 page errors.

## Delete safety (probe_05 and later)

- Enter on the trash opens the dialog with focus on Cancel. Enter again keeps the habit. Enter held for 6 repeats keeps it. Space opens on key up, Space again is Cancel. Esc keeps. A backdrop click keeps. After deleting A, opening B and pressing Esc keeps B (the `returnValue` reset works).
- Per viewport, no scrolling: the third row overlaps at 390x844 (8 x 27 px), 360x780 (8 x 3), 412x915 (8 x 30), 1440x900 (34 x 23). None at 1280x800, 1366x768, 1920x1080, 375x667.
- Widths with a reachable overlap (12 habits, scrolled): 320 (28 px wide), 330 (18), 340 to 440 (8), 450 (3), 1000 (14), 1100 to 1920 (34). Widths without: 460 to 550 step 10, 600, 700, 800, 899, 900.
- Reproduction on the sample: 1440x900 mouse, double click at (743,512), `['Read 20 pages', 'Stretch 10 minutes']` left, stored state updated. 412x915 touch, double tap at (364,498), same. Gap sweep (0, 40, 80, 120, 200, 300, 450, 700 ms, two runs each): 1440x900 mouse and 412x915 touch deleted at every gap, 390x844 touch only at 0 ms. In `probe_05b` a 390x844 touch double tap with a 60 ms gap and a mouse double click both deleted.
- The second click of a double click or tap on a deliberate "Delete habit": no side effect at 66 scroll positions (36 at 390x844, 30 at 1440x900, 12 habits).

## Network, globals, origin, framing

- `probe_07` part 1, one context over open, tick, add, delete, reload, midnight rollover, visibility change, a cancelled delete: 14 requests, all `GET`, all the page's own origin, no query string: `/`, `/src/app.js`, `/src/dates.js`, `/src/habits.js`, `/src/storage.js`, `/src/styles.css`, `/src/view.js`. No websocket, worker or service worker, 0 service worker registrations, 0 console messages, 0 page errors.
- R26: no property on `window` that a blank same-origin page does not have, and none missing. `/?demo=1`, `/?seed`, `/#sample`, `/?sample=1&seed=1&demo=true#sample` and `/?state=%7B%7D` give a body equal to `/`, with 0 storage keys.
- T9: with the app open, a sibling page wrote the key, and the app showed nothing new (no `storage` listener). The app's next save overwrote the sibling's value (last save wins). After a plant and a reload the hostile name showed as literal text and `window.__pwned` stayed undefined. The sibling page can read `streaks.state` (names and history).
- T10, Chromium with partitioning on (07f): the cross-site frame renders the app and sees an empty separate store, and a habit typed into it never reaches the first-party store. The same-site frame (another origin on the same site) sees the first-party habits and a habit typed into it is saved to the real store. The parent cannot read the frame's document in either case. With Playwright's default Chromium (07d), the cross-site frame sees the first-party habits, because that build disables `ThirdPartyStoragePartitioning` (07e).

## Rollover, clock, clobbering, focus (probe_08, probe_08b)

- Hostile valid dates (`0001-01-01`, `9999-12-31`, the window edges and a run of future days): rollover re-renders, 0 errors, future cells counted correctly (3 future before, 2 after).
- Device clock: year 1970, 0001 and 2100 behave. Year 10000 (clock set that far ahead): a tick saves `10000-01-01`, and the next load shows the reset note with no habits (SEC-05).
- Habits named like ids and window members (`new-habit`, `del-title`, `h1-name`, `document`, `location`, `localStorage`, `__proto__`, `constructor`, `length`, `forms`): every id still resolves to the app's own element once, `document.forms` is intact, delete and add work.
- `data-date` set by hand to an outside date, `__proto__`, empty, 4 MB, a future date: state unchanged. A different day inside the window: that day is toggled (the intended behaviour).
- Rollover while the dialog is open: the dialog stays open, its title still names the same habit, and Delete removes that habit.
- Selector metacharacters in names (probe_09): rows, ticks and delete act on the right habit.
- T12: A adds, then B (opened before A saved) adds: only B's habit remains.

## Unicode and layout (probe_06, probe_06b)

- 20 name shapes at 320, 360 and 390: no horizontal overflow, the name stays in its row, the trash button stays hit-testable. `h3.habit-name` computes `direction ltr`, `unicode-bidi isolate`.
- Dialog title with an unterminated override: `Delete "?"ereh txet desreveR` and `Delete "Read 20 pagessyield ?"png.` (`shots/dlg-rlo-prefix.png`, `shots/dlg-rlo-spoof-tail.png`). A name of 1 base plus 39 combining marks overprints the brand and the dialog title (`shots/dlg-zalgo.png`).

## Fix sketches (probe_10), applied in memory

- Arming window (500 ms from the opening click's `event.timeStamp`) in a capture listener on the dialog that calls `preventDefault()` on a click on `.btn-danger`: two activations 0, 120 and 300 ms apart at the overlap keep the habit at 1440x900 mouse and 412x915 touch (3 rows). A deliberate click after the window deletes, Enter on the focused Delete button after the window deletes, Cancel works at once, 0 page errors.
- FSI and PDI around the name in the dialog title (`Delete "⁨<name>⁩"?`): the closing quote and question mark stay at the end of the title (`shots/fix-rlo-prefix.png`).
