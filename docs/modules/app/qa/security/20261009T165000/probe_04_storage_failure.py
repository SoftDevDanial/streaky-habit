"""T6 / R18: storage blocked, throwing, or really full. The app must keep working in memory with no exception in the console.

Cases: window.localStorage getter throws SecurityError; Storage.prototype.getItem throws; setItem throws QuotaExceededError
(seeded readable state); a really full origin (a filler key written to the brim); unreadable value with a full origin.
Each case runs add, tick, delete through real gestures and then reads console errors and page errors.
Run: PYTHONDONTWRITEBYTECODE=1 python <this file>   (cwd = project root)
"""
from lib import Run, open_app, state_text, stored, row_names, SAMPLE_HABITS

BLOCK_GETTER = "Object.defineProperty(window, 'localStorage', { get() { throw new DOMException('denied', 'SecurityError'); }, configurable: true });"
THROW_GET = "Storage.prototype.getItem = function () { throw new DOMException('denied', 'SecurityError'); };"
THROW_SET = "Storage.prototype.setItem = function () { throw new DOMException('full', 'QuotaExceededError'); };"

FILL = """() => {
  let size = 1 << 22, filler = '';
  localStorage.removeItem('filler');
  while (size >= 1) {
    try { localStorage.setItem('filler', filler + 'x'.repeat(size)); filler += 'x'.repeat(size); } catch (e) { size >>= 1; }
  }
  return filler.length;
}"""


def gestures(page, label, log):
    """add, tick, add again, delete, with real clicks; print what the page shows afterwards."""
    page.locator("#new-habit").click()
    page.keyboard.type("Walk")
    page.get_by_role("button", name="Add", exact=True).click()
    page.locator("li.habit").filter(has=page.get_by_text("Walk", exact=True)).locator("button.day").last.click()
    page.locator("#new-habit").click()
    page.keyboard.type("Stretch")
    page.keyboard.press("Enter")
    page.wait_for_timeout(200)
    names = row_names(page)
    page.get_by_role("button", name="Delete Walk", exact=True).click()
    page.locator("dialog .btn-danger").click()
    page.wait_for_function("() => !document.querySelector('dialog').open")
    page.wait_for_timeout(200)
    after = row_names(page)
    print(f"   {label}: rows after add+tick+add: {names} ; after delete Walk: {after}; "
          f"cons_err={[c['text'][:100] for c in log.console_errors()]} page_err={log.errors}", flush=True)


def main():
    with Run() as run:
        b, base = run.browser, run.base
        seed = state_text(SAMPLE_HABITS)

        print("--- localStorage getter throws SecurityError (qa.md R18 form)")
        ctx, page, log = open_app(b, base, init_script=BLOCK_GETTER)
        print(f"   boot: note={page.locator('div.note').count()} p.empty={page.locator('p.empty').count()} cons_err={len(log.console_errors())} page_err={log.errors}")
        gestures(page, "blocked getter", log)
        ctx.close()

        print("--- Storage.prototype.getItem throws")
        ctx, page, log = open_app(b, base, storage=seed, init_script=THROW_GET)
        print(f"   boot: note={page.locator('div.note').count()} rows={row_names(page)} (sample is stored but unreadable to the app)")
        gestures(page, "getItem throws", log)
        ctx.close()

        print("--- Storage.prototype.setItem throws QuotaExceededError (saves fail)")
        ctx, page, log = open_app(b, base, storage=seed, init_script=THROW_SET)
        print(f"   boot: rows={row_names(page)}")
        gestures(page, "setItem throws", log)
        print(f"   stored value unchanged (changes live in memory only): {stored(page) == seed}")
        page.reload()
        print(f"   after reload the in-memory changes are gone: rows={row_names(page)}  (accepted residual CG-5)")
        ctx.close()

        print("--- a really full origin (filler key written to the brim)")
        ctx, page, log = open_app(b, base, storage=seed)
        used = page.evaluate(FILL)
        full = page.evaluate("() => { try { localStorage.setItem('probe', 'y'.repeat(100)); return false; } catch (e) { return e.name; } }")
        print(f"   filler {used} chars; a 100-char write now throws: {full}")
        page.reload()
        gestures(page, "full origin", log)
        print(f"   stored value unchanged by the failed saves: {stored(page) == seed}")
        ctx.close()

        print("--- unreadable value with a full origin (the reset save fails)")
        ctx, page, log = open_app(b, base, storage="{")
        page.evaluate(FILL)
        page.reload()
        print(f"   boot: note={page.locator('div.note').count()} p.empty={page.locator('p.empty').count()} stored={stored(page)!r}")
        page.reload()
        print(f"   second boot: note={page.locator('div.note').count()} (note repeats while the reset cannot be saved)  cons_err={len(log.console_errors())} page_err={log.errors}")
        ctx.close()
    print("done")


if __name__ == "__main__":
    main()
