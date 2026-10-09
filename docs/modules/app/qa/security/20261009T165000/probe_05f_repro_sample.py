"""T7 reproduction on the three-habit sample, no scrolling, real input: the third habit's trash button, double click or
double tap at a point inside the button where it overlaps the dialog's 'Delete habit'.

Prints the point, how far it is from the icon centre, and the habits before and after. A single click at the same point
is the control: it must only open the dialog.
Run: PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python <this file>   (cwd = project root)
"""
from lib import Run, open_app, state_text, row_names, SAMPLE_HABITS

SEED = state_text(SAMPLE_HABITS)


def overlap(page):
    trash = page.get_by_role("button", name="Delete No phone after 11pm", exact=True)
    rect = trash.bounding_box()
    trash.click()
    d = page.locator("dialog .btn-danger").bounding_box()
    page.keyboard.press("Escape")
    page.wait_for_timeout(250)
    left, right = max(rect["x"], d["x"]), min(rect["x"] + rect["width"], d["x"] + d["width"])
    top, bottom = max(rect["y"], d["y"]), min(rect["y"] + rect["height"], d["y"] + d["height"])
    return rect, d, (left, top, right, bottom)


def main():
    with Run() as run:
        b, base = run.browser, run.base
        for label, vp, touch in [("desktop 1440x900, mouse", (1440, 900), False), ("phone 390x844, touch", (390, 844), True), ("phone 412x915, touch", (412, 915), True)]:
            kw = {"has_touch": True, "is_mobile": True} if touch else {}
            ctx, page, log = open_app(b, base, storage=SEED, viewport=vp, **kw)
            rect, d, ov = overlap(page)
            x, y = (ov[0] + ov[2]) / 2, (ov[1] + ov[3]) / 2
            cx = rect["x"] + rect["width"] / 2
            cy = rect["y"] + rect["height"] / 2
            print(f"--- {label}: trash box ({rect['x']:.0f},{rect['y']:.0f})-({rect['x'] + rect['width']:.0f},{rect['y'] + rect['height']:.0f}), Delete habit box ({d['x']:.0f},{d['y']:.0f})-({d['x'] + d['width']:.0f},{d['y'] + d['height']:.0f}), overlap ({ov[0]:.0f},{ov[1]:.0f})-({ov[2]:.0f},{ov[3]:.0f})")
            print(f"    point ({x:.0f},{y:.0f}) is {x - cx:+.0f} px in x and {y - cy:+.0f} px in y from the trash button centre (the icon is 20 px wide)")
            # control: single activation at that point
            if touch:
                page.touchscreen.tap(x, y)
            else:
                page.mouse.click(x, y)
            page.wait_for_timeout(500)
            print(f"    single click/tap there -> habits={row_names(page)} dialog open={page.evaluate('() => document.querySelector(\"dialog\").open')}")
            if page.evaluate("() => document.querySelector('dialog').open"):
                page.keyboard.press("Escape")
                page.wait_for_timeout(300)
            if touch:
                page.touchscreen.tap(x, y)
                page.wait_for_timeout(100)
                page.touchscreen.tap(x, y)
            else:
                page.mouse.dblclick(x, y, delay=60)
            page.wait_for_timeout(600)
            print(f"    DOUBLE click/tap there -> habits={row_names(page)} dialog open={page.evaluate('() => document.querySelector(\"dialog\").open')}; stored={page.evaluate('() => localStorage.getItem(\"streaks.state\")')[:60]}...")
            ctx.close()
    print("done")


if __name__ == "__main__":
    main()
