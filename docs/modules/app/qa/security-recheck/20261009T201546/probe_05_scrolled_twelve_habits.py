"""SEC-01 as fixed, part 5: the audit's scrolled-list vector (probe_05b/05e), re-run on the fix.

Twelve habits, so any row can be scrolled to the height of the dialog's "Delete habit". For each viewport and row the
page is scrolled so the trash button's vertical centre sits at the centre of the dialog's Delete habit (measured on a
throwaway page), then a real double click (viewports 1000 and wider) or double tap (450 and narrower) is made at the
middle of the overlap of the two boxes (the trash centre when they do not overlap at that width). Expect: no delete,
no tick, no second dialog, stored text unchanged.
Run: PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python -B <this file>   (cwd = project root)
"""
from lib import Run, box, centre, double, events, fmt_clicks, make_context, overlap_of, reseed, snap, state_text, verdict

HABITS = [{"name": f"Habit {i:02d}", "done": ["2026-10-06", "2026-10-07"] if i % 2 else []} for i in range(1, 13)]
SEED12 = state_text(HABITS)
VIEWPORTS = [(1000, 700, False), (1280, 800, False), (1440, 900, False), (1920, 1080, False),
             (450, 800, True), (390, 844, True), (360, 640, True), (320, 568, True)]
ROWS = (1, 4, 8, 12)


def delete_rect(run, vp, touch):
    ctx = make_context(run.browser, vp, touch)
    page = ctx.new_page()
    page.goto(run.base + "__seed__")
    page.evaluate("(t) => localStorage.setItem('streaks.state', t)", SEED12)
    page.goto(run.base)
    page.wait_for_selector("li.habit")
    page.locator("li.habit:nth-child(1) .icon-btn").click()
    page.wait_for_selector("dialog[open]")
    page.wait_for_timeout(450)
    rect = box(page, "dialog .btn-danger")
    ctx.close()
    return rect


def main():
    with Run() as run:
        say = run.say
        say("== 12-habit list, scrolled so the row is level with Delete habit ==")
        total = deleted = ticked = reopened = 0
        for w, h, touch in VIEWPORTS:
            vp = (w, h)
            d = delete_rect(run, vp, touch)
            ctx = make_context(run.browser, vp, touch)
            page = ctx.new_page()
            page.goto(run.base + "__seed__")
            page.evaluate("(t) => localStorage.setItem('streaks.state', t)", SEED12)
            page.goto(run.base)
            page.wait_for_selector("li.habit")
            try:
                for row in ROWS:
                    reseed(page, SEED12)
                    page.evaluate("(y) => window.scrollTo(0, 0)", 0)
                    t0 = page.locator(f"li.habit:nth-child({row}) .icon-btn").bounding_box()
                    target_y = d["y"] + d["height"] / 2
                    scroll = max(0, (t0["y"] + t0["height"] / 2) - target_y)
                    page.evaluate("(y) => window.scrollTo(0, y)", scroll)
                    page.wait_for_timeout(120)
                    t = page.locator(f"li.habit:nth-child({row}) .icon-btn").bounding_box()
                    ov = overlap_of(t, d)
                    if ov:
                        x, y = (ov[0] + ov[2]) / 2, (ov[1] + ov[3]) / 2
                    else:
                        x, y = centre(t)
                    before = snap(page)
                    double(page, x, y, touch, gap_ms=60 if touch else 0)
                    page.wait_for_timeout(700)
                    after = snap(page)
                    total += 1
                    d_flag = len(after["names"]) < len(before["names"])
                    t_flag = len(after["names"]) == len(before["names"]) and after["pressed"] != before["pressed"]
                    deleted += d_flag
                    ticked += t_flag
                    say(f"  {w}x{h} {'touch' if touch else 'mouse'} row {row:2d}: scrolled {scroll:.0f}; overlap {('%.0fx%.0f px' % (ov[2] - ov[0], ov[3] - ov[1])) if ov else 'none'}; point ({x:.0f},{y:.0f}); {verdict(before, after)}; stored unchanged={after['stored'] == before['stored']}")
                    if after["open"] and d_flag:
                        reopened += 1
            finally:
                ctx.close()
        say(f"== totals: {total} trials, deleted {deleted}, ticked {ticked} ==")
    run.finish("probe_05")


if __name__ == "__main__":
    main()
