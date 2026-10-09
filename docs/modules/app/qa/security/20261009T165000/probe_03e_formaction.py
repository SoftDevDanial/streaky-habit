"""T5 native submission, final version (supersedes probe_03b, 03c and 03d).

Those used time.sleep, which does not pump Playwright's sync event loop, so their request and navigation logs were
read before the events arrived. This one waits with page.wait_for_timeout. Three cases: a CSP-free copy of the page with
the script blocked (positive control: the native GET is real), the real page with the script blocked, and the real page
with JavaScript disabled.
Run: PYTHONDONTWRITEBYTECODE=1 python <this file>   (cwd = project root)
"""
import re
from lib import Run, new_context, attach


def report(label, page, log, before):
    page.wait_for_timeout(1500)
    queries = [r["url"] for r in log.requests if "?" in r["url"]]
    print(f"--- {label}")
    print(f"   url before={before}")
    print(f"   url after ={page.url}")
    print(f"   requests whose URL carries a query string: {queries}")
    print(f"   console: {[c['text'][:150] for c in log.console]}")


def main():
    with Run() as run:
        b, base = run.browser, run.base
        html = (run.server.directory / "index.html").read_text(encoding="utf-8")
        no_csp = re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]*>', "", html)
        assert "Content-Security-Policy" not in no_csp

        ctx = new_context(b)
        page = ctx.new_page()
        page.route(re.compile(r".*/control\.html.*"), lambda route: route.fulfill(status=200, content_type="text/html", body=no_csp))
        page.route("**/src/app.js", lambda route: route.abort())
        log = attach(page)
        page.goto(base + "control.html")
        page.locator("#new-habit").click()
        page.keyboard.type("No alcohol secret")
        before = page.url
        page.keyboard.press("Enter")
        report("CONTROL, no CSP, app.js blocked, Enter (a native GET with ?name= is expected)", page, log, before)
        ctx.close()

        ctx = new_context(b)
        page = ctx.new_page()
        page.route("**/src/app.js", lambda route: route.abort())
        log = attach(page)
        page.goto(base)
        page.locator("#new-habit").click()
        page.keyboard.type("No alcohol secret")
        before = page.url
        page.keyboard.press("Enter")
        report("REAL page, app.js blocked, Enter in the field", page, log, before)
        page.locator("button.btn-primary").click()
        report("REAL page, app.js blocked, click Add", page, log, before)
        ctx.close()

        ctx = new_context(b, java_script_enabled=False)
        page = ctx.new_page()
        log = attach(page)
        page.goto(base)
        page.locator("#new-habit").fill("No alcohol secret")
        before = page.url
        page.keyboard.press("Enter")
        report("REAL page, JavaScript disabled, Enter in the field", page, log, before)
        ctx.close()
    print("done")


if __name__ == "__main__":
    main()
