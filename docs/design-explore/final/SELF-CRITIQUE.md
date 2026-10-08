# Self-critique (design step 8)

**Date** 2026-10-08 · **Files walked** `system.md`, `system.css`, `today.html`, `today-empty.html`, `delete-dialog.html`, `states.html` and their `.md` files
**Evidence** screenshots and scripts in `harness/_scratch/design-final/` (`verify.py`, `contrast.py`, `measure.py`, `zoom.py`, `gen_fragments.py`)
**Skills applied** `taste-skill:taste-skill` and `frontend-design:frontend-design`, both invoked. What transferred is listed at the top of `system.md`.

## Walk against the checklist

| Check | today | today-empty | delete-dialog | states | How it was checked |
|---|---|---|---|---|---|
| One primary action per view | Add is the only filled button. The beads are toggles, not actions. | Add | Delete habit (danger) with Cancel as secondary | n/a, a specimen sheet | screenshots |
| Spacing on the system scale | yes | yes | yes | yes, plus sheet-only spacing from the same scale | every margin, padding and gap uses a `--space-*` token or 0, checked by reading the shared block |
| AA contrast | yes | yes | yes | yes | `contrast.py`. Every text pair 4.5:1 or more, every control and graphic 3:1 or more, table in `system.md` |
| Every state present | S1 plus all three thread states | S2 | M1 | S3 (3), S4, S5, new habit row, hover, focus, press, disabled | inventory in `BRIEF.md` against the files |
| Real, consistent copy | yes | yes | yes | yes | strings checked against `brainstorm.md`, list of unworded copy below |
| No AI-template tells | none found | none found | none found | none found | list below |
| 390, 360, 1280 with no horizontal scroll | pass | pass | pass | pass | `verify.py` (scrollWidth and per-element right edge) |
| Console clean, no network | pass | pass | pass | pass | `verify.py` |
| Zero long dashes | 0 | 0 | 0 | 0 | `verify.py` counts U+2014 and U+2013 in every file in `final/`, md and css included |
| Same tokens and component CSS everywhere | yes | yes | yes | yes | `verify.py` compares every token with `system.css` and the component block byte for byte with `today.html` |
| Heatmap matches the sample | 81 cells match `heatmapLevels`, counts match the done lists, order is chronological, Fri 9 to Sun 11 Oct blank | all 81 at level 0 | same as today | n/a | `verify.py` |
| Touch targets | day cells 45.7 to 71.4 wide and 88 to 96 tall, icon buttons 44, controls 48 | controls 48 | buttons 48 | same components | `measure.py` |
| Done vs not done beyond colour | filled bead with a check vs hollow ring | n/a | n/a | yes | screenshots |
| Reduced motion | all transitions 0s | same | dialog animation `none` | same | Playwright with `reduced_motion="reduce"` |
| Keyboard | tab order is trash then the seven days per habit, then the field and Add. Focus ring visible on every control. | same | focus starts on Cancel (specified, not drawable statically) | forced focus looks shown | Playwright Tab walk, `focus-*.png` |

AI-tell sweep. No eyebrows or all-caps labels, no middle-dot strings in the UI, no long dashes, no gradients except the two functional thread fades, no glass, no cards except the heatmap panel and the dialog, no shadow except on the dialog, no decorative dots, no hand-drawn icons (Phosphor check, trash and x only), no invented numbers (all from `sample-history.json`), no purple, no cream with terracotta. One accent (the bead green) and one danger red, used only for errors and delete.

## What I changed during composition and critique

