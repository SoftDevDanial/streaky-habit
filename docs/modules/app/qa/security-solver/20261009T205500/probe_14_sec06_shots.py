"""Pictures of the SEC-06 repro name on the real tree: before the fix (commit 8e655e8, its view.js put back in memory with
page.route) and with the fix (the working tree), and the SEC-02 residual name with the fix. The dialog element is saved as PNG
in shots/ (written by Playwright). Read-only against the app; nothing is stored beyond the seeded state of a throwaway context.
Run: PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python -B <this file>   (cwd = project root)
"""
import pathlib
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "security-recheck" / "20261009T201546"))

from chars import ALEF, LRI, PDI, RLO  # noqa: E402
from lib import ROOT, Run, open_app, state_text  # noqa: E402

BASE = "8e655e8"
NAMES = {"alef-lri-abc": ALEF + LRI + "abc", "pdi-rlo-yz": "x" + PDI + RLO + "y z"}


def shot(run, label, name, patched_view):
    ctx, page = open_app(run.browser, run.base, (390, 844), False, seed=state_text([{"name": name, "done": []}]))
    try:
        if patched_view is not None:
            page.route("**/src/view.js", lambda route, request: route.fulfill(status=200, content_type="text/javascript", body=patched_view))
            page.reload()
            page.wait_for_selector("li.habit")
        page.locator("button.icon-btn").first.click()
        page.wait_for_selector("dialog[open]")
        page.locator("dialog").evaluate("(d) => Promise.all(d.getAnimations().map((a) => a.finished))")
        (HERE / "shots").mkdir(exist_ok=True)
        page.locator("dialog").screenshot(path=str(HERE / "shots" / f"sec06-{label}.png"))
        run.say(f"  saved shots/sec06-{label}.png (page errors: {page.errors})")
    finally:
        ctx.close()


def main():
    base_view = subprocess.run(["git", "show", f"{BASE}:src/view.js"], cwd=str(ROOT), capture_output=True, check=True).stdout.decode("utf-8")
    with Run() as run:
        for key, name in NAMES.items():
            shot(run, f"{key}-before-{BASE}", name, base_view)
            shot(run, f"{key}-fixed", name, None)


if __name__ == "__main__":
    main()
