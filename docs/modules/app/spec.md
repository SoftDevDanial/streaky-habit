# Module: app

> Build contract. Read by the Senior Frontend Dev agent. Build ONLY what is here.
> Stack: LOCKED to project stack (static page, vanilla JavaScript ES modules, plain CSS, `localStorage`, zero dependencies). Depends on: `habit-logic` (its Contracts only).
> Nature: FE, and the mandatory **live-composition module**. It owns the shipped entry point `index.html`, the composition root, storage, the clock and the midnight rollover, and it carries the **cold-boot live-e2e gate** for the whole system.
> Written by: the solutions architect (sdlc planner), 2026-10-08 (1.0, sealed, full text in git tag `v1.0.0`). v1.1.0 delta written by the planner (solutions architect role), 2026-10-13. 1.0 clarify items CG-2 to CG-9 stay ruled as recorded in `../ROADMAP.md`. v1.1.0 clarify gate part 1 (ledger S4 row 2, S5 row 2, S6 row 2, off-scope rows 6 and 7) is ruled and applied here. v1.1.0 clarify gate part 2 items CG-10 to CG-19 are ruled. The owner ruled all ten on 2026-10-13 with the recommended answers this spec applies (ledger S1 row 4 for CG-12, CG-13 and CG-19, S3 row 2 for CG-10 and CG-11, S4 row 3 for CG-17, S7 row 12 for CG-14, CG-15, CG-16 and CG-18). Each place that applies one names its item, and no task waits on any of them (`../ROADMAP.md`, v1.1.0, Clarify gate). Changed 2026-10-13 after the plan check (F1). This line first said CG-10 to CG-18 were open, left out CG-19, and held the tasks that depend on them.
> Changed 2026-10-13 after the plan check (B1, F1, F3 to F6, F8, N1, N3, N7). Each change carries a dated note where a reader of this contract needs it. The prose colons and the "1.0 text" labels of the v1.1.0 text were rewritten without a change of meaning (F8), so they carry no note.
> Changed 2026-10-13 after the plan re-check (F12 to F15, N8, N9). The Tasks header gains the rule for a test that waits on a later task (F12) and the stub method for names and files under test (F13). Task 11 places the `@R30` scenarios (N9, F13), task 12 records the owner's ruling on its removals (F15) and the successors of two `test_tick.py` tests (F14), tasks 15 to 22 name the marks they write and remove (F12), and T8 states the planted case (N8). Each change carries its own dated note.

## v1.1.0 delta
| R# | Status | Ledger scope | What changes |
|---|---|---|---|
| R1 | Changed | S6, S7, S8 | Title "Danial's Streaky Habit", the golden's viewport meta, the tab icon link, the new skeleton and five dialogs |
| R2 | Changed | S7 | The stylesheet is the v1.1.0 `system.css` without its golden stand-ins |
| R3 | Changed | S7 | First visit is the S1 golden (`today-empty.html`) |
| R4 | Changed | S6, S7, S8 | The header carries the mark, "Streaky Habit", the date and, below 1024 px, the Overview button |
| R5 | Changed | S7 | Rows with a bin, Year and Done today, in a list frame that scrolls on its own |
| R6 | Changed | S2 | The numbers are labelled Current and Best |
| R7 | Retired in v1.1.0, replaced by R31 and R33 | S1, S7 | The 7-day strip is gone |
| R8 | Retired in v1.1.0, replaced by R31, R32, R34 and R37 | S1 | Ticking moves to Done today, the year view and the day editor |
| R9 | Retired in v1.1.0, replaced by R35 and R38 | S7 | The heatmap becomes the overview band and the overview popup |
| R10 | Changed | S7 | New markup, the frame shows the new row (CG-15) |
| R11 | Changed | S7 | The message sits above the field, and typing clears it |
| R12 | Changed | S7 | The composer's full state of the S3 golden |
| R13 | Changed | S3, S7 | M1 opens from a row's bin or from the year view. A time-free guard replaces the 500 ms Delete habit window (CG-10) |
| R14 | Changed | S3, S7 | Keeping returns focus to the control that opened M1. The page guard covers every popup (CG-11) |
| R15 | Changed | S3, S7 | Focus after a delete depends on where it started. From the year view both popups close |
| R16 | Changed | S1, S4 | Every edit path saves, and a save reports whether it worked |
| R17 | Changed | S4, S7 | The unreadable note is the S5 banner. It shows with the warning when the reset save fails |
| R18 | Retired in v1.1.0, replaced by R41 | S4 | A failed save is no longer silent |
| R19 | Changed | S1, S7 | The rollover redraws the rows, the overview and every open popup |
| R20 | Unchanged | | |
| R21 | Changed | S7 | The new sizes at 360 px, and no page scroll |
| R22 | Changed | S7 | The new tab order, focus rings and Esc order |
| R23 | Changed | S7 | The v1.1.0 motion table, pop and bump |
| R24 | Changed | S7 | The places a name appears |
| R25 | Changed | S6 | `/src/icon.svg` joins the request list |
| R26 | Unchanged | | |
| R27 | Changed | S1 to S8, S5 | The new headline flows, in Chromium and in WebKit |
| R28 | Changed | S7 | Eight screens at their widths, and the states sheet |
| R29 | New | S6 | The tab icon file |
| R30 | New | S5 | The browser suite and the live gate run in Chromium and WebKit |
| R31 | New | S1, S7 | Done today |
| R32 | New | S1, S2 | Every edit updates every view at once |
| R33 | New | S1, S2, S3, S7 | The habit's year view (P2) |
| R34 | New | S1 | Ticking a day in the year view |
| R35 | New | S7 | The overview band (desktop) |
| R36 | New | S1, S7 | The day editor (P1) |
| R37 | New | S1 | Ticking in the day editor |
| R38 | New | S7 | The overview popup (P3, phone) |
| R39 | New | S1, S7 | The overview year view (P4) |
| R40 | New | S7 | Popups, their stack, Esc and the backdrop |
| R41 | New | S4 | The save warning |
| R42 | New | S7 | How a ring and the legend are drawn |

Counts. 14 new (R29 to R42), 22 changed, 4 retired (R7, R8, R9, R18), 2 unchanged (R20, R26), 42 in all (38 live).

## Sources
| Source | What it fixes here |
|---|---|
| `docs/brainstorm/brainstorm.md`, the 1.0 part and "v1.1.0 delta" with its Round 1 and Round 2 rulings | capabilities, rules, copy, the reach of past days, the layout, non-goals |
| `docs/v1.1.0/CHANGE-LEDGER.md`, S1 to S8, clarify gate part 1 rulings, H-01, H-02 | scope, the save warning at boot, WebKit, the icon as a file, the name |
| `docs/design/` goldens `today.html` (K1), `day-editor.html` (P1), `year-view.html` (P2), `overview.html` (P3), `overview-year.html` (P4), `delete-dialog.html` (M1), `today-empty.html` (S1), `today-full.html` (S3), `states.html` (S2, S4, S5), each with its `.md` | markup, classes, copy, layout, states |
| `docs/design/system.md`, `system.css` | tokens, components, rings, beads, motion, breakpoints, accessible names |
| `docs/design/RULINGS.md` (1.0) and `RULINGS-v1.1.0.md` | the browser floor, the approved copy and the seven interaction rules, the small points, the mark |
| `docs/design-explore/v1.1.0/final/SELF-CRITIQUE.md` | the approved copy list and the seven interaction rules (rules 1 to 7 below) |
| `docs/design-explore/v1.1.0/round-2/f2.html` and `f2.md` (the direction the owner accepted) | readings where the goldens and rules are silent, each named with its CG item |
| `docs/design/sample-history.json` | the v1.1.0 test data (tests only, never shipped) |
| `docs/brainstorm/research/webkit-testing.md`, `save-warning-and-tab-icon.md` | the engine switch, the save rules SW1 to SW8, the test drivers, the icon file |

The seven approved interaction rules (SELF-CRITIQUE, approved in RULINGS-v1.1.0) are cited as "rule N". Rule 1, focus on open and focus back to the opener. Rule 2, Esc closes the top layer only, and the backdrop closes a popup. Rule 3, focus after a delete. Rule 4, the phone day editor keeps the chosen day in sight. Rule 5, a tick anywhere redraws everything at once. Rule 6, ring and bead numbers are SVG text. Rule 7, name errors on Add, typing clears, Dismiss moves focus to the field.

Phase skills. The plan phase has none assigned. This module is UI work, so its builder, and any solver fixing a UI or fidelity finding, loads the design row of `docs/phase-skills.md` (`taste-skill`, `frontend-design`) before writing UI and declares in `BUILD.md` what it loaded and what changed. The goldens already apply those skills (`system.md`, "Skills loaded"), so the build copies the goldens rather than re-deciding anything.

## Invariants & assumptions
- `index.html` at the project root is the only entry point and the composition root. It boots the real app on the real `localStorage` with whatever is saved there, or with nothing. There is no demo, seed, fixture, flag or query-string path.
- The goldens are the truth for markup, classes, copy and CSS. The app copies their CSS (R2) and mirrors their DOM. `docs/design/` is read-only for everyone.
- The current day comes from the device clock in exactly one function, `readToday()` in `src/app.js`, which returns `localDateKey(new Date())`. Tests control time only with Playwright's `page.clock`, never with a hook in the app.
- All state is one in-memory array of `Habit` (habit-logic Contracts) plus the shown `todayKey` and which popups are open for what. Every change goes through a habit-logic function, then a save, then a render.
- Every render runs synchronously inside the event handler that caused it. No `requestAnimationFrame`, `setTimeout`, `queueMicrotask`, promise deferral or observer callback renders anything, so a test sees the result as soon as the event has been handled.
- Text that comes from data (habit names, dates, counts) reaches the DOM only through `textContent` and `setAttribute`.
- One tab at a time (CG-9 of 1.0, an accepted residual, kept by the owner at the 1.0 seal). The app does not listen to the `storage` event.
- Browser floor (RULINGS 1.0, still standing). Current Chrome, Edge, Safari and Firefox, at least Chrome 105, Safari 15.4, Firefox 121. v1.1.0 changed (S5). Tests run in headless Chromium and headless WebKit (R30). Firefox is not tested. WebKit on Windows is Safari's engine, not Safari on an iPhone (research, webkit-testing section 3), so touch gestures, the on-screen keyboard and Safari's storage expiry stay with the owner's iPhone cases in UAT.
- The page is served as static files. GitHub Pages in production, `python -m http.server` in tests, possibly under a sub-path. The public deployment serves only `index.html` and `src/` plus `.nojekyll` (CLAUDE.md, Publish, 1.0 SEC-04).
- GitHub Pages serves every project site of one user from one origin, so other pages on that origin can read and write this app's `localStorage` key. Saved data is untrusted input. v1.1.0 (research A4). The showcase hub frames the app from that same origin, without `sandbox`, so the framed app and the app opened on its own share one store. The hub never writes `streaks.state` and never calls `localStorage.clear()` (a constraint on the hub, recorded here).
- Engine behaviour that differs by design (R30). A mouse click on a `<button>` focuses it in Chromium and focuses no element in WebKit (as Safari does). WebKit's mouse-down handler looks for a mouse-focusable element under the pointer, finds none for a button without `tabindex`, and clears focus (research webkit-testing, section 2). Wherever a requirement says a control "keeps focus" after it is pressed, it means the app never moves focus away from it. After a keyboard press both engines show the control focused. After a mouse press Chromium shows the control focused and WebKit shows `document.activeElement` as `body`, whatever had focus before. Task 11's probe confirms it, and a different measurement is written into qa.md with its value. Changed 2026-10-13 (planner, solutions architect role). The last sentence first read "WebKit shows `document.activeElement` unchanged (`body` when nothing had focus)", which disagrees with the research (a click on Add after typing in the field leaves `body`, not the field).

## Requirements

### Entry point, stylesheet and icon

