"""Static checks of the shipped files (index.html, src/) and the publish set. No browser, no server.

Prints findings to stdout. Never prints a secret value: credential-shaped files are reported by path, size,
mtime and key names only.
"""
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
import time
import urllib.parse

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[5]
INDEX = ROOT / "index.html"
SRC = ROOT / "src"
DESIGN = ROOT / "docs" / "design"

R1_CSP = ("default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'none'; "
          "object-src 'none'; base-uri 'none'; form-action 'none'")

print("== 1. CSP")
html = INDEX.read_text(encoding="utf-8")
metas = re.findall(r'<meta http-equiv="Content-Security-Policy" content="([^"]*)">', html)
print("csp metas:", len(metas))
print("equals R1 string:", metas == [R1_CSP])
roadmap = (ROOT / "docs" / "modules" / "ROADMAP.md").read_text(encoding="utf-8")
d2 = re.search(r"\| D2 \| A meta Content Security Policy: `([^`]*)`", roadmap)
print("equals ROADMAP D2 string:", bool(d2) and d2.group(1) == R1_CSP)
head = html.split("</head>")[0]
order = [m.group(0)[:40] for m in re.finditer(r"<(meta|title|link|script)[^>]*>", head)]
print("head order:", order)
csp_pos = head.find("Content-Security-Policy")
print("CSP before every link and script:", all(head.find(t) > csp_pos for t in ("<link", "<script")))

print("== 2. index.html markup")
scripts = re.findall(r"<script\b[^>]*>(.*?)</script>", html, flags=re.S)
print("script elements:", len(scripts), "inline bodies non-empty:", sum(1 for s in scripts if s.strip()))
print("script tags:", re.findall(r"<script\b[^>]*>", html))
print("on* attributes:", re.findall(r"\son[a-z]+\s*=", html))
print("javascript: urls:", re.findall(r"javascript:", html, flags=re.I))
print("xmlns attributes:", re.findall(r"xmlns", html))
urls = re.findall(r'(?:href|src)="([^"]*)"', html)
print("href/src values:", sorted(set(urls)))
print("absolute or scheme urls:", [u for u in urls if u.startswith("/") or re.match(r"^[a-z][a-z0-9+.-]*:", u, re.I)])
print("style attributes:", re.findall(r'style="[^"]*"', html))
print("non-ascii bytes in index.html:", sum(1 for b in INDEX.read_bytes() if b > 127))

print("== 3. banned APIs in src/*.js (code lines)")
banned = {
    "innerHTML/outerHTML/insertAdjacentHTML": r"\b(innerHTML|outerHTML|insertAdjacentHTML)\b",
    "document.write": r"\bdocument\.write",
    "eval / Function ctor": r"\beval\s*\(|\bnew\s+Function\b|(?<![.\w])Function\s*\(",
    "string timers / timers": r"\bset(Timeout|Immediate)\b|\brequestAnimationFrame\b|\bqueueMicrotask\b",
    "network": r"\b(fetch|XMLHttpRequest|WebSocket|EventSource|sendBeacon|RTCPeerConnection)\b|\bimport\s*\(",
    "other storage": r"\b(sessionStorage|indexedDB|caches|cookie)\b",
    "messaging": r"\bpostMessage\b|['\"]message['\"]|BroadcastChannel|SharedWorker|\bWorker\b|serviceWorker",
    "storage event": r"['\"]storage['\"]",
    "navigation / window.open": r"\blocation\b|\bwindow\.open\b|\.open\s*\(",
    "srcdoc / javascript:": r"srcdoc|javascript:",
    "window/globalThis writes": r"\b(window|globalThis|self)\s*(\.\s*[\w$]+\s*=[^=]|\[)",
    "__ dunder names": r"__\w+",
    "console / debugger": r"\bconsole\.|\bdebugger\b",
    "Promise / async": r"\bPromise\b|\basync\b|\bawait\b|\.then\(",
    "clipboard": r"\bclipboard\b|execCommand",
    "dataset / data- from data": r"data-key",
    "selector built from text": r"querySelector(All)?\(\s*`[^`]*\$\{|querySelector(All)?\([^)]*\+|closest\(\s*`[^`]*\$\{",
    "setAttribute('style'|on*)": r"setAttribute\(\s*['\"](style|on\w+|href|src)['\"]",
}
for path in sorted(SRC.glob("*.js")):
    lines = path.read_text(encoding="utf-8").splitlines()
    in_block = False
    for number, line in enumerate(lines, 1):
        code = line
        stripped = code.strip()
        if stripped.startswith("/*") or stripped.startswith("*") or stripped.startswith("//"):
            continue
        code = re.sub(r"//.*$", "", code)
        for label, pattern in banned.items():
            if re.search(pattern, code):
                print(f"  {path.name}:{number} [{label}] {stripped[:150]}")

