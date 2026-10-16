# Future upgrade: unlimited habits, each in its own colour

**Status.** Not built. An idea for a later version, to be brainstormed first because it changes the habit logic.
**Asked for.** 2026-10-16, by the owner in his note on UAT-03 at the v1.1.0 test.
**Ledger.** v1.1.0, Off-scope and new, row 28. The 12 habit limit stays in 1.1.0 on purpose (README Known limits, row 27).

## Why this note exists
Streaky Habit keeps at most 12 habits. That limit is intentional today. Every habit draws a thin grey arc on every
day of the ring, so more habits would mean thinner and thinner arcs. The owner wants a later version to drop the
limit and still keep each day readable.

## His words (typos fixed, voice kept)
"In the future upgrades note, one of the things needed is to change the habits logic so that we can have infinite
habits. The plan is, instead of a habit inhabiting all the dates as a grey line, remove the grey line altogether and
only light up the ones that are ticked. For example, if we have Habit 1, Habit 2 and Habit 3, and Habit 1 is ticked on
5th October 2026, all the other days will not have a grey line. Only 5th October will have a full amber outline. If I
do the same for Habit 2, then it will have 2 amber outlines that are divided equally into 2. Same logic if I do it for
Habit 3. This makes it so that we can have hundreds of habits. Also, I'm thinking of giving each habit a color that can
be changed with a color picker, but different habits can't have overlapping colors. So we can tell on each day which
one is ticked. The streak in each habit's year will connect with the same color. When clicking a day in the band, it
will have a scrollable list of the habits so we can click which one we did that day. I prefer a scrollable box of the
list instead of the whole modal being scrollable."

## What the user would get
- **No habit limit.** Tens or hundreds of habits.
- **A ring that shows only what was done.** A day with nothing ticked has no arcs. One ticked habit draws one full
  outline. Two ticked habits split the ring into two equal arcs, three into three, and so on.
- **A colour per habit.** Chosen with a colour picker, never the same as another habit's colour, so a day shows which
  habits were done.
- **Year views in the habit's colour.** The thread that joins a streak's days takes that habit's colour.
- **A day editor that scrolls its list, not the whole window.** The habit list sits in its own scrollable box.

## What it would change
| Area | Change |
|---|---|
| Brainstorm | The 12 habit limit leaves the rules. A colour per habit is a new capability |
| Design | The ring drawing (ticked arcs only, split equally), the colour picker, the scrollable list box in the day editor, coloured threads in the year views |
| habit-logic | No `MAX_HABITS` cap. A colour stored with each habit, kept unique |
| app | The ring renderer, the day editor list, the colour picker, a new saved format that reads the old one |

## Questions for the brainstorm
- How many colours stay easy to tell apart, in both themes, and for someone who is colour blind?
- What does a fully done day look like when the middle no longer fills amber for "every habit done"?
- How does the overview list stay usable with hundreds of habit rows?
