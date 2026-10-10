"""Quick render probe while composing. Screenshots the goldens in FILES at the three sizes into checks/peek/
and measures how far each ring or bead number's ink sits from its shape's centre. Every wait bounded,
the browser closes in a finally block. Run with: python -B "<this file>"."""
import io
import json
import pathlib
from PIL import Image
from playwright.sync_api import sync_playwright

FILES = ["today.html", "year-view.html"]
F2_TOO = False
KS = [".352em", ".345em"]
HERE = pathlib.Path(__file__).resolve().parent
FINAL = HERE.parent
OUT = HERE / "peek"
T = 5000
SIZES = [(360, 780), (390, 844), (1280, 800)]

HIDE = """
.seg, .c-core, .c-today { visibility: hidden !important; }
.hc, .hc.is-open { background: transparent !important; box-shadow: none !important; }
.c-num, .c-num.on, .c-num.dim { fill: #fff !important; }
.bead { border-color: transparent !important; background: transparent !important; box-shadow: none !important; color: #fff !important; }
.yc::before, .yc::after { display: none !important; }
"""

SHAPES = """() => {
  const out = [];
  const take = (shape, text, kind) => {
    const r = shape.getBoundingClientRect();
    if (r.width === 0 || r.top < 0 || r.left < 0 || r.bottom > innerHeight || r.right > innerWidth) return;
    const cx = r.left + r.width / 2, cy = r.top + r.height / 2;
    const top = document.elementFromPoint(cx, cy);
    const cell = shape.closest('.hc, .yc') || shape;
    if (!top || !(cell === top || cell.contains(top) || top.contains(cell))) return;
    out.push({ kind, text, x: r.left, y: r.top, w: r.width, h: r.height });
  };
  for (const t of document.querySelectorAll('.c-num')) {
    const svg = t.ownerSVGElement, host = svg.closest('.hc');
    const kind = host && host.closest('.dlg-all') ? 'p4 ring' : host && host.closest('.dlg-ov') ? 'p3 ring' : 'band ring';
    take(svg, t.textContent, kind + (t.classList.contains('dim') ? ' closed' : ''));
  }
  for (const b of document.querySelectorAll('.bead')) take(b, b.textContent.trim(), 'p2 bead' + (b.closest('.closed') ? ' closed' : ''));
  return out;
}"""


def ink_offsets(png, shapes, scale):
    img = Image.open(io.BytesIO(png)).convert("RGB")
    px = img.load()
    res = []
    for s in shapes:
        x0, y0 = int(round(s["x"] * scale)), int(round(s["y"] * scale))
        x1, y1 = int(round((s["x"] + s["w"]) * scale)), int(round((s["y"] + s["h"]) * scale))
        bg = px[x0 + 1, y0 + 1]
        rows, cols = [], []
        for y in range(y0 + 1, y1 - 1):
            for x in range(x0 + 1, x1 - 1):
                p = px[x, y]
                if max(abs(p[0] - bg[0]), abs(p[1] - bg[1]), abs(p[2] - bg[2])) > 48:
                    rows.append(y)
                    cols.append(x)
        if not rows:
            continue
        icy = (min(rows) + max(rows) + 1) / 2 / scale
        icx = (min(cols) + max(cols) + 1) / 2 / scale
        res.append({"kind": s["kind"], "text": s["text"], "dy": round(icy - (s["y"] + s["h"] / 2), 3), "dx": round(icx - (s["x"] + s["w"] / 2), 3),
                    "ink_top": min(rows) / scale - (s["y"] + s["h"] / 2), "ink_bottom": (max(rows) + 1) / scale - (s["y"] + s["h"] / 2), "shape_y": s["y"], "shape_h": s["h"]})
    return res


def summarise(res):
    by = {}
    for r in res:
        k = by.setdefault(r["kind"], {"n": 0, "max_abs_dy": 0, "max_abs_dx": 0, "mean_dy": 0.0, "worst_dy": None, "worst_dx": None})
        k["n"] += 1
        k["mean_dy"] += r["dy"]
        if abs(r["dy"]) >= k["max_abs_dy"]:
            k["max_abs_dy"], k["worst_dy"] = abs(r["dy"]), r["text"]
        if abs(r["dx"]) >= k["max_abs_dx"]:
            k["max_abs_dx"], k["worst_dx"] = abs(r["dx"]), r["text"]
    for k in by.values():
        k["mean_dy"] = round(k["mean_dy"] / k["n"], 3)
    return by


