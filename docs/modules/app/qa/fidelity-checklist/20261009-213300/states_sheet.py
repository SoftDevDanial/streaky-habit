"""States sheet (qa.md ST-01 to ST-17): each specimen of docs/design/states.html compared with the live element in the
same state, reached with real gestures, at a 360x780 viewport. Scratch, read-only on the product.

For every pair it compares computed color, background-color, the four border colours and widths and the style,
outline colour/style/width/offset, box-shadow, border-radius, font-size/weight/line-height, transform, opacity, cursor,
fill, display, margin and padding. Bead and icon-button width and height are compared too. Specimen-only styling is
excluded (frame padding and outline, .spec-day > .day width 56px, the hidden thread in bead specimens, .spec-input
width 240, .spec-cell .hc width 24). Writes states_sheet.json.
"""
import json

from common import *  # noqa: F401,F403
from playwright.sync_api import sync_playwright

VP = (360, 780)
STD = [
    "color", "background-color", "border-top-color", "border-right-color", "border-bottom-color", "border-left-color",
    "border-top-width", "border-right-width", "border-bottom-width", "border-left-width", "border-top-style",
    "outline-color", "outline-style", "outline-width", "outline-offset", "box-shadow", "border-radius",
    "font-size", "font-weight", "line-height", "transform", "opacity", "cursor", "fill", "display",
    "margin-top", "margin-bottom", "padding-top", "padding-right", "padding-bottom", "padding-left",
    "letter-spacing", "font-variant-numeric", "text-align",
]
SIZE = ["__w", "__h"]

FIND_JS = r"""
function find(spec) {
  if (spec.css) return document.querySelector(spec.css);
  const frames = Array.from(document.querySelectorAll('figure.frame')).filter((f) => f.querySelector('figcaption').textContent.trim().startsWith(spec.frame));
  if (!frames.length) return null;
  const specs = Array.from(frames[0].querySelectorAll('.spec')).filter((s) => s.querySelector('.frame-cap').textContent.trim() === spec.label);
  for (const s of specs) { const el = s.querySelector(spec.sel); if (el) return el; }
  return null;
}
"""

GET_JS = "(arg) => {" + FIND_JS + r"""
  const el = find(arg.spec);
  if (!el) return null;
  const cs = getComputedStyle(el, arg.pseudo || undefined);
  const o = {};
  for (const k of arg.keys) o[k] = cs.getPropertyValue(k);
  const r = el.getBoundingClientRect();
  o.__w = Math.round(r.width * 100) / 100; o.__h = Math.round(r.height * 100) / 100;
  o.__text = (el.textContent || '').trim();
  o.__attrs = Object.fromEntries(Array.from(el.attributes).map((a) => [a.name, a.value]));
  return o;
}"""

# every element under a root, in order, with its tag, class and the standard properties (and the slot's thread halves)
DUMP_JS = "(arg) => {" + FIND_JS + r"""
  const root = find(arg.spec);
  if (!root) return null;
  const out = [];
  for (const el of [root, ...root.querySelectorAll('*')]) {
    const cs = getComputedStyle(el);
    const o = { tag: el.tagName.toLowerCase(), cls: typeof el.className === 'string' ? el.className : '', props: {} };
    for (const k of arg.keys) o.props[k] = cs.getPropertyValue(k);
    const r = el.getBoundingClientRect();
    o.w = Math.round(r.width * 100) / 100; o.h = Math.round(r.height * 100) / 100;
    o.text = Array.from(el.childNodes).filter((n) => n.nodeType === 3).map((n) => n.nodeValue.trim()).join('');
    if (el.classList && el.classList.contains('slot')) {
      o.pseudo = {};
      for (const ps of ['::before', '::after']) {
        const p = getComputedStyle(el, ps);
        o.pseudo[ps] = { display: p.display, height: p.height, marginTop: p.marginTop, bg: p.backgroundColor, img: p.backgroundImage };
      }
    }
    out.push(o);
  }
  return out;
}"""


def getp(page, spec, keys=STD, pseudo=None):
    return page.evaluate(GET_JS, {"spec": spec, "keys": keys, "pseudo": pseudo})


def compare(a, b, keys, skip=()):
    diffs = []
    if a is None or b is None:
        return [("<element>", "missing" if a is None else "present", "missing" if b is None else "present")]
    for k in keys:
        if k in skip:
            continue
        if a.get(k) != b.get(k):
            diffs.append((k, a.get(k), b.get(k)))
    return diffs