- **R1.** (v1.1.0 changed, S6, S7, S8) `index.html` at the project root is the shipped entry point.
  - It starts `<!doctype html>` and `<html lang="en">`. Its head holds, in this order. `<meta charset="utf-8">`. The Content Security Policy `<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'">`, unchanged from 1.0 (ledger S6 row 2, "CSP as strict as 1.0"). `<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">` (the goldens' value, needed for `env(safe-area-inset-bottom)`). `<title>Danial's Streaky Habit</title>` (S8). `<link rel="icon" type="image/svg+xml" href="src/icon.svg">` (R29, after the CSP meta so the policy covers it). `<link rel="stylesheet" href="src/styles.css">`. `<script type="module" src="src/app.js"></script>`. A comment in the head credits the icons as the goldens do, Phosphor Icons (MIT), "x", "plus" and "trash" regular and "check" bold, paths inlined, and names the mark as the app's own.
  - Every URL in `index.html` and every `import` specifier in `src/` is relative (`src/...`, `./...`), never starting with `/` and never holding a scheme, so the app works from a sub-path. No element in `index.html` carries an `xmlns` attribute (inline SVG in HTML needs none).
  - The body is the static skeleton in Contracts, with no habit data. Its element children are, in order, the sprite `svg`, `div.app`, `dialog.dlg-ov`, `dialog.dlg-all`, `dialog.dlg-year`, `dialog.dlg-day`, `dialog.dlg-del`.
  (1.0 text) title "Streaks", viewport without `viewport-fit=cover`, no icon link, the 1.0 skeleton.

- **R2.** (v1.1.0 changed, S7) `src/styles.css` is the golden stylesheet. Its rules equal the text of `docs/design/system.css` from `:root{` up to, and not including, the comment that opens the golden stand-ins block (`/* ---------- golden stand-ins`), with exactly these changes and no other added, removed or changed rule, selector, property or value.
  1. The stand-ins block is left out (its own comment says "the app does not need them"). The app opens every popup with `showModal()`, so the top layer and the native `::backdrop` replace `.scrim`, `dialog[open]{ position:fixed; inset:0; z-index:10; }` and `.below-desktop`.
  2. Inside `@media (prefers-reduced-motion: no-preference)` the selector `dialog[open]::backdrop, .scrim` becomes `dialog[open]::backdrop`, because no `.scrim` element exists in the app.
  3. CG-3 of 1.0, carried to the new stylesheet. The two backdrop colours read `dialog::backdrop{ background:var(--scrim, rgba(10,11,13,.74)); }` and `.dlg-day::backdrop{ background:var(--scrim-soft, rgba(10,11,13,.52)); }`, the same colours as the tokens, so the scrim still shows in Chrome before 122 and Safari before 17.4, where `::backdrop` does not inherit custom properties. Both are inside the browser floor.
  The comparison ignores comments and whitespace. The reduced-motion change of 1.0 (`::backdrop` added to the `reduce` selector) is not needed, because the backdrop's only animation sits inside the `no-preference` block.
  (1.0 text) the style element of 1.0's `today.html` with three listed changes.

- **R29.** (v1.1.0 new, S6) The tab icon is the file `src/icon.svg`. Its bytes equal, byte for byte as UTF-8 with nothing added, the percent-decoded payload after the first comma of the `href` of the `<link rel="icon">` in every golden that carries one (`today.html`, `day-editor.html`, `year-view.html`, `overview.html`, `overview-year.html`, `delete-dialog.html`, `today-empty.html`, `today-full.html`, one identical href, `states.html` has none). The file parses as XML with the root `{http://www.w3.org/2000/svg}svg` and `viewBox` `0 0 16 16`. It is linked as R1 says. Under the live CSP, loading the link's resolved `href` into an image on the app's page fires `load` and no `securitypolicyviolation`, in both engines. In Chromium, the icon drawn under `prefers-color-scheme: dark` has the fill `#FFB020` (255, 176, 32) and under `light` `#9A5B00` (154, 91, 0) (RULINGS-v1.1.0, the mark). WebKit's colour result is recorded as information only (research B8, item 4). Safari 26 showing one colour in both themes is accepted as Safari's bug (ledger S6 row 2) and is checked in UAT. Never `docs/brand/favicon.svg`, which is the 1.0 mark on a tile.

### The key screen (K1)

- **R3.** (v1.1.0 changed, S7) First visit (brainstorm flow 1, golden `today-empty.html`). When the storage key is absent the app renders S1. `ul.rows` holds exactly one `li.empty` with the golden's orbit `svg` (a dotted `circle.e-orbit` r 50 and a `circle.e-core` r 18 on a 120 box) and `div > p.lead` "No habits yet." and `p.line` "Add one you want to do every day.". No `li.row` exists. The composer is enabled, the field empty, `#nh-msg` hidden and empty. The band (R35) draws every day up to today as a button whose ring is one thin `circle.seg` (r 15) with its day number, named "<Ddd D Mon>, 0 of 0 habits", today with the today circle and `aria-current="date"`. The legend holds "None", one ring of one thin circle, "All". The Overview button carries one thin circle and is named "Overview, today 0 of 0 habits done". No banner shows. Nothing is written to storage until the first change.
  (1.0 text) `p.empty` and 84 heat cells at level 0.

- **R4.** (v1.1.0 changed, S6, S7, S8) Header (today.md, golden K1). `header.top` holds `div.brand` with the mark, an inline `svg.mark` (`viewBox="0 0 28 28"`, `aria-hidden="true"`, `focusable="false"`, one `path` whose `d` equals the golden's) drawn in `--amber` through `currentColor`, and `h1.word` "Streaky Habit". Then `button.ov-btn` (R38), then `time.date` with `datetime` set to today's key and the text `longDate(today)`, for example `datetime="2026-10-10"` and "Saturday 10 October". All copy stays English under a non-English browser locale (for example `de-DE`). At 1024 px and up the Overview button is not displayed (CSS) and the date sits at the right end of the brand line. Below 1024 px the brand line holds the brand and the Overview button and the date has its own line.
  (1.0 text) `h1.brand` "Streaks" and `p.date > time`.

- **R5.** (v1.1.0 changed, S7) Habit rows and the list frame (today.md, system.md Row, principle 4). With one or more habits `ul.rows` holds one `li.row` per habit in stored order, each built as the habit-row markup in Contracts. Position N (1-based) gives the ids `rn-N` (the name) and `rs-N` (the stats). The bin is named `Delete "<name>"` with straight double quotes, Year is named "Year view, <name>", Done today is named "Done today, <name>" with its state in `aria-pressed` and is described by `rs-N`. The page itself never scrolls at any width (`document.documentElement.scrollHeight` equals the viewport height at 360 x 780, 390 x 844 and 1280 x 800 with any number of habits from 0 to 12). The list scrolls inside `div.frame`, and the composer stays where it is however many habits there are. `div.frame-wrap` has the class `more-above` exactly when `div.frame` is scrolled away from its top, and `more-below` exactly when more of its content lies below its visible part. The app sets both from the frame's scroll position in the frame's `scroll` handler, after every render of the rows and on window `resize`, never through an observer callback (Invariants).
  (1.0 text) `ul.habits > li.habit` with a trash button, a streak line and a strip.

- **R6.** (v1.1.0 changed, S2) Current and Best (brainstorm C3, C4 and v1.1.0 "Label them Current and Best", system.md Row). `p.stats#rs-N` holds `span.stat.cur` with `span.lbl` "Current" and then, when the current streak N is above 0, `span.val` holding `b.num` "N" and `span.unit` "day" (N is 1) or "days", or, when it is 0, `span.none` "No streak yet". Then, only when the best streak B is above 0, `span.stat.best` with `span.lbl` "Best" and `span.val` holding `b.num` "B". When B is 0 no `span.stat.best` element exists. The values are `currentStreak` and `bestStreak` for today. The same stats markup shows in P2 (R33, `p.yr-stats`). In P1 a tick shows them as text (R36).
  v1.1.0 sample, today 10 Oct 2026. Read 20 pages "Current 4 days" and "Best 9". Stretch 10 minutes "Current 2 days" and "Best 5". No phone after 11pm "Current" with "No streak yet" and "Best 14". A habit just added shows "Current" with "No streak yet" and no Best block.
  (1.0 text) `span.cur` "6 days" and `span.best` "Best 14", without labels.

- **R7.** Retired in v1.1.0, replaced by R31 and R33. The 7-day week strip is not built (brainstorm v1.1.0, Round 1 rulings, "The per-habit 7-day strip is gone").

- **R8.** Retired in v1.1.0, replaced by R31, R32, R34 and R37.

- **R9.** Retired in v1.1.0, replaced by R35 and R38.

- **R31.** (v1.1.0 new, S1, S7) Done today (brainstorm v1.1.0, Round 1 rulings, "a Done today button", "Done today toggles"). Activating a row's Done today (click, tap, or Space or Enter while it has focus) calls `toggleDay(habits, index, today, today)`. In the same handler the same button element, not a replacement, flips `aria-pressed` (`"true"` when today is in that habit's `done`), the app never moves focus away from it (Invariants, engine note), and R32 runs. A second activation unticks today.
  v1.1.0 sample. Stretch 10 minutes, Done today pressed, gives "Current 3 days" and "Best 5", today's ring 2 of 3. Read 20 pages, Done today unpressed, gives "Current 3 days" and "Best 9", today's ring 0 of 3.

- **R32.** (v1.1.0 new, S1, S2) Every edit updates every view at once (rule 5, brainstorm v1.1.0 "An edit updates the streaks ... at once"). After a tick from any place (R31, R34, R37), an add (R10) or a delete (R15), the same handler saves once (R16) and then shows the new state everywhere it is drawn. Every row's stats (R6) and Done today state. The band's ring and name for every changed day (R35). The Overview button's ring and name (R38). And, when open, P1's subtitle, mini ring, tick states and tick stats (R36), P2's beads, their threads and its stats (R33), P3's cells (R38) and P4's cells (R39). A ring, Done today dot, tick box or bead whose drawn state changed carries the class `pop`, and every `span.val` or `span.none` whose number or text changed carries `bump`, so the motion of R23 plays once for each change. Elements that did not change carry neither class from that edit.

- **R10.** (v1.1.0 changed, S7) Add (brainstorm C1, flow 1, Order). Submitting the composer (Add pressed, or Enter in the field) with a name that `addHabit` accepts appends the habit as a new last `li.row` with "Current" and "No streak yet", no Best block and Done today unpressed. When it is the first habit, `li.empty` goes. The field empties. Any message clears (`#nh-msg` hidden and empty, the field without `aria-invalid`). R32 runs (the band and the Overview button recount against the new number of habits). Then `div.frame` scrolls so the new row lies fully inside its visible part (CG-15, ruled 2026-10-13, ledger S7 row 12, as F2 does). The app does not move focus after a successful add (Invariants, engine note). Worked example, v1.1.0 sample plus "  Drink water  " (stored and shown as "Drink water"). The band's 2026-07-21 reads "Tue 21 Jul, 3 of 4 habits" and its ring has four segments, three of them on and no core. 2026-10-10 reads "Sat 10 Oct, 1 of 4 habits".
  (1.0 text) the bottom row with 7 not-done beads, `p.empty` replaced by `ul.habits`.

- **R11.** (v1.1.0 changed, S7) Name errors (brainstorm, Habit name, golden `states.html` S2, rule 7, system.md Field). Errors show only when the composer is submitted. On a rejected name the habit is not added. `#nh-msg` loses `hidden`, has the classes `field-msg err` and holds exactly one message. The field has `aria-invalid="true"`. The typed text stays unchanged (not trimmed). The field has focus afterwards, also after a click on Add, in both engines (the app moves it there). The message sits above the field, so the field does not move. The messages are `empty` "Name the habit first.", `too-long` "Keep it to 40 characters or fewer.", `duplicate` "You already track this habit.". Typing in the field (any `input` event) clears the error at once (`#nh-msg` hidden and empty, classes `field-msg`, no `aria-invalid`), as rule 7 says. The next submit shows the next result's message or clears it on success.
  (1.0 text) the message under the field with `field-msg field-error`, staying until the next submit.

- **R12.** (v1.1.0 changed, S7) Twelve habits (brainstorm, golden `today-full.html`). Whenever there are 12 habits (after an add, or at load) `form.composer` has the class `is-full`, the field and Add carry `disabled`, `#nh-msg` is shown with the classes `field-msg note` and holds "You track 12 habits, the most this app holds. Delete one to add another.", and the field has no `aria-invalid`. The field keeps `aria-describedby="nh-msg"`. When the count drops below 12 all of this is undone (`is-full` gone, enabled, `#nh-msg` hidden and empty with the classes `field-msg`). After the 12th add the app does not move focus (CG-7 of 1.0). At 12 habits each row keeps its bin (f2.md reading 31).

### The overview

- **R35.** (v1.1.0 new, S7) The overview band (golden `today.html` at 1280, system.md Band). `section.band[aria-labelledby=h-ov]` holds `div.band-meta` (the head line with `h2#h-ov` "Last 12 weeks" and `button.btn-all` named "Year view, all habits" with the text "Year", then `p.hint` "Tap a day to change it.", then `div.legend[aria-hidden=true]`) and `div.ovg-cols[role=group][aria-labelledby=h-ov]`. The grid's children are one empty `div[aria-hidden=true]`, seven `div.og-wd[aria-hidden=true]` reading M, T, W, T, F, S, S, then for each of the 12 weeks of `heatmapCells(habits, today)`, oldest first, one `div.og-mo[aria-hidden=true]` (the short month of `monthLabels(today)` for that column, else empty) followed by its 7 cells, Monday to Sunday. A day up to today is the day-cell button of Contracts named "<shortDate>, <count> of <total> habits", today's also with `aria-current="date"`. A day after today is an empty `span.hc[aria-hidden=true]`. The legend is R42's. The band is in the DOM at every width and is displayed from 1024 px (CSS). Activating a day opens P1 for it (R36). Year opens P4 (R39).
  v1.1.0 sample, today 10 Oct 2026. Cells from Mon 20 Jul to Sun 11 Oct, 83 buttons and one empty cell (Sun 11 Oct). Months "Jul" over week 1, "Aug" 3, "Sep" 8, "Oct" 12. "Mon 20 Jul, 2 of 3 habits", "Tue 22 Sep, 1 of 3 habits", "Sat 10 Oct, 1 of 3 habits" with the today circle. Of the 83, 2 rings have no segment on, 16 one, 47 two and 18 all three with the amber core.

- **R38.** (v1.1.0 new, S7) The overview popup (golden `overview.html`, overview.md). Below 1024 px `button.ov-btn` in the header (type `button`, `aria-haspopup="dialog"`) holds `span.ov-ring[aria-hidden=true]` with today's ring (R42, 28 px by CSS, no number, no today circle) and the text "Overview". Its `aria-label` is "Overview, today <count> of <total> habits done" (the golden's way, no hidden span). Activating it opens `dialog.dlg-ov` (P3) with `showModal()`. P3's head holds `h2#ov-title` "Last 12 weeks", `p.hint` "Tap a day to change it.", Year (`button.btn-all` named "Year view, all habits") and Close (`button.icon-btn` named "Close"). Its body holds `div.ovg-rows[role=group][aria-labelledby=ov-title]` with the same children as the band's grid except that weeks run newest first, one row each, and then `div.legend[aria-hidden=true]` (R42). A row's `div.og-mo` holds the short month of the week's Monday when the row is the newest week, the oldest week, or a week whose Monday is day 1 to 7 of its month, and is empty otherwise (CG-16, ruled 2026-10-13, ledger S7 row 12, F2's rule, which gives Oct, Sep, Aug and Jul for the golden). On opening, Close has focus and the body is scrolled to its top. A day opens P1 over P3 (R36). Year opens P4 over P3 (R39). Close, Esc and, where a backdrop shows, the backdrop close P3 and put focus on the Overview button (rule 1).

- **R39.** (v1.1.0 new, S1, S7) The overview year view (golden `overview-year.html`, brainstorm v1.1.0 Round 2 C5). The band's Year (1024 px and up) and P3's Year (below) open `dialog.dlg-all` (P4) with `showModal()`, over K1 or over P3. Its head holds `h2#all-title` "All habits", `p#all-sub.dlg-sub` "The last 12 months", Close, and `div.yr-tools` with `p.hint` "Tap a day to change it." and `div.legend[aria-hidden=true]` (R42). Its body holds `div.months.months-all` with one `section.month[aria-labelledby=amo-<year>-<month>]` per month of `yearMonths(today)`, newest first (the month number without a leading zero, for example `amo-2026-10`, `amo-2025-10`). Each holds `h3#amo-<year>-<month>` with the month's `title` and `div.mgrid[role=group]` labelled by it, holding seven `span.mwd[aria-hidden=true]` (M, T, W, T, F, S, S), `lead` empty `span.hc.lead[aria-hidden=true]` cells, then one cell per day. An open day is the day-cell button of Contracts named "<yearDate>, <count> of <total> habits" (the year because P4 holds two Octobers, system.md), today's with `aria-current="date"`. A closed day is `span.hc.closed[aria-hidden=true]` holding an `svg` with only `text.c-num.dim` (the day number). An empty day is `span.hc.blank[aria-hidden=true]`. On opening, Close has focus and the body is scrolled to its top. A day opens P1 over P4 (R36). Close and Esc close P4 and put focus on the Year button that opened it. The backdrop closes it where one shows.
  v1.1.0 sample. 366 day buttons from "Fri 10 Oct 2025, 3 of 3 habits" to "Sat 10 Oct 2026, 1 of 3 habits", 21 closed cells (11 to 31 Oct 2026), 9 empty cells (1 to 9 Oct 2025), 39 lead cells.

### The day editor

- **R36.** (v1.1.0 new, S1, S7) Opening a day (golden `day-editor.html`, day-editor.md, brainstorm v1.1.0 "The overview calendar still opens any day in the day editor"). Activating a day button of the band, P3 or P4 opens `dialog.dlg-day` (P1) with `showModal()` for that day, over K1, P3 or P4. Its head holds `div.day-mini[aria-hidden=true]` with the day's ring (R42, 56 px by CSS, no number, no today circle), `h2#day-title` with `longDate(day)` (for example "Tuesday 22 September"), `p#day-sub.dlg-sub` "<count> of <total> habits" and Close. Its `ul.day-list` holds one `li` per habit in list order with the tick of Contracts, named by the habit's name, `aria-pressed` `"true"` when the habit is done that day, described by `ts-N`, whose `span.tstat#ts-N` shows the habit's numbers for today, not as of the chosen day (day-editor.md). That is `span.tcur` "Current N day" or "Current N days", or `span.tcur.none` "No streak yet", then, when Best is above 0, a `span` "Best B". While P1 is open, every day button for that date in the band, P3 and P4 carries the class `is-open`, and loses it when P1 closes. On opening, the first tick has focus (rule 1). Below 768 px, when P1 opens over P3 or P4, the host's `div.sheet-body` scrolls so the chosen day's button lies fully between the bottom of the host's head and the top of P1's box (rule 4), and stays outlined. Close, Esc and the backdrop close P1 and put focus on the day button that opened it, in its host (rule 1, rule 2).
  With no habits (S1) a day still opens P1. Its subtitle reads "0 of 0 habits", its mini ring is one thin circle, its list holds one `li.day-empty` "No habits yet." and Close has focus (CG-12, ruled 2026-10-13, ledger S1 row 4, as F2 does and `system.css` styles `.day-empty`).
  v1.1.0 sample. Tue 22 Sep opens with "1 of 3 habits", ticks Read 20 pages off ("Current 4 days", "Best 9"), Stretch 10 minutes off ("Current 2 days", "Best 5"), No phone after 11pm on ("No streak yet", "Best 14").

- **R37.** (v1.1.0 new, S1) Ticking in the day editor. Activating a tick calls `toggleDay(habits, index, day, today)`. In the same handler the same tick element flips `aria-pressed` and its class `on`, the app never moves focus away from it, the subtitle and mini ring show the new count, and R32 runs. A tick stays in P1 (day-editor.md, Links).
  v1.1.0 sample. Tue 22 Sep, tick Read 20 pages. The tick reads "Current 4 days" and "Best 13", the subtitle "2 of 3 habits", the band's day "Tue 22 Sep, 2 of 3 habits", and Read's row "Best 13".

### The habit's year view

- **R33.** (v1.1.0 new, S1, S2, S3, S7) Opening a habit's year (golden `year-view.html`, year-view.md, brainstorm v1.1.0 Round 1 "a button that opens that habit's year view"). A row's Year opens `dialog.dlg-year` (P2) with `showModal()` for that habit. Its head holds `h2#yr-title` with the habit's name, `p#yr-sub.dlg-sub` "The last 12 months", Close, then `div.yr-mid` with `p.yr-stats` (the R6 stats markup) and `button.btn-del` (type `button`, the trash glyph, the text "Delete habit"), then `div.yr-tools` with `p.hint` "Tap a day to mark it done or not done." and `p.yr-legend[aria-hidden=true]` (`span.mini.on`, "Done", `span.mini`, "Not done"). Its body holds `div.months` with one `section.month[aria-labelledby=mo-<year>-<month>]` per month of `yearMonths(today)`, newest first, each with `h3` and a `div.mgrid[role=group]` holding seven `span.mwd`, `lead` empty `span.yc.lead[aria-hidden=true]` cells, then one cell per day. An open day is the bead button of Contracts, named "Mark <yearDate> as done" whatever its state, with `aria-pressed` and the classes of R34. A closed day is `span.yc.closed[aria-hidden=true]` holding the bead with its number. An empty day is `span.yc.blank[aria-hidden=true]`. On opening, Close has focus and the body is scrolled to its top. Close, Esc and, where it shows, the backdrop close P2 and put focus on that row's Year (rule 1). Delete habit opens M1 for this habit over P2 (R13).
  v1.1.0 sample. Read 20 pages, "Current 4 days", "Best 9", 366 bead buttons of which 250 are done, today's done with the halo, 21 closed and 9 empty cells.

- **R34.** (v1.1.0 new, S1) Ticking a day in the year view (brainstorm v1.1.0 "tapping a day ticks or unticks it for that habit"). Activating a bead calls `toggleDay(habits, index, day, today)` for P2's habit. In the same handler the same button flips `aria-pressed`, the app never moves focus away from it, and R32 runs. A bead button carries `on` when its day is done, `today` (and `aria-current="date"`) when its day is today, `l` when it and the day before are both done and the day before is not before `yearStart(today)`, and `r` when it and the day after are both done and the day after is not after today (system.md, Bead, "consecutive done days ... on one amber thread"). A tick updates `l` and `r` on the neighbours it joins or splits. No control exists for a day after today or before `yearStart(today)`, so neither can be ticked (brainstorm v1.1.0, "Days after today stay closed"). A day before the habit was added is an open day like any other (brainstorm v1.1.0 Rules).
  v1.1.0 sample. No phone after 11pm, tick Fri 9 Oct 2026. "Current 8 days", "Best 14". The bead gains `on`, `l` and nothing on the right (10 Oct is not done).

### Delete a habit

- **R13.** (v1.1.0 changed, S3, S7) Open, and the time-free guard (brainstorm C6 and v1.1.0 "A slow double click can never delete, and Delete habit no longer waits half a second", golden `delete-dialog.html`, CG-10, v1.0.0 ledger row 37). Changed 2026-10-13 after the plan check (N7), this citation first named f2.md reading 29, which is about focus after a delete (R15) and not the guard. A row's bin, or Delete habit in P2, opens the one `dialog.dlg-del` (M1) with `showModal()`, over K1 or over P2. Its title `#del-title` reads `Delete "<name>"?`, its body `#del-body` "Its history is deleted too.", its buttons "Cancel" (`.btn.btn-secondary`) then "Delete habit" (`.btn.btn-danger`), both type `button` as the golden draws them. Cancel has focus once M1 is open (rule 1). The title keeps the two 1.0 security notes, SEC-02 and SEC-06 (full text at tag `v1.0.0`). The name sits between U+2068 and U+2069, and the title's copy of it has the bidi format characters U+202A to U+202E, U+2066 to U+2069, U+0085, U+001C to U+001E and U+2029 taken out. The stored name and every other place keep the name as typed.
  The guard (CG-10, ruled 2026-10-13, ledger S3 row 2). When M1 opens, the app records the box of the control that opened it (`getBoundingClientRect()` of the bin or of P2's Delete habit). Delete habit ignores a mouse or touch activation (a `click` whose `detail` is above 0) when its point lies inside that box, or when its `detail` is above 1. M1 stays open and nothing changes. A keyboard activation (`detail` 0) always acts. Nothing depends on time. Delete habit acts on the first activation that meets neither condition, however soon after opening. Cancel, Esc and the backdrop always act.
  Why. M1 opens under the pointer, and its Delete habit can lie over the bin that opened it (measured in 1.0, T7). The second click of a double click, slow or fast, lands at the point of the first. The 1.0 500 ms window let a slower second click through (v1.0.0 ledger row 37) and made a deliberate click wait.
  (1.0 text) two 500 ms guards measured in `event.timeStamp`, the first holding Delete habit after the opening click.

- **R14.** (v1.1.0 changed, S3, S7) Keep (rule 1, CG-6 of 1.0). Cancel, Esc, or a backdrop click (pressed and released outside M1's box, R40) closes M1, keeps the habit and its history unchanged, saves nothing, and puts focus on the control that opened M1, looked up after any re-render (the row's bin, or P2's Delete habit with P2 still open). A click inside M1's box that hits no button, or a drag that starts inside the box and ends on the backdrop, leaves it open.
  The tap-through guard (CG-11, ruled 2026-10-13, ledger S3 row 2, the 1.0 page guard kept by the owner's UAT-06 ruling and extended to the new popups). For 500 ms after a mouse or touch click inside any popup (`detail` above 0), measured in `event.timeStamp`, a click on the page or on a popup that was already open beneath it is cancelled and goes no further. Clicks inside that same popup, and in popups opened after it, are never held. Closing with the keyboard starts no window. Why. A click that closes a popup sends the second click of the same gesture to the layer behind (measured in 1.0, T7 b). In v1.1.0 the layer behind holds Done today buttons, band days and bins.
  (1.0 text) focus back to the trash button, the page guard after a click in the one dialog.

- **R15.** (v1.1.0 changed, S3, S7) Delete (brainstorm, Delete, rule 3, f2.md reading 29). Delete habit removes the habit and its whole history with `deleteHabit`, saves (R16), closes M1, closes P2 too when M1 was opened from it (f.md reading 18), and R32 runs. Deleting the only habit shows S1's `li.empty` again. A later habit with the same name starts with no history. Focus then goes as rule 3 says. From a row's bin, to the bin of the row now at the deleted position, else (the last row went) to the bin of the row above, else (the list is empty) to the field. From P2, to the Year of the row now at the deleted position, else to the Year of the row above (CG-18, ruled 2026-10-13, ledger S7 row 12, F2's code), else to the field. When the focused row lies outside the frame's visible part, the frame scrolls it into view.
  v1.1.0 sample. Delete "Stretch 10 minutes" from its bin. Two rows remain, focus is on `Delete "No phone after 11pm"`, the band's 2026-07-21 reads "Tue 21 Jul, 2 of 2 habits" with a full core. Delete "No phone after 11pm" from its bin. Focus is on `Delete "Stretch 10 minutes"`.
  (1.0 text) focus to the next trash button or the field, after the 500 ms window.

### Storage

- **R16.** (v1.1.0 changed, S1, S4) Kept on the device (brainstorm C7, Storage). The state is saved under the `localStorage` key `streaks.state` as `encodeState(habits)` (Contracts, format unchanged from 1.0), synchronously after every change (add, Done today, a P1 tick, a P2 tick, delete) and at no other time except the reset of R17. A reload, or closing the tab and opening the page again in the same browser, shows the same habits in the same order with the same done days. Loading writes nothing (a saved value is left byte for byte as it was until the next change). `saveHabits` reports whether the write worked (Contracts, R41).

- **R17.** (v1.1.0 changed, S4, S7) Unreadable saved data (brainstorm, Storage, golden `states.html` S5, rule 7). When a saved value exists but `decodeState` reports it unreadable (the 1.0 rule, CG-4 of 1.0), the app starts with no habits, at once saves the empty state `{"version":1,"habits":[]}`, and shows `div.banner.note[role=status]` in `div.banners` holding `p` "Your saved habits could not be read, so the list was reset." and `button.icon-btn` (type `button`) named "Dismiss note" with the x glyph. S1's empty list shows under it. Dismiss removes the note, changes nothing else, and moves focus to the field (rule 7). The note does not come back on the next load. When that reset save fails, the save warning of R41 shows as well, above the note (CG-17, ruled 2026-10-13, ledger S4 row 3, the research's reading).

- **R18.** Retired in v1.1.0, replaced by R41. (1.0 text) a failed save shows no message (CG-5 of 1.0). Ledger S4 row 2 replaces that rule.

- **R41.** (v1.1.0 new, S4) The save warning (brainstorm v1.1.0 Rules, golden `states.html` S4, research SW1 to SW8, ledger S4 row 2). `div.banner.warn[role=status]` holding `p` "Your habits are not being saved on this device. Changes will be lost when you close this tab." is the first child of `div.banners` while saving fails, and has no dismiss control.
  - A save attempt (SW1) is every call of `saveHabits`. It fails (SW2) when `localStorage` cannot be read or `setItem` throws, whatever the exception. The app never reads the exception's name or code. It works (SW3) when `setItem` returns.
  - The latest attempt decides (SW4). After a failed attempt the warning shows. After a working one it is removed. No timer, no probe write, no read back.
  - At boot (part 1 CG-1, ruled "Yes, show it at once"). When reading the saved state fails (reading `localStorage` or `getItem` throws), the warning shows from the first render and the app starts empty with no note. When the reset save of R17 fails, it shows as well. A readable or absent value at boot shows no warning, because loading saves nothing.
  - Every attempt reads `localStorage` afresh, so the warning can clear without a reload (SW6).
  - The banner element is inserted only when the state turns to failing and removed only when it turns to working, so the live region is not touched while saves keep failing (SW7).
  - When a save fails the change stays in memory and on screen and the app keeps working. No exception reaches the console.
  - Out of scope, a known limit for the README (part 1 CG-2, SW8). Private browsing, Safari's 7-day clean-up and the user clearing site data lose data with no failure the page can see.

### Time

- **R19.** (v1.1.0 changed, S1, S7) Rollover while visible (brainstorm, Rolling over midnight). While the page is open the app compares `readToday()` with the shown day every 30 seconds (so at most 60 seconds after local midnight). When the local date has changed, the same handler redraws everything derived from today for the new day. The header date, every row's stats and Done today state (Done today now means the new day), the band (cells, today's ring, closed cells, months), the Overview button's ring and name, and every open popup. P1 keeps its chosen day and updates its numbers. P2 and P4 show the new year (`yearMonths` of the new day), P3 the new 12 weeks. The view never changes day before local midnight. The composer keeps its typed text, its message and its `aria-invalid` state. The control that had focus keeps it when it still exists (the same element, or the control for the same date and the same habit). When its day left the view, focus goes to the open-focus target of the top popup (rule 1), or with no popup open to the first focusable control of the page (CG-14, ruled 2026-10-13, ledger S7 row 12). When P1 is open for a day that leaves the editable year at the rollover (it was `yearStart` of the old day), P1 stays open on that day and its ticks change nothing, because `toggleDay` refuses the day (habit-logic R9) and the app draws each tick from the data, so no tick flips and nothing is saved. Whenever P1 closes after a rollover removed the day button that opened it (from the band, P3 or P4), focus goes as CG-14 says (CG-19, ruled 2026-10-13, ledger S1 row 4. Added 2026-10-13 by the planner, solutions architect role, because no rule or golden covers it).
  v1.1.0 sample, Sat 10 to Sun 11 Oct 2026. Header "Sunday 11 October". Read 20 pages "Current 4 days", "Best 9", Done today unpressed. Stretch 10 minutes "No streak yet", "Best 5". No phone after 11pm "No streak yet", "Best 14". The band's Sun 11 Oct is a button named "Sun 11 Oct, 0 of 3 habits" with the today circle, and Sat 10 Oct loses it.
  (1.0 text) the strips, streak lines and heatmap move, focus on a day button keeps its strip position.

- **R20.** Rollover when shown again (brainstorm: "immediately when the tab is shown again"). When `visibilitychange` fires and `document.visibilityState` is "visible", the app runs the R19 check at once, synchronously in that handler, without waiting for the next 30 second check.

### Popups

- **R40.** (v1.1.0 new, S7) Popups (rules 1 and 2, system.md Elevation and layers, Sheet). P1, P2, P3, P4 and M1 are the five `dialog` elements of the skeleton, each opened with `showModal()` and never with `show()` or the `open` attribute. They stack in the order they open (on a phone P1 over P3 or P4, P4 over P3, M1 over P2). Esc closes the top popup only (the native `cancel`), so on a phone Esc closes P1, then P4, then P3. A click whose press and release both land outside a popup's box closes that popup (its backdrop, the 1.0 CG-6 rule for every popup), and closes nothing else. That holds at every width, 768 to 1023 px included, where rule 2 names only desktop and phone. `f2.html` closes every dialog on a backdrop click (`if (e.target === d) d.close()`). Changed 2026-10-13 after the plan check (N1), the `f2.html` source for 768 to 1023 px was added. A click inside the box, or a drag from inside the box to the backdrop, closes nothing. Everything under the top popup is inert (native), the page does not scroll (`html:has(dialog[open])`), and Tab never reaches a control outside the top popup. Each popup's first focus and its return of focus on closing are in R13, R33, R36, R38 and R39. The app sets focus by hand on closing in both engines, because a clicked button never took focus in WebKit (Invariants).

### Platform

- **R21.** (v1.1.0 changed, S7) Phone width (CLAUDE.md, system.md Breakpoints and Sizes). At 360 x 780, with K1, S1, S3 or any popup showing, the page has no horizontal scrolling (`scrollWidth` at most 360) and no vertical page scrolling (R5). Every button that is not a day cell is at least 44 x 44 px, the field and Add are 48 px tall. P2's beads are 34 px. P3 and P4 rings are 40 px in 46 px tall cells, P3's cells 43.1 px wide (RULINGS-v1.1.0 small point 3 accepts day cells under 44). At 390 x 844 beads are 36 px and P3 and P4 rings 42 px in 48 px cells.
  (1.0 text) day buttons at least 44 wide and 32 px beads.

- **R22.** (v1.1.0 changed, S7) Keyboard (brainstorm Platform, system.md Row and Accessible names). Every control can be reached and used with the keyboard. Tab order on K1 below 1024 px is the Overview button, then the Dismiss button when the note shows, then for each row its bin, Year and Done today, then the field, then Add. From 1024 px it is the band's Year, the band's day buttons oldest first (column by column, Monday to Sunday), then the Dismiss button, the rows, the field and Add. Space and Enter activate a focused button, Enter in the field submits, Esc closes the top popup. Focus rings show only on `:focus-visible`, as `system.css` sets them. A 2px solid `--focus` outline, computed `rgb(237, 238, 240)`, offset 2px by default, -2px on `.icon-btn`, `.btn-bin`, `.hc` and `.tick`, 3px on `.btn`, and on a bead the outline is drawn on `.bead` 3px out while the button itself has none. A focused bin's glyph turns `--danger`. A mouse click draws no ring.
  (1.0 text) trash then 7 day buttons per habit, `rgb(28, 37, 35)` rings.

- **R23.** (v1.1.0 changed, S7) Motion (system.md Motion, Reduced motion). Without reduced motion. A Done today, Year, bin, tick or bead transition runs as `system.css` sets it (for example `.btn-done` has the computed `transition-duration` `0.17s, 0.17s, 0.17s, 0.12s`). An element with `pop` plays the `pop` animation (260 ms on a Done today dot, tick box and bead, 300 ms on a ring and on the Overview button's ring). A `bump` plays `bump` (280 ms). An opening popup's `div.dlg-box` plays `rise` (220 ms), P1's plays `sheet` (260 ms), and its `::backdrop` plays `fade` (180 ms). Each change replays its animation, also when the same element changes twice in a row. With `prefers-reduced-motion: reduce` every element, pseudo-element and backdrop has no transition and no animation (computed `transition-duration` `0s` and `animation-name` `none`), so every change and every popup appears at once. Nothing moves on load.
  (1.0 text) bead transitions `0.18s, 0.18s, 0.12s` and the dialog's `dialog-in`.

- **R24.** (v1.1.0 changed, S7) Names are text (threat model). A habit name is never read as markup. A name such as `<img src=x onerror=alert(1)>` is stored and shown literally in the row's `h3`, in the bin's, Year's and Done today's accessible names, in P1's tick, in P2's title and in M1's title, no element is created from it and no script runs. `src/` uses none of `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, `eval` or `new Function`.

- **R25.** (v1.1.0 changed, S6) Nothing leaves the device (brainstorm, CLAUDE.md no network calls). Through any use of the app the only requests the page makes are same-origin `GET` requests, with no query string, for the page itself (`/` or `/index.html`), `src/styles.css`, `src/icon.svg` (allowed, not required, research B8 item 5), the `src/*.js` modules, and `/favicon.ico` if the browser asks for it. The R1 CSP is present and in force (a `fetch` from the page is refused). No console error and no uncaught page error occurs in any qa.md flow, in either engine. R25 is about what the page sends, not who else on the origin can read the stored key (T9).

- **R26.** No seed, no hooks, no globals (constitution, cold-boot rule). The shipped files (`index.html` and everything in `src/`) contain no habit data: none of the names in `sample-history.json` and no reference to that file. No code path writes habits other than the user's add, tick and delete, and the R17 reset. Query strings and fragments have no effect: `/?demo=1`, `/?seed` and `/#sample` boot exactly like `/`. The app adds no property to `window` and exposes no test hook.

### Engines and gates

- **R30.** (v1.1.0 new, S5) Two engines (ledger S5 row 2, research webkit-testing sections 4 and 5). One browser suite and one live gate script, run once per engine.
  - `tests/browser/conftest.py` adds the pytest option `--engine` with the choices `chromium` and `webkit`, default `chromium`, so `python -m pytest tests/browser -q` runs Chromium as before and `python -m pytest tests/browser -q --engine webkit` runs WebKit. A session `engine` fixture returns it. One helper, `launch(playwright, engine)`, is the only place a browser is launched (`getattr(playwright, engine).launch(headless=True, args=LAUNCH_ARGS[engine])`), with `--force-color-profile=srgb` for Chromium only and no argument for WebKit, and it refuses any other engine. `live_e2e.py` imports it.
  - A registered marker `chromium_only(reason=...)` turns a test into a skip when the engine is not Chromium. Each such skip carries its written reason, is listed in the run's evidence and is counted, never reported as a pass.
  - No context sets `is_mobile` (it breaks `mouse.wheel` in WebKit). Touch uses `has_touch` as in 1.0.
  - `tests/browser/live_e2e.py` takes `--engine` (default `chromium`). Its `summary.json` records the engine and `browser.version`, never a hard-coded engine name.
  - Evidence folder names carry the engine (`<datetimestamp>-chromium`, `<datetimestamp>-webkit`).
  - The functional suite and the cold-boot live gate run green in both engines, and a WebKit failure blocks the seal. The fidelity pixel gate stays Chromium only (R28).
  - Every 1.0 spec line that said "headless Chromium only" is replaced by this requirement. The same line in `CLAUDE.md` is the orchestrator's to amend (ledger S5 row 2).

- **R27.** (v1.1.0 changed, S1 to S8) Cold-boot live-e2e gate (constitution, Definition of done). In a fresh headless context of the chosen engine, with empty storage and the real system clock, the app served from the project root by `python -m http.server <port> --bind 127.0.0.1` performs the v1.1.0 headline flows (first visit, add, Done today, a past day through the overview and the day editor, a past day through a habit's year view, the year of all habits, a delete kept and a delete done, a name error, the save survives reloads) at 390 x 844 and the desktop band at 1280 x 800, driven only by real gestures, and writes its evidence to `docs/modules/app/qa/live-e2e/<datetimestamp>-<engine>/`. It passes in Chromium and in WebKit (R30). The exact steps are the `@R27` scenario in qa.md.
  The gate's control (constitution, Gates and evidence). The same script run with `--control seeded` in the same engine, against the same server, opens the app on storage that already holds the sample (seeded through the same-origin `__seed__` page before the app loads). It must fail at its first-visit step, on `stored(page)` being null and on `li.empty` with "No habits yet.", and its evidence is kept as a RED capture in `docs/modules/app/qa/live-e2e/<datetimestamp>-<engine>-control/` beside the green run. A control run that passes the first-visit step means the gate cannot tell a seeded start from a cold one, and the gate is not met. Added 2026-10-13 after the plan check (F5). The red-first rule cannot reach this gate, because task 27 writes the script after the app is built, so the control is its watched failure.
  (1.0 text) Chromium only, flows 1 to 4 on the strip and heatmap.

- **R28.** (v1.1.0 changed, S7) Looks right (constitution, 1-to-1 with the design). In Chromium, K1 (`today.html`), P1 (`day-editor.html`), P2 (`year-view.html`), P4 (`overview-year.html`), M1 (`delete-dialog.html`), S1 (`today-empty.html`) and S3 (`today-full.html`) render 1-to-1 with their goldens at 360 x 780, 390 x 844 and 1280 x 800, and P3 (`overview.html`) at 360 x 780 and 390 x 844 (MANIFEST, "Widths that matter", P3's 1280 render is reference only), under the Fidelity gate in qa.md. Every row of the FE element checklist matches, the `states.html` frames included.

- **R42.** (v1.1.0 new, S7) Rings and the legend (system.md Ring and Legend, principle 1, rule 6, f2.html `ring` and `legendHTML`). A ring is an `svg` with `viewBox="0 0 40 40"` and `aria-hidden="true"`. In this order it holds `circle.c-today` (cx 20, cy 20, r 19.2) when the ring is today's in the band, P3 or P4. Then, for N habits and their flags in list order (`doneFlags`), the segments. N 0 gives one `circle.seg` (cx 20, cy 20, r 15). N 1 gives one `circle.seg` (r 15) with the class `on` when done. N 2 or more gives N `path.seg`, `on` when done, each with the `d` of the arc rule below. Then `circle.c-core` (cx 20, cy 20, r 11.5) when N is above 0 and every flag is true. Then, for a day cell, `text.c-num` (x 20, y 20, `dy=".352em"`) with the day number, with the class `on` when the core is drawn. The arc rule, for segment i of N. The step is 360/N degrees, the gap `min(22, 0.3 x step)`, the start angle `i x step + gap/2` and the end angle `(i + 1) x step - gap/2`, clockwise from 12 o'clock on radius 15 round (20, 20). Each point is `20 + 15 sin(a)`, `20 - 15 cos(a)`, rounded to 2 decimals (`Math.round(v * 100) / 100`, written as JavaScript writes the number). The `d` is `M<x1> <y1>A15 15 0 <large> 1 <x2> <y2>`, where `<large>` is 1 when `step - gap` is above 180 and 0 otherwise. This reproduces the goldens' `#a3-0` to `#a3-2` and `#a12-0` to `#a12-11` exactly. The legend (`div.legend[aria-hidden=true]`) holds `span` "None", then for N 0 one ring of one thin circle, and otherwise one ring for each distinct count of `[0, ceil(N/3), ceil(2N/3), N]` in that order, a ring for count c having its first c segments on (and the core when c equals N), then `span` "All". Legend, Overview button and P1 mini rings carry no number and no today circle. The pure part (arc `d`, legend counts) lives in `src/ring.js`.
  Examples. N 3 gives the legend counts 0, 1, 2, 3. N 12 gives 0, 4, 8, 12 (today-full). N 1 gives 0, 1. N 2 gives 0, 1, 2. Segment 0 of 3 is `M22.86 5.28A15 15 0 0 1 34.18 24.88`, segment 0 of 12 is `M21.18 5.05A15 15 0 0 1 26.46 6.46`.

## Contracts

### Files
| File | Owns |
|---|---|
| `index.html` | R1. Head, CSP, icon link, the sprite, the static skeleton, the five dialogs |
| `src/styles.css` | R2 |
| `src/icon.svg` (v1.1.0 new) | R29 |
| `src/app.js` | Composition root. Boot, `readToday()`, the state (habits, shown `todayKey`, which popups are open for which habit or day, the opener of each), every event handler (Done today, Year, bin, band, P3 and P4 days, P1 ticks, P2 beads, Delete habit, Cancel, Close, backdrops, Esc, the composer, Dismiss, the frame's scroll), the guards of R13 and R14, the rollover. Calls `storage.js` and the view modules. Exports nothing |
| `src/view.js` | DOM for K1. Header and Overview button, banners, rows and their stats, the frame's fade classes, the composer's states. No storage, no clock, no event registration |
| `src/calendar.js` (v1.1.0 new) | DOM for every day grid. Day cells with rings for the band, P3 and P4, P2's beads with their threads, the month sections. No storage, no clock, no event registration |
| `src/popups.js` (v1.1.0 new) | DOM for the popups' own parts. P1's head and ticks, P2's head and stats, M1's title, `showModal`, `close`, the `is-open` marks, the phone scroll of rule 4. No storage, no clock, no event registration |
| `src/ring.js` (v1.1.0 new) | Pure. The arc `d` of R42 and the legend counts. No DOM |
| `src/storage.js` | The storage contract below |
| `tests/browser/` | The pytest suite, `conftest.py` (R30), the fidelity state scripts in `tests/browser/fidelity/`, the live gate `live_e2e.py`. Not shipped |
| `tests/fixtures/design-v1.0.0/` (v1.1.0, tasks 11 and 12 only) | The four 1.0 goldens that the 1.0 browser tests read, restored byte for byte for task 11's baseline and removed at task 12 with their readers (task 11, task 12). Not shipped. Added 2026-10-13 after the plan check (B1) |
| `tests/storage.test.js`, `tests/ring.test.js` (v1.1.0 new) | Node unit tests of the pure exports of `storage.js` and `ring.js`. Not shipped |

v1.1.0. The split follows cohesion lines (composition and events, K1's DOM, the day grids, the popups' DOM, ring geometry, persistence). The 1.0 `view.js` held everything visible. In v1.1.0 that would be one file for five popups and four grids, so it is cut where the reasons to change differ. `ring.js` is pure so its geometry is proven by unit tests against the goldens' paths. There is still no storage or clock abstraction.

### Uses from habit-logic
`localDateKey`, `isDateKey`, `dayParts`, `shortDate`, `longDate`, `yearDate`, `monthTitle` (from `src/dates.js`). `MAX_HABITS`, `currentStreak`, `bestStreak`, `toggleDay`, `heatmapCells`, `monthLabels`, `doneFlags`, `yearStart`, `yearMonths`, `validateName`, `addHabit`, `deleteHabit` (from `src/habits.js`). The app re-implements none of these rules. P3's extra month label (R38) reads `dayParts(...).month` of the newest week's Monday.

### Ring contract (`src/ring.js`, v1.1.0 new)
| Export | Signature | Behaviour |
|---|---|---|
| `arcPath` | `(i: number, n: number) => string` | The `d` of segment `i` of `n` by R42's arc rule, for `n` 2 or more and `i` 0 to `n - 1`. For example `arcPath(0, 3)` is `M22.86 5.28A15 15 0 0 1 34.18 24.88` |
| `legendCounts` | `(n: number) => number[]` | The distinct values of `[0, ceil(n/3), ceil(2n/3), n]` in that order, so `[0]` for `n` 0, `[0, 1]` for 1, `[0, 1, 2, 3]` for 3 and `[0, 4, 8, 12]` for 12 |

Nothing else is exported. Changed 2026-10-13 (planner, solutions architect role). This table was missing. The Files table named `src/ring.js` but gave no export names or signatures, so its unit tests (qa.md `@R42`) had no surface to call.

### Storage contract (`src/storage.js`)
- Key `streaks.state`. Value and readable rule unchanged from 1.0 (`{"version":1,"habits":[{"name":...,"done":[...]}]}`, CG-4 of 1.0, rules 1 to 5, at tag `v1.0.0`).
- Exports.
  | Export | Signature | Behaviour |
  |---|---|---|
  | `STORAGE_KEY` | `"streaks.state"` | |
  | `decodeState` | `(raw: string \| null) => { status: "absent" } \| { status: "ok", habits: Habit[] } \| { status: "unreadable" }` | Pure, unchanged |
  | `encodeState` | `(habits: Habit[]) => string` | Pure, unchanged |
  | `loadHabits` (v1.1.0 changed) | `() => { habits: Habit[], reset: boolean, saveFailed: boolean }` | Reads the key, guarding only the storage access. A failed read gives `{ habits: [], reset: false, saveFailed: true }`. Absent gives `saveFailed: false`. Unreadable saves `encodeState([])` and gives `{ habits: [], reset: true, saveFailed: <that save failed> }`. Readable gives the habits, `reset: false`, `saveFailed: false`. Never throws |
  | `saveHabits` (v1.1.0 changed) | `(habits: Habit[]) => boolean` | Reads `localStorage` and calls `setItem` inside `try`. Returns `true` when `setItem` returned, `false` on any exception. Never inspects the exception |
- (1.0 text) `loadHabits` returned `{ habits, reset }` and `saveHabits` returned nothing (CG-5 of 1.0, retired with R18).

### Static skeleton (`index.html` body)
In this order, with the goldens' classes, ids and attributes. Static text shown here is the copy. Parts marked "filled" are built by the view modules.
```html
<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">
  <symbol id="i-x" viewBox="0 0 256 256"><path d="..."/></symbol>
  <symbol id="i-plus" viewBox="0 0 256 256"><path d="..."/></symbol>
  <symbol id="i-check" viewBox="0 0 256 256"><path d="..."/></symbol>
  <symbol id="i-trash" viewBox="0 0 256 256"><path d="..."/></symbol>
</svg>
<div class="app">
  <header class="top">
    <div class="brand">
      <svg class="mark" viewBox="0 0 28 28" aria-hidden="true" focusable="false"><path d="..."/></svg>
      <h1 class="word">Streaky Habit</h1>
    </div>
    <button type="button" class="ov-btn" aria-haspopup="dialog" aria-label="(filled)"><span class="ov-ring" aria-hidden="true">(filled)</span>Overview</button>
    <time class="date" datetime="(filled)">(filled)</time>
  </header>
  <main class="main">
    <section class="band" aria-labelledby="h-ov">
      <div class="band-meta">
        <div class="band-head"><h2 id="h-ov">Last 12 weeks</h2><button type="button" class="btn-all" aria-haspopup="dialog" aria-label="Year view, all habits">Year</button></div>
        <p class="hint">Tap a day to change it.</p>
        <div class="legend" aria-hidden="true">(filled)</div>
      </div>
      <div class="ovg-cols" role="group" aria-labelledby="h-ov">(filled)</div>
    </section>
    <div class="banners">(filled when R17 or R41 applies)</div>
    <h2 id="h-habits" class="sr">Habits</h2>
    <div class="frame-wrap">
      <div class="frame">
        <div class="sentinel" aria-hidden="true"></div>
        <ul class="rows" aria-labelledby="h-habits">(filled)</ul>
        <div class="sentinel" aria-hidden="true"></div>
      </div>
    </div>
    <form class="composer" novalidate>
      <p id="nh-msg" class="field-msg" aria-live="polite" hidden></p>
      <div class="add-row">
        <label for="nh" class="add-label">New habit</label>
        <div class="add-ctl">
          <input id="nh" class="input" type="text" autocomplete="off" spellcheck="false" aria-describedby="nh-msg">
          <button id="add-btn" class="btn btn-primary" type="submit"><svg class="ph" aria-hidden="true"><use href="#i-plus"/></svg>Add</button>
        </div>
      </div>
    </form>
  </main>
</div>
<dialog class="dlg-full dlg-ov" aria-modal="true" aria-labelledby="ov-title">
  <div class="dlg-box">
    <div class="sheet-head"><div class="ov-head">
      <div><h2 id="ov-title">Last 12 weeks</h2><p class="hint">Tap a day to change it.</p></div>
      <button type="button" class="btn-all" aria-haspopup="dialog" aria-label="Year view, all habits">Year</button>
      <button type="button" class="icon-btn" aria-label="Close"><svg class="ph" aria-hidden="true"><use href="#i-x"/></svg></button>
    </div></div>
    <div class="sheet-body"><div class="ovg-rows" role="group" aria-labelledby="ov-title">(filled)</div><div class="legend" aria-hidden="true">(filled)</div></div>
  </div>
</dialog>
<dialog class="dlg-full dlg-all" aria-modal="true" aria-labelledby="all-title" aria-describedby="all-sub">
  <div class="dlg-box">
    <div class="sheet-head">
      <div class="head-top"><div><h2 id="all-title">All habits</h2><p id="all-sub" class="dlg-sub">The last 12 months</p></div>
        <button type="button" class="icon-btn" aria-label="Close"><svg class="ph" aria-hidden="true"><use href="#i-x"/></svg></button></div>
      <div class="yr-tools"><p class="hint">Tap a day to change it.</p><div class="legend" aria-hidden="true">(filled)</div></div>
    </div>
    <div class="sheet-body"><div class="months months-all">(filled)</div></div>
  </div>
</dialog>
<dialog class="dlg-full dlg-year" aria-modal="true" aria-labelledby="yr-title" aria-describedby="yr-sub">
  <div class="dlg-box">
    <div class="sheet-head">
      <div class="head-top"><div><h2 id="yr-title">(filled)</h2><p id="yr-sub" class="dlg-sub">The last 12 months</p></div>
        <button type="button" class="icon-btn" aria-label="Close"><svg class="ph" aria-hidden="true"><use href="#i-x"/></svg></button></div>
      <div class="yr-mid"><p class="yr-stats">(filled)</p><button type="button" class="btn-del"><svg class="ph" aria-hidden="true"><use href="#i-trash"/></svg>Delete habit</button></div>
      <div class="yr-tools"><p class="hint">Tap a day to mark it done or not done.</p><p class="yr-legend" aria-hidden="true"><span class="mini on"></span><span>Done</span><span class="mini"></span><span>Not done</span></p></div>
    </div>
    <div class="sheet-body"><div class="months">(filled)</div></div>
  </div>
</dialog>
<dialog class="dlg-day" aria-modal="true" aria-labelledby="day-title" aria-describedby="day-sub">
  <div class="dlg-box">
    <div class="day-head">
      <div class="day-mini" aria-hidden="true">(filled)</div>
      <div><h2 id="day-title">(filled)</h2><p id="day-sub" class="dlg-sub">(filled)</p></div>
      <button type="button" class="icon-btn" aria-label="Close"><svg class="ph" aria-hidden="true"><use href="#i-x"/></svg></button>
    </div>
    <ul class="day-list">(filled)</ul>
  </div>
</dialog>
<dialog class="dlg-del" role="alertdialog" aria-modal="true" aria-labelledby="del-title" aria-describedby="del-body">
  <div class="dlg-box">
    <h2 id="del-title">(filled)</h2>
    <p id="del-body">Its history is deleted too.</p>
    <div class="dlg-actions"><button type="button" class="btn btn-secondary">Cancel</button><button type="button" class="btn btn-danger">Delete habit</button></div>
  </div>
</dialog>
```
- The four symbol paths and the mark's path are copied exactly from `today.html`. No other icon exists. The goldens' ring `<defs>` (`#a3-*`, `#a12-*`) are not copied, because the app draws each segment as a `path` with R42's `d`, which renders the same.
- Inner `svg` elements in buttons carry `aria-hidden="true"` and no `focusable` (the goldens dropped it, SELF-CRITIQUE). The sprite and the mark keep `focusable="false"` as the goldens do.
- `svg`, `use`, `path`, `circle` and `text` are created with `document.createElementNS("http://www.w3.org/2000/svg", ...)`. Only in `src/` code, never as markup in `index.html` (R1, no `xmlns`).

### Rendered markup (the view modules), mirroring the goldens
Habit row (whitespace between tags is free. Elements, classes, ids, attributes and text are not):
```html
<li class="row">
  <div class="r-head">
    <h3 class="r-name" id="rn-1">Read 20 pages</h3>
    <button type="button" class="btn-bin" aria-haspopup="dialog" aria-label="Delete &quot;Read 20 pages&quot;"><svg class="ph" aria-hidden="true"><use href="#i-trash"/></svg></button>
  </div>
  <p class="stats" id="rs-1"><span class="stat cur"><span class="lbl">Current</span><span class="val"><b class="num">4</b><span class="unit">days</span></span></span><span class="stat best"><span class="lbl">Best</span><span class="val"><b class="num">9</b></span></span></p>
  <button type="button" class="btn-year" aria-haspopup="dialog" aria-label="Year view, Read 20 pages">Year</button>
  <button type="button" class="btn-done" aria-pressed="true" aria-label="Done today, Read 20 pages" aria-describedby="rs-1"><span class="dot"><svg aria-hidden="true"><use href="#i-check"/></svg></span>Done today</button>
</li>
```
- No streak. `<span class="stat cur"><span class="lbl">Current</span><span class="none">No streak yet</span></span>`. No `span.stat.best` when Best is 0.
- Empty list. `<li class="empty"><svg viewBox="0 0 120 120" aria-hidden="true"><circle class="e-orbit" cx="60" cy="60" r="50"/><circle class="e-core" cx="60" cy="60" r="18"/></svg><div><p class="lead">No habits yet.</p><p class="line">Add one you want to do every day.</p></div></li>`.
- Day cell (band, P3, P4). `<button type="button" class="hc" data-key="2026-07-20" aria-haspopup="dialog" aria-label="Mon 20 Jul, 2 of 3 habits"><svg viewBox="0 0 40 40" aria-hidden="true">(R42 ring with the day number)</svg></button>`. Today adds `aria-current="date"` and the today circle. While its P1 is open it adds the class `is-open`.
- Bead (P2). `<button type="button" class="yc on r" data-key="2025-10-10" aria-pressed="true" aria-label="Mark Fri 10 Oct 2025 as done"><span class="bead"><svg aria-hidden="true"><text x="50%" y="50%" dy=".352em">10</text></svg></span></button>`. Closed, `<span class="yc closed" aria-hidden="true"><span class="bead"><svg aria-hidden="true"><text x="50%" y="50%" dy=".352em">11</text></svg></span></span>`.
- Tick (P1). `<li><button type="button" class="tick on" aria-pressed="true" aria-label="No phone after 11pm" aria-describedby="ts-3"><span class="tbox"><svg aria-hidden="true"><use href="#i-check"/></svg></span><span class="tname">No phone after 11pm</span><span class="tstat" id="ts-3"><span class="tcur none">No streak yet</span><span>Best 14</span></span></button></li>`. With a streak the first span is `<span class="tcur">Current 4 days</span>`.
- Banners. `<div class="banner warn" role="status"><p>Your habits are not being saved on this device. Changes will be lost when you close this tab.</p></div>` and `<div class="banner note" role="status"><p>Your saved habits could not be read, so the list was reset.</p><button type="button" class="icon-btn" aria-label="Dismiss note"><svg class="ph" aria-hidden="true"><use href="#i-x"/></svg></button></div>`, in that order when both show.
- Message line. Hidden and empty with the class `field-msg`. An error with `field-msg err`. The 12-habit note with `field-msg note`.

### Events and focus (`src/app.js`)
- Delegated `click` listeners on stable containers (`div.app`, each dialog), a `submit` listener on `form.composer` (calls `preventDefault()`), an `input` listener on the field (R11), a `close` listener on each dialog, and a `scroll` listener on `div.frame` (R5).
- No row, button or cell carries an index attribute. A row's habit is its position in `ul.rows`. A day is found by `data-key`, whose values are validated date keys.
- Focus targets. R11 (field), R12 (unmoved), R13 (Cancel), R14 (the opener), R15 (rule 3), R17 (field), R19 (CG-14), R31, R34 and R37 (unmoved), R33, R38 and R39 (Close on open, the opener on close), R36 (first tick on open, the day on close).
- Rollover. `setInterval(checkDay, 30000)` started at boot, and a `visibilitychange` listener that calls `checkDay` when visible.

### Copy (every user-facing string)
| Where | Text | Source |
|---|---|---|
| `title` | Danial's Streaky Habit | brainstorm v1.1.0 Name, today.md |
| `h1.word` | Streaky Habit | brainstorm v1.1.0 Name, today.md |
| header date | `longDate(today)`, e.g. Saturday 10 October | today.md |
| Overview button | Overview, named "Overview, today N of T habits done" | SELF-CRITIQUE copy |
| band and P3 title, hint | Last 12 weeks, Tap a day to change it. | SELF-CRITIQUE copy |
| Year on the overview | Year, named "Year view, all habits" | SELF-CRITIQUE copy |
| legends | None, All. P2 Done, Not done | SELF-CRITIQUE copy |
| weekday letters | M T W T F S S | goldens |
| hidden list heading | Habits | today.md |
| row | Current, Best, "1 day", "N days" (unit "day" or "days"), No streak yet, Year, Done today | SELF-CRITIQUE copy, brainstorm |
| row names | `Delete "<name>"`, "Year view, <name>", "Done today, <name>" | SELF-CRITIQUE copy |
| empty list | No habits yet. Add one you want to do every day. | today-empty.md |
| field label, button | New habit, Add | today.md |
| errors | Name the habit first. / Keep it to 40 characters or fewer. / You already track this habit. | brainstorm, states.md |
| 12-habit note | You track 12 habits, the most this app holds. Delete one to add another. | brainstorm |
| day names | "Ddd D Mon, N of T habits", P4 "Ddd D Mon YYYY, N of T habits" | system.md |
| P1 | `longDate(day)`, "N of T habits", "Current N days", "Current 1 day", "No streak yet", "Best N", Close. With no habits "No habits yet." (CG-12) | day-editor.md, CG-12 |
| P2 | the habit's name, The last 12 months, Delete habit, Tap a day to mark it done or not done., month titles "October 2026", bead names "Mark Ddd D Mon YYYY as done" | year-view.md |
| P4 | All habits, The last 12 months, Tap a day to change it. | overview-year.md |
| M1 | `Delete "<name>"?` (with U+2068 and U+2069 round the name, SEC-02 and SEC-06), Its history is deleted too., Cancel, Delete habit | delete-dialog.md |
| S4 warning | Your habits are not being saved on this device. Changes will be lost when you close this tab. | brainstorm v1.1.0, states.md |
| S5 note | Your saved habits could not be read, so the list was reset. Dismiss note | brainstorm, states.md |
| Close | Close | SELF-CRITIQUE copy |

No other user-facing string exists.

## Tasks
> Atomic, ordered, one commit each. Each commit carries the code and the tests that prove it (qa.md). Browser tests use pytest with Playwright's sync API. pytest-playwright is not installed and is not needed. Every UI task (12 and up except 14, 27 and 28) loads the design row (`taste-skill`, `frontend-design`) first and declares it in `BUILD.md`. Changed 2026-10-13 (planner, solutions architect role). This read "13 and up", which left out task 12 (the markup, the stylesheet and the icon), UI work by `docs/phase-skills.md`. Every new test is run once before its code lands and recorded RED against the property it asserts (constitution, Gates and evidence). For a new export of `src/` (`arcPath` and `legendCounts` in task 13) the RED comes from a throwaway stub, never from the import error (the method is stated once, in `../habit-logic/qa.md`, named data). The live gate's watched failure is its control run (R27, task 28). Added 2026-10-13 after the plan check (F5, F6). A test whose subject is a name or a file that its own task creates, and that would otherwise fail at import, on a missing fixture or on a missing file, gets a stub by the same method (task 11's `conftest.py` names, task 12's `src/icon.svg`, task 26's new state scripts, listed in qa.md, "Controls are watched failing first"). Added 2026-10-13 after the plan re-check (F13).
> **A test that waits on a later task.** One rule, added 2026-10-13 after the plan re-check (F12). A scenario that uses a feature a later task builds has its test in the file qa.md names for it, and that test is green from task N, the task that lands the last feature it uses. It is written at its file's task and committed with `pytest.mark.xfail(strict=True, reason="task N")`, or, where qa.md says so, it is written at task N itself. Either way it is run once before the code of the task that writes it and recorded RED, like every new test. In a Scenario Outline the mark sits only on the Examples rows that wait (`pytest.param(..., marks=...)`), so the other rows are green at once. Task N removes the mark in its commit. The mark is strict, so a marked test that passes early fails the run. The builder then reads the test against its scenario, and only when the test is right and every feature it uses already exists does the builder remove the mark in that commit and record why in `BUILD.md`. So every commit ends with the suite green and each waiting test reported XFAIL. No mark is left after task 22, the last task the table names, so the QA finder's runs hold none, and a mark left over is a FAIL of its scenario. qa.md, "Scenarios that wait on a later task", names N for every such scenario and row.
1. to 10. [x] The 1.0 tasks, done (`BUILD.md`, tag `v1.0.0`).
11. [x] The engine switch and the WebKit baseline (S5, first of all v1.1.0 work). The orchestrator installs WebKit before it (`python -m playwright install webkit`, owner approved). `conftest.py` gains `--engine`, `engine`, `launch`, the `chromium_only` marker and the engine in evidence folder names. `live_e2e.py` gains `--engine` and an engine-neutral summary. Three `@R30` scenarios of the Feature "Two engines" are tests in the new file `tests/browser/test_engines.py`, "The run uses the engine it was asked for", "An unknown engine is refused before any browser starts" and "One helper launches every browser". Their RED comes from throwaway stubs of the `conftest.py` names, never committed (qa.md, "Controls are watched failing first"). "Every context has the clipboard stand-in" presses Done today and Year, so it is written into `test_engines.py` at task 19 (qa.md). The other two are finder checks on run output and no test function holds them. The QA finder reads "A Chromium-only test is a counted skip with its reason in WebKit" from the `-rA` output of its Chromium and WebKit runs (build step 5, after task 12 has given CO-1 its marker), and "The live gate records its engine" is read from the evidence of the live gate's runs at task 28. Changed 2026-10-13 after the plan re-check (N9, F13). This task first put both finder checks into `test_engines.py`, where the first would fail before any test carries `chromium_only`, and it named no RED method for the conftest names. The 1.0 suite is then made to run on the current tree, with no change to any 1.0 assertion, in two steps.
    - The 1.0 sample. `conftest.py`'s `SAMPLE` (so `SAMPLE_HABITS`, `SAMPLE_LEVELS` and the state helpers built on it, under the same names) reads `tests/fixtures/sample-history-v1.0.0.json` (habit-logic task 6) instead of `docs/design/sample-history.json`.
    - The 1.0 goldens. Four 1.0 browser tests read goldens that the design finalize of 2026-10-13 replaced in `docs/design/` (the v1.1.0 goldens have no `/* ---------- end components ---------- */` block, no `.page` and no `dialog.dialog`). The four files are restored as test fixtures, each byte for byte the output of `git show v1.0.0:<source>`, the same way habit-logic task 6 restores the sample.

    | Fixture | Source in tag `v1.0.0` | Blob id of the source | Tests that read it |
    |---|---|---|---|
    | `tests/fixtures/design-v1.0.0/today.html` | `docs/design/today.html` | `40a3fdb648053a9902c4a6cc64592b73cf376c29` | `test_entry.py` `test_R2_golden_style_block_is_the_same_in_every_golden` and `test_R2_stylesheet_is_the_golden_css_with_the_listed_changes` (through `golden_style`), `test_render.py` `test_R28_the_rendered_page_has_the_markup_of_the_goldens` (through `canonical_pair`), `test_entry.py` `test_R1_static_skeleton` (through `golden_icon_paths`) |
    | `tests/fixtures/design-v1.0.0/today-empty.html` | `docs/design/today-empty.html` | `9439584b7004012a6fbe56ec0f8ede496bba2298` | `test_R2_golden_style_block_is_the_same_in_every_golden`, `test_R28_the_rendered_page_has_the_markup_of_the_goldens` |
    | `tests/fixtures/design-v1.0.0/delete-dialog.html` | `docs/design/delete-dialog.html` | `1d9fb01f28bfc0de9739ed0c33a748a76b12f7ed` | `test_R2_golden_style_block_is_the_same_in_every_golden`, `test_delete.py` `test_R28_the_open_dialog_has_the_markup_of_the_golden` (through `canonical_pair`) |
    | `tests/fixtures/design-v1.0.0/states.html` | `docs/design/states.html` | `9258f8f3d079bb7c284b2745131d3804360be3fc` | `test_R2_golden_style_block_is_the_same_in_every_golden`, `test_R28_the_rendered_page_has_the_markup_of_the_goldens` (`symbol#i-x`), `test_R1_static_skeleton` (through `golden_icon_paths`) |

    `conftest.py` gains `DESIGN_V10_DIR` (that folder), and the three helpers that read a 1.0 golden, `canonical_pair` in `conftest.py` and `golden_style` and `golden_icon_paths` in `test_entry.py`, read from it. `DESIGN_DIR` still names `docs/design/`. `test_R1_static_skeleton` passes on either folder (its three icon paths are equal in 1.0 and v1.1.0, plan check B1), and it reads the fixtures too, so no 1.0 test reads a v1.1.0 golden. The fixtures are test data under `tests/`, which is never published (CLAUDE.md, Publish), and `docs/design/` is only read.
    - Proof, in Chromium with no `src/` change. (1) `git hash-object` of each of the four fixtures prints the blob id in the table, which `git rev-parse v1.0.0:<source>` gives. The blob id is the check because `core.autocrlf` is true on this machine, so a later checkout may change a fixture's line ends while its blob stays equal. (2) The nine 1.0 test files, run by name (`test_add.py`, `test_delete.py`, `test_entry.py`, `test_fidelity_inputs.py`, `test_platform.py`, `test_render.py`, `test_rollover.py`, `test_storage.py`, `test_tick.py`), give the sealed count, 179 passed, 0 failed, 0 skipped (`docs/v1.0.0/SEAL.md`). (3) `test_engines.py` passes.
    - Changed 2026-10-13 after the plan check (B1). This task first named only the sample as the cause of the red state, so its 179 could not be reached. The plan check found the four golden reads. The fixture approach is the orchestrator's choice (ORCH, reversible, ledger off-scope row 9).

    Then one WebKit run of the same nine 1.0 files and of the 1.0 live gate is recorded with its pass, fail and skip counts, every failure and the run time, in `docs/modules/app/qa/webkit-baseline/<datetimestamp>-webkit/`. The research probes run here (P1 `Object.defineProperty(window, "localStorage", ...)` in WebKit, P2 the quota fill time per engine, P3 the `.svg` type `http.server` sends, the click `detail` of two quick taps, `getComputedStyle(dialog, "::backdrop")`, the CSP console text, the computed `outline` string). Each WebKit failure is classed (a) an app defect Safari would show, (b) an engine difference written into qa.md with its measurement, or (c) Chromium-only tooling marked `chromium_only` with its reason. → R30
12. [x] `index.html` (head, icon link, sprite, skeleton, five dialogs), `src/styles.css` (R2), `src/icon.svg` (R29), and `tests/browser/test_entry.py` written again with the v1.1.0 `@R1`, `@R2` and `@R29` scenarios. → R1, R2, R29
    The new skeleton and stylesheet break every 1.0 locator, and the 1.0 view code finds none of its elements, so from this task until task 15 the page renders no habit data. This task therefore also removes what only the 1.0 app needed. Each removed file stays at tag `v1.0.0`, and qa.md holds the scenarios that replace it.
    - The removals are ruled. The owner answered "git rm, kept in tag v1.0.0 (Recommended)" on 2026-10-13 at 22:20 (ledger off-scope row 11). This task's commit removes the eight 1.0 test files named below and the folder `tests/fixtures/design-v1.0.0/` with `git rm`, and makes no archive copy. Each of the eight test files is recoverable with `git checkout v1.0.0 -- tests/browser/<file>`. The four golden fixtures never sat at that path in tag `v1.0.0`, so that command does not reach them. They are recoverable with `git checkout <task 11's commit> -- tests/fixtures/design-v1.0.0/`, or each from `git show v1.0.0:docs/design/<file>` checked against its blob id in task 11. Never with `git checkout v1.0.0 -- docs/design/<file>`, which would overwrite a v1.1.0 golden (constitution, Filesystem safety). These are the only whole files the plan removes. Added 2026-10-13 after the plan re-check (F15). The task first deleted files its builder did not create with no recorded authorization.
    - It removes the 1.0 browser test files that a later task writes again. `test_render.py` (written again at task 15), `test_add.py` (21), `test_delete.py` (22), `test_storage.py` (23), `test_rollover.py` (24), `test_platform.py` (25) and `test_fidelity_inputs.py` (26).
    - It removes `test_tick.py`, which no task writes again. Done today (`test_today.py`, task 16), the day editor (`test_day_editor.py`, task 18) and the year view (`test_year.py`, task 19) replace ticking on the strip. Its six tests (four `@R8`, one `@R6`, one JC3) all drive the 1.0 strip, so none can run on the v1.1.0 page. The four `@R8` tests have their scenarios under Feature "Retired in v1.1.0" in qa.md. The other two had no 1.0 scenario. `test_R6_best_goes_back_to_zero_in_place_when_the_only_tick_is_undone` guarded a 1.0 defect (a Best of 0 left behind the Best element a tick had added), and its property is now the `@R6 @R32` scenario "Best back to 0 removes the Best block in every place" (`test_today.py`, task 16). `test_JC3_a_tick_writes_only_the_text_that_changed` kept a tick from writing a text again, because the 1.0 streak line was a live region (1.0 R6, `p.streak[aria-live=polite]`) and a screen reader may read a rewritten text again (`BUILD.md` item 3). The v1.1.0 stats are not a live region (in every golden only `#nh-msg` carries `aria-live`), so that reason lapses and no scenario counts text writes. What stays of it is R32's rule that an element whose value did not change carries no class from the edit, held by the `@R32` scenario "A tick that changes Current and leaves Best moves Current only" (`test_today.py`, task 16) beside "One Done today updates every place at once, and only what changed moves". The P1 and P2 rows of both new scenarios wait on tasks 18 and 19 (qa.md, W12 and W13). Changed 2026-10-13 after the plan re-check (F14). This bullet first said the scenarios of all six were retired or replaced, while these two had none, so the R6 guard would have been lost here.
    - It removes `tests/fixtures/design-v1.0.0/` and `DESIGN_V10_DIR`, whose only readers are now gone.
    - In `conftest.py`, `SAMPLE_HABITS`, `TWELVE`, `sample_state()` and `twelve_state()` switch to the v1.1.0 sample (qa.md, conftest table), and `SAMPLE_LEVELS`, the read of `tests/fixtures/sample-history-v1.0.0.json` and every helper that only a removed file used go. That fixture stays for habit-logic's unit tests.
    - `live_e2e.py` (pytest does not collect it) and the 1.0 fidelity scripts `tests/browser/fidelity/seed-sample.js` and `open-delete-dialog.js` (no test reads them once `test_fidelity_inputs.py` is gone) stay as they are until task 27 and task 26 write them again. Nothing runs them in between.
    - After this task the browser suite holds `test_entry.py` and `test_engines.py`. Two `test_entry.py` scenarios need a page that boots and adds, so they are written and recorded RED here and committed with `xfail(strict=True)` under the Tasks rule above. "The page links the icon and the policy lets it load" carries `reason="task 15"` (a boot with no page error), and "The app works from a sub-path" carries `reason="task 21"` (it adds a habit). The suite is green at the end of this task, with those two reported XFAIL. Changed 2026-10-13 after the plan re-check (F12). This bullet first said the two "stay RED", so the suite was red between commits, and it gave task 21 as "at the latest".
    - Changed 2026-10-13 after the plan check (F3). No task removed `test_tick.py`, none said what the 1.0 files do between this task and the task that writes each again, and the qa's conftest table gave `SAMPLE_HABITS` the v1.1.0 sample while task 11 needs the 1.0 one.
13. [x] `src/ring.js` and `tests/ring.test.js`. → R42
14. [x] `src/storage.js` results (`saveHabits` boolean, `loadHabits` with `saveFailed`), `tests/storage.test.js`. → R16, R41
15. [x] Boot render. Header, Overview button, band, rows, stats, frame fades, composer at load, S1. `tests/browser/test_render.py`. Its proof includes the `test_entry.py` scenario "The page links the icon and the policy lets it load" (task 12), whose `xfail` mark it removes (W1). It writes W3 to W6 with their marks (qa.md, "Scenarios that wait on a later task"). → R3, R4, R5, R6, R12, R35, R42
16. [x] Done today and the every-view update with `pop` and `bump`. `tests/browser/test_today.py` (`test_tick.py` went at task 12). It writes W7 to W13 with their marks. → R31, R32, R23
17. [ ] Popup plumbing and P3. `tests/browser/test_popups.py`, `tests/browser/test_overview.py`. It writes W14 to W18 with their marks. → R40, R38
18. [ ] P1, opening and ticking, from the band and from P3. `tests/browser/test_day_editor.py`. It removes the marks of task 18 (W6, W8, W12, W13 and W15 to W18). → R36, R37, R32
19. [ ] P2, opening and ticking. `tests/browser/test_year.py`, and the `@R30` scenario "Every context has the clipboard stand-in" in `test_engines.py`, because it presses Done today and Year (task 11, W21). It removes the marks of task 19 (W3, W7, W10, W12, W13 and W15 to W18) and writes W19 with its mark. → R33, R34, R32, R30
20. [ ] P4, from the band and from P3, and P1 over P4. Added to `test_overview.py` and `test_day_editor.py`, with the P4 rows of W22. It removes the marks of task 20 (W9, W14, W15, W16 and W18). → R39, R36
21. [ ] The composer. `tests/browser/test_add.py`. Its proof includes the `test_entry.py` scenario "The app works from a sub-path" (task 12). It removes the marks of task 21 (W2, W4, W5 and W19) and writes W20 with its mark. → R10, R11, R12
22. [ ] Delete from a row and from P2, the time-free guard (CG-10), the tap-through guard (CG-11), focus (CG-18), all three ruled 2026-10-13. `tests/browser/test_delete.py`. It removes the last marks (W11, W15 to W18 and W20). → R13, R14, R15
23. [ ] Persistence, the unreadable note, the save warning. `tests/browser/test_storage.py`. → R16, R17, R41
24. [ ] Rollover with popups open (CG-14 and CG-19, ruled 2026-10-13). `tests/browser/test_rollover.py`. → R19, R20
25. [ ] Platform checks and anything they expose. `tests/browser/test_platform.py`. → R21, R22, R23, R24, R25, R26
26. [ ] The fidelity state scripts for the plugin harness, each seed script starting with the clipboard stand-in and each after-load script checking for it before it clicks, and `tests/browser/test_fidelity_inputs.py` (qa.md, Fidelity gate). → R28
27. [ ] `tests/browser/live_e2e.py`, the v1.1.0 cold-boot gate in both engines, with its control mode `--control seeded` (qa.md, `@R27`, R27). → R27, R30
28. [ ] Gates, run by the finders after the suite is green in both engines. Fidelity in Chromium (23 captures and the states check), then the cold-boot live gate in Chromium and in WebKit, each engine's green run with its control run, which must fail at the first-visit step (R27). → R28, R27
Changed 2026-10-13 after the plan check (F1, F3, F4, F5, N3). Tasks 22 and 24 first waited on their clarify items, which are now ruled. Task 19 gained the clipboard scenario that task 11 cannot pass on the 1.0 app (F3). Task 26 names the stand-in (F4). Tasks 27 and 28 name the live gate's control (F5).
Changed 2026-10-13 after the plan re-check (F12). Tasks 15 to 22 name the waiting tests they write with an `xfail` mark and the marks they remove (W1 to W22 in qa.md).

## Threat model
> Feeds the security gate. A static page with no backend. The data is personal (habits can be sensitive) and lives only in this browser. v1.1.0 changes are marked. Rows without a mark are 1.0's and still hold (their dated notes are at tag `v1.0.0`).

**Assets.** The user's habit names and day history (privacy and integrity). The page's DOM and script context. The promise that this app sends nothing (R25).

**Trust boundaries.** (1) `localStorage` into the app, untrusted. (2) Typed habit names into the DOM. (3) The page out to the network, which must stay closed. (4) The static host serving the files. (5) v1.1.0. The same-origin hub that frames the app.

| # | Threat | Required mitigation |
|---|---|---|
| T1 | Tampered or corrupt saved data crashes the app, breaks invariants, or smuggles values into code paths | `JSON.parse` inside `try`, the strict readable rule, anything else resets with the S5 note (R17). Saved values are never used as HTML, selectors, property paths or code. v1.1.0. Dates in `done` that lie before the year or after today are kept and never drawn as editable (R34, R39) |
| T2 | Prototype pollution through parsed keys such as `__proto__` | Decoded habits are rebuilt as literal `{ name, done }` objects. Tested with a `__proto__` key |
| T3 | Script injection through a habit name | Names reach the DOM only through `textContent` and `setAttribute` (R24), in every place v1.1.0 adds. CSP `script-src 'self'` as a second layer |
| T4 | Selector injection | No CSS selector is built from a name. Rows are found by position, days by `data-key` |
| T5 | Data leaving the device | No network code, no third-party resource, CSP unchanged (R1), the icon is a same-origin file (R29). Verified by the request log (R25) in both engines |
| T6 | Storage blocked or full. v1.1.0 changed | Every storage call inside `try`. The app keeps working in memory and now says so (R41). Residual (part 1 CG-2). Private browsing, Safari's 7-day clean-up and cleared site data lose habits with no failure the page can see. Stated in the README |
| T7 | Accidental deletion. v1.1.0 changed | Focus opens on Cancel. Esc and the backdrop keep. Delete habit ignores a pointer activation inside the opener's box or with `detail` above 1, with no time window (R13, CG-10). The layer behind a popup ignores clicks for 500 ms after a pointer click in the popup (R14, CG-11). Residual. A deliberate click on the part of Delete habit that lies over the opener's box does nothing, and the user clicks elsewhere on it. WebKit on Windows cannot prove an iPhone's double tap (`detail` of a tap), so UAT carries a double tap on a bin and then on Delete habit on the owner's iPhone (ledger S5 row 2) |
| T8 | A huge value planted in storage slows parsing and, v1.1.0, the year views | Bounded by the origin quota. Linear parsing and validation. v1.1.0 changed. A planted `done` list is not bounded by use. `doneFlags` reads each habit's `done` at most once per call, so one P4 draw reads the planted lists up to about 367 times and the band or P3 up to about 84 times (habit-logic threat model, "Responsiveness of the year views"). Still bounded by the quota. Residual, a value planted near the quota makes P4 slow to open. Changed 2026-10-13 after the plan re-check (N8). This cell said each render reads at most 367 days per habit, which planted data breaks |
| T9 | Another page on the shared origin reads or writes the key | Unchanged, accepted residual (kept by the owner at the 1.0 seal) |
| T10 | Framing. v1.1.0 changed | A meta CSP cannot set `frame-ancestors`. A cross-site framer gets a separate partitioned store. The showcase hub is same-origin and shares the store by design (research A4). It never writes `streaks.state` and never clears storage. Accepted |
| T11 | Supply chain | Zero dependencies, no CDN, no web fonts. Four Phosphor paths (MIT) inlined and credited, the mark is the owner's own |
| T12 | Two tabs, the last save wins | Unchanged, accepted residual (kept at the 1.0 seal) |
| T13 | v1.1.0 new. The tab icon file is swapped or carries script | It is a static file under `src/`, compared byte for byte with the golden (R29). An SVG loaded as an icon or image runs no script. Same-origin only, CSP unchanged |

The 1.0 notes SEC-02, SEC-05 and SEC-06 (the title's bidi isolates and strip, the year 10000 residual) still hold as written at tag `v1.0.0`. SEC-01's time window is replaced for Delete habit by the guard of R13 and kept for the layer behind by R14.

## Non-goals
> Explicit "do NOT build". Building any of these is a defect.
- From the brainstorm. Reminders or notifications. Accounts, login, sync between devices. Weekly targets or any schedule other than daily. Renaming or reordering habits. Export or import. More than one tick per day, notes or amounts. Stats beyond Current, Best and the overview and year views. A theme switcher (v1.1.0 changed, one dark theme only). ~~Editing days older than the last 7~~ (removed in v1.1.0, brainstorm "v1.1.0 delta", USER). Editing a day after today or before the same date last year stays out.
- From the design. No motion other than the system.md Motion table. No icons other than x, plus, trash and check, and the mark. No shadow other than the dialogs'. No streak count-up animation. No Undo bar after a delete (f2.md, "only an idea").
- v1.1.0. No home-screen icon, no `apple-touch-icon`, no web app manifest, no install prompt (ledger off-scope row 7, DEFERRED). No `data:` URL anywhere and no CSP change (ledger S6 row 2).
- v1.1.0. No start date per habit. No detection of private browsing or of Safari's clean-up. No `storage` event handling.
- v1.1.0. No `.scrim` element, no `inert` attribute, no `<dialog open>` (golden stand-ins). No "Prototype states" tab or any review tooling of the prototypes. No screen for `today-warning.html` (today.md names it, no such golden exists, the warning is the S4 frame of `states.html`).
- No undo after delete. No toast, banner or message other than the S2 errors, the S3 note, the S4 warning and the S5 note.
- No service worker or offline cache. "Works offline" means it needs nothing beyond its own files.
- No migration code for other storage versions. Only `version` 1 exists.
- No cross-tab sync. No URL parameters or routes. No keyboard shortcuts beyond native button, dialog and form behaviour.
- No analytics, logging, error reporting or any network request.
- No demo data, seed, fixture or test hook in the shipped files.

## Roadmap
- **Build order.** 2 of 2. Depends on `habit-logic` (its tasks 6 to 9 land before app task 15).
- **Nature.** FE, live-composition module.
- **Gates.** Functional QA green in Chromium and in WebKit (qa.md Gherkin against the running app), code review pass, security pass, fidelity 1-to-1 in Chromium (after functional green), and the cold-boot live-e2e gate (`@R27`) in both engines with its evidence. Then the module is done.
- **Size note.** This is the larger module. A builder that nears its context limit hands off at a task boundary. Tasks 11 to 27 are each committable on their own.
