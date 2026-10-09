"""T5 native submission with JavaScript disabled in the context (the other half of probe_03e, which stopped at a click
that Playwright could not finish: after a CSP-blocked form navigation it waits for a navigation that never commits).
Run: PYTHONDONTWRITEBYTECODE=1 python <this file>   (cwd = project root)
"""
from lib import Run, new_context, attach


def main():
    with Run() as run:
        b, base = run.browser, run.base
        ctx = new_context(b, java_script_enabled=False)
        page = ctx.new_page()
        log = attach(page)
        page.goto(base)
        page.locator("#new-habit").fill("No alcohol secret")
        before = page.url
        page.keyboard.press("Enter")
        page.wait_for_timeout(1500)
        print(f"JS disabled, Enter: url before={before} after={page.url}")
        print(f"   requests with a query string: {[r['url'] for r in log.requests if '?' in r['url']]}")
        print(f"   console: {[c['text'][:150] for c in log.console]}")
        ctx.close()
    print("done")


if __name__ == "__main__":
    main()
