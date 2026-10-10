"""Prints element widths at 360 px to find what overflows. Read only, writes nothing."""
import json
import pathlib

from playwright.sync_api import sync_playwright

URL = (pathlib.Path(__file__).resolve().parent.parent.parent / "b.html").as_uri()

with sync_playwright() as p:
    browser = None
    try:
        browser = p.chromium.launch(headless=True, timeout=30000)
        page = browser.new_page(viewport={"width": 360, "height": 780})
        page.set_default_timeout(5000)
        page.goto(URL, wait_until="load", timeout=5000)
        out = page.evaluate("""() => {
          const r = s => { const e = document.querySelector(s); if (!e) return null; const b = e.getBoundingClientRect(); return [Math.round(b.left), Math.round(b.right), Math.round(b.width)]; };
          return { client: document.documentElement.clientWidth, scroll: document.documentElement.scrollWidth, inner: innerWidth,
            page: r('.page'), top: r('.top'), layout: r('.layout'), col: r('.col'), section: r('.col > section'), ul: r('.habits'), habit: r('.habit'),
            rail: r('.rail'), streak: r('.streak'), form: r('#add'), sky: r('#sky'), hm: r('#hm'), legend: r('.legend') };
        }""")
        print(json.dumps(out, indent=1))
    finally:
        if browser:
            browser.close()
