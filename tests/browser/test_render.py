"""R3, R4, R5, R6, R35 and R42: what the page draws when it loads (app qa.md, Features "First visit and header",
"Rows, numbers and the list frame", "The overview band", and the browser half of "Rings and the legend").

Each test opens the running app on a named starting state and reads the DOM, computed styles and boxes. Four
scenarios use a feature of a later task, so they carry a strict xfail mark naming that task (qa.md, "Scenarios that
wait on a later task", W3 to W6).
"""
import datetime
import re

import pytest
from playwright.sync_api import expect

from conftest import (
    ARCS3,
    ARCS12,
    CIRCLE_SEG,
    CIRCLE_SEG_ON,
    CORE,
    SAMPLE_HABITS,
    TODAY,
    TODAY_CIRCLE,
    TWELVE,
    add_habit,
    best_block,
    current_block,
    done_btn,
    encode,
    grid_children,
    legend_parts,
    number,
    p3_day,
    ring_of,
    ring_parts,
    row,
    row_numbers,
    sample_state,
    seg,
    short_date,
    stats_tree,
    stored,
    twelve_state,
    year_btn,
)

# The band's 84 places, Monday 20 July to Sunday 11 October. Its weeks are columns of Monday to Sunday, oldest first,
# so grid order is calendar order.
BAND_KEYS = [(datetime.date(2026, 7, 20) + datetime.timedelta(days=i)).isoformat() for i in range(84)]
OPEN_KEYS = BAND_KEYS[:83]


def band_grid(page):
    """The band grid's children: the corner, seven weekday letters, then per week its month label and 7 cells."""
    return grid_children(page, "section.band div.ovg-cols")


def band_cells(grid):
    """The 84 day places of a band grid, in calendar order."""
    weeks = grid[8:]
    return [cell for position, cell in enumerate(weeks) if position % 8 != 0]


def done_count(habits, key):
    return sum(key in habit["done"] for habit in habits)


def band_ring(page, key):
    return ring_parts(page, f'section.band button.hc[data-key="{key}"] > svg')


# ---------------------------------------------------------------------------------------------------------------
# Feature: First visit and header

EMPTY_JS = """() => {
  const empty = document.querySelector('ul.rows > li.empty');
  const svg = empty && empty.querySelector(':scope > svg');
  const field = document.querySelector('#nh');
  const message = document.querySelector('#nh-msg');
  return {
    list: Array.from(document.querySelector('ul.rows').children).map((node) => `${node.localName}.${node.className}`),
    emptyChildren: empty && Array.from(empty.children).map((node) => node.localName),
    svg: svg && {
      viewBox: svg.getAttribute('viewBox'),
      hidden: svg.getAttribute('aria-hidden'),
      circles: Array.from(svg.children).map((node) =>
        [node.localName, node.getAttribute('class'), node.getAttribute('cx'), node.getAttribute('cy'), node.getAttribute('r')]),
    },
    texts: empty && Array.from(empty.querySelectorAll(':scope > div > p')).map((p) => [p.className, p.textContent]),
    rows: document.querySelectorAll('li.row').length,
    banners: document.querySelector('div.banners').childElementCount,
    field: { disabled: field.disabled, value: field.value, invalid: field.hasAttribute('aria-invalid') },
    addDisabled: document.querySelector('#add-btn').disabled,
    message: { hidden: message.hidden, text: message.textContent, classes: message.className },
  };
}"""


