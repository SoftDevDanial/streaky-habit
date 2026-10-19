# Streaks brand

Made on 2026-10-10 at the owner's request ("Add a simple but decent looking logo for the examples apps", and "logo include in
their respective projects as well where needed"). Designed by the `logo-designer` agent, art directed by the orchestrator,
passed by the `logo-qa` agent. Drawn from the app's own tokens in `docs/design/system.md`.

## The mark
**"The thread is the streak."** Three done beads on one thick thread that turns a corner, and today's open bead in the fourth
corner, not yet strung. It is the app's own language: a done day is a filled bead, a not-done day a hollow ring, a run of done
days a thick thread. One closed path in one fill, built on one module m (bead 5m, thread 3m, gaps 2m, ring m, hole 3m). The
favicon is the same geometry at m = 1 px, with every edge on a whole pixel.

| Round | What happened |
|---|---|
| 1 | Two beads on a straight thread and an open bead. Rejected by the orchestrator after a render: it read as a dumbbell (a fitness cliché) and the favicon was a 4 px band |
| 2 | The 2 x 2 above. Tested against dumbbell, stepper, network nodes, tetromino, dice, pattern lock and letter readings |
| QA | **PASS, 22 of 24**, no gate below 2 except distinctiveness (1). A faint "r o" letter reading was judged weak and harmless, since the name always sits beside the mark |

## Files
| File | Use |
|---|---|
| `mark.svg` | the symbol in colour (`#3B6B60`) |
| `mark-black.svg`, `mark-white.svg` | one colour, ink `#1C2523` or `#F7FAF9` |
| `lockup-light.svg`, `lockup-dark.svg` | symbol and word for light pages and for dark pages (`#0d1117`, mark 8.1:1, word 15.1:1) |
| `favicon.svg` | the app's favicon from v1.1.0 |
| `sheet.html` | the brand sheet |
| `badges/` | static README badges, each a fact at a named version, never a live status |
| `screens/showcase.png` | the README image, two real captures from the pixel gate |

## Rules
- The word "Streaks" is live text in the app's own system font stack, so it looks a little different on each platform. Never
  trace a system font into paths (that copies licensed outlines).
- The word is `--bead-deep` on light pages, the same as the app's header.
- The favicon goes into the app in v1.1.0, through the design phase. The v1.0 screens and goldens do not change.

## Use of the name and logo
The names "Danial's Streaky Habit" and "Streaky Habit" and the logo in every file here, and in `src/icon.svg`, are not covered by the MIT licence in `LICENSE`. They stay all rights reserved. A copy or fork of the code uses its own name and logo.
