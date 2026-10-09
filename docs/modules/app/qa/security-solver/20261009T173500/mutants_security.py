"""Mutants for the security solver round (SEC-01 with its tap-through follow-up, and SEC-02). Format of the
code-review runner `mut.py`: id, what, and patches = [(file, old text, new text)], where the old text must occur
exactly once in the file as it stands (the working tree, after the fixes). The runner applies a patch in memory,
serves the patched copy and runs the browser suite against it. No project file is written.
"""

APP = "src/app.js"
VIEW = "src/view.js"

# \u{2068} and \u{2069} are written with chr() so that no tool turns the escape text into raw characters.
FSI_ESCAPE = chr(92) + "u{2068}"
PDI_ESCAPE = chr(92) + "u{2069}"
TITLE_LINE = '$("#del-title").textContent = `Delete "' + FSI_ESCAPE + "${habitName}" + PDI_ESCAPE + '"?`;'

PAGE_GUARD_LINE = '  page.addEventListener("click", swallowTapThrough, true);\n'
RECORD_PRESS = "if (event.detail > 0) dialogPressedAt = event.timeStamp;"

MUTANTS = [
    # ---- SEC-01 part 1: "Delete habit" ignores a click soon after the opening click
    {"id": "S1-window-0", "what": "window of 0 ms (no guard at all)",
     "patches": [(APP, "const DIALOG_GUARD_MS = 500;", "const DIALOG_GUARD_MS = 0;")]},
    {"id": "S1-window-50", "what": "window of 50 ms (too short)",
     "patches": [(APP, "const DIALOG_GUARD_MS = 500;", "const DIALOG_GUARD_MS = 50;")]},
    {"id": "S1-window-5000", "what": "window of 5 s (a deliberate click is held back too long)",
     "patches": [(APP, "const DIALOG_GUARD_MS = 500;", "const DIALOG_GUARD_MS = 5000;")]},
    {"id": "S1-no-prevent", "what": "the early click on Delete habit is seen but not cancelled",
     "patches": [(APP, "withinGuard(event, dialogOpenedAt)) event.preventDefault();", "withinGuard(event, dialogOpenedAt)) void 0;")]},
    {"id": "S1-first-opening-only", "what": "the window runs from the first opening only, never again",
     "patches": [(APP, "dialogOpenedAt = openingClick.timeStamp;", "if (dialogOpenedAt === -Infinity) dialogOpenedAt = openingClick.timeStamp;")]},
    {"id": "S1-inverted", "what": "both guards inverted: early clicks go through, late ones are held",
     "patches": [(APP, "event.timeStamp - since < DIALOG_GUARD_MS", "event.timeStamp - since > DIALOG_GUARD_MS")]},
    {"id": "S1-holds-cancel", "what": "every dialog button is held back, Cancel too",
     "patches": [(VIEW, 'node.closest(".dialog .btn-danger")', 'node.closest(".dialog button")')]},
    {"id": "S1-bubble-phase", "what": "the dialog listener is registered for the bubble phase (EXPECTED EQUIVALENT: a cancelled click cancels the submit in either phase)",
     "patches": [(APP, 'dialog.addEventListener("click", guardDialogClick, true);', 'dialog.addEventListener("click", guardDialogClick);')]},
    # ---- SEC-01 part 2: the page ignores the second click after a mouse or touch click in the dialog
    {"id": "T-no-page-guard", "what": "the page guard is not registered (the tap-through defect)",
     "patches": [(APP, PAGE_GUARD_LINE, "")]},
    {"id": "T-no-stop", "what": "the page guard cancels the click but does not stop it, so the delegated handlers still run",
     "patches": [(APP, "  event.stopPropagation();\n", "")]},
    {"id": "T-no-prevent", "what": "the page guard stops the click but does not cancel it, so the Add button still submits",
     "patches": [(APP, "  event.preventDefault();\n  event.stopPropagation();\n", "  event.stopPropagation();\n")]},
    {"id": "T-keyboard-too", "what": "a keyboard click in the dialog also starts the page's guard window",
     "patches": [(APP, RECORD_PRESS, "dialogPressedAt = event.timeStamp;")]},
    {"id": "T-document-scope", "what": "the page guard is registered on the document, so it also holds clicks inside the dialog",
     "patches": [(APP, PAGE_GUARD_LINE, '  document.addEventListener("click", swallowTapThrough, true);\n')]},
    {"id": "T-bubble-phase", "what": "the page guard is registered for the bubble phase, after the delegated handlers",
     "patches": [(APP, PAGE_GUARD_LINE, '  page.addEventListener("click", swallowTapThrough);\n')]},
    {"id": "T-delete-only", "what": "only a click on Delete habit starts the page's guard window (Cancel and the backdrop do not)",
     "patches": [(APP, RECORD_PRESS, "if (event.detail > 0 && view.confirmButtonOf(event.target)) dialogPressedAt = event.timeStamp;")]},
    {"id": "T-never-recorded", "what": "no press in the dialog is ever recorded",
     "patches": [(APP, RECORD_PRESS, "")]},
    # ---- SEC-02: the name is isolated in the dialog title
    {"id": "S2-no-isolate", "what": "no isolate marks around the name (the finding)",
     "patches": [(VIEW, TITLE_LINE, '$("#del-title").textContent = `Delete "${habitName}"?`;')]},
    {"id": "S2-fsi-only", "what": "an opening FSI and no closing PDI",
     "patches": [(VIEW, TITLE_LINE, '$("#del-title").textContent = `Delete "' + FSI_ESCAPE + '${habitName}"?`;')]},
    {"id": "S2-pdi-only", "what": "a closing PDI and no opening FSI",
     "patches": [(VIEW, TITLE_LINE, '$("#del-title").textContent = `Delete "${habitName}' + PDI_ESCAPE + '"?`;')]},
    {"id": "S2-marks-outside-quotes", "what": "the marks sit outside the quotes",
     "patches": [(VIEW, TITLE_LINE, '$("#del-title").textContent = `Delete ' + FSI_ESCAPE + '"${habitName}"' + PDI_ESCAPE + '?`;')]},
    {"id": "S2-lri", "what": "U+2066 LEFT-TO-RIGHT ISOLATE instead of FIRST STRONG ISOLATE",
     "patches": [(VIEW, TITLE_LINE, '$("#del-title").textContent = `Delete "' + chr(92) + 'u{2066}${habitName}' + PDI_ESCAPE + '"?`;')]},
]
