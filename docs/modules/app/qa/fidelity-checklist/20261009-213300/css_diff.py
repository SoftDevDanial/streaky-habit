"""Compares src/styles.css with the style block of each golden (scratch, read-only). Comments and whitespace are ignored,
as spec R2 says. Reports the rule-level differences, so that the three changes R2 allows are the only ones.
Writes css_diff.json.
"""
import difflib
import json
import re
from pathlib import Path

ROOT = Path(r"{workspace}\examples\streaks")
HERE = Path(__file__).resolve().parent


def strip(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    return re.sub(r"\s+", " ", css).strip()


def golden_block(path):
    html = path.read_text(encoding="utf-8")
    style = re.search(r"<style>(.*?)</style>", html, flags=re.S).group(1)
    start = style.index(":root {")
    end_marker = "/* ---------- end components ---------- */"
    end = style.index(end_marker) + len(end_marker)
    return style[start:end]


def rules(css):
    """Splits a stripped stylesheet into top-level rules (blocks may nest one level for @media and @keyframes)."""
    out, depth, cur = [], 0, ""
    for ch in css:
        cur += ch
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                out.append(cur.strip())
                cur = ""
    if cur.strip():
        out.append(cur.strip())
    return out


app = strip((ROOT / "src/styles.css").read_text(encoding="utf-8"))
result = {"goldens": {}}
blocks = {}
for name in ("today", "today-empty", "delete-dialog", "states"):
    block = strip(golden_block(ROOT / f"docs/design/{name}.html"))
    blocks[name] = block
    gr, ar = rules(block), rules(app)
    sm = difflib.SequenceMatcher(None, gr, ar, autojunk=False)
    changes = []
    for op, g1, g2, a1, a2 in sm.get_opcodes():
        if op != "equal":
            changes.append({"op": op, "golden": gr[g1:g2], "app": ar[a1:a2]})
    result["goldens"][name] = {"golden_rules": len(gr), "app_rules": len(ar), "identical_to_app": block == app, "changes": changes if name == "delete-dialog" or name == "today" else [{"op": c["op"], "golden_rule_count": len(c["golden"]), "app_rule_count": len(c["app"])} for c in changes]}
result["four_goldens_have_the_same_block"] = len(set(blocks.values())) == 1
(HERE / "css_diff.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(result, indent=1, ensure_ascii=False)[:6000])
