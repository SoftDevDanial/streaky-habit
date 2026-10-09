"""FE element checklist, S2 rows (qa.md), measured on the running app at 390x844 and 1280x800 (scratch).
The app is opened with empty storage (no seed). Writes rows_s2.json and measure_s2_<vp>_{golden,candidate}.json.
"""
import json
from datetime import date as Date

from common import *  # noqa: F401,F403
from measure import MEASURE_JS
from playwright.sync_api import sync_playwright

BEAD_DEEP = "rgb(46, 90, 80)"
INK = "rgb(28, 37, 35)"
INK_SOFT = "rgb(82, 96, 91)"
RING = "rgb(126, 142, 136)"
BG = "rgb(242, 245, 243)"
BEAD = "rgb(59, 107, 96)"
ON_BEAD = "rgb(247, 250, 249)"
SURFACE = "rgb(250, 252, 251)"
TRANSPARENT = "rgba(0, 0, 0, 0)"
WD = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

EXP = {
    "390": dict(pageX=0, pageW=390, pagePad="24px 20px 48px", maxW="600px", hdrPB="24px", emptyTop=77, formTop=173, heatTop=293, heatBottom=588, heatW=350,
                heatPad="20px 16px", inputW=256, contentL=20, contentR=370),
    "1280": dict(pageX=120, pageW=1040, pagePad="40px 48px 48px", maxW="1040px", hdrPB="32px", emptyTop=101, formTop=197, heatTop=101, heatBottom=None, heatW=380,
                 heatPad="24px", inputW=406, contentL=168, contentR=1112),
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


def run():
    rows = Rows()
    with sync_playwright() as pw:
        browser = launch(pw)
        for vk, vp in VIEWPORTS.items():
            e = EXP[vk]
            gctx, gpage = open_page(browser, golden_url("S2"), vp)
            cctx, cpage = open_page(browser, BASE, vp, seed=False)
            g = gpage.evaluate(MEASURE_JS)
            m = cpage.evaluate(MEASURE_JS)
            stored = cpage.evaluate("() => localStorage.getItem('streaks.state')")
            save_json(f"measure_s2_{vk}_golden.json", g)
            save_json(f"measure_s2_{vk}_candidate.json", m)
            gctx.close()
            cctx.close()

            def R(row, cond, measured, expected, note=""):
                rows.chk(f"{row}@{vk}", cond, measured, expected, note)

            gg, mm = json.loads(json.dumps(g)), json.loads(json.dumps(m))
            for d in (gg, mm):
                d.pop("controls", None)
                d["nodes"].pop("dialog", None)
                d.pop("sprite", None)
                d.pop("visibleSvgs", None)
            diffs = list(deep_diff(gg, mm))
            R("S2-GOLDEN-EQ", not diffs, f"{len(diffs)} differences", "0 differences between the golden's and the app's measurement (the sprite and the closed dialog aside)", note=json.dumps(diffs[:5]))

            # S2-01: the shared frame (S1-01, 03 to 08, 24 to 31, 36), re-measured on S2
            b = m["body"]
            p = m["page"]
            h = m["header"]
            br, dt = m["brand"], m["date"]
            L = m["layout"]
            hh = m["hiddenHeading"]
            fm = m["form"]
            lb, ip, ab, ms = fm["label"], fm["input"], fm["btn"], fm["msg"]
            ht = m["heat"]
            tt = ht["title"]
            lg = ht["legend"]
            cw = ht["cellsRect"]["w"] / 12
            ch = ht["cellsRect"]["h"] / 7
            shared = {
                "S1-01 page": b["bg"] == BG and b["color"] == INK and b["size"] == "16px" and b["lh"] == "24px",
                "S1-03 frame": p["rect"]["x"] == e["pageX"] and p["rect"]["w"] == e["pageW"] and p["padding"] == e["pagePad"] and p["maxWidth"] == e["maxW"],
                "S1-04 header": h["display"] == "flex" and h["alignItems"] == "baseline" and h["justify"] == "space-between" and h["gap"] == "12px" and h["paddingBottom"] == e["hdrPB"],
                "S1-05 brand": br["tag"] == "H1" and br["text"] == "Streaks" and br["font"]["size"] == "22px" and br["font"]["lh"] == "28px" and br["font"]["weight"] == "700"
                and br["font"]["ls"] == "-0.22px" and br["font"]["color"] == BEAD_DEEP and br["rect"]["x"] == e["contentL"],
                "S1-06 date": dt["datetime"] == "2026-10-08" and dt["timeText"] == "Thursday 8 October" and dt["font"]["size"] == "16px" and dt["font"]["color"] == INK_SOFT
                and dt["font"]["align"] == "right" and abs(dt["rect"]["r"] - e["contentR"]) < 0.01,
                "S1-07 layout": (L["display"] == "grid" and L["cols"] == "500px 380px" and L["colGap"] == "64px" and L["colMain"]["x"] == 168 and L["heat"]["x"] == 732) if vk == "1280"
                else (L["display"] == "block" and L["colMain"]["w"] == 350),
                "S1-08 hidden heading": hh["text"] == "Habits" and hh["cls"] == "sr-only" and hh["rect"]["w"] == 1 and hh["rect"]["h"] == 1 and hh["sectionLabelledby"] == "habits-title",
                "S1-24 label": lb["text"] == "New habit" and lb["size"] == "16px" and lb["lh"] == "24px" and lb["weight"] == "600" and lb["color"] == INK and abs(ip["rect"]["y"] - lb["rect"]["b"] - 8) < 0.01,
                "S1-25 input": ip["rect"]["h"] == 48 and abs(ip["rect"]["w"] - e["inputW"]) < 0.05 and ip["radius"] == "999px" and ip["border"] == f"2px solid {RING}" and ip["bg"] == "rgb(253, 254, 254)"
                and "placeholder" not in ip["attrs"] and "maxlength" not in ip["attrs"] and ip["attrs"].get("autocomplete") == "off" and ip["attrs"].get("aria-describedby") == "new-habit-msg",
                "S1-26 add button": ab["text"] == "Add" and ab["rect"]["h"] == 48 and abs(ab["rect"]["w"] - 82) < 0.05 and ab["bg"] == BEAD and ab["color"] == ON_BEAD and abs(ab["rect"]["x"] - ip["rect"]["r"] - 12) < 0.01,
                "S1-27 message": ms["id"] == "new-habit-msg" and ms["cls"] == "field-msg field-error" and ms["live"] == "polite" and ms["text"] == "" and ms["display"] == "none",
                "S1-28 panel (all but the top)": ht["rect"]["w"] == e["heatW"] and ht["padding"] == e["heatPad"] and ht["bg"] == SURFACE and ht["radius"] == "20px"
                and (abs(ht["rect"]["y"] - fm["rect"]["b"] - 40) < 0.01 if vk == "390" else (ht["position"] == "sticky" and ht["top"] == "32px")),
                "S1-29 heat title": tt["text"] == "Last 12 weeks" and tt["size"] == "16px" and tt["lh"] == "24px" and tt["weight"] == "600" and abs(ht["grid"]["y"] - tt["rect"]["b"] - 12) < 0.01,
                "S1-30 month axis": [(s["text"], s["col"]) for s in ht["months"]["spans"]] == [("Jul", "1"), ("Aug", "3"), ("Sep", "8"), ("Oct", "12")] and ht["months"]["ariaHidden"] == "true"
                and all(s["size"] == "12px" and s["color"] == INK_SOFT for s in ht["months"]["spans"]),
                "S1-31 weekday axis": [s["text"] for s in ht["wdays"]["spans"]] == ["Mon", "", "Wed", "", "Fri", "", "Sun"] and abs(ht["cellsRect"]["x"] - ht["wdays"]["rect"]["r"] - 8) < 0.01
                and all(abs(s["rect"]["y"] + s["rect"]["h"] / 2 - (ht["cellsRect"]["y"] + (i + 0.5) * ch)) < 0.6 for i, s in enumerate(ht["wdays"]["spans"])),
                "S1-36 legend": lg["ariaHidden"] == "true" and lg["justify"] == "flex-end" and abs(lg["rect"]["y"] - ht["grid"]["b"] - 12) < 0.01
                and [k["text"] for k in lg["kids"] if not k["cls"]] == ["None", "All"] and sum(1 for k in lg["kids"] if k["cls"].startswith("hc")) == 5,
            }
            bad = [k for k, v in shared.items() if not v]
            R("S2-01", not bad, f"{len(shared)} shared rows re-measured on S2, failing: {bad or 'none'}; S1-28's top is {ht['rect']['y']} here (S2-04), not 793",
              "S1-01, 03 to 08, 24 to 31, 36 hold unchanged on S2 (S1-28's top excepted)")

            # S2-02
            em = m["empty"]
            st = em["strong"]
            ok = (em is not None and m["list"] is None and em["innerHTML"] == "<strong>No habits yet.</strong> Add one you want to do every day."
                  and st["text"] == "No habits yet." and st["display"] == "block" and st["size"] == "18px" and st["lh"] == "28px" and st["weight"] == "600" and st["color"] == INK and st["mb"] == "4px"
                  and em["size"] == "16px" and em["lh"] == "24px" and em["color"] == INK_SOFT and em["rect"]["y"] == e["emptyTop"] and em["rect"]["h"] == 56 and em["rect"]["x"] == e["contentL"])
            R("S2-02", ok, f"p.empty top {em['rect']['y']} x {em['rect']['x']} h {em['rect']['h']}; strong '{st['text']}' {st['display']} {st['size']}/{st['lh']} w{st['weight']} {st['color']} mb {st['mb']}; text {em['size']}/{em['lh']} {em['color']}; ul.habits present: {m['list'] is not None}",
              f"top {e['emptyTop']}, 56 tall, strong block 18/28 600 ink, then 16/24 ink-soft 4 below, no ul.habits")

            # S2-03
            R("S2-03", abs(fm["rect"]["y"] - e["formTop"]) < 0.01 and abs(fm["rect"]["y"] - em["rect"]["b"] - 40) < 0.01 and not ip["disabled"] and not ab["disabled"] and ip["value"] == "" and ms["text"] == "" and ms["display"] == "none",
              f"form top {fm['rect']['y']}, {round(fm['rect']['y'] - em['rect']['b'], 2)} below the message; input disabled {ip['disabled']}, Add disabled {ab['disabled']}, value '{ip['value']}', message '{ms['text']}' ({ms['display']})",
              f"top {e['formTop']}, 40 below the message, enabled, empty, no message")

            # S2-04
            if vk == "390":
                ok = abs(ht["rect"]["y"] - 293) < 0.01 and abs(ht["rect"]["b"] - 588) < 0.6 and m["scroll"][1] == 844 and m["scroll"][0] == 390
                meas = f"panel top {ht['rect']['y']}, bottom {ht['rect']['b']}, page scroll size {m['scroll'][0]}x{m['scroll'][1]}"
                want = "top 293, ends at 588, whole first screen fits 390x844 (no scroll)"
            else:
                filler = L["colMain"]["h"] - (em["rect"]["h"] + 40 + fm["rect"]["h"])
                ok = abs(ht["rect"]["y"] - 101) < 0.01 and ht["rect"]["x"] == 732 and abs(filler) < 0.01 and L["colMain"]["y"] == ht["rect"]["y"]
                meas = f"panel top {ht['rect']['y']} at x {ht['rect']['x']}; left column {L['colMain']['h']} tall = message 56 + 40 + form {fm['rect']['h']} (filler {round(filler, 2)})"
                want = "top 101 in the right column, no filler added to the short left column"
            R("S2-04", ok, meas, want)

            # S2-05
            cells = ht["cells"]
            start = Date(2026, 7, 20)
            bad = []
            for i, c in enumerate(cells):
                d = Date.fromordinal(start.toordinal() + i)
                key = d.isoformat()
                if key <= "2026-10-08":
                    label = f"{WD[d.weekday()]} {d.day} {MON[d.month - 1]}, 0 of 0 habits"
                    today = key == "2026-10-08"
                    want_cls = "hc l0 today" if today else "hc l0"
                    hollow = c["bw"] == "6px" and c["bbg"] == TRANSPARENT and "inset" in c["bshadow"] and RING in c["bshadow"]
                    cond = c["date"] == key and c["cls"] == want_cls and c["role"] == "img" and c["label"] == label and hollow and ((c["aw"] == "22px" and c["current"] == "date") if today else c["current"] is None)
                else:
                    cond = c["cls"] == "hc future" and c["ariaHidden"] == "true" and c["role"] is None and c["label"] is None and c["bbg"] == TRANSPARENT
                if not cond:
                    bad.append((key, c["cls"], c["label"]))
            R("S2-05", len(cells) == 84 and not bad,
              f"{sum(1 for c in cells if 'future' not in c['cls'])} hollow l0 rings (6px, ring {RING}), names '{cells[0]['label']}' to '{cells[80]['label']}'; Thu 8 Oct class '{cells[80]['cls']}' ring {cells[80]['aw']}; Fri 9 to Sun 11: {[c['cls'] for c in cells[81:]]}; failing {bad[:2]}",
              "81 hollow l0 rings named '<Ddd D Mon>, 0 of 0 habits', Thu 8 Oct l0 with the today ring, Fri 9 to Sun 11 blank")

            # S2-06
            sp = m["sprite"]
            R("S2-06", m["visibleSvgs"] == 0 and sp is not None and sp["rect"]["w"] == 0 and sp["rect"]["h"] == 0,
              f"visible svgs {m['visibleSvgs']}; sprite present {sp is not None} at {sp['rect']['w']}x{sp['rect']['h']}", "no icon visible (sprite present with zero size)")
            R("S2-R3", stored is None, f"localStorage 'streaks.state' after load = {stored!r}", "nothing written to storage until the first change (spec R3)")
        browser.close()
    rows.save("rows_s2.json")
    passed, failed = rows.summary()
    print("rows", len(rows.rows), "pass", passed, "fail", failed)
    for r in rows.rows:
        if r["result"] == "FAIL":
            print(json.dumps(r, indent=1, ensure_ascii=False)[:1800])
        else:
            print(r["id"], "PASS |", str(r["measured"])[:260])


run()
