# Manifest, Streaky Habit v1.1.0 goldens

**Folder** `docs/design-explore/v1.1.0/final/` (staging, finalize moves it)
**System** `system.md`, `system.css`
**Data** `sample-history.json`, today Saturday 10 October 2026
**Flow** `LINKS.json`
**Checks** `checks/check.py` (render check, `results.json`, `shots/`, `compare/`), `checks/data.py` (histories and contrast from f2), `checks/peek.py` (ink centring probe)

## Inventory to golden

| ID | Screen, popup or state | Golden | State shown | Widths that matter |
|---|---|---|---|---|
| K1 | Habit list with the overview (key screen) | `today.html` | Three habits, today 1 of 3 done, nothing open | all three. Phone shows the Overview button and two-line rows, 1280 the band and one-line rows |
| P1 | Day editor | `day-editor.html` | Tuesday 22 September open, 1 of 3 habits | 360 and 390 (bottom sheet over P3), 1280 (centred over K1 and the band) |
| P2 | Year view of one habit | `year-view.html` | Read 20 pages, Current 4 days, Best 9 | 360 and 390 (full sheet), 1280 (centred dialog, three months across) |
| P3 | Overview popup | `overview.html` | Last 12 weeks, nothing open | 360 and 390 only. The 1280 render is reference, P3 cannot open at 1024 and up |
| P4 | Overview year view | `overview-year.html` | All habits, October 2026 at the top | 360 and 390 (full sheet), 1280 (centred dialog) |
| M1 | Delete dialog | `delete-dialog.html` | Delete "Stretch 10 minutes"? from its row bin | all three |
| S1 | First visit | `today-empty.html` | No habits yet | all three |
| S2 | Name error (three messages) | `states.html` | three composer frames | all three (phone and desktop composer) |
| S3 | Twelve habits | `today-full.html` | twelve rows, field disabled, frame scrolls | all three |
| S4 | Save warning | `states.html` | the warning banner | all three |
| S5 | Saved habits could not be read | `states.html` | the note with Dismiss above the empty list | all three |

## File names
Kept from 1.0 where the job is the same (`today.html`, `today-empty.html`, `delete-dialog.html`, `states.html`). New for new screens (`day-editor.html`, `year-view.html`, `overview.html`, `overview-year.html`). `today-full.html` is new because S3 now changes the whole screen (the list frame scrolls, twelve-segment rings), where 1.0 showed it as a frame on the states sheet.

## Static stand-ins every builder should know
Popups are `<dialog open>` after a `.scrim` element, the page under them is `inert`. The app uses `showModal()` and `::backdrop` instead. P3 in `day-editor.html` carries `.below-desktop`. Ring arcs are `<use>` of shared paths (`#a3-*`, `#a12-*`) with the state class on the `<use>`. The mark is one inline `<svg class="mark">` per page plus the data URL favicon, so the redrawn logo swaps in mechanically.
