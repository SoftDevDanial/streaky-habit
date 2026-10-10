"""Data and markup fragments for the v1.1.0 goldens, read from round-2/f2.html.

Prints only, writes nothing. Run with: python -B "<this file>".
The histories come from f2 itself (window.__streaky.histories() in K1 and in S3), so every figure is f2's.
The fragments follow f2's own ring(), dayCell(), monthsHTML(), rowHTML() and legendHTML() line by line,
with the static changes the compose brief asks for (no script, no data-act/data-fk, no pop classes).
PART picks what to print, CHUNK picks which slice of a long fragment (the Bash output is capped).
"""
import datetime as dt
import json
import math
import pathlib
from playwright.sync_api import sync_playwright

PART = ["p4-codes", "s3-band-codes", "ovring12", "rows12", "bits"]
CHUNK = 0
CHUNK_CHARS = 29500

HERE = pathlib.Path(__file__).resolve().parent
F2 = HERE.parent.parent / "round-2" / "f2.html"
T = 5000

TODAY = dt.date(2026, 10, 10)
GRID_START = dt.date(2026, 7, 20)
YEAR_START = dt.date(2025, 10, 10)
WD = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
WDL = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
WD1 = ["M", "T", "W", "T", "F", "S", "S"]
MS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
ML = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
DAY = dt.timedelta(days=1)


def get_histories():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            ctx = browser.new_context(viewport={"width": 1280, "height": 800})
            page = ctx.new_page()
            page.set_default_timeout(T)
            page.goto(F2.as_uri(), timeout=T)
            page.wait_for_selector("#list .row", timeout=T)
            k1 = page.evaluate("() => window.__streaky.histories()")
            page.click("#proto-tab", timeout=T)
            page.click('[data-state="s3"]', timeout=T)
            page.wait_for_timeout(300)
            s3 = page.evaluate("() => window.__streaky.histories()")
            return k1, s3, browser.version
        finally:
            browser.close()


def streaks(keys):
    days = sorted(dt.date.fromisoformat(k) for k in keys)
    s = set(days)
    d = TODAY if TODAY in s else TODAY - DAY
    cur = 0
    while d in s:
        cur += 1
        d -= DAY
    best = run = 0
    prev = None
    for x in days:
        run = run + 1 if prev and (x - prev).days == 1 else 1
        best = max(best, run)
        prev = x
    return cur, best


def short(d):
    return f"{WD[d.weekday()]} {d.day} {MS[d.month - 1]}"


def yeard(d):
    return f"{short(d)} {d.year}"


def jn(x):
    """JavaScript's String(Math.round(x * 100) / 100)."""
    r = math.floor(x * 100 + 0.5) / 100
    if r == 0:
        r = 0.0
    s = repr(r)
    return s[:-2] if s.endswith(".0") else s


def arc(n, i):
    step = 360 / n
    gap = min(22, step * 0.3)
    a1 = (i * step + gap / 2) * math.pi / 180
    a2 = ((i + 1) * step - gap / 2) * math.pi / 180
    x1, y1 = 20 + 15 * math.sin(a1), 20 - 15 * math.cos(a1)
    x2, y2 = 20 + 15 * math.sin(a2), 20 - 15 * math.cos(a2)
    return f"M{jn(x1)} {jn(y1)}A15 15 0 {1 if step - gap > 180 else 0} 1 {jn(x2)} {jn(y2)}"


def ring(flags, today=False, num=None):
    n = len(flags)
    full = n > 0 and all(flags)
    s = '<svg viewBox="0 0 40 40" aria-hidden="true">'
    if today:
        s += '<circle class="c-today" cx="20" cy="20" r="19.2"/>'
    if n <= 1:
        s += f'<circle class="seg{" on" if n == 1 and flags[0] else ""}" cx="20" cy="20" r="15"/>'
    else:
        for i, on in enumerate(flags):
            s += f'<use class="seg{" on" if on else ""}" href="#a{n}-{i}"/>'
    if full:
        s += '<circle class="c-core" cx="20" cy="20" r="11.5"/>'
    if num is not None:
        s += f'<text class="c-num{" on" if full else ""}" x="20" y="20" dy=".352em">{num}</text>'
    return s + "</svg>"


def day_cell(d, sets, with_year=False, open_key=None):
    k = d.isoformat()
    if d > TODAY:
        return '<span class="hc" aria-hidden="true"></span>'
    flags = [k in s for s in sets]
    n, total = sum(flags), len(flags)
    label = (yeard(d) if with_year else short(d)) + f", {n} of {total} habits"
    cls = "hc" + (" is-open" if k == open_key else "")
    cur = ' aria-current="date"' if d == TODAY else ""
    return f'<button type="button" class="{cls}" data-key="{k}" aria-haspopup="dialog" aria-label="{label}"{cur}>{ring(flags, d == TODAY, d.day)}</button>'


