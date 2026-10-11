"""Render check for the v1.1.0 goldens. Headless Chromium, file:/// URLs, no server, no network.
Writes results.json, shots/ and compare/ beside this file only. Every wait bounded, the browser closes in a finally.
Run with: python -B "<this file>"."""
import io
import json
import pathlib
import re
from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright
import data
import peek

HERE = pathlib.Path(__file__).resolve().parent
FINAL = HERE.parent
F2 = (FINAL.parent / "round-2" / "f2.html").as_uri()
T = 6000
SIZES = [(360, 780), (390, 844), (1280, 800)]
GOLDENS = ["today", "day-editor", "year-view", "overview", "overview-year", "delete-dialog", "today-empty", "today-full", "states"]
NO_SCROLL_1280 = ["today", "day-editor", "year-view", "overview", "overview-year", "delete-dialog", "today-empty", "today-full"]
F2_STATE = {  # how to reach the same state in f2: (proto state, clicks at phone, clicks at 1280)
    "today": (None, [], []),
    "day-editor": (None, ["#ov-btn", '#ov-grid [data-key="2026-09-22"]'], ['#band-grid [data-key="2026-09-22"]']),
    "year-view": (None, ["#list .row:nth-child(1) .btn-year"], ["#list .row:nth-child(1) .btn-year"]),
    "overview": (None, ["#ov-btn"], None),
    "overview-year": (None, ["#ov-btn", "#ov-yr"], ["#band-yr"]),
    "delete-dialog": (None, ["#list .row:nth-child(2) .btn-bin"], ["#list .row:nth-child(2) .btn-bin"]),
    "today-empty": ("s1", [], []),
    "today-full": ("s3", [], []),
}
F2_NO_PROTO = """.proto{display:none!important} .top{grid-template-areas:"brand ov" "date date"!important}
@media (min-width:1024px){ .top{grid-template-columns:minmax(0,1fr) auto!important; grid-template-areas:"brand date"!important} }"""
R = {"console_errors": {}, "requests": {}, "scroll": {}, "targets_under_44": {}, "css_equal_system": {}, "numbers": {},
     "rings_vs_history": {}, "beads_vs_history": {}, "centring": {}, "lifted_pair": {}, "contrast": None, "dashes": {},
     "compare": {}, "asserts": {}}


def ok(name, cond, detail=None):
    R["asserts"][name] = {"pass": bool(cond), "detail": detail}


hist = json.loads((FINAL / "sample-history.json").read_text(encoding="utf-8"))
START = data.YEAR_START
SETS = []
for h in hist["habits"]:
    SETS.append({(START + data.DAY * i).isoformat() for i, c in enumerate(h["done"]) if c == "1"})
NAMES = [h["name"] for h in hist["habits"]]
EXPECT = {n: data.streaks(s) for n, s in zip(NAMES, SETS)}
for h in hist["habits"]:
    ok(f"history {h['name']} current and best as stated", (h["current"], h["best"]) == EXPECT[h["name"]], [h["current"], h["best"], EXPECT[h["name"]]])

ROWS = """() => [...document.querySelectorAll('li.row, .tick, .yr-stats')].map(r => {
  if (r.classList.contains('tick')) { const s = r.querySelector('.tstat').innerText, c = s.match(/Current (\\d+)/), b = s.match(/Best (\\d+)/);
    return { kind: 'p1', name: r.querySelector('.tname').textContent, cur: c ? +c[1] : 0, best: b ? +b[1] : 0 }; }
  const cur = r.querySelector('.stat.cur .num'), best = r.querySelector('.stat.best .num');
  const name = r.classList.contains('yr-stats') ? document.querySelector('#yr-title').textContent : r.querySelector('.r-name').textContent;
  return { kind: r.classList.contains('yr-stats') ? 'p2' : 'row', name, cur: cur ? +cur.textContent : 0, best: best ? +best.textContent : 0 };
})"""
RINGS = """() => [...document.querySelectorAll('button.hc[data-key]')].map(b => ({ key: b.dataset.key, label: b.getAttribute('aria-label'),
  segs: [...b.querySelectorAll('svg > .seg')].map(s => s.classList.contains('on')), core: !!b.querySelector('.c-core'), n: [...b.querySelectorAll('svg > .seg')].length }))"""
BEADS = """() => [...document.querySelectorAll('button.yc[data-key]')].map(b => ({ key: b.dataset.key, on: b.getAttribute('aria-pressed') === 'true',
  cls: b.className, today: b.getAttribute('aria-current') === 'date' }))"""
