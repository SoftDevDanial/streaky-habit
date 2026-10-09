"""FE element checklist, S1 rows (qa.md), measured on the running app at 390x844 and 1280x800 (scratch).

Each row is judged on the running app against the value qa.md gives. The same measurement is also taken on the
golden and the two are compared, so a row that passes also equals the golden. Writes rows_s1.json and
measure_s1_<vp>_{golden,candidate}.json.
"""
import json
import re
from datetime import date as Date

from common import *  # noqa: F401,F403
from measure import MEASURE_JS
from playwright.sync_api import sync_playwright

HIST = json.loads((ROOT / "docs/design/sample-history.json").read_text(encoding="utf-8"))
LEVELS = HIST["heatmapLevels"]
HABITS = HIST["habits"]

BEAD = "rgb(59, 107, 96)"
BEAD_DEEP = "rgb(46, 90, 80)"
INK = "rgb(28, 37, 35)"
INK_SOFT = "rgb(82, 96, 91)"
RING = "rgb(126, 142, 136)"
BG = "rgb(242, 245, 243)"
THREAD = "rgb(198, 208, 204)"
ON_BEAD = "rgb(247, 250, 249)"
SURFACE = "rgb(250, 252, 251)"
TRANSPARENT = "rgba(0, 0, 0, 0)"
WD = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

EXP = {
    "390": dict(pageX=0, pageW=390, pagePad="24px 20px 48px", maxW="600px", hdrPB="24px", rowTops=[77, 273, 469], dayW=50.0, dayH=92,
                bead=36, formTop=673, inputW=256, heatTop=793, heatW=350, heatPad="20px 16px", cell=23.8, contentL=20, contentR=370),
    "1280": dict(pageX=120, pageW=1040, pagePad="40px 48px 48px", maxW="1040px", hdrPB="32px", rowTops=[101, 301, 501], dayW=71.43, dayH=96,
                 bead=40, formTop=709, inputW=406, heatTop=101, heatW=380, heatPad="24px", cell=24.9, contentL=168, contentR=1112),
}


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


def layers(shadow):
    found = re.findall(r"(rgba?\([^)]*\))\s+(-?[\d.]+)px\s+(-?[\d.]+)px\s+(-?[\d.]+)px\s+(-?[\d.]+)px(\s+inset)?", shadow)
    return [(c, float(x), float(y), float(b), float(s), bool(i)) for c, x, y, b, s, i in found]


def kind(half, slot_w):
    """Names what one half of the thread draws."""
    if half["display"] == "none":
        return "none"
    h, img, col = half["height"], half["bgImage"], half["bgColor"]
    if "linear-gradient" in img:
        if half["bgSize"].startswith("7px"):
            side = "right" if half["bgPos"].startswith("100%") else "left"
            ok = h == "4px" and img == "linear-gradient(to right, rgb(59, 107, 96) 0px, rgb(59, 107, 96) 4px, rgba(0, 0, 0, 0) 4px)" and half["bgRepeat"] == "repeat-x"
            return f"dashed-{side}" if ok else f"dashed?{img}|{half['bgSize']}|{half['bgPos']}"
        if h == "4px" and img.startswith("linear-gradient(to right, rgba(0, 0, 0, 0)") and BEAD in img:
            return "fade-run"
        if h == "2px" and img.startswith("linear-gradient(to right, rgba(0, 0, 0, 0)") and THREAD in img:
            return "fade-thin"
        return f"gradient?{img}"
    if h == "4px" and col == BEAD:
        return "run"
    if h == "2px" and col == THREAD:
        return "thin"
    return f"other?{h}|{col}|{img}"


