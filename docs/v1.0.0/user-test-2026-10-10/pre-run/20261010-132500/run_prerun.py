# UAT pre-run driver for Streaks 1.0.0 (read-only on the product, never edits TEST-CASES.md).
# Usage: python run_prerun.py <evidence folder>
# One browser, one fresh context, cases run in written order, real clock, real hit-tested gestures only.
# Revision 2: the first run's three UAT-05/06 "FAIL" checks were my measurement (legend dot width read through an
# anti-aliased row, and the ring's declared 1.5px drawn as 1px at 1x), and the midnight extra passed the fake time in
# the wrong unit. Those are fixed here; the product behaviour seen in run 1 is unchanged.
import io
import json
import sys
import time
import traceback
from datetime import datetime, timedelta, timezone
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8731/"
OUT = Path(sys.argv[1])
VIEWPORT = {"width": 1280, "height": 800}
GREENS = [(59, 107, 96), (46, 90, 80)]
THREAD = (198, 208, 204)
BG = (242, 245, 243)
SURFACE = (250, 252, 251)
HUMAN_MS = 900  # a person takes about a second between two steps

CASES = []
EXTRAS = {}
CONSOLE = []
ISO = dict.fromkeys([0x2068, 0x2069])


def strip_iso(text):
    return text.translate(ISO)


def near(a, b, tol):
    return all(abs(x - y) <= tol for x, y in zip(a, b))


def is_green(px):
    return any(near(px, g, 30) for g in GREENS)


class Case:
    def __init__(self, cid, title):
        self.cid, self.title = cid, title
        self.checks, self.notes, self.shots = [], [], []
        self.crashed = None
        print(f"\n=== {cid}: {title}")

    def check(self, name, ok, detail=""):
        self.checks.append({"name": name, "ok": bool(ok), "detail": detail})
        print(("  ok    " if ok else "  FAIL  ") + name + ((" :: " + str(detail)) if detail != "" else ""))

    def note(self, text):
        self.notes.append(text)
        print("  note  " + text)

    def shot(self, page, name, **kw):
        path = OUT / name
        page.screenshot(path=str(path), **kw)
        self.shots.append(name)
        size = path.stat().st_size
        self.check(f"screenshot {name} is not empty", size > 2000, f"{size} bytes")

    def to_json(self):
        return {
            "id": self.cid,
            "title": self.title,
            "auto_all_checks_ok": all(c["ok"] for c in self.checks) and not self.crashed,
            "crashed": self.crashed,
            "shots": self.shots,
            "notes": self.notes,
            "checks": self.checks,
        }


SNAP_JS = """() => {
  const rows = [...document.querySelectorAll('.habits > .habit')].map(li => {
    const btns = [...li.querySelectorAll('button.day')];
    return {
      name: li.querySelector('h3').textContent,
      cur: li.querySelector('.streak .cur') ? li.querySelector('.streak .cur').textContent : null,
      curClass: li.querySelector('.streak .cur') ? li.querySelector('.streak .cur').className : null,
      best: li.querySelector('.streak .best') ? li.querySelector('.streak .best').textContent : null,
      pressed: btns.map(b => b.getAttribute('aria-pressed')),
      labels: btns.map(b => b.getAttribute('aria-label')),
      current: btns.map(b => b.hasAttribute('aria-current')),
      runContinues: li.querySelector('.strip').hasAttribute('data-run-continues'),
      deleteLabel: li.querySelector('.icon-btn').getAttribute('aria-label'),
    };
  });
  const heat = [...document.querySelectorAll('.cells > .hc')].map(c => ({
    date: c.getAttribute('data-date'), cls: c.className, label: c.getAttribute('aria-label')}));
  const msg = document.querySelector('#new-habit-msg');
  const field = document.querySelector('#new-habit');
  return {
    rows, heat,
    empty: !!document.querySelector('.empty'),
    emptyText: document.querySelector('.empty') ? document.querySelector('.empty').textContent : null,
    msg: msg.textContent, msgClass: msg.className, msgColor: getComputedStyle(msg).color,
    msgDisplay: getComputedStyle(msg).display,
    fieldValue: field.value, fieldInvalid: field.getAttribute('aria-invalid'),
    headerText: document.querySelector('.date time').textContent,
    headerDatetime: document.querySelector('.date time').getAttribute('datetime'),
    dialogOpen: document.querySelectorAll('dialog[open]').length,
    active: document.activeElement ? (document.activeElement.tagName + '#' + document.activeElement.id + '.' + document.activeElement.className) : null,
    storage: Object.fromEntries(Object.entries(localStorage)),
  };
}"""

CS_JS = """(el, p) => { const c = getComputedStyle(el, p || null);
  return {width: c.width, height: c.height, backgroundColor: c.backgroundColor, backgroundImage: c.backgroundImage,
          boxShadow: c.boxShadow, border: c.borderTopWidth + ' ' + c.borderTopColor, color: c.color, opacity: c.opacity}; }"""


def snap(page):
    return page.evaluate(SNAP_JS)


def pause(page, ms=HUMAN_MS):
    page.wait_for_timeout(ms)


def shot_img(page):
    return Image.open(io.BytesIO(page.screenshot())).convert("RGB")


def hit_click(case, page, loc, label):
    """Assert elementFromPoint at the click point resolves inside the intended element, then a real click."""
    box = loc.bounding_box()
    if box is None:
        case.check(f"{label}: found on screen", False, "no bounding box")
        raise RuntimeError("no box for " + label)
    cx, cy = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
    res = loc.evaluate(
        "(el,p)=>{const t=document.elementFromPoint(p[0],p[1]);if(!t)return {ok:false,hit:null};"
        "const cn=(t.className&&t.className.baseVal!==undefined)?t.className.baseVal:t.className;"
        "return {ok:el.contains(t),hit:t.tagName+'.'+cn};}",
        [cx, cy],
    )
    case.check(f"hit-test {label}", res["ok"], f"elementFromPoint({cx:.0f},{cy:.0f}) -> {res['hit']}")
    if not res["ok"]:
        raise RuntimeError("hit-test failed for " + label)
    loc.click(timeout=5000)


