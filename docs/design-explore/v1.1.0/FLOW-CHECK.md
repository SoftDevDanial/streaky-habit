# Flow check, v1.1.0

**Run:** 2026-10-11 11:56 · **Method:** headless Chromium (Python Playwright), one fresh page per link, at the width the link
exists at (360 x 780, 390 x 844 or 1280 x 800). The prototype is `v1.1.0/prototype/`, a copy of `v1.1.0/final/` with
one wiring script per page. The wiring script is not part of any golden.

| width | from | trigger | expected | landed on | console | result |
|---|---|---|---|---|---|---|
| 390 | today.html | button "Overview, today 1 of 3 habits done" | overview.html | overview.html | clean | PASS |
| 1280 | today.html | button "Year view, all habits" | overview-year.html | overview-year.html | clean | PASS |
| 1280 | today.html | button "Tue 22 Sep, 1 of 3 habits" | day-editor.html | day-editor.html | clean | PASS |
| 360 | today.html | button "Year view, Read 20 pages" | year-view.html | year-view.html | clean | PASS |
| 390 | today.html | button "Year view, Read 20 pages" | year-view.html | year-view.html | clean | PASS |
| 1280 | today.html | button "Year view, Read 20 pages" | year-view.html | year-view.html | clean | PASS |
| 360 | today.html | button "Delete "Stretch 10 minutes"" | delete-dialog.html | delete-dialog.html | clean | PASS |
| 390 | today.html | button "Delete "Stretch 10 minutes"" | delete-dialog.html | delete-dialog.html | clean | PASS |
| 1280 | today.html | button "Delete "Stretch 10 minutes"" | delete-dialog.html | delete-dialog.html | clean | PASS |
| 390 | overview.html | button "Tue 22 Sep, 1 of 3 habits" | day-editor.html | day-editor.html | clean | PASS |
| 390 | overview.html | button "Year view, all habits" | overview-year.html | overview-year.html | clean | PASS |
| 390 | overview.html | button "Close" | today.html | today.html | clean | PASS |
| 390 | overview.html | key Escape | today.html | today.html | clean | PASS |
| 360 | overview-year.html | button "Tue 22 Sep 2026, 1 of 3 habits" | day-editor.html | day-editor.html | clean | PASS |
| 390 | overview-year.html | button "Tue 22 Sep 2026, 1 of 3 habits" | day-editor.html | day-editor.html | clean | PASS |
| 1280 | overview-year.html | button "Tue 22 Sep 2026, 1 of 3 habits" | day-editor.html | day-editor.html | clean | PASS |
| 390 | overview-year.html | button "Close" | overview.html | overview.html | clean | PASS |
| 390 | overview-year.html | key Escape | overview.html | overview.html | clean | PASS |
| 1280 | overview-year.html | button "Close" | today.html | today.html | clean | PASS |
| 1280 | overview-year.html | key Escape | today.html | today.html | clean | PASS |
| 1280 | overview-year.html | click at [10, 10] (backdrop) | today.html | today.html | clean | PASS |
| 390 | day-editor.html | button "Close" | overview.html | overview.html | clean | PASS |
| 390 | day-editor.html | key Escape | overview.html | overview.html | clean | PASS |
| 390 | day-editor.html | click at [10, 10] (backdrop above the bottom sheet) | overview.html | overview.html | clean | PASS |
| 1280 | day-editor.html | button "Close" | today.html | today.html | clean | PASS |
| 1280 | day-editor.html | key Escape | today.html | today.html | clean | PASS |
| 1280 | day-editor.html | click at [10, 10] (backdrop) | today.html | today.html | clean | PASS |
| 360 | year-view.html | button "Close" | today.html | today.html | clean | PASS |
| 390 | year-view.html | button "Close" | today.html | today.html | clean | PASS |
| 1280 | year-view.html | button "Close" | today.html | today.html | clean | PASS |
| 360 | year-view.html | key Escape | today.html | today.html | clean | PASS |
| 390 | year-view.html | key Escape | today.html | today.html | clean | PASS |
| 1280 | year-view.html | key Escape | today.html | today.html | clean | PASS |
| 1280 | year-view.html | click at [10, 10] (backdrop) | today.html | today.html | clean | PASS |
| 360 | year-view.html | button "Delete habit" | delete-dialog.html | delete-dialog.html | clean | PASS |
| 390 | year-view.html | button "Delete habit" | delete-dialog.html | delete-dialog.html | clean | PASS |
| 1280 | year-view.html | button "Delete habit" | delete-dialog.html | delete-dialog.html | clean | PASS |
| 360 | delete-dialog.html | button "Cancel" | today.html | today.html | clean | PASS |
| 390 | delete-dialog.html | button "Cancel" | today.html | today.html | clean | PASS |
| 1280 | delete-dialog.html | button "Cancel" | today.html | today.html | clean | PASS |
| 360 | delete-dialog.html | key Escape | today.html | today.html | clean | PASS |
| 390 | delete-dialog.html | key Escape | today.html | today.html | clean | PASS |
| 1280 | delete-dialog.html | key Escape | today.html | today.html | clean | PASS |
| 360 | delete-dialog.html | click at [10, 10] (backdrop) | today.html | today.html | clean | PASS |
| 390 | delete-dialog.html | click at [10, 10] (backdrop) | today.html | today.html | clean | PASS |
| 1280 | delete-dialog.html | click at [10, 10] (backdrop) | today.html | today.html | clean | PASS |
| 360 | states.html | button "Dismiss note" | today-empty.html | today-empty.html | clean | PASS |
| 390 | states.html | button "Dismiss note" | today-empty.html | today-empty.html | clean | PASS |
| 1280 | states.html | button "Dismiss note" | today-empty.html | today-empty.html | clean | PASS |

**Result:** 49 of 49 links pass. Zero errors.
