"""T5 control for probe_03b: the same page WITHOUT the CSP, script blocked, to prove the native GET submission is real.

probe_03b's control matched only the exact path, so the query URL was not served and the run proved nothing. This one
matches the path with or without a query string.
Run: PYTHONDONTWRITEBYTECODE=1 python <this file>   (cwd = project root)
"""
import re
import time
from lib import Run, new_context, attach


def main():
    with Run() as run:
        b, base = run.browser, run.base
        ctx = new_context(b)
        page = ctx.new_page()
        html = (run.server.directory / "index.html").read_text(encoding="utf-8")
        no_csp = re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]*>', "", html)
        assert no_csp != html
        page.route(re.compile(r".*/control\.html(\?.*)?$"), lambda route: route.fulfill(status=200, content_type="text/html", body=no_csp))
        page.route("**/src/app.js", lambda route: route.abort())
        log = attach(page)
        page.goto(base + "control.html")
        page.locator("#new-habit").click()
        page.keyboard.type("No alcohol secret")
        before = page.url
        page.keyboard.press("Enter")
        time.sleep(1.5)
        print(f"CONTROL (no CSP, script blocked): url before={before}")
        print(f"                                  url after ={page.url}")
        print(f"   requests with a query string: {[r['url'] for r in log.requests if '?' in r['url']]}")
        ctx.close()
    print("done")


if __name__ == "__main__":
    main()
