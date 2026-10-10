"""Debug: why the day editor is open again after a prototype state switch."""
import pathlib

from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
URL = (HERE.parent.parent / "c.html").as_uri()
T = 5000

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    try:
        page = browser.new_page(viewport={"width": 390, "height": 844})
        page.set_default_timeout(T)
        page.on("console", lambda m: print("console:", m.text, flush=True))
        page.goto(URL, wait_until="load", timeout=10000)
        page.evaluate("""() => {
          const d = document.querySelector('#day-dlg');
          const orig = d.showModal.bind(d);
          d.showModal = () => { console.log('showModal from', new Error().stack.split('\\n').slice(1,4).join(' | ')); orig(); };
          document.addEventListener('click', e => console.log('click', e.target.className || e.target.tagName, e.detail, e.isTrusted), true);
          document.addEventListener('keydown', e => console.log('keydown', e.key), true);
        }""")
        st = page.locator('.habit:nth-child(2) .day[aria-current="date"]')
        st.scroll_into_view_if_needed(timeout=T)
        st.click(timeout=T)
        page.click("#proto-toggle", timeout=T)
        page.click('[data-state="k1"]', timeout=T)
        print("menu hidden after k1:", page.evaluate("document.querySelector('#proto-menu').hidden"), flush=True)
        cell = page.locator('.mc[data-date="2026-09-22"]')
        cell.scroll_into_view_if_needed(timeout=T)
        page.evaluate("window.scrollBy(0, 120)")
        cell.click(timeout=T)
        page.click('#day-list .pick:has-text("Read 20 pages")', timeout=T)
        print("menu hidden after pick:", page.evaluate("document.querySelector('#proto-menu').hidden"), flush=True)
        page.keyboard.press("Escape")
        page.wait_for_timeout(100)
        cell.click(timeout=T)
        page.mouse.click(6, 6)
        page.wait_for_timeout(100)
        print("open after backdrop:", page.evaluate("document.querySelector('#day-dlg').open"), flush=True)
        print("menu hidden before toggle:", page.evaluate("document.querySelector('#proto-menu').hidden"), flush=True)
        page.click("#proto-toggle", timeout=T)
        print("open after toggle:", page.evaluate("document.querySelector('#day-dlg').open"), flush=True)
        print("menu hidden after toggle:", page.evaluate("document.querySelector('#proto-menu').hidden"), flush=True)
        page.click('[data-state="k1"]', timeout=T)
        print("open after k1:", page.evaluate("document.querySelector('#day-dlg').open"), flush=True)
    finally:
        browser.close()
