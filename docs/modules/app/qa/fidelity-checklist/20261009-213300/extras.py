"""Extra measurements for the fidelity report (scratch, read-only): the machine and browser the gate ran on, the S5 note on a
desktop width, and the heatmap panel's sticky behaviour (S1-28), which a static 1280x800 screenshot does not exercise.
Writes extras.json.
"""
import json

from common import *  # noqa: F401,F403
from playwright.sync_api import sync_playwright

out = {}
with sync_playwright() as pw:
    browser = launch(pw)
    out["chromium_version"] = browser.version
    ctx, page = open_page(browser, BASE, (1280, 800))
    out["page_timezone"] = page.evaluate("() => Intl.DateTimeFormat().resolvedOptions().timeZone + ' offset ' + (-new Date().getTimezoneOffset() / 60)")
    out["page_now_with_fixed_clock"] = page.evaluate("() => new Date().toString()")
    out["page_font_used"] = page.evaluate("() => getComputedStyle(document.body).fontFamily")
    ctx.close()

    # S5 note on desktop: top of the left column, not across both columns
    ctx, page = open_page(browser, BASE, (1280, 800), seed=False, clock=True)
    ctx.close()
    ctx = browser.new_context(viewport={"width": 1280, "height": 800}, device_scale_factor=1, color_scheme="light", locale="en-US")
    page = ctx.new_page()
    page.clock.set_fixed_time(FIXED)
    page.add_init_script("localStorage.setItem('streaks.state', '{')")
    page.goto(BASE, wait_until="networkidle")
    page.wait_for_timeout(400)
    out["S5_note_at_1280"] = page.evaluate(
        """() => { const r = (el) => { const b = el.getBoundingClientRect(); return { x: b.x, y: b.y, w: b.width, h: b.height, r: b.right, b: b.bottom }; };
          const note = document.querySelector('.note'), col = document.querySelector('.col-main'), heat = document.querySelector('section.heat'), btn = note.querySelector('.icon-btn');
          return { note: r(note), colMain: r(col), heat: r(heat), dismiss: r(btn), first_child_of_col_main: col.firstElementChild === note,
                   note_to_empty: document.querySelector('p.empty').getBoundingClientRect().top - note.getBoundingClientRect().bottom,
                   note_width_equals_column: Math.abs(r(note).w - r(col).w) < 0.01, dismiss_inset_top_right: [r(btn).y - r(note).y, r(note).r - r(btn).r] }; }"""
    )
    ctx.close()

    # sticky heatmap panel: golden and app at 1280x500, scrolled
    res = {}
    for label, url, seed in (("golden", golden_url("S1"), False), ("app", BASE, True)):
        ctx, page = open_page(browser, url, (1280, 500), seed=seed)
        rows = []
        for y in (0, 40, 100, 200, 400):
            page.evaluate(f"() => window.scrollTo(0, {y})")
            page.wait_for_timeout(120)
            rows.append(page.evaluate("() => [Math.round(window.scrollY), Math.round(document.querySelector('section.heat').getBoundingClientRect().top * 100) / 100, document.documentElement.scrollHeight]"))
        res[label] = rows
        ctx.close()
    out["sticky_heat_top_after_scroll"] = res
    out["sticky_equal"] = res["golden"] == res["app"]
    browser.close()

(SCRATCH / "extras.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(out, indent=1, ensure_ascii=False))
