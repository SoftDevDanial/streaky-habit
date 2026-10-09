"""FE element checklist, M1 rows (qa.md), measured on the running app at 390x844 and 1280x800 (scratch).
The dialog is opened with a real mouse click on "Delete Read 20 pages" (and, for M1-09, with the keyboard).
Writes rows_m1.json.
"""
import json

from common import *  # noqa: F401,F403
from measure import MEASURE_JS
from PIL import Image
from playwright.sync_api import sync_playwright

INK = "rgb(28, 37, 35)"
INK_SOFT = "rgb(82, 96, 91)"
RING = "rgb(126, 142, 136)"
BG = "rgb(242, 245, 243)"
SURFACE = "rgb(250, 252, 251)"
DANGER = "rgb(162, 59, 50)"
ON_BEAD = "rgb(247, 250, 249)"
TRANSPARENT = "rgba(0, 0, 0, 0)"
TITLE = 'Delete "⁨Read 20 pages⁩"?'
QA_DIR = ROOT / "docs/modules/app/qa"

EXP = {
    "390": dict(box=(20, 332, 350, 180), btnW=145),
    "1280": dict(box=(440, 310, 400, 180), btnW=170),
}

DIALOG_JS = r"""
() => {
  const round = (v) => Math.round(v * 100) / 100;
  const q = (s, r = document) => r.querySelector(s);
  const R = (el) => { const r = el.getBoundingClientRect(); return { x: round(r.x), y: round(r.y), w: round(r.width), h: round(r.height), r: round(r.right), b: round(r.bottom) }; };
  const C = (el, p, ps) => getComputedStyle(el, ps).getPropertyValue(p);
  const A = (el) => Object.fromEntries(Array.from(el.attributes).map((a) => [a.name, a.value]));
  const dlg = q("dialog.dialog"), title = q("#del-title"), body = q("#del-body"), form = q(".dialog-actions");
  const [cancel, del] = Array.from(form.querySelectorAll("button"));
  const font = (el) => ({ size: C(el, "font-size"), lh: C(el, "line-height"), weight: C(el, "font-weight"), color: C(el, "color") });
  const btn = (b) => ({ attrs: A(b), text: b.textContent.trim(), rect: R(b), bg: C(b, "background-color"), color: C(b, "color"), size: C(b, "font-size"), weight: C(b, "font-weight"),
    border: `${C(b, "border-top-width")} ${C(b, "border-top-style")} ${C(b, "border-top-color")}`, radius: C(b, "border-radius") });
  const bd = getComputedStyle(dlg, "::backdrop");
  return {
    open: dlg.open, modal: dlg.matches(":modal"), attrs: A(dlg), rect: R(dlg), bg: C(dlg, "background-color"), radius: C(dlg, "border-radius"), padding: C(dlg, "padding"),
    shadow: C(dlg, "box-shadow"), position: C(dlg, "position"), transform: C(dlg, "transform"), width: C(dlg, "width"), maxWidth: C(dlg, "max-width"),
    backdrop: { bg: bd.backgroundColor, position: bd.position, inset: bd.inset, animationName: bd.animationName, animationDuration: bd.animationDuration },
    title: { tag: title.tagName, id: title.id, text: title.textContent, rect: R(title), ...font(title) },
    body: { tag: body.tagName, id: body.id, text: body.textContent, rect: R(body), ...font(body) },
    form: { tag: form.tagName, attrs: A(form), display: C(form, "display"), cols: C(form, "grid-template-columns"), gap: C(form, "gap"), rect: R(form) },
    cancel: btn(cancel), del: btn(del),
    active: document.activeElement ? { tag: document.activeElement.tagName, text: document.activeElement.textContent.trim().slice(0, 30), inDialog: dlg.contains(document.activeElement),
      focusVisible: document.activeElement.matches(":focus-visible"), outline: `${C(document.activeElement, "outline-width")} ${C(document.activeElement, "outline-style")} ${C(document.activeElement, "outline-color")}`,
      outlineOffset: C(document.activeElement, "outline-offset") } : null,
    html: { height: C(document.documentElement, "height"), overflow: C(document.documentElement, "overflow"), bodyHeight: C(document.body, "height"), bodyOverflow: C(document.body, "overflow") },
    viewport: [innerWidth, innerHeight],
  };
}
"""