def test_R3_R35_R42_the_empty_first_screen(app):
    page = app(viewport=(1280, 800))
    expect(page.locator("ul.rows > li.empty")).to_have_count(1)

    assert page.evaluate(EMPTY_JS) == {
        "list": ["li.empty"],
        "emptyChildren": ["svg", "div"],
        "svg": {
            "viewBox": "0 0 120 120",
            "hidden": "true",
            "circles": [["circle", "e-orbit", "60", "60", "50"], ["circle", "e-core", "60", "60", "18"]],
        },
        "texts": [["lead", "No habits yet."], ["line", "Add one you want to do every day."]],
        "rows": 0,
        "banners": 0,
        "field": {"disabled": False, "value": "", "invalid": False},
        "addDisabled": False,
        "message": {"hidden": True, "text": "", "classes": "field-msg"},
    }

    cells = band_cells(band_grid(page))
    buttons = [cell for cell in cells if cell["tag"] == "button"]
    assert [cell["label"] for cell in buttons] == [f"{short_date(key)}, 0 of 0 habits" for key in OPEN_KEYS]
    assert [cell["key"] for cell in buttons] == OPEN_KEYS
    assert cells[-1] == {
        "tag": "span", "cls": "hc", "hidden": "true", "text": "", "type": None, "key": None,
        "popup": None, "label": None, "current": None, "ring": None,
    }
    for cell in buttons:
        today = cell["key"] == TODAY
        day = int(cell["key"][-2:])
        assert cell["ring"] == ring_of(([TODAY_CIRCLE] if today else []) + [CIRCLE_SEG, number(day)]), cell["key"]
        assert cell["current"] == ("date" if today else None), cell["key"]

    assert legend_parts(page, "section.band div.legend") == ["span:None", ring_of([CIRCLE_SEG]), "span:All"]
    assert stored(page) is None

    page.set_viewport_size({"width": 390, "height": 844})
    assert ring_parts(page, "button.ov-btn > span.ov-ring > svg") == ring_of([CIRCLE_SEG])
    expect(page.locator("button.ov-btn")).to_have_attribute("aria-label", "Overview, today 0 of 0 habits done")


HEADER_JS = """() => {
  const tagged = (nodes) => Array.from(nodes).map((node) => [node.localName, ...node.classList].join('.'));
  const date = document.querySelector('header.top > time.date');
  return {
    top: tagged(document.querySelector('header.top').children),
    brand: tagged(document.querySelector('header.top > div.brand').children),
    word: document.querySelector('div.brand > h1.word').textContent,
    fill: getComputedStyle(document.querySelector('svg.mark path')).fill,
    datetime: date && date.getAttribute('datetime'),
    date: date && date.textContent,
  };
}"""


def test_R4_brand_mark_and_date(app):
    page = app(storage=sample_state())
    assert page.evaluate(HEADER_JS) == {
        "top": ["div.brand", "button.ov-btn", "time.date"],
        "brand": ["svg.mark", "h1.word"],
        "word": "Streaky Habit",
        "fill": "rgb(255, 176, 32)",
        "datetime": "2026-10-10",
        "date": "Saturday 10 October",
    }


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
    date = page.locator("header.top > time.date")
    expect(date).to_have_attribute("datetime", key)
    expect(date).to_have_text(text, use_inner_text=False)


HEADER_BOXES_JS = """() => {
  const box = (selector) => document.querySelector(selector).getBoundingClientRect().toJSON();
  return {
    overview: getComputedStyle(document.querySelector('button.ov-btn')).display,
    brand: box('header.top > div.brand'),
    date: box('header.top > time.date'),
    top: box('header.top'),
  };
}"""


# The scenario reads "inline-flex", the value system.css writes. A grid item's display is blockified, so today.html
# itself computes "flex" in both engines (measured at task 15, BUILD.md). The test asserts what the golden computes.
@pytest.mark.parametrize(
    "viewport, overview",
    [((360, 780), "flex"), ((390, 844), "flex"), ((1280, 800), "none")],
    ids=["360x780", "390x844", "1280x800"],
)
def test_R4_R38_the_header_on_a_phone_and_on_a_desktop(app, viewport, overview):
    page = app(viewport=viewport, storage=sample_state())
    found = page.evaluate(HEADER_BOXES_JS)
    assert found["overview"] == overview
    brand, date = found["brand"], found["date"]
    if overview == "none":
        centre = date["top"] + date["height"] / 2
        assert brand["top"] < centre < brand["bottom"], found
        assert abs(date["right"] - found["top"]["right"]) <= 1, found
    else:
        assert date["top"] > brand["bottom"], found


