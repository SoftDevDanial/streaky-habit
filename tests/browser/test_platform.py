"""R21 to R26: phone sizes, the keyboard, motion, names as text, requests, no seed and no hooks (app qa.md, Feature
"Platform", and the three @R26 scenarios of Feature "Shipped entry point, stylesheet and icon").

Each test drives the running app with real gestures and reads boxes, focus, computed styles, the request log or the
files under src/. Two Platform lines are held elsewhere, so they are not repeated here. The three rows of the Outline
"Nothing scrolls at 360 pixels" with no popup open are `test_R5_R21_the_page_never_scrolls_and_the_composer_stays_put`
in test_render.py (at 360 x 780), and the icon's load under the CSP is `test_R29_R25_...` in test_entry.py.
"""
import datetime
import json
import time

import pytest
from playwright.sync_api import expect

import conftest
from conftest import (
    NOON,
    ROOT,
    SAMPLE_FILE,
    SAMPLE_HABITS,
    add_button,
    add_habit,
    animation_log,
    animations,
    band_day,
    bin_btn,
    bead,
    confirm_delete,
    dialog_title,
    done_btn,
    let_guard_pass,
    p3_day,
    record,
    sample_state,
    stored,
    tab_to,
    tick,
    wait_for_close,
    watch_close,
    year_btn,
)

SMALL = (360, 780)
PHONE = (390, 844)
DESKTOP = (1280, 800)
SAMPLE = sample_state()
READ, STRETCH, NO_PHONE = (habit["name"] for habit in SAMPLE_HABITS)
FOCUS_COLOUR = "rgb(237, 238, 240)"  # --focus (system.css), spec R22
SRC_DIR = ROOT / "src"


def click_open(control, dialog):
    """Click `control` and wait until `dialog.<dialog>` is open."""
    control.click()
    expect(control.page.locator(f"dialog.{dialog}")).to_have_attribute("open", "")


def close_with_escape(page, dialog):
    page.keyboard.press("Escape")
    expect(page.locator(f"dialog.{dialog}")).not_to_have_attribute("open", "")


def open_p3(page):
    click_open(page.locator("button.ov-btn"), "dlg-ov")


def open_p3_then_p1(page):
    open_p3(page)
    click_open(p3_day(page, "2026-09-22"), "dlg-day")


def open_p3_then_p4(page):
    open_p3(page)
    click_open(page.locator("dialog.dlg-ov button.btn-all"), "dlg-all")


def open_p2_for_read(page):
    click_open(year_btn(page, READ), "dlg-year")


def open_m1_from_read(page):
    click_open(bin_btn(page, READ), "dlg-del")


def open_p4_from_the_band(page):
    click_open(page.locator("section.band button.btn-all"), "dlg-all")


def open_p1_from_the_band(page):
    click_open(band_day(page, "2026-09-22"), "dlg-day")


def by_keyboard(page, opener, dialog):
    """Tab to `opener`, press Enter and wait until `dialog.<dialog>` is open."""
    tab_to(page, opener)
    page.keyboard.press("Enter")
    expect(page.locator(f"dialog.{dialog}")).to_have_attribute("open", "")


_BOXES_JS = "(nodes) => nodes.map((node) => { const box = node.getBoundingClientRect(); return [box.width, box.height]; })"


def boxes(locator):
    """[width, height] of every element `locator` matches, in document order."""
    return locator.evaluate_all(_BOXES_JS)


def sizes(locator):
    """The distinct (width, height) pairs of the elements `locator` matches."""
    return {tuple(box) for box in boxes(locator)}


def settle(page, seconds=2):
    """Wait until no animation runs, so boxes are read where a popup rests. Mid `rise` the box's transform rounds
    sizes in the last bits (45.99994 for a 46 px cell). Polled from here with a deadline."""
    deadline = time.monotonic() + seconds
    while page.evaluate("() => document.getAnimations().length") > 0:
        if time.monotonic() > deadline:
            pytest.fail(f"animations still ran {seconds} s after the popup opened")
        time.sleep(0.02)


# ---------------------------------------------------------------------------------------------------- R21


