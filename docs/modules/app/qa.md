# QA: app

> Test contract. Functional cases run against the RUNNING app; fidelity runs after functional is green.
> Every scenario is tagged `@R#` and maps to a requirement in `spec.md`.
> Written by: the solutions architect (sdlc planner), 2026-10-08.

## How these scenarios run

### The running app
- Serve from the project root, on a free port, bound to loopback only:
  `python -m http.server <port> --bind 127.0.0.1`
  The app is at `http://127.0.0.1:<port>/`. Python serves `.js` as `text/javascript` here (measured), which ES modules need.
- The `@R1` sub-path scenario needs a second server for the parent folder of the project root:
  `python -m http.server <port2> --bind 127.0.0.1 --directory ..` (run from the project root), app at `http://127.0.0.1:<port2>/streaks/`.

### The tests
- The builder implements every scenario below as pytest test functions in `tests/browser/test_*.py`, using Playwright's sync API directly (headless Chromium only) and the shared fixtures and helpers in `tests/browser/conftest.py`. pytest-playwright is not installed and is not needed.
- Test function names start with the tag, for example `test_R8_tick_today_on_stretch`, so `-k R8` selects a requirement. A Scenario Outline may be `pytest.mark.parametrize` over its Examples rows or one function looping over them. Each row is asserted.
- Command (Git Bash), from the project root, capped at 15 minutes:
  `STREAKS_BASE_URL=http://127.0.0.1:<port>/ STREAKS_SUBPATH_URL=http://127.0.0.1:<port2>/streaks/ STREAKS_EVIDENCE_DIR=docs/modules/app/qa/functional/<datetimestamp>/ timeout 900 python -m pytest tests/browser -q -rA`
  This is the CLAUDE.md command `python -m pytest tests/browser -q` with the environment it needs. `-rA` only adds a one-line outcome per test so the finder can map results to `@R` tags. Changed 2026-10-09 (code-review WR-10, ORCH): the environment is optional now. The bare CLAUDE.md command starts and stops its own two servers (see the conftest table), so a finder who wants its own servers keeps the variables and everyone else leaves them out.
- The QA finder runs the suite and also reads each test against its scenario. A test whose assertions are weaker than the scenario's `Then` lines is a FAIL of that scenario even when green. A skipped test (for example `@R1` sub-path without `STREAKS_SUBPATH_URL`) is BLOCKED, never PASS.
- Every Playwright wait has a timeout (5 seconds per expectation unless a step says otherwise). No unbounded wait anywhere.

### Rules every test follows
- **Real gestures only** for user actions: `click`, `hover`, `keyboard.type`, `keyboard.press`, `mouse.*`, `fill` for typing into the field. Tests never call app code (the app exposes none) and never write app state except by seeding `localStorage` before the app loads.
- **Reading is allowed**: DOM attributes and text, computed styles, `localStorage.getItem`, `document.activeElement`.
- **Time** is controlled only with Playwright's clock (`page.clock`), never with a hook in the app. Every context uses `timezone_id="Asia/Kuala_Lumpur"` (UTC+8 all year, no DST) and every instant is written with an explicit `+08:00` offset, so results do not depend on the machine's zone. DST is covered by the habit-logic unit tests.
- **Seeding** (finders only, never the shipped default): before the app loads, open `<base>__seed__` (a same-origin 404 page from `http.server`, so no app code runs), call `localStorage.setItem("streaks.state", <text>)`, then open the app URL. The fidelity gate seeds differently, through the plugin harness's `--candidate-init-script` (see Fidelity gate).
- **Hiding the tab** is simulated test-side: override the `document.visibilityState` and `document.hidden` getters on the page with `Object.defineProperty` and dispatch a `visibilitychange` event on `document`. Measured 2026-10-08 on headless Chromium 149: bringing another tab to the front and minimising the window through CDP both leave `visibilityState` at "visible", so a real hide is not available headless.
- `docs/design/` is read-only. Tests read `sample-history.json` and the golden HTML files and never write there.

