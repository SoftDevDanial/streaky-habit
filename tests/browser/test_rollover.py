"""R19 and R20, the rollover at local midnight while the page is open, and when the tab is shown again (app qa.md,
Feature "Rolling over midnight").

Each test installs the clock 30 seconds before the instant it pauses at, opens the page and pauses there
(`page.clock.pause_at`), so no wall time passes before the clock runs (the Feature's header). The cadence test boots
nine seconds before its pause instead, because the boot instant is what it measures from. `run_for` then fires the
app's 30 second check past midnight, and the redraw is done when it returns, because the app draws inside that handler
(spec Invariants). Under a paused clock a locator click can wait forever on animation frames, so presses are keys or raw
mouse clicks at measured points, each checked to land on its control, and every read is an `evaluate` or an `expect`.
A focus check after a popup closes reads focus only after the popup's close event (conftest `watch_close`).
"""
import datetime
import time

import pytest
from playwright.sync_api import expect

from conftest import (
    TODAY,
    TODAY_CIRCLE,
    band_day,
    bead,
    best_block,
    current_block,
    done_btn,
    grid_children,
    hide_tab,
    p3_day,
    p4_day,
    row_numbers,
    sample_state,
    show_tab,
    stats_tree,
    stored,
    tab_to,
    tick,
    wait_for_close,
    watch_close,
    write_count,
    year_btn,
)

PHONE = (390, 844)
DESKTOP = (1280, 800)
SATURDAY_2359 = "2026-10-10T23:59:00+08:00"  # a minute before the sample's day ends
SUNDAY_2359 = "2026-10-11T23:59:00+08:00"  # a minute before a new week starts on Monday 12 October
PAST_MIDNIGHT_MS = 90_000  # from 30 seconds before midnight to a minute after it, so two 30 second checks fall after it
NAMES = ["Read 20 pages", "Stretch 10 minutes", "No phone after 11pm"]
SEP_22 = "2026-09-22"
YEAR_START = "2025-10-10"  # the oldest day of the year on Saturday 10 October 2026, gone from it on Sunday
BAND = "section.band div.ovg-cols"
P3_GRID = "dialog.dlg-ov div.ovg-rows"


def seconds_after(instant, seconds):
    return (datetime.datetime.fromisoformat(instant) + datetime.timedelta(seconds=seconds)).isoformat()


def open_paused(app, installed, **options):
    """The page on a clock installed at `installed`, opened and paused 30 seconds later (qa.md, this Feature)."""
    page = app(install_time=installed, **options)
    page.clock.pause_at(seconds_after(installed, 30))
    return page


def days(first, count):
    start = datetime.date.fromisoformat(first)
    return [(start + datetime.timedelta(days=n)).isoformat() for n in range(count)]


def weeks(page, selector):
    """A day grid's weeks in grid order, each as (its month label, its 7 cells), after the corner and the weekday
    letters (spec R35, R38)."""
    body = grid_children(page, selector)[8:]
    return [(body[n]["text"], body[n + 1:n + 8]) for n in range(0, len(body), 8)]


def cell_kinds(cells):
    return [(cell["tag"], cell["cls"], cell["key"]) for cell in cells]


def press(page, locator):
    """One mouse click at the centre of `locator`, after checking that the topmost element there lies inside it."""
    box = locator.bounding_box()
    assert box is not None, f"{locator} is not shown"
    point = [box["x"] + box["width"] / 2, box["y"] + box["height"] / 2]
    assert locator.evaluate("(node, [x, y]) => node.contains(document.elementFromPoint(x, y))", point), (
        f"{locator} is not under {point}"
    )
    page.mouse.click(*point)


def settle(page, seconds=5):
    """Wait until no animation runs, so a box measured now is where it rests. CSS animations follow real time, so they
    end under a paused clock too. Fails after `seconds`."""
    deadline = time.monotonic() + seconds
    while page.evaluate("() => document.getAnimations().some((animation) => animation.playState === 'running')"):
        if time.monotonic() > deadline:
            pytest.fail(f"an animation still runs after {seconds} seconds")
        time.sleep(0.02)


ACTIVE_JS = """() => {
  const active = document.activeElement;
  if (!active || active === document.body) return 'body';
  const layer = active.closest('dialog') || document.querySelector('div.app');
  const name = (active.getAttribute('aria-label') || active.textContent.trim()).slice(0, 60);
  return `${[active.localName, ...active.classList].join('.')} "${name}" in ${[layer.localName, ...layer.classList].join('.')}`;
}"""


