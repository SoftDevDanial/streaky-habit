"""Does Playwright's page.clock move Event.timeStamp? It decides how the tests can pass the guard window of the dialog.

Measured per case: the event.timeStamp gaps between three clicks, with a real wait of 300 ms between clicks 1 and 2 and
page.clock.run_for(450) between clicks 2 and 3 (nothing for "set_fixed_time", where run_for does not apply).
Result recorded in evidence.md: with an installed clock the timestamps follow the fake time (frozen while paused, moved by
run_for), with a fixed time they follow real time.
Run: PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python -B <this file>   (cwd = project root). Writes nothing.
"""
import sys

sys.path.insert(0, "{workspace}/examples/streaks/docs/modules/app/qa/security/20261009T165000")
from lib import Run, new_context, NOON  # noqa: E402

SCRIPT = """
window.__stamps = [];
document.addEventListener('click', (e) => window.__stamps.push([e.timeStamp, performance.now(), e.detail]), true);
"""


def main():
    with Run() as run:
        for label, touch, mode in [
            ("mouse, installed and running", False, "install"),
            ("touch, installed and running", True, "install"),
            ("mouse, installed and paused", False, "paused"),
            ("touch, installed and paused", True, "paused"),
            ("mouse, set_fixed_time", False, "fixed"),
        ]:
            kw = {"has_touch": True} if touch else {}
            ctx = new_context(run.browser, fixed_time=NOON, **kw) if mode == "fixed" else new_context(run.browser, install_time=NOON, **kw)
            page = ctx.new_page()
            page.goto(run.base + "__seed__")
            page.evaluate(SCRIPT)
            if mode == "paused":
                page.clock.pause_at("2026-10-08T12:00:05+08:00")
            tap = page.touchscreen.tap if touch else page.mouse.click
            tap(10, 10)
            page.wait_for_timeout(300)
            tap(10, 10)
            if mode != "fixed":
                page.clock.run_for(450)
            tap(10, 10)
            stamps = page.evaluate("() => window.__stamps")
            gaps = [round(stamps[i + 1][0] - stamps[i][0], 1) for i in range(len(stamps) - 1)]
            print(f"{label}: event.timeStamp = {[round(s[0], 1) for s in stamps]}, gaps 1-2 and 2-3 = {gaps}")
            ctx.close()
    print("done")


if __name__ == "__main__":
    main()
