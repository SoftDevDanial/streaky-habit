"""Render check for round-2 direction F (Orbit List). Headless Chromium, file:/// URL, no server, no network.

Writes screenshots and results.json beside this file only. Every wait is bounded, the browser closes in a finally block.
"""
import datetime as dt
import json
import pathlib
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
PAGE = HERE.parent.parent / "f.html"
D_PAGE = HERE.parent.parent.parent / "round-1" / "d.html"
URL = PAGE.as_uri()
T = 5000  # every wait is bounded

TODAY = dt.date(2026, 10, 10)
GRID_START = dt.date(2026, 7, 20)
YEAR_START = dt.date(2025, 10, 10)
ROUND1 = {
    "Read 20 pages": ["1101100", "1110110", "0111011", "1100111", "0110110", "1110011", "0111100", "1100101", "1111111", "1011100", "1101101", "1011111"],
    "Stretch 10 minutes": ["0101010", "1001001", "0110100", "1111100", "0010110", "1100100", "0011010", "1101100", "0110011", "1001110", "0111010", "1001100"],
    "No phone after 11pm": ["1110111", "0111101", "1011110", "0111011", "1101110", "1111111", "1111111", "0110111", "1101111", "0110110", "1110111", "1111000"],
}
EXPECTED = {"Read 20 pages": (4, 9), "Stretch 10 minutes": (2, 5), "No phone after 11pm": (0, 14)}

CLIP_STANDIN = """
window.__clipWrites = [];
try {
  Object.defineProperty(navigator, 'clipboard', { configurable: true, value: {
    writeText: (t) => { window.__clipWrites.push(String(t)); return Promise.resolve(); },
    write: (items) => { window.__clipWrites.push('[items]'); return Promise.resolve(); },
    readText: () => Promise.resolve(''),
    read: () => Promise.resolve([]),
  }});
} catch (e) {}
"""

R = {"console_errors": [], "page_errors": [], "requests_off_file": [], "clipboard_writes": {}, "asserts": {}, "info": {},
     "contrast": {}, "overflow_360": {}, "shots": []}


def ok(name, cond, detail=None):
    R["asserts"][name] = {"pass": bool(cond), "detail": detail}


# ---------- colour ----------
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


# ---------- streaks, computed here from the page's histories ----------
def streaks(keys):
    days = sorted(dt.date.fromisoformat(k) for k in keys)
    s = set(days)
    d = TODAY if TODAY in s else TODAY - dt.timedelta(days=1)
    cur = 0
    while d in s:
        cur += 1
        d -= dt.timedelta(days=1)
    best = run = 0
    prev = None
    for x in days:
        run = run + 1 if prev and (x - prev).days == 1 else 1
        best = max(best, run)
        prev = x
    return cur, best


def round1_set(weeks):
    out = set()
    for wi, w in enumerate(weeks):
        for d in range(7):
            if w[d] == "1":
                day = GRID_START + dt.timedelta(days=wi * 7 + d)
                if day <= TODAY:
                    out.add(day.isoformat())
    return out


# ---------- page helpers ----------
def shot(page, name, full=False):
    page.mouse.move(1, 1)
    page.wait_for_timeout(150)
    path = HERE / name
    page.screenshot(path=str(path), full_page=full)
    R["shots"].append(name)


def set_state(page, state):
    page.click("#proto-tab", timeout=T)
    page.click(f'[data-state="{state}"]', timeout=T)
    page.wait_for_timeout(400)


def rows(page):
    return page.evaluate("""() => [...document.querySelectorAll('#list .row')].map(r => {
        const cur = r.querySelector('.stat.cur .num'), best = r.querySelector('.stat.best .num');
        return { name: r.querySelector('.r-name').textContent,
                 current: cur ? Number(cur.textContent) : (r.querySelector('.stat.cur .none') ? 0 : null),
                 best: best ? Number(best.textContent) : 0,
                 doneToday: r.querySelector('.btn-done').getAttribute('aria-pressed') === 'true',
                 text: r.querySelector('.stats').innerText.replace(/\\s+/g, ' ').trim() };
    })""")


