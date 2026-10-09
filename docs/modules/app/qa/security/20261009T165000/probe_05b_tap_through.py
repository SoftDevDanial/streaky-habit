"""T7 follow-up: the trash button and the dialog's 'Delete habit' button overlap on screen.

When a habit's trash button is tapped, the modal dialog opens at once under the same finger. A second tap (a double tap)
at the same point is delivered to whatever is there. If that point is inside 'Delete habit' the habit is deleted without
any deliberate second action. This probe (1) summarises, per viewport size, the largest overlap any row can reach (the
page may be scrolled so that the row sits where the dialog's button is), and (2) performs the double tap with real input
events and reports the outcome.
Run: PYTHONDONTWRITEBYTECODE=1 python <this file>   (cwd = project root)
"""
from lib import Run, state_text, new_context

HABITS = state_text([{"name": f"Habit {i}", "done": []} for i in range(1, 13)])


def open_page(browser, base, width, height, touch=False):
    kw = {"has_touch": True, "is_mobile": True} if touch else {}
    ctx = new_context(browser, viewport=(width, height), **kw)
    page = ctx.new_page()
    page.goto(base + "__seed__")
    page.evaluate("(t) => localStorage.setItem('streaks.state', t)", HABITS)
    page.goto(base)
    page.wait_for_selector("li.habit")
    return ctx, page


def delete_rect(page):
    """The dialog's Delete habit box for the first row (position does not depend on the row for one-line titles)."""
    page.evaluate("() => window.scrollTo(0, 0)")
    page.locator(".habit-head .icon-btn").first.click()
    r = page.locator("dialog .btn-danger").bounding_box()
    page.keyboard.press("Escape")
    page.wait_for_timeout(60)
    return r


def best_overlap(page, d):
    """Best (area, scrollY, row index, overlap rect, trash rect) over rows, scrolling a row onto the Delete button."""
    info = page.evaluate(
        """() => ({ maxScroll: document.documentElement.scrollHeight - innerHeight, height: innerHeight,
          rows: [...document.querySelectorAll('.habit-head .icon-btn')].map(b => { const r = b.getBoundingClientRect(); return [r.left, r.top + scrollY, r.right, r.bottom + scrollY]; }) })"""
    )
    best = None
    for index, (left, top, right, bottom) in enumerate(info["rows"]):
        sy = round(max(0, min(info["maxScroll"], (top + bottom) / 2 - (d["y"] + d["height"] / 2))))
        t, bt = top - sy, bottom - sy
        ol, orr = max(left, d["x"]), min(right, d["x"] + d["width"])
        ot, ob = max(t, d["y"]), min(bt, d["y"] + d["height"])
        if ol < orr and ot < ob and t >= 0 and bt <= info["height"]:
            area = (orr - ol) * (ob - ot)
            cand = (area, sy, index, (round(ol), round(ot), round(orr), round(ob)), (round(left), round(t), round(right), round(bt)))
            if best is None or area > best[0]:
                best = cand
    return best


