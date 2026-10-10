"""Render check for round-1 direction D (Orbit Rings). Headless Chromium, file:/// URL, no server, no network."""
import json
import pathlib
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
PAGE = HERE.parent.parent / "d.html"
URL = PAGE.as_uri()
T = 5000  # every wait is bounded

results = {"console_errors": [], "page_errors": [], "requests_off_file": [], "checks": {}, "contrast": {}, "overflow_360": {}, "shots": []}


def lum(hexv):
    hexv = hexv.strip().lstrip("#")
    r, g, b = (int(hexv[i:i + 2], 16) / 255 for i in (0, 2, 4))

    def ch(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def ratio(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return round((hi + 0.05) / (lo + 0.05), 2)


def shot(page, name, full=False):
    page.mouse.move(1, 1)  # no stray hover in the picture
    page.wait_for_timeout(150)
    path = HERE / name
    page.screenshot(path=str(path), full_page=full)
    results["shots"].append(str(path))


def text(page, sel):
    return page.locator(sel).first.inner_text(timeout=T).strip()


def card_numbers(page):
    out = {}
    for card in page.locator("li.habit").all():
        name = card.locator(".h-name").inner_text(timeout=T)
        core = card.locator(".core").inner_text(timeout=T).replace("\n", " ")
        best = card.locator(".best").inner_text(timeout=T).replace("\n", " ") if card.locator(".best").count() else ""
        out[name] = {"current": core, "best": best}
    return out


def overflow(page, width):
    return page.evaluate(
        """(w) => {
          const doc = document.documentElement;
          const bad = [];
          for (const el of document.querySelectorAll('body *')) {
            if (el.closest('dialog:not([open])') || el.closest('[hidden]')) continue;
            const r = el.getBoundingClientRect();
            if (r.width === 0 && r.height === 0) continue;
            if (r.right > w + 0.5 || r.left < -0.5) bad.push((el.className && el.className.baseVal !== undefined ? el.className.baseVal : el.className) + ' ' + el.tagName + ' ' + Math.round(r.left) + '..' + Math.round(r.right));
          }
          return { scrollWidth: doc.scrollWidth, clientWidth: doc.clientWidth, poking: bad.slice(0, 20) };
        }""",
        width,
    )


def set_state(page, state):
    page.click("#proto-tab", timeout=T)
    page.click(f'[data-state="{state}"]', timeout=T)
    page.wait_for_timeout(450)


def run_size(browser, w, h, tag, full_suite):
    ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1)
    page = ctx.new_page()
    page.on("console", lambda m: results["console_errors"].append(f"{tag}: {m.text}") if m.type == "error" else None)
    page.on("pageerror", lambda e: results["page_errors"].append(f"{tag}: {e}"))
    page.on("request", lambda r: results["requests_off_file"].append(r.url) if not r.url.startswith(("file:", "data:")) else None)
    page.goto(URL, timeout=T)
    page.wait_for_selector("li.habit", timeout=T)
    page.wait_for_timeout(600)
    shot(page, f"k1-{tag}.png")
    shot(page, f"k1-{tag}-full.png", full=True)
    results["checks"][f"k1-numbers-{tag}"] = card_numbers(page)
    results["checks"][f"title-{tag}"] = page.title()

    if w == 360:
        results["overflow_360"]["k1"] = overflow(page, w)

    # strip tick: today on Stretch 10 minutes
    if full_suite:
        page.click('li.habit:nth-child(2) .node.today', timeout=T)
        page.wait_for_timeout(500)
        results["checks"][f"after-strip-tick-{tag}"] = card_numbers(page)["Stretch 10 minutes"]
        results["checks"][f"today-cell-after-strip-{tag}"] = page.get_attribute('[data-key="2026-10-10"].hc', "aria-label", timeout=T)
        shot(page, f"k1-{tag}-after-strip-tick.png")
        page.click('li.habit:nth-child(2) .node.today', timeout=T)  # undo
        page.wait_for_timeout(300)

    # P1: open Tuesday 22 September from the grid
    cell = page.locator('button.hc[data-key="2026-09-22"]')
    cell.scroll_into_view_if_needed(timeout=T)
    cell.click(timeout=T)
    page.wait_for_selector("#day-dlg[open]", timeout=T)
    page.wait_for_timeout(400)
    results["checks"][f"p1-title-{tag}"] = text(page, "#day-title")
    results["checks"][f"p1-cell-label-before-{tag}"] = cell.get_attribute("aria-label")
    shot(page, f"p1-{tag}.png")
    page.click('#day-list .tick[data-hid]:has-text("Read 20 pages")', timeout=T)
    page.wait_for_timeout(450)
    results["checks"][f"p1-after-tick-row-{tag}"] = text(page, "#day-list li:first-child .tstat")
    shot(page, f"p1-{tag}-after-tick.png")
    page.keyboard.press("Escape")
    page.wait_for_timeout(300)
    results["checks"][f"p1-closed-by-esc-{tag}"] = page.locator("#day-dlg[open]").count() == 0
    results["checks"][f"after-p1-read-{tag}"] = card_numbers(page)["Read 20 pages"]
    results["checks"][f"p1-cell-label-after-{tag}"] = cell.get_attribute("aria-label")
    if full_suite:
        page.evaluate("window.scrollTo(0,0)")
        page.wait_for_timeout(200)
        shot(page, f"k1-{tag}-after-p1-tick.png")

    # future day cannot be opened
    results["checks"][f"future-day-closed-{tag}"] = page.locator('button.hc[data-key="2026-10-11"]').count() == 0

    # M1 from the bin, closed by the backdrop
    page.evaluate("window.scrollTo(0,0)")
    page.click('li.habit:nth-child(2) .trash', timeout=T)
    page.wait_for_selector("#del-dlg[open]", timeout=T)
    page.wait_for_timeout(350)
    results["checks"][f"m1-title-{tag}"] = text(page, "#del-title")
    shot(page, f"m1-{tag}.png")
    page.mouse.click(4, 4)
    page.wait_for_timeout(300)
    results["checks"][f"m1-closed-by-backdrop-{tag}"] = page.locator("#del-dlg[open]").count() == 0

    if full_suite:
        # P1 closed by the backdrop too
        cell.scroll_into_view_if_needed(timeout=T)
        cell.click(timeout=T)
        page.wait_for_selector("#day-dlg[open]", timeout=T)
        page.mouse.click(4, 4)
        page.wait_for_timeout(300)
        results["checks"][f"p1-closed-by-backdrop-{tag}"] = page.locator("#day-dlg[open]").count() == 0
        # M1 closed by Esc
        page.evaluate("window.scrollTo(0,0)")
        page.click('li.habit:nth-child(2) .trash', timeout=T)
        page.wait_for_selector("#del-dlg[open]", timeout=T)
        page.keyboard.press("Escape")
        page.wait_for_timeout(300)
        results["checks"][f"m1-closed-by-esc-{tag}"] = page.locator("#del-dlg[open]").count() == 0

    # prototype menu
    page.click("#proto-tab", timeout=T)
    page.wait_for_timeout(200)
    shot(page, f"proto-menu-{tag}.png")
    page.keyboard.press("Escape")

    states = ["s1", "s2-empty", "s2-long", "s2-dup", "s3", "s4", "s5"] if full_suite else ["s1", "s3", "s4"]
    for s in states:
        set_state(page, s)
        shot(page, f"{s}-{tag}.png")
        if s in ("s1", "s3"):
            shot(page, f"{s}-{tag}-full.png", full=True)
        if w == 360:
            results["overflow_360"][s] = overflow(page, w)
    if w == 360:
        # P1 open at 360, check the sheet fits
        set_state(page, "k1")
        cell = page.locator('button.hc[data-key="2026-09-22"]')
        cell.scroll_into_view_if_needed(timeout=T)
        cell.click(timeout=T)
        page.wait_for_selector("#day-dlg[open]", timeout=T)
        page.wait_for_timeout(350)
        results["overflow_360"]["p1"] = overflow(page, w)
        page.keyboard.press("Escape")

    if w == 1280:
        set_state(page, "k1")
        page.keyboard.press("Tab")
        page.keyboard.press("Tab")
        page.keyboard.press("Tab")
        page.wait_for_timeout(200)
        shot(page, "focus-1280.png")

    # tokens for contrast
    tokens = page.evaluate(
        """() => { const s = getComputedStyle(document.documentElement); const o = {};
          for (const n of ['--bg','--surface','--surface-2','--raise','--field','--ink','--ink-soft','--amber','--amber-hover','--on-amber','--danger','--danger-hover','--ring','--track','--focus','--line']) o[n] = s.getPropertyValue(n).trim();
          return o; }"""
    )
    ctx.close()
    return tokens


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            run_size(browser, 390, 844, "390", True)
            run_size(browser, 360, 780, "360", False)
            tk = run_size(browser, 1280, 800, "1280", True)
            # reduced motion: page still renders with no errors
            ctx = browser.new_context(viewport={"width": 390, "height": 844}, reduced_motion="reduce")
            page = ctx.new_page()
            page.on("pageerror", lambda e: results["page_errors"].append(f"reduced: {e}"))
            page.goto(URL, timeout=T)
            page.wait_for_selector("li.habit", timeout=T)
            results["checks"]["reduced-motion-run-arcs-visible"] = page.evaluate(
                "() => [...document.querySelectorAll('.run')].every(p => getComputedStyle(p).strokeDashoffset === '0px' || getComputedStyle(p).strokeDasharray === 'none')"
            )
            ctx.close()
        finally:
            browser.close()

    pairs = [
        ("ink on bg (body text)", "--ink", "--bg"),
        ("ink on surface (habit names)", "--ink", "--surface"),
        ("ink on surface-2 (dialog)", "--ink", "--surface-2"),
        ("ink-soft on bg (date)", "--ink-soft", "--bg"),
        ("ink-soft on surface (labels, grid numbers)", "--ink-soft", "--surface"),
        ("ink-soft on surface-2 (dialog body)", "--ink-soft", "--surface-2"),
        ("amber on bg (accent)", "--amber", "--bg"),
        ("amber on surface (Current number, done ring)", "--amber", "--surface"),
        ("amber on surface-2 (Current in the editor)", "--amber", "--surface-2"),
        ("on-amber on amber (Add, done day number)", "--on-amber", "--amber"),
        ("on-amber on amber-hover", "--on-amber", "--amber-hover"),
        ("on-amber on danger (Delete habit)", "--on-amber", "--danger"),
        ("danger on bg (field error)", "--danger", "--bg"),
        ("ring on surface (not-done outline, 3:1)", "--ring", "--surface"),
        ("ring on field (input border, 3:1)", "--ring", "--field"),
        ("ring on surface-2 (tick outline, 3:1)", "--ring", "--surface-2"),
        ("focus on bg", "--focus", "--bg"),
        ("focus on surface", "--focus", "--surface"),
        ("ink on field (typed text)", "--ink", "--field"),
    ]
    for label, a, b in pairs:
        results["contrast"][label] = {"fg": tk[a], "bg": tk[b], "ratio": ratio(tk[a], tk[b])}

    out = HERE / "results.json"
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in results.items() if k != "shots"}, indent=2))
    print("shots:", len(results["shots"]))


if __name__ == "__main__":
    main()
