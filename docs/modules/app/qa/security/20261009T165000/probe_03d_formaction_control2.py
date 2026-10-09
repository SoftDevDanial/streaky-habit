"""T5 control, second attempt: serve the CSP-free copy from a real file path via a route that handles any query string.

Prints the navigation events and the response status, to see whether the native submission is made.
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
        assert "Content-Security-Policy" not in no_csp
        seen = []

        def handle(route):
            seen.append(route.request.url)
            route.fulfill(status=200, content_type="text/html", body=no_csp)

        page.route(re.compile(r".*/control\.html.*"), handle)
        page.route("**/src/app.js", lambda route: route.abort())
        page.on("framenavigated", lambda f: seen.append("framenavigated " + f.url))
        log = attach(page)
        page.goto(base + "control.html")
        print("loaded; CSP meta present:", page.evaluate("() => !!document.querySelector('meta[http-equiv]')"))
        page.locator("#new-habit").click()
        page.keyboard.type("No alcohol secret")
        print("input value:", page.locator("#new-habit").input_value())
        page.keyboard.press("Enter")
        time.sleep(1.5)
        print("after Enter  url:", page.url)
        page.evaluate("() => document.querySelector('.add').requestSubmit()")
        time.sleep(1.5)
        print("after requestSubmit url:", page.url)
        page.evaluate("() => document.querySelector('.add').submit()")
        time.sleep(1.5)
        print("after submit() url:", page.url)
        print("route/nav events:", seen)
        print("form attrs:", page.evaluate("() => { const f = document.querySelector('.add'); return {action: f.action, method: f.method, noValidate: f.noValidate, inputName: f.querySelector('input').name}; }"))
        ctx.close()
    print("done")


if __name__ == "__main__":
    main()
