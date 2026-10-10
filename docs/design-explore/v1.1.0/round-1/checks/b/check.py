"""Render check for round-1 direction B (Neon Thread).

Opens b.html by its file:/// URL in headless Chromium at 390x844, 360x780 and 1280x800, screenshots the key screen,
every popup and dialog and every prototype state, and records console errors, external requests, sideways scroll,
touch target sizes, the computed streak numbers and the contrast ratios of the tokens.
Every wait is bounded and the browser is closed in a finally block.
"""
import json
import pathlib
import sys

from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
HTML = HERE.parent.parent / "b.html"
URL = HTML.as_uri()
TIMEOUT = 5000

results = {
    "url": URL,
    "console_errors": [],
    "external_requests": [],
    "sideways_scroll": {},
    "streaks": {},
    "flows": {},
    "targets": {},
    "contrast": {},
    "reduced_motion": {},
    "screenshots": [],
}


def lum(hex_colour):
    h = hex_colour.strip().lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))

    def ch(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def ratio(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return round((hi + 0.05) / (lo + 0.05), 2)


def watch(page, tag):
    page.on("console", lambda m: results["console_errors"].append(f"{tag}: {m.text}") if m.type == "error" else None)
    page.on("pageerror", lambda e: results["console_errors"].append(f"{tag}: pageerror {e}"))
    page.on("request", lambda r: results["external_requests"].append(r.url)
            if not r.url.startswith(("file:", "data:", "about:")) else None)


def shot(page, name, full=False):
    path = HERE / name
    page.screenshot(path=str(path), full_page=full, timeout=TIMEOUT)
    results["screenshots"].append(str(path))


def sideways(page):
    # Compare against the body's laid-out width, which excludes a reserved scrollbar gutter. The root's clientWidth
    # can include that gutter and hide a small overflow. Also flag any visible element whose right edge passes it.
    return page.evaluate("""() => {
        const w = Math.ceil(document.body.getBoundingClientRect().width);
        if (Math.ceil(document.documentElement.scrollWidth) > w) return true;
        for (const e of document.querySelectorAll('body *')) {
            if (e.closest('dialog:not([open])') || e.closest('.proto')) continue;
            const r = e.getBoundingClientRect();
            if (r.width && r.right > w + 0.5) return e.tagName + '.' + e.className;
        }
        return false;
    }""")


def streak_texts(page):
    return page.eval_on_selector_all(".habit", "els => els.map(e => e.querySelector('.habit-name').textContent + ' | ' + e.querySelector('.streak').innerText.replace(/\\s+/g, ' ').trim())")


def proto(page, state):
    page.click("#proto-toggle", timeout=TIMEOUT)
    page.click(f'[data-state="{state}"]', timeout=TIMEOUT)
    page.wait_for_timeout(150)


def fresh(page):
    page.goto(URL, wait_until="load", timeout=TIMEOUT)
    page.wait_for_selector(".habit", timeout=TIMEOUT)


def sizes(page, selector):
    return page.eval_on_selector_all(selector, "els => { const r = els.map(e => e.getBoundingClientRect()); return r.length ? {count: r.length, minW: Math.min(...r.map(x => x.width)).toFixed(1), minH: Math.min(...r.map(x => x.height)).toFixed(1)} : null }")


def run_phone(browser, w, h, tag):
    ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=2)
    try:
        page = ctx.new_page()
        page.set_default_timeout(TIMEOUT)
        watch(page, tag)
        fresh(page)
        shot(page, f"k1-{w}.png")
        shot(page, f"k1-{w}-full.png", full=True)
        results["sideways_scroll"][f"k1-{w}"] = sideways(page)
        results["streaks"][f"k1-{w}"] = streak_texts(page)
        results["targets"][f"{w}"] = {
            "strip day": sizes(page, ".rail .day"),
            "heatmap day": sizes(page, "button.hm-cell"),
            "icon button (bins)": sizes(page, ".habit .icon-btn"),
            "input": sizes(page, "#new-habit"),
            "add button": sizes(page, "#add-btn"),
        }

        # strip tick: No phone after 11pm, yesterday (Fri 9 Oct)
        page.click('.habit[data-id="h3"] .day[data-key="2026-10-09"]')
        page.wait_for_timeout(500)
        results["flows"][f"strip tick {w}"] = streak_texts(page)[2]
        if w == 390:
            page.locator('.habit[data-id="h3"]').scroll_into_view_if_needed()
            shot(page, f"k1-{w}-after-strip-tick.png")
        page.click('.habit[data-id="h3"] .day[data-key="2026-10-09"]')

        # P1: open Tue 22 Sep from the starfield
        fresh(page)
        page.locator('[data-key="2026-09-22"]').scroll_into_view_if_needed()
        page.click('button.hm-cell[data-key="2026-09-22"]')
        page.wait_for_selector("#editor[open]", timeout=TIMEOUT)
        page.wait_for_timeout(400)
        p1 = {"title": page.inner_text("#ed-title"), "count": page.inner_text("#ed-count"),
              "edited star visible above the sheet": page.evaluate("""() => {
                  const c = document.querySelector('#hm [data-key="2026-09-22"]').getBoundingClientRect();
                  const s = document.getElementById('editor').getBoundingClientRect();
                  return c.top >= 0 && c.bottom <= s.top; }"""),
              "close button": sizes(page, "#ed-close"),
              "editor rows": sizes(page, ".ed-row")}
        shot(page, f"p1-{w}.png")
        results["sideways_scroll"][f"p1-{w}"] = sideways(page)
        page.click('.ed-row[data-id="h1"]')
        page.wait_for_timeout(600)
        p1["after tick count"] = page.inner_text("#ed-count")
        p1["after tick Read row"] = page.inner_text('.ed-row[data-id="h1"]').replace("\n", " ")
        p1["after tick heat label"] = page.get_attribute('button.hm-cell[data-key="2026-09-22"]', "aria-label")
        p1["after tick list"] = streak_texts(page)[0]
        shot(page, f"p1-{w}-after-tick.png")
        page.keyboard.press("Escape")
        page.wait_for_timeout(200)
        p1["closed by Esc"] = not page.evaluate("document.getElementById('editor').open")
        p1["focus back on cell"] = page.evaluate("document.activeElement && document.activeElement.dataset.key")
        page.click('button.hm-cell[data-key="2026-10-01"]')
        page.wait_for_selector("#editor[open]", timeout=TIMEOUT)
        p1["title 1 Oct"] = page.inner_text("#ed-title")
        page.mouse.click(10, 10)
        page.wait_for_timeout(200)
        p1["closed by backdrop"] = not page.evaluate("document.getElementById('editor').open")
        p1["future cell is a button"] = page.locator('button.hm-cell[data-key="2026-10-11"]').count() > 0
        p1["future cells"] = page.locator(".hm-cell.is-future").count()
        results["flows"][f"p1 {w}"] = p1

        # M1: delete Stretch 10 minutes
        fresh(page)
        page.click('[data-del="h2"]')
        page.wait_for_selector("#confirm[open]", timeout=TIMEOUT)
        page.wait_for_timeout(300)
        m1 = {"title": page.inner_text("#cf-title"), "body": page.inner_text("#cf-body"),
              "focus": page.evaluate("document.activeElement.id")}
        shot(page, f"m1-{w}.png")
        results["sideways_scroll"][f"m1-{w}"] = sideways(page)
        page.keyboard.press("Escape")
        page.wait_for_timeout(200)
        m1["closed by Esc"] = not page.evaluate("document.getElementById('confirm').open")
        m1["focus back on bin"] = page.evaluate("document.activeElement.dataset.del")
        page.click('[data-del="h2"]')
        page.wait_for_selector("#confirm[open]", timeout=TIMEOUT)
        page.mouse.click(10, 10)
        page.wait_for_timeout(200)
        m1["closed by backdrop"] = not page.evaluate("document.getElementById('confirm').open")
        page.click('[data-del="h2"]')
        page.wait_for_selector("#confirm[open]", timeout=TIMEOUT)
        page.click("#cf-delete")
        page.wait_for_timeout(200)
        m1["habits after delete"] = page.eval_on_selector_all(".habit-name", "els => els.map(e => e.textContent)")
        results["flows"][f"m1 {w}"] = m1

        # prototype states
        fresh(page)
        page.click("#proto-toggle")
        if w == 390:
            shot(page, f"proto-menu-{w}.png")
        page.click("#proto-toggle")
        states = {}
        for state in ["s1", "s2-empty", "s2-long", "s2-dup", "s3", "s4", "s5"]:
            proto(page, state)
            states[state] = {
                "message": page.inner_text("#new-habit-msg") if page.is_visible("#new-habit-msg") else "",
                "banner": page.inner_text("#banner") if page.is_visible("#banner") else "",
                "empty": page.inner_text("#empty") if page.is_visible("#empty") else "",
                "habits": page.locator(".habit").count(),
                "input disabled": page.is_disabled("#new-habit"),
                "add disabled": page.is_disabled("#add-btn"),
                "heat buttons": page.locator("button.hm-cell").count(),
            }
            results["sideways_scroll"][f"{state}-{w}"] = sideways(page)
            if w == 390 or state in ("s1", "s3"):
                shot(page, f"{state}-{w}.png")
        results["flows"][f"states {w}"] = states

        # tokens and contrast, read from the page itself
        if w == 390:
            tokens = page.evaluate("""() => { const s = getComputedStyle(document.documentElement);
                const names = ['--bg','--well','--surface','--surface-hi','--line','--ring','--ink','--ink-soft','--aqua','--aqua-hi','--on-aqua',
                               '--star-1','--star-2','--star-3','--danger','--danger-hi','--on-danger'];
                return Object.fromEntries(names.map(n => [n, s.getPropertyValue(n).trim()])); }""")
            t = tokens
            results["tokens"] = tokens
            pairs = {
                "body text --ink on --bg": (t["--ink"], t["--bg"]),
                "body text --ink on --surface (dialogs)": (t["--ink"], t["--surface"]),
                "secondary --ink-soft on --bg": (t["--ink-soft"], t["--bg"]),
                "secondary --ink-soft on --well (rail, starfield)": (t["--ink-soft"], t["--well"]),
                "secondary --ink-soft on --surface (dialog body)": (t["--ink-soft"], t["--surface"]),
                "accent --aqua on --bg (current streak text)": (t["--aqua"], t["--bg"]),
                "accent --aqua on --well (done node, trail)": (t["--aqua"], t["--well"]),
                "accent --aqua on --surface (done node in editor)": (t["--aqua"], t["--surface"]),
                "--on-aqua on --aqua (check mark, Add text)": (t["--on-aqua"], t["--aqua"]),
                "--on-aqua on --aqua-hi (Add hover)": (t["--on-aqua"], t["--aqua-hi"]),
                "--ring on --well (not-done node, empty star)": (t["--ring"], t["--well"]),
                "--ring on --bg (input border)": (t["--ring"], t["--bg"]),
                "--ring on --surface (Cancel border, empty node in editor)": (t["--ring"], t["--surface"]),
                "--star-1 on --well": (t["--star-1"], t["--well"]),
                "--star-2 on --well": (t["--star-2"], t["--well"]),
                "--star-3 on --well": (t["--star-3"], t["--well"]),
                "--star-4 (= aqua) on --well": (t["--aqua"], t["--well"]),
                "--danger on --bg (field error)": (t["--danger"], t["--bg"]),
                "--danger on --surface (save warning edge)": (t["--danger"], t["--surface"]),
                "--on-danger on --danger (Delete habit)": (t["--on-danger"], t["--danger"]),
                "--on-danger on --danger-hi (Delete habit hover)": (t["--on-danger"], t["--danger-hi"]),
                "--ink-soft on --surface (disabled Add text)": (t["--ink-soft"], t["--surface"]),
                "focus ring --ink on --well": (t["--ink"], t["--well"]),
                "--ink on --surface-hi (hover rows, tooltip)": (t["--ink"], t["--surface-hi"]),
            }
            results["contrast"] = {k: ratio(*v) for k, v in pairs.items()}
    finally:
        ctx.close()


def run_desktop(browser):
    w, h = 1280, 800
    ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1)
    try:
        page = ctx.new_page()
        page.set_default_timeout(TIMEOUT)
        watch(page, "1280")
        fresh(page)
        shot(page, "k1-1280.png")
        results["sideways_scroll"]["k1-1280"] = sideways(page)
        results["streaks"]["k1-1280"] = streak_texts(page)
        results["targets"]["1280"] = {"strip day": sizes(page, ".rail .day"), "heatmap day": sizes(page, "button.hm-cell")}
        sky = page.eval_on_selector("#sky", "e => { const r = e.getBoundingClientRect(); return {top: r.top, bottom: r.bottom} }")
        results["flows"]["starfield fits 800 high"] = sky

        # hover tooltip on a star
        page.hover('button.hm-cell[data-key="2026-09-22"]')
        page.wait_for_timeout(250)
        shot(page, "k1-1280-hover-tip.png")

        page.click('button.hm-cell[data-key="2026-09-22"]')
        page.wait_for_selector("#editor[open]", timeout=TIMEOUT)
        page.wait_for_timeout(400)
        shot(page, "p1-1280.png")
        page.click('.ed-row[data-id="h1"]')
        page.wait_for_timeout(600)
        results["flows"]["p1 1280 after tick"] = {"count": page.inner_text("#ed-count"), "list": streak_texts(page)[0]}
        shot(page, "p1-1280-after-tick.png")
        page.keyboard.press("Escape")
        page.wait_for_timeout(200)

        fresh(page)
        page.click('[data-del="h2"]')
        page.wait_for_selector("#confirm[open]", timeout=TIMEOUT)
        page.wait_for_timeout(300)
        shot(page, "m1-1280.png")
        page.keyboard.press("Escape")

        for state in ["s1", "s3", "s4", "s5", "s2-dup"]:
            proto(page, state)
            results["sideways_scroll"][f"{state}-1280"] = sideways(page)
            shot(page, f"{state}-1280.png")

        # keyboard focus on a strip node
        fresh(page)
        page.focus('.habit[data-id="h2"] .day[data-key="2026-10-09"]')
        page.keyboard.press("Tab")
        page.keyboard.press("Shift+Tab")
        page.wait_for_timeout(150)
        results["flows"]["focus visible on node"] = page.evaluate("document.activeElement.matches(':focus-visible') && getComputedStyle(document.activeElement).outlineStyle")
        shot(page, "focus-1280.png")
    finally:
        ctx.close()


