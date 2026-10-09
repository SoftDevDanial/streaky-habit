"""Independent R2 check: golden style block vs src/styles.css, token level, plus the whole diff.

usage: python css_diff.py <project root>      (reads only)
"""
import difflib
import pathlib
import re
import sys

ROOT = pathlib.Path(sys.argv[1])
golden = (ROOT / "docs/design/today.html").read_text(encoding="utf-8")
m = re.search(r":root \{.*?/\* ---------- end components ---------- \*/", golden, re.DOTALL)
block = m.group(0)
app = (ROOT / "src/styles.css").read_text(encoding="utf-8")

print("golden block chars", len(block), "app css chars", len(app))
print("app starts with:", repr(app[:200]))


def norm(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    css = re.sub(r"\s+", " ", css).strip()
    return css


def tokens(css):
    css = norm(css)
    # split into rule-ish chunks at braces/semicolons so the diff is readable
    return re.findall(r"[^{};]+[{};]", css)


g = tokens(block)
a = tokens(app)
print("golden tokens", len(g), "app tokens", len(a))
for line in difflib.unified_diff(g, a, "golden", "app", lineterm="", n=1):
    print(line)

print("---- raw line diff (golden block vs app file) ----")
gl = block.splitlines()
al = app.splitlines()
for line in difflib.unified_diff(gl, al, "golden", "app", lineterm="", n=0):
    print(line)
