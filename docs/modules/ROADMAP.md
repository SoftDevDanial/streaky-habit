# Roadmap: Streaks v0.1.0

> Written by: the solutions architect (sdlc planner), 2026-10-08. Inputs: `docs/brainstorm/brainstorm.md`, `docs/design/` (goldens, `.md` docs, `RULINGS.md`, `sample-history.json`), `CLAUDE.md`, `docs/constitution.md`. No research folder and no repo summary (greenfield).
> Phase skills: the registry assigns none to plan. The `app` builder loads the design row (`taste-skill`, `frontend-design`) because its work is UI.

## Modules

| # | Module | Nature | Depends on | Requirements | Owns |
|---|---|---|---|---|---|
| 1 | `habit-logic` | logic (no UI, no I/O) | none | R1 to R16 | `src/dates.js`, `src/habits.js`, `tests/*.test.js` |
| 2 | `app` | FE, live-composition module | `habit-logic` (Contracts only) | R1 to R28 | `index.html`, `src/styles.css`, `src/app.js`, `src/view.js`, `src/storage.js`, `tests/browser/` |

**Why two modules.** The brief's expected shape holds and nothing argued for changing it. The rules (days, streaks, heatmap levels, name checks, list changes) are pure functions of data and a passed-in day, with no DOM and no clock, so they form one cohesive module that `node --test` can prove exhaustively, including DST and the golden sample. Everything that touches the browser (DOM, storage, clock, dialog, rollover) changes for the same reasons and is wired from the one entry point, so it stays together in `app`, which is also the mandatory live-composition module carrying the cold-boot gate. Splitting `app` further (for example a separate storage module) would put a seam where nothing varies: `localStorage` and `Date` are the only implementations the locked stack allows. The storage codec stays in `app` because the stored format is the app's persistence contract; it reuses `validateName` and `isDateKey` from `habit-logic` rather than restating the rules.

## Build order
1. **`habit-logic`**: independent, so first. Done when `node --test "tests/**/*.test.js"` is green for every `@R` scenario, code review passes and security passes. No fidelity gate (no UI).
2. **`app`**: after `habit-logic`. Done when the browser suite (`python -m pytest tests/browser -q` against the running app) is green, code review and security pass, the fidelity gate is 1-to-1 (6 captures plus the states sheet), and the cold-boot live-e2e gate (`@R27`) passes with its evidence artifact in `docs/modules/app/qa/live-e2e/<datetimestamp>/`.

No dependency deadlock: `app` uses `habit-logic`, never the reverse.

```
habit-logic  -->  app (index.html, composition root, cold-boot gate)
```

## Capability trace
| Brainstorm item | habit-logic | app |
|---|---|---|
| C1 Add a habit (name rules, 12 limit, order) | R13, R14 | R10, R11, R12 |
| C2 Tick the week (7 days, only these editable) | R5, R9 | R7, R8 |
| C3 Current streak (does not break until today ends) | R6 | R6, R8 |
| C4 Best streak | R7 | R6 |
| C5 12-week heatmap (levels, Monday weeks, blanks) | R10, R11, R12 | R9 |
| C6 Delete a habit (confirmation, history gone) | R15 | R13, R14, R15 |
| C7 Kept on the device (saved, unreadable reset) | | R16, R17, R18 |
| Days are local calendar days | R1, R2, R3 | R19, R20 |
| Rolling over midnight | | R19, R20 |
| Platform: phone 360+, keyboard, focus, reduced motion, English | R4 | R4, R21, R22, R23 |
| Nothing leaves the device, no accounts | | R24, R25 |
| Live composition, no seed, cold boot | | R1, R26, R27 |
| 1-to-1 with the goldens | | R2, R28 |

Golden coverage: `today.html` (S1 rows), `today-empty.html` (S2 rows), `delete-dialog.html` (M1 rows) and `states.html` (ST rows) are all in `app/qa.md`'s FE element checklist. `states.html` is a specimen sheet, checked by computed style and Gherkin, never by a pixel diff.

## Clarify gate
All items are closed. CG-1 was resolved by a CLAUDE.md change during planning. CG-2 to CG-9 were ruled on 2026-10-08 by the orchestrator under the owner's delegation (ORCH: reversible, the owner may overturn any of them). The specs follow the rulings and mark each affected place with the item's number. The planning-time recommendation is kept beside each ruling as the record.

