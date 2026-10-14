"""R38 and R40: the overview popup P3 on a phone (app qa.md, Feature "The overview popup and the year of all habits").

Each test opens the running app on the sample day and drives the Overview button with real gestures. Task 20 adds the
scenarios of P4 to this file.
"""
import datetime

import pytest
from playwright.sync_api import expect

from conftest import (
    ARCS3,
    CORE,
    TODAY,
    TODAY_CIRCLE,
    grid_children,
    legend_parts,
    ring_of,
    ring_parts,
    sample_state,
    seg,
    short_date,
)

PHONE = (390, 844)

OVERVIEW_HEAD_JS = """() => {
  const head = document.querySelector('dialog.dlg-ov div.ov-head');
  const named = (node) => [[node.localName, ...node.classList].join('.'), node.id || null,
    node.getAttribute('aria-label'), node.children.length && node.localName !== 'button' ? null : node.textContent];
  return Array.from(head.querySelectorAll('h2, p, button')).map(named);
}"""

GRID_ATTRS_JS = """() => { const grid = document.querySelector('dialog.dlg-ov div.ovg-rows');
  return [grid.getAttribute('role'), grid.getAttribute('aria-labelledby'), grid.childElementCount,
    grid.nextElementSibling && [grid.nextElementSibling.className, grid.nextElementSibling.getAttribute('aria-hidden')]]; }"""


def day_keys(first, count):
    start = datetime.date.fromisoformat(first)
    return [(start + datetime.timedelta(days=i)).isoformat() for i in range(count)]


def test_R38_R42_the_overview_button_opens_p3(app):
    page = app(viewport=PHONE, storage=sample_state())
    button = page.locator("button.ov-btn")
    expect(button).to_have_attribute("type", "button")
    expect(button).to_have_attribute("aria-haspopup", "dialog")
    expect(button).to_have_attribute("aria-label", "Overview, today 1 of 3 habits done")
    expect(button).to_have_text("Overview")
    expect(button.locator(":scope > span.ov-ring")).to_have_attribute("aria-hidden", "true")
    ring_box = button.locator(":scope > span.ov-ring > svg").bounding_box()
    assert (ring_box["width"], ring_box["height"]) == (28, 28)
    assert ring_parts(page, "button.ov-btn > span.ov-ring > svg") == ring_of(
        [seg(ARCS3[0], True), seg(ARCS3[1], False), seg(ARCS3[2], False)]
    )

    button.click()
    dialog = page.locator("dialog.dlg-ov")
    expect(dialog).to_have_attribute("open", "")
    assert dialog.evaluate("(d) => d.matches(':modal')") is True
    expect(dialog.get_by_role("button", name="Close", exact=True)).to_be_focused()
    assert dialog.locator("div.sheet-body").evaluate("(body) => body.scrollTop") == 0

    assert page.evaluate(OVERVIEW_HEAD_JS) == [
        ["h2", "ov-title", None, "Last 12 weeks"],
        ["p.hint", None, None, "Tap a day to change it."],
        ["button.btn-all", None, "Year view, all habits", "Year"],
        ["button.icon-btn", None, "Close", ""],
    ]
    assert page.evaluate(GRID_ATTRS_JS) == ["group", "ov-title", 104, ["legend", "true"]]

    grid = grid_children(page, "dialog.dlg-ov div.ovg-rows")
    assert grid[0]["tag"] == "div" and grid[0]["hidden"] == "true" and grid[0]["text"] == "" and grid[0]["cls"] is None
    assert [(cell["cls"], cell["hidden"], cell["text"]) for cell in grid[1:8]] == [("og-wd", "true", letter) for letter in "MTWTFSS"]
    rows = [grid[8 + 8 * week: 16 + 8 * week] for week in range(12)]
    assert [(r[0]["tag"], r[0]["cls"], r[0]["hidden"]) for r in rows] == [("div", "og-mo", "true")] * 12
    assert [r[0]["text"] for r in rows] == ["Oct", "", "", "", "Sep", "", "", "", "", "Aug", "", "Jul"]

    first, last = rows[0][1:], rows[11][1:]
    assert [cell["key"] for cell in first[:6]] == day_keys("2026-10-05", 6)
    assert (first[6]["tag"], first[6]["cls"], first[6]["hidden"], first[6]["ring"]) == ("span", "hc", "true", None)
    assert [cell["key"] for cell in last] == day_keys("2026-07-20", 7)

    buttons = [cell for r in rows for cell in r[1:] if cell["tag"] == "button"]
    assert len(buttons) == 83
    band = {cell["key"]: cell for cell in grid_children(page, "section.band div.ovg-cols") if cell["tag"] == "button"}
    for cell in buttons:
        twin = band[cell["key"]]
        assert (cell["cls"], cell["type"], cell["popup"], cell["label"], cell["current"], cell["ring"]) == (
            twin["cls"], twin["type"], twin["popup"], twin["label"], twin["current"], twin["ring"]
        ), cell["key"]
        assert cell["label"].startswith(short_date(cell["key"]) + ", ")
    today = next(cell for cell in buttons if cell["key"] == TODAY)
    assert today["current"] == "date" and today["ring"]["parts"][0] == TODAY_CIRCLE
    assert [cell["key"] for cell in buttons if cell["current"]] == [TODAY]

    legend = legend_parts(page, "dialog.dlg-ov div.sheet-body > div.legend")
    assert legend == [
        "span:None",
        ring_of([seg(ARCS3[0], False), seg(ARCS3[1], False), seg(ARCS3[2], False)]),
        ring_of([seg(ARCS3[0], True), seg(ARCS3[1], False), seg(ARCS3[2], False)]),
        ring_of([seg(ARCS3[0], True), seg(ARCS3[1], True), seg(ARCS3[2], False)]),
        ring_of([seg(ARCS3[0], True), seg(ARCS3[1], True), seg(ARCS3[2], True), CORE]),
        "span:All",
    ]


@pytest.mark.parametrize("action", ["clicks Close", "presses Escape"])
def test_R38_R40_p3_closes_and_gives_focus_back_to_overview(app, action):
    page = app(viewport=PHONE, storage=sample_state())
    page.locator("button.ov-btn").click()
    dialog = page.locator("dialog.dlg-ov")
    expect(dialog).to_have_attribute("open", "")
    if action == "clicks Close":
        dialog.get_by_role("button", name="Close", exact=True).click()
    else:
        page.keyboard.press("Escape")
    page.wait_for_function("() => !document.querySelector('dialog.dlg-ov').open", timeout=5000)
    expect(page.locator("button.ov-btn")).to_be_focused()


def test_R38_R22_p3_cannot_be_reached_on_a_desktop(app):
    page = app(viewport=(1280, 800), storage=sample_state())
    expect(page.locator("section.band div.ovg-cols > button.hc")).to_have_count(83)
    assert page.evaluate("() => document.activeElement === document.body") is True
    for press in range(1, 96):
        page.keyboard.press("Tab")
        found = page.evaluate(
            """() => ({ overview: document.activeElement === document.querySelector('button.ov-btn'),
                        open: document.querySelector('dialog.dlg-ov').open })"""
        )
        assert found == {"overview": False, "open": False}, f"after Tab {press}"
