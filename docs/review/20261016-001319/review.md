# Stakeholder review, Danial's Streaky Habit v1.1.0

**Role.** Stakeholder reviewer (agent), `sdlc:review`. This is an agent's verdict. UAT is the owner's, and only he seals the version.
**When.** 2026-10-16, 00:13 to 00:22 local (UTC+8). **Code.** HEAD `18a4227`, the code `sdlc:regression --full` passed at 2026-10-15 23:58 (`docs/regression/REGRESSION.md`).
**Direction.** Personal, so the compliance audit is skipped.

## Verdict

**Shippable to UAT.** Every capability the v1.1.0 brainstorm delta promised works on a cold boot with no seed, in Chromium 149 and in WebKit 26.5 (the engine of Safari on iPhone), at 390 x 844 with taps and at 1280 x 800 with clicks and keys. 264 checks pass, 0 fail, 10 are recorded as information. The first visit equals its golden to the pixel in both engines.

One new item needs the owner's eye on his iPhone, and it does not block UAT. In WebKit every popup opened by a tap or a click draws the white keyboard focus ring on the control the app focuses (the first habit in the day editor, Close in the three sheets, Cancel in the delete dialog). The goldens draw no ring and Chromium draws none. No gate looks at WebKit's rendering, and no record names it. Deviation D1 below.

## How it was driven

