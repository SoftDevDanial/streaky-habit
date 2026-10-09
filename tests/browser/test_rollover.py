"""R19, R20: the page moves to the new day while it is open or when the tab is shown again
(app qa.md, Rolling over midnight). Time moves only through Playwright's clock.
"""
from playwright.sync_api import expect

from conftest import (
    add_button,
    add_habit,
    cell,
    day,
    heat_cells,
    hide_tab,
    is_focused,
    pattern,
    pretty_sample_state,
    row,
    sample_state,
    show_tab,
    stored,
    streak,
    tab_until,
    type_name,
    write_count,
)

SAMPLE_NAMES = ["Read 20 pages", "Stretch 10 minutes", "No phone after 11pm"]
BEFORE_MIDNIGHT = "2026-10-08T23:59:30+08:00"


def week_dates(page, name):
    return row(page, name).locator("button.day").evaluate_all("(els) => els.map((e) => e.getAttribute('data-date'))")


def has_run_continues(page, name):
    return row(page, name).locator("div.strip").get_attribute("data-run-continues") is not None


def hold_heat_cells(page):
    """A handle to the 84 heat cell elements as they are now, to compare with after a new day."""
    return page.evaluate_handle("() => Array.from(document.querySelectorAll('.cells > span'))")


def assert_the_heat_cells_were_set_in_place(held):
    """JC2 and R8: the same 84 elements stand in the same places, so the dot transition runs."""
    assert held.evaluate(
        "(els) => els.length === 84 && els.every((el, place) => el.isConnected && el.parentElement.children[place] === el)"
    )


def assert_every_heat_cell_fits_its_day(page, today, future):
    """The cells are recycled, so each must have dropped what belonged to the role it had yesterday.

    A future cell is hidden and has no role, name or current mark. Every other cell is a named image that
    is not hidden. Only today's cell says it is the current date, and none says it twice.
    """
    for css, date, role, hidden, label, current in heat_cells(page):
        if date in future:
            assert (css, role, hidden, label, current) == ("hc future", None, "true", None, None), date
        else:
            assert (role, hidden, label is not None) == ("img", None, True), date
            assert current == ("date" if date == today else None), date


def assert_the_sample_on_friday(page, held_cells):
    """The state the first @R19 scenario and @R20 both end in: the sample, one day later.

    The page must have been opened with the indented sample and `count_writes=True`: a new day saves
    nothing (R16: saves happen "at no other time" than add, tick and delete). `held_cells` is
    `hold_heat_cells(page)` taken before the new day.
    """
    assert write_count(page) == 0
    assert stored(page) == pretty_sample_state()
    expect(page.locator("p.date time")).to_have_text("Friday 9 October")
    expect(page.locator("p.date time")).to_have_attribute("datetime", "2026-10-09")
    for name in SAMPLE_NAMES:
        assert week_dates(page, name) == [f"2026-10-0{n}" for n in range(3, 10)]
    current = page.locator("button.day[aria-current]")
    assert current.evaluate_all("(els) => els.map((e) => e.getAttribute('data-date'))") == ["2026-10-09"] * 3

    expected = [
        ("Read 20 pages", "D D D D D D .", "6 days", "Best 14", False),
        ("Stretch 10 minutes", "D . D D D . .", "No streak yet", "Best 9", True),
        ("No phone after 11pm", "D . . D . D .", "1 day", "Best 4", False),
    ]
    for name, strip, current_text, best, run in expected:
        assert pattern(page, name) == strip, name
        line = streak(page, name)
        assert (line["cur"], line["best"]) == (current_text, best), name
        assert has_run_continues(page, name) is run, name

    friday = cell(page, "2026-10-09")
    assert friday.get_attribute("class") == "hc l0 today"
    assert friday.get_attribute("aria-label") == "Fri 9 Oct, 0 of 3 habits"
    thursday = cell(page, "2026-10-08")
    assert thursday.get_attribute("class") == "hc l2"
    assert thursday.get_attribute("aria-label") == "Thu 8 Oct, 2 of 3 habits"
    assert [c[1] for c in heat_cells(page) if c[0] == "hc future"] == ["2026-10-10", "2026-10-11"]
    assert_every_heat_cell_fits_its_day(page, "2026-10-09", future=["2026-10-10", "2026-10-11"])
    assert_the_heat_cells_were_set_in_place(held_cells)


def test_R19_the_view_moves_to_the_new_day_within_a_minute_while_visible(app):
    page = app(storage=pretty_sample_state(), install_time="2026-10-08T23:59:00+08:00", count_writes=True)
    held_cells = hold_heat_cells(page)
    page.clock.pause_at(BEFORE_MIDNIGHT)

    page.clock.run_for(29000)
    expect(page.locator("p.date time")).to_have_text("Thursday 8 October")
    for name in SAMPLE_NAMES:
        assert week_dates(page, name)[-1] == "2026-10-08"

    page.clock.run_for(61000)
    assert_the_sample_on_friday(page, held_cells)