@pytest.mark.parametrize(
    "popups",
    [
        pytest.param(open_p3, id="P3"),
        pytest.param(open_p3_then_p1, id="P3, then P1 for 2026-09-22"),
        pytest.param(open_p3_then_p4, id="P3, then P4 from its Year"),
        pytest.param(open_p2_for_read, id="P2 for Read"),
        pytest.param(open_m1_from_read, id="M1, from 'Delete \"Read 20 pages\"'"),
    ],
)
def test_R21_nothing_scrolls_at_360_pixels_with_a_popup_open(app, popups):
    page = app(viewport=SMALL, storage=SAMPLE)
    popups(page)
    width, height = page.evaluate("() => [document.documentElement.scrollWidth, document.documentElement.scrollHeight]")
    assert width <= 360 and height == 780, f"the page scrolls with the popup open: scrollWidth {width}, scrollHeight {height}"


def test_R21_sizes_at_360_pixels(app):
    page = app(viewport=SMALL, storage=SAMPLE, install_time=NOON)
    controls = boxes(page.locator("ul.rows button.btn-bin, ul.rows button.btn-year, ul.rows button.btn-done, button.ov-btn"))
    assert len(controls) == 10 and all(width >= 44 and height >= 44 for width, height in controls), f"under 44 by 44: {controls}"
    assert [height for _, height in boxes(page.locator("#nh, #add-btn"))] == [48, 48]

    open_p2_for_read(page)
    settle(page)
    assert sizes(page.locator("dialog.dlg-year span.bead")) == {(34, 34)}
    assert boxes(page.locator("dialog.dlg-year button.icon-btn")) == [[44, 44]]

    close_with_escape(page, "dlg-year")
    open_p3(page)
    settle(page)
    cells = boxes(page.locator("dialog.dlg-ov div.ovg-rows .hc"))
    assert len(cells) == 84 and all(height == 46 and 42.6 <= width <= 43.6 for width, height in cells), f"P3 cells {sorted(set(map(tuple, cells)))}"
    assert sizes(page.locator("dialog.dlg-ov div.ovg-rows button.hc > svg")) == {(40, 40)}
    head = boxes(page.locator("dialog.dlg-ov div.ov-head > button"))
    assert len(head) == 2 and all(width >= 44 and height >= 44 for width, height in head), f"P3's Year and Close {head}"

    click_open(page.locator("dialog.dlg-ov button.btn-all"), "dlg-all")
    settle(page)
    assert {height for _, height in boxes(page.locator("dialog.dlg-all div.mgrid .hc:not(.lead)"))} == {46}
    assert sizes(page.locator("dialog.dlg-all div.mgrid button.hc > svg")) == {(40, 40)}

    click_open(page.locator("dialog.dlg-all").get_by_role("button", name="Tue 22 Sep 2026, 1 of 3 habits", exact=True), "dlg-day")
    settle(page)
    ticks = boxes(page.locator("dialog.dlg-day button.tick"))
    assert len(ticks) == 3 and all(height >= 60 for _, height in ticks), f"P1's ticks {ticks}"
    assert boxes(page.locator("dialog.dlg-day button.icon-btn")) == [[44, 44]]

    for dialog in ("dlg-day", "dlg-all", "dlg-ov"):
        close_with_escape(page, dialog)
    let_guard_pass(page)  # the clicks inside P3 and P4 hold the page's clicks for 500 ms (R14)
    open_m1_from_read(page)
    settle(page)
    assert [height for _, height in boxes(page.locator("dialog.dlg-del div.dlg-actions > button"))] == [48, 48]

    unreadable = app(viewport=SMALL, storage="{")
    assert boxes(unreadable.get_by_role("button", name="Dismiss note", exact=True)) == [[44, 44]]


def test_R21_sizes_at_390_pixels(app):
    page = app(viewport=PHONE, storage=SAMPLE)
    open_p2_for_read(page)
    settle(page)
    assert sizes(page.locator("dialog.dlg-year span.bead")) == {(36, 36)}
    assert {height for _, height in boxes(page.locator("dialog.dlg-year button.yc"))} == {44}

    close_with_escape(page, "dlg-year")
    open_p3(page)
    settle(page)
    assert {height for _, height in boxes(page.locator("dialog.dlg-ov div.ovg-rows .hc"))} == {48}
    assert sizes(page.locator("dialog.dlg-ov div.ovg-rows button.hc > svg")) == {(42, 42)}

    click_open(page.locator("dialog.dlg-ov button.btn-all"), "dlg-all")
    settle(page)
    assert {height for _, height in boxes(page.locator("dialog.dlg-all div.mgrid .hc:not(.lead)"))} == {48}
    assert sizes(page.locator("dialog.dlg-all div.mgrid button.hc > svg")) == {(42, 42)}


