"""R40 and R14: the popups' stack, Esc, the backdrop, Tab and the page under a popup (app qa.md, Feature "Popups").

Each test opens popups with real gestures and reads which dialogs are open, the focus and computed styles. A row that
opens a popup a later task builds carries a strict xfail mark naming that task until it lands (qa.md, "Scenarios that
wait on a later task", W14 to W18).
"""
import pytest
from playwright.sync_api import expect

from conftest import band_day, bin_btn, p3_day, p4_day, sample_state, year_btn

PHONE = (390, 844)
DESKTOP = (1280, 800)


def wait(task):
    return pytest.mark.xfail(strict=True, reason=f"task {task}")


# Each starting state, opened with the gestures its qa.md row names, and the dialog that ends on top.
def open_m1_from_stretch(page):
    bin_btn(page, "Stretch 10 minutes").click()


def open_m1_from_read(page):
    bin_btn(page, "Read 20 pages").click()


def open_p3(page):
    page.locator("button.ov-btn").click()


def open_p3_then_p1(page):
    open_p3(page)
    p3_day(page, "2026-09-22").click()


def open_p3_then_p4(page):
    open_p3(page)
    page.locator("dialog.dlg-ov button.btn-all").click()


def open_p1_from_band(page):
    band_day(page, "2026-09-22").click()


def open_p2_for_read(page):
    year_btn(page, "Read 20 pages").click()


def open_p4_from_band(page):
    page.locator("section.band button.btn-all").click()


def open_p2_then_m1(page):
    open_p2_for_read(page)
    page.locator("dialog.dlg-year button.btn-del").click()


OPEN = {
    "M1 from Stretch's bin": (open_m1_from_stretch, "dlg-del"),
    "M1 from Read's bin": (open_m1_from_read, "dlg-del"),
    "P3": (open_p3, "dlg-ov"),
    "P3, then P1 for 2026-09-22": (open_p3_then_p1, "dlg-day"),
    "P3, then P4 from its Year": (open_p3_then_p4, "dlg-all"),
    "P1 for 2026-09-22 from the band": (open_p1_from_band, "dlg-day"),
    "P2 for Read": (open_p2_for_read, "dlg-year"),
    "P4 from the band's Year": (open_p4_from_band, "dlg-all"),
    "P2 for Read, then M1 from its Delete habit": (open_p2_then_m1, "dlg-del"),
}


def open_popups(page, state):
    """Open `state` and return the class of the dialog on top, once it is open."""
    opener, top = OPEN[state]
    opener(page)
    expect(page.locator(f"dialog.{top}")).to_have_attribute("open", "")
    return top


def open_dialogs(page):
    return page.evaluate("() => Array.from(document.querySelectorAll('dialog')).filter((d) => d.open).map((d) => d.classList[d.classList.length - 1])")


def wait_closed(page, cls):
    page.wait_for_function("(cls) => !document.querySelector('dialog.' + cls).open", arg=cls, timeout=5000)


def outside_box(page, cls, x, y):
    box = page.locator(f"dialog.{cls} > div.dlg-box").bounding_box()
    return not (box["x"] <= x <= box["x"] + box["width"] and box["y"] <= y <= box["y"] + box["height"])


def is_modal(page):
    return page.evaluate("() => Array.from(document.querySelectorAll('dialog')).filter((d) => d.open).map((d) => d.matches(':modal'))")


# ---------------------------------------------------------------------------------------------------------------