@pytest.mark.xfail(strict=True, reason="task 19")
def test_R4_english_under_a_german_browser_locale(app):
    page = app(storage=sample_state(), locale="de-DE")
    expect(page.locator("header.top > time.date")).to_have_text("Saturday 10 October")
    expect(page.locator("button.ov-btn")).to_have_attribute("aria-label", "Overview, today 1 of 3 habits done")
    grid = band_grid(page)
    assert band_cells(grid)[0]["label"] == "Mon 20 Jul, 2 of 3 habits"
    months = [cell["text"] for cell in grid[8::8] if cell["text"]]
    assert months == ["Jul", "Aug", "Sep", "Oct"]

    year_btn(page, "Read 20 pages").click()
    expect(page.locator("dialog.dlg-year div.months > section.month h3").first).to_have_text("October 2026")
    expect(page.locator('dialog.dlg-year button.yc[data-key="2026-10-10"]')).to_have_attribute(
        "aria-label", "Mark Sat 10 Oct 2026 as done"
    )


# ---------------------------------------------------------------------------------------------------------------
# Feature: Rows, numbers and the list frame

ROWS_JS = """() => {
  const tagged = (nodes) => Array.from(nodes).map((node) => [node.localName, ...node.classList].join('.'));
  const icon = (svg) => {
    const use = svg && svg.querySelector(':scope > use');
    return svg && [svg.getAttribute('class'), svg.getAttribute('aria-hidden'), use && use.getAttribute('href')];
  };
  const button = (node) => node && {
    type: node.getAttribute('type'),
    popup: node.getAttribute('aria-haspopup'),
    label: node.getAttribute('aria-label'),
    text: node.textContent,
  };
  const list = document.querySelector('ul.rows');
  return {
    labelledby: list.getAttribute('aria-labelledby'),
    rows: Array.from(list.children).map((row) => {
      const name = row.querySelector(':scope > div.r-head > h3');
      const bin = row.querySelector(':scope > div.r-head > button.btn-bin');
      const done = row.querySelector(':scope > button.btn-done');
      const dot = done && done.querySelector(':scope > span.dot');
      return {
        tag: `${row.localName}.${row.className}`,
        children: tagged(row.children),
        head: tagged(row.querySelector(':scope > div.r-head').children),
        name: [name.textContent, name.id],
        stats: row.querySelector(':scope > p.stats').id,
        bin: { ...button(bin), icon: icon(bin.querySelector(':scope > svg')) },
        year: button(row.querySelector(':scope > button.btn-year')),
        done: {
          ...button(done),
          pressed: done.getAttribute('aria-pressed'),
          describedby: done.getAttribute('aria-describedby'),
          dot: dot && icon(dot.querySelector(':scope > svg')),
        },
      };
    }),
  };
}"""


def test_R5_R6_rows_in_stored_order(app):
    page = app(storage=sample_state())
    expect(page.locator("ul.rows > li.row")).to_have_count(3)
    found = page.evaluate(ROWS_JS)
    assert found["labelledby"] == "h-habits"
    pressed = ["true", "false", "false"]
    expected = []
    for position, habit in enumerate(SAMPLE_HABITS, start=1):
        name = habit["name"]
        expected.append(
            {
                "tag": "li.row",
                "children": ["div.r-head", "p.stats", "button.btn-year", "button.btn-done"],
                "head": ["h3.r-name", "button.btn-bin"],
                "name": [name, f"rn-{position}"],
                "stats": f"rs-{position}",
                "bin": {"type": "button", "popup": "dialog", "label": f'Delete "{name}"', "text": "", "icon": ["ph", "true", "#i-trash"]},
                "year": {"type": "button", "popup": "dialog", "label": f"Year view, {name}", "text": "Year"},
                "done": {
                    "type": "button",
                    "popup": None,
                    "label": f"Done today, {name}",
                    "text": "Done today",
                    "pressed": pressed[position - 1],
                    "describedby": f"rs-{position}",
                    "dot": [None, "true", "#i-check"],
                },
            }
        )
    assert [habit["name"] for habit in SAMPLE_HABITS] == ["Read 20 pages", "Stretch 10 minutes", "No phone after 11pm"]
    assert found["rows"] == expected


def row_stats(page, name):
    return stats_tree(row(page, name).locator(":scope > p.stats"))


