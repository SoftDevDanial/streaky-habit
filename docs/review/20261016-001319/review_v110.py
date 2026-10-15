"""Stakeholder review drive of Danial's Streaky Habit v1.1.0 (stakeholder reviewer, agent).

Cold boot with no seed and real localStorage, the real device clock (the look compare and the rollover pin the clock
and say so), real gestures (taps on a 390 x 844 touch phone, clicks and keys at 1280 x 800), headless.
A clipboard stand-in is loaded into every context before any page, so the system clipboard is never reached.
Starts its own static server on a free 127.0.0.1 port, stops it by PID at the end and checks the port refuses.

usage: python -B review_v110.py <project root> <out dir> <engine>
Writes <engine>-*.png, results-<engine>.json and run-log-<engine>.txt into <out dir>, and refuses to run when any
file of that engine is already there.
"""
import calendar
import json
import os
import shutil
import socket
import subprocess
import sys
import threading
import time
import traceback
import urllib.parse
from datetime import date, timedelta
from pathlib import Path

from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT, OUT, ENGINE = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
assert ENGINE in ("chromium", "webkit")
OUT.mkdir(parents=True, exist_ok=True)
assert not list(OUT.glob(f"{ENGINE}-*")) and not (OUT / f"results-{ENGINE}.json").exists(), "files of this engine exist"
DEADLINE_S = 540
TZ = "Asia/Kuala_Lumpur"
A, B, C = "Read 20 pages", "Stretch 10 minutes", "No phone after 11pm"
FSI, PDI = chr(0x2068), chr(0x2069)

results, log_lines, shots, contexts_net = [], [], [], []
CTX = {"engine": ENGINE, "size": None}
STARTED = time.strftime("%Y-%m-%d %H:%M:%S")


def say(text):
    log_lines.append(text)
    print(text, flush=True)


def check(group, name, ok, seen=None):
    row = {"engine": ENGINE, "size": CTX["size"], "group": group, "check": name, "result": "PASS" if ok else "FAIL", "seen": seen}
    results.append(row)
    say(f"{row['result']} {ENGINE} {CTX['size']} | {group} | {name} | {str(seen)[:220]}")
    return ok


def note(group, name, seen):
    row = {"engine": ENGINE, "size": CTX["size"], "group": group, "check": name, "result": "INFO", "seen": seen}
    results.append(row)
    say(f"INFO {ENGINE} {CTX['size']} | {group} | {name} | {str(seen)[:220]}")


def write_out():
    (OUT / f"results-{ENGINE}.json").write_text(json.dumps({"started": STARTED, "engine": ENGINE, "results": results, "shots": shots, "network": contexts_net}, indent=1, ensure_ascii=False), encoding="utf-8")
    (OUT / f"run-log-{ENGINE}.txt").write_text("\n".join(log_lines) + "\n", encoding="utf-8")


# ---------- the server, owned by this script ----------
def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def port_accepts(port):
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.5):
            return True
    except OSError:
        return False


PORT = free_port()
SERVER = subprocess.Popen([sys.executable, "-B", "-m", "http.server", str(PORT), "--bind", "127.0.0.1"], cwd=str(ROOT), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
say(f"server pid {SERVER.pid} port {PORT} cwd {ROOT}")
for _ in range(40):
    if port_accepts(PORT):
        break
    time.sleep(0.25)
else:
    SERVER.terminate()
    raise SystemExit("server gave up after 10 s")
BASE = f"http://127.0.0.1:{PORT}/"
ORIGIN = f"http://127.0.0.1:{PORT}"


def stop_server():
    if SERVER.poll() is None:
        SERVER.terminate()
        try:
            SERVER.wait(timeout=10)
        except subprocess.TimeoutExpired:
            SERVER.kill()
    refused = not port_accepts(PORT)
    say(f"server pid {SERVER.pid} stopped, exit {SERVER.returncode}, port {PORT} refuses {refused}")
    return refused


def on_deadline():
    say(f"DEADLINE {DEADLINE_S} s reached, stopping")
    stop_server()
    write_out()
    os._exit(3)


WATCHDOG = threading.Timer(DEADLINE_S, on_deadline)
WATCHDOG.daemon = True
WATCHDOG.start()

# ---------- dates ----------
TODAY = date.today()
WD = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MO = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


def short(d):
    return f"{WD[d.weekday()][:3]} {d.day} {MO[d.month - 1][:3]}"


def long_(d):
    return f"{WD[d.weekday()]} {d.day} {MO[d.month - 1]}"


def yeard(d):
    return f"{short(d)} {d.year}"


def year_start(d):
    try:
        return d.replace(year=d.year - 1)
    except ValueError:
        return d.replace(year=d.year - 1, day=28)


Y, D2 = TODAY - timedelta(1), TODAY - timedelta(2)
MON = TODAY - timedelta(TODAY.weekday())
OLDEST_MON = MON - timedelta(77)
LOWER = OLDEST_MON + timedelta(2)
YS = year_start(TODAY)
BAND_BUTTONS = (TODAY - OLDEST_MON).days + 1
YEAR = {"open": (TODAY - YS).days + 1, "closed": calendar.monthrange(TODAY.year, TODAY.month)[1] - TODAY.day, "blank": YS.day - 1}
RUN = [TODAY - timedelta(200 - i) for i in range(5)]
say(f"today {TODAY} yesterday {Y} lower P3 day {LOWER} year start {YS} band buttons {BAND_BUTTONS} year {YEAR} run {RUN[0]}..{RUN[-1]}")

# ---------- page scripts (read only) ----------
CLIPBOARD_STANDIN = """(() => {
  if (!navigator.clipboard || typeof Clipboard !== 'function') return;
  for (const method of ['writeText', 'write', 'readText', 'read']) {
    if (!(method in Clipboard.prototype)) continue;
    Object.defineProperty(Clipboard.prototype, method, {
      configurable: true, writable: true,
      value: function () { console.log('test:clipboard:' + method); return Promise.resolve(method === 'readText' ? '' : method === 'read' ? [] : undefined); },
    });
  }
})();"""
FAIL_GETTER = """(() => {
  const store = Object.getOwnPropertyDescriptor(window, 'localStorage');
  Object.defineProperty(window, 'localStorage', { configurable: true, enumerable: store.enumerable,
    get() { throw new DOMException('review denied', 'SecurityError'); } });
})();"""
FILL_JS = """() => {
  const write = (key, value) => { try { localStorage.setItem(key, value); return true; } catch { return false; } };
  let keys = 0, writes = 0;
  for (let size = 1 << 20; size >= 1 && writes < 1000; writes += 1) { if (write('review.fill.' + keys, 'x'.repeat(size))) keys += 1; else size = Math.floor(size / 2); }
  const last = 'review.fill.' + (keys - 1);
  for (let size = 64; size >= 1 && writes < 2000; writes += 1) { if (!write(last, localStorage.getItem(last) + 'x'.repeat(size))) size = Math.floor(size / 2); }
  return { keys, writes, full: keys > 0 && !write(last, localStorage.getItem(last) + 'x') };
}"""
CLEAR_FILL_JS = """() => { const k = Array.from({ length: localStorage.length }, (_, n) => localStorage.key(n)).filter((x) => x.startsWith('review.fill.')); k.forEach((x) => localStorage.removeItem(x)); return k.length; }"""
STATS_JS = """(el) => Array.from(el.querySelectorAll('.stat')).map((s) => Array.from(s.querySelectorAll('.lbl,.num,.unit,.none')).map((e) => e.textContent.trim()).join(' '))"""
TICK_STATS_JS = """(b) => { const s = document.getElementById(b.getAttribute('aria-describedby')); return s ? Array.from(s.children).map((e) => e.textContent.trim()).join(' | ') : null; }"""
DIALOGS_JS = """() => Array.from(document.querySelectorAll('dialog[open]')).map((d) => ['dlg-day','dlg-year','dlg-ov','dlg-all','dlg-del'].find((c) => d.classList.contains(c)) || d.className).sort()"""
ACTIVE_JS = """() => { const a = document.activeElement; if (!a) return null; return { tag: a.localName, label: a.getAttribute('aria-label') || (a.localName === 'button' ? a.textContent.trim().slice(0, 40) : null), key: a.dataset ? (a.dataset.key || null) : null, id: a.id || null }; }"""
YEAR_COUNT_JS = """(sel) => { const d = document.querySelector(sel); return { open: d.querySelectorAll('div.months button.hc, div.months button.yc').length, closed: d.querySelectorAll('div.months .closed').length, blank: d.querySelectorAll('div.months .blank').length }; }"""
SCROLL_JS = """() => ({ h: document.documentElement.scrollHeight, w: document.documentElement.scrollWidth, ih: innerHeight, iw: innerWidth })"""


def norm(text):
    return " ".join((text or "").split())


def new_ctx(browser, w, h, touch, clock=None, fixed=None, scheme="dark", init=None, dpr=1, app=True):
    ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=dpr, color_scheme=scheme, timezone_id=TZ, locale="en-GB", has_touch=touch)
    ctx.add_init_script(CLIPBOARD_STANDIN)
    for script in init or []:
        ctx.add_init_script(script)
    ctx.set_default_timeout(5000)
    ctx.set_default_navigation_timeout(10000)
    if clock:
        ctx.clock.install(time=clock)
    if fixed:
        ctx.clock.set_fixed_time(fixed)
    net = {"engine": ENGINE, "size": CTX["size"], "requests": [], "console_errors": [], "page_errors": [], "clipboard": [], "app": app}
    contexts_net.append(net)
    page = ctx.new_page()
    watch(page, net)
    ctx._review_net = net
    return ctx, page