def test_R40_popups_stack_and_esc_closes_the_top_one_only(app):
    page = app(viewport=PHONE, storage=sample_state())
    open_p3_then_p4(page)
    page.locator("dialog.dlg-all").get_by_role("button", name="Tue 22 Sep 2026, 1 of 3 habits", exact=True).click()
    expect(page.locator("dialog.dlg-day")).to_have_attribute("open", "")
    assert sorted(open_dialogs(page)) == ["dlg-all", "dlg-day", "dlg-ov"]
    assert is_modal(page) == [True, True, True]
    box = page.locator("dialog.dlg-day > div.dlg-box").bounding_box()
    centre = (box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    assert page.evaluate("([x, y]) => !!document.elementFromPoint(x, y).closest('dialog.dlg-day')", list(centre))

    page.keyboard.press("Escape")
    wait_closed(page, "dlg-day")
    assert sorted(open_dialogs(page)) == ["dlg-all", "dlg-ov"]
    expect(p4_day(page, "2026-09-22")).to_be_focused()

    page.keyboard.press("Escape")
    wait_closed(page, "dlg-all")
    assert open_dialogs(page) == ["dlg-ov"]
    expect(page.locator("dialog.dlg-ov button.btn-all")).to_be_focused()

    page.keyboard.press("Escape")
    wait_closed(page, "dlg-ov")
    assert open_dialogs(page) == []
    expect(page.locator("button.ov-btn")).to_be_focused()


FOCUS = {
    'Delete "Stretch 10 minutes"': lambda page: bin_btn(page, "Stretch 10 minutes"),
    "P3's 2026-09-22 button": lambda page: p3_day(page, "2026-09-22"),
    "the band's 2026-09-22 button": lambda page: band_day(page, "2026-09-22"),
    '"Year view, Read 20 pages"': lambda page: year_btn(page, "Read 20 pages"),
    "the band's Year": lambda page: page.locator("section.band button.btn-all"),
    "P2's Delete habit": lambda page: page.locator("dialog.dlg-year button.btn-del"),
    "the Overview button": lambda page: page.locator("button.ov-btn"),
}


@pytest.mark.parametrize(
    "viewport, popups, still_open, focus",
    [
        pytest.param(PHONE, "M1 from Stretch's bin", [], 'Delete "Stretch 10 minutes"', marks=wait(22), id="390x844 M1"),
        pytest.param(DESKTOP, "M1 from Stretch's bin", [], 'Delete "Stretch 10 minutes"', marks=wait(22), id="1280x800 M1"),
        pytest.param(PHONE, "P3, then P1 for 2026-09-22", ["dlg-ov"], "P3's 2026-09-22 button", id="390x844 P3 then P1"),
        pytest.param(DESKTOP, "P1 for 2026-09-22 from the band", [], "the band's 2026-09-22 button", id="1280x800 P1"),
        pytest.param(DESKTOP, "P2 for Read", [], '"Year view, Read 20 pages"', id="1280x800 P2"),
        pytest.param(DESKTOP, "P4 from the band's Year", [], "the band's Year", id="1280x800 P4"),
        pytest.param(DESKTOP, "P2 for Read, then M1 from its Delete habit", ["dlg-year"], "P2's Delete habit", marks=wait(22), id="1280x800 P2 then M1"),
        pytest.param((800, 900), "P3", [], "the Overview button", id="800x900 P3"),
    ],
)
def test_R40_R14_a_backdrop_click_closes_that_popup_only(app, viewport, popups, still_open, focus):
    page = app(viewport=viewport, storage=sample_state())
    top = open_popups(page, popups)
    assert outside_box(page, top, 5, 5), "the point (5, 5) lies inside the top popup's box"
    page.mouse.click(5, 5)
    wait_closed(page, top)
    assert open_dialogs(page) == still_open
    expect(FOCUS[focus](page)).to_be_focused()


@pytest.mark.parametrize(
    "viewport, popup, title",
    [
        pytest.param(PHONE, "M1 from Stretch's bin", "#del-title", marks=wait(22), id="390x844 M1"),
        pytest.param(DESKTOP, "P1 for 2026-09-22 from the band", "h2#day-title", id="1280x800 P1"),
        pytest.param(DESKTOP, "P2 for Read", "h2#yr-title", id="1280x800 P2"),
        pytest.param(DESKTOP, "P4 from the band's Year", "h2#all-title", id="1280x800 P4"),
    ],
)
def test_R40_R14_a_click_inside_the_box_or_a_drag_that_leaves_it_closes_nothing(app, viewport, popup, title):
    page = app(viewport=viewport, storage=sample_state())
    top = open_popups(page, popup)
    box = page.locator(f"dialog.{top} > div.dlg-box").bounding_box()
    x, y = box["x"] + 6, box["y"] + 6
    hit = page.evaluate(
        """([x, y, cls]) => { const node = document.elementFromPoint(x, y);
          return { inside: !!node.closest('dialog.' + cls), control: !!node.closest('button, input, a') }; }""",
        [x, y, top],
    )
    assert hit == {"inside": True, "control": False}, hit
    page.mouse.click(x, y)
    expect(page.locator(f"dialog.{top}")).to_have_attribute("open", "")

    heading = page.locator(f"dialog.{top} {title}").bounding_box()
    page.mouse.move(heading["x"] + heading["width"] / 2, heading["y"] + heading["height"] / 2)
    page.mouse.down()
    page.mouse.move(5, 5)
    page.mouse.up()
    expect(page.locator(f"dialog.{top}")).to_have_attribute("open", "")


@pytest.mark.parametrize(
    "viewport, popups, presses",
    [
        pytest.param(PHONE, "P3, then P1 for 2026-09-22", 6, id="390x844 P3 then P1"),
        pytest.param(DESKTOP, "P2 for Read", 10, id="1280x800 P2"),
        pytest.param(PHONE, "M1 from Read's bin", 4, marks=wait(22), id="390x844 M1"),
    ],
)
def test_R40_tab_never_reaches_a_control_outside_the_top_popup(app, viewport, popups, presses):
    page = app(viewport=viewport, storage=sample_state())
    top = open_popups(page, popups)
    for press in range(1, presses + 1):
        page.keyboard.press("Tab")
        outside = page.evaluate(
            """(cls) => { const active = document.activeElement;
              return !!active && active !== document.body && !active.closest('dialog.' + cls); }""",
            top,
        )
        assert not outside, f"Tab {press} reached a control outside dialog.{top}"


@pytest.mark.parametrize(
    "viewport, popup",
    [
        pytest.param(PHONE, "P3", id="390x844 P3"),
        pytest.param(PHONE, "P3, then P4 from its Year", id="390x844 P3 then P4"),
        pytest.param(PHONE, "P2 for Read", id="390x844 P2"),
        pytest.param(DESKTOP, "P1 for 2026-09-22 from the band", id="1280x800 P1"),
        pytest.param(PHONE, "M1 from Read's bin", marks=wait(22), id="390x844 M1"),
    ],
)
def test_R40_every_popup_is_modal_and_the_page_does_not_scroll_under_it(app, viewport, popup):
    page = app(viewport=viewport, storage=sample_state())
    open_popups(page, popup)
    assert all(is_modal(page)) and is_modal(page)
    expect(page.locator("html")).to_have_css("overflow", "hidden")
    for _ in range(5):
        before = open_dialogs(page)
        if not before:
            break
        page.keyboard.press("Escape")
        page.wait_for_function(
            "(count) => Array.from(document.querySelectorAll('dialog')).filter((d) => d.open).length < count",
            arg=len(before),
            timeout=5000,
        )
    assert open_dialogs(page) == []
    expect(page.locator("html")).to_have_css("overflow", "visible")
