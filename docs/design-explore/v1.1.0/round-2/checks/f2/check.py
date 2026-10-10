"""Render check for round-2 direction F2 (Orbit List, revised). Headless Chromium, file:/// URL, no server, no network.

Starts from checks/f/check.py: every F assert that still applies is kept. Added: P4 (the overview's year view, every
habit together) and the bin button on every habit row.
Writes screenshots and results.json beside this file only. Every wait is bounded, the browser closes in a finally block.
"""
import datetime as dt
import json
import pathlib
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
PAGE = HERE.parent.parent / "f2.html"
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
LONG_NAME = "Stretch hamstrings and calves for 10 min"  # 40 characters, the most the field takes

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


# ---------- geometry ----------
def overlap(a, b):
    ix = min(a["x"] + a["w"], b["x"] + b["w"]) - max(a["x"], b["x"])
    iy = min(a["y"] + a["h"], b["y"] + b["h"]) - max(a["y"], b["y"])
    return ix > 0.5 and iy > 0.5


def gap(a, b):
    dx = max(0.0, max(a["x"], b["x"]) - min(a["x"] + a["w"], b["x"] + b["w"]))
    dy = max(0.0, max(a["y"], b["y"]) - min(a["y"] + a["h"], b["y"] + b["h"]))
    return round((dx * dx + dy * dy) ** 0.5, 2)


# ---------- page helpers ----------
def shot(page, name, full=False):
    page.mouse.move(1, 1)
    page.wait_for_timeout(150)
    path = HERE / name
    page.screenshot(path=str(path), full_page=full)
    R["shots"].append(name)


def shot_here(page, name):
    """A screenshot that keeps the pointer where it is (for hover states)."""
    page.wait_for_timeout(250)
    page.screenshot(path=str(HERE / name))
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


def p1_stats(page):
    return page.evaluate("""() => [...document.querySelectorAll('#day-list .tick')].map(t => {
        const s = t.querySelector('.tstat').innerText;
        const c = s.match(/Current (\\d+)/), b = s.match(/Best (\\d+)/);
        return { name: t.querySelector('.tname').textContent, current: c ? Number(c[1]) : 0, best: b ? Number(b[1]) : 0,
                 on: t.getAttribute('aria-pressed') === 'true' };
    })""")


def histories(page):
    return page.evaluate("() => window.__streaky.histories()")


def page_scroll(page):
    return page.evaluate("""() => { const d = document.scrollingElement;
        return { scrollHeight: d.scrollHeight, innerHeight: innerHeight, scrollWidth: d.scrollWidth, innerWidth: innerWidth }; }""")


def rect(page, sel):
    return page.evaluate("(s) => { const e = document.querySelector(s); if (!e) return null; const r = e.getBoundingClientRect(); return {x: r.x, y: r.y, w: r.width, h: r.height}; }", sel)


def visible(page, sel):
    return page.evaluate("(s) => { const e = document.querySelector(s); if (!e) return false; const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0 && getComputedStyle(e).visibility !== 'hidden'; }", sel)


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

# every ring in a grid against the histories: one segment per habit in list order, the core when all are done, the label count
RINGS_VS_HISTORY = """(sel) => {
    const hist = window.__streaky.histories(), sets = hist.map(h => new Set(h.done)), N = sets.length, bad = [];
    let n = 0;
    for (const b of document.querySelectorAll(sel + ' button.hc')) {
      n++;
      const k = b.dataset.key, want = sets.map(s => s.has(k)), cnt = want.filter(Boolean).length;
      const segs = [...b.querySelectorAll('.seg')].map(s => s.classList.contains('on'));
      const segOk = N <= 1 ? true : JSON.stringify(segs) === JSON.stringify(want);
      const lblOk = b.getAttribute('aria-label').endsWith(', ' + cnt + ' of ' + N + ' habits');
      const coreOk = !!b.querySelector('.c-core') === (N > 0 && cnt === N);
      if (!segOk || !lblOk || !coreOk) bad.push(k);
    }
    return { buttons: n, mismatches: bad.length, first: bad.slice(0, 8) };
}"""

P4_COUNTS = """() => {
    const btns = [...document.querySelectorAll('#all-months button.hc')], keys = btns.map(b => b.dataset.key).sort();
    const closed = [...document.querySelectorAll('#all-months .hc.closed')];
    const months = [...document.querySelectorAll('#all-months .month h3')].map(h => h.textContent);
    const oct25 = [...document.querySelectorAll('#all-months .month')].find(m => m.querySelector('h3').textContent === 'October 2025');
    return { buttons: btns.length, closed: closed.length, closedDays: closed.map(e => e.textContent.trim()),
             closedButtons: document.querySelectorAll('#all-months button.hc.closed').length,
             blank: document.querySelectorAll('#all-months .hc.blank').length,
             oct25FirstButton: oct25 ? oct25.querySelector('button.hc').dataset.key : null,
             months: months, first: keys[0], last: keys[keys.length - 1],
             today: (document.querySelector('#all-months [aria-current="date"]') || {}).dataset?.key || null,
             sampleLabel: document.querySelector('#all-months [data-key="2025-11-03"]')?.getAttribute('aria-label') || null };
}"""