def p2_numbers(page):
    return page.evaluate("""() => {
        const s = document.querySelector('#yr-stats');
        const cur = s.querySelector('.stat.cur .num'), best = s.querySelector('.stat.best .num');
        return { title: document.querySelector('#yr-title').textContent,
                 current: cur ? Number(cur.textContent) : (s.querySelector('.stat.cur .none') ? 0 : null),
                 best: best ? Number(best.textContent) : 0,
                 text: s.innerText.replace(/\\s+/g, ' ').trim(),
                 dayButtons: document.querySelectorAll('#months button.yc').length,
                 closed: document.querySelectorAll('#months .yc.closed').length };
    }""")


def histories(page):
    return page.evaluate("() => window.__streaky.histories()")


def page_scroll(page):
    return page.evaluate("""() => { const d = document.scrollingElement;
        return { scrollHeight: d.scrollHeight, innerHeight: innerHeight, scrollWidth: d.scrollWidth, innerWidth: innerWidth }; }""")


def rect(page, sel):
    return page.evaluate("(s) => { const e = document.querySelector(s); if (!e) return null; const r = e.getBoundingClientRect(); return {x: r.x, y: r.y, w: r.width, h: r.height}; }", sel)


def overflow(page, width):
    return page.evaluate(
        """(w) => {
          const doc = document.documentElement, bad = [];
          for (const el of document.querySelectorAll('body *')) {
            if (el.closest('dialog:not([open])') || el.closest('[hidden]')) continue;
            const cs = getComputedStyle(el); if (cs.display === 'none' || cs.visibility === 'hidden') continue;
            const r = el.getBoundingClientRect();
            if (r.width === 0 && r.height === 0) continue;
            if (el.closest('.sr')) continue;
            if (r.right > w + 0.5 || r.left < -0.5) bad.push((el.className && el.className.baseVal !== undefined ? el.className.baseVal : el.className) + ' ' + el.tagName + ' ' + Math.round(r.left) + '..' + Math.round(r.right));
          }
          return { scrollWidth: doc.scrollWidth, clientWidth: doc.clientWidth, poking: bad.slice(0, 20) };
        }""",
        width,
    )


def proto_overlaps(page):
    return page.evaluate("""() => {
        const tab = document.querySelector('#proto-tab').getBoundingClientRect();
        const sels = ['.brand', '.date', '#ov-btn', '#band', '#banners .banner', '.frame', '#list .row', '#list .empty', '.composer', '#nh', '#add-btn'];
        const hits = [];
        for (const s of sels) for (const el of document.querySelectorAll(s)) {
          const cs = getComputedStyle(el); if (cs.display === 'none') continue;
          const r = el.getBoundingClientRect(); if (!r.width || !r.height) continue;
          const ix = Math.min(tab.right, r.right) - Math.max(tab.left, r.left), iy = Math.min(tab.bottom, r.bottom) - Math.max(tab.top, r.top);
          if (ix > 0 && iy > 0) hits.push(s);
        }
        return { tab: { x: tab.x, y: tab.y, w: tab.width, h: tab.height }, overlaps: hits };
    }""")


MEASURE = """(sel) => {
    const t = document.querySelector(sel); if (!t) return null;
    const svg = t.ownerSVGElement, vb = svg.viewBox.baseVal.width, w = svg.getBoundingClientRect().width;
    const fs = parseFloat(getComputedStyle(t).fontSize);
    return { fontSizeUserUnits: fs, svgPx: Math.round(w * 100) / 100, viewBox: vb, renderedPx: Math.round(fs * w / vb * 100) / 100 };
}"""


def new_page(browser, w, h, tag, reduced=False):
    ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1, reduced_motion="reduce" if reduced else "no-preference")
    ctx.add_init_script(CLIP_STANDIN)
    page = ctx.new_page()
    page.on("console", lambda m: R["console_errors"].append(f"{tag}: {m.text}") if m.type == "error" else None)
    page.on("pageerror", lambda e: R["page_errors"].append(f"{tag}: {e}"))
    page.on("request", lambda r: R["requests_off_file"].append(r.url) if not r.url.startswith(("file:", "data:")) else None)
    page.set_default_timeout(T)
    return ctx, page


def load(page, url=URL, wait="#list .row"):
    page.goto(url, timeout=T)
    page.wait_for_selector(wait, timeout=T)
    page.wait_for_timeout(500)


