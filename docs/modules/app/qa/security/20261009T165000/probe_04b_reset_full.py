"""R17 + R18 together: unreadable saved value while the origin is full, so the reset save itself fails.

probe_04's last case booted the app once before filling, so it never reached this path. Here the value and the filler are
both written from the same-origin 404 page, before the app first loads.
Run: PYTHONDONTWRITEBYTECODE=1 python <this file>   (cwd = project root)
"""
from lib import Run, new_context, attach, stored

FILL = """() => {
  let size = 1 << 22, filler = '';
  localStorage.clear();
  localStorage.setItem('streaks.state', '{');
  while (size >= 1) {
    try { localStorage.setItem('filler', filler + 'x'.repeat(size)); filler += 'x'.repeat(size); } catch (e) { size >>= 1; }
  }
  return filler.length;
}"""


def main():
    with Run() as run:
        b, base = run.browser, run.base
        ctx = new_context(b)
        page = ctx.new_page()
        log = attach(page)
        page.goto(base + "__seed__")
        print("filler chars:", page.evaluate(FILL))
        print("a 27-char write fails:", page.evaluate("() => { try { localStorage.setItem('streaks.state', '{\"version\":1,\"habits\":[]}'); return false; } catch (e) { return e.name; } }"))
        page.goto(base)
        print(f"boot 1: note={page.locator('div.note').count()} p.empty={page.locator('p.empty').count()} stored={stored(page)!r}")
        page.locator("#new-habit").click()
        page.keyboard.type("Walk")
        page.keyboard.press("Enter")
        print(f"   add Walk while the origin is full: rows={page.locator('h3.habit-name').all_text_contents()}")
        page.reload()
        print(f"boot 2: note={page.locator('div.note').count()} (the note shows again because the reset could not be saved) stored={stored(page)!r}")
        print(f"console errors={len(log.console_errors())} page errors={log.errors}")
        ctx.close()
    print("done")


if __name__ == "__main__":
    main()
