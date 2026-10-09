"""SEC-01 as fixed, part 2: hunting the fix with real mouse and touch input.

Families (each trial starts from the three-habit sample, reloaded):
  A  triple click / triple tap on the trash button at the overlap point (back to back, 100 ms apart)
  B  slow triple (260 ms apart): the third press is the first one past the 500 ms window
  C  double press on Cancel (what lies behind Cancel is measured), then a bead 300, 450 and 650 ms after one Cancel press
  D  Esc then an immediate click on a bead and on a trash button (a keyboard close must not hold the page)
  G  backdrop edge: 1 px inside, 1 px outside, drags between the box and the backdrop, a double click on the edge,
     a double click on the backdrop over a bead
  H  a deliberate Delete habit (after the window) pressed twice: the second press must do nothing
Real input only (page.mouse, page.touchscreen). An installed clock runs in real time. Nothing writes except the
JSON transcript saved by `run.finish`.
Run: PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python -B <this file>   (cwd = project root)
"""
from lib import Run, box, centre, double, events, fmt_clicks, geometry, open_app, press, reseed, snap, verdict

DESK = ("1440x900 mouse", (1440, 900), False)
PHONE = ("412x915 touch", (412, 915), True)
SMALLS = [("375x667 touch", (375, 667), True), ("360x640 touch", (360, 640), True)]
ALL = [DESK, PHONE] + SMALLS


def trash_c(page, row):
    return centre(page.locator(f"li.habit:nth-child({row}) .icon-btn").bounding_box())


def open_dialog(page, row, touch, wait=650):
    x, y = trash_c(page, row)
    press(page, x, y, touch)
    page.wait_for_selector("dialog[open]")
    if wait:
        page.wait_for_timeout(wait)


def behind(page, x, y):
    return page.evaluate(
        "([x, y]) => { const e = document.elementFromPoint(x, y); return e ? e.tagName.toLowerCase() + '.' + (typeof e.className === 'string' ? e.className : '') : null; }",
        [x, y])


def fam_a_b(run, say):
    say("== A/B: triple press at the overlap point ==")
    for label, vp, touch in (DESK, PHONE):
        g = geometry(run.browser, run.base, vp, touch)
        ov = g["overlap"]
        x, y = (ov[0] + ov[2]) / 2, (ov[1] + ov[3]) / 2
        ctx, page = open_app(run.browser, run.base, vp, touch)
        try:
            for name, gaps in (("A triple back to back", (0, 0)), ("A triple 100 ms apart", (100, 100)),
                               ("B slow triple 260 ms apart", (260, 260))):
                reseed(page)
                before = snap(page)
                for i, count in enumerate((1, 2, 3)):
                    press(page, x, y, touch, count)
                    if i < 2 and gaps[i]:
                        page.wait_for_timeout(gaps[i])
                page.wait_for_timeout(800)
                after = snap(page)
                say(f"  {label} {name}: {verdict(before, after)}")
                say(f"      clicks: {fmt_clicks(events(page))}")
        finally:
            ctx.close()