def watch(page, net):
    page.on("request", lambda r: net["requests"].append(r.method + " " + r.url))
    page.on("pageerror", lambda e: net["page_errors"].append(str(e)[:200]))

    def on_console(m):
        if m.text.startswith("test:clipboard:"):
            net["clipboard"].append(m.text)
        elif m.type == "error":
            net["console_errors"].append(m.text[:200])
    page.on("console", on_console)


ALLOWED_JS = {"app.js", "calendar.js", "dates.js", "habits.js", "popups.js", "ring.js", "storage.js", "view.js"}


def close_ctx(ctx, group="no network, no errors"):
    net = ctx._review_net
    ctx.close()
    if not net["app"]:
        return
    bad = []
    for line in net["requests"]:
        method, url = line.split(" ", 1)
        path = url[len(ORIGIN):] if url.startswith(ORIGIN) else None
        ok = method == "GET" and path is not None and "?" not in path and (
            path in ("/", "/index.html", "/src/styles.css", "/src/icon.svg", "/favicon.ico") or (path.startswith("/src/") and path[5:] in ALLOWED_JS))
        if not ok:
            bad.append(line)
    check(group, "only same-origin GETs for the page's own files", not bad, {"requests": len(net["requests"]), "outside the rule": bad[:5]})
    check(group, "no console error, no page error, no clipboard use", not net["console_errors"] and not net["page_errors"] and not net["clipboard"],
          {"console": net["console_errors"][:3], "page": net["page_errors"][:3], "clipboard": net["clipboard"][:3]})


def shot(page, name):
    path = OUT / f"{ENGINE}-{CTX['size'].split()[0]}-{name}.png"
    page.wait_for_timeout(450)  # let pop, bump and transitions finish, so the capture shows the settled state
    page.screenshot(path=str(path))
    shots.append(path.name)
    return path


# ---------- gestures and reads ----------
def press(loc, touch):
    loc.tap() if touch else loc.click()


def press_at(page, x, y, touch):
    page.touchscreen.tap(x, y) if touch else page.mouse.click(x, y)


def settle(page, ms=650):
    """A person's pace between layers. The page guard (spec R14) holds page clicks for 500 ms after a click in a popup."""
    page.wait_for_timeout(ms)


def wait_open(page, cls):
    page.wait_for_selector(f"dialog.{cls}[open]", timeout=4000)
    page.wait_for_timeout(350)


def wait_closed(page, cls):
    page.wait_for_function(f"() => !document.querySelector('dialog.{cls}').open", timeout=4000)
    page.wait_for_timeout(150)


def dialogs(page):
    return page.evaluate(DIALOGS_JS)


def active(page):
    return page.evaluate(ACTIVE_JS)


def focused(loc):
    return loc.evaluate("(e) => e === document.activeElement")


def names(page):
    return [t.strip() for t in page.locator("ul.rows > li.row h3.r-name").all_text_contents()]


def row(page, n):
    return page.locator("ul.rows > li.row").filter(has=page.locator("h3.r-name").get_by_text(n, exact=True))


def stats(page, n):
    return row(page, n).locator("p.stats").evaluate(STATS_JS)


def done_btn(page, n):
    return row(page, n).locator(".btn-done")


def year_btn(page, n):
    return page.get_by_role("button", name=f"Year view, {n}", exact=True)


