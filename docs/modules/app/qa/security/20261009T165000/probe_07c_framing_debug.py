"""T10 debug: why did probe_07b see no app in the frame? Prints frames, requests, console and the frame's DOM.
Run: PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python <this file>   (cwd = project root)
"""
import re
from urllib.parse import urlsplit
from lib import Run, new_context, state_text, SAMPLE_HABITS

SEED = state_text(SAMPLE_HABITS)


def main():
    with Run() as run:
        b, base = run.browser, run.base
        origin = base.rstrip("/")
        port = urlsplit(base).port
        top_origin = f"http://localhost:{port}"
        ctx = new_context(b)
        first = ctx.new_page()
        first.goto(base + "__seed__")
        first.evaluate("(t) => localStorage.setItem('streaks.state', t)", SEED)
        html = f'<!doctype html><title>attacker</title><iframe id="f" src="{origin}/" style="width:390px;height:844px"></iframe>'

        def handle(route, request, html=html):
            route.fulfill(status=200, content_type="text/html", body=html)

        top = ctx.new_page()
        reqs, cons = [], []
        top.on("request", lambda r: reqs.append((r.method, r.url, r.resource_type)))
        top.on("requestfailed", lambda r: reqs.append(("FAILED", r.url, r.failure)))
        top.on("console", lambda m: cons.append((m.type, m.text[:200])))
        top.route(re.compile(re.escape(top_origin) + r"/frame\.html.*"), handle)
        top.goto(top_origin + "/frame.html")
        top.wait_for_timeout(2500)
        print("frames:", [f.url for f in top.frames])
        for r in reqs:
            print("  req", r)
        print("console:", cons)
        for f in top.frames:
            if f != top.main_frame:
                try:
                    print("frame body (first 200 chars):", f.evaluate("() => document.body ? document.body.innerHTML.slice(0, 200) : 'no body'"))
                    print("frame has cells:", f.evaluate("() => document.querySelectorAll('.cells .hc').length"))
                    print("frame localStorage access:", f.evaluate("() => { try { return 'ok, keys=' + localStorage.length + ' streaks=' + (localStorage.getItem('streaks.state') ? 'present' : 'absent'); } catch (e) { return 'threw ' + e.name; } }"))
                except Exception as error:  # noqa: BLE001
                    print("frame evaluate failed:", error)
        ctx.close()
    print("done")


if __name__ == "__main__":
    main()
