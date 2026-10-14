"""Shared fixtures and helpers for the Streaks browser tests (app qa.md, "conftest.py").

Why: every test opens the running app the same way (one headless browser of the run's engine, a fixed time
zone, a controlled clock, optional seeded storage, the clipboard stand-in), so that setup lives here once.
Input: the pytest option --engine (chromium, the default, or webkit), and STREAKS_BASE_URL (ends with "/"),
STREAKS_SUBPATH_URL and STREAKS_EVIDENCE_DIR, all optional. When
STREAKS_BASE_URL is absent this module serves the app itself for the run (see `pytest_configure`), so
`python -m pytest tests/browser -q` works with nothing set. Output: fixtures and helpers; nothing here
touches the app's code, and tests only ever reach the app through real gestures and by seeding
localStorage before it loads.
"""
import datetime
import json
import os
import pathlib
import re
import socket
import subprocess
import sys
import time
import urllib.request
import weakref
from urllib.parse import urlsplit

import pytest
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[2]
DESIGN_DIR = ROOT / "docs" / "design"
SAMPLE_FILE = DESIGN_DIR / "sample-history.json"  # read-only, like every file in DESIGN_DIR

# Rebound by `pytest_configure`: the two URLs when the run serves the app itself, EVIDENCE_DIR to end with the
# engine. Test modules read them with `from conftest import ...` at import, which pytest does only after that hook.
BASE_URL = os.environ.get("STREAKS_BASE_URL", "")
SUBPATH_URL = os.environ.get("STREAKS_SUBPATH_URL", "")
EVIDENCE_DIR = os.environ.get("STREAKS_EVIDENCE_DIR", "")

ENGINES = ("chromium", "webkit")
# Chromium switches must never reach WebKit. srgb keeps Chromium's colours equal to the Chromium renders of the goldens.
LAUNCH_ARGS = {"chromium": ["--force-color-profile=srgb"], "webkit": []}

SERVER_READY_SECONDS = 10  # qa.md: poll every 250 ms and give up after 10 seconds
SERVER_POLL_SECONDS = 0.25
SERVER_STOP_SECONDS = 10

STORAGE_KEY = "streaks.state"
# UTC+8 all year, no DST, so a result never depends on the machine's own zone (ROADMAP D5).
TZ = "Asia/Kuala_Lumpur"
TODAY = "2026-10-10"  # the sample's today, Saturday 10 October 2026
NOON = "2026-10-10T12:00:00+08:00"
# A test that freezes an installed clock pauses here, 20 seconds after NOON: later than a page needs to
# load, earlier than the app's first 30 second rollover check.
PAUSE_AT = "2026-10-10T12:00:20+08:00"
# The page guard of spec R14 (CG-11). For this long after a mouse or touch click inside a popup, the page and any
# popup open beneath it ignore clicks. The spec's number, written out and not read from src/ on purpose, so the
# edge scenarios (pressed at this value minus 1 ms and at this value) fail for any other window in src/app.js.
GUARD_WINDOW_MS = 500
DEFAULT_TIMEOUT_MS = 5000


def _sample_habits():
    """Every habit of the v1.1.0 design sample as `{ name, done }`, in the sample's order.

    Each `done` there is one character a day from the sample's `from`, "1" for a done day, so position i
    becomes the date key `from` plus i days (qa.md, conftest table).
    """
    sample = json.loads(SAMPLE_FILE.read_text(encoding="utf-8"))
    start = datetime.date.fromisoformat(sample["from"])
    return [
        {
            "name": habit["name"],
            "done": [(start + datetime.timedelta(days=i)).isoformat() for i, flag in enumerate(habit["done"]) if flag == "1"],
        }
        for habit in sample["habits"]
    ]


TWELVE = _sample_habits()  # the S3 golden's twelve habits
SAMPLE_HABITS = TWELVE[:3]  # K1, P1 to P4 and M1 use the first three


def encode(habits):
    """The text `encodeState` writes for a list of habits: compact JSON, non-ASCII kept as is."""
    return json.dumps({"version": 1, "habits": habits}, separators=(",", ":"), ensure_ascii=False)


def sample_state():
    return encode(SAMPLE_HABITS)


def twelve_state():
    return encode(TWELVE)


def plain_state(count):
    """qa.md's named state "N plain habits", "Habit 1" to "Habit N" with no done day."""
    return encode([{"name": f"Habit {n}", "done": []} for n in range(1, count + 1)])


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


