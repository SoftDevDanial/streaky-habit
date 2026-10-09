"""First screen, header, rows, streak lines, strips, heatmap, the 12-habit state at load, loading writes
nothing (app qa.md: First visit and header, Habit rows streak lines and strips, 12-week heatmap).
"""
import re

import pytest
from playwright.sync_api import expect

from conftest import (
    SAMPLE_HABITS,
    SAMPLE_LEVELS,
    add_days,
    canonical_pair,
    cell,
    heat_cells,
    long_date,
    pattern,
    plain_state,
    pretty_sample_state,
    row,
    sample_state,
    shot,
    short_date,
    streak,
    stored,
    write_count,
)

SAMPLE_NAMES = ["Read 20 pages", "Stretch 10 minutes", "No phone after 11pm"]
WEEK = ["2026-10-02", "2026-10-03", "2026-10-04", "2026-10-05", "2026-10-06", "2026-10-07", "2026-10-08"]


def test_R3_the_empty_first_screen(app):
    page = app()
    shot(page, "01-first-visit")

    empty = page.locator("section[aria-labelledby='habits-title'] > p.empty")
    expect(empty.locator("strong")).to_have_text("No habits yet.")
    assert empty.text_content() == "No habits yet. Add one you want to do every day."
    assert page.locator("ul.habits").count() == 0
    assert page.locator("div.note").count() == 0

    field = page.locator("#new-habit")
    expect(field).to_be_enabled()
    expect(field).to_have_value("")
    expect(page.locator(".add .btn")).to_be_enabled()
    expect(page.locator("#new-habit-msg")).to_have_text("")
    expect(page.locator("#new-habit-msg")).to_have_class("field-msg field-error")
    assert field.get_attribute("aria-invalid") is None

    cells = heat_cells(page)
    assert len(cells) == 84
    for position, (css, date, role, hidden, label, current) in enumerate(cells):
        assert date == add_days("2026-07-20", position)
        if date <= "2026-10-08":
            assert css.split()[:2] == ["hc", "l0"], date
            assert role == "img" and hidden is None, date
        else:
            assert (css, hidden, role, label) == ("hc future", "true", None, None), date
    assert cells[0][4] == "Mon 20 Jul, 0 of 0 habits"
    today = cell(page, "2026-10-08")
    expect(today).to_have_attribute("aria-label", "Thu 8 Oct, 0 of 0 habits")
    expect(today).to_have_class("hc l0 today")
    expect(today).to_have_attribute("aria-current", "date")
    assert [position for position, c in enumerate(cells) if c[5] == "date"] == [81 - 1]
    assert stored(page) is None


def test_R4_brand_and_date(app):
    page = app(storage=sample_state())
    shot(page, "02-sample-day")
    expect(page.locator("h1.brand")).to_have_text("Streaks")
    expect(page.locator("p.date time")).to_have_attribute("datetime", "2026-10-08")
    expect(page.locator("p.date time")).to_have_text("Thursday 8 October")


@pytest.mark.parametrize(
    "instant, key, text",
    [
        ("2026-10-05T09:00:00+08:00", "2026-10-05", "Monday 5 October"),
        ("2026-10-07T23:59:59+08:00", "2026-10-07", "Wednesday 7 October"),
        ("2027-01-01T00:00:30+08:00", "2027-01-01", "Friday 1 January"),
    ],
)
def test_R4_the_date_follows_the_device_clock(app, instant, key, text):
    page = app(fixed_time=instant)
    expect(page.locator("p.date time")).to_have_attribute("datetime", key)
    expect(page.locator("p.date time")).to_have_text(text)
    assert text == long_date(key)


def test_R4_english_under_a_german_browser_locale(app):
    page = app(storage=sample_state(), locale="de-DE")
    assert page.evaluate("() => navigator.language") == "de-DE"
    expect(page.locator("p.date time")).to_have_text("Thursday 8 October")
    expect(row(page, "Read 20 pages").locator("button.day").first).to_have_attribute(
        "aria-label", "Mark Fri 2 Oct as done"
    )
    expect(page.locator(".cells .hc").first).to_have_attribute("aria-label", "Mon 20 Jul, 3 of 3 habits")
    assert page.locator(".months span").all_inner_texts() == ["Jul", "Aug", "Sep", "Oct"]


