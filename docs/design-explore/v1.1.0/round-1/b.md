# Direction B, Neon Thread

**File** `b.html` (one self-contained page, no network) · **Checks** `checks/b/` · **Date** 2026-10-10

## Thesis
The 1.0 thread grows a light. A done day is a lit aqua node with a check, and two done days side by side are joined by a glowing trail. Today's open node waits at the end of a dashed trail while yesterday is lit. The past is a quiet starfield of 84 days, each one a button that opens the day.

Design read. A personal one-screen habit tool for one person on a phone, shown to visitors, "futuristic but minimal". Built in plain CSS on system fonts, with the lit thread as the single expressive element.

## What it bets on, and what it costs
| Bet | Cost |
|---|---|
| Glow is spent in one place, the done nodes and the run trail. Everything else is flat deep blue, so a glance reads "lit means done" | Five lit nodes in a row is a lot of light. If the owner wants calmer, the halo can drop a step without touching the rest |
| Light lives in two dark "wells" (the strip rail and the starfield). Text sits on the page blue, light sits in the wells. It gives the page depth without cards everywhere | Two more surfaces to keep consistent in the build |
| The streak line is literally a line. "Current 4 days" on the left, a hairline, "Best 9" on the right, so left is current and right is best without a legend | None worth naming |
| The day editor shows each habit's streak line live, so ticking a forgotten day visibly moves Best (Read 20 pages goes from Best 9 to Best 18 when 22 Sep is ticked) | The editor is taller than a bare list of ticks |
| On desktop each habit becomes one line of light (name and streak on the left, the rail in the middle, the bin on the right), and the day editor opens as a popover beside the starfield, pointing at the row of the day | Two layouts to build (stacked under 1200 px, one line from 1200 px) |

## 1.0 rules this direction changes
| 1.0 rule | Neon Thread | Why |
|---|---|---|
| Heatmap is 12 columns (weeks), newest on the right, rows Monday to Sunday | **Turned on its side.** 7 columns (Mon to Sun) by 12 rows (weeks), oldest week at the top, this week at the bottom. Month labels sit on the left, on the first row whose Monday falls in that month (Jul, Aug, Sep, Oct) | Every day now opens the editor, so every day is a touch target. 12 columns on a 358 px phone gives about 24 px per day. 7 columns gives 45.8 px at 390 and 41.8 px at 360 (measured with a desktop scrollbar taking 15 px, 44 px on a real 360 phone). It also reads like a calendar, so "Tuesday 22 September" is found by month and weekday |
| Heatmap sits in a rounded panel | On phones under 600 px the starfield runs edge to edge (hairline top and bottom), on desktop it is a sticky panel | The extra width is what keeps each day at a full touch target |
| Heatmap level 0 to 4 as dots of 6 to 17 px | Level 0 a hollow 8 px ring, levels 1 to 4 filled 6, 9, 12 and 15 px "stars" in four tones of the one aqua | The starfield look, still told apart by form and size first, tone second |
| Radius, pills for controls | Controls 12 px, containers 16 px, nodes and stars round | Closer to the chat-app feel the owner named, and different from 1.0's soft pills |
| Light theme | One dark theme (allowed by the v1.1.0 delta) | The thesis needs a night sky for the light to read |

Nothing else changes. Strip of 7 days, oldest left, today right. Current counts back from today if done, else from yesterday. Best is the longest run in the whole history. Levels are the share of current habits done that day. Days after today are blank and cannot be opened. Accessible names follow 1.0 ("Mark Tue 6 Oct as done", "Tue 6 Oct, 2 of 3 habits", "Delete Read 20 pages").

## Copy added beyond the inventory
| Where | Text | Note |
|---|---|---|
| Under "Last 12 weeks" | "Open any day to edit it." | Makes the new day editor discoverable. Hidden when there are no habits, because then the days cannot be opened |
| Hover tooltip on a star (pointer devices only) | The cell's accessible name, for example "Tue 22 Sep, 1 of 3 habits" | Not new content, the 1.0 accessible name made visible |
| Day editor, under the date | "1 of 3 habits" with that day's star | Same wording as the cell's accessible name |
| Close button in the editor | accessible name "Close" | |

## How every inventory row is reached
| ID | How |
|---|---|
| K1 | The default view. "Prototype states" then "K1 Today, sample data" resets to it |
| P1 | Tap or click any past day (or today) in the "Last 12 weeks" starfield. Tap a habit row in the sheet to tick or untick it. Close with the x button, Esc, or a tap on the dimmed backdrop. Focus returns to the day you opened |
| M1 | The bin button on any habit. "Cancel", Esc or the backdrop keeps the habit and returns focus to the bin. "Delete habit" removes it and its history |
| S1 | "Prototype states" then "S1 First visit". Adding a habit there works and lights up the starfield |
| S2 | Type in "New habit" and press Add (empty, more than 40 characters, or a name you already track). Also "S2 Name empty", "S2 Name too long" and "S2 Name taken" in the bar |
| S3 | "Prototype states" then "S3 12 habits reached" (nine habits added with no history, field and Add disabled, the note under the field) |
| S4 | "Prototype states" then "S4 Save warning". Not dismissible |
| S5 | "Prototype states" then "S5 Saved habits unreadable". List reset to empty, the note has a dismiss button |

