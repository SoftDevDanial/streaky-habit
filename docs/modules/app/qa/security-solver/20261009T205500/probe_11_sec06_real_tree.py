"""SEC-06 on the real tree: the same 27 names as the re-check's probe_10, measured with the title line before the fix
(commit 8e655e8, its src/view.js put back in memory with page.route) and with the working tree as it stands (the fix, from disk).

For every name: are the opening quote, the name, the closing quote and the question mark in reading order, is the title text
exactly Delete, quote, FSI, the name without the stripped characters, PDI, quote, question mark, is the stored name the one
that was seeded, and does the trash button's aria-label still hold the name as typed.
It imports the re-check's helpers (read only) and does NOT call `Run.finish`, which would write into that folder.
Run: PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python -B <this file>   (cwd = project root)
"""
import json
import pathlib
import re
import subprocess
import sys

sys.dont_write_bytecode = True
RECHECK = pathlib.Path(__file__).resolve().parents[2] / "security-recheck" / "20261009T201546"
sys.path.insert(0, str(RECHECK))

from chars import FSI, PDI, chars  # noqa: E402
from lib import ROOT, Run  # noqa: E402
from probe_06_sec02_title import FIVE, MORE, RESIDUAL, ok, title_spots  # noqa: E402
from probe_08_sec02_unmatched_initiator import NAMES as INITIATOR_NAMES  # noqa: E402

# The stripped set, written out here independently of the app's regular expression (built from code points).
STRIPPED = re.compile("[" + "".join(chr(c) for c in (*range(0x202A, 0x202F), *range(0x2066, 0x206A), 0x0085, *range(0x001C, 0x001F), 0x2029)) + "]")


BASE = "8e655e8"  # the commit before the fix: HEAD moved to the fix, so the base is named, not HEAD


def committed_view():
    """src/view.js as committed at BASE (read only; git show prints it)."""
    return subprocess.run(["git", "show", f"{BASE}:src/view.js"], cwd=str(ROOT), capture_output=True, check=True).stdout.decode("utf-8")


def main():
    head_view = committed_view()
    with Run() as run:
        say = run.say
        say(f"  the view.js of {BASE} has no TITLE_STRIPPED in it: " + str("TITLE_STRIPPED" not in head_view))
        groups = (("suite names (SEC-02)", FIVE), ("extra names", MORE), ("accepted residual (b): U+2069 / U+2029 then an override", RESIDUAL),
                  ("SEC-06 names and controls", INITIATOR_NAMES))
        total = in_place_head = in_place_fix = text_ok = untouched = 0
        for group, names in groups:
            say(f"  -- {group} --")
            for label, name in names.items():
                head = title_spots(run, name, head_view)
                fixed = title_spots(run, name)
                expected = f'Delete "{FSI}{STRIPPED.sub("", name)}{PDI}"?'
                same_text = fixed["text"] == expected
                keeps_name = fixed["trash_label"] == "Delete " + name and json.loads(fixed["stored"])["habits"][0]["name"] == name
                total += 1
                in_place_head += ok(head)
                in_place_fix += ok(fixed)
                text_ok += same_text
                untouched += keeps_name
                say(f"    {label:50s} {BASE}: {'in place' if ok(head) else 'QUOTES MOVED':12s} | fix: {'in place' if ok(fixed) else 'QUOTES MOVED':12s} | title text as specified: {same_text} | trash label and stored name hold the typed name: {keeps_name}")
        say(f"  names measured: {total}; in place at {BASE}: {in_place_head}; in place with the fix: {in_place_fix}; title text as specified: {text_ok}; trash label and stored name unchanged: {untouched}")


if __name__ == "__main__":
    main()