# ---------------------------------------------------------------------------------------------------- R22

# What has focus, as a test reads a tab order. A band day by its date, else a control by its accessible name, else by id.
_FOCUS_JS = """() => {
  const active = document.activeElement;
  if (!active || active === document.body) return 'body';
  if (active.matches('section.band button.hc')) return 'band ' + active.getAttribute('data-key');
  return active.getAttribute('aria-label') || (active.id ? '#' + active.id : active.localName);
}"""

BAND_DAYS = [f"band {datetime.date(2026, 7, 20) + datetime.timedelta(days=n)}" for n in range(83)]  # Mon 20 Jul to Sat 10 Oct
COMPOSER = ["#nh", "#add-btn"]


def row_controls(*names):
    return [label for name in names for label in (f'Delete "{name}"', f"Year view, {name}", f"Done today, {name}")]


def tab_through(page, presses):
    """Press Tab `presses` times from nothing focused, and return what had focus after each press."""
    assert page.evaluate(_FOCUS_JS) == "body", "something had focus before the first Tab"
    visited = []
    for _ in range(presses):
        page.keyboard.press("Tab")
        visited.append(page.evaluate(_FOCUS_JS))
    return visited


def test_R22_tab_order_on_a_phone(app):
    page = app(viewport=PHONE, storage=SAMPLE)
    assert tab_through(page, 12) == ["Overview, today 1 of 3 habits done", *row_controls(READ, STRETCH, NO_PHONE), *COMPOSER]


def test_R22_R35_tab_order_on_a_desktop(app):
    page = app(viewport=DESKTOP, storage=SAMPLE)
    assert BAND_DAYS[-1] == "band 2026-10-10"
    assert tab_through(page, 95) == ["Year view, all habits", *BAND_DAYS, *row_controls(READ, STRETCH, NO_PHONE), *COMPOSER]


@pytest.mark.parametrize(
    "viewport, presses, order",
    [
        pytest.param(PHONE, 4, ["Overview, today 0 of 0 habits done", "Dismiss note", *COMPOSER], id="390x844"),
        pytest.param(DESKTOP, 87, ["Year view, all habits", *BAND_DAYS, "Dismiss note", *COMPOSER], id="1280x800"),
    ],
)
def test_R22_R17_tab_order_with_the_note(app, viewport, presses, order):
    page = app(viewport=viewport, storage="{")
    assert tab_through(page, presses) == order


_RING_JS = """(node) => {
  const style = getComputedStyle(node);
  return [style.outlineColor, style.outlineStyle, style.outlineWidth, style.outlineOffset];
}"""


def ring(locator):
    """The outline longhands of the element, which both engines write alike (qa.md, engine table)."""
    return locator.evaluate(_RING_JS)


def p2_by_keyboard(page):
    by_keyboard(page, year_btn(page, READ), "dlg-year")


def p1_by_keyboard(page):
    by_keyboard(page, band_day(page, "2026-09-22"), "dlg-day")


def m1_by_keyboard(page):
    by_keyboard(page, bin_btn(page, READ), "dlg-del")