def assert_focus_on(page, locator, what):
    """The element of `locator` is document.activeElement, else the message says what has focus instead."""
    assert locator.evaluate("(node) => node === document.activeElement"), f"focus is not on {what} but on {page.evaluate(ACTIVE_JS)}"


def shown_date(page):
    return page.locator("header.top > time.date").evaluate("(date) => [date.getAttribute('datetime'), date.textContent]")


def numbers(page):
    return [row_numbers(page, name) for name in NAMES]


def band_today(page):
    """The date key of the band's day button that carries aria-current, or None."""
    return page.evaluate("() => document.querySelector('section.band button.hc[aria-current]')?.getAttribute('data-key') ?? null")


def today_marks(cell):
    """A day cell's name, its aria-current and whether its ring draws the today circle."""
    return cell["label"], cell["current"], TODAY_CIRCLE in cell["ring"]["parts"]


SUNDAY_NUMBERS = [
    {"current": "4 days", "best": "9"},
    {"current": "No streak yet", "best": "5"},
    {"current": "No streak yet", "best": "14"},
]


def assert_the_page_shows_sunday(page):
    """K1 after the rollover from Saturday 10 to Sunday 11 October 2026, spec R19's worked example."""
    assert shown_date(page) == ["2026-10-11", "Sunday 11 October"], f"the header shows {shown_date(page)}"
    assert numbers(page) == SUNDAY_NUMBERS, "the rows do not show Sunday's numbers"
    pressed = [done_btn(page, name).get_attribute("aria-pressed") for name in NAMES]
    assert pressed == ["false"] * 3, f"Done today does not mean Sunday, aria-pressed {pressed}"
    cells = [cell for _, week in weeks(page, BAND) for cell in week]
    assert cell_kinds(cells) == [("button", "hc", key) for key in days("2026-07-20", 84)], (
        "the band is not 84 day buttons from 20 July to 11 October"
    )
    day = {cell["key"]: cell for cell in cells}
    assert today_marks(day["2026-10-11"]) == ("Sun 11 Oct, 0 of 3 habits", "date", True), day["2026-10-11"]
    assert today_marks(day[TODAY]) == ("Sat 10 Oct, 1 of 3 habits", None, False), day[TODAY]
    assert page.locator("button.ov-btn").get_attribute("aria-label") == "Overview, today 0 of 3 habits done"


# ---------------------------------------------------------------------------------------------------------------


def test_R19_R35_the_view_moves_to_the_new_day_within_a_minute_while_visible(app):
    page = open_paused(app, SATURDAY_2359, viewport=DESKTOP, storage=sample_state())
    page.clock.run_for(29_000)
    assert shown_date(page) == [TODAY, "Saturday 10 October"], f"the view changed day before local midnight, {shown_date(page)}"
    assert band_today(page) == TODAY, "the band's today moved before local midnight"

    page.clock.run_for(61_000)
    assert_the_page_shows_sunday(page)


def test_R19_a_page_booted_ten_seconds_before_midnight_shows_the_new_day_thirty_seconds_after_it(app):
    """Pins the 30 second check of R19 (the 1.0 code review's guard, WR-04). A page booted at about 23:59:50 checks at
    about 00:00:20, and a check every 45 seconds or more first runs after 00:00:30. The "within a minute" test reads
    only at 00:01:00, which any check under about two minutes meets."""
    page = app(viewport=DESKTOP, storage=sample_state(), install_time="2026-10-10T23:59:50+08:00")
    page.clock.pause_at("2026-10-10T23:59:59+08:00")
    page.clock.run_for(900)  # 23:59:59.9, the new day must not show before midnight
    assert shown_date(page) == [TODAY, "Saturday 10 October"], f"the view changed day before local midnight, {shown_date(page)}"
    page.clock.run_for(30_100)  # 00:00:30.0
    assert_the_page_shows_sunday(page)


