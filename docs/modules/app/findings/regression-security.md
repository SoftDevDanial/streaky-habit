---
module: app
kind: security
status: issues_found
counts: { critical: 0, high: 0, medium: 0, low: 1 }
---
# Security audit, app, v1.1.0 regression

> Written by the security finder (read-only), 2026-10-15, against HEAD `ddf43f6` on `main`. Scope is the app delta since the last security pass at `4e860ff` (`git diff 4e860ff HEAD -- src index.html`, five files, the step 5 solver round and task 27a), judged against the app spec's Threat model (T1 to T13), Invariants, R1, R16, R17, R24 to R26, R29 and R41, plus item CS-01 of `docs/regression/20261015-185800/consistency.md`. habit-logic `src/` is unchanged since `4e860ff` (`git diff` of `dates.js`, `habits.js`, `storage.js`, `ring.js`, `styles.css`, `icon.svg` is empty), so its verdict stands. The 4e860ff instruments were run again unchanged and five new probes were written for the delta and CS-01. Engines Chromium 149.0.7827.55 and WebKit 26.5 (Playwright 1.61.0), headless, the clipboard stand-in first in every context. Evidence is `docs/modules/app/qa/regression-security/20261015-192841/` (`evidence.md` first). Line numbers are as of `ddf43f6`.

## Verdict

**ISSUES FOUND, LOW only. 0 CRITICAL, 0 HIGH, 0 MEDIUM, 1 LOW.**

Every required mitigation of T1 to T13 still holds on the delta, with fresh captures in both engines. The delta adds no trust boundary, no sink and no global. Done today now reads `doneFlags`, and its state equalled the stored data at every step under hostile values. Dismiss with the field disabled saves nothing and never leaves focus on `body`. The one finding is the v1.1.0 form of the year 10000 residual (CS-01). It loses no data any more, but in October to December of the years 10000 to 10009 a year view freezes the tab, which neither the accepted 1.0 note nor CS-01 describes.

## CRITICAL

None.

## HIGH

None.

## MEDIUM

None.

## LOW

