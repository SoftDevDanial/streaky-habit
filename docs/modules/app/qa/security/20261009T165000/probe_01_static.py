"""Static scan of the shipped files for sinks and egress APIs (T3, T5, T11, R24, R26). Prints hits with line numbers.

Run: PYTHONDONTWRITEBYTECODE=1 python <this file>   (no browser, no server)
"""
import pathlib
import re
from lib import ROOT

FILES = [ROOT / "index.html"] + sorted((ROOT / "src").glob("*.js")) + [ROOT / "src" / "styles.css"]

PATTERNS = {
    "html sinks": r"innerHTML|outerHTML|insertAdjacentHTML|document\.write|createContextualFragment|DOMParser|srcdoc|\.setHTML|execCommand|\bSetHTMLUnsafe\b|setHTMLUnsafe",
    "code from string": r"\beval\b|new\s+Function|\bFunction\s*\(|setTimeout\s*\(\s*[\"'`]|setInterval\s*\(\s*[\"'`]|\bimport\s*\(",
    "network": r"\bfetch\b|XMLHttpRequest|WebSocket|EventSource|sendBeacon|navigator\.|\bpostMessage\b|BroadcastChannel|serviceWorker|\bImage\s*\(|window\.open|\bping=",
    "navigation": r"location\s*[.=]|history\.|\.href\s*=|\.src\s*=|\.action\s*=|document\.domain|target=",
    "other storage": r"sessionStorage|indexedDB|document\.cookie|caches\b|\bcookie\b",
    "globals": r"\bwindow\s*\.\s*\w+\s*=|globalThis|\bself\b\s*\.|\bwindow\[",
    "dynamic selectors": r"querySelector(All)?\s*\(\s*[`\"'][^`\"']*\$\{|querySelector(All)?\s*\([^)]*\+",
    "url() in css": r"url\s*\(|@import",
    "inline handlers/js urls in html": r"\son[a-z]+\s*=|javascript:",
    "external urls": r"https?://",
}

total = 0
for name, pattern in PATTERNS.items():
    hits = []
    for f in FILES:
        for number, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if re.search(pattern, line):
                hits.append(f"{f.relative_to(ROOT).as_posix()}:{number}: {line.strip()[:150]}")
    total += len(hits)
    print(f"== {name}: {len(hits)} hit(s)")
    for h in hits:
        print("   ", h)

print("\nsetAttribute / textContent / className / style call sites in src/ (every data-to-DOM write):")
for f in sorted((ROOT / "src").glob("*.js")):
    if f.name in ("dates.js", "habits.js"):
        continue
    for number, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
        if re.search(r"setAttribute|textContent|className|\.style\.|\.value\s*=|\.append\(|\.prepend\(|replaceChildren|createElement", line):
            print(f"    {f.name}:{number}: {line.strip()[:140]}")

print("\nsrc/ import specifiers (must be relative):")
for f in sorted((ROOT / "src").glob("*.js")):
    for number, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
        if re.match(r"\s*import\b", line):
            print(f"    {f.name}:{number}: {line.strip()}")

print("\nnon-ASCII / bidi / control characters in shipped files:")
for f in FILES:
    text = f.read_text(encoding="utf-8")
    bad = [(i, hex(ord(c))) for i, c in enumerate(text) if (ord(c) > 126 or (ord(c) < 32 and c not in "\n\r\t"))]
    print(f"    {f.name}: {len(bad)} {bad[:5]}")
