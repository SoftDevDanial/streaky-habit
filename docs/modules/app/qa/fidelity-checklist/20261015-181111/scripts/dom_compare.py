"""Whole-page comparison, golden against the running app, for the 23 captures (checklist evidence, task 28).

Run from the project root:  python -B <this file> <checklist folder>
Renders each golden and each candidate exactly as the 2.6.0 harness does (its own freeze script and freeze
stylesheet are imported from fidelity.py, the same launch flags and context options, the same state scripts),
then walks both DOM trees and compares every element: classes, attributes, own text, rectangle, every computed
property, ::before and ::after, and for dialogs :modal and ::backdrop. Children are paired by tag, id and
data-key, then by the largest class overlap in order. Writes <checklist>/dom-compare/<capture>.json and
<checklist>/dom-compare-summary.json, refusing to overwrite. One http.server, started and stopped here.
"""
import collections
import datetime
import importlib.util
import json
import pathlib
import sys

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import gate_runner as gr  # noqa: E402  (server helpers, capture table, the ROOT check)

from playwright.sync_api import sync_playwright  # noqa: E402

spec = importlib.util.spec_from_file_location("harness_fidelity", gr.HARNESS)
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)

OUT = pathlib.Path(sys.argv[1]) / "dom-compare"
if OUT.exists():
    sys.exit(f"refused, {OUT} exists")

DUMP_JS = r"""() => {
  const table = []; const index = new Map();
  const sid = (cs) => {
    let s = '';
    for (let i = 0; i < cs.length; i++) { const n = cs[i]; s += n + ':' + cs.getPropertyValue(n) + ';\n'; }
    let k = index.get(s);
    if (k === undefined) { k = table.length; table.push(s); index.set(s, k); }
    return k;
  };
  const pseudo = (el, p) => {
    const cs = getComputedStyle(el, p);
    const c = cs.getPropertyValue('content');
    return (!c || c === 'none' || c === 'normal') ? -1 : sid(cs);
  };
  const walk = (el) => {
    const r = el.getBoundingClientRect();
    const a = {};
    for (const at of el.attributes) if (at.name !== 'class') a[at.name] = at.value;
    let x = '';
    for (const n of el.childNodes) if (n.nodeType === 3) x += n.nodeValue;
    const node = { t: el.tagName.toLowerCase(), c: Array.from(el.classList), a, x,
      r: [r.x, r.y, r.width, r.height].map((v) => Math.round(v * 100) / 100),
      s: sid(getComputedStyle(el)), b: pseudo(el, '::before'), f: pseudo(el, '::after'), k: [] };
    if (node.t === 'use') {
      const ref = (a.href || a['xlink:href'] || '');
      const target = ref.startsWith('#') ? document.getElementById(ref.slice(1)) : null;
      node.ud = target ? (target.getAttribute('d') || target.tagName) : null;
    }
    if (node.t === 'dialog') { node.modal = el.matches(':modal'); node.bd = sid(getComputedStyle(el, '::backdrop')); }
    for (const ch of el.children) node.k.push(walk(ch));
    return node;
  };
  const icons = Array.from(document.querySelectorAll('link[rel~="icon"]')).map((l) => ({
    type: l.type, href_start: (l.getAttribute('href') || '').slice(0, 40), href_length: (l.getAttribute('href') || '').length }));
  return { tree: walk(document.body), html: sid(getComputedStyle(document.documentElement)), styles: table,
    title: document.title, icons, active: document.activeElement ? document.activeElement.tagName : null,
    now: new Date().toString(), tz: Intl.DateTimeFormat().resolvedOptions().timeZone,
    scroll: [scrollX, scrollY, document.documentElement.scrollWidth, document.documentElement.scrollHeight],
    open_dialogs: Array.from(document.querySelectorAll('dialog[open]')).map((d) => d.className) };
}"""


def render(browser, url, viewport, init_js=None, after_js=None):
    w, h = (int(v) for v in viewport.split("x"))
    ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1, reduced_motion="reduce",
                              color_scheme="dark", bypass_csp=True)
    page = ctx.new_page()
    page.clock.set_fixed_time(datetime.datetime.fromisoformat(gr.FIXED))
    page.add_init_script(harness.FREEZE_INIT_JS)
    if init_js:
        page.add_init_script(init_js)
    page.goto(url, wait_until="networkidle", timeout=30000)
    if after_js:
        page.evaluate(f"async () => {{ {after_js}\n }}")
    page.add_style_tag(content=harness.FREEZE_CSS)
    page.wait_for_timeout(300)
    data = page.evaluate(DUMP_JS)
    ctx.close()
    return data


