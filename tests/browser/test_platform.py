"""R21 to R26: phone width, keyboard, motion, names as text, requests, no seed and no hooks
(app qa.md: Platform, and the R26 scenarios of Shipped entry point).
"""
import os
from urllib.parse import urlsplit

import pytest
from playwright.sync_api import expect

from conftest import (
    BASE_URL,
    ROOT,
    SAMPLE_NAMES,
    add_button,
    add_habit,
    day,
    open_delete_dialog,
    record,
    sample_state,
    tab_until,
    trash,
)

SRC_DIR = ROOT / "src"
FOCUSED_NAME = "() => document.activeElement.getAttribute('aria-label') || document.activeElement.id || document.activeElement.textContent.trim()"
MARKUP_NAME = "<img src=x onerror=alert(1)>"


def src_text():
    """Every regular file under src/ (JavaScript, CSS or anything else) by path, because R24 and R26 say "every file".

    Decoded leniently so that a file that is not UTF-8 text is still scanned and cannot hide a sink.
    """
    return {
        path.relative_to(SRC_DIR).as_posix(): path.read_bytes().decode("utf-8", errors="replace")
        for path in sorted(SRC_DIR.rglob("*"))
        if path.is_file()
    }


# ---------------------------------------------------------------------------- R21


def test_R21_phone_width_360(app):
    page = app(storage=sample_state(), viewport=(360, 780))
    assert page.evaluate("() => document.documentElement.scrollWidth") <= 360
    widths = page.locator("button.day").evaluate_all("(els) => els.map((e) => e.getBoundingClientRect().width)")
    assert len(widths) == 21 and min(widths) >= 44
    icon_sizes = page.locator("button.icon-btn").evaluate_all(
        "(els) => els.map((e) => { const r = e.getBoundingClientRect(); return [r.width, r.height]; })"
    )
    assert icon_sizes == [[44, 44]] * 3
    assert page.locator("#new-habit").bounding_box()["height"] == 48
    assert add_button(page).bounding_box()["height"] == 48
    beads = page.locator("span.bead").evaluate_all(
        "(els) => els.map((e) => { const r = e.getBoundingClientRect(); return [r.width, r.height]; })"
    )
    assert beads == [[32, 32]] * 21


# ---------------------------------------------------------------------------- R22


def test_R22_tab_order(app):
    page = app(storage=sample_state())
    visited = []
    for _ in range(26):
        page.keyboard.press("Tab")
        visited.append(page.evaluate(FOCUSED_NAME))
    days = [f"Mark {label} as done" for label in ("Fri 2 Oct", "Sat 3 Oct", "Sun 4 Oct", "Mon 5 Oct", "Tue 6 Oct", "Wed 7 Oct", "Thu 8 Oct")]
    expected = []
    for name in SAMPLE_NAMES:
        expected += [f"Delete {name}"] + days
    assert visited == expected + ["new-habit", "Add"]


def test_R22_tab_order_with_the_note(app):
    page = app(storage="{")
    visited = []
    for _ in range(3):
        page.keyboard.press("Tab")
        visited.append(page.evaluate(FOCUSED_NAME))
    assert visited == ["Dismiss note", "new-habit", "Add"]


FOCUS_TARGETS = {
    "a day button": (lambda page: day(page, "Read 20 pages", "2026-10-02"), "0px"),
    "an icon button": (lambda page: trash(page, "Read 20 pages"), "-2px"),
    "the input": (lambda page: page.locator("#new-habit"), "2px"),
    "the Add button": (lambda page: add_button(page), "3px"),
}


@pytest.mark.parametrize("target", FOCUS_TARGETS)
def test_R22_focus_rings_on_keyboard_focus(app, target):
    page = app(storage=sample_state())
    locate, offset = FOCUS_TARGETS[target]
    tab_until(page, locate(page))
    outline = locate(page).evaluate("(e) => [getComputedStyle(e).outline, getComputedStyle(e).outlineOffset]")
    assert outline == ["rgb(28, 37, 35) solid 2px", offset]


def test_R22_a_mouse_click_draws_no_ring(app):
    page = app(storage=sample_state())
    button = day(page, "Read 20 pages", "2026-10-05")
    button.click()
    assert button.evaluate("(e) => e.matches(':focus-visible')") is False
    assert button.evaluate("(e) => getComputedStyle(e).outlineStyle") == "none"


# ---------------------------------------------------------------------------- R23


def test_R23_motion_without_reduced_motion(app):
    page = app(storage=sample_state(), reduced_motion="no-preference")
    durations = page.locator("span.bead").evaluate_all("(els) => els.map((e) => getComputedStyle(e).transitionDuration)")
    assert set(durations) == {"0.18s, 0.18s, 0.12s"}
    open_delete_dialog(page, "Read 20 pages")
    assert page.locator("dialog.dialog").evaluate("(e) => getComputedStyle(e).animationName") == "dialog-in"
    assert page.locator("dialog.dialog").evaluate("(e) => getComputedStyle(e, '::backdrop').animationName") == "scrim-in"