class Cases:
    def __init__(self):
        self.out = []

    def add(self, row, name, sheet, live, keys=STD, skip=(), sizes=False, extra_ok=True, note=""):
        ks = list(keys) + (SIZE if sizes else [])
        diffs = compare(sheet, live, ks, skip)
        self.out.append({"row": row, "case": name, "compared": len(ks) - len(skip), "diffs": diffs, "note": note,
                         "sheet_text": (sheet or {}).get("__text"), "live_text": (live or {}).get("__text")})
        return not diffs

    def add_dump(self, row, name, sheet_list, live_list, keys=STD, skip_sizes=True, skip=()):
        diffs = []
        if len(sheet_list) != len(live_list):
            diffs.append(("<element count>", len(sheet_list), len(live_list)))
        for i, (s, l) in enumerate(zip(sheet_list, live_list)):
            tag = f"{i}:{s['tag']}.{s['cls'].replace(' ', '.')}"
            if s["tag"] != l["tag"] or s["cls"] != l["cls"]:
                diffs.append((f"{tag} <tag/class>", f"{s['tag']}.{s['cls']}", f"{l['tag']}.{l['cls']}"))
            if s["text"] != l["text"]:
                diffs.append((f"{tag} <text>", s["text"], l["text"]))
            for k in keys:
                if k in skip:
                    continue
                if s["props"].get(k) != l["props"].get(k):
                    diffs.append((f"{tag} {k}", s["props"].get(k), l["props"].get(k)))
            if "bead" in s["cls"].split() or "icon-btn" in s["cls"].split():
                if (s["w"], s["h"]) != (l["w"], l["h"]):
                    diffs.append((f"{tag} size", [s["w"], s["h"]], [l["w"], l["h"]]))
            if "pseudo" in s:
                if s["pseudo"] != l.get("pseudo"):
                    diffs.append((f"{tag} thread halves", s["pseudo"], l.get("pseudo")))
        self.out.append({"row": row, "case": name, "compared": len(sheet_list) * len(keys), "diffs": diffs})
        return not diffs


def twelve_habits():
    return json.dumps({"version": 1, "habits": [{"name": f"Habit {n}", "done": []} for n in range(1, 13)]})


def ctx_page(browser, url, seed_text=None, reduced="no-preference", seed_sample=False):
    ctx = browser.new_context(viewport={"width": VP[0], "height": VP[1]}, device_scale_factor=1, color_scheme="light", reduced_motion=reduced, locale="en-US")
    page = ctx.new_page()
    page.clock.set_fixed_time(FIXED)
    if seed_sample:
        page.add_init_script(SEED)
    elif seed_text is not None:
        page.add_init_script(f"localStorage.setItem('streaks.state', {json.dumps(seed_text)})")
    page.goto(url, wait_until="networkidle")
    page.wait_for_timeout(500)
    return ctx, page


def center(page, css):
    box = page.locator(css).first.bounding_box()
    return box["x"] + box["width"] / 2, box["y"] + box["height"] / 2


