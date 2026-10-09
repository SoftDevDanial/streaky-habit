"""T10: the app framed by another origin, with a REAL top-page server (an in-process thread), not a route.

probe_07b and 07c served the top page through page.route, which Chromium's Local Network Access check treated as a
public page, so the loopback frame was blocked (ERR_BLOCKED_BY_LOCAL_NETWORK_ACCESS_CHECKS). Here the framing page is
served from a real loopback listener. Cross-site: top http://localhost:<p2>, frame http://127.0.0.1:<p1>. Same-site:
top http://127.0.0.1:<p2>, frame http://127.0.0.1:<p1>.
Run: PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python <this file>   (cwd = project root)
"""
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit
from lib import Run, new_context, state_text, row_names, SAMPLE_HABITS

SEED = state_text(SAMPLE_HABITS)


def make_top(origin):
    page = f'<!doctype html><title>attacker</title><iframe id="f" src="{origin}/" style="width:390px;height:844px;border:0"></iframe>'.encode()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(page)

        def log_message(self, *args):
            pass

    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


def main():
    with Run() as run:
        b, base = run.browser, run.base
        origin = base.rstrip("/")
        top_server = make_top(origin)
        p2 = top_server.server_address[1]
        try:
            for label, top_origin in [("cross-site (top localhost:p2, frame 127.0.0.1:p1)", f"http://localhost:{p2}"),
                                      ("same-site other origin (top 127.0.0.1:p2, frame 127.0.0.1:p1)", f"http://127.0.0.1:{p2}")]:
                ctx = new_context(b)
                first = ctx.new_page()
                first.goto(base + "__seed__")
                first.evaluate("(t) => localStorage.setItem('streaks.state', t)", SEED)
                first.goto(base)
                first.wait_for_selector("li.habit")
                first_rows = row_names(first)
                top = ctx.new_page()
                cons = []
                top.on("console", lambda m: cons.append(m.text[:120]))
                top.goto(top_origin + "/frame.html")
                top.wait_for_timeout(2000)
                frame = [f for f in top.frames if f != top.main_frame]
                f = frame[0] if frame else None
                cells = f.evaluate("() => document.querySelectorAll('.cells .hc').length") if f else None
                rows = f.evaluate("() => [...document.querySelectorAll('h3.habit-name')].map(e => e.textContent)") if f else None
                ls = f.evaluate("() => { try { return 'ok, streaks.state ' + (localStorage.getItem('streaks.state') ? 'present' : 'absent'); } catch (e) { return 'threw ' + e.name; } }") if f else None
                print(f"{label}")
                print(f"    frame url={f.url if f else None}; app rendered (cells={cells}); framed app habits={rows}; first-party habits were {first_rows}")
                print(f"    framed localStorage: {ls}")
                print(f"    top page reading the frame's document: {top.evaluate('() => { try { return document.getElementById(\"f\").contentDocument === null ? \"null (cross-origin)\" : \"READABLE\"; } catch (e) { return \"threw \" + e.name; } }')}")
                if f:
                    # a deliberate click inside the frame works (clickjacking surface exists): add a habit in the framed copy
                    f.locator("#new-habit").click()
                    top.keyboard.type("Framed add")
                    top.keyboard.press("Enter")
                    top.wait_for_timeout(300)
                    print(f"    after typing into the framed app: framed habits={f.evaluate('() => [...document.querySelectorAll(\"h3.habit-name\")].map(e => e.textContent)')}; first-party page still {row_names(first)} (reload to check)")
                    first.reload()
                    first.wait_for_selector("li.habit")
                    print(f"    first-party habits after reload: {row_names(first)}")
                ctx.close()
        finally:
            top_server.shutdown()
            top_server.server_close()
    print("done")


if __name__ == "__main__":
    main()