def bin_btn(page, n):
    return page.get_by_role("button", name=f'Delete "{n}"', exact=True)


def tick(page, n):
    return page.locator("dialog.dlg-day ul.day-list").get_by_role("button", name=n, exact=True)


def text(page, sel):
    return norm(page.locator(sel).text_content())


def add(page, name, touch, enter=False):
    press(page.locator("#nh"), touch)
    page.keyboard.type(name)
    if enter:
        page.keyboard.press("Enter")
    else:
        press(page.get_by_role("button", name="Add", exact=True), touch)
    page.wait_for_timeout(120)


def clear_field(page):
    for _ in range(len(page.locator("#nh").input_value())):
        page.keyboard.press("Backspace")


def msg(page):
    return norm(page.locator("#nh-msg").text_content())


def centre(box):
    return box["x"] + box["width"] / 2, box["y"] + box["height"] / 2


def inside(pt, box):
    return box is not None and box["x"] <= pt[0] <= box["x"] + box["width"] and box["y"] <= pt[1] <= box["y"] + box["height"]


def point_beside(box, avoid):
    left, top, right, bottom = box["x"], box["y"], box["x"] + box["width"], box["y"] + box["height"]
    al, at, ar, ab = avoid["x"], avoid["y"], avoid["x"] + avoid["width"], avoid["y"] + avoid["height"]
    parts = [(left, top, min(right, al), bottom), (max(left, ar), top, right, bottom), (left, top, right, min(bottom, at)), (left, max(top, ab), right, bottom)]
    parts = [p for p in parts if p[2] > p[0] + 2 and p[3] > p[1] + 2]
    x0, y0, x1, y1 = max(parts, key=lambda p: (p[2] - p[0]) * (p[3] - p[1]))
    return (x0 + x1) / 2, (y0 + y1) / 2


def hit(page, pt):
    return page.evaluate("([x, y]) => { const e = document.elementFromPoint(x, y); const b = e && e.closest('button'); return b ? b.getAttribute('aria-label') : null; }", [pt[0], pt[1]])


def m1_open(page):
    return page.evaluate("() => document.querySelector('dialog.dlg-del').open")


def close_m1(page):
    if m1_open(page):
        page.keyboard.press("Escape")
        wait_closed(page, "dlg-del")
    settle(page)


def room_check(page, day_loc, host, group, label):
    page.wait_for_timeout(300)
    b = day_loc.bounding_box()
    p1 = page.locator("dialog.dlg-day").bounding_box()
    hd = page.locator(f"dialog.{host} div.sheet-head").bounding_box()
    seen = {"day top": round(b["y"], 1), "day bottom": round(b["y"] + b["height"], 1), "head bottom": round(hd["y"] + hd["height"], 1), "P1 top": round(p1["y"], 1)}
    check(group, label, b["y"] + b["height"] <= p1["y"] + 1 and b["y"] >= hd["y"] + hd["height"] - 1, seen)


def guard_suite(page, touch, group, candidates):
    """The time-free delete guard (spec R13, ledger S3). A slow and a fast double press on a bin never delete."""
    first = bin_btn(page, candidates[0])
    press(first, touch)
    page.wait_for_selector("dialog.dlg-del[open]")
    page.wait_for_timeout(300)
    danger = page.locator("dialog.dlg-del button.btn-danger").bounding_box()
    page.keyboard.press("Escape")
    wait_closed(page, "dlg-del")
    settle(page)
    victim, over = candidates[0], False
    for n in candidates:
        box = bin_btn(page, n).bounding_box()
        if box and inside(centre(box), danger) and hit(page, centre(box)) == f'Delete "{n}"':
            victim, over = n, True
            break
    note(group, "a bin under M1's Delete habit at this size", {"victim": victim, "bin centre inside Delete habit": over, "Delete habit box": danger})
    before = names(page)
    x, y = centre(bin_btn(page, victim).bounding_box())
    if hit(page, (x, y)) != f'Delete "{victim}"':
        bin_btn(page, victim).scroll_into_view_if_needed()
        x, y = centre(bin_btn(page, victim).bounding_box())
    press_at(page, x, y, touch)
    page.wait_for_selector("dialog.dlg-del[open]")
    page.wait_for_timeout(800)
    press_at(page, x, y, touch)
    page.wait_for_timeout(500)
    check(group, f"slow double {'tap' if touch else 'click'} on a bin (800 ms apart) deletes nothing", names(page) == before,
          {"victim": victim, "second press on Delete habit": over, "M1 open after": m1_open(page)})
    close_m1(page)
    x, y = centre(bin_btn(page, victim).bounding_box())
    if touch:
        page.touchscreen.tap(x, y)
        page.touchscreen.tap(x, y)
    else:
        page.mouse.dblclick(x, y)
    page.wait_for_timeout(500)
    check(group, f"fast double {'tap' if touch else 'click'} on a bin deletes nothing", names(page) == before, {"victim": victim, "M1 open after": m1_open(page)})
    close_m1(page)


def quick_delete(page, touch, n, group):
    """Delete habit acts on the first deliberate press, with no half-second wait (ledger S3)."""
    opener = bin_btn(page, n)
    obox = opener.bounding_box()
    press(opener, touch)
    page.wait_for_selector("dialog.dlg-del[open]")
    t0 = time.monotonic()
    title = page.locator("#del-title").text_content()
    dbox = page.locator("dialog.dlg-del button.btn-danger").bounding_box()
    x, y = point_beside(dbox, obox)
    press_at(page, x, y, touch)
    dt = round((time.monotonic() - t0) * 1000)
    page.wait_for_timeout(300)
    check(group, "M1 asks the brainstorm's question", title == f'Delete "{FSI}{n}{PDI}"?', title)
    check(group, f"Delete habit acts on the first press, {dt} ms after the dialog opened", n not in names(page) and not m1_open(page), {"ms": dt, "rows": names(page)})