def habit_row(page, name):
    return page.locator("li.habit").filter(has=page.locator("h3", has_text=name))


def bead(row, i):
    return row.locator("button.day").nth(i).locator(".bead")


def bead_probe(img, box):
    cx, cy = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
    fill = img.getpixel((round(cx), round(cy - box["height"] * 0.33)))
    white = 0
    for x in range(round(cx) - 8, round(cx) + 9):
        for y in range(round(cy) - 8, round(cy) + 9):
            r, g, b = img.getpixel((x, y))
            if r >= 245 and g >= 248 and b >= 247:
                white += 1
    return {"fill_px": fill, "filled": is_green(fill), "hollow": near(fill, BG, 6), "check_white_px": white}


def classify_gap(cols):
    n = len(cols)
    if n < 6:
        return "n/a", {}
    thick = [g >= 3 for g, t in cols]
    frac = sum(thick) / n
    runs = sum(1 for k in range(n) if thick[k] and (k == 0 or not thick[k - 1]))
    thinfrac = sum(1 for g, t in cols if t >= 1 and g == 0) / n
    maxg = max(g for g, t in cols)
    maxt = max(t for g, t in cols)
    if frac >= 0.95:
        label = "thick"
    elif runs >= 3 and frac >= 0.3:
        label = "dashed"
    elif thinfrac >= 0.9:
        label = "thin"
    elif frac > 0:
        label = "partial"
    else:
        label = "none"
    return label, {"px": n, "green_frac": round(frac, 2), "green_runs": runs, "max_green_rows": maxg, "max_thread_rows": maxt}


def strip_profile(page, row):
    """Reads the PAINTED pixels between each pair of adjacent beads: returns beads state and 6 gap labels."""
    img = shot_img(page)
    boxes = [bead(row, i).bounding_box() for i in range(7)]
    beads = [bead_probe(img, b) for b in boxes]
    gaps = []
    for i in range(6):
        a, b = boxes[i], boxes[i + 1]
        cy = round(a["y"] + a["height"] / 2)
        x0 = int(a["x"] + a["width"]) + 2
        x1 = int(b["x"]) - 2 - (7 if i + 1 == 6 else 0)
        cols = []
        for x in range(x0, x1):
            g = t = 0
            for y in range(cy - 8, cy + 9):
                px = img.getpixel((x, y))
                if is_green(px):
                    g += 1
                elif near(px, THREAD, 10):
                    t += 1
            cols.append((g, t))
        label, info = classify_gap(cols)
        gaps.append({"gap": f"{i}-{i + 1}", "label": label, **info})
    return beads, gaps


def gap_labels(gaps):
    return [g["label"] for g in gaps]


def run_width(img, cx, cy, ref):
    """Widest contiguous run of dot-coloured pixels through the dot's centre (three rows, so a half-pixel offset cannot shave it)."""
    best = 0
    for dy in (-1, 0, 1):
        y = cy + dy
        left = right = 0
        x = cx
        while x >= 0 and near(img.getpixel((x, y)), ref, 40):
            left += 1
            x -= 1
        x = cx + 1
        while x < img.width and near(img.getpixel((x, y)), ref, 40):
            right += 1
            x += 1
        best = max(best, left + right)
    return best


def heat_probe(page):
    img = shot_img(page)
    out = {}
    today = page.locator(".cells .hc.today")
    out["today_cells"] = today.count()
    box = today.bounding_box()
    cx, cy = round(box["x"] + box["width"] / 2), round(box["y"] + box["height"] / 2)
    ref = img.getpixel((cx, cy))
    out["cls"] = today.get_attribute("class")
    out["label"] = today.get_attribute("aria-label")
    out["center_px"] = ref
    out["dot_px_width"] = run_width(img, cx, cy, ref)
    out["css_dot"] = today.evaluate(CS_JS, "::before")
    out["css_ring"] = today.evaluate(CS_JS, "::after")
    # the ring as painted: a ring-coloured pixel on the centre row, 9 to 13 px left of the centre
    out["ring_px_found"] = any(near(img.getpixel((cx - d, cy)), (126, 142, 136), 40) for d in range(9, 14))
    legend = {}
    for lv in "01234":
        e = page.locator(f".legend .hc.l{lv}")
        b = e.bounding_box()
        lx, ly = round(b["x"] + b["width"] / 2), round(b["y"] + b["height"] / 2)
        lref = img.getpixel((lx, ly))
        css = e.evaluate(CS_JS, "::before")
        legend[lv] = {"css_w": css["width"], "css_bg": css["backgroundColor"], "center_px": lref, "dot_px_width": run_width(img, lx, ly, lref)}
    out["legend"] = legend
    return out


def attach(page, tag):
    page.on("console", lambda m: CONSOLE.append({"page": tag, "type": m.type, "text": m.text}) if m.type in ("error", "warning") else None)
    page.on("pageerror", lambda e: CONSOLE.append({"page": tag, "type": "pageerror", "text": str(e)}))