def test_R19_R35_R38_the_band_and_p3_move_when_a_new_week_starts(app):
    page = open_paused(app, SUNDAY_2359, viewport=DESKTOP, storage=sample_state())
    page.clock.run_for(PAST_MIDNIGHT_MS)

    band = weeks(page, BAND)
    cells = [cell for _, week in band for cell in week]
    assert cell_kinds(cells) == [("button", "hc", key) for key in days("2026-07-27", 78)] + [("span", "hc", None)] * 6, (
        "the band does not run from 27 July to 18 October with 13 to 18 October empty"
    )
    assert [month for month, _ in band] == ["Jul", "Aug", "", "", "", "", "Sep", "", "", "", "Oct", ""]
    monday = {cell["key"]: cell for cell in cells}["2026-10-12"]
    assert (monday["label"], monday["current"]) == ("Mon 12 Oct, 0 of 3 habits", "date"), monday
    assert numbers(page) == [{"current": "No streak yet", "best": best} for best in ("9", "5", "14")]

    page.set_viewport_size({"width": PHONE[0], "height": PHONE[1]})
    press(page, page.locator("button.ov-btn"))
    expect(page.locator("dialog.dlg-ov")).to_have_attribute("open", "")
    rows = weeks(page, P3_GRID)
    assert cell_kinds(rows[0][1]) == [("button", "hc", "2026-10-12")] + [("span", "hc", None)] * 6, (
        "P3's first row is not Monday 12 October and six empty cells"
    )
    assert rows[11][1][0]["key"] == "2026-07-27", "P3's last row does not start on Monday 27 July"
    assert [month for month, _ in rows] == ["Oct", "Oct", "", "", "", "Sep", "", "", "", "", "Aug", "Jul"]


P2_JS = """() => {
  const months = document.querySelector('dialog.dlg-year div.months');
  const cell = (key) => Array.from(months.querySelectorAll('[data-key]')).find((node) => node.dataset.key === key) ?? null;
  const describe = (node) => node && [node.localName, Array.from(node.classList).sort().join(' '), node.getAttribute('aria-label'),
    node.getAttribute('aria-pressed'), node.getAttribute('aria-current')];
  const grid = (id) => months.querySelector(`section.month[aria-labelledby="${id}"] > div.mgrid`);
  const october = grid('mo-2026-10');
  const oldest = grid('mo-2025-10');
  return {
    open: months.closest('dialog').open,
    sunday: describe(cell('2026-10-11')),
    saturday: describe(cell('2026-10-10')),
    closed: october && Array.from(october.querySelectorAll(':scope > span.yc.closed')).map((node) => node.textContent),
    blank: oldest && oldest.querySelectorAll(':scope > span.yc.blank').length,
    yearStart: describe(cell('2025-10-10')),
    beads: months.querySelectorAll('button.yc').length,
  };
}"""


def test_R19_R33_an_open_year_view_moves_to_the_new_year(app):
    page = open_paused(app, SATURDAY_2359, viewport=PHONE, storage=sample_state())
    press(page, year_btn(page, "Read 20 pages"))
    expect(page.locator("dialog.dlg-year")).to_have_attribute("open", "")
    page.clock.run_for(PAST_MIDNIGHT_MS)

    year = page.evaluate(P2_JS)
    assert year["open"] is True, "P2 closed at the rollover"
    assert year["sunday"] == ["button", "today yc", "Mark Sun 11 Oct 2026 as done", "false", "date"], (
        f"the 2026-10-11 cell is not today's open bead, {year['sunday']}"
    )
    assert year["closed"] == [str(day) for day in range(12, 32)], f"12 to 31 October 2026 are not closed, {year['closed']}"
    assert "today" not in year["saturday"][1].split() and year["saturday"][4] is None, (
        f"the 2026-10-10 bead is still today, {year['saturday']}"
    )
    assert year["blank"] == 10, f"October 2025 holds {year['blank']} blank cells, not 1 to 10 October"
    assert year["yearStart"] is None, f"P2 still holds a cell for 2025-10-10, {year['yearStart']}"
    assert year["beads"] == 366, f"P2 holds {year['beads']} bead buttons"
    assert stats_tree(page.locator("dialog.dlg-year p.yr-stats")) == [current_block(4, "days"), best_block(9)]


TICK_STAT_JS = "(button) => Array.from(button.querySelector(':scope > span.tstat').children).map((node) => [[node.localName, ...node.classList].join('.'), node.textContent])"
P1_HEAD_JS = "(day) => [day.open, day.querySelector('#day-title').textContent, day.querySelector('#day-sub').textContent]"


