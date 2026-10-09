"""Behaviour probes for the code review: does a surviving mutant really behave differently from the app?

usage: python probe.py <work dir> [pristine | id,id,...]
For each (mutant id or "pristine") it serves the work copy with the in-memory patches on a free 127.0.0.1 port,
drives headless Chromium with real gestures, and prints what it observed. It writes no file.
"""
import http.server
import json
import pathlib
import sys
import threading

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from mutants import MUTANTS  # noqa: E402

WORK = pathlib.Path(sys.argv[1]).resolve()
TZ = "Asia/Kuala_Lumpur"
NOON = "2026-10-08T12:00:00+08:00"
SAMPLE = json.loads((WORK / "docs/design/sample-history.json").read_text(encoding="utf-8"))["habits"]
TYPES = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8"}
COUNT_WRITES = """(() => {
  const original = Storage.prototype.setItem;
  let n = 0;
  Storage.prototype.setItem = function (...args) { n++; console.log('SETITEM ' + n); return original.apply(this, args); };
})();"""


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WORK), **kwargs)

    def log_message(self, *args):
        pass

    def do_GET(self):
        path = self.path.split("?", 1)[0].split("#", 1)[0]
        key = "index.html" if path in ("/", "/index.html") else path.lstrip("/")
        body = self.server.patched.get(key)
        if body is None:
            return super().do_GET()
        data = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", TYPES.get(pathlib.PurePosixPath(key).suffix, "application/octet-stream"))
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)


def patched_files(mutant):
    files = {}
    for relpath, old, new in mutant["patches"]:
        text = files.get(relpath) or (WORK / relpath).read_text(encoding="utf-8")
        assert text.count(old) == 1, (mutant["id"], old[:50])
        files[relpath] = text.replace(old, new)
    return files


def state(habits):
    return json.dumps({"version": 1, "habits": habits}, separators=(",", ":"))


class Env:
    def __init__(self, browser, base):
        self.browser, self.base = browser, base

    def open(self, storage=None, fixed=NOON, install=None, viewport=(390, 844), count_writes=False):
        context = self.browser.new_context(viewport={"width": viewport[0], "height": viewport[1]}, device_scale_factor=1,
                                           color_scheme="light", timezone_id=TZ, locale="en-US")
        context.set_default_timeout(5000)
        if install:
            context.clock.install(time=install)
        else:
            context.clock.set_fixed_time(fixed)
        page = context.new_page()
        page.writes = []
        page.errors = []
        if storage is not None:
            page.goto(self.base + "__seed__")
            page.evaluate("(t) => localStorage.setItem('streaks.state', t)", storage)
        if count_writes:
            context.add_init_script(COUNT_WRITES)
        page.on("console", lambda m: page.writes.append(m.text) if m.text.startswith("SETITEM") else None)
        page.on("pageerror", lambda e: page.errors.append(str(e)))
        page.goto(self.base)
        return context, page


def stored(page):
    return page.evaluate("() => localStorage.getItem('streaks.state')")


def probe_decoder_sort(env):
    unsorted = [{"name": "A", "done": ["2026-10-08", "2026-10-07", "2026-10-08"]}, {"name": "B", "done": []}]
    context, page = env.open(storage=state(unsorted))
    page.locator('li.habit:has(h3:text-is("B")) button.day[data-date="2026-10-08"]').click()
    out = json.loads(stored(page))["habits"][0]["done"]
    context.close()
    return f"after a tick on B, A.done in storage = {out}"


def probe_decoder_first_date(env):
    context, page = env.open(storage=state([{"name": "A", "done": ["2026-10-08", "2026-02-30"]}]))
    out = f"notes={page.locator('div.note').count()} rows={page.locator('li.habit').count()} stored={stored(page)}"
    context.close()
    return out


def probe_decoder_dup(env):
    context, page = env.open(storage=state([{"name": "A", "done": []}, {"name": "B", "done": []}, {"name": "a", "done": []}]))
    out = f"notes={page.locator('div.note').count()} rows={page.locator('li.habit').count()}"
    context.close()
    return out