# --------------------------------------------------------------------------------------------------
def uat01(page):
    c = Case("UAT-01", "I can add a habit by name")
    s = snap(page)
    c.check("precondition: empty first screen", s["empty"] and "No habits yet." in s["emptyText"] and "Add one you want to do every day." in s["emptyText"], s["emptyText"])
    c.check("precondition: nothing saved in this browser", s["storage"] == {}, s["storage"])
    c.check("page title and header", page.title() == "Streaks", f"{page.title()} / {s['headerText']} / {s['headerDatetime']}")

    # step 1
    field = page.get_by_label("New habit")
    lb, fb = page.locator("label.add-label").bounding_box(), field.bounding_box()
    c.check("step 1: the field sits under the 'New habit' label", fb["y"] >= lb["y"] + lb["height"] - 1, f"label y={lb['y']:.0f} h={lb['height']:.0f}, field y={fb['y']:.0f}")
    hit_click(c, page, field, "step 1 text field")
    c.check("step 1: field has focus", page.evaluate("document.activeElement.id") == "new-habit")
    pause(page)
    # step 2
    page.keyboard.type("Read 20 pages", delay=40)
    c.check("step 2: typed text is in the field", field.input_value() == "Read 20 pages", field.input_value())
    pause(page)
    # step 3
    add = page.get_by_role("button", name="Add", exact=True)
    ab = add.bounding_box()
    c.check("step 3: Add is to the right of the field", ab["x"] >= fb["x"] + fb["width"] - 1, f"field right={fb['x'] + fb['width']:.0f}, Add x={ab['x']:.0f}")
    bg = add.evaluate(CS_JS)["backgroundColor"]
    c.check("step 3: Add is green", bg == "rgb(59, 107, 96)", bg)
    hit_click(c, page, add, "step 3 Add button")
    pause(page, 700)
    s = snap(page)
    c.check("step 3: one habit 'Read 20 pages' appears", [r["name"] for r in s["rows"]] == ["Read 20 pages"], [r["name"] for r in s["rows"]])
    r = s["rows"][0] if s["rows"] else None
    if r:
        c.check("step 3: 7 day circles, all hollow (aria-pressed false)", len(r["pressed"]) == 7 and all(p == "false" for p in r["pressed"]), r["pressed"])
        c.check("step 3: last 7 days, today (Sat 10 Oct) last with aria-current", r["labels"][-1] == "Mark Sat 10 Oct as done" and r["current"] == [False] * 6 + [True], r["labels"])
        c.check("step 3: line reads 'No streak yet'", r["cur"] == "No streak yet" and r["best"] is None, (r["cur"], r["best"]))
        row = habit_row(page, "Read 20 pages")
        ring = bead(row, 6).evaluate(CS_JS)["boxShadow"]
        c.check("step 3: today's circle has a thin ring (box-shadow)", ring != "none" and "rgb(126, 142, 136)" in ring, ring)
        beads, gaps = strip_profile(page, row)
        c.check("step 3 PAINT: all 7 circles are hollow in the screenshot pixels", all(b["hollow"] for b in beads), [b["fill_px"] for b in beads])
        c.note("gap profile after step 3: " + str(gap_labels(gaps)))
    c.note("after step 3 the field holds " + repr(s["fieldValue"]) + "; keyboard focus is on " + str(s["active"]))
    c.shot(page, "uat01-step3.png")
    focus_after_add = s["active"]
    pause(page)

    # step 4: literal, no click on the field first (the script says "in the same field")
    page.keyboard.type("Stretch 10 minutes", delay=40)
    pause(page, 400)
    s = snap(page)
    landed = s["fieldValue"] == "Stretch 10 minutes"
    c.check("step 4 LITERAL: typing 'Stretch 10 minutes' without clicking the field lands in the field", landed,
            f"field value={s['fieldValue']!r}, msg={s['msg']!r}, focus before typing was {focus_after_add}")
    if not landed:
        c.note(f"SCRIPT GAP: after step 3 focus is on {focus_after_add}, so step 4 did not land. Field now {s['fieldValue']!r}, message {s['msg']!r}, rows {[r['name'] for r in s['rows']]}")
        c.shot(page, "uat01-step4-literal-typing-lost.png")
        # recover the way a person would: click the field, clear it, type again
        field = page.get_by_label("New habit")
        hit_click(c, page, field, "recovery: click the field")
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        page.keyboard.type("Stretch 10 minutes", delay=40)
        c.check("step 4 RECOVERED: text now in field", field.input_value() == "Stretch 10 minutes", field.input_value())
    pause(page)
    # step 5
    page.keyboard.press("Enter")
    pause(page, 700)
    s = snap(page)
    names = [r["name"] for r in s["rows"]]
    c.check("step 5: 'Stretch 10 minutes' appears under 'Read 20 pages'", names == ["Read 20 pages", "Stretch 10 minutes"], names)
    ys = [habit_row(page, n).bounding_box()["y"] for n in names] if len(names) == 2 else []
    c.check("step 5: second habit is physically below the first", len(ys) == 2 and ys[1] > ys[0], ys)
    c.check("step 5: field cleared and no error shown after a good add", s["fieldValue"] == "" and s["msg"] == "", (s["fieldValue"], s["msg"]))
    c.shot(page, "uat01-step5.png")
    pause(page)
    # step 6
    page.keyboard.type("read 20 pages", delay=40)
    c.check("step 6: lower-case text is in the field", page.get_by_label("New habit").input_value() == "read 20 pages", page.get_by_label("New habit").input_value())
    pause(page)
    # step 7
    page.keyboard.press("Enter")
    pause(page, 700)
    s = snap(page)
    names = [r["name"] for r in s["rows"]]
    c.check("step 7: no third habit", names == ["Read 20 pages", "Stretch 10 minutes"], names)
    c.check("step 7: red text reads 'You already track this habit.'", s["msg"] == "You already track this habit." and s["msgDisplay"] != "none", s["msg"])
    c.check("step 7: the text is red (rgb(162, 59, 50))", s["msgColor"] == "rgb(162, 59, 50)", s["msgColor"])
    c.check("step 7: your typed text stays in the field", s["fieldValue"] == "read 20 pages", s["fieldValue"])
    mb = page.locator("#new-habit-msg").bounding_box()
    c.check("step 7: the message is under the field", mb is not None and mb["y"] > fb["y"], mb)
    c.shot(page, "uat01-final.png", full_page=True)
    return c