@pytest.mark.parametrize(
    "viewport, storage, opened, target, on_bead, offset",
    [
        pytest.param(PHONE, SAMPLE, None, lambda page: page.locator("button.ov-btn"), False, "2px", id="390x844 Overview"),
        pytest.param(PHONE, SAMPLE, None, lambda page: year_btn(page, READ), False, "2px", id="390x844 Year view, Read"),
        pytest.param(PHONE, SAMPLE, None, lambda page: done_btn(page, READ), False, "2px", id="390x844 Done today, Read"),
        pytest.param(PHONE, SAMPLE, None, lambda page: page.locator("#nh"), False, "2px", id="390x844 the field"),
        pytest.param(PHONE, SAMPLE, None, add_button, False, "3px", id="390x844 Add"),
        pytest.param(DESKTOP, SAMPLE, None, lambda page: page.locator("section.band button.btn-all"), False, "2px", id="1280x800 the band's Year"),
        pytest.param(
            DESKTOP, SAMPLE, None,
            lambda page: page.locator("section.band").get_by_role("button", name="Mon 20 Jul, 2 of 3 habits", exact=True),
            False, "-2px", id="1280x800 the band's Mon 20 Jul",
        ),
        pytest.param(PHONE, SAMPLE, p2_by_keyboard, lambda page: page.locator("dialog.dlg-year button.icon-btn"), False, "-2px", id="390x844 P2's Close"),
        pytest.param(PHONE, SAMPLE, p2_by_keyboard, lambda page: page.locator("dialog.dlg-year button.btn-del"), False, "2px", id="390x844 P2's Delete habit"),
        pytest.param(
            PHONE, SAMPLE, p2_by_keyboard,
            lambda page: page.get_by_role("button", name="Mark Thu 1 Oct 2026 as done", exact=True),
            True, "3px", id="390x844 the bead Thu 1 Oct 2026",
        ),
        pytest.param(DESKTOP, SAMPLE, p1_by_keyboard, lambda page: tick(page, STRETCH), False, "-2px", id="1280x800 P1's tick Stretch"),
        pytest.param(PHONE, SAMPLE, m1_by_keyboard, lambda page: page.locator("dialog.dlg-del button.btn-secondary"), False, "3px", id="390x844 M1's Cancel"),
        pytest.param(PHONE, "{", None, lambda page: page.get_by_role("button", name="Dismiss note", exact=True), False, "-2px", id="390x844 Dismiss note"),
    ],
)
def test_R22_focus_rings_on_keyboard_focus(app, viewport, storage, opened, target, on_bead, offset):
    page = app(viewport=viewport, storage=storage)
    if opened:
        opened(page)
    control = target(page)
    tab_to(page, control)
    assert ring(control.locator("span.bead") if on_bead else control) == [FOCUS_COLOUR, "solid", "2px", offset]


def test_R22_a_focused_bin_shows_its_glyph_in_the_danger_colour_and_a_focused_bead_has_no_ring_of_its_own(app):
    page = app(viewport=PHONE, storage=SAMPLE)
    read_bin = bin_btn(page, READ)
    tab_to(page, read_bin)
    assert ring(read_bin) == [FOCUS_COLOUR, "solid", "2px", "-2px"]
    expect(read_bin).to_have_css("color", "rgb(255, 107, 102)")  # after its 170 ms colour transition
    p2_by_keyboard(page)
    first_of_october = page.get_by_role("button", name="Mark Thu 1 Oct 2026 as done", exact=True)
    tab_to(page, first_of_october)
    assert first_of_october.evaluate("(node) => getComputedStyle(node).outlineStyle") == "none"
    assert ring(first_of_october.locator("span.bead")) == [FOCUS_COLOUR, "solid", "2px", "3px"]


def test_R22_a_mouse_click_draws_no_ring(app, engine):
    page = app(storage=SAMPLE)
    button = done_btn(page, STRETCH)
    button.click()
    expect(button).to_have_attribute("aria-pressed", "true")
    assert button.evaluate("(node) => [node.matches(':focus-visible'), getComputedStyle(node).outlineStyle]") == [False, "none"]
    focus = button.evaluate("(node) => document.activeElement === node ? 'the button' : document.activeElement.localName")
    assert focus == ("the button" if engine == "chromium" else "body")


