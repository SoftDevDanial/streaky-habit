---
module: app
kind: security
status: pass
counts: { critical: 0, high: 0, medium: 0, low: 0 }
---
# Security audit, app (v1.1.0, step 5)

> Written by the security finder (read-only), 2026-10-15, against HEAD `4e860ff` on `main`. It replaces the 1.0 verdict of this file (2026-10-09 with its solver and re-check sections, all at tag `v1.0.0` and in git history). Scope is `git diff v1.0.0..HEAD -- index.html src tests` and the files it touches, judged against the spec's Threat model (T1 to T13), Invariants, R1, R16, R17, R24 to R26, R29, R41, the D2 Content Security Policy in `docs/modules/ROADMAP.md` and the Publish rules of `CLAUDE.md`. This round's QA and code-review verdicts were read as context only. Engines Chromium 149.0.7827.55 and WebKit 26.5 (Playwright 1.61.0, Python 3.14.0), headless, Windows 11. Evidence is `docs/modules/app/qa/security/20261015-131500/` (`evidence.md` first). Line numbers are as of `4e860ff`.

## Verdict

**PASS. 0 CRITICAL, 0 HIGH, 0 MEDIUM, 0 LOW.**

Every required mitigation of T1 to T13 is in the code and held when driven in both engines. Names stay text in every v1.1.0 sink. 29 crafted stored values reset with the note, and 7 hostile but readable ones load without polluting a prototype and without a control for any day outside the year. A value at the 5 MiB quota costs at most about 1.9 s per tick on this desktop. 25 egress and code attempts from inside the page reached a canary origin 0 times, and every flow made only same-origin GET requests with no query string. No hook or global is added. The time-free delete guard held at 8 viewports for mouse, touch, slow and triple clicks. The new surface gave four observations and no finding.

## CRITICAL

None.

## HIGH

None.

## MEDIUM

None.

## LOW

None.

## Threat model, row by row (what I ran and what it showed)