### SEC-R01. With the device clock in October to December of the years 10000 to 10009, a year view freezes the tab, and the accepted SEC-05 text no longer describes the year 10000 residual
- **File.** `src/habits.js:226` `yearMonths`, whose loop (`:230`) ends only when a month's `YYYY-M` prefix equals the prefix of `yearStart(todayKey)` (`:232`). It is reached through `layOutMonths` (`src/calendar.js:271`) from `drawHabitYear` (`:306`) and `drawAllHabitsYear` (`:190`), that is from `openYear` (`src/app.js:117`), `openAllHabits` (`src/app.js:101`) and the rollover's `render` in `checkDay` (`src/app.js:338`). The today key comes from `readToday` (`src/app.js:23`) through `localDateKey` (`src/dates.js:76`), which writes a five digit year that `isDateKey` (`src/dates.js:86`) rejects. **Boundary.** device clock → `readToday` → `todayKey` → `yearMonths`.
- **Failure scenario.** The clock reads 15 October 10000. The user presses a row's Year, the band's Year or P3's Year. `yearStart` gives `09990-10-15`, a prefix `formatKey` never writes, so the month-by-month walk runs past year 1 and never meets that prefix. The press never returns, the renderer runs one core flat out and its working set grows about 90 MiB a second (107 to 1,301 MiB in 12 s in Chromium) until it gives out. Node's run of the same call hit a 256 MB heap cap in about 3.3 s. The freeze also comes with no press at all. At the midnight into 1 October 10000 with P4 open, the day check redraws P4 and freezes (both engines). P4 can be open on 30 September because a second press on Year opens it on the layout the first press's error left behind (`drawAllHabitsYear` records the day at `src/calendar.js:188` before `layOutMonths` runs). In every case nothing was saved and nothing was lost. A second tab of the same browser booted with the habit and no banner, and a reload does the same. The other far clocks fail safe and visibly. January to September of any five digit year, and six digit years, make P2 and P4 throw a `TypeError` and not open. Later five digit Octobers to Decembers open them with ten one-day months whose keys fail `isDateKey`, and every tick there is refused. Done today does nothing at any such clock.
- **Reach.** Only the device's own clock, set at least 7,974 years ahead (JavaScript dates go to the year 275760). No stored value, typed name or same-origin page can set it, so no trust boundary of the Threat model leads here. It denies the tab, not the data.
- **Maps to spec threat.** The 1.0 note SEC-05 (accepted LOW at the 1.0 seal), which the Threat model's closing line says "still hold[s] as written at tag `v1.0.0`". It no longer does. The v1.1.0 form, and the freeze in particular, is NEW, not in the threat model. The README's Known limits row still gives the 1.0 text.
- **Why LOW.** The precondition is not realistic and not attacker-controlled, there is no data loss, exposure or code execution, and a reload recovers. It is filed rather than noted because the accepted residual describes a different failure (a wipe at the next load), and a freeze with unbounded memory growth needs the owner's own acceptance or a fix.
- **Fix direction.** The owner rules one of two. (a) Re-accept with the v1.1.0 text. The planner adds a dated note under the Threat model's closing line (the v1.1.0 form, the freeze included) and the orchestrator rewrites the README row (CS-01, RM-01). (b) Close the freeze with one bound, then re-accept the rest. Either `yearMonths` stops after the 13 months its own doc comment promises, which ends the walk for any input (a habit-logic change, the planner's call), or the app opens and redraws no year view while `isDateKey(todayKey)` is false. A guard in `toggleDay` on `todayKey` (habit-logic security O1) is not needed for integrity, because `toggleDay` already refused every key a control offered at every far clock driven here.
- **Evidence.** `probe_10_yearmonths.txt` (the function at 13 clocks, the out-of-memory rows), `probe_11_chromium_hang.txt` and `probe_11_webkit_hang.txt` (the presses, storage and a second tab during the freeze, the 9999-10-15 control in the `far_rollover_bcontrol` captures), `probe_12_hang_memory.txt` (CPU and memory), `probe_14_rollover_hang.txt` (no press, P4 open at midnight, with a control), `probe_11_*_basic_phone.txt` and `probe_11_*_far_rollover_bcontrol.txt` (the throw, the eleven-month and rollover forms).

## CS-01 judgment