def test_R22_R40_every_popup_can_be_used_with_the_keyboard_alone(app):
    page = app(viewport=PHONE, storage=SAMPLE)
    overview = page.locator("button.ov-btn")
    assert page.evaluate(_FOCUS_JS) == "body"
    page.keyboard.press("Tab")
    expect(overview).to_be_focused()
    page.keyboard.press("Enter")
    expect(page.locator("dialog.dlg-ov")).to_have_attribute("open", "")
    expect(page.locator("dialog.dlg-ov button.icon-btn")).to_be_focused()
    page.keyboard.press("Shift+Tab")
    expect(page.locator("dialog.dlg-ov button.btn-all")).to_be_focused()
    page.keyboard.press("Enter")
    expect(page.locator("dialog.dlg-all")).to_have_attribute("open", "")
    expect(page.locator("dialog.dlg-all button.icon-btn")).to_be_focused()
    page.keyboard.press("Tab")
    expect(page.locator("dialog.dlg-all").get_by_role("button", name="Thu 1 Oct 2026, 2 of 3 habits", exact=True)).to_be_focused()
    page.keyboard.press("Enter")
    expect(page.locator("dialog.dlg-day")).to_have_attribute("open", "")
    expect(page.locator("#day-title")).to_have_text("Thursday 1 October")
    expect(tick(page, READ)).to_be_focused()
    page.keyboard.press("Space")
    expect(tick(page, READ)).to_have_attribute("aria-pressed", "false")
    expect(page.locator("#day-sub")).to_have_text("1 of 3 habits")
    closed = watch_close(page, "dialog.dlg-ov")
    # Each press once the popup before it has closed, as a person presses. WebKit drops a press that comes before the
    # previous close took effect, so three sent back to back leave P3 open (qa/escape-pace-probe, BUILD.md task 25).
    for dialog in ("dlg-day", "dlg-all", "dlg-ov"):
        close_with_escape(page, dialog)
    wait_for_close(closed)  # the app's close handler has run (conftest watch_close)
    assert page.locator("dialog[open]").count() == 0
    expect(overview).to_be_focused()


# ---------------------------------------------------------------------------------------------------- R23


def transition_durations(locator):
    """The distinct computed transition-duration strings of the elements `locator` matches."""
    return set(locator.evaluate_all("(nodes) => nodes.map((node) => getComputedStyle(node).transitionDuration)"))


def test_R23_transitions_without_reduced_motion(app):
    page = app(viewport=DESKTOP, storage=SAMPLE)
    assert page.evaluate("() => document.getAnimations().map((animation) => animation.constructor.name)") == [], "something moved on load"
    found = {
        selector: transition_durations(page.locator(selector))
        for selector in ("button.btn-done", "button.btn-year", "button.btn-bin", "button.hc", "button.ov-btn", "#add-btn")
    }
    assert found == {
        "button.btn-done": {"0.17s, 0.17s, 0.17s, 0.12s"},
        "button.btn-year": {"0.17s, 0.17s, 0.17s, 0.12s"},
        "button.btn-bin": {"0.17s, 0.17s, 0.12s"},
        "button.hc": {"0.17s"},
        "button.ov-btn": {"0.17s, 0.12s"},
        "#add-btn": {"0.17s, 0.12s"},
    }
    open_p1_from_the_band(page)
    assert transition_durations(page.locator("dialog.dlg-day button.tick")) == {"0.17s"}
    assert transition_durations(page.locator("dialog.dlg-day span.tbox")) == {"0.17s, 0.17s"}
    close_with_escape(page, "dlg-day")
    open_p2_for_read(page)
    assert transition_durations(page.locator("dialog.dlg-year span.bead")) == {"0.17s, 0.17s, 0.12s"}


@pytest.mark.parametrize(
    "viewport, opened, dialog, name, duration",
    [
        pytest.param(PHONE, open_p2_for_read, "dlg-year", "rise", "0.22s", id="390x844 P2 for Read"),
        pytest.param(PHONE, open_p3, "dlg-ov", "rise", "0.22s", id="390x844 P3"),
        pytest.param(DESKTOP, open_p4_from_the_band, "dlg-all", "rise", "0.22s", id="1280x800 P4 from the band's Year"),
        pytest.param(DESKTOP, open_p1_from_the_band, "dlg-day", "sheet", "0.26s", id="1280x800 P1 for 2026-09-22 from the band"),
        pytest.param(PHONE, open_m1_from_read, "dlg-del", "rise", "0.22s", id="390x844 M1"),
    ],
)
def test_R23_popups_rise_and_backdrops_fade(app, viewport, opened, dialog, name, duration):
    page = app(viewport=viewport, storage=SAMPLE)
    opened(page)
    motion = page.locator(f"dialog.{dialog}").evaluate(
        """(dialog) => {
  const box = getComputedStyle(dialog.querySelector(':scope > div.dlg-box'));
  const backdrop = getComputedStyle(dialog, '::backdrop');
  return [box.animationName, box.animationDuration, backdrop.animationName, backdrop.animationDuration];
}"""
    )
    assert motion == [name, duration, "fade", "0.18s"]


