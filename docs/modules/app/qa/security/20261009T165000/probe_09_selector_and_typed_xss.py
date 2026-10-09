"""T4 (selector injection) and T3 (typed names), through real gestures.

Names with CSS selector metacharacters and markup are typed into the field, ticked, reloaded, opened in the dialog
and deleted. The checks: the habit that is ticked or deleted is the one the user acted on (rows are found by position),
nothing is created from a name, no script runs, no console error. Also the typed path for the three spec payloads.
Run: PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python <this file>   (cwd = project root)
"""
from lib import Run, open_app

NAMES = [
    'x"],body,[a="',
    "a'b",
    "a\\",
    "):not(.habit",
    "#h1-name",
    ".habit .day",
    "] [data-date",
    "*",
    "h3, button",
    "<img src=x onerror=alert(1)>",
    "<svg onload=alert(1)>",
    "javascript:alert(1)",
]


def main():
    with Run() as run:
        b, base = run.browser, run.base
        ctx, page, log = open_app(b, base)
        for n in NAMES:
            page.locator("#new-habit").click()
            page.keyboard.type(n)
            page.keyboard.press("Enter")
        names = page.locator("h3.habit-name").all_text_contents()
        print(f"typed {len(NAMES)} names; rows shown: {len(names)}; all literal: {names == NAMES}")
        # tick today on every row in turn and check only that row changed
        problems = 0
        for i in range(len(NAMES)):
            before = page.evaluate("() => [...document.querySelectorAll('li.habit')].map(r => [...r.querySelectorAll('button.day')].map(b => b.getAttribute('aria-pressed')[0]).join(''))")
            page.locator("li.habit").nth(i).locator("button.day").last.click()
            after = page.evaluate("() => [...document.querySelectorAll('li.habit')].map(r => [...r.querySelectorAll('button.day')].map(b => b.getAttribute('aria-pressed')[0]).join(''))")
            changed = [j for j in range(len(NAMES)) if before[j] != after[j]]
            if changed != [i]:
                problems += 1
                print(f"   tick row {i} changed rows {changed}")
        print(f"tick on each row changed only that row: {problems == 0}")
        page.reload()
        page.wait_for_selector("li.habit")
        print(f"after reload rows literal: {page.locator('h3.habit-name').all_text_contents() == NAMES}")
        # delete a middle row by clicking its trash, check the title and the removal
        target = NAMES[3]
        page.locator("li.habit").nth(3).locator(".icon-btn").click()
        title = page.locator("#del-title").inner_text()
        page.locator("dialog .btn-danger").click()
        page.wait_for_timeout(300)
        left = page.locator("h3.habit-name").all_text_contents()
        print(f"delete row 3: title={title!r}; removed exactly it: {left == NAMES[:3] + NAMES[4:]}")
        extra = page.evaluate("() => ({imgs: document.querySelectorAll('img, iframe, script:not([src])').length, handlers: [...document.querySelectorAll('*')].filter(e => [...e.attributes].some(a => /^on/i.test(a.name))).length, svgs: document.querySelectorAll('svg').length})")
        print(f"elements created from names: {extra}")
        print(f"JS dialogs: {log.dialogs}; console errors: {[c['text'][:100] for c in log.console_errors()]}; page errors: {log.errors}")
        ctx.close()
    print("done")


if __name__ == "__main__":
    main()
