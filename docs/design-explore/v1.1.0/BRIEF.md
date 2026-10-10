# Design brief: Danial's Streaky Habit, v1.1.0

**Phase:** design (sdlc:design, steps 1 to 3) · **Date:** 2026-10-10 · **Run with the owner** (not delegated)
**Sources:** `docs/brainstorm/brainstorm.md` (1.0 rules plus the v1.1.0 delta), `docs/v1.1.0/CHANGE-LEDGER.md`, the 1.0
goldens in `docs/design/` (for content and rules only, not for looks)

## Who uses it
One person keeping a few daily habits, on a phone, a few seconds at a time. They tick today, glance at their
streaks, and now and then fix or add an older day they forgot.

## The one job of the key screen
Show in one glance what is done today and how long each run has lasted, make ticking a day a single tap, and let
any past day be opened and corrected.

## Three feeling words
**Bright, rewarding, focused.** (Chosen by the orchestrator, the owner said "Decide for me".)

## What the owner asked for
- "Futuristic but minimal", "Like discord and stuff like that."
- 1.0 was "great" but "so dull. Need to spice it up so it looks nicer."
- "the missing previous dates is actually a big thing", and the streak line must "show that left side is current and
  right is best".
- "Doesnt need to be functionable, as long as i can see the design. Including popups and modals or anything that
  requires a button click." Quick prototypes, design first. Working is fine if it is faster.

## Hard constraints
- **Platform:** a static web page. Phone first at 390 x 844, must work from 360 px, deliberate at 1280 px.
- **One theme per direction, light or dark.** No theme switcher (non-goal).
- **No network.** No web fonts, no CDN, no remote images. System font stacks only (for example
  `ui-sans-serif, system-ui, "Segoe UI", Roboto, sans-serif` and `ui-monospace, "Cascadia Mono", Consolas, monospace`).
  Icons only from Phosphor (MIT), inlined as SVG paths, never hand-drawn.
- **Accessibility:** WCAG AA text contrast (record the ratio of body text and the accent on its background), a visible
  keyboard focus, touch targets of at least 44 px (a day cell may be 40 px at 360 px if the gap makes up the hit
  area), reduced motion respected, done and not done differ by more than colour.
- **Real copy from the brainstorm.** Habits "Read 20 pages", "Stretch 10 minutes", "No phone after 11pm". Today in the
  samples is Saturday 10 October 2026.
- **Avoid the AI defaults:** a purple-to-blue gradient glow, acid green on black, cream paper with a serif and a
  terracotta accent, glass on every card.

## Logo
The mark stays: `docs/brand/mark.svg`, three done beads on one thick thread that turns a corner on a 2 x 2 grid,
and today's open bead in the fourth corner (`docs/brand/BRAND.md`). It may take the
direction's colours. The wordmark is live text "Streaky Habit" in the direction's type. No "Danial", no "D". The page
title is "Danial's Streaky Habit".

## Inventory (what every direction shows)
| ID | Screen, popup or state | Traces to | Content |
|---|---|---|---|
| K1 | **Today screen with three habits (KEY SCREEN)** | C1 to C5 | Add field, three habits with their 7-day strips, each streak line labelled "Current 4 days" and "Best 9" style, and the 12-week heatmap. Histories must agree with the numbers shown |
| P1 | **Day editor (new)** | C2 | Tap any past day in the heatmap. A popup titled with the date ("Tuesday 22 September") lists the three habits with a tick each, and closes. A tick there changes the streaks and the heatmap. Days after today cannot be opened |
| M1 | Delete dialog | C6 | `Delete "Stretch 10 minutes"?` "Its history is deleted too." Buttons "Cancel" and "Delete habit" |
| S1 | First visit | C1 C5 | "No habits yet." "Add one you want to do every day." Heatmap all empty |
| S2 | Name error | C1 | "Name the habit first.", "Keep it to 40 characters or fewer.", "You already track this habit." |
| S3 | 12 habits reached | C1 | "You track 12 habits, the most this app holds. Delete one to add another." Field and Add disabled |
| S4 | Save warning | C8 | "Your habits are not being saved on this device. Changes will be lost when you close this tab." |
| S5 | Saved habits could not be read | C7 | "Your saved habits could not be read, so the list was reset." with a dismiss button |

**Key screen:** K1, with P1 as the new interaction the owner cares most about.

## Prototype rules
- One self-contained HTML file per direction: inline CSS and JS, colours as CSS custom properties, no network.
- Clickable through the design's own controls: ticking a day on the strip, opening a past day from the heatmap and
  ticking in it, the bin and the delete dialog, Esc and the backdrop to close.
- States with no natural trigger (S1 to S5) sit behind a small fixed bar labelled "Prototype states", clearly not part
  of the design.

## The five directions (the starting ground, chosen by the orchestrator)
| Dir | Name | Thesis | Theme and accent |
|---|---|---|---|
| A | Night Console | A chat-app-native dark console: habits read like channels, each streak like a live badge | Dark, layered slate surfaces, one teal accent |
| B | Neon Thread | The 1.0 thread grows a light: done days are glowing nodes joined by a light trail, the heatmap a quiet starfield | Dark deep blue, one luminous aqua |
| C | Daylight Instrument | Futuristic in daylight: a precise instrument with oversized Current and Best numerals and a crisp matrix heatmap | Light, cool white, electric cobalt |
| D | Orbit Rings | Each habit is a ring that fills through the week, the current streak at its centre | Dark charcoal, one warm amber accent |
| E | Command Line | Keyboard-first and monospaced, habits as aligned rows of marks, the add field like a command palette | Light pale graphite, ink text, one signal orange |

Each direction is a genuinely different bet, not a colour swap. Output: `round-1/<a|b|c|d|e>.html`, then
`round-1/compare.html` by the orchestrator, with the orchestrator's recommendation.