| Row | Control found (file:line) | Driven | Verdict |
|---|---|---|---|
| T1 tampered or corrupt data | `JSON.parse` in `try` (`src/storage.js:51`), the strict readable rule in `readHabit` and `readHabits` (`:24`, `:32`), anything else resets with the note (`loadHabits`, `:74`). Values reach the DOM only through `element`, `svgElement` and `textContent` (`src/calendar.js:64`, `:73`). Days outside the year get no control because P2 and P4 are laid out from `yearMonths` and the band from `heatmapCells` | `probe_02_tamper.txt`. 29 unreadable values (bad JSON, wrong version, 13 habits, duplicate, untrimmed, 41 code points, bad or far or fullwidth or year-0000 or year-10000 keys, keys only in `__proto__`) all reset to `{"version":1,"habits":[]}` with the note in both engines, 0 page errors. A readable value with `0001-01-01`, `2025-10-09`, `2026-10-11` and `9999-12-31` loads, P2 and P4 hold 366 controls from 2025-10-10 to 2026-10-10 and the band 83 up to today, and the outside days survive the next save. Loading writes nothing (`probe_02b_surrogate_write.txt`, 0 `setItem` calls) | PASS |
| T2 prototype pollution | Habits rebuilt as `{ name, done }` literals (`src/storage.js:29`), no spread or `Object.assign` of parsed objects | `__proto__` and `constructor.prototype` at both levels and as names. `Object.prototype` and `Array.prototype` own names equal a clean page, `({}).polluted` is undefined, the first save holds only `version`, `habits`, `name`, `done` (`probe_02_tamper.txt`). Twelve object-key names such as `__proto__`, `constructor`, `then`, `rn-1` render and persist | PASS |
| T3 script injection through a name | Every name sink is `textContent` or `setAttribute` (`createRow` `src/view.js:80`, `createTick` `src/popups.js:128`, `#yr-title` `src/popups.js:99`, `renderDeleteTitle` `src/popups.js:68`). `src/` has no `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, `eval` or `Function` (`probe_00_static.txt`). CSP `script-src 'self'` behind it | `probe_01_names.txt`. 12 hostile names (`<img onerror>`, `<svg onload>`, a script breaker, `javascript:`, `<style>`, `<iframe srcdoc>`, `<base>`, entities, template markers, selector breakers), planted at 1280 and 390 and typed, in both engines. Row `h3`, the bin's, Year's and Done today's names, P1's tick name and `.tname`, P2's title and M1's title over P2 all equal the name with no child element. 0 `img`, `iframe`, `style`, `base`, `object` elements, 0 `on*` attributes, 0 JS dialogs, 0 CSP violations, baseURI unchanged | PASS |
| T4 selector injection | No selector is built from data. Rows by position, days compared by `data-key` with `===` (`dayControlAt` `src/calendar.js:55`, `markOpenDay`), never interpolated (`probe_00_static.txt`, the selector rule found nothing) | Selector-breaking names act only on their own row (`probe_01_names.txt`). DOM edits of `data-key` to `2027-01-01`, `2025-10-09`, `__proto__`, empty and nonsense open P1 with a nonsense title, and no tick reaches storage, because `toggleDay` refuses them (`probe_02_tamper.txt`, a defence-in-depth check that needs script on the page) | PASS |
| T5 data leaving the device | No network code (`probe_00_static.txt`). CSP equal to R1 and D2 (`index.html:5`), before every link and script. The icon is the same-origin file `src/icon.svg` (`index.html:12`) | `probe_04_csp_network.txt`. A canary server on another origin logged 0 requests after fetch (both origins), XHR, WebSocket, EventSource, sendBeacon, image, stylesheet, `@import`, `url()` in a style element and attribute, iframe, object, embed, audio, prefetch, external script, dynamic import, blob worker, form submit and `<base>`, in both engines. Inline script, inline handler and string timer never ran, `eval` and `new Function` threw `EvalError` | PASS |
| T6 storage blocked or full | Reads and writes in `try` (`src/storage.js:74`, `:95`), the thrown value never read, the warning from `saveFailed` | With `FAIL_SETITEM_PROBE` the warning shows on a failing save and 0 `test:storage-read:` markers appear (SW2). With `FAIL_GETTER` the warning shows at boot. 0 page errors (`probe_04_csp_network.txt`). The private browsing and Safari clean-up residual stays as the spec states | PASS |
| T7 accidental deletion | `isStrayPress` (`src/app.js:139`) on every Delete habit click (`:241`), the opener's box kept at `openDelete` (`:126`), the tap-through guard `guardTapThrough` (`:280`) | `probe_07_delete_guard.txt`. The bin overlaps M1's Delete habit at 7 of 8 viewports. At the overlap a mouse double click, a touch double tap, a second click 700 ms later with `detail` 1 and a triple click delete nothing in either engine. P2's Delete habit never overlaps M1's, and a double press there closes M1 on its backdrop. A click on Delete habit beside the opener's box and Enter both delete the named habit | PASS |
| T8 huge planted value, v1.1.0 year views | Linear decode, `doneFlags` one `includes` per habit per call (habit-logic evidence, part 6) | `probe_03_planted_size.txt`. Quota 5,242,880 UTF-16 units in both engines. At 5.1 M characters (395,000 valid days in one habit, or 12 x 32,900) boot takes 0.8 to 1.1 s, opening P4 0.4 to 0.5 s, a tick in P1 over P4 1.3 to 1.9 s, a bead tick 0.6 to 1.8 s, in both engines. Five years of real daily use for 12 habits stays under 0.15 s everywhere. "Slow to open" holds and nothing hangs | PASS, residual as stated |
| T9 shared origin | Accepted residual, unchanged | Not re-measured. The app ignores the `storage` event (no listener found) | Accepted |
| T10 framing, v1.1.0 hub | Accepted, the meta CSP cannot set `frame-ancestors` | The hub is outside this project and was not read (see Not audited) | Accepted |
| T11 supply chain | Zero dependencies, every URL relative (`probe_00_static.txt`, href and src values only `src/...` and `#i-*`), the Phosphor credit in the head comment | Every request in every flow was to the app's own origin (`probe_04_csp_network.txt`) | PASS |
| T12 two tabs | Accepted residual, unchanged | Not re-measured | Accepted |
| T13 the tab icon | `src/icon.svg` equals, byte for byte, the decoded icon of all 8 goldens that carry one, and holds no script, handler, href, `url(`, `@import`, `foreignObject`, entity or external scheme (`probe_00_static.txt`, sha256 `e064a981...0382`) | Loaded as an image from the link's href under the live CSP, `load` fires (150 px wide) with 0 violations, both engines (`probe_04_csp_network.txt`) | PASS |