def uat02(page):
    c = Case("UAT-02", "I can tick and untick the days of this week")
    s = snap(page)
    c.check("precondition: two habits, nothing ticked", [r["name"] for r in s["rows"]] == ["Read 20 pages", "Stretch 10 minutes"] and all(p == "false" for r in s["rows"] for p in r["pressed"]))
    # precondition: clear the field (select its text and delete it)
    field = page.get_by_label("New habit")
    hit_click(c, page, field, "precondition: click the field")
    page.keyboard.press("Control+A")
    page.keyboard.press("Delete")
    s = snap(page)
    c.check("precondition: field is empty after select-all + Delete", s["fieldValue"] == "", repr(s["fieldValue"]))
    c.note(f"after clearing, the red message reads {s['msg']!r} (it stays until the next add)")
    pause(page)
    row = habit_row(page, "Read 20 pages")

    def tick(i, label):
        hit_click(c, page, bead(row, i), label)
        pause(page, 650)
        return snap(page)["rows"][0], *strip_profile(page, row)

    # step 1
    r, beads, gaps = tick(6, "step 1 today's circle")
    c.check("step 1: today's circle is ticked (aria-pressed true), nothing else", r["pressed"] == ["false"] * 6 + ["true"], r["pressed"])
    c.check("step 1 PAINT: today's circle is filled green with a white check", beads[6]["filled"] and beads[6]["check_white_px"] >= 8, beads[6])
    c.note("step 1 gap profile: " + str(gap_labels(gaps)) + "; streak line: " + str((r["cur"], r["best"])))
    row.screenshot(path=str(OUT / "uat02-step1-row.png")); c.shots.append("uat02-step1-row.png")
    pause(page)
    # step 2
    r, beads, gaps = tick(5, "step 2 yesterday's circle")
    c.check("step 2: yesterday and today ticked", r["pressed"] == ["false"] * 5 + ["true", "true"], r["pressed"])
    c.check("step 2 PAINT: both circles filled green", beads[5]["filled"] and beads[6]["filled"], (beads[5]["fill_px"], beads[6]["fill_px"]))
    c.check("step 2 PAINT: a thick green line joins the two filled circles", gaps[5]["label"] == "thick", gaps[5])
    c.check("step 2 PAINT: no other gap is thick", [g["label"] for g in gaps[:5]].count("thick") == 0, gap_labels(gaps))
    row.screenshot(path=str(OUT / "uat02-step2-row.png")); c.shots.append("uat02-step2-row.png")
    pause(page)
    # step 3
    r, beads, gaps = tick(6, "step 3 today's circle again")
    c.check("step 3: today is unticked, yesterday still ticked", r["pressed"] == ["false"] * 5 + ["true", "false"], r["pressed"])
    c.check("step 3 PAINT: today is a hollow circle", beads[6]["hollow"], beads[6])
    c.note("step 3 gap profile (what joins yesterday to the open circle): " + str(gap_labels(gaps)))
    row.screenshot(path=str(OUT / "uat02-step3-row.png")); c.shots.append("uat02-step3-row.png")
    pause(page)
    # step 4
    r, beads, gaps = tick(6, "step 4 today's circle once more")
    c.check("step 4: today ticked again", r["pressed"] == ["false"] * 5 + ["true", "true"], r["pressed"])
    c.check("step 4 PAINT: today filled again", beads[6]["filled"] and beads[6]["check_white_px"] >= 8, beads[6])
    c.check("step 4 PAINT: joined to yesterday by a thick line", gaps[5]["label"] == "thick", gaps[5])
    c.shot(page, "uat02-final.png", full_page=True)
    return c


def uat03(page):
    c = Case("UAT-03", "The streak counts days in a row and does not break before today is over")
    row = habit_row(page, "Read 20 pages")
    s = snap(page)["rows"][0]
    c.check("precondition: yesterday and today ticked", s["pressed"][5:] == ["true", "true"], s["pressed"])
    # step 1
    cur, best = row.locator(".streak .cur"), row.locator(".streak .best")
    cur_css, best_css = cur.evaluate(CS_JS), best.evaluate(CS_JS)
    c.check("step 1: line reads '2 days' then 'Best 2'", (s["cur"], s["best"]) == ("2 days", "Best 2"), (s["cur"], s["best"]))
    c.check("step 1: '2 days' is green", cur_css["color"] == "rgb(46, 90, 80)", cur_css["color"])
    c.check("step 1: 'Best 2' is grey", best_css["color"] == "rgb(82, 96, 91)", best_css["color"])
    cb, bb = cur.bounding_box(), best.bounding_box()
    c.check("step 1: 'Best 2' comes after '2 days' on the same line", bb["x"] > cb["x"] + cb["width"] - 1 and abs(bb["y"] - cb["y"]) < 8, (cb, bb))
    row.screenshot(path=str(OUT / "uat03-step1-row.png")); c.shots.append("uat03-step1-row.png")
    pause(page)
    # step 2
    hit_click(c, page, bead(row, 6), "step 2 today's circle")
    pause(page, 700)
    # step 3
    s = snap(page)["rows"][0]
    beads, gaps = strip_profile(page, row)
    c.check("step 3: line reads '1 day'", s["cur"] == "1 day", (s["cur"], s["best"]))
    c.check("step 3: today's circle is open (hollow), yesterday still ticked", s["pressed"][5:] == ["true", "false"] and beads[6]["hollow"], (s["pressed"], beads[6]["fill_px"]))
    c.check("step 3 PAINT: a dashed green line runs from yesterday into today's open circle", gaps[5]["label"] == "dashed", gaps[5])
    c.note("step 3 streak line: " + str((s["cur"], s["best"])) + " (the script does not mention the Best figure here)")
    row.screenshot(path=str(OUT / "uat03-step3-row.png")); c.shots.append("uat03-step3-row.png")
    pause(page)
    # step 4
    hit_click(c, page, bead(row, 6), "step 4 today's circle")
    pause(page, 700)
    s = snap(page)["rows"][0]
    beads, gaps = strip_profile(page, row)
    c.check("step 4: line reads '2 days' again", (s["cur"], s["best"]) == ("2 days", "Best 2"), (s["cur"], s["best"]))
    c.check("step 4 PAINT: solid (thick, not dashed) line", gaps[5]["label"] == "thick", gaps[5])
    c.shot(page, "uat03-final.png", full_page=True)
    return c


