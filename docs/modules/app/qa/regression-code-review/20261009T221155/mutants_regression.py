"""Mutants for the regression code review of the app delta fa58481..9ebc54e (SEC-01 guards, SEC-02 isolate, SEC-06 strip).

Format of the earlier code-review runner `mut.py`: id, what, and patches = [(file, old text, new text)], where the old
text must occur exactly once in the file as it stands (the working tree). The runner applies a patch in memory, serves the
patched copy on a free 127.0.0.1 port and runs the browser suite against it. No project file is written.

Escapes inside the JavaScript are built from chr(92) so that no tool can turn escape text in this file into a raw character.
"""

APP = "src/app.js"
VIEW = "src/view.js"
BS = chr(92)


def one(code):
    return BS + "u{%04X}" % code


GUARD_CONST = "const DIALOG_GUARD_MS = 500;"
WITHIN = "const withinGuard = (event, since) => event.timeStamp - since < DIALOG_GUARD_MS;"
CONFIRM_GUARD = "if (view.confirmButtonOf(event.target) && withinGuard(event, dialogOpenedAt)) event.preventDefault();"
SWALLOW_CHECK = "if (!withinGuard(event, dialogPressedAt)) return;"
DIALOG_CAPTURE = 'dialog.addEventListener("click", guardDialogClick, true);'
PAGE_CAPTURE = 'page.addEventListener("click", swallowTapThrough, true);'
SWALLOW_BODY = "  event.preventDefault();\n  event.stopPropagation();\n}"
OPENED_STAMP = "dialogOpenedAt = openingClick.timeStamp;"
PRESSED_STAMP = "if (event.detail > 0) dialogPressedAt = event.timeStamp;"
TITLE_LINE = 'habitName.replace(TITLE_STRIPPED, "")'
TITLE_TEXT = "`Delete \"" + one(0x2068) + "${habitName.replace(TITLE_STRIPPED, \"\")}" + one(0x2069) + "\"?`"
CLOSING_MARK = "}" + one(0x2069) + "\"?`"

MUTANTS = [
    # --- the window length and its edge
    {"id": "G-450", "what": "DIALOG_GUARD_MS 500 -> 450", "patches": [(APP, GUARD_CONST, "const DIALOG_GUARD_MS = 450;")]},
    {"id": "G-600", "what": "DIALOG_GUARD_MS 500 -> 600", "patches": [(APP, GUARD_CONST, "const DIALOG_GUARD_MS = 600;")]},
    {"id": "G-700", "what": "DIALOG_GUARD_MS 500 -> 700", "patches": [(APP, GUARD_CONST, "const DIALOG_GUARD_MS = 700;")]},
    {"id": "G-300", "what": "DIALOG_GUARD_MS 500 -> 300", "patches": [(APP, GUARD_CONST, "const DIALOG_GUARD_MS = 300;")]},
    {"id": "G-le", "what": "withinGuard uses <= instead of <", "patches": [(APP, WITHIN, WITHIN.replace(" < ", " <= "))]},
    # --- Delete habit guard
    {"id": "G-kbd-delete-open", "what": "Delete habit is held only for a mouse or touch click (detail > 0), a keyboard activation inside the window deletes",
     "patches": [(APP, CONFIRM_GUARD, CONFIRM_GUARD.replace("if (view", "if (event.detail > 0 && view"))]},
    {"id": "G-no-open-stamp", "what": "the opening click's time is never recorded", "patches": [(APP, OPENED_STAMP, "")]},
    {"id": "G-open-stamp-once", "what": "the window runs only from the first opening",
     "patches": [(APP, OPENED_STAMP, "if (dialogOpenedAt === -Infinity) dialogOpenedAt = openingClick.timeStamp;")]},
    {"id": "G-bubble", "what": "guardDialogClick registered for the bubble phase", "patches": [(APP, DIALOG_CAPTURE, 'dialog.addEventListener("click", guardDialogClick);')]},
    # --- page guard
    {"id": "P-kbd-click-passes", "what": "the page swallows only mouse or touch clicks (detail > 0), a keyboard click inside the window passes",
     "patches": [(APP, SWALLOW_CHECK, "if (event.detail === 0 || !withinGuard(event, dialogPressedAt)) return;")]},
    {"id": "P-no-stop", "what": "swallowTapThrough does not stopPropagation", "patches": [(APP, SWALLOW_BODY, "  event.preventDefault();\n}")]},
    {"id": "P-no-prevent", "what": "swallowTapThrough does not preventDefault", "patches": [(APP, SWALLOW_BODY, "  event.stopPropagation();\n}")]},
    {"id": "P-bubble", "what": "page listener registered for the bubble phase", "patches": [(APP, PAGE_CAPTURE, 'page.addEventListener("click", swallowTapThrough);')]},
    {"id": "P-on-document", "what": "swallowTapThrough sits on the document, so it holds the dialog's own clicks too",
     "patches": [(APP, PAGE_CAPTURE, 'document.addEventListener("click", swallowTapThrough, true);')]},
    {"id": "P-stamp-always", "what": "every click in the dialog starts the page window, keyboard ones too", "patches": [(APP, PRESSED_STAMP, "dialogPressedAt = event.timeStamp;")]},
    {"id": "P-stamp-never-on-delete", "what": "a click on Delete habit does not start the page window",
     "patches": [(APP, PRESSED_STAMP, "if (event.detail > 0 && !view.confirmButtonOf(event.target)) dialogPressedAt = event.timeStamp;")]},
    {"id": "P-stamp-only-backdrop", "what": "only a click on the dialog element itself (padding or backdrop) starts the page window",
     "patches": [(APP, PRESSED_STAMP, "if (event.detail > 0 && event.target === event.currentTarget) dialogPressedAt = event.timeStamp;")]},
    # --- title
    {"id": "T-strip-whole", "what": "the strip runs over the finished title, so it also removes the isolate marks",
     "patches": [(VIEW, TITLE_TEXT, "(" + TITLE_TEXT + ").replace(TITLE_STRIPPED, \"\")")]},
    {"id": "T-open-lri", "what": "the opening mark is LEFT-TO-RIGHT ISOLATE instead of FIRST STRONG ISOLATE",
     "patches": [(VIEW, one(0x2068) + "${habitName", one(0x2066) + "${habitName")]},
    {"id": "T-close-missing", "what": "no closing mark", "patches": [(VIEW, CLOSING_MARK, "}\"?`")]},
    {"id": "T-name-lowercased", "what": "the title's name is lowercased", "patches": [(VIEW, TITLE_LINE, 'habitName.toLowerCase().replace(TITLE_STRIPPED, "")')]},
]