def fam_c(run, say):
    say("== C: double press on Cancel (dialog open 650 ms first) ==")
    for label, vp, touch in ALL:
        ctx, page = open_app(run.browser, run.base, vp, touch)
        try:
            for row in (1, 2, 3):
                reseed(page)
                before = snap(page)
                open_dialog(page, row, touch)
                cx, cy = centre(box(page, "dialog .btn-secondary"))
                double(page, cx, cy, touch, gap_ms=60 if touch else 0)
                page.wait_for_timeout(400)
                after = snap(page)
                under = behind(page, cx, cy)
                clean = after["pressed"] == before["pressed"] and len(after["names"]) == 3 and not after["open"]
                say(f"  {label} row {row}: Cancel at ({cx:.0f},{cy:.0f}), element behind it once closed: {under}; {verdict(before, after)}; closed with nothing ticked, deleted or reopened: {clean}")
                say(f"      clicks: {fmt_clicks(events(page))}")
        finally:
            ctx.close()
    say("  -- one Cancel press, then a bead after 300 / 450 / 650 ms (lost inside the window, must tick after it) --")
    for label, vp, touch in (DESK, PHONE, SMALLS[0]):
        ctx, page = open_app(run.browser, run.base, vp, touch)
        try:
            bead = page.locator("li.habit:nth-child(1) button.day").nth(6)
            for wait_ms in (300, 450, 650):
                reseed(page)
                before = snap(page)
                open_dialog(page, 2, touch)
                cx, cy = centre(box(page, "dialog .btn-secondary"))
                press(page, cx, cy, touch)
                page.wait_for_timeout(wait_ms)
                bx, by = centre(bead.bounding_box())
                press(page, bx, by, touch)
                page.wait_for_timeout(300)
                after = snap(page)
                ev = events(page)
                dt = round(ev[-1]["t"] - ev[-2]["t"], 1)
                ticked = after["pressed"] != before["pressed"]
                say(f"  {label} Cancel then bead after {wait_ms} ms (dt {dt} ms): {'TICKED' if ticked else 'lost'}; clicks: {fmt_clicks(ev[-2:])}")
        finally:
            ctx.close()


def fam_d(run, say):
    say("== D: Esc then an immediate click (a keyboard close holds nothing) ==")
    for label, vp, touch in (DESK, PHONE):
        ctx, page = open_app(run.browser, run.base, vp, touch)
        try:
            bead = page.locator("li.habit:nth-child(1) button.day").nth(6)
            reseed(page)
            before = snap(page)
            open_dialog(page, 3, touch, wait=0)
            page.keyboard.press("Escape")
            bx, by = centre(bead.bounding_box())
            press(page, bx, by, touch)
            page.wait_for_timeout(300)
            after = snap(page)
            say(f"  {label} click-open, Esc at once, bead right after: {'TICKED' if after['pressed'] != before['pressed'] else 'lost'}; {verdict(before, after)}; clicks: {fmt_clicks(events(page))}")
            reseed(page)
            open_dialog(page, 3, touch, wait=0)
            page.keyboard.press("Escape")
            x, y = trash_c(page, 2)
            press(page, x, y, touch)
            page.wait_for_timeout(300)
            after = snap(page)
            say(f"  {label} click-open, Esc at once, another trash right after: dialog open={after['open']}; title={page.locator('#del-title').text_content()!r}; clicks: {fmt_clicks(events(page))}")
        finally:
            ctx.close()


