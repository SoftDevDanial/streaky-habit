# Brainstorm: Streaks

**Phase:** brainstorm · **Date:** 2026-10-08 · **Direction:** personal · **Track:** sdlc

> **How this brainstorm was run.** The owner delegated this whole run ("Auto create with lifecycles for 2
> projects. Split bill and a todo app (or anything else you think is better suited that doesnt take too
> much but is good to showcase)", 2026-10-08). The orchestrator chose a daily habit tracker over a plain
> todo list because its date and streak rules give the reviewing agents real edge cases to test. The
> grill below was walked by the orchestrator. Every decision is tagged **ORCH**, which means it is
> reversible and the owner may overturn it.

## The problem
Someone wants to do a few things every day (read, stretch, drink water) and see at a glance whether
today is done and how long each run has lasted. Most trackers want an account and an email address.
This one keeps everything on the device.

## Who uses it
One person, mostly on their phone, a few times a day. Each visit takes seconds: open, tick, close.

## Direction
Personal. Free, private, no accounts. No market panel.

## Resolved scope

### Core capabilities
| ID | Capability | What the user gets |
|---|---|---|
| C1 | Add a habit | Name a habit and it joins the list. |
| C2 | Tick the week | Each habit shows the last 7 days. Tap a day to mark it done or not done. |
| C3 | Current streak | How many days in a row the habit has been done, counted so it does not break until today is over. |
| C4 | Best streak | The longest run the habit has ever had. |
| C5 | 12-week heatmap | One grid for all habits, one cell per day for the last 12 weeks, darker when more habits were done. |
| C6 | Delete a habit | Removes the habit and its history after a confirmation. |
| C7 | Kept on the device | Habits and history survive reloads and closed tabs on the same browser. |

### Key flows
1. **First visit.** The list is empty and says how to start. Type "Read 20 pages", press Add. The habit
   appears with 7 empty days and "No streak yet".
2. **Daily tick.** Open the app, tap today's cell on two habits. Each streak goes up, today's heatmap
   cell darkens.
3. **Catch up.** Forgot to tick yesterday. Tap yesterday's cell. The streak counts it.
4. **Delete.** Tap delete on a habit, confirm, it is gone along with its history. Cancel keeps it.

### Rules the build must follow
- **Days are local calendar days.** A day is the user's local date (YYYY-MM-DD), changing at local
  midnight. No time zones are stored.
- **Habit name:** trimmed, 1 to 40 characters, unique ignoring case. Errors show inline under the field:
  - empty: "Name the habit first."
  - too long: "Keep it to 40 characters or fewer."
  - duplicate: "You already track this habit."
- **At most 12 habits.** At 12 the add field and button are disabled with the note "You track 12
  habits, the most this app holds. Delete one to add another."
- **The week strip** shows 7 cells, oldest on the left, today on the right. Each cell shows the short
  weekday and the day of the month and has an accessible name like "Mark Tue 6 Oct as done". Only these
  7 days can be changed. Days older than 7 days are read-only (they still count for streaks and the
  heatmap). Future days are never shown.
- **Current streak:** if today is done, count back from today. If today is not done, count back from
  yesterday. Count consecutive done days. Shown as "1 day" or "N days". At 0 it shows "No streak yet".
- **Best streak:** the longest run of consecutive done days in the habit's whole history. Shown as
  "Best N". At 0 it is not shown.
- **Heatmap:** 12 columns, one per week, the newest week on the right. Weeks start on Monday, rows run
  Monday to Sunday. Each cell's level is the share of the current habits done that day: 0 (none), 1 (up
  to a third), 2 (up to two thirds), 3 (more than two thirds, not all), 4 (all). Days after today are
  left blank. Each cell has an accessible name like "Tue 6 Oct, 2 of 3 habits". With no habits, every
  past cell is level 0.
- **Rolling over midnight.** If the app is left open across local midnight, the week strip and the
  heatmap move to the new day within a minute, and immediately when the tab is shown again.
- **Delete** asks "Delete "Read 20 pages"? Its history is deleted too." with "Delete habit" and "Cancel".
- **Storage:** saved after every change. If saved data cannot be read, the app starts empty and says
  "Your saved habits could not be read, so the list was reset." The note can be dismissed.
- **Order:** habits stay in the order they were added. New habits go to the bottom.
- **Platform:** a static web page. Works on a phone (360 px wide and up) and on desktop. Keyboard usable,
  visible focus, reduced motion respected. English only.

### Non-goals (do NOT build)
- Reminders or notifications.
- Accounts, login, sync between devices.
- Weekly targets ("3 times a week") or any schedule other than daily.
- Renaming or reordering habits.
- Export or import.
- Editing days older than the last 7.
- More than one tick per day, notes, or amounts.
- Stats beyond current streak, best streak and the heatmap.
- A theme switcher.

