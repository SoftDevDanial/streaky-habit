# M1 Delete dialog

**Golden** `delete-dialog.html`
**Inventory** M1, delete a habit (C6)
**Opened from** the bin on the Stretch 10 minutes row (shown) or Delete habit in P2 (same dialog)

## Intent
One deliberate step between a tap on a bin and losing a habit's whole history. Cancel is the safe default.

## What the golden shows
K1 unchanged and inert under `--scrim`, M1 centred, `min(400px, 100vw - 32px)` wide, `--surface-2`, 20 radius, 20 padding, `--shadow-dlg`.

## Exact copy

| Element | Text |
|---|---|
| Title (h2) | Delete "Stretch 10 minutes"? |
| Body | Its history is deleted too. |
| Buttons | Cancel (secondary, left), Delete habit (danger, right), two equal columns 12 apart, 48 tall |

`role="alertdialog"`, labelled by the title and described by the body. Focus starts on Cancel (not drawn, see the interaction rules in `SELF-CRITIQUE.md`).

## Links
Cancel, Esc and the backdrop return to `today.html`. Delete habit has no golden after it (K1 with two rows).
