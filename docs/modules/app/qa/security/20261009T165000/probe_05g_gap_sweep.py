"""T7: how reliable is the double-tap delete, by gap between the two taps and by viewport (sample data, no scrolling)?

For each viewport and gap, a fresh context opens the sample, the point inside both the third habit's trash button and the
dialog's Delete habit button is found, and two touch taps (or two mouse clicks) are sent with the gap between them.
Prints deleted yes/no. Also prints the tap-to-dialog timeline once: when does a second tap stop reaching Delete habit?
Run: PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python <this file>   (cwd = project root)
"""
from lib import Run, open_app, state_text, row_names, SAMPLE_HABITS

SEED = state_text(SAMPLE_HABITS)
GAPS = [0, 40, 80, 120, 200, 300, 450, 700]


def find_overlap(b, base, vp, touch):
    kw = {"has_touch": True, "is_mobile": True} if touch else {}
    ctx, page, log = open_app(b, base, storage=SEED, viewport=vp, **kw)
    trash = page.get_by_role("button", name="Delete No phone after 11pm", exact=True)
    rect = trash.bounding_box()
    trash.click()
    d = page.locator("dialog .btn-danger").bounding_box()
    ctx.close()
    left, right = max(rect["x"], d["x"]), min(rect["x"] + rect["width"], d["x"] + d["width"])
    top, bottom = max(rect["y"], d["y"]), min(rect["y"] + rect["height"], d["y"] + d["height"])
    if left >= right or top >= bottom:
        return None
    return (left + right) / 2, (top + bottom) / 2


def main():
    with Run() as run:
        b, base = run.browser, run.base
        for label, vp, touch in [("390x844 touch", (390, 844), True), ("412x915 touch", (412, 915), True), ("1440x900 mouse", (1440, 900), False)]:
            pt = find_overlap(b, base, vp, touch)
            print(f"--- {label}: overlap point {pt}")
            if pt is None:
                continue
            x, y = pt
            row = []
            for gap in GAPS:
                for attempt in range(2):
                    kw = {"has_touch": True, "is_mobile": True} if touch else {}
                    ctx, page, log = open_app(b, base, storage=SEED, viewport=vp, **kw)
                    page.wait_for_selector("li.habit")
                    if touch:
                        page.touchscreen.tap(x, y)
                        if gap:
                            page.wait_for_timeout(gap)
                        page.touchscreen.tap(x, y)
                    else:
                        page.mouse.click(x, y)
                        if gap:
                            page.wait_for_timeout(gap)
                        page.mouse.click(x, y)
                    page.wait_for_timeout(700)
                    deleted = len(row_names(page)) == 2
                    row.append(f"{gap}ms#{attempt + 1}:{'DELETED' if deleted else 'kept'}")
                    ctx.close()
            print("   " + "  ".join(row), flush=True)
    print("done")


if __name__ == "__main__":
    main()