def test_R19_R36_an_open_day_editor_keeps_its_day_and_shows_todays_numbers(app):
    page = open_paused(app, SATURDAY_2359, viewport=DESKTOP, storage=sample_state())
    press(page, band_day(page, SEP_22))
    p1 = page.locator("dialog.dlg-day")
    expect(p1).to_have_attribute("open", "")
    page.clock.run_for(PAST_MIDNIGHT_MS)

    assert p1.evaluate(P1_HEAD_JS) == [True, "Tuesday 22 September", "1 of 3 habits"], "P1 did not keep its day"
    assert [tick(page, name).evaluate(TICK_STAT_JS) for name in NAMES] == [
        [["span.tcur", "Current 4 days"], ["span", "Best 9"]],
        [["span.tcur.none", "No streak yet"], ["span", "Best 5"]],
        [["span.tcur.none", "No streak yet"], ["span", "Best 14"]],
    ], "P1's ticks do not show Sunday's numbers"
    assert band_today(page) == "2026-10-11", "the band's today is not Sunday"
    # R36. While P1 is open its day is marked open, and on its close focus goes back to that day in its host. The new
    # day laid the band out again, so both now concern the band's new button for 22 September.
    assert band_day(page, SEP_22).evaluate("(day) => day.classList.contains('is-open')"), "the band's 22 September lost is-open"
    watch = watch_close(page, "dialog.dlg-day")
    page.keyboard.press("Escape")
    wait_for_close(watch)
    assert_focus_on(page, band_day(page, SEP_22), "the band's 22 September, the day that opened P1")


def test_R19_the_composer_keeps_its_text_and_its_focus(app):
    page = open_paused(app, SATURDAY_2359, storage=sample_state())
    field = page.locator("#nh")
    press(page, field)
    page.keyboard.type("Drink")
    page.clock.run_for(PAST_MIDNIGHT_MS)

    assert shown_date(page)[1] == "Sunday 11 October", f"the header shows {shown_date(page)}"
    assert field.input_value() == "Drink", f"the field holds {field.input_value()!r} after the rollover"
    assert_focus_on(page, field, "the field")


MESSAGE_JS = "(message) => [message.textContent, message.className, message.hidden]"
EMPTY_ERROR = ["Name the habit first.", "field-msg err", False]


def test_R19_an_error_message_survives_the_rollover(app):
    page = open_paused(app, SATURDAY_2359, storage=sample_state())
    press(page, page.locator("#add-btn"))
    message = page.locator("#nh-msg")
    assert message.evaluate(MESSAGE_JS) == EMPTY_ERROR, "precondition, Add with an empty field shows the empty name error"
    page.clock.run_for(PAST_MIDNIGHT_MS)

    assert shown_date(page)[1] == "Sunday 11 October", f"precondition, the rollover happened, the header shows {shown_date(page)}"
    assert message.evaluate(MESSAGE_JS) == EMPTY_ERROR, f"the error did not survive the rollover, {message.evaluate(MESSAGE_JS)}"
    assert page.locator("#nh").get_attribute("aria-invalid") == "true", "the field lost aria-invalid at the rollover"


def test_R19_R22_focus_on_a_done_today_button_stays_on_it(app):
    page = open_paused(app, SATURDAY_2359, storage=sample_state())
    done = done_btn(page, "Read 20 pages")
    tab_to(page, done)
    handle = done.element_handle()
    page.clock.run_for(PAST_MIDNIGHT_MS)

    assert handle.evaluate("(button) => button === document.activeElement"), (
        f"focus is not on the Done today button it was on but on {page.evaluate(ACTIVE_JS)}"
    )
    assert handle.get_attribute("aria-pressed") == "false", "Done today still means Saturday"


def test_R19_R22_focus_on_a_day_that_stays_in_view_stays_on_that_day(app):
    page = open_paused(app, SATURDAY_2359, viewport=PHONE, storage=sample_state())
    tab_to(page, year_btn(page, "Read 20 pages"))
    page.keyboard.press("Enter")
    expect(page.locator("dialog.dlg-year")).to_have_attribute("open", "")
    tab_to(page, bead(page, TODAY))
    page.clock.run_for(PAST_MIDNIGHT_MS)

    saturday = bead(page, TODAY)
    assert_focus_on(page, saturday, "the bead of 10 October")
    marks = saturday.evaluate("(day) => [day.classList.contains('today'), day.getAttribute('aria-current')]")
    assert marks == [False, None], f"the bead of 10 October is still today, {marks}"