def fam_g(run, say):
    say("== G: backdrop edge and drags ==")
    for label, vp, touch in (DESK, PHONE):
        ctx, page = open_app(run.browser, run.base, vp, touch)
        try:
            reseed(page)
            open_dialog(page, 3, touch)
            dlg = box(page, "dialog")
            mid = dlg["y"] + dlg["height"] / 2
            say(f"  {label}: dialog box ({dlg['x']:.1f},{dlg['y']:.1f}) {dlg['width']:.1f}x{dlg['height']:.1f}")
            cases = [
                ("1 px inside the left edge", lambda: press(page, dlg["x"] + 1, mid, touch), "stay open"),
                ("1 px outside the left edge", lambda: press(page, dlg["x"] - 1, mid, touch), "close, keep"),
                ("double on 1 px inside the edge", lambda: double(page, dlg["x"] + 1, mid, touch, 60 if touch else 0), "stay open"),
                ("double 1 px outside the edge", lambda: double(page, dlg["x"] - 1, mid, touch, 60 if touch else 0), "close, keep"),
            ]
            for name, act, expect in cases:
                reseed(page)
                before = snap(page)
                open_dialog(page, 3, touch)
                act()
                page.wait_for_timeout(500)
                after = snap(page)
                say(f"    {name} (expect {expect}): {verdict(before, after)}")
            if not touch:
                for name, start, end in [
                    ("down inside (title), up on the backdrop", "title", "out"),
                    ("down on the backdrop, up on Delete habit", "out", "danger"),
                    ("down on the backdrop, up on Cancel", "out", "cancel"),
                    ("down on Delete habit, up on Cancel", "danger", "cancel"),
                    ("down on Cancel, up on Delete habit", "cancel", "danger"),
                    ("down on Delete habit, up on the backdrop", "danger", "out"),
                ]:
                    reseed(page)
                    before = snap(page)
                    open_dialog(page, 3, touch)
                    spots = {
                        "title": centre(box(page, "#del-title")),
                        "danger": centre(box(page, "dialog .btn-danger")),
                        "cancel": centre(box(page, "dialog .btn-secondary")),
                        "out": (box(page, "dialog")["x"] - 20, mid),
                    }
                    page.mouse.move(*spots[start])
                    page.mouse.down()
                    page.mouse.move(*spots[end], steps=4)
                    page.mouse.up()
                    page.wait_for_timeout(500)
                    after = snap(page)
                    say(f"    {name}: {verdict(before, after)}; clicks: {fmt_clicks(events(page)[-2:])}")
        finally:
            ctx.close()
    say("  -- double on the backdrop right over a bead (the dialog box does not cover it) --")
    for label, vp, touch in ALL:
        ctx, page = open_app(run.browser, run.base, vp, touch)
        try:
            reseed(page)
            beads = [(r, i, page.locator(f"li.habit:nth-child({r}) button.day").nth(i).bounding_box()) for r in (1, 2, 3) for i in range(7)]
            open_dialog(page, 3, touch)
            dlg = box(page, "dialog")
            chosen = None
            for r, i, b in beads:
                x, y = centre(b)
                inside = dlg["x"] <= x <= dlg["x"] + dlg["width"] and dlg["y"] <= y <= dlg["y"] + dlg["height"]
                if not inside and 0 < y < vp[1]:
                    chosen = (r, i, x, y)
                    if r == 2:
                        break
            r, i, x, y = chosen
            reseed(page)
            before = snap(page)
            open_dialog(page, 3, touch)
            double(page, x, y, touch, 60 if touch else 0)
            page.wait_for_timeout(500)
            after = snap(page)
            say(f"  {label}: bead row {r} #{i} at ({x:.0f},{y:.0f}) outside the box; {verdict(before, after)}; clicks: {fmt_clicks(events(page)[-2:])}")
        finally:
            ctx.close()


def fam_h(run, say):
    say("== H: a deliberate Delete habit (dialog open 650 ms), pressed twice ==")
    for label, vp, touch in ALL:
        ctx, page = open_app(run.browser, run.base, vp, touch)
        try:
            for row in (1, 2, 3):
                reseed(page)
                before = snap(page)
                open_dialog(page, row, touch)
                x, y = centre(box(page, "dialog .btn-danger"))
                double(page, x, y, touch, gap_ms=60 if touch else 0)
                page.wait_for_timeout(800)
                after = snap(page)
                gone = sorted(set(before["names"]) - set(after["names"]))
                under = behind(page, x, y)
                expected_pressed = [p for k, p in enumerate(before["pressed"]) if k != row - 1]
                ok = len(after["names"]) == 2 and gone == [before["names"][row - 1]] and not after["open"] and after["pressed"] == expected_pressed
                say(f"  {label} row {row}: deleted {gone}; under the pointer afterwards: {under}; no other change (ticks as before, no dialog): {ok}")
                say(f"      clicks: {fmt_clicks(events(page))}")
        finally:
            ctx.close()


def main():
    with Run() as run:
        say = run.say
        fam_a_b(run, say)
        fam_c(run, say)
        fam_d(run, say)
        fam_g(run, say)
        fam_h(run, say)
    run.finish("probe_02")


if __name__ == "__main__":
    main()