# ---------- walks ----------
def walk_phone(browser):
    CTX["size"] = "390x844 phone"
    touch = True
    ctx, page = new_ctx(browser, 390, 844, touch)
    page.goto(BASE)
    page.wait_for_selector("ul.rows")
    g = "first visit"
    check(g, "nothing stored on a cold boot", page.evaluate("localStorage.length") == 0, page.evaluate("localStorage.length"))
    empty = norm(page.locator("ul.rows").inner_text())
    check(g, "the empty list says how to start", "No habits yet." in empty and "Add one you want to do every day." in empty, empty)
    check("name", "the tab title is the full name", page.title() == "Danial's Streaky Habit", page.title())
    check("name", "the header shows Streaky Habit only", text(page, "h1.word") == "Streaky Habit", text(page, "h1.word"))
    check("logo", "the header mark is drawn in amber", page.locator("svg.mark").evaluate("(e) => getComputedStyle(e).color") == "rgb(255, 176, 32)", page.locator("svg.mark").evaluate("(e) => getComputedStyle(e).color"))
    ov = page.locator("button.ov-btn")
    check(g, "the Overview button shows on a phone, named with today's count", ov.is_visible() and ov.get_attribute("aria-label") == "Overview, today 0 of 0 habits done", ov.get_attribute("aria-label"))
    check(g, "the band is not shown on a phone", not page.locator("section.band").is_visible())
    check(g, "the header date is today", page.locator("time.date").get_attribute("datetime") == TODAY.isoformat() and text(page, "time.date") == long_(TODAY), text(page, "time.date"))
    shot(page, "01-first-visit")

    g = "add and name rules"
    press(page.get_by_role("button", name="Add", exact=True), touch)
    check(g, "an empty name says Name the habit first.", msg(page) == "Name the habit first.", msg(page))
    add(page, "  " + A + "  ", touch)
    check(g, "the name is trimmed, the habit shows Current and No streak yet, no Best", names(page) == [A] and stats(page, A) == ["Current No streak yet"], [names(page), stats(page, A)])
    add(page, B, touch, enter=True)
    add(page, C, touch)
    check(g, "new habits go to the bottom", names(page) == [A, B, C], names(page))
    add(page, "read 20 PAGES", touch)
    check(g, "a duplicate ignoring case says You already track this habit.", msg(page) == "You already track this habit." and page.locator("#nh").get_attribute("aria-invalid") == "true", msg(page))
    shot(page, "02-name-error")
    page.keyboard.press("Backspace")
    check(g, "typing clears the message", msg(page) == "" and page.locator("#nh-msg").is_hidden(), msg(page))
    clear_field(page)
    page.keyboard.type("x" * 41)
    press(page.get_by_role("button", name="Add", exact=True), touch)
    check(g, "41 characters says Keep it to 40 characters or fewer.", msg(page) == "Keep it to 40 characters or fewer.", msg(page))
    clear_field(page)

    g = "done today and labels"
    press(done_btn(page, A), touch)
    check(g, "Done today is pressed", done_btn(page, A).get_attribute("aria-pressed") == "true")
    check(g, "the row reads Current 1 day and Best 1", stats(page, A) == ["Current 1 day", "Best 1"], stats(page, A))
    check(g, "the Overview button counts today", ov.get_attribute("aria-label") == "Overview, today 1 of 3 habits done", ov.get_attribute("aria-label"))

    g = "past day, overview popup and day editor"
    press(ov, touch)
    wait_open(page, "dlg-ov")
    check(g, "P3 opens with Close focused", focused(page.locator("dialog.dlg-ov").get_by_role("button", name="Close")), active(page))
    p3y = page.locator(f'dialog.dlg-ov button.hc[data-key="{Y}"]')
    check(g, "P3 names yesterday with its count", p3y.get_attribute("aria-label") == f"{short(Y)}, 0 of 3 habits", p3y.get_attribute("aria-label"))
    shot(page, "03-overview-popup")
    press(p3y, touch)
    wait_open(page, "dlg-day")
    check(g, "P1 title is the long date of the day", text(page, "#day-title") == long_(Y), text(page, "#day-title"))
    check(g, "P1 subtitle reads 0 of 3 habits", text(page, "#day-sub") == "0 of 3 habits", text(page, "#day-sub"))
    check(g, "the chosen day is marked open in P3", "is-open" in (p3y.get_attribute("class") or ""))
    t = tick(page, A)
    press(t, touch)
    check(g, "the tick is pressed and the subtitle reads 1 of 3 habits", t.get_attribute("aria-pressed") == "true" and text(page, "#day-sub") == "1 of 3 habits", text(page, "#day-sub"))
    check(g, "the tick reads Current 2 days and Best 2", t.evaluate(TICK_STATS_JS) == "Current 2 days | Best 2", t.evaluate(TICK_STATS_JS))
    check(g, "the row behind updates at once", stats(page, A) == ["Current 2 days", "Best 2"], stats(page, A))
    check(g, "P3's day name updates", p3y.get_attribute("aria-label") == f"{short(Y)}, 1 of 3 habits", p3y.get_attribute("aria-label"))
    shot(page, "04-day-editor-over-p3")
    page.keyboard.press("Escape")
    wait_closed(page, "dlg-day")
    check(g, "Esc closes P1 only and focus returns to the day", dialogs(page) == ["dlg-ov"] and focused(p3y), [dialogs(page), active(page)])
    settle(page)
    low = page.locator(f'dialog.dlg-ov button.hc[data-key="{LOWER}"]')
    press(low, touch)
    wait_open(page, "dlg-day")
    room_check(page, low, "dlg-ov", "rule 4, room under P1 (H-03)", f"a day in P3's oldest week ({LOWER}) stays in sight above P1")
    shot(page, "05-day-editor-oldest-week")
    press(tick(page, C), touch)
    check(g, "a tick far back reads No streak yet and Best 1", tick(page, C).evaluate(TICK_STATS_JS) == "No streak yet | Best 1", tick(page, C).evaluate(TICK_STATS_JS))
    page.keyboard.press("Escape")
    wait_closed(page, "dlg-day")
    settle(page)

    g = "past day, year of all habits"
    press(page.locator("dialog.dlg-ov button.btn-all"), touch)
    wait_open(page, "dlg-all")
    counts = page.evaluate(YEAR_COUNT_JS, "dialog.dlg-all")
    check(g, "P4 holds the last 12 months, future days closed", counts == YEAR, counts)
    check(g, "P4 opens with Close focused and its titles", focused(page.locator("dialog.dlg-all").get_by_role("button", name="Close")) and text(page, "#all-title") == "All habits" and text(page, "#all-sub") == "The last 12 months", active(page))
    oldest = page.locator(f'dialog.dlg-all button.hc[data-key="{YS}"]')
    check(g, "the oldest open day is the same date last year, named with its year", oldest.get_attribute("aria-label") == f"{yeard(YS)}, 0 of 3 habits", oldest.get_attribute("aria-label"))
    check(g, "no control for the day before the reach or for tomorrow", page.locator(f'dialog.dlg-all button.hc[data-key="{YS - timedelta(1)}"]').count() == 0 and page.locator(f'dialog.dlg-all button.hc[data-key="{TODAY + timedelta(1)}"]').count() == 0)
    shot(page, "06-year-all-habits")
    press(oldest, touch)
    wait_open(page, "dlg-day")
    room_check(page, oldest, "dlg-all", "rule 4, room under P1 (H-03)", f"P4's oldest day ({YS}) stays in sight above P1")
    check(g, "P1 opens on the oldest day", text(page, "#day-title") == long_(YS), text(page, "#day-title"))
    press(tick(page, B), touch)
    check(g, "the oldest day can be ticked, Best 1", tick(page, B).evaluate(TICK_STATS_JS) == "No streak yet | Best 1", tick(page, B).evaluate(TICK_STATS_JS))
    shot(page, "07-day-editor-over-p4")
    page.keyboard.press("Escape")
    wait_closed(page, "dlg-day")
    s1 = dialogs(page)
    page.keyboard.press("Escape")
    wait_closed(page, "dlg-all")
    s2, f2 = dialogs(page), focused(page.locator("dialog.dlg-ov button.btn-all"))
    page.keyboard.press("Escape")
    wait_closed(page, "dlg-ov")
    s3, f3 = dialogs(page), focused(ov)
    check(g, "Esc closes P1, then P4, then P3, focus back on each opener", s1 == ["dlg-all", "dlg-ov"] and s2 == ["dlg-ov"] and f2 and s3 == [] and f3, [s1, s2, f2, s3, f3])
    settle(page)
    check(g, "the rows show every past edit", [stats(page, n) for n in (A, B, C)] == [["Current 2 days", "Best 2"], ["Current No streak yet", "Best 1"], ["Current No streak yet", "Best 1"]], [stats(page, n) for n in (A, B, C)])

    g = "past day, the habit's year view"
    press(year_btn(page, A), touch)
    wait_open(page, "dlg-year")
    yr = page.locator("dialog.dlg-year p.yr-stats")
    check(g, "P2 shows the habit, The last 12 months and the row's Current and Best", text(page, "#yr-title") == A and text(page, "#yr-sub") == "The last 12 months" and yr.evaluate(STATS_JS) == stats(page, A), [text(page, "#yr-title"), yr.evaluate(STATS_JS)])
    check(g, "P2 opens with Close focused", focused(page.locator("dialog.dlg-year").get_by_role("button", name="Close")), active(page))
    counts = page.evaluate(YEAR_COUNT_JS, "dialog.dlg-year")
    check(g, "P2 holds the last 12 months", counts == YEAR, counts)
    bead = lambda d: page.locator(f'dialog.dlg-year button.yc[data-key="{d}"]')
    check(g, "today's and yesterday's beads are done", bead(TODAY).get_attribute("aria-pressed") == "true" and bead(Y).get_attribute("aria-pressed") == "true")
    check(g, "a bead is named Mark <date> as done", bead(D2).get_attribute("aria-label") == f"Mark {yeard(D2)} as done", bead(D2).get_attribute("aria-label"))
    shot(page, "08-year-view-open")
    press(bead(D2), touch)
    check(g, "a bead tick reads Current 3 days and Best 3", yr.evaluate(STATS_JS) == ["Current 3 days", "Best 3"], yr.evaluate(STATS_JS))
    for d in RUN:
        press(bead(d), touch)
    check(g, "five beads 200 days back make Best 5", yr.evaluate(STATS_JS) == ["Current 3 days", "Best 5"], yr.evaluate(STATS_JS))
    mid, first, last = (bead(RUN[i]).get_attribute("class") or "" for i in (2, 0, 4))
    check(g, "the run is drawn on one thread", {"l", "r"} <= set(mid.split()) and "r" in first.split() and "l" not in first.split() and "l" in last.split() and "r" not in last.split(), [first, mid, last])
    shot(page, "09-year-view-run")
    page.keyboard.press("Escape")
    wait_closed(page, "dlg-year")
    check(g, "Esc closes P2 and focus returns to the row's Year", focused(year_btn(page, A)), active(page))
    settle(page)
    check(g, "the row shows the year view's numbers", stats(page, A) == ["Current 3 days", "Best 5"], stats(page, A))

    g = "streak rule"
    press(done_btn(page, A), touch)
    check(g, "unticking today keeps the run counted from yesterday", stats(page, A) == ["Current 2 days", "Best 5"], stats(page, A))
    press(done_btn(page, A), touch)
    check(g, "Done today again", stats(page, A) == ["Current 3 days", "Best 5"], stats(page, A))
    shot(page, "10-three-habits")

    g = "delete"
    guard_suite(page, touch, g, [B, C, A])
    quick_delete(page, touch, C, g)
    check(g, "focus goes to the bin of the row above", focused(bin_btn(page, B)), active(page))
    settle(page)
    press(year_btn(page, B), touch)
    wait_open(page, "dlg-year")
    settle(page, 300)
    delb = page.locator("dialog.dlg-year button.btn-del")
    q = centre(delb.bounding_box())
    qbox = delb.bounding_box()
    press_at(page, *q, touch)
    page.wait_for_selector("dialog.dlg-del[open]")
    page.wait_for_timeout(300)
    over = inside(q, page.locator("dialog.dlg-del button.btn-danger").bounding_box())
    shot(page, "11-delete-over-year-view")
    page.wait_for_timeout(500)
    press_at(page, *q, touch)
    page.wait_for_timeout(500)
    check(g, "a slow second tap where P2's Delete habit was deletes nothing", B in names(page), {"second tap inside M1's Delete habit": over, "M1 open after": m1_open(page)})
    if not m1_open(page):
        settle(page)
        press(delb, touch)
        page.wait_for_selector("dialog.dlg-del[open]")
    x, y = point_beside(page.locator("dialog.dlg-del button.btn-danger").bounding_box(), qbox)
    press_at(page, x, y, touch)
    page.wait_for_timeout(500)
    check(g, "Delete habit from P2 deletes and closes both popups", B not in names(page) and dialogs(page) == [], [names(page), dialogs(page)])
    check(g, "focus goes to the Year of the row above", focused(year_btn(page, A)), active(page))
    settle(page)

    g = "kept on the device"
    page.reload()
    page.wait_for_selector("ul.rows")
    check(g, "a reload shows the same habit and numbers", names(page) == [A] and stats(page, A) == ["Current 3 days", "Best 5"] and done_btn(page, A).get_attribute("aria-pressed") == "true", [names(page), stats(page, A)])
    other = ctx.new_page()
    watch(other, ctx._review_net)
    page.close()
    other.goto(BASE)
    other.wait_for_selector("ul.rows")
    page = other
    check(g, "a closed tab opened again shows the same", names(page) == [A] and stats(page, A) == ["Current 3 days", "Best 5"], [names(page), stats(page, A)])
    add(page, B, touch)
    check(g, "a habit deleted and added again starts with no history", stats(page, B) == ["Current No streak yet"], stats(page, B))
    g = "tap-through guard (spec R14, owner's CG-11)"
    settle(page)
    press(year_btn(page, B), touch)
    wait_open(page, "dlg-year")
    press(page.locator("dialog.dlg-year").get_by_role("button", name="Close"), touch)
    wait_closed(page, "dlg-year")
    t0 = time.monotonic()
    press(done_btn(page, B), touch)
    quick_ms = round((time.monotonic() - t0) * 1000)
    quick = done_btn(page, B).get_attribute("aria-pressed")
    settle(page)
    press(done_btn(page, B), touch)
    later = done_btn(page, B).get_attribute("aria-pressed")
    note(g, "Done today tapped right after closing a popup with a tap, then again 650 ms later", {"first tap counted": quick == "true", "ms after the close": quick_ms, "second tap state": later})
    if later == "true":
        press(done_btn(page, B), touch)

    g = "twelve habits"
    for _ in range(15):
        n = len(names(page))
        if n >= 12:
            break
        add(page, f"Habit {n + 1}", touch, enter=True)
    sc = page.evaluate(SCROLL_JS)
    check(g, "at 12 the field and Add are disabled with the note", page.locator("#nh").is_disabled() and page.get_by_role("button", name="Add", exact=True).is_disabled() and msg(page) == "You track 12 habits, the most this app holds. Delete one to add another.", msg(page))
    check(g, "the page does not scroll, the list frame does", sc["h"] <= sc["ih"] and sc["w"] <= sc["iw"], sc)
    shot(page, "12-twelve")
    guard_suite(page, touch, "delete guard at twelve", names(page)[::-1])
    close_ctx(ctx)