## Grill log
| # | Question | Recommended answer | Decision | Tag |
|---|---|---|---|---|
| 1 | A todo app or something else? | A daily habit tracker. Same size of build, but dates and streaks give the agents real edge cases. | Habit tracker, named Streaks. | ORCH |
| 2 | Direction? | Personal. No business model. | Personal, so no market panel. | ORCH |
| 3 | Which days can be ticked? | The last 7. Enough to catch up after a weekend, small enough to fit a phone row. | As recommended. | ORCH |
| 4 | When does a streak break? | Not until today is over. Not ticking yet this morning should not show a broken streak. | As recommended. | ORCH |
| 5 | One heatmap or one per habit? | One for all habits. Twelve grids would bury the list on a phone. | One combined heatmap. | ORCH |
| 6 | How is a heatmap day shaded? | Share of current habits done that day, in 5 levels. | As recommended. | ORCH |
| 7 | How many habits? | Up to 12. More than that stops being a daily routine. | As recommended. | ORCH |
| 8 | Are duplicate names allowed? | No, case-insensitive. Two "Read" rows would be confusing. | As recommended. | ORCH |
| 9 | What marks the day change? | Local midnight. The user thinks in local days. | As recommended. | ORCH |
| 10 | What if the app stays open past midnight? | Roll over within a minute, and at once when the tab is shown again. | As recommended. | ORCH |
| 11 | Rename or reorder? | Not now. Delete and re-add covers the rare case. | Non-goals. | ORCH |

## Gate
**Resummarized idea.** Streaks is a one-page web app for keeping daily habits. The user adds up to 12
named habits. Each shows the last 7 days as tappable cells, the current streak (which does not break
until today is over) and the best streak. One 12-week heatmap shows how much of the routine was done each
day. Habits can be deleted after a confirmation. Everything stays in the browser on the device. No
reminders, accounts, schedules, renaming or export.

**Approval:** given by the orchestrator under the owner's delegation on 2026-10-08, tagged ORCH. The
owner may reopen any row above.

---

## v1.1.0 delta (2026-10-10, from the owner's UAT and his answers)

> Not delegated. **USER** rows are the owner's words or choices. **ORCH** rows are details the orchestrator
> settled so design can start. They are reversible and shown to him in the design round.

### Name
**Danial's Streaky Habit.** The logo and the header show "Streaky Habit" only ("Logo wise, dont need danial or
even initial D. Danial is just to make it unique."). The page title and the READMEs use the full name. (USER)

### Capabilities added or changed
| ID | Capability | What the user gets | Tag |
|---|---|---|---|
| C2 | Tick the week, and any past day (changed) | Tap any day in the 12-week heatmap to open it and tick or untick each habit for that day. The 7-day strip stays | USER |
| C3, C4 | Current and best streak (changed) | The streak line names both numbers, for example "Current 2 days" and "Best 3" | USER |
| C6 | Delete a habit (changed) | A slow double click can never delete, and Delete habit no longer waits half a second | USER |
| C8 | Save warning | If this browser cannot save the habits, a note says so | USER |
| C0 | Look (changed) | A new look, futuristic but minimal, picked by the owner from five directions. The logo shows in the header and as the tab icon | USER |

### Rules
- **Past days:** any day inside the heatmap's 12 weeks, today included. Days after today stay closed. A day before
  a habit was added can be ticked too, since 1.0 stores no start date. An edit updates the streaks, the strip and
  the heatmap at once. (ORCH on the details, USER on the reach)
- The non-goal "Editing days older than the last 7" is removed. (USER)
- **Save warning copy:** "Your habits are not being saved on this device. Changes will be lost when you close
  this tab." It shows while saving fails and goes away after the next save works. It cannot be dismissed. (ORCH)
- **One theme**, which may now be dark. A theme switcher stays a non-goal. (ORCH)
- **Still no web fonts and no network.** Designs use system font stacks. (ORCH, the stack lock)

### Grill log (v1.1.0)
| # | Question | Decision | Tag |
|---|---|---|---|
| 12 | Can older days be changed? | Yes. Tap a day in the heatmap to open it | USER |
| 13 | Which number is which? | Label them Current and Best | USER |
| 14 | How should it feel? | Futuristic but minimal, "like discord" | USER |
| 15 | Feeling words | Owner: "Decide for me". Bright, rewarding, focused | ORCH |
| 16 | Name | Danial's Streaky Habit, logo without his name or initial | USER |

### Round 1 rulings (2026-10-10 21:43 to 21:49, design round 1, ledger H-02)
The owner picked D Orbit Rings' look and gave the key screen a new layout. These change the rows above where they say so.

| ID | Capability | What the user gets | Tag |
|---|---|---|---|
| C2 | Tick today, and any past day (changed again) | Each habit is a row in a list with a **Done today** button, a button that opens **that habit's year view**, and its Current and Best. The year view shows the last 12 months, and tapping a day ticks or unticks it for that habit. The overview calendar still opens any day in the day editor (every habit for that day). The per-habit 7-day strip is gone | USER |
| C3, C4 | Current and best streak (changed) | Shown on each row and again in the habit's year view | USER |
| C5 | Overview (changed) | The 12-week calendar becomes an overview: a band at the top on a desktop, a popup or page behind a button on a phone. Day numbers bigger | USER |

- **Past days:** any day in the last 12 months, today included (today back to the same date last year). Days after today stay closed. Replaces "any day inside the heatmap's 12 weeks". (USER on the reach, ORCH on "same date last year")
- **Layout:** the habit list scrolls inside its own frame, the page does not. The add field sits outside that frame and does not move when habits are added. On a phone it is pinned at the bottom. (USER, ORCH on "below the list on every width")
- **Delete habit** lives in the habit's year view. **Done today** toggles. (ORCH, reversible)

| # | Question | Decision | Tag |
|---|---|---|---|
| 17 | Which direction? | D Orbit Rings, colours and fonts, with his list layout | USER |
| 18 | How far back does the year view go? | The last 12 months | USER |
| 19 | Does tapping an overview day still open it? | Yes, the day editor | USER |