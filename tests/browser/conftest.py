"""Shared fixtures and helpers for the Streaks browser tests (app qa.md, "conftest.py").

Why: every test opens the running app the same way (one headless Chromium, a fixed time zone, a
controlled clock, optional seeded storage), so that setup lives here once.
Input: STREAKS_BASE_URL (ends with "/"), STREAKS_SUBPATH_URL and STREAKS_EVIDENCE_DIR, all optional. When
STREAKS_BASE_URL is absent this module serves the app itself for the run (see `pytest_configure`), so
`python -m pytest tests/browser -q` works with nothing set. Output: fixtures and helpers; nothing here
touches the app's code, and tests only ever reach the app through real gestures and by seeding
localStorage before it loads.
"""
import datetime
import json
import os
import pathlib
import socket
import subprocess
import sys
import time
import urllib.request
import weakref
from urllib.parse import urlsplit

import pytest
from playwright.sync_api import expect, sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[2]
DESIGN_DIR = ROOT / "docs" / "design"

# Rebound by `pytest_configure` when the run serves the app itself. Test modules read them with
# `from conftest import ...` at import, which pytest does only after that hook has run.
BASE_URL = os.environ.get("STREAKS_BASE_URL", "")
SUBPATH_URL = os.environ.get("STREAKS_SUBPATH_URL", "")
EVIDENCE_DIR = os.environ.get("STREAKS_EVIDENCE_DIR", "")

SERVER_READY_SECONDS = 10  # qa.md: poll every 250 ms and give up after 10 seconds
SERVER_POLL_SECONDS = 0.25
SERVER_STOP_SECONDS = 10

STORAGE_KEY = "streaks.state"
# UTC+8 all year, no DST, so a result never depends on the machine's own zone (ROADMAP D5).
TZ = "Asia/Kuala_Lumpur"
NOON = "2026-10-08T12:00:00+08:00"
# A test that freezes an installed clock pauses here, 20 seconds after NOON: later than a page needs to
# load, earlier than the app's first 30 second rollover check.
PAUSE_AT = "2026-10-08T12:00:20+08:00"
# The second click of a double click or double tap is ignored for this long (spec R13, T7): on "Delete habit"
# after the click that opened the dialog, and on the page after a mouse or touch click in the dialog.
# The spec's number, written out and not read from src/ on purpose: the two edge tests of test_delete.py press at
# this value minus 1 ms (ignored) and at this value (acts), so they fail for any other DIALOG_GUARD_MS in src/app.js.
GUARD_WINDOW_MS = 500
DEFAULT_TIMEOUT_MS = 5000

SAMPLE = json.loads((DESIGN_DIR / "sample-history.json").read_text(encoding="utf-8"))
SAMPLE_HABITS = SAMPLE["habits"]
SAMPLE_LEVELS = SAMPLE["heatmapLevels"]
# Written out, not read from the sample, so a test that compares the page with them is not comparing a file with itself.
SAMPLE_NAMES = ["Read 20 pages", "Stretch 10 minutes", "No phone after 11pm"]


def state_text(habits):
    """The text the app stores for a list of habits, in the same compact form."""
    return json.dumps({"version": 1, "habits": habits}, separators=(",", ":"))


def sample_state():
    return state_text(SAMPLE_HABITS)


def pretty_sample_state():
    """The sample as indented JSON. The app writes compact JSON, so any save changes this text.

    Seed with it wherever a test says "saves nothing": with `sample_state()` a re-save of the unchanged
    habits would produce the very same text and the check could not fail.
    """
    return json.dumps({"version": 1, "habits": SAMPLE_HABITS}, indent=2)


def plain_state(count):
    """N plain habits named "Habit 1" to "Habit N" with no done days."""
    return state_text([{"name": f"Habit {number}", "done": []} for number in range(1, count + 1)])


def _free_port():
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def _port_accepts(port):
    try:
        socket.create_connection(("127.0.0.1", port), timeout=0.5).close()
    except OSError:
        return False
    return True


