# Logo brief, Streaky Habit v1.1.0

**Date.** 2026-10-11 · **Ruling.** The owner, 2026-10-11, "redraw both marks", Streaky Habit's mark grows from the orbit ring, four directions, each QA-checked, he picks on the design board. No "Danial" and no "D" in the mark (`../RULINGS.md`).

## The product
Streaky Habit is a daily habit tracker for one person on a phone. One screen, offline, no account. A list of habits, a Done today tick on each, the current and best streak, a 12-week band of days and a year view.

## The source motif, the orbit ring
The orbit ring is the one expressive element in the app (locked direction F2 "Orbit List, revised", `../final/system.md`). **The ring is the day.** One segment per habit, clockwise from the top in list order, small even gaps between segments. Done is a thick amber arc, not done a thin grey arc, and a day with every habit done fills its core. Done differs by stroke width and fill, never by hue alone. Everything else on the page is quiet dark charcoal.

Read `../final/today.html` (the 12-week band of rings) and `../final/overview.html` before drawing.

## Tone
Steady, warm, quietly proud of a run of days. A personal tool, never a fitness gym, never a game. One warm amber light on charcoal.

## The category to stand apart from
Habit trackers and streak counters. Their marks lean on concentric activity rings, streak flames, checkmarks in circles and rounded squares, calendar grids, progress spinners and loading arcs. A ring is close to that category by nature, so every ring direction must carry one idea a progress ring does not.

## Hard constraints (every direction)
1. **One colour, fill only.** The production mark is one or a few `<path>` elements, no `stroke` attributes (outline any stroke into a filled path), `fill-rule` allowed. The app colours it with CSS `.mark { fill: currentColor }` in amber, so it must be complete in one flat fill. No gradient, no opacity, no glow. The thick and thin weights of the app's ring are allowed, since weight is form, not colour.
2. **Its real slots.** The app header shows it at 28 x 28 px (32 on desktop) beside the live wordmark "Streaky Habit" (system font stack, 700, -0.01em) on the page `#18191C`, in `#FFB020`. The favicon is the mark alone in `#FFB020` on a transparent 16 x 16 ground, no tile (owner, 2026-10-11 20:40, "no background color or tile"), every edge on a whole pixel at 16 and 32 px. It must hold at both sizes.
3. **No "D", no "Danial".** No letter D, nothing that reads as a D at 16 px. The only letter allowed is an S, and only in the lettermark direction.
4. **No myths, no rationalisation.** One idea you can say in one sentence. No golden ratio claims.
5. **The wordmark is live text,** never traced into paths (licensed outlines). "Streaky Habit" on one line.
6. **No em or en dashes** anywhere in the file. Draw the mark, do not use an icon set.
7. **The idea must read at the real slots.** At 28 px and in the 16 px favicon, every feature that carries the idea is at least 2 px. A feature that only reads at hero size is texture, not the idea (round 1 retired two directions for this, `QA.md`).

## The four directions (one designer each, one idea each)
| Id | Type | The one idea |
|---|---|---|
| T1 | Abstract geometric | **The full day.** Three thick ring segments with equal gaps around a filled core, the app's day with every habit done. Pressure test against a camera aperture, the radiation trefoil, a three-pointed star, a loading spinner and concentric activity rings |
| T2 | Abstract, one stroke | **Another lap.** One thick ring drawn as a single band that runs past its own start at the top, the end passing over the beginning with a knockout gap. The ring keeps going, day after day. Pressure test against a power icon, a refresh arrow, a coiled spring, the letters O and Q and an awareness ribbon |
| T3 | Lettermark | **The orbit S.** An S drawn as two ring arcs in the ring's thick weight, the top arc open to the right and the bottom arc open to the left, their ends cut square like ring segments. Two days in a row write the S. Pressure test against a dollar sign, a snake, a yin-yang and the number 5 |
| T4 | Abstract, motion | **Wound up.** One thick arc that spirals inward, lap after lap, into the filled core of a full day. The streak winding tighter. Pressure test against a snail, a hypnosis spiral, a lollipop, a cinnamon roll and a loading spinner |
| T5 | Pictorial reduction | **Today on its orbit.** One full ring in the app's thin weight, the days going round, and one filled disc, today, riding on the ring at the upper right, cut free of it by a knockout gap. The ring's own language, thin for the run, filled for a day done. Pressure test against an avatar with a status dot, a notification badge, an engagement ring, a planet in orbit, a power icon and the letters O and Q |
| T6 | Build on T1, the owner's direction | **The thread, with today's arc.** The 1.0 mark (`../../../brand/mark.svg`, three done beads on one thick thread that turns a corner, today's open bead in the fourth corner) with one outer arc in the ring's thick weight round the outer corner of the top left bead, from its left round to its top, like one segment of T1's ring. Amber on charcoal as v1.1.0. Pressure test against a wifi or signal icon, a pattern lock, network nodes, a dumbbell, a stepper, a tetromino and the letters r and o |

T2 was retired after one QA review (`QA.md`). Its over-under crossing needs about 10 px of a 14 px favicon at 2 px per feature, so at 16 px it read as a letter O with accents. T5 replaces it.

## Output contract
A self-contained HTML brand sheet, exactly 1440 x 900, background `#0c0d10`, inline CSS and SVG only, no network, system fonts only (`'Segoe UI', system-ui, sans-serif`). Four sections.
1. **Hero.** The mark about 240 px, centred, in `#FFB020`, with the direction's id and one-sentence idea beneath in muted text (sentence case, no all caps).
2. **In the app.** The real header row on `#18191C`, mark 28 px in `#FFB020`, the word "Streaky Habit" 19 px 700 in `#EDEEF0`, a 10 px gap. Beside it the desktop size, mark 32 px and word 21 px.
3. **Legibility.** The mark at 96, 48, 28 and 18 px, then the favicon tile at 32 and 16 px at their actual pixel size, each with a small px label.
4. **Swatches.** The lockup on a dark card `#15171c` and on a light card `#f7f6f3` (mark in `#9A5B00`, word in `#1C2523`), and the mark alone in pure black on white and pure white on black.

Put the production sources in the sheet so they can be lifted without guessing.
- `<svg id="mark-src" viewBox="..." aria-hidden="true">` holding only the mark's path(s) with `fill="currentColor"` and nothing else.
- `<svg id="favicon-src" viewBox="0 0 16 16">` holding only the pixel-snapped mark in the brand colour, no tile rect, transparent.
Both sit at the end of the body hidden with `style="display:none"` (the `hidden` attribute does not hide an svg in Chromium, so the sheet must stay exactly 900 px tall).

Write the complete file (it must end with `</html>`) to the path you are given. Then reply with one line, the idea, the path and an honest self-critique naming the rubric criterion a reviewer is most likely to dock.