def with_engine(folder, engine):
    """`folder` with its last part ending in "-<engine>", so the evidence of two engines never shares a folder.

    Used for STREAKS_EVIDENCE_DIR here and for the live gate's --out (app spec R30). An empty folder stays empty.
    """
    if not folder:
        return folder
    path = pathlib.PurePath(folder)
    return folder if path.name.endswith(f"-{engine}") else str(path.with_name(f"{path.name}-{engine}"))


def pytest_configure(config):
    """Serve the app for the run when no server is named, so `python -m pytest tests/browser -q` works alone.

    STREAKS_BASE_URL names a server somebody else runs (the mutation runner, a QA finder) and wins.
    Otherwise this starts two: the project root, and its parent folder for the sub-path scenario
    (STREAKS_SUBPATH_URL still wins for the second). Each is registered for cleanup before it starts.
    It also registers the chromium_only marker and gives the evidence folder its engine (app spec R30).
    """
    global BASE_URL, SUBPATH_URL, EVIDENCE_DIR
    config.addinivalue_line(
        "markers", "chromium_only(reason): a counted skip with that reason when the engine is not Chromium (app spec R30)"
    )
    EVIDENCE_DIR = with_engine(EVIDENCE_DIR, config.getoption("--engine"))
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


def pytest_addoption(parser):
    parser.addoption(
        "--engine", choices=ENGINES, default="chromium", help="browser engine of this run, chromium or webkit (app spec R30)"
    )


def pytest_collection_modifyitems(config, items):
    """Turn every `chromium_only(reason=...)` test into a skip that carries its reason when the engine is not Chromium."""
    if config.getoption("--engine") == "chromium":
        return
    for item in items:
        marker = item.get_closest_marker("chromium_only")
        if marker is None:
            continue
        reason = marker.kwargs.get("reason", "")
        if not reason:
            raise pytest.UsageError(f"{item.nodeid}: chromium_only needs reason=... (app spec R30)")
        item.add_marker(pytest.mark.skip(reason=f"chromium_only: {reason}"))


def pytest_terminal_summary(terminalreporter, config):
    """Count and list the chromium_only skips, so a WebKit run never reports them as passes (app spec R30)."""
    skips = [
        report for report in terminalreporter.stats.get("skipped", [])
        if isinstance(report.longrepr, tuple) and "chromium_only: " in report.longrepr[2]
    ]
    terminalreporter.write_line(f"engine {config.getoption('--engine')}: {len(skips)} chromium_only skip(s)")
    for report in skips:
        terminalreporter.write_line(f"  {report.nodeid}: {report.longrepr[2]}")


@pytest.fixture(scope="session")
def engine(pytestconfig):
    return pytestconfig.getoption("--engine")


def launch(playwright, engine):
    """Start one headless browser of `engine` ("chromium" or "webkit") and return it.

    The only place in tests/browser that launches a browser (app spec R30, checked by test_engines.py), so each
    engine gets only its own arguments. Any other engine raises ValueError before anything starts.
    """
    if engine not in ENGINES:
        raise ValueError(f"unknown engine {engine!r}, expected one of {', '.join(ENGINES)}")
    return getattr(playwright, engine).launch(headless=True, args=LAUNCH_ARGS[engine])


@pytest.fixture(scope="session")
def playwright():
    """The one Playwright driver of the run, shared by `browser` and by tests that call `launch` themselves."""
    with sync_playwright() as driver:
        yield driver


@pytest.fixture(scope="session")
def browser(playwright, engine):
    started = launch(playwright, engine)
    yield started
    started.close()


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