def entry(name, tag, classes, owner, duration):
    """One `animation_log` entry, as the scenario names it."""
    return {"name": name, "tag": tag, "pseudo": "", "classes": classes, "owner": owner, "duration": duration}


def logged_within(log, wanted, seconds=1.0, since=0):
    """The log's entries from `since` on, once every entry of `wanted` is among them or after `seconds`."""
    deadline = time.monotonic() + seconds
    while True:
        entries = animations(log)[since:]
        if all(item in entries for item in wanted) or time.monotonic() > deadline:
            return entries
        time.sleep(0.02)


def settled_entries(log, since):
    """The log's entries from `since` on, read again 100 ms after the wanted ones came, so every animation one edit
    started in the same frame is among them."""
    time.sleep(0.1)
    return animations(log)[since:]


STRETCH_DOT = entry("pop", "span", ["dot"], f"Done today, {STRETCH}", "0.26s")
STRETCH_CURRENT = entry("bump", "span", ["val", "bump"], "rs-2", "0.28s")


def first_done_today(page):
    """Start an `animation_log`, press Stretch's Done today once, and return the log and the moment of the press."""
    log = animation_log(page)
    done_btn(page, STRETCH).click()
    return log, time.monotonic()


def test_R23_R32_a_change_pops_what_changed_and_bumps_its_number_and_replays_on_the_next_change(app):
    # The Overview button is not displayed from 1024 px (R4, the goldens), and an element that is not displayed starts
    # no animation. So its ring's pop is read as its class and computed animation at 1280 and seen playing at 390,
    # where that button shows and the band does not (BUILD.md task 25, open question for the planner).
    phone = app(viewport=PHONE, storage=SAMPLE)
    log, _ = first_done_today(phone)
    on_a_phone = [STRETCH_DOT, entry("pop", "svg", [], "Overview, today 2 of 3 habits done", "0.3s"), STRETCH_CURRENT]
    found = logged_within(log, on_a_phone)
    assert sorted(found, key=str) == sorted(on_a_phone, key=str), "at 390 px Done today did not pop and bump exactly what changed"

    page = app(viewport=DESKTOP, storage=SAMPLE, install_time=NOON)
    log, clicked = first_done_today(page)
    done = done_btn(page, STRETCH)
    first = [STRETCH_DOT, entry("pop", "svg", [], "Sat 10 Oct, 2 of 3 habits", "0.3s"), STRETCH_CURRENT]
    found = logged_within(log, first)
    assert sorted(found, key=str) == sorted(first, key=str), "the first Done today did not pop and bump exactly what changed"
    overview_ring = page.locator("button.ov-btn > span.ov-ring").evaluate(
        "(ring) => [ring.classList.contains('pop'), getComputedStyle(ring.firstElementChild).animationName, getComputedStyle(ring.firstElementChild).animationDuration]"
    )
    assert overview_ring == [True, "pop", "0.3s"], "the Overview button's ring does not carry the pop of a changed ring"

    elapsed = time.monotonic() - clicked
    if elapsed >= 0.26:
        pytest.fail(f"the second click could not come while the first pop runs, {elapsed:.3f} s had passed")
    time.sleep(max(0.0, 0.1 - elapsed))
    done.click()
    again = [STRETCH_DOT, STRETCH_CURRENT]
    found = logged_within(log, again, since=len(first))
    assert all(item in found for item in again), f"the second Done today did not replay the pop and the bump: {found}"

    seen = len(animations(log))
    open_p1_from_the_band(page)
    tick(page, READ).click()
    tick_pop = entry("pop", "span", ["tbox"], READ, "0.26s")
    found = logged_within(log, [tick_pop], since=seen)
    assert tick_pop in found, f"the tick did not pop its box: {found}"
    found = settled_entries(log, seen)
    assert [item for item in found if item["classes"] == ["tbox"]] == [tick_pop], f"a tick that did not change popped: {found}"

    close_with_escape(page, "dlg-day")
    let_guard_pass(page)  # the click on the tick holds the page's clicks for 500 ms (R14)
    seen = len(animations(log))
    open_p2_for_read(page)
    bead(page, "2026-10-06").click()
    popped = entry("pop", "span", ["bead"], "Mark Tue 6 Oct 2026 as done", "0.26s")
    found = logged_within(log, [popped], since=seen)
    assert popped in found, f"the bead did not pop: {found}"
    found = settled_entries(log, seen)
    assert [item for item in found if item["classes"] == ["bead"]] == [popped], f"a bead that did not change popped, a neighbour included: {found}"