def walk_desktop(browser):
    CTX["size"] = "1280x800 desktop"
    touch = False
    ctx, page = new_ctx(browser, 1280, 800, touch)
    page.goto(BASE)
    page.wait_for_selector("ul.rows")
    g = "first visit"
    check(g, "nothing stored on a cold boot", page.evaluate("localStorage.length") == 0)
    band = page.locator("section.band")
    check(g, "the band shows, the Overview button does not", band.is_visible() and not page.locator("button.ov-btn").is_visible())
    count = page.locator("section.band div.ovg-cols button.hc").count()
    tb = page.locator(f'section.band button.hc[data-key="{TODAY}"]')
    check(g, "the band holds the last 12 weeks up to today", text(page, "#h-ov") == "Last 12 weeks" and count == BAND_BUTTONS and tb.get_attribute("aria-current") == "date" and tb.get_attribute("aria-label") == f"{short(TODAY)}, 0 of 0 habits", [count, tb.get_attribute("aria-label")])
    shot(page, "01-first-visit")
    add(page, A, touch)
    add(page, B, touch, enter=True)
    add(page, C, touch)
    check("add", "three habits in order", names(page) == [A, B, C], names(page))
    press(done_btn(page, A), touch)
    press(done_btn(page, B), touch)
    check("done today and labels", "the band's today counts 2 of 3", tb.get_attribute("aria-label") == f"{short(TODAY)}, 2 of 3 habits", tb.get_attribute("aria-label"))
    check("done today and labels", "rows read Current 1 day and Best 1, and No streak yet", [stats(page, n) for n in (A, B, C)] == [["Current 1 day", "Best 1"], ["Current 1 day", "Best 1"], ["Current No streak yet"]], [stats(page, n) for n in (A, B, C)])
    shot(page, "02-three-habits")

    g = "past day, band and day editor"
    by = page.locator(f'section.band button.hc[data-key="{Y}"]')
    press(by, touch)
    wait_open(page, "dlg-day")
    p1 = page.locator("dialog.dlg-day").bounding_box()
    check(g, "P1 opens centred over the list with the first tick focused", abs(p1["x"] + p1["width"] / 2 - 640) <= 2 and focused(tick(page, A)), [p1, active(page)])
    check(g, "P1 title and subtitle", text(page, "#day-title") == long_(Y) and text(page, "#day-sub") == "0 of 3 habits", [text(page, "#day-title"), text(page, "#day-sub")])
    press(tick(page, C), touch)
    check(g, "a tick updates P1, the band and the row at once", text(page, "#day-sub") == "1 of 3 habits" and by.get_attribute("aria-label") == f"{short(Y)}, 1 of 3 habits" and stats(page, C) == ["Current 1 day", "Best 1"], [text(page, "#day-sub"), by.get_attribute("aria-label"), stats(page, C)])
    shot(page, "03-day-editor")
    page.mouse.click(20, 400)
    wait_closed(page, "dlg-day")
    check(g, "a backdrop click closes P1 and focus returns to the band day", dialogs(page) == [] and focused(by), active(page))
    settle(page)

    g = "past day, year of all habits"
    press(page.locator("section.band button.btn-all"), touch)
    wait_open(page, "dlg-all")
    counts = page.evaluate(YEAR_COUNT_JS, "dialog.dlg-all")
    check(g, "P4 holds the last 12 months", counts == YEAR, counts)
    shot(page, "04-year-all-habits")
    oldest = page.locator(f'dialog.dlg-all button.hc[data-key="{YS}"]')
    press(oldest, touch)
    wait_open(page, "dlg-day")
    check(g, "P1 opens over P4 on the oldest day", text(page, "#day-title") == long_(YS) and dialogs(page) == ["dlg-all", "dlg-day"], [text(page, "#day-title"), dialogs(page)])
    press(tick(page, A), touch)
    check(g, "the oldest day ticks, A keeps Current 1 day and Best 1", tick(page, A).evaluate(TICK_STATS_JS) == "Current 1 day | Best 1", tick(page, A).evaluate(TICK_STATS_JS))
    page.keyboard.press("Escape")
    wait_closed(page, "dlg-day")
    f1 = focused(oldest)
    page.keyboard.press("Escape")
    wait_closed(page, "dlg-all")
    check(g, "Esc closes P1 then P4, focus back on the day then the band's Year", f1 and focused(page.locator("section.band button.btn-all")), active(page))
    settle(page)

    g = "past day, the habit's year view"
    press(year_btn(page, B), touch)
    wait_open(page, "dlg-year")
    xs = page.locator("dialog.dlg-year section.month").evaluate_all("(m) => m.slice(0, 3).map((e) => [Math.round(e.getBoundingClientRect().x), Math.round(e.getBoundingClientRect().y)])")
    check(g, "P2 shows three months across", len({x for x, _ in xs}) == 3 and len({y for _, y in xs}) == 1, xs)
    yr = page.locator("dialog.dlg-year p.yr-stats")
    press(page.locator(f'dialog.dlg-year button.yc[data-key="{Y}"]'), touch)
    check(g, "a bead tick reads Current 2 days and Best 2", yr.evaluate(STATS_JS) == ["Current 2 days", "Best 2"], yr.evaluate(STATS_JS))
    shot(page, "05-year-view")
    press(page.locator("dialog.dlg-year").get_by_role("button", name="Close"), touch)
    wait_closed(page, "dlg-year")
    check(g, "Close returns focus to the row's Year and the row matches", focused(year_btn(page, B)) and stats(page, B) == ["Current 2 days", "Best 2"], [active(page), stats(page, B)])
    settle(page)

    g = "delete"
    guard_suite(page, touch, g, [C, B, A])
    page.reload()
    page.wait_for_selector("ul.rows")
    page.keyboard.press("Tab")
    first = page.locator("section.band button.btn-all")
    check("keyboard", "the first Tab lands on the band's Year with a visible ring", focused(first) and first.evaluate("(e) => getComputedStyle(e).outlineStyle") == "solid", [active(page), first.evaluate("(e) => getComputedStyle(e).outlineStyle")])
    target = bin_btn(page, C)
    for _ in range(150):
        if focused(target):
            break
        page.keyboard.press("Tab")
    check("keyboard", "Tab reaches a bin", focused(target), active(page))
    page.keyboard.press("Enter")
    page.wait_for_selector("dialog.dlg-del[open]")
    page.wait_for_timeout(200)
    c1 = focused(page.locator("dialog.dlg-del button.btn-secondary"))
    page.keyboard.press("Tab")
    page.keyboard.press("Enter")
    page.wait_for_timeout(400)
    check("keyboard", "Enter on a bin, Cancel focused, Tab, Enter deletes", c1 and C not in names(page) and focused(bin_btn(page, B)), [c1, names(page), active(page)])
    quick_delete(page, touch, B, g)
    check(g, "focus goes to the bin of the row above", focused(bin_btn(page, A)), active(page))
    page.reload()
    page.wait_for_selector("ul.rows")
    check("kept on the device", "a reload shows what is left", names(page) == [A] and stats(page, A) == ["Current 1 day", "Best 1"], [names(page), stats(page, A)])

    g = "twelve habits"
    for _ in range(15):
        n = len(names(page))
        if n >= 12:
            break
        add(page, f"Habit {n + 1}", touch, enter=True)
    sc = page.evaluate(SCROLL_JS)
    check(g, "at 12 the field and Add are disabled with the note, the page does not scroll", page.locator("#nh").is_disabled() and msg(page).startswith("You track 12 habits") and sc["h"] <= sc["ih"], [msg(page), sc])
    shot(page, "06-twelve")
    guard_suite(page, touch, "delete guard at twelve", names(page)[::-1])
    close_ctx(ctx)