def run_reduced(browser):
    ctx = browser.new_context(viewport={"width": 390, "height": 844}, reduced_motion="reduce")
    try:
        page = ctx.new_page()
        page.set_default_timeout(TIMEOUT)
        watch(page, "reduced")
        fresh(page)
        page.click('.habit[data-id="h2"] .day[data-key="2026-10-10"]')
        results["reduced_motion"] = page.evaluate("""() => { const n = document.querySelector('.habit[data-id="h2"] .day[data-key="2026-10-10"] .node');
            const s = getComputedStyle(n); return {nodeAnimation: s.animationName, nodeTransition: s.transitionDuration,
            ignited: n.classList.contains('ignite')}; }""")
    finally:
        ctx.close()


def main():
    with sync_playwright() as p:
        browser = None
        try:
            browser = p.chromium.launch(headless=True, timeout=30000)
            run_phone(browser, 390, 844, "390")
            run_phone(browser, 360, 780, "360")
            run_desktop(browser)
            run_reduced(browser)
        finally:
            if browser:
                browser.close()
    results["summary"] = {
        "console errors": len(results["console_errors"]),
        "external requests": len(results["external_requests"]),
        "sideways scroll anywhere at 360": any(v for k, v in results["sideways_scroll"].items() if k.endswith("-360")),
        "sideways scroll anywhere": any(results["sideways_scroll"].values()),
    }
    print(json.dumps(results, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