### `tests/browser/conftest.py` (shared fixtures and helpers, at least these)
| Helper | Does |
|---|---|
| `browser` fixture | one headless Chromium per session, launched with `--force-color-profile=srgb`, closed at session end |
| `BASE_URL`, `SUBPATH_URL`, `EVIDENCE_DIR` | from `STREAKS_BASE_URL` (ends with `/`), `STREAKS_SUBPATH_URL`, `STREAKS_EVIDENCE_DIR`. Changed 2026-10-09 (code-review WR-10, ORCH): `STREAKS_BASE_URL` is no longer required. When it is absent, `pytest_configure` starts `python -m http.server <free port> --bind 127.0.0.1` for the project root and another for its parent folder (the sub-path scenario, unless `STREAKS_SUBPATH_URL` is set), waits for each with a bounded poll, and stops both at the end, checking that both ports refuse connections. |
| `SAMPLE_HABITS`, `sample_state()` | the habits of `docs/design/sample-history.json` (read-only) and the text `{"version":1,"habits":[...]}` |
| `TZ`, `NOON` | `"Asia/Kuala_Lumpur"`, `"2026-10-08T12:00:00+08:00"` |
| `open_app(browser, viewport=(390, 844), locale="en-US", reduced_motion="no-preference", fixed_time=NOON, install_time=None, storage=None, init_script=None, record=False, path="")` | new context (viewport, `device_scale_factor=1`, `color_scheme="light"`, `timezone_id=TZ`, locale, reduced motion), the clock (`set_fixed_time` or `install`), then in this order: (1) seeding, when `storage` is given (open `BASE_URL + "__seed__"` in the context and call `localStorage.setItem("streaks.state", storage)`); (2) the init script, when `init_script` is given (`context.add_init_script`, so it applies to the app's page load and later documents and never to the seeding page); (3) recording, when `record=True` (calls `record(page)`, so the `GET /__seed__` request is not in the log); (4) opens `BASE_URL + path`; returns context and page. Changed 2026-10-08 (plan-check flag, ORCH): the order first read "optional init script, optional seeding, then opens". With an init script that makes `Storage.prototype.setItem` throw (`@R18` "A save that fails") the seeding page threw on its own `setItem`, and `@R25` had no point at which `record(page)` could start after seeding and before the app opens. Scenarios that assert on requests, console messages or page errors open with `record=True`. |
| `hide_tab(page)`, `show_tab(page)` | the visibility simulation above |
| `record(page)` | collects requests, console messages and page errors from that point on. Added 2026-10-08: it returns the page's log, and a second call returns the same log without resetting it, so a test opened with `open_app(..., record=True)` reads the log with `record(page)` |
| `stored(page)` | `localStorage.getItem("streaks.state")` |
| `row(page, name)`, `day(page, name, date)`, `cell(page, date)` | locators by habit name, `data-date` and heat cell |

### Named starting states
- **the sample day**: `open_app` with the clock fixed at `2026-10-08T12:00:00+08:00` and storage seeded with `sample_state()`. Today is Thursday 8 October 2026. Habits in order: "Read 20 pages", "Stretch 10 minutes", "No phone after 11pm".
- **a fresh day**: `open_app` with the clock fixed at `2026-10-08T12:00:00+08:00` and no storage at all.
- **N plain habits**: storage `{"version":1,"habits":[{"name":"Habit 1","done":[]}, ..., {"name":"Habit N","done":[]}]}`, clock as above.

### Processes and evidence
- The QA finder starts each server in the background, records its PID, waits for it to answer (polls the URL every 250 ms, gives up after 10 seconds and reports BLOCKED), runs the suite, stops each server by PID, and confirms the port refuses connections. All of this goes in its `PROCESSES` block.
- Screenshots or logs a test saves go to `STREAKS_EVIDENCE_DIR` (`docs/modules/app/qa/functional/<datetimestamp>/`). The verdict goes to `docs/modules/app/findings/qa.md`.

## Functional test cases (Gherkin)

```gherkin
Feature: Shipped entry point

  @R1
  Scenario: Head, CSP and relative URLs
    Given the file index.html at the project root
    Then it starts with "<!doctype html>" and its html element has lang "en"
    And its head children, ignoring comments, are in order: meta charset "utf-8"; meta http-equiv "Content-Security-Policy" with content "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'"; meta name "viewport" content "width=device-width, initial-scale=1"; title "Streaks"; link rel "stylesheet" href "src/styles.css"; script type "module" src "src/app.js"
    And a comment in the head names Phosphor Icons (MIT)
    And no src or href attribute in index.html starts with "/" or contains "://"
    And every import specifier in src/*.js starts with "./"

  @R1
  Scenario: The app works from a sub-path
    Given the project's parent folder is served and the clock is fixed at 2026-10-08T12:00:00+08:00 with no storage
    When the page opens SUBPATH_URL
    Then p.empty starts with "No habits yet." and div.cells has 84 children
    And the user can add "Read 20 pages" with the field and Add, and one li.habit appears

  @R1
  Scenario: The static skeleton
    Given a fresh day
    Then the body's element children are, in order, the sprite svg, div.page and dialog.dialog
    And the sprite has width "0", height "0", aria-hidden "true" and symbols "i-check", "i-trash" and "i-x" whose path data equal the goldens' (i-check and i-trash from today.html, i-x from states.html)
    And the dialog is closed and has role "alertdialog", aria-modal "true", aria-labelledby "del-title", aria-describedby "del-body"

  @R2
  Scenario: The stylesheet is the golden CSS with the three listed changes
    Given the text of src/styles.css and the text of the style element of docs/design/today.html from ":root {" through "/* ---------- end components ---------- */"
    When the golden text gets the three changes of spec R2 (remove the .scrim rule and the ".scrim, " in the scrim-in selector; backdrop background "var(--scrim, rgb(28 37 35 / 0.5))"; "::backdrop" added to the reduced-motion selector list)
    And both texts have comments removed and runs of whitespace collapsed to one space
    Then the two texts are identical

  @R26
  Scenario: No sample data in the shipped files
    Given the text of index.html and of every file under src/
    Then none contains "Read 20 pages", "Stretch 10 minutes", "No phone after 11pm" or "sample-history"

  @R26
  Scenario Outline: Query strings and fragments do not seed
    Given the clock is fixed at 2026-10-08T12:00:00+08:00 and there is no storage
    When the page opens "<path>"
    Then p.empty is shown, there is no li.habit, and stored(page) is null

    Examples:
      | path       |
      | ?demo=1    |
      | ?seed      |
      | #sample    |

  @R26
  Scenario: No globals and no hooks
    Given the sample day
    When the own property names of window are read on the app page and on the same-origin page "__seed__" in the same context
    Then every name present on the app page is also present on the "__seed__" page

Feature: First visit and header

  @R3
  Scenario: The empty first screen
    Given a fresh day
    Then the list section holds p.empty whose strong reads "No habits yet." and whose text content is "No habits yet. Add one you want to do every day."
    And there is no ul.habits and no div.note
    And the input #new-habit is enabled with value "", the Add button is enabled, #new-habit-msg is empty with classes "field-msg field-error", and the input has no aria-invalid
    And div.cells has 84 children: 81 span.hc.l0 with role "img" for 2026-07-20 to 2026-10-08, then span.hc.future with aria-hidden "true" for 2026-10-09, 2026-10-10 and 2026-10-11
    And the cell 2026-07-20 is named "Mon 20 Jul, 0 of 0 habits" and the cell 2026-10-08 is named "Thu 8 Oct, 0 of 0 habits" with classes "hc l0 today" and aria-current "date"
    And stored(page) is null

  @R4
  Scenario: Brand and date
    Given the sample day
    Then h1.brand reads "Streaks"
    And p.date time has datetime "2026-10-08" and text "Thursday 8 October"

  @R4
  Scenario Outline: The date follows the device clock
    Given the clock is fixed at <instant> with no storage
    Then p.date time has datetime "<key>" and text "<text>"

    Examples:
      | instant                   | key        | text                |
      | 2026-10-05T09:00:00+08:00 | 2026-10-05 | Monday 5 October    |
      | 2026-10-07T23:59:59+08:00 | 2026-10-07 | Wednesday 7 October |
      | 2027-01-01T00:00:30+08:00 | 2027-01-01 | Friday 1 January    |

  @R4
  Scenario: English under a German browser locale
    Given the sample day with locale "de-DE"
    Then the date reads "Thursday 8 October"
    And Read's first day button is named "Mark Fri 2 Oct as done"
    And the cell 2026-07-20 is named "Mon 20 Jul, 3 of 3 habits"
    And the month axis reads "Jul", "Aug", "Sep", "Oct"

Feature: Habit rows, streak lines and strips

  @R5
  Scenario: Rows in stored order
    Given the sample day
    Then ul.habits has 3 li.habit whose h3.habit-name texts are "Read 20 pages", "Stretch 10 minutes", "No phone after 11pm" with ids "h1-name", "h2-name", "h3-name"
    And their trash buttons are named "Delete Read 20 pages", "Delete Stretch 10 minutes", "Delete No phone after 11pm" and contain an svg using "#i-trash"
    And each div.strip has role "group" and aria-labelledby equal to its row's h3 id

  @R6
  Scenario Outline: The sample's streak lines
    Given the sample day
    Then the p.streak of "<habit>" has aria-live "polite", a span.cur without class "none" reading "<cur>" and a span.best reading "<best>"

    Examples:
      | habit               | cur    | best    |
      | Read 20 pages       | 6 days | Best 14 |
      | Stretch 10 minutes  | 3 days | Best 9  |
      | No phone after 11pm | 1 day  | Best 4  |

  @R6
  Scenario: No streak yet, with and without a best
    Given the clock is fixed at 2026-10-12T12:00:00+08:00 and storage holds the sample
    Then each of the three streak lines has span.cur with classes "cur none" reading "No streak yet"
    And the span.best texts are "Best 14", "Best 9" and "Best 4"
    When the user adds "Drink water"
    Then the new row's streak line holds only span.cur.none "No streak yet" and no span.best element

  @R7
  Scenario Outline: The sample's week strips
    Given the sample day
    Then the strip of "<habit>" has exactly 7 button.day with type "button" and data-date 2026-10-02 to 2026-10-08 in order
    And their span.wd texts are Fri, Sat, Sun, Mon, Tue, Wed, Thu and their span.dm texts are 2, 3, 4, 5, 6, 7, 8
    And their aria-pressed values read "<pattern>" (D is "true", . is "false")
    And the strip <has> the attribute data-run-continues

    Examples:
      | habit               | pattern       | has         |
      | Read 20 pages       | . D D D D D D | does not have |
      | Stretch 10 minutes  | D D . D D D . | has         |
      | No phone after 11pm | . D . . D . D | does not have |

  @R7
  Scenario: Day names, today, and nothing outside the window
    Given the sample day
    Then the day buttons of every strip are named "Mark Fri 2 Oct as done", "Mark Sat 3 Oct as done", "Mark Sun 4 Oct as done", "Mark Mon 5 Oct as done", "Mark Tue 6 Oct as done", "Mark Wed 7 Oct as done", "Mark Thu 8 Oct as done"
    And only the three 2026-10-08 buttons have aria-current "date"
    And no button in the document has a data-date before 2026-10-02 or after 2026-10-08

  @R7 @R8
  Scenario: The name does not change with the state
    Given the sample day
    When the user clicks Stretch's day 2026-10-08
    Then that button is still named "Mark Thu 8 Oct as done" and its aria-pressed is "true"

Feature: Tick the week

  @R8 @R16
  Scenario Outline: Toggling a day updates the bead in place, the streak, the heatmap and storage
    Given the sample day
    And a handle to the day button <date> of "<habit>"
    When the user clicks that day button
    Then the same handle is still connected to the document and its aria-pressed is "<pressed>"
    And the streak line of "<habit>" reads "<cur>" and "<best>"
    And the strip of "<habit>" <run> the attribute data-run-continues
    And the cell <date> has class "l<level>" and is named "<name>"
    And in stored(page) the done list of "<habit>" <stored> "<date>"

    Examples:
      | habit               | date       | pressed | cur     | best    | run           | level | name                       | stored               |
      | Stretch 10 minutes  | 2026-10-08 | true    | 4 days  | Best 9  | has           | 4     | Thu 8 Oct, 3 of 3 habits   | contains             |
      | Read 20 pages       | 2026-10-08 | false   | 5 days  | Best 14 | does not have | 1     | Thu 8 Oct, 1 of 3 habits   | does not contain     |
      | No phone after 11pm | 2026-10-07 | true    | 3 days  | Best 4  | does not have | 4     | Wed 7 Oct, 3 of 3 habits   | contains             |
      | Stretch 10 minutes  | 2026-10-04 | true    | 7 days  | Best 9  | has           | 2     | Sun 4 Oct, 2 of 3 habits   | contains             |
      | Stretch 10 minutes  | 2026-10-02 | false   | 3 days  | Best 9  | does not have | 0     | Fri 2 Oct, 0 of 3 habits   | does not contain     |
      | Read 20 pages       | 2026-10-02 | true    | 10 days | Best 14 | has           | 2     | Fri 2 Oct, 2 of 3 habits   | contains             |

  @R8
  Scenario: Keyboard toggling keeps focus
    Given the sample day
    When the user presses Tab until Stretch's day 2026-10-08 has focus, then presses Space
    Then that button has aria-pressed "true" and is still document.activeElement
    When the user presses Enter
    Then that button has aria-pressed "false" and is still document.activeElement
    And the streak line of "Stretch 10 minutes" reads "3 days" and "Best 9"

  @R8
  Scenario: Ticking twice restores the saved value
    Given the sample day and the stored text S before any action
    When the user clicks Read's day 2026-10-05 twice
    Then stored(page) parses to the same object as S

Feature: 12-week heatmap

  @R9
  Scenario: The sample's heatmap
    Given the sample day
    Then h2.heat-title reads "Last 12 weeks"
    And div.months is aria-hidden and holds 4 spans: "Jul" with grid-column 1, "Aug" with 3, "Sep" with 8, "Oct" with 12
    And div.wdays is aria-hidden and its 7 spans read "Mon", "", "Wed", "", "Fri", "", "Sun"
    And div.cells holds 84 span.hc whose data-date run from 2026-07-20 to 2026-10-11, one day apart
    And for each of the 81 dates in heatmapLevels of sample-history.json, the cell has class "l<level>" with the file's level, role "img", and the name "<Ddd D Mon>, <n> of 3 habits" where n is the number of sample habits done that day
    And the cell 2026-10-08 has classes "hc l2 today", aria-current "date" and the name "Thu 8 Oct, 2 of 3 habits"
    And no other cell has class "today" or aria-current
    And the cells 2026-10-09, 2026-10-10 and 2026-10-11 have classes "hc future", aria-hidden "true", and no role, name or level class
    And div.legend is aria-hidden and reads "None", then five span.hc with classes l0, l1, l2, l3, l4, then "All"

  @R9
  Scenario: A Monday shows six future cells and a shifted grid
    Given the clock is fixed at 2026-10-12T12:00:00+08:00 with no storage
    Then div.cells runs from 2026-07-27 to 2026-10-18
    And the month labels are "Jul" at 1, "Aug" at 2, "Sep" at 7, "Oct" at 11
    And the cells 2026-10-13 to 2026-10-18 are future
    And the cell 2026-10-12 is named "Mon 12 Oct, 0 of 0 habits" and has class "today"

Feature: Add a habit

  @R10 @R16
  Scenario: First habit on a fresh day (brainstorm flow 1)
    Given a fresh day
    When the user clicks the "New habit" field, types "Read 20 pages" and clicks "Add"
    Then p.empty is gone and ul.habits holds one li.habit with h3#h1-name "Read 20 pages"
    And its 7 day buttons all have aria-pressed "false" and the last has aria-current "date"
    And its streak line holds only span.cur.none "No streak yet"
    And the field's value is "", #new-habit-msg is empty and the input has no aria-invalid
    And the cell 2026-10-08 is named "Thu 8 Oct, 0 of 1 habits" with class l0
    And stored(page) is exactly '{"version":1,"habits":[{"name":"Read 20 pages","done":[]}]}'

  @R10
  Scenario: Enter adds at the bottom, trimmed, and the heatmap recounts
    Given the sample day
    When the user types "  Drink water  " into the field and presses Enter
    Then the fourth li.habit has h3#h4-name "Drink water"
    And the cells read: 2026-07-20 "Mon 20 Jul, 3 of 4 habits" l3; 2026-10-06 "Tue 6 Oct, 3 of 4 habits" l3; 2026-10-08 "Thu 8 Oct, 2 of 4 habits" l2; 2026-07-21 "Tue 21 Jul, 1 of 4 habits" l1; 2026-08-12 "Wed 12 Aug, 0 of 4 habits" l0
    And the last habit in stored(page) is {"name":"Drink water","done":[]}
    And the input still has focus

  @R11
  Scenario Outline: Rejected names keep the text and show one message
    Given the sample day and the stored text S
    When the user types "<typed>" into the field and clicks "Add"
    Then #new-habit-msg reads "<message>" and has classes "field-msg field-error"
    And the input has aria-invalid "true", its value is still "<typed>", and it is document.activeElement
    And there are still 3 li.habit and stored(page) equals S

    Examples:
      | typed                                               | message                            |
      |                                                     | Name the habit first.              |
      |                                                     | Name the habit first.              |
      | Walk to the end of the street and back after dinner | Keep it to 40 characters or fewer. |
      | Read twenty pages before bed every night.           | Keep it to 40 characters or fewer. |
      | read 20 pages                                       | You already track this habit.      |
      |  STRETCH 10 MINUTES                                 | You already track this habit.      |
    # Row 2 types three spaces. Row 6 types " STRETCH 10 MINUTES " with a leading and a trailing space.

  @R11
  Scenario: Exactly 40 characters is accepted
    Given the sample day
    When the user types "Read twenty pages before bed every night" and clicks "Add"
    Then a fourth li.habit has that name and #new-habit-msg is empty

  @R11
  Scenario: No message while typing
    Given the sample day
    When the user types "Walk to the end of the street and back after dinner" without submitting
    Then #new-habit-msg is empty and the input has no aria-invalid

  @R11
  Scenario: One message at a time, replaced, then cleared on success
    Given the sample day
    When the user clicks "Add" with the field empty
    Then #new-habit-msg reads "Name the habit first."
    When the user types "read 20 pages" and presses Enter
    Then #new-habit-msg reads only "You already track this habit."
    When the user clears the field, types "Drink water" and presses Enter
    Then #new-habit-msg is empty, the input has no aria-invalid, and there are 4 li.habit

  @R12
  Scenario: The twelfth habit disables the form
    Given 11 plain habits
    When the user types "Habit 12" and clicks "Add"
    Then there are 12 li.habit
    And the input and the Add button have the disabled attribute
    And #new-habit-msg reads "You track 12 habits, the most this app holds. Delete one to add another." with classes "field-msg field-note"
    And the input's aria-describedby is "new-habit-msg"

  @R12
  Scenario: Twelve habits at load
    Given 12 plain habits
    Then the input and the Add button are disabled and #new-habit-msg holds the 12-habit note with class "field-note"

  @R12 @R15
  Scenario: Deleting one of twelve enables the form again
    Given 12 plain habits
    When the user clicks "Delete Habit 5" and then "Delete habit"
    Then there are 11 li.habit, the input and Add are enabled, and #new-habit-msg is empty with classes "field-msg field-error"

Feature: Delete a habit

  @R13
  Scenario: The confirmation opens as a modal with focus on Cancel
    Given the sample day
    When the user clicks "Delete Read 20 pages"
    Then dialog.dialog is open and matches ":modal"
    And #del-title reads 'Delete "Read 20 pages"?' and #del-body reads "Its history is deleted too."
    And the dialog's buttons are "Cancel" (value "cancel") then "Delete habit" (value "delete")
    And document.activeElement is the Cancel button
    And the computed overflow of html is "hidden"
    When the user scrolls the mouse wheel down by 800 pixels
    Then window.scrollY is 0
    When the user clicks the viewport point at the centre of "Delete Stretch 10 minutes", which lies on the backdrop
    Then the dialog closes as with Cancel and no dialog for "Stretch 10 minutes" ever opens
    And there are still 3 li.habit and document.activeElement is the button named "Delete Read 20 pages"

  @R13
  Scenario: Tab never leaves the dialog for the page
    Given the dialog is open for "Read 20 pages"
    When the user presses Tab 4 times
    Then after each press document.activeElement is not inside div.page

  @R13
  Scenario: A long name wraps in the title and the box keeps its width
    Given the clock is fixed at 2026-10-08T12:00:00+08:00 and storage holds one habit "Read twenty pages before bed every night" with no done days
    When the user clicks "Delete Read twenty pages before bed every night"
    Then the dialog's bounding box is 350 pixels wide at 390 x 844 and its title spans more than one 28 pixel line

  @R14
  Scenario Outline: Cancel, Esc and a backdrop click keep the habit
    Given the sample day and the stored text S
    When the user clicks "Delete Stretch 10 minutes" and then <action>
    Then the dialog is closed
    And there are 3 li.habit, and Stretch's streak line reads "3 days" and "Best 9" and its strip's aria-pressed pattern is "D D . D D D ."
    And stored(page) equals S
    And document.activeElement is the button named "Delete Stretch 10 minutes"

    Examples:
      | action                                                  |
      | clicks "Cancel"                                         |
      | presses Escape                                          |
      | clicks the viewport point (5, 5), which is the backdrop |

  @R14
  Scenario: Clicks inside the box, and drags out of it, keep the dialog open
    Given the sample day and the dialog is open for "Stretch 10 minutes"
    When the user clicks inside the dialog box 6 pixels right of and below its top-left corner (its padding, no button)
    Then the dialog is still open with title 'Delete "Stretch 10 minutes"?'
    When the user presses the mouse button on the title, moves the mouse to the viewport point (5, 5) and releases it there
    Then the dialog is still open

  @R14
  Scenario: Esc after an earlier delete still keeps the habit
    Given the sample day
    When the user deletes "No phone after 11pm" with "Delete habit"
    And then opens the dialog for "Stretch 10 minutes" and presses Escape
    Then "Stretch 10 minutes" is still in the list

  @R15 @R16
  Scenario: Deleting a habit moves focus to the next one and recounts
    Given the sample day
    When the user clicks "Delete Read 20 pages" and then "Delete habit"
    Then the dialog is closed and there are 2 li.habit: "Stretch 10 minutes" (h1-name) and "No phone after 11pm" (h2-name)
    And document.activeElement is the button named "Delete Stretch 10 minutes"
    And the cells read: 2026-07-20 "Mon 20 Jul, 2 of 2 habits" l4; 2026-07-21 "Tue 21 Jul, 1 of 2 habits" l2; 2026-10-08 "Thu 8 Oct, 1 of 2 habits" l2
    And stored(page) holds the two remaining sample habits, unchanged, and no "Read 20 pages"

  @R15
  Scenario: Deleting the bottom habit moves focus to the field
    Given the sample day
    When the user clicks "Delete No phone after 11pm" and then "Delete habit"
    Then document.activeElement is the input #new-habit
    And the cell 2026-10-08 is named "Thu 8 Oct, 1 of 2 habits" with class l2

  @R15
  Scenario: Deleting the only habit shows the empty message
    Given a fresh day
    When the user adds "Read 20 pages", clicks its day 2026-10-08, then deletes it with "Delete habit"
    Then p.empty is shown, there is no ul.habits, and document.activeElement is the input #new-habit
    And the cell 2026-10-08 is named "Thu 8 Oct, 0 of 0 habits" with class l0
    And stored(page) is exactly '{"version":1,"habits":[]}'

  @R15
  Scenario: History goes with the habit
    Given the sample day
    When the user deletes "Stretch 10 minutes" and then adds "Stretch 10 minutes"
    Then the new last row's 7 day buttons are all aria-pressed "false" and its streak line is "No streak yet" with no best

Feature: Kept on the device

  @R16
  Scenario: Changes survive a reload and a closed tab
    Given the sample day
    When the user clicks Stretch's day 2026-10-08, adds "Drink water", and deletes "No phone after 11pm"
    And the page reloads
    Then the rows are "Read 20 pages", "Stretch 10 minutes", "Drink water"
    And Stretch's day 2026-10-08 has aria-pressed "true" and its streak line reads "4 days" and "Best 9"
    And stored(page) parses to {"version":1,"habits":[Read with its sample done list, Stretch with its sample done list plus "2026-10-08" in order, {"name":"Drink water","done":[]}]}
    When the page is closed and a new page in the same context opens the app
    Then the same three rows and states show

  @R16
  Scenario: Loading writes nothing
    Given storage holds the sample as pretty-printed JSON (indented, with line breaks) and the clock is fixed at 2026-10-08T12:00:00+08:00
    When the page opens and 2 seconds pass
    Then stored(page) is still the identical pretty-printed text

  @R17
  Scenario Outline: Unreadable saved data resets the list and shows the note
    Given the clock is fixed at 2026-10-08T12:00:00+08:00 and storage holds <raw>
    When the page opens
    Then the first child of div.col-main is div.note with role "status"
    And its p.note-text reads "Your saved habits could not be read, so the list was reset."
    And it holds a button.icon-btn named "Dismiss note" containing an svg using "#i-x"
    And p.empty is shown and there is no ul.habits
    And the cell 2026-10-08 is named "Thu 8 Oct, 0 of 0 habits"
    And stored(page) is exactly '{"version":1,"habits":[]}'

    Examples:
      | case                      | raw                                                                              |
      | not JSON                  | {                                                                                |
      | JSON null                 | null                                                                             |
      | an array                  | []                                                                               |
      | wrong version             | {"version":2,"habits":[]}                                                        |
      | version as text           | {"version":"1","habits":[]}                                                      |
      | no habits array           | {"version":1,"habits":{}}                                                        |
      | 13 habits                 | {"version":1,"habits":[13 habits named "H1" to "H13", each with done []]}         |
      | empty name                | {"version":1,"habits":[{"name":"","done":[]}]}                                   |
      | untrimmed name            | {"version":1,"habits":[{"name":" Read","done":[]}]}                              |
      | 41 characters             | {"version":1,"habits":[{"name":"Read twenty pages before bed every night.","done":[]}]} |
      | duplicate ignoring case   | {"version":1,"habits":[{"name":"Read","done":[]},{"name":"read","done":[]}]}     |
      | name not text             | {"version":1,"habits":[{"name":5,"done":[]}]}                                    |
      | done not a list           | {"version":1,"habits":[{"name":"Read","done":"2026-10-08"}]}                     |
      | impossible date           | {"version":1,"habits":[{"name":"Read","done":["2026-02-30"]}]}                   |
      | date with a time          | {"version":1,"habits":[{"name":"Read","done":["2026-10-08T00:00"]}]}             |
      | habit is null             | {"version":1,"habits":[null]}                                                    |

  @R17
  Scenario Outline: Readable edge cases load without a note
    Given the clock is fixed at 2026-10-08T12:00:00+08:00 and storage holds <raw>
    When the page opens
    Then there is no div.note and <result>

    Examples:
      | raw                                                                                                   | result                                                                                         |
      | {"version":1,"habits":[]}                                                                             | p.empty is shown                                                                               |
      | {"version":1,"habits":[{"name":"Read","done":["2026-10-08"],"color":"red"}],"theme":"dark"}           | one row "Read" with day 2026-10-08 pressed; after the user clicks day 2026-10-07, stored(page) contains neither "color" nor "theme" |
      | {"version":1,"habits":[{"name":"Read","done":["2026-10-08","2026-10-07","2026-10-08"]}]}              | the streak line reads "2 days" and "Best 2"                                                    |
      | {"version":1,"habits":[{"name":"Read","done":["2026-10-09"]}]}                                        | no button has data-date "2026-10-09", the streak line reads "No streak yet" and "Best 1"        |
      | {"version":1,"habits":[{"name":"Read","done":[],"__proto__":{"polluted":true}}]}                      | one row "Read", and evaluating ({}).polluted in the page gives undefined                        |

  @R17 @R22
  Scenario: Dismiss removes the note, moves focus to the field, and it does not come back
    Given the clock is fixed at 2026-10-08T12:00:00+08:00 and storage holds "{"
    When the user clicks "Dismiss note"
    Then there is no div.note, p.empty is still shown, and document.activeElement is the input #new-habit
    When the page reloads
    Then there is no div.note
    When storage is set to "{" again through the "__seed__" page and the app is opened again
    Then div.note is shown again

  @R17
  Scenario: On desktop the note sits in the left column
    Given the clock is fixed at 2026-10-08T12:00:00+08:00, the viewport is 1280 x 800 and storage holds "{"
    Then div.note's bounding box lies inside div.col-main's box (x 168, width 500)
    And section.heat starts at x 732

  @R18
  Scenario: Storage that cannot be used at all
    Given a context whose init script makes reading window.localStorage throw a DOMException named "SecurityError"
    And the clock is fixed at 2026-10-08T12:00:00+08:00
    When the page opens
    Then p.empty is shown and there is no div.note
    When the user adds "Read 20 pages" and clicks its day 2026-10-08
    Then the row shows "1 day" and "Best 1"
    And no page error was recorded

  @R18
  Scenario: A save that fails
    # Added 2026-10-08: open_app seeds before it adds the init script, so the sample is stored first and only the later saves throw.
    Given the sample day with an init script that makes Storage.prototype.setItem throw a DOMException named "QuotaExceededError"
    When the user clicks Stretch's day 2026-10-08 and adds "Drink water"
    Then Stretch's streak line reads "4 days" and a fourth row "Drink water" is shown
    And #new-habit-msg is empty and no page error was recorded

Feature: Rolling over midnight

  @R19
  Scenario: The view moves to the new day within a minute while visible
    # Changed 2026-10-08 (plan-check flag, ORCH): the clock was installed at 2026-10-08T23:59:30+08:00 and left running, and an installed clock follows wall time until run_for. So "still Thursday after 29 seconds" held only while under about 1 second of wall time passed between boot and run_for. The clock is now installed at 23:59:00, paused at 23:59:30 once the page is open, and only then run.
    Given storage holds the sample and the clock is installed at 2026-10-08T23:59:00+08:00
    And the page is open
    And the clock is paused at 2026-10-08T23:59:30+08:00 (page.clock.pause_at), so no wall time passes before the next step
    When the clock runs for 29 seconds (page.clock.run_for(29000))
    Then the date still reads "Thursday 8 October" and every strip still ends with data-date 2026-10-08
    When the clock runs for 61 more seconds (to 2026-10-09T00:01:00+08:00)
    Then the date reads "Friday 9 October" with datetime "2026-10-09"
    And every strip runs from 2026-10-03 to 2026-10-09 and only the 2026-10-09 buttons have aria-current "date"
    And Read's pattern is "D D D D D D ." with streak "6 days" and "Best 14" and no data-run-continues
    And Stretch's pattern is "D . D D D . ." with streak "No streak yet" and "Best 9" and data-run-continues
    And No phone's pattern is "D . . D . D ." with streak "1 day" and "Best 4" and no data-run-continues
    And the cell 2026-10-09 has classes "hc l0 today" and is named "Fri 9 Oct, 0 of 3 habits"
    And the cell 2026-10-08 has classes "hc l2" without "today" and is named "Thu 8 Oct, 2 of 3 habits"
    And only 2026-10-10 and 2026-10-11 are future cells

  @R19
  Scenario: The heatmap shifts when a new week starts
    Given storage holds the sample and the clock is installed at 2026-10-11T23:59:30+08:00
    And the page is open
    When the clock runs for 90 seconds
    Then div.cells runs from 2026-07-27 to 2026-10-18 and the month labels are "Jul" at 1, "Aug" at 2, "Sep" at 7, "Oct" at 11
    And the cells 2026-10-13 to 2026-10-18 are future and the cell 2026-10-12 is named "Mon 12 Oct, 0 of 3 habits" with class "today"
    And every strip runs from 2026-10-06 to 2026-10-12
    And the streak lines read "No streak yet" with "Best 14", "No streak yet" with "Best 9", "No streak yet" with "Best 4"

  @R19
  Scenario: The add form and its focus survive the rollover
    Given storage holds the sample and the clock is installed at 2026-10-08T23:59:30+08:00
    And the user has typed "Drink" into the field without submitting
    When the clock runs for 90 seconds
    Then the date reads "Friday 9 October", the field's value is "Drink" and the input is document.activeElement

  @R19
  Scenario: An error message survives the rollover
    Given storage holds the sample and the clock is installed at 2026-10-08T23:59:30+08:00
    And the user has clicked "Add" with the field empty
    When the clock runs for 90 seconds
    Then #new-habit-msg still reads "Name the habit first." and the input still has aria-invalid "true"

  @R19 @R22
  Scenario: Focus on today's bead stays on today's bead
    Given storage holds the sample and the clock is installed at 2026-10-08T23:59:30+08:00
    And the user has pressed Tab until Read's day 2026-10-08 has focus
    When the clock runs for 90 seconds
    Then document.activeElement is the seventh day button of Read's strip, named "Mark Fri 9 Oct as done", with aria-current "date"

  @R20
  Scenario: The view moves at once when the tab is shown again
    Given storage holds the sample and the clock is installed at 2026-10-08T23:58:00+08:00
    And the page is open
    And the clock is paused at 2026-10-08T23:59:00+08:00 (page.clock.pause_at)
    And the test marks the tab hidden (hide_tab)
    And the system time is set to 2026-10-09T07:30:00+08:00 (page.clock.set_system_time, which fires no timer)
    Then the date still reads "Thursday 8 October"
    When the test marks the tab visible (show_tab)
    Then, without advancing the clock, the date reads "Friday 9 October"
    And the strips, streak lines and heatmap equal those of the first @R19 scenario after the rollover

Feature: Platform

  @R21
  Scenario: Phone width 360
    Given the sample day at a 360 x 780 viewport
    Then document.documentElement.scrollWidth is at most 360
    And every button.day is at least 44 pixels wide
    And every icon button is 44 x 44 pixels, and the input and the Add button are 48 pixels tall
    And every span.bead is 32 x 32 pixels

  @R22
  Scenario: Tab order
    Given the sample day with nothing focused
    When the user presses Tab 26 times
    Then focus visits, in order: "Delete Read 20 pages", its 7 day buttons from "Mark Fri 2 Oct as done" to "Mark Thu 8 Oct as done", "Delete Stretch 10 minutes", its 7 day buttons, "Delete No phone after 11pm", its 7 day buttons, the input #new-habit, the "Add" button

  @R22
  Scenario: Tab order with the note
    Given the clock is fixed at 2026-10-08T12:00:00+08:00 and storage holds "{"
    When the user presses Tab 3 times
    Then focus visits "Dismiss note", the input #new-habit, then "Add"

  @R22
  Scenario Outline: Focus rings on keyboard focus only
    Given the sample day
    When the user presses Tab until <target> has focus
    Then its computed outline is "rgb(28, 37, 35) solid 2px" and its outline-offset is "<offset>"

    Examples:
      | target                                   | offset |
      | Read's day 2026-10-02                    | 0px    |
      | the button "Delete Read 20 pages"        | -2px   |
      | the input #new-habit                     | 2px    |
      | the "Add" button                         | 3px    |

  @R22
  Scenario: A mouse click draws no ring
    Given the sample day
    When the user clicks Read's day 2026-10-05
    Then that button does not match ":focus-visible" and its computed outline-style is "none"

  @R23
  Scenario: Motion without reduced motion
    Given the sample day with reduced motion "no-preference"
    Then the computed transition-duration of every span.bead is "0.18s, 0.18s, 0.12s"
    When the user clicks "Delete Read 20 pages"
    Then the dialog's computed animation-name is "dialog-in"

  @R23
  Scenario: Everything appears at once under reduced motion
    Given the sample day with reduced motion "reduce"
    Then the computed transition-duration of every span.bead and every .hc::before is "0s"
    When the user clicks "Delete Read 20 pages"
    Then the dialog's computed animation-name is "none" and its ::backdrop's computed animation-name is "none"

  @R24
  Scenario: Markup in a name stays text
    Given a fresh day and a record of every JavaScript dialog the page opens
    When the user types "<img src=x onerror=alert(1)>" and clicks "Add"
    Then h3#h1-name has text content "<img src=x onerror=alert(1)>" and no child elements
    And the document holds no img element
    And the trash button is named "Delete <img src=x onerror=alert(1)>"
    When the user clicks that trash button
    Then #del-title has text content 'Delete "<img src=x onerror=alert(1)>"?' and no child elements
    And no JavaScript dialog opened and no page error was recorded

  @R24
  Scenario: No HTML sinks in the source
    Given the text of every file under src/
    Then none contains "innerHTML", "outerHTML", "insertAdjacentHTML", "document.write", "eval(" or "new Function"

  @R25
  Scenario: Every request stays on the device's own files
    # Changed 2026-10-08 (plan-check flag, ORCH): the Given first read "the sample day with record(page) started before the app URL opens". open_app now has the record option, ordered after seeding, so recording starts after seeding and before the app URL opens.
    Given the sample day opened with open_app(record=True), so the GET /__seed__ request is not in the log
    When the user clicks Stretch's day 2026-10-08, adds "Drink water", deletes "Read 20 pages" and the page reloads
    Then every recorded request is a GET to the BASE_URL origin with no query string
    And every request path is "/", "/index.html", "/favicon.ico", "/src/styles.css" or "/src/<name>.js" for a file that exists in src/
    And no console message of type "error" and no page error was recorded

  @R25
  Scenario: The CSP is in force
    Given the sample day
    When the test evaluates fetch("https://example.com/") in the page
    Then the promise rejects and the console records a Content Security Policy violation for connect-src
```

### Cold-boot live-e2e gate (`@R27`)
Run by `python tests/browser/live_e2e.py --base-url http://127.0.0.1:<port>/ --out docs/modules/app/qa/live-e2e/<datetimestamp>/` after every other gate is green. Its file name keeps it out of pytest collection, because it uses the real clock and writes the gate's evidence.

```gherkin
Feature: Cold boot, real gestures, evidence

  @R27
  Scenario: The headline flows on a cold start
    Given the app is served from the project root by python -m http.server <port> --bind 127.0.0.1
    And a fresh headless Chromium context at 390 x 844 with empty storage, the real system clock (no page.clock), and no init script
    And the test reads the browser's local date once (T) from about:blank before opening the app, and derives yesterday (Y)
    When the page opens BASE_URL with no query string or fragment
    Then p.empty reads "No habits yet. Add one you want to do every day.", every heat cell up to T is l0 named "..., 0 of 0 habits", T's cell has class "today", and stored(page) is null
    When the user clicks the "New habit" field, types "Read 20 pages" and clicks "Add"
    Then one row "Read 20 pages" shows 7 not-pressed beads ending with T, "No streak yet" and no best, and the field is empty
    When the user types "Stretch 10 minutes" and presses Enter
    Then a second row "Stretch 10 minutes" shows under the first
    When the user clicks the T bead of "Read 20 pages" and the T bead of "Stretch 10 minutes"
    Then both streak lines read "1 day" and "Best 1", and T's cell is l4 named "<T short>, 2 of 2 habits"
    When the user clicks the Y bead of "Read 20 pages"
    Then its streak line reads "2 days" and "Best 2", and Y's cell is l2 named "<Y short>, 1 of 2 habits"
    When the page reloads
    Then both rows, their pressed beads and their streak lines are unchanged
    When the user clicks "Delete Stretch 10 minutes"
    Then the dialog reads 'Delete "Stretch 10 minutes"?' and Cancel has focus
    When the user clicks "Cancel"
    Then 2 rows remain and focus is on "Delete Stretch 10 minutes"
    When the user clicks "Delete Stretch 10 minutes" and then "Delete habit"
    Then 1 row remains, focus is on the input, and T's cell is l4 named "<T short>, 1 of 1 habits"
    When the user types "read 20 pages" and presses Enter
    Then #new-habit-msg reads "You already track this habit." and the field still holds "read 20 pages"
    When the page reloads
    Then exactly one row "Read 20 pages" shows "2 days" and "Best 2"
    And the browser's local date is still T (otherwise the run is void and is repeated)
    # Changed 2026-10-08 (plan-check flag, ORCH): the last step first read "every request was a same-origin GET for index.html or a file under src/", which is narrower than @R25 (it left out "/" and "/favicon.ico", which the browser may ask for). @R27 now reuses the @R25 path list.
    And no console error and no page error was recorded, and every request meets the @R25 request rule: a GET to the BASE_URL origin with no query string, for the path "/", "/index.html", "/favicon.ico", "/src/styles.css" or "/src/<name>.js" for a file that exists in src/
```
- **Gestures:** only `click`, `keyboard.type`, `keyboard.press` and `reload`. No `evaluate` that writes anything; reading DOM, `localStorage` and the date is allowed.
- **Evidence** in `docs/modules/app/qa/live-e2e/<datetimestamp>/`: one full-page screenshot after each `Then` (`01-first-visit.png`, `02-added.png`, and so on), `steps.json` (each step: name, gesture, expected, observed, pass, time), `console.json`, `network.json`, and `summary.json` (start and end date T, browser version, base URL, overall pass). No artifact means the gate is not met.
- The script starts nothing itself. The agent that runs it starts and stops the server and declares it in `PROCESSES`.

### Fidelity scenarios (`@R28`, run by the fidelity finder after functional green)
```gherkin
Feature: Looks right

  @R28
  Scenario Outline: Each screen is 1-to-1 with its golden
    Given the fidelity capture of "<screen>" at <viewport> as defined in the Fidelity gate below
    Then report.json has dimensions_match true and mismatch_pixels 0 at threshold 0.1
    And every FE element checklist row for "<screen>" matches

    Examples:
      | screen            | viewport  |
      | today.html        | 390x844   |
      | today.html        | 1280x800  |
      | today-empty.html  | 390x844   |
      | today-empty.html  | 1280x800  |
      | delete-dialog.html| 390x844   |
      | delete-dialog.html| 1280x800  |

  @R28
  Scenario: The fidelity state scripts are right
    Given tests/browser/fidelity/seed-sample.js and tests/browser/fidelity/open-delete-dialog.js
    Then the text the seed script writes parses to exactly {"version":1,"habits":<the habits of sample-history.json>}
    When a page with the clock fixed at 2026-10-08T09:00:00 local time loads the app with the seed script as an init script and then runs the after-load script as the body of an async function
    Then dialog.dialog is open, matches ":modal", its title reads 'Delete "Read 20 pages"?', and document.activeElement is body

  @R28
  Scenario: Every specimen on the states sheet matches the live state
    Given the states.html checklist rows below and the computed-style method in the Fidelity gate
    Then every row matches
```

## FE element checklist
> Every visible or interactive element of every golden, one row each. Each row passes or fails on its own. Colours are the system.css tokens, given as computed values where a test reads them.
> Measured positions come from the goldens' `.md` files. The pixel diff covers them; a row fails if its element is off.

### S1, golden `./docs/design/today.html` (sample day)
| # | Element | Must match the golden |
|---|---|---|
| S1-01 | Page | body `--bg` rgb(242, 245, 243), text `--ink`, the system rounded font stack, 16/24 |
| S1-02 | Icon sprite | hidden `svg` (0 x 0, `position:absolute`, aria-hidden), symbols `i-check` (Phosphor check bold) and `i-trash` (Phosphor trash regular) with the golden's exact path data. The app's extra `i-x` symbol is invisible. |
| S1-03 | Page frame | phone: max 600, padding 24 top, 20 sides, 48 bottom. Desktop (900 and up): max 1040, centred at x 120 on 1280, padding 40, 48, 48 |
| S1-04 | Header row | `header.top`, flex, baseline-aligned, space between, gap 12; 24 below on phone, 32 on desktop |
| S1-05 | Brand | `h1.brand` "Streaks", 22/28, 700, letter-spacing -0.01em, `--bead-deep` rgb(46, 90, 80), left |
| S1-06 | Date | `p.date > time[datetime="2026-10-08"]` "Thursday 8 October", 16/24, `--ink-soft` rgb(82, 96, 91), right, on the brand's baseline |
| S1-07 | Desktop layout | `main.layout` grid `minmax(0, 1fr)` and 380px, gap 64; main column 500 wide at x 168; heatmap 380 wide at x 732; top aligned |
| S1-08 | Hidden list heading | `h2#habits-title.sr-only` "Habits" (clipped to 1 x 1), the section labelled by it |
| S1-09 | Habit list | `ul.habits`, no bullets, no padding, rows 32 apart; row tops 77, 273, 469 at 390 and 101, 301, 501 at 1280 |
| S1-10 | Row 1 head | `h3#h1-name` "Read 20 pages", 18/28, 600, `--ink`, 8 top padding, wraps anywhere; trash button "Delete Read 20 pages" |
| S1-11 | Row 1 streak | `span.cur` "6 days" 14/20 600 `--bead-deep`; `span.best` "Best 14" 14/20 400 `--ink-soft`; 12 apart; tabular numbers; 8 above the strip |
| S1-12 | Row 1 strip | Fri 2 to Thu 8, pattern `. D D D D D D`; no `data-run-continues`; thin thread fading in at the left of Fri 2; 4px `--bead` run thread joining Sat 3 to Thu 8; Thu 8 done with the today ring |
| S1-13 | Row 2 head | `h3#h2-name` "Stretch 10 minutes"; trash "Delete Stretch 10 minutes" |
| S1-14 | Row 2 streak | "3 days", "Best 9" |
| S1-15 | Row 2 strip | pattern `D D . D D D .`, `data-run-continues`: thick thread fading in at the left of Fri 2; run Fri 2 to Sat 3; thin thread Sat 3 to Mon 5; run Mon 5 to Wed 7; dashed holding thread Wed 7 to Thu 8 (4px dashes, 3px gaps, a dash starting at the cell boundary); Thu 8 hollow with the today ring |
| S1-16 | Row 3 head | `h3#h3-name` "No phone after 11pm"; trash "Delete No phone after 11pm" |
| S1-17 | Row 3 streak | "1 day", "Best 4" |
| S1-18 | Row 3 strip | pattern `. D . . D . D`; isolated done beads, thin thread only, no dashed thread; Thu 8 done with the today ring |
| S1-19 | Trash buttons | 44 x 44 circle, transparent, Phosphor trash 20px in `--ink-soft`, pulled 12 right so the glyph's right edge sits on the content edge; the name's first line centred on it |
| S1-20 | Day cells | 50 x 92 at 390, 71.4 x 96 at 1280; padding 4 top, 8 bottom, 8 gap; pill radius; weekday 12/16 `--ink-soft`; number 16/20 500 tabular; today's weekday and number `--ink` 700 |
| S1-21 | Beads | 36px at 390, 40px at 1280. Not done: 2px `--ring` stroke, `--bg` fill, no check. Done: `--bead` fill and stroke, check in `--on-bead` at 56%. Today: `box-shadow: 0 0 0 3px var(--bg), 0 0 0 4.5px var(--ring)` |
| S1-22 | Thin thread | 2px `--thread` through the bead centres, each cell drawing its own halves; the last cell has no right half |
| S1-23 | Add form | `form.add[novalidate]`, 40 below the list; top 673 at 390, 709 at 1280 |
| S1-24 | Field label | `label[for=new-habit]` "New habit", 16/24, 600, `--ink`, 8 above the input |
| S1-25 | Input | `#new-habit`, 48 tall pill, 2px `--ring` border, `--field` fill, 0 20 padding, no placeholder, no maxlength, `autocomplete="off"`, `aria-describedby="new-habit-msg"`; 256 wide at 390, 406 at 1280 |
| S1-26 | Add button | "Add", 48 tall pill, 82 wide, `--bead` fill, `--on-bead` 16 600 text, 12 right of the input |
| S1-27 | Message line | `p#new-habit-msg.field-msg.field-error[aria-live=polite]`, empty and not displayed |
| S1-28 | Heatmap panel | `section.heat`, `--surface`, radius 20; phone: 40 below the form, top 793 at 390, 350 wide, padding 20 by 16; desktop: top 101 (level with the first habit), 380 wide, padding 24, sticky 32 from the top |
| S1-29 | Heatmap title | `h2.heat-title` "Last 12 weeks", 16/24, 600, 12 above the grid |
| S1-30 | Month axis | "Jul" over column 1, "Aug" 3, "Sep" 8, "Oct" 12; 12/16 `--ink-soft`; aria-hidden |
| S1-31 | Weekday axis | "Mon", blank, "Wed", blank, "Fri", blank, "Sun" against rows 1 to 7; 12px `--ink-soft`; 8 from the cells; aria-hidden |
| S1-32 | Heat cells | 84 squares, column-major, 23.8 at 390 and 24.9 at 1280; the 81 levels of `heatmapLevels`; names "Mon 20 Jul, 3 of 3 habits" to "Thu 8 Oct, 2 of 3 habits"; role img |
| S1-33 | Level dots | l0 6px hollow ring 1.5px `--ring`; l1 7px rgb(120, 150, 139); l2 11px rgb(79, 124, 112); l3 14px `--bead`; l4 17px `--bead-deep`; all round |
| S1-34 | Today cell | 2026-10-08: its l2 dot inside a 22px ring, 1.5px `--ring`; class `today`, `aria-current="date"` |
| S1-35 | Future cells | Fri 9, Sat 10, Sun 11 Oct: nothing drawn, aria-hidden, no role |
| S1-36 | Legend | right aligned, 12 below the grid: "None", the five level dots in 20px cells, "All"; 12/16 `--ink-soft`; aria-hidden |
| S1-37 | Nothing else | no note, no visible dialog, no other control or text anywhere on the page |

### S2, golden `./docs/design/today-empty.html` (a fresh day)
| # | Element | Must match the golden |
|---|---|---|
| S2-01 | Shared frame | S1-01, S1-03 to S1-08 and S1-24 to S1-31, S1-36 hold unchanged, except that S1's measured positions do not carry over: S1-28's phone top 793 at 390 is replaced by S2-04's 293, and S2-02 to S2-05 give S2's positions. The rest of S1-28 holds (40 below the form, 350 wide, padding 20 by 16, and the desktop values). Changed 2026-10-08 (plan-check flag, ORCH): the row first read "S1-01, S1-03 to S1-08 and S1-24 to S1-31, S1-36 hold unchanged", which carried S1-28's top 793 against S2-04's 293. |
| S2-02 | Empty message | `p.empty`: `strong` "No habits yet." as a block, 18/28 600 `--ink`; then "Add one you want to do every day." 16/24 `--ink-soft`, 4 below; top 77 at 390, 101 at 1280 (where the first habit name would sit); 56 tall; takes the place of `ul.habits` |
| S2-03 | Add form | 40 below the message: top 173 at 390, 197 at 1280; enabled, empty, no message |
| S2-04 | Heatmap panel | top 293 at 390, ending at 588 so the whole first screen fits 390 x 844; top 101 in the right column at 1280; no filler added to the short left column |
| S2-05 | Heat cells | 81 hollow l0 rings named "<Ddd D Mon>, 0 of 0 habits"; Thu 8 Oct l0 with the today ring; Fri 9 to Sun 11 Oct blank |
| S2-06 | Icons | none visible (the app's sprite is present but has zero size) |

### M1, golden `./docs/design/delete-dialog.html` (sample day, "Delete Read 20 pages" clicked)
| # | Element | Must match the golden |
|---|---|---|
| M1-01 | Page behind | S1 unchanged underneath; it cannot be clicked or focused |
| M1-02 | Backdrop | `--scrim` rgb(28 37 35 / 0.5) over the whole viewport (native `::backdrop`) |
| M1-03 | Dialog box | `dialog.dialog` opened with `showModal()`, role alertdialog, `aria-modal="true"`, labelled by `#del-title`, described by `#del-body`; `--surface`, radius 20, padding 24, the dialog shadow; width `min(400px, 100% - 40px)`; 350 x 180 at x 20, y 332 on 390 x 844 and 400 x 180 at x 440, y 310 on 1280 x 800; centred both ways |
| M1-04 | Title | `h2#del-title` `Delete "Read 20 pages"?` with straight quotes, 18/28 600 `--ink`, one line, 24 from the top; long names wrap and the box grows in height only |
| M1-05 | Body | `p#del-body` "Its history is deleted too.", 16/24 `--ink-soft`, 8 below the title |
| M1-06 | Buttons row | `form.dialog-actions[method=dialog]`, two equal columns 12 apart, 24 below the body; each 145 wide at 390 and 170 at 1280, 48 tall |
| M1-07 | Cancel | left; `.btn.btn-secondary[type=submit][value=cancel]` "Cancel"; transparent, 2px `--ring` border, `--ink` 16 600 |
| M1-08 | Delete habit | right; `.btn.btn-danger[type=submit][value=delete]` "Delete habit"; `--danger` rgb(162, 59, 50) fill, `--on-bead` text; the only filled button |
| M1-09 | Initial focus | Cancel is focused on open; no ring after a mouse open, the 3px-offset ring after a keyboard open |
| M1-10 | No scroll | `html` and `body` `height: 100%` and `overflow: hidden` while open |
| M1-11 | Entrance | backdrop fades in over 180ms, dialog fades and rises 8px over 200ms; both instant under reduced motion |

### States sheet, golden `./docs/design/states.html` (specimen sheet, checked by computed style, no pixel diff)
| # | Specimen | Must match the specimen in the live app |
|---|---|---|
| ST-01 | S3 empty name | after submitting an empty field: input `aria-invalid="true"` with `--danger` border; message "Name the habit first." 14/20 `--danger`, 8 below the row; classes `field-msg field-error`; the form grows by 28 and nothing moves sideways |
| ST-02 | S3 too long | field holding "Walk to the end of the street and back after dinner": message "Keep it to 40 characters or fewer."; the text stays |
| ST-03 | S3 duplicate | field holding "read 20 pages": message "You already track this habit." |
| ST-04 | S4 twelve habits | input disabled: `--wash` fill, `--thread` border, `--ink-soft` text, not-allowed cursor; label `--ink-soft`; Add disabled: `--thread` fill, `--ink-soft` text, no hover change, no press scale; note in `--ink-soft` 14/20 (`field-note`), wrapping to two lines at phone width |
| ST-05 | A habit just added | at the bottom of the list; name 18/28 600; "No streak yet" as `span.cur.none` in `--ink-soft` 600; no best element; 7 hollow beads, today ringed, thin thread only |
| ST-06 | S5 note | `div.note[role=status]`: `--wash` fill, radius 20, padding 8 8 8 20; text 16/24 `--ink` with 8 vertical padding; the 44px Dismiss button with Phosphor "x" regular (path from states.html) at the top right; 32 above the empty message; the brand stays `h1.brand` in the app (the sheet's `p.brand` is sheet-only) |
| ST-07 | Primary button | default `--bead`; hover `--bead-deep`; keyboard focus 2px `--focus` outline 3px out; disabled per ST-04; press scale 0.98 |
| ST-08 | Secondary button | Cancel: transparent with 2px `--ring` border and `--ink` text; hover `--wash` fill |
| ST-09 | Danger button | Delete habit: `--danger` fill; hover `--danger-deep` rgb(132, 48, 42) |
| ST-10 | Text input | default `--ring` border on `--field`; keyboard focus 2px `--focus` outline 2px out with the border unchanged; error `--danger` border; disabled per ST-04 |
| ST-11 | Day bead states | not done, done, today, today done, as S1-21 |
| ST-12 | Day bead hover | pointer hover: a not-done stroke turns `--bead`; a done bead's fill and stroke turn `--bead-deep` |
| ST-13 | Day bead focus | keyboard focus: 2px `--focus` outline around the whole cell, offset 0, following the pill shape (a vertical capsule), never on the bead, the today ring unchanged |
| ST-14 | Day bead press | the bead scales to 0.94 while pressed |
| ST-15 | Icon button | rest: transparent, `--ink-soft` glyph; hover: `--wash` fill, `--ink` glyph; keyboard focus: 2px `--focus` outline 2px inside the edge |
| ST-16 | Heat cell levels | l0 to l4, today ring and future blank as S1-33 to S1-35; level 3 is seen live on the sample plus a fourth habit (Mon 20 Jul, 3 of 4 habits) |
| ST-17 | Sheet chrome | NOT built: the sheet title "Streaks states", its subtitle, the group headings, frame captions and outlines, specimen labels, and the specimen-only names such as "Level 0, none of the habits" |

## Fidelity gate
*(FE module. Opus, effort xhigh, runs AFTER functional green.)*

- **Harness:** the sdlc browser-harness in frozen mode, **version 2.1.1 or later**, run directly: `python "$CLAUDE_PLUGIN_ROOT/harness/fidelity.py"` (on this machine `{sdlc}/harness/fidelity.py`). CG-2, ruled 2026-10-08, ORCH: the plugin gained the state-setup flags this app needs, so no project-side capture driver exists. Every Streaks run passes `--fixed-time 2026-10-08T09:00:00` (2.1.1 always pins time and would otherwise use 2023-11-14T22:13:20Z). The time is a local datetime: the harness sets no time zone, so the clock and the browser both use the machine's zone and the page sees 09:00 on Thursday 8 October whatever that zone is.
- **Harness version history and the 2.1.2 check** (added 2026-10-08, plan-check flag, ORCH). Changed 2026-10-08: the bullet above and the text in `spec.md` and `../ROADMAP.md` first credited the four state flags (`--candidate-init-script`, `--candidate-after-load`, `--fixed-time`, repeatable `--browser-arg`) to sdlc 2.1.1. The correct history is that 2.1.0 added the four flags, 2.1.1 fixed the freeze so time is pinned through Playwright's clock, and 2.1.2 added `bypass_csp`. The minimum stays "2.1.1 or later". The installed harness is 2.1.2. The 0-pixel baseline below was measured on 2.1.1, so the first fidelity run on 2.1.2 must confirm it: the fidelity tester records the harness version it ran, and the first set of captures on 2.1.2 must show 0 mismatched pixels and `dimensions_match` true. A non-zero count on 2.1.2 that was 0 on 2.1.1 is a finding for the owner, and the budget is not widened to absorb it.
- **Test-side state scripts** (in `tests/browser/fidelity/`, never shipped, never loaded by the app):
  - `seed-sample.js`, passed as `--candidate-init-script`. One statement, `localStorage.setItem("streaks.state", <text>)`, where `<text>` is exactly `{"version":1,"habits":<the habits of sample-history.json>}`. It runs before the app's scripts.
  - `open-delete-dialog.js`, passed as `--candidate-after-load` (the harness runs it as the body of an `async` function after load). It clicks the button named "Delete Read 20 pages", throws unless `dialog.dialog` is open and matches `:modal` with the title `Delete "Read 20 pages"?`, then calls `document.activeElement.blur()`. The blur is required: the golden draws no focus (delete-dialog.md: "Not drawn in the golden, because a static page has no keyboard focus"), and focus moved by script without a prior pointer gesture matches `:focus-visible` in Chromium, so the Cancel ring would show. Measured with harness 2.1.1: 877 mismatched pixels at 390 and 977 at 1280 without the blur, all of them the Cancel ring, and 0 with it. Focus on Cancel is proven by `@R13`, not by this gate.
  - `tests/browser/test_fidelity_inputs.py` (part of the pytest suite, `@R28`) proves both scripts: the seed's text parses to `{"version":1,"habits":<sample habits>}` exactly, and running the after-load body on the seeded app leaves the dialog open with that title and `document.activeElement` as `body`.
- **Golden / candidate / state:**
  | Screen | Golden | Candidate | State flags |
  |---|---|---|---|
  | S1 | `./docs/design/today.html` | `http://127.0.0.1:<port>/` | `--candidate-init-script tests/browser/fidelity/seed-sample.js` |
  | S2 | `./docs/design/today-empty.html` | `http://127.0.0.1:<port>/` | none (each harness render is a fresh context with empty storage) |
  | M1 | `./docs/design/delete-dialog.html` | `http://127.0.0.1:<port>/` | `--candidate-init-script tests/browser/fidelity/seed-sample.js --candidate-after-load tests/browser/fidelity/open-delete-dialog.js` |
- **Command** (one per screen and viewport, 6 runs), from the project root with the app served:
  `python "$CLAUDE_PLUGIN_ROOT/harness/fidelity.py" --golden ./docs/design/<screen>.html --candidate http://127.0.0.1:<port>/ --viewport <390x844|1280x800> --dpr 1 --color-scheme light --fixed-time 2026-10-08T09:00:00 <state flags> --out ./docs/modules/app/qa/fidelity-<screen>-<viewport>/<datetimestamp>/`
  `--browser-arg=--disable-lcd-text` is not used: measured with harness 2.1.1 on the M1 case it changed nothing (877 and 977 pixels with and without it).
- **Viewport:** `390x844` and `1280x800` for every screen (6 captures). **deviceScaleFactor:** `1`. **Color scheme:** `light`. **Full page:** yes.
- **Threshold:** per-pixel `0.1` (the harness default, normalised RGB distance). **Budget: 0 mismatched pixels, and `dimensions_match` true.** Why zero is right, measured 2026-10-08 on headless Chromium 149: with harness 2.1.1 and `--fixed-time 2026-10-08T09:00:00`, the S1 golden against itself gives 0 pixels, and the M1 golden against a native `showModal()` copy (`::backdrop` instead of `.scrim`) opened by an after-load script ending in the blur above gives 0 pixels at both 390 and 1280. The candidate uses the same CSS, the same DOM and the same system fonts on the same engine, so any pixel over 0.1 is a real difference. Expected golden sizes (measured): S1 and M1 are 390 x 1136 and 1280 x 837; S2's sizes are read from its `report.json`.
- **Evidence:** `./docs/modules/app/qa/fidelity-<screen>-<viewport>/<datetimestamp>/` (`golden.png`, `candidate.png`, `diff.png`, `styles.json`, `report.json`). Verdict in `./docs/modules/app/findings/fidelity.md`.
- **Method:** screenshot both, pixel diff at the threshold above, per-element computed-style check from `styles.json`, then every S1, S2 and M1 checklist row above.
- **states.html (no pixel diff, it is a specimen sheet, not a screen):** at a 360 x 780 viewport (the frames pin beads to 32px, the live size at 360), the tester opens `states.html` from its file path and the running app in the same state, reached with real gestures (`hover`, keyboard Tab, `mouse.down` for press under reduced motion, a submit for errors, 12 seeded habits for S4, `{` seeded for S5, the sample plus an added habit for level 3). For each ST row it compares the specimen element's computed `color`, `background-color`, border colours and widths, `outline-color`, `outline-style`, `outline-width`, `outline-offset`, `box-shadow`, `border-radius`, `font-size`, `font-weight`, `line-height`, `transform` (press only), the check `svg` `opacity`, and bead and icon-button `width` and `height` with the live element's. Specimen-only styling is excluded: frame padding and outline, `.spec-day > .day { width: 56px }`, the hidden thread in bead specimens, `.spec-input` width 240, `.spec-cell .hc` width 24.
- **Verdict:** 1-to-1 only, with no additions, subtractions or modifications.

## Regression
- Re-run the whole pytest suite (`python -m pytest tests/browser -q`), the 6 fidelity captures with the states check, and the `@R27` cold-boot gate in the final parallel all-modules pass.
