"""SEC-01 as fixed, part 4: the 500 ms edge of both guards, measured exactly with a paused page clock.

The clock is installed, then paused, so `event.timeStamp` (which follows the page clock) is frozen between real inputs
and moves only by `page.clock.run_for(k)`. Real mouse and touch input is used for every press. One new context per trial.
  W1  press trash (opens), run_for(k), press Delete habit: held when k < 500, deletes when k >= 500
  W2  press Cancel, run_for(k), press a bead: lost when k < 500, ticks when k >= 500
Run: PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python -B <this file>   (cwd = project root)
"""
from lib import SEED, Run, box, centre, events, fmt_clicks, make_context, press, snap, verdict

KS = [0, 1, 250, 498, 499, 500, 501, 600]
CASES = [("1440x900 mouse", (1440, 900), False), ("412x915 touch", (412, 915), True)]


def new_page(run, vp, touch):
    ctx = make_context(run.browser, vp, touch, clock="install")
    page = ctx.new_page()
    page.goto(run.base + "__seed__")
    page.evaluate("(t) => localStorage.setItem('streaks.state', t)", SEED)
    page.goto(run.base)
    page.wait_for_selector("li.habit")
    page.clock.pause_at("2026-10-08T12:01:00+08:00")
    return ctx, page


def main():
    with Run() as run:
        say = run.say
        say("== W1: opening click, then k ms of page time, then Delete habit ==")
        for label, vp, touch in CASES:
            for k in KS:
                ctx, page = new_page(run, vp, touch)
                try:
                    before = snap(page)
                    press(page, *centre(page.locator("li.habit:nth-child(3) .icon-btn").bounding_box()), touch)
                    page.wait_for_timeout(250)  # real time for the render; the page clock is paused
                    if k:
                        page.clock.run_for(k)
                    press(page, *centre(box(page, "dialog .btn-danger")), touch)
                    page.wait_for_timeout(250)
                    page.clock.run_for(1)  # lets the dialog's close event run its task under the paused clock
                    page.wait_for_timeout(150)
                    after = snap(page)
                    ev = events(page)
                    dt = round(ev[-1]["t"] - ev[0]["t"], 2)
                    deleted = len(after["names"]) < len(before["names"])
                    expect = k >= 500
                    flag = "ok" if deleted == expect else "UNEXPECTED"
                    say(f"  {label} k={k:3d} (event dt {dt} ms): {'DELETED' if deleted else 'held'} (expected {'delete' if expect else 'held'}: {flag}); {verdict(before, after)}")
                finally:
                    ctx.close()
        say("== W2: Cancel click, then k ms of page time, then a bead click ==")
        for label, vp, touch in CASES:
            for k in KS:
                ctx, page = new_page(run, vp, touch)
                try:
                    before = snap(page)
                    press(page, *centre(page.locator("li.habit:nth-child(2) .icon-btn").bounding_box()), touch)
                    page.wait_for_timeout(250)
                    press(page, *centre(box(page, "dialog .btn-secondary")), touch)
                    page.wait_for_timeout(250)
                    if k:
                        page.clock.run_for(k)
                    press(page, *centre(page.locator("li.habit:nth-child(1) button.day").nth(6).bounding_box()), touch)
                    page.wait_for_timeout(250)
                    after = snap(page)
                    ev = events(page)
                    dt = round(ev[-1]["t"] - ev[-2]["t"], 2)
                    ticked = after["pressed"] != before["pressed"]
                    expect = k >= 500
                    flag = "ok" if ticked == expect else "UNEXPECTED"
                    say(f"  {label} k={k:3d} (event dt {dt} ms): {'TICKED' if ticked else 'lost'} (expected {'tick' if expect else 'lost'}: {flag}); clicks: {fmt_clicks(ev[-2:])}")
                finally:
                    ctx.close()
    run.finish("probe_04")


if __name__ == "__main__":
    main()