def run():
    rows = Rows()
    with sync_playwright() as pw:
        browser = launch(pw)
        for vk, vp in VIEWPORTS.items():
            e = EXP[vk]
            gctx, gpage = open_page(browser, golden_url("S1"), vp)
            cctx, cpage = open_page(browser, BASE, vp, seed=True)
            g = gpage.evaluate(MEASURE_JS)
            m = cpage.evaluate(MEASURE_JS)
            save_json(f"measure_s1_{vk}_golden.json", g)
            save_json(f"measure_s1_{vk}_candidate.json", m)
            gctx.close()
            cctx.close()

            def R(row, cond, measured, expected, note=""):
                rows.chk(f"{row}@{vk}", cond, measured, expected, note)

            # ---- golden vs app, whole measurement (known, allowed differences removed first)
            gg, mm = json.loads(json.dumps(g)), json.loads(json.dumps(m))
            gg["sprite"]["symbols"] = [s for s in gg["sprite"]["symbols"]]
            mm["sprite"]["symbols"] = [s for s in mm["sprite"]["symbols"] if s["id"] != "i-x"]
            for d in (gg, mm):
                d.pop("controls", None)
            mm["nodes"].pop("dialog", None)
            gg["nodes"].pop("dialog", None)
            for c in mm["heat"]["months"]["spans"]:
                pass
            diffs = list(deep_diff(gg, mm))
            R("S1-GOLDEN-EQ", not diffs, f"{len(diffs)} differences", "0 differences between the golden's and the app's measurement",
              note=json.dumps(diffs[:5]))

            # S1-01
            b = m["body"]
            R("S1-01", b["bg"] == BG and b["color"] == INK and b["size"] == "16px" and b["lh"] == "24px" and b["weight"] == "400"
              and b["family"] == 'ui-rounded, "SF Pro Rounded", system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
              and b["margin"] == "0px",
              f"bg {b['bg']}, ink {b['color']}, {b['size']}/{b['lh']} w{b['weight']}, family {b['family'][:40]}...",
              f"{BG}, {INK}, 16px/24px, system rounded stack")

            # S1-02
            sp = m["sprite"]
            gsyms = {s["id"]: s for s in g["sprite"]["symbols"]}
            msyms = {s["id"]: s for s in sp["symbols"]}
            R("S1-02", sp["rect"]["w"] == 0 and sp["rect"]["h"] == 0 and sp["position"] == "absolute" and sp["attrs"].get("aria-hidden") == "true"
              and sp["attrs"].get("width") == "0" and sp["attrs"].get("height") == "0" and sp["attrs"].get("focusable") == "false"
              and msyms["i-check"]["d"] == gsyms["i-check"]["d"] and msyms["i-trash"]["d"] == gsyms["i-trash"]["d"]
              and sorted(msyms) == ["i-check", "i-trash", "i-x"],
              f"svg {sp['rect']['w']}x{sp['rect']['h']} {sp['position']} aria-hidden={sp['attrs'].get('aria-hidden')}; symbols {sorted(msyms)}; check/trash paths equal golden: "
              f"{msyms['i-check']['d'] == gsyms['i-check']['d']}/{msyms['i-trash']['d'] == gsyms['i-trash']['d']}",
              "0x0 absolute aria-hidden sprite, check and trash paths equal the golden, plus the invisible i-x")

            # S1-03
            p = m["page"]
            R("S1-03", p["rect"]["x"] == e["pageX"] and p["rect"]["w"] == e["pageW"] and p["padding"] == e["pagePad"] and p["maxWidth"] == e["maxW"],
              f"page x {p['rect']['x']} w {p['rect']['w']}, max-width {p['maxWidth']}, padding {p['padding']}",
              f"x {e['pageX']} w {e['pageW']}, max-width {e['maxW']}, padding {e['pagePad']}")

            # S1-04
            h = m["header"]
            R("S1-04", h["display"] == "flex" and h["alignItems"] == "baseline" and h["justify"] == "space-between" and h["gap"] == "12px" and h["paddingBottom"] == e["hdrPB"],
              f"{h['display']}, align {h['alignItems']}, justify {h['justify']}, gap {h['gap']}, padding-bottom {h['paddingBottom']}",
              f"flex, baseline, space-between, 12px, padding-bottom {e['hdrPB']}")

            # S1-05
            br = m["brand"]
            f = br["font"]
            R("S1-05", br["tag"] == "H1" and br["text"] == "Streaks" and f["size"] == "22px" and f["lh"] == "28px" and f["weight"] == "700"
              and f["ls"] == "-0.22px" and f["color"] == BEAD_DEEP and f["align"] in ("left", "start") and br["rect"]["x"] == e["contentL"],
              f"{br['tag']} '{br['text']}' {f['size']}/{f['lh']} w{f['weight']} ls {f['ls']} {f['color']} align {f['align']} x {br['rect']['x']}",
              f"H1 'Streaks' 22px/28px 700 -0.22px {BEAD_DEEP} left x {e['contentL']}")

            # S1-06
            dt = m["date"]
            f = dt["font"]
            R("S1-06", dt["timeTag"] == "TIME" and dt["datetime"] == "2026-10-08" and dt["timeText"] == "Thursday 8 October" and f["size"] == "16px" and f["lh"] == "24px"
              and f["color"] == INK_SOFT and f["align"] == "right" and abs(dt["rect"]["r"] - e["contentR"]) < 0.01,
              f"time[datetime={dt['datetime']}] '{dt['timeText']}' {f['size']}/{f['lh']} {f['color']} align {f['align']} right edge {dt['rect']['r']}",
              f"time[datetime=2026-10-08] 'Thursday 8 October' 16px/24px {INK_SOFT} right, right edge {e['contentR']}")
            R("S1-06b", abs(dt["baseline"] - br["baseline"]) <= 0.51, f"baseline brand {br['baseline']}, date {dt['baseline']}", "same baseline (within half a pixel)",
              note="baseline computed from the used font's ascent and descent and the line box")

            # S1-07
            L = m["layout"]
            if vk == "1280":
                ok = (L["display"] == "grid" and L["cols"] == "500px 380px" and L["colGap"] == "64px" and L["colMain"]["x"] == 168 and L["colMain"]["w"] == 500
                      and L["heat"]["x"] == 732 and L["heat"]["w"] == 380 and L["colMain"]["y"] == L["heat"]["y"] and L["alignItems"] in ("start", "flex-start"))
                R("S1-07", ok, f"{L['display']} cols {L['cols']} gap {L['colGap']}; main x {L['colMain']['x']} w {L['colMain']['w']}; heat x {L['heat']['x']} w {L['heat']['w']}; tops {L['colMain']['y']}/{L['heat']['y']}",
                  "grid 500px 380px, gap 64px, main 500 at x168, heat 380 at x732, top aligned")
            else:
                R("S1-07", L["display"] == "block" and L["colMain"]["w"] == 350 and L["heat"]["w"] == 350 and L["heat"]["y"] > L["colMain"]["b"],
                  f"phone: layout display {L['display']}, one column: main w {L['colMain']['w']}, heat below main (y {L['heat']['y']} > {L['colMain']['b']})",
                  "single column on the phone (the two-column grid applies from 900px)", note="the row's grid values are desktop values")

            # S1-08
            hh = m["hiddenHeading"]
            R("S1-08", hh["tag"] == "H2" and hh["text"] == "Habits" and hh["cls"] == "sr-only" and hh["rect"]["w"] == 1 and hh["rect"]["h"] == 1 and hh["position"] == "absolute"
              and hh["sectionTag"] == "SECTION" and hh["sectionLabelledby"] == "habits-title",
              f"{hh['tag']}#habits-title.{hh['cls']} '{hh['text']}' {hh['rect']['w']}x{hh['rect']['h']} {hh['position']}; section labelledby {hh['sectionLabelledby']}",
              "h2.sr-only 'Habits' clipped to 1x1, section labelled by it")

            # S1-09
            li = m["list"]
            tops = [r["y"] for r in li["rows"]]
            gaps = [round(li["rows"][i + 1]["y"] - li["rows"][i]["b"], 2) for i in range(2)]
            R("S1-09", li["listStyle"] == "none" and li["padding"] == "0px" and li["margin"] == "0px" and tops == e["rowTops"] and gaps == [32, 32] and li["rowGap"] == "32px",
              f"list-style {li['listStyle']}, padding {li['padding']}, row tops {tops}, gaps {gaps}", f"none, 0, row tops {e['rowTops']}, 32 apart")

            names = ["Read 20 pages", "Stretch 10 minutes", "No phone after 11pm"]
            curs = [("6 days", "Best 14"), ("3 days", "Best 9"), ("1 day", "Best 4")]
            patterns = [". D D D D D D", "D D . D D D .", ". D . . D . D"]
            continues = [False, True, False]
            # expected thread halves per row [(before, after) for each of 7 days]
            thread = [
                [("fade-thin", "thin"), ("thin", "run"), ("run", "run"), ("run", "run"), ("run", "run"), ("run", "run"), ("run", "none")],
                [("fade-run", "run"), ("run", "thin"), ("thin", "thin"), ("thin", "run"), ("run", "run"), ("run", "dashed-right"), ("dashed-left", "none")],
                [("fade-thin", "thin"), ("thin", "thin"), ("thin", "thin"), ("thin", "thin"), ("thin", "thin"), ("thin", "thin"), ("thin", "none")],
            ]
            ids = [("S1-10", "S1-11", "S1-12"), ("S1-13", "S1-14", "S1-15"), ("S1-16", "S1-17", "S1-18")]
            for i, row in enumerate(m["rows"]):
                r_head, r_streak, r_strip = ids[i]
                n = row["name"]
                bt = row["btn"]
                R(r_head, n["tag"] == "H3" and n["id"] == f"h{i + 1}-name" and n["text"] == names[i] and n["size"] == "18px" and n["lh"] == "28px" and n["weight"] == "600"
                  and n["color"] == INK and n["paddingTop"] == "8px" and n["wrap"] == "anywhere" and bt["label"] == f"Delete {names[i]}" and bt["type"] == "button",
                  f"{n['tag']}#{n['id']} '{n['text']}' {n['size']}/{n['lh']} w{n['weight']} {n['color']} pt {n['paddingTop']} wrap {n['wrap']}; trash '{bt['label']}'",
                  f"H3#h{i + 1}-name '{names[i]}' 18px/28px 600 {INK} pt 8px anywhere; trash 'Delete {names[i]}'")
                s = row["streak"]
                cu, be = s["cur"], s["best"]
                gap = round(be["rect"]["x"] - cu["rect"]["r"], 2) if be else None
                R(r_streak, cu["text"] == curs[i][0] and be and be["text"] == curs[i][1] and cu["size"] == "14px" and cu["lh"] == "20px" and cu["weight"] == "600" and cu["color"] == BEAD_DEEP
                  and cu["cls"] == "cur" and be["cls"] == "best" and be["size"] == "14px" and be["lh"] == "20px" and be["weight"] == "400" and be["color"] == INK_SOFT
                  and abs(gap - 12) < 0.01 and "tabular-nums" in s["tabular"] and abs(row["strip"]["rect"]["y"] - s["rect"]["b"] - 8) < 0.01 and s["live"] == "polite",
                  f"cur '{cu['text']}' {cu['size']}/{cu['lh']} w{cu['weight']} {cu['color']}; best '{be['text']}' {be['size']}/{be['lh']} w{be['weight']} {be['color']}; gap {gap}; {s['tabular']}; strip {round(row['strip']['rect']['y'] - s['rect']['b'], 2)} below",
                  f"'{curs[i][0]}' 14/20 600 {BEAD_DEEP}; '{curs[i][1]}' 14/20 400 {INK_SOFT}; 12 apart; tabular-nums; 8 above the strip")
                st = row["strip"]
                days = row["days"]
                pat = " ".join("D" if d["pressed"] == "true" else "." for d in days)
                dates = [d["date"] for d in days]
                halves = [(kind(d["before"], d["slot"]["w"]), kind(d["after"], d["slot"]["w"])) for d in days]
                # geometry of each half: before spans the left half of the slot, after the right half; centred on the bead
                geo_ok = True
                geo_note = []
                for d in days:
                    sw = d["slot"]["w"]
                    for nm, hv in (("before", d["before"]), ("after", d["after"])):
                        if hv["display"] == "none":
                            continue
                        height = float(hv["height"][:-2])
                        centre = float(hv["top"][:-2]) + float(hv["marginTop"][:-2]) + height / 2
                        want = d["slot"]["h"] / 2
                        if abs(centre - want) > 0.01 or abs(float(hv["marginTop"][:-2]) + height / 2) > 0.01:
                            geo_ok = False
                            geo_note.append((d["date"], nm, centre, want))
                        if nm == "before" and not (hv["left"] == "0px" and abs(float(hv["right"][:-2]) - sw / 2) < 0.02):
                            geo_ok = False
                            geo_note.append((d["date"], nm, hv["left"], hv["right"]))
                        if nm == "after" and not (hv["right"] == "0px" and abs(float(hv["left"][:-2]) - sw / 2) < 0.02):
                            geo_ok = False
                            geo_note.append((d["date"], nm, hv["left"], hv["right"]))
                today = days[6]
                ok = (dates == ["2026-10-02", "2026-10-03", "2026-10-04", "2026-10-05", "2026-10-06", "2026-10-07", "2026-10-08"] and pat == patterns[i] and st["runContinues"] == continues[i]
                      and halves == thread[i] and geo_ok and today["current"] == "date" and all(d["current"] is None for d in days[:6])
                      and st["role"] == "group" and st["labelledby"] == f"h{i + 1}-name")
                R(r_strip, ok, f"pattern '{pat}', data-run-continues {st['runContinues']}, halves {halves}, geometry ok {geo_ok} {geo_note[:2]}",
                  f"pattern '{patterns[i]}', data-run-continues {continues[i]}, halves {thread[i]}, every half centred on the bead")
            # dashed pattern detail (row 2)
            dd = m["rows"][1]["days"]
            a, b2 = dd[5]["after"], dd[6]["before"]
            R("S1-15b", a["bgSize"].startswith("7px") and a["bgPos"].startswith("100%") and b2["bgSize"].startswith("7px") and b2["bgPos"].startswith("0%")
              and a["bgImage"] == "linear-gradient(to right, rgb(59, 107, 96) 0px, rgb(59, 107, 96) 4px, rgba(0, 0, 0, 0) 4px)" and a["bgImage"] == b2["bgImage"],
              f"Wed 7 after: size {a['bgSize']} pos {a['bgPos']}; Thu 8 before: size {b2['bgSize']} pos {b2['bgPos']}; image {a['bgImage']}",
              "4px dash + 3px gap tile (7px), anchored right on Wed 7's right half and left on Thu 8's left half (a dash starts at the boundary)")

            # S1-19
            ok = True
            det = []
            for i, row in enumerate(m["rows"]):
                bt = row["btn"]
                n = row["name"]
                centre_line = n["rect"]["y"] + 8 + 14
                centre_btn = bt["rect"]["y"] + 22
                glyph_right = bt["svg"]["r"]
                cond = (bt["rect"]["w"] == 44 and bt["rect"]["h"] == 44 and bt["radius"] == "50%" and bt["bg"] == TRANSPARENT and bt["color"] == INK_SOFT and bt["svg"]["w"] == 20
                        and bt["svg"]["h"] == 20 and bt["svgFill"] == INK_SOFT and abs(bt["rect"]["r"] - row["head"]["r"] - 12) < 0.01 and abs(glyph_right - row["head"]["r"]) < 0.01
                        and abs(centre_line - centre_btn) < 0.01 and bt["href"] == "#i-trash")
                ok &= cond
                det.append(f"row{i + 1}: {bt['rect']['w']}x{bt['rect']['h']} {bt['radius']} {bt['color']}, glyph {bt['svg']['w']}px right edge {glyph_right} vs content edge {row['head']['r']}, name line centre {centre_line} vs button centre {centre_btn}")
            R("S1-19", ok, "; ".join(det), "44x44 circle, transparent, 20px trash glyph in ink-soft, glyph right edge on the content edge, name's first line centred on the button")

            # S1-20
            ok = True
            det = []
            for i, row in enumerate(m["rows"]):
                for d in row["days"]:
                    is_today = d["current"] == "date"
                    cond = (abs(d["rect"]["w"] - e["dayW"]) < 0.02 and d["rect"]["h"] == e["dayH"] and d["padding"] == "4px 0px 8px" and d["gap"] == "8px" and d["radius"] == "999px"
                            and d["wd"]["size"] == "12px" and d["wd"]["lh"] == "16px"
                            and d["wd"]["color"] == (INK if is_today else INK_SOFT) and d["wd"]["weight"] == ("700" if is_today else "400")
                            and d["dm"]["size"] == "16px" and d["dm"]["lh"] == "20px" and d["dm"]["weight"] == ("700" if is_today else "500")
                            and d["dm"]["color"] == (INK if is_today else INK) and "tabular-nums" in d["dm"]["tabular"] and d["bgColor"] == TRANSPARENT)
                    ok &= cond
                    if not cond:
                        det.append(f"row{i + 1} {d['date']}: {d['rect']} {d['padding']} {d['wd']} {d['dm']}")
            d0 = m["rows"][0]["days"][0]
            d6 = m["rows"][0]["days"][6]
            R("S1-20", ok and not det, f"all 21 cells {d0['rect']['w']} x {d0['rect']['h']}, padding {d0['padding']}, gap {d0['gap']}, radius {d0['radius']}; weekday {d0['wd']['size']}/{d0['wd']['lh']} {d0['wd']['color']}; number {d0['dm']['size']}/{d0['dm']['lh']} w{d0['dm']['weight']} {d0['dm']['tabular']}; today wd/num {d6['wd']['color']} w{d6['wd']['weight']} / {d6['dm']['color']} w{d6['dm']['weight']}" + ("; FAIL " + "; ".join(det[:2]) if det else ""),
              f"{e['dayW']} x {e['dayH']}, padding 4px 0 8px, gap 8, pill, weekday 12/16 ink-soft, number 16/20 500 tabular, today's weekday and number ink 700")

            # S1-21
            ok = True
            det = []
            for i, row in enumerate(m["rows"]):
                for d in row["days"]:
                    pressed = d["pressed"] == "true"
                    is_today = d["current"] == "date"
                    sh = layers(d["beadShadow"])
                    want_border = f"2px solid {BEAD if pressed else RING}"
                    cond = (d["bead"]["w"] == e["bead"] and d["bead"]["h"] == e["bead"] and d["beadBorder"] == want_border and d["beadBg"] == (BEAD if pressed else BG)
                            and d["beadRadius"] == "50%" and d["check"]["opacity"] == ("1" if pressed else "0") and (d["check"]["fill"] == ON_BEAD)
                            and abs(d["check"]["rect"]["w"] / (1 if pressed else 0.6) - 0.56 * (e["bead"] - 4)) < 0.03 and d["check"]["href"] == "#i-check")
                    if pressed:
                        cond &= d["check"]["transform"] == "none"
                    if is_today:
                        cond &= sorted((s[0], s[4]) for s in sh) == sorted([(BG, 3.0), (RING, 4.5)]) and all(s[1] == 0 and s[2] == 0 and s[3] == 0 and not s[5] for s in sh)
                    else:
                        cond &= d["beadShadow"] == "none"
                    ok &= cond
                    if not cond:
                        det.append(f"row{i + 1} {d['date']}: {d['bead']} {d['beadBorder']} {d['beadBg']} {d['check']} {d['beadShadow']}")
            nd = m["rows"][0]["days"][0]
            dn = m["rows"][0]["days"][1]
            td = m["rows"][0]["days"][6]
            R("S1-21", ok and not det,
              f"{nd['bead']['w']}px beads; not done: {nd['beadBorder']}, fill {nd['beadBg']}, check opacity {nd['check']['opacity']}; done: {dn['beadBorder']}, fill {dn['beadBg']}, check {dn['check']['fill']} opacity {dn['check']['opacity']} {dn['check']['rect']['w']}px; today shadow {td['beadShadow']}" + ("; FAIL " + "; ".join(det[:2]) if det else ""),
              f"{e['bead']}px; not done 2px {RING} stroke, {BG} fill, no check; done {BEAD} fill and stroke, check {ON_BEAD} at 56%; today 0 0 0 3px {BG}, 0 0 0 4.5px {RING}")

            # S1-22 (thin thread): all thin halves, 2px, thread colour, centred
            thin_ok = True
            thin_n = 0
            for row in m["rows"]:
                for d in row["days"]:
                    for nm in ("before", "after"):
                        k = kind(d[nm], d["slot"]["w"])
                        if k in ("thin", "fade-thin"):
                            thin_n += 1
                            thin_ok &= d[nm]["height"] == "2px" and d[nm]["marginTop"] == "-1px"
            last = [r["days"][6]["after"]["display"] for r in m["rows"]]
            R("S1-22", thin_ok and thin_n > 0 and last == ["none", "none", "none"],
              f"{thin_n} thin halves, all height 2px, margin-top -1px, colour {THREAD}, top 50%; last cell right half display {last}",
              "2px --thread through the bead centres, each cell draws its own halves, the last cell has no right half")

            # S1-23 .. S1-27
            fm = m["form"]
            lb = fm["label"]
            R("S1-23", fm["novalidate"] and abs(fm["rect"]["y"] - e["formTop"]) < 0.01 and abs(fm["rect"]["y"] - m["list"]["rect"]["b"] - 40) < 0.01,
              f"form[novalidate] top {fm['rect']['y']}, {round(fm['rect']['y'] - m['list']['rect']['b'], 2)} below the list", f"top {e['formTop']}, 40 below the list")
            R("S1-24", lb["tag"] == "LABEL" and lb["htmlFor"] == "new-habit" and lb["text"] == "New habit" and lb["size"] == "16px" and lb["lh"] == "24px" and lb["weight"] == "600"
              and lb["color"] == INK and lb["display"] == "block" and abs(fm["input"]["rect"]["y"] - lb["rect"]["b"] - 8) < 0.01,
              f"label[for={lb['htmlFor']}] '{lb['text']}' {lb['size']}/{lb['lh']} w{lb['weight']} {lb['color']}, {round(fm['input']['rect']['y'] - lb['rect']['b'], 2)} above the input",
              "label[for=new-habit] 'New habit' 16/24 600 ink, 8 above the input")
            ip = fm["input"]
            ia = ip["attrs"]
            R("S1-25", ip["rect"]["h"] == 48 and abs(ip["rect"]["w"] - e["inputW"]) < 0.05 and ip["radius"] == "999px" and ip["border"] == f"2px solid {RING}" and ip["bg"] == "rgb(253, 254, 254)"
              and ip["padding"] == "0px 20px" and "placeholder" not in ia and "maxlength" not in ia and ia.get("autocomplete") == "off" and ia.get("aria-describedby") == "new-habit-msg"
              and ia.get("id") == "new-habit" and ia.get("type") == "text" and not ip["disabled"] and ip["value"] == "",
              f"#new-habit {ip['rect']['w']}x{ip['rect']['h']} radius {ip['radius']} border {ip['border']} bg {ip['bg']} padding {ip['padding']}; attrs {sorted(ia)}",
              f"{e['inputW']}x48 pill, 2px {RING} border, rgb(253, 254, 254) fill, 0 20 padding, no placeholder, no maxlength, autocomplete=off, aria-describedby=new-habit-msg")
            ab = fm["btn"]
            R("S1-26", ab["text"] == "Add" and ab["rect"]["h"] == 48 and abs(ab["rect"]["w"] - 82) < 0.05 and ab["bg"] == BEAD and ab["color"] == ON_BEAD and ab["size"] == "16px" and ab["weight"] == "600"
              and abs(ab["rect"]["x"] - ip["rect"]["r"] - 12) < 0.01 and ab["type"] == "submit" and ab["radius"] == "999px",
              f"'{ab['text']}' {ab['rect']['w']}x{ab['rect']['h']} {ab['bg']} {ab['color']} {ab['size']} w{ab['weight']}, {round(ab['rect']['x'] - ip['rect']['r'], 2)} right of the input",
              f"'Add' 82x48 pill, {BEAD} fill, {ON_BEAD} 16px 600 text, 12 right of the input")
            ms = fm["msg"]
            R("S1-27", ms["tag"] == "P" and ms["id"] == "new-habit-msg" and ms["cls"] == "field-msg field-error" and ms["live"] == "polite" and ms["text"] == "" and ms["display"] == "none",
              f"{ms['tag']}#{ms['id']}.{ms['cls'].replace(' ', '.')}[aria-live={ms['live']}] text '{ms['text']}' display {ms['display']}", "p#new-habit-msg.field-msg.field-error[aria-live=polite], empty, display none")

            # S1-28
            ht = m["heat"]
            if vk == "390":
                ok = abs(ht["rect"]["y"] - e["heatTop"]) < 0.01 and ht["rect"]["w"] == 350 and ht["padding"] == "20px 16px" and abs(ht["rect"]["y"] - fm["rect"]["b"] - 40) < 0.01
                meas = f"top {ht['rect']['y']}, {round(ht['rect']['y'] - fm['rect']['b'], 2)} below the form, w {ht['rect']['w']}, padding {ht['padding']}"
                want = "top 793, 40 below the form, 350 wide, padding 20px 16px"
            else:
                ok = abs(ht["rect"]["y"] - 101) < 0.01 and ht["rect"]["w"] == 380 and ht["padding"] == "24px" and ht["position"] == "sticky" and ht["top"] == "32px" and ht["marginTop"] == "0px"
                meas = f"top {ht['rect']['y']} (first habit top {m['rows'][0]['li']['y']}), w {ht['rect']['w']}, padding {ht['padding']}, {ht['position']} top {ht['top']}"
                want = "top 101 level with the first habit, 380 wide, padding 24px, sticky 32px from the top"
                ok &= ht["rect"]["y"] == m["rows"][0]["li"]["y"]
            ok &= ht["bg"] == SURFACE and ht["radius"] == "20px" and ht["tag"] == "SECTION" and ht["labelledby"] == "heat-title"
            R("S1-28", ok, f"{meas}, bg {ht['bg']}, radius {ht['radius']}", f"{want}, bg {SURFACE}, radius 20px")

            # S1-29
            tt = ht["title"]
            R("S1-29", tt["tag"] == "H2" and tt["id"] == "heat-title" and tt["text"] == "Last 12 weeks" and tt["size"] == "16px" and tt["lh"] == "24px" and tt["weight"] == "600"
              and abs(ht["grid"]["y"] - tt["rect"]["b"] - 12) < 0.01,
              f"{tt['tag']}#{tt['id']} '{tt['text']}' {tt['size']}/{tt['lh']} w{tt['weight']}, {round(ht['grid']['y'] - tt['rect']['b'], 2)} above the grid", "h2.heat-title 'Last 12 weeks' 16/24 600, 12 above the grid")

            # S1-30
            cw = ht["cellsRect"]["w"] / 12
            mo = ht["months"]
            ok = mo["ariaHidden"] == "true" and [(s["text"], s["col"]) for s in mo["spans"]] == [("Jul", "1"), ("Aug", "3"), ("Sep", "8"), ("Oct", "12")]
            for s in mo["spans"]:
                ok &= s["size"] == "12px" and s["lh"] == "16px" and s["color"] == INK_SOFT and abs(s["rect"]["x"] - (ht["cellsRect"]["x"] + (int(s["col"]) - 1) * cw)) < 0.02
            R("S1-30", ok, f"aria-hidden={mo['ariaHidden']}; " + ", ".join(f"{s['text']} col {s['col']} x {s['rect']['x']}" for s in mo["spans"]) + f"; {mo['spans'][0]['size']}/{mo['spans'][0]['lh']} {mo['spans'][0]['color']}",
              "Jul over column 1, Aug 3, Sep 8, Oct 12; 12/16 ink-soft; aria-hidden; each label starts on its column")

            # S1-31
            wdx = ht["wdays"]
            ch = ht["cellsRect"]["h"] / 7
            ok = wdx["ariaHidden"] == "true" and [s["text"] for s in wdx["spans"]] == ["Mon", "", "Wed", "", "Fri", "", "Sun"] and abs(ht["cellsRect"]["x"] - wdx["rect"]["r"] - 8) < 0.01
            for i, s in enumerate(wdx["spans"]):
                row_centre = ht["cellsRect"]["y"] + (i + 0.5) * ch
                span_centre = s["rect"]["y"] + s["rect"]["h"] / 2
                ok &= s["size"] == "12px" and s["color"] == INK_SOFT and abs(span_centre - row_centre) < 0.6
            R("S1-31", ok, f"labels {[s['text'] for s in wdx['spans']]}, {round(ht['cellsRect']['x'] - wdx['rect']['r'], 2)} from the cells, {wdx['spans'][0]['size']} {wdx['spans'][0]['color']}, each centred on its row (max offset {max(abs(s['rect']['y'] + s['rect']['h'] / 2 - (ht['cellsRect']['y'] + (i + 0.5) * ch)) for i, s in enumerate(wdx['spans'])):.2f})",
              "Mon, blank, Wed, blank, Fri, blank, Sun against rows 1 to 7; 12px ink-soft; 8 from the cells; aria-hidden")

            # S1-32
            cells = ht["cells"]
            start = Date(2026, 7, 20)
            ok = len(cells) == 84
            bad = []
            per_ok = True
            for i, c in enumerate(cells):
                d = Date.fromordinal(start.toordinal() + i)
                key = d.isoformat()
                col, rw = divmod(i, 7)
                exp_x = ht["cellsRect"]["x"] + col * cw
                exp_y = ht["cellsRect"]["y"] + rw * (cw)
                geo = abs(c["rect"]["x"] - exp_x) < 0.15 and abs(c["rect"]["y"] - exp_y) < 0.2 and abs(c["rect"]["w"] - cw) < 0.05 and abs(c["rect"]["h"] - cw) < 0.05
                if key <= "2026-10-08":
                    cnt = sum(1 for h_ in HABITS if key in h_["done"])
                    lvl = LEVELS[key]
                    label = f"{WD[d.weekday()]} {d.day} {MON[d.month - 1]}, {cnt} of 3 habits"
                    cond = c["date"] == key and f"hc l{lvl}" in c["cls"] and c["role"] == "img" and c["label"] == label and c["ariaHidden"] is None
                else:
                    cond = c["date"] == key and c["cls"] == "hc future" and c["role"] is None and c["label"] is None and c["ariaHidden"] == "true"
                if not (cond and geo):
                    bad.append((key, c["cls"], c["label"], c["rect"]))
            R("S1-32", ok and not bad, f"84 cells, {sum(1 for c in cells if 'future' not in c['cls'])} with levels equal to sample-history heatmapLevels and names from '{cells[0]['label']}' to '{cells[80]['label']}', square {cells[0]['rect']['w']}, column-major; mismatches {bad[:2]}",
              f"84 squares column-major, {e['cell']} wide, the 81 levels of heatmapLevels, names 'Mon 20 Jul, 3 of 3 habits' to 'Thu 8 Oct, 2 of 3 habits', role img")
            R("S1-32b", abs(cells[0]["rect"]["w"] - e["cell"]) <= 0.06, f"cell width {cells[0]['rect']['w']}", f"{e['cell']} (qa.md rounds to one decimal)")

            # S1-33
            lg = ht["legend"]
            kids = {k["cls"]: k for k in lg["kids"] if k["cls"].startswith("hc")}
            want = {"hc l0": ("6px", TRANSPARENT, True), "hc l1": ("7px", "rgb(120, 150, 139)", False), "hc l2": ("11px", "rgb(79, 124, 112)", False),
                    "hc l3": ("14px", BEAD, False), "hc l4": ("17px", BEAD_DEEP, False)}
            ok = True
            det = []
            for cls, (px, col, hollow) in want.items():
                k = kids[cls]
                cond = k["bw"] == px and k["bh"] == px and k["bbg"] == col and k["bradius"] in ("50%", "50% 50% 50% 50%")
                if hollow:
                    lay = layers(k["bshadow"])
                    cond &= len(lay) == 1 and lay[0][0] == RING and lay[0][4] == 1.5 and lay[0][5]
                else:
                    cond &= k["bshadow"] == "none"
                ok &= cond
                det.append(f"{cls.split()[1]} {k['bw']} {k['bbg']}" + (f" ring {k['bshadow']}" if hollow else ""))
            # grid cells of each level used must also match (l0, l1, l2, l4)
            for cls, px in (("l0", "6px"), ("l1", "7px"), ("l2", "11px"), ("l4", "17px")):
                c = next(x for x in cells if f"hc {cls}" in x["cls"])
                ok &= c["bw"] == px and c["bh"] == px
            R("S1-33", ok, "; ".join(det), "l0 6px hollow ring 1.5px --ring; l1 7px rgb(120, 150, 139); l2 11px rgb(79, 124, 112); l3 14px --bead; l4 17px --bead-deep; all round")

            # S1-34
            tc = next(c for c in cells if c["date"] == "2026-10-08")
            R("S1-34", tc["cls"] == "hc l2 today" and tc["current"] == "date" and tc["aw"] == "22px" and tc["ah"] == "22px" and tc["aborder"] in (f"1.5px solid {RING}", f"1px solid {RING}") and tc["bw"] == "11px" and m.get("tokens", {}).get("todayRing") == "1.5px"
              and tc["aradius"] in ("50%", "50% 50% 50% 50%") and tc["label"] == "Thu 8 Oct, 2 of 3 habits",
              f"class '{tc['cls']}', aria-current={tc['current']}, ring {tc['aw']} x {tc['ah']} border {tc['aborder']} (token --today-ring {m.get('tokens', {}).get('todayRing')}; Chrome draws a 1.5px border as 1px at 1x), dot {tc['bw']}",
              f"l2 dot (11px) inside a 22px ring, 1.5px {RING}; class today; aria-current=date")

            # S1-35
            fut = [c for c in cells if c["date"] in ("2026-10-09", "2026-10-10", "2026-10-11")]
            ok = len(fut) == 3
            for c in fut:
                ok &= c["cls"] == "hc future" and c["ariaHidden"] == "true" and c["role"] is None and c["label"] is None and c["bbg"] == TRANSPARENT and c["bshadow"] == "none" and c["aborder"].startswith("0px")
            R("S1-35", ok, "; ".join(f"{c['date']} class '{c['cls']}' aria-hidden={c['ariaHidden']} role={c['role']} dot bg {c['bbg']} shadow {c['bshadow']} ring border {c['aborder']}" for c in fut),
              "Fri 9, Sat 10, Sun 11 Oct: nothing drawn, aria-hidden, no role")

            # S1-36
            kids_l = lg["kids"]
            hcs = [k for k in kids_l if k["cls"].startswith("hc")]
            R("S1-36", lg["ariaHidden"] == "true" and lg["justify"] == "flex-end" and abs(lg["rect"]["y"] - ht["grid"]["b"] - 12) < 0.01 and [k["text"] for k in kids_l if not k["cls"]] == ["None", "All"]
              and len(hcs) == 5 and all(k["rect"]["w"] == 20 and k["rect"]["h"] == 20 for k in hcs) and lg["size"] == "12px" and lg["lh"] == "16px" and lg["color"] == INK_SOFT and lg["gap"] == "4px"
              and abs(lg["rect"]["r"] - (ht["rect"]["r"] - (16 if vk == "390" else 24))) < 0.01 and kids_l[0]["text"] == "None" and kids_l[-1]["text"] == "All",
              f"aria-hidden={lg['ariaHidden']} {lg['justify']}, {round(lg['rect']['y'] - ht['grid']['b'], 2)} below the grid, labels {[k['text'] for k in kids_l if not k['cls']]}, {len(hcs)} dots in {hcs[0]['rect']['w']}x{hcs[0]['rect']['h']} cells, {lg['size']}/{lg['lh']} {lg['color']}, gap {lg['gap']}",
              "right aligned, 12 below the grid, None + five dots in 20px cells + All, 12/16 ink-soft, aria-hidden")

            # S1-37
            ctrl = m["controls"]
            kinds = sorted(set((c["tag"], c["cls"]) for c in ctrl))
            vis_ctrl = [c for c in ctrl if c["visible"]]
            allowed = {("button", "icon-btn"): 3, ("button", "day"): 21, ("input", "input"): 1, ("button", "btn btn-primary"): 1}
            counts = {}
            for c in vis_ctrl:
                counts[(c["tag"], c["cls"])] = counts.get((c["tag"], c["cls"]), 0) + 1
            gtext = g["innerText"].strip()
            mtext = m["innerText"].strip()
            R("S1-37", counts == allowed and m["nodes"]["note"] is False and m["nodes"]["dialog"] == {"open": False, "display": "none"} and m["nodes"]["img"] == 0 and mtext == gtext and m["visibleSvgs"] == g["visibleSvgs"] == 24,
              f"visible controls {dict((f'{a}.{b}', n) for (a, b), n in counts.items())}; note shown: {m['nodes']['note']}; dialog {m['nodes']['dialog']}; images/canvas/iframe: {m['nodes']['img']}; visible text equals the golden's ({mtext == gtext}); visible svgs {m['visibleSvgs']} (3 trash + 21 check glyphs, golden {g['visibleSvgs']})",
              "3 trash + 21 day buttons + input + Add, no note, dialog closed and not displayed, no other control or text")
        browser.close()
    rows.save("rows_s1.json")
    passed, failed = rows.summary()
    print("rows", len(rows.rows), "pass", passed, "fail", failed)
    for r in rows.rows:
        if r["result"] == "FAIL":
            print(json.dumps(r, indent=1, ensure_ascii=False)[:1800])


run()
