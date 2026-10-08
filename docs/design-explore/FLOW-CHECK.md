# Flow check

**Run:** 2026-10-08 15:52 · **Method:** headless Chromium (Python Playwright) at 390 x 844, one fresh page per link.
The prototype is `prototype/`, a copy of `final/` with one wiring script per page. The wiring script is
not part of any golden.

| from | trigger | expected | landed on | console | result |
|---|---|---|---|---|---|
| today-empty.html | button "Add" | today.html | today.html | clean | PASS |
| today.html | button "Delete Read 20 pages" | delete-dialog.html | delete-dialog.html | clean | PASS |
| delete-dialog.html | button "Cancel" | today.html | today.html | clean | PASS |
| delete-dialog.html | key Escape | today.html | today.html | clean | PASS |
| delete-dialog.html | click at [10, 10] (backdrop) | today.html | today.html | clean | PASS |
| delete-dialog.html | button "Delete habit" | today.html | today.html | clean | PASS |

**Result:** 6 of 6 links pass. Zero errors.

**Two links land on an approximation.** "Add" from the empty screen and "Delete habit" from the dialog
both go to `today.html`, the closest designed screen. The real app adds one habit or removes one. The
check proves the trigger and the close are wired, not the resulting data.