| # | Status | Question | Recommended at planning | Ruling |
|---|---|---|---|---|
| CG-1 | Resolved 2026-10-08 | The unit-test command `node --test tests/` in CLAUDE.md exits 1 on Node 24.11.1 ("Cannot find module ...\tests", measured in a scratch copy). | CLAUDE.md now reads `node --test "tests/**/*.test.js"` (changed on disk during planning). Both specs use it. | CLAUDE.md now reads `node --test "tests/**/*.test.js"` (changed on disk during planning). Both specs use it. |
| CG-2 | Ruled 2026-10-08, ORCH | The stock `harness/fidelity.py` cannot reach S1 or M1: it has no clock control, no storage seeding and no gesture step, and its frozen init script pins `Date.now` to 1700000000000 (14 Nov 2023), which conflicts with a clock fixed to 8 Oct 2026. Only S2 on the real date 8 Oct 2026 would be reachable, by coincidence. **Correction (2026-10-08, orchestrator, measured):** this row first also said the 2.1.0 frozen init script pinned `Date.now` to 1700000000000 (14 Nov 2023). That was wrong: the script was an uninvoked arrow function and pinned nothing. | The `app` builder writes `tests/browser/fidelity_capture.py`: the golden through the harness's own `render()`, the candidate with the same launch flags and context plus `page.clock`, the Asia/Kuala_Lumpur zone, seeding from `sample-history.json` and a real click for M1, then the harness's own `diff_images()` and `STYLE_DUMP_JS`, writing the same five files. The fidelity tester runs this driver instead of `fidelity.py` directly. | **Resolved in the plugin instead.** sdlc 2.1.1 `harness/fidelity.py` adds `--candidate-init-script <file.js>` (runs before the app's scripts; seeds storage), `--candidate-after-load <file.js>` (runs after load, may await; opens the dialog), `--fixed-time <ISO local datetime>` (Playwright clock for both renders, covering `Date.now()` and `new Date()`) and repeatable `--browser-arg`. The custom capture driver is dropped. The fidelity tester runs the plugin harness; the two state scripts stay test-side in `tests/browser/fidelity/`. Every Streaks run passes `--fixed-time 2026-10-08T09:00:00`, because 2.1.1 always pins time (default 2023-11-14T22:13:20Z). The measured 0-pixel budget is kept, re-measured with 2.1.1 (D8). Changed 2026-10-08 (plan-check flag, ORCH): this ruling first credited the four state flags to "sdlc 2.1.1" ("sdlc 2.1.1 `harness/fidelity.py` adds ..." above). Corrected from the plugin CHANGELOG, see the version history under Measurements: 2.1.0 added the four flags, 2.1.1 fixed the freeze (time is always pinned through Playwright's clock), 2.1.2 added `bypass_csp`. The minimum stays "2.1.1 or later" and `--fixed-time 2026-10-08T09:00:00` stays on every run. The first fidelity run on 2.1.2 must confirm the 0-pixel baseline measured on 2.1.1 (D8). |
| CG-3 | Ruled 2026-10-08, ORCH | Moving the golden's `.scrim` element to the app's native `::backdrop` (as delete-dialog.md requires) breaks two things in the golden CSS: (a) `background: var(--scrim)` on `::backdrop` is transparent in Chrome and Edge before 122 and Safari before 17.4, which the approved floor includes (Chrome 105+, Safari 15.4+), so the dialog opens with no dim and its edge loses the 3:1 contrast the scrim gives; (b) the reduced-motion rule `*, *::before, *::after` does not reach `::backdrop`, so the backdrop still fades for 180ms under reduced motion (measured), against system.md "both appear at once". | Two additions to the copied CSS, recorded in `app` R2: `background: var(--scrim, rgb(28 37 35 / 0.5))` (same colour, renders identically on current browsers) and `::backdrop` added to the reduced-motion selector list. | Accepted as recommended: the `var(--scrim, rgb(28 37 35 / 0.5))` fallback and `::backdrop` in the reduced-motion selector (`app` R2). |
| CG-4 | Ruled 2026-10-08, ORCH | The brainstorm says the app resets when saved data "cannot be read" but does not say which values count. This decides when a user loses data. | Unreadable = not JSON; not an object; `version` not 1; `habits` not an array of 0 to 12; a name that breaks the name rules (untrimmed, empty, over 40, duplicate ignoring case); a `done` that is not an array of real dates. Lossless oddities are repaired, not reset: unknown extra properties are ignored, `done` is sorted and de-duplicated, dates after today are kept (a clock or time-zone change can create them). On a reset the empty state is saved at once, so "the list was reset" is true and the note shows once, returning only when a later load fails again. Full rule in `app` spec, Storage contract. | Accepted as recommended, including saving the empty state at once after a reset (`app` R17 and the Storage contract). |
| CG-5 | Ruled 2026-10-08, ORCH | No design or copy covers storage being unusable (blocked by the browser) or a failed save (quota or security error). | Never crash. If storage cannot be used at load, start empty without the S5 note (nothing was reset). If a save fails, keep the change on screen for the session and show nothing. Residual: in such a browser the habits are lost on reload without a warning. | Accepted as recommended: keep working in memory, never crash (`app` R18). Recorded as an accepted residual. |
| CG-6 | Ruled 2026-10-08, ORCH | `docs/design-explore/FLOW-CHECK.md` exercised a backdrop click as a dialog exit (PASS), but that came from the flow-check wiring script. `delete-dialog.md`, `system.md` and `RULINGS.md` name only Cancel and Esc. | A backdrop click does nothing (the native `showModal()` behaviour, nothing added). | **Ruled against the recommendation: a backdrop click acts as Cancel** (same result as Cancel, including focus return to the trash button). This matches the design flow check and the Split app. `app` R14, its Contracts (press and release both outside the dialog box) and the `@R13`/`@R14` scenarios follow it. |
| CG-7 | Ruled 2026-10-08, ORCH | Two actions remove or disable the focused control and no approved rule says where focus goes: (a) Dismiss on the S5 note (the button disappears); (b) the 12th add (the input and Add become disabled). | (a) Focus moves to the "New habit" input when it is enabled. (b) The app does not move focus (the browser returns it to the document); the S4 note is announced through the existing live message line. | Accepted as recommended (`app` R12 and R17). |
| CG-8 | Ruled 2026-10-08, ORCH | "1 to 40 characters" does not say what a character is. | Unicode code points (`Array.from(name).length`). Counting graphemes needs `Intl.Segmenter`, which Firefox 121 to 124 (inside the floor) lack, and counting UTF-16 units would make one emoji count as 2. The duplicate check compares `toLowerCase()` of both trimmed names. | Accepted: Unicode code points (`habit-logic` R13). |
| CG-9 | Ruled 2026-10-08, ORCH | The brainstorm does not cover two open tabs. | No cross-tab sync in v0.1.0. Each tab keeps its own state and the last save wins, so a stale tab can overwrite ticks made in another. Recorded as an accepted residual. | Accepted: no sync, last save wins. Recorded as an accepted residual. |