def check_numbers(page, tag):
    hist = histories(page)
    shown = {r["name"]: r for r in rows(page)}
    out = {}
    for h in hist:
        if h["name"] not in EXPECTED:
            continue
        cur, best = streaks(h["done"])
        out[h["name"]] = {"computed": [cur, best], "row": [shown[h["name"]]["current"], shown[h["name"]]["best"]], "row_text": shown[h["name"]]["text"],
                          "expected": list(EXPECTED[h["name"]]), "first_day": min(h["done"]), "days_done": len(h["done"])}
        ok(f"{tag} {h['name']} row matches history", (cur, best) == (shown[h["name"]]["current"], shown[h["name"]]["best"]) == EXPECTED[h["name"]], out[h["name"]])
        # the last 12 weeks are round 1 D's grid exactly
        window = {k for k in h["done"] if k >= GRID_START.isoformat()}
        ok(f"{tag} {h['name']} last 12 weeks equal round 1", window == round1_set(ROUND1[h["name"]]))
        ok(f"{tag} {h['name']} history inside the last 12 months", min(h["done"]) >= YEAR_START.isoformat() and max(h["done"]) <= TODAY.isoformat(), [min(h["done"]), max(h["done"])])
    return out


def today_cell_label(page, pfx):
    return page.get_attribute(f'[data-fk="{pfx}-2026-10-10"]', "aria-label", timeout=T)


