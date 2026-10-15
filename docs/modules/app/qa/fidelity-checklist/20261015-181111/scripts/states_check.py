"""states.html checklist rows ST-01 to ST-06 by the computed-style method of qa.md (Fidelity gate), task 28.

Run from the project root:  python -B <this file> <checklist folder>
At 360x780 and 1280x800 it opens docs/design/states.html from its file path (read only) and the running app in
the same state, reached with real gestures through conftest.open_app (clipboard stand-in first in every context,
the sample day's fixed clock, seeding on the __seed__ page). S2 by three submits, S4 by driver D-a and one press of
"Done today, Stretch 10 minutes", S5 by storage "{". Each specimen element is compared with its live element on the
method's properties (and width and height for buttons). Every other computed property is compared too and reported
as information. Writes <checklist>/states/ (states-check.json, screenshots), refusing to overwrite. One server.
"""
import json
import pathlib
import re
import sys
import time

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import gate_runner as gr  # noqa: E402

sys.path.insert(0, str(gr.ROOT / "tests" / "browser"))
import conftest as cf  # noqa: E402  (CLIPBOARD_STANDIN, FAIL_SETITEM, sample_state, open_app; nothing starts on import)

from playwright.sync_api import sync_playwright  # noqa: E402

OUT = pathlib.Path(sys.argv[1]) / "states"
if OUT.exists():
    sys.exit(f"refused, {OUT} exists")

SIDES = ["top", "right", "bottom", "left"]
METHOD = (["color", "background-color"]
          + [f"border-{s}-{p}" for s in SIDES for p in ("color", "style", "width")]
          + [f"border-{c}-radius" for c in ("top-left", "top-right", "bottom-right", "bottom-left")]
          + [f"padding-{s}" for s in SIDES] + [f"margin-{s}" for s in SIDES]
          + ["font-size", "font-weight", "line-height"])
BUTTON = ["width", "height"]
SVG = ["fill", "stroke", "stroke-width", "stroke-dasharray", "stroke-linecap", "r", "width", "height"]

READ_JS = """([selector, props]) => {
  const nodes = document.querySelectorAll(selector);
  if (nodes.length !== 1) return { count: nodes.length };
  const el = nodes[0];
  const cs = getComputedStyle(el);
  const picked = {};
  for (const p of props) picked[p] = cs.getPropertyValue(p);
  const all = {};
  for (let i = 0; i < cs.length; i++) all[cs[i]] = cs.getPropertyValue(cs[i]);
  const r = el.getBoundingClientRect();
  const attrs = {};
  for (const a of el.attributes) attrs[a.name] = a.value;
  return { count: 1, tag: el.tagName.toLowerCase(), picked, all, attrs, text: el.textContent,
    rect: [r.x, r.y, r.width, r.height].map((v) => Math.round(v * 100) / 100),
    children: Array.from(el.children).map((c) => c.tagName.toLowerCase() + (c.className && typeof c.className === 'string' ? '.' + c.className.split(' ').join('.') : '')),
    value: 'value' in el ? el.value : null, focused: document.activeElement === el };
}"""

# Properties that differ by layout or by the sheet's frame and say nothing about the element's own styling.
LAYOUT_INFO = {"width", "height", "inline-size", "block-size", "inset-block-start", "inset-block-end", "inset-inline-start",
               "inset-inline-end", "top", "bottom", "left", "right", "perspective-origin", "transform-origin",
               "min-inline-size", "min-block-size", "max-inline-size", "max-block-size", "grid-column-start", "grid-row-start",
               "grid-column-end", "grid-row-end"}

SAMPLE = None


def settle(page, seconds=3.0):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if page.evaluate("() => document.getAnimations().filter((a) => a.playState === 'running').length") == 0:
            return True
        time.sleep(0.05)
    return False


def park(page):
    page.mouse.move(2, 2)  # the page's own margin, so no hover state shows


def read(page, selector, props):
    return page.evaluate(READ_JS, [selector, props])


