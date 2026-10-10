"""Render check for round-1 direction A (Night Console).

Opens a.html by file:/// URL in headless Chromium, captures the key screen at 390, 360 and 1280,
every popup and dialog open, every prototype state, and prints the checks:
console errors, sideways scroll at 360, contrast ratios, touch target sizes, and the day-editor effect.
Every wait is bounded. The browser is closed in a finally block.
"""
import json
import pathlib
import sys

from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
PAGE = (HERE.parent.parent / "a.html").resolve()
URL = PAGE.as_uri()
SHOTS = HERE
TIMEOUT = 5000


def lum(hex_):
    h = hex_.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    rgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def ratio(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return round((hi + 0.05) / (lo + 0.05), 2)


PAIRS = [
    # (foreground var, background var, use, needed)
    ("--ink", "--bg-2", "body text on the page (habit names, typed text)", 4.5),
    ("--ink", "--bg-1", "text in the log pane and dock", 4.5),
    ("--ink", "--bg-0", "wordmark on the app bar", 4.5),
    ("--ink", "--bg-3", "Best value and text on chips and the composer", 4.5),
    ("--ink", "--raise", "dialog and day editor titles", 4.5),
    ("--ink-soft", "--bg-2", "secondary text (weekday labels, divider date)", 4.5),
    ("--ink-soft", "--bg-1", "legend, weekday header, 12-habit note", 4.5),
    ("--ink-soft", "--bg-3", "Best label, No streak yet, composer label", 4.5),
    ("--ink-soft", "--raise", "dialog body, day editor subtitle", 4.5),
    ("--accent", "--bg-2", "accent text on the page (holding Current badge)", 4.5),
    ("--accent", "--raise", "holding badge inside the day editor", 4.5),
    ("--accent-ink", "--accent", "text on the accent (live Current badge, Add, full heat day)", 4.5),
    ("--accent-ink", "--accent-hi", "Add on hover", 4.5),
    ("--ink", "--heat-1", "day number on heat level 1", 4.5),
    ("--ink", "--heat-2", "day number on heat level 2", 4.5),
    ("--ink", "--heat-3", "day number on heat level 3", 4.5),
    ("--danger", "--bg-1", "field error text in the dock", 4.5),
    ("--on-danger", "--danger-fill", "Delete habit", 4.5),
    ("--on-danger", "--danger-fill-hi", "Delete habit on hover", 4.5),
    ("--ink", "--warn-wash", "save warning text", 4.5),
    ("--accent", "--bg-1", "graphic: focus ring, level bars, mark (3:1)", 3.0),
    ("--accent", "--heat-3", "graphic: level bar on heat level 3 (3:1)", 3.0),
    ("--accent", "--bg-2", "graphic: done tile, focus ring (3:1)", 3.0),
    ("--edge", "--bg-2", "graphic: open day tile edge (3:1)", 3.0),
    ("--edge", "--bg-1", "graphic: empty heat cell edge (3:1)", 3.0),
    ("--accent", "--brand-chip", "graphic: mark on its chip (3:1)", 3.0),
    ("--warn", "--warn-wash", "graphic: save warning edge (3:1)", 3.0),
]


def main():
    out = {"url": URL, "console_errors": [], "checks": {}, "contrast": [], "shots": []}
    errors = out["console_errors"]

    def shot(page, name, full=False):
        path = SHOTS / name
        if full:
            # Grow the viewport to the page height so the fixed dock lands at the real bottom.
            vp = page.viewport_size
            h = page.evaluate("() => document.documentElement.scrollHeight")
            page.set_viewport_size({"width": vp["width"], "height": h})
            page.wait_for_timeout(150)
            page.screenshot(path=str(path))
            page.set_viewport_size(vp)
            page.wait_for_timeout(100)
        else:
            page.screenshot(path=str(path))
        out["shots"].append(str(path))

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            def new_page(w, h):
                ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1)
                pg = ctx.new_page()
                pg.set_default_timeout(TIMEOUT)
                pg.on("console", lambda m: errors.append(f"{w}px console: {m.text}") if m.type == "error" else None)
                pg.on("pageerror", lambda e: errors.append(f"{w}px pageerror: {e}"))
                pg.goto(URL, wait_until="load", timeout=TIMEOUT)
                pg.wait_for_selector(".habit", timeout=TIMEOUT)
                return ctx, pg

            # ---------- 390 x 844 ----------
            ctx, pg = new_page(390, 844)
            shot(pg, "k1-390.png")
            shot(pg, "k1-390-full.png", full=True)

            # contrast from the live :root tokens
            names = sorted({a for a, _, _, _ in PAIRS} | {b for _, b, _, _ in PAIRS})
            vals = pg.evaluate("(ns) => { const cs = getComputedStyle(document.documentElement); "
                               "return Object.fromEntries(ns.map(n => [n, cs.getPropertyValue(n).trim()])); }", names)
            # --heat-4 / --focus are var() references, resolve the ones we use by hand if needed
            for fg, bg, use, need in PAIRS:
                f, b = vals[fg], vals[bg]
                r = ratio(f, b)
                out["contrast"].append({"fg": f"{fg} {f}", "bg": f"{bg} {b}", "ratio": r, "need": need,
                                        "pass": r >= need, "use": use})

            # streak numbers shown in K1
            out["checks"]["k1_badges"] = pg.evaluate(
                "() => [...document.querySelectorAll('.habit')].map(li => li.querySelector('.h-name').textContent + ' | ' + "
                "li.querySelector('.cur').textContent.trim() + ' | ' + li.querySelector('.best').textContent.trim())")

            # touch targets at 390
            out["checks"]["targets_390"] = pg.evaluate("""() => {
                const m = s => [...document.querySelectorAll(s)].map(e => e.getBoundingClientRect()).filter(r => r.width > 0)
                  .reduce((a, r) => ({w: Math.min(a.w, r.width), h: Math.min(a.h, r.height)}), {w: 1e9, h: 1e9});
                return {day: m('.day'), dayTile: m('.day .tile'), cell: m('button.cell'), iconBtn: m('.icon-btn'), add: m('#add-btn'), input: m('#new-habit')};
            }""")

            # ticking today on the strip changes streak and heatmap
            before = pg.evaluate("() => ({cur: document.querySelectorAll('.habit')[1].querySelector('.cur').textContent.trim(),"
                                 " heat: document.querySelector('.cell[data-key=\"2026-10-10\"]').className})")
            pg.locator(".habit").nth(1).locator(".day.today").click()
            pg.wait_for_timeout(350)
            after = pg.evaluate("() => ({cur: document.querySelectorAll('.habit')[1].querySelector('.cur').textContent.trim(),"
                                " heat: document.querySelector('.cell[data-key=\"2026-10-10\"]').className})")
            out["checks"]["strip_tick_today_stretch"] = {"before": before, "after": after}
            shot(pg, "k1-390-after-strip-tick.png")
            pg.locator(".habit").nth(1).locator(".day.today").click()  # undo
            pg.wait_for_timeout(250)

            # P1 day editor (bottom sheet) from the 22 Sep cell
            cell = pg.locator('.cell[data-key="2026-09-22"]')
            cell.scroll_into_view_if_needed()
            pre = pg.evaluate("() => ({cell: document.querySelector('.cell[data-key=\"2026-09-22\"]').className,"
                              " best: document.querySelectorAll('.habit')[1].querySelector('.best').textContent.trim()})")
            cell.click()
            pg.wait_for_selector("#day-dlg[open]", timeout=TIMEOUT)
            pg.wait_for_timeout(300)
            out["checks"]["p1_title"] = pg.inner_text("#day-title")
            shot(pg, "p1-390.png")
            pg.locator(".day-row").nth(1).click()
            pg.wait_for_timeout(350)
            shot(pg, "p1-390-after-tick.png")
            post = pg.evaluate("() => ({cell: document.querySelector('.cell[data-key=\"2026-09-22\"]').className,"
                               " best: document.querySelectorAll('.habit')[1].querySelector('.best').textContent.trim(),"
                               " sub: document.querySelector('#day-sub').textContent})")
            out["checks"]["p1_tick_stretch_22sep"] = {"before": pre, "after": post}
            pg.keyboard.press("Escape")
            pg.wait_for_timeout(250)
            out["checks"]["p1_esc_closes"] = not pg.evaluate("() => document.querySelector('#day-dlg').open")
            # backdrop close
            cell.click()
            pg.wait_for_selector("#day-dlg[open]", timeout=TIMEOUT)
            pg.mouse.click(10, 60)
            pg.wait_for_timeout(250)
            out["checks"]["p1_backdrop_closes"] = not pg.evaluate("() => document.querySelector('#day-dlg').open")
            out["checks"]["future_cell_is_button"] = pg.evaluate(
                "() => !!document.querySelector('.cal button.cell.future') || document.querySelectorAll('.cal .cell.future').length !== 1")
            # today cell opens too
            pg.locator('.cell[data-key="2026-10-10"]').click()
            pg.wait_for_selector("#day-dlg[open]", timeout=TIMEOUT)
            out["checks"]["p1_today_title"] = pg.inner_text("#day-title")
            pg.keyboard.press("Escape")
            pg.wait_for_timeout(200)

            # M1 delete dialog
            pg.evaluate("() => window.scrollTo(0, 0)")
            pg.locator(".habit").nth(1).locator(".trash").click()
            pg.wait_for_selector("#del-dlg[open]", timeout=TIMEOUT)
            pg.wait_for_timeout(300)
            out["checks"]["m1_title"] = pg.inner_text("#del-title")
            shot(pg, "m1-390.png")
            pg.keyboard.press("Escape")
            pg.wait_for_timeout(200)
            out["checks"]["m1_esc_closes"] = not pg.evaluate("() => document.querySelector('#del-dlg').open")
            pg.locator(".habit").nth(1).locator(".trash").click()
            pg.wait_for_selector("#del-dlg[open]", timeout=TIMEOUT)
            pg.mouse.click(10, 820)
            pg.wait_for_timeout(200)
            out["checks"]["m1_backdrop_closes"] = not pg.evaluate("() => document.querySelector('#del-dlg').open")
            pg.locator(".habit").nth(1).locator(".trash").click()
            pg.click("#del-confirm")
            pg.wait_for_timeout(200)
            out["checks"]["m1_delete_removes"] = pg.evaluate("() => document.querySelectorAll('.habit').length")

            # prototype states
            pg.click(".proto-toggle")
            pg.wait_for_timeout(150)
            shot(pg, "proto-menu-390.png")
            for state in ["s1", "s2-empty", "s2-long", "s2-dup", "s3", "s4", "s5"]:
                pg.evaluate(f"() => window.__proto.setState('{state}')")
                pg.wait_for_timeout(200)
                shot(pg, f"{state}-390.png")
                if state == "s3":
                    shot(pg, "s3-390-full.png", full=True)
            out["checks"]["s1_cells_interactive"] = pg.evaluate("() => (window.__proto.setState('s1'), document.querySelectorAll('.cal button.cell').length)")
            ctx.close()

            # ---------- 360 x 780 ----------
            ctx, pg = new_page(360, 780)
            shot(pg, "k1-360.png")
            shot(pg, "k1-360-full.png", full=True)
            out["checks"]["scroll_360"] = pg.evaluate(
                "() => ({scrollWidth: document.documentElement.scrollWidth, clientWidth: document.documentElement.clientWidth,"
                " sideways: document.documentElement.scrollWidth > document.documentElement.clientWidth})")
            out["checks"]["targets_360"] = pg.evaluate("""() => {
                const m = s => [...document.querySelectorAll(s)].map(e => e.getBoundingClientRect()).filter(r => r.width > 0)
                  .reduce((a, r) => ({w: Math.min(a.w, r.width), h: Math.min(a.h, r.height)}), {w: 1e9, h: 1e9});
                return {day: m('.day'), dayTile: m('.day .tile'), cell: m('button.cell'), iconBtn: m('.icon-btn'), add: m('#add-btn')};
            }""")
            for state in ["s2-long", "s3", "s5"]:
                pg.evaluate(f"() => window.__proto.setState('{state}')")
                pg.wait_for_timeout(150)
                sw = pg.evaluate("() => document.documentElement.scrollWidth > document.documentElement.clientWidth")
                out["checks"][f"scroll_360_{state}"] = sw
            pg.evaluate("() => window.__proto.setState('k1')")
            pg.evaluate("() => window.__proto.openDay('2026-09-22')")
            pg.wait_for_timeout(300)
            shot(pg, "p1-360.png")
            ctx.close()

            # ---------- 1280 x 800 ----------
            ctx, pg = new_page(1280, 800)
            shot(pg, "k1-1280.png")
            out["checks"]["scroll_1280"] = pg.evaluate("() => document.documentElement.scrollWidth > document.documentElement.clientWidth")
            pg.locator('.cell[data-key="2026-09-22"]').click()
            pg.wait_for_selector("#day-dlg[open]", timeout=TIMEOUT)
            pg.wait_for_timeout(300)
            shot(pg, "p1-1280.png")
            pg.locator(".day-row").nth(1).click()
            pg.wait_for_timeout(350)
            shot(pg, "p1-1280-after-tick.png")
            pg.mouse.click(400, 700)
            pg.wait_for_timeout(250)
            out["checks"]["p1_1280_backdrop_closes"] = not pg.evaluate("() => document.querySelector('#day-dlg').open")
            pg.locator(".habit").nth(1).locator(".trash").click()
            pg.wait_for_selector("#del-dlg[open]", timeout=TIMEOUT)
            pg.wait_for_timeout(300)
            shot(pg, "m1-1280.png")
            pg.keyboard.press("Escape")
            pg.wait_for_timeout(200)
            for state in ["s1", "s2-dup", "s3", "s4", "s5"]:
                pg.evaluate(f"() => window.__proto.setState('{state}')")
                pg.wait_for_timeout(200)
                shot(pg, f"{state}-1280.png")
            # keyboard focus ring visible
            pg.evaluate("() => window.__proto.setState('k1')")
            pg.keyboard.press("Tab")
            pg.keyboard.press("Tab")
            pg.keyboard.press("Tab")
            pg.wait_for_timeout(150)
            shot(pg, "focus-1280.png")
            out["checks"]["focus_outline"] = pg.evaluate(
                "() => { const e = document.activeElement; const cs = getComputedStyle(e); return e.className + ' ' + cs.outlineStyle + ' ' + cs.outlineWidth + ' ' + cs.outlineColor; }")
            ctx.close()

            # ---------- reduced motion ----------
            ctx = browser.new_context(viewport={"width": 390, "height": 844}, reduced_motion="reduce")
            pg = ctx.new_page()
            pg.set_default_timeout(TIMEOUT)
            pg.goto(URL, wait_until="load", timeout=TIMEOUT)
            out["checks"]["reduced_motion_tile_transition"] = pg.evaluate(
                "() => getComputedStyle(document.querySelector('.tile')).transitionDuration")
            ctx.close()
        finally:
            browser.close()

    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