TARGETS = """() => { const out = [];
  for (const e of document.querySelectorAll('button, input, a[href]')) {
    if (e.closest('[inert]') || e.closest('.sr')) continue;
    const cs = getComputedStyle(e); if (cs.display === 'none' || cs.visibility === 'hidden') continue;
    const r = e.getBoundingClientRect(); if (!r.width || !r.height) continue;
    if (r.bottom < 0 || r.top > innerHeight) continue;
    if (r.width < 43.5 || r.height < 43.5) out.push({ what: (e.getAttribute('aria-label') || e.textContent.trim()).slice(0, 40), cls: e.className, w: Math.round(r.width * 100) / 100, h: Math.round(r.height * 100) / 100 });
  } return out; }"""
ALLOW = ("yc", "hc")  # day cells, see system.md "Sizes and touch targets"


def check_rings(g, rings):
    bad = []
    for r in rings:
        flags = [r["key"] in s for s in (SETS[:len(r["segs"])] if r["n"] > 1 else [])]
        n = sum(flags)
        total = len(r["segs"]) if r["n"] > 1 else 0
        if r["n"] > 1 and (r["segs"] != flags or r["core"] != (n == total) or not r["label"].endswith(f", {n} of {total} habits")):
            bad.append(r["key"])
        if r["n"] == 1 and not r["label"].endswith("0 of 0 habits"):
            bad.append(r["key"])
    R["rings_vs_history"][g] = {"rings": len(rings), "mismatches": bad[:10], "count": len(bad)}
    ok(f"{g} every ring equals sample-history.json", not bad, bad[:10])


def check_beads(g, beads):
    s = SETS[0]
    bad = []
    for b in beads:
        k = b["key"]
        on = k in s
        if b["on"] != on or ("on" in b["cls"].split()) != on:
            bad.append(k)
    R["beads_vs_history"][g] = {"beads": len(beads), "mismatches": bad[:10]}
    ok(f"{g} every bead equals Read 20 pages in sample-history.json", len(beads) == 366 and not bad, {"beads": len(beads), "bad": bad[:10]})


def composite(a_png, b_png, path):
    a, b = Image.open(io.BytesIO(a_png)).convert("RGB"), Image.open(io.BytesIO(b_png)).convert("RGB")
    diff = ImageChops.difference(a, b).convert("L").point(lambda v: 255 if v > 24 else 0)
    frac = round(sum(1 for v in diff.getdata() if v) / (a.width * a.height), 4)
    out = Image.new("RGB", (a.width * 2 + 12, a.height), (255, 0, 255))
    out.paste(a, (0, 0))
    out.paste(b, (a.width + 12, 0))
    out.save(path)
    return frac


