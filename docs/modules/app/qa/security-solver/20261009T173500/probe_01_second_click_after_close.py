"""Does the second click of a double click or double tap on Cancel, on Delete habit or on the backdrop reach the page?

The first press closes the dialog; the second lands on whatever sits under that point. A tick on a day bead changes
saved data. Real input only (mouse.dblclick, two touchscreen taps), real browser time (the clock is only pinned to
2026-10-08 12:00 +08:00). 'Delete habit' is pressed 600 ms after the dialog opened, past the SEC-01 window.
Two page states: the three-habit sample, and twelve plain habits (rows behind the dialog everywhere).

Prints one line per case: the point, what sat under it once the dialog was closed, and what changed.
With --no-page-guard the served src/app.js has the page guard line removed in memory (page.route), which is the state
before the tap-through fix; src/ is not touched.
Run: PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python -B <this file> [--no-page-guard]   (cwd = project root). Writes nothing.
"""
import json
import pathlib
import sys

sys.path.insert(0, "{workspace}/examples/streaks/docs/modules/app/qa/security/20261009T165000")
from lib import Run, open_app, state_text, stored, row_names, SAMPLE_HABITS, ROOT  # noqa: E402

SAMPLE = state_text(SAMPLE_HABITS)
PAGE_GUARD_LINE = '  page.addEventListener("click", swallowTapThrough, true);\n'
PLAIN12 = state_text([{"name": f"Habit {n}", "done": []} for n in range(1, 13)])
VIEWPORTS = [(390, 844), (412, 915), (1440, 900), (360, 640), (375, 667)]  # the first three were asked for, the last two are small phones

DESCRIBE = """([x, y]) => {
  const el = document.elementFromPoint(x, y);
  if (!el) return 'nothing';
  const b = el.closest('button');
  if (b && b.classList.contains('day')) return 'day bead ' + b.getAttribute('data-date') + ' of ' + b.closest('li').querySelector('h3').textContent;
  if (b) return 'button ' + (b.getAttribute('aria-label') || b.textContent.trim());
  return el.tagName.toLowerCase() + (el.className ? '.' + String(el.className).split(' ')[0] : '');
}"""


def done_counts(text):
    return [len(h["done"]) for h in json.loads(text)["habits"]]


def target_point(page, target):
    d = page.locator("dialog")
    box = d.bounding_box()
    if target == "cancel":
        b = page.locator("dialog .btn-secondary").bounding_box()
    elif target == "delete":
        b = page.locator("dialog .btn-danger").bounding_box()
    else:  # backdrop: the centre of the first day bead that lies outside the dialog box
        for bead in page.locator("li.habit button.day").all():
            r = bead.bounding_box()
            cx, cy = r["x"] + r["width"] / 2, r["y"] + r["height"] / 2
            if not (box["x"] <= cx <= box["x"] + box["width"] and box["y"] <= cy <= box["y"] + box["height"]):
                return cx, cy
        return None
    return b["x"] + b["width"] / 2, b["y"] + b["height"] / 2


def run_case(run, seed, vp, touch, target, patched_app=None):
    kw = {"has_touch": True} if touch else {}
    ctx, page, log = open_app(run.browser, run.base, storage=seed, viewport=vp, **kw)
    try:
        if patched_app is not None:
            page.route("**/src/app.js", lambda route, request: route.fulfill(status=200, content_type="text/javascript", body=patched_app))
            page.reload()
            page.wait_for_selector("li.habit")
        before = stored(page)
        rows_before = row_names(page)
        page.get_by_role("button", name=f"Delete {rows_before[0]}", exact=True).click()
        page.locator("dialog").evaluate("(d) => Promise.all(d.getAnimations().map((a) => a.finished))")
        page.wait_for_timeout(600)
        point = target_point(page, target)
        if point is None:
            return "no bead outside the dialog box at this size"
        x, y = point
        if touch:
            page.touchscreen.tap(x, y)
            page.touchscreen.tap(x, y)
        else:
            page.mouse.dblclick(x, y)
        page.wait_for_timeout(500)
        after = stored(page)
        under = page.evaluate(DESCRIBE, [x, y])
        dialog_open = page.evaluate("() => document.querySelector('dialog').open")
        rows_after = row_names(page)
        # What the first press alone leaves: the same habits, minus the first one when the press was 'Delete habit'.
        expected = json.loads(before)["habits"][1:] if target == "delete" else json.loads(before)["habits"]
        notes = []
        if rows_after != rows_before:
            notes.append(f"rows {len(rows_before)}->{len(rows_after)}")
        if dialog_open:
            notes.append("dialog OPEN again (second press opened a dialog)")
        names_after = [h["name"] for h in json.loads(after)["habits"]]
        if names_after not in ([h["name"] for h in expected], [h["name"] for h in json.loads(before)["habits"]]):
            notes.append("A HABIT THAT WAS NOT ASKED ABOUT WAS DELETED")
        if json.loads(after)["habits"] != expected:
            notes.append(f"STORED DATA CHANGED by the second press, done counts {done_counts(before)}->{done_counts(after)}")
        if not notes:
            notes.append("nothing changed")
        return f"point ({x:.0f},{y:.0f}) under it now: {under}; " + "; ".join(notes)
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
        for seed_name, seed in [("sample (3 habits)", SAMPLE), ("12 plain habits", PLAIN12)]:
            print(f"=== {seed_name}")
            for vp in VIEWPORTS:
                for touch in (False, True):
                    for target in ("cancel", "delete", "backdrop"):
                        result = run_case(run, seed, vp, touch, target, patched_app)
                        print(f"  {vp[0]}x{vp[1]} {'touch' if touch else 'mouse'} {target:8s} -> {result}", flush=True)
    print("done")


if __name__ == "__main__":
    main()
