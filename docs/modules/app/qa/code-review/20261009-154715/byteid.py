"""Is the golden style block byte-identical in the four goldens, as spec R2 claims ("measured")?

usage: python byteid.py <docs/design folder>      (reads only)
"""
import hashlib
import pathlib
import re
import sys

design = pathlib.Path(sys.argv[1])
block = re.compile(r":root \{.*?/\* ---------- end components ---------- \*/", re.DOTALL)
for name in ("today.html", "today-empty.html", "delete-dialog.html", "states.html"):
    text = (design / name).read_bytes().decode("utf-8")
    found = block.search(text)
    raw = found.group(0)
    print(name, "chars", len(raw), "sha1", hashlib.sha1(raw.encode()).hexdigest()[:12],
          "has CRLF" if "\r" in raw else "LF only")