# ---------- runs ----------
def run_1280(browser):
    ctx, page = new_page(browser, 1280, 800, "1280")
    try:
        load(page)
        shot(page, "k1-1280.png")
        R["info"]["title"] = page.title()
        ok("title is Danial's Streaky Habit", page.title() == "Danial's Streaky Habit")
        R["info"]["numbers-1280"] = check_numbers(page, "1280")
        ps = page_scroll(page)
        ok("1280 K1 page does not scroll", ps["scrollHeight"] <= ps["innerHeight"] and ps["scrollWidth"] <= ps["innerWidth"], ps)
        k1_input = rect(page, "#nh")
        R["info"]["1280 K1 frame"] = rect(page, ".frame")
        R["info"]["1280 proto K1"] = proto_overlaps(page)
        ok("1280 K1 proto tab overlaps no content", not R["info"]["1280 proto K1"]["overlaps"], R["info"]["1280 proto K1"])
        R["info"]["overview number size 1280"] = page.evaluate(MEASURE, "#band-grid .c-num")
        R["info"]["band height 1280"] = rect(page, "#band")

        # Done today on Stretch: row and overview today cell update, then undo
        before = today_cell_label(page, "b")
        page.click('#list .row:nth-child(2) .btn-done', timeout=T)
        page.wait_for_timeout(450)
        r2 = {r["name"]: r for r in rows(page)}["Stretch 10 minutes"]
        after = today_cell_label(page, "b")
        shot(page, "k1-1280-after-done-today.png")
        ok("1280 Done today updates the row and the overview", r2["doneToday"] and r2["current"] == 3 and before.endswith("1 of 3 habits") and after.endswith("2 of 3 habits"),
           {"row": r2, "today cell before": before, "after": after})
        page.click('#list .row:nth-child(2) .btn-done', timeout=T)
        page.wait_for_timeout(300)
        r2b = {r["name"]: r for r in rows(page)}["Stretch 10 minutes"]
        ok("1280 Done today unticks on a second tap", (not r2b["doneToday"]) and r2b["current"] == 2 and today_cell_label(page, "b").endswith("1 of 3 habits"), r2b)

        # P1 from an overview day
        page.click('#band-grid [data-key="2026-09-22"]', timeout=T)
        page.wait_for_selector("#day-dlg[open]", timeout=T)
        page.wait_for_timeout(350)
        R["info"]["p1 title 1280"] = page.inner_text("#day-title", timeout=T)
        shot(page, "p1-1280.png")
        lbl0 = page.get_attribute('#band-grid [data-key="2026-09-22"]', "aria-label", timeout=T)
        page.click('#day-list .tick:has-text("Read 20 pages")', timeout=T)
        page.wait_for_timeout(400)
        lbl1 = page.get_attribute('#band-grid [data-key="2026-09-22"]', "aria-label", timeout=T)
        ok("1280 P1 tick updates the overview", lbl0.endswith("1 of 3 habits") and lbl1.endswith("2 of 3 habits"), [lbl0, lbl1])
        page.click('#day-list .tick:has-text("Read 20 pages")', timeout=T)  # undo
        page.wait_for_timeout(250)
        page.mouse.click(6, 6)
        page.wait_for_timeout(300)
        ok("1280 P1 closes on the backdrop", page.locator("#day-dlg[open]").count() == 0)
        ok("1280 future day closed", page.locator('#band-grid button[data-key="2026-10-11"]').count() == 0)

        # P2 for every sample habit: header numbers equal the row and the history
        hist = {h["name"]: h["done"] for h in histories(page)}
        for i, name in enumerate(EXPECTED, start=1):
            page.click(f'#list .row:nth-child({i}) .btn-year', timeout=T)
            page.wait_for_selector("#yr-dlg[open]", timeout=T)
            page.wait_for_timeout(300)
            p2 = p2_numbers(page)
            ok(f"1280 P2 {name} numbers match history", p2["title"] == name and (p2["current"], p2["best"]) == streaks(hist[name]) == EXPECTED[name], p2)
            ok(f"1280 P2 {name} shows 366 days, 21 closed", p2["dayButtons"] == 366 and p2["closed"] == 21, p2)
            if i == 2:
                shot(page, "p2-1280.png")
                # tick Wed 7 Oct for Stretch: row, P2 and the overview update at once
                ov0 = page.get_attribute('#band-grid [data-key="2026-10-07"]', "aria-label", timeout=T)
                page.click('#months [data-key="2026-10-07"]', timeout=T)
                page.wait_for_timeout(400)
                p2b = p2_numbers(page)
                rowb = {r["name"]: r for r in rows(page)}[name]
                ov1 = page.get_attribute('#band-grid [data-key="2026-10-07"]', "aria-label", timeout=T)
                shot(page, "p2-1280-after-tick.png")
                ok("1280 P2 tick updates P2, the row and the overview", p2b["current"] == 3 and rowb["current"] == 3 and ov0.endswith("2 of 3 habits") and ov1.endswith("3 of 3 habits"),
                   {"p2": p2b["text"], "row": rowb["text"], "overview": [ov0, ov1]})
                page.click('#months [data-key="2026-10-07"]', timeout=T)  # undo
                page.wait_for_timeout(250)
                # M1 from P2, closed by the backdrop (P2 stays open)
                page.click("#yr-dlg [data-act=del]", timeout=T)
                page.wait_for_selector("#del-dlg[open]", timeout=T)
                page.wait_for_timeout(300)
                R["info"]["m1 title 1280"] = page.inner_text("#del-title", timeout=T)
                ok("1280 M1 copy", page.inner_text("#del-title") == 'Delete "Stretch 10 minutes"?' and page.inner_text("#del-body") == "Its history is deleted too.")
                shot(page, "m1-1280.png")
                page.mouse.click(6, 6)
                page.wait_for_timeout(300)
                ok("1280 M1 closes on the backdrop, P2 stays", page.locator("#del-dlg[open]").count() == 0 and page.locator("#yr-dlg[open]").count() == 1)
            page.keyboard.press("Escape")
            page.wait_for_timeout(250)
            ok(f"1280 P2 {name} closes on Esc", page.locator("#yr-dlg[open]").count() == 0)

        # delete for real from P2 and M1
        page.click('#list .row:nth-child(2) .btn-year', timeout=T)
        page.wait_for_selector("#yr-dlg[open]", timeout=T)
        page.click("#yr-dlg [data-act=del]", timeout=T)
        page.wait_for_selector("#del-dlg[open]", timeout=T)
        page.click("[data-act=confirm-del]", timeout=T)
        page.wait_for_timeout(400)
        names = [r["name"] for r in rows(page)]
        ok("1280 Delete habit removes the row and closes both popups", names == ["Read 20 pages", "No phone after 11pm"] and page.locator("dialog[open]").count() == 0, names)
        R["info"]["focus after delete"] = page.evaluate("() => document.activeElement.getAttribute('aria-label') || document.activeElement.id")

        # proto menu
        set_state(page, "k1")
        page.click("#proto-tab", timeout=T)
        page.wait_for_timeout(200)
        shot(page, "proto-menu-1280.png")
        page.keyboard.press("Escape")

        for s in ["s1", "s2-empty", "s2-long", "s2-dup", "s3", "s4", "s5"]:
            set_state(page, s)
            shot(page, f"{s}-1280.png")
            if s == "s3":
                ps = page_scroll(page)
                ok("1280 S3 page does not scroll", ps["scrollHeight"] <= ps["innerHeight"] and ps["scrollWidth"] <= ps["innerWidth"], ps)
                s3_input = rect(page, "#nh")
                ok("1280 add field does not move between K1 and S3", s3_input == k1_input, {"k1": k1_input, "s3": s3_input})
                fr = page.evaluate("() => { const f = document.querySelector('.frame'); return { scrollHeight: f.scrollHeight, clientHeight: f.clientHeight, rows: document.querySelectorAll('#list .row').length, fadeBelow: document.querySelector('#frame-wrap').classList.contains('more-below') }; }")
                ok("1280 S3 list frame scrolls and shows it", fr["rows"] == 12 and fr["scrollHeight"] > fr["clientHeight"] and fr["fadeBelow"], fr)
                ok("1280 S3 field and Add disabled", page.is_disabled("#nh") and page.is_disabled("#add-btn"))
                R["info"]["1280 proto S3"] = proto_overlaps(page)
                ok("1280 S3 proto tab overlaps no content", not R["info"]["1280 proto S3"]["overlaps"], R["info"]["1280 proto S3"])
                page.evaluate("() => { document.querySelector('.frame').scrollTop = 99999; }")
                page.wait_for_timeout(300)
                shot(page, "s3-1280-scrolled.png")
            if s.startswith("s2"):
                ok(f"1280 {s} add field does not move", rect(page, "#nh") == k1_input, rect(page, "#nh"))
            if s == "s4":
                R["info"]["1280 proto S4"] = proto_overlaps(page)
                ok("1280 S4 proto tab overlaps no content", not R["info"]["1280 proto S4"]["overlaps"])
                ps = page_scroll(page)
                ok("1280 S4 page does not scroll", ps["scrollHeight"] <= ps["innerHeight"], ps)

        # keyboard focus is visible
        set_state(page, "k1")
        page.focus('#list .row:nth-child(1) .btn-done')
        page.keyboard.press("Tab")
        page.wait_for_timeout(150)
        page.keyboard.press("Shift+Tab")
        page.wait_for_timeout(150)
        page.screenshot(path=str(HERE / "focus-1280.png"))
        R["shots"].append("focus-1280.png")
        R["info"]["focus outline"] = page.evaluate("() => { const s = getComputedStyle(document.activeElement); return s.outlineStyle + ' ' + s.outlineWidth + ' ' + s.outlineColor; }")

        tokens = page.evaluate("""() => { const s = getComputedStyle(document.documentElement); const o = {};
          for (const n of ['--bg','--surface','--surface-2','--raise','--field','--ink','--ink-soft','--amber','--amber-hover','--on-amber','--danger','--ring','--track','--focus','--line']) o[n] = s.getPropertyValue(n).trim();
          return o; }""")
        R["clipboard_writes"]["1280"] = page.evaluate("() => window.__clipWrites")
        return tokens
    finally:
        ctx.close()