# Never touch the system clipboard (constitution, Browser gates). Every context gets this before anything else:
# when the page can reach a clipboard, its four methods log the marker "test:clipboard:<method>" and resolve
# instead. The app has no copy feature, so any marker in a run is a finding. It adds no property to window.
CLIPBOARD_STANDIN = """(() => {
  if (!navigator.clipboard || typeof Clipboard !== 'function') return;
  for (const method of ['writeText', 'write', 'readText', 'read']) {
    if (!(method in Clipboard.prototype)) continue;
    Object.defineProperty(Clipboard.prototype, method, {
      configurable: true,
      writable: true,
      value: function () {
        console.log('test:clipboard:' + method);
        return Promise.resolve(method === 'readText' ? '' : method === 'read' ? [] : undefined);
      },
    });
  }
})();"""


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
    `touch` gives the context a touch screen, so `page.touchscreen.tap` works. `init_script` is one script or a list.
    """
    if base_url is None:
        _require_base_url()
        base_url = BASE_URL
    context = browser.new_context(
        viewport={"width": viewport[0], "height": viewport[1]},
        device_scale_factor=1,
        color_scheme="dark",  # the app has one dark theme and no rule reads the scheme (qa.md, open_app)
        timezone_id=TZ,
        locale=locale,
        reduced_motion=reduced_motion,
        has_touch=touch,
    )
    context.add_init_script(CLIPBOARD_STANDIN)
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
    scripts = init_script if isinstance(init_script, list) else [] if init_script is None else [init_script]
    for script in scripts:
        context.add_init_script(script)
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


# The storage drivers of qa.md ("Storage failures are driven from the test side only"), D-a, D-b, D-c and D-e. Each is
# an init script for `open_app(init_script=...)`, which adds it after seeding. Each starts failing and follows
# `storage_switch`. None touches localStorage at its top level, because an init script also runs in the blank first
# document, where storage access is denied. Test code only, never shipped.
_DRIVER = """(() => {
  let failing = true;
  window.addEventListener('test:storage', (event) => { failing = event.detail; });
%s
})();"""

# D-a, setItem throws a quota error while failing.
FAIL_SETITEM = _DRIVER % """  const setItem = Storage.prototype.setItem;
  Storage.prototype.setItem = function (...args) {
    if (failing) throw new DOMException('test quota', 'QuotaExceededError');
    return setItem.apply(this, args);
  };"""

# D-b, reading window.localStorage throws while failing (honoured by both engines, task 11 probe P1).
FAIL_GETTER = _DRIVER % """  const store = Object.getOwnPropertyDescriptor(window, 'localStorage');
  Object.defineProperty(window, 'localStorage', {
    configurable: true,
    enumerable: store.enumerable,
    get() {
      if (failing) throw new DOMException('test denied', 'SecurityError');
      return store.get.call(window);
    },
  });"""

# D-c, getItem throws while failing.
FAIL_GETITEM = _DRIVER % """  const getItem = Storage.prototype.getItem;
  Storage.prototype.getItem = function (...args) {
    if (failing) throw new DOMException('test read', 'SecurityError');
    return getItem.apply(this, args);
  };"""

# D-e, D-a whose thrown value logs "test:storage-read:<property>" when its name, code or message is read.
STORAGE_READ_MARK = "test:storage-read:"
FAIL_SETITEM_PROBE = _DRIVER % ("""  const setItem = Storage.prototype.setItem;
  const watched = () => {
    const thrown = {};
    for (const property of ['name', 'code', 'message']) {
      Object.defineProperty(thrown, property, {
        get() {
          console.log('%s' + property);
          return property === 'code' ? 22 : 'test quota';
        },
      });
    }
    return thrown;
  };
  Storage.prototype.setItem = function (...args) {
    if (failing) throw watched();
    return setItem.apply(this, args);
  };""" % STORAGE_READ_MARK)


def storage_switch(page, failing):
    """Turn the page's storage driver to failing (True) or working (False), through the event every driver listens for."""
    page.evaluate("(failing) => window.dispatchEvent(new CustomEvent('test:storage', { detail: failing }))", failing)


FILL_SECONDS = 60  # qa.md's cap for driver D-d. Task 11 measured the fill at 0.03 s or less in both engines.
# Driver D-d. New test.fill.<n> keys of halving sizes, then the last key grown in halving steps, until even one more
# character is refused. Bounded by its count of writes, so it cannot spin.
_FILL_JS = """() => {
  const write = (key, value) => { try { localStorage.setItem(key, value); return true; } catch { return false; } };
  let keys = 0;
  let writes = 0;
  for (let size = 1 << 20; size >= 1 && writes < 1000; writes += 1) {
    if (write('test.fill.' + keys, 'x'.repeat(size))) keys += 1;
    else size = Math.floor(size / 2);
  }
  const last = 'test.fill.' + (keys - 1);
  for (let size = 64; size >= 1 && writes < 2000; writes += 1) {
    if (!write(last, localStorage.getItem(last) + 'x'.repeat(size))) size = Math.floor(size / 2);
  }
  const full = keys > 0 && !write(last, localStorage.getItem(last) + 'x');
  let characters = 0;
  for (let n = 0; n < keys; n += 1) characters += localStorage.getItem('test.fill.' + n).length;
  return { keys, characters, writes, full };
}"""