- **The form CS-01 measured is the same residual at a lower weight, not a new finding.** At 10000-01-05 (`probe_11_chromium_basic_phone.txt`, `probe_11_webkit_basic_phone.txt`) Done today stays unpressed and saves nothing, the band shows 5 day buttons, P2 and P4 throw `TypeError` on opening (both engines), a reload keeps the habit with no banner and no reset. 1.0 wiped every habit at the next load. v1.1.0 writes nothing unreadable because `toggleDay` checks `isDateKey` on the day first (`src/habits.js:125`), so the integrity half of SEC-05 is gone and what is left fails visibly. CS-01's docs fix (planner note, README RM-01) is right for this part.
- **CS-01 did not reach the October to December branch, which is a freeze.** That branch is filed as SEC-R01 so the owner accepts the residual knowing it, or one bound removes it.
- **Integrity held at every far clock driven, in both engines.** 10000-01-05 at 1280 and 390 (Done today, a band day and a P3 day with their P1 ticks), 10015-11-20 (a P2 bead and a P4 day tick on invalid keys), 10000-10-15 (Done today, then the freeze), and the rollover from 9999-12-31 23:59 into 10000-01-01 with P2 or P4 open (beads 9999-12-31 and 9999-12-30, a stale P4 day's tick, Done today). Each stored value stayed byte for byte readable and a reload kept the habit.

## Threat model, row by row (what I ran and what it showed)

| Row | Control found (file:line) | Driven | Verdict |
|---|---|---|---|
| T1 tampered or corrupt data | `JSON.parse` in `try` and the strict readable rule in `src/storage.js` (unchanged), values reach the DOM only through `element`, `svgElement`, `textContent` and `setAttribute`. Days outside the year get no control | `probe_02_tamper.txt`, 29 unreadable values reset to the empty state with the note, 7 readable ones load, P2 and P4 hold 366 controls from 2025-10-10 to 2026-10-10 and the band 83, outside dates survive the next save, both engines. `probe_02b_surrogate_write.txt`, loading makes 0 `setItem` calls. `probe_13_delta.txt`, every row's Done today equals the stored data | PASS |
| T2 prototype pollution | `{ name, done }` literals in `readHabit` and in habit-logic, no spread or `Object.assign` of parsed objects | `probe_02_tamper.txt`, every case `proto_clean`, saved keys only `version`, `habits`, `name`, `done`. Twelve object-key names render, save and match storage (`probe_13_delta.txt`) | PASS |
| T3 script injection through a name | Every name sink is `textContent` or `setAttribute` (`createRow` `src/view.js:92`, `createTick` `src/popups.js:126`, `renderHabitYear` `src/popups.js:95`, `renderDeleteTitle` `src/popups.js:66`). No HTML sink in `src/` (`probe_00_static.txt` section 3). CSP `script-src 'self'` | `probe_01_names.txt`, 12 hostile names planted at 1280 and 390 and typed, every sink equals the name with no child element, 0 `img`, `iframe`, `style`, `base`, `object`, 0 `on*` attributes, 0 JS dialogs, 0 CSP violations, both engines | PASS |
| T4 selector injection | No selector built from data (`probe_00_static.txt`, the rule found nothing). Days compared by `data-key` with `===` (`dayControlAt` `src/calendar.js:55`, `markOpenDay` `src/popups.js:183`) | DOM edits of `data-key` open P1 with a nonsense title and no tick reaches storage, both engines (`probe_02_tamper.txt`) | PASS |
| T5 data leaving the device | No network code (`probe_00_static.txt`). CSP equal to R1 and D2 (`index.html:5`), before every link and script | `probe_04_csp_network.txt`, 25 egress and code attempts reach a canary origin 0 times, every flow makes only same-origin GET requests with no query string, both engines | PASS |
| T6 storage blocked or full | Reads and writes in `try`, the thrown value never read, the warning from `saveFailed` | `probe_04_csp_network.txt`, the warning shows on a failing save and at boot with storage denied, 0 `test:storage-read:` markers, 0 page errors | PASS |
| T7 accidental deletion | `isStrayPress` (`src/app.js:140`) on Delete habit (`:242`), the opener's box kept by `openDelete` (`:127`), `guardTapThrough` (`:281`, only its comment changed) | `probe_07_delete_guard.txt`, at the 7 of 8 viewports where the bin overlaps Delete habit, a double click, a double tap, a slow second click and a triple click delete nothing, a click beside the opener's box and Enter delete the named habit, both engines. Run 1 of `probe_11` also met the R14 window holding a fast page click (`probe_11_run1_note.txt`) | PASS |
| T8 huge planted value | Linear decode, one `includes` per habit per `doneFlags` call. The delta shares one `doneFlags` for today between the Overview button and the rows | `probe_03_planted_size.txt`, at the quota the slowest step is a tick in P1 over P4, 1.93 s in Chromium and 1.53 s in WebKit (1.86 s at `4e860ff`). Five years of real use stays at or under 0.14 s | PASS, residual as stated |
| T9 shared origin | Accepted residual. No `storage` listener (`probe_00_static.txt`) | Not re-measured | Accepted |
| T10 framing, the hub | Accepted, a meta CSP cannot set `frame-ancestors` | The hub is outside this project and was not read | Accepted |
| T11 supply chain | Zero dependencies, every URL relative, the Phosphor credit in the head comment | `probe_00_static.txt`, href and src values only `src/...` and `#i-*`. Every request same-origin (`probe_04_csp_network.txt`) | PASS |
| T12 two tabs | Accepted residual | Not re-measured | Accepted |
| T13 the tab icon | `src/icon.svg` equals the decoded icon of all 8 goldens, sha256 `e064a981...0382`, unchanged, no script, handler, href or external scheme | Loaded as an image under the live CSP, `load` at 150 px, 0 violations, both engines (`probe_04_csp_network.txt`) | PASS |

Requirements that carry security weight.

| Item | Driven | Verdict |
|---|---|---|
| R1 and D2, the CSP | One meta equal to both strings, before the icon link, the stylesheet and the one module script, no inline script (`probe_00_static.txt`). The `index.html` delta is one comment | PASS |
| R17, Dismiss (task 27a) | With 12 habits typed in after a reset, Dismiss by mouse and by keyboard at 390 and 1280 leaves the stored text unchanged, removes the note for good, and puts focus on the Overview button (390) or the band's Year (1280), never `body`. With the field enabled focus goes to the field. Both engines, 0 page errors (`probe_13_delta.txt`) | PASS |
| R24 names are text | See T3, and bidi names never move P1's tick numbers, P2's stats, a row's stats or M1's quotes (`probe_05_bidi_layout.txt`) | PASS |
| R25 nothing leaves the device | See T5, 0 console and page errors in every flow, both engines | PASS |
| R26 no seed, hooks or globals | 0 window properties added after every flow, query strings and fragments boot like `/` with 0 storage keys, no sample name in any shipped file (`probe_04_csp_network.txt`, `probe_00_static.txt`) | PASS |
| R41 SW2 | See T6 | PASS |
| Publish copy | The shipped set is `index.html` and the 10 files of `src/`, all tracked. `.nojekyll` is the orchestrator's release step (`probe_00_static.txt`) | PASS |

## The delta, piece by piece

- **`render`, `renderRows`, `syncRow` (`src/app.js:51`, `src/view.js:66`, `:107`).** Done today's `aria-pressed` now comes from `doneFlags(habits, todayKey)`, the same array the Overview button reads. The data path is unchanged (the decoded habits, one `includes` per habit), the index is the row's position and the rows equal the habits in number. Driven with today duplicated, unsorted lists, keys after today and twelve object-key names, at boot, after Done today by keyboard and mouse, after a P1 tick, a P2 bead and a rollover, the row state equalled the stored data and the Overview count equalled the pressed rows in both engines (`probe_13_delta.txt`).
- **`dismissNote` and `firstControl` (`src/view.js:271`, `:282`).** Reads the DOM only and moves focus. It saves nothing (checked byte for byte) and cannot return nothing while the field is disabled, because twelve rows' controls are then shown.
- **`dayUnit` and `icon` moved to `src/view.js`.** `popups.js` now imports them from `view.js`, and `view.js` imports nothing from `popups.js`, so no import cycle. `icon` builds `use href` from a constant `#i-*` id, never from data. No global and no new export reachable from the page.
- **`guardTapThrough` comment, `index.html` comment.** No behaviour change. The guard is still registered first in the capture phase (`src/app.js:366`, `:373`) and held in `probe_07`.

## Observations (not filed)

- **O-R1. At 27 to 31 December 9999 the band offers days after today as buttons.** `heatmapCells` compares keys as text, and `10000-01-01` sorts before `9999-12-31`, so the band at 9999-12-31 held 84 buttons up to 10000-01-02 (`probe_11_*_far_rollover_bcontrol.txt`). Their P1 ticks are refused. Same family as SEC-R01, nothing saved.
- **O-R2. A rollover into the year 10000 with P2 or P4 open stops `render` before the rows.** `render` draws the open popups before `renderRows` (`src/app.js:59` to `:63`), so the throw in P2's or P4's redraw left Done today showing 9999-12-31's state on 10000-01-01. Pressing it changed nothing, and a reload showed the right state. Same family.
- **O-R3. `drawAllHabitsYear` records the day before it lays P4 out (`src/calendar.js:188`).** After a throw, the next press opens P4 empty or on the old year. This is the path to SEC-R01's no-press freeze, and a robustness point for code review.
- **O-R4. For the habit-logic record.** Its `4e860ff` security O1 says `yearMonths` "throws `TypeError` at once for `10000-01-05` and returns 11 months for `99999-12-31`". The October to December branch of 10000 to 10009 never returns (`probe_10_yearmonths.txt`). Its PASS stands, because the input breaks that module's contract (valid date keys) and the app is the caller, so the finding sits here. The habit-logic file is not mine to edit.
- **O-R5. Playwright's fake clock rethrows a timer's exception into `clock.run_for`.** A test that drives a rollover into a failing redraw sees a Playwright error, not a page error (`probe_11_run1_note.txt`). For the QA lane.
- **Carried from `4e860ff`.** O1 (a popup reopened before its close event ran) still fails safe, 28 of 28 deletes matched M1's title and 11 of 11 ticks matched P1 (`probe_06_close_race.txt`). O3 (T8 on a phone), O4 (local paths in the repository) and O5 (CSP hardening left out by the owner's ruling) are untouched by the delta and were not measured again.

