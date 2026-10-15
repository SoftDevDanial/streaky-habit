"""T7 (v1.1.0 changed), R13 and R14. The time-free guard of Delete habit, measured with real pointer input.

Part 1  Geometry. For 8 viewports and each visible row of 12 habits, the overlap of the bin (the opener) with M1's
        Delete habit, and of P2's Delete habit (the opener over P2) with M1's Delete habit.
Part 2  Gestures at an overlap point (or at the opener's centre where there is none): mouse double click, touch
        double tap, a slow second click 700 ms later (two separate clicks, detail 1 each), a triple click. Nothing
        may be deleted. Controls: a single click at that point only opens M1, a click on Delete habit outside the
        opener's box deletes, Enter on Delete habit deletes.
Usage: python -B probe_07_delete_guard.py [chromium] [webkit]
"""
import json
import time

from playwright.sync_api import sync_playwright

import conftest
import lib

NOON = "2026-10-10T12:00:00+08:00"
NAMES = [f"Habit {i}" for i in range(1, 13)]
STATE = lib.encode([{"name": n, "done": ["2026-10-10"]} for n in NAMES])
VIEWPORTS = [(360, 780), (390, 844), (412, 915), (768, 1024), (1024, 768), (1280, 800), (1440, 900), (1920, 1080)]
CLOSE_LOGGER = "document.addEventListener('close', (e) => console.log('closed:' + e.target.className), true);"


def rect(page, selector):
    return page.evaluate("(s) => { const r = document.querySelector(s).getBoundingClientRect(); return [r.left, r.top, r.right, r.bottom]; }", selector)


def overlap(a, b):
    x0, y0, x1, y1 = max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])
    return [x0, y0, x1, y1] if x1 - x0 >= 2 and y1 - y0 >= 2 else None


def esc_wait(s):
    n = sum(1 for c in s.console if c.startswith("log: closed:"))
    s.page.keyboard.press("Escape")
    deadline = time.time() + 5
    while sum(1 for c in s.console if c.startswith("log: closed:")) == n:
        if time.time() > deadline:
            raise RuntimeError("close not seen, gave up after 5 s")
        s.page.wait_for_timeout(20)


def geometry(browser, base, viewport):
    s = lib.Session(browser, base, viewport=viewport, seed_js=lib.SEED_TEXT, seed_arg=STATE, clock=NOON, init=[CLOSE_LOGGER], route_log=False)
    found = {"bin": None, "p2": None}
    try:
        page = s.page
        frame = rect(page, "div.frame")
        for i in range(1, 13):
            sel = f"ul.rows > li.row:nth-child({i}) button.btn-bin"
            box = rect(page, sel)
            if box[1] < frame[1] or box[3] > frame[3]:
                continue
            page.locator(sel).focus()
            page.keyboard.press("Enter")
            o = overlap(box, rect(page, "dialog.dlg-del button.btn-danger"))
            esc_wait(s)
            if o and not found["bin"]:
                found["bin"] = {"row": i, "opener": [round(v) for v in box], "overlap": [round(v) for v in o]}
        page.locator("ul.rows > li.row:nth-child(1) button.btn-year").focus()
        page.keyboard.press("Enter")
        box = rect(page, "dialog.dlg-year button.btn-del")
        page.locator("dialog.dlg-year button.btn-del").focus()
        page.keyboard.press("Enter")
        o = overlap(box, rect(page, "dialog.dlg-del button.btn-danger"))
        found["p2"] = {"opener": [round(v) for v in box], "overlap": [round(v) for v in o] if o else None}
    finally:
        s.close()
    return found


def gesture(browser, base, viewport, opener_kind, row, point, how):
    touch = how == "tap"
    s = lib.Session(browser, base, viewport=viewport, seed_js=lib.SEED_TEXT, seed_arg=STATE, clock=NOON, init=[CLOSE_LOGGER], route_log=False, touch=touch)
    try:
        page = s.page
        x, y = point
        if opener_kind == "p2":
            page.locator(f"ul.rows > li.row:nth-child({row}) button.btn-year").focus()
            page.keyboard.press("Enter")
        if how == "dblclick":
            page.mouse.dblclick(x, y)
        elif how == "tap":
            page.touchscreen.tap(x, y)
            page.touchscreen.tap(x, y)
        elif how == "slow":
            page.mouse.click(x, y)
            page.wait_for_timeout(700)
            page.mouse.click(x, y)
        elif how == "triple":
            page.mouse.click(x, y, click_count=3)
        elif how == "single":
            page.mouse.click(x, y)
        elif how in ("outside", "enter"):
            page.mouse.click(x, y)
            page.wait_for_timeout(600)  # past the R14 page guard, which a pointer click inside M1 does not start anyway
            if how == "outside":
                opener = rect(page, f"ul.rows > li.row:nth-child({row}) button.btn-bin") if opener_kind == "bin" else None
                target = page.locator("dialog.dlg-del button.btn-danger")
                if opener_kind == "bin":
                    tx, ty = conftest.point_beside(target, page.locator(f"ul.rows > li.row:nth-child({row}) button.btn-bin"))
                else:
                    tx, ty = conftest.point_beside(target, page.locator("dialog.dlg-year button.btn-del"))
                page.mouse.click(tx, ty)
            else:
                page.locator("dialog.dlg-del button.btn-danger").focus()
                page.keyboard.press("Enter")
        page.wait_for_timeout(200)
        left = [h["name"] for h in json.loads(s.stored())["habits"]]
        m1_open = page.evaluate("() => document.querySelector('dialog.dlg-del').open")
        return {"deleted": [n for n in NAMES if n not in left], "m1_open": m1_open, "errors": s.errors}
    finally:
        s.close()


def main():
    proc, port, _ = lib.start_server()
    try:
        base = f"http://127.0.0.1:{port}/"
        with sync_playwright() as p:
            for engine in lib.engines_from_argv():
                browser = lib.launch(p, engine)
                print("engine", engine, browser.version, flush=True)
                try:
                    for vp in VIEWPORTS:
                        g = geometry(browser, base, vp)
                        print(f"{vp[0]}x{vp[1]} geometry {json.dumps(g)}", flush=True)
                        for kind in ("bin", "p2"):
                            info = g[kind]
                            if kind == "bin" and not info:
                                continue
                            row = info.get("row", 1)
                            o = info["overlap"] or info["opener"]
                            point = ((o[0] + o[2]) / 2, (o[1] + o[3]) / 2)
                            results = {}
                            for how in ("single", "dblclick", "tap", "slow", "triple", "outside", "enter"):
                                results[how] = gesture(browser, base, vp, kind, row, point, how)
                            print(f"  {kind} at {[round(v) for v in point]} ({'overlap' if info['overlap'] else 'opener centre, no overlap'}): {json.dumps(results)}", flush=True)
                finally:
                    browser.close()
    finally:
        lib.stop_server(proc, port)


if __name__ == "__main__":
    main()