def band(sets, open_key=None):
    out = ['<div aria-hidden="true"></div>' + "".join(f'<div class="og-wd" aria-hidden="true">{l}</div>' for l in WD1)]
    for w in range(12):
        mon = GRID_START + dt.timedelta(days=w * 7)
        prev = GRID_START + dt.timedelta(days=(w - 1) * 7) if w else None
        lbl = MS[mon.month - 1] if (not prev or prev.month != mon.month) else ""
        out.append(f'<div class="og-mo" aria-hidden="true">{lbl}</div>' + "".join(day_cell(mon + dt.timedelta(days=d), sets, open_key=open_key) for d in range(7)))
    return "\n".join(out)


def popup_grid(sets, open_key=None):
    out = ['<div aria-hidden="true"></div>' + "".join(f'<div class="og-wd" aria-hidden="true">{l}</div>' for l in WD1)]
    for w in range(11, -1, -1):
        mon = GRID_START + dt.timedelta(days=w * 7)
        lbl = MS[mon.month - 1] if (w == 11 or w == 0 or mon.day <= 7) else ""
        out.append(f'<div class="og-mo" aria-hidden="true">{lbl}</div>' + "".join(day_cell(mon + dt.timedelta(days=d), sets, open_key=open_key) for d in range(7)))
    return "\n".join(out)


def legend(n):
    lg = "<span>None</span>"
    if n == 0:
        lg += ring([], False, None)
    else:
        steps = []
        for c in (0, math.ceil(n / 3), math.ceil(2 * n / 3), n):
            if c <= n and c not in steps:
                steps.append(c)
        for c in steps:
            lg += ring([i < c for i in range(n)], False, None)
    return lg + "<span>All</span>"


def months(pfx, cell_cls, day_fn, closed_fn):
    out = []
    m = dt.date(TODAY.year, TODAY.month, 1)
    stop = dt.date(YEAR_START.year, YEAR_START.month, 1)
    while m >= stop:
        y, mo = m.year, m.month
        mid = f"{pfx}mo-{y}-{mo}"
        nxt = dt.date(y + (mo == 12), mo % 12 + 1, 1)
        days = (nxt - m).days
        lead = m.weekday()
        h = f'<section class="month" aria-labelledby="{mid}"><h3 id="{mid}">{ML[mo - 1]} {y}</h3><div class="mgrid" role="group" aria-labelledby="{mid}">'
        h += "".join(f'<span class="mwd" aria-hidden="true">{l}</span>' for l in WD1)
        h += "".join(f'<span class="{cell_cls} lead" aria-hidden="true"></span>' for _ in range(lead))
        cells = []
        for dd in range(1, days + 1):
            d = dt.date(y, mo, dd)
            if d < YEAR_START:
                cells.append(f'<span class="{cell_cls} blank" aria-hidden="true"></span>')
            elif d > TODAY:
                cells.append(closed_fn(dd))
            else:
                cells.append(day_fn(d))
        # one week per line, so a chunk boundary never cuts a cell
        lines = [h]
        week = []
        for i, c in enumerate(cells):
            week.append(c)
            if (lead + i) % 7 == 6:
                lines.append("".join(week))
                week = []
        if week:
            lines.append("".join(week))
        lines.append("</div></section>")
        out.append("\n".join(lines))
        m = dt.date(y - (mo == 1), (mo - 2) % 12 + 1, 1)
    return "\n".join(out)


def p4(sets, open_key=None):
    closed = lambda dd: f'<span class="hc closed" aria-hidden="true"><svg viewBox="0 0 40 40" aria-hidden="true"><text class="c-num dim" x="20" y="20" dy=".352em">{dd}</text></svg></span>'
    return months("a", "hc", lambda d: day_cell(d, sets, True, open_key), closed)