def probe_add_focus(env):
    context, page = env.open(storage=state(SAMPLE))
    page.locator("#new-habit").click()
    page.keyboard.type("Drink")
    page.get_by_role("button", name="Add", exact=True).click()
    out = page.evaluate("() => document.activeElement.tagName + '#' + document.activeElement.id + '.' + document.activeElement.textContent.trim()")
    context.close()
    return f"after clicking Add, focus is on {out}"


def probe_writes(env):
    lines = []
    # sample loaded; open dialog then Cancel / Esc / backdrop; reject an empty name
    context, page = env.open(storage=state(SAMPLE), count_writes=True)
    base = len(page.writes)

    def open_dialog():
        page.get_by_role("button", name="Delete Stretch 10 minutes", exact=True).click()
        page.locator("dialog.dialog[open]").wait_for()

    open_dialog()
    page.get_by_role("button", name="Cancel", exact=True).click()
    page.wait_for_function("() => !document.querySelector('dialog.dialog').open")
    after_cancel = len(page.writes) - base
    open_dialog()
    page.keyboard.press("Escape")
    page.wait_for_function("() => !document.querySelector('dialog.dialog').open")
    after_esc = len(page.writes) - base
    open_dialog()
    page.mouse.click(5, 5)
    page.wait_for_function("() => !document.querySelector('dialog.dialog').open")
    after_backdrop = len(page.writes) - base
    page.get_by_role("button", name="Add", exact=True).click()
    page.wait_for_timeout(100)
    after_reject = len(page.writes) - base
    # The dialog's close event is queued, so each count lags one step behind its gesture.
    lines.append(f"writes: at load={base}, cumulative after Cancel={after_cancel}, Esc={after_esc}, backdrop={after_backdrop}, rejected name={after_reject}")
    context.close()
    # dismiss
    context, page = env.open(storage="{", count_writes=True)
    base = len(page.writes)
    page.get_by_role("button", name="Dismiss note", exact=True).click()
    page.wait_for_timeout(100)
    lines.append(f"writes: unreadable load={base}, after Dismiss={len(page.writes) - base} more")
    context.close()
    # rollover
    context, page = env.open(storage=state(SAMPLE), install="2026-10-08T23:59:30+08:00", count_writes=True)
    base = len(page.writes)
    page.clock.run_for(90000)
    page.wait_for_function("() => document.querySelector('p.date time').textContent === 'Friday 9 October'")
    lines.append(f"writes: at load={base}, after the rollover={len(page.writes) - base} more")
    context.close()
    return "\n      ".join(lines)


def probe_cadence(env):
    result = []
    for after in (31000, 61000):
        context, page = env.open(storage=state(SAMPLE), install="2026-10-08T23:59:58+08:00")
        page.clock.pause_at("2026-10-08T23:59:59+08:00")
        page.clock.run_for(after)
        text = page.locator("p.date time").text_content()
        result.append(f"{after // 1000} s after 23:59:59 (page booted at about 23:59:58) the date reads {text!r}")
        context.close()
    return "; ".join(result)


def probe_cells(env):
    context, page = env.open(storage=state(SAMPLE), install="2026-10-11T23:59:30+08:00")
    page.clock.run_for(90000)
    page.wait_for_function("() => document.querySelector('p.date time').textContent === 'Monday 12 October'")
    data = page.evaluate("""() => {
      const cells = Array.from(document.querySelectorAll('.cells > span'));
      const future = cells.filter((c) => c.className === 'hc future');
      const today = cells.find((c) => c.classList.contains('today'));
      return {
        futureCount: future.length,
        futureWithRoleOrName: future.filter((c) => c.hasAttribute('role') || c.hasAttribute('aria-label')).length,
        futureWithCurrent: future.filter((c) => c.hasAttribute('aria-current')).length,
        todayDate: today.getAttribute('data-date'),
        todayAriaHidden: today.getAttribute('aria-hidden'),
        ariaCurrentCells: cells.filter((c) => c.hasAttribute('aria-current')).map((c) => c.getAttribute('data-date')),
      };
    }""")
    context.close()
    return json.dumps(data)


