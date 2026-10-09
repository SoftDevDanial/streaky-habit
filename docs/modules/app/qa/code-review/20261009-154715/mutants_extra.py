"""Second set of mutants (QA N4 re-check and three more seams). Same format as mutants.py.

Run with the same runner by pointing it at this list, for example
python -c "import sys; sp=...; import mutants, mutants_extra; mutants.MUTANTS[:] = mutants_extra.MUTANTS; ..."
(see evidence.md). The runner reads `from mutants import MUTANTS`.
"""

APP = "src/app.js"
VIEW = "src/view.js"

MUTANTS = [
    {
        "id": "E1-returnvalue-not-reset",
        "what": "N4 (QA M11): the dialog's returnValue is not reset before showModal",
        "patches": [(VIEW, '  dialog.returnValue = "";\n', "")],
    },
    {
        "id": "E2-no-focus-return-after-keep",
        "what": "N4 (QA M02): no explicit focus return to the trash button after Cancel / Esc / backdrop",
        "patches": [(APP, "  else view.focusDeleteButton(index);", "  else {\n    // focus left to the browser\n  }")],
    },
    {
        "id": "E3-visibility-check-dropped",
        "what": "visibilitychange runs the day check whatever the visibility state",
        "patches": [(APP, '    if (document.visibilityState === "visible") checkDay();', "    checkDay();")],
    },
    {
        "id": "E4-prevent-default-dropped",
        "what": "the add form's submit is not preventDefault()ed (CSP form-action 'none' is the only guard)",
        "patches": [(APP, "function submitName(event) {\n  event.preventDefault();\n", "function submitName(event) {\n")],
    },
    {
        "id": "E5-rollover-rebuilds-rows",
        "what": "checkDay rebuilds every row (renderHabits) instead of updating in place (R19 focus, JC1)",
        "patches": [(APP, "  view.syncHabits(state.habits, today);\n  view.renderHeatmap(state.habits, today);", "  renderHabits();")],
    },
    {
        "id": "E6-heat-cells-rebuilt",
        "what": "renderHeatmap replaces all 84 cells on every render instead of setting them in place (R8 'in place', JC2)",
        "patches": [(VIEW, "  while (grid.children.length < cells.length) grid.append(element(\"span\"));", "  grid.replaceChildren();\n  while (grid.children.length < cells.length) grid.append(element(\"span\"));")],
    },
]
