"""T7 accidental deletion, against the running app.

A. Keyboard: Enter, Space and auto-repeat on the trash button; Enter and Space on the dialog as it opens; Esc; backdrop.
B. returnValue reuse: delete A, then open B and press Esc (must keep B).
C. Double click and double tap on the trash button, then on "Delete habit".
D. Geometry: for every viewport width, does a point of the trash button lie inside the "Delete habit" button of the
   dialog it opens? If so, a double tap there deletes without a deliberate second action.
Run: PYTHONDONTWRITEBYTECODE=1 python <this file>   (cwd = project root)
"""
from lib import Run, open_app, state_text, stored, row_names, SAMPLE_HABITS, new_context, attach

SEED = state_text(SAMPLE_HABITS)


def count(page):
    return page.locator("li.habit").count()


def active(page):
    return page.evaluate("() => { const a = document.activeElement; return a.tagName + ':' + (a.getAttribute('aria-label') || a.textContent.trim().slice(0, 20)); }")


def main():
    with Run() as run:
        b, base = run.browser, run.base

        print("--- A. keyboard paths (390 x 844, sample, 3 habits)")
        ctx, page, log = open_app(b, base, storage=SEED)
        trash = page.get_by_role("button", name="Delete Stretch 10 minutes", exact=True)
        trash.focus()
        page.keyboard.press("Enter")
        print(f"   Enter on trash -> dialog open={page.evaluate('() => document.querySelector(\"dialog\").open')} focus={active(page)}")
        page.keyboard.press("Enter")
        page.wait_for_timeout(150)
        print(f"   Enter again (focus is Cancel) -> habits={count(page)} dialog open={page.evaluate('() => document.querySelector(\"dialog\").open')} focus={active(page)}")
        # auto-repeat: key held down on the trash button
        trash.focus()
        for _ in range(6):
            page.keyboard.down("Enter")
            page.wait_for_timeout(60)
        page.keyboard.up("Enter")
        page.wait_for_timeout(300)
        print(f"   Enter held (6 repeats) on trash -> habits={count(page)} dialog open={page.evaluate('() => document.querySelector(\"dialog\").open')} focus={active(page)}")
        if page.evaluate("() => document.querySelector('dialog').open"):
            page.keyboard.press("Escape")
        trash.focus()
        page.keyboard.down("Space")
        page.keyboard.up("Space")
        page.wait_for_timeout(150)
        print(f"   Space on trash -> dialog open={page.evaluate('() => document.querySelector(\"dialog\").open')} focus={active(page)}")
        page.keyboard.press("Space")
        page.wait_for_timeout(150)
        print(f"   Space again (Cancel) -> habits={count(page)} dialog open={page.evaluate('() => document.querySelector(\"dialog\").open')}")
        trash.focus()
        page.keyboard.press("Enter")
        page.keyboard.press("Escape")
        page.wait_for_timeout(150)
        print(f"   Enter then Esc -> habits={count(page)} focus={active(page)}")
        trash.click()
        page.mouse.click(5, 5)
        page.wait_for_timeout(150)
        print(f"   click trash then click on the backdrop (5,5) -> habits={count(page)} dialog open={page.evaluate('() => document.querySelector(\"dialog\").open')}")
        print(f"   stored unchanged after all of that: {stored(page) == SEED}; cons_err={len(log.console_errors())} page_err={log.errors}")
        ctx.close()

        print("--- B. returnValue reuse")
        ctx, page, log = open_app(b, base, storage=SEED)
        page.get_by_role("button", name="Delete Read 20 pages", exact=True).click()
        page.locator("dialog .btn-danger").click()
        page.wait_for_function("() => document.querySelectorAll('li.habit').length === 2")
        page.get_by_role("button", name="Delete Stretch 10 minutes", exact=True).click()
        page.keyboard.press("Escape")
        page.wait_for_timeout(200)
        print(f"   delete A, open B, Esc -> rows={row_names(page)}  (B must remain)")
        page.get_by_role("button", name="Delete Stretch 10 minutes", exact=True).click()
        page.locator("dialog .btn-secondary").click()
        page.wait_for_timeout(200)
        print(f"   open B, Cancel -> rows={row_names(page)}")
        ctx.close()

        print("--- C. double click / double tap")
        for label, vp, touch in [("mouse 390x844", (390, 844), False), ("mouse 1280x800", (1280, 800), False), ("touch 360x780", (360, 780), True)]:
            kw = {"has_touch": True, "is_mobile": True} if touch else {}
            ctx, page, log = open_app(b, base, storage=SEED, viewport=vp, **kw)
            tr = page.get_by_role("button", name="Delete Stretch 10 minutes", exact=True)
            if touch:
                box = tr.bounding_box()
                x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
                page.touchscreen.tap(x, y)
                page.touchscreen.tap(x, y)
            else:
                tr.dblclick()
            page.wait_for_timeout(300)
            print(f"   {label}: double click/tap on trash -> habits={count(page)} dialog open={page.evaluate('() => document.querySelector(\"dialog\").open')}")
            ctx.close()
        for label, vp, touch in [("mouse 390x844", (390, 844), False), ("mouse 1280x800", (1280, 800), False), ("touch 360x780", (360, 780), True), ("touch 412x915", (412, 915), True)]:
            kw = {"has_touch": True, "is_mobile": True} if touch else {}
            ctx, page, log = open_app(b, base, storage=SEED, viewport=vp, **kw)
            before = page.evaluate("() => [...document.querySelectorAll('button.day')].map(b => b.getAttribute('aria-pressed')[0]).join('')")
            page.get_by_role("button", name="Delete Read 20 pages", exact=True).click()
            btn = page.locator("dialog .btn-danger")
            box = btn.bounding_box()
            x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
            if touch:
                page.touchscreen.tap(x, y)
                page.wait_for_timeout(40)
                page.touchscreen.tap(x, y)
            else:
                page.mouse.dblclick(x, y)
            page.wait_for_timeout(500)
            after = page.evaluate("() => [...document.querySelectorAll('button.day')].map(b => b.getAttribute('aria-pressed')[0]).join('')")
            hit = page.evaluate("([x, y]) => { const e = document.elementFromPoint(x, y); return e ? (e.closest('button') ? (e.closest('button').className + ' ' + (e.closest('button').getAttribute('aria-label') || '')) : e.tagName + '.' + e.className) : null; }", [x, y])
            print(f"   {label}: double click/tap on 'Delete habit' at ({x:.0f},{y:.0f}) -> rows={row_names(page)} dialog open={page.evaluate('() => document.querySelector(\"dialog\").open')}")
            print(f"        element now under that point: {hit}; day states before={before} after={after} (7 per habit; ticks that changed: {sum(1 for i in range(min(len(before), len(after))) if before[i] != after[i]) if len(before) == len(after) else 'rows differ'})")
            ctx.close()

        print("--- D. geometry: can a tap point on a trash button also be inside 'Delete habit' of the dialog it opens?")
        ctx = new_context(b, viewport=(390, 844))
        page = ctx.new_page()
        page.goto(base + "__seed__")
        page.evaluate("(t) => localStorage.setItem('streaks.state', t)", state_text([{"name": f"Habit {i}", "done": []} for i in range(1, 13)]))
        overlaps = []
        checked = 0
        for width in list(range(320, 1000, 10)) + [1024, 1100, 1280, 1366, 1440, 1536, 1920]:
            for height in (568, 700, 844):
                page.set_viewport_size({"width": width, "height": height})
                page.goto(base)
                page.wait_for_selector("li.habit")
                # trash buttons: x range is the same for every row; y depends on scroll, so scan scroll positions
                page.locator(".habit-head .icon-btn").first.click()
                d = page.locator("dialog .btn-danger").bounding_box()
                page.keyboard.press("Escape")
                page.wait_for_timeout(30)
                tx = page.evaluate("() => { const r = document.querySelector('.habit-head .icon-btn').getBoundingClientRect(); return [r.left, r.right, r.width, r.height]; }")
                checked += 1
                x_overlap = tx[0] < d["x"] + d["width"] and tx[1] > d["x"]
                if x_overlap:
                    # find a row/scroll where the trash y-range meets the Delete button y-range
                    page_h = page.evaluate("() => document.documentElement.scrollHeight")
                    hit = None
                    for sy in range(0, max(1, page_h - height) + 1, 8):
                        page.evaluate("(y) => window.scrollTo(0, y)", sy)
                        rects = page.evaluate("() => [...document.querySelectorAll('.habit-head .icon-btn')].map(b => { const r = b.getBoundingClientRect(); return [r.left, r.top, r.right, r.bottom]; })")
                        for r in rects:
                            if r[0] < d["x"] + d["width"] and r[2] > d["x"] and r[1] < d["y"] + d["height"] and r[3] > d["y"]:
                                hit = (sy, r)
                                break
                        if hit:
                            break
                    overlaps.append((width, height, round(tx[0]), round(tx[1]), "x-overlap", hit))
        ctx.close()
        print(f"   viewport sizes checked: {checked}; sizes where the trash x-range meets the Delete habit x-range: {len(overlaps)}")
        for o in overlaps[:30]:
            print("   ", o)
    print("done")


if __name__ == "__main__":
    main()
