"""Read-only hygiene scan for the regression re-check: non-ASCII bytes (so no em or en dash) in what a3d3ed1..HEAD added, and
the committed names that README.md, BUILD.md and qa.md cite checked against the code.

usage: python -B scan_hygiene.py <project root>
Runs `git diff` and `git log` (read-only) and reads files as bytes. Prints, and saves the same text as scan_hygiene_output.txt
next to itself.
"""
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = pathlib.Path(sys.argv[1]).resolve()
LOG = []


def say(text=""):
    print(text, flush=True)
    LOG.append(text)


def git(*args):
    return subprocess.run(["git", *args], cwd=str(ROOT), capture_output=True, check=True).stdout


def main():
    # 1. non-ASCII bytes in added lines, whole range, excluding the solver's evidence folder and my own
    diff = git("diff", "a3d3ed1", "HEAD", "--", ".", ":!docs/modules/app/qa/regression-solver", ":!docs/modules/app/qa/regression-recheck")
    bad = [line for line in diff.split(b"\n") if line.startswith(b"+") and not line.startswith(b"+++") and any(b > 127 for b in line)]
    say(f"added lines with a non-ASCII byte in git diff a3d3ed1 HEAD (solver evidence folder excluded): {len(bad)}")
    for line in bad[:5]:
        say("   " + repr(line[:160]))
    for name in ("README.md", "CLAUDE.md", "docs/modules/app/BUILD.md", "docs/modules/app/spec.md", "docs/modules/app/qa.md",
                 "tests/browser/test_delete.py", "tests/browser/conftest.py", "src/app.js", "src/view.js", "index.html"):
        data = (ROOT / name).read_bytes()
        say(f"non-ASCII bytes in {name}: {sum(b > 127 for b in data)}")
    # 2. commit messages: vendor watermark or Co-Authored-By
    messages = git("log", "a3d3ed1..HEAD", "--format=%h %an <%ae>%n%B").decode("utf-8")
    hits = [m for m in re.findall(r"(?im)^.*(claude|anthropic|co-authored-by|generated with).*$", messages)]
    say(f"commit lines in a3d3ed1..HEAD naming a vendor or Co-Authored-By: {len(hits)}")
    # 3. BUILD.md view.js exports bullet against `export` in src/view.js
    view = (ROOT / "src/view.js").read_text(encoding="utf-8")
    exported = re.findall(r"^export (?:async )?(?:function|const|let|class) ([A-Za-z0-9_]+)", view, re.M)
    build = (ROOT / "docs/modules/app/BUILD.md").read_text(encoding="utf-8")
    bullet = next(line for line in build.splitlines() if line.startswith("- `src/view.js` exports:"))
    # the list ends at the first "Changed" sentence
    listed = re.findall(r"`([A-Za-z0-9_]+)`", bullet.split("Changed 2026")[0])
    say(f"view.js exports in code: {len(exported)}; listed in BUILD.md bullet: {len(listed)}; "
        f"in code not listed: {sorted(set(exported) - set(listed))}; listed not in code: {sorted(set(listed) - set(exported))}")
    # 4. BUILD.md app.js bullet: every listed name is a top-level declaration of app.js; which declarations are not listed
    app = (ROOT / "src/app.js").read_text(encoding="utf-8")
    declared = re.findall(r"^(?:async )?(?:function|const|let) ([A-Za-z0-9_]+)", app, re.M)
    bullet = next(line for line in build.splitlines() if line.startswith("- `src/app.js` (exports nothing):"))
    listed = re.findall(r"`([A-Za-z0-9_]+)`", bullet.split("(exports nothing)")[1])
    listed = [name for name in listed if name != "visibilitychange"]
    say(f"app.js declarations: {len(declared)}; listed in BUILD.md app.js bullet: {len(listed)}; "
        f"listed not declared: {sorted(set(listed) - set(declared))}; declared not listed: {sorted(set(declared) - set(listed))}")
    say(f"app.js has an export statement: {bool(re.search(r'^export ', app, re.M))}")
    # 5. README: every backticked identifier of the code map exists somewhere in src/
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    sources = "".join((ROOT / "src" / name).read_text(encoding="utf-8") for name in ("app.js", "view.js", "storage.js", "dates.js", "habits.js"))
    code_map = readme.split("## How it is built")[1].split("## Saved data")[0]
    names = sorted(set(re.findall(r"`([A-Za-z_][A-Za-z0-9_]*)`", code_map)))
    missing = [name for name in names if not re.search(r"\b" + re.escape(name) + r"\b", sources)]
    say(f"README code map: {len(names)} identifiers cited; not found as a word in src/: {missing}")


try:
    main()
finally:
    (HERE / "scan_hygiene_output.txt").write_text("\n".join(LOG) + "\n", encoding="utf-8")