| # | Found | Change |
|---|---|---|
| 1 | DECISION change 1, heatmap levels 1 and 2 too close | Level 1 is a 7px dot in #78968B, level 2 an 11px dot in #4F7C70. The largest size step and the largest tone step now sit between 1 and 2. Every filled dot reaches 3:1 against the panel (B's level 1 was about 1.6:1). |
| 2 | Small heat dots rendered as 7 by 8 px ovals (percent sizes snapped unevenly, measured in pixels) | Dots use whole-pixel sizes (`--dot-0` to `--dot-4`). Beads moved from a fluid clamp to 32, 36 and 40 px steps for the same reason. |
| 3 | B's today ring (#A9B6B2, 1.91:1) and heat level 0 ring (2.03:1) were under 3:1 | Both now use `--ring` (3.13 on the page, 3.33 on the panel). `--halo` and `--heat-0` removed. |
| 4 | B drew keyboard focus as a ring on the bead, which collided with the today ring and replaced it | Focus is now a capsule outline around the whole day cell, so it also shows the true hit area. |
| 5 | B's dashed holding thread restarted its pattern at each cell edge, so the dashes met unevenly | Dash tiles are anchored on the boundary between yesterday and today. Checked at 3x zoom at 360 and 390. |
| 6 | B used off-scale spacing (6, 9, 10, 14, 18, 22, 28, 34, 72) and a 650 weight | Normalised to the 4px scale and to weights 400, 500, 600, 700. |
| 7 | Dialog edge against the dimmed page was 2.88:1 at a 45% scrim | Scrim raised to 50%, edge now 3.28:1. |
| 8 | The full-page render of M1 showed an undimmed page below the first screen | The page behind the dialog no longer scrolls while it is open. That is also the right behaviour for a modal. |
| 9 | The single column would stretch strips to 700px and more on tablets | Single column capped at 600px below 900px wide. |
| 10 | States sheet at 1280 used 40px beads inside phone-width frames (cramped strip), bead specimens shrank so the focus capsule hugged the bead, heat specimens sat in rounded boxes that read like app icons, groups did not follow where states live | Frames pin beads to 32px, bead specimens are full cell width, heat specimens sit on one panel surface, frames are grouped as "Add field", "Habit list" and "Component states" with the inventory ID in each caption. |
| 11 | The empty message was a single grey line that read as a hint, not a state | Same text, now a block lead ("No habits yet." 18/28 600 `--ink`) and a line, placed exactly where the first habit name would sit. |
| 12 | B carried its own demo heatmap data and a script | Replaced by `sample-history.json` exactly, and every golden is static with no script. |

## Copy the brainstorm does not word (for the orchestrator to approve)

| Copy | Where | Origin |
|---|---|---|
| Thursday 8 October | header date, full weekday and month | B |
| Habits | visually hidden h2 over the list | B |
| New habit | field label | B |
| Last 12 weeks | heatmap heading | B, kept by DECISION |
| None, All | legend ends | B, kept by DECISION |
| Jul, Aug, Sep, Oct and Mon, Wed, Fri, Sun | heatmap axes | B, kept by DECISION |
| No habits yet. Add one you want to do every day. | empty list (S2, S5) | the orchestrator's prompt. The brainstorm only says the list "says how to start". |
| Mark Ddd D Mon as done, never switching to "as not done" | day bead accessible name rule | the brainstorm's example, plus my rule that state lives in `aria-pressed` only |
| Ddd D Mon, 0 of 0 habits | heatmap cells with no habits | the brainstorm formula applied literally. Alternative if preferred, "Mon 20 Jul, no habits". |
| Delete Read 20 pages | trash accessible name | the orchestrator's prompt |
| Dismiss note | S5 dismiss accessible name | new |
| Delete "Read 20 pages"? | dialog title | brainstorm wording, kept with straight quotes. Typographic quotes would read better if the owner wants them. |

Sheet-only text, not app copy. "Streaks states", the sheet subtitle, the group headings "Add field", "Habit list" and "Component states", every frame caption and specimen label, the specimen cell names ("Level 0, none of the habits" and so on), and the sample inputs "Walk to the end of the street and back after dinner" and "read 20 pages".

## Interaction rules I specified that the brainstorm leaves open (for approval)
These are not features. They are the details a 1-to-1 build needs.
1. Focus moves to Cancel when the delete dialog opens. Esc acts as Cancel. After Cancel, focus returns to the trash button that opened it. After Delete habit, focus moves to the next habit's trash button, or to the "New habit" input if none is left.
2. The page behind the open dialog is inert and does not scroll.
3. Name errors appear when Add is pressed, not while typing. The typed text stays. The name is trimmed, then checked in the order empty, too long, duplicate, so one message shows at a time.
4. On desktop the S5 note sits at the top of the left column, not across both columns.
5. A strip whose first day is done and whose previous day is also done draws the run thread fading in from the left (`data-run-continues`). Otherwise the thin thread fades in, to say older days exist.

## Residuals and notes for plan
- **`:has()` is required** for the thread states (Chrome 105+, Safari 15.4+, Firefox 121+). The alternative is classes set by script. Plan should record the browser floor.
- **Day number weight 500** renders as 400 on Segoe UI (Windows has no medium). The fidelity gate runs on Windows and will see 400 in both the golden and the build, so they match.
- **Coloured fringes on small text** in the Windows captures come from subpixel font smoothing in headless Chromium. The computed colours are correct.
- **The holding dash is small on the narrowest phone.** At 360 about 9px of thread shows between Wed's bead and today's ring (a dash, a gap, a dash). It reads as dashed at 3x zoom and at 1x. If the owner wants it stronger, the cheapest change is a 2px today gap instead of 3px.
- **Level 3 never appears in the sample** because 3 habits cannot produce it. It is shown in the legend and in `states.html`.
- **S1 at 1280 x 800** is 837px tall. The add field ends at 789, so all of the main column is visible in the first screen.

## Suggestions (not in the brainstorm, not designed)
- Carried from DECISION, a flip animation on the streak number when it goes up.