class _StaticServer:
    """`python -m http.server <free port> --bind 127.0.0.1 --directory <directory>`, owned by this run.

    `stop` is safe to call at any point (never started, already stopped) and does not return until the
    port refuses connections, so a leaked server fails the run instead of going unnoticed.
    """

    def __init__(self, directory):
        self.directory = directory
        self.process = None
        self.port = None

    def start(self):
        for _ in range(3):  # a free port can be taken between the probe and the bind
            self.port = _free_port()
            self.process = subprocess.Popen(
                [sys.executable, "-m", "http.server", str(self.port), "--bind", "127.0.0.1", "--directory", str(self.directory)],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            if self._wait_until_ready():
                return
            self._kill()
            self.process = None  # this one never held the port, so `stop` has nothing to re-check
        raise RuntimeError(f"no http.server for {self.directory} answered on a free 127.0.0.1 port after 3 tries")

    def _wait_until_ready(self):
        deadline = time.monotonic() + SERVER_READY_SECONDS
        while time.monotonic() < deadline and self.process.poll() is None:
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{self.port}/", timeout=1).close()
                return self.process.poll() is None  # an answer from another process means ours lost the port
            except OSError:
                time.sleep(SERVER_POLL_SECONDS)
        return False

    def _kill(self):
        if self.process.poll() is not None:
            return
        if os.name == "nt":  # the whole tree, by the PID this run started
            subprocess.run(["taskkill", "/PID", str(self.process.pid), "/T", "/F"], capture_output=True, timeout=SERVER_STOP_SECONDS)
        else:
            self.process.terminate()
        try:
            self.process.wait(timeout=SERVER_STOP_SECONDS)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=SERVER_STOP_SECONDS)

    def stop(self):
        if self.process is None:
            return
        self._kill()
        deadline = time.monotonic() + SERVER_STOP_SECONDS
        while _port_accepts(self.port):
            if time.monotonic() > deadline:
                raise RuntimeError(f"127.0.0.1:{self.port} still accepts connections after http.server pid {self.process.pid} was stopped")
            time.sleep(SERVER_POLL_SECONDS)
        print(f"streaks tests: stopped http.server pid {self.process.pid}, 127.0.0.1:{self.port} refuses connections", file=sys.stderr)
        self.process = None


def pytest_configure(config):
    """Serve the app for the run when no server is named, so `python -m pytest tests/browser -q` works alone.

    STREAKS_BASE_URL names a server somebody else runs (the mutation runner, a QA finder) and wins.
    Otherwise this starts two: the project root, and its parent folder for the sub-path scenario
    (STREAKS_SUBPATH_URL still wins for the second). Each is registered for cleanup before it starts.
    """
    global BASE_URL, SUBPATH_URL
    if BASE_URL:
        return
    root = _StaticServer(ROOT)
    config.add_cleanup(root.stop)
    root.start()
    BASE_URL = f"http://127.0.0.1:{root.port}/"
    if not SUBPATH_URL:
        parent = _StaticServer(ROOT.parent)
        config.add_cleanup(parent.stop)
        parent.start()
        SUBPATH_URL = f"http://127.0.0.1:{parent.port}/{ROOT.name}/"


def _require_base_url():
    if not BASE_URL.endswith("/"):
        pytest.fail(
            "STREAKS_BASE_URL must end with '/', for example http://127.0.0.1:8765/ "
            "(leave it unset and the run serves the app itself)"
        )


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as playwright:
        chromium = playwright.chromium.launch(headless=True, args=["--force-color-profile=srgb"])
        yield chromium
        chromium.close()


class PageLog:
    """Requests, console messages and page errors seen by one page since `record` was called."""

    def __init__(self):
        self.requests = []
        self.console = []
        self.errors = []


_LOGS = weakref.WeakKeyDictionary()