@pytest.mark.parametrize(
    "habit, current, best",
    [
        ("Read 20 pages", current_block(4, "days"), 9),
        ("Stretch 10 minutes", current_block(2, "days"), 5),
        ("No phone after 11pm", current_block(), 14),
    ],
)
def test_R6_current_and_best_for_the_sample(app, habit, current, best):
    page = app(storage=sample_state())
    expect(page.locator("ul.rows > li.row")).to_have_count(3)
    assert row_stats(page, habit) == [current, best_block(best)]


TWELVE_TABLE = [
    ("Read 20 pages", "4 days", "9", "true"),
    ("Stretch 10 minutes", "2 days", "5", "false"),
    ("No phone after 11pm", "No streak yet", "14", "false"),
    ("Drink 2 litres of water", "1 day", "11", "true"),
    ("Walk 8,000 steps", "1 day", "11", "false"),
    ("Journal one page", "8 days", "11", "true"),
    ("Practise guitar", "1 day", "11", "true"),
    ("Cook dinner at home", "5 days", "11", "true"),
    ("Lights out by midnight", "2 days", "11", "false"),
    ("Meditate 5 minutes", "2 days", "11", "true"),
    ("Floss", "1 day", "11", "true"),
    ("Learn 10 Malay words", "1 day", "11", "false"),
]


def test_R6_R31_twelve_habits_show_the_goldens_numbers(app):
    page = app(storage=twelve_state())
    expect(page.locator("ul.rows > li.row")).to_have_count(12)
    names = page.locator("ul.rows > li.row h3.r-name").all_text_contents()
    found = []
    for name in names:
        numbers = row_numbers(page, name)
        found.append((name, numbers["current"], numbers["best"], done_btn(page, name).get_attribute("aria-pressed")))
    assert found == TWELVE_TABLE
    for _, current, _, _ in found:
        if current != "No streak yet":
            count, unit = current.split(" ")
            assert unit == ("day" if count == "1" else "days"), current


@pytest.mark.xfail(strict=True, reason="task 21")
def test_R6_R10_a_new_habit_shows_no_best_block(app):
    page = app(storage=sample_state())
    add_habit(page, "Drink water")
    expect(page.locator("ul.rows > li.row")).to_have_count(4)
    assert row_stats(page, "Drink water") == [current_block()]


STATES = {"a fresh day": None, "the sample day": sample_state(), "twelve habits": twelve_state()}

PLACES_JS = """() => {
  const box = (selector) => document.querySelector(selector).getBoundingClientRect().toJSON();
  return {
    scrollHeight: document.documentElement.scrollHeight,
    scrollWidth: document.documentElement.scrollWidth,
    composer: box('form.composer'),
    field: box('#nh'),
  };
}"""


@pytest.mark.parametrize("state", list(STATES))
@pytest.mark.parametrize("viewport", [(360, 780), (390, 844), (1280, 800)], ids=["360x780", "390x844", "1280x800"])
def test_R5_R21_the_page_never_scrolls_and_the_composer_stays_put(app, viewport, state):
    fresh = app(viewport=viewport)
    expect(fresh.locator("ul.rows > li.empty")).to_have_count(1)
    expected = fresh.evaluate(PLACES_JS)
    page = app(viewport=viewport, storage=STATES[state])
    expect(page.locator("ul.rows > li")).to_have_count({"a fresh day": 1, "the sample day": 3, "twelve habits": 12}[state])
    found = page.evaluate(PLACES_JS)
    assert found["scrollHeight"] == viewport[1]
    assert found["scrollWidth"] <= viewport[0]
    assert found["field"] == expected["field"]
    # With twelve habits the 12-habit note grows form.composer upward (today-full.html, checklist S3-07 and S3-08), so
    # only the field keeps the fresh day's box there. The scenario's composer line is an open question (BUILD.md, task 15).
    if state != "twelve habits":
        assert found["composer"] == expected["composer"]


FRAME_JS = """() => {
  const frame = document.querySelector('div.frame');
  return {
    scrollTop: frame.scrollTop,
    clientHeight: frame.clientHeight,
    scrollHeight: frame.scrollHeight,
    windowY: window.scrollY,
    classes: Array.from(frame.parentElement.classList),
  };
}"""


