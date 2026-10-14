"""R28, the state scripts the plugin fidelity harness is given (app qa.md, Fidelity gate, scenario "The fidelity state
scripts are right").

They are test-side files in tests/browser/fidelity/, never shipped. These tests run them the way the 2.6.0 harness does,
the seed as the one init script of a fresh context with the clock fixed at 2026-10-10 09:00 local time, and the
after-load script as the body of an async function once the page has loaded. That context gets no `CLIPBOARD_STANDIN`
from `open_app`, because the seed script has to bring it. A second stand-in, defined on the navigator object, is added
after the seed so that no context of this file can ever reach the system clipboard. It leaves `Clipboard.prototype`
alone, so the check that reads the prototype still sees only what the seed did.
"""
import json
import re

import pytest

import conftest
from conftest import CLIPBOARD_STANDIN, ROOT, SAMPLE_HABITS, TWELVE, TZ, dialog_title, record, write_evidence

FIDELITY_DIR = ROOT / "tests" / "browser" / "fidelity"
SEEDS = {"seed-sample.js": SAMPLE_HABITS, "seed-twelve.js": TWELVE}
HARNESS_TIME = "2026-10-10T09:00:00+08:00"  # qa.md's --fixed-time 2026-10-10T09:00:00, in the zone the tests use
PHONES = [(360, 780), (390, 844)]
DESKTOP = (1280, 800)
ALL_THREE = PHONES + [DESKTOP]
SEPT_22 = "2026-09-22"
BIN_NAME = "Stretch 10 minutes"

# The control's stand-in of qa.md, on the navigator object, so Clipboard.prototype.writeText stays native.
NAVIGATOR_STANDIN = """(() => {
  const refuse = () => Promise.reject(new Error('test:clipboard stand-in'));
  Object.defineProperty(navigator, 'clipboard', {
    configurable: true,
    value: { writeText: refuse, write: refuse, readText: refuse, read: refuse },
  });
})();"""

STANDIN_IN_PLACE_JS = """() => !navigator.clipboard
  || !Function.prototype.toString.call(Clipboard.prototype.writeText).includes('[native code]')"""

# One record per dialog of the page, by its class that names the popup, for the state table of the scenario.
DIALOGS_JS = """() => Array.from(document.querySelectorAll('dialog')).map((dialog) => ({
  name: ['dlg-ov', 'dlg-all', 'dlg-year', 'dlg-day', 'dlg-del'].find((c) => dialog.classList.contains(c)),
  open: dialog.open,
  modal: dialog.matches(':modal'),
  scrollTop: dialog.querySelector('div.sheet-body') ? dialog.querySelector('div.sheet-body').scrollTop : null,
}))"""

ACTIVE_JS = """() => {
  const node = document.activeElement;
  if (!node) return 'null';
  if (node === document.body) return 'body';
  return node.tagName.toLowerCase() + (node.className ? '.' + String(node.className).split(' ').join('.') : '');
}"""

SETITEM = re.compile(r'\AlocalStorage\.setItem\("streaks\.state", ("(?:[^"\\]|\\.)*")\);\Z')


def script(name):
    return (FIDELITY_DIR / name).read_text(encoding="utf-8")


def seed_statement(name):
    """The text after the stand-in in the seed script `name`, stripped of the line breaks around it."""
    return script(name)[len(CLIPBOARD_STANDIN):].strip()


def harness_page(browser, viewport, init_scripts):
    """A context like the harness's candidate side, its init scripts in order, and the app loaded. Returns (context, page)."""
    context = browser.new_context(
        viewport={"width": viewport[0], "height": viewport[1]},
        device_scale_factor=1,
        color_scheme="dark",
        timezone_id=TZ,
    )
    context.set_default_timeout(conftest.DEFAULT_TIMEOUT_MS)
    context.clock.set_fixed_time(HARNESS_TIME)
    for source in init_scripts:
        context.add_init_script(source)
    page = context.new_page()
    record(page)
    page.goto(conftest.BASE_URL)
    return context, page


