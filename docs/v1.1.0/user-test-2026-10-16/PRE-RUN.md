---
version: 1.1.0
kind: uat-pre-run
sitting: 1 and 2 of 2
ran_against: running-app @ http://127.0.0.1:8741/
counts: { pass: 7, fail: 0, blocked_product: 0, blocked_script: 3, blocked_seat: 2 }
run: pre-run/20261016-0156/
rerun_2026-10-16: { run: pre-run/20261016-0217/, cases: 6, pass: 4, fail: 0, blocked_product: 0, blocked_script: 1, blocked_seat: 1 }
author: automated UAT pre-run agent (read-only)
---
# UAT pre-run, Danial's Streaky Habit 1.1.0

A green row here proves the script can be run. It is never proof that a feature works. The owner's own verdict sits beside each row in `TEST-CASES.md` and is the one that counts. Every disagreement between the two is a finding about this pre-run.

## Seats

| sitting | engine | seat | notes |
|---|---|---|---|
| 1 (UAT-01 to UAT-07) | headless Chromium 149.0.7827.55 | 1280 x 800, device scale 2, prefers-color-scheme dark | fresh context, real clock Fri 16 Oct 2026 from 01:56 (UTC+08:00) |
| 2 (UAT-08 to UAT-12) | headless WebKit 26.5 on Windows | Playwright's iPhone 13 context, 390 x 664 visible, device scale 3, touch, mobile | fresh context, real clock from 01:58 |
| 2, supplementary | the same WebKit | the same context at 390 x 844, the design's phone frame | fresh context, from 01:58 |

Every click and tap was hit-tested with `elementFromPoint` at the exact point before it was sent, and none missed. Paint (ring arcs, fills, outlines, threads, white rings) was read from a device-scale capture and checked by eye in the saved captures. A clipboard stand-in was loaded into every context before the page, and it recorded 0 writes. The app was not started, changed or reloaded by any hook. Nothing was set through a URL, the console or a DEV hook.

What WebKit on Windows can and cannot show. It is Safari's engine, so layout, focus rules (the white rings of A1), dialogs and the save warning behave as Safari's engine does. It is not an iPhone. It has no on-screen keyboard, no Safari interface (tab overview, address bar, Share menu), no iOS Settings, no swipe, and it refuses the mouse wheel in mobile mode. A tap's click reports pointerType "mouse", maxTouchPoints is 0, and the second tap of a quick double tap reports click count 1. Safari's visible height on the owner's phone is not known. It decides four lines (see UAT-08 and UAT-09).

Stand-ins, all declared in the case logs.
- UAT-07 and UAT-11. A test cookie, set and cleared from outside the page, switches on an init script that makes every `localStorage` access throw a SecurityError, as a blocked site does. It cannot show whether Chrome or Safari drop the saved data when the block is switched on.
- UAT-07. Headless Chromium did not turn F5 into a reload, so the page was reloaded with the browser's reload command. UAT-11 has no address bar, so it was reloaded the same way.
- UAT-09 step 6. No swipe and no wheel in mobile WebKit, so Tab then End (real keys) scrolled All habits to its end.
- UAT-05 step 3. prefers-color-scheme emulated as light stands in for the Windows switch, for the page line only.

## Verdicts