def test_R5_rows_in_stored_order(app):
    page = app(storage=sample_state())
    items = page.locator("ul.habits > li.habit")
    assert items.count() == 3
    for index, name in enumerate(SAMPLE_NAMES):
        item = items.nth(index)
        heading = item.locator("h3.habit-name")
        expect(heading).to_have_text(name)
        expect(heading).to_have_id(f"h{index + 1}-name")
        trash = item.locator(".habit-head > button.icon-btn")
        expect(trash).to_have_attribute("aria-label", f"Delete {name}")
        assert trash.locator("use").get_attribute("href") == "#i-trash"
        strip = item.locator("div.strip")
        expect(strip).to_have_attribute("role", "group")
        expect(strip).to_have_attribute("aria-labelledby", f"h{index + 1}-name")


@pytest.mark.parametrize("name, current, best", [
    ("Read 20 pages", "6 days", "Best 14"),
    ("Stretch 10 minutes", "3 days", "Best 9"),
    ("No phone after 11pm", "1 day", "Best 4"),
])
def test_R6_the_samples_streak_lines(app, name, current, best):
    page = app(storage=sample_state())
    expect(row(page, name).locator("p.streak")).to_have_attribute("aria-live", "polite")
    assert streak(page, name) == {"cur": current, "cur_class": "cur", "best": best, "children": 2}


def test_R6_no_streak_yet_with_a_best(app):
    page = app(storage=sample_state(), fixed_time="2026-10-12T12:00:00+08:00")
    for name, best in zip(SAMPLE_NAMES, ["Best 14", "Best 9", "Best 4"]):
        assert streak(page, name) == {"cur": "No streak yet", "cur_class": "cur none", "best": best, "children": 2}


@pytest.mark.parametrize("name, expected, run_continues", [
    ("Read 20 pages", ". D D D D D D", False),
    ("Stretch 10 minutes", "D D . D D D .", True),
    ("No phone after 11pm", ". D . . D . D", False),
])
def test_R7_the_samples_week_strips(app, name, expected, run_continues):
    page = app(storage=sample_state())
    buttons = row(page, name).locator("div.strip > button.day")
    assert buttons.count() == 7
    assert buttons.evaluate_all("(els) => els.map((e) => e.getAttribute('type'))") == ["button"] * 7
    assert buttons.evaluate_all("(els) => els.map((e) => e.getAttribute('data-date'))") == WEEK
    assert buttons.locator(".wd").all_inner_texts() == ["Fri", "Sat", "Sun", "Mon", "Tue", "Wed", "Thu"]
    assert buttons.locator(".dm").all_inner_texts() == ["2", "3", "4", "5", "6", "7", "8"]
    assert pattern(page, name) == expected
    has_attribute = row(page, name).locator("div.strip").get_attribute("data-run-continues") is not None
    assert has_attribute is run_continues


def test_R7_day_names_today_and_nothing_outside_the_window(app):
    page = app(storage=sample_state())
    names = [f"Mark {short_date(key)} as done" for key in WEEK]
    for name in SAMPLE_NAMES:
        labels = row(page, name).locator("button.day").evaluate_all("(els) => els.map((e) => e.getAttribute('aria-label'))")
        assert labels == names
    assert names[0] == "Mark Fri 2 Oct as done" and names[-1] == "Mark Thu 8 Oct as done"

    current = page.locator("button.day[aria-current]")
    assert current.evaluate_all("(els) => els.map((e) => [e.getAttribute('data-date'), e.getAttribute('aria-current')])") == [
        ["2026-10-08", "date"]
    ] * 3
    dates = page.locator("button[data-date]").evaluate_all("(els) => els.map((e) => e.getAttribute('data-date'))")
    assert dates and all("2026-10-02" <= date <= "2026-10-08" for date in dates)


def test_R9_the_samples_heatmap(app):
    page = app(storage=sample_state())
    expect(page.locator("h2.heat-title")).to_have_text("Last 12 weeks")

    months = page.locator("div.months")
    expect(months).to_have_attribute("aria-hidden", "true")
    assert months.locator("span").evaluate_all("(els) => els.map((e) => [e.textContent, e.style.gridColumn])") == [
        ["Jul", "1"], ["Aug", "3"], ["Sep", "8"], ["Oct", "12"]
    ]
    weekdays = page.locator("div.wdays")
    expect(weekdays).to_have_attribute("aria-hidden", "true")
    assert weekdays.locator("span").all_inner_texts() == ["Mon", "", "Wed", "", "Fri", "", "Sun"]

    cells = heat_cells(page)
    assert [c[1] for c in cells] == [add_days("2026-07-20", n) for n in range(84)]
    assert len(SAMPLE_LEVELS) == 81
    for css, date, role, hidden, label, current in cells:
        if date in SAMPLE_LEVELS:
            count = sum(date in habit["done"] for habit in SAMPLE_HABITS)
            assert css.split()[:2] == ["hc", f"l{SAMPLE_LEVELS[date]}"], date
            assert (role, hidden) == ("img", None), date
            assert label == f"{short_date(date)}, {count} of 3 habits", date
            assert (css.split()[2:], current) == (
                (["today"], "date") if date == "2026-10-08" else ([], None)
            ), date
        else:
            assert (css, hidden, role, label, current) == ("hc future", "true", None, None, None), date
    assert [c[1] for c in cells if c[0] == "hc future"] == ["2026-10-09", "2026-10-10", "2026-10-11"]
    assert cell(page, "2026-10-08").get_attribute("aria-label") == "Thu 8 Oct, 2 of 3 habits"

    legend = page.locator("div.legend")
    expect(legend).to_have_attribute("aria-hidden", "true")
    assert legend.evaluate("(e) => Array.from(e.children).map((c) => [c.className, c.textContent])") == [
        ["", "None"], ["hc l0", ""], ["hc l1", ""], ["hc l2", ""], ["hc l3", ""], ["hc l4", ""], ["", "All"]
    ]