def run_after_load(page, source):
    page.evaluate(f"async () => {{ {source}\n }}")


def open_dialogs(page):
    return {entry["name"]: entry for entry in page.evaluate(DIALOGS_JS) if entry["open"]}


def clipboard_markers(page):
    return [entry["text"] for entry in record(page).console if entry["text"].startswith("test:clipboard:")]


@pytest.mark.parametrize("name", SEEDS)
def test_R28_each_seed_script_is_the_standin_then_one_setItem_of_the_sample(browser, name):
    text = script(name)
    assert text.startswith(CLIPBOARD_STANDIN), f"{name} does not start with the exact text of CLIPBOARD_STANDIN"
    statement = seed_statement(name)
    match = SETITEM.match(statement)
    assert match, f"after the stand-in {name} holds more or less than one localStorage.setItem statement"
    state = json.loads(json.loads(match.group(1)))
    assert state == {"version": 1, "habits": SEEDS[name]}, f"{name} stores a state other than its sample habits"
    for habit in state["habits"]:
        assert habit["done"] == sorted(set(habit["done"])), f"{habit['name']} has a done list that is not ascending"

    context = browser.new_context()
    try:
        page = context.new_page()
        page.goto("about:blank")  # no CSP here, so the statement can run through new Function against a stand-in store
        calls = page.evaluate(
            """(source) => {
              const calls = [];
              new Function('localStorage', source)({ setItem: (key, value) => calls.push([key, value]) });
              return calls;
            }""",
            statement,
        )
    finally:
        context.close()
    assert calls == [["streaks.state", json.loads(match.group(1))]], f"{name} does not make exactly one setItem call"


# The after-load script, the viewport, the open dialogs it must leave, and the extra checks of its table row.
CASES = [
    ("open-day-editor.js", PHONES, {"dlg-ov", "dlg-day"}),
    ("open-day-editor.js", [DESKTOP], {"dlg-day"}),
    ("open-year-view.js", ALL_THREE, {"dlg-year"}),
    ("open-overview.js", PHONES, {"dlg-ov"}),
    ("open-overview-year.js", PHONES, {"dlg-ov", "dlg-all"}),
    ("open-overview-year.js", [DESKTOP], {"dlg-all"}),
    ("open-delete-dialog.js", ALL_THREE, {"dlg-del"}),
]
PARAMS = [
    pytest.param(name, viewport, dialogs, id=f"{name}-{viewport[0]}x{viewport[1]}")
    for name, viewports, dialogs in CASES
    for viewport in viewports
]