def deep_diff(a, b, path=""):
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                yield f"{path}.{k}", a.get(k, "<absent>"), b.get(k, "<absent>")
            else:
                yield from deep_diff(a[k], b[k], f"{path}.{k}")
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            yield f"{path}[len]", len(a), len(b)
        for i, (x, y) in enumerate(zip(a, b)):
            yield from deep_diff(x, y, f"{path}[{i}]")
    elif isinstance(a, float) and isinstance(b, float):
        if abs(a - b) > 0.011:
            yield path, a, b
    elif a != b:
        yield path, a, b


def latest(name):
    folders = sorted(p for p in (QA_DIR / name).iterdir() if p.is_dir())
    return folders[-1]


def run():
    rows = Rows()
    with sync_playwright() as pw:
        browser = launch(pw)
        for vk, vp in VIEWPORTS.items():
            e = EXP[vk]

            def R(row, cond, measured, expected, note=""):
                rows.chk(f"{row}@{vk}", cond, measured, expected, note)

            # ---- real mouse open
            ctx, page = open_page(browser, BASE, vp, seed=True)
            before = page.evaluate(MEASURE_JS)
            page.get_by_role("button", name="Delete Read 20 pages").click()
            page.wait_for_timeout(600)
            d = page.evaluate(DIALOG_JS)
            after = page.evaluate(MEASURE_JS)

            # M1-01: the page underneath is unchanged, cannot be clicked or focused
            b1, a1 = json.loads(json.dumps(before)), json.loads(json.dumps(after))
            for x in (b1, a1):
                x["nodes"].pop("dialog", None)
                x.pop("controls", None)
                x.pop("scroll", None)
                x.pop("innerText", None)  # the open dialog's own text is part of body.innerText
            diffs = list(deep_diff(b1, a1))
            probe = page.evaluate(
                """() => {
                  const out = [];
                  for (const sel of ['button.day', '.icon-btn', '#new-habit', '.add .btn', '.cells .hc', 'h1.brand']) {
                    const el = document.querySelector(sel);
                    const r = el.getBoundingClientRect();
                    const hit = document.elementFromPoint(r.x + r.width / 2, r.y + r.height / 2);
                    const before = document.activeElement;
                    try { el.focus(); } catch (e) {}
                    out.push({ sel, hitIsPage: !!(hit && hit.closest('.page')), hit: hit ? hit.tagName + '.' + hit.className : null, focusMoved: document.activeElement === el });
                    if (before && before !== document.activeElement) before.focus();
                  }
                  return out;
                }"""
            )
            tab_ok = True
            tab_trail = []
            for _ in range(10):
                page.keyboard.press("Tab")
                st = page.evaluate(
                    "() => { const a = document.activeElement; return { name: a === document.body ? '(document, focus left the page)' : (a.textContent || '').trim().slice(0, 20),"
                    " inDialog: !!a.closest('dialog.dialog'), isDocument: a === document.body || a === document.documentElement, behindPage: !!a.closest('.page') }; }"
                )
                tab_trail.append(st["name"])
                tab_ok &= (st["inDialog"] or st["isDocument"]) and not st["behindPage"]
            R("M1-01", not diffs and all(not p["hitIsPage"] and not p["focusMoved"] for p in probe) and tab_ok,
              f"page measurement with the dialog open vs closed: {len(diffs)} differences; hit test on 6 page targets reaches the page: {[p['hitIsPage'] for p in probe]}; focus() on them moves focus: {[p['focusMoved'] for p in probe]}; 10 Tab presses never land on a page control: {tab_ok} (trail {tab_trail[:5]})",
              "S1 unchanged underneath, not clickable (hit test lands on the dialog layer), not focusable, Tab never reaches a control behind the dialog", note=json.dumps(diffs[:3]))

            # M1-02 backdrop: computed style plus the pixel the harness captured
            cand = latest(f"fidelity-delete-dialog-{vk}x{vp[1]}") / "candidate.png"
            im = Image.open(cand).convert("RGB")
            px = [im.getpixel((2, 2)), im.getpixel((vp[0] - 3, 2)), im.getpixel((2, vp[1] - 3)), im.getpixel((vp[0] - 3, vp[1] - 3))]
            want = (135, 141, 139)
            pix_ok = all(all(abs(c - w) <= 1 for c, w in zip(p, want)) for p in px)
            bdp = d["backdrop"]
            R("M1-02", bdp["bg"] == "rgba(28, 37, 35, 0.5)" and bdp["position"] == "fixed" and bdp["inset"] == "0px" and pix_ok,
              f"::backdrop {bdp['bg']} {bdp['position']} inset {bdp['inset']}; harness candidate.png corner pixels {px} (page bg {BG} under --scrim blends to {want})",
              "--scrim rgb(28 37 35 / 0.5) over the whole viewport, native ::backdrop")

            # M1-03 box
            bx = d["rect"]
            cx_ok = abs(bx["x"] - (vp[0] - bx["w"]) / 2) < 0.51 and abs(bx["y"] - (vp[1] - bx["h"]) / 2) < 0.51
            sh = d["shadow"]
            R("M1-03", d["open"] and d["modal"] and d["attrs"].get("role") == "alertdialog" and d["attrs"].get("aria-modal") == "true" and d["attrs"].get("aria-labelledby") == "del-title"
              and d["attrs"].get("aria-describedby") == "del-body" and d["bg"] == SURFACE and d["radius"] == "20px" and d["padding"] == "24px"
              and sh == "rgba(28, 37, 35, 0.18) 0px 16px 48px 0px, rgba(28, 37, 35, 0.08) 0px 2px 6px 0px"
              and (bx["x"], bx["y"], bx["w"], bx["h"]) == e["box"] and cx_ok and d["transform"] == "none",
              f"open {d['open']}, :modal {d['modal']}, role {d['attrs'].get('role')}, aria-modal {d['attrs'].get('aria-modal')}, labelledby {d['attrs'].get('aria-labelledby')}, describedby {d['attrs'].get('aria-describedby')}; {bx['w']}x{bx['h']} at x {bx['x']}, y {bx['y']}; bg {d['bg']}, radius {d['radius']}, padding {d['padding']}, shadow {sh}",
              f"{e['box'][2]}x{e['box'][3]} at x {e['box'][0]}, y {e['box'][1]}, centred both ways, surface fill, radius 20, padding 24, dialog shadow, alertdialog/aria-modal/labelledby/describedby")

            # M1-04 title
            t = d["title"]
            visible_title = t["text"].replace("⁨", "").replace("⁩", "")
            R("M1-04", t["tag"] == "H2" and t["id"] == "del-title" and t["text"] == TITLE and visible_title == 'Delete "Read 20 pages"?' and '"' in visible_title and "“" not in t["text"]
              and t["size"] == "18px" and t["lh"] == "28px" and t["weight"] == "600" and t["color"] == INK and t["rect"]["h"] == 28 and abs(t["rect"]["y"] - bx["y"] - 24) < 0.01,
              f"text {json.dumps(t['text'])} (visible: {visible_title}), {t['size']}/{t['lh']} w{t['weight']} {t['color']}, height {t['rect']['h']}, {round(t['rect']['y'] - bx['y'], 2)} from the top",
              'Delete "Read 20 pages"? with straight quotes (plus the invisible U+2068 and U+2069 of SEC-02), 18/28 600 ink, one line, 24 from the top')

            # M1-05
            bo = d["body"]
            R("M1-05", bo["tag"] == "P" and bo["id"] == "del-body" and bo["text"] == "Its history is deleted too." and bo["size"] == "16px" and bo["lh"] == "24px" and bo["color"] == INK_SOFT
              and abs(bo["rect"]["y"] - t["rect"]["b"] - 8) < 0.01,
              f"'{bo['text']}' {bo['size']}/{bo['lh']} {bo['color']}, {round(bo['rect']['y'] - t['rect']['b'], 2)} below the title", "'Its history is deleted too.' 16/24 ink-soft, 8 below the title")

            # M1-06
            fo = d["form"]
            c, dl = d["cancel"], d["del"]
            R("M1-06", fo["tag"] == "FORM" and fo["attrs"].get("method") == "dialog" and fo["attrs"].get("class") == "dialog-actions" and abs(fo["rect"]["y"] - bo["rect"]["b"] - 24) < 0.01
              and abs(c["rect"]["w"] - e["btnW"]) < 0.01 and abs(dl["rect"]["w"] - e["btnW"]) < 0.01 and c["rect"]["h"] == 48 and dl["rect"]["h"] == 48 and abs(dl["rect"]["x"] - c["rect"]["r"] - 12) < 0.01,
              f"form[method={fo['attrs'].get('method')}].{fo['attrs'].get('class')}, {round(fo['rect']['y'] - bo['rect']['b'], 2)} below the body; columns {fo['cols']}, gap {fo['gap']}; buttons {c['rect']['w']} and {dl['rect']['w']} wide, {c['rect']['h']} and {dl['rect']['h']} tall, {round(dl['rect']['x'] - c['rect']['r'], 2)} apart",
              f"two equal columns 12 apart, 24 below the body, each {e['btnW']} wide and 48 tall")

            # M1-07 / M1-08
            R("M1-07", c["attrs"].get("class") == "btn btn-secondary" and c["attrs"].get("type") == "submit" and c["attrs"].get("value") == "cancel" and c["text"] == "Cancel" and c["bg"] == TRANSPARENT
              and c["border"] == f"2px solid {RING}" and c["color"] == INK and c["size"] == "16px" and c["weight"] == "600" and c["rect"]["x"] < dl["rect"]["x"],
              f".{c['attrs'].get('class').replace(' ', '.')}[type={c['attrs'].get('type')}][value={c['attrs'].get('value')}] '{c['text']}' bg {c['bg']}, border {c['border']}, {c['color']} {c['size']} w{c['weight']}, left (x {c['rect']['x']})",
              f".btn.btn-secondary[type=submit][value=cancel] 'Cancel', transparent, 2px {RING} border, {INK} 16 600, left")
            R("M1-08", dl["attrs"].get("class") == "btn btn-danger" and dl["attrs"].get("type") == "submit" and dl["attrs"].get("value") == "delete" and dl["text"] == "Delete habit" and dl["bg"] == DANGER
              and dl["color"] == ON_BEAD and c["bg"] == TRANSPARENT and dl["rect"]["x"] > c["rect"]["x"],
              f".{dl['attrs'].get('class').replace(' ', '.')}[type={dl['attrs'].get('type')}][value={dl['attrs'].get('value')}] '{dl['text']}' bg {dl['bg']}, text {dl['color']}, right (x {dl['rect']['x']}); Cancel bg {c['bg']}",
              f".btn.btn-danger[type=submit][value=delete] 'Delete habit', {DANGER} fill, {ON_BEAD} text, the only filled button")

            # M1-10 no scroll while open, restored after
            h = d["html"]
            R("M1-10", h["height"] == f"{vp[1]}px" and h["overflow"] == "hidden" and h["bodyHeight"] == f"{vp[1]}px" and h["bodyOverflow"] == "hidden",
              f"open: html height {h['height']} overflow {h['overflow']}, body height {h['bodyHeight']} overflow {h['bodyOverflow']}", f"html and body height 100% ({vp[1]}px) and overflow hidden while open")
            page.keyboard.press("Escape")
            page.wait_for_timeout(300)
            closed = page.evaluate("() => ({ open: document.querySelector('dialog.dialog').open, ov: getComputedStyle(document.documentElement).overflow, bov: getComputedStyle(document.body).overflow })")
            R("M1-10b", (not closed["open"]) and closed["ov"] == "visible" and closed["bov"] == "visible", f"after Esc: open {closed['open']}, html overflow {closed['ov']}, body overflow {closed['bov']}", "page scrolls again once closed")
            ctx.close()

            # M1-09 initial focus after a mouse open, then after a keyboard open
            ctx, page = open_page(browser, BASE, vp, seed=True)
            page.get_by_role("button", name="Delete Read 20 pages").click()
            page.wait_for_timeout(400)
            dm = page.evaluate(DIALOG_JS)
            ctx.close()
            ctx, page = open_page(browser, BASE, vp, seed=True)
            page.keyboard.press("Tab")
            first = page.evaluate("() => document.activeElement.getAttribute('aria-label')")
            page.keyboard.press("Enter")
            page.wait_for_timeout(400)
            dk = page.evaluate(DIALOG_JS)
            ctx.close()
            am, ak = dm["active"], dk["active"]
            R("M1-09", am["text"] == "Cancel" and am["inDialog"] and not am["focusVisible"] and am["outline"].split()[1] == "none"
              and ak["text"] == "Cancel" and ak["focusVisible"] and ak["outline"] == f"2px solid {INK}" and ak["outlineOffset"] == "3px",
              f"mouse open: focus on '{am['text']}', :focus-visible {am['focusVisible']}, outline {am['outline']}; keyboard open (Tab to '{first}', Enter): focus on '{ak['text']}', :focus-visible {ak['focusVisible']}, outline {ak['outline']}, offset {ak['outlineOffset']}",
              "Cancel is focused on open; no ring after a mouse open, the 2px --focus ring with a 3px offset after a keyboard open")

            # M1-11 entrance, normal and reduced motion
            ctx, page = open_page(browser, BASE, vp, seed=True, reduced="no-preference")
            anim = page.evaluate(
                """() => {
                  document.querySelector('button[aria-label="Delete Read 20 pages"]').click();
                  return document.getAnimations().map((a) => {
                    const ef = a.effect;
                    const t = ef.getTiming();
                    return { name: a.animationName, pseudo: ef.pseudoElement, target: ef.target ? ef.target.className : null, duration: t.duration, easing: t.easing,
                             keyframes: ef.getKeyframes().map((k) => ({ opacity: k.opacity, transform: k.transform, offset: k.offset })) };
                  });
                }"""
            )
            ctx.close()
            ctx, page = open_page(browser, BASE, vp, seed=True, reduced="reduce")
            anim_reduced = page.evaluate(
                """() => {
                  document.querySelector('button[aria-label="Delete Read 20 pages"]').click();
                  const dlg = document.querySelector('dialog.dialog');
                  return { count: document.getAnimations().length, dialogAnim: getComputedStyle(dlg).animationName, backdropAnim: getComputedStyle(dlg, '::backdrop').animationName,
                           dialogTransition: getComputedStyle(dlg).transitionDuration };
                }"""
            )
            ctx.close()
            backdrop_a = next((a for a in anim if a["pseudo"] == "::backdrop"), None)
            dialog_a = next((a for a in anim if a["pseudo"] is None and "dialog" in (a["target"] or "")), None)
            R("M1-11", backdrop_a and dialog_a and backdrop_a["name"] == "scrim-in" and backdrop_a["duration"] == 180 and dialog_a["name"] == "dialog-in" and dialog_a["duration"] == 200
              and dialog_a["keyframes"][0]["opacity"] == "0" and dialog_a["keyframes"][0]["transform"] == "translateY(8px)" and anim_reduced["count"] == 0
              and anim_reduced["dialogAnim"] == "none" and anim_reduced["backdropAnim"] == "none",
              f"normal motion: backdrop {backdrop_a['name'] if backdrop_a else None} {backdrop_a['duration'] if backdrop_a else None}ms {backdrop_a['keyframes'] if backdrop_a else None}; dialog {dialog_a['name'] if dialog_a else None} {dialog_a['duration'] if dialog_a else None}ms first keyframe {dialog_a['keyframes'][0] if dialog_a else None}; reduced motion: {anim_reduced['count']} running animations, dialog animation-name {anim_reduced['dialogAnim']}, ::backdrop {anim_reduced['backdropAnim']}",
              "backdrop fades in over 180ms, dialog fades and rises 8px over 200ms; both instant under reduced motion")

            # M1-04b: a long name wraps, the box grows in height only
            long_name = "W" * 40
            seed_long = json.dumps({"version": 1, "habits": [{"name": long_name, "done": []}]})
            ctx = browser.new_context(viewport={"width": vp[0], "height": vp[1]}, device_scale_factor=1, color_scheme="light", locale="en-US")
            page = ctx.new_page()
            page.clock.set_fixed_time(FIXED)
            page.add_init_script(f"localStorage.setItem('streaks.state', {json.dumps(seed_long)})")
            page.goto(BASE, wait_until="networkidle")
            page.get_by_role("button", name=f"Delete {long_name}").click()
            page.wait_for_timeout(600)
            dlong = page.evaluate(DIALOG_JS)
            ctx.close()
            lines = round(dlong["title"]["rect"]["h"] / 28)
            R("M1-04b", dlong["rect"]["w"] == e["box"][2] and dlong["rect"]["h"] > 180 and lines >= 2 and dlong["rect"]["b"] <= vp[1] and abs(dlong["rect"]["y"] - (vp[1] - dlong["rect"]["h"]) / 2) < 0.51,
              f"40-character name: title {lines} lines ({dlong['title']['rect']['h']}px), box {dlong['rect']['w']}x{dlong['rect']['h']} (width unchanged {e['box'][2]}), still centred at y {dlong['rect']['y']}",
              "long names wrap and the box grows in height only")
        browser.close()
    rows.save("rows_m1.json")
    passed, failed = rows.summary()
    print("rows", len(rows.rows), "pass", passed, "fail", failed)
    for r in rows.rows:
        if r["result"] == "FAIL":
            print(json.dumps(r, indent=1, ensure_ascii=False)[:2500])
        else:
            print(r["id"], "PASS |", str(r["measured"])[:300])


run()