def fill_quota(page):
    """Driver D-d, a real full quota. Fills the origin's storage until even one more character is refused, and returns
    what it wrote. Fails when the store still takes a character, or when the fill took longer than FILL_SECONDS."""
    started = time.monotonic()
    fill = page.evaluate(_FILL_JS)
    fill["seconds"] = round(time.monotonic() - started, 3)
    assert fill["full"], f"the store still takes a character after the fill: {fill}"
    assert fill["seconds"] < FILL_SECONDS, f"the fill took longer than {FILL_SECONDS} seconds: {fill}"
    return fill


def clear_fill(page):
    """Remove the keys `fill_quota` wrote, and return how many there were."""
    return page.evaluate(
        """() => {
  const keys = Array.from({ length: localStorage.length }, (_, n) => localStorage.key(n)).filter((key) => key.startsWith('test.fill.'));
  keys.forEach((key) => localStorage.removeItem(key));
  return keys.length;
}"""
    )


_MUTATION_LOG_JS = """(node) => {
  const log = { added: 0, removed: 0 };
  const count = (records) => records.forEach((record) => {
    log.added += record.addedNodes.length;
    log.removed += record.removedNodes.length;
  });
  const observer = new MutationObserver(count);
  observer.observe(node, { childList: true });
  log.read = () => {
    count(observer.takeRecords());
    return { added: log.added, removed: log.removed };
  };
  return log;
}"""


def mutation_log(page, selector):
    """A test-side handle on the child additions and removals a MutationObserver sees on the element at `selector` from
    now on, read with `mutations`. It adds no property to window."""
    return page.locator(selector).evaluate_handle(_MUTATION_LOG_JS)


def mutations(log):
    """{"added": n, "removed": m}, the children `log` saw added and removed so far, records not yet delivered included."""
    return log.evaluate("(log) => log.read()")


def write_evidence(name, data):
    """Write `data` as JSON into the run's evidence folder (STREAKS_EVIDENCE_DIR, ending with the engine), when set."""
    if not EVIDENCE_DIR:
        return
    folder = pathlib.Path(EVIDENCE_DIR)
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{name}.json").write_text(json.dumps(data, indent=1), encoding="utf-8")


def add_button(page):
    return page.get_by_role("button", name="Add", exact=True)


def type_name(page, text):
    """Click the 'New habit' field and type into it, without submitting."""
    page.locator("#nh").click()
    page.keyboard.type(text)


def add_habit(page, text, enter=False):
    """Add a habit with real gestures: type the name, then click Add or press Enter."""
    type_name(page, text)
    if enter:
        page.keyboard.press("Enter")
    else:
        add_button(page).click()


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


def let_guard_pass(page):
    """Let the page guard's window (GUARD_WINDOW_MS) pass, as the time between two deliberate clicks does.

    Needs a page opened with `install_time`. Event timestamps follow Playwright's installed clock
    (a fixed one does not move them), so `run_for` passes the window at once and without a sleep.
    """
    assert page in _CLOCK_INSTALLED, "open the page with open_app(install_time=...)"
    page.clock.run_for(GUARD_WINDOW_MS + 100)


def row(page, name):
    """The `li.row` whose `h3` reads `name` exactly."""
    return page.locator("ul.rows > li.row").filter(has=page.locator("h3.r-name").get_by_text(name, exact=True))


def bin_btn(page, name):
    return page.get_by_role("button", name=f'Delete "{name}"', exact=True)


def year_btn(page, name):
    return page.get_by_role("button", name=f"Year view, {name}", exact=True)


def done_btn(page, name):
    return page.get_by_role("button", name=f"Done today, {name}", exact=True)


def band_day(page, key):
    """The band's day button for the date key (in the DOM at every width, displayed from 1024 px)."""
    return page.locator(f'section.band div.ovg-cols button.hc[data-key="{key}"]')


def p3_day(page, key):
    return page.locator(f'dialog.dlg-ov div.ovg-rows button.hc[data-key="{key}"]')


def p4_day(page, key):
    return page.locator(f'dialog.dlg-all div.months button.hc[data-key="{key}"]')


def bead(page, key):
    """P2's day button for the date key."""
    return page.locator(f'dialog.dlg-year div.months button.yc[data-key="{key}"]')


