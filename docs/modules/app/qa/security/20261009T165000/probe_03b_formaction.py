"""T5 native submission: the add form with the script blocked or disabled, and with a CSP-free control page.

form-action 'none' must stop a GET submission that would put the typed name in a URL.
Run: PYTHONDONTWRITEBYTECODE=1 python <this file>   (cwd = project root)
"""
import time
from lib import Run, new_context, attach, state_text


def report(label, page, log, before):
    time.sleep(1.2)
    queries = [r["url"] for r in log.requests if "?" in r["url"]]
    print(f"--- {label}")
    print(f"   url before={before}")
    print(f"   url after ={page.url}")
    print(f"   requests whose URL carries a query string: {queries}")
    print(f"   console: {[c['text'][:150] for c in log.console]}")


def main():
    with Run() as run:
        b, base = run.browser, run.base

        # control: the same form on a page WITHOUT the CSP (copy of index.html served by the probe through a route)
        ctx = new_context(b)
        page = ctx.new_page()
        html = (run.server.directory / "index.html").read_text(encoding="utf-8")
        import re
        no_csp = re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]*>', "", html)
        assert no_csp != html
        page.route("**/control.html", lambda route: route.fulfill(status=200, content_type="text/html", body=no_csp))
        page.route("**/src/app.js", lambda route: route.abort())
        log = attach(page)
        page.goto(base + "control.html")
        page.locator("#new-habit").click()
        page.keyboard.type("No alcohol secret")
        before = page.url
        page.keyboard.press("Enter")
        report("CONTROL (no CSP, app.js blocked): Enter in the field -> a native GET with ?name= is expected", page, log, before)
        ctx.close()

        # the real page, app.js blocked
        ctx = new_context(b)
        page = ctx.new_page()
        page.route("**/src/app.js", lambda route: route.abort())
        log = attach(page)
        page.goto(base)
        page.locator("#new-habit").click()
        page.keyboard.type("No alcohol secret")
        before = page.url
        page.keyboard.press("Enter")
        report("REAL page, app.js blocked: Enter in the field", page, log, before)
        page.evaluate("() => document.querySelector('.add').requestSubmit()")
        report("REAL page, app.js blocked: requestSubmit()", page, log, before)
        ctx.close()

        # the real page, javascript disabled
        ctx = new_context(b, java_script_enabled=False)
        page = ctx.new_page()
        log = attach(page)
        page.goto(base)
        page.locator("#new-habit").fill("No alcohol secret")
        before = page.url
        page.keyboard.press("Enter")
        report("REAL page, JavaScript disabled: Enter in the field", page, log, before)
        ctx.close()
    print("done")


if __name__ == "__main__":
    main()