P4_TARGETS = """() => { let small = 0, min = 999; for (const b of document.querySelectorAll('#all-months button.hc')) {
    const r = b.getBoundingClientRect(); min = Math.min(min, r.width, r.height); if (r.width < 43.5 || r.height < 43.5) small++; }
    return { small, min: Math.round(min * 100) / 100 }; }"""

ROW_GEOM = """() => [...document.querySelectorAll('#list .row')].map(r => {
    const q = s => { const e = r.querySelector(s); if (!e) return null; const b = e.getBoundingClientRect(); return { x: b.x, y: b.y, w: b.width, h: b.height }; };
    const rr = r.getBoundingClientRect(), bin = r.querySelector('.btn-bin');
    return { name: r.querySelector('.r-name').textContent, row: { x: rr.x, y: rr.y, w: rr.width, h: rr.height },
             parts: { name: q('.r-name'), bin: q('.btn-bin'), stats: q('.stats'), year: q('.btn-year'), done: q('.btn-done') },
             binLabel: bin ? bin.getAttribute('aria-label') : null };
})"""


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


def check_rows(page, tag, need_gap=12.0):
    """Every row control at least 44 px, nothing overlaps, nothing leaves the row, the bin named for its habit and apart from Done today."""
    geo = page.evaluate(ROW_GEOM)
    problems, min_gap = [], 9999.0
    for g in geo:
        p, row = g["parts"], g["row"]
        for k in ("bin", "year", "done"):
            if p[k] is None or p[k]["w"] < 43.5 or p[k]["h"] < 43.5:
                problems.append(f"{g['name']}: {k} under 44 px {p[k]}")
        keys = list(p)
        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                if p[keys[i]] and p[keys[j]] and overlap(p[keys[i]], p[keys[j]]):
                    problems.append(f"{g['name']}: {keys[i]} overlaps {keys[j]}")
        for k, v in p.items():
            if v and (v["x"] < row["x"] - 0.5 or v["x"] + v["w"] > row["x"] + row["w"] + 0.5):
                problems.append(f"{g['name']}: {k} leaves the row")
        if g["binLabel"] != f'Delete "{g["name"]}"':
            problems.append(f"{g['name']}: bin label {g['binLabel']}")
        if p["bin"] and p["done"]:
            min_gap = min(min_gap, gap(p["bin"], p["done"]))
    info = {"rows": len(geo), "problems": problems, "bin_to_done_min_gap_px": min_gap,
            "sample": geo[0] if geo else None}
    R["info"][f"row geometry {tag}"] = info
    ok(f"{tag} row controls 44 px, no overlap, inside the row, bin named", len(geo) > 0 and not problems, problems[:10])
    ok(f"{tag} bin sits apart from Done today (gap >= {need_gap} px)", min_gap >= need_gap, min_gap)
    return info


def today_cell_label(page, pfx):
    return page.get_attribute(f'[data-fk="{pfx}-2026-10-10"]', "aria-label", timeout=T)


def focused(page):
    return page.evaluate("() => { const a = document.activeElement; return a ? (a.getAttribute('aria-label') || a.id || a.textContent.trim()) : null; }")