def compare(case, spec_page, spec_sel, live_page, live_sel, kind="box"):
    props = METHOD + (BUTTON if kind == "button" else []) + (SVG if kind == "svg" else [])
    a, b = read(spec_page, spec_sel, props), read(live_page, live_sel, props)
    rec = {"case": case, "specimen": spec_sel, "live": live_sel, "kind": kind}
    if a["count"] != 1 or b["count"] != 1:
        rec.update({"result": "FAIL", "why": f"found {a['count']} specimen and {b['count']} live elements"})
        return rec
    diffs = {p: [a["picked"][p], b["picked"][p]] for p in props if a["picked"][p] != b["picked"][p]}
    info = {p: [a["all"].get(p), b["all"].get(p)] for p in sorted(set(a["all"]) | set(b["all"]))
            if p not in props and a["all"].get(p) != b["all"].get(p)}
    rec.update({"result": "PASS" if not diffs else "FAIL", "compared": len(props), "differences": diffs,
                "other_properties_differing": {p: v for p, v in info.items() if p not in LAYOUT_INFO},
                "layout_properties_differing": sorted(p for p in info if p in LAYOUT_INFO),
                "text": [a["text"], b["text"]], "tag": [a["tag"], b["tag"]],
                "children": [a["children"], b["children"]], "rect": [a["rect"], b["rect"]],
                "attrs": [a["attrs"], b["attrs"]], "value": [a["value"], b["value"]], "live_focused": b["focused"]})
    return rec


def check(rec, name, ok, detail=None):
    rec.setdefault("checks", []).append({"check": name, "result": "PASS" if ok else "FAIL", "detail": detail})