def walk_storage(browser):
    CTX["size"] = "390x844 storage"
    touch = True
    ctx, page = new_ctx(browser, 390, 844, touch)
    page.goto(BASE)
    page.wait_for_selector("ul.rows")
    g = "save warning"
    warn = page.locator("div.banners > div.banner.warn")
    add(page, A, touch)
    check(g, "no warning while saving works", warn.count() == 0)
    fill = page.evaluate(FILL_JS)
    check(g, "this context's storage is filled to its quota (test context only)", fill["full"], fill)
    press(done_btn(page, A), touch)
    copy = "Your habits are not being saved on this device. Changes will be lost when you close this tab."
    first = page.locator("div.banners > *").first
    check(g, "a failed save shows the warning with the brainstorm's words", warn.count() == 1 and text(page, "div.banner.warn p") == copy and first.evaluate("(e) => e.classList.contains('warn')") and warn.get_attribute("role") == "status", text(page, "div.banners"))
    check(g, "the warning cannot be dismissed", warn.locator("button").count() == 0)
    check(g, "the change stays on screen", done_btn(page, A).get_attribute("aria-pressed") == "true")
    shot(page, "01-save-warning")
    add(page, B, touch)
    check(g, "the app keeps working while saves fail", names(page) == [A, B] and warn.count() == 1, names(page))
    cleared = page.evaluate(CLEAR_FILL_JS)
    press(done_btn(page, B), touch)
    check(g, "the warning goes after the next save works", warn.count() == 0, {"fill keys removed": cleared})
    page.reload()
    page.wait_for_selector("ul.rows")
    check(g, "after a reload the last working save is what shows", names(page) == [A, B] and done_btn(page, A).get_attribute("aria-pressed") == "true" and done_btn(page, B).get_attribute("aria-pressed") == "true", names(page))
    close_ctx(ctx)

    ctx, page = new_ctx(browser, 390, 844, touch, init=[FAIL_GETTER])
    page.goto(BASE)
    page.wait_for_selector("ul.rows")
    check(g, "storage refused at boot shows the warning from the first render, no note", page.locator("div.banners > div.banner.warn").count() == 1 and page.locator("div.banner.note").count() == 0 and "No habits yet." in page.locator("ul.rows").inner_text(), text(page, "div.banners"))
    add(page, A, touch)
    check(g, "habits can still be added, the warning stays", names(page) == [A] and page.locator("div.banner.warn").count() == 1, names(page))
    shot(page, "02-save-warning-at-boot")
    close_ctx(ctx)

    g = "unreadable data"
    ctx, page = new_ctx(browser, 390, 844, touch)
    page.goto(BASE)
    page.wait_for_selector("ul.rows")
    page.evaluate("() => localStorage.setItem('streaks.state', '{broken')")
    page.reload()
    page.wait_for_selector("ul.rows")
    nt = page.locator("div.banners > div.banner.note")
    check(g, "unreadable data starts empty with the note", nt.count() == 1 and text(page, "div.banner.note p") == "Your saved habits could not be read, so the list was reset.", text(page, "div.banners"))
    shot(page, "03-unreadable-note")
    press(nt.get_by_role("button", name="Dismiss note"), touch)
    page.wait_for_timeout(200)
    check(g, "Dismiss removes the note and focus goes to the field", nt.count() == 0 and focused(page.locator("#nh")), active(page))
    close_ctx(ctx)


