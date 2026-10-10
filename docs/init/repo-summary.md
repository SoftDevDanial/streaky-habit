# Repo summary: Streaks

Written at review on 2026-10-10, once the v1.0.0 build was approved for the owner's test.

## What it is
A daily habit tracker on one web page. Add up to 12 habits, tick the last 7 days, see each habit's current and best
streak and one 12-week heatmap for all habits. Everything is saved in the browser's `localStorage`. No account,
no server, no network call, no dependencies, no build step.

## Where things are
| Path | What it holds |
|---|---|
| `index.html` | the page, with its Content Security Policy |
| `src/dates.js`, `src/habits.js` | `habit-logic`: every rule about days, streaks, the heatmap and names, as pure functions |
| `src/app.js` | boots the page, handles every gesture, reads the clock, rolls over at midnight |
| `src/view.js` | builds and updates the page's elements, owns every selector |
| `src/storage.js` | saves and loads the list, treats stored text as untrusted |
| `src/styles.css` | the approved design's stylesheet with three marked changes |
| `tests/` | Node unit tests (99) and Python Playwright browser tests (179), plus the live gate script |
| `docs/brainstorm/`, `docs/design/` | what was asked for and the approved screens (immutable outside the design phase) |
| `docs/modules/<module>/` | each module's spec, test contract, build notes, findings and evidence |
| `docs/v1.0.0/CHANGE-LEDGER.md` | every scope, decision, finding and fix of this version, dated, with who decided |
| `docs/regression/`, `docs/review/` | the last full re-check and the stakeholder review drive |
| `docs/brand/` | the logo, README badges and showcase image |
| `docs/progress/` | the run's state, its log and the process ledger |

## How to run and test it
Serve the folder (`python -m http.server 8000 --bind 127.0.0.1`) and open it. Unit tests `node --test "tests/**/*.test.js"`,
browser tests `python -m pytest tests/browser -q`. The README has the gates.

## What to know before changing it
- Dates are local calendar days, `YYYY-MM-DD`. `readToday` in `src/app.js` is the only place the clock is read.
- Time-dependent tests use Playwright's clock. Never add a test hook to the app.
- Only `index.html`, `src/` and a `.nojekyll` file are ever published.
- The delete dialog's two 500 ms guards are deliberate (security SEC-01). v1.1.0 replaces the Delete habit one with a guard that does not depend on time.