_MOVING_JS = """() => {
  const moving = [];
  let checked = 0;
  for (const node of document.querySelectorAll('*')) {
    for (const pseudo of [null, '::before', '::after']) {
      const style = getComputedStyle(node, pseudo);
      checked += 1;
      if (style.transitionDuration.split(', ').some((value) => value !== '0s') || style.animationName !== 'none') {
        moving.push(`${node.localName}.${Array.from(node.classList).join('.')}${pseudo || ''}: ${style.transitionDuration} ${style.animationName}`);
      }
    }
  }
  return { checked, moving };
}"""


def test_R23_everything_appears_at_once_under_reduced_motion(app):
    page = app(viewport=DESKTOP, storage=SAMPLE, reduced_motion="reduce")
    found = page.evaluate(_MOVING_JS)
    assert found["checked"] > 1000 and found["moving"] == [], found["moving"][:10]
    done_btn(page, STRETCH).click()
    expect(done_btn(page, STRETCH)).to_have_attribute("aria-pressed", "true")
    open_p2_for_read(page)
    assert page.evaluate("() => document.getAnimations().length") == 0
    motion = page.locator("dialog.dlg-year").evaluate(
        "(dialog) => [getComputedStyle(dialog.querySelector(':scope > div.dlg-box')).animationName, getComputedStyle(dialog, '::backdrop').animationName]"
    )
    assert motion == ["none", "none"]


# ---------------------------------------------------------------------------------------------------- R24

MARKUP_NAME = "<img src=x onerror=alert(1)>"
_TEXT_JS = "(node) => [node.textContent, node.children.length]"


def test_R24_markup_in_a_name_stays_text_everywhere(app):
    page = app(viewport=DESKTOP, record=True)
    opened_dialogs = []
    page.on("dialog", lambda opened: (opened_dialogs.append(opened.message), opened.dismiss()))
    add_habit(page, MARKUP_NAME)
    expect(page.locator("ul.rows > li.row")).to_have_count(1)
    assert page.locator("h3#rn-1").evaluate(_TEXT_JS) == [MARKUP_NAME, 0]
    assert page.locator("img").count() == 0
    for name in (f'Delete "{MARKUP_NAME}"', f"Year view, {MARKUP_NAME}", f"Done today, {MARKUP_NAME}"):
        expect(page.get_by_role("button", name=name, exact=True)).to_have_count(1)

    click_open(year_btn(page, MARKUP_NAME), "dlg-year")
    assert page.locator("h2#yr-title").evaluate(_TEXT_JS) == [MARKUP_NAME, 0]
    close_with_escape(page, "dlg-year")
    click_open(page.locator("section.band").get_by_role("button", name="Sat 10 Oct, 0 of 1 habits", exact=True), "dlg-day")
    expect(tick(page, MARKUP_NAME)).to_have_count(1)
    assert tick(page, MARKUP_NAME).locator("span.tname").evaluate(_TEXT_JS) == [MARKUP_NAME, 0]
    close_with_escape(page, "dlg-day")
    click_open(bin_btn(page, MARKUP_NAME), "dlg-del")
    assert page.locator("#del-title").evaluate(_TEXT_JS) == [dialog_title(MARKUP_NAME), 0]
    assert page.locator("img").count() == 0
    assert opened_dialogs == [] and record(page).errors == []


def shipped_texts():
    """index.html and every regular file under src/, by path, decoded leniently, so a file that is not UTF-8 text is
    still scanned and cannot hide a sink or a name. R24 and R26 say "every file", so the stylesheet and the icon count."""
    texts = {"index.html": (ROOT / "index.html").read_bytes().decode("utf-8", errors="replace")}
    for path in sorted(SRC_DIR.rglob("*")):
        if path.is_file():
            texts["src/" + path.relative_to(SRC_DIR).as_posix()] = path.read_bytes().decode("utf-8", errors="replace")
    assert {"src/app.js", "src/styles.css", "src/icon.svg"} <= set(texts), sorted(texts)
    return texts


