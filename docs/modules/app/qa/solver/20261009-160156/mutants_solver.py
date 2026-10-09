"""The solver's own mutants (code-review solver round, 2026-10-09). Same format as the reviewer's mutants.py.

Each patch is (file, old text, new text) and `old` must occur exactly once in the file it patches at the
commit the mutant is run against, or the runner stops. They are applied in memory by the serving process,
so no project file is written. Run them through run_mutants.py next to this file.
"""

APP = "src/app.js"
VIEW = "src/view.js"
STORAGE = "src/storage.js"

MUTANTS = [
    # ---- WR-02: the write counter must see a write that leaves the stored text byte for byte the same
    {
        "id": "A1b-cancel-rewrites-the-same-text",
        "what": "the keep path writes back the exact text already stored (only a setItem counter can see it)",
        "patches": [(APP, "  else view.focusDeleteButton(index);", '  else {\n    localStorage.setItem("streaks.state", localStorage.getItem("streaks.state"));\n    view.focusDeleteButton(index);\n  }')],
    },
    {
        "id": "A3b-rollover-rewrites-the-same-text",
        "what": "the rollover writes back the exact text already stored (only a setItem counter can see it)",
        "patches": [(APP, "  state.todayKey = today;\n  view.renderHeader(today);", '  state.todayKey = today;\n  localStorage.setItem("streaks.state", localStorage.getItem("streaks.state"));\n  view.renderHeader(today);')],
    },
]