def run():
    cases = Cases()
    facts = {}
    with sync_playwright() as pw:
        browser = launch(pw)
        sctx, sheet = ctx_page(browser, golden_url("ST"))
        BTN = "Buttons: default, hover, keyboard focus, disabled"
        INP = "Text input: default, keyboard focus, error, disabled"
        DAY = "Day bead and icon button"
        HEAT = "Heatmap cell: levels 0 to 4, today, a future day"

        def sp(frame, label, sel):
            return {"frame": frame, "label": label, "sel": sel}

        # ---------------------------------------------------------------- ST-01, ST-02, ST-03 name errors
        ctx, page = ctx_page(browser, BASE)
        form_before = page.evaluate("() => { const f = document.querySelector('form.add').getBoundingClientRect(); const i = document.querySelector('#new-habit').getBoundingClientRect(); const b = document.querySelector('.add .btn').getBoundingClientRect(); return { h: f.height, ix: i.x, iw: i.width, bx: b.x, bw: b.width }; }")
        page.get_by_role("button", name="Add").click()
        page.wait_for_timeout(300)
        focused = getp(page, {"css": "#new-habit"}, ["outline-color", "outline-style", "outline-width", "outline-offset", "border-top-color"])
        form_after = page.evaluate("() => { const f = document.querySelector('form.add').getBoundingClientRect(); const i = document.querySelector('#new-habit').getBoundingClientRect(); const b = document.querySelector('.add .btn').getBoundingClientRect(); return { h: f.height, ix: i.x, iw: i.width, bx: b.x, bw: b.width }; }")
        page.evaluate("() => document.activeElement.blur()")
        page.wait_for_timeout(300)
        live_in = getp(page, {"css": "#new-habit"})
        live_msg = getp(page, {"css": "#new-habit-msg"})
        live_label = getp(page, {"css": "label.add-label"})
        live_btn = getp(page, {"css": ".add .btn"})
        live_attrs = live_in["__attrs"]
        s_in, s_msg = getp(sheet, {"css": "#s3a"}), getp(sheet, {"css": "#s3a-msg"})
        s_label, s_btn = getp(sheet, {"css": "form:has(#s3a) .add-label"}), getp(sheet, {"css": "form:has(#s3a) .btn"})
        cases.add("ST-01", "S3 empty: input (error border)", s_in, live_in, skip=("outline-color",), sizes=True, note="input width differs: .frame-body is 280 wide and the live form 320, so width is not compared")
        cases.out[-1]["diffs"] = [d for d in cases.out[-1]["diffs"] if d[0] != "__w"]
        cases.add("ST-01", "S3 empty: message line", s_msg, live_msg, skip=())
        cases.add("ST-01", "S3 empty: label", s_label, live_label)
        cases.add("ST-01", "S3 empty: Add button", s_btn, live_btn)
        grows = round(form_after["h"] - form_before["h"], 2)
        facts["ST-01"] = {"form_height_before": form_before["h"], "form_height_after": form_after["h"], "grew_by": grows,
                          "input_x_before_after": [form_before["ix"], form_after["ix"]], "input_w_before_after": [form_before["iw"], form_after["iw"]],
                          "button_x_before_after": [form_before["bx"], form_after["bx"]], "aria_invalid": live_attrs.get("aria-invalid"),
                          "message": live_msg["__text"], "message_classes": live_msg["__attrs"].get("class"), "focus_after_submit": focused,
                          "sheet_message": s_msg["__text"], "sheet_message_classes": s_msg["__attrs"].get("class"), "sheet_aria_invalid": s_in["__attrs"].get("aria-invalid")}
        ctx.close()

        # ST-02 too long, typed through the keyboard
        ctx, page = ctx_page(browser, BASE)
        long_text = "Walk to the end of the street and back after dinner"
        page.locator("#new-habit").click()
        page.keyboard.type(long_text)
        page.keyboard.press("Enter")
        page.wait_for_timeout(300)
        stays = page.evaluate("() => document.querySelector('#new-habit').value")
        page.evaluate("() => document.activeElement.blur()")
        page.wait_for_timeout(300)
        live_in, live_msg = getp(page, {"css": "#new-habit"}), getp(page, {"css": "#new-habit-msg"})
        s_in, s_msg = getp(sheet, {"css": "#s3b"}), getp(sheet, {"css": "#s3b-msg"})
        cases.add("ST-02", "S3 too long: input", s_in, live_in, skip=())
        cases.out[-1]["diffs"] = [d for d in cases.out[-1]["diffs"] if d[0] != "__w"]
        cases.add("ST-02", "S3 too long: message", s_msg, live_msg)
        facts["ST-02"] = {"message": live_msg["__text"], "text_stays": stays == long_text, "sheet_message": s_msg["__text"]}
        ctx.close()

        # ST-03 duplicate
        ctx, page = ctx_page(browser, BASE, seed_sample=True)
        page.locator("#new-habit").click()
        page.keyboard.type("read 20 pages")
        page.get_by_role("button", name="Add").click()
        page.wait_for_timeout(300)
        stays = page.evaluate("() => document.querySelector('#new-habit').value")
        page.evaluate("() => document.activeElement.blur()")
        page.wait_for_timeout(300)
        live_in, live_msg = getp(page, {"css": "#new-habit"}), getp(page, {"css": "#new-habit-msg"})
        s_in, s_msg = getp(sheet, {"css": "#s3c"}), getp(sheet, {"css": "#s3c-msg"})
        cases.add("ST-03", "S3 duplicate: input", s_in, live_in)
        cases.out[-1]["diffs"] = [d for d in cases.out[-1]["diffs"] if d[0] != "__w"]
        cases.add("ST-03", "S3 duplicate: message", s_msg, live_msg)
        facts["ST-03"] = {"message": live_msg["__text"], "text_stays": stays == "read 20 pages", "sheet_message": s_msg["__text"]}
        ctx.close()

        # ---------------------------------------------------------------- ST-04 twelve habits (+ disabled button states)
        ctx, page = ctx_page(browser, BASE, seed_text=twelve_habits())
        live_in = getp(page, {"css": "#new-habit"})
        live_btn = getp(page, {"css": ".add .btn"})
        live_label = getp(page, {"css": "label.add-label"})
        live_msg = getp(page, {"css": "#new-habit-msg"})
        s_in, s_btn = getp(sheet, {"css": "#s4"}), getp(sheet, {"css": "form:has(#s4) .btn"})
        s_label, s_msg = getp(sheet, {"css": "form:has(#s4) .add-label"}), getp(sheet, {"css": "#s4-msg"})
        cases.add("ST-04", "S4 disabled input", s_in, live_in)
        cases.out[-1]["diffs"] = [d for d in cases.out[-1]["diffs"] if d[0] != "__w"]
        cases.add("ST-04", "S4 disabled Add button", s_btn, live_btn, sizes=True)
        cases.add("ST-04", "S4 label", s_label, live_label)
        cases.add("ST-04", "S4 note line", s_msg, live_msg, sizes=False)
        # hover and press on the disabled Add
        x, y = center(page, ".add .btn")
        page.mouse.move(x, y)
        page.wait_for_timeout(300)
        hov = getp(page, {"css": ".add .btn"}, ["background-color", "transform", "cursor"])
        page.mouse.down()
        page.wait_for_timeout(300)
        prs = getp(page, {"css": ".add .btn"}, ["background-color", "transform"])
        page.mouse.up()
        facts["ST-04"] = {"note_text": live_msg["__text"], "note_classes": live_msg["__attrs"].get("class"), "note_height_live": live_msg["__h"], "note_height_sheet": s_msg["__h"],
                          "input_disabled": "disabled" in live_in["__attrs"], "add_disabled": "disabled" in live_btn["__attrs"], "describedby": live_in["__attrs"].get("aria-describedby"),
                          "disabled_add_hover": hov, "disabled_add_pressed": prs, "cursor_input": live_in["cursor"], "sheet_note_text": s_msg["__text"]}
        ctx.close()

        # ---------------------------------------------------------------- ST-05 a habit just added
        ctx, page = ctx_page(browser, BASE)
        page.locator("#new-habit").click()
        page.keyboard.type("Read 20 pages")
        page.keyboard.press("Enter")
        page.wait_for_timeout(400)
        page.mouse.move(2, 2)
        live_rows = page.evaluate(DUMP_JS, {"spec": {"css": "li.habit"}, "keys": STD})
        sheet_rows = sheet.evaluate(DUMP_JS, {"spec": {"css": "li.habit:has(#new-name)"}, "keys": STD})
        cases.add_dump("ST-05", "A habit just added: the whole row, every element", sheet_rows, live_rows, skip=("text-align",))
        facts["ST-05"] = {"elements_compared": len(live_rows), "streak_line": next(e["text"] for e in live_rows if e["cls"] == "cur none"), "best_elements": sum(1 for e in live_rows if e["cls"] == "best"),
                          "name": next(e["text"] for e in live_rows if e["cls"] == "habit-name"), "beads": sum(1 for e in live_rows if e["cls"] == "bead"),
                          "pressed_beads": page.evaluate("() => document.querySelectorAll('li.habit .day[aria-pressed=true]').length"),
                          "thread_halves": [e.get("pseudo") for e in live_rows if e["cls"] == "slot"][:2]}
        ctx.close()

        # ---------------------------------------------------------------- ST-06 note after unreadable data
        ctx, page = ctx_page(browser, BASE, seed_text="{")
        page.mouse.move(2, 2)
        live_note = page.evaluate(DUMP_JS, {"spec": {"css": ".note"}, "keys": STD})
        sheet_note = sheet.evaluate(DUMP_JS, {"spec": {"css": ".note"}, "keys": STD})
        cases.add_dump("ST-06", "S5 note: banner, text, Dismiss button and glyph", sheet_note, live_note, skip=("text-align",))
        for what, sspec, lspec in (("empty message", {"css": ".frame-body .page > .empty"}, {"css": "p.empty"}), ("empty lead", {"css": ".frame-body .page > .empty strong"}, {"css": "p.empty strong"}),
                                   ("brand (sheet p.brand vs app h1.brand)", {"css": ".frame-body .page .brand"}, {"css": "h1.brand"}), ("date", {"css": ".frame-body .page .date"}, {"css": "p.date"}),
                                   ("add form label", {"css": "form:has(#s5) .add-label"}, {"css": "label.add-label"}), ("add input", {"css": "#s5"}, {"css": "#new-habit"})):
            s_el, l_el = getp(sheet, sspec), getp(page, lspec)
            cases.add("ST-06", f"S5: {what}", s_el, l_el, skip=("text-align",))
            cases.out[-1]["diffs"] = [d for d in cases.out[-1]["diffs"] if d[0] != "__w"]
        gap_live = page.evaluate("() => document.querySelector('p.empty').getBoundingClientRect().top - document.querySelector('.note').getBoundingClientRect().bottom")
        gap_sheet = sheet.evaluate("() => document.querySelector('.frame-body .page > .empty').getBoundingClientRect().top - document.querySelector('.frame-body .page > .note').getBoundingClientRect().bottom")
        live_x_path = page.evaluate("() => document.querySelector('#i-x path').getAttribute('d')")
        sheet_x_path = sheet.evaluate("() => document.querySelector('#i-x path').getAttribute('d')")
        dismiss = page.evaluate("() => { const b = document.querySelector('.note .icon-btn'); const n = document.querySelector('.note'); const br = b.getBoundingClientRect(); const nr = n.getBoundingClientRect(); return { label: b.getAttribute('aria-label'), top_gap: br.top - nr.top, right_gap: nr.right - br.right, w: br.width, h: br.height, href: b.querySelector('use').getAttribute('href'), role: n.getAttribute('role'), noteText: n.querySelector('.note-text').textContent }; }")
        sheet_dismiss = sheet.evaluate("() => { const n = document.querySelector('.frame-body .page > .note'); const b = n.querySelector('.icon-btn'); const br = b.getBoundingClientRect(); const nr = n.getBoundingClientRect(); return { label: b.getAttribute('aria-label'), top_gap: br.top - nr.top, right_gap: nr.right - br.right, w: br.width, h: br.height, href: b.querySelector('use').getAttribute('href'), role: n.getAttribute('role'), noteText: n.querySelector('.note-text').textContent }; }")
        facts["ST-06"] = {"gap_note_to_empty_live": gap_live, "gap_note_to_empty_sheet": gap_sheet, "x_path_equal": live_x_path == sheet_x_path, "dismiss_live": dismiss, "dismiss_sheet": sheet_dismiss,
                          "brand_tag_live": page.evaluate("() => document.querySelector('.brand').tagName"), "brand_tag_sheet": sheet.evaluate("() => document.querySelector('.frame-body .page .brand').tagName"),
                          "note_is_first_child_of_col_main": page.evaluate("() => document.querySelector('.col-main').firstElementChild.className"),
                          "empty_message_shows": page.evaluate("() => !!document.querySelector('p.empty')")}
        ctx.close()

        # ---------------------------------------------------------------- ST-07 / ST-10: primary button and text input, fresh app
        ctx, page = ctx_page(browser, BASE)
        add = {"css": ".add .btn"}
        inp = {"css": "#new-habit"}
        cases.add("ST-07", "Primary: default", getp(sheet, sp(BTN, "Primary", ".btn")), getp(page, add), sizes=True, skip=())
        cases.add("ST-10", "Input: default", getp(sheet, sp(INP, "Default", ".input")), getp(page, inp), note="width differs by specimen-only .spec-input rule")
        cases.out[-1]["diffs"] = [d for d in cases.out[-1]["diffs"] if d[0] != "__w"]
        x, y = center(page, ".add .btn")
        page.mouse.move(x, y)
        page.wait_for_timeout(350)
        cases.add("ST-07", "Primary: hover", getp(sheet, sp(BTN, "Primary hover", ".btn")), getp(page, add), sizes=True)
        page.mouse.down()
        page.wait_for_timeout(350)
        press_normal = getp(page, add, ["transform", "background-color"])
        page.mouse.move(2, 2)
        page.mouse.up()
        ctx.close()
        # keyboard focus on the input and on the Add button
        ctx, page = ctx_page(browser, BASE)
        page.keyboard.press("Tab")
        page.wait_for_timeout(300)
        cases.add("ST-10", "Input: keyboard focus", getp(sheet, sp(INP, "Focus", ".input")), getp(page, inp))
        cases.out[-1]["diffs"] = [d for d in cases.out[-1]["diffs"] if d[0] != "__w"]
        page.keyboard.press("Tab")
        page.wait_for_timeout(300)
        cases.add("ST-07", "Primary: keyboard focus", getp(sheet, sp(BTN, "Primary focus", ".btn")), getp(page, add), sizes=True)
        ctx.close()
        # press scale under reduced motion
        ctx, page = ctx_page(browser, BASE, reduced="reduce")
        x, y = center(page, ".add .btn")
        page.mouse.move(x, y)
        page.mouse.down()
        page.wait_for_timeout(200)
        press_reduced = getp(page, add, ["transform"])
        page.mouse.move(2, 2)
        page.mouse.up()
        ctx.close()
        facts["ST-07"] = {"press_normal_motion_after_350ms": press_normal, "press_reduced_motion": press_reduced}
        # disabled primary and disabled input: ST-04 pairs, repeated under the ST-07 and ST-10 labels
        ctx, page = ctx_page(browser, BASE, seed_text=twelve_habits())
        cases.add("ST-07", "Primary: disabled", getp(sheet, sp(BTN, "Disabled", ".btn")), getp(page, add), sizes=True)
        cases.add("ST-10", "Input: disabled", getp(sheet, sp(INP, "Disabled", ".input")), getp(page, inp))
        cases.out[-1]["diffs"] = [d for d in cases.out[-1]["diffs"] if d[0] != "__w"]
        ctx.close()
        # error input (already compared under ST-01), compared again to the specimen "Error"
        ctx, page = ctx_page(browser, BASE)
        page.get_by_role("button", name="Add").click()
        page.evaluate("() => document.activeElement.blur()")
        page.wait_for_timeout(300)
        cases.add("ST-10", "Input: error", getp(sheet, sp(INP, "Error", ".input")), getp(page, inp))
        cases.out[-1]["diffs"] = [d for d in cases.out[-1]["diffs"] if d[0] != "__w"]
        ctx.close()

        # ---------------------------------------------------------------- ST-08 / ST-09: dialog buttons
        ctx, page = ctx_page(browser, BASE, seed_sample=True)
        page.get_by_role("button", name="Delete Read 20 pages").click()
        page.wait_for_timeout(600)
        page.mouse.move(2, 2)
        page.wait_for_timeout(300)
        cancel = {"css": "dialog .btn-secondary"}
        dele = {"css": "dialog .btn-danger"}
        cases.add("ST-08", "Secondary (Cancel): default", getp(sheet, sp(BTN, "Secondary", ".btn")), getp(page, cancel), skip=("outline-style", "outline-width", "outline-color", "outline-offset"),
                  note="Cancel has script focus on open, no ring after a mouse open (M1-09); outline props excluded because the live button holds focus")
        cases.add("ST-09", "Danger (Delete habit): default", getp(sheet, sp(BTN, "Danger", ".btn")), getp(page, dele))
        x, y = center(page, "dialog .btn-secondary")
        page.mouse.move(x, y)
        page.wait_for_timeout(350)
        cases.add("ST-08", "Secondary (Cancel): hover", getp(sheet, sp(BTN, "Secondary hover", ".btn")), getp(page, cancel), skip=("outline-style", "outline-width", "outline-color", "outline-offset"))
        x, y = center(page, "dialog .btn-danger")
        page.mouse.move(x, y)
        page.wait_for_timeout(350)
        cases.add("ST-09", "Danger (Delete habit): hover", getp(sheet, sp(BTN, "Danger hover", ".btn")), getp(page, dele))
        facts["ST-09"] = {"danger_hover_bg": getp(page, dele, ["background-color"])["background-color"]}
        ctx.close()

        # ---------------------------------------------------------------- ST-11 .. ST-15 beads and icon buttons on the sample day
        ctx, page = ctx_page(browser, BASE, seed_sample=True)
        page.mouse.move(2, 2)

        def bead_spec(row_n, date):
            return {"css": f"li.habit:nth-child({row_n}) .day[data-date='{date}']"}

        def bead_of(row_n, date):
            return {"css": f"li.habit:nth-child({row_n}) .day[data-date='{date}'] .bead"}

        def check_of(row_n, date):
            return {"css": f"li.habit:nth-child({row_n}) .day[data-date='{date}'] .bead svg"}

        BEADK = STD
        pairs = (("Not done", ".bead", ".bead", (1, "2026-10-02"), "aria-pressed false"), ("Done", ".bead", ".bead", (1, "2026-10-03"), "aria-pressed true"),
                 ("Today", ".bead", ".bead", (2, "2026-10-08"), "today, not done"), ("Today done", ".bead", ".bead", (1, "2026-10-08"), "today, done"))
        for label, ssel, lsel, (rn, dt), desc in pairs:
            s_bead = getp(sheet, sp(DAY, label, ".bead"))
            l_bead = getp(page, bead_of(rn, dt))
            cases.add("ST-11", f"Bead '{label}' ({desc}): the bead", s_bead, l_bead, sizes=True)
            s_chk = getp(sheet, sp(DAY, label, ".bead svg"))
            l_chk = getp(page, check_of(rn, dt))
            cases.add("ST-11", f"Bead '{label}': the check glyph", s_chk, l_chk, sizes=True)
            s_cell = getp(sheet, sp(DAY, label, ".day"))
            l_cell = getp(page, bead_spec(rn, dt))
            cases.add("ST-11", f"Bead '{label}': the day cell", s_cell, l_cell, sizes=False)
            s_wd, l_wd = getp(sheet, sp(DAY, label, ".wd")), getp(page, {"css": f"li.habit:nth-child({rn}) .day[data-date='{dt}'] .wd"})
            s_dm, l_dm = getp(sheet, sp(DAY, label, ".dm")), getp(page, {"css": f"li.habit:nth-child({rn}) .day[data-date='{dt}'] .dm"})
            cases.add("ST-11", f"Bead '{label}': weekday and number", s_wd, l_wd)
            cases.add("ST-11", f"Bead '{label}': number", s_dm, l_dm)
        # hover on a not-done bead and on a done bead
        for label, (rn, dt) in (("Hover", (1, "2026-10-02")), ("Done hover", (1, "2026-10-03"))):
            x, y = center(page, f"li.habit:nth-child({rn}) .day[data-date='{dt}']")
            page.mouse.move(x, y)
            page.wait_for_timeout(350)
            cases.add("ST-12", f"Bead '{label}' (real hover)", getp(sheet, sp(DAY, label, ".bead")), getp(page, bead_of(rn, dt)), sizes=True)
            cases.add("ST-12", f"Bead '{label}': the day cell", getp(sheet, sp(DAY, label, ".day")), getp(page, bead_spec(rn, dt)))
        page.mouse.move(2, 2)
        # icon button: rest and hover
        cases.add("ST-15", "Icon button: rest", getp(sheet, sp(DAY, "Delete", ".icon-btn")), getp(page, {"css": "li.habit:nth-child(1) .icon-btn"}), sizes=True)
        cases.add("ST-15", "Icon button: rest, glyph", getp(sheet, sp(DAY, "Delete", ".icon-btn svg")), getp(page, {"css": "li.habit:nth-child(1) .icon-btn svg"}), sizes=True)
        x, y = center(page, "li.habit:nth-child(1) .icon-btn")
        page.mouse.move(x, y)
        page.wait_for_timeout(350)
        cases.add("ST-15", "Icon button: hover", getp(sheet, sp(DAY, "Hover", ".icon-btn")), getp(page, {"css": "li.habit:nth-child(1) .icon-btn"}), sizes=True)
        cases.add("ST-15", "Icon button: hover, glyph", getp(sheet, sp(DAY, "Hover", ".icon-btn svg")), getp(page, {"css": "li.habit:nth-child(1) .icon-btn svg"}), sizes=True)
        ctx.close()
        # keyboard focus: the first Tab reaches the first trash button
        ctx, page = ctx_page(browser, BASE, seed_sample=True)
        page.keyboard.press("Tab")
        page.wait_for_timeout(300)
        cases.add("ST-15", "Icon button: keyboard focus", getp(sheet, sp(DAY, "Focus", ".icon-btn")), getp(page, {"css": "li.habit:nth-child(1) .icon-btn"}), sizes=True)
        # 15 more tabs: trash1, 7 beads of row 1, trash2, then Thu 8 of row 2 (today, not done)
        for _ in range(15):
            page.keyboard.press("Tab")
        page.wait_for_timeout(300)
        which = page.evaluate("() => { const a = document.activeElement; return { cls: a.className, date: a.getAttribute('data-date'), pressed: a.getAttribute('aria-pressed'), current: a.getAttribute('aria-current'), row: Array.from(document.querySelectorAll('li.habit')).indexOf(a.closest('li.habit')) + 1 }; }")
        focus_cell = {"css": "li.habit:nth-child(2) .day[data-date='2026-10-08']"}
        cases.add("ST-13", "Bead focus: the day cell's ring", getp(sheet, sp(DAY, "Focus", ".day")), getp(page, focus_cell), skip=())
        cases.add("ST-13", "Bead focus: the bead keeps the today ring and no outline", getp(sheet, sp(DAY, "Focus", ".bead")), getp(page, {"css": "li.habit:nth-child(2) .day[data-date='2026-10-08'] .bead"}), sizes=True)
        facts["ST-13"] = {"focused": which, "cell_outline": getp(page, focus_cell, ["outline-style", "outline-width", "outline-offset", "outline-color", "border-radius"]),
                          "bead_outline": getp(page, {"css": "li.habit:nth-child(2) .day[data-date='2026-10-08'] .bead"}, ["outline-style", "box-shadow"]),
                          "cell_rect": page.evaluate("() => { const r = document.activeElement.getBoundingClientRect(); return [r.width, r.height]; }")}
        ctx.close()
        # press on a bead and on an icon button under reduced motion
        ctx, page = ctx_page(browser, BASE, seed_sample=True, reduced="reduce")
        x, y = center(page, "li.habit:nth-child(1) .day[data-date='2026-10-02']")
        page.mouse.move(x, y)
        page.mouse.down()
        page.wait_for_timeout(200)
        press_bead = getp(page, bead_of(1, "2026-10-02"), ["transform"])
        page.mouse.move(2, 2)
        page.mouse.up()
        facts["ST-14"] = {"pressed_bead_transform": press_bead["transform"], "unchanged_after_release_outside": page.evaluate("() => document.querySelector(\"li.habit:nth-child(1) .day[data-date='2026-10-02']\").getAttribute('aria-pressed')")}
        ctx.close()

        # ---------------------------------------------------------------- ST-16 heat cell levels (sample, then sample plus a fourth habit)
        ctx, page = ctx_page(browser, BASE, seed_sample=True)
        page.mouse.move(2, 2)

        def cell(date):
            return {"css": f".cells .hc[data-date='{date}']"}

        for label, date in (("0 None", "2026-08-12"), ("1 Up to a third", "2026-07-21"), ("2 Up to two thirds", "2026-07-24"), ("4 All", "2026-07-20")):
            for ps in ("::before",):
                cases.add("ST-16", f"Heat cell '{label}' ({date}) dot", getp(sheet, sp(HEAT, label, ".hc"), pseudo=ps, keys=STD + ["content", "background-color", "box-shadow"]),
                          getp(page, cell(date), pseudo=ps, keys=STD + ["content", "background-color", "box-shadow"]), sizes=False)
            cases.add("ST-16", f"Heat cell '{label}' ({date}) cell", getp(sheet, sp(HEAT, label, ".hc")), getp(page, cell(date)))
        # the dot sizes (pseudo width and height) for every level
        dots_live = page.evaluate("() => Object.fromEntries(['2026-08-12', '2026-07-21', '2026-07-24', '2026-07-20'].map((d) => { const s = getComputedStyle(document.querySelector(`.cells .hc[data-date='${d}']`), '::before'); return [d, [s.width, s.height]]; }))")
        dots_sheet = sheet.evaluate("() => { const fr = Array.from(document.querySelectorAll('figure.frame')).find((f) => f.querySelector('figcaption').textContent.startsWith('Heatmap cell')); return Array.from(fr.querySelectorAll('.spec')).map((sp) => { const hc = sp.querySelector('.hc'); const b = getComputedStyle(hc, '::before'); const a = getComputedStyle(hc, '::after'); return [sp.querySelector('.frame-cap').textContent.trim(), b.width, b.height, a.width, a.height, a.borderTopWidth]; }); }")
        s_today = getp(sheet, sp(HEAT, "Today", ".hc"), pseudo="::after", keys=STD + ["width", "height", "border-top-width", "border-top-style", "border-top-color"])
        l_today = getp(page, cell("2026-10-08"), pseudo="::after", keys=STD + ["width", "height", "border-top-width", "border-top-style", "border-top-color"])
        cases.add("ST-16", "Today ring (::after) on the live today cell vs the sheet's 'Today'", s_today, l_today)
        s_fut = getp(sheet, sp(HEAT, "Future, blank", ".hc"), pseudo="::before", keys=STD + ["width", "height"])
        l_fut = getp(page, cell("2026-10-09"), pseudo="::before", keys=STD + ["width", "height"])
        cases.add("ST-16", "Future cell dot", s_fut, l_fut)
        s_fut_a = getp(sheet, sp(HEAT, "Future, blank", ".hc"), pseudo="::after", keys=STD + ["width", "height"])
        l_fut_a = getp(page, cell("2026-10-09"), pseudo="::after", keys=STD + ["width", "height"])
        cases.add("ST-16", "Future cell ring", s_fut_a, l_fut_a)
        ctx.close()
        # level 3: the sample plus a fourth habit added through the form
        ctx, page = ctx_page(browser, BASE, seed_sample=True)
        page.locator("#new-habit").click()
        page.keyboard.type("Drink water")
        page.keyboard.press("Enter")
        page.wait_for_timeout(400)
        page.mouse.move(2, 2)
        l3_cell = getp(page, cell("2026-07-20"), keys=["__w"])
        cases.add("ST-16", "Level 3 live (Mon 20 Jul, 3 of 4 habits) dot", getp(sheet, sp(HEAT, "3 More than two thirds", ".hc"), pseudo="::before", keys=STD + ["content"]),
                  getp(page, cell("2026-07-20"), pseudo="::before", keys=STD + ["content"]))
        facts["ST-16"] = {"level3_cell_class": page.evaluate("() => document.querySelector(\".cells .hc[data-date='2026-07-20']\").className"),
                          "level3_cell_label": page.evaluate("() => document.querySelector(\".cells .hc[data-date='2026-07-20']\").getAttribute('aria-label')"),
                          "worked_example_cells": page.evaluate("() => Object.fromEntries(['2026-10-06', '2026-10-08', '2026-07-21', '2026-08-12'].map((d) => { const c = document.querySelector(`.cells .hc[data-date='${d}']`); return [d, c.className + ' | ' + c.getAttribute('aria-label')]; }))"),
                          "dots_live": dots_live, "dots_sheet": dots_sheet}
        ctx.close()

        # ---------------------------------------------------------------- ST-17 sheet chrome not built
        chrome_strings = ["Streaks states", "A specimen sheet", "Add field", "Habit list", "Component states", "S3 Add pressed", "S4 Twelve habits", "S5 Saved habits", "A habit just added, at the bottom",
                          "Level 0, none of the habits", "Level 1, up to a third", "Level 2, up to two thirds", "Level 3, more than two thirds", "Level 4, all habits", "Today at level 4",
                          "Primary hover", "Secondary hover", "Danger hover", "Done hover", "Future, blank", "Up to a third", "More than two thirds", "Buttons: default", "Text input: default",
                          "Day bead and icon button", "Heatmap cell: levels"]
        chrome_classes = [".sheet", ".sheet-head", ".sheet-title", ".sheet-sub", ".group", ".group-title", ".frames", ".frame", ".frame-body", ".frame-cap", ".specs", ".spec", ".is-hover", ".is-focus", ".spec-input", ".spec-day", ".spec-cell", "figure", "figcaption"]
        found = {}
        states_checked = []
        for name, kwargs in (("S1 sample", dict(seed_sample=True)), ("S2 fresh", dict()), ("S4 twelve habits", dict(seed_text=twelve_habits())), ("S5 unreadable", dict(seed_text="{")),
                             ("sample + added habit", dict(seed_sample=True))):
            ctx, page = ctx_page(browser, BASE, **kwargs)
            if name == "sample + added habit":
                page.locator("#new-habit").click()
                page.keyboard.type("Drink water")
                page.keyboard.press("Enter")
                page.wait_for_timeout(300)
            if name == "S2 fresh":
                page.get_by_role("button", name="Add").click()
                page.wait_for_timeout(200)
            dom_text = page.evaluate("() => document.documentElement.outerHTML.replace(/<script[\\s\\S]*?<\\/script>/g, '')")
            hit_strings = [s for s in chrome_strings if s in dom_text]
            hit_classes = [c for c in chrome_classes if page.evaluate("(c) => document.querySelectorAll(c).length", c)]
            states_checked.append(name)
            if hit_strings or hit_classes:
                found[name] = {"strings": hit_strings, "classes": hit_classes}
            ctx.close()
        css_text = (ROOT / "src/styles.css").read_text(encoding="utf-8")
        css_hits = [c for c in (".sheet", ".group", ".frame", ".spec", ".is-hover", ".is-focus", "sheet only", ".specs", ".spec-input", ".spec-day", ".spec-cell") if c in css_text]
        facts["ST-17"] = {"states_scanned": states_checked, "sheet_strings_or_classes_found_in_live_dom": found, "sheet_only_rules_found_in_src_styles_css": css_hits}
        browser.close()

    save_json("states_sheet.json", {"cases": cases.out, "facts": facts})
    by_row = {}
    for c in cases.out:
        by_row.setdefault(c["row"], []).append(c)
    for row in sorted(by_row):
        bad = [c for c in by_row[row] if c["diffs"]]
        print(row, "cases", len(by_row[row]), "with differences", len(bad))
        for c in bad:
            print("   ", c["case"], c["diffs"][:6])
    print(json.dumps({k: v for k, v in facts.items() if k in ("ST-17",)}, indent=1))


run()
