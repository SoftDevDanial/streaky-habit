"""SEC-01 as fixed, part 1: the audit's own reproduction, then a gap sweep across the 500 ms edge.

For each viewport: the third habit's trash button and the dialog's "Delete habit" are measured on a throwaway page;
the point is the middle of their overlap (the trash centre when they do not overlap). Control: one click or tap at
the point only opens the dialog. Then a double click (mouse: two presses back to back, the second with click count
2) or a double tap (60 ms between taps) at the same point. Real mouse and touch input, an installed clock that runs
in real time. The event log shows each click's browser time, `detail`, target and whether a guard cancelled or
stopped it.
Part 2 repeats the audit's two exact points. Part 3 sweeps the gap between the two clicks on the audit's two
reproduction viewports.
Run: PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python -B <this file>   (cwd = project root)
"""
from lib import Run, centre, double, events, fmt_clicks, geometry, open_app, press, reseed, snap, verdict

VIEWPORTS = [
    ("1440x900 mouse", (1440, 900), False),
    ("412x915 touch", (412, 915), True),
    ("390x844 touch", (390, 844), True),
    ("390x844 mouse", (390, 844), False),
    ("375x667 touch", (375, 667), True),
    ("360x640 touch", (360, 640), True),
]


def main():
    with Run() as run:
        say = run.say
        say("== Part 1: audit reproduction, third habit, three-habit sample ==")
        for label, vp, touch in VIEWPORTS:
            g = geometry(run.browser, run.base, vp, touch)
            ov = g["overlap"]
            t, d = g["trash"], g["danger"]
            if ov:
                x, y = (ov[0] + ov[2]) / 2, (ov[1] + ov[3]) / 2
                where = f"overlap ({ov[0]:.0f},{ov[1]:.0f})-({ov[2]:.0f},{ov[3]:.0f})"
            else:
                x, y = centre(t)
                where = "NO overlap at rest (trash centre used)"
            say(f"--- {label}: trash ({t['x']:.0f},{t['y']:.0f}) {t['width']:.0f}x{t['height']:.0f}, Delete habit at rest ({d['x']:.0f},{d['y']:.0f}) {d['width']:.0f}x{d['height']:.0f}, {where}, point ({x:.0f},{y:.0f})")
            ctx, page = open_app(run.browser, run.base, vp, touch)
            try:
                before = snap(page)
                press(page, x, y, touch)
                page.wait_for_timeout(700)
                one = snap(page)
                say(f"    control, one activation: {verdict(before, one)}; clicks: {fmt_clicks(events(page))}")
                page.keyboard.press("Escape")
                page.wait_for_timeout(300)
                reseed(page)
                before = snap(page)
                double(page, x, y, touch, gap_ms=60 if touch else 0)
                page.wait_for_timeout(900)
                after = snap(page)
                say(f"    DOUBLE at the point: {verdict(before, after)}")
                say(f"      clicks: {fmt_clicks(events(page))}")
                say(f"      stored unchanged: {after['stored'] == before['stored']}; page errors: {page.errors}")
            finally:
                ctx.close()

        say("== Part 2: the audit's two exact points on the sample ==")
        for label, vp, touch, (x, y) in [("1440x900 mouse (743,512)", (1440, 900), False, (743, 512)),
                                          ("412x915 touch (364,498)", (412, 915), True, (364, 498))]:
            ctx, page = open_app(run.browser, run.base, vp, touch)
            try:
                before = snap(page)
                double(page, x, y, touch, gap_ms=60 if touch else 0)
                page.wait_for_timeout(900)
                after = snap(page)
                say(f"--- {label}: {verdict(before, after)}; clicks: {fmt_clicks(events(page))}")
            finally:
                ctx.close()

        say("== Part 3: gap sweep at the overlap point (gap = wait between the two activations; dt = measured event time gap of the two clicks) ==")
        for label, vp, touch in [VIEWPORTS[0], VIEWPORTS[1]]:
            g = geometry(run.browser, run.base, vp, touch)
            ov = g["overlap"]
            x, y = (ov[0] + ov[2]) / 2, (ov[1] + ov[3]) / 2
            ctx, page = open_app(run.browser, run.base, vp, touch)
            try:
                for gap in [0, 100, 200, 300, 400, 450, 500, 550, 600, 700]:
                    reseed(page)
                    before = snap(page)
                    double(page, x, y, touch, gap_ms=gap)
                    page.wait_for_timeout(700)
                    after = snap(page)
                    ev = events(page)
                    dt = round(ev[1]["t"] - ev[0]["t"], 1) if len(ev) >= 2 else None
                    deleted = len(after["names"]) < len(before["names"])
                    say(f"  {label} gap {gap:3d} ms -> dt {dt} ms: {'DELETED' if deleted else 'kept'}; {verdict(before, after)}; clicks: {fmt_clicks(ev)}")
            finally:
                ctx.close()
    run.finish("probe_01")


if __name__ == "__main__":
    main()