def frame_state(page):
    return page.evaluate(FRAME_JS)


def wheel_over_frame(page, delta):
    box = page.locator("div.frame").bounding_box()
    page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    page.mouse.wheel(0, delta)


def test_R5_the_list_scrolls_inside_its_frame_and_shows_where_more_lies(app):
    page = app(storage=twelve_state())
    wrap = page.locator("div.frame-wrap")
    expect(page.locator("ul.rows > li.row")).to_have_count(12)
    found = frame_state(page)
    assert found["scrollHeight"] > found["clientHeight"] and found["scrollTop"] == 0, found
    expect(wrap).to_have_class(re.compile(r"\bmore-below\b"))
    expect(wrap).not_to_have_class(re.compile(r"\bmore-above\b"))

    wheel_over_frame(page, 200)
    page.wait_for_function("() => document.querySelector('div.frame').scrollTop > 0", timeout=5000)
    expect(wrap).to_have_class(re.compile(r"(?=.*\bmore-above\b)(?=.*\bmore-below\b)"))
    assert frame_state(page)["windowY"] == 0

    wheel_over_frame(page, 3000)
    page.wait_for_function(
        "() => { const f = document.querySelector('div.frame'); return f.scrollTop + f.clientHeight >= f.scrollHeight; }",
        timeout=5000,
    )
    expect(wrap).to_have_class(re.compile(r"\bmore-above\b"))
    expect(wrap).not_to_have_class(re.compile(r"\bmore-below\b"))

    wheel_over_frame(page, -3000)
    page.wait_for_function("() => document.querySelector('div.frame').scrollTop === 0", timeout=5000)
    expect(wrap).to_have_class(re.compile(r"\bmore-below\b"))
    expect(wrap).not_to_have_class(re.compile(r"\bmore-above\b"))


def plain_state(count):
    return encode([{"name": f"Habit {n}", "done": []} for n in range(1, count + 1)])


@pytest.mark.xfail(strict=True, reason="task 21")
def test_R5_the_fades_follow_the_rows_and_a_resize(app):
    page = app(storage=plain_state(4))
    wrap = page.locator("div.frame-wrap")
    expect(page.locator("ul.rows > li.row")).to_have_count(4)
    found = frame_state(page)
    assert found["scrollHeight"] == found["clientHeight"], found
    expect(wrap).to_have_class("frame-wrap")

    page.set_viewport_size({"width": 390, "height": 520})
    page.wait_for_function(
        "() => { const f = document.querySelector('div.frame'); return f.scrollHeight > f.clientHeight; }", timeout=5000
    )
    expect(wrap).to_have_class(re.compile(r"\bmore-below\b"))

    page.set_viewport_size({"width": 390, "height": 844})
    expect(wrap).to_have_class("frame-wrap")

    for name in ("Habit 5", "Habit 6", "Habit 7"):
        add_habit(page, name)
    expect(page.locator("ul.rows > li.row")).to_have_count(7)
    found = frame_state(page)
    assert found["scrollHeight"] > found["clientHeight"], found
    above = found["scrollTop"] > 0
    below = found["scrollTop"] + found["clientHeight"] < found["scrollHeight"]
    assert ("more-above" in found["classes"]) == above, found
    assert ("more-below" in found["classes"]) == below, found
    assert above or below, found


# ---------------------------------------------------------------------------------------------------------------
# Feature: The overview band

BAND_META_JS = """() => {
  const band = document.querySelector('section.band');
  const tagged = (nodes) => Array.from(nodes).map((node) => [node.localName, ...node.classList].join('.'));
  const meta = band.querySelector(':scope > div.band-meta');
  const head = meta.querySelector(':scope > div.band-head');
  const year = head.querySelector(':scope > button.btn-all');
  const grid = band.querySelector(':scope > div.ovg-cols');
  return {
    labelledby: band.getAttribute('aria-labelledby'),
    display: getComputedStyle(band).display,
    meta: tagged(meta.children),
    head: tagged(head.children),
    title: [head.querySelector(':scope > h2').id, head.querySelector(':scope > h2').textContent],
    year: [year.getAttribute('type'), year.getAttribute('aria-haspopup'), year.getAttribute('aria-label'), year.textContent],
    hint: meta.querySelector(':scope > p.hint').textContent,
    legendHidden: meta.querySelector(':scope > div.legend').getAttribute('aria-hidden'),
    grid: [grid.getAttribute('role'), grid.getAttribute('aria-labelledby'), grid.childElementCount],
  };
}"""