def probe_best_zero(env):
    context, page = env.open()
    page.locator("#new-habit").click()
    page.keyboard.type("Read")
    page.keyboard.press("Enter")
    bead = page.locator('button.day[data-date="2026-10-08"]')
    bead.click()
    first = page.locator("p.streak").evaluate("(e) => Array.from(e.children).map((c) => c.className + ':' + c.textContent)")
    bead.click()
    second = page.locator("p.streak").evaluate("(e) => Array.from(e.children).map((c) => c.className + ':' + c.textContent)")
    context.close()
    return f"after tick {first}; after untick {second}"


def probe_error_then_delete(env):
    context, page = env.open(storage=state(SAMPLE))
    page.locator("#new-habit").click()
    page.keyboard.type("read 20 pages")
    page.keyboard.press("Enter")
    page.get_by_role("button", name="Delete No phone after 11pm", exact=True).click()
    page.get_by_role("button", name="Delete habit", exact=True).click()
    page.wait_for_function("() => document.querySelectorAll('li.habit').length === 2")
    out = page.evaluate("() => [document.querySelector('#new-habit-msg').textContent, document.querySelector('#new-habit-msg').className, document.querySelector('#new-habit').getAttribute('aria-invalid')]")
    context.close()
    return f"after a duplicate error then a delete: message, class, aria-invalid = {out}"


def probe_svg(env):
    context, page = env.open(storage=state(SAMPLE))
    data = page.evaluate("""() => {
      const svg = document.querySelector('.habit-head .icon-btn svg');
      const rect = svg.getBoundingClientRect();
      return { ns: svg.namespaceURI, w: rect.width, h: rect.height, useNs: svg.firstElementChild.namespaceURI };
    }""")
    context.close()
    return json.dumps(data)


def probe_layout(env):
    context, page = env.open(storage=state(SAMPLE))
    top = page.evaluate("() => Math.round(document.querySelector('h1.brand').getBoundingClientRect().top)")
    page.get_by_role("button", name="Delete Read 20 pages", exact=True).click()
    page.locator("dialog.dialog[open]").wait_for()
    data = page.evaluate("""() => ({
      titleFont: getComputedStyle(document.querySelector('#del-title')).fontSize,
      deleteBg: getComputedStyle(document.querySelector('.dialog-actions button[value=delete]')).backgroundColor,
    })""")
    context.close()
    return f"brand top={top}px; {json.dumps(data)}"


def probe_backdrop_drag_in(env):
    context, page = env.open(storage=state(SAMPLE))
    page.get_by_role("button", name="Delete Read 20 pages", exact=True).click()
    page.locator("dialog.dialog[open]").wait_for()
    box = page.locator("#del-title").bounding_box()
    page.mouse.move(5, 5)
    page.mouse.down()
    page.mouse.move(box["x"] + 20, box["y"] + 10)
    page.mouse.up()
    page.wait_for_timeout(300)
    state_open = page.evaluate("() => document.querySelector('dialog.dialog').open")
    context.close()
    return f"press on the backdrop, release on the title: dialog open = {state_open}"


def probe_svg_pixels(env):
    import io
    from PIL import Image
    context, page = env.open(storage=state(SAMPLE))
    shot = page.get_by_role("button", name="Delete Read 20 pages", exact=True).screenshot()
    image = Image.open(io.BytesIO(shot)).convert("RGB")
    background = image.getpixel((0, 0))
    ink = sum(1 for pixel in image.getdata() if sum(abs(a - b) for a, b in zip(pixel, background)) > 60)
    bead = page.locator('li.habit').first.locator('button.day[aria-pressed="true"] .bead').first.screenshot()
    bead_image = Image.open(io.BytesIO(bead)).convert("RGB")
    light = sum(1 for pixel in bead_image.getdata() if sum(pixel) > 600)
    context.close()
    return f"trash button 44x44: {ink} glyph pixels differ from the background; done bead: {light} near-white check pixels"