def uat04(page):
    c = Case("UAT-04", "The best streak remembers the longest run")
    row = habit_row(page, "Stretch 10 minutes")
    s = snap(page)
    c.check("precondition: UAT-03 done and 'Stretch 10 minutes' has nothing ticked",
            s["rows"][0]["cur"] == "2 days" and all(p == "false" for p in s["rows"][1]["pressed"]), (s["rows"][0]["cur"], s["rows"][1]["pressed"]))
    for i, step in ((1, "step 1: 2nd circle from the left"), (2, "step 2: 3rd circle from the left"), (3, "step 3: 4th circle from the left"), (6, "step 4: rightmost circle (today)")):
        lbl = row.locator("button.day").nth(i).get_attribute("aria-label")
        c.note(f"{step} is {lbl}")
        hit_click(c, page, bead(row, i), step)
        pause(page, 700)
    # step 5
    s = snap(page)["rows"][1]
    beads, gaps = strip_profile(page, row)
    c.check("step 5: line reads '1 day' then 'Best 3'", (s["cur"], s["best"]) == ("1 day", "Best 3"), (s["cur"], s["best"]))
    c.check("ticked circles are the 2nd, 3rd, 4th and today", s["pressed"] == ["false", "true", "true", "true", "false", "false", "true"], s["pressed"])
    c.check("PAINT: 2nd-3rd-4th are joined by one thick line (gaps 1-2 and 2-3)", gaps[1]["label"] == "thick" and gaps[2]["label"] == "thick", gap_labels(gaps))
    c.check("PAINT: the run is not joined to circle 1 or to circle 5 (gaps 0-1 and 3-4 are not thick)", gaps[0]["label"] != "thick" and gaps[3]["label"] != "thick", gap_labels(gaps))
    c.check("PAINT: today is filled but not joined to the run (gap 5-6 not thick, not dashed)", beads[6]["filled"] and gaps[5]["label"] in ("thin", "none"), (beads[6]["fill_px"], gaps[5]))
    c.note("gap profile: " + str(gap_labels(gaps)))
    row.screenshot(path=str(OUT / "uat04-row.png")); c.shots.append("uat04-row.png")
    c.shot(page, "uat04-final.png", full_page=True)
    return c


def uat05(page):
    c = Case("UAT-05", "The heatmap shows how much of each day got done")
    s = snap(page)
    c.check("precondition: both habits have today ticked", all(r["pressed"][6] == "true" for r in s["rows"]), [r["pressed"][6] for r in s["rows"]])
    hb, mb = page.locator("section.heat").bounding_box(), page.locator(".col-main").bounding_box()
    c.check("panel 'Last 12 weeks' is on the right on a wide window", page.locator("#heat-title").inner_text() == "Last 12 weeks" and hb["x"] >= mb["x"] + mb["width"], f"heat x={hb['x']:.0f}, main right={mb['x'] + mb['width']:.0f}")
    c.check("panel is on screen without scrolling", hb["y"] + hb["height"] <= VIEWPORT["height"], f"heat y={hb['y']:.0f} h={hb['height']:.0f}")
    # step 1
    h = heat_probe(page)
    leg4 = h["legend"]["4"]
    c.check("step 1: exactly one ringed (today) dot", h["today_cells"] == 1, h["today_cells"])
    c.check("step 1: today's dot is the largest kind (class l4, 17px)", " l4" in (" " + h["cls"]) and h["css_dot"]["width"] == "17px", (h["cls"], h["css_dot"]["width"]))
    c.check("step 1 PAINT: the painted dot is as wide and as dark as 'All' in the legend",
            h["center_px"] == leg4["center_px"] and abs(h["dot_px_width"] - leg4["dot_px_width"]) <= 1 and h["css_dot"]["width"] == leg4["css_w"] and h["css_dot"]["backgroundColor"] == leg4["css_bg"],
            f"today px={h['center_px']} w={h['dot_px_width']} css={h['css_dot']['width']}/{h['css_dot']['backgroundColor']}; legend All px={leg4['center_px']} w={leg4['dot_px_width']} css={leg4['css_w']}/{leg4['css_bg']}")
    c.check("step 1: a thin ring around it (22px wide, ring-coloured border, painted)", h["css_ring"]["width"] == "22px" and h["css_ring"]["border"].endswith("rgb(126, 142, 136)") and h["ring_px_found"],
            f"{h['css_ring']['width']} / border {h['css_ring']['border']} (declared 1.5px; Chromium draws 1px at 1x) / painted ring pixel found={h['ring_px_found']}")
    c.note("step 1 today cell label: " + str(h["label"]))
    hp = page.locator("section.heat")
    hp.screenshot(path=str(OUT / "uat05-step1-heat.png")); c.shots.append("uat05-step1-heat.png")
    pause(page)
    # step 2
    row = habit_row(page, "Stretch 10 minutes")
    hit_click(c, page, bead(row, 6), "step 2 Stretch today's circle")
    pause(page, 800)
    # step 3
    h3 = heat_probe(page)
    leg2 = h3["legend"]["2"]
    c.check("step 3: Stretch today is unticked", snap(page)["rows"][1]["pressed"][6] == "false")
    c.check("step 3: today's dot is smaller and lighter (class l2, 11px)", " l2" in (" " + h3["cls"]) and h3["css_dot"]["width"] == "11px", (h3["cls"], h3["css_dot"]["width"]))
    c.check("step 3 PAINT: smaller than before and lighter than before",
            h3["dot_px_width"] < h["dot_px_width"] and sum(h3["center_px"]) > sum(h["center_px"]), f"before px={h['center_px']} w={h['dot_px_width']}; now px={h3['center_px']} w={h3['dot_px_width']}")
    c.check("step 3 PAINT: equals the legend's middle dot", h3["center_px"] == leg2["center_px"] and abs(h3["dot_px_width"] - leg2["dot_px_width"]) <= 1,
            f"today px={h3['center_px']} w={h3['dot_px_width']}; legend l2 px={leg2['center_px']} w={leg2['dot_px_width']} css={leg2['css_w']}")
    c.note("step 3 today cell label: " + str(h3["label"]))
    hp.screenshot(path=str(OUT / "uat05-step3-heat.png")); c.shots.append("uat05-step3-heat.png")
    pause(page)
    # step 4
    hit_click(c, page, bead(row, 6), "step 4 Stretch today's circle")
    pause(page, 800)
    h4 = heat_probe(page)
    c.check("step 4: largest again (class l4, 17px, same colour as before)", " l4" in (" " + h4["cls"]) and h4["css_dot"]["width"] == "17px" and h4["center_px"] == h["center_px"] and abs(h4["dot_px_width"] - h["dot_px_width"]) <= 1, (h4["cls"], h4["css_dot"]["width"], h4["center_px"], h4["dot_px_width"]))
    # days after today
    fut = page.evaluate("""() => [...document.querySelectorAll('.cells > .hc.future')].map(c => { const cs = getComputedStyle(c, '::before');
        const b = c.getBoundingClientRect(); return {date: c.getAttribute('data-date'), w: cs.width, bg: cs.backgroundColor, hidden: c.getAttribute('aria-hidden'),
        role: c.getAttribute('role'), cx: b.x + b.width / 2, cy: b.y + b.height / 2}; })""")
    img = shot_img(page)
    px = [img.getpixel((round(f["cx"]), round(f["cy"]))) for f in fut]
    c.check("days after today have no dot (computed dot 0px, transparent, painted pixel = panel colour)",
            len(fut) >= 1 and all(f["w"] in ("0px",) and f["bg"] == "rgba(0, 0, 0, 0)" for f in fut) and all(near(p, SURFACE, 2) for p in px), {"future": fut, "pixels": px})
    total = page.locator(".cells > .hc").count()
    c.note(f"{total} cells in the grid, {len(fut)} after today ({[f['date'] for f in fut]})")
    c.shot(page, "uat05-final.png", full_page=True)
    hp.screenshot(path=str(OUT / "uat05-step4-heat.png")); c.shots.append("uat05-step4-heat.png")
    return c


