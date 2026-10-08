# M1 Delete confirmation

**Golden** `delete-dialog.html` · **System** `system.md`, `system.css` · **Opened from** "Delete Read 20 pages" on S1

## Intent
Deleting removes a habit and all of its history, which cannot be undone, so it asks once, plainly, and makes keeping the habit the easy choice. The page stays visible but dimmed behind it so the user knows what they are deleting from.

## Capabilities shown

| ID | Where |
|---|---|
| C6 Delete a habit | The dialog, its "Delete habit" action and its "Cancel" |

## States on this screen
- Dialog open over S1. S1 underneath is unchanged and `inert`, the page does not scroll, the backdrop is `--ink` at 50%.
- Focus starts on Cancel when the dialog opens (the safe choice). Not drawn in the golden, because a static page has no keyboard focus.
- Hover and focus looks of both buttons are in `states.html` (Component states).

Outcomes, for the flow check.
- **Cancel** or **Esc**. The dialog closes, the habit stays, focus returns to the trash button that opened it.
- **Delete habit**. The habit and its history are removed, the dialog closes, the heatmap recounts against the remaining habits, focus moves to the next habit's trash button, or to the "New habit" input if none is left.

## Exact copy

| Element | Text |
|---|---|
| Title (h2) | Delete "Read 20 pages"? (straight quotes, as worded in the brainstorm, with the habit name inserted as typed) |
| Body | Its history is deleted too. |
| Secondary button | Cancel |
| Danger button | Delete habit |

## Layout and spacing that matter (measured)

| Item | 390 x 844 | 360 x 780 | 1280 x 800 |
|---|---|---|---|
| Dialog box | 350 x 180 at x 20, y 332 | 320 x 180 at x 20, y 300 | 400 x 180 at x 440, y 310 |
| Title | one line, 28 tall, 24 from the top | one line | one line |
| Buttons | two equal columns, 145 wide each, 48 tall, 12 apart, 24 below the body | 119.5 each | 170 each |

Rules.
- Centred in the viewport both ways. Width is `min(400px, 100% - 40px)`, so on phones it keeps the same 20px side margin as the page.
- Padding 24. Title to body 8. Body to buttons 24.
- Cancel left, Delete habit right, equal width. Delete habit is the only filled button.
- Long habit names (up to 40 characters) wrap inside the title. The box grows in height, never in width.
- Entering motion. The backdrop fades in over 180ms, the dialog fades and rises 8px over 200ms. Under reduced motion both appear at once.

## Markup contract the build mirrors
- The app uses one `<dialog class="dialog">` opened with `showModal()`, with `role="alertdialog"`, `aria-modal="true"`, `aria-labelledby` the title and `aria-describedby` the body. Its `::backdrop` uses `--scrim`.
- The golden has no script, so it renders `<dialog open>` plus a `div.scrim[aria-hidden]` drawn with the same `--scrim`, and marks the page `inert`. The two render the same.
- Buttons sit in `form.dialog-actions[method=dialog]`, Cancel first (`.btn.btn-secondary`, value "cancel"), then Delete habit (`.btn.btn-danger`, value "delete").
- While the dialog is open, `html:has(.dialog[open])` and its `body` get `height: 100%; overflow: hidden` so the page behind does not scroll.
