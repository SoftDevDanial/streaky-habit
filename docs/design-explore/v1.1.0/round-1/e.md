# Direction E, Command Line

**File** `round-1/e.html` · **Checks** `round-1/checks/e/` (script `check_e.py`, `results.json`, 38 screenshots)

## Thesis
Keyboard first and monospaced. Habits are aligned rows of marks under one shared week header, the add field is a command palette in the top bar, and past days live in a 12-week calendar you can read and tap.

Design read. A personal one-screen tool for one person on a phone, shown to visitors, in the language of a modern keyboard tool (a command palette in a polished developer app), built in plain CSS on the system monospace stack with one signal orange. Dials are variance 4, motion 3, density 6.

## The bet
- **Orange means live, and nothing else.** It marks today's column, the Current chip while a run is alive, the keyboard cursor (focus ring and the bar beside the focused row), the palette caret and prompt, and the two things that need attention now (a name error, the save warning). Everything else is ink on pale graphite. At 0 the Current value drops its chip, so the orange disappears when nothing is live.
- **Left is Current, right is Best, on every row.** "Current" and an orange chip on the left, "Best" and the number on the right. On desktop both sit under the name, Current first.
- **The heatmap is a calendar.** Seven columns Monday to Sunday, twelve rows of weeks, newest at the bottom. Every cell prints its date, so a missing day is found by reading, not guessing, and each cell is a 44 px button (41 px at 360) that opens the day editor. The level is a 4-segment meter in the cell, and the count of ink segments is the level, so levels differ by count, not tone.
- **Visible keys, never key-only.** The palette shows `/` and the Add button shows the return key. A Keys pane lists every shortcut from 768 px. The day editor footer shows its keys. Every action also works by tap.

## What it costs
- The calendar is tall on a phone (about 700 px). The habits stay above the fold and the calendar starts below them.
- Monospace is wider than a sans, so long habit names wrap sooner (they wrap, they never overflow).
- The light theme is calm rather than "futuristic" in the neon sense. The futurism is in precision and keyboard feel, not glow.
- On desktop the left column is short with three habits, so there is open space under the Keys pane. It fills as habits are added.

## 1.0 rules this direction changes
| 1.0 rule | Here | Why |
|---|---|---|
| Heatmap is 12 columns (weeks) by 7 rows (Monday to Sunday), newest week on the right | 7 columns (Monday to Sunday) by 12 rows (weeks), newest week at the bottom | Seven columns give 44 px cells at 390 px and 41 px at 360 px, so every past day is a real tap target and can print its date. Twelve columns would give 24 px cells |
| Heat levels differ by dot form, size and tone | Levels are 0 to 4 ink segments of a 4-segment meter | Count reads apart without colour and stays crisp at small sizes |
| Each strip cell shows its own weekday and day number | One shared week header above all habits, today in orange with a bar | Makes the habits read as aligned rows. Each mark button still carries the full name, for example "Mark Tue 6 Oct as done" |
| Done is a filled bead joined by a thread | Done is a solid ink square with a check, not done is a hollow square | The mono row of marks is this direction's language. Done and not done differ by fill and the check |
| At 0 the streak line reads "No streak yet" | It reads "Current" then "No streak yet" | Keeps the Current label on the left in every state |

## How each inventory row is reached
| ID | By tap | By keyboard |
|---|---|---|
| K1 | Default view | Tab moves palette, Add, then the habit grid and bins, then the calendar |
| P1 | Tap any past day in the 12 weeks calendar, for example 22 Sep | Tab to the calendar (lands on today), arrows move by day and week, Enter or Space opens it. Arrows Up and Down move between habits in the editor, Space ticks |
| M1 | The bin on a habit row | Tab to a bin and press Enter, or press Del or Backspace on any mark in that row |
| Close P1 and M1 | The x button, Cancel, or a tap on the backdrop | Esc |
| S1 to S5 | "Prototype states" tab, bottom left | Tab to the tab, Enter, pick a state |
| S2 also | Type nothing, more than 40 characters, or "read 20 pages", then Add | The same, with `/` to focus the field and Enter to add |

Days after today (Sun 11 Oct) are drawn as an empty outline and are not buttons.

