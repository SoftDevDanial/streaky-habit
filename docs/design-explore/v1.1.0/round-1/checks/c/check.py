"""Render checks for round-1 direction C (Daylight Instrument).

Opens c.html by its file URL in headless Chromium, saves screenshots of the key screen at
390 x 844, 360 x 780 and 1280 x 800 plus every popup, dialog and prototype state, and prints
console errors, sideways scroll, streak numbers and contrast ratios. Every wait is bounded and
the browser is closed in a finally block.
"""
import json
import pathlib

from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
HTML = HERE.parent.parent / "c.html"
URL = HTML.as_uri()
T = 5000  # ms, every action and wait is bounded by this

report = {"console_errors": {}, "scroll_360": {}, "numbers": {}, "contrast": {}, "checks": {}}


def lum(hex_str):
    h = hex_str.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    rgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def ratio(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return round((hi + 0.05) / (lo + 0.05), 2)


def shot(page, name, full=False):
    page.wait_for_timeout(350)
    page.screenshot(path=str(HERE / f"{name}.png"), full_page=full, timeout=T)


def state(page, key):
    page.click("#proto-toggle", timeout=T)
    page.click(f'#proto-menu button[data-state="{key}"]', timeout=T)
    page.wait_for_timeout(150)


def readouts(page):
    return page.eval_on_selector_all(
        ".habit",
        "els => els.map(e => ({name: e.querySelector('.h-name').textContent,"
        " cur: +e.querySelector('.readout').dataset.cur, best: +e.querySelector('.readout').dataset.best}))",
    )


def hscroll(page):
    return page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")


def cell_clear(page, date):
    """True when the opened matrix cell is on screen and not covered by the day editor."""
    return page.evaluate("""date => {
      const c = document.querySelector(`.mc[data-date="${date}"]`).getBoundingClientRect();
      const d = document.querySelector('#day-dlg').getBoundingClientRect();
      const overlap = !(c.right <= d.left || c.left >= d.right || c.bottom <= d.top || c.top >= d.bottom);
      return c.top >= 0 && c.bottom <= innerHeight && !overlap;
    }""", date)


def dialog_open(page, sel):
    return page.evaluate(f"document.querySelector('{sel}').open")


def run_viewport(browser, w, h, tag):
    ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1)
    page = ctx.new_page()
    page.set_default_timeout(T)
    errors = []
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(URL, wait_until="load", timeout=10000)
    page.wait_for_timeout(200)

    report["numbers"][f"k1-{tag}"] = readouts(page)
    report["checks"][f"targets-{tag}"] = page.evaluate("""() => {
      const box = s => { const r = document.querySelector(s).getBoundingClientRect(); return [Math.round(r.width * 10) / 10, Math.round(r.height * 10) / 10]; };
      const a = document.querySelector('.mc[data-i="0"]').getBoundingClientRect();
      const b = document.querySelector('.mc[data-i="1"]').getBoundingClientRect();
      return { day_cell: box('.day'), matrix_cell: box('.mc[data-i="0"]'), gauge: box('.mc[data-i="0"] .gauge'),
               matrix_pitch: Math.round(Math.max(b.left - a.left, b.top - a.top) * 10) / 10,
               icon_btn: box('.del'), add_btn: box('#add-btn'), input: box('#new-habit'),
               client_width: document.documentElement.clientWidth };
    }""")
    shot(page, f"k1-{tag}")
    shot(page, f"k1-{tag}-full", full=True)
    if tag == "360":
        report["scroll_360"]["k1"] = hscroll(page)

    # strip tick: today on Stretch 10 minutes
    if tag in ("390", "1280"):
        stretch_today = page.locator('.habit:nth-child(2) .day[aria-current="date"]')
        stretch_today.scroll_into_view_if_needed(timeout=T)
        stretch_today.click(timeout=T)
        report["numbers"][f"after-strip-tick-{tag}"] = readouts(page)[1]
        report["checks"][f"today-level-after-strip-tick-{tag}"] = page.get_attribute('.mc[data-date="2026-10-10"]', "data-level")
        shot(page, f"k1-{tag}-after-strip-tick")
        state(page, "k1")

    # P1 day editor from the matrix
    cell = page.locator('.mc[data-date="2026-09-22"]')
    cell.scroll_into_view_if_needed(timeout=T)
    cell.click(timeout=T)
    report["checks"][f"p1-open-{tag}"] = dialog_open(page, "#day-dlg")
    report["checks"][f"p1-title-{tag}"] = page.text_content("#day-title")
    report["checks"][f"p1-level-before-{tag}"] = page.get_attribute('.mc[data-date="2026-09-22"]', "data-level")
    report["checks"][f"p1-cell-visible-{tag}"] = cell_clear(page, "2026-09-22")
    shot(page, f"p1-{tag}")
    if tag == "360":
        report["scroll_360"]["p1"] = hscroll(page)
    page.click('#day-list .pick:has-text("Read 20 pages")', timeout=T)
    report["numbers"][f"after-p1-tick-{tag}"] = readouts(page)[0]
    report["checks"][f"p1-level-after-{tag}"] = page.get_attribute('.mc[data-date="2026-09-22"]', "data-level")
    report["checks"][f"p1-count-after-{tag}"] = page.text_content("#day-count")
    shot(page, f"p1-{tag}-after-tick")
    page.keyboard.press("Escape")
    page.wait_for_timeout(100)
    report["checks"][f"p1-esc-closes-{tag}"] = not dialog_open(page, "#day-dlg")
    cell.click(timeout=T)
    report["checks"][f"p1-reopens-{tag}"] = dialog_open(page, "#day-dlg")
    page.mouse.click(6, 6)
    page.wait_for_timeout(100)
    report["checks"][f"p1-backdrop-closes-{tag}"] = not dialog_open(page, "#day-dlg")
    if tag == "1280":
        shot(page, f"k1-{tag}-after-p1-tick")
    # P1 on today's cell, the bottom row on a phone
    page.click('.mc[data-date="2026-10-10"]', timeout=T)
    report["checks"][f"p1-today-cell-visible-{tag}"] = cell_clear(page, "2026-10-10")
    shot(page, f"p1-today-{tag}")
    page.keyboard.press("Escape")
    page.wait_for_timeout(100)
    state(page, "k1")
    report["checks"][f"future-cell-not-button-{tag}"] = page.evaluate(
        "document.querySelector('.mc.future').tagName !== 'BUTTON'")

    # M1 delete dialog
    page.evaluate("window.scrollTo(0, 0)")
    page.click('[aria-label="Delete Stretch 10 minutes"]', timeout=T)
    report["checks"][f"m1-title-{tag}"] = page.text_content("#del-title")
    report["checks"][f"m1-focus-cancel-{tag}"] = page.evaluate("document.activeElement.id")
    shot(page, f"m1-{tag}")
    page.keyboard.press("Escape")
    page.wait_for_timeout(100)
    report["checks"][f"m1-esc-closes-{tag}"] = not dialog_open(page, "#del-dlg")
    page.click('[aria-label="Delete Stretch 10 minutes"]', timeout=T)
    page.mouse.click(6, 6)
    page.wait_for_timeout(100)
    report["checks"][f"m1-backdrop-closes-{tag}"] = not dialog_open(page, "#del-dlg")
    page.click('[aria-label="Delete Stretch 10 minutes"]', timeout=T)
    page.click("#del-ok", timeout=T)
    report["checks"][f"m1-delete-leaves-{tag}"] = [r["name"] for r in readouts(page)]
    state(page, "k1")

    # prototype states
    if tag == "390":
        page.click("#proto-toggle", timeout=T)
        shot(page, f"proto-menu-{tag}")
        page.click("#proto-toggle", timeout=T)
    for key in ("s1", "s2-empty", "s2-long", "s2-dup", "s3", "s4", "s5"):
        if tag == "360" and key not in ("s1", "s3", "s2-long"):
            continue
        state(page, key)
        shot(page, f"{key}-{tag}")
        if key in ("s3", "s1"):
            shot(page, f"{key}-{tag}-full", full=True)
        if tag == "360":
            report["scroll_360"][key] = hscroll(page)
        if key == "s3":
            report["checks"][f"s3-disabled-{tag}"] = page.evaluate(
                "[document.querySelector('#new-habit').disabled, document.querySelector('#add-btn').disabled]")
        if key == "s5":
            page.click('[aria-label="Dismiss note"]', timeout=T)
            report["checks"][f"s5-dismissed-{tag}"] = page.evaluate("document.querySelector('#notes').children.length === 0")
    state(page, "k1")

    if tag == "1280":
        # keyboard focus ring on a strip cell and in the matrix
        page.evaluate("window.scrollTo(0, 0)")
        page.focus("#new-habit")
        page.keyboard.press("Shift+Tab")
        page.wait_for_timeout(100)
        shot(page, f"focus-strip-{tag}")
        page.focus('.mc[data-date="2026-10-10"]')
        page.keyboard.press("ArrowLeft")
        page.wait_for_timeout(100)
        report["checks"]["matrix-arrow-left-1280"] = page.evaluate("document.activeElement.dataset.date")
        shot(page, f"focus-matrix-{tag}")

    report["console_errors"][tag] = errors
    ctx.close()


