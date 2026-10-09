"""Follow-up to probe_01: put a double click or double tap on Cancel and on Delete habit at a point where a page
control (a day bead or a trash button) lies under the button, and see whether the second press reaches that control.

Twelve plain habits, so day beads and trash buttons lie behind the dialog. The dialog is opened from habit k
(1, 6, 12). For each button the first point (a 2 px grid over the overlap of the button and a control) that really
hits the button while the dialog is open is pressed twice. 'Delete habit' is pressed well past the opening window.
Real input, real browser time (the clock is only pinned to 2026-10-08 12:00 +08:00).

Each line says whether the FIRST press did its job (Cancel: the dialog closed; Delete habit: the row went) and what
the SECOND press changed: a tick (stored data differs from what the first press alone leaves) or a dialog opened again.

With --no-page-guard the served src/app.js has the page guard line removed in memory (page.route), which is the
state before the tap-through fix; src/ is not touched.
Run: PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python -B <this file> [--no-page-guard]   (cwd = project root). Writes nothing.
"""
import json
import pathlib
import sys

sys.path.insert(0, "{workspace}/examples/streaks/docs/modules/app/qa/security/20261009T165000")
from lib import Run, open_app, state_text, stored, row_names, ROOT  # noqa: E402

PLAIN12 = state_text([{"name": f"Habit {n}", "done": []} for n in range(1, 13)])
VIEWPORTS = [(390, 844), (412, 915), (1440, 900), (360, 640), (375, 667)]
PAGE_GUARD_LINE = '  page.addEventListener("click", swallowTapThrough, true);\n'

# A point inside the button and a page control at once that hits the button while the dialog is open.
FIND_POINT = """([selector]) => {
  const target = document.querySelector(selector);
  const t = target.getBoundingClientRect();
  const controls = Array.from(document.querySelectorAll('li.habit button.day, li.habit .icon-btn'));
  for (const c of controls) {
    const r = c.getBoundingClientRect();
    const left = Math.max(t.left, r.left), right = Math.min(t.right, r.right);
    const top = Math.max(t.top, r.top), bottom = Math.min(t.bottom, r.bottom);
    if (right - left < 4 || bottom - top < 4) continue;
    for (let y = top + 1; y < bottom; y += 2) {
      for (let x = left + 1; x < right; x += 2) {
        if (document.elementFromPoint(x, y)?.closest('button') === target) {
          const kind = c.classList.contains('day') ? 'day bead ' + c.getAttribute('data-date') : 'trash';
          return [x, y, kind + ' of ' + c.closest('li').querySelector('h3').textContent];
        }
      }
    }
  }
  return null;
}"""

UNDER = """([x, y]) => {
  const el = document.elementFromPoint(x, y);
  const b = el && el.closest('button');
  if (b && b.classList.contains('day')) return 'day bead ' + b.getAttribute('data-date') + ' of ' + b.closest('li').querySelector('h3').textContent;
  if (b) return 'button ' + (b.getAttribute('aria-label') || b.textContent.trim());
  return el ? el.tagName.toLowerCase() : 'nothing';
}"""


def run_case(run, vp, touch, k, target, patched_app):
    kw = {"has_touch": True} if touch else {}
    ctx, page, log = open_app(run.browser, run.base, storage=PLAIN12, viewport=vp, **kw)
    try:
        if patched_app is not None:
            page.route("**/src/app.js", lambda route, request: route.fulfill(status=200, content_type="text/javascript", body=patched_app))
            page.reload()
            page.wait_for_selector("li.habit")
        before, rows_before = stored(page), row_names(page)
        page.get_by_role("button", name=f"Delete Habit {k}", exact=True).click()
        page.locator("dialog").evaluate("(d) => Promise.all(d.getAnimations().map((a) => a.finished))")
        page.wait_for_timeout(700)
        selector = "dialog .btn-secondary" if target == "cancel" else "dialog .btn-danger"
        found = page.evaluate(FIND_POINT, [selector])
        if found is None:
            return "no point where a page control lies under the button and the press still hits the button"
        x, y, kind = found
        if touch:
            page.touchscreen.tap(x, y)
            page.touchscreen.tap(x, y)
        else:
            page.mouse.dblclick(x, y)
        page.wait_for_timeout(500)
        after, rows_after = stored(page), row_names(page)
        habits_before = json.loads(before)["habits"]
        expected = habits_before[:k - 1] + habits_before[k:] if target == "delete" else habits_before
        first_press = (len(rows_after) == len(rows_before) - 1) if target == "delete" else True
        notes = []
        if not first_press:
            notes.append("FIRST PRESS DID NOT DELETE")
        names_after = [h["name"] for h in json.loads(after)["habits"]]
        if names_after not in ([h["name"] for h in expected], [h["name"] for h in habits_before]):
            notes.append("A HABIT THAT WAS NOT ASKED ABOUT WAS DELETED")
        if json.loads(after)["habits"] != expected:
            notes.append("SECOND PRESS CHANGED STORED DATA")
        if page.evaluate("() => document.querySelector('dialog').open"):
            notes.append("a dialog is OPEN after the gesture (the second press opened one)")
        return f"point ({x:.0f},{y:.0f}) over {kind}; now over {page.evaluate(UNDER, [x, y])}; " + ("; ".join(notes) or "first press did its job, second press changed nothing")
    finally:
        ctx.close()


def main():
    patched_app = None
    if "--no-page-guard" in sys.argv:
        text = (pathlib.Path(ROOT) / "src" / "app.js").read_text(encoding="utf-8")
        assert text.count(PAGE_GUARD_LINE) == 1
        patched_app = text.replace(PAGE_GUARD_LINE, "")
        print("(page guard removed in memory)")
    with Run() as run:
        for vp in VIEWPORTS:
            for touch in (False, True):
                for target in ("cancel", "delete"):
                    for k in (1, 6, 12):
                        result = run_case(run, vp, touch, k, target, patched_app)
                        print(f"  {vp[0]}x{vp[1]} {'touch' if touch else 'mouse'} {target:6s} from habit {k:2d} -> {result}", flush=True)
    print("done")


if __name__ == "__main__":
    main()
