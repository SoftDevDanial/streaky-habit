"""R28: the two state scripts the plugin fidelity harness is given (app qa.md, Fidelity gate).

They are test-side files in tests/browser/fidelity/. These tests prove they do what the gate needs,
the same way the harness runs them: the seed as an init script, the after-load script as the body of an
async function.
"""
import json

from conftest import ROOT, SAMPLE_HABITS

FIDELITY_DIR = ROOT / "tests" / "browser" / "fidelity"
SEED_JS = (FIDELITY_DIR / "seed-sample.js").read_text(encoding="utf-8")
OPEN_DIALOG_JS = (FIDELITY_DIR / "open-delete-dialog.js").read_text(encoding="utf-8")
HARNESS_TIME = "2026-10-08T09:00:00+08:00"  # the harness gets 2026-10-08T09:00:00 local time


def test_R28_the_seed_script_writes_the_sample_and_nothing_else(browser):
    context = browser.new_context()
    try:
        page = context.new_page()
        page.goto("about:blank")  # no CSP here, so the script can be run through new Function
        calls = page.evaluate(
            """(source) => {
              const calls = [];
              new Function('localStorage', source)({ setItem: (key, value) => calls.push([key, value]) });
              return calls;
            }""",
            SEED_JS,
        )
    finally:
        context.close()

    assert len(calls) == 1
    key, text = calls[0]
    assert key == "streaks.state"
    assert json.loads(text) == {"version": 1, "habits": SAMPLE_HABITS}
    assert text == json.dumps({"version": 1, "habits": SAMPLE_HABITS}, separators=(",", ":"))


def test_R28_the_after_load_script_leaves_the_dialog_open_with_nothing_focused(app):
    page = app(init_script=SEED_JS, fixed_time=HARNESS_TIME)
    assert page.locator("li.habit").count() == 3
    assert page.locator("dialog.dialog").evaluate("(d) => d.open") is False

    page.evaluate(f"async () => {{ {OPEN_DIALOG_JS}\n }}")

    dialog = page.locator("dialog.dialog")
    assert dialog.evaluate("(d) => d.open && d.matches(':modal')") is True
    assert page.locator("#del-title").text_content() == 'Delete "Read 20 pages"?'
    assert page.evaluate("() => document.activeElement === document.body") is True
