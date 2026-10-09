"""Mutant definitions for the app code review. Each patch is (file under the work copy, old text, new text).

Every `old` must occur exactly once in the pristine file, or the runner stops (a patch that did not apply
would be a fake survivor). Patches are applied in memory by the serving process; no file is changed.
"""

APP = "src/app.js"
VIEW = "src/view.js"
STORAGE = "src/storage.js"
INDEX = "index.html"

MUTANTS = [
    # ---- controls: these must be KILLED, or the runner cannot be trusted
    {
        "id": "C1-interval-300s",
        "what": "control: rollover interval 300000 ms (the builder's own negative control)",
        "patches": [(APP, "const ROLLOVER_CHECK_MS = 30000;", "const ROLLOVER_CHECK_MS = 300000;")],
    },
    {
        "id": "C2-hook-on-window",
        "what": "control: a test hook on window (R26)",
        "patches": [(APP, "\nboot();\n", "\nwindow.__hook = boot;\nboot();\n")],
    },
    {
        "id": "C3-strip-aria-current-stale",
        "what": "control: syncDay never removes aria-current from the old today button (R19)",
        "patches": [(VIEW, '  else button.removeAttribute("aria-current");\n  setText(button.querySelector(".wd"), weekday);', '  setText(button.querySelector(".wd"), weekday);')],
    },
    # ---- QA N2: "stored equals S" cannot tell "no write" from "same write"
    {
        "id": "A1-cancel-resaves",
        "what": "N2: Cancel / Esc / backdrop (the keep path) saves the unchanged habits (R14 says saves nothing)",
        "patches": [(APP, "  else view.focusDeleteButton(index);", "  else {\n    saveHabits(state.habits);\n    view.focusDeleteButton(index);\n  }")],
    },
    {
        "id": "A2-reject-resaves",
        "what": "N2: a rejected name saves the unchanged habits (R11 says no write)",
        "patches": [(APP, "  if (!result.ok) {\n    rejectName(result.error);", "  if (!result.ok) {\n    saveHabits(state.habits);\n    rejectName(result.error);")],
    },
    {
        "id": "A3-rollover-saves",
        "what": "N2 (QA M22): the rollover saves (R16: at no other time)",
        "patches": [(APP, "  state.todayKey = today;\n  view.renderHeader(today);", "  state.todayKey = today;\n  saveHabits(state.habits);\n  view.renderHeader(today);")],
    },
    {
        "id": "A4-dismiss-saves",
        "what": "N2: Dismiss saves (R17: changes nothing else)",
        "patches": [(APP, "  view.removeNote();\n  view.focusNameField();\n}", "  saveHabits(state.habits);\n  view.removeNote();\n  view.focusNameField();\n}")],
    },
    # ---- QA N3: load-time sort and de-duplication
    {
        "id": "S1-no-sort-no-dedupe",
        "what": "N3 (QA M10): decode keeps done as stored (neither sorted nor de-duplicated)",
        "patches": [(STORAGE, "  return { name: entry.name, done: [...new Set(entry.done)].sort() };", "  return { name: entry.name, done: entry.done };")],
    },
    {
        "id": "S2-dedupe-only",
        "what": "N3: decode de-duplicates but does not sort",
        "patches": [(STORAGE, "  return { name: entry.name, done: [...new Set(entry.done)].sort() };", "  return { name: entry.name, done: [...new Set(entry.done)] };")],
    },
    {
        "id": "S3-sort-only",
        "what": "N3: decode sorts but does not de-duplicate",
        "patches": [(STORAGE, "  return { name: entry.name, done: [...new Set(entry.done)].sort() };", "  return { name: entry.name, done: [...entry.done].sort() };")],
    },
    {
        "id": "S4-parsed-object-reused",
        "what": "T2: decode returns the parsed object itself (spec: never the parsed objects)",
        "patches": [(STORAGE, "  return { name: entry.name, done: [...new Set(entry.done)].sort() };", "  entry.done = [...new Set(entry.done)].sort();\n  return entry;")],
    },
    {
        "id": "S5-first-date-only",
        "what": "strict decoder: only the first saved date is validated",
        "patches": [(STORAGE, "  if (!entry.done.every((value) => isDateKey(value))) return null;", "  if (entry.done.length > 0 && !isDateKey(entry.done[0])) return null;")],
    },
    {
        "id": "S6-duplicate-vs-previous-only",
        "what": "strict decoder: a duplicate name is only caught against the previous entry",
        "patches": [(STORAGE, "    const habit = readHabit(entry, habits.map((existing) => existing.name));", "    const habit = readHabit(entry, habits.slice(-1).map((existing) => existing.name));")],
    },
    # ---- focus and dialog close path
    {
        "id": "A5-add-moves-focus",
        "what": "N5: a successful add moves focus to the input (R10: the app does not move focus)",
        "patches": [(APP, "  view.clearNameField();\n  renderHabits();\n}", "  view.clearNameField();\n  renderHabits();\n  view.focusNameField();\n}")],
    },
    {
        "id": "A7-backdrop-press-only",
        "what": "dialog: close when the press began on the backdrop, whatever the release point",
        "patches": [(APP, '  if (pressedOutside && releasedOutside) dialog.close("cancel");', '  if (pressedOutside) dialog.close("cancel");')],
    },
    {
        "id": "A8-backdrop-release-only",
        "what": "control: close on the release point alone (a drag out of the box would close it)",
        "patches": [(APP, '  if (pressedOutside && releasedOutside) dialog.close("cancel");', '  if (releasedOutside) dialog.close("cancel");')],
    },
    # ---- rollover cadence
    {
        "id": "A6-interval-60s",
        "what": "rollover cadence 60 s (spec: every 30 seconds)",
        "patches": [(APP, "const ROLLOVER_CHECK_MS = 30000;", "const ROLLOVER_CHECK_MS = 60000;")],
    },
    {
        "id": "A6-interval-85s",
        "what": "rollover cadence 85 s (breaks the 60 second promise)",
        "patches": [(APP, "const ROLLOVER_CHECK_MS = 30000;", "const ROLLOVER_CHECK_MS = 85000;")],
    },
    # ---- in-place recycling of heat cells (JC2) and streak lines
    {
        "id": "V3-future-cell-keeps-role-label-current",
        "what": "fillCell: a cell that becomes future keeps role, aria-label and aria-current",
        "patches": [(VIEW, '    for (const name of ["role", "aria-label", "aria-current"]) node.removeAttribute(name);\n', "")],
    },
    {
        "id": "V4-new-today-cell-keeps-aria-hidden",
        "what": "fillCell: a cell that stops being future keeps aria-hidden=true",
        "patches": [(VIEW, '  node.removeAttribute("aria-hidden");\n  node.setAttribute("role", "img");', '  node.setAttribute("role", "img");')],
    },
    {
        "id": "V5-old-today-cell-keeps-aria-current",
        "what": "fillCell: the cell that was today keeps aria-current after the rollover",
        "patches": [(VIEW, '  if (cell.today) node.setAttribute("aria-current", "date");\n  else node.removeAttribute("aria-current");', '  if (cell.today) node.setAttribute("aria-current", "date");')],
    },
    {
        "id": "V2-stale-best",
        "what": "syncStreak: span.best is not removed when best drops to 0 (R6: no span.best at all)",
        "patches": [(VIEW, "    bestNode?.remove();\n    return;", "    return;")],
    },
    {
        "id": "V6-settext-always-writes",
        "what": "BUILD JC3: setText writes even an unchanged text (live regions re-announce)",
        "patches": [(VIEW, "  if (node.textContent !== text) node.textContent = text;", "  node.textContent = text;")],
    },
    {
        "id": "V7-error-cleared-by-render",
        "what": "setAddLimit: any render below 12 clears the message, also an error",
        "patches": [(VIEW, '  } else if (message.classList.contains("field-note")) {', "  } else {")],
    },
    # ---- svg namespace, markup outside .page
    {
        "id": "V1-svg-html-namespace",
        "what": "icon(): svg and use made with createElement (spec: an HTML svg does not render)",
        "patches": [
            (VIEW, '  const svg = document.createElementNS(SVG_NAMESPACE, "svg");', '  const svg = document.createElement("svg");'),
            (VIEW, '  const use = document.createElementNS(SVG_NAMESPACE, "use");', '  const use = document.createElement("use");'),
        ],
    },
    {
        "id": "H4-dialog-title-class",
        "what": "index.html: h2.dialog-title loses its class",
        "patches": [(INDEX, '<h2 class="dialog-title" id="del-title"></h2>', '<h2 id="del-title"></h2>')],
    },
    {
        "id": "H5-sprite-in-flow",
        "what": "index.html: the sprite loses position:absolute (a 0 x 0 inline svg opens a line box)",
        "patches": [(INDEX, '<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">', '<svg width="0" height="0" aria-hidden="true" focusable="false">')],
    },
    {
        "id": "H8-delete-button-class",
        "what": "index.html: Delete habit button is btn-primary instead of btn-danger",
        "patches": [(INDEX, 'class="btn btn-danger" type="submit" value="delete"', 'class="btn btn-primary" type="submit" value="delete"')],
    },
]