def test_R24_no_html_sinks_in_the_source():
    found = [
        (name, sink)
        for name, text in shipped_texts().items() if name.startswith("src/")
        for sink in ("innerHTML", "outerHTML", "insertAdjacentHTML", "document.write", "eval(", "new Function")
        if sink in text
    ]
    assert found == []


# ---------------------------------------------------------------------------------------------------- R25


def test_R25_every_request_stays_on_the_devices_own_files(app):
    page = app(viewport=DESKTOP, storage=SAMPLE, record=True, install_time=NOON)
    done_btn(page, STRETCH).click()
    expect(done_btn(page, STRETCH)).to_have_attribute("aria-pressed", "true")
    open_p1_from_the_band(page)
    tick(page, READ).click()
    expect(tick(page, READ)).to_have_attribute("aria-pressed", "true")
    close_with_escape(page, "dlg-day")
    let_guard_pass(page)
    open_p2_for_read(page)
    bead(page, "2026-10-06").click()
    expect(bead(page, "2026-10-06")).to_have_attribute("aria-pressed", "true")
    close_with_escape(page, "dlg-year")
    let_guard_pass(page)
    open_p4_from_the_band(page)
    close_with_escape(page, "dlg-all")
    add_habit(page, "Drink water")
    expect(page.locator("ul.rows > li.row")).to_have_count(4)
    open_m1_from_read(page)
    confirm_delete(page, bin_btn(page, READ))
    expect(page.locator("ul.rows > li.row")).to_have_count(3)
    page.reload()
    expect(page.locator("ul.rows > li.row h3")).to_have_text([STRETCH, NO_PHONE, "Drink water"])

    log = record(page)
    origin = conftest.BASE_URL.rstrip("/")
    allowed = {"/", "/index.html", "/favicon.ico", "/src/styles.css", "/src/icon.svg"}
    allowed |= {f"/{name}" for name in shipped_texts() if name.endswith(".js")}
    assert log.requests, "no request was recorded"
    strays = [
        request for request in log.requests
        if request["method"] != "GET" or request["origin"] != origin or request["query"] or request["path"] not in allowed
    ]
    assert strays == []
    assert [message for message in log.console if message["type"] == "error"] == [] and log.errors == []


_REFUSED_FETCH_JS = """() => new Promise((resolve) => {
  const directives = [];
  document.addEventListener('securitypolicyviolation', (event) => directives.push(event.effectiveDirective));
  const giveUp = setTimeout(() => resolve({ result: 'still pending after 5 s', directives }), 5000);
  const settle = (result) => { clearTimeout(giveUp); setTimeout(() => resolve({ result, directives }), 500); };
  fetch('https://example.com/').then(() => settle('resolved'), () => settle('rejected'));
})"""


def test_R25_the_csp_is_in_force(app):
    page = app(storage=SAMPLE)
    assert page.evaluate(_REFUSED_FETCH_JS) == {"result": "rejected", "directives": ["connect-src"]}


# ---------------------------------------------------------------------------------------------------- R26


def test_R26_no_sample_data_in_the_shipped_files():
    names =[habit["name"] for habit in json.loads(SAMPLE_FILE.read_text(encoding="utf-8"))["habits"]]
    assert len(names) == 12
    found = [(file, word) for file, text in shipped_texts().items() for word in (*names, "sample-history") if word in text]
    assert found == []


@pytest.mark.parametrize("path", ["?demo=1", "?seed", "#sample"])
def test_R26_query_strings_and_fragments_do_not_seed(app, path):
    page = app(path=path)
    expect(page.locator("ul.rows > li.empty")).to_have_count(1)
    assert page.locator("ul.rows > li.row").count() == 0
    assert stored(page) is None


def test_R26_no_globals_and_no_hooks(app):
    page = app(storage=SAMPLE)
    expect(page.locator("ul.rows > li.row")).to_have_count(3)
    own_names = "() => Object.getOwnPropertyNames(window)"
    on_the_app = set(page.evaluate(own_names))
    page.goto(conftest.BASE_URL + "__seed__")
    on_a_plain_page = set(page.evaluate(own_names))
    assert sorted(on_the_app - on_a_plain_page) == []