def p2(s):
    def has(x):
        return YEAR_START <= x <= TODAY and x.isoformat() in s

    def cell(d):
        k = d.isoformat()
        on = k in s
        left, right = on and has(d - DAY), on and has(d + DAY)
        cls = "yc" + (" on" if on else "") + (" l" if left else "") + (" r" if right else "") + (" today" if d == TODAY else "")
        cur = ' aria-current="date"' if d == TODAY else ""
        return f'<button type="button" class="{cls}" data-key="{k}" aria-pressed="{"true" if on else "false"}" aria-label="Mark {yeard(d)} as done"{cur}><span class="bead">{d.day}</span></button>'

    return months("", "yc", cell, lambda dd: f'<span class="yc closed" aria-hidden="true"><span class="bead">{dd}</span></span>')


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def stats_html(cur, best):
    if cur > 0:
        c = f'<span class="stat cur"><span class="lbl">Current</span><span class="val"><b class="num">{cur}</b><span class="unit">{"day" if cur == 1 else "days"}</span></span></span>'
    else:
        c = '<span class="stat cur"><span class="lbl">Current</span><span class="none">No streak yet</span></span>'
    b = f'<span class="stat best"><span class="lbl">Best</span><span class="val"><b class="num">{best}</b></span></span>' if best > 0 else ""
    return c + b


def row(h, hid):
    cur, best = streaks(h["done"])
    name = esc(h["name"])
    today = "true" if TODAY.isoformat() in h["done"] else "false"
    return (f'<li class="row"><div class="r-head"><h3 class="r-name" id="rn-{hid}">{name}</h3>'
            f'<button type="button" class="btn-bin" aria-haspopup="dialog" aria-label="Delete &quot;{name}&quot;"><svg class="ph" aria-hidden="true"><use href="#i-trash"/></svg></button></div>'
            f'<p class="stats" id="rs-{hid}">{stats_html(cur, best)}</p>'
            f'<button type="button" class="btn-year" aria-haspopup="dialog" aria-label="Year view, {name}">Year</button>'
            f'<button type="button" class="btn-done" aria-pressed="{today}" aria-label="Done today, {name}" aria-describedby="rs-{hid}"><span class="dot"><svg aria-hidden="true"><use href="#i-check"/></svg></span>Done today</button></li>')


def tick(h, hid, key):
    cur, best = streaks(h["done"])
    on = key in h["done"]
    name = esc(h["name"])
    ct = f'<span class="tcur">Current {cur} {"day" if cur == 1 else "days"}</span>' if cur > 0 else '<span class="tcur none">No streak yet</span>'
    bt = f"<span>Best {best}</span>" if best > 0 else ""
    return (f'<li><button type="button" class="tick{" on" if on else ""}" aria-pressed="{"true" if on else "false"}" aria-label="{name}" aria-describedby="ts-{hid}">'
            f'<span class="tbox"><svg aria-hidden="true"><use href="#i-check"/></svg></span><span class="tname">{name}</span>'
            f'<span class="tstat" id="ts-{hid}">{ct}{bt}</span></button></li>')


def history_json(hs):
    parts = []
    for h in hs:
        days = sorted(h["done"])
        lines = []
        for i in range(0, len(days), 8):
            lines.append("        " + ", ".join(f'"{x}"' for x in days[i:i + 8]))
        cur, best = streaks(days)
        parts.append('    {\n      "name": ' + json.dumps(h["name"]) + f',\n      "current": {cur},\n      "best": {best},\n      "doneToday": {"true" if TODAY.isoformat() in days else "false"},\n      "daysDone": {len(days)},\n      "done": [\n' + ",\n".join(lines) + "\n      ]\n    }")
    return ",\n".join(parts)


def defs():
    out = []
    for n in (3, 12):
        out.append("".join(f'<path id="a{n}-{i}" d="{arc(n, i)}"/>' for i in range(n)))
    return "\n".join(out)


def tokens_from_css():
    import re
    css = (HERE.parent / "system.css").read_text(encoding="utf-8")
    root = css[css.index(":root{"):css.index("}", css.index(":root{"))]
    return dict(re.findall(r"(--[a-z0-9-]+):\s*([^;]+);", root))


def rgba(v):
    v = v.strip()
    if v.startswith("#"):
        return tuple(int(v[i:i + 2], 16) for i in (1, 3, 5)) + (1.0,)
    nums = v[v.index("(") + 1:v.index(")")].split(",")
    return (int(nums[0]), int(nums[1]), int(nums[2]), float(nums[3]))


def over(top, under):
    a = top[3]
    return tuple(round(top[i] * a + under[i] * (1 - a)) for i in range(3)) + (1.0,)


def lum(c):
    def ch(x):
        x /= 255
        return x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4
    return 0.2126 * ch(c[0]) + 0.7152 * ch(c[1]) + 0.0722 * ch(c[2])


def ratio(a, b):
    la, lb = lum(a), lum(b)
    return round((max(la, lb) + 0.05) / (min(la, lb) + 0.05), 2)