def test_R9_a_monday_shows_six_future_cells_and_a_shifted_grid(app):
    page = app(fixed_time="2026-10-12T12:00:00+08:00")
    cells = heat_cells(page)
    assert [c[1] for c in cells] == [add_days("2026-07-27", n) for n in range(84)]
    assert cells[0][1] == "2026-07-27" and cells[-1][1] == "2026-10-18"
    assert page.locator("div.months span").evaluate_all(
        "(els) => els.map((e) => [e.textContent, e.style.gridColumn])"
    ) == [["Jul", "1"], ["Aug", "2"], ["Sep", "7"], ["Oct", "11"]]
    assert [c[1] for c in cells if c[0] == "hc future"] == [add_days("2026-10-12", n) for n in range(1, 7)]
    today = cell(page, "2026-10-12")
    expect(today).to_have_attribute("aria-label", "Mon 12 Oct, 0 of 0 habits")
    assert "today" in today.get_attribute("class").split()


def test_R12_twelve_habits_at_load(app):
    page = app(storage=plain_state(12))
    expect(page.locator("#new-habit")).to_be_disabled()
    expect(page.locator(".add .btn")).to_be_disabled()
    message = page.locator("#new-habit-msg")
    expect(message).to_have_text("You track 12 habits, the most this app holds. Delete one to add another.")
    expect(message).to_have_class("field-msg field-note")
    expect(page.locator("#new-habit")).to_have_attribute("aria-describedby", "new-habit-msg")
    assert page.locator("li.habit").count() == 12


def test_R16_loading_writes_nothing(app):
    pretty = pretty_sample_state()
    page = app(storage=pretty, count_writes=True)
    expect(row(page, "Read 20 pages")).to_be_visible()
    page.wait_for_timeout(2000)
    assert write_count(page) == 0
    assert stored(page) == pretty


def test_R28_the_rendered_page_has_the_markup_of_the_goldens(app):
    """Beyond the qa.md scenarios: the page's DOM equals today.html and today-empty.html, attribute for attribute.

    That covers the sprite too (today.html has i-check and i-trash, the app adds i-x, which is checked
    against states.html). The open dialog is compared in test_delete.
    """
    sample_page = app(storage=sample_state())
    live, golden = canonical_pair(sample_page, "today.html", ".page")
    assert live == golden
    live, golden = canonical_pair(sample_page, "today.html", "body > svg", ignore=["symbol#i-x"])
    assert live == golden
    live, golden = canonical_pair(sample_page, "states.html", "symbol#i-x")
    assert live == golden

    fresh_page = app()
    live, golden = canonical_pair(fresh_page, "today-empty.html", ".page")
    assert live == golden


SVG_NAMESPACE = "http://www.w3.org/2000/svg"
EVERY_SVG_AND_USE = """() => Array.from(document.querySelectorAll('svg, use')).map((node) => ({
  tag: node.localName,
  namespace: node.namespaceURI,
  // an HTML element named "use" has no getBBox; a use whose symbol is missing has no width
  drawn: node.localName !== 'use' || (typeof node.getBBox === 'function' && node.getBBox().width > 0),
}))"""


@pytest.mark.parametrize("storage, expected_uses", [(sample_state(), 3 + 21), ("{", 1)], ids=["habit rows", "the note"])
def test_R5_every_svg_and_use_is_in_the_svg_namespace_and_draws(app, storage, expected_uses):
    """Contracts: an svg made with createElement is an HTML element and does not render, so every icon would vanish."""
    page = app(storage=storage)
    found = page.evaluate(EVERY_SVG_AND_USE)
    assert sum(item["tag"] == "use" for item in found) == expected_uses
    assert {item["namespace"] for item in found} == {SVG_NAMESPACE}
    assert all(item["drawn"] for item in found)