def walk_rollover(browser):
    CTX["size"] = "1280x800 rollover"
    start = f"{TODAY.isoformat()}T23:59:30+08:00"
    ctx, page = new_ctx(browser, 1280, 800, False, clock=start)
    page.goto(BASE)
    page.wait_for_selector("ul.rows")
    add(page, A, False)
    press(done_btn(page, A), False)
    press(page.locator("section.band button.btn-all"), False)
    wait_open(page, "dlg-all")
    page.clock.run_for(70_000)
    page.wait_for_timeout(200)
    tm = TODAY + timedelta(1)
    g = "midnight (clock pinned at 23:59:30, then 70 s)"
    check(g, "the header moves to the new day", page.locator("time.date").get_attribute("datetime") == tm.isoformat() and text(page, "time.date") == long_(tm), text(page, "time.date"))
    t4 = page.locator(f'dialog.dlg-all button.hc[data-key="{tm}"]')
    check(g, "open P4 now ends at the new today", t4.count() == 1 and t4.get_attribute("aria-current") == "date" and dialogs(page) == ["dlg-all"], dialogs(page))
    check(g, "Done today means the new day, the run still counts", done_btn(page, A).get_attribute("aria-pressed") == "false" and stats(page, A) == ["Current 1 day", "Best 1"], stats(page, A))
    close_ctx(ctx)


