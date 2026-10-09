# Module: app

> Build contract. Read by the Senior Frontend Dev agent. Build ONLY what is here.
> Stack: LOCKED to project stack (static page, vanilla JavaScript ES modules, plain CSS, `localStorage`, zero dependencies). Depends on: `habit-logic` (its Contracts only).
> Nature: FE, and the mandatory **live-composition module**: it owns the shipped entry point `index.html`, the composition root, storage, the clock and the midnight rollover, and it carries the **cold-boot live-e2e gate** for the whole system.
> Written by: the solutions architect (sdlc planner), 2026-10-08. Clarify-gate items that touch this module: CG-2 to CG-7 and CG-9, all ruled 2026-10-08, ORCH (the orchestrator under the owner's delegation, see `../ROADMAP.md`). CG-6 was ruled differently from the recommendation (a backdrop click acts as Cancel) and CG-2 was resolved in the plugin harness (the four state flags arrived in sdlc 2.1.0, 2.1.1 fixed the freeze so time is pinned through Playwright's clock, 2.1.2 added `bypass_csp`; minimum 2.1.1). Changed 2026-10-08 (plan-check flag, ORCH): this header first read "CG-2 was resolved in the plugin harness 2.1.1", which credited the four state flags to 2.1.1. They were added in 2.1.0. The version history and the 2.1.2 check are under Measurements in `../ROADMAP.md` and in the Fidelity gate of `qa.md`. The text below follows the rulings and marks each place with its CG number. CG-8's counting rule lives in `habit-logic`, and CG-1 is resolved.

## Sources
| Source | What it fixes here |
|---|---|
| `docs/brainstorm/brainstorm.md` | capabilities C1 to C7, key flows 1 to 4, every rule and copy string, non-goals |
| `docs/design/today.html` (S1, key screen), `today.md` | markup contract, copy, layout, the sample's values |
| `docs/design/today-empty.html` (S2), `today-empty.md` | first visit |
| `docs/design/delete-dialog.html` (M1), `delete-dialog.md` | the delete confirmation |
| `docs/design/states.html` (specimen sheet), `states.md` | S3 errors, S4 limit, a habit just added, S5 note, component states |
| `docs/design/system.md`, `system.css` | tokens, components, focus, motion, accessible names |
| `docs/design/RULINGS.md` | approved added copy, the five interaction rules, the browser floor |
| `docs/design/sample-history.json` | the data behind the goldens (tests only, never shipped) |

Phase skills: the plan phase has none assigned. This module is UI work, so its builder (and any solver fixing a UI or fidelity finding) loads the design row of `docs/phase-skills.md` (`taste-skill`, `frontend-design`) before writing UI, and declares in `BUILD.md` what it loaded and what changed. The goldens already apply those skills, so the build copies the goldens rather than re-deciding anything.