def main():
    head = gr.git("rev-parse", "HEAD")
    proc, port, cmd = gr.start_server()
    base = f"http://127.0.0.1:{port}/"
    print(json.dumps({"server": {"pid": proc.pid, "port": port}, "head": head}), flush=True)
    sheet_url = (gr.ROOT / "docs" / "design" / "states.html").resolve().as_uri()
    result = {"head": head, "server": {"pid": proc.pid, "port": port, "command": cmd}, "rows": {}, "viewports": {}}
    OUT.mkdir(parents=True)
    try:
        with sync_playwright() as pw:
            browser = cf.launch(pw, "chromium")
            result["browser_version"] = browser.version
            for vp in ((360, 780), (1280, 800)):
                tag = f"{vp[0]}x{vp[1]}"
                rows = {f"ST-0{n}": [] for n in range(1, 7)}
                sctx = browser.new_context(viewport={"width": vp[0], "height": vp[1]}, device_scale_factor=1,
                                           color_scheme="dark", timezone_id=cf.TZ)
                sctx.add_init_script(cf.CLIPBOARD_STANDIN)
                sheet = sctx.new_page()
                sheet.goto(sheet_url)
                settle(sheet)
                sheet.screenshot(path=(OUT / f"states-sheet-{tag}.png").as_posix(), full_page=True)

                # S2, three submits on the sample day
                ctx, page = cf.open_app(browser, viewport=vp, storage=cf.sample_state(), base_url=base)
                settle(page)
                field_before = read(page, "#nh", [])["rect"]
                k1_field = read(page, "#nh", METHOD)
                for row, typed, spec, msg_text in (("ST-01", None, "s2a", "Name the habit first."),
                                                   ("ST-02", "Read twenty pages of a novel before bed each night", "s2b", "Keep it to 40 characters or fewer."),
                                                   ("ST-03", "read 20 pages", "s2c", "You already track this habit.")):
                    if typed is not None:
                        page.fill("#nh", typed)
                    page.click("#add-btn")
                    page.wait_for_function("(t) => document.querySelector('#nh-msg').textContent === t && !document.querySelector('#nh-msg').hidden",
                                           arg=msg_text, timeout=5000)
                    park(page)
                    settle(page)
                    page.screenshot(path=(OUT / f"live-{row}-{tag}.png").as_posix())
                    s = f"section[aria-labelledby={spec}] "
                    msg = compare(row + " message", sheet, s + "p.field-msg", page, "#nh-msg")
                    check(msg, "text", msg["text"] == [msg_text, msg_text], msg["text"])
                    check(msg, "classes field-msg err", msg["attrs"][1].get("class") == "field-msg err", msg["attrs"][1].get("class"))
                    check(msg, "aria-live polite", msg["attrs"][1].get("aria-live") == "polite")
                    rows[row].append(msg)
                    fld = compare(row + " field", sheet, s + "input.input", page, "#nh")
                    check(fld, "aria-invalid true", fld["attrs"][1].get("aria-invalid") == "true", fld["attrs"][1].get("aria-invalid"))
                    check(fld, "field value equals the specimen's", fld["value"][1] == (fld["value"][0] or ""), fld["value"])
                    check(fld, "the field did not move", fld["rect"][1] == field_before, [field_before, fld["rect"][1]])
                    rows[row].append(fld)
                    rows[row].append(compare(row + " label", sheet, s + "label.add-label", page, "form.composer label.add-label"))
                    add = compare(row + " Add", sheet, s + "button.btn-primary", page, "#add-btn", "button")
                    rows[row].append(add)
                    rows[row].append(compare(row + " Add icon", sheet, s + "button.btn-primary svg.ph", page, "#add-btn svg.ph", "svg"))
                    rows[row].append(compare(row + " composer", sheet, s + "form.composer", page, "form.composer"))
                    rows[row].append(compare(row + " add-ctl", sheet, s + "div.add-ctl", page, "form.composer div.add-ctl"))
                    # "the rest of the composer as K1": the label and Add of K1 equal these, the field only by its edge colour
                    err_field = read(page, "#nh", METHOD)
                    changed = {q: [k1_field["picked"][q], err_field["picked"][q]] for q in METHOD
                               if k1_field["picked"][q] != err_field["picked"][q]}
                    edges = [f"border-{side}-color" for side in SIDES]
                    check(fld, "against K1's field only the edge colour changed, to --danger",
                          sorted(changed) == sorted(edges) and all(v[1] == "rgb(255, 107, 102)" for v in changed.values()), changed)
                ctx.close()

                # S4, driver D-a and one press of Done today, Stretch 10 minutes
                ctx, page = cf.open_app(browser, viewport=vp, storage=cf.sample_state(), init_script=cf.FAIL_SETITEM, base_url=base)
                settle(page)
                page.click('button[aria-label="Done today, Stretch 10 minutes"]')
                page.wait_for_selector("div.banners div.banner.warn", state="visible", timeout=5000)
                park(page)
                settle(page)
                page.screenshot(path=(OUT / f"live-ST-04-{tag}.png").as_posix())
                s = "section[aria-labelledby=s4] "
                ban = compare("ST-04 banner", sheet, s + "div.banner.warn", page, "div.banners div.banner.warn")
                check(ban, "role status", ban["attrs"][1].get("role") == "status")
                check(ban, "holds only a p, no button", ban["children"][1] == ["p"], ban["children"])
                geo = page.evaluate("""() => {
                  const r = (s) => { const e = document.querySelector(s); if (!e) return null; const b = e.getBoundingClientRect(); return getComputedStyle(e).display === 'none' ? null : [b.top, b.bottom]; };
                  return { header: r('header.top'), band: r('section.band'), banners: r('div.banners'), frame: r('div.frame-wrap'),
                           first_in_banners: document.querySelector('div.banners').firstElementChild.className };
                }""")
                above = geo["band"] if geo["band"] else geo["header"]
                check(ban, "between the band (desktop) or the header (phone) and the list",
                      above[1] <= geo["banners"][0] and geo["banners"][1] <= geo["frame"][0], geo)
                rows["ST-04"].append(ban)
                p = compare("ST-04 text", sheet, s + "div.banner.warn p", page, "div.banners div.banner.warn p")
                check(p, "text", p["text"][0] == p["text"][1], p["text"])
                rows["ST-04"].append(p)
                ctx.close()

                # S5, storage "{"
                ctx, page = cf.open_app(browser, viewport=vp, storage="{", base_url=base)
                page.wait_for_selector("div.banners div.banner.note", state="visible", timeout=5000)
                park(page)
                settle(page)
                page.screenshot(path=(OUT / f"live-ST-05-{tag}.png").as_posix())
                s = "section[aria-labelledby=s5] "
                ban = compare("ST-05 banner", sheet, s + "div.banner.note", page, "div.banners div.banner.note")
                check(ban, "role status", ban["attrs"][1].get("role") == "status")
                check(ban, "children p then button.icon-btn", ban["children"][1] == ["p", "button.icon-btn"], ban["children"])
                rows["ST-05"].append(ban)
                p = compare("ST-05 text", sheet, s + "div.banner.note p", page, "div.banners div.banner.note p")
                check(p, "text", p["text"][0] == p["text"][1], p["text"])
                rows["ST-05"].append(p)
                btn = compare("ST-05 Dismiss", sheet, s + "button.icon-btn", page, "div.banner.note button.icon-btn", "button")
                check(btn, "named Dismiss note", btn["attrs"][1].get("aria-label") == "Dismiss note")
                rows["ST-05"].append(btn)
                rows["ST-05"].append(compare("ST-05 Dismiss icon", sheet, s + "button.icon-btn svg.ph", page, "div.banner.note button.icon-btn svg.ph", "svg"))
                rows["ST-05"].append(compare("ST-05 Dismiss icon use", sheet, s + "button.icon-btn svg.ph use", page, "div.banner.note button.icon-btn svg.ph use", "svg"))
                for spec_sel, live_sel, kind in (("li.empty", "ul.rows li.empty", "box"), ("li.empty svg", "ul.rows li.empty svg", "svg"),
                                                 ("li.empty circle.e-orbit", "ul.rows li.empty circle.e-orbit", "svg"),
                                                 ("li.empty circle.e-core", "ul.rows li.empty circle.e-core", "svg"),
                                                 ("li.empty > div", "ul.rows li.empty > div", "box"), ("li.empty p.lead", "ul.rows li.empty p.lead", "box"),
                                                 ("li.empty p.line", "ul.rows li.empty p.line", "box"), ("ul.rows", "div.frame ul.rows", "box")):
                    rec = compare("ST-05 " + spec_sel, sheet, s + spec_sel, page, live_sel, kind)
                    if spec_sel.endswith("p.lead") or spec_sel.endswith("p.line"):
                        check(rec, "text", rec["text"][0] == rec["text"][1], rec["text"])
                    rows["ST-05"].append(rec)
                gap = page.evaluate("() => document.querySelector('div.frame-wrap').getBoundingClientRect().top - document.querySelector('div.banners').getBoundingClientRect().bottom")
                sgap = sheet.evaluate("() => document.querySelector('section[aria-labelledby=s5] div.frame').getBoundingClientRect().top - document.querySelector('section[aria-labelledby=s5] div.banners').getBoundingClientRect().bottom")
                check(rows["ST-05"][0], "12 apart from the empty list, as the specimen", gap == sgap == 12, [sgap, gap])
                ctx.close()

                # ST-06, the sheet's own chrome exists nowhere in the app (four live states and the stylesheet)
                chrome = {"selectors": ["main.sheet", ".spec", ".stack", "#n1", "#n2", "#n3", "#m1", "#m2", "#m3"],
                          "texts": [sheet.evaluate("() => document.querySelector('main.sheet > h1').textContent")]
                          + sheet.evaluate("() => Array.from(document.querySelectorAll('section.spec > h2'), (h) => h.textContent)")}
                found = []
                for name, storage, init in (("sample", cf.sample_state(), None), ("fresh", None, None), ("twelve", cf.twelve_state(), None),
                                            ("unreadable", "{", None), ("save-fails", cf.sample_state(), cf.FAIL_SETITEM)):
                    ctx, page = cf.open_app(browser, viewport=vp, storage=storage, init_script=init, base_url=base)
                    settle(page)
                    if name == "save-fails":
                        page.click('button[aria-label="Done today, Stretch 10 minutes"]')
                        page.wait_for_selector("div.banner.warn", timeout=5000)
                    hits = page.evaluate("""([sels, texts]) => ({
                      selectors: sels.filter((s) => document.querySelector(s) !== null),
                      texts: texts.filter((t) => document.body.textContent.includes(t)) })""", [chrome["selectors"], chrome["texts"]])
                    found.append({"state": name, **hits})
                    ctx.close()
                css = (gr.ROOT / "src" / "styles.css").read_text(encoding="utf-8")
                css_hits = sorted(set(re.findall(r"\.(?:sheet|spec|stack)(?![\w-])", css)))
                st6 = {"case": "ST-06 sheet chrome absent", "chrome": chrome, "found_in_live_dom": found, "styles_css_hits": css_hits}
                ok = all(not f["selectors"] and not f["texts"] for f in found) and not css_hits
                st6["result"] = "PASS" if ok else "FAIL"
                rows["ST-06"].append(st6)
                sctx.close()

                verdict = {}
                for row, recs in rows.items():
                    fails = [r["case"] for r in recs if r["result"] != "PASS"] + \
                            [f"{r['case']}: {c['check']}" for r in recs for c in r.get("checks", []) if c["result"] != "PASS"]
                    verdict[row] = {"result": "PASS" if not fails else "FAIL", "comparisons": len(recs),
                                    "property_comparisons": sum(r.get("compared", 0) for r in recs),
                                    "checks": sum(len(r.get("checks", [])) for r in recs), "fails": fails}
                result["viewports"][tag] = {"verdict": verdict, "rows": rows}
                print(json.dumps({tag: verdict}), flush=True)
            browser.close()
    finally:
        result["stopped"] = gr.stop_server(proc, port)
        (OUT / "states-check.json").write_text(json.dumps(result, indent=1, ensure_ascii=True), encoding="utf-8")
        print(json.dumps({"stopped": result["stopped"]}), flush=True)


if __name__ == "__main__":
    main()
