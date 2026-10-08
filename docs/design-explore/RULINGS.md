# Design rulings: Streaks

**Date:** 2026-10-08 · **Ruled by:** orchestrator under the owner's delegation (**ORCH**, reversible)

The composer listed copy and interaction details the brainstorm leaves open (`final/SELF-CRITIQUE.md`).
They are ruled here so the plan phase does not have to guess.

## Added copy, approved
All copy in the "copy the brainstorm does not word" list of `final/SELF-CRITIQUE.md` is approved as
written: the date line, the hidden "Habits" heading, "New habit", "Last 12 weeks", "None" and "All", the
axis labels, "No habits yet. Add one you want to do every day.", "Delete <habit name>", "Dismiss note",
the day bead name "Mark Tue 6 Oct as done" (state carried by `aria-pressed`), and "0 of 0 habits" for a
heatmap cell when no habit exists.

## Interaction rules, approved
All five rules in "Interaction rules I specified" of `final/SELF-CRITIQUE.md` are approved:
1. Dialog focus: focus moves to Cancel on open, Esc acts as Cancel, focus returns to the trash button
   after Cancel, and after Delete habit it moves to the next habit's trash button or to "New habit".
2. The page behind the open dialog is inert and does not scroll.
3. Name errors appear when Add is pressed, not while typing. The typed text stays. The name is trimmed,
   then checked in the order empty, too long, duplicate, so one message shows at a time.
4. On desktop the S5 note sits at the top of the left column.
5. The thread fade at the left edge of a strip, as specified.

## Browser floor
The thread states use CSS `:has()`. The supported browsers are current Chrome, Edge, Safari and Firefox
(Chrome 105+, Safari 15.4+, Firefox 121+). Older browsers are out of scope.