The strip works too. Tap any of the 7 nodes to light or unlight it. The node flares once and the trail draws in from the lit neighbours (off under reduced motion).

## Sample history (today is Saturday 10 October 2026)
| Habit | Strip, Sun 4 to Sat 10 | Current | Best | Where Best comes from |
|---|---|---|---|---|
| Read 20 pages | done, no, no, done, done, done, done | 4 days | 9 | 13 to 21 Sep. 22 Sep is the forgotten day. Tick it in the day editor and Best becomes 18 (13 to 30 Sep) |
| Stretch 10 minutes | no, done, done, no, done, done, open | 2 days | 6 | 24 to 29 Aug. Yesterday is lit and today is not, so the trail into today is dashed |
| No phone after 11pm | done, done, done, no, done, no, open | No streak yet | 5 | 25 to 29 Jul. Tick Fri 9 and it reads Current 2 days |

The numbers are computed in the page from these histories, never typed. Tue 22 Sep starts at 1 of 3 habits (level 1).

## Tokens
| Token | Hex | Role |
|---|---|---|
| `--bg` | #0B1433 | page |
| `--well` | #070D24 | the strip rail and the starfield |
| `--surface` | #121D46 | dialogs, the sheet, notes |
| `--surface-hi` | #1B2A57 | hover fill, tooltip |
| `--line` | #24356B | hairlines, the unlit thread (decorative) |
| `--ring` | #6676AA | not-done node stroke, empty star, input and Cancel borders |
| `--ink` | #E9EEFF | primary text, focus ring |
| `--ink-soft` | #9DABD3 | secondary text, today ring |
| `--aqua` | #5CF2E3 | the one accent. Done node, run trail, current streak, Add |
| `--on-aqua` | #03211F | check mark and text on aqua |
| `--star-1` to `--star-3` | #27807A, #37AFA6, #4CD9CD | heat levels 1 to 3 (level 4 is `--aqua`) |
| `--danger` | #FF8090 | field errors, save warning edge, Delete habit |

Type is the system stack (Segoe UI Variable Display for the wordmark and dialog titles where present). Sizes 12, 14, 16, 18 and 22 px. Space on a 4 px scale. Motion 120 to 460 ms, only after a tap, all of it off under reduced motion.

## Contrast (computed by `checks/b/check.py` from the page's own tokens)
| Pair | Ratio |
|---|---|
| Body text `--ink` on `--bg` | 15.61 |
| Body text `--ink` on `--surface` (dialogs) | 14.06 |
| Secondary `--ink-soft` on `--bg` / `--well` / `--surface` | 7.92 / 8.42 / 7.13 |
| Accent `--aqua` on `--bg` (current streak text) | 13.14 |
| Accent `--aqua` on `--well` (done node, trail) | 13.98 |
| Check mark and Add text `--on-aqua` on `--aqua` | 12.30 |
| Not-done node `--ring` on `--well` | 4.34 |
| Input border `--ring` on `--bg` | 4.08 |
| Cancel border `--ring` on `--surface` | 3.67 |
| Stars, levels 1 to 4 on `--well` | 4.08, 7.18, 11.09, 13.98 |
| Field error `--danger` on `--bg` | 7.52 |
| Delete habit text on `--danger` | 7.60 |
| Focus ring `--ink` on `--well` | 16.61 |

Done and not done never differ by glow alone. Done is a filled node with a check, not done is a hollow ring. A run is a thick trail, a break is a thin dim thread. Heat levels differ by form (ring or filled) and size.

## Check results
| Check | Result |
|---|---|
| Console errors | 0 |
| Requests that are not `file:` | 0 |
| Sideways scroll at 360 (every state, both dialogs open) | none |
| Sideways scroll at 390 and 1280 | none |
| Touch targets at 390 | strip day 48.1 px wide, starfield day 45.8 px, bins 44, editor close 44, editor rows 64 tall, input and Add 48 tall |
| Touch targets at 360 | strip day 43.8 px, starfield day 41.8 px (allowed 40 at 360) |
| Starfield at 1280 x 800 | fully in view (top 108, bottom 784) |
| Day editor | Esc and backdrop close it, focus returns to the day, the edited star stays visible above the phone sheet, Sun 11 Oct cannot be opened |
| Delete dialog | focus starts on Cancel, Esc and backdrop close it and return focus to the bin |
| Reduced motion | node animation none, transitions 0s |

## Suggestions (not built, outside the brief)
1. Previous and next day buttons inside the day editor, so a run of forgotten days can be fixed without closing it.
2. Swipe down to close the phone sheet.
3. A small mark on the starfield's month labels for the 1st of each month, if finding a date still feels slow in testing.
4. Let the strip's today node pulse once when the app opens on a new day, as a "your thread is waiting" cue. Needs the owner's call because it is motion without a tap.
