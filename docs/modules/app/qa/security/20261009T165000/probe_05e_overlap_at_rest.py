"""T7 likelihood: with the page NOT scrolled, how often does a row's trash button overlap the dialog's 'Delete habit'?

For habit counts 1 to 12 and common viewports, opens the app unscrolled, computes (without clicking trash twice) the rect
of every trash button and the Delete habit rect of the dialog that row opens, and reports the rows whose rects overlap.
Titles are one line ("Habit N") and two lines (a 30-character name).
Run: PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python <this file>   (cwd = project root)
"""
from lib import Run, new_context, state_text

VIEWPORTS = [(390, 844), (360, 780), (412, 915), (375, 667), (1280, 800), (1440, 900), (1920, 1080), (1366, 768)]


def run_case(page, base, count, long_names, viewport):
    names = [(("Read twenty pages before bed " if long_names else "Habit ") + f"{i:02d}")[:40] for i in range(1, count + 1)]
    page.set_viewport_size({"width": viewport[0], "height": viewport[1]})
    page.goto(base)
    page.evaluate("(t) => localStorage.setItem('streaks.state', t)", state_text([{"name": n, "done": []} for n in names]))
    page.reload()
    page.wait_for_selector("li.habit")
    page.evaluate("() => window.scrollTo(0, 0)")
    hits = []
    for i in range(count):
        rect = page.evaluate("(i) => { const r = document.querySelectorAll('.habit-head .icon-btn')[i].getBoundingClientRect(); return [r.left, r.top, r.right, r.bottom]; }", i)
        in_view = rect[3] > 0 and rect[1] < viewport[1]
        if not in_view:
            continue
        page.evaluate("(i) => document.querySelectorAll('.habit-head .icon-btn')[i].click()", i)
        d = page.locator("dialog .btn-danger").bounding_box()
        page.evaluate("() => document.querySelector('dialog').close('cancel')")
        ol, orr = max(rect[0], d["x"]), min(rect[2], d["x"] + d["width"])
        ot, ob = max(rect[1], d["y"]), min(rect[3], d["y"] + d["height"])
        if ol < orr and ot < ob:
            hits.append((i + 1, round(orr - ol), round(ob - ot)))
        page.evaluate("() => window.scrollTo(0, 0)")
    return hits


def main():
    with Run() as run:
        b, base = run.browser, run.base
        ctx = new_context(b)
        page = ctx.new_page()
        page.goto(base + "__seed__")
        for long_names in (False, True):
            print(f"=== {'two-line' if long_names else 'one-line'} dialog titles; entries are (row, overlap width px, overlap height px)")
            for vp in VIEWPORTS:
                cells = []
                for count in (1, 2, 3, 4, 5, 6, 8, 12):
                    h = run_case(page, base, count, long_names, vp)
                    cells.append(f"{count}:{h if h else '-'}")
                print(f"  {vp[0]}x{vp[1]}  " + "  ".join(cells), flush=True)
        ctx.close()
    print("done")


if __name__ == "__main__":
    main()
