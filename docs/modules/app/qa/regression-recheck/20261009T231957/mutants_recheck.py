"""Four extra mutants for the regression re-check: each guard's window moved by one millisecond on its own.

The finder's G-450, G-600, G-499 and G-501 change DIALOG_GUARD_MS, which both guards share, so they cannot show which edge
test pins which guard. These change one guard's comparison only (the other keeps 500), to show that each edge test pins its own
guard and does not pass because of the other one:
  S-G1-499 / S-G1-501  "Delete habit" guard (dialogOpenedAt) with a 499 / 501 ms window; the page guard stays 500
  S-G2-499 / S-G2-501  page guard (dialogPressedAt) with a 499 / 501 ms window; the "Delete habit" guard stays 500
Same format as the finder's mutants_regression.py (id, what, patches = [(file, old text, new text)], the old text occurs
exactly once in the working tree). Applied in memory by the first review's mut.py; no project file is written.
"""

APP = "src/app.js"
G1_OLD = "withinGuard(event, dialogOpenedAt)"
G2_OLD = "if (!withinGuard(event, dialogPressedAt)) return;"


def g1(ms):
    return {"id": f"S-G1-{ms}", "what": f"'Delete habit' guard window {ms} ms, page guard unchanged",
            "patches": [(APP, G1_OLD, f"event.timeStamp - dialogOpenedAt < {ms}")]}


def g2(ms):
    return {"id": f"S-G2-{ms}", "what": f"page guard window {ms} ms, 'Delete habit' guard unchanged",
            "patches": [(APP, G2_OLD, f"if (!(event.timeStamp - dialogPressedAt < {ms})) return;")]}


MUTANTS = [g1(499), g1(501), g2(499), g2(501)]