- Served from the project root by `python -m http.server <free port> --bind 127.0.0.1`, started and stopped by the drive script itself, one server per engine run, each stopped by PID with its port checked refusing.
- Every context fresh, empty `localStorage`, the real device clock (Friday 16 October 2026), headless. A clipboard stand-in loaded before any page in every context, so the system clipboard was never reached and no copy happened.
- Real gestures only. Taps on a touch phone at 390 x 844, mouse clicks and the keyboard at 1280 x 800. A person's pace between layers (650 ms), since the page guard holds page taps for 500 ms after a tap in a popup.
- Two checks pin the clock and say so. The midnight rollover (23:59:30, then 70 seconds) and the look compare against the goldens (10 October 2026 09:00, the goldens' own day).
- Storage failure was made only inside a throwaway test context, by filling that context's quota and by a context whose storage access throws from boot.
- The script is `review_v110.py` in this folder. Results per check are in `results-chromium.json` and `results-webkit.json`, the printed runs in `run-log-chromium.txt` and `run-log-webkit.txt`, the focus probe in `focus-visible-probe.json`.

## What was driven, per capability

Counts are per engine and equal in both.

| Brainstorm capability | What was done with real gestures | Checks | Result | Captures (`<engine>-` prefix) |
|---|---|---|---|---|
| C1 Add (rules unchanged) | Empty name, a name with spaces, Enter and Add, a duplicate in another case, 41 characters, typing clears the message, twelve habits | 10 | PASS | `390x844-02-name-error`, `390x844-12-twelve`, `1280x800-06-twelve` |
| C2 Tick today and any past day | Done today, yesterday from the overview popup and from the band, a day in the oldest week of the overview, the oldest open day (16 October 2025) from the year of all habits, five beads 200 days back in a habit's year view, no control before the reach or after today | 45 | PASS | `390x844-03` to `-09`, `1280x800-03` to `-05` |
| C3, C4 Current and Best | Labels on every row, in the day editor and in the year view, always equal. Unticking today keeps the run counted from yesterday. Best appears only above 0 | 7 | PASS | `390x844-10-three-habits`, `1280x800-02-three-habits` |
| C5 Overview | Band on the desktop (82 day buttons, the last 12 weeks, today marked), popup behind the Overview button on the phone, Year opens the last 12 months for every habit, 366 open days, 15 closed, 15 blank | in C2 | PASS | `390x844-03-overview-popup`, `-06-year-all-habits`, `1280x800-04-year-all-habits` |
| C6 Delete, time-free guard | A slow double press (800 ms apart) and a fast double press on a bin, with and without the bin lying under Delete habit, a slow second tap where the year view's Delete habit was, then a deliberate Delete habit that acted 27 to 35 ms after the dialog opened. Keyboard delete. Focus after each delete | 17 | PASS | `390x844-11-delete-over-year-view` |
| C7 Kept on the device | Reload, a closed tab opened again, a deleted habit added again starts with no history | 5 | PASS | |
| C8 Save warning | Quota full in a test context, the warning with the brainstorm's words, no dismiss, the change stays on screen, the app keeps working, the warning goes after the next save works, the reload shows the last working save. Storage refused from boot shows it from the first render | 10 | PASS | `390x844-01-save-warning`, `390x844-02-save-warning-at-boot` |
| Unreadable data (S5 restyled) | Broken saved text, the note, Dismiss, focus to the field | 2 | PASS | `390x844-03-unreadable-note` |
| C0 Look | First visit against `today-empty.html`, 0 pixels differ at 390 x 844 and 1280 x 800 in each engine, golden and app rendered by the same engine. Rows, band, sheets and dialog judged by eye against `today.html` | 2 | PASS, D1 below | `*-golden-today-empty`, `*-app-first-visit-pinned`, `*-golden-today` |
| Logo | Header mark equals the golden's, drawn in amber. `src/icon.svg` equals the golden's tab icon byte for byte (458 bytes), linked, loads under the CSP | 5 | PASS | `1280-logo-header`, `16-tab-icon-dark`, `16-tab-icon-light` |
| Name | Tab title "Danial's Streaky Habit", header "Streaky Habit" only, no name or initial in the mark | 2 | PASS, D2 below | |
| Midnight | With the year of all habits open, the header, Done today and the open sheet move to the new day | 3 | PASS | |
| Keyboard | First Tab on the desktop lands on the band's Year with the ring, Tab reaches a bin, Enter, Cancel focused, Tab, Enter deletes | 3 | PASS | |
| Nothing leaves the device | Every request a same-origin GET for the page's own files, no console error, no page error, no clipboard use, in all 8 app contexts per engine | 16 | PASS | |
| Rule 4, room under the day editor (H-03) | A day in the overview's oldest week and the oldest day of the year stay fully between the sheet's head and the day editor | 2 | PASS | `390x844-05-day-editor-oldest-week`, `-07-day-editor-over-p4` |

Information recorded (not pass or fail).
- At 390 x 844 with three habits no bin lies under Delete habit, so a slow second tap lands on the backdrop and closes the dialog (the backdrop is Cancel). At twelve habits, and at 1280 x 800 with three or twelve, a bin does lie under Delete habit and the second press is ignored with the dialog left open.
- A tap on Done today 40 ms (Chromium) and 113 ms (WebKit) after closing a sheet with a tap is dropped, and the same tap 650 ms later works. This is the page guard of spec R14, kept and extended by the owner (CG-11).

## The hard questions

**Every brainstorm capability delivered.** Yes. C0, C2, C3, C4, C5, C6, C8, the name and the logo, each as changed by the Round 1 and Round 2 rulings. The per-habit 7-day strip of the first delta row is gone by the owner's Round 1 ruling, not by a drop.

**Every R# working.** Every v1.1.0 requirement this drive touched works in both engines (app R3 to R6, R10 to R17, R19, R21 in part, R22 in part, R25, R29, R31 to R41, habit-logic R9, R17 to R20 through the views). The rest (sizes at 360 x 780, motion and reduced motion, names as text, no hooks, the ring geometry, the pixel gate) were not driven here and stand on the regression (Node 151, Chromium 358, WebKit 358 with one counted skip, fidelity 23 of 23 at 0 px in Chromium).

**Vision and quality held.** Yes. It reads as the F2 "Orbit List" the owner picked. Amber on near black, the rings, the list with Year and Done today, the composer pinned at the bottom of the phone, the page never scrolls. Each visit is still open, tap, close.

**Any spec silently dropped.** None found. Every user-facing string in `index.html` and `src/` is in the app spec's Copy table, and every Copy row shows where the spec says.

**Anything built that no spec or design asked for.** Nothing visible at the product level. Behaviour beyond the brainstorm's words exists, and each piece was ruled (table below).

**Any design not one-to-one.** In Chromium, no. In WebKit, D1.

## Deviations

| # | Where | What | Cause | Tag |
|---|---|---|---|---|
| D1 | Every popup opened by a tap or a click, in WebKit, at 390 x 844 and 1280 x 800 (P1 first tick, Close on P2, P3 and P4, Cancel on M1) | The app's first focus matches `:focus-visible`, so a 2 px white ring is drawn. The goldens draw none (qa.md checklist P1-17 "Focus not drawn") and Chromium draws none after a pointer. Opened by the keyboard both engines draw it, as designed. Measured in `focus-visible-probe.json`, seen in `webkit-390x844-focus-probe-m1-after-tap.png` and `webkit-390x844-08-year-view-open.png` | Neither an agent's code change nor the owner's mid-flight change. WebKit treats focus set by script as keyboard-like when the press focused nothing, and the app sets each popup's first focus by hand (rule 1, approved by the owner, spec R40). It went unseen because the pixel gate is Chromium only by the owner's ruling (ledger S5 row 2), and the engine table in qa.md does not name it. Not in the ledger | New, for the owner |
| D2 | `README.md` header | Still the 1.0 name "Streaks", the 1.0 lockup and the 1.0 captures, where the brainstorm delta says the READMEs use the full name | Orchestrator ruling (ledger S1 row 18), the header changes at the 1.1.0 seal from sealed captures, a note under the header says so | ORCH, reversible |
| D3 | Day editor over the overview or the year of all habits, on a phone | The sheet under the day editor gets bottom room and scrolls so the chosen day stays visible. No golden shows this state | The owner's ruling "Fix, give P3 room" and "Same fix for P4" (ledger H-03) | USER |
| D4 | Same, with nine or more habits | The day editor reaches its height cap and only part of the chosen day shows (about 5 px of a year-view day at 360 x 780 with twelve habits) | Orchestrator ruling, the day's top meets the sheet's head (ledger S1 rows 10 and 12) | ORCH, reversible |
| D5 | Same, in desktop windows narrower than 768 px | The room shows a thin scrollbar | Orchestrator, accepted residual (ledger S1 row 10 item 3) | ORCH, reversible |
| D6 | Same, at a Monday midnight with the day editor open | The redraw can move the chosen day under the day editor | Orchestrator, accepted residual for v1.1.0 (ledger S1 row 10 item 4) | ORCH, reversible |
| D7 | `src/styles.css` | Three marked changes from the golden CSS (native `::backdrop` for the golden's scrim, a fallback colour, reduced motion on the backdrop). No visible difference | Carried from 1.0, app spec R2 | ORCH |
| D8 | Device clock in the year 10000 and later | Year views show odd months or nothing, a second press of the band's Year can open an empty sheet. Nothing is saved, nothing is lost | The 1.0 residual SEC-05 re-accepted in its measured v1.1.0 form after the owner's bound (ledger H-06, S1 rows 29 to 32) | USER on the bound, ORCH on the residual |

Behaviour beyond the brainstorm's words, each ruled and working (not deviations).

| Where | What | Who ruled |
|---|---|---|
| Any popup | A tap on the page or on a popup beneath is dropped for 500 ms after a tap inside a popup | USER, CG-11 "Keep and extend it" |
| Delete dialog | A press inside the opener's box, or a second press of a double press, is ignored. The keyboard always acts | USER, CG-10 |
| The note after unreadable data | Dismiss with the field disabled at twelve habits sends focus to the page's first control | USER, H-05 |
| Year views | `yearMonths` stops after 13 months, so a far device clock cannot freeze the tab | USER, H-06 |
| A habit added | The list frame scrolls to show it | USER, CG-15 |

Known limits the owner already accepted, for the UAT script. No home-screen icon (DEFERRED, ledger off-scope row 7). Safari 26 shows the tab icon in one colour in both themes (S6 row 2, checked in UAT). Private browsing and Safari's 7-day clean-up lose data with no failure the page can see, the README says so (S4 row 2).

## Follow-ups

1. D1 to the owner in UAT on his iPhone. If he keeps it, add a row to qa.md's "Engine differences by design" and a ledger entry. If he wants no ring after a tap, that changes rule 1 or the focus style, so it goes to the design or plan phase, never a patch from here.
2. Ledger close for the orchestrator. The At a glance table still reads OPEN for S1 to S8 and no scope carries SHIPPED, and S8 row 1 still reads Open though H-01 ruled the name. Off-scope rows run 19, 23, 22, 21, 20, 24.
3. Staleness check, said out loud. The newest handoff (`docs/progress/handoff/handoff-2026-10-16-execute-orchestrator-7.md`, 2026-10-16 00:08) is newer than the ledger's newest entry (S1 row 33, 2026-10-15 23:58), so by the rule the ledger is stale until this review's close is written. The handoff is a pointer that names this review as in flight and holds no close of its own.
4. D2 at the 1.1.0 seal and publish prep, with off-scope row 20 (local paths in tracked files).
5. Items already deferred to the v1.2.0 plan stay there (CS-04, CS-07, CS-08, the RC-9A-1 wording "between 1 and 13 months").
6. A WebKit look check of the open states, for the owner to weigh at v1.2.0. The Chromium-only pixel gate was his ruling, and D1 is what it cannot see.

## Candidate UAT cases

iPhone first, since headless WebKit is the engine but not the device.

| # | Case | What correct looks like |
|---|---|---|
| U1 | iPhone. Tap Overview, a day, Year, a row's Year and a bin, one at a time | Each opens. Note whether a white ring shows on Close, the first habit or Cancel (D1). Keep it or ask for a change |
| U2 | iPhone. Tap the New habit field with a few habits listed | The keyboard opens and the field and Add stay visible above it. Headless runs cannot show the on-screen keyboard |
| U3 | iPhone. Overview, tap a day in the bottom week | The day editor rises and the chosen day stays visible above it, outlined |
| U4 | iPhone. Overview, Year, scroll to the bottom, tap the oldest day | The day editor opens on the same date last year, the day stays visible above it |
| U5 | iPhone. Double tap a bin quickly, then tap a bin, wait a second and tap the same spot | Nothing is deleted either time |
| U6 | iPhone. Tap a bin, then Delete habit straight away | The habit goes at once, no wait |
| U7 | iPhone. Close a sheet and tap Done today right away | The quick tap is dropped, a tap half a second later works. Does that feel right |
| U8 | iPhone. Settings, Safari, block all cookies, open the app, add a habit | The save warning shows. Turn cookies back on, tick something, the warning goes |
| U9 | iPhone. Private Browsing, add a habit, close the tab, open again | The habit is gone and no warning showed (known limit) |
| U10 | iPhone. Look at the tab icon in light and dark mode | Amber mark, one colour in both is Safari's known bug |
| U11 | Any device. Tick Done today, untick it, open yesterday and tick it | Current counts from yesterday when today is not done, Best never drops |
| U12 | Desktop. Band day, the band's Year, a row's Year | The day editor centred, the year of all habits, three months across in a habit's year |
| U13 | Any device. Leave the app open past midnight, or come back the next morning | The date, Done today and any open sheet move to the new day |

## Out-of-project artifacts

No out-of-project artifacts logged. `docs/progress/out-of-project-artifacts.md` does not exist.

## Process

- Servers, each a `python -m http.server` child of the drive script on a free 127.0.0.1 port. Chromium run PID 8740 port 55524, WebKit run PID 19712 port 18253, focus probe PID 1748 port 18426. Each stopped by PID, each port checked refusing (in the logs and `focus-visible-probe.json`). Three earlier trial runs into the session scratch folder (PIDs 3396, 19864, 23728) stopped the same way.
- Every wait bounded (5 s per action, a 540 s watchdog per run, `timeout` on each command).
- Process slip, disclosed. One edit of the scratch copy of the drive script was made with a Python one-off fed through a heredoc, in the scratch folder, nothing in the project.

## Files in this folder

`review.md`, `review_v110.py`, `results-chromium.json`, `results-webkit.json`, `run-log-chromium.txt`, `run-log-webkit.txt`, `focus-visible-probe.json`, and 64 captures. 30 per engine from the drive, named `<engine>-<size>-<step>.png`, and 4 from the focus probe (`chromium-390x844-focus-probe-m1-after-tap.png`, `webkit-390x844-focus-probe-m1-after-tap.png`, `chromium-1280x800-focus-probe-m1-after-click.png`, `webkit-1280x800-focus-probe-m1-after-click.png`).