def main():
    OUT.mkdir(exist_ok=True)
    report = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            for f in FILES:
                url = (FINAL / f).as_uri()
                for w, h in SIZES:
                    ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1, reduced_motion="reduce")
                    try:
                        page = ctx.new_page()
                        errs, reqs = [], []
                        page.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
                        page.on("pageerror", lambda e: errs.append(str(e)))
                        page.on("request", lambda r: reqs.append(r.url) if not r.url.startswith(("file:", "data:")) else None)
                        page.goto(url, timeout=T)
                        page.wait_for_timeout(200)
                        page.screenshot(path=str(OUT / f"{f[:-5]}-{w}.png"))
                        m = page.evaluate("""() => { const o = { sw: document.scrollingElement.scrollWidth, sh: document.scrollingElement.scrollHeight };
                          const b = document.querySelector('.yc:not(.closed) .bead');
                          if (b) { const r = b.getBoundingClientRect(), rg = document.createRange(); rg.selectNodeContents(b); const t = rg.getBoundingClientRect();
                            o.bead = { y: r.y, h: r.height, strut: getComputedStyle(b, '::before').height, fs: getComputedStyle(b).fontSize, textTop: t.y, textH: t.height, textTopFromCentre: t.y - (r.y + r.height / 2) }; }
                          return o; }""")
                        report[f"{f} {w}"] = {"errors": errs, "requests": reqs, "scroll": m}
                    finally:
                        ctx.close()
                    if w in (390, 1280):
                        ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=4, reduced_motion="reduce")
                        try:
                            page = ctx.new_page()
                            page.goto(url, timeout=T)
                            page.add_style_tag(content=HIDE)
                            page.wait_for_timeout(200)
                            shapes = page.evaluate(SHAPES)
                            png = page.screenshot()
                            res = ink_offsets(png, shapes, 4)
                            report[f"{f} {w}"]["centring"] = summarise(res)
                            per = {}
                            for r in res:
                                per.setdefault(r["kind"] + " " + r["text"], []).append((r["dx"], r["dy"]))
                            report[f"{f} {w}"]["per_number"] = {k: [round(sum(a for a, _ in v) / len(v), 2), round(sum(b for _, b in v) / len(v), 2)] for k, v in sorted(per.items())}
                        finally:
                            ctx.close()
            if F2_TOO:
                f2 = (FINAL.parent / "round-2" / "f2.html").as_uri()
                cases = [(390, 844, "#ov-btn", None, "p3"), (390, 844, "#ov-btn", "#ov-yr", "p4"), (390, 844, "#list .row:nth-child(1) .btn-year", None, "p2"),
                         (360, 780, "#ov-btn", None, "p3"), (360, 780, "#list .row:nth-child(1) .btn-year", None, "p2"),
                         (1280, 800, None, None, "band"), (1280, 800, "#band-yr", None, "p4"), (1280, 800, "#list .row:nth-child(1) .btn-year", None, "p2")]
                for k in KS:
                    for w, h, opener, then, label in cases:
                        ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=4, reduced_motion="reduce")
                        try:
                            page = ctx.new_page()
                            page.goto(f2, timeout=T)
                            page.wait_for_selector("#list .row", timeout=T)
                            if opener:
                                page.click(opener, timeout=T)
                                page.wait_for_timeout(250)
                            if then:
                                page.click(then, timeout=T)
                                page.wait_for_timeout(250)
                            css = HIDE + ".proto{display:none!important}"
                            if k != "f2":
                                css += ".bead{font-variant-numeric:proportional-nums}.bead svg{position:absolute;inset:0;width:100%;height:100%;overflow:visible}.bead text{fill:#fff;text-anchor:middle;dominant-baseline:alphabetic}"
                                page.evaluate("""(k) => { document.querySelectorAll('.c-num').forEach(t => t.setAttribute('dy', k));
                                  document.querySelectorAll('.bead').forEach(b => { const n = b.textContent; b.innerHTML = '<svg aria-hidden="true"><text x="50%" y="50%" dy="' + k + '">' + n + '</text></svg>'; }); }""", k)
                            page.add_style_tag(content=css)
                            page.wait_for_timeout(150)
                            res = ink_offsets(page.screenshot(), page.evaluate(SHAPES), 4)
                            s = summarise(res)
                            report.setdefault(f"k {k}", {})[f"{label} {w}"] = {kk: [v["n"], v["mean_dy"], v["max_abs_dy"]] for kk, v in s.items()}
                        finally:
                            ctx.close()
        finally:
            browser.close()
    print(json.dumps({k: (v if k.startswith("k ") else {kk: vv for kk, vv in v.items() if kk != "per_number"}) for k, v in report.items()}))


if __name__ == "__main__":
    main()