def check_p4(page, tag):
    c = page.evaluate(P4_COUNTS)
    R["info"][f"p4 counts {tag}"] = c
    ok(f"{tag} P4 shows 366 day buttons", c["buttons"] == 366 and c["first"] == "2025-10-10" and c["last"] == "2026-10-10", {k: c[k] for k in ("buttons", "first", "last")})
    ok(f"{tag} P4 closes the 21 days after today and they cannot be tapped", c["closed"] == 21 and c["closedButtons"] == 0 and c["closedDays"] == [str(d) for d in range(11, 32)], {"closed": c["closed"], "days": c["closedDays"]})
    ok(f"{tag} P4 leaves 1 to 9 October 2025 blank", c["blank"] == 9 and c["oct25FirstButton"] == "2025-10-10", {"blank": c["blank"], "first Oct 2025 button": c["oct25FirstButton"]})
    ok(f"{tag} P4 months newest first, October 2026 to October 2025", len(c["months"]) == 13 and c["months"][0] == "October 2026" and c["months"][-1] == "October 2025", c["months"])
    ok(f"{tag} P4 today marked", c["today"] == "2026-10-10", c["today"])
    rv = page.evaluate(RINGS_VS_HISTORY, "#all-months")
    ok(f"{tag} P4 every ring equals the histories", rv["buttons"] == 366 and rv["mismatches"] == 0, rv)
    copy = page.evaluate("() => ({ title: document.querySelector('#all-title').textContent, sub: document.querySelector('#all-sub').textContent, hint: document.querySelector('#all-dlg .hint').textContent, legend: document.querySelector('#all-legend').textContent })")
    ok(f"{tag} P4 copy", copy == {"title": "All habits", "sub": "The last 12 months", "hint": "Tap a day to change it.", "legend": "NoneAll"}, copy)
    size = page.evaluate(MEASURE, "#all-months button.hc .c-num")
    R["info"][f"p4 number size {tag}"] = size
    ok(f"{tag} P4 day numbers no smaller than the overview's 16 px", size and size["renderedPx"] >= 15.99, size)
    tg = page.evaluate(P4_TARGETS)
    R["info"][f"p4 targets {tag}"] = tg
    return c, tg


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
        R["info"]["1280 K1 add field"] = k1_input
        R["info"]["1280 K1 frame"] = rect(page, ".frame")
        R["info"]["1280 proto K1"] = proto_overlaps(page)
        ok("1280 K1 proto tab overlaps no content", not R["info"]["1280 proto K1"]["overlaps"], R["info"]["1280 proto K1"])
        R["info"]["overview number size 1280"] = page.evaluate(MEASURE, "#band-grid .c-num")
        R["info"]["band height 1280"] = rect(page, "#band")
        rv = page.evaluate(RINGS_VS_HISTORY, "#band-grid")
        ok("1280 overview band rings equal the histories", rv["buttons"] == 83 and rv["mismatches"] == 0, rv)
        check_rows(page, "1280 K1")
        fr = page.evaluate("() => { const f = document.querySelector('.frame'); return { scrollHeight: f.scrollHeight, clientHeight: f.clientHeight }; }")
        ok("1280 K1 three rows fit the frame without scrolling", fr["scrollHeight"] <= fr["clientHeight"], fr)

        # the band's Year button: in the band's header line, beside the title, never in the ring grid
        by, meta, grid, title = rect(page, "#band-yr"), rect(page, ".band-meta"), rect(page, "#band-grid"), rect(page, "#h-ov")
        R["info"]["1280 band Year button"] = {"button": by, "meta": meta, "grid": grid, "title": title}
        ok("1280 band Year button sits in the header line, not in the grid",
           by and by["x"] + by["w"] <= meta["x"] + meta["w"] + 0.5 and by["x"] + by["w"] <= grid["x"] and abs((by["y"] + by["h"] / 2) - (title["y"] + title["h"] / 2)) <= 2 and by["h"] >= 44,
           R["info"]["1280 band Year button"])
        ok("1280 band Year button named", page.get_attribute("#band-yr", "aria-label") == "Year view, all habits" and page.inner_text("#band-yr") == "Year")
        ok("1280 P3 not reachable on a desktop (Overview button hidden)", not visible(page, "#ov-btn"))

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

        # ---------- P4 from the band ----------
        page.click("#band-yr", timeout=T)
        page.wait_for_selector("#all-dlg[open]", timeout=T)
        page.wait_for_timeout(350)
        ok("1280 P4 opens from the band's Year button", page.locator("#all-dlg[open]").count() == 1)
        shot(page, "p4-1280.png")
        check_p4(page, "1280")
        dl = page.evaluate("() => { const b = document.querySelector('#all-dlg .dlg-box').getBoundingClientRect(), s = document.querySelector('#all-body'); return { box: { x: b.x, y: b.y, w: b.width, h: b.height }, bodyScrolls: s.scrollHeight > s.clientHeight, monthsAcross: getComputedStyle(document.querySelector('#all-months')).gridTemplateColumns.split(' ').length }; }")
        R["info"]["p4 dialog 1280"] = dl
        ok("1280 P4 is a centred dialog, months across, inner scroll", dl["box"]["x"] > 0 and abs((dl["box"]["x"] + dl["box"]["w"] / 2) - 640) <= 1 and dl["monthsAcross"] == 3 and dl["bodyScrolls"], dl)
        ps = page_scroll(page)
        ok("1280 page does not scroll with P4 open", ps["scrollHeight"] <= ps["innerHeight"] and ps["scrollWidth"] <= ps["innerWidth"], ps)
        page.evaluate("() => { document.querySelector('#all-body').scrollTop = 99999; }")
        page.wait_for_timeout(200)
        shot(page, "p4-1280-scrolled.png")
        page.evaluate("() => { document.querySelector('#all-body').scrollTop = 0; }")

        # a P4 day opens P1 for that date; a tick there updates P4, the band and the row at once
        hist = {h["name"]: h["done"] for h in histories(page)}
        a0 = page.get_attribute('#all-months [data-key="2026-09-22"]', "aria-label")
        page.click('#all-months [data-key="2026-09-22"]', timeout=T)
        page.wait_for_selector("#day-dlg[open]", timeout=T)
        page.wait_for_timeout(350)
        ok("1280 a P4 day opens P1 for that date", page.inner_text("#day-title") == "Tuesday 22 September" and page.locator("#all-dlg[open]").count() == 1, page.inner_text("#day-title"))
        p1s = {x["name"]: x for x in p1_stats(page)}
        ok("1280 P1 from P4 shows Current and Best equal to the histories", all((p1s[n]["current"], p1s[n]["best"]) == streaks(hist[n]) == EXPECTED[n] for n in EXPECTED), p1s)
        shot(page, "p4-p1-1280.png")
        page.click('#day-list .tick:has-text("Read 20 pages")', timeout=T)
        page.wait_for_timeout(400)
        a1 = page.get_attribute('#all-months [data-key="2026-09-22"]', "aria-label")
        b1 = page.get_attribute('#band-grid [data-key="2026-09-22"]', "aria-label")
        segs = page.evaluate("() => [...document.querySelectorAll('#all-months [data-key=\"2026-09-22\"] .seg')].map(s => s.classList.contains('on'))")
        ok("1280 P1 tick changes the matching ring in P4 and the overview", a0.endswith("1 of 3 habits") and a1.endswith("2 of 3 habits") and b1.endswith("2 of 3 habits") and segs[0] is True,
           {"p4 before": a0, "p4 after": a1, "band after": b1, "p4 segments": segs})
        rv4 = page.evaluate(RINGS_VS_HISTORY, "#all-months")
        rvb = page.evaluate(RINGS_VS_HISTORY, "#band-grid")
        ok("1280 after the tick P4 and the band still equal the histories", rv4["mismatches"] == 0 and rvb["mismatches"] == 0, {"p4": rv4, "band": rvb})
        # Esc closes the top layer first: P1, then P4
        page.keyboard.press("Escape")
        page.wait_for_timeout(250)
        ok("1280 Esc closes P1 first, P4 stays", page.locator("#day-dlg[open]").count() == 0 and page.locator("#all-dlg[open]").count() == 1)
        # today in P1 from P4: every Current at once
        page.click('#all-months [data-key="2026-10-10"]', timeout=T)
        page.wait_for_selector("#day-dlg[open]", timeout=T)
        page.wait_for_timeout(300)
        page.click('#day-list .tick:has-text("Stretch 10 minutes")', timeout=T)
        page.wait_for_timeout(400)
        rs = {r["name"]: r for r in rows(page)}["Stretch 10 minutes"]
        p1t = {x["name"]: x for x in p1_stats(page)}["Stretch 10 minutes"]
        at = page.get_attribute('#all-months [data-key="2026-10-10"]', "aria-label")
        bt = today_cell_label(page, "b")
        ok("1280 a tick for today in P1 over P4 updates the row, P1, P4 and the band", rs["current"] == 3 and rs["doneToday"] and p1t["current"] == 3 and at.endswith("2 of 3 habits") and bt.endswith("2 of 3 habits"),
           {"row": rs["text"], "p1": p1t, "p4": at, "band": bt})
        page.click('#day-list .tick:has-text("Stretch 10 minutes")', timeout=T)  # undo
        page.wait_for_timeout(250)
        page.keyboard.press("Escape")
        page.wait_for_timeout(250)
        page.keyboard.press("Escape")
        page.wait_for_timeout(300)
        ok("1280 Esc then closes P4 and focus returns to the band's Year button", page.locator("dialog[open]").count() == 0 and focused(page) == "Year view, all habits", focused(page))
        # the backdrop closes P4 too
        page.click("#band-yr", timeout=T)
        page.wait_for_selector("#all-dlg[open]", timeout=T)
        page.wait_for_timeout(300)
        page.mouse.click(6, 6)
        page.wait_for_timeout(300)
        ok("1280 P4 closes on the backdrop", page.locator("#all-dlg[open]").count() == 0)
        page.click("#band-yr", timeout=T)
        page.wait_for_selector("#all-dlg[open]", timeout=T)
        page.click("#all-dlg [data-act=close-all]", timeout=T)
        page.wait_for_timeout(250)
        ok("1280 P4 Close button closes it", page.locator("#all-dlg[open]").count() == 0)

        # the tick made in P1 over P4 reads the same in P2, and a P2 untick reads back in the band
        page.click('#list .row:nth-child(1) .btn-year', timeout=T)
        page.wait_for_selector("#yr-dlg[open]", timeout=T)
        page.wait_for_timeout(300)
        pressed = page.get_attribute('#months [data-key="2026-09-22"]', "aria-pressed")
        hist = {h["name"]: h["done"] for h in histories(page)}
        p2r = p2_numbers(page)
        ok("1280 P2 shows the day ticked in P1 over P4, numbers equal the histories", pressed == "true" and (p2r["current"], p2r["best"]) == streaks(hist["Read 20 pages"]), {"pressed": pressed, "p2": p2r["text"]})
        page.click('#months [data-key="2026-09-22"]', timeout=T)  # undo through P2
        page.wait_for_timeout(300)
        ok("1280 a P2 untick reads back in the band", page.get_attribute('#band-grid [data-key="2026-09-22"]', "aria-label").endswith("1 of 3 habits"))
        page.keyboard.press("Escape")
        page.wait_for_timeout(250)

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

        # delete for real from P2 and M1 (Delete habit in P2 stays)
        page.click('#list .row:nth-child(2) .btn-year', timeout=T)
        page.wait_for_selector("#yr-dlg[open]", timeout=T)
        page.click("#yr-dlg [data-act=del]", timeout=T)
        page.wait_for_selector("#del-dlg[open]", timeout=T)
        page.click("[data-act=confirm-del]", timeout=T)
        page.wait_for_timeout(400)
        names = [r["name"] for r in rows(page)]
        ok("1280 Delete habit removes the row and closes both popups", names == ["Read 20 pages", "No phone after 11pm"] and page.locator("dialog[open]").count() == 0, names)
        R["info"]["focus after delete from P2"] = focused(page)
        ok("1280 after a delete from P2 focus moves to the next row's Year button (F reading 18)", focused(page) == "Year view, No phone after 11pm", focused(page))

        # ---------- the bin on every row ----------
        set_state(page, "k1")
        # quiet at rest, the danger colour on hover and on keyboard focus, never a red fill
        rest = page.evaluate("() => { const s = getComputedStyle(document.querySelector('#list .row:nth-child(1) .btn-bin')); return { color: s.color, bg: s.backgroundColor, border: s.borderTopColor }; }")
        page.hover('#list .row:nth-child(1) .btn-bin', timeout=T)
        page.wait_for_timeout(300)
        hov = page.evaluate("() => { const s = getComputedStyle(document.querySelector('#list .row:nth-child(1) .btn-bin')); return { color: s.color, bg: s.backgroundColor, border: s.borderTopColor }; }")
        shot_here(page, "bin-hover-1280.png")
        page.mouse.move(1, 1)
        page.focus('#list .row:nth-child(1) .btn-year')
        page.keyboard.press("Shift+Tab")
        page.wait_for_timeout(250)
        foc = page.evaluate("() => { const a = document.activeElement, s = getComputedStyle(a); return { label: a.getAttribute('aria-label'), color: s.color, bg: s.backgroundColor, outline: s.outlineStyle + ' ' + s.outlineWidth + ' ' + s.outlineColor, focusVisible: a.matches(':focus-visible') }; }")
        shot_here(page, "bin-focus-1280.png")
        R["info"]["bin states 1280"] = {"rest": rest, "hover": hov, "focus": foc}
        ok("1280 bin grey at rest, danger on hover and focus, never a red fill",
           rest["color"] == "rgb(168, 171, 178)" and hov["color"] == "rgb(255, 107, 102)" and hov["border"] == "rgb(255, 107, 102)" and foc["color"] == "rgb(255, 107, 102)"
           and foc["focusVisible"] and foc["outline"].startswith("solid 2px") and all(x["bg"] in ("rgba(0, 0, 0, 0)", "transparent") for x in (rest, hov, foc)),
           R["info"]["bin states 1280"])
        ok("1280 bin comes before Year in the tab order of its row", foc["label"] == 'Delete "Read 20 pages"', foc["label"])

        # each row's bin opens M1 with that habit's name; Esc returns focus to the bin
        for i, name in enumerate(EXPECTED, start=1):
            page.click(f'#list .row:nth-child({i}) .btn-bin', timeout=T)
            page.wait_for_selector("#del-dlg[open]", timeout=T)
            page.wait_for_timeout(300)
            t, b = page.inner_text("#del-title"), page.inner_text("#del-body")
            btns = page.evaluate("() => [...document.querySelectorAll('#del-dlg .dlg-actions button')].map(b => b.textContent.trim())")
            ok(f"1280 row bin opens M1 for {name}", t == f'Delete "{name}"?' and b == "Its history is deleted too." and btns == ["Cancel", "Delete habit"] and focused(page) == "del-cancel", {"title": t, "buttons": btns, "focus": focused(page)})
            if i == 2:
                shot(page, "m1-row-1280.png")
            page.keyboard.press("Escape")
            page.wait_for_timeout(300)
            ok(f"1280 Esc closes M1 from the {name} bin and focus returns to it", page.locator("#del-dlg[open]").count() == 0 and focused(page) == f'Delete "{name}"', focused(page))
        # Cancel keeps the habit
        page.click('#list .row:nth-child(1) .btn-bin', timeout=T)
        page.wait_for_selector("#del-dlg[open]", timeout=T)
        page.click("#del-cancel", timeout=T)
        page.wait_for_timeout(300)
        ok("1280 Cancel keeps the habit", len(rows(page)) == 3 and page.locator("dialog[open]").count() == 0)

        # delete from the rows: next row's bin, then the previous row's when the last went, then the add field
        page.click('#list .row:nth-child(2) .btn-bin', timeout=T)
        page.wait_for_selector("#del-dlg[open]", timeout=T)
        page.click("[data-act=confirm-del]", timeout=T)
        page.wait_for_timeout(400)
        names = [r["name"] for r in rows(page)]
        f1 = focused(page)
        shot(page, "k1-1280-after-row-delete.png")
        rv = page.evaluate(RINGS_VS_HISTORY, "#band-grid")
        ok("1280 a row delete removes the row and the overview redraws from the histories", names == ["Read 20 pages", "No phone after 11pm"] and page.locator("dialog[open]").count() == 0 and rv["mismatches"] == 0, {"names": names, "band": rv})
        ok("1280 after a row delete focus moves to the next row's bin", f1 == 'Delete "No phone after 11pm"', f1)
        page.click('#list .row:nth-child(2) .btn-bin', timeout=T)
        page.wait_for_selector("#del-dlg[open]", timeout=T)
        page.click("[data-act=confirm-del]", timeout=T)
        page.wait_for_timeout(400)
        f2 = focused(page)
        ok("1280 when the last row goes focus moves to the previous row's bin", [r["name"] for r in rows(page)] == ["Read 20 pages"] and f2 == 'Delete "Read 20 pages"', f2)
        page.keyboard.press("Enter")  # the focused bin opens M1 from the keyboard
        page.wait_for_selector("#del-dlg[open]", timeout=T)
        page.click("[data-act=confirm-del]", timeout=T)
        page.wait_for_timeout(400)
        f3 = page.evaluate("() => document.activeElement.id")
        ok("1280 when the list empties focus moves to the add field", page.locator("#list .row").count() == 0 and page.locator("#list .empty").count() == 1 and f3 == "nh", f3)

        # S3: the bin is the short way to make room
        set_state(page, "s3")
        page.click('#list .row:nth-child(4) .btn-bin', timeout=T)
        page.wait_for_selector("#del-dlg[open]", timeout=T)
        page.click("[data-act=confirm-del]", timeout=T)
        page.wait_for_timeout(400)
        ok("1280 S3 a row delete re-enables the add field", len(rows(page)) == 11 and not page.is_disabled("#nh") and not page.is_disabled("#add-btn") and focused(page) == 'Delete "Walk 8,000 steps"', focused(page))

        # a 40-character name
        set_state(page, "k1")
        page.fill("#nh", LONG_NAME)
        page.click("#add-btn", timeout=T)
        page.wait_for_timeout(400)
        check_rows(page, "1280 long name")
        shot(page, "k1-1280-long-name.png")

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
                ok("1280 S3 copy", page.inner_text("#nh-msg") == "You track 12 habits, the most this app holds. Delete one to add another.")
                R["info"]["1280 proto S3"] = proto_overlaps(page)
                ok("1280 S3 proto tab overlaps no content", not R["info"]["1280 proto S3"]["overlaps"], R["info"]["1280 proto S3"])
                check_rows(page, "1280 S3")
                page.click("#band-yr", timeout=T)
                page.wait_for_selector("#all-dlg[open]", timeout=T)
                page.wait_for_timeout(300)
                rv = page.evaluate(RINGS_VS_HISTORY, "#all-months")
                ok("1280 S3 P4 draws twelve segments per ring from the histories", rv["buttons"] == 366 and rv["mismatches"] == 0, rv)
                shot(page, "p4-1280-s3.png")
                page.keyboard.press("Escape")
                page.wait_for_timeout(250)
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
            if s == "s1":
                page.click("#band-yr", timeout=T)
                page.wait_for_selector("#all-dlg[open]", timeout=T)
                page.wait_for_timeout(300)
                c = page.evaluate(P4_COUNTS)
                ok("1280 S1 P4 opens with empty rings", c["buttons"] == 366 and page.locator("#all-months .seg.on").count() == 0, c["buttons"])
                page.keyboard.press("Escape")
                page.wait_for_timeout(250)

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
          for (const n of ['--bg','--surface','--surface-2','--raise','--field','--ink','--ink-soft','--amber','--amber-hover','--on-amber','--danger','--ring','--track','--focus','--line','--closed']) o[n] = s.getPropertyValue(n).trim();
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
        check_rows(page, f"{tag} K1")
        ok(f"{tag} the band (and its Year button) is hidden on a phone", not visible(page, "#band-yr"))
        if w == 360:
            R["overflow_360"]["k1"] = overflow(page, w)

        # Done today on Stretch: row and the Overview button ring update
        page.click('#list .row:nth-child(2) .btn-done', timeout=T)
        page.wait_for_timeout(400)
        r2 = {r["name"]: r for r in rows(page)}["Stretch 10 minutes"]
        sr = page.evaluate("() => document.querySelector('#ov-btn-sr').textContent")
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
        yb, cl = rect(page, "#ov-yr"), rect(page, "#ov-dlg [data-act=close-ov]")
        R["info"][f"{tag} P3 Year button"] = {"year": yb, "close": cl}
        ok(f"{tag} P3 Year button sits in P3's header beside Close", yb and cl and abs(yb["y"] - cl["y"]) <= 1 and yb["x"] + yb["w"] <= cl["x"] and yb["h"] >= 44 and yb["w"] >= 44 and
           page.get_attribute("#ov-yr", "aria-label") == "Year view, all habits" and page.inner_text("#ov-yr") == "Year", R["info"][f"{tag} P3 Year button"])
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

        # ---------- P4 from P3 ----------
        page.click("#ov-yr", timeout=T)
        page.wait_for_selector("#all-dlg[open]", timeout=T)
        page.wait_for_timeout(400)
        box = rect(page, "#all-dlg .dlg-box")
        ok(f"{tag} P4 opens from P3 as a full-screen sheet over it", page.locator("#ov-dlg[open]").count() == 1 and box and box["x"] == 0 and box["y"] == 0 and abs(box["w"] - w) <= 0.5 and abs(box["h"] - h) <= 0.5, box)
        shot(page, f"p4-{tag}.png")
        c, tg = check_p4(page, tag)
        ok(f"{tag} P4 one month across, every day a 44 px target", page.evaluate("() => getComputedStyle(document.querySelector('#all-months')).gridTemplateColumns.split(' ').length") == 1 and tg["small"] == 0, tg)
        if w == 360:
            R["overflow_360"]["p4"] = overflow(page, w)
        ps = page_scroll(page)
        ok(f"{tag} page does not scroll with P4 open", ps["scrollHeight"] <= ps["innerHeight"] and ps["scrollWidth"] <= ps["innerWidth"], ps)
        if full:
            page.evaluate("() => { document.querySelector('#all-body').scrollTop = 1500; }")
            page.wait_for_timeout(200)
            shot(page, f"p4-{tag}-scrolled.png")
            page.evaluate("() => { document.querySelector('#all-body').scrollTop = 0; }")
            page.wait_for_timeout(150)

        # a P4 day opens P1 as P4's bottom sheet, with the chosen day in sight above it
        hist = {x["name"]: x["done"] for x in histories(page)}
        a0 = page.get_attribute('#all-months [data-key="2026-09-22"]', "aria-label")
        o0 = page.get_attribute('#ov-grid [data-key="2026-09-22"]', "aria-label")
        page.click('#all-months [data-key="2026-09-22"]', timeout=T)
        page.wait_for_selector("#day-dlg[open]", timeout=T)
        page.wait_for_timeout(450)
        ok(f"{tag} a P4 day opens P1 for that date", page.inner_text("#day-title") == "Tuesday 22 September" and page.locator("#all-dlg[open]").count() == 1, page.inner_text("#day-title"))
        cell = rect(page, '#all-months [data-key="2026-09-22"]')
        sheet = rect(page, "#day-dlg .dlg-box")
        ok(f"{tag} P1 over P4 is a bottom sheet that leaves the chosen day in sight", abs(sheet["y"] + sheet["h"] - h) <= 1 and cell["y"] + cell["h"] <= sheet["y"] + 1 and cell["y"] >= 0, {"cell": cell, "sheet": sheet})
        p1s = {x["name"]: x for x in p1_stats(page)}
        ok(f"{tag} P1 from P4 shows Current and Best equal to the histories", all((p1s[n]["current"], p1s[n]["best"]) == streaks(hist[n]) == EXPECTED[n] for n in EXPECTED), p1s)
        shot(page, f"p4-p1-{tag}.png")
        if w == 360:
            R["overflow_360"]["p4-p1"] = overflow(page, w)
        page.click('#day-list .tick:has-text("Read 20 pages")', timeout=T)
        page.wait_for_timeout(400)
        a1 = page.get_attribute('#all-months [data-key="2026-09-22"]', "aria-label")
        o1 = page.get_attribute('#ov-grid [data-key="2026-09-22"]', "aria-label")
        ok(f"{tag} P1 tick changes the matching ring in P4 and the overview", a0.endswith("1 of 3 habits") and a1.endswith("2 of 3 habits") and o0.endswith("1 of 3 habits") and o1.endswith("2 of 3 habits"),
           {"p4": [a0, a1], "p3": [o0, o1]})
        if full:
            shot(page, f"p4-p1-{tag}-after-tick.png")
        page.click('#day-list .tick:has-text("Read 20 pages")', timeout=T)  # undo
        page.wait_for_timeout(250)
        # Esc closes the top layer first: P1, then P4, then P3
        page.keyboard.press("Escape")
        page.wait_for_timeout(300)
        s1 = [page.locator(f"#{d}[open]").count() for d in ("day-dlg", "all-dlg", "ov-dlg")]
        page.keyboard.press("Escape")
        page.wait_for_timeout(300)
        s2 = [page.locator(f"#{d}[open]").count() for d in ("day-dlg", "all-dlg", "ov-dlg")]
        f_after_p4 = focused(page)
        page.keyboard.press("Escape")
        page.wait_for_timeout(300)
        s3 = [page.locator(f"#{d}[open]").count() for d in ("day-dlg", "all-dlg", "ov-dlg")]
        ok(f"{tag} Esc closes P1, then P4, then P3", s1 == [0, 1, 1] and s2 == [0, 0, 1] and s3 == [0, 0, 0], {"after 1": s1, "after 2": s2, "after 3": s3, "open = [P1, P4, P3]": True})
        ok(f"{tag} closing P4 returns focus to P3's Year button", f_after_p4 == "Year view, all habits", f_after_p4)
        # Close returns to P3
        page.click("#ov-btn", timeout=T)
        page.wait_for_selector("#ov-dlg[open]", timeout=T)
        page.click("#ov-yr", timeout=T)
        page.wait_for_selector("#all-dlg[open]", timeout=T)
        page.wait_for_timeout(300)
        page.click("#all-dlg [data-act=close-all]", timeout=T)
        page.wait_for_timeout(300)
        ok(f"{tag} P4 Close returns to P3", page.locator("#all-dlg[open]").count() == 0 and page.locator("#ov-dlg[open]").count() == 1 and focused(page) == "Year view, all habits")
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

        # ---------- the row bin on a phone ----------
        page.click('#list .row:nth-child(2) .btn-bin', timeout=T)
        page.wait_for_selector("#del-dlg[open]", timeout=T)
        page.wait_for_timeout(300)
        ok(f"{tag} row bin opens M1 with that habit's name", page.inner_text("#del-title") == 'Delete "Stretch 10 minutes"?' and page.inner_text("#del-body") == "Its history is deleted too.", page.inner_text("#del-title"))
        shot(page, f"m1-row-{tag}.png")
        if w == 360:
            R["overflow_360"]["m1-row"] = overflow(page, w)
        page.click("[data-act=confirm-del]", timeout=T)
        page.wait_for_timeout(400)
        ok(f"{tag} a row delete removes the row and moves focus to the next row's bin", [r["name"] for r in rows(page)] == ["Read 20 pages", "No phone after 11pm"] and focused(page) == 'Delete "No phone after 11pm"', focused(page))
        shot(page, f"k1-{tag}-after-row-delete.png")
        check_rows(page, f"{tag} after a row delete")

        # a 40-character name wraps cleanly on the name line
        set_state(page, "k1")
        page.fill("#nh", LONG_NAME)
        page.click("#add-btn", timeout=T)
        page.wait_for_timeout(400)
        check_rows(page, f"{tag} long name")
        if w == 360:
            R["overflow_360"]["long-name"] = overflow(page, w)
        page.evaluate("() => { document.querySelector('.frame').scrollTop = 99999; }")
        page.wait_for_timeout(250)
        shot(page, f"k1-{tag}-long-name.png")
        ok(f"{tag} add field does not move after adding a long name", rect(page, "#nh") == k1_input, rect(page, "#nh"))

        if full:
            set_state(page, "k1")
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
                check_rows(page, f"{tag} S3")
                page.evaluate("() => { document.querySelector('.frame').scrollTop = 99999; }")
                page.wait_for_timeout(300)
                shot(page, f"s3-{tag}-scrolled.png")
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
                page.click("#ov-btn", timeout=T)
                page.wait_for_selector("#ov-dlg[open]", timeout=T)
                page.click("#ov-yr", timeout=T)
                page.wait_for_selector("#all-dlg[open]", timeout=T)
                page.wait_for_timeout(200)
                R["info"]["reduced motion animation on P4"] = page.evaluate("() => getComputedStyle(document.querySelector('#all-dlg .dlg-box')).animationName")
                ok("reduced motion: no animation on Done today or P4", R["info"]["reduced motion animation on the tapped dot"] == "none" and R["info"]["reduced motion animation on P4"] == "none",
                   [R["info"]["reduced motion animation on the tapped dot"], R["info"]["reduced motion animation on P4"]])
            finally:
                ctx.close()
        finally:
            browser.close()

    f1280 = R["info"]["overview number size 1280"]["renderedPx"]
    f390 = R["info"]["overview number size 390"]["renderedPx"]
    r1 = R["info"]["round 1 overview number size"]
    ok("overview numbers bigger than round 1 at 1280", f1280 > r1["1280"]["renderedPx"], {"round 2": f1280, "round 1": r1["1280"]["renderedPx"]})
    ok("overview numbers bigger than round 1 at 390", f390 > r1["390"]["renderedPx"], {"round 2": f390, "round 1": r1["390"]["renderedPx"]})

    o = R["overflow_360"]
    ok("360 no sideways scroll and nothing past the viewport", all(v["scrollWidth"] <= v["clientWidth"] and not v["poking"] for v in o.values()), o)
    ok("console errors 0", not R["console_errors"] and not R["page_errors"], R["console_errors"] + R["page_errors"])
    ok("no network requests", not R["requests_off_file"], R["requests_off_file"])
    ok("no clipboard writes", all(not v for v in R["clipboard_writes"].values()), R["clipboard_writes"])

    pairs = [
        # F's pairs, unchanged
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
        # new in F2: the row bin
        ("NEW ink-soft on surface (row bin at rest, 3:1 icon)", "--ink-soft", "--surface", 3.0),
        ("NEW danger on surface (row bin icon and edge on hover and focus, 3:1)", "--danger", "--surface", 3.0),
        ("NEW focus on surface (row bin focus ring)", "--focus", "--surface", 3.0),
        # new in F2: the overview's Year button
        ("NEW ink on surface (band Year label)", "--ink", "--surface", 4.5),
        ("NEW ring on surface (band Year edge, 3:1)", "--ring", "--surface", 3.0),
        ("NEW ink on surface-2 (P3 Year label)", "--ink", "--surface-2", 4.5),
        ("NEW ring on surface-2 (P3 Year edge, 3:1)", "--ring", "--surface-2", 3.0),
        ("NEW ink on raise (Year label on hover)", "--ink", "--raise", 4.5),
        # new in F2: P4 on surface-2
        ("NEW ink-soft on surface-2 (P4 day numbers, month names, legend)", "--ink-soft", "--surface-2", 4.5),
        ("NEW on-amber on amber (P4 number on a full day's core)", "--on-amber", "--amber", 4.5),
        ("NEW amber on surface-2 (P4 done segment, 3:1)", "--amber", "--surface-2", 3.0),
        ("NEW ring on surface-2 (P4 not-done segment, 3:1)", "--ring", "--surface-2", 3.0),
        ("NEW ink on surface-2 (P4 today circle and month titles)", "--ink", "--surface-2", 4.5),
        ("NEW ink-soft on raise (P4 open day and hover, day number)", "--ink-soft", "--raise", 4.5),
        ("NEW amber on raise (P4 open day outline, 3:1)", "--amber", "--raise", 3.0),
        ("NEW focus on surface-2 (P4 day focus ring)", "--focus", "--surface-2", 3.0),
    ]
    for label, a, b, need in pairs:
        rt = ratio(tk[a], tk[b])
        R["contrast"][label] = {"fg": tk[a], "bg": tk[b], "ratio": rt, "needs": need}
        ok(f"contrast {label}", rt >= need, rt)
    # inactive, recorded only: days after today in P4 (and P2), exempt as disabled content
    R["contrast"]["NEW closed on surface-2 (P4 days after today, inactive, exempt)"] = {"fg": tk["--closed"], "bg": tk["--surface-2"], "ratio": ratio(tk["--closed"], tk["--surface-2"]), "needs": None}
    # inherited from F, recorded only: a thin not-done segment while its day is hovered or open (raise behind it)
    R["contrast"]["F inherited ring on raise (thin segment on a hovered or open day)"] = {"fg": tk["--ring"], "bg": tk["--raise"], "ratio": ratio(tk["--ring"], tk["--raise"]), "needs": None}

    failed = [k for k, v in R["asserts"].items() if not v["pass"]]
    R["summary"] = {"asserts": len(R["asserts"]), "passed": len(R["asserts"]) - len(failed), "failed": failed, "shots": len(R["shots"])}
    out = HERE / "results.json"
    out.write_text(json.dumps(R, indent=2), encoding="utf-8")
    print(json.dumps(R["summary"], indent=2))
    for k in failed:
        print("FAIL", k, json.dumps(R["asserts"][k]["detail"])[:600])


if __name__ == "__main__":
    main()
