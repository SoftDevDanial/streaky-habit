"""T7 fix hints: what does the second click of a double click / double tap look like to a listener on 'Delete habit'?

Logs, in the capture phase on the dialog, every click: target, event.detail (click count), pointerType, and the gap
since the click that opened the dialog (event.timeStamp). A guard on detail or on elapsed time could separate a
deliberate click from tap-through.
Run: PYTHONDONTWRITEBYTECODE=1 python <this file>   (cwd = project root)
"""
from lib import Run, state_text, new_context

HABITS = state_text([{"name": f"Habit {i}", "done": []} for i in range(1, 13)])

LISTEN = """() => {
  window.__log = [];
  let last = null;
  document.addEventListener('click', (e) => {
    const t = e.target.closest && e.target.closest('button');
    window.__log.push({ target: t ? (t.textContent.trim() || t.className) : e.target.tagName, detail: e.detail, pointerType: e.pointerType, gap: last === null ? null : Math.round(e.timeStamp - last) });
    last = e.timeStamp;
  }, true);
}"""


def best(page):
    from probe_05b_tap_through import delete_rect, best_overlap
    d = delete_rect(page)
    return best_overlap(page, d)


def main():
    with Run() as run:
        b, base = run.browser, run.base
        for label, touch, vp in [("mouse dblclick 390x844", False, (390, 844)), ("touch double tap 390x844", True, (390, 844)), ("mouse dblclick 1280x800", False, (1280, 800))]:
            kw = {"has_touch": True, "is_mobile": True} if touch else {}
            ctx = new_context(b, viewport=vp, **kw)
            page = ctx.new_page()
            page.goto(base + "__seed__")
            page.evaluate("(t) => localStorage.setItem('streaks.state', t)", HABITS)
            page.goto(base)
            page.wait_for_selector("li.habit")
            area, sy, index, rect, trash = best(page)
            page.evaluate("(y) => window.scrollTo(0, y)", sy)
            page.evaluate(LISTEN)
            x, y = (rect[0] + rect[2]) / 2, (rect[1] + rect[3]) / 2
            if touch:
                page.touchscreen.tap(x, y)
                page.wait_for_timeout(120)
                page.touchscreen.tap(x, y)
            else:
                page.mouse.dblclick(x, y, delay=80)
            page.wait_for_timeout(500)
            print(f"--- {label}: tap point ({x:.0f},{y:.0f}) rows now {page.locator('li.habit').count()}")
            for entry in page.evaluate("() => window.__log"):
                print("    ", entry)
            ctx.close()
    print("done")


if __name__ == "__main__":
    main()
