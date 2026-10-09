"""New-threat hunt: rollover with hostile stored dates, device-clock extremes, DOM clobbering, tampered data-date,
dialog and focus paths, and the two-tab overwrite (T12).

After a fake clock is installed this probe waits with expect(), because in-page polling uses the mocked timers.
Run: PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python <this file>   (cwd = project root)
"""
from playwright.sync_api import expect
from lib import Run, new_context, attach, open_app, state_text, stored, row_names, SAMPLE_HABITS

SEED = state_text(SAMPLE_HABITS)


def cells_summary(page):
    return page.evaluate("() => { const c = [...document.querySelectorAll('.cells .hc')]; return {n: c.length, future: c.filter(e => e.classList.contains('future')).length, today: c.filter(e => e.classList.contains('today')).length, firstLabel: c[0].getAttribute('aria-label'), todayLabel: (document.querySelector('.hc.today') || {getAttribute: () => null}).getAttribute('aria-label')}; }")


def main():
    with Run() as run:
        b, base = run.browser, run.base

        print("--- rollover with hostile but valid stored dates (far past, far future, window edges)")
        hostile = state_text([{"name": "Edge", "done": ["0001-01-01", "2026-10-02", "2026-10-08", "2026-10-09", "2026-10-10", "2026-10-11", "2026-10-12", "9999-12-31"]},
                              {"name": "Far", "done": ["0001-01-01", "9999-12-31"]}])
        ctx, page, log = open_app(b, base, storage=hostile, fixed_time=None, install_time="2026-10-08T23:59:30+08:00")
        expect(page.locator("li.habit")).to_have_count(2)
        before = cells_summary(page)
        page.clock.run_for(61_000)
        expect(page.locator(".date time")).to_have_attribute("datetime", "2026-10-09")
        after = cells_summary(page)
        streaks = page.locator(".streak").all_inner_texts()
        print(f"    before {before}")
        print(f"    after  {after}; streak lines {streaks}")
        print(f"    cons_err={len(log.console_errors())} page_err={log.errors}")
        for _ in range(3):
            page.clock.run_for(24 * 3600 * 1000)
        print(f"    3 more days: header {page.locator('.date time').inner_text()}; page_err={log.errors}")
        ctx.close()

        print("--- device clock extremes (not attacker reachable: needs control of the clock)")
        for label, when in [("year 9999-12-31 23:59:30 rolling into 10000", "9999-12-31T23:59:30+00:00"), ("year 0001-01-02", "0001-01-02T12:00:00+00:00"), ("year 1970", "1970-01-01T12:00:00+00:00"), ("year 2100-02-28 into leap-less 03-01", "2100-02-28T23:59:30+00:00")]:
            try:
                ctx = new_context(b, fixed_time=None, install_time=when)
                page = ctx.new_page()
                log = attach(page)
                page.goto(base)
                expect(page.locator(".cells .hc").first).to_be_attached()
                head = page.locator(".date time").inner_text()
                key = page.locator(".date time").get_attribute("datetime")
                page.locator("#new-habit").click()
                page.keyboard.type("Clock test")
                page.keyboard.press("Enter")
                page.locator("li.habit button.day").last.click()
                page.clock.run_for(61_000)
                print(f"    {label}: header '{head}' key '{key}' -> after +61s '{page.locator('.date time').get_attribute('datetime')}'; cons_err={len(log.console_errors())} page_err={log.errors[:1]}")
                saved = stored(page)
                page.reload()
                expect(page.locator(".cells .hc").first).to_be_attached()
                print(f"       saved={saved[:110]}  after reload: rows={row_names(page)} note={page.locator('div.note').count()}")
                ctx.close()
            except Exception as error:  # noqa: BLE001
                print(f"    {label}: EXCEPTION {str(error)[:160]}")

        print("--- DOM clobbering: names equal to ids and special words")
        names = ["new-habit", "new-habit-msg", "del-title", "h1-name", "habits-title", "document", "location", "localStorage", "__proto__", "constructor", "length", "forms", "name", "toString", "children", "ownerDocument"]
        ctx, page, log = open_app(b, base, storage=state_text([{"name": n, "done": []} for n in names[:12]]))
        ids = page.evaluate("() => ['new-habit', 'new-habit-msg', 'del-title', 'h1-name', 'habits-title', 'heat-title', 'del-body'].map(i => [i, document.querySelectorAll('#' + i).length, document.getElementById(i) && document.getElementById(i).tagName])")
        print(f"    ids resolve to the app's own elements after loading 12 habits named like ids: {ids}")
        page.locator("#new-habit").click()
        page.keyboard.type("ownerDocument")
        page.keyboard.press("Enter")
        print(f"    typed name 'ownerDocument' -> error shown (12 habits is the limit, input disabled)? input disabled={page.locator('#new-habit').is_disabled()}")
        page.get_by_role("button", name="Delete document", exact=True).click()
        page.locator("dialog .btn-danger").click()
        page.wait_for_timeout(300)
        print(f"    delete the habit named 'document' works: rows={len(row_names(page))}; cons_err={len(log.console_errors())} page_err={log.errors}")
        page.locator("#new-habit").click()
        page.keyboard.type("forms")
        page.keyboard.press("Enter")
        page.wait_for_timeout(200)
        print(f"    add 'forms' works: rows={len(row_names(page))}; window.forms/document.forms intact={page.evaluate('() => document.forms.length')}; cons_err={len(log.console_errors())}")
        ctx.close()

        print("--- tampered data-date on a day button (devtools or an extension): window-checked in toggleDay")
        ctx, page, log = open_app(b, base, storage=SEED)
        for label, value in [("outside window (2020-01-01)", "2020-01-01"), ("__proto__", "__proto__"), ("empty", ""), ("a 4 MB string", "x" * 4_000_000), ("future 2026-10-09", "2026-10-09"), ("inside window, other day 2026-10-05", "2026-10-05")]:
            page.evaluate("(v) => document.querySelector('li.habit button.day').setAttribute('data-date', v)", value)
            before = stored(page)
            page.locator("li.habit button.day").first.click()
            page.wait_for_timeout(100)
            after = stored(page)
            print(f"    data-date {label}: changed state={before != after}; cons_err={len(log.console_errors())} page_err={log.errors[:1]}")
        ctx.close()

        print("--- dialog and focus paths")
        ctx, page, log = open_app(b, base, storage=SEED, fixed_time=None, install_time="2026-10-08T23:59:40+08:00")
        page.get_by_role("button", name="Delete Stretch 10 minutes", exact=True).click()
        page.clock.run_for(40_000)
        expect(page.locator(".date time")).to_have_attribute("datetime", "2026-10-09")
        print(f"    rollover while the dialog is open: dialog open={page.evaluate('() => document.querySelector(\"dialog\").open')} title={page.locator('#del-title').inner_text()!r}")
        page.locator("dialog .btn-danger").click()
        expect(page.locator("li.habit")).to_have_count(2)
        print(f"    delete after rollover removes the habit named in the title: rows={row_names(page)}; focus={page.evaluate('() => document.activeElement.getAttribute(\"aria-label\")')}")
        ctx.close()

        ctx, page, log = open_app(b, base, storage=SEED)
        page.get_by_role("button", name="Delete Read 20 pages", exact=True).click()
        r1 = page.evaluate("() => { const d = document.querySelector('dialog'); try { d.showModal(); return 'showModal on an open dialog did not throw'; } catch (e) { return 'showModal again threw ' + e.name; } }")
        print(f"    {r1}; habits={len(row_names(page))}")
        page.keyboard.press("Escape")
        page.keyboard.press("Tab")
        print(f"    focus after Esc then Tab: {page.evaluate('() => document.activeElement.tagName + \":\" + (document.activeElement.getAttribute(\"aria-label\") || document.activeElement.textContent.trim().slice(0, 20))')}")
        ctx.close()

        print("--- T12 two tabs: last save wins (accepted residual)")
        ctx = new_context(b)
        a = ctx.new_page(); a.goto(base); a.wait_for_selector(".cells .hc")
        c = ctx.new_page(); c.goto(base); c.wait_for_selector(".cells .hc")
        a.locator("#new-habit").click(); a.keyboard.type("From A"); a.keyboard.press("Enter")
        c.locator("#new-habit").click(); c.keyboard.type("From B"); c.keyboard.press("Enter")
        a.reload(); a.wait_for_selector(".cells .hc")
        print(f"    after A adds 'From A' then B adds 'From B' (B opened before A saved): stored rows={row_names(a)}")
        ctx.close()
    print("done")


if __name__ == "__main__":
    main()