def tick(page, name):
    """P1's tick for a habit, named by the habit's name."""
    return page.locator("dialog.dlg-day ul.day-list").get_by_role("button", name=name, exact=True)


def tab_to(page, target, limit=200):
    """Press Tab until the locator `target` has focus. Fails after `limit` presses. Raw keys, so it works under a
    paused clock."""
    for _ in range(limit):
        if target.evaluate("(node) => node === document.activeElement"):
            return
        page.keyboard.press("Tab")
    pytest.fail(f"{target} did not take focus in {limit} presses of Tab")


def point_beside(target, avoid):
    """The centre of the largest part of the box of the locator `target` that lies outside the box of `avoid`.

    Fails at once when `target` lies wholly inside `avoid`, or when either is not shown.
    """
    box, other = target.bounding_box(), avoid.bounding_box()
    if box is None or other is None:
        pytest.fail(f"no box to measure, {target} gives {box} and {avoid} gives {other}")
    left, top = box["x"], box["y"]
    right, bottom = left + box["width"], top + box["height"]
    a_left, a_top = other["x"], other["y"]
    a_right, a_bottom = a_left + other["width"], a_top + other["height"]
    parts = [
        (left, top, min(right, a_left), bottom),
        (max(left, a_right), top, right, bottom),
        (left, top, right, min(bottom, a_top)),
        (left, max(top, a_bottom), right, bottom),
    ]
    parts = [part for part in parts if part[2] > part[0] and part[3] > part[1]]
    if not parts:
        pytest.fail(f"{box} lies wholly inside {other}")
    x0, y0, x1, y1 = max(parts, key=lambda part: (part[2] - part[0]) * (part[3] - part[1]))
    return (x0 + x1) / 2, (y0 + y1) / 2


def confirm_delete(page, opener):
    """Click M1's Delete habit at the centre of the largest part of its box that lies outside the opener's box.

    The guard of spec R13 ignores a pointer click inside the box of the control that opened M1 (CG-10), so a
    deliberate click lands beside it. Fails at once when Delete habit lies wholly inside the opener's box.
    """
    page.mouse.click(*point_beside(page.locator("dialog.dlg-del button.btn-danger"), opener))


_CLOSE_WATCH_JS = """(dialog) => {
  const seen = { closed: false };
  dialog.addEventListener('close', () => { seen.closed = true; }, { once: true });
  return seen;
}"""


def watch_close(page, selector):
    """Watch the dialog at `selector` for its next close event, for `wait_for_close`.

    The close event is a queued task, so right after a gesture closes a dialog the app's close handler may not have
    run yet, and in Chromium the browser's own focus restore can already show the opener focused. This test-side
    listener is added after the app's, so once it has run the app's handler has run too. It adds no property to window.
    """
    return page.locator(selector).evaluate_handle(_CLOSE_WATCH_JS)


def wait_for_close(watch, seconds=5):
    """Wait until the close event that `watch` looks for has come. Polled from here, so it works under a paused clock.
    Fails after `seconds`."""
    deadline = time.monotonic() + seconds
    while not watch.evaluate("(seen) => seen.closed"):
        if time.monotonic() > deadline:
            pytest.fail(f"no close event within {seconds} seconds")
        time.sleep(0.02)


def press_twice(page, x, y, how):
    """Two presses at one point, what a person's double click ("mouse", `mouse.dblclick`) or double tap ("touch", two
    `touchscreen.tap`) sends. Meant for a paused installed clock, so both land at the same instant on any machine.
    Fails at once on a page opened without `install_time`.
    """
    assert page in _CLOCK_INSTALLED, "open the page with open_app(install_time=...) and pause its clock"
    if how == "mouse":
        page.mouse.dblclick(x, y)
    elif how == "touch":
        page.touchscreen.tap(x, y)
        page.touchscreen.tap(x, y)
    else:
        raise ValueError(f"how is 'mouse' or 'touch', not {how!r}")


# p.stats or p.yr-stats as a tree. An element is "tag.class.class", a leaf adds ":text", a parent is [name, [children]].
# The motion class "bump" (spec R32) is left out, so a tree reads the same during and after a number's rise.
_STATS_TREE_JS = """(stats) => {
  const label = (node) => [node.localName, ...Array.from(node.classList).filter((name) => name !== 'bump')].join('.');
  const tree = (node) => node.children.length ? [label(node), Array.from(node.children).map(tree)] : `${label(node)}:${node.textContent}`;
  return Array.from(stats.children).map(tree);
}"""