def _start_recording(page):
    """Start collecting the page's requests, console messages and page errors, and return the log.

    A second call returns the same log without resetting it, so a test opened with
    `open_app(..., record=True)` reads the log with `record(page)`.
    """
    if page in _LOGS:
        return _LOGS[page]
    log = PageLog()
    _LOGS[page] = log

    def on_request(request):
        parts = urlsplit(request.url)
        log.requests.append(
            {
                "method": request.method,
                "url": request.url,
                "origin": f"{parts.scheme}://{parts.netloc}",
                "path": parts.path,
                "query": parts.query,
            }
        )

    page.on("request", on_request)
    page.on("console", lambda message: log.console.append({"type": message.type, "text": message.text}))
    page.on("pageerror", lambda error: log.errors.append(str(error)))
    return log


# Public name of `_start_recording`. `open_app` has a parameter called `record`, which shadows this
# name inside that function, so the function itself keeps a private name.
record = _start_recording


# Counts localStorage writes without adding a property to window (R26): each call logs a marker to the
# console, which the page log records. It wraps the real setItem, so the app still saves.
WRITE_MARK = "streaks-test: setItem"
_WRITE_COUNTER_SCRIPT = """(() => {
  const original = Storage.prototype.setItem;
  Storage.prototype.setItem = function (...args) {
    console.log('%s');
    return original.apply(this, args);
  };
})();""" % WRITE_MARK
_COUNTING = weakref.WeakSet()
_CLOCK_INSTALLED = weakref.WeakSet()


def open_app(
    browser,
    viewport=(390, 844),
    locale="en-US",
    reduced_motion="no-preference",
    fixed_time=NOON,
    install_time=None,
    storage=None,
    init_script=None,
    record=False,
    path="",
    base_url=None,
    count_writes=False,
    touch=False,
):
    """Open the running app in a new context and return (context, page).

    Order matters: the clock; then seeding (a same-origin 404 page, so no app code runs before the
    seed); then the init script, which therefore never runs on the seeding page; then recording, so the
    seeding request is not in the log; then the app URL. `install_time` wins over `fixed_time`: an
    installed clock lets a test advance time with `page.clock`, a fixed one only pins the date.
    `base_url` replaces STREAKS_BASE_URL, for the sub-path scenario. `count_writes` makes
    `write_count(page)` work: it adds the counter after seeding, so the seed is not counted, and records.
    `touch` gives the context a touch screen, so `page.touchscreen.tap` works.
    """
    if base_url is None:
        _require_base_url()
        base_url = BASE_URL
    context = browser.new_context(
        viewport={"width": viewport[0], "height": viewport[1]},
        device_scale_factor=1,
        color_scheme="light",
        timezone_id=TZ,
        locale=locale,
        reduced_motion=reduced_motion,
        has_touch=touch,
    )
    context.set_default_timeout(DEFAULT_TIMEOUT_MS)
    context.set_default_navigation_timeout(2 * DEFAULT_TIMEOUT_MS)
    if install_time is not None:
        context.clock.install(time=install_time)
    elif fixed_time is not None:
        context.clock.set_fixed_time(fixed_time)
    page = context.new_page()
    if install_time is not None:
        _CLOCK_INSTALLED.add(page)
    if storage is not None:
        page.goto(base_url + "__seed__")
        page.evaluate("(text) => localStorage.setItem('streaks.state', text)", storage)
    if init_script is not None:
        context.add_init_script(init_script)
    if count_writes:
        context.add_init_script(_WRITE_COUNTER_SCRIPT)
        _COUNTING.add(page)
    if record or count_writes:
        _start_recording(page)
    page.goto(base_url + path)
    return context, page


@pytest.fixture
def app(browser):
    """`app(**options)` opens the app like `open_app` and returns the page; contexts close at teardown."""
    contexts = []

    def open_page(**options):
        context, page = open_app(browser, **options)
        contexts.append(context)
        return page

    yield open_page
    for context in contexts:
        context.close()


_VISIBILITY_SCRIPT = """(state) => {
  const hidden = state === 'hidden';
  Object.defineProperty(document, 'visibilityState', { value: state, configurable: true });
  Object.defineProperty(document, 'hidden', { value: hidden, configurable: true });
  document.dispatchEvent(new Event('visibilitychange'));
}"""


def hide_tab(page):
    """Simulate a hidden tab test-side: headless Chromium keeps visibilityState 'visible' otherwise."""
    page.evaluate(_VISIBILITY_SCRIPT, "hidden")