def dlg_text(page):
    return strip_iso(page.locator("#del-title").text_content()), page.locator("#del-body").text_content()


def uat06(page):
    c = Case("UAT-06", "I can delete a habit, but only on purpose")
    s0 = snap(page)
    c.check("precondition: two habits", len(s0["rows"]) == 2)
    read_before = {k: s0["rows"][0][k] for k in ("name", "cur", "best", "pressed")}
    # step 1
    bin_btn = page.get_by_role("button", name="Delete Stretch 10 minutes")
    bb = bin_btn.bounding_box()
    rb = habit_row(page, "Stretch 10 minutes").bounding_box()
    c.check("step 1: the bin is at the right of 'Stretch 10 minutes'", bb["x"] > rb["x"] + rb["width"] * 0.7, f"bin x={bb['x']:.0f}, row x={rb['x']:.0f} w={rb['width']:.0f}")
    hit_click(c, page, bin_btn, "step 1 bin icon")
    pause(page, 700)
    # step 2
    s = snap(page)
    title, body = dlg_text(page)
    c.check("step 2: a box opens (dialog[open])", s["dialogOpen"] == 1, s["dialogOpen"])
    c.check("step 2: it asks Delete \"Stretch 10 minutes\"?", title == 'Delete "Stretch 10 minutes"?', repr(title))
    c.check("step 2: 'Its history is deleted too.' is under it", body == "Its history is deleted too.", body)
    cancel = page.get_by_role("button", name="Cancel", exact=True)
    delete = page.get_by_role("button", name="Delete habit", exact=True)
    c.check("step 2: two buttons Cancel and Delete habit are visible", cancel.is_visible() and delete.is_visible())
    db = page.locator("dialog[open]").bounding_box()
    dcx, dcy = db["x"] + db["width"] / 2, db["y"] + db["height"] / 2
    c.check("step 2: the box is in the middle of the page", abs(dcx - 640) <= 40 and abs(dcy - 400) <= 60, f"centre=({dcx:.0f},{dcy:.0f}) of 1280x800")
    c.shot(page, "uat06-dialog.png")
    pause(page, 1100)
    # step 3
    hit_click(c, page, cancel, "step 3 Cancel")
    pause(page, 800)
    s = snap(page)
    c.check("step 3: the box closes", s["dialogOpen"] == 0, s["dialogOpen"])
    c.check("step 3: both habits are still there", [r["name"] for r in s["rows"]] == ["Read 20 pages", "Stretch 10 minutes"], [r["name"] for r in s["rows"]])
    c.note("after Cancel, keyboard focus is on " + str(s["active"]))
    pause(page, 1100)
    # step 4 (a person is not faster than ~1 s here; the 500 ms guard is probed separately in extras)
    bin_btn = page.get_by_role("button", name="Delete Stretch 10 minutes")
    hit_click(c, page, bin_btn, "step 4 bin icon again")
    pause(page, 300)
    s = snap(page)
    c.check("step 4: the box opens again, same question", s["dialogOpen"] == 1 and dlg_text(page)[0] == 'Delete "Stretch 10 minutes"?', dlg_text(page)[0])
    # step 5
    page.wait_for_timeout(1000)
    c.note("step 5: waited 1000 ms as the script says (plus ~300 ms already elapsed)")
    # step 6
    delete = page.get_by_role("button", name="Delete habit", exact=True)
    hit_click(c, page, delete, "step 6 Delete habit")
    pause(page, 900)
    s = snap(page)
    c.check("step 6: the box is closed", s["dialogOpen"] == 0, s["dialogOpen"])
    c.check("step 6: 'Stretch 10 minutes' is gone, only 'Read 20 pages' remains", [r["name"] for r in s["rows"]] == ["Read 20 pages"], [r["name"] for r in s["rows"]])
    if s["rows"]:
        read_after = {k: s["rows"][0][k] for k in ("name", "cur", "best", "pressed")}
        c.check("step 6: 'Read 20 pages' is unchanged", read_after == read_before, {"before": read_before, "after": read_after})
    h = heat_probe(page)
    leg4 = h["legend"]["4"]
    c.check("step 6: heatmap counts one habit, today's cell reads 1 of 1", "1 of 1" in (h["label"] or ""), h["label"])
    c.check("step 6 PAINT: today's dot is the largest kind again (l4, matches legend All)",
            " l4" in (" " + h["cls"]) and h["center_px"] == leg4["center_px"] and abs(h["dot_px_width"] - leg4["dot_px_width"]) <= 1,
            f"{h['cls']} px={h['center_px']} w={h['dot_px_width']} css={h['css_dot']['width']}; legend All px={leg4['center_px']} w={leg4['dot_px_width']}")
    c.check("step 6: storage no longer holds the deleted habit's name", "Stretch" not in json.dumps(s["storage"]), "saved keys: " + str(list(s["storage"].keys())))
    c.note("after Delete, keyboard focus is on " + str(s["active"]))
    c.shot(page, "uat06-final.png", full_page=True)
    return c