def test_R19_a_page_booted_ten_seconds_before_midnight_has_the_new_day_thirty_seconds_after_it(app):
    """Pins the cadence. The other tests boot so that some check lands in their window whatever the
    interval is. Here the page boots at about 23:59:50, so a check every 30 s runs at about 00:00:20, and a
    check every 45, 60 or 85 s runs after 00:00:30, which breaks "at most 60 seconds after midnight" too."""
    page = app(storage=pretty_sample_state(), install_time="2026-10-08T23:59:50+08:00", count_writes=True)
    held_cells = hold_heat_cells(page)
    page.clock.pause_at("2026-10-08T23:59:59+08:00")

    page.clock.run_for(900)  # 23:59:59.9, the new day must not show before midnight
    expect(page.locator("p.date time")).to_have_text("Thursday 8 October")
    for name in SAMPLE_NAMES:
        assert week_dates(page, name)[-1] == "2026-10-08"

    page.clock.run_for(30100)  # 00:00:30.0
    assert_the_sample_on_friday(page, held_cells)


def test_R19_the_heatmap_shifts_when_a_new_week_starts(app):
    page = app(storage=sample_state(), install_time="2026-10-11T23:59:30+08:00")
    held_cells = hold_heat_cells(page)
    page.clock.run_for(90000)

    cells = heat_cells(page)
    assert cells[0][1] == "2026-07-27" and cells[-1][1] == "2026-10-18"
    # Sunday had no future cell, so six cells that were named images become future ones here.
    assert_every_heat_cell_fits_its_day(page, "2026-10-12", future=[f"2026-10-{n}" for n in range(13, 19)])
    assert_the_heat_cells_were_set_in_place(held_cells)
    assert page.locator("div.months span").evaluate_all(
        "(els) => els.map((e) => [e.textContent, e.style.gridColumn])"
    ) == [["Jul", "1"], ["Aug", "2"], ["Sep", "7"], ["Oct", "11"]]
    assert [c[1] for c in cells if c[0] == "hc future"] == [f"2026-10-{n}" for n in range(13, 19)]
    monday = cell(page, "2026-10-12")
    assert monday.get_attribute("aria-label") == "Mon 12 Oct, 0 of 3 habits"
    assert "today" in monday.get_attribute("class").split()
    for name in SAMPLE_NAMES:
        assert week_dates(page, name) == [f"2026-10-{n:02d}" for n in range(6, 13)]
    lines = [streak(page, name) for name in SAMPLE_NAMES]
    assert [(line["cur"], line["best"]) for line in lines] == [
        ("No streak yet", "Best 14"), ("No streak yet", "Best 9"), ("No streak yet", "Best 4")
    ]


def test_R19_the_add_form_and_its_focus_survive_the_rollover(app):
    page = app(storage=sample_state(), install_time=BEFORE_MIDNIGHT)
    type_name(page, "Drink")
    page.clock.run_for(90000)

    expect(page.locator("p.date time")).to_have_text("Friday 9 October")
    expect(page.locator("#new-habit")).to_have_value("Drink")
    assert is_focused(page.locator("#new-habit"))


def test_R19_an_error_message_survives_the_rollover(app):
    page = app(storage=sample_state(), install_time=BEFORE_MIDNIGHT)
    add_button(page).click()
    expect(page.locator("#new-habit-msg")).to_have_text("Name the habit first.")
    page.clock.run_for(90000)

    expect(page.locator("p.date time")).to_have_text("Friday 9 October")
    expect(page.locator("#new-habit-msg")).to_have_text("Name the habit first.")
    expect(page.locator("#new-habit")).to_have_attribute("aria-invalid", "true")


def test_R19_focus_on_todays_bead_stays_on_todays_bead(app):
    page = app(storage=sample_state(), install_time=BEFORE_MIDNIGHT)
    tab_until(page, day(page, "Read 20 pages", "2026-10-08"))
    page.clock.run_for(90000)

    expect(page.locator("p.date time")).to_have_text("Friday 9 October")
    focused = page.locator("button.day:focus")
    assert focused.count() == 1
    assert focused.get_attribute("aria-label") == "Mark Fri 9 Oct as done"
    assert focused.get_attribute("aria-current") == "date"
    assert is_focused(row(page, "Read 20 pages").locator("button.day").nth(6))


def test_R19_a_habit_added_before_the_rollover_rolls_over_too(app):
    page = app(install_time=BEFORE_MIDNIGHT)
    add_habit(page, "Drink water")
    page.clock.run_for(90000)

    expect(page.locator("p.date time")).to_have_text("Friday 9 October")
    assert week_dates(page, "Drink water") == [f"2026-10-0{n}" for n in range(3, 10)]
    assert cell(page, "2026-10-09").get_attribute("aria-label") == "Fri 9 Oct, 0 of 1 habits"


def test_R20_the_view_moves_at_once_when_the_tab_is_shown_again(app):
    page = app(storage=pretty_sample_state(), install_time="2026-10-08T23:58:00+08:00", count_writes=True)
    held_cells = hold_heat_cells(page)
    page.clock.pause_at("2026-10-08T23:59:00+08:00")
    hide_tab(page)
    page.clock.set_system_time("2026-10-09T07:30:00+08:00")
    expect(page.locator("p.date time")).to_have_text("Thursday 8 October")

    show_tab(page)
    assert_the_sample_on_friday(page, held_cells)
