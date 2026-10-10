# Round 2 brief, F2 "Orbit List, revised": Danial's Streaky Habit, v1.1.0

**Phase:** design (sdlc:design step 4, critique and converge) · **Date:** 2026-10-10 · **Ledger:** S7 row 4, S1 row 3,
H-02 round 2 ruling · **Brainstorm:** "Round 2 rulings" at the end of `docs/brainstorm/brainstorm.md`
**Base:** `round-2/f.html` and `f.md`. Everything in F stays unless this file changes it. `BRIEF.md` (round 2) and
`../BRIEF.md` (round 1) still apply. Where they differ, this file wins.

## The owner's words (2026-10-10 22:59, after seeing F)
"For streaky mobile or overview, it should be last 12 weeks but have a button to check last year because each
habit on the list has yearly selection so we need some sort of yearly popup for overview as well. Both desktop and
mobile. Also, n eed button or icon to remove a habit in the list itself as well"

## The two changes
### 1. A year popup for the overview, P4 (new)
The overview keeps **the last 12 weeks**, as F draws it (desktop band, phone popup P3). A **Year** button on the
overview opens P4, the overview's own year view.

| Part | What |
|---|---|
| Where the button sits | Desktop: in the overview band's own header line, beside the legend or title, never inside the ring grid. Phone: in P3's header beside Close. (ORCH reading (g), flagged) |
| Button | Same treatment as the row's Year button. Visible text "Year", accessible name "Year view, all habits" |
| P4 content | **The last 12 months, every habit together.** Today (Saturday 10 October 2026) back to Friday 10 October 2025, the same 366 days as P2. Each day is D's small ring, one segment per habit, a filled core when every habit is done, exactly as the overview draws it. Legend None to All. Days after today closed and dim, days before 10 October 2025 blank. (ORCH reading (f), flagged) |
| P4 order | Month by month, newest month first, as P2 |
| P4 copy | Title "All habits", subtitle "The last 12 months", hint "Tap a day to change it." |
| Tapping a P4 day | Opens P1, the day editor for that day (every habit), as an overview day does. A tick in P1 updates P4's ring, the overview, the rows, P2 and every Current and Best at once |
| Desktop | A centred dialog like P2 (months across, inner scroll with the soft edge, day numbers no smaller than the overview's 16 px) |
| Phone | A full-screen sheet over P3, one month across, 44 px touch targets, day numbers about 16 px. Close returns to P3. P1 opens over P4 as its bottom sheet |
| Closing | Close, Esc and the backdrop (desktop). Esc closes the top layer first (P1, then P4, then P3) |

### 2. A delete button on every habit row
| Part | What |
|---|---|
| Control | A bin icon button on each row (D's Phosphor trash path, already inline in `f.html`). Accessible name `Delete "Read 20 pages"`. 44 px target |
| Treatment | Quiet like Delete habit in P2: grey at rest, the danger colour on hover and focus. Never a red fill. The red fill stays M1's confirm |
| What it does | Opens M1 for that habit (`Delete "Stretch 10 minutes"?`, "Its history is deleted too.", Cancel, Delete habit) |
| Delete habit in P2 | **Stays.** "in the list itself as well" reads as in addition to P2. (ORCH reading (h), flagged) |
| After a delete | M1 closes, focus moves to the next row's bin button, or the previous row's when the last row went, or the add field when the list is empty |
| Row fit | Name, Done today, Year, the bin, Current and Best at 360, 390 and 1280 px. No sideways scroll, no overlap, every target 44 px. Long names wrap or clip cleanly. The bin sits apart from Done today so one cannot be hit for the other (say how you placed it) |

S3 still reads "Delete one to add another." The bin on each row is now the short way to do that.

## Inventory, F2
Everything in F (K1, P1, P2, P3, M1, S1 to S5) plus:
| ID | Screen, popup or state | Content |
|---|---|---|
| P4 | **Overview year view (new)** | As above. Reached from the overview band (desktop) and from P3 (phone) |
| M1 | Delete dialog | Now reached from a row's bin **and** from P2 |

## Must not change
- The sample data and every figure: Read 20 pages Current 4 Best 9, Stretch 10 minutes Current 2 Best 5, No phone
  after 11pm no streak yet Best 14, the same seeded histories back to 10 October 2025. P4's rings come from the
  same histories as P2 and the overview, so a day reads the same in all three.
- The page does not scroll at 1280 x 800, 390 x 844 or 360 x 780. Only the list frame scrolls. The add field does
  not move between K1, S2 and S3.
- F's colours, type, radii, motion rules and contrast. Any new pair goes in the contrast table.
- The Prototype states tab never covers content, sits under every backdrop, never overlaps the add field.

## Output
`round-2/f2.html` (start from `f.html`, keep `f.html` untouched), `round-2/f2.md` (what changed from F, every new
reading, the row layout at 360 and 1280 and why, updated contrast table, suggestions not built), render checks in
`round-2/checks/f2/` (start from `checks/f/check.py`, keep every F assert that still applies, add asserts for P4 and
the row bin).