def run_reduced(browser):
    ctx = browser.new_context(viewport={"width": 390, "height": 844}, reduced_motion="reduce")
    page = ctx.new_page()
    page.set_default_timeout(T)
    page.goto(URL, wait_until="load", timeout=10000)
    report["checks"]["reduced-motion-seg-transition"] = page.evaluate(
        "getComputedStyle(document.querySelector('.seg')).transitionDuration")
    report["checks"]["reduced-motion-fill-transition"] = page.evaluate(
        "getComputedStyle(document.querySelector('.mc .fill')).transitionDuration")
    ctx.close()


def run_contrast(browser):
    ctx = browser.new_context(viewport={"width": 390, "height": 844})
    page = ctx.new_page()
    page.set_default_timeout(T)
    page.goto(URL, wait_until="load", timeout=10000)
    names = ["bg", "panel", "wash", "rule", "line", "ink", "ink-soft", "cobalt", "cobalt-deep",
             "on-cobalt", "danger", "danger-deep", "focus", "cell"]
    v = page.evaluate(
        "names => Object.fromEntries(names.map(n => [n, getComputedStyle(document.documentElement)"
        ".getPropertyValue('--' + n).trim()]))", names)
    pairs = [
        ("ink", "bg", "body text, habit names"),
        ("ink", "panel", "text on faceplates, popup, dialog"),
        ("ink-soft", "bg", "labels, dates, units"),
        ("ink-soft", "panel", "labels on faceplates, dialog body"),
        ("ink-soft", "rule", "disabled Add text"),
        ("cobalt", "bg", "accent: Current numerals, done segments"),
        ("cobalt", "panel", "accent on faceplates, gauge fills"),
        ("cobalt", "cell", "gauge fill against the empty cell"),
        ("on-cobalt", "cobalt", "Add label, check mark"),
        ("on-cobalt", "cobalt-deep", "Add on hover"),
        ("cobalt-deep", "panel", "Current line in the day editor"),
        ("danger", "bg", "field error text"),
        ("on-cobalt", "danger", "Delete habit"),
        ("on-cobalt", "danger-deep", "Delete habit on hover"),
        ("line", "bg", "control borders, gauge zero line"),
        ("line", "panel", "input border, Cancel border"),
        ("line", "cell", "gauge zero line on the cell"),
        ("focus", "bg", "focus ring"),
        ("focus", "panel", "focus ring on faceplates"),
        ("ink", "panel", "today frame"),
    ]
    report["contrast"] = {f"{a} on {b}": {"ratio": ratio(v[a], v[b]), "use": use, "fg": v[a], "bg": v[b]}
                          for a, b, use in pairs}
    ctx.close()


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            for w, h, tag in ((390, 844, "390"), (360, 780, "360"), (1280, 800, "1280")):
                run_viewport(browser, w, h, tag)
            run_reduced(browser)
            run_contrast(browser)
        finally:
            browser.close()
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