def test_R35_R42_the_band_on_a_desktop(app):
    page = app(viewport=(1280, 800), storage=sample_state())
    expect(page.locator("section.band div.ovg-cols > button.hc")).to_have_count(83)
    assert page.evaluate(BAND_META_JS) == {
        "labelledby": "h-ov",
        "display": "grid",
        "meta": ["div.band-head", "p.hint", "div.legend"],
        "head": ["h2", "button.btn-all"],
        "title": ["h-ov", "Last 12 weeks"],
        "year": ["button", "dialog", "Year view, all habits", "Year"],
        "hint": "Tap a day to change it.",
        "legendHidden": "true",
        "grid": ["group", "h-ov", 104],
    }

    grid = band_grid(page)
    assert grid[0] == {
        "tag": "div", "cls": None, "hidden": "true", "text": "", "type": None, "key": None,
        "popup": None, "label": None, "current": None, "ring": None,
    }
    assert [(cell["cls"], cell["hidden"], cell["text"]) for cell in grid[1:8]] == [
        ("og-wd", "true", letter) for letter in "MTWTFSS"
    ]
    months = grid[8::8]
    assert [(cell["tag"], cell["cls"], cell["hidden"]) for cell in months] == [("div", "og-mo", "true")] * 12
    assert [cell["text"] for cell in months] == ["Jul", "", "Aug", "", "", "", "", "Sep", "", "", "", "Oct"]

    cells = band_cells(grid)
    buttons = cells[:83]
    assert [(cell["tag"], cell["cls"], cell["type"], cell["popup"]) for cell in buttons] == [
        ("button", "hc", "button", "dialog")
    ] * 83
    assert [cell["key"] for cell in buttons] == OPEN_KEYS
    assert (cells[83]["tag"], cells[83]["cls"], cells[83]["hidden"], cells[83]["ring"], cells[83]["text"]) == (
        "span", "hc", "true", None, ""
    )
    assert [cell["label"] for cell in buttons] == [
        f"{short_date(key)}, {done_count(SAMPLE_HABITS, key)} of 3 habits" for key in OPEN_KEYS
    ]
    labels = {cell["key"]: cell["label"] for cell in buttons}
    assert labels["2026-07-20"] == "Mon 20 Jul, 2 of 3 habits"
    assert labels["2026-09-22"] == "Tue 22 Sep, 1 of 3 habits"
    assert labels["2026-10-10"] == "Sat 10 Oct, 1 of 3 habits"
    assert [cell["key"] for cell in buttons if cell["current"]] == [TODAY]
    assert [cell["current"] for cell in buttons if cell["current"]] == ["date"]

    tally = {0: 0, 1: 0, 2: 0, 3: 0}
    for cell in buttons:
        parts = cell["ring"]["parts"]
        on = sum(part.startswith("path.seg.on") for part in parts)
        assert on == done_count(SAMPLE_HABITS, cell["key"]), cell["key"]
        tally[on] += 1
        full = on == 3
        assert (CORE in parts) == full, cell["key"]
        assert parts[-1] == number(int(cell["key"][-2:]), on=full), cell["key"]
    assert tally == {0: 2, 1: 16, 2: 47, 3: 18}

    legend = legend_parts(page, "section.band div.legend")
    assert legend == [
        "span:None",
        ring_of([seg(ARCS3[0], False), seg(ARCS3[1], False), seg(ARCS3[2], False)]),
        ring_of([seg(ARCS3[0], True), seg(ARCS3[1], False), seg(ARCS3[2], False)]),
        ring_of([seg(ARCS3[0], True), seg(ARCS3[1], True), seg(ARCS3[2], False)]),
        ring_of([seg(ARCS3[0], True), seg(ARCS3[1], True), seg(ARCS3[2], True), CORE]),
        "span:All",
    ]


