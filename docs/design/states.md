# States sheet (specimen, not a screen)

**File** `states.html` · **System** `system.md`, `system.css`

## Intent
Show, in the locked system, every state that the three screens do not show on their own, so the build can match each one 1 to 1. Each frame is drawn at phone width and its caption says where it sits on the real screen. The sheet's own chrome (title, group headings, captions, frame outlines) is not part of the app.

## What the sheet covers

| Frame | Inventory | Capability | Where it sits in the app |
|---|---|---|---|
| S3 Add pressed with an empty name | S3 | C1 | The add form under the list on S1 or S2 |
| S3 Name longer than 40 characters | S3 | C1 | same |
| S3 Name already tracked, ignoring case | S3 | C1 | same |
| S4 Twelve habits, field and button disabled | S4 | C1 | same, after the 12th habit |
| A habit just added | Flow 1 | C1 C2 C3 C4 | The bottom of the list |
| S5 Saved habits could not be read | S5 | C7 | Top of the main column, above the (now empty) list |
| Buttons | system | C1 C6 | Add, Cancel, Delete habit in every state |
| Text input | system | C1 | default, focus, error, disabled |
| Day bead and icon button | system | C2 C6 | not done, done, today, today done, hover, done hover, focus, then trash at rest, hover, focus |
| Heatmap cell | system | C5 | levels 0 to 4, today, future |

Hover and focus are drawn with `.is-hover` and `.is-focus` classes that exist only on this sheet. In the app the same looks come from `:hover` (pointer devices only) and `:focus-visible`.

## Exact copy (app copy only)

| State | Text |
|---|---|
| S3 empty | Name the habit first. |
| S3 too long | Keep it to 40 characters or fewer. |
| S3 duplicate | You already track this habit. |
| S4 note | You track 12 habits, the most this app holds. Delete one to add another. |
| S5 note | Your saved habits could not be read, so the list was reset. |
| S5 dismiss (accessible name) | Dismiss note |
| New habit row | Read 20 pages, No streak yet, Delete Read 20 pages |
| Empty message (in S5) | No habits yet. Add one you want to do every day. |

Sample input shown in the S3 frames (typed by the user, not app copy). Empty, "Walk to the end of the street and back after dinner" (51 characters), "read 20 pages" (lower case, to show the duplicate check ignores case).

## Rules per state

### S3 name errors
- Shown after Add is pressed, not while typing. The habit is not added.
- Input gets `aria-invalid="true"` and a `--danger` border. The message line under the row (`#new-habit-msg`, `.field-error`, 14/20, `--danger`, 8px below) holds the text and is announced (`aria-live="polite"`).
- The typed text stays in the field so the user can fix it. Focus stays in the input.
- The name is trimmed before checking. Check order is empty, then too long, then duplicate, so only one message shows.
- The error clears when the name is accepted. The form grows by the 28px message line and nothing moves sideways.

### S4 twelve habits
- At 12 habits the input and Add are `disabled`. The input fill turns `--wash` with a `--thread` border, Add turns `--thread` with `--ink-soft` text, the label turns `--ink-soft`.
- The note uses the same message line with `.field-note` (`--ink-soft`) and wraps to two lines at phone width. The input keeps `aria-describedby` on it.
- Deleting a habit re-enables both and removes the note.

### A habit just added
- Appears at the bottom of the list with all seven beads hollow, today ringed, thin thread only.
- The streak line reads "No streak yet" (`span.cur.none`, `--ink-soft` 600). No best element is rendered while best is 0.
- The field empties after a successful add.

### S5 saved habits could not be read
- Shown once at start when saved data cannot be read. The list starts empty, so the empty message shows under the note.
- Note banner. `--wash`, 20px radius, padding 8 8 8 20, text 16/24 `--ink` with 8px vertical padding, dismiss button 44px (Phosphor "x") top right, 32px gap to the content below. `role="status"`.
- Dismiss removes the banner. Nothing else changes.
- On desktop it sits at the top of the left column, not across both columns, so the dismiss button stays near the text.
- In the sheet the brand is a `p` so the sheet keeps one h1. In the app it stays the page's h1.

### Component states
All as specified in `system.md`, Component inventory. Two notes. The day bead focus ring is a vertical capsule around the whole cell (weekday, number and bead), never a ring on the bead itself, so it cannot be confused with the today ring. In the bead specimens the thread is hidden because a lone bead has no neighbours.

## Specimen-only styling
The `sheet only` block at the end of the style element (`.sheet`, `.group`, `.frames`, `.frame`, `.frame-cap`, `.frame-body`, `.specs`, `.spec*`, `.is-hover`, `.is-focus`) is not part of the app. Frames pin `--bead-size` to 32px, the narrowest phone size, so the new-habit strip reads as it does on a 360 phone at any viewport.
