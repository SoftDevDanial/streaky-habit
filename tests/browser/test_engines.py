"""R30: two engines (app qa.md, Feature "Two engines", the three scenarios of task 11 and the clipboard one of task 19).

Why: the browser suite and the live gate run once in Chromium and once in WebKit, so a run must use the
engine it was asked for, refuse any other before a browser starts, and launch every browser through
conftest's one helper. Every context that presses gets the clipboard stand-in, so no run reaches the system clipboard.
Input: the run's --engine option and the text of tests/browser/. Output: pass or fail.
Each test gathers every broken property before it fails, so one RED run shows all of them.
"""
import ast
import os
import pathlib
import subprocess
import sys

from playwright.sync_api import expect

import conftest
from conftest import LAUNCH_ARGS, ROOT, STANDIN_IN_PLACE_JS, done_btn, launch, record, sample_state, year_btn

BROWSER_TESTS = ROOT / "tests" / "browser"
COLLECT_ONLY_SECONDS = 60
# Built from parts so that this file does not hold the very text the scan below looks for.
LAUNCH_CALL = ".launch" + "("
NEVER_USED = ("launch_persistent" + "_context", "connect_over" + "_cdp", "is_" + "mobile")
GENERATED_DIRS = ("__pycache__", ".pytest_cache")  # written by Python and pytest, not source


def engine_on_command_line(config):
    return any(arg == "--engine" or arg.startswith("--engine=") for arg in config.invocation_params.args)


def test_R30_the_run_uses_the_engine_it_was_asked_for(browser, pytestconfig):
    asked = pytestconfig.getoption("--engine")
    problems = []
    if browser.browser_type.name != asked:
        problems.append(f"the session browser is {browser.browser_type.name}, the run asked for {asked}")
    if not engine_on_command_line(pytestconfig) and asked != "chromium":
        problems.append(f"with no --engine on the command line the run uses {asked}, not chromium")
    if os.environ.get("STREAKS_EVIDENCE_DIR"):
        folder = pathlib.PurePath(conftest.EVIDENCE_DIR).name
        if not folder.endswith("-" + asked):
            problems.append(f"the evidence folder {folder!r} does not end with -{asked}")
    assert not problems, problems


def test_R30_an_unknown_engine_is_refused_before_any_browser_starts(playwright):
    environment = dict(os.environ, STREAKS_BASE_URL=conftest.BASE_URL, STREAKS_SUBPATH_URL=conftest.SUBPATH_URL)
    run = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/browser", "--engine", "firefox", "--collect-only", "-q"],
        cwd=ROOT,
        env=environment,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=COLLECT_ONLY_SECONDS,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    problems = []
    if run.returncode != 4:
        problems.append(f"--engine firefox --collect-only exited {run.returncode}, not 4")
    if not ("chromium" in run.stderr and "webkit" in run.stderr):
        problems.append(f"its error output does not name the choices chromium and webkit: {run.stderr.strip()!r}")
    try:
        started = launch(playwright, "firefox")
    except ValueError:
        pass
    else:
        started.close()
        problems.append("launch(playwright, 'firefox') raised no ValueError")
    assert not problems, problems


def test_R30_one_helper_launches_every_browser():
    conftest_source = (BROWSER_TESTS / "conftest.py").read_text(encoding="utf-8")
    helper = next(
        node for node in ast.parse(conftest_source).body if isinstance(node, ast.FunctionDef) and node.name == "launch"
    )
    inside_helper = range(helper.lineno, helper.end_lineno + 1)
    problems = []
    for path in sorted(BROWSER_TESTS.rglob("*")):
        if not path.is_file() or any(part in GENERATED_DIRS for part in path.parts):
            continue
        name = path.relative_to(ROOT).as_posix()
        for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if LAUNCH_CALL in line and not (path.name == "conftest.py" and number in inside_helper):
                problems.append(f"{name} line {number} launches a browser outside conftest.launch")
            problems += [f"{name} line {number} uses {word}" for word in NEVER_USED if word in line]

    live_gate = ast.parse((BROWSER_TESTS / "live_e2e.py").read_text(encoding="utf-8"))
    if not any(
        isinstance(node, ast.ImportFrom) and node.module == "conftest" and any(alias.name == "launch" for alias in node.names)
        for node in ast.walk(live_gate)
    ):
        problems.append("live_e2e.py does not import launch from conftest")
    if LAUNCH_ARGS != {"chromium": ["--force-color-profile=srgb"], "webkit": []}:
        problems.append(f"LAUNCH_ARGS is {LAUNCH_ARGS}")
    assert not problems, problems


CLIPBOARD_MARK = "test:clipboard:"


def test_R30_every_context_has_the_clipboard_stand_in(app):
    page = app(storage=sample_state(), record=True)
    assert page.evaluate(STANDIN_IN_PLACE_JS) is True, "navigator.clipboard is the browser's own"

    done_btn(page, "Stretch 10 minutes").click()
    expect(done_btn(page, "Stretch 10 minutes")).to_have_attribute("aria-pressed", "true")
    year_btn(page, "Read 20 pages").click()
    dialog = page.locator("dialog.dlg-year")
    expect(dialog).to_have_attribute("open", "")
    dialog.get_by_role("button", name="Close", exact=True).click()
    page.wait_for_function("() => !document.querySelector('dialog.dlg-year').open", timeout=5000)

    page.evaluate("() => 0")  # a round trip, so every console message sent before it is in the log
    marks = [message["text"] for message in record(page).console if message["text"].startswith(CLIPBOARD_MARK)]
    assert marks == [], marks