def main():
    with Run() as run:
        b, base = run.browser, run.base

        print("--- (1) per viewport: largest overlap of any trash button with the dialog's 'Delete habit' (12 habits, one-line titles)")
        ctx, page = open_page(b, base, 390, 844)
        summary = {}
        for width in list(range(320, 560, 10)) + [600, 700, 800, 899, 900, 1000, 1100, 1280, 1440, 1920]:
            for height in (568, 667, 780, 844, 915):
                page.set_viewport_size({"width": width, "height": height})
                page.reload()
                page.wait_for_selector("li.habit")
                d = delete_rect(page)
                best = best_overlap(page, d)
                if best:
                    summary.setdefault(width, []).append((height, best[3][2] - best[3][0], best[3][3] - best[3][1]))
        ctx.close()
        for w in sorted(summary):
            print(f"   width {w}: heights with an overlap {[h for h, _, _ in summary[w]]}; overlap w x h px at those heights {[(ow, oh) for _, ow, oh in summary[w]]}")
        print(f"   widths with a reachable overlap: {sorted(summary)}")
        print(f"   widths checked without overlap: {[w for w in list(range(320, 560, 10)) + [600, 700, 800, 899, 900, 1000, 1100, 1280, 1440, 1920] if w not in summary]}")

        print("--- (2) end-to-end double tap at the overlap, 390 x 844, touch events")
        ctx, page = open_page(b, base, 390, 844, touch=True)
        d = delete_rect(page)
        best = best_overlap(page, d)
        area, sy, index, rect, trash = best
        page.evaluate("(y) => window.scrollTo(0, y)", sy)
        x, y = (rect[0] + rect[2]) / 2, (rect[1] + rect[3]) / 2
        before = page.locator("h3.habit-name").all_text_contents()
        icon = (trash[0] + 12, trash[0] + 32)
        print(f"   scrollY={sy}, row {index + 1} ('{before[index]}'), trash rect {trash}, Delete button {tuple(round(v) for v in (d['x'], d['y'], d['x'] + d['width'], d['y'] + d['height']))}, overlap {rect}")
        print(f"   tap point ({x:.0f},{y:.0f}); the 20 px icon spans x {icon[0]}..{icon[1]}; point is {'inside' if icon[0] <= x <= icon[1] else 'outside'} the icon, {x - (trash[0] + trash[2]) / 2:+.0f} px from the button centre")
        page.touchscreen.tap(x, y)
        page.wait_for_timeout(60)
        page.touchscreen.tap(x, y)
        page.wait_for_timeout(500)
        after = page.locator("h3.habit-name").all_text_contents()
        print(f"   after two taps: rows {len(before)} -> {len(after)}; dialog open={page.evaluate('() => document.querySelector(\"dialog\").open')}; removed={[n for n in before if n not in after]}")
        ctx.close()

        print("--- (3) same with a mouse double click, 390 x 844")
        ctx, page = open_page(b, base, 390, 844)
        d = delete_rect(page)
        area, sy, index, rect, trash = best_overlap(page, d)
        page.evaluate("(y) => window.scrollTo(0, y)", sy)
        x, y = (rect[0] + rect[2]) / 2, (rect[1] + rect[3]) / 2
        before = page.locator("li.habit").count()
        page.mouse.dblclick(x, y)
        page.wait_for_timeout(500)
        print(f"   dblclick at ({x:.0f},{y:.0f}) on row {index + 1}: rows {before} -> {page.locator('li.habit').count()}")
        ctx.close()

        print("--- (4) 1280 x 800 desktop, mouse double click at the best overlap")
        ctx, page = open_page(b, base, 1280, 800)
        d = delete_rect(page)
        best = best_overlap(page, d)
        print(f"   best overlap: {best}")
        if best:
            area, sy, index, rect, trash = best
            page.evaluate("(y) => window.scrollTo(0, y)", sy)
            x, y = (rect[0] + rect[2]) / 2, (rect[1] + rect[3]) / 2
            before = page.locator("li.habit").count()
            page.mouse.dblclick(x, y)
            page.wait_for_timeout(500)
            print(f"   dblclick at ({x:.0f},{y:.0f}) on row {index + 1}, trash rect {trash}: rows {before} -> {page.locator('li.habit').count()}")
        ctx.close()

        print("--- (5) long titles move the Delete button down: does a 3-line title (40 W) still leave an overlap at 390 x 844?")
        ctx = new_context(b, viewport=(390, 844))
        page = ctx.new_page()
        page.goto(base + "__seed__")
        page.evaluate("(t) => localStorage.setItem('streaks.state', t)", state_text([{"name": ("W" * 39) + str(i % 10), "done": []} for i in range(12)]))
        page.goto(base)
        page.wait_for_selector("li.habit")
        d = delete_rect(page)
        best = best_overlap(page, d)
        print(f"   Delete button box: {tuple(round(v) for v in (d['x'], d['y'], d['x'] + d['width'], d['y'] + d['height']))}; best overlap: {best}")
        ctx.close()
    print("done")


if __name__ == "__main__":
    main()
