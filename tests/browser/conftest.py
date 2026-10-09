"""Shared fixtures and helpers for the Streaks browser tests (app qa.md, "conftest.py").

Why: every test opens the running app the same way (one headless Chromium, a fixed time zone, a
controlled clock, optional seeded storage), so that setup lives here once.
Input: STREAKS_BASE_URL (required for tests that open the app, ends with "/"), STREAKS_SUBPATH_URL and
STREAKS_EVIDENCE_DIR (both optional). Output: fixtures and helpers; nothing here touches the app's code,
and tests only ever reach the app through real gestures and by seeding localStorage before it loads.
"""
import json
import os
import pathlib
import weakref
from urllib.parse import urlsplit

import pytest
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[2]
DESIGN_DIR = ROOT / "docs" / "design"

BASE_URL = os.environ.get("STREAKS_BASE_URL", "")
SUBPATH_URL = os.environ.get("STREAKS_SUBPATH_URL", "")
EVIDENCE_DIR = os.environ.get("STREAKS_EVIDENCE_DIR", "")

STORAGE_KEY = "streaks.state"
# UTC+8 all year, no DST, so a result never depends on the machine's own zone (ROADMAP D5).
TZ = "Asia/Kuala_Lumpur"
NOON = "2026-10-08T12:00:00+08:00"
DEFAULT_TIMEOUT_MS = 5000

SAMPLE_HABITS = json.loads((DESIGN_DIR / "sample-history.json").read_text(encoding="utf-8"))["habits"]


def state_text(habits):
    """The text the app stores for a list of habits, in the same compact form."""
    return json.dumps({"version": 1, "habits": habits}, separators=(",", ":"))


def sample_state():
    return state_text(SAMPLE_HABITS)


def plain_state(count):
    """N plain habits named "Habit 1" to "Habit N" with no done days."""
    return state_text([{"name": f"Habit {number}", "done": []} for number in range(1, count + 1)])


def _require_base_url():
    if not BASE_URL.endswith("/"):
        pytest.fail(
            "STREAKS_BASE_URL must be set and end with '/', for example http://127.0.0.1:8765/ "
            "(serve the project root with: python -m http.server <port> --bind 127.0.0.1)"
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
):
    """Open the running app in a new context and return (context, page).

    Order matters: the clock; then seeding (a same-origin 404 page, so no app code runs before the
    seed); then the init script, which therefore never runs on the seeding page; then recording, so the
    seeding request is not in the log; then the app URL. `install_time` wins over `fixed_time`: an
    installed clock lets a test advance time with `page.clock`, a fixed one only pins the date.
    """
    _require_base_url()
    context = browser.new_context(
        viewport={"width": viewport[0], "height": viewport[1]},
        device_scale_factor=1,
        color_scheme="light",
        timezone_id=TZ,
        locale=locale,
        reduced_motion=reduced_motion,
    )
    context.set_default_timeout(DEFAULT_TIMEOUT_MS)
    context.set_default_navigation_timeout(2 * DEFAULT_TIMEOUT_MS)
    if install_time is not None:
        context.clock.install(time=install_time)
    elif fixed_time is not None:
        context.clock.set_fixed_time(fixed_time)
    page = context.new_page()
    if storage is not None:
        page.goto(BASE_URL + "__seed__")
        page.evaluate("(text) => localStorage.setItem('streaks.state', text)", storage)
    if init_script is not None:
        context.add_init_script(init_script)
    if record:
        _start_recording(page)
    page.goto(BASE_URL + path)
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


def row(page, name):
    return page.locator("li.habit").filter(has=page.get_by_text(name, exact=True))


def day(page, name, date):
    return row(page, name).locator(f'button.day[data-date="{date}"]')


def cell(page, date):
    return page.locator(f'.cells .hc[data-date="{date}"]')


def shot(page, name):
    """Save a full-page screenshot under STREAKS_EVIDENCE_DIR when it is set, and do nothing otherwise."""
    if not EVIDENCE_DIR:
        return
    folder = pathlib.Path(EVIDENCE_DIR)
    if not folder.is_absolute():
        folder = ROOT / folder
    folder.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(folder / f"{name}.png"), full_page=True)