def diff_count(a, b):
    ia, ib = Image.open(a).convert("RGB"), Image.open(b).convert("RGB")
    if ia.size != ib.size:
        return None
    d = ImageChops.difference(ia, ib)
    return sum(1 for px in d.get_flattened_data() if px != (0, 0, 0))


def look_compare(browser):
    fixed = "2026-10-10T09:00:00+08:00"
    for w, h in ((390, 844), (1280, 800)):
        CTX["size"] = f"{w}x{h} look"
        ctx, page = new_ctx(browser, w, h, False, fixed=fixed, app=False)
        page.goto(BASE + "docs/design/today-empty.html")
        page.wait_for_timeout(400)
        golden = shot(page, "golden-today-empty")
        page.goto(BASE + "docs/design/today.html")
        page.wait_for_timeout(400)
        shot(page, "golden-today")
        ctx.close()
        ctx, page = new_ctx(browser, w, h, False, fixed=fixed)
        page.goto(BASE)
        page.wait_for_selector("ul.rows")
        page.wait_for_timeout(400)
        mine = shot(page, "app-first-visit-pinned")
        n = diff_count(golden, mine)
        check("look against the goldens (clock pinned to 10 Oct 2026 09:00)", f"first visit equals today-empty.html in {ENGINE}", n == 0, {"pixels that differ": n})
        close_ctx(ctx)


def logo_checks(browser):
    CTX["size"] = "1280x800 logo"
    ctx, page = new_ctx(browser, 1280, 800, False, app=False)
    page.goto(BASE + "docs/design/today.html")
    gd = page.locator("svg.mark path").get_attribute("d")
    href = page.locator("link[rel=icon]").get_attribute("href")
    page.goto(BASE)
    page.wait_for_selector("ul.rows")
    ad = page.locator("svg.mark path").get_attribute("d")
    check("logo", "the header mark is the golden's mark", gd == ad and bool(gd))
    payload = urllib.parse.unquote(href.split(",", 1)[1]).encode("utf-8")
    check("logo", "src/icon.svg is the golden's tab icon byte for byte", (ROOT / "src" / "icon.svg").read_bytes() == payload, {"file": len((ROOT / 'src' / 'icon.svg').read_bytes()), "golden": len(payload)})
    check("logo", "the tab icon link points at src/icon.svg", page.locator("link[rel=icon]").get_attribute("href") == "src/icon.svg")
    loaded = page.evaluate("""() => new Promise((ok) => { const i = new Image(); i.onload = () => ok('load'); i.onerror = () => ok('error'); i.src = document.querySelector('link[rel=icon]').href; })""")
    check("logo", "the tab icon loads under the page's CSP", loaded == "load", loaded)
    page.locator("div.brand").screenshot(path=str(OUT / f"{ENGINE}-1280-logo-header.png"))
    shots.append(f"{ENGINE}-1280-logo-header.png")
    ctx.close()
    for scheme in ("dark", "light"):
        ctx, page = new_ctx(browser, 16, 16, False, scheme=scheme, dpr=8, app=False)
        page.goto(BASE + "src/icon.svg")
        page.wait_for_timeout(200)
        name = f"{ENGINE}-16-tab-icon-{scheme}.png"
        page.screenshot(path=str(OUT / name))
        shots.append(name)
        ctx.close()


def main():
    try:
        with sync_playwright() as p:
            browser = getattr(p, ENGINE).launch(headless=True, args=["--force-color-profile=srgb"] if ENGINE == "chromium" else [])
            say(f"{ENGINE} {browser.version}, headless")
            for walk in (walk_phone, walk_desktop, walk_storage, walk_rollover, look_compare, logo_checks):
                t0 = time.monotonic()
                try:
                    walk(browser)
                except Exception as error:
                    check(walk.__name__, "the walk ran to its end", False, traceback.format_exc()[-900:])
                    for ctx in browser.contexts:
                        try:
                            pg = ctx.pages[-1] if ctx.pages else None
                            if pg:
                                pg.screenshot(path=str(OUT / f"{ENGINE}-error-{walk.__name__}.png"))
                                shots.append(f"{ENGINE}-error-{walk.__name__}.png")
                            ctx.close()
                        except Exception:
                            pass
                say(f"{walk.__name__} took {time.monotonic() - t0:.1f} s")
            browser.close()
    finally:
        refused = stop_server()
        results.append({"engine": ENGINE, "size": None, "group": "process", "check": "own server stopped by PID and its port refuses", "result": "PASS" if refused else "FAIL", "seen": {"pid": SERVER.pid, "port": PORT, "exit": SERVER.returncode}})
        WATCHDOG.cancel()
        script = OUT / "review_v110.py"
        if not script.exists():
            shutil.copyfile(__file__, script)
        write_out()
        passed = sum(r["result"] == "PASS" for r in results)
        failed = [r for r in results if r["result"] == "FAIL"]
        say(f"TOTAL {ENGINE} pass {passed} fail {len(failed)} info {sum(r['result'] == 'INFO' for r in results)}")
        write_out()


main()