def show_tab(page):
    page.evaluate(_VISIBILITY_SCRIPT, "visible")


def stored(page):
    return page.evaluate("() => localStorage.getItem('streaks.state')")


def write_count(page):
    """How many times the page has called localStorage.setItem since it opened with `count_writes=True`.

    Fails for a page that was not opened that way, because a count nobody takes would read as zero.
    The evaluate is a round trip, so console messages sent before it are in the log when it is read.
    """
    assert page in _COUNTING, "open the page with open_app(count_writes=True)"
    page.evaluate("() => 0")
    return sum(message["text"] == WRITE_MARK for message in _LOGS[page].console)


def row(page, name):
    return page.locator("li.habit").filter(has=page.get_by_text(name, exact=True))


def day(page, name, date):
    return row(page, name).locator(f'button.day[data-date="{date}"]')


def cell(page, date):
    return page.locator(f'.cells .hc[data-date="{date}"]')


def level_classes(locator):
    """The heat level classes of one cell ('l0' to 'l4'), for example ['l2']."""
    return [c for c in locator.get_attribute("class").split() if c[0] == "l" and c[1:].isdigit()]


_HEAT_CELL_FIELDS = (
    "(els) => els.map((e) => [e.className, e.getAttribute('data-date'), e.getAttribute('role'),"
    " e.getAttribute('aria-hidden'), e.getAttribute('aria-label'), e.getAttribute('aria-current')])"
)


def heat_cells(page):
    """Every heat cell as (class, data-date, role, aria-hidden, aria-label, aria-current)."""
    return page.locator(".cells > span").evaluate_all(_HEAT_CELL_FIELDS)


def add_button(page):
    return page.get_by_role("button", name="Add", exact=True)


def type_name(page, text):
    """Click the 'New habit' field and type into it, without submitting."""
    page.locator("#new-habit").click()
    page.keyboard.type(text)


def add_habit(page, text, enter=False):
    """Add a habit with real gestures: type the name, then click Add or press Enter."""
    type_name(page, text)
    if enter:
        page.keyboard.press("Enter")
    else:
        add_button(page).click()


def is_focused(locator):
    return locator.evaluate("(element) => element === document.activeElement")


def trash(page, name):
    """The delete button of the habit called `name`."""
    return page.get_by_role("button", name=f"Delete {name}", exact=True)


# U+2068 FIRST STRONG ISOLATE and U+2069 POP DIRECTIONAL ISOLATE wrap the name in the dialog title, so a
# bidirectional override inside a name cannot reorder the quotes around it (spec R13 note, SEC-02). Built with
# chr() so that no tool turns an escape in this source into the raw characters.
FSI, PDI = chr(0x2068), chr(0x2069)


def dialog_title(name):
    """The exact text of #del-title when the name is shown as `name`.

    That is the stored name unless it holds a bidi format character: the title leaves those out (spec R13 note,
    SEC-06), so a test of such a name writes the shown name out, it does not pass the stored one.
    """
    return f'Delete "{FSI}{name}{PDI}"?'


def open_delete_dialog(page, name):
    trash(page, name).click()
    expect(page.locator("dialog.dialog")).to_have_attribute("open", "")


def let_guard_pass(page):
    """Let the dialog's guard window (GUARD_WINDOW_MS) pass, as the time between two deliberate clicks does.

    Needs a page opened with `install_time`. Event timestamps follow Playwright's installed clock
    (a fixed one does not move them), so `run_for` passes the window at once and without a sleep.
    """
    assert page in _CLOCK_INSTALLED, "open the page with open_app(install_time=...)"
    page.clock.run_for(GUARD_WINDOW_MS + 100)


def confirm_delete(page):
    """Click 'Delete habit' the way a person who means it does, then let the page listen again.

    'Delete habit' ignores a click that comes too soon after the one that opened the dialog, and the page
    ignores clicks that come too soon after a click in the dialog, so the window passes before and after.
    """
    let_guard_pass(page)
    page.get_by_role("button", name="Delete habit", exact=True).click()
    let_guard_pass(page)