def uat07(context, page):
    c = Case("UAT-07", "My habits are still there when I come back")
    before = snap(page)
    c.check("precondition: one habit 'Read 20 pages', yesterday and today ticked", [r["name"] for r in before["rows"]] == ["Read 20 pages"] and before["rows"][0]["pressed"][5:] == ["true", "true"])
    keep = {"rows": before["rows"], "heat": before["heat"], "header": before["headerDatetime"]}
    c.note("saved data in localStorage: " + json.dumps(before["storage"]))

    # step 1, literal: press F5. In headless automation the browser's own shortcut does not run, so prove it, then reload.
    page.evaluate("window.__marker = 'still-the-same-page'")
    page.keyboard.press("F5")
    page.wait_for_timeout(1500)
    marker = page.evaluate("window.__marker || null")
    c.note("pressing F5 through automation " + ("did NOT reload (marker survived), so page.reload() was used as instructed" if marker else "reloaded the page"))
    if marker:
        page.reload()
    page.wait_for_selector("li.habit", timeout=5000)
    pause(page, 600)
    after1 = snap(page)
    cmp1 = {"rows": after1["rows"], "heat": after1["heat"], "header": after1["headerDatetime"]}
    r = after1["rows"][0] if after1["rows"] else {}
    c.check("step 1: 'Read 20 pages' with the same filled circles, '2 days' and 'Best 2'", r.get("name") == "Read 20 pages" and r.get("pressed") == keep["rows"][0]["pressed"] and (r.get("cur"), r.get("best")) == ("2 days", "Best 2"), r)
    c.check("step 1: same heatmap (all 84 cells identical: class and label)", cmp1["heat"] == keep["heat"], "differs" if cmp1["heat"] != keep["heat"] else "84 cells equal")
    c.shot(page, "uat07-step1-after-reload.png", full_page=True)
    row = habit_row(page, "Read 20 pages")
    beads, gaps = strip_profile(page, row)
    c.check("step 1 PAINT: yesterday and today painted filled and joined by a thick line", beads[5]["filled"] and beads[6]["filled"] and gaps[5]["label"] == "thick", (beads[5]["fill_px"], beads[6]["fill_px"], gaps[5]))
    pause(page)

    # step 2: close the tab
    page.close()
    c.note("step 2: closed the tab (page.close()); the context and its localStorage stay")
    # step 3: new tab, same address
    page2 = context.new_page()
    attach(page2, "uat07-newtab")
    page2.goto(URL)
    page2.wait_for_selector("li.habit", timeout=5000)
    pause(page2, 600)
    after3 = snap(page2)
    r = after3["rows"][0] if after3["rows"] else {}
    c.check("step 3: new tab shows 'Read 20 pages' with the same filled circles, '2 days' and 'Best 2'", r.get("name") == "Read 20 pages" and r.get("pressed") == keep["rows"][0]["pressed"] and (r.get("cur"), r.get("best")) == ("2 days", "Best 2"), r)
    c.check("step 3: same heatmap (all 84 cells identical: class and label)", after3["heat"] == keep["heat"], "differs" if after3["heat"] != keep["heat"] else "84 cells equal")
    c.check("step 3: no 'list was reset' note shown", page2.locator(".note").count() == 0)
    c.shot(page2, "uat07-final.png", full_page=True)
    return c, page2