def parse(style):
    out = {}
    for line in style.split(";\n"):
        if ":" in line:
            k, v = line.split(":", 1)
            out[k] = v
    return out


def label(n):
    s = n["t"]
    if n["a"].get("id"):
        s += "#" + n["a"]["id"]
    if n["c"]:
        s += "." + ".".join(n["c"])
    if n["a"].get("data-key"):
        s += f"[{n['a']['data-key']}]"
    return s


class Diff:
    def __init__(self, gdata, cdata):
        self.gs = [parse(s) for s in gdata["styles"]]
        self.cs = [parse(s) for s in cdata["styles"]]
        self.by_kind = collections.Counter()
        self.by_prop = collections.Counter()
        self.examples = collections.defaultdict(list)
        self.items = []
        self.matched = 0

    def add(self, kind, path, detail, prop=None):
        key = f"{kind}:{prop}" if prop else kind
        self.by_kind[kind] += 1
        if prop:
            self.by_prop[key] += 1
        if len(self.examples[key]) < 5:
            self.examples[key].append({"path": path, **detail})
        if len(self.items) < 3000:
            self.items.append({"kind": key, "path": path, **detail})

    def styles(self, kind, path, gi, ci):
        if gi == ci == -1:
            return
        if gi == -1 or ci == -1:
            self.add(kind + "-presence", path, {"golden": gi != -1, "candidate": ci != -1})
            return
        g, c = self.gs[gi], self.cs[ci]
        for p in sorted(set(g) | set(c)):
            if g.get(p) != c.get(p):
                self.add(kind, path, {"golden": g.get(p), "candidate": c.get(p)}, p)

    def compare(self, g, c, path):
        self.matched += 1
        if g["c"] != c["c"]:
            self.add("class", path, {"golden": g["c"], "candidate": c["c"]})
        for k in sorted(set(g["a"]) | set(c["a"])):
            if g["a"].get(k) != c["a"].get(k):
                self.add("attribute", path, {"golden": g["a"].get(k), "candidate": c["a"].get(k)}, k)
        if g["x"] != c["x"]:
            ws = g["x"].strip() == "" and c["x"].strip() == ""
            self.add("text-whitespace-only" if ws else "text", path, {"golden": g["x"][:120], "candidate": c["x"][:120]})
        if any(abs(a - b) > 0.01 for a, b in zip(g["r"], c["r"])):
            self.add("rect", path, {"golden": g["r"], "candidate": c["r"]})
        self.styles("style", path, g["s"], c["s"])
        self.styles("before", path, g["b"], c["b"])
        self.styles("after", path, g["f"], c["f"])
        if g["t"] == "dialog":
            if g.get("modal") != c.get("modal"):
                self.add("dialog-modal", path, {"golden": g.get("modal"), "candidate": c.get("modal")})
            self.styles("backdrop", path, g["bd"], c["bd"])
        if g["t"] == "use" and g.get("ud") != c.get("ud"):
            self.add("use-target", path, {"golden": (g.get("ud") or "")[:80], "candidate": (c.get("ud") or "")[:80]})
        self.children(g["k"], c["k"], path)

    def children(self, gk, ck, path):
        used = set()
        g_only = []
        for gn in gk:
            sig = (gn["t"], gn["a"].get("id"), gn["a"].get("data-key"))
            best, score = None, None
            for i, cn in enumerate(ck):
                if i in used or (cn["t"], cn["a"].get("id"), cn["a"].get("data-key")) != sig:
                    continue
                s = 10 * len(set(gn["c"]) & set(cn["c"])) - len(set(gn["c"]) ^ set(cn["c"]))
                if score is None or s > score:
                    best, score = i, s
            if best is None:
                g_only.append(gn)
            else:
                used.add(best)
                self.compare(gn, ck[best], f"{path}>{label(gn)}")
        c_only = [cn for i, cn in enumerate(ck) if i not in used]
        # The goldens draw ring arcs as <use> of shared paths, the app as <path> (MANIFEST, static stand-ins).
        # Pair them in order and compare what they draw: the referenced path data and the computed styles.
        g_use = [n for n in g_only if n["t"] == "use"]
        c_path = [n for n in c_only if n["t"] == "path"]
        if g_use and len(g_use) == len(c_path):
            for gn, cn in zip(g_use, c_path):
                p = f"{path}>{label(gn)}~{label(cn)}"
                self.add("use-vs-path-pair", p, {})
                if (gn.get("ud") or "").replace(" ", "") != (cn["a"].get("d") or "").replace(" ", ""):
                    self.add("use-vs-path-geometry", p, {"golden": (gn.get("ud") or "")[:80], "candidate": (cn["a"].get("d") or "")[:80]})
                if gn["c"] != cn["c"]:
                    self.add("use-vs-path-class", p, {"golden": gn["c"], "candidate": cn["c"]})
                if any(abs(a - b) > 0.01 for a, b in zip(gn["r"], cn["r"])):
                    self.add("use-vs-path-rect", p, {"golden": gn["r"], "candidate": cn["r"]})
                self.styles("use-vs-path-style", p, gn["s"], cn["s"])
            g_only = [n for n in g_only if n["t"] != "use"]
            c_only = [n for n in c_only if n["t"] != "path"]
        for gn in g_only:
            self.add("golden-only", f"{path}>{label(gn)}", {"rect": gn["r"], "attrs": {k: v[:60] for k, v in gn["a"].items()}, "descendants": count(gn)})
        for cn in c_only:
            self.add("candidate-only", f"{path}>{label(cn)}", {"rect": cn["r"], "attrs": {k: v[:60] for k, v in cn["a"].items()}, "descendants": count(cn)})


