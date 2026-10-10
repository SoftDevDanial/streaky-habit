# Compose brief: Danial's Streaky Habit v1.1.0 (sdlc:design steps 5, 6 and 8)

**Date:** 2026-10-11 · **Ledger:** S7 row 6, H-02 final ruling · **Owner's words:** "Both looks good. We can procceed as usual"

## The accepted direction
`round-2/f2.html` (F2 "Orbit List, revised", ring numbers centred at `7b79e25`) with `round-2/f2.md`, `round-2/f.md`
and `round-2/BRIEF-F2.md`. Every reading in f.md and f2.md stands (ledger H-02, readings (a) to (h) and the
designer's). The prototype is the truth for look, copy, figures and behaviour. Your job is to turn it into a locked
system and one golden per screen. Not a redesign. Nothing new.

## Rulings for this step (ORCH, reversible, from the open items)
1. **The 2.97 pair is lifted.** A thin not-done segment on a hovered or open day draws in a colour that meets 3 to
   1 against `--raise` (f2.md suggestion, for example `--ink-soft`). Record the new ratio.
2. **Numbers centre by their ink, everywhere.** The owner's note: "the numbers surrounded by the yellow lines should
   be centered". f2 fixed the rings (alphabetic baseline, `dy .367em`, proportional figures). P2's beads (HTML
   spans) still sit about 0.7 px low on a phone. Centre every number inside a ring, bead or circle the same way, and
   measure it (ink centre within 0.3 px of the shape's centre at 390 and 1280).
3. **The header mark** stays the current `docs/brand/mark.svg` recoloured, as in f2. The logo is redrawn with the
   name "Streaky Habit" after this step and swapped in before finalize. Keep the mark in one inline `<svg>` per page
   so the swap is mechanical.

## Output, all in `docs/design-explore/v1.1.0/final/` (nothing anywhere else)
| File | What |
|---|---|
| `system.md` + `system.css` | Step 5. Colour roles (not only hex), type scale, spacing scale, radius rule, elevation, motion (with reduced motion), breakpoints, the component inventory (button kinds, icon button, ring, bead, row, field, dialog, sheet, band, popup, banner). **Every text and non-text pair with its WCAG ratio**, computed from the tokens. A token not in f2 needs a written reason |
| One golden `<screen>.html` + `<screen>.md` per screen below | Step 6. Self-contained, `system.css` values inlined in a `<style>`, real content, no network, no Prototype states tab, static (no script needed to show the state). Each renders correctly at 360 x 780, 390 x 844 and 1280 x 800, the phone and the desktop layout from one file as f2 does. The `.md` gives intent, states, the exact copy, icons, sizes and spacing that matter, and which inventory row and capability it serves |
| `sample-history.json` | The seeded histories of the three habits back to 10 October 2025, and the nine extra habits for S3, exactly as f2 computes them. Current and Best from it must match every golden |
| `MANIFEST.md` | Every inventory row (K1, P1, P2, P3, P4, M1, S1 to S5) mapped to its golden file and the state shown. Keep the 1.0 file name where the screen's job is the same (`today.html` for K1, `today-empty.html` for S1, `delete-dialog.html` for M1, `states.html` as the specimen sheet for states without their own screen). New names for new screens (for example `day-editor.html`, `year-view.html`, `overview.html`, `overview-year.html`). Say which golden shows which width matters |
| `LINKS.json` | For step 7 (the orchestrator wires and drives it). Format `{"links": [{"from": "a.html", "role": "button", "name": "Year view, Read 20 pages", "to": "year-view.html", "exact": true}, {"from": "x.html", "key": "Escape", "to": "a.html"}, {"from": "x.html", "click": [10, 10], "to": "a.html", "why": "backdrop"}]}`. Every natural trigger and every close between goldens, at the width where it applies (add `"width": 390` or `1280` to a link when it only exists there) |
| `SELF-CRITIQUE.md` | Step 8. Walk every golden against the list (one primary action per view, alignment and spacing on the scale, AA contrast, every state present, real and consistent copy, no AI-template tells per the loaded skills, works at 360, 390 and 1280). What failed and what you changed. Then "copy the brainstorm does not word" and "interaction rules I specified", as 1.0's `final/SELF-CRITIQUE.md` did, for the owner's rulings |
| `checks/` | Your render checks (script, results.json, screenshots) |

Read 1.0's `docs/design-explore/final/` (today.md, states.md, SELF-CRITIQUE.md) for the shape of the notes. Never
write to `docs/design/` (1.0's immutable goldens) or to `docs/design-explore/final/` (1.0's staging).
