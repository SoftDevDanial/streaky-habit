"""Mutation spot-check of the browser tests: can each test fail?

Copies the project (never touching the original) into a scratch folder, applies ONE small bug at a time to the
copy, serves the copy from an in-process http.server thread on a free loopback port, runs the whole pytest suite
against it and records which tests fail. A mutation that no test notices means a gap in the tests.

Usage: python mutate.py <scratch_dir> <results_json>
"""
import functools
import http.server
import json
import os
import pathlib
import shutil
import subprocess
import sys
import threading

SCRATCH = pathlib.Path(sys.argv[1])
RESULTS = pathlib.Path(sys.argv[2])
ROOT = pathlib.Path(__file__).resolve().parents[6]  # .../streaks

MUTATIONS = [
    ("M01", "src/app.js", 'if (pressedOutside && releasedOutside) dialog.close("cancel");', 'if (false) dialog.close("cancel");', "backdrop click no longer closes"),
    ("M02", "src/app.js", "  else view.focusDeleteButton(index);", "  else {}", "no focus return to trash after keep"),
    ("M03", "src/app.js", "  view.syncHabits(state.habits, today);\n  view.renderHeatmap(state.habits, today);", "  view.syncHabits(state.habits, today);", "rollover leaves the heatmap alone"),
    ("M04", "src/storage.js", "  saveHabits([]);\n  return { habits: [], reset: true };", "  return { habits: [], reset: true };", "unreadable data is not reset in storage"),
    ("M05", "src/app.js", "if (index < state.habits.length) view.focusDeleteButton(index);", "if (false) view.focusDeleteButton(index);", "delete always focuses the input"),
    ("M06", "src/view.js", '  $("#new-habit").setAttribute("aria-invalid", "true");\n', "", "no aria-invalid on error"),
    ("M07", "src/app.js", "  saveHabits(state.habits);\n  view.syncHabit(index", "  view.syncHabit(index", "tick is not saved"),
    ("M08", "src/view.js", '  if (cell.today) node.setAttribute("aria-current", "date");', '  if (false) node.setAttribute("aria-current", "date");', "today cell loses aria-current"),
    ("M09", "src/app.js", 'if (document.visibilityState === "visible") checkDay();', "if (false) checkDay();", "visibilitychange does not roll over"),
    ("M10", "src/storage.js", "return { name: entry.name, done: [...new Set(entry.done)].sort() };", "return { name: entry.name, done: [...entry.done] };", "saved days not sorted or de-duplicated"),
    ("M11", "src/view.js", '  dialog.returnValue = "";\n', "", "dialog returnValue not reset"),
    ("M12", "index.html", "connect-src 'none'; ", "", "CSP loses connect-src"),
    ("M13", "src/app.js", "  view.showNameError(error);\n  view.focusNameField();", "  view.showNameError(error);", "no focus to the input after a rejected name"),
    ("M14", "src/app.js", "  view.renderHeatmap(state.habits, state.todayKey);\n  view.setAddLimit", "  view.setAddLimit", "add/delete do not recount the heatmap"),
    ("M15", "src/view.js", '  $(".add .btn").disabled = full;\n', "", "Add button not disabled at 12"),
    ("M16", "src/app.js", "  view.syncHabit(index, state.habits[index], state.todayKey);\n  view.renderHeatmap(state.habits, state.todayKey);", "  view.syncHabit(index, state.habits[index], state.todayKey);", "tick does not update the heat cell"),
    ("M17", "src/app.js", "if (pressedOutside && releasedOutside)", "if (releasedOutside)", "drag from inside to the backdrop closes the dialog"),
    ("M18", "src/view.js", "button.setAttribute(\"aria-label\", `Mark ${shortDate(key)} as done`);", "button.setAttribute(\"aria-label\", isDone ? `Unmark ${shortDate(key)}` : `Mark ${shortDate(key)} as done`);", "day button name changes with state"),
    ("M19", "src/view.js", '$(".col-main").prepend(note);', '$(".col-main").append(note);', "note is not the first child"),
    ("M20", "src/app.js", "  setInterval(checkDay, ROLLOVER_CHECK_MS);\n", "", "no 30 s rollover check"),
    ("M21", "src/storage.js", "  } catch {\n    return { habits: [], reset: false };\n  }", "  } catch {\n    throw new Error('x');\n  }", "storage read failure is not caught"),
    ("M22", "src/app.js", "  if (today === state.todayKey) return;\n", "  if (today === state.todayKey) return;\n  saveHabits(state.habits);\n", "rollover writes storage"),
    ("M23", "src/view.js", '    section.append(emptyMessage());\n    return;', '    section.append(emptyMessage());\n    section.append(element("ul", "habits"));\n    return;', "empty list also renders an empty ul.habits"),
    ("M24", "src/view.js", '  node.className = `hc l${cell.level}${cell.today ? " today" : ""}`;', '  node.className = `hc l${Math.min(cell.level, 3)}${cell.today ? " today" : ""}`;', "heat level 4 capped at 3"),
]


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def copy_project():
    if SCRATCH.exists():
        shutil.rmtree(SCRATCH)
    shutil.copytree(ROOT, SCRATCH, ignore=shutil.ignore_patterns(".git", "qa", "findings", "__pycache__", ".pytest_cache", "node_modules", "_scratch"))


def run_suite(port):
    env = dict(os.environ, STREAKS_BASE_URL=f"http://127.0.0.1:{port}/", PYTHONDONTWRITEBYTECODE="1")
    env.pop("STREAKS_EVIDENCE_DIR", None)
    env.pop("STREAKS_SUBPATH_URL", None)
    proc = subprocess.run([sys.executable, "-m", "pytest", "tests/browser", "-q", "--tb=no", "-rf", "-p", "no:cacheprovider"],
                          cwd=SCRATCH, env=env, capture_output=True, text=True, timeout=240)
    failed = [line.split(" ", 1)[1].split(" - ")[0] for line in proc.stdout.splitlines() if line.startswith("FAILED ")]
    summary = [line for line in proc.stdout.splitlines() if " passed" in line or " failed" in line][-1:]
    return failed, summary


def main():
    copy_project()
    handler = functools.partial(Quiet, directory=str(SCRATCH))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    out = []
    try:
        baseline, summary = run_suite(port)
        out.append({"id": "M00", "what": "unmutated copy (baseline)", "failed": baseline, "summary": summary})
        print("M00 baseline", summary, flush=True)
        for mid, rel, old, new, what in MUTATIONS:
            target = SCRATCH / rel
            original = target.read_text(encoding="utf-8")
            if original.count(old) != 1:
                out.append({"id": mid, "what": what, "failed": None, "summary": [f"SKIPPED: pattern found {original.count(old)} times"]})
                print(mid, "SKIPPED pattern count", original.count(old), flush=True)
                continue
            target.write_text(original.replace(old, new), encoding="utf-8")
            try:
                failed, summary = run_suite(port)
            finally:
                target.write_text(original, encoding="utf-8")
            out.append({"id": mid, "what": what, "failed": failed, "summary": summary})
            print(mid, what, "->", len(failed), "failing:", [f.split("::")[-1][:60] for f in failed][:4], flush=True)
    finally:
        server.shutdown()
        server.server_close()
        RESULTS.write_text(json.dumps(out, indent=1), encoding="utf-8")
        shutil.rmtree(SCRATCH, ignore_errors=True)


if __name__ == "__main__":
    main()
