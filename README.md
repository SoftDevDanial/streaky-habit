# Streaks

Streaks is a daily habit tracker. Add up to 12 habits, tick the days you did them in this week's strip,
and see your current streak, your best streak and a 12-week heatmap. Everything stays in this browser.
There is no account, no server and no network call.

Built end to end with the sdlc pipeline. The run's state is in `docs/progress/STATE.md` and every decision,
finding and fix of this version is in `docs/v1.0.0/CHANGE-LEDGER.md`.

## Status, v1.0.0

| Module | What it is | State |
|---|---|---|
| `habit-logic` | dates, streaks, heatmap and name rules, pure functions, no DOM | closed 2026-10-09 |
| `app` | the page, saving, the delete dialog, the day rollover | gates green, closing |

- 176 browser tests and 99 unit tests pass.
- The page matches its three approved design screens to the pixel at 390 x 844 and 1280 x 800 (6 of 6 captures, 0 mismatched pixels), and 71 of 71 element checks pass.
- The cold-boot live gate passes 11 of 11 steps with real gestures on the shipped page.
- QA, code review and security reviews are done, with their findings fixed or accepted below.

## Run it

```
python -m http.server 8000 --bind 127.0.0.1
```

Run that from the project root, then open `http://127.0.0.1:8000/`. Stop the server when you are done.
Any static host works. There is no build step and nothing to install.

## Test it

| What | Command | Evidence |
|---|---|---|
| Unit tests | `node --test "tests/**/*.test.js"` | none |
| Browser tests | `python -m pytest tests/browser -q` | none unless `STREAKS_EVIDENCE_DIR` is set |
| Works right (live gate) | `python tests/browser/live_e2e.py --base-url http://127.0.0.1:<port>/ --out docs/modules/app/qa/live-e2e/<ts>/` | that folder |
| Looks right (fidelity gate) | the sdlc harness commands in `docs/modules/app/qa.md`, Fidelity gate | `docs/modules/app/qa/fidelity-<screen>-<viewport>/<ts>/` |

Node 24, Python with pytest and Playwright, headless Chromium. The browser tests start and stop their own
local servers. The live gate needs the app already served, so start a server first and stop it after.
A bare `node --test tests/` fails on Node 24, so keep the quoted glob. Every time-dependent test controls
the clock with Playwright's clock API, never with a hook in the app.

## How it is built

Vanilla JavaScript ES modules and plain CSS. Zero dependencies, no framework, no web fonts.

**`habit-logic`** (`src/dates.js`, `src/habits.js`) holds every rule about days and streaks. Days are local
calendar dates written `YYYY-MM-DD`.
- `localDateKey`, `addDays` and the other date helpers work on those keys.
- `weekWindow`, `toggleDay`, `currentStreak` and `bestStreak` drive the week strip and the streak line.
- `heatmapCells`, `heatLevel` and `monthLabels` build the 12-week heatmap.
- `validateName`, `addHabit` and `deleteHabit` keep the list valid, at most 12 habits with names up to 40 characters.

**`app`** (`index.html`, `src/app.js`, `src/view.js`, `src/storage.js`) is the page.
- `src/app.js` boots the page and handles every gesture. `readToday` is the only place the clock is read. `checkDay` rolls the page over to a new day every 30 seconds and when the tab is shown again.
- `src/view.js` owns every DOM lookup and write. Rows are rebuilt on add and delete and updated in place on a tick, so focus and the bead animations survive.
- `src/storage.js` saves and loads the list (`STORAGE_KEY`, `encodeState`, `decodeState`, `loadHabits`, `saveHabits`).
- The delete dialog is decided in its `close` event (`onDialogClose`). Two guards stop a double click or double tap from deleting through it. `guardDialogClick` keeps "Delete habit" inert for 500 ms after the dialog opens, and `swallowTapThrough` ignores page clicks for 500 ms after a press inside the dialog (`DIALOG_GUARD_MS`).
- The dialog title wraps the name in an isolate and leaves the name's text-direction control characters out of that copy (`TITLE_STRIPPED`), so a crafted name cannot reorder the question. The saved name is unchanged.

**The look.** `src/styles.css` is the approved design's stylesheet with three marked rule changes. No other
CSS is added.

## Saved data

One key, `streaks.state` in `localStorage`, holding `{ "version": 1, "habits": [...] }`. It is saved after
every add, tick and delete, and read once at boot.

`decodeState` treats the stored text as untrusted and accepts it only under the readable rule in
`docs/modules/app/spec.md` (Contracts). Anything else resets the list to empty and shows a short note
saying so. If storage is blocked or full, the page keeps working in memory without a message.

## Security

- Habit names reach the page only as text. `src/` contains no `innerHTML`, `eval` or similar, and the page adds nothing to `window`.
- The page carries a Content Security Policy.
  ```
  default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'
  ```
- Nothing leaves the device. Every test run checks that the only requests are same-origin GETs for the page's own files.
- **Publish only `index.html`, `src/` and a `.nojekyll` file.** Never serve the repository root. It holds build records, screenshots, local paths and deliberate mutant copies of `src/` used to prove the tests can fail.

## Behaviour worth knowing

- "Delete habit" does nothing for the first half second after the dialog opens.
- Right after a mouse or touch press in the dialog, a click on the page behind is ignored for half a second.
- Both come from the double-click guards above.

## Known limits in v1.0.0

Each was found during this version and accepted on purpose. The ledger has the reasoning.

| Limit | Planned |
|---|---|
| A slow double click (more than half a second between clicks) where the trash button and "Delete habit" overlap can still delete | fixed in v1.1.0 with a guard that does not depend on time |
| Another page on the same `github.io` origin can read the saved names | kept, no way to isolate it on that host |
| A name made of many combining marks draws over its neighbours | kept, cosmetic, only the user can type it |
| A device clock set to the year 10000 or later saves a day the app cannot read back | kept |
| Only Chromium is tested. Safari and Firefox are not verified | kept |

## Where the record lives

- `docs/v1.0.0/CHANGE-LEDGER.md` lists every scope, decision, finding and fix, dated, with who decided.
- `docs/modules/<module>/spec.md` and `qa.md` hold the requirements and the test contract.
- `docs/modules/<module>/findings/` holds each review's verdict (QA, code review, security, fidelity).
- `docs/modules/<module>/qa/` holds the evidence of every run.
- `docs/design/` holds the approved design screens. They do not change outside the design phase.