@pytest.mark.parametrize(
    "viewport, display",
    [((390, 844), "none"), ((1023, 800), "none"), ((1024, 800), "grid"), ((1280, 800), "grid")],
    ids=["390x844", "1023x800", "1024x800", "1280x800"],
)
def test_R35_the_band_shows_from_1024_pixels(app, viewport, display):
    page = app(viewport=viewport, storage=sample_state())
    expect(page.locator("section.band div.ovg-cols > button.hc")).to_have_count(83)
    expect(page.locator("section.band")).to_have_css("display", display)


# ---------------------------------------------------------------------------------------------------------------
# Feature: Rings and the legend (browser scenarios)


def test_R42_a_rings_parts_and_their_order(app):
    page = app(viewport=(1280, 800), storage=sample_state())
    expect(page.locator("section.band div.ovg-cols > button.hc")).to_have_count(83)
    assert band_ring(page, "2026-10-10") == ring_of(
        [TODAY_CIRCLE, seg(ARCS3[0], True), seg(ARCS3[1], False), seg(ARCS3[2], False), number(10)]
    )
    assert band_ring(page, "2026-07-21") == ring_of(
        [seg(ARCS3[0], True), seg(ARCS3[1], True), seg(ARCS3[2], True), CORE, number(21, on=True)]
    )
    assert band_ring(page, "2026-09-27") == ring_of(
        [seg(ARCS3[0], False), seg(ARCS3[1], False), seg(ARCS3[2], False), number(27)]
    )


@pytest.mark.parametrize(
    "storage, parts",
    [
        ('{"version":1,"habits":[]}', [TODAY_CIRCLE, CIRCLE_SEG, number(10)]),
        ('{"version":1,"habits":[{"name":"Read","done":[]}]}', [TODAY_CIRCLE, CIRCLE_SEG, number(10)]),
        ('{"version":1,"habits":[{"name":"Read","done":["2026-10-10"]}]}', [TODAY_CIRCLE, CIRCLE_SEG_ON, CORE, number(10, on=True)]),
    ],
    ids=["no habit", "one habit not done", "one habit done"],
)
def test_R42_rings_for_no_habit_and_for_one_habit(app, storage, parts):
    page = app(viewport=(1280, 800), storage=storage)
    expect(page.locator("section.band div.ovg-cols > button.hc")).to_have_count(83)
    assert band_ring(page, "2026-10-10") == ring_of(parts)


def test_R42_twelve_habits_draw_twelve_segments(app):
    page = app(viewport=(1280, 800), storage=twelve_state())
    expect(page.locator("section.band div.ovg-cols > button.hc")).to_have_count(83)
    cells = band_cells(band_grid(page))[:83]
    for cell in cells:
        segments = [part for part in cell["ring"]["parts"] if part.startswith("path")]
        flags = [key_done(habit, cell["key"]) for habit in TWELVE]
        assert segments == [seg(ARCS12[i], flags[i]) for i in range(12)], cell["key"]

    legend = legend_parts(page, "section.band div.legend")
    assert legend[0] == "span:None" and legend[-1] == "span:All"
    expected = []
    for count in (0, 4, 8, 12):
        parts = [seg(ARCS12[i], i < count) for i in range(12)]
        expected.append(ring_of(parts + ([CORE] if count == 12 else [])))
    assert legend[1:-1] == expected


def key_done(habit, key):
    return key in habit["done"]


def test_R42_small_rings_carry_no_number_and_no_today_circle(app):
    page = app(storage=sample_state())
    three = [seg(ARCS3[0], True), seg(ARCS3[1], False), seg(ARCS3[2], False)]
    assert ring_parts(page, "button.ov-btn > span.ov-ring > svg") == ring_of(three)
    page.locator("button.ov-btn").click()
    p3_day(page, TODAY).click()
    expect(page.locator("dialog.dlg-day")).to_have_attribute("open", "")
    assert ring_parts(page, "dialog.dlg-day div.day-mini > svg") == ring_of(three)