Requirements that carry security weight.

| Item | Driven | Verdict |
|---|---|---|
| R1 and D2, the CSP | One meta, equal to the R1 and D2 strings, before the icon link, the stylesheet and the module script. One script element, `src/app.js`, no inline body. The only inline style is the sprite's `position:absolute` (`probe_00_static.txt`) | PASS |
| R24 names are text | See T3. Also bidi in the new sinks (`probe_05_bidi_layout.txt`). 11 names with overrides, embeddings, unmatched isolates, PDI and paragraph separators never move P1's tick numbers, P2's stats or a row's stats, because each name sits in its own block or grid item. M1's quotes stay right of the name for all 11, so the 1.0 strip (`TITLE_STRIPPED`, `src/popups.js:61`) still holds after its move from `view.js`. At 360 x 780 with 12 wide, combining, ZWJ, override, Arabic and CJK names the page never scrolls sideways | PASS |
| R25 nothing leaves the device | Every v1.1.0 flow (add, Done today, P1 from the band and from P3, P4 from the band and from P3, P1 over P4, P2, a bead, M1 kept and done, a failing save, a reload, a rollover with P4 open) at 1280 and 390 in both engines made only `GET /`, `src/*.js` and `src/styles.css`, no query string, 0 console errors, 0 page errors (`probe_04_csp_network.txt`). Neither headless engine requested `src/icon.svg` on its own, which R25 allows | PASS |
| R26 no seed, hooks or globals | No `window` or `globalThis` write and no dunder name in `src/` (`probe_00_static.txt`). 0 own properties added to `window` against a same-origin blank page with the same clock, after every flow, both engines (`probe_01_names.txt`, `probe_04_csp_network.txt`). `?demo=1`, `?seed`, `#sample`, `?sample=1&seed=1&demo=true#sample`, `?state=...` and `index.html?debug=1` give the same body as `/` with 0 storage keys. No sample name and no reference to `sample-history` in any shipped file. 0 clipboard markers in every context | PASS |
| R41 SW2, the thrown value is never read | See T6 | PASS |
| Publish copy (CLAUDE.md Publish, 1.0 SEC-04) | The publish set is `index.html` and the 10 files of `src/`, all tracked, nothing else in `src/`. No shipped file refers to `docs/`, `tests/` or `harness/` except a comment in `styles.css` that names `docs/design/system.css`. No credential-shaped file name anywhere in the project and no secret pattern in the shipped files. `.nojekyll` is not made yet, which is the orchestrator's release step (`probe_00_static.txt`) | PASS |

## New surface hunted (v1.1.0)

- **Day editor, year view, overview and overview year.** Name sinks, `data-key` handling, the editable range and the cost of the year views. Covered above (T1, T3, T4, T8, R24).
- **The save warning.** Static copy, never built from the exception. Covered (T6).
- **The tab icon.** Covered (T13).
- **The rollover.** It ran with P4 open in both engines with no error and no request (`probe_04_csp_network.txt`). It changes no habit, so a popup's index stays right.
- **The strict decoder.** Covered (T1, T2). Duplicates and order are fixed in memory and nothing is written at load.
- **Reopening a popup before its close event ran.** Found by my own probe, see O1. It fails safe.
- **Popups and focus as an injection path.** No popup builds markup or a selector from data. `keepDayInSight` writes one inline `padding-bottom` through the CSSOM from measured numbers (`src/popups.js:195`).

## Observations (not filed)

