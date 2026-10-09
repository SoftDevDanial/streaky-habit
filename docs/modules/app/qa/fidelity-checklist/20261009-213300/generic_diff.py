"""Whole-page structural and computed-style comparison of each golden with the running app (scratch).

For S1, S2 and M1 at 390x844 and 1280x800 it serialises both pages (every element: attributes, own text, rectangle,
all computed styles, the ::before and ::after styles) and walks the two trees side by side. It reports every
difference, grouped, so that nothing the 0.1 pixel threshold hides can stay hidden. Writes generic_diff.json.
"""
import difflib
import json
import re
import sys
from collections import defaultdict

from common import *  # noqa: F401,F403
from playwright.sync_api import sync_playwright

AFTER_LOAD = (ROOT / "tests/browser/fidelity/open-delete-dialog.js").read_text(encoding="utf-8")


def sig(node):
    return (node["tag"], node["attrs"].get("class", ""), node["attrs"].get("id", ""))


def norm_attr(name, value):
    if name == "style":
        return re.sub(r"\s+", "", value)
    return value


def label(node, index):
    s = node["tag"]
    if node["attrs"].get("id"):
        s += "#" + node["attrs"]["id"]
    if node["attrs"].get("class"):
        s += "." + ".".join(node["attrs"]["class"].split())
    return f"{s}[{index}]"


def compare(g, c, path, out):
    # attributes
    ga = {k: norm_attr(k, v) for k, v in g["attrs"].items()}
    ca = {k: norm_attr(k, v) for k, v in c["attrs"].items()}
    for k in sorted(set(ga) | set(ca)):
        if ga.get(k) != ca.get(k):
            out["attr"].append({"path": path, "attr": k, "golden": ga.get(k), "candidate": ca.get(k)})
    if g["text"] != c["text"]:
        out["text"].append({"path": path, "golden": g["text"], "candidate": c["text"]})
    if any(abs(a - b) > 0.01 for a, b in zip(g["rect"], c["rect"])):
        out["rect"].append({"path": path, "golden": g["rect"], "candidate": c["rect"]})
    for p in sorted(set(g["style"]) | set(c["style"])):
        if g["style"].get(p) != c["style"].get(p):
            out["style"].append({"path": path, "prop": p, "golden": g["style"].get(p), "candidate": c["style"].get(p)})
    for ps in ("pseudo::before", "pseudo::after"):
        gp, cp = g.get(ps), c.get(ps)
        if (gp is None) != (cp is None):
            out["pseudo_presence"].append({"path": path, "pseudo": ps, "golden": gp is not None, "candidate": cp is not None})
        elif gp is not None:
            for p in sorted(set(gp) | set(cp)):
                if gp.get(p) != cp.get(p):
                    out["pseudo_style"].append({"path": path, "pseudo": ps, "prop": p, "golden": gp.get(p), "candidate": cp.get(p)})
    # children, aligned by (tag, class, id)
    gs = [sig(n) for n in g["children"]]
    cs = [sig(n) for n in c["children"]]
    sm = difflib.SequenceMatcher(None, gs, cs, autojunk=False)
    for op, g1, g2, c1, c2 in sm.get_opcodes():
        if op == "equal":
            for off in range(g2 - g1):
                gn, cn = g["children"][g1 + off], c["children"][c1 + off]
                compare(gn, cn, f"{path} > {label(gn, g1 + off)}", out)
        else:
            for i in range(g1, g2):
                n = g["children"][i]
                out["only_golden"].append({"path": f"{path} > {label(n, i)}", "text": n["text"][:60], "rect": n["rect"]})
            for i in range(c1, c2):
                n = c["children"][i]
                out["only_candidate"].append({"path": f"{path} > {label(n, i)}", "text": n["text"][:60], "rect": n["rect"]})


def group(items, keys):
    groups = defaultdict(list)
    for it in items:
        groups[tuple(it[k] for k in keys)].append(it["path"])
    return [
        {**dict(zip(keys, k)), "count": len(v), "examples": v[:3]}
        for k, v in sorted(groups.items(), key=lambda kv: -len(kv[1]))
    ]


def run():
    result = {}
    with sync_playwright() as pw:
        browser = launch(pw)
        for screen in ("S1", "S2", "M1"):
            for vk, vp in VIEWPORTS.items():
                # reduced motion "reduce" like the harness, so the dumps are in the state the gate photographs
                gctx, gpage = open_page(browser, golden_url(screen), vp, reduced="reduce")
                cctx, cpage = open_page(browser, BASE, vp, seed=screen != "S2", reduced="reduce")
                if screen == "M1":
                    cpage.evaluate(f"async () => {{ {AFTER_LOAD}\n }}")
                    cpage.wait_for_timeout(300)
                gt = gpage.evaluate(TREE_JS)
                ct = cpage.evaluate(TREE_JS)
                backdrop = None
                if screen == "M1":
                    backdrop = cpage.evaluate(
                        "() => { const cs = getComputedStyle(document.querySelector('dialog.dialog'), '::backdrop');"
                        " return {background: cs.backgroundColor, position: cs.position, inset: cs.inset, display: cs.display}; }"
                    )
                out = defaultdict(list)
                compare(gt["body"], ct["body"], "body", out)
                html_diffs = [
                    {"prop": p, "golden": gt["html"].get(p), "candidate": ct["html"].get(p)}
                    for p in sorted(set(gt["html"]) | set(ct["html"]))
                    if gt["html"].get(p) != ct["html"].get(p)
                ]
                key = f"{screen}-{vk}"
                result[key] = {
                    "scroll_golden": gt["scroll"],
                    "scroll_candidate": ct["scroll"],
                    "html_style_diffs": html_diffs,
                    "attr_diffs": out["attr"],
                    "text_diffs": out["text"],
                    "rect_diffs": out["rect"],
                    "only_golden": out["only_golden"],
                    "only_candidate": out["only_candidate"],
                    "style_diffs_grouped": group(out["style"], ["prop", "golden", "candidate"]),
                    "pseudo_presence_diffs": out["pseudo_presence"],
                    "pseudo_style_diffs_grouped": group(out["pseudo_style"], ["pseudo", "prop", "golden", "candidate"]),
                    "counts": {k: len(v) for k, v in out.items()},
                    "element_count_golden": len(json.dumps(gt["body"]).split('"tag"')) - 1,
                    "element_count_candidate": len(json.dumps(ct["body"]).split('"tag"')) - 1,
                    "backdrop": backdrop,
                }
                gctx.close()
                cctx.close()
        browser.close()
    save_json("generic_diff.json", result)
    for key, r in result.items():
        print(key, r["counts"], "elements", r["element_count_golden"], r["element_count_candidate"])


run()