@pytest.mark.parametrize("name, viewport, dialogs", PARAMS)
def test_R28_each_after_load_script_leaves_its_state_with_nothing_focused(browser, engine, name, viewport, dialogs):
    context, page = harness_page(browser, viewport, [script("seed-sample.js"), NAVIGATOR_STANDIN])
    try:
        assert page.locator("ul.rows > li.row").count() == 3, "the seed did not give the app the three sample habits"
        assert page.evaluate(STANDIN_IN_PLACE_JS), "Clipboard.prototype.writeText is native before the after-load script"
        assert open_dialogs(page) == {}, "a dialog is open before the after-load script"

        error = None
        try:
            run_after_load(page, script(name))
        except Exception as caught:  # Playwright's Error carries the script's own message
            error = str(caught)
        assert error is None, f"{name} threw on a page where its state can be reached, {error}"

        shown = open_dialogs(page)
        assert set(shown) == dialogs, f"{name} left {sorted(shown)} open, the table names {sorted(dialogs)}"
        for entry in shown.values():
            if entry["scrollTop"] is not None and entry["name"] in ("dlg-ov", "dlg-all", "dlg-year"):
                if entry["name"] == "dlg-ov" and "dlg-all" in shown:
                    continue  # the table names P4's scroll only, P3 lies under it
                assert entry["scrollTop"] == 0, f"{entry['name']}'s div.sheet-body is at scrollTop {entry['scrollTop']}"
        if name == "open-day-editor.js":
            assert page.locator("#day-title").text_content() == "Tuesday 22 September"
            host = "dialog.dlg-ov div.ovg-rows" if viewport != DESKTOP else "section.band div.ovg-cols"
            marked = page.locator(f"{host} button.hc.is-open").evaluate_all("(nodes) => nodes.map((n) => n.dataset.key)")
            assert marked == [SEPT_22], f"the marked day of {host} is {marked}, not {SEPT_22}"
        if name == "open-year-view.js":
            assert page.locator("#yr-title").text_content() == "Read 20 pages"
        if name == "open-delete-dialog.js":
            assert shown["dlg-del"]["modal"], "M1 is open but not :modal"
            assert page.locator("#del-title").text_content() == dialog_title(BIN_NAME)

        active = page.evaluate(ACTIVE_JS)
        write_evidence(f"fidelity-blur-{name[:-3]}-{viewport[0]}x{viewport[1]}", {"engine": engine, "activeElement": active})
        assert active == "body", f"after {name}'s blur() document.activeElement is {active}, not body"
        assert clipboard_markers(page) == [], "a clipboard marker was recorded"
    finally:
        context.close()


AFTER_LOAD = ["open-day-editor.js", "open-year-view.js", "open-overview.js", "open-overview-year.js", "open-delete-dialog.js"]
# A planted break for the throw check. showModal does nothing, so no script can reach its state.
DEAD_SHOWMODAL = "(() => { HTMLDialogElement.prototype.showModal = function () {}; })();"


@pytest.mark.parametrize("name", AFTER_LOAD)
def test_R28_each_after_load_script_throws_when_its_state_is_not_reached(browser, name):
    context, page = harness_page(browser, (390, 844), [script("seed-sample.js"), NAVIGATOR_STANDIN, DEAD_SHOWMODAL])
    try:
        assert page.evaluate(STANDIN_IN_PLACE_JS), "Clipboard.prototype.writeText is native before the after-load script"
        error = None
        try:
            run_after_load(page, script(name))
        except Exception as caught:  # Playwright's Error carries the script's own message
            error = str(caught)
        assert error is not None, f"{name} returned although no dialog opened"
        assert "fidelity:" in error, f"{name} failed by something other than its own state check, {error}"
        assert clipboard_markers(page) == [], "a clipboard marker was recorded"
    finally:
        context.close()


@pytest.mark.parametrize("name", AFTER_LOAD)
def test_R28_each_after_load_script_refuses_to_click_without_the_standin(browser, engine, name):
    seed = seed_statement("seed-sample.js")
    context, page = harness_page(browser, (390, 844), [seed, NAVIGATOR_STANDIN])
    try:
        has_clipboard = page.evaluate("() => Boolean(navigator.clipboard)")
        if engine != "chromium":
            # The fidelity gate never runs in WebKit, so this line only records what the engine has (qa.md).
            write_evidence(f"fidelity-control-{name[:-3]}", {"engine": engine, "navigator.clipboard": has_clipboard})
            return
        assert has_clipboard and not page.evaluate(STANDIN_IN_PLACE_JS), "the control page has the prototype stand-in"
        clicks = page.evaluate_handle(
            """() => {
              const seen = { count: 0 };
              document.addEventListener('click', () => { seen.count += 1; }, { capture: true });
              return seen;
            }"""
        )
        error = None
        try:
            run_after_load(page, script(name))
        except Exception as caught:
            error = str(caught)
        assert error is not None and "stand-in" in error, f"{name} did not refuse to click without the stand-in, {error}"
        assert clicks.evaluate("(seen) => seen.count") == 0, f"{name} clicked before it checked the stand-in"
        assert open_dialogs(page) == {}, f"{name} opened a dialog without the stand-in"
    finally:
        context.close()