- **O1. A popup reopened before the previous `close` event ran loses its state, and it fails safe.** `onPopupClose` (`src/app.js:298`) clears `state.year`, `state.day` and `state.remove` and moves focus to the opener, and the `close` event is a queued task. Key presses with no wait between them can be handled first. In 72 trials (`probe_06_close_race.txt`) every delete removed exactly the habit M1's title named (28 of 28), every tick changed exactly the day and habit P1 showed, and the rest did nothing (P2's Delete habit or M1's Delete habit threw `TypeError`, or `toggleDay` refused a null day). One WebKit trial ticked the day P1 showed just before an Escape that closed it. No wrong habit or day was ever changed. Reached only at automation speed, not a trust-boundary issue. For code review, a reopen could clear only state that still belongs to the closed popup.
- **O2. Device clock in the year 10000 (1.0 SEC-05, accepted).** `yearMonths` throws on a five-digit key, so P2 and P4 do not open, which the code review already gave to the README. `toggleDay` compares such keys as text and would accept `1000-06-01` for today `10000-01-05`, but no control of the app offers that day (habit-logic evidence, part 7). Nothing new to rule.
- **O3. T8 on a phone is unmeasured.** The figures above are desktop figures. A phone may be several times slower at the quota, which stays "slow", not a hang. The streak counts of every row cost more than the year views (habit-logic evidence, part 9).
- **O4. The repository, unlike the publish copy, holds local paths.** Of 2,163 tracked files, 75 hold `D:/` project paths and 15 the Windows user path, and none holds the owner's email address or a secret pattern (a count from `git ls-files`, not saved as a file). The Publish rule keeps them off Pages. If the repository itself is made public, as the showcase plan has it, they go with it. For the orchestrator's publish preparation.
- **O5. Hardening that the owner's CSP ruling leaves out.** `style-src 'unsafe-inline'` is needed only by the sprite's inline style, and Chromium's `require-trusted-types-for 'script'` would turn any future HTML sink into an error. Neither is needed while no HTML sink exists. Ledger S6 row 2 keeps the CSP as 1.0's.

## Not audited

- The showcase hub that frames the app (trust boundary 5, T10). It lives outside this project. The constraint that it never writes `streaks.state` and never calls `localStorage.clear()` is unverified here.
- Firefox and real iPhone Safari (out of the test floor by design. T7's iPhone double tap stays with UAT).
- GitHub Pages response headers (no network was used).
- Screen reader output for names with bidi or invisible characters.

## Processes and process notes

PROCESSES: none alive. Every probe ran in the foreground under `timeout`. Each started its own `python -m http.server` on a free 127.0.0.1 port from the project root and stopped it by its exact PID in a `finally`, printing that the port refuses connections, and launched one headless browser per engine through Playwright, closed in a `finally`. The server PIDs, all STOPPED, are 9944, 9256, 13244, 25480, 520, 21468, 17412, 9048, 23516, 15444, 19516, 22160, 6044, 23484, 12616, 19728, 13128, 13884, 14568, 21192 with its canary 5700, 7428, 8528 and 7568. The node probe and one `node --test` run started no server. The closing sweep at 13:52 with `Get-CimInstance Win32_Process`, filtered by name on python, node, chrome, headless, Playwright and WebKit and listed with parent, creation time and command line, found none. `Get-NetTCPConnection -State Listen` on 127.0.0.1 showed 8 ports, none owned by a PID above.

Process notes.
- The first version of `probe_03` (one script, buffered output, a tick check that could never be met) ran into the shell's 590 s timeout with no output. Its server PID was never printed. The sweep right after found no chrome, no http.server of mine and no python of mine. It was replaced by `probe_03a` and the fixed `probe_03`.
- Another agent's `python -m pytest tests/browser -q --tb=no -rN --engine webkit` (PID 23720, parent 3784, from 13:29) with its server on port 2662 and its WebKit processes was running during my T8 timings. It was not mine and I left it alone. It may have made those timings higher.
- One lapse against the brief. The unit-suite command `node --test "tests/**/*.test.js" 2>&1 | tail -9` used `2>&1`. It wrote no file. Its output is in `docs/modules/habit-logic/qa/security/20261015-131500/unit-suite-tail.txt`.
- `git status` shows no change under `src/`, `tests/`, `index.html` or `docs/design/`. My only writes are this file, the habit-logic findings file and the two evidence folders.