def main():
    (HERE / "shots").mkdir(exist_ok=True)
    (HERE / "compare").mkdir(exist_ok=True)
    system = (FINAL / "system.css").read_text(encoding="utf-8").strip()
    for g in GOLDENS:
        txt = (FINAL / f"{g}.html").read_text(encoding="utf-8")
        style = re.search(r"<style>\n(.*?)\n</style>", txt, re.S).group(1).strip()
        R["css_equal_system"][g] = style == system
        ok(f"{g} style block is system.css", R["css_equal_system"][g])
    for p in FINAL.rglob("*"):
        if p.is_file() and p.suffix in (".html", ".md", ".css", ".json"):
            t = p.read_text(encoding="utf-8")
            n = t.count("—") + t.count("–")
            if n:
                R["dashes"][str(p.relative_to(FINAL))] = n
    ok("no em or en dashes in final/", not R["dashes"], R["dashes"])
    R["contrast"] = data.contrast()
    ok("contrast pairs all pass", all(p["pass"] for p in R["contrast"]["pairs"]), [p for p in R["contrast"]["pairs"] if not p["pass"]])

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            for g in GOLDENS:
                url = (FINAL / f"{g}.html").as_uri()
                for w, h in SIZES:
                    tag = f"{g} {w}"
                    ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1, reduced_motion="reduce")
                    try:
                        page = ctx.new_page()
                        errs, reqs = [], []
                        page.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
                        page.on("pageerror", lambda e: errs.append(str(e)))
                        page.on("request", lambda r: reqs.append(r.url) if not r.url.startswith(("file:", "data:")) else None)
                        page.goto(url, timeout=T)
                        page.wait_for_timeout(250)
                        gp = page.screenshot()
                        (HERE / "shots" / f"{g}-{w}.png").write_bytes(gp)
                        sc = page.evaluate("() => ({ sw: document.scrollingElement.scrollWidth, sh: document.scrollingElement.scrollHeight, iw: innerWidth, ih: innerHeight })")
                        R["console_errors"][tag], R["requests"][tag], R["scroll"][tag] = errs, reqs, sc
                        under = page.evaluate(TARGETS)
                        R["targets_under_44"][tag] = under
                        ok(f"{tag} targets 44 px (day cells excepted, listed)", not [u for u in under if not any(a in u["cls"].split() for a in ALLOW)], under)
                        if w == 360:
                            ok(f"{tag} no sideways scroll", sc["sw"] <= sc["iw"], sc)
                        if w == 1280 and g in NO_SCROLL_1280:
                            ok(f"{tag} page does not scroll", sc["sh"] <= sc["ih"] and sc["sw"] <= sc["iw"], sc)
                        if w == 1280:
                            nums = page.evaluate(ROWS)
                            bad = [n for n in nums if (n["cur"], n["best"]) != EXPECT.get(n["name"])]
                            R["numbers"][g] = {"shown": len(nums), "mismatches": bad}
                            ok(f"{g} Current and Best equal the history", not bad, bad)
                            rings = page.evaluate(RINGS)
                            if rings:
                                check_rings(g, rings)
                            beads = page.evaluate(BEADS)
                            if beads:
                                check_beads(g, beads)
                        if g == "day-editor" and w == 1280:
                            st = page.evaluate("() => { const u = document.querySelector('.band .hc.is-open use.seg:not(.on)'); return u ? getComputedStyle(u).stroke : null; }")
                            r = data.ratio(data.rgba("#A8ABB2"), data.rgba("#35373D"))
                            R["lifted_pair"] = {"stroke on the open day": st, "ink-soft on raise": r}
                            ok("lifted pair, thin segment on the open day draws in --ink-soft at 3 to 1 or more", st == "rgb(168, 171, 178)" and r >= 3, R["lifted_pair"])
                        # f2 at the same state and width
                        spec = F2_STATE.get(g)
                        clicks = None if spec is None else (spec[2] if w == 1280 else spec[1])
                        if clicks is not None:
                            p2 = ctx.new_page()
                            p2.goto(F2, timeout=T)
                            p2.wait_for_selector("#list", state="attached", timeout=T)
                            if spec[0]:
                                p2.click("#proto-tab", timeout=T)
                                p2.click(f'[data-state="{spec[0]}"]', timeout=T)
                                p2.wait_for_timeout(250)
                            p2.add_style_tag(content=F2_NO_PROTO)
                            for c in clicks:
                                p2.click(c, timeout=T)
                                p2.wait_for_timeout(250)
                            p2.mouse.move(1, 1)
                            p2.wait_for_timeout(200)
                            fp = p2.screenshot()
                            R["compare"][tag] = composite(gp, fp, HERE / "compare" / f"{g}-{w}.png")
                            p2.close()
                    finally:
                        ctx.close()
                    if w in (390, 1280) and g != "states":
                        ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=4, reduced_motion="reduce")
                        try:
                            page = ctx.new_page()
                            page.goto(url, timeout=T)
                            page.add_style_tag(content=peek.HIDE)
                            page.wait_for_timeout(200)
                            shapes = page.evaluate(peek.SHAPES)
                            res = peek.ink_offsets(page.screenshot(), shapes, 4)
                            s = peek.summarise(res)
                            R["centring"][tag] = s
                            if res:
                                ok(f"{tag} every ring and bead number's ink within 0.3 px of centre (vertical)", max(abs(r["dy"]) for r in res) <= 0.3, {k: [v["n"], v["max_abs_dy"], v["max_abs_dx"]] for k, v in s.items()})
                        finally:
                            ctx.close()
        finally:
            browser.close()
    ok("console errors 0", not any(R["console_errors"].values()), {k: v for k, v in R["console_errors"].items() if v})
    ok("network requests 0", not any(R["requests"].values()), {k: v for k, v in R["requests"].items() if v})
    failed = [k for k, v in R["asserts"].items() if not v["pass"]]
    R["summary"] = {"asserts": len(R["asserts"]), "passed": len(R["asserts"]) - len(failed), "failed": failed}
    (HERE / "results.json").write_text(json.dumps(R, indent=1), encoding="utf-8")
    print(json.dumps(R["summary"]))
    for k in failed:
        print("FAIL", k, json.dumps(R["asserts"][k]["detail"])[:400])
    print("compare (share of pixels that differ):", json.dumps(R["compare"]))
    print("centring:", json.dumps({k: {kk: [vv["n"], vv["max_abs_dy"], vv["max_abs_dx"]] for kk, vv in v.items()} for k, v in R["centring"].items()}))
    print("under 44:", json.dumps({k: sorted({(u["cls"].split()[0] if u["cls"] else "", u["w"], u["h"]) for u in v}) for k, v in R["targets_under_44"].items() if v}))


if __name__ == "__main__":
    main()