def extras_guards(page):
    """Not a case. Measures the two documented half-second pauses so the owner's ruling rests on a measurement."""
    ex = {}
    page.evaluate("window.__clicks = []; window.addEventListener('click', e => window.__clicks.push({t: e.timeStamp, cls: (e.target.className && e.target.className.baseVal === undefined ? e.target.className : 'svg'), e}), true)")
    bin_btn = page.get_by_role("button", name="Delete Read 20 pages")
    cancel = page.get_by_role("button", name="Cancel", exact=True)
    delete = page.get_by_role("button", name="Delete habit", exact=True)
    # (b) bin immediately after Cancel
    bin_btn.click()
    page.wait_for_timeout(1200)
    cancel.click()
    t0 = time.perf_counter()
    bin_btn.click()
    dt = (time.perf_counter() - t0) * 1000
    page.wait_for_timeout(300)
    opened = page.locator("dialog[open]").count()
    ex["bin_click_right_after_Cancel"] = {"python_gap_ms": round(dt), "dialog_open_after": opened}
    if opened:
        page.wait_for_timeout(1000)
        cancel.click()
    page.wait_for_timeout(1200)
    # (c) control: bin after a calm second
    bin_btn.click()
    page.wait_for_timeout(500)
    ex["bin_click_after_calm_second_opens"] = page.locator("dialog[open]").count() == 1
    page.wait_for_timeout(1200)
    cancel.click()
    page.wait_for_timeout(1200)
    # (a) Delete habit immediately after the bin opened the box
    bin_btn.click()
    t0 = time.perf_counter()
    delete.click()
    dt = (time.perf_counter() - t0) * 1000
    page.wait_for_timeout(300)
    still_open = page.locator("dialog[open]").count()
    habits_now = page.locator("li.habit").count()
    ev = page.evaluate("window.__clicks.map(c => ({t: Math.round(c.t), cls: c.cls, prevented: c.e.defaultPrevented}))")
    ex["delete_habit_click_right_after_open"] = {"python_gap_ms": round(dt), "dialog_still_open": still_open, "habits_left": habits_now, "click_events": ev[-4:]}
    if still_open:
        page.wait_for_timeout(1000)
        cancel.click()
        page.wait_for_timeout(600)
    ex["habit_still_there_at_end"] = page.locator("li.habit").count() == 1
    return ex


def extra_midnight(browser):
    out = {}
    ctx = browser.new_context(viewport=VIEWPORT, timezone_id="Asia/Kuala_Lumpur", locale="en-GB")
    try:
        page = ctx.new_page()
        attach(page, "midnight")
        start = datetime(2026, 10, 10, 23, 59, 40, tzinfo=timezone(timedelta(hours=8)))  # 23:59:40 Kuala Lumpur, today
        page.clock.install(time=start)
        page.goto(URL)
        out["fake_now_after_load"] = page.evaluate("new Date().toString()")
        field = page.get_by_label("New habit")
        field.click()
        page.keyboard.type("Midnight check", delay=30)
        page.get_by_role("button", name="Add", exact=True).click()
        page.wait_for_selector("li.habit")
        row = habit_row(page, "Midnight check")
        bead(row, 6).click()
        page.wait_for_timeout(500)

        def state():
            s = snap(page)
            r = s["rows"][0]
            return {"clock": page.evaluate("new Date().toString()"), "header": s["headerText"], "headerDatetime": s["headerDatetime"],
                    "first_day": r["labels"][0], "last_day": r["labels"][-1], "pressed": r["pressed"], "streak": [r["cur"], r["best"]],
                    "today_cell": [h["label"] for h in s["heat"] if "today" in h["cls"].split()], "aria_current": r["current"]}

        out["before"] = state()
        page.screenshot(path=str(OUT / "extra-midnight-before.png"))
        page.clock.run_for(60000)
        page.wait_for_timeout(600)
        out["after_run_60s"] = state()
        page.screenshot(path=str(OUT / "extra-midnight-after.png"))
        out["last_day_moved_to_tomorrow"] = out["before"]["last_day"] != out["after_run_60s"]["last_day"] and "11 Oct" in out["after_run_60s"]["last_day"]
    finally:
        ctx.close()
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pw = sync_playwright().start()
    browser = None
    try:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(viewport=VIEWPORT, timezone_id="Asia/Kuala_Lumpur", locale="en-GB")
        page = context.new_page()
        attach(page, "main")
        resp = page.goto(URL)
        print("goto status", resp.status, "real now:", datetime.now().astimezone().isoformat())
        page.wait_for_selector(".empty", timeout=5000)
        cur_page = page
        for fn in (uat01, uat02, uat03, uat04, uat05, uat06):
            try:
                case = fn(cur_page)
            except Exception as exc:  # keep going so later cases still get a literal attempt
                case = Case(fn.__name__.upper(), "crashed")
                case.crashed = f"{type(exc).__name__}: {exc}"
                case.note(traceback.format_exc())
                try:
                    case.shot(cur_page, f"{fn.__name__}-crash.png")
                except Exception:
                    pass
            CASES.append(case)
        try:
            case, cur_page = uat07(context, cur_page)
        except Exception as exc:
            case = Case("UAT-07", "crashed")
            case.crashed = f"{type(exc).__name__}: {exc}"
            case.note(traceback.format_exc())
            if not cur_page.is_closed():
                try:
                    case.shot(cur_page, "uat07-crash.png")
                except Exception:
                    pass
        CASES.append(case)
        try:
            if cur_page.is_closed():
                cur_page = context.new_page()
                cur_page.goto(URL)
                cur_page.wait_for_selector("li.habit")
            EXTRAS["guards"] = extras_guards(cur_page)
        except Exception as exc:
            EXTRAS["guards_error"] = f"{type(exc).__name__}: {exc}"
        try:
            EXTRAS["midnight"] = extra_midnight(browser)
        except Exception as exc:
            EXTRAS["midnight_error"] = f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}"
        context.close()
    finally:
        if browser:
            browser.close()
        pw.stop()
    raw = {"url": URL, "viewport": VIEWPORT, "ran_at": datetime.now().astimezone().isoformat(), "cases": [c.to_json() for c in CASES], "extras": EXTRAS, "console": CONSOLE}
    (OUT / "results-raw.json").write_text(json.dumps(raw, indent=2, default=str), encoding="utf-8")
    print("\nSUMMARY")
    for c in CASES:
        bad = [k["name"] for k in c.checks if not k["ok"]]
        print(c.cid, "auto-ok" if c.to_json()["auto_all_checks_ok"] else "CHECKS FAILED", bad)
    print("console:", CONSOLE)
    print("extras:", json.dumps(EXTRAS, indent=1, default=str))


main()