## Architect decisions (within the plan's remit, reversible)
| # | Decision | Why |
|---|---|---|
| D1 | Storage key `streaks.state`, value `{"version":1,"habits":[{"name","done"}]}` | Mirrors the habit shape of `sample-history.json`, so tests seed the sample directly. A specific key because all of one user's GitHub Pages sites share an origin. |
| D2 | A meta Content Security Policy: `default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'` | Enforces "nothing leaves the device" and backs up text-only rendering of names. `'unsafe-inline'` for styles keeps the goldens' inline `style` attributes. Measured: `form-action 'none'` does not block the dialog's `method="dialog"` form; `connect-src 'none'` refuses `fetch`. |
| D3 | Renders are synchronous; a tick updates the existing day button and heat cell in place | The system.md bead and dot transitions can only run on an element that persists, focus stays put, and Playwright's paused clock cannot stall a render. |
| D4 | Rollover check every 30 seconds plus `visibilitychange` | Meets "within a minute" with margin for timer jitter. The header date and streak lines roll over with the strips because they derive from the same day. |
| D5 | Tests use the `Asia/Kuala_Lumpur` zone (UTC+8, no DST) and instants with an explicit `+08:00` | Results do not depend on the test machine's zone. DST is proven in the `habit-logic` unit tests under `America/New_York`. |
| D6 | Functional tests seed through a same-origin 404 page (`<base>__seed__`) before the app loads; the fidelity gate seeds through the harness's `--candidate-init-script` | No app code runs before the seed, and nothing in the shipped app knows about seeding. |
| D7 | The hidden tab is simulated test-side (`visibilityState` getter plus a `visibilitychange` event) | Measured: headless Chromium keeps `visibilityState` "visible" when another tab is brought to the front and when the window is minimised through CDP. |
| D8 | Fidelity budget 0 mismatched pixels at per-pixel threshold 0.1 | Measured, first with a planning probe and again with harness 2.1.1 and `--fixed-time 2026-10-08T09:00:00`: the S1 golden against itself gives 0 pixels; a native modal with `::backdrop` against the M1 golden gives 0 pixels at 390 and 1280 once the after-load script blurs the script-focused Cancel (D12). Added 2026-10-08: these zeros were measured on 2.1.1 and the installed harness is 2.1.2 (which adds `bypass_csp` only). The first fidelity run on 2.1.2 must confirm the 0-pixel baseline before the budget is trusted. A non-zero count on 2.1.2 that was 0 on 2.1.1 is reported to the owner and is not absorbed into the budget. |
| D12 | The M1 after-load script ends with `document.activeElement.blur()` | The golden draws no focus. Script focus without a prior pointer gesture matches `:focus-visible` in Chromium, and that Cancel ring was the whole diff (877 pixels at 390, 977 at 1280, measured with 2.1.1). Focus on Cancel is proven by `@R13`. |
| D13 | A backdrop click (CG-6) counts only when both the press and the release land outside the dialog box | Clicks on `::backdrop` and on the dialog's padding both target the dialog element, so the box test is needed; the press test keeps a text-selection drag from the title from closing the dialog. |
| D9 | After Delete habit, "the next habit" is the one directly below; deleting the bottom habit focuses the input | RULINGS rule 1 read literally ("the next habit's trash button or "New habit""). |
| D10 | After a rejected submit the input has focus, also after a click on Add | states.md "Focus stays in the input" and "so the user can fix it". |
| D11 | Heat cell names always say "habits" ("1 of 1 habits") | The approved formula in system.md, applied literally as RULINGS did for "0 of 0 habits". |

