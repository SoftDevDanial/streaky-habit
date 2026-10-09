"""probe_08 stopped in its DOM-clobbering section (it typed into the input that is disabled at 12 habits). This runs the
rest: clobbering names, tampered data-date, dialog and focus paths, and the two-tab overwrite (T12).

After a fake clock is installed this probe waits with expect(), because in-page polling uses the mocked timers.
Run: PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python <this file>   (cwd = project root)
"""
from playwright.sync_api import expect
from lib import Run, new_context, open_app, state_text, stored, row_names, SAMPLE_HABITS

SEED = state_text(SAMPLE_HABITS)


def main():
    with Run() as run:
        b, base = run.browser, run.base

        print("--- DOM clobbering: habits named like ids and special words")
        names = ["new-habit", "new-habit-msg", "del-title", "h1-name", "habits-title", "document", "location", "localStorage", "__proto__", "constructor", "length", "forms"]
        ctx, page, log = open_app(b, base, storage=state_text([{"name": n, "done": []} for n in names]))
        ids = page.evaluate("() => ['new-habit', 'new-habit-msg', 'del-title', 'h1-name', 'habits-title', 'heat-title', 'del-body'].map(i => [i, document.querySelectorAll('#' + i).length, document.getElementById(i) && document.getElementById(i).tagName])")
        print(f"    ids resolve to the app's own elements: {ids}")
        print(f"    window.document is the document, window.location is the Location, forms intact: {page.evaluate('() => [document.forms.length, typeof location.href, typeof localStorage.getItem]')}")
        page.get_by_role("button", name="Delete document", exact=True).click()
        page.locator("dialog .btn-danger").click()
        expect(page.locator("li.habit")).to_have_count(11)
        page.locator("#new-habit").click()
        page.keyboard.type("ownerDocument")
        page.keyboard.press("Enter")
        expect(page.locator("li.habit")).to_have_count(12)
        print(f"    delete 'document' then add 'ownerDocument' works: rows={len(row_names(page))} cons_err={len(log.console_errors())} page_err={log.errors}")
        ctx.close()

        print("--- tampered data-date on a day button (devtools or an extension)")
        ctx, page, log = open_app(b, base, storage=SEED)
        for label, value in [("outside window (2020-01-01)", "2020-01-01"), ("__proto__", "__proto__"), ("empty", ""), ("a 4 MB string", "x" * 4_000_000), ("future 2026-10-09", "2026-10-09"), ("inside window, other day 2026-10-05", "2026-10-05")]:
            page.evaluate("(v) => document.querySelector('li.habit button.day').setAttribute('data-date', v)", value)
            before = stored(page)
            page.locator("li.habit button.day").first.click()
            page.wait_for_timeout(100)
            after = stored(page)
            print(f"    data-date {label}: state changed={before != after}; cons_err={len(log.console_errors())} page_err={log.errors[:1]}")
        ctx.close()

        print("--- dialog and focus paths")
        ctx, page, log = open_app(b, base, storage=SEED, fixed_time=None, install_time="2026-10-08T23:59:40+08:00")
        page.get_by_role("button", name="Delete Stretch 10 minutes", exact=True).click()
        page.clock.run_for(40_000)
        expect(page.locator(".date time")).to_have_attribute("datetime", "2026-10-09")
        print(f"    rollover while the dialog is open: dialog open={page.evaluate('() => document.querySelector(\"dialog\").open')} title={page.locator('#del-title').inner_text()!r}")
        page.locator("dialog .btn-danger").click()
        expect(page.locator("li.habit")).to_have_count(2)
        print(f"    delete after rollover removes the habit named in the title: rows={row_names(page)}; focus={page.evaluate('() => document.activeElement.getAttribute(\"aria-label\")')}; page_err={log.errors}")
        ctx.close()

        ctx, page, log = open_app(b, base, storage=SEED)
        page.get_by_role("button", name="Delete Read 20 pages", exact=True).click()
        r1 = page.evaluate("() => { const d = document.querySelector('dialog'); try { d.showModal(); return 'showModal on an open dialog did not throw'; } catch (e) { return 'showModal again threw ' + e.name; } }")
        print(f"    {r1}; habits={len(row_names(page))}")
        page.keyboard.press("Escape")
        page.keyboard.press("Tab")
        print(f"    focus after Esc then Tab: {page.evaluate('() => document.activeElement.tagName + \":\" + (document.activeElement.getAttribute(\"aria-label\") || document.activeElement.textContent.trim().slice(0, 20))')}")
        print(f"    cons_err={len(log.console_errors())} page_err={log.errors}")
        ctx.close()

        print("--- T12 two tabs: last save wins (accepted residual)")
        ctx = new_context(b)
        a = ctx.new_page(); a.goto(base); a.wait_for_selector(".cells .hc")
        c = ctx.new_page(); c.goto(base); c.wait_for_selector(".cells .hc")
        a.locator("#new-habit").click(); a.keyboard.type("From A"); a.keyboard.press("Enter")
        c.locator("#new-habit").click(); c.keyboard.type("From B"); c.keyboard.press("Enter")
        a.reload(); a.wait_for_selector(".cells .hc")
        print(f"    A adds 'From A', then B (opened before A saved) adds 'From B': stored rows={row_names(a)}")
        ctx.close()
    print("done")


if __name__ == "__main__":
    main()