CONTRAST_PAIRS = [
    # (fg, bg, needs, where). bg may be "wash" (amber-wash over bg) or "scrimbg" (scrim over bg)
    ("--ink", "--bg", 4.5, "brand word, body text"),
    ("--ink", "--surface", 4.5, "habit names, Year and Done today labels, band title, empty lead"),
    ("--ink", "--surface-2", 4.5, "dialog and sheet titles, tick names, month names, S5 note"),
    ("--ink", "--raise", 4.5, "a label on a hovered button or tick"),
    ("--ink", "--field", 4.5, "typed text in the field"),
    ("--ink", "wash", 4.5, "S4 warning text on the amber wash"),
    ("--ink-soft", "--bg", 4.5, "the date"),
    ("--ink-soft", "--surface", 4.5, "row labels and units, hint, band numbers, legend, field note"),
    ("--ink-soft", "--surface-2", 4.5, "dialog subtitles, P3 and P4 numbers, Delete habit at rest, tick stats"),
    ("--ink-soft", "--raise", 4.5, "a number on a hovered or open day"),
    ("--amber", "--surface", 4.5, "Current on a row"),
    ("--amber", "--surface-2", 4.5, "Current in P2, Current in P1"),
    ("--on-amber", "--amber", 4.5, "Done today pressed, Add, a number on a full core or done bead"),
    ("--on-amber", "--amber-hover", 4.5, "the same on hover"),
    ("--on-amber", "--danger", 4.5, "Delete habit in M1"),
    ("--on-amber", "--danger-hover", 4.5, "Delete habit in M1 on hover"),
    ("--danger", "--surface", 4.5, "field error"),
    ("--danger", "--surface-2", 4.5, "Delete habit in P2 on hover"),
    ("--ink-soft", "--surface-2", 4.5, "disabled field text in S3 (exempt, still passes)"),
    ("--ring", "--surface", 3.0, "not-done segment, Year and Done today edges, Done today dot"),
    ("--ring", "--surface-2", 3.0, "not-done bead, P3 and P4 not-done segment, tick box, Cancel edge"),
    ("--ring", "--bg", 3.0, "Overview button edge"),
    ("--ring", "--field", 3.0, "field border"),
    ("--ink-soft", "--raise", 3.0, "RULING 1 thin not-done segment on a hovered or open day"),
    ("--amber", "--surface", 3.0, "done segment in the band, done bead thread"),
    ("--amber", "--surface-2", 3.0, "done segment in P3 and P4, done bead"),
    ("--amber", "--raise", 3.0, "open day outline"),
    ("--amber", "--bg", 3.0, "S4 banner edge (on the page)"),
    ("--ink", "--surface", 3.0, "today's ring circle in the band"),
    ("--ink", "--surface-2", 3.0, "today's ring circle in P3 and P4, today's bead halo"),
    ("--ink-soft", "--surface", 3.0, "bin icon at rest"),
    ("--danger", "--surface", 3.0, "bin icon and edge on hover and focus"),
    ("--danger", "--field", 3.0, "error field border"),
    ("--focus", "--bg", 3.0, "focus ring on the page"),
    ("--focus", "--surface", 3.0, "focus ring in the list and band"),
    ("--focus", "--surface-2", 3.0, "focus ring in dialogs and sheets"),
]
INFO_PAIRS = [
    ("--ring", "--raise", "RETIRED by ruling 1, f2's thin segment on a hovered or open day"),
    ("--closed", "--surface-2", "days after today in P2 and P4 (inactive, exempt)"),
    ("--closed", "--surface", "none, --closed is only used on --surface-2"),
    ("--surface-2", "scrimbg", "dialog fill against the page under --scrim (the dialog edge, no ratio required)"),
    ("--line", "--surface", "row dividers (decorative)"),
    ("--track", "--surface", "the empty-state core circle (decorative)"),
]


def contrast():
    tk = tokens_from_css()
    bg = rgba(tk["--bg"])
    col = {k: rgba(v) for k, v in tk.items() if v.strip().startswith(("#", "rgba("))}
    col["wash"] = over(col["--amber-wash"], bg)
    col["scrimbg"] = over(col["--scrim"], bg)
    rows = []
    for fg, b, need, where in CONTRAST_PAIRS:
        r = ratio(col[fg], col[b])
        rows.append({"fg": fg, "bg": b, "ratio": r, "needs": need, "pass": r >= need, "where": where})
    info = [{"fg": fg, "bg": b, "ratio": ratio(col[fg], col[b]), "where": w} for fg, b, w in INFO_PAIRS]
    return {"wash": "#%02X%02X%02X" % col["wash"][:3], "scrim over bg": "#%02X%02X%02X" % col["scrimbg"][:3], "pairs": rows, "info": info}