## Measurements taken while planning (scratch scripts outside the project)
- `sample-history.json` independently re-derived: strips, current streaks 6, 3, 1, best streaks 14, 9, 4, `data-run-continues` only on Stretch, all 81 heat levels, month columns 1, 3, 8, 12. All match the goldens.
- The component CSS block is byte-identical in all four goldens; the M1 page body equals the S1 body apart from `inert`.
- Node 24.11.1: `node --test tests/` fails, the quoted glob and bare `node --test` pass; ES module syntax is detected without `package.json`; a runtime `process.env.TZ` change takes effect at once.
- Python 3.14: `http.server` serves `.js` as `text/javascript`; Playwright 1.61 with Chromium 149; pytest available.
- Playwright clock: `run_for` fires interval timers deterministically across midnight, `set_system_time` fires none, an installed clock otherwise follows wall time.
- Golden full-page sizes: S1 and M1 are 390 x 1136 and 1280 x 837.
- Harness 2.1.1 (after the rulings): `--fixed-time 2026-10-08T09:00:00` with an after-load script on a native-dialog copy of M1 gives 877 pixels at 390 and 977 at 1280, all of them the Cancel focus ring; `--disable-lcd-text` leaves both counts unchanged; ending the script with a blur gives 0 and 0.
- Harness version history (corrected 2026-10-08 from the plugin CHANGELOG; earlier text in the CG-2 row and in the `app/spec.md` header credited the four state flags to 2.1.1): 2.1.0 added `--candidate-init-script`, `--candidate-after-load`, `--fixed-time` and repeatable `--browser-arg`; 2.1.1 fixed the freeze so time is always pinned through Playwright's clock (default 2023-11-14T22:13:20Z); 2.1.2 added `bypass_csp` and nothing else. Minimum for Streaks is 2.1.1 or later. The installed harness is 2.1.2. Streaks should render the same on 2.1.2 because its CSP already allows inline styles (D2), but that stays unmeasured until the first fidelity run on 2.1.2 confirms the 0-pixel baseline of D8.

## Residuals to carry into the change ledger
- Safari and Firefox are inside the browser floor but are not tested (CLAUDE.md allows headless Chromium only).
- Clickjacking cannot be blocked from a meta CSP on GitHub Pages; storage partitioning limits the impact.
- CG-5, accepted residual (ruled 2026-10-08, ORCH): where storage is blocked or a save fails, the app works for the session but changes are lost on reload, without a warning.
- CG-9, accepted residual (ruled 2026-10-08, ORCH): two open tabs do not sync and the last save wins, so a stale tab can overwrite ticks made in another.
