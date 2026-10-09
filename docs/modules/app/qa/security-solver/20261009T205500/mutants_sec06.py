"""Mutants for SEC-06 (the delete dialog title strips bidi format characters from its copy of the name).

Format of the code-review runner `mut.py`: id, what, and patches = [(file, old text, new text)], where the old text must
occur exactly once in the file as it stands (the working tree, with the fix). The runner applies a patch in memory,
serves the patched copy and runs the browser suite against it. No project file is written.

Every escape in the JavaScript is built from chr(92) (a backslash), so that no tool can turn escape text in this file
into a raw character.
"""

VIEW = "src/view.js"
BS = chr(92)


def one(code):
    return BS + "u{%04X}" % code


def span(low, high):
    return one(low) + "-" + one(high)


def regex(parts, flags="gu"):
    return "const TITLE_STRIPPED = /[" + "".join(parts) + "]/" + flags + ";"


EMBEDDINGS = span(0x202A, 0x202E)
ISOLATES = span(0x2066, 0x2069)
NEL = one(0x0085)
SEPARATORS = span(0x001C, 0x001E)
PARAGRAPH = one(0x2029)

ORIGINAL = regex([EMBEDDINGS, ISOLATES, NEL, SEPARATORS, PARAGRAPH])
USE = 'habitName.replace(TITLE_STRIPPED, "")'
FILL_NAME = 'row.querySelector(".habit-name").textContent = habit.name;'
FILL_LABEL = 'setAttribute("aria-label", `Delete ${habit.name}`);'


def mutant(identifier, what, parts=None, flags="gu"):
    return {"id": identifier, "what": what, "patches": [(VIEW, ORIGINAL, regex(parts, flags))]}


MUTANTS = [
    {"id": "S6-no-strip", "what": "the title uses the name as stored (the finding: the tree before the fix)",
     "patches": [(VIEW, USE, "habitName")]},
    mutant("S6-missing-2066-2069", "the strip lacks U+2066 to U+2069 (the ruling's example)",
           [EMBEDDINGS, NEL, SEPARATORS, PARAGRAPH]),
    mutant("S6-missing-202A-202E", "the strip lacks U+202A to U+202E", [ISOLATES, NEL, SEPARATORS, PARAGRAPH]),
    mutant("S6-missing-2066-only", "the strip lacks U+2066 only (LRI)", [EMBEDDINGS, span(0x2067, 0x2069), NEL, SEPARATORS, PARAGRAPH]),
    mutant("S6-missing-2068", "the strip lacks U+2068 only (FSI)", [EMBEDDINGS, span(0x2066, 0x2067), one(0x2069), NEL, SEPARATORS, PARAGRAPH]),
    mutant("S6-missing-2069", "the strip lacks U+2069 only (PDI)", [EMBEDDINGS, span(0x2066, 0x2068), NEL, SEPARATORS, PARAGRAPH]),
    mutant("S6-missing-202E", "the strip lacks U+202E only (RLO)", [span(0x202A, 0x202D), ISOLATES, NEL, SEPARATORS, PARAGRAPH]),
    mutant("S6-missing-0085", "the strip lacks U+0085", [EMBEDDINGS, ISOLATES, SEPARATORS, PARAGRAPH]),
    mutant("S6-missing-001C-001E", "the strip lacks U+001C to U+001E", [EMBEDDINGS, ISOLATES, NEL, PARAGRAPH]),
    mutant("S6-short-001E", "the strip stops at U+001D (U+001E left in)", [EMBEDDINGS, ISOLATES, NEL, span(0x001C, 0x001D), PARAGRAPH]),
    mutant("S6-missing-2029", "the strip lacks U+2029", [EMBEDDINGS, ISOLATES, NEL, SEPARATORS]),
    mutant("S6-wide-low-2065", "the second range starts at U+2065", [EMBEDDINGS, span(0x2065, 0x2069), NEL, SEPARATORS, PARAGRAPH]),
    mutant("S6-wide-high-206A", "the second range ends at U+206A", [EMBEDDINGS, span(0x2066, 0x206A), NEL, SEPARATORS, PARAGRAPH]),
    mutant("S6-wide-high-202F", "the first range ends at U+202F", [span(0x202A, 0x202F), ISOLATES, NEL, SEPARATORS, PARAGRAPH]),
    mutant("S6-wide-low-2028", "the first range starts at U+2028", [span(0x2028, 0x202E), ISOLATES, NEL, SEPARATORS, PARAGRAPH]),
    mutant("S6-wide-marks", "U+200E, U+200F and U+061C (LRM, RLM, ALM) are stripped too",
           [EMBEDDINGS, ISOLATES, NEL, SEPARATORS, PARAGRAPH, span(0x200E, 0x200F), one(0x061C)]),
    mutant("S6-wide-0084-0086", "the NEL entry becomes U+0084 to U+0086", [EMBEDDINGS, ISOLATES, span(0x0084, 0x0086), SEPARATORS, PARAGRAPH]),
    mutant("S6-no-g-flag", "no g flag: only the first match is removed", [EMBEDDINGS, ISOLATES, NEL, SEPARATORS, PARAGRAPH], "u"),
    {"id": "S6-replace-with-space", "what": "a space replaces each stripped character",
     "patches": [(VIEW, USE, 'habitName.replace(TITLE_STRIPPED, " ")')]},
    {"id": "S6-list-too", "what": "the list row's name is stripped too (the stored-as-typed rule)",
     "patches": [(VIEW, FILL_NAME, 'row.querySelector(".habit-name").textContent = habit.name.replace(TITLE_STRIPPED, "");')]},
    {"id": "S6-label-too", "what": "the trash button's aria-label is stripped too",
     "patches": [(VIEW, FILL_LABEL, 'setAttribute("aria-label", `Delete ${habit.name.replace(TITLE_STRIPPED, "")}`);')]},
    {"id": "S6-no-isolate-marks", "what": "the strip stays, the FSI and PDI around the name go (the SEC-02 control removed)",
     "patches": [(VIEW, "`Delete \"" + one(0x2068) + "${" + USE + "}" + one(0x2069) + "\"?`", "`Delete \"${" + USE + "}\"?`")]},
]
