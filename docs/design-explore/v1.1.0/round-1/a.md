# Direction A, Night Console

**File** `a.html`, made 2026-10-10
**Checks** `checks/a/check.py` and the screenshots beside it

## Thesis
A chat app's dark console. Each habit reads like a channel (a `#` before its name, a hover band like a message row), each streak is a live badge, and the 12-week heatmap is the scrollback log with this week at the bottom next to the composer. Dark layered slate surfaces and one teal accent.

Design read. A one-screen personal tool for a phone, in the visual language of Discord, built in plain CSS on system fonts, with the strip and the live badge as the one place the page is loud.

## What it bets on
| Bet | Why |
|---|---|
| Three slate surfaces (app bar, page, log pane) and one teal | The owner asked for "like discord". Layered dark panes and a single bright accent are what make that family recognisable at a glance |
| A done day morphs from an open circle into a filled teal squircle with a check | The Discord server icon move. Done and not done differ by shape and by the check, not only colour. It is the rewarding moment of the page |
| Current is a live badge on the left, Best a quiet chip on the right | The owner wants "left side is current and right is best". Current is solid teal with a check when today is done, a dashed teal outline while the run is still holding, a grey chip at zero. Best never changes style |
| The heatmap is a calendar log. Weeks are rows, oldest on top, this week at the bottom, every past day shows its date | "The missing previous dates is actually a big thing". With dates printed in each cell the person finds "22 September" without counting columns, and every cell is a 41 to 47 px target |
| Heat levels use a growing bar as well as a tint | Empty days are dashed slots, partly done days carry a bar at a quarter, half or three quarters, an all-done day is solid teal. Levels read without colour |
| The add field is a docked composer, like a chat input | It stays in reach on a phone and reads as "type here to add". The label "New habit" sits inside the composer, never as a placeholder |
| P1 is a bottom sheet on a phone and a popout beside the tapped day on desktop | Discord uses both. On desktop the light scrim keeps the habit rows readable, so the person sees Best jump and the cell fill while ticking |

## What it costs
- The heatmap orientation changes a 1.0 build rule ("12 columns, one per week, newest on the right"). Here it is 7 columns by 12 rows, newest week at the bottom. The owner needs to accept that rule change if A is picked.
- The log is tall on a phone (about 560 px), so the heatmap sits below the fold under three habits.
- Desktop at 1280 leaves empty space between three habit rows and the composer. A chat feed accepts that, but it is quieter than a dashboard.
- It is the most "app chrome" of the directions. If the owner wants a lighter, more airy look, this is the wrong bet.

## Tokens (the core)
| Token | Hex | Role |
|---|---|---|
| `--bg-0` | #0D1116 | app bar |
| `--bg-1` | #131920 | log pane, composer dock, dialog footer |
| `--bg-2` | #182028 | page and main feed |
| `--bg-3` | #212B35 | chips, composer, hover |
| `--raise` | #1E2731 | dialogs and the day editor |
| `--ink` / `--ink-soft` | #E7EDF2 / #9DABB8 | text |
| `--accent` / `--accent-ink` | #3CD3C1 / #04211D | the one teal, and text on it |
| `--heat-1..3` | #1A3739 / #1F5150 / #266F6A | partial heat tints (level 4 is the accent) |
| `--edge` | #66757F | open tiles and empty heat cells, 3:1 |
| `--danger-fill`, `--danger`, `--warn` | #C63A33, #FF8F86, #E9B949 | Delete habit, field errors, the save warning edge. Status only |

Type is the system sans stack, five sizes (11, 13, 15, 17, 20), weights 500 to 800, tabular numbers on every count. Radius rule is chips 8, controls 12, done tiles 14, panels and dialogs 16, and every open (not done) state is a circle.

## How each inventory row is reached
| ID | How |
|---|---|
| K1 | The default view |
| P1 | Tap or click any past day or today in "Last 12 weeks". Sunday 11 October is blank and cannot be opened. Tick a habit row to change it. The x button, Esc and the backdrop close it |
| M1 | The bin button on a habit row. Cancel, Esc and the backdrop close it. Delete habit removes the habit and the heatmap recounts |
| S1 | Prototype states, "S1 First visit" |
| S2 | Prototype states, the three "S2 Name error" items. Also live, by pressing Add with an empty field, a name over 40 characters, or a name already tracked |
| S3 | Prototype states, "S3 12 habits reached". Also live, by adding habits until there are 12 |
| S4 | Prototype states, "S4 Save warning" |
| S5 | Prototype states, "S5 Could not be read". The x dismisses the note |

The 7-day strip ticks for real, and so does the day editor. Every streak number is computed from the sample history, never typed in.

## Sample history and the numbers it gives
| Habit | Current | Best | Note |
|---|---|---|---|
| Read 20 pages | 8 days (3 to 10 Oct, today done) | 15 (8 to 22 Sep) | live badge |
| Stretch 10 minutes | 4 days (6 to 9 Oct, today open) | 9 (24 Aug to 1 Sep) | holding badge. 22 Sep was missed. Ticking it in the day editor joins two runs and Best becomes 13 |
| No phone after 11pm | 2 days (8 to 9 Oct, today open) | 6 (2 to 7 Aug) | holding badge |

Today's heat cell is level 1 (1 of 3). Ticking Stretch today makes it level 2 and Current 5 days.

## Choices the brief did not settle
- S3 needs twelve habits, so it adds nine more names with no history ("Drink 2 litres of water" and others). They exist only in that state.
- In S1 and S5 there are no habits, so the heatmap cells are not openable (a day editor with nothing in it has no job).
- The delete title uses straight quotes to match the brief's copy exactly.

## Check results (`python -B checks/a/check.py`)
| Check | Result |
|---|---|
| Console errors | 0 |
| Sideways scroll at 360 | none (scrollWidth 360, also none in S2, S3 and S5) |
| Sideways scroll at 1280 | none |
| Body text `--ink` on `--bg-2` | 13.94 |
| Secondary text `--ink-soft` on `--bg-2` | 7.01 |
| Accent `--accent` on `--bg-2` (holding badge text, done tile) | 8.84 |
| Text on the accent `--accent-ink` on `--accent` | 9.09 |
| Lowest text pair | day number on heat level 3, 4.99. Delete habit text, 4.87 |
| Lowest graphic pair | level bar on heat level 3, 3.16. Open tile edge on the page, 3.46 |
| Day buttons | 51 by 94 at 390, 47 by 90 at 360 (tile 44 and 40) |
| Heat cells | 47 at 390, 43 at 360 |
| Day editor tick on 22 Sep | cell level 2 to 4, Stretch Best 9 to 13, "3 of 3 habits" |
| Esc and backdrop | close P1 (phone and desktop) and M1 |
| Focus ring | 2px teal, visible on a day button (`focus-1280.png`) |
| Reduced motion | transitions are 0s |

All 27 measured pairs pass AA. The full table prints from the script.

## Suggestions (not built)
- A short hint under "Last 12 weeks" such as "Tap a day to change it", since the heatmap is now the way to fix older days.
- Typographic quotes in the delete title.
- Keep the composer visible on the desktop at all times but let the feed anchor to the bottom like a chat, once there are more than six habits.
- A keyboard shortcut to jump to today's cell in the log.