def run_phone(browser, w, h, tag, full):
    ctx, page = new_page(browser, w, h, tag)
    try:
        load(page)
        shot(page, f"k1-{tag}.png")
        R["info"][f"numbers-{tag}"] = check_numbers(page, tag)
        ps = page_scroll(page)
        R["info"][f"{tag} K1 page scroll"] = ps
        ok(f"{tag} K1 page does not scroll", ps["scrollHeight"] <= ps["innerHeight"] and ps["scrollWidth"] <= ps["innerWidth"], ps)
        k1_input = rect(page, "#nh")
        R["info"][f"{tag} K1 add field"] = k1_input
        ok(f"{tag} add field pinned at the bottom", k1_input and abs((k1_input["y"] + k1_input["h"]) - (h - 12 - 12 - 1)) <= 2, k1_input)
        R["info"][f"{tag} proto K1"] = proto_overlaps(page)
        ok(f"{tag} K1 proto tab overlaps no content", not R["info"][f"{tag} proto K1"]["overlaps"], R["info"][f"{tag} proto K1"])
        if w == 360:
            R["overflow_360"]["k1"] = overflow(page, w)

        # Done today on Stretch: row and the Overview button ring update
        page.click('#list .row:nth-child(2) .btn-done', timeout=T)
        page.wait_for_timeout(400)
        r2 = {r["name"]: r for r in rows(page)}["Stretch 10 minutes"]
        sr = page.inner_text("#ov-btn-sr") if False else page.evaluate("() => document.querySelector('#ov-btn-sr').textContent")
        if full:
            shot(page, f"k1-{tag}-after-done-today.png")
        page.click("#ov-btn", timeout=T)
        page.wait_for_selector("#ov-dlg[open]", timeout=T)
        page.wait_for_timeout(350)
        lbl = today_cell_label(page, "o")
        ok(f"{tag} Done today updates the row and the overview", r2["doneToday"] and r2["current"] == 3 and "2 of 3" in sr and lbl.endswith("2 of 3 habits"), {"row": r2["text"], "button": sr, "popup today": lbl})
        R["info"][f"overview number size {tag}"] = page.evaluate(MEASURE, "#ov-grid .c-num")
        shot(page, f"p3-{tag}-after-done-today.png" if full else f"p3-{tag}.png")
        page.keyboard.press("Escape")
        page.wait_for_timeout(250)
        page.click('#list .row:nth-child(2) .btn-done', timeout=T)  # undo
        page.wait_for_timeout(250)

        # P3 overview popup, then P1 from one of its days
        page.click("#ov-btn", timeout=T)
        page.wait_for_selector("#ov-dlg[open]", timeout=T)
        page.wait_for_timeout(350)
        if full:
            shot(page, f"p3-{tag}.png")
        if w == 360:
            R["overflow_360"]["p3"] = overflow(page, w)
        page.click('#ov-grid [data-key="2026-09-22"]', timeout=T)
        page.wait_for_selector("#day-dlg[open]", timeout=T)
        page.wait_for_timeout(400)
        cell = rect(page, '#ov-grid [data-key="2026-09-22"]')
        sheet = rect(page, "#day-dlg .dlg-box")
        ok(f"{tag} P1 sheet leaves the chosen day in sight", cell["y"] + cell["h"] <= sheet["y"] + 1 and cell["y"] >= 0, {"cell": cell, "sheet": sheet})
        shot(page, f"p1-{tag}.png")
        lbl0 = page.get_attribute('#ov-grid [data-key="2026-09-22"]', "aria-label")
        page.click('#day-list .tick:has-text("Read 20 pages")', timeout=T)
        page.wait_for_timeout(400)
        lbl1 = page.get_attribute('#ov-grid [data-key="2026-09-22"]', "aria-label")
        ok(f"{tag} P1 tick updates the overview popup", lbl0.endswith("1 of 3 habits") and lbl1.endswith("2 of 3 habits"), [lbl0, lbl1])
        if full:
            shot(page, f"p1-{tag}-after-tick.png")
        if w == 360:
            R["overflow_360"]["p1"] = overflow(page, w)
        page.click('#day-list .tick:has-text("Read 20 pages")', timeout=T)  # undo
        page.wait_for_timeout(200)
        page.keyboard.press("Escape")
        page.wait_for_timeout(250)
        ok(f"{tag} Esc closes P1 first, P3 stays", page.locator("#day-dlg[open]").count() == 0 and page.locator("#ov-dlg[open]").count() == 1)
        page.click("#ov-dlg [data-act=close-ov]", timeout=T)
        page.wait_for_timeout(250)
        ok(f"{tag} P3 Close button closes it", page.locator("#ov-dlg[open]").count() == 0)

        # P2 year view on Stretch
        page.click('#list .row:nth-child(2) .btn-year', timeout=T)
        page.wait_for_selector("#yr-dlg[open]", timeout=T)
        page.wait_for_timeout(350)
        p2 = p2_numbers(page)
        hist = {x["name"]: x["done"] for x in histories(page)}
        ok(f"{tag} P2 numbers match history", (p2["current"], p2["best"]) == streaks(hist["Stretch 10 minutes"]) == (2, 5), p2)
        shot(page, f"p2-{tag}.png")
        if w == 360:
            R["overflow_360"]["p2"] = overflow(page, w)
        page.click('#months [data-key="2026-10-07"]', timeout=T)
        page.wait_for_timeout(400)
        p2b = p2_numbers(page)
        rowb = {r["name"]: r for r in rows(page)}["Stretch 10 minutes"]
        ok(f"{tag} P2 tick updates P2 and the row", p2b["current"] == 3 and rowb["current"] == 3, {"p2": p2b["text"], "row": rowb["text"]})
        if full:
            shot(page, f"p2-{tag}-after-tick.png")
            page.evaluate("() => { document.querySelector('#yr-body').scrollTop = 1500; }")
            page.wait_for_timeout(200)
            shot(page, f"p2-{tag}-scrolled.png")
        page.click('#months [data-key="2026-10-07"]', timeout=T)  # undo
        page.wait_for_timeout(250)
        # M1 from P2
        page.click("#yr-dlg [data-act=del]", timeout=T)
        page.wait_for_selector("#del-dlg[open]", timeout=T)
        page.wait_for_timeout(300)
        shot(page, f"m1-{tag}.png")
        page.keyboard.press("Escape")
        page.wait_for_timeout(250)
        ok(f"{tag} Esc closes M1, P2 stays", page.locator("#del-dlg[open]").count() == 0 and page.locator("#yr-dlg[open]").count() == 1)
        page.click("#yr-dlg [data-act=close-year]", timeout=T)
        page.wait_for_timeout(250)
        ok(f"{tag} P2 Close button closes it", page.locator("#yr-dlg[open]").count() == 0)

        if full:
            page.click("#proto-tab", timeout=T)
            page.wait_for_timeout(200)
            shot(page, f"proto-menu-{tag}.png")
            page.keyboard.press("Escape")

        states = ["s1", "s2-empty", "s2-long", "s2-dup", "s3", "s4", "s5"] if full else ["s1", "s2-long", "s3", "s4"]
        for s in states:
            set_state(page, s)
            shot(page, f"{s}-{tag}.png")
            if w == 360:
                R["overflow_360"][s] = overflow(page, w)
            if s == "s3":
                s3_input = rect(page, "#nh")
                ok(f"{tag} add field does not move between K1 and S3", s3_input == k1_input, {"k1": k1_input, "s3": s3_input})
                ps = page_scroll(page)
                ok(f"{tag} S3 page does not scroll", ps["scrollHeight"] <= ps["innerHeight"] and ps["scrollWidth"] <= ps["innerWidth"], ps)
                fr = page.evaluate("() => { const f = document.querySelector('.frame'); return { scrollHeight: f.scrollHeight, clientHeight: f.clientHeight, rows: document.querySelectorAll('#list .row').length, fadeBelow: document.querySelector('#frame-wrap').classList.contains('more-below') }; }")
                ok(f"{tag} S3 list frame scrolls and shows it", fr["rows"] == 12 and fr["scrollHeight"] > fr["clientHeight"] and fr["fadeBelow"], fr)
                R["info"][f"{tag} proto S3"] = proto_overlaps(page)
                ok(f"{tag} S3 proto tab overlaps no content", not R["info"][f"{tag} proto S3"]["overlaps"], R["info"][f"{tag} proto S3"])
            if s.startswith("s2"):
                ok(f"{tag} {s} add field does not move", rect(page, "#nh") == k1_input, rect(page, "#nh"))
            if s == "s4":
                R["info"][f"{tag} proto S4"] = proto_overlaps(page)
                ok(f"{tag} S4 proto tab overlaps no content", not R["info"][f"{tag} proto S4"]["overlaps"])
        R["clipboard_writes"][tag] = page.evaluate("() => window.__clipWrites")
    finally:
        ctx.close()


