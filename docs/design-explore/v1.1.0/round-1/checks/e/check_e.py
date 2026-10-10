"""Render checks for direction E (Command Line). Headless Chromium, file:/// URL, no server, no network.

Run: python -B <this file>
Writes screenshots and results.json beside this file.
"""
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
PAGE = HERE.parent.parent / "e.html"
URL = PAGE.as_uri()
OUT = HERE
results = {"url": URL, "console_errors": [], "page_errors": [], "requests_non_file": [], "sizes": {}, "checks": {}}


def lum(hex_):
    hex_ = hex_.strip().lstrip("#")
    r, g, b = (int(hex_[i:i + 2], 16) / 255 for i in (0, 2, 4))

    def ch(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def ratio(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return round((hi + 0.05) / (lo + 0.05), 2)


def wire(page, tag):
    page.on("console", lambda m: results["console_errors"].append(f"{tag}: {m.text}") if m.type == "error" else None)
    page.on("pageerror", lambda e: results["page_errors"].append(f"{tag}: {e}"))
    page.on("request", lambda r: results["requests_non_file"].append(r.url) if not (r.url.startswith("file:") or r.url.startswith("data:")) else None)


def overflow(page, width):
    return page.evaluate(
        """(w) => {
        const de = document.documentElement;
        const bad = [];
        for (const el of document.querySelectorAll('body *')) {
          const cs = getComputedStyle(el);
          if (cs.display === 'none' || cs.visibility === 'hidden') continue;
          if (el.closest('svg[width="0"]')) continue;
          const r = el.getBoundingClientRect();
          if (!r.width && !r.height) continue;
          if (r.right > w + 0.5 || r.left < -0.5) bad.push((el.id ? '#' + el.id : el.tagName.toLowerCase() + '.' + [...el.classList].join('.')) + ' ' + Math.round(r.left) + '..' + Math.round(r.right));
        }
        return { scrollWidth: de.scrollWidth, clientWidth: de.clientWidth, poking: bad.slice(0, 20) };
      }""",
        width,
    )


def targets(page):
    return page.evaluate(
        """() => {
        const out = {};
        for (const sel of ['.day', 'button.hc', '.del', '.btn-add', '#proto-tab']) {
          const els = [...document.querySelectorAll(sel)].filter(e => e.getBoundingClientRect().width);
          if (!els.length) continue;
          const w = Math.min(...els.map(e => e.getBoundingClientRect().width));
          const h = Math.min(...els.map(e => e.getBoundingClientRect().height));
          out[sel] = [Math.round(w * 10) / 10, Math.round(h * 10) / 10];
        }
        return out;
      }"""
    )


def streak_text(page, name):
    return page.evaluate(
        """(n) => { const li = [...document.querySelectorAll('.habit')].find(l => l.querySelector('.name').textContent === n);
                    return li ? li.querySelector('.streak').textContent.replace(/\\s+/g, ' ').trim() : null; }""",
        name,
    )


def shot(page, name, full=False):
    path = OUT / f"{name}.png"
    page.screenshot(path=str(path), full_page=full)
    return str(path)


def main():
    shots = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            for (w, h) in [(390, 844), (360, 780), (1280, 800)]:
                ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1)
                page = ctx.new_page()
                page.set_default_timeout(5000)
                wire(page, f"{w}")
                page.goto(URL, wait_until="load", timeout=10000)
                size = {}
                shots.append(shot(page, f"k1-{w}"))
                shots.append(shot(page, f"k1-{w}-full", full=True))
                size["overflow_k1"] = overflow(page, w)
                size["targets"] = targets(page)
                size["streaks_k1"] = {n: streak_text(page, n) for n in ["Read 20 pages", "Stretch 10 minutes", "No phone after 11pm"]}

                # P1 day editor by tap on Tue 22 Sep (day 64)
                cell = page.locator('button.hc[data-i="64"]')
                before_level = cell.get_attribute("data-l")
                cell.click()
                page.wait_for_selector("#day-dlg[open]", timeout=3000)
                page.wait_for_timeout(350)
                size["p1_title"] = page.text_content("#day-title")
                size["p1_sub_before"] = page.text_content("#day-sub")
                shots.append(shot(page, f"p1-{w}"))
                stretch_row = page.locator('.drow[data-h="2"]')
                size["p1_stretch_before"] = stretch_row.locator(".streak").text_content()
                stretch_row.click()
                page.wait_for_timeout(450)
                size["p1_stretch_after"] = stretch_row.locator(".streak").text_content()
                size["p1_sub_after"] = page.text_content("#day-sub")
                after_level = page.locator('button.hc[data-i="64"]').get_attribute("data-l")
                size["p1_heat_level"] = f"{before_level} -> {after_level}"
                size["p1_list_best_after"] = streak_text(page, "Stretch 10 minutes")
                shots.append(shot(page, f"p1-{w}-ticked"))
                if w != 1280:
                    size["overflow_p1"] = overflow(page, w)
                page.keyboard.press("Escape")
                page.wait_for_selector("#day-dlg:not([open])", state="attached", timeout=3000)
                size["p1_closed_by_esc"] = page.evaluate("!document.querySelector('#day-dlg').open")
                size["p1_focus_after_close"] = page.evaluate("document.activeElement.getAttribute('aria-label')")
                # backdrop closes P1 too
                page.locator('button.hc[data-i="70"]').click()
                page.wait_for_selector("#day-dlg[open]", timeout=3000)
                page.mouse.click(4, h - 4)
                page.wait_for_timeout(250)
                size["p1_closed_by_backdrop"] = page.evaluate("!document.querySelector('#day-dlg').open")
                # future day cannot be opened
                size["future_cells_are_buttons"] = page.evaluate("document.querySelectorAll('.hc.future').length + ':' + document.querySelectorAll('button.hc.future').length")

                # strip tick changes streaks and today's heat cell
                page.evaluate("window.__proto.setState('K1')")
                lvl0 = page.locator('button.hc[data-i="82"]').get_attribute("data-l")
                s0 = streak_text(page, "Stretch 10 minutes")
                page.locator('.habit[data-id="2"] .day[data-i="82"]').click()
                page.wait_for_timeout(450)
                size["strip_tick_stretch"] = f"{s0}  ->  {streak_text(page, 'Stretch 10 minutes')}"
                size["strip_tick_heat_today"] = f"{lvl0} -> {page.locator('button.hc[data-i=\"82\"]').get_attribute('data-l')}"
                page.evaluate("window.__proto.setState('K1')")

                # M1 delete dialog from the bin
                page.mouse.move(2, 2)
                page.evaluate("window.scrollTo(0, 0)")
                page.locator('.habit[data-id="2"] .del').click()
                page.wait_for_selector("#del-dlg[open]", timeout=3000)
                page.wait_for_timeout(350)
                size["m1_title"] = page.text_content("#del-title")
                size["m1_focus"] = page.evaluate("document.activeElement.id")
                shots.append(shot(page, f"m1-{w}"))
                if w != 1280:
                    size["overflow_m1"] = overflow(page, w)
                page.mouse.click(4, 4)
                page.wait_for_timeout(250)
                size["m1_closed_by_backdrop"] = page.evaluate("!document.querySelector('#del-dlg').open")
                page.locator('.habit[data-id="2"] .del').click()
                page.wait_for_selector("#del-dlg[open]", timeout=3000)
                page.keyboard.press("Escape")
                page.wait_for_timeout(200)
                size["m1_closed_by_esc"] = page.evaluate("!document.querySelector('#del-dlg').open")
                size["m1_focus_after_esc"] = page.evaluate("document.activeElement.getAttribute('aria-label')")

                # prototype menu and states
                page.click("#proto-tab")
                shots.append(shot(page, f"proto-menu-{w}"))
                page.click("#proto-tab")
                for s in ["S1", "S2a", "S2b", "S2c", "S3", "S4", "S5"]:
                    page.evaluate(f"window.__proto.setState('{s}')")
                    page.evaluate("window.scrollTo(0, 0)")
                    page.mouse.move(2, 2)
                    page.wait_for_timeout(250)
                    if w == 390 or s in ("S3", "S4", "S2b") or (w == 1280 and s == "S1"):
                        shots.append(shot(page, f"{s.lower()}-{w}"))
                    if w == 360:
                        size[f"overflow_{s}"] = overflow(page, w)["poking"]
                    if s == "S3":
                        size["s3_disabled"] = page.evaluate("document.querySelector('#new-habit').disabled && document.querySelector('#add-btn').disabled")
                        size["s3_rows"] = page.evaluate("document.querySelectorAll('.habit').length")
                        shots.append(shot(page, f"s3-{w}-full", full=True))
                page.evaluate("window.__proto.setState('K1')")

                # S3 delete one frees the field (rule)
                results["sizes"][str(w)] = size
                ctx.close()

            # ---- keyboard reachability (desktop width) ----
            ctx = browser.new_context(viewport={"width": 1280, "height": 800})
            page = ctx.new_page()
            page.set_default_timeout(5000)
            wire(page, "kbd")
            page.goto(URL, wait_until="load", timeout=10000)
            kb = {}
            order = []
            reached_hc = None
            for n in range(1, 40):
                page.keyboard.press("Tab")
                info = page.evaluate("(() => { const a = document.activeElement; return [a.tagName, a.className, a.getAttribute('aria-label') || a.textContent.trim().slice(0, 24)]; })()")
                order.append(" ".join(x for x in info if x))
                if "hc" in info[1].split() and reached_hc is None:
                    reached_hc = n
                    break
            kb["tab_order_to_heatmap"] = order
            kb["tabs_to_heatmap"] = reached_hc
            page.keyboard.press("ArrowUp")
            page.keyboard.press("ArrowLeft")
            kb["arrow_to"] = page.evaluate("document.activeElement.getAttribute('aria-label')")
            page.keyboard.press("Enter")
            page.wait_for_selector("#day-dlg[open]", timeout=3000)
            page.wait_for_timeout(350)
            kb["p1_open_by_enter"] = page.text_content("#day-title")
            kb["p1_first_focus"] = page.evaluate("document.activeElement.getAttribute('aria-label')")
            page.keyboard.press("ArrowDown")
            page.keyboard.press("Space")
            page.wait_for_timeout(300)
            kb["p1_space_toggled"] = page.evaluate("document.activeElement.getAttribute('aria-pressed')")
            shots.append(shot(page, "p1-1280-keyboard"))
            page.keyboard.press("Escape")
            page.wait_for_timeout(200)
            kb["p1_closed"] = page.evaluate("!document.querySelector('#day-dlg').open")
            kb["focus_back"] = page.evaluate("document.activeElement.getAttribute('aria-label')")
            # M1 via Tab to a bin + Enter
            page.evaluate("window.__proto.setState('K1')")
            page.evaluate("document.activeElement && document.activeElement.blur()")
            page.keyboard.press("/")
            kb["slash_focuses_input"] = page.evaluate("document.activeElement.id")
            tabs_to_bin = None
            for n in range(1, 20):
                page.keyboard.press("Tab")
                if page.evaluate("document.activeElement.classList.contains('del')"):
                    tabs_to_bin = n
                    break
            kb["tabs_from_input_to_bin"] = tabs_to_bin
            kb["bin_label"] = page.evaluate("document.activeElement.getAttribute('aria-label')")
            page.keyboard.press("Enter")
            page.wait_for_selector("#del-dlg[open]", timeout=3000)
            kb["m1_open_by_enter"] = page.text_content("#del-title")
            page.keyboard.press("Escape")
            page.wait_for_timeout(200)
            kb["m1_closed_by_esc"] = page.evaluate("!document.querySelector('#del-dlg').open")
            # M1 via Del key on a mark
            page.locator('.habit[data-id="3"] .day[data-i="82"]').focus()
            page.keyboard.press("Delete")
            page.wait_for_selector("#del-dlg[open]", timeout=3000)
            page.wait_for_timeout(350)
            kb["m1_open_by_del_key"] = page.text_content("#del-title")
            shots.append(shot(page, "m1-1280-keyboard"))
            page.keyboard.press("Tab")
            page.keyboard.press("Enter")
            page.wait_for_timeout(250)
            kb["deleted_and_focus"] = [page.evaluate("document.querySelectorAll('.habit').length"), page.evaluate("document.activeElement.getAttribute('aria-label') || document.activeElement.id")]
            # visible focus ring on a mark
            page.evaluate("window.__proto.setState('K1')")
            page.locator('.habit[data-id="1"] .day[data-i="82"]').focus()
            page.keyboard.press("ArrowLeft")
            kb["focus_ring"] = page.evaluate("(() => { const cs = getComputedStyle(document.activeElement); return cs.outlineStyle + ' ' + cs.outlineWidth + ' ' + cs.outlineColor; })()")
            shots.append(shot(page, "k1-1280-focus"))
            results["checks"]["keyboard"] = kb

            # ---- reduced motion ----
            ctx2 = browser.new_context(viewport={"width": 390, "height": 844}, reduced_motion="reduce")
            p2 = ctx2.new_page()
            p2.set_default_timeout(5000)
            wire(p2, "rm")
            p2.goto(URL, wait_until="load", timeout=10000)
            results["checks"]["reduced_motion_mark_transition"] = p2.evaluate("getComputedStyle(document.querySelector('.mk')).transitionDuration")
            ctx2.close()

            # ---- contrast from the page's own tokens ----
            v = page.evaluate(
                """() => { const cs = getComputedStyle(document.documentElement); const o = {};
                for (const k of ['--bg','--panel','--raised','--well','--ink','--ink-soft','--mute','--on-ink','--signal','--signal-ink','--signal-tint','--line-strong','--seg-off']) o[k] = cs.getPropertyValue(k).trim();
                return o; }"""
            )
            pairs = [
                ("body text --ink on --panel", "--ink", "--panel"),
                ("body text --ink on --bg", "--ink", "--bg"),
                ("secondary --ink-soft on --panel", "--ink-soft", "--panel"),
                ("secondary --ink-soft on --bg", "--ink-soft", "--bg"),
                ("secondary --ink-soft on --well (heat numbers)", "--ink-soft", "--well"),
                ("accent text --signal-ink on --panel (today, errors)", "--signal-ink", "--panel"),
                ("accent text --signal-ink on --raised (palette prompt)", "--signal-ink", "--raised"),
                ("accent text --signal-ink on --well (today heat number)", "--signal-ink", "--well"),
                ("Current chip --ink on --signal", "--ink", "--signal"),
                ("Add / Delete habit --on-ink on --ink", "--on-ink", "--ink"),
                ("save warning --ink on --signal-tint", "--ink", "--signal-tint"),
                ("focus ring --signal-ink vs --panel (3:1)", "--signal-ink", "--panel"),
                ("focus ring --signal-ink vs --bg (3:1)", "--signal-ink", "--bg"),
                ("open mark stroke --mute on --panel (3:1)", "--mute", "--panel"),
                ("open mark stroke --mute on --signal-tint (3:1)", "--mute", "--signal-tint"),
                ("meter segment --ink on --well (3:1)", "--ink", "--well"),
                ("meter segment --ink vs empty --seg-off (3:1)", "--ink", "--seg-off"),
                ("today ring --signal-ink on --well (3:1)", "--signal-ink", "--well"),
                ("signal fill --signal vs --panel (decorative)", "--signal", "--panel"),
            ]
            results["checks"]["tokens"] = v
            results["checks"]["contrast"] = {name: ratio(v[a], v[b]) for name, a, b in pairs}
            ctx.close()
        finally:
            browser.close()
    results["screenshots"] = shots
    (OUT / "results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    brief = {k: v for k, v in results.items() if k != "screenshots"}
    print(json.dumps(brief, indent=1))
    print("screenshots:", len(shots))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # report and exit non-zero, browser already closed in finally
        print("CHECK FAILED:", repr(exc))
        print(json.dumps(results, indent=2))
        sys.exit(1)