print("== 4. non-ascii bytes per src file")
for path in sorted(SRC.iterdir()):
    data = path.read_bytes()
    print(f"  {path.name}: {len(data)} bytes, non-ascii {sum(1 for b in data if b > 127)}")

print("== 5. icon.svg against the goldens (R29, T13)")
icon = (SRC / "icon.svg").read_bytes()
payloads = {}
for golden in sorted(DESIGN.glob("*.html")):
    m = re.search(r'<link rel="icon"[^>]*href="([^"]*)"', golden.read_text(encoding="utf-8"))
    if m:
        href = m.group(1)
        payloads[golden.name] = urllib.parse.unquote(href.split(",", 1)[1]).encode("utf-8")
print("goldens with an icon link:", sorted(payloads))
print("distinct payloads:", len(set(payloads.values())))
print("icon.svg equals every payload:", all(p == icon for p in payloads.values()))
text = icon.decode("utf-8")
for label, pattern in {"script": r"<script", "on* attribute": r"\son\w+\s*=", "href/xlink": r"href",
                       "url(": r"url\(", "@import": r"@import", "foreignObject": r"foreignObject",
                       "entity/DOCTYPE": r"<!DOCTYPE|<!ENTITY", "external scheme": r"https?://(?!www\.w3\.org/2000/svg)"}.items():
    print(f"  icon {label}: {re.findall(pattern, text, flags=re.I)}")
print("icon sha256:", hashlib.sha256(icon).hexdigest())

print("== 6. habit data in shipped files (R26)")
sample = json.loads((DESIGN / "sample-history.json").read_text(encoding="utf-8"))
names = [h["name"] for h in sample["habits"]]
fixture = ROOT / "tests" / "fixtures" / "sample-history-v1.0.0.json"
if fixture.exists():
    names += [h["name"] for h in json.loads(fixture.read_text(encoding="utf-8"))["habits"]]
shipped = [INDEX] + sorted(p for p in SRC.iterdir() if p.is_file())
hits = []
for path in shipped:
    body = path.read_text(encoding="utf-8")
    for name in set(names):
        if name in body:
            hits.append((path.name, name))
    if "sample-history" in body:
        hits.append((path.name, "sample-history"))
print("sample names checked:", len(set(names)), "hits:", hits)

print("== 7. publish set (CLAUDE.md Publish: index.html, src/, .nojekyll)")
for path in shipped:
    st = path.stat()
    print(f"  {path.relative_to(ROOT).as_posix()} {st.st_size} bytes sha256 {hashlib.sha256(path.read_bytes()).hexdigest()[:16]}")
print("src entries:", sorted(p.name for p in SRC.iterdir()))
print(".nojekyll at root:", (ROOT / ".nojekyll").exists())
tracked_src = subprocess.run(["git", "-C", str(ROOT), "ls-files", "src", "index.html"], capture_output=True, text=True, timeout=30).stdout.split()
print("tracked shipped files:", tracked_src)
refs_out = []
for path in shipped:
    for m in re.finditer(r"(docs/|tests/|harness/|\.\./)", path.read_text(encoding="utf-8")):
        refs_out.append((path.name, m.group(0)))
print("shipped files referring to docs/, tests/, harness/ or ../:", sorted(set(refs_out)))
workflows = list((ROOT / ".github").rglob("*")) if (ROOT / ".github").exists() else []
print("deploy workflow files:", [p.relative_to(ROOT).as_posix() for p in workflows])

print("== 8. credential-shaped files and strings (names only, never values)")
name_pattern = re.compile(r"(^\.env(\..*)?$|\.pem$|\.key$|\.p12$|\.pfx$|credentials\.json$|^id_(rsa|ed25519)|\.npmrc$|\.netrc$|secrets?\.(json|ya?ml|txt)$)", re.I)
skip = {".git", "node_modules", "__pycache__", ".pytest_cache"}
found = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in skip]
    for filename in filenames:
        if name_pattern.search(filename):
            p = pathlib.Path(dirpath) / filename
            st = p.stat()
            found.append(f"{p.relative_to(ROOT).as_posix()} size={st.st_size} mtime={time.strftime('%Y-%m-%d %H:%M', time.localtime(st.st_mtime))}")
print("credential-shaped file names:", found)
secret_patterns = {
    "github token": r"gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}",
    "aws key id": r"AKIA[0-9A-Z]{16}",
    "openai/anthropic style": r"\bsk-[A-Za-z0-9_-]{20,}",
    "private key block": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    "assignment": r"(?i)\b(api[_-]?key|secret|password|passwd|token|bearer)\b\s*[:=]\s*['\"][^'\"]{6,}",
}
for path in shipped:
    body = path.read_text(encoding="utf-8")
    for label, pattern in secret_patterns.items():
        count = len(re.findall(pattern, body))
        if count:
            print(f"  {path.name}: {label} x{count}")
print("secret-pattern scan of shipped files done")
