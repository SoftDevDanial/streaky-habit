"""Two extra mutants for the regression solver round (app, RG-CR-01): the window one millisecond either side of 500.

Same format as the finder's mutants_regression.py (id, what, patches = [(file, old text, new text)], the old text must
occur exactly once in the working tree). The finder's G-450, G-600 and G-le are off by 50 ms or by the comparison; these
two show that the edge tests also reject the closest constants, which is what the comment on GUARD_WINDOW_MS in
tests/browser/conftest.py claims ("fail for any other DIALOG_GUARD_MS").
"""

APP = "src/app.js"
GUARD_CONST = "const DIALOG_GUARD_MS = 500;"

MUTANTS = [
    {"id": "G-499", "what": "DIALOG_GUARD_MS 500 -> 499", "patches": [(APP, GUARD_CONST, "const DIALOG_GUARD_MS = 499;")]},
    {"id": "G-501", "what": "DIALOG_GUARD_MS 500 -> 501", "patches": [(APP, GUARD_CONST, "const DIALOG_GUARD_MS = 501;")]},
]
