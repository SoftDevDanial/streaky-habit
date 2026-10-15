# Repo summary: Streaks

Written at review on 2026-10-10, once the v1.0.0 build was approved for the owner's test.
Brought up to v1.1.0 at review on 2026-10-16 by the stakeholder reviewer (agent). Statements that changed are kept and labelled with the date, the v1.1.0 text sits beside them.

## What it is
~~A daily habit tracker on one web page. Add up to 12 habits, tick the last 7 days, see each habit's current and best
streak and one 12-week heatmap for all habits.~~ (v1.0.0 text, changed 2026-10-16 for v1.1.0, see the next paragraph.) Everything is saved in the browser's `localStorage`. No account,
no server, no network call, no dependencies, no build step.

**v1.1.0, Danial's Streaky Habit (added 2026-10-16).** The same tracker under a new name and an amber on near black look. Each habit is a row with a delete bin, a Year button and a Done today button, and shows its Current and Best streak with those words. Any day of the last 12 months can be ticked or unticked, from a habit's year view, from the overview (a 12-week band on a desktop, a popup behind an Overview button on a phone) or from the year of all habits, both of which open a day editor for every habit on that day. A double press can never delete a habit, and Delete habit acts at once. If the browser cannot save, a warning says so. The logo shows in the header and as the tab icon. Up to 12 habits, saved on the device only, as before.

## Where things are
| Path | What it holds |
|---|---|
| `index.html` | the page, with its Content Security Policy. Since v1.1.0 also the five popups and the tab icon link |
| `src/dates.js`, `src/habits.js` | `habit-logic`: every rule about days, streaks, ~~the heatmap~~ (v1.0.0, changed 2026-10-16) the overview, the editable year of the last 12 months, and names, as pure functions |
| `src/app.js` | boots the page, handles every gesture, reads the clock, rolls over at midnight |
| `src/view.js` | builds and updates the page's elements, owns every selector. Since v1.1.0 (2026-10-16) the main screen only, the header, band, banners, rows and composer |
| `src/calendar.js` | added in v1.1.0 (2026-10-16). Every ring and day grid, the band, the overview popup, both year views, the day editor's ring |
| `src/popups.js` | added in v1.1.0 (2026-10-16). Opening and closing the five popups, their parts, and the room under the day editor on a phone |
| `src/ring.js` | added in v1.1.0 (2026-10-16). The geometry of a ring segment and of the legend, pure |
| `src/icon.svg` | added in v1.1.0 (2026-10-16). The tab icon, amber on dark, dark amber on light |
| `src/storage.js` | saves and loads the list, treats stored text as untrusted. Since v1.1.0 (2026-10-16) a save reports whether it worked, for the save warning |
| `src/styles.css` | the approved design's stylesheet with three marked changes |
| `tests/` | ~~Node unit tests (99) and Python Playwright browser tests (179), plus the live gate script~~ (v1.0.0, changed 2026-10-16). Node unit tests (151) and Python Playwright browser tests (358, run in Chromium and in WebKit), plus the live gate script |
| `docs/brainstorm/`, `docs/design/` | what was asked for and the approved screens (immutable outside the design phase). Since v1.1.0 the v1.1.0 goldens, the 1.0 ones are in tag v1.0.0 |
| `docs/modules/<module>/` | each module's spec, test contract, build notes, findings and evidence |
| `docs/v1.0.0/CHANGE-LEDGER.md` | every scope, decision, finding and fix of this version, dated, with who decided |
| `docs/v1.1.0/CHANGE-LEDGER.md` | added 2026-10-16. The same record for v1.1.0, scopes S1 to S8 and the items that need the owner |
| `docs/regression/`, `docs/review/` | the last full re-check and the stakeholder review drive |
| `docs/brand/` | the logo, README badges and showcase image (still the 1.0 ones until the 1.1.0 seal) |
| `docs/progress/` | the run's state, its log and the process ledger |

## How to run and test it
Serve the folder (`python -m http.server 8000 --bind 127.0.0.1`) and open it. Unit tests `node --test "tests/**/*.test.js"`,
browser tests `python -m pytest tests/browser -q`. The README has the gates.
Added 2026-10-16. Browser tests in WebKit, Safari's engine, `python -m pytest tests/browser -q --engine webkit`. The live gate takes `--engine` too.

## What to know before changing it
- Dates are local calendar days, `YYYY-MM-DD`. `readToday` in `src/app.js` is the only place the clock is read.
- Time-dependent tests use Playwright's clock. Never add a test hook to the app.
- Only `index.html`, `src/` and a `.nojekyll` file are ever published.
- ~~The delete dialog's two 500 ms guards are deliberate (security SEC-01). v1.1.0 replaces the Delete habit one with a guard that does not depend on time.~~ (v1.0.0 text, changed 2026-10-16.) Since v1.1.0 Delete habit ignores a press inside the box of the control that opened the dialog and the second press of a double press, with no time window, and the keyboard always acts. The page guard stays, so for 500 ms after a tap or click inside a popup a tap on the layer beneath is dropped (owner's ruling CG-11).
- Added 2026-10-16. The pixel gate against the goldens runs in Chromium only. WebKit draws a focus ring on the control a popup focuses when it opens by a tap or click, which the goldens do not show (review 2026-10-16, deviation D1, for the owner's UAT).
- Added 2026-10-16. `yearMonths` in `src/habits.js` stops after 13 months, so a far device clock cannot freeze the tab (ledger H-06).