## Not audited

- The showcase hub (trust boundary 5, T10), Firefox, real iPhone Safari, GitHub Pages headers, screen reader output, as at `4e860ff`.
- The credential gate (`credential_sweep.py`) was refused by the permission classifier and is NOT RUN here. It is the orchestrator's gate. `probe_00_static.txt` section 8 holds this finder's own scan (no secret pattern in the shipped files, no credential-shaped file name in the project).

## Processes and lapses

PROCESSES: none alive. Every probe ran in the foreground under `timeout`, started its own `python -m http.server` on a free 127.0.0.1 port from the project root and stopped it by PID in a `finally` with the port checked refused, and closed its headless browsers in `finally`. The full table of server PIDs and ports, the hung renderer (19808, closed with its browser) and the closing sweep at 19:59:18 by name, parent, creation time, command line and loopback port (shells included, only the sweep's own bash found) are in `processes.txt` of the evidence folder.

Lapses. One command at 19:28 used `2>&1` (`ls` of the evidence path before the run), it wrote no file. Two probe runs were instrument faults and are kept as records (`probe_11_run1_note.txt`, `probe_13_run1.txt`). The times first written into the headers of the `probe_10` to `probe_12` captures were wrong by several minutes and were corrected in place, in this run, to the times the save stamps support. `git status` shows no change under `src/`, `tests/`, `index.html` or `docs/design/` from this run. My only writes are this file and the evidence folder.

## Solver pass 2026-10-15 (habit-logic task 9a)
Written by the dev solver (solver role). The finder's text above is unchanged. Detail in `docs/modules/habit-logic/BUILD.md`, section "v1.1.0 task 9a, the bound on `yearMonths`". Folders below are under `docs/modules/habit-logic/qa/`.

| Finding | Verdict | Commit | RED | Green |
|---|---|---|---|---|
| SEC-R01 | RESOLVED by the bound the owner ruled (ledger H-06, option 1). `yearMonths` stops after 13 months, so it ends for every key, and its result for a valid key is unchanged. The rest of SEC-05 is the re-accepted residual and was not touched | `eafc9e5` | `red-first/20261015-223234-task9a-node/`, the six far rows and the 920-key row "did not end" (heap limit or timer), the valid-key rows green in the same run | `solver/20261015-224014-node/`, 151 of 151. The finder's `probe_11` (group `hang`) and `probe_14` on `40848ce`, `solver/20261015-224907-probes-chromium/` and `solver/20261015-225045-probes-webkit/`. At 10000-10-15 both presses return and the page answers, and at the midnight into 10000-10-01 with P4 open the page answers, in both engines |

## Re-check 2026-10-15, task 9a

> Written by the security finder (read-only), 2026-10-15, 23:13 to 23:44, against HEAD `c00bc8c` (then `23cd4cf`, records only). `git diff 40848ce HEAD -- src tests index.html` is empty, so every run measured the tree of `40848ce`. Scope is `git diff a6f7e18 40848ce -- src tests` (`eafc9e5` the bound in `yearMonths` and its `@R20` worker test, `40848ce` a comment in `src/view.js`), SEC-R01, and the SEC-05 text of the app spec's Threat model (`docs/modules/app/spec.md:547` to `:550`, unchanged since `b3183c0`). Engines Chromium 149.0.7827.55 and WebKit 26.5, headless, the suite's clipboard stand-in first in every context, the clock set only with Playwright's clock API. Evidence is `docs/modules/app/qa/regression-security/20261015-233254/` (`evidence.md` first). The text above this section is unchanged. This file was rewritten whole with the Write tool, because no Edit tool was available, and `git diff` shows only these lines added. Line numbers are as of `40848ce`.

### Verdict

**SEC-R01 CLOSED. 0 CRITICAL, 0 HIGH, 0 MEDIUM, 0 LOW, 3 INFO.** The three INFO items are about how the accepted residual is written down, not about the code.

- **SEC-R01 is closed in both engines.** At nine October to December days of 10000 to 10009 (10000-10-01, 10000-10-15, 10000-11-30, 10000-12-31, 10003-11-15, 10005-11-20, 10007-12-01, 10009-10-01, 10009-12-31) the row's Year and the band's Year (twice) returned in 0.02 to 0.07 s in Chromium and 0.12 to 0.17 s in WebKit, and P3's Year at 390 px in 0.26 to 0.38 s. Every read of the page after each press answered (`rs9a_views_chromium.txt`, `rs9a_views_webkit.txt`). With no press, the midnight into 10000-10-01 with P4 open (the old freeze path), into 10000-11-01 with P2 or P4 open and into 10009-10-01 with P4 open all answered within 0.01 s (`rs9a_rollover.txt`). The first audit's `probe_11` group `hang` and `probe_14`, run unchanged, now answer where they froze (`probe_11_hang_and_probe_14.txt`, control `../20261015-192841/`).
- **Memory stays flat.** At 10000-10-15 the renderer's working set went 94 to 129 MiB in Chromium and 82 to 100 MiB in WebKit across both year views, then held or fell from 1 s to 12 s, close to the 9999-10-15 control. After 40 opens it stood at 164 and 115 MiB (control 155 and 138). The old freeze grew 107 to 1,301 MiB in 12 s (`rs9a_memory.txt`).
- **The bound ends the walk for every clock a browser can give.** In Node, 616,624 keys written as `localDateKey` writes them (every day of 10000 to 10200, 99990 to 100010 and 275750 to 275760, and two days of every year up to 275760) all ended. 930 returned 13 months, 108,482 returned 11, 507,212 threw the `TypeError`, none returned more than 13, and the slowest call took 11.63 ms. For valid keys the result is unchanged, 157,608 keys against `a6f7e18` with 0 differences. The unit suite is 151 of 151 and the 14 `@R20` bound rows pass (`rs9a_node.txt`).
- **Integrity held.** At every far clock driven, Done today, every open bead in P2, and P4's day with P1's tick left the stored text byte for byte as it was, in both engines. Not one open control at a far clock carried a key that passes `isDateKey` (`openKeysPassingIsDateKey` 0 in every row). The 9999-10-15 control saved all three.
- **No new threat from the change.** The bound is a constant counter in a pure function (`YEAR_VIEW_MONTHS`, `src/habits.js:32`, used at `:235`). It reads no input, adds no I/O, export or import, and changes no result for a valid key. The worker test lives in `tests/habits.test.js`, which is not in the publish copy (`index.html` and `src/` only). Its worker source is a fixed string literal, its `workerData` is the module's own file URL and keys the test builds, and the 256 MB heap cap and 5 s timer with `terminate` make a regression fail its row instead of hanging the runner. Nothing from outside the test reaches it. The `src/view.js` change is a doc comment only.

### What P2 and P4 show, measured against the SEC-05 text

Both engines gave the same months, counts and storage results at every date. P2 and P4 held the same months at each date.

| Clock | P2 and P4 | Ticks and Done today | SEC-05 text | Same as the text |
|---|---|---|---|---|
| 10000-10-15 (also 10000-10-01, 10000-11-30, 10000-12-31, and 390 px) | Open. 13 months, "January 10000" with one day (key `10000-1-01`, one open control, named "Sat 1 Jan 10000"), then December 9999 back to January 9999 with all 365 days drawn as locked cells after today, 0 blank | Nothing saved | `:550` says a year view at those clocks "opens on months that are not a calendar" and "the tab no longer freezes", and calls this "a prediction here and not a measurement" | The words fit, the form is not written down. RS-9A-1 |
| 10003-11-15, 10005-11-20, 10007-12-01, 10009-10-01, 10009-12-31 | Open. 13 months, one-day Januaries of each five digit year down to 10000 (4, 6, 8, 10, 10 of them), then the newest 9 to 3 months of 9999, every day locked (275, 214, 153, 92, 92 cells) | Nothing saved | As above | As above. RS-9A-1 |
| 10000-01-05, 10000-05-20, 10000-09-30, 10010-03-10, 100000-10-15, 100000-03-03 | The first press of the row's Year and of the band's Year throws the `TypeError` and opens nothing. A second press of the band's Year opens P4 with 0 months and 0 controls | Nothing saved | `:547` and `:548` say P2 and P4 "do not open, each throws a page error", for January to September of every year from 10000 on and every six digit year, and that Done today does nothing | Yes for the first press. The second press opens an empty P4. RS-9A-2 |
| 10010-10-15, 10010-12-31, 10123-11-11, and 10010-10-15 at 390 px | Open. 11 months of one day each, January of the year back to January ten years earlier. 10 are open controls whose keys fail `isDateKey`, the oldest is a blank cell | Nothing saved | `:548` says from October of the year 10010 on "P2 and P4 open with 11 one-day months whose keys fail `isDateKey`, and `toggleDay` refuses every tick there" | Yes |

### INFO

#### RS-9A-1. The SEC-05 line still carries the prediction, and the October to December form of 10000 to 10009 is a third form the accepted text does not describe
- **Threat.** None to data or to the tab. The written residual is incomplete, so a reader of the spec cannot tell what the year views show at those clocks.
- **Symbol.** `yearMonths` (`src/habits.js:229`, the bound at `:235`) through `layOutMonths` (`src/calendar.js:267`). `dayKind` (`src/habits.js:208`) compares keys as text, so every day of 9999 sorts after a five digit today and is drawn as a closed cell.
- **What I saw.** In both engines and at 1280 and 390 px, P2 and P4 open on 13 months. The newest 1 to 10 are one-day "January" months of the five digit years (keys like `10005-1-01`, each an open control whose tick is refused), and the rest are real months of 9999 whose every day, all in the past, is drawn as a locked day after today. `docs/modules/app/spec.md:550` still says "What the browser shows after the bound is a prediction here and not a measurement", and the line above it (`:548`) names only the January to September throw and the 11 one-day months from October 10010.
- **Capture.** `rs9a_views_chromium.txt`, `rs9a_views_webkit.txt`, `rs9a_rollover.txt`.
- **Fix direction.** The planner replaces the prediction with the measured form in a dated note. No code change. The owner's acceptance of "months that are not a calendar" already covers it.

#### RS-9A-2. At January to September clocks a second press of the band's Year opens an empty P4, where the SEC-05 text says P4 does not open
- **Threat.** None. Nothing is saved, and the empty P4 closes normally.
- **Symbol.** `drawAllHabitsYear` (`src/calendar.js:186`) records the day at `:188` before `layOutMonths` runs. After the first press throws, the second press skips the layout and opens P4 with nothing in it. `drawHabitYear` records its day after the layout (`:310`), so P2 stays shut on a second press (`rs9a_rollover.txt`, "P2 open (two presses)").
- **What I saw.** At 10000-01-05, 10000-05-20, 10000-09-30, 10010-03-10, 100000-10-15 and 100000-03-03, in both engines, P4 opened on the second press with 0 months and 0 controls. This is O-R3 of the first audit and the bound did not cause it. After the bound, this empty P4 is also where the midnight into 1 October now redraws a 13-month P4 instead of freezing. `docs/modules/app/spec.md:547` and `:548` say P2 and P4 "do not open".
- **Capture.** `rs9a_views_chromium.txt`, `rs9a_views_webkit.txt` (the "second time" rows of the January to September and six digit cases), `rs9a_rollover.txt` (the "before midnight" rows).
- **Fix direction.** The planner adds the second press to the SEC-05 line, or code review rules O-R3. No acceptance change is needed.

#### RS-9A-3. The README's Known limits row still says the year views freeze
- **Threat.** None. The public copy describes a failure that no longer happens.
- **Symbol.** `README.md:112`.
- **What I saw.** The row says "From October to December of those years, opening a year view freezes the tab, open with the owner (ledger H-06)", and that "the year views and the overview popup fail to open". On `40848ce` no year view freezes, the year views open from October to December of every five digit year driven, and the overview popup (P3) opened at every far clock driven at 390 px (10000-10-15, 10005-11-20 and 10010-10-15 here, 10000-01-05 in the first audit's `probe_11_*_basic_phone.txt`).
- **Capture.** `rs9a_views_chromium.txt`, `rs9a_views_webkit.txt` (the phone rows), `rs9a_memory.txt`.
- **Fix direction.** The orchestrator rewrites the row from the spec's SEC-05 text once RS-9A-1 and RS-9A-2 are settled (CS-01, RM-01).

### Observations (not filed)

- **RS-9A-O1. A midnight into a January with P4 open leaves P4 on the day before's layout.** From 10000-12-31 into 10001-01-01, and in the 9999-12-31 control into 10000-01-01, the header showed the new day and P4 kept the old months, in both engines, with nothing saved. The redraw throws in `yearMonths`, and Playwright's installed clock did not report it as a page error (O-R5). Same family as O-R2, not changed by the bound (`rs9a_rollover.txt`).
- **RS-9A-O2. From reading the code, not driven.** `toggleDay` checks its range as text (`src/habits.js:126`), so at a clock of 10000-10-15 a valid key of the year 1000 (for example `1000-05-05`) sorts between `yearStart` (`09990-10-15`) and today and would be accepted. No control offers such a key at any far clock driven (0 open keys pass `isDateKey`), so only an edit of the page's own DOM could reach it, and the saved key would still be readable. Noted for the habit-logic record.
- **The band at the far October to December clocks** held 81 to 84 day buttons. That is O-R1's family and was not measured further.

### Processes and lapses

PROCESSES: none alive. Thirteen `python -m http.server` runs on 127.0.0.1, each stopped by PID in a `finally` with its port refused, every headless browser closed in a `finally`, and a closing sweep at 23:43:36 that found only the session's own memory hook. The table is `processes.txt` of the evidence folder.

Lapses. Run 1 of the memory probe counted unrelated processes through a reused parent PID and is kept as a record, not used (`rs9a_memory_run1_note.txt`). The memory probe only read the process table. The two view captures are kept here in a compact form derived by `compact_views.py`, with the raw stdout's sha256, because the raw files are 86 KB each. The trial run of the view probe on two dates kept no stdout. One shell group ran the Node sweep in the background and printed its output from the project root, where the files were not, so it printed nothing. The files had been written to the scratch folder as meant, and `git status` showed no file added in the project. My only writes are this section and the evidence folder.