def stats_tree(stats):
    """The tree of a `p.stats` or `p.yr-stats` locator, to compare with `current_block` and `best_block`."""
    return stats.evaluate(_STATS_TREE_JS)


def current_block(value=None, unit=None):
    """span.stat.cur as `stats_tree` gives it: with no value, "No streak yet"."""
    if value is None:
        return ["span.stat.cur", ["span.lbl:Current", "span.none:No streak yet"]]
    return ["span.stat.cur", ["span.lbl:Current", ["span.val", [f"b.num:{value}", f"span.unit:{unit}"]]]]


def best_block(value):
    return ["span.stat.best", ["span.lbl:Best", ["span.val", [f"b.num:{value}"]]]]


_ROW_NUMBERS_JS = """(row) => {
  const current = row.querySelector('.stat.cur');
  const value = current.querySelector(':scope > span.val');
  const best = row.querySelector('.stat.best .num');
  return {
    current: value ? `${value.querySelector('b.num').textContent} ${value.querySelector('span.unit').textContent}`
      : current.querySelector(':scope > span.none').textContent,
    best: best && best.textContent,
  };
}"""


def row_numbers(page, name):
    """{"current": "4 days" or "No streak yet", "best": "9" or None} as the row of `name` reads them."""
    return row(page, name).evaluate(_ROW_NUMBERS_JS)


# Rings read as text, so a whole ring compares in one assert (spec R42). The JS turns each child of a ring svg into a
# string, and the Python names below build the same strings from the spec's values.
_RING_PARTS_JS = """const part = (node) => {
  const classes = (node.getAttribute('class') || '').split(/\\s+/).filter(Boolean).map((name) => '.' + name).join('');
  const names = { circle: ['cx', 'cy', 'r'], path: ['d'], text: ['x', 'y', 'dy'] }[node.localName] || [];
  const attributes = names.map((name) => `${name}=${node.getAttribute(name)}`).join(' ');
  const text = node.localName === 'text' ? ` "${node.textContent}"` : '';
  return `${node.localName}${classes}${attributes ? ' ' + attributes : ''}${text}`;
};
const ring = (svg) => svg && {
  viewBox: svg.getAttribute('viewBox'),
  hidden: svg.getAttribute('aria-hidden'),
  parts: Array.from(svg.children).map(part),
};"""

_GRID_JS = (
    "(selector) => {\n"
    + _RING_PARTS_JS
    + """
  return Array.from(document.querySelector(selector).children).map((node) => ({
    tag: node.localName,
    cls: node.getAttribute('class'),
    hidden: node.getAttribute('aria-hidden'),
    text: node.children.length ? null : node.textContent,
    type: node.getAttribute('type'),
    key: node.getAttribute('data-key'),
    popup: node.getAttribute('aria-haspopup'),
    label: node.getAttribute('aria-label'),
    current: node.getAttribute('aria-current'),
    ring: ring(node.querySelector(':scope > svg')),
  }));
}"""
)

_LEGEND_JS = (
    "(selector) => {\n"
    + _RING_PARTS_JS
    + """
  return Array.from(document.querySelector(selector).children).map((node) =>
    node.localName === 'svg' ? ring(node) : `${node.localName}:${node.textContent}`);
}"""
)

_RING_JS = "(selector) => {\n" + _RING_PARTS_JS + "\n  return ring(document.querySelector(selector));\n}"


def grid_children(page, selector):
    """Each child of an overview grid (div.ovg-cols, div.ovg-rows) with its attributes, text and ring."""
    return page.evaluate(_GRID_JS, selector)


def legend_parts(page, selector):
    """A legend's children, "span:<text>" for a word and a `ring_of` dict for a ring."""
    return page.evaluate(_LEGEND_JS, selector)


def ring_parts(page, selector):
    """The ring svg at `selector` as a `ring_of` dict, or None when there is none."""
    return page.evaluate(_RING_JS, selector)


def golden_arcs(golden, prefix, count):
    """The `d` of the shared arc paths `<prefix>-0` to `<prefix>-<count - 1>` of a golden, which R42's rule reproduces."""
    text = (DESIGN_DIR / golden).read_text(encoding="utf-8")
    return [re.search(rf'<path id="{prefix}-{i}" d="([^"]+)"/>', text).group(1) for i in range(count)]