## Sample data
The three histories are written as runs of done days from Mon 20 Jul to Sat 10 Oct, and every number on screen is computed from them.

| Habit | Current | Best | 22 Sep | Strip, Sun 4 to Sat 10 |
|---|---|---|---|---|
| Read 20 pages | 4 days (today done) | 9 (14 to 22 Sep) | done | done, done, open, done, done, done, done |
| Stretch 10 minutes | 2 days (holds from yesterday) | 7 (15 to 21 Sep) | open | done, done, open, open, done, done, open |
| No phone after 11pm | 6 days (holds from yesterday) | 11 (27 Jul to 6 Aug) | open | done six times, then today open |

Ticking Stretch on Tuesday 22 September joins two runs (15 to 21 Sep and 23 to 26 Sep), so its Best goes from 7 to 12 and that calendar cell goes from level 1 to level 2. Ticking Stretch today takes Current from 2 to 3 days and today's cell from level 1 to 2. The 12-habit state adds nine habits with seeded random histories.

## Tokens
| Token | Hex | Role |
|---|---|---|
| `--bg` | #E6E8EB | page, pale graphite |
| `--panel` | #F5F6F8 | panes and top bar |
| `--raised` | #FCFCFD | palette field, dialogs, open mark fill |
| `--well` | #EBEDF0 | calendar cell, hover |
| `--ink` | #15181C | text, done marks, meter segments, primary buttons |
| `--ink-soft` | #535A64 | secondary text |
| `--mute` | #737A84 | open mark stroke |
| `--signal` | #FF5A1F | Current chip, today bar, caret (always with ink text on it) |
| `--signal-ink` | #B23A00 | orange text, today ring, focus cursor, error |
| `--signal-tint` | #FFE6D9 | today column, open day, save warning |

Type is the system monospace stack only (`ui-monospace`, Cascadia Mono, SF Mono, Menlo, Consolas). Sizes 11, 13, 15, 17. Radius rule is panes 12, controls and cells 8 (calendar cells 6), marks and keys 4. Icons are Phosphor x, check and trash, copied path strings. The mark is `docs/brand/mark.svg` in ink, also the tab icon.

## Contrast (computed by the check script from the page's own tokens)
| Pair | Ratio |
|---|---|
| Body text, ink on panel | 16.47 |
| Body text, ink on page | 14.51 |
| Secondary, ink-soft on panel | 6.44 |
| Secondary, ink-soft on page | 5.68 |
| Accent text, signal-ink on panel | 5.55 |
| Accent text, signal-ink on calendar cell | 5.12 |
| Current chip, ink on signal orange | 5.71 |
| Add and Delete habit, light text on ink | 16.47 |
| Save warning, ink on orange tint | 14.90 |
| Focus ring, signal-ink against panel and page | 5.55 and 4.89 |
| Open mark stroke against panel and today tint | 4.01 and 3.63 |
| Meter segment, ink against cell | 15.18 |

The signal orange fill itself is 2.88 against the panel, so it is never used alone to carry meaning. It always holds ink text (the chip) or sits beside orange text (the today bar).

## Check results
- Console errors 0, page errors 0, network requests 0.
- No sideways scroll at 360 px in K1, P1, M1 and S1 to S5, and no element pokes past the viewport.
- P1 by tap and by keyboard (7 Tabs from the page top reach the calendar, arrows move, Enter opens, Esc closes and focus returns to the cell). M1 by tap, by Tab and Enter on a bin, and by Del on a mark. Both close with Esc and the backdrop.
- Touch targets are marks 44 by 44 (41.4 by 44 at 360), calendar cells 44 (41.4 at 360 with a 4 px gap), bins and Add 44 tall.
- Reduced motion turns every transition and animation off (checked on the mark transition).

## Suggestions (not built)
1. Left and Right arrows inside the day editor to step to the previous or next day without closing it.
2. A key to jump the calendar cursor back to today.
3. Number keys 1 to 9 to tick a habit in the day editor.
4. Hovering a habit row could highlight its done days in the calendar.
5. A month label gutter beside the calendar at 430 px and up, where it fits without shrinking cells below 44 px.