| case | title | tester verdict | observed | lines not matching or not drivable | evidence |
|------|-------|----------------|----------|------------------------------------|----------|
| UAT-01 | Open any past day and fix it, three ways | PASS | all 80 lines match, the starting state and the three adds included | none. Wording note on step 3 line 3, see Script defects | pre-run/20261016-0156/UAT-01/s01-day-editor-15.png, s07-bead17.png, s14-esc1.png, log.txt |
| UAT-02 | Each streak line names Current and Best | PASS | all 32 lines match | none | UAT-02/s05-bead14.png, s08-day-editor-16.png, log.txt |
| UAT-03 | The amber look, a list that scrolls in its box | PASS | all 48 lines match. The list scrolls inside its box, the field and the composer's bottom edge stay put, the band and the header never move | none | UAT-03/s05-day16-zoom.png, s07-twelve.png, s08-list-top.png, log.txt |
| UAT-04 | A double click on a bin never deletes | BLOCKED (script) | 26 of 27 lines match. Nothing was deleted by any double click or second click. Delete habit acted at once (483 ms after opening). The quick double-click of step 3 opened the dialog, then its second press landed on the dim page and closed it again. The dialog was on screen 131 ms | step 3 line 1. After the gesture no dialog is on screen, so its title cannot be read | UAT-04/s01a-after-first-click.png, s03a-120ms-after-double-click.png, s03b-after-double-click.png, s09b-deleted.png, log.txt |
| UAT-05 | The logo in the header and on the tab | BLOCKED (seat) | 3 of 13 lines drivable, all 3 match. The header mark is amber with no letter. Under a light preference the page stays dark | not drivable, step 0 line 1, steps 2 and 4 (the tab strip), step 3 line 1 (Windows), steps 5 to 7 (Firefox, none on this PC) | UAT-05/s01-mark-zoom.png, s03-page-under-light-preference.png, log.txt |
| UAT-06 | Full name on the tab, short name in the header | PASS | the header reads Streaky Habit with no Danial and the mark holds no initial | not drivable, step 1 (no tab hover card). The page title reads Danial's Streaky Habit, context only | UAT-06/s02-header.png, s02-mark-zoom.png, log.txt |
| UAT-07 | When the browser will not save, the app says so | PASS | 16 of 20 lines drivable, all 16 match. With the storage stand-in on, the warning shows between the band and the list, no close button, empty list, plain rings. Water added and ticked, the warning stays. With it lifted, eleven habits are back, Read 20 pages Current 2 days and Best 2, no Water, no warning | not drivable, steps 1, 2, 3 and 7 (Chrome's settings), stand-in used | UAT-07/s04-blocked-reload.png, s08-unblocked-reload.png, log.txt |
| UAT-08 | Every screen on the iPhone, the white ring | BLOCKED (script) | 67 of 69 drivable lines match at 390 x 664. The A1 white rings show round Close, the first habit and Cancel, as the sheet says. All 69 match at 390 x 844 | step 8 line 6, the bottom row shows only its top half. Step 8 line 9, the legend is below the screen edge. Not drivable, step 2 lines 1 and 2, step 6 lines 1 and 2 (no on-screen keyboard) | UAT-08/s08-overview.png, s09-day-editor-15.png, s17-delete-dialog.png, supplementary-390x844/UAT-08/s08-overview.png, log.txt |
| UAT-09 | A low day stays in sight above the day editor | BLOCKED (script) | 30 of 32 lines match at 390 x 664. 27 July and 16 October 2025 each show whole above the day editor. All 32 match at 390 x 844 | step 1 line 2, the bottom row shows 46 percent. Step 4 line 2, after Close the top row 12 to 16 October stays under the sheet's title area | UAT-09/s02-day-editor-27.png, s04-closed.png, supplementary-390x844/UAT-09/s04-closed.png, log.txt |
| UAT-10 | Double taps on a bin or Delete habit delete nothing | PASS | all 17 lines match. Nothing deleted by any double tap. Step 1's dialog opened at the first tap and was closed by the second tap on the dim page after 140 ms, as the case's own text allows. Delete habit acted at once | none. Note on step 1 line 1, see Script defects | UAT-10/s01-after-double-tap.png, s07-delete-dialog.png, s08-deleted.png, log.txt |
| UAT-11 | Block All Cookies, the app warns | PASS | 17 of 20 lines drivable, all 17 match. With the stand-in on, the warning shows under the date line, empty list, empty Overview ring. Water added and ticked. Lifted, both habits back, Read 20 pages 2 days and Best 2, no Water | not drivable, steps 1 and 6 (iOS Settings, stand-in used), step 4 (keyboard) | UAT-11/s02-blocked-reload.png, s07-unblocked-reload.png, log.txt |
| UAT-12 | The tab icon in Safari, the home screen | BLOCKED (seat) | nothing drivable | every line. Tab overview, Settings, Share menu and home screen are Safari and iOS interface | UAT-12/log.txt |

All evidence paths are under `docs/v1.1.0/user-test-2026-10-16/pre-run/20261016-0156/`, and they were listed on disk before they were cited. Totals, sitting 1 223 lines (207 match, 1 does not, 15 not drivable), sitting 2 at 664 153 lines (131 match, 4 do not, 18 not drivable), sitting 2 at 844 153 lines (135 match, 0 do not, 18 not drivable).

## Script defects

1. **UAT-04 step 3 line 1, expected result not observable as written.** The line reads "A dialog titled Delete "Habit 12"? opens". At 1280 x 800 the bin of the last row sits about 200 px below the dialog's Delete habit. So the second press of a quick double-click lands on the dim page, which closes the dialog like Cancel, and the dialog shows for about 130 ms. The owner will see at most a flash, then step 4's Esc does nothing. The same is expected at any window tall enough for the app (480 px or more), because the last row sits near the bottom and the dialog in the middle. Only 800 px was observed. Suggested words for step 3. "The dialog flashes open and closes again at once, because the second click lands on the dim page below it, which acts like Cancel. Nothing is deleted." Add step 3 to the Note's sentence about the dim page, and say that step 4's Esc then does nothing.
2. **UAT-08 step 8 lines 6 and 9, and UAT-09 step 1 line 2, expected result not observable without a scroll the script does not ask for.** The Last 12 weeks sheet needs about 724 px of screen to show whole (legend bottom at y 724). At 390 x 664 (an iPhone 13 in Safari with its toolbar shown) its body scrolls, by design. The bottom row 27 July to 2 August shows only its top half, and the legend is below the screen edge. At 390 x 844 both show. Suggested words. Add to UAT-08 step 8, "Scroll the sheet down until it stops" before the bottom-row and legend lines. In UAT-09 step 1 write "Its bottom row, at the foot of the sheet (scroll down if it is cut off), is 27 July to 2 August, labelled Jul". In UAT-09 step 2 write "Tap 27 in the bottom row, the part that shows is enough".
3. **UAT-09 step 4 line 2, expected result depends on screen height.** The line reads "The top row, 12 to 16 October, is in view again". At 390 x 664 the sheet keeps 27 July in view after Close (focus goes back to 27, and the sheet scrolls by design), so the top row sits under the sheet's title area and the first row in view is 5 October. At 390 x 844 the sheet does not scroll and the line holds. Suggested words. "The day editor goes down. 27 July is still in view. If your screen shows the whole grid, the top row 12 to 16 October shows too, else scroll up to see it."
4. **Minor wording, UAT-01 step 3 line 3, not blocking.** "with 1 in amber and "day" under it" can be read as "day" under the 1. On screen "day" sits beside the amber 1, on the line under "Current". UAT-02 step 1 words it clearly as 'Under "Current" it reads 1 in amber, then "day"'. Use that.
5. **Minor wording, UAT-10 step 1 line 1, not blocking.** In this seat the dialog showed 140 ms before the second tap on the dim page closed it, too short to read its title. The case's own text allows that. Suggested words. "The first tap opens a dialog titled Delete "Stretch 10 minutes"?. It may close again at once if the second tap lands on the dim page."
6. **Information for UAT-05, not a defect.** No Firefox was found at the standard install paths or in the Start menu of this PC, so steps 5 to 7 will likely take the case's own "no Firefox" cross.

## Product defects

None found. Every drivable line that did not match is explained by the script (above) or by the seat. Facts that are not defects. In WebKit the second tap of a double tap reports click count 1, so the delete guard there rests on the dim page or the opener's box, and in every double tap here the second tap landed on the dim page. After Esc on the desktop, the white keyboard focus ring shows on the control that opened the popup.

## Instrument history

Two dry runs per sitting went to the scratchpad before this run, to prove the instruments. They found harness faults only (a log key clash, the wheel refused in mobile WebKit, a thread sample too strict next to today's white ring). This run's captures are the only ones in `pre-run/20261016-0156/`.

## PROCESSES

| what | PID | why | state at return | kill command |
|---|---|---|---|---|
| python sitting 1 driver, its Playwright driver and headless Chromium | not kept (background task b52kewhwl) | the final sitting 1 run, bounded by timeout 300 s | STOPPED, exit 0 | none |
| python sitting 2 driver, its Playwright driver and headless WebKit at 390 x 664 | not kept (background task bkxknsn20) | the final sitting 2 run, bounded by timeout 300 s | STOPPED, exit 0 | none |
| python sitting 2 driver, its Playwright driver and headless WebKit at 390 x 844 | not kept (background task bs3t6z657) | the supplementary run, bounded by timeout 300 s | STOPPED, exit 0 | none |
| probes and dry runs (python, Chromium, WebKit) | not kept | instrument checks, foreground, each bounded by timeout 120 to 300 s | STOPPED, exit 0 | none |

Every wait was bounded. The runs were capped by `timeout 300`, wheels and End presses had iteration caps (40 and 4), and the completion wait looped at most 24 times.

Sweep at return (02:03:58). It ran `Get-CimInstance Win32_Process` filtered by name (python, pythonw, node, chrome, chrome-headless-shell, Playwright, WebKit processes, bash, sh, cmd, timeout) and by command line (streaks-uat, ms-playwright, sitting1, sitting2, probe), plus `netstat` on port 8741. It found
- PID 11048, `python -m http.server 8741 --bind 127.0.0.1`, the orchestrator's server, the only listener on 8741. Not touched.
- A chain started at 02:03:44 that this agent did not start. bash PIDs 12900, 11096 and 27860, then `node mutate_app.mjs chromium UC1 UC2 UC3 UC4 UC5 U4 E1 G1` PID 25828, then `python -m pytest tests/browser -q -p no:cacheprovider -k R62 --engine chromium -rA -s` PID 13912, with python 26824, node 25932 and chrome-headless-shell 24680 and 15900. Another lane's. Not touched.
- No process of this agent alive.

---

## Re-run 2026-10-16

Run at 02:17 on the repaired `TEST-CASES.md` (59422 bytes, saved 02:09), against the same app (`127.0.0.1:8741`, PID 11048). Only the changed cases were re-run, each from its own precondition, rebuilt by real gestures in a fresh context. Sitting 1 drove UAT-01 to UAT-05 in order. UAT-02 and UAT-03 were driven only to rebuild the state of UAT-04, so they have no new verdict. Sitting 2 drove UAT-08 to UAT-10 in order, once at 390 x 664 and once at 390 x 844. The seats, stand-ins and checks are the first run's, mapped to the repaired wording. Every click and tap was hit-tested and none missed. The clipboard stand-in recorded 0 writes. Evidence is in `pre-run/20261016-0217/`, with a run log at `pre-run/20261016-0217/log.txt`.

| case | what changed | tester verdict | observed | lines not matching or not drivable | evidence |
|------|--------------|----------------|----------|------------------------------------|----------|
| UAT-01 | step 3 line 3 reworded | PASS | all 80 lines match, the new line 3 included | none | pre-run/20261016-0217/UAT-01/s03-closed.png |
| UAT-04 | steps 3 and 4 reworded | PASS | all 28 lines match. The double-click's dialog flashed for 142.5 ms and closed (second press on the dim page), Esc then changed nothing, nothing deleted. Delete habit acted 481 ms after the bin click | none | UAT-04/s03a-120ms-after-double-click.png, s03b-after-double-click.png, s04-esc.png, s09b-deleted.png |
| UAT-05 | steps 5 and 7 Firefox only, new step 8 | BLOCKED (seat) | 3 of 13 lines drivable, all 3 match | not drivable, step 2, 3 line 1, 4, 5 and 7 (skipped, no Firefox), 6, 8 (tab strip and Windows) | UAT-05/s01-header.png, s03-page-under-light-preference.png |
| UAT-08 | new step 12, old 12 to 18 now 13 to 19 | BLOCKED (script) at 390 x 664, all drivable lines match at 390 x 844 | at 664, 68 of 69 drivable lines match. The new step 12 shows the bottom row labelled Jul and the legend after the scroll. At 844, all 69 match | at 664, step 8 line 6 (the Jul label is below the screen edge until step 12). Not drivable, step 2 lines 1 and 2, step 6 lines 1 and 2 (keyboard) | UAT-08/s08-overview.png, s12-scrolled.png, supplementary-390x844/UAT-08/s08-overview.png |
| UAT-09 | steps 1, 2 and 4 reworded | PASS at both sizes | all 33 lines match at 664 and at 844. At 664 step 1 used the scroll the line allows (Tab then End) and step 4 the scroll up it allows (Home) | none | UAT-09/s01b-scrolled.png, s02-day-editor-27.png, s04-closed.png, s04b-scrolled-up.png, supplementary-390x844/UAT-09/s04-closed.png |
| UAT-10 | step 1 line 1 reworded | PASS at both sizes | all 17 lines match at 664 and at 844. The dialog closed again after about 140 ms, as the new line allows | none | UAT-10/s01-after-double-tap.png, s08-deleted.png |

Totals, sitting 1 201 lines (191 match, 10 not drivable), sitting 2 at 664 123 lines (118 match, 1 does not, 4 not drivable), sitting 2 at 844 123 lines (119 match, 4 not drivable).

### Script defect still open after the repair

1. **UAT-08 step 8 line 6, height-dependent.** The line reads "Down the left, "Oct" twice, "Sep", "Aug" and "Jul" label five of the rows". At 390 x 664 the Jul label belongs to the bottom row, which sits below the screen edge until the new step 12 scroll, so only four labels show at step 8. At 390 x 844 all five show. Suggested words for step 8. 'Down the left, "Oct" twice, "Sep" and "Aug" label rows'. Step 12 line 1 already checks that the bottom row is labelled "Jul".

### Orchestrator probe P1 (H-08)

Not a UAT case. Headless Chromium 1280 x 800, one fresh context, real gestures. A LIVE stand-in replaced `window.localStorage` with a getter that checks a test cookie on every access. So clearing the cookie from the test side made the next access work in the open page, with no reload. It tests the app's own logic. It does not show whether Chrome or Safari themselves let an open page save again once a block is lifted. Each reload used the browser's reload command, because headless Chromium ignores F5.

| step | page | `streaks.state` |
|---|---|---|
| (a) three habits added, reload | Read 20 pages, Stretch 10 minutes, No phone after 11pm, no warning | the same three |
| (b) stand-in on, reload | "No habits yet.", save warning, page access throws SecurityError | the same three |
| (c) Water added | Water, warning | the same three (the save failed) |
| (d) stand-in off, no reload | Water, warning, page access readable | before (e), `{"version":1,"habits":[{"name":"Read 20 pages","done":[]},{"name":"Stretch 10 minutes","done":[]},{"name":"No phone after 11pm","done":[]}]}` |
| (e) Done today on Water | Water ticked, the warning went | `{"version":1,"habits":[{"name":"Water","done":["2026-10-16"]}]}` |
| (f) reload | Water only, no warning | after (f), `{"version":1,"habits":[{"name":"Water","done":["2026-10-16"]}]}` |

The three earlier habits did not survive. The first change after storage came back wrote the page's one-habit list over them, so H-08 is confirmed under this stand-in. Evidence is in `pre-run/20261016-0217/probe-P1-H08/` (a-after-reload.png, b-blocked-reload.png, c-water.png, e-water-done.png, f-after-reload.png, log.txt).

### PROCESSES (re-run)

| what | PID | why | state at return | kill command |
|---|---|---|---|---|
| re-run sitting 1 driver, Playwright driver, headless Chromium | not kept (background task bn658rbvj) | UAT-01 to UAT-05, timeout 280 s | STOPPED, exit 0 | none |
| re-run sitting 2 driver at 390 x 664, Playwright driver, headless WebKit | not kept (background task bcbh74u2s) | UAT-08 to UAT-10, timeout 280 s | STOPPED, exit 0 | none |
| re-run sitting 2 driver at 390 x 844, Playwright driver, headless WebKit | not kept (background task bmcty6h2m) | UAT-08 to UAT-10, timeout 280 s | STOPPED, exit 0 | none |
| probe P1 driver, Playwright driver, headless Chromium | not kept (background task bt3a7jjd0) | H-08 probe, timeout 150 s | STOPPED, exit 0 | none |
| dry runs of the three drivers | not kept | instrument checks into the scratchpad, foreground, timeout 120 to 240 s each | STOPPED, exit 0 | none |

Every wait was bounded. The runs were capped by `timeout`, the End presses by 4, and the completion wait looped at most 40 times (it ended after 8). Sweep at 02:19:27. It ran `Get-CimInstance Win32_Process` by name (python, pythonw, node, chrome, chrome-headless-shell, Playwright, WebKit processes, MiniBrowser) and by command line (rerun1.py, rerun2.py, probe_h08.py, sitting1.py, sitting2.py), plus `netstat` on 8741. It found only PID 11048, the orchestrator's server, which is the only listener on 8741 and was not touched. The other lane's chain from the first sweep had already ended. No process of this agent alive.
