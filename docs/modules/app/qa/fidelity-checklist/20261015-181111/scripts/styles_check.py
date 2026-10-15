"""Per-element computed-style check from the harness's own styles.json (qa.md, Fidelity gate, Method).

Run from the project root:  python -B <this file> <checklist folder> <capture folder> [<capture folder> ...]
Matches golden and candidate entries by path and occurrence (the n-th element with that path), then compares
text, rect and the 27 properties the harness dumps. Writes <checklist folder>/styles-json-check.json, refusing
to overwrite. Reads only.
"""
import collections
import json
import pathlib
import sys

out_dir = pathlib.Path(sys.argv[1])
target = out_dir / "styles-json-check.json"
if target.exists():
    sys.exit(f"refused, {target} exists")


def keyed(entries):
    seen = collections.Counter()
    result = {}
    order = []
    for e in entries:
        k = f"{e['path']}|{seen[e['path']]}"
        seen[e["path"]] += 1
        result[k] = e
        order.append(k)
    return result, order


results = []
for folder in sys.argv[2:]:
    folder = pathlib.Path(folder)
    data = json.loads((folder / "styles.json").read_text(encoding="utf-8"))
    g, gorder = keyed(data["golden"])
    c, corder = keyed(data["candidate"])
    only_g = [k for k in gorder if k not in c]
    only_c = [k for k in corder if k not in g]
    rect_d, text_d, style_d = [], [], collections.Counter()
    style_examples = collections.defaultdict(list)
    for k in gorder:
        if k not in c:
            continue
        a, b = g[k], c[k]
        if a["rect"] != b["rect"]:
            rect_d.append({"key": k, "golden": a["rect"], "candidate": b["rect"]})
        if a.get("text") != b.get("text"):
            text_d.append({"key": k, "golden": a.get("text"), "candidate": b.get("text")})
        for p, v in a["styles"].items():
            if b["styles"].get(p) != v:
                style_d[p] += 1
                if len(style_examples[p]) < 4:
                    style_examples[p].append({"key": k, "golden": v, "candidate": b["styles"].get(p)})
    order_same = [k for k in gorder if k in c] == [k for k in corder if k in g]
    results.append({
        "capture": folder.as_posix(),
        "golden_entries": len(gorder), "candidate_entries": len(corder),
        "golden_capped_at_600": len(gorder) >= 600, "candidate_capped_at_600": len(corder) >= 600,
        "matched": sum(1 for k in gorder if k in c), "same_order": order_same,
        "golden_only": only_g, "candidate_only": only_c,
        "rect_differences": rect_d, "text_differences": text_d,
        "style_differences_by_property": dict(style_d), "style_examples": dict(style_examples),
    })
    print(json.dumps({"capture": folder.parent.name, "g": len(gorder), "c": len(corder), "matched": results[-1]["matched"],
                      "golden_only": only_g[:6], "candidate_only": only_c[:6], "rect": len(rect_d), "text": len(text_d),
                      "styles": dict(style_d), "same_order": order_same}))

out_dir.mkdir(parents=True, exist_ok=True)
target.write_text(json.dumps(results, indent=1), encoding="utf-8")
print("wrote", target.as_posix())