def round1_number_sizes(browser):
    out = {}
    for w, h, tag in ((1280, 800, "1280"), (390, 844, "390")):
        ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1)
        try:
            page = ctx.new_page()
            page.goto(D_PAGE.as_uri(), timeout=T)
            page.wait_for_selector(".hc .c-num", timeout=T)
            out[tag] = page.evaluate(MEASURE, ".hc .c-num")
        finally:
            ctx.close()
    return out


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            tk = run_1280(browser)
            run_phone(browser, 390, 844, "390", True)
            run_phone(browser, 360, 780, "360", False)
            R["info"]["round 1 overview number size"] = round1_number_sizes(browser)
            ctx, page = new_page(browser, 390, 844, "reduced", reduced=True)
            try:
                load(page)
                page.click('#list .row:nth-child(2) .btn-done', timeout=T)
                page.wait_for_timeout(200)
                R["info"]["reduced motion animation on the tapped dot"] = page.evaluate("() => getComputedStyle(document.querySelector('#list .row:nth-child(2) .btn-done .dot')).animationName")
            finally:
                ctx.close()
        finally:
            browser.close()

    f1280 = R["info"]["overview number size 1280"]["renderedPx"]
    f390 = R["info"]["overview number size 390"]["renderedPx"]
    r1 = R["info"]["round 1 overview number size"]
    ok("overview numbers bigger than round 1 at 1280", f1280 > r1["1280"]["renderedPx"], {"round 2": f1280, "round 1": r1["1280"]["renderedPx"]})
    ok("overview numbers bigger than round 1 at 390", f390 > r1["390"]["renderedPx"], {"round 2": f390, "round 1": r1["390"]["renderedPx"]})

    for name in ("360", "k1"):
        pass
    o = R["overflow_360"]
    ok("360 no sideways scroll and nothing past the viewport", all(v["scrollWidth"] <= v["clientWidth"] and not v["poking"] for v in o.values()), o)
    ok("console errors 0", not R["console_errors"] and not R["page_errors"], R["console_errors"] + R["page_errors"])
    ok("no network requests", not R["requests_off_file"], R["requests_off_file"])
    ok("no clipboard writes", all(not v for v in R["clipboard_writes"].values()), R["clipboard_writes"])

    pairs = [
        ("ink on bg (body text)", "--ink", "--bg", 4.5),
        ("ink on surface (habit names)", "--ink", "--surface", 4.5),
        ("ink on surface-2 (dialog text)", "--ink", "--surface-2", 4.5),
        ("ink-soft on bg (date)", "--ink-soft", "--bg", 4.5),
        ("ink-soft on surface (labels, overview numbers)", "--ink-soft", "--surface", 4.5),
        ("ink-soft on surface-2 (dialog labels)", "--ink-soft", "--surface-2", 4.5),
        ("amber on bg (accent)", "--amber", "--bg", 4.5),
        ("amber on surface (Current on a row)", "--amber", "--surface", 4.5),
        ("amber on surface-2 (Current in P2)", "--amber", "--surface-2", 4.5),
        ("on-amber on amber (Done today, Add, done numbers)", "--on-amber", "--amber", 4.5),
        ("on-amber on danger (Delete habit in M1)", "--on-amber", "--danger", 4.5),
        ("danger on surface (field error)", "--danger", "--surface", 4.5),
        ("ink-soft on surface-2 (Delete habit in P2 at rest)", "--ink-soft", "--surface-2", 4.5),
        ("danger on surface-2 (Delete habit in P2 on hover)", "--danger", "--surface-2", 4.5),
        ("ring on surface (not-done outline, 3:1)", "--ring", "--surface", 3.0),
        ("ring on surface-2 (not-done bead in P2, 3:1)", "--ring", "--surface-2", 3.0),
        ("ring on bg (Overview button edge, 3:1)", "--ring", "--bg", 3.0),
        ("ring on field (input border, 3:1)", "--ring", "--field", 3.0),
        ("focus on bg", "--focus", "--bg", 3.0),
        ("focus on surface-2", "--focus", "--surface-2", 3.0),
    ]
    for label, a, b, need in pairs:
        rt = ratio(tk[a], tk[b])
        R["contrast"][label] = {"fg": tk[a], "bg": tk[b], "ratio": rt, "needs": need}
        ok(f"contrast {label}", rt >= need, rt)

    failed = [k for k, v in R["asserts"].items() if not v["pass"]]
    R["summary"] = {"asserts": len(R["asserts"]), "failed": failed, "shots": len(R["shots"])}
    out = HERE / "results.json"
    out.write_text(json.dumps(R, indent=2), encoding="utf-8")
    print(json.dumps(R["summary"], indent=2))
    for k in failed:
        print("FAIL", k, json.dumps(R["asserts"][k]["detail"])[:600])


if __name__ == "__main__":
    main()
