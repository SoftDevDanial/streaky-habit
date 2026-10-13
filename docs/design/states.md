# States sheet (specimen, not a screen)

**File** `states.html`
**Covers** S2, S4 and S5, the states that are a part of K1 or S1 rather than a screen of their own

## Frames

| Frame | Inventory | Where it sits in the app |
|---|---|---|
| Add pressed with no name | S2 | K1's composer, message above the field |
| A name longer than 40 characters | S2 | same |
| A name already tracked, ignoring case | S2 | same |
| Save warning | S4 | K1, between the band (desktop) or the header (phone) and the list, in `.banners` |
| Saved habits could not be read | S5 | S1 with the note in `.banners` above the empty list |

Each frame uses the app's classes at the page's width, so 360 and 390 show the phone composer (label above) and 1280 the desktop one (label left, message above the field). The sheet's title, captions and spacing are sheet-only and live in the second style block.

## Exact copy

| State | Text |
|---|---|
| S2 empty | Name the habit first. |
| S2 too long | Keep it to 40 characters or fewer. |
| S2 duplicate | You already track this habit. |
| S4 | Your habits are not being saved on this device. Changes will be lost when you close this tab. |
| S5 | Your saved habits could not be read, so the list was reset. |
| S5 dismiss name | Dismiss note |

Typed text shown, not app copy. "Read twenty pages of a novel before bed each night" (50 characters) and "read 20 pages".

## Rules per state
- S2. The message appears when Add is pressed, the field gets `aria-invalid="true"` and the `--danger` edge, the typed text stays, the field does not move (the message grows the bar upward). Checks run empty, then too long, then duplicate.
- S4. `role="status"`, no dismiss, shown while saving fails and gone after the next save works.
- S5. `role="status"`, Dismiss note removes it and focus moves to the field.

## Links
Dismiss note leads to S1 (`today-empty.html`).