def test_R23_everything_appears_at_once_under_reduced_motion(app):
    page = app(storage=sample_state(), reduced_motion="reduce")
    beads = page.locator("span.bead").evaluate_all("(els) => els.map((e) => getComputedStyle(e).transitionDuration)")
    dots = page.locator(".cells .hc").evaluate_all("(els) => els.map((e) => getComputedStyle(e, '::before').transitionDuration)")
    assert set(beads) == {"0s"} and set(dots) == {"0s"}
    open_delete_dialog(page, "Read 20 pages")
    dialog = page.locator("dialog.dialog")
    assert dialog.evaluate("(e) => getComputedStyle(e).animationName") == "none"
    assert dialog.evaluate("(e) => getComputedStyle(e, '::backdrop').animationName") == "none"


# ---------------------------------------------------------------------------- R24


def test_R24_markup_in_a_name_stays_text(app):
    page = app(record=True)
    dialogs = []
    page.on("dialog", lambda opened: (dialogs.append(opened.message), opened.dismiss()))
    add_habit(page, MARKUP_NAME)

    heading = page.locator("#h1-name")
    assert heading.text_content() == MARKUP_NAME
    assert heading.evaluate("(e) => e.children.length") == 0
    assert page.locator("img").count() == 0
    expect(trash(page, MARKUP_NAME)).to_have_count(1)

    trash(page, MARKUP_NAME).click()
    title = page.locator("#del-title")
    assert title.text_content() == f'Delete "{MARKUP_NAME}"?'
    assert title.evaluate("(e) => e.children.length") == 0
    page.wait_for_timeout(200)
    assert dialogs == []
    assert record(page).errors == []


def test_R24_R26_the_source_scan_reads_every_file_under_src():
    """Guards the scans themselves: a scan that skips the stylesheet or a nested file proves nothing about it."""
    on_disk = {
        os.path.relpath(os.path.join(folder, name), SRC_DIR).replace(os.sep, "/")
        for folder, _, names in os.walk(SRC_DIR)
        for name in names
    }
    assert set(src_text()) == on_disk
    assert {"app.js", "styles.css"} <= on_disk


def test_R24_no_html_sinks_in_the_source():
    for name, text in src_text().items():
        for sink in ("innerHTML", "outerHTML", "insertAdjacentHTML", "document.write", "eval(", "new Function"):
            assert sink not in text, f"{name} uses {sink}"


# ---------------------------------------------------------------------------- R25


def test_R25_every_request_stays_on_the_devices_own_files(app):
    page = app(storage=sample_state(), record=True)
    day(page, "Stretch 10 minutes", "2026-10-08").click()
    add_habit(page, "Drink water")
    open_delete_dialog(page, "Read 20 pages")
    page.get_by_role("button", name="Delete habit", exact=True).click()
    expect(page.locator("li.habit")).to_have_count(3)
    page.reload()
    expect(page.locator("li.habit")).to_have_count(3)

    log = record(page)
    origin = "{0.scheme}://{0.netloc}".format(urlsplit(BASE_URL))
    allowed = {"/", "/index.html", "/favicon.ico", "/src/styles.css"} | {f"/src/{name}" for name in src_text() if name.endswith(".js")}
    assert log.requests, "the page made requests"
    for request in log.requests:
        assert request["method"] == "GET", request
        assert request["origin"] == origin, request
        assert request["query"] == "", request
        assert request["path"] in allowed, request
    assert [m for m in log.console if m["type"] == "error"] == []
    assert log.errors == []


def test_R25_the_csp_is_in_force(app):
    page = app(storage=sample_state(), record=True)
    outcome = page.evaluate("() => fetch('https://example.com/').then(() => 'resolved', () => 'rejected')")
    assert outcome == "rejected"
    page.wait_for_timeout(200)
    violations = [m["text"] for m in record(page).console if "Content Security Policy" in m["text"]]
    assert any("connect-src" in text for text in violations), violations


# ---------------------------------------------------------------------------- R26


def test_R26_no_sample_data_in_the_shipped_files():
    shipped = {"index.html": (ROOT / "index.html").read_text(encoding="utf-8"), **src_text()}
    for name, text in shipped.items():
        for forbidden in (*SAMPLE_NAMES, "sample-history"):
            assert forbidden not in text, f"{name} contains {forbidden}"


@pytest.mark.parametrize("path", ["?demo=1", "?seed", "#sample"])
def test_R26_query_strings_and_fragments_do_not_seed(app, path):
    page = app(path=path)
    assert page.locator("p.empty").count() == 1
    assert page.locator("li.habit").count() == 0
    assert page.evaluate("() => localStorage.getItem('streaks.state')") is None


def test_R26_no_globals_and_no_hooks(app):
    page = app(storage=sample_state())
    names = "() => Object.getOwnPropertyNames(window)"
    app_names = set(page.evaluate(names))
    page.goto(BASE_URL + "__seed__")
    plain_names = set(page.evaluate(names))
    assert app_names - plain_names == set()
