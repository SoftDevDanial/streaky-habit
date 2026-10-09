"""Does Chromium keep a dialog's returnValue between openings? (view.js openDeleteDialog says it does.)

Result on Chromium 149.0.7827.55: after Delete the value is 'delete', it is still 'delete' right after the next
showModal(), and the close event of a later Esc reports ''. So the reset in openDeleteDialog is a safeguard for
engines whose Esc keeps the stale value, and its removal cannot be seen on Chromium (QA mutant M11).
"""
from playwright.sync_api import sync_playwright

PAGE = """<dialog id=d><form method=dialog><button value=cancel>Cancel</button><button value=delete id=del>Delete</button></form></dialog>
<script>window.log = []; d.addEventListener('close', () => log.push(d.returnValue));</script>"""

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.set_content(PAGE)
    page.evaluate("() => d.showModal()")
    page.click("#del")
    page.wait_for_function("() => log.length === 1")
    print("after Delete: returnValue =", repr(page.evaluate("() => d.returnValue")))
    page.evaluate("() => d.showModal()")
    print("right after reopening (no reset by the page): returnValue =", repr(page.evaluate("() => d.returnValue")))
    page.keyboard.press("Escape")
    page.wait_for_function("() => log.length === 2")
    print("close event values:", page.evaluate("() => log"))
    print("browser", browser.version)
    browser.close()