ARCS3 = golden_arcs("today.html", "a3", 3)
ARCS12 = golden_arcs("today-full.html", "a12", 12)
CIRCLE_SEG = "circle.seg cx=20 cy=20 r=15"
CIRCLE_SEG_ON = "circle.seg.on cx=20 cy=20 r=15"
TODAY_CIRCLE = "circle.c-today cx=20 cy=20 r=19.2"
CORE = "circle.c-core cx=20 cy=20 r=11.5"


def seg(d, on):
    return f"path.seg{'.on' if on else ''} d={d}"


def number(day, on=False):
    return f'text.c-num{".on" if on else ""} x=20 y=20 dy=.352em "{day}"'


def ring_of(parts):
    return {"viewBox": "0 0 40 40", "hidden": "true", "parts": parts}


def focused(page):
    """The accessible name of document.activeElement (its aria-label, else its text), or "body"."""
    return page.evaluate(
        """() => {
  const active = document.activeElement;
  if (!active || active === document.body) return 'body';
  return active.getAttribute('aria-label') || active.textContent.trim();
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


def year_date(key):
    """'Fri 10 Oct 2025' for '2025-10-10', the short date with its year (the year views' day names)."""
    return f"{short_date(key)} {key[:4]}"


def month_title(year, month):
    """'October 2026' for (2026, 10)."""
    return f"{_MONTHS[month - 1]} {year}"


def focus_after_a_click_in_a_popup(engine, handle, dialog):
    """Assert where focus is after a mouse click on the button `handle` inside the open popup `dialog` (a selector).

    In Chromium the clicked button has it. WebKit focuses no button on a mouse press (spec Invariants, engine note),
    and inside a modal dialog it leaves focus on the dialog element, not on body (qa.md "Engine differences by
    design", measured at task 18). Either way the app has not moved focus.
    """
    active = handle.evaluate(
        "(button, dialog) => document.activeElement === button ? 'button' : document.activeElement.matches(dialog) ? dialog : document.activeElement.localName",
        dialog,
    )
    assert active == ("button" if engine == "chromium" else dialog), active


# A subtree as [tag, attributes, own text, children], so the app's markup and a golden's compare in one assert. Classes
# are a set (sorted) and the motion classes "pop" and "bump" are left out, since they mark an edit, not the state.
# Whitespace between tags is free (spec Contracts, Rendered markup), so text nodes are trimmed and empty ones dropped.
_CANON_JS = """const canon = (node) => {
  const attributes = Array.from(node.attributes).map((attribute) => attribute.name === 'class'
    ? 'class=' + Array.from(node.classList).filter((name) => name !== 'pop' && name !== 'bump').sort().join(' ')
    : attribute.name + '=' + attribute.value).sort();
  const text = Array.from(node.childNodes).filter((child) => child.nodeType === Node.TEXT_NODE)
    .map((child) => child.textContent.trim()).filter(Boolean).join(' ');
  return [node.localName, attributes, text, Array.from(node.children).map(canon)];
};"""


def canon_tree(page, selector, golden=None):
    """The `_CANON_JS` tree of the first element matching `selector` in the page, or, with `golden` (a file name in
    DESIGN_DIR, read only), in that golden parsed by DOMParser in the page, which runs none of its scripts."""
    if golden is None:
        return page.evaluate("(selector) => {\n" + _CANON_JS + "\nreturn canon(document.querySelector(selector));\n}", selector)
    text = (DESIGN_DIR / golden).read_text(encoding="utf-8")
    return page.evaluate(
        "([selector, text]) => {\n" + _CANON_JS
        + "\nreturn canon(new DOMParser().parseFromString(text, 'text/html').querySelector(selector));\n}",
        [selector, text],
    )


def first_difference(found, expected, path=""):
    """Where two `canon_tree` trees first differ, as a short message, or None when they are equal. Kept short on
    purpose, because pytest's own diff of two trees of several thousand nodes is slow and unreadable."""
    tag, attributes, text, children = found
    if [tag, attributes, text] != expected[:3]:
        return f"{path}/{tag}: {[tag, attributes, text]} != {expected[:3]}"
    for index, (child, twin) in enumerate(zip(children, expected[3])):
        difference = first_difference(child, twin, f"{path}/{tag}[{index}]")
        if difference:
            return difference
    if len(children) != len(expected[3]):
        return f"{path}/{tag}: {len(children)} children != {len(expected[3])}"
    return None