@pytest.mark.parametrize(
    "viewport, installed, opener, focused, name, target, what",
    [
        pytest.param(
            DESKTOP, SUNDAY_2359, None, lambda page: band_day(page, "2026-07-20"), "Mon 20 Jul, 2 of 3 habits",
            "section.band button.btn-all", "the band's Year", id="1280x800 no popup, the band's 20 July",
        ),
        pytest.param(
            DESKTOP, SATURDAY_2359, "section.band button.btn-all", lambda page: p4_day(page, YEAR_START),
            "Fri 10 Oct 2025, 3 of 3 habits", "dialog.dlg-all button.icon-btn", "P4's Close", id="1280x800 P4, 10 Oct 2025",
        ),
        pytest.param(
            PHONE, SATURDAY_2359, "ul.rows > li.row:first-child button.btn-year", lambda page: bead(page, YEAR_START),
            "Mark Fri 10 Oct 2025 as done", "dialog.dlg-year button.icon-btn", "P2's Close", id="390x844 P2, 10 Oct 2025",
        ),
        pytest.param(
            PHONE, SUNDAY_2359, "button.ov-btn", lambda page: p3_day(page, "2026-07-20"), "Mon 20 Jul, 2 of 3 habits",
            "dialog.dlg-ov button.icon-btn", "P3's Close", id="390x844 P3, 20 July",
        ),
    ],
)
def test_R19_R22_focus_whose_day_leaves_the_view_goes_to_the_top_popups_first_focus_or_the_pages_first_control(
    app, viewport, installed, opener, focused, name, target, what
):
    page = open_paused(app, installed, viewport=viewport, storage=sample_state())
    if opener:
        press(page, page.locator(opener))
        expect(page.locator("dialog[open]")).to_have_count(1)
    day = focused(page)
    tab_to(page, day, limit=400)
    assert day.get_attribute("aria-label") == name, "precondition, Tab reached the day the scenario names"
    page.clock.run_for(PAST_MIDNIGHT_MS)

    assert_focus_on(page, page.locator(target), what)


def test_R19_R37_p1_open_on_the_oldest_day_of_the_year_when_midnight_passes(app):
    page = open_paused(app, SATURDAY_2359, viewport=DESKTOP, storage=sample_state(), count_writes=True)
    press(page, page.locator("section.band button.btn-all"))
    expect(page.locator("dialog.dlg-all")).to_have_attribute("open", "")
    tab_to(page, p4_day(page, YEAR_START), limit=400)
    page.keyboard.press("Enter")
    p1 = page.locator("dialog.dlg-day")
    expect(p1).to_have_attribute("open", "")
    text = stored(page)
    page.clock.run_for(PAST_MIDNIGHT_MS)

    assert p1.evaluate(P1_HEAD_JS) == [True, "Friday 10 October", "3 of 3 habits"], "P1 did not stay open on its day"
    assert p4_day(page, YEAR_START).count() == 0, "P4 still holds a button for 10 October 2025"

    read = tick(page, "Read 20 pages")
    settle(page)
    press(page, read)
    assert read.get_attribute("aria-pressed") == "true", "the tick flipped on a day the year no longer holds"
    assert write_count(page) == 0, "a tick on a day outside the year was saved"
    assert stored(page) == text

    watch = watch_close(page, "dialog.dlg-day")
    page.keyboard.press("Escape")
    wait_for_close(watch)
    assert page.evaluate("() => ['dlg-day', 'dlg-all'].map((name) => document.querySelector(`dialog.${name}`).open)") == [False, True]
    assert_focus_on(page, page.locator("dialog.dlg-all button.icon-btn"), "P4's Close")


def test_R20_the_view_moves_at_once_when_the_tab_is_shown_again(app):
    page = app(install_time="2026-10-10T23:58:00+08:00", viewport=DESKTOP, storage=sample_state())
    page.clock.pause_at("2026-10-10T23:59:00+08:00")
    hide_tab(page)
    page.clock.set_system_time("2026-10-11T07:30:00+08:00")
    assert shown_date(page)[1] == "Saturday 10 October", "precondition, setting the system time fired no check"

    show_tab(page)
    assert_the_page_shows_sunday(page)