## Invariants & assumptions
- `index.html` at the project root is the only entry point and the composition root. It boots the real app on the real `localStorage` with whatever is saved there, or with nothing. There is no demo, seed, fixture, flag or query-string path.
- The goldens are the truth for markup, classes, copy and CSS. The app copies their component CSS and mirrors their DOM. `docs/design/` is read-only for everyone.
- The current day comes from the device clock in exactly one function, `readToday()` in `src/app.js`, which returns `localDateKey(new Date())`. Tests control time only with Playwright's `page.clock`.
- All state is one in-memory array of `Habit` (habit-logic Contracts) plus the shown `todayKey`. Every change goes through a habit-logic function, then a save, then a render.
- Every render runs synchronously inside the event handler that caused it. No `requestAnimationFrame`, `setTimeout`, `queueMicrotask` or promise deferral, so a test sees the result as soon as the event has been handled (and Playwright's paused clock cannot stall a render).
- Text that comes from data (habit names, dates, counts) reaches the DOM only through `textContent` and `setAttribute`.
- One tab at a time (CG-9, ruled 2026-10-08, ORCH, an accepted residual). Two open tabs do not see each other's changes and the last save wins.
- Browser floor (RULINGS): current Chrome, Edge, Safari and Firefox, at least Chrome 105, Safari 15.4, Firefox 121. Tests run on headless Chromium only (CLAUDE.md), so Safari and Firefox behaviour is not verified by this plan.
- The page is served as static files: GitHub Pages in production, `python -m http.server` in tests, possibly under a sub-path.
- GitHub Pages serves every project site of one user from a single origin (`<user>.github.io`), so other pages on that origin can read and write this app's `localStorage` key. Saved data is untrusted input.

## Requirements

### Entry point and stylesheet

- **R1.** `index.html` at the project root is the shipped entry point.
  - It starts `<!doctype html>` and `<html lang="en">`. Its head holds, in this order: `<meta charset="utf-8">`; the Content Security Policy `<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'">`; `<meta name="viewport" content="width=device-width, initial-scale=1">`; `<title>Streaks</title>`; `<link rel="stylesheet" href="src/styles.css">`; `<script type="module" src="src/app.js"></script>`. A comment in the head credits the icons as the goldens do: Phosphor Icons (MIT), "check" bold, "trash" regular and "x" regular, paths inlined.
  - Every URL in `index.html` and every `import` specifier in `src/` is relative (`src/...`, `./...`), never starting with `/` or a scheme, so the app works when served from a sub-path.
  - The body is the static skeleton in Contracts, with no habit data.

- **R2.** `src/styles.css` is the golden stylesheet: the text of the `<style>` element of `docs/design/today.html` from `:root {` through the `/* ---------- end components ---------- */` comment (the tokens, the two bead-size media queries and the component block, byte-identical in all four goldens, measured), with exactly these changes and no other added, removed or changed rule, selector, property or value:
  1. The `.scrim { ... }` rule is removed and the selector `.scrim, .dialog::backdrop` of the `scrim-in` animation rule becomes `.dialog::backdrop`. The golden draws its backdrop with a `.scrim` element because it has no script. The app draws it with the native `::backdrop` (delete-dialog.md, "Markup contract"), so the `.scrim` rule would be dead code.
  2. (CG-3) The backdrop colour reads `.dialog::backdrop { background: var(--scrim, rgb(28 37 35 / 0.5)); }`, the same colour as `--scrim`, so the scrim still shows in Chrome before 122 and Safari before 17.4, where `::backdrop` does not inherit custom properties.
  3. (CG-3) Inside `@media (prefers-reduced-motion: reduce)` the selector list becomes `*, *::before, *::after, ::backdrop`, so the backdrop also appears at once under reduced motion (system.md, Motion: "Under reduced motion both appear at once"). Measured: with the golden rule alone a native `::backdrop` keeps `scrim-in 0.18s` under reduced motion.
  The comparison ignores comments and whitespace.

### First visit, header and list

- **R3.** First visit (brainstorm flow 1; S2, today-empty.html). When the storage key is absent, the app renders S2: the list section holds `<p class="empty"><strong>No habits yet.</strong> Add one you want to do every day.</p>` (with the space after `</strong>`) and no `ul.habits`; the add form is enabled, empty and shows no message; the heatmap shows every cell up to today at level 0 named "<shortDate>, 0 of 0 habits", today's cell ringed, later days blank. No note shows. Nothing is written to storage until the first change.

- **R4.** Header (today.md; RULINGS). `h1.brand` reads "Streaks". `p.date > time` has `datetime` set to today's date key and the text `longDate(today)`, for example `datetime="2026-10-08"` and "Thursday 8 October". All copy stays English when the browser locale is not English (for example `de-DE`).

- **R5.** Habit list (brainstorm, Order; today.md markup contract). With one or more habits the list section holds `ul.habits` with one `li.habit` per habit, in stored order. Each row follows the habit-row markup in Contracts: `h3.habit-name` with `id="h<N>-name"` (N is the 1-based position) and the name as text; a trash `button.icon-btn` named `Delete <name>`; the streak line; the strip, whose `aria-labelledby` is the row's `h3` id.

- **R6.** Streak line (brainstorm C3, C4; system.md, Habit row). `p.streak[aria-live=polite]` holds `span.cur` and then, only when best is above 0, `span.best`:
  - current 1 shows `span.cur` "1 day"; current N of 2 or more shows "N days"; current 0 shows `span.cur.none` (classes `cur none`) "No streak yet";
  - best N of 1 or more shows `span.best` "Best N"; best 0 renders no `span.best` element at all.
  Values are `currentStreak` and `bestStreak` for today. Sample, today 8 Oct: Read "6 days" and "Best 14"; Stretch "3 days" and "Best 9"; No phone "1 day" and "Best 4". A habit just added: "No streak yet" and no best element. Current 0 with best above 0: "No streak yet" then "Best N" (for example the sample on Mon 12 Oct: Read "No streak yet", "Best 14").

- **R7.** Week strip (brainstorm, The week strip; system.md; RULINGS). `div.strip[role=group]` holds 7 `button.day` for `weekWindow(today)`, oldest first. Each has `type="button"`, `data-date` set to its key, `aria-pressed` "true" when done and "false" when not, `aria-label="Mark <shortDate> as done"` (the label never changes with the state, which lives only in `aria-pressed`), and inside it `span.wd` with `dayParts.weekday` and `span.dm` with `dayParts.day`. Only today's button has `aria-current="date"`. The strip has the boolean attribute `data-run-continues` exactly when `runContinues(done, today)` is true. No control exists for any day older than the window or after today.
  Sample, today 8 Oct, Fri 2 to Thu 8 (D done, . not): Read `. D D D D D D`; Stretch `D D . D D D .` with `data-run-continues`; No phone `. D . . D . D`.

- **R8.** Tick (brainstorm C2, flows 2 and 3). Activating a day button (click, tap, or Space or Enter while it has focus) toggles that day for that habit with `toggleDay`, then in the same handler:
  - the same button element, not a replacement, flips `aria-pressed`, so the bead's CSS transitions run and the button keeps focus;
  - the strip's `data-run-continues` is recomputed;
  - the habit's streak line shows the new current and best values;
  - the heatmap cell for that date changes its level class and its name in place;
  - the new state is saved (R16).
  Worked examples, sample, today 8 Oct:

  | Habit | Day | After | Streak line | Heat cell |
  |---|---|---|---|---|
  | Stretch 10 minutes | Thu 8 | pressed | 4 days, Best 9 | Thu 8 Oct, 3 of 3 habits, l4 |
  | Read 20 pages | Thu 8 | not pressed | 5 days, Best 14 | Thu 8 Oct, 1 of 3 habits, l1 |
  | No phone after 11pm | Wed 7 | pressed | 3 days, Best 4 | Wed 7 Oct, 3 of 3 habits, l4 |
  | Stretch 10 minutes | Sun 4 | pressed | 7 days, Best 9 | Sun 4 Oct, 2 of 3 habits, l2 |
  | Stretch 10 minutes | Fri 2 | not pressed, strip loses `data-run-continues` | 3 days, Best 9 | Fri 2 Oct, 0 of 3 habits, l0 |
  | Read 20 pages | Fri 2 | pressed, strip gains `data-run-continues` | 10 days, Best 14 | Fri 2 Oct, 2 of 3 habits, l2 |

- **R9.** Heatmap (brainstorm C5; system.md, Heatmap; today.md markup contract). `section.heat` holds `h2.heat-title` "Last 12 weeks"; `div.heat-grid` with `div.months[aria-hidden=true]` (one `span` per `monthLabels(today)` entry, text the month, inline style `grid-column: <column>`), the static `div.wdays`, and `div.cells` with the 84 `heatmapCells` in order; then the static `div.legend`. A cell that is not in the future is `span.hc.l<level>` with `data-date`, `role="img"` and `aria-label="<shortDate>, <count> of <total> habits"`; today's cell also has class `today` and `aria-current="date"`; a future cell is `span.hc.future` with `data-date` and `aria-hidden="true"` and no level class, role or name. The name always says "habits", also for "1 of 1 habits" (the formula as approved in system.md and RULINGS).
  Sample, today 8 Oct: cells Mon 20 Jul to Sun 11 Oct; the 81 levels equal `heatmapLevels`; names from "Mon 20 Jul, 3 of 3 habits" to "Thu 8 Oct, 2 of 3 habits"; Fri 9 to Sun 11 Oct future; months Jul 1, Aug 3, Sep 8, Oct 12.

### Add a habit

- **R10.** Add (brainstorm C1, flow 1, Order; states.md, "A habit just added"). Submitting the add form (Add pressed, or Enter in the field) with a name that `addHabit` accepts appends the habit at the bottom with 7 not-done beads (today ringed) and "No streak yet" with no best element; replaces `p.empty` with `ul.habits` when it is the first habit; empties the field; clears any message (the message is empty with classes `field-msg field-error` and the input has no `aria-invalid`); recounts the heatmap against the new number of habits; and saves. The app does not move focus after a successful add.
  Worked example, sample plus "  Drink water  " (stored and shown as "Drink water"): "Mon 20 Jul, 3 of 4 habits" l3; "Tue 6 Oct, 3 of 4 habits" l3; "Thu 8 Oct, 2 of 4 habits" l2; "Tue 21 Jul, 1 of 4 habits" l1; "Wed 12 Aug, 0 of 4 habits" l0.

- **R11.** Name errors (brainstorm, Habit name; RULINGS rule 3; states.md S3). Errors appear only when the form is submitted, never while typing. On a rejected name: the habit is not added; `#new-habit-msg` holds exactly one message and has the classes `field-msg field-error`; the input has `aria-invalid="true"`; the typed text stays in the field unchanged (not trimmed); the input has focus afterwards (states.md: "Focus stays in the input"), so after a click on Add the app moves focus to the input. Messages:
  - `empty`: "Name the habit first."
  - `too-long`: "Keep it to 40 characters or fewer."
  - `duplicate`: "You already track this habit."
  The message stays until the next submit, which replaces it with the next result's message or clears it on success.

- **R12.** Twelve habits (brainstorm; states.md S4). Whenever there are 12 habits (after an add, or at load), the input and the Add button carry the `disabled` attribute and `#new-habit-msg` holds "You track 12 habits, the most this app holds. Delete one to add another." with the classes `field-msg field-note`; the input keeps `aria-describedby="new-habit-msg"`. When the count drops below 12, both are enabled again and the message is empty with the classes `field-msg field-error`. After the 12th add the app does not move focus (CG-7 b); the note reaches screen readers through the message line's `aria-live="polite"`.

### Delete a habit

- **R13.** Open (brainstorm C6, flow 4, Delete; delete-dialog.md; RULINGS rules 1 and 2). Activating a habit's trash button opens the one `dialog.dialog` with `showModal()`. Its title `#del-title` reads `Delete "<name>"?` (straight double quotes, the stored name); its body `#del-body` reads "Its history is deleted too."; its buttons are "Cancel" then "Delete habit". Cancel has focus once the dialog is open. The page behind cannot be clicked or focused (native modal inertness) and does not scroll (`html:has(.dialog[open])`).

- **R14.** Keep (RULINGS rule 1; CG-6 ruled 2026-10-08, ORCH). Cancel, Esc, or a click on the backdrop (pressed and released outside the dialog box) closes the dialog, keeps the habit and its history unchanged, saves nothing, and puts focus on the trash button of the same habit (looked up after any re-render, for example a rollover while the dialog was open). A click inside the dialog box that hits no button, or a drag that starts inside the box and ends on the backdrop, leaves the dialog open.

- **R15.** Delete (brainstorm, Delete; RULINGS rule 1). "Delete habit" removes the habit and its whole history with `deleteHabit`, saves, closes the dialog, re-renders the list and recounts the heatmap against the remaining habits. Focus then moves to the trash button of the habit that was directly below the deleted one; when the deleted habit was the last one in the list (or the only one), focus moves to the "New habit" input. Deleting the only habit shows `p.empty` again. The deleted habit's days no longer count anywhere, and adding a habit with the same name later starts with no history.
  Worked examples, sample: delete "Read 20 pages" leaves 2 habits, focus on "Delete Stretch 10 minutes", "Mon 20 Jul, 2 of 2 habits" l4, "Tue 21 Jul, 1 of 2 habits" l2, "Thu 8 Oct, 1 of 2 habits" l2. Delete "No phone after 11pm": focus on the "New habit" input, "Thu 8 Oct, 1 of 2 habits" l2.

### Storage

- **R16.** Kept on the device (brainstorm C7, Storage). The state is saved under the `localStorage` key `streaks.state` as `encodeState(habits)` (Contracts), synchronously after every change (add, tick, delete) and at no other time except the reset in R17. A reload, or closing the tab and opening the page again in the same browser, shows the same habits in the same order with the same done days. Loading writes nothing (a saved value is left byte for byte as it was until the next change).

- **R17.** Unreadable saved data (brainstorm, Storage; states.md S5; RULINGS rule 4). When a saved value exists but `decodeState` reports it unreadable (the rule in Contracts, CG-4), the app starts with no habits, immediately saves the empty state `{"version":1,"habits":[]}`, and shows the note as the first child of `div.col-main`: `div.note[role=status]` holding `p.note-text` "Your saved habits could not be read, so the list was reset." and a `button.icon-btn[type=button]` named "Dismiss note" with the Phosphor "x" glyph. The empty message shows under it. Dismiss removes the note and changes nothing else; focus then moves to the "New habit" input when it is enabled (CG-7 a). The note does not come back on the next load (the saved value is now readable); it shows again only when a later load finds unreadable data. On desktop the note sits at the top of the left column, not across both columns.

- **R18.** Storage failures (CG-5, ruled 2026-10-08, ORCH, an accepted residual). If `localStorage` cannot be used at load (reading the property, or `getItem`, throws), the app starts empty with no note. If a save throws (for example `QuotaExceededError` or `SecurityError`), the change stays on screen and in memory, no message shows, and the app keeps working. No exception reaches the console in either case.

### Time

- **R19.** Rollover while visible (brainstorm, Rolling over midnight). While the page is open the app compares `readToday()` with the shown day every 30 seconds (so at most 60 seconds after local midnight). When the local date has changed, the same handler re-renders everything derived from today for the new day: the header date, every strip (new window, `aria-current`, `data-run-continues`), every streak line, and the heatmap (cells, today ring, future cells, months). The view never changes day before local midnight. The add form keeps its typed text, its message and its `aria-invalid` state. The element that had focus still has focus; a day button keeps focus at the same position in its strip, so focus on today's bead stays on the new today's bead.
  Worked example, sample, Thu 8 to Fri 9 Oct: header "Friday 9 October"; strips Sat 3 to Fri 9 with today Fri 9; Read `D D D D D D .`, "6 days", "Best 14", no `data-run-continues`; Stretch `D . D D D . .`, "No streak yet", "Best 9", with `data-run-continues`; No phone `D . . D . D .`, "1 day", "Best 4"; heatmap today "Fri 9 Oct, 0 of 3 habits" l0 ringed, "Thu 8 Oct, 2 of 3 habits" l2 without the ring, future Sat 10 and Sun 11 only.
  Second example, sample, Sun 11 to Mon 12 Oct: heatmap from Mon 27 Jul to Sun 18 Oct, months Jul 1, Aug 2, Sep 7, Oct 11, six future cells Tue 13 to Sun 18 Oct, today "Mon 12 Oct, 0 of 3 habits" l0 ringed; strips Tue 6 to Mon 12; all three streak lines "No streak yet" with "Best 14", "Best 9", "Best 4".

- **R20.** Rollover when shown again (brainstorm: "immediately when the tab is shown again"). When `visibilitychange` fires and `document.visibilityState` is "visible", the app runs the R19 check at once, synchronously in that handler, without waiting for the next 30 second check.

### Platform

- **R21.** Phone width (brainstorm, Platform; CLAUDE.md). At 360 x 780 the page has no horizontal scrolling (`document.documentElement.scrollWidth` at most 360), each day button is at least 44 px wide, each icon button is 44 x 44 px, the input and every button are 48 px tall, and beads are 32 px.

- **R22.** Keyboard (brainstorm, Platform). Every control can be reached and used with the keyboard. Tab order: the Dismiss button (when the note shows); then, for each habit in order, its trash button and its 7 day buttons oldest first; then the input; then Add. Space and Enter toggle a focused day button. Enter in the input submits. Focus rings show only on `:focus-visible` with the golden values: a 2px solid `--focus` (`rgb(28, 37, 35)`) outline, offset 0 on day buttons, -2px on icon buttons, 2px on the input, 3px on buttons. A mouse click draws no ring. While the dialog is open, Tab never reaches a control behind it.

- **R23.** Reduced motion (brainstorm, Platform; system.md, Motion). With `prefers-reduced-motion: reduce`, every element, pseudo-element and the dialog's backdrop has no transition and no animation, so state changes and the dialog appear at once. Without it, a bead's `transition-duration` is `0.18s, 0.18s, 0.12s` and the dialog's `animation-name` is `dialog-in` while it opens.

- **R24.** Names are text (threat model). A habit name is never interpreted as markup. A name such as `<img src=x onerror=alert(1)>` is stored and shown literally in the habit name, in the trash button's accessible name and in the dialog title; no element is created from it and no script runs. `src/` uses none of `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, `eval` or `new Function`.

- **R25.** Nothing leaves the device (brainstorm: "This one keeps everything on the device"; CLAUDE.md: no network calls). Through any use of the app the only requests the page makes are same-origin `GET` requests for the page itself (`/` or `/index.html`), `src/styles.css` and the `src/*.js` modules (plus `/favicon.ico` if the browser asks for it), with no query string. The R1 CSP is present and in force (a `fetch` from the page is refused). No console error and no uncaught page error occurs in any qa.md flow.

- **R26.** No seed, no hooks, no globals (constitution, cold-boot rule). The shipped files (`index.html` and everything in `src/`) contain no habit data: none of the names in `sample-history.json` and no reference to that file. No code path writes habits other than the user's add, tick and delete, and the R17 reset. Query strings and fragments have no effect: `/?demo=1`, `/?seed` and `/#sample` boot exactly like `/`. The app adds no property to `window` and exposes no test hook.

- **R27.** Cold-boot live-e2e gate (constitution, Definition of done). In a fresh headless Chromium context with empty storage and the real system clock, the app served from the project root by `python -m http.server <port> --bind 127.0.0.1` performs brainstorm flows 1 to 4 and survives a reload, driven only by real gestures (`click`, `keyboard.type`, `keyboard.press`), and writes an evidence artifact (screenshot sequence, step log, console log, network log) to `docs/modules/app/qa/live-e2e/<datetimestamp>/`. The exact steps are the `@R27` scenario in qa.md.

- **R28.** Looks right (constitution: 1-to-1 with the design). S1 (`today.html`), S2 (`today-empty.html`) and M1 (`delete-dialog.html`) render 1-to-1 with their goldens at 390 x 844 and 1280 x 800 under the Fidelity gate in qa.md, and every row of the FE element checklist, including each `states.html` specimen, matches.

## Contracts

### Files
| File | Owns |
|---|---|
| `index.html` | R1: head, CSP, icon sprite, static skeleton, dialog |
| `src/styles.css` | R2 |
| `src/app.js` | Composition root. Boot; `readToday()`; the state (habits array and shown `todayKey`); event handlers (tick, add submit, trash, dialog close, dismiss); the rollover interval and `visibilitychange` listener; focus rules. Calls `storage.js` and `view.js`. Exports nothing. |
| `src/view.js` | All DOM building and updating from state: header date, list or empty message, rows, strips, streak lines, heatmap, add-form message and disabled state, note. No storage, no clock, no event registration. |
| `src/storage.js` | The storage contract below. |
| `tests/browser/` | Browser tests (pytest with Playwright, run by the CLAUDE.md command `python -m pytest tests/browser -q`), their `conftest.py`, the two fidelity state scripts in `tests/browser/fidelity/` (fed to the plugin harness, CG-2) and the cold-boot gate script `live_e2e.py` (qa.md). Not shipped. |
| `tests/storage.test.js` | Node unit tests (`node --test "tests/**/*.test.js"`) of the pure exports of `src/storage.js` (`decodeState`, `encodeState`, `STORAGE_KEY`): the readable rule of the Storage contract and the rebuild of every habit. Not shipped. |

Changed 2026-10-09 (code-review WR-03, ORCH): the row for `tests/storage.test.js` is new. A browser test can see what `decodeState` keeps only through a later save, and cannot see whether it returned the parsed objects themselves (T2), so the pure exports get a unit test file. No other file or contract changes.

The split follows cohesion lines (composition and events, DOM, persistence), not speculative seams. There is no storage or clock abstraction: `localStorage` and `Date` are the only implementations the brief allows.

### Uses from habit-logic
`localDateKey`, `isDateKey`, `dayParts`, `shortDate`, `longDate` (from `src/dates.js`); `MAX_HABITS`, `weekWindow`, `currentStreak`, `bestStreak`, `runContinues`, `toggleDay`, `heatmapCells`, `monthLabels`, `validateName`, `addHabit`, `deleteHabit` (from `src/habits.js`). The app re-implements none of these rules.

### Storage contract (`src/storage.js`)
- Key: `streaks.state`.
- Value: compact JSON from `JSON.stringify`, for example `{"version":1,"habits":[{"name":"Read 20 pages","done":["2026-10-03","2026-10-04"]}]}`. `version` is the number 1. `habits` is in display order. Each habit has exactly `name` and `done`, with `done` ascending and without duplicates. A habit has the same shape as one in `sample-history.json`, so tests seed `{"version":1,"habits":<sample habits>}`.
- Exports:
  | Export | Signature | Behaviour |
  |---|---|---|
  | `STORAGE_KEY` | `"streaks.state"` | |
  | `decodeState` | `(raw: string \| null) => { status: "absent" } \| { status: "ok", habits: Habit[] } \| { status: "unreadable" }` | Pure. The readable rule below. |
  | `encodeState` | `(habits: Habit[]) => string` | Pure. `JSON.stringify({ version: 1, habits: habits.map(h => ({ name: h.name, done: h.done })) })`. |
  | `loadHabits` | `() => { habits: Habit[], reset: boolean }` | Reads the key inside `try`. Absent, or storage not usable: `{ habits: [], reset: false }`. Unreadable: saves `encodeState([])` (errors ignored) and returns `{ habits: [], reset: true }`. Readable: the decoded habits and `reset: false`. Never throws. |
  | `saveHabits` | `(habits: Habit[]) => void` | Writes `encodeState(habits)` inside `try`; ignores any exception (R18). |
- Readable rule (CG-4). `decodeState` returns `absent` when `raw` is `null`. It returns `ok` only when all of these hold, and `unreadable` otherwise:
  1. `raw` parses with `JSON.parse`;
  2. the result is a non-null object that is not an array, and its `version` is the number `1`;
  3. its `habits` is an array of 0 to 12 entries;
  4. each entry is a non-null object that is not an array, whose `name` is a string for which `validateName(name, <names of earlier entries>)` is ok and returns exactly `name` (so it is already trimmed, 1 to 40 code points, and unique ignoring case);
  5. each entry's `done` is an array whose every element satisfies `isDateKey`.
  On `ok`: each `done` is sorted ascending and de-duplicated; dates after today are kept (a clock or time-zone change can create them; they are never shown and do not count for the current streak); properties other than `version`, `habits`, `name` and `done` are ignored and disappear at the next save; the habits are new objects built as `{ name, done: [...] }`, never the parsed objects and never through `Object.assign` from them.

### Static skeleton (`index.html` body)
In this order, with the classes, ids and attributes of the goldens:
```html
<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">
  <symbol id="i-check" viewBox="0 0 256 256"><path d="..."/></symbol>
  <symbol id="i-trash" viewBox="0 0 256 256"><path d="..."/></symbol>
  <symbol id="i-x" viewBox="0 0 256 256"><path d="..."/></symbol>
</svg>
<div class="page">
  <header class="top">
    <h1 class="brand">Streaks</h1>
    <p class="date"><time></time></p>
  </header>
  <main class="layout">
    <div class="col-main">
      <section aria-labelledby="habits-title">
        <h2 id="habits-title" class="sr-only">Habits</h2>
      </section>
      <form class="add" novalidate>
        <label class="add-label" for="new-habit">New habit</label>
        <div class="add-row">
          <input class="input" id="new-habit" name="name" type="text" autocomplete="off" aria-describedby="new-habit-msg">
          <button class="btn btn-primary" type="submit">Add</button>
        </div>
        <p class="field-msg field-error" id="new-habit-msg" aria-live="polite"></p>
      </form>
    </div>
    <section class="heat" aria-labelledby="heat-title">
      <h2 class="heat-title" id="heat-title">Last 12 weeks</h2>
      <div class="heat-grid">
        <div class="months" aria-hidden="true"></div>
        <div class="wdays" aria-hidden="true"><span>Mon</span><span></span><span>Wed</span><span></span><span>Fri</span><span></span><span>Sun</span></div>
        <div class="cells"></div>
      </div>
      <div class="legend" aria-hidden="true">
        <span>None</span>
        <span class="hc l0"></span><span class="hc l1"></span><span class="hc l2"></span><span class="hc l3"></span><span class="hc l4"></span>
        <span>All</span>
      </div>
    </section>
  </main>
</div>
<dialog class="dialog" role="alertdialog" aria-modal="true" aria-labelledby="del-title" aria-describedby="del-body">
  <h2 class="dialog-title" id="del-title"></h2>
  <p class="dialog-body" id="del-body">Its history is deleted too.</p>
  <form class="dialog-actions" method="dialog">
    <button class="btn btn-secondary" type="submit" value="cancel">Cancel</button>
    <button class="btn btn-danger" type="submit" value="delete">Delete habit</button>
  </form>
</dialog>
```
- The three `path` values are copied exactly: `i-check` and `i-trash` from `today.html`, `i-x` from `states.html`. No other icon exists.
- The sprite's inline `style` attribute and the month labels' inline `grid-column` are allowed by the CSP's `style-src 'unsafe-inline'` (the goldens use both).
- The view fills: the `time` element; the list section after its `h2` (either `p.empty` or `ul.habits`); `div.months`; `div.cells`; the add form's message, `aria-invalid` and `disabled` states; the note, inserted as the first child of `div.col-main` when R17 applies. The dialog's title text is set before each `showModal()`.

### Rendered markup (`src/view.js`), mirroring today.md "Markup contract"
Habit row (whitespace between tags is free; elements, classes, ids, attributes and text are not):
```html
<li class="habit">
  <div class="habit-head">
    <h3 class="habit-name" id="h1-name">Read 20 pages</h3>
    <button class="icon-btn" type="button" aria-label="Delete Read 20 pages"><svg aria-hidden="true" focusable="false"><use href="#i-trash"/></svg></button>
  </div>
  <p class="streak" aria-live="polite"><span class="cur">6 days</span><span class="best">Best 14</span></p>
  <div class="strip" role="group" aria-labelledby="h1-name">
    <button class="day" type="button" data-date="2026-10-02" aria-pressed="false" aria-label="Mark Fri 2 Oct as done"><span class="day-label" aria-hidden="true"><span class="wd">Fri</span><span class="dm">2</span></span><span class="slot" aria-hidden="true"><span class="bead"><svg aria-hidden="true" focusable="false"><use href="#i-check"/></svg></span></span></button>
    <!-- six more day buttons; the last (today) also has aria-current="date" -->
  </div>
</li>
```
- No streak: `<span class="cur none">No streak yet</span>`, and no `span.best` when best is 0.
- The check `svg` is always present; CSS shows it when `aria-pressed="true"`.
- Empty list: `<p class="empty"><strong>No habits yet.</strong> Add one you want to do every day.</p>`.
- Heat cell, past or today: `<span class="hc l2" data-date="2026-10-07" role="img" aria-label="Wed 7 Oct, 2 of 3 habits"></span>`. Today adds class `today` after the level class and `aria-current="date"`: `<span class="hc l2 today" data-date="2026-10-08" role="img" aria-current="date" aria-label="Thu 8 Oct, 2 of 3 habits"></span>`. Future: `<span class="hc future" data-date="2026-10-09" aria-hidden="true"></span>`.
- Month label: `<span style="grid-column:3">Aug</span>` (set through `element.style.gridColumn` or the attribute).
- Note: `<div class="note" role="status"><p class="note-text">Your saved habits could not be read, so the list was reset.</p><button class="icon-btn" type="button" aria-label="Dismiss note"><svg aria-hidden="true" focusable="false"><use href="#i-x"/></svg></button></div>`.
- `svg` and `use` elements must be created in the SVG namespace with `document.createElementNS("http://www.w3.org/2000/svg", ...)`. An `svg` created with `document.createElement` is an HTML element and does not render. Changed 2026-10-08 (plan-check flag, ORCH): this note first also allowed `svg` elements "cloned from parsed markup such as a `<template>` in `index.html`". That option is removed. R1 fixes the head children and the Static skeleton fixes the body, so `index.html` carries no `<template>` or any other element beyond the skeleton, and `@R1` asserts that the body's element children are, in order, the sprite svg, `div.page` and `dialog.dialog`. Only `createElementNS` is allowed.
- Message line states: empty with classes `field-msg field-error` (as in the goldens); an error with `field-msg field-error`; the 12-habit note with `field-msg field-note`.

### Events and focus (`src/app.js`)
- Delegated `click` listeners on stable containers (the list section, `div.col-main`), a `submit` listener on `form.add` (calls `preventDefault()`), and a `close` listener on the dialog.
- The trash button and the `li` carry no index attribute; the habit index is the row's position in `ul.habits`. Day buttons are found by `data-date` within the row.
- Dialog: before every `showModal()` set `dialog.returnValue = ""` and the title text. On `close`, `returnValue === "delete"` deletes; anything else (Cancel, Esc, a backdrop click) keeps. The reset is required because `returnValue` persists between openings, so a later Esc would otherwise repeat the last "delete".
- Backdrop click (CG-6, ruled 2026-10-08, ORCH): a `pointerdown` listener and a `click` listener on the dialog. A click closes the dialog with `dialog.close("cancel")`, which then runs the same keep path as Cancel, only when the click's target is the dialog element itself, its `clientX`/`clientY` fall outside `dialog.getBoundingClientRect()`, and the matching `pointerdown` also landed outside that box. Clicks on `::backdrop` are dispatched to the dialog element, and so are clicks on the dialog's own padding, so the target check alone is not enough; the `pointerdown` check keeps a drag that starts on the title and ends on the backdrop from closing it. The native `closedby="any"` attribute is not used because Safari and Firefox versions inside the floor lack it.
- Focus targets: R8 (same day button), R11 (input), R14 (same habit's trash), R15 (next habit's trash, else the input), R17 (input after Dismiss), R19 (same element or same strip position).
- Rollover: `setInterval(checkDay, 30000)` started at boot, and `document.addEventListener("visibilitychange", ...)` that calls `checkDay` when `document.visibilityState === "visible"`. `checkDay` compares `readToday()` with the shown key and re-renders on a change.

### Copy (every user-facing string)
| Where | Text | Source |
|---|---|---|
| `title`, `h1.brand` | Streaks | goldens |
| header date | `longDate(today)`, e.g. Thursday 8 October | today.md, RULINGS |
| hidden list heading | Habits | RULINGS |
| empty list | **No habits yet.** Add one you want to do every day. | RULINGS |
| field label | New habit | RULINGS |
| submit button | Add | brainstorm flow 1 |
| errors | "Name the habit first.", "Keep it to 40 characters or fewer.", "You already track this habit." | brainstorm |
| 12-habit note | You track 12 habits, the most this app holds. Delete one to add another. | brainstorm |
| streak line | "1 day", "N days", "No streak yet", "Best N" | brainstorm |
| day button name | Mark <Ddd D Mon> as done | brainstorm, RULINGS |
| trash name | Delete <name> | RULINGS |
| heatmap heading | Last 12 weeks | RULINGS |
| axes | Jan to Dec short names from `monthLabels`; Mon, Wed, Fri, Sun | RULINGS |
| legend | "None", "All" | RULINGS |
| heat cell name | <Ddd D Mon>, <n> of <T> habits | brainstorm, RULINGS ("0 of 0 habits") |
| dialog | `Delete "<name>"?`, "Its history is deleted too.", "Cancel", "Delete habit" | brainstorm |
| S5 note | Your saved habits could not be read, so the list was reset. | brainstorm |
| dismiss name | Dismiss note | RULINGS |

No other user-facing string exists.

## Tasks
> Atomic, ordered, one commit each. Each commit carries the code and the browser tests that prove it (qa.md). Browser tests use pytest (the CLAUDE.md command) with Playwright's sync API and the fixtures in `tests/browser/conftest.py`. pytest-playwright is not installed and is not needed.
1. [x] `index.html` (head, CSP, icon credit comment, sprite, static skeleton, dialog) and `src/styles.css` (R2), plus `tests/browser/conftest.py` (fixtures and helpers listed in qa.md) and the static checks of `tests/browser/test_entry.py`. → R1, R2
2. [x] `src/storage.js`, `src/view.js` and `src/app.js` boot path: load, `readToday()`, render header, empty message or list, rows, streak lines, strips, heatmap, and the add form's 12-habit state at load; plus `tests/browser/test_render.py`. → R3, R4, R5, R6, R7, R9, R12, R16
3. [x] Tick in place with focus kept, streak line and heat cell update, save; plus `tests/browser/test_tick.py`. → R8, R16
4. [x] Add form: submit, `addHabit`, errors, message states, focus, 12-habit limit; plus `tests/browser/test_add.py`. → R10, R11, R12
5. [x] Delete dialog: open, Cancel, Esc and a backdrop click as Cancel, Delete habit, focus targets; plus `tests/browser/test_delete.py`. → R13, R14, R15
6. [x] Unreadable data note and dismiss, storage failures, reload persistence; plus `tests/browser/test_storage.py`. → R16, R17, R18
7. [x] Rollover: 30 second check and `visibilitychange`, full re-render with form and focus kept; plus `tests/browser/test_rollover.py`. → R19, R20
8. [x] Platform checks and anything they expose: `tests/browser/test_platform.py`. → R21, R22, R23, R24, R25, R26
9. [x] The fidelity state scripts for the plugin harness (CG-2, ruled 2026-10-08, ORCH): `tests/browser/fidelity/seed-sample.js` (candidate init script that seeds the sample) and `tests/browser/fidelity/open-delete-dialog.js` (candidate after-load script that opens the M1 dialog), plus `tests/browser/test_fidelity_inputs.py` proving both (qa.md, Fidelity gate). → R28
10. [x] `tests/browser/live_e2e.py`, the cold-boot live-e2e gate script (qa.md, `@R27`). → R27

## Threat model
> Feeds the security gate. A static page with no backend. The data is personal (habits can be sensitive, for example "No alcohol") and lives only in this browser.

**Assets.** The user's habit names and day history (privacy and integrity). The page's DOM and script context. The promise that nothing leaves the device.

**Trust boundaries.** (1) `localStorage` into the app: untrusted, because any page on the same origin (all of one user's GitHub Pages sites share `<user>.github.io`), a browser extension, or a manual edit can write it. (2) Typed habit names into the DOM. (3) The page out to the network, which must stay closed. (4) The static host serving the files.

| # | Threat | Required mitigation |
|---|---|---|
| T1 | Tampered or corrupt saved data crashes the app, breaks invariants, or smuggles values into code paths | `JSON.parse` inside `try`; the strict readable rule (Contracts); anything else resets with the S5 note (R17). Saved values are never used as HTML, selectors, property paths or code. |
| T2 | Prototype pollution through parsed keys such as `__proto__` | Decoded habits are rebuilt as literal `{ name, done }` objects; no `Object.assign`, no merging of parsed objects. Tested with a `__proto__` key (qa.md). |
| T3 | Script injection through a habit name (stored XSS, including a name planted in storage by another page on the origin) | Names reach the DOM only through `textContent` and `setAttribute`; `src/` has no `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, `eval` or `new Function` (R24). CSP `script-src 'self'` blocks inline scripts and inline event handlers as a second layer. |
| T4 | Selector injection | No CSS selector is built from a name. Rows are found by position, day buttons by `data-date`, whose values are validated date keys. |
| T5 | Data leaving the device (analytics, fetch, beacons, third-party assets, a native form submission putting the name in a URL if the script fails to load) | No network code and no third-party resources. CSP `default-src 'self'`, `connect-src 'none'` (blocks fetch, XHR, WebSocket, `sendBeacon`), `object-src 'none'`, `base-uri 'none'`, `form-action 'none'` (blocks a native GET submission of `name=`). The add form's submit is always `preventDefault()`ed. Measured 2026-10-08: `form-action 'none'` does not block the dialog's `method="dialog"` form, and `connect-src 'none'` refuses `fetch`. Verified by the request log (R25). |
| T6 | Storage blocked or full | Every storage call inside `try`; the app keeps working in memory (R18). Losing changes on reload in that case is an accepted residual (CG-5, ruled 2026-10-08, ORCH). Growth is small: at most 12 habits x 365 days x about 13 bytes, about 57 KB a year, against a quota of about 5 MB. |
| T7 | Accidental deletion | Focus opens on Cancel, so a stray Enter keeps the habit; Esc keeps it; a backdrop click keeps it (acts as Cancel, CG-6) (R13, R14). |
| T8 | A huge value planted in storage slows parsing | Bounded by the origin quota (about 5 MB); parsing and validation are linear; only the linear date-key pattern runs on it. Accepted. |
| T9 | Another app on the shared origin uses the same key | The key is specific (`streaks.state`). A foreign value there is unreadable and is reset with the note. Accepted residual. |
| T10 | Clickjacking by framing the page | A meta CSP cannot set `frame-ancestors` and GitHub Pages cannot send headers. Current browsers partition storage for third-party frames, so a framed copy sees an empty, separate store. Accepted residual. |
| T11 | Supply chain | Zero dependencies, no CDN, no web fonts. The three Phosphor paths (MIT) are inlined and credited in a comment. |
| T12 | Stale tab overwrites newer data (two tabs) | Not mitigated in v0.1.0. Accepted residual (CG-9, ruled 2026-10-08, ORCH). |

## Non-goals
> Explicit "do NOT build". Building any of these is a defect.
- From the brainstorm: reminders or notifications; accounts, login, sync between devices; weekly targets or any schedule other than daily; renaming or reordering habits; export or import; editing days older than the last 7; more than one tick per day, notes or amounts; stats beyond current streak, best streak and the heatmap; a theme switcher (one light theme only, no dark mode).
- From the design: no flip or count-up animation on the streak number (a "Suggestion, not designed" in DECISION.md and SELF-CRITIQUE.md); no motion other than the system.md Motion table; no icons other than check, trash and x; no shadow other than the dialog's.
- No undo after delete. No toast, banner or message other than the S3 errors, the S4 note and the S5 note.
- No interaction on heatmap cells (they are images with names, not buttons), no per-habit heatmap, no tooltips.
- No service worker, web app manifest, install prompt or offline cache. "Works offline" means it needs nothing beyond its own files.
- No migration code for other storage versions; only `version` 1 exists.
- No cross-tab sync (CG-9). No URL parameters or routes. No keyboard shortcuts beyond native button and form behaviour.
- No analytics, logging, error reporting or any network request.
- No demo data, seed, fixture or test hook in the shipped files.
- No `inert` attribute on the page and no `.scrim` element (the goldens need them only because they have no script; the native modal provides both).

## Roadmap
- **Build order:** 2 of 2. Depends on `habit-logic` (done first).
- **Nature:** FE, live-composition module.
- **Gates:** functional QA green (qa.md Gherkin against the running app), code review pass, security pass, fidelity 1-to-1 (after functional green), and the cold-boot live-e2e gate (`@R27`) with its evidence artifact. Then the module is done.
- **Size note:** this is the larger module. If a builder approaches its context limit, it hands off at a task boundary; tasks 1 to 8 are each independently committable.