def center(locator):
    box = locator.bounding_box()
    return box["x"] + box["width"] / 2, box["y"] + box["height"] / 2


def tab_until(page, locator, limit=60):
    """Press Tab (at most `limit` times) until `locator` has focus, as a keyboard user would."""
    for _ in range(limit):
        page.keyboard.press("Tab")
        if is_focused(locator):
            return
    pytest.fail(f"focus did not reach the target within {limit} Tab presses")


def pattern(page, name):
    """The row's strip as 'D' (done) and '.' (not done), oldest day first, for example '. D D D D D D'."""
    return row(page, name).locator("button.day").evaluate_all(
        "(buttons) => buttons.map((b) => (b.getAttribute('aria-pressed') === 'true' ? 'D' : '.')).join(' ')"
    )


def streak(page, name):
    """The row's streak line as {'cur', 'cur_class', 'best', 'children'}; 'best' is None without a span.best."""
    return row(page, name).locator("p.streak").evaluate(
        """(line) => {
          const best = line.querySelector('.best');
          return {
            cur: line.querySelector('.cur').textContent,
            cur_class: line.querySelector('.cur').className,
            best: best ? best.textContent : null,
            children: line.children.length,
          };
        }"""
    )


_WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
_MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


def short_date(key):
    """'Tue 6 Oct' for '2026-10-06', worked out here from the calendar so tests do not reuse the app's code."""
    moment = datetime.date.fromisoformat(key)
    return f"{_WEEKDAYS[moment.weekday()][:3]} {moment.day} {_MONTHS[moment.month - 1][:3]}"


def long_date(key):
    """'Tuesday 6 October' for '2026-10-06'."""
    moment = datetime.date.fromisoformat(key)
    return f"{_WEEKDAYS[moment.weekday()]} {moment.day} {_MONTHS[moment.month - 1]}"


def add_days(key, days):
    return (datetime.date.fromisoformat(key) + datetime.timedelta(days=days)).isoformat()


# Both sides are reduced to the same text: namespace and element name (an `svg` made with createElement
# is an HTML element that never draws, so the namespace is part of the markup), attributes sorted by
# name, the style attribute as the browser normalises it, and text with the whitespace-only nodes between
# tags dropped. `ignore` lists selectors of live-side parts the golden does not have, removed from a clone.
_CANONICAL_PAIR_JS = """([goldenHtml, selector, ignore]) => {
  const canon = (node) => {
    if (node.nodeType === Node.TEXT_NODE) return node.textContent.trim() === '' ? '' : node.textContent;
    if (node.nodeType !== Node.ELEMENT_NODE) return '';
    const attributes = Array.from(node.attributes)
      .map((a) => a.name + '="' + (a.name === 'style' ? node.style.cssText : a.value) + '"')
      .sort()
      .join(' ');
    const inner = Array.from(node.childNodes).map(canon).join('');
    const name = node.namespaceURI + ' ' + node.localName;
    return '<' + name + ' ' + attributes + '>' + inner + '</' + name + '>';
  };
  const live = document.querySelector(selector).cloneNode(true);
  for (const part of ignore) live.querySelectorAll(part).forEach((node) => node.remove());
  const golden = new DOMParser().parseFromString(goldenHtml, 'text/html');
  return [canon(live), canon(golden.querySelector(selector))];
}"""


def canonical_pair(page, screen, selector, ignore=()):
    """(live, golden) canonical text of the element `selector` in the running page and in docs/design/<screen>."""
    golden = (DESIGN_DIR / screen).read_text(encoding="utf-8")
    return page.evaluate(_CANONICAL_PAIR_JS, [golden, selector, list(ignore)])


def shot(page, name):
    """Save a full-page screenshot under STREAKS_EVIDENCE_DIR when it is set, and do nothing otherwise."""
    if not EVIDENCE_DIR:
        return
    folder = pathlib.Path(EVIDENCE_DIR)
    if not folder.is_absolute():
        folder = ROOT / folder
    folder.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(folder / f"{name}.png"), full_page=True)
