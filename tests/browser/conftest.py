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
    `touch` gives the context a touch screen, so `page.touchscreen.tap` works.
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


_WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
_MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


def short_date(key):
    """'Tue 6 Oct' for '2026-10-06', worked out here from the calendar so tests do not reuse the app's code."""
    moment = datetime.date.fromisoformat(key)
    return f"{_WEEKDAYS[moment.weekday()][:3]} {moment.day} {_MONTHS[moment.month - 1][:3]}"