def main():
    if PART == "contrast":
        print(json.dumps(contrast(), indent=1))
        return
    k1, s3, ver = get_histories()
    sets3 = [set(h["done"]) for h in k1]
    sets12 = [set(h["done"]) for h in s3]
    frags = {}
    frags["defs"] = defs()
    frags["band"] = band(sets3)
    frags["band-open"] = band(sets3, "2026-09-22")
    frags["band-s1"] = band([])
    frags["band-s3"] = band(sets12)
    frags["p3"] = popup_grid(sets3)
    frags["p3-open"] = popup_grid(sets3, "2026-09-22")
    frags["p4"] = p4(sets3)
    frags["p2-read"] = p2(set(k1[0]["done"]))
    frags["legend3"] = legend(3)
    frags["legend12"] = legend(12)
    frags["legend0"] = legend(0)
    frags["ovring3"] = ring([TODAY.isoformat() in s for s in sets3])
    frags["ovring12"] = ring([TODAY.isoformat() in s for s in sets12])
    frags["ovring0"] = ring([])
    frags["rows3"] = "\n".join(row(h, i + 1) for i, h in enumerate(k1))
    frags["rows12"] = "\n".join(row(h, i + 1) for i, h in enumerate(s3))
    frags["ticks-0922"] = "\n".join(tick(h, i + 1, "2026-09-22") for i, h in enumerate(k1))
    frags["mini-0922"] = ring(["2026-09-22" in s for s in sets3])
    frags["hist3"] = history_json(k1)
    frags["hist12"] = history_json(s3[3:])
    # compact codes: per month, lead blanks then one character a day. "." before 10 Oct 2025, "x" after today,
    # otherwise the bitmask of done habits (1 = first habit, 2 = second, 4 = third; hex for twelve habits)
    def codes(sets):
        out = []
        m = dt.date(TODAY.year, TODAY.month, 1)
        while m >= dt.date(YEAR_START.year, YEAR_START.month, 1):
            nxt = dt.date(m.year + (m.month == 12), m.month % 12 + 1, 1)
            s = ""
            for dd in range(1, (nxt - m).days + 1):
                d = dt.date(m.year, m.month, dd)
                s += "." if d < YEAR_START else "x" if d > TODAY else format(sum(1 << i for i, st in enumerate(sets) if d.isoformat() in st), "x")
            out.append(f"{ML[m.month - 1]} {m.year} lead={m.weekday()} {s}")
            m = dt.date(m.year - (m.month == 1), (m.month - 2) % 12 + 1, 1)
        return "\n".join(out)
    frags["p4-codes"] = codes(sets3)
    frags["s3-band-codes"] = " ".join(format(sum(1 << i for i, st in enumerate(sets12) if (GRID_START + dt.timedelta(days=j)).isoformat() in st), "03x") for j in range(83))
    frags["bits"] = "\n".join(h["name"] + " " + "".join("1" if (YEAR_START + dt.timedelta(days=j)).isoformat() in set(h["done"]) else "0" for j in range(366)) for h in s3)

    if PART == "info":
        try:
            import PIL  # noqa: F401
            pil = "yes " + PIL.__version__
        except Exception as e:  # noqa: BLE001
            pil = "no (" + type(e).__name__ + ")"
        info = {
            "chromium": ver, "PIL": pil,
            "k1 names": [h["name"] for h in k1], "s3 first three equal k1": [h["done"] for h in s3[:3]] == [h["done"] for h in k1],
            "streaks": {h["name"]: list(streaks(h["done"])) + [TODAY.isoformat() in h["done"], len(h["done"]), min(h["done"]), max(h["done"])] for h in s3},
            "fragment chars": {k: len(v) for k, v in frags.items()},
        }
        print(json.dumps(info, indent=1))
        return
    if isinstance(PART, list):
        for k in PART:
            print(f"<!-- {k} -->")
            print(frags[k])
        return
    text = frags[PART]
    # chunk on line boundaries
    chunks, cur = [], ""
    for line in text.split("\n"):
        if cur and len(cur) + len(line) + 1 > CHUNK_CHARS:
            chunks.append(cur)
            cur = line
        else:
            cur = line if not cur else cur + "\n" + line
    chunks.append(cur)
    print(f"<!-- {PART} chunk {CHUNK + 1} of {len(chunks)} -->")
    print(chunks[CHUNK])


if __name__ == "__main__":
    main()
