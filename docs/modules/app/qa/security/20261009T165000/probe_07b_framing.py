"""T10: the app framed by another origin (probe_07 part 4, whose route handler took the wrong arguments).

Cross-site top page (localhost over 127.0.0.1) and same-site top page (another port on 127.0.0.1). For each: is the app
rendered in the frame (no frame-ancestors, no X-Frame-Options), and does the frame see the habits saved first-party?
Run: PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python <this file>   (cwd = project root)
"""
import re
from urllib.parse import urlsplit
from lib import Run, new_context, state_text, row_names, SAMPLE_HABITS

SEED = state_text(SAMPLE_HABITS)


def main():
    with Run() as run:
        b, base = run.browser, run.base
        origin = base.rstrip("/")
        port = urlsplit(base).port
        for label, top_origin in [("cross-site (top localhost, frame 127.0.0.1)", f"http://localhost:{port}"),
                                  ("same-site other origin (top 127.0.0.1:1, frame 127.0.0.1:port)", "http://127.0.0.1:1")]:
            ctx = new_context(b)
            first = ctx.new_page()
            first.goto(base + "__seed__")
            first.evaluate("(t) => localStorage.setItem('streaks.state', t)", SEED)
            first.goto(base)
            first.wait_for_selector("li.habit")
            first_rows = row_names(first)
            html = f'<!doctype html><title>attacker</title><iframe id="f" src="{origin}/" style="width:390px;height:844px"></iframe>'

            def handle(route, request, html=html):
                route.fulfill(status=200, content_type="text/html", body=html)

            top = ctx.new_page()
            top.route(re.compile(re.escape(top_origin) + r"/frame\.html.*"), handle)
            top.goto(top_origin + "/frame.html")
            top.wait_for_timeout(1500)
            frame = top.frame_locator("#f")
            framed = frame.locator(".cells .hc").count() > 0
            rows = frame.locator("h3.habit-name").all_text_contents()
            print(f"{label}: app rendered inside the frame={framed}; framed app habits={rows}; first-party habits were {first_rows}")
            # what a framing page can do to the framed app from outside: nothing cross-origin; show that parent cannot read it
            can_read = top.evaluate("() => { try { return document.getElementById('f').contentDocument === null ? 'contentDocument null (cross-origin)' : 'READABLE'; } catch (e) { return 'threw ' + e.name; } }")
            print(f"    top page reading the frame's document: {can_read}")
            ctx.close()
    print("done")


if __name__ == "__main__":
    main()