def count(n):
    return 1 + sum(count(k) for k in n["k"])


def main():
    head = gr.git("rev-parse", "HEAD")
    proc, port, cmd = gr.start_server()
    server = {"pid": proc.pid, "port": port, "command": cmd}
    print(json.dumps({"server": server, "head": head}), flush=True)
    base = f"http://127.0.0.1:{port}/"
    summary = {"head": head, "server": server, "captures": []}
    OUT.mkdir(parents=True)
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(args=["--force-color-profile=srgb", "--hide-scrollbars"])
            summary["browser_version"] = browser.version
            for screen, viewports, flags in gr.CAPTURES:
                init_js = after_js = None
                if "--candidate-init-script" in flags:
                    init_js = pathlib.Path(flags[flags.index("--candidate-init-script") + 1]).read_text(encoding="utf-8")
                if "--candidate-after-load" in flags:
                    after_js = pathlib.Path(flags[flags.index("--candidate-after-load") + 1]).read_text(encoding="utf-8")
                for vp in viewports:
                    golden_url = (gr.ROOT / "docs" / "design" / f"{screen}.html").resolve().as_uri()
                    g = render(browser, golden_url, vp)
                    c = render(browser, base, vp, init_js, after_js)
                    d = Diff(g, c)
                    d.compare(g["tree"], c["tree"], "body")
                    d.styles("html-style", "html", g["html"], c["html"])
                    meta = {k: {"golden": g[k], "candidate": c[k]} for k in ("title", "icons", "active", "now", "tz", "scroll", "open_dialogs")}
                    rec = {"capture": f"{screen}-{vp}", "golden_elements": count(g["tree"]), "candidate_elements": count(c["tree"]),
                           "matched": d.matched, "by_kind": dict(d.by_kind), "by_property": dict(d.by_prop), "meta": meta,
                           "examples": dict(d.examples), "items": d.items}
                    (OUT / f"{screen}-{vp}.json").write_text(json.dumps(rec, indent=1, ensure_ascii=True), encoding="utf-8")
                    short = {k: rec[k] for k in ("capture", "golden_elements", "candidate_elements", "matched", "by_kind")}
                    short["by_property"] = rec["by_property"]
                    summary["captures"].append(short)
                    print(json.dumps(short), flush=True)
            browser.close()
    finally:
        summary["stopped"] = gr.stop_server(proc, port)
        (OUT.parent / "dom-compare-summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
        print(json.dumps({"stopped": summary["stopped"]}), flush=True)


if __name__ == "__main__":
    main()