def probe_cells_weekday(env):
    context, page = env.open(storage=state(SAMPLE), install="2026-10-08T23:59:30+08:00")
    page.clock.run_for(90000)
    page.wait_for_function("() => document.querySelector('p.date time').textContent === 'Friday 9 October'")
    data = page.evaluate("""() => {
      const cells = Array.from(document.querySelectorAll('.cells > span'));
      const at = (d) => cells.find((c) => c.getAttribute('data-date') === d);
      return {
        fri9: { cls: at('2026-10-09').className, ariaHidden: at('2026-10-09').getAttribute('aria-hidden'), current: at('2026-10-09').getAttribute('aria-current') },
        thu8: { cls: at('2026-10-08').className, current: at('2026-10-08').getAttribute('aria-current') },
        ariaCurrentCells: cells.filter((c) => c.hasAttribute('aria-current')).map((c) => c.getAttribute('data-date')),
      };
    }""")
    context.close()
    return json.dumps(data)


PROBES = {
    None: [probe_decoder_sort, probe_decoder_first_date, probe_decoder_dup, probe_add_focus, probe_writes, probe_cadence,
           probe_cells, probe_cells_weekday, probe_best_zero, probe_error_then_delete, probe_svg, probe_svg_pixels, probe_layout, probe_backdrop_drag_in],
    "S1-no-sort-no-dedupe": [probe_decoder_sort],
    "S2-dedupe-only": [probe_decoder_sort],
    "S3-sort-only": [probe_decoder_sort],
    "S5-first-date-only": [probe_decoder_first_date],
    "S6-duplicate-vs-previous-only": [probe_decoder_dup],
    "A5-add-moves-focus": [probe_add_focus],
    "A1-cancel-resaves": [probe_writes],
    "A2-reject-resaves": [probe_writes],
    "A3-rollover-saves": [probe_writes],
    "A4-dismiss-saves": [probe_writes],
    "A6-interval-60s": [probe_cadence],
    "A6-interval-85s": [probe_cadence],
    "V3-future-cell-keeps-role-label-current": [probe_cells],
    "V4-new-today-cell-keeps-aria-hidden": [probe_cells_weekday],
    "V5-old-today-cell-keeps-aria-current": [probe_cells_weekday],
    "V2-stale-best": [probe_best_zero],
    "V7-error-cleared-by-render": [probe_error_then_delete],
    "V1-svg-html-namespace": [probe_svg, probe_svg_pixels],
    "H5-sprite-in-flow": [probe_layout],
    "H4-dialog-title-class": [probe_layout],
    "H8-delete-button-class": [probe_layout],
    "A7-backdrop-press-only": [probe_backdrop_drag_in],
}


def main():
    ids = sys.argv[2].split(",") if len(sys.argv) > 2 else None
    by_id = {m["id"]: m for m in MUTANTS}
    runs = [(None, PROBES[None])] if ids is None else []
    if ids:
        for name in ids:
            runs.append((name, PROBES[None] if name == "pristine" else PROBES[name]))
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=["--force-color-profile=srgb"])
        try:
            for name, probes in runs:
                files = {} if name in (None, "pristine") else patched_files(by_id[name])
                server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
                server.patched = files
                threading.Thread(target=server.serve_forever, daemon=True).start()
                env = Env(browser, f"http://127.0.0.1:{server.server_address[1]}/")
                label = name or "pristine"
                try:
                    for probe in probes:
                        try:
                            print(f"[{label}] {probe.__name__[6:]}: {probe(env)}", flush=True)
                        except Exception as exc:
                            print(f"[{label}] {probe.__name__[6:]}: ERROR {exc!r}"[:400], flush=True)
                finally:
                    server.shutdown()
                    server.server_close()
        finally:
            browser.close()


main()
