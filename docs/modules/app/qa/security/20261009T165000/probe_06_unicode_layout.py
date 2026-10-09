"""New-threat hunt: Unicode, bidi and long names in the list, the dialog and the page layout.

Names up to 40 code points are valid. This feeds such names (stored by another page, so any code point goes through) and
reports: horizontal scroll at 320/360/390, whether the name stays inside its row, whether the trash button stays where it
is and hittable, the dialog title and button geometry, bidi isolation, and whether text from a name can spill into the
dialog's own words. Screenshots of a few cases land in this folder under shots/.
Run: PYTHONDONTWRITEBYTECODE=1 python <this file>   (cwd = project root)
"""
import pathlib
from lib import Run, open_app, state_text, HERE

SHOTS = HERE / "shots"

NAMES = {
    "40 W (widest latin)": "W" * 40,
    "40 fullwidth W": "Ｗ" * 40,
    "40 CJK": "漢" * 40,
    "40 emoji": "\U0001F600" * 40,
    "5 family ZWJ emoji + 5": ("\U0001F468‍\U0001F469‍\U0001F467‍\U0001F466" * 5) + "12345",
    "zalgo 1 base + 39 marks": "Z" + "҉̸̶̀́̂̃̄̅̕" * 3 + "̆" * 9,
    "RLO + latin, no PDF": "‮Reversed text here",
    "RLO then ' pwned' (spoof tail)": "Read 20 pages‮ dleiys .gnp",
    "RLI isolate no PDI": "⁧abc⁧def",
    "LRO + Hebrew": "‭שלום world",
    "Arabic": "عادة القراءة كل يوم",
    "mixed bidi + digits": "abc אבג 123 def דה",
    "40 ZWSP (invisible)": "​" * 40,
    "ZWSP + 'Read'": "​Read",
    "NUL + control": "a\u0000b\u0007c\u001bd",
    "newline inside": "line one\nline two",
    "LS/PS separators": "a b c",
    "unbroken 40 digits": "1234567890" * 4,
    "40 hyphens": "-" * 40,
    "quotes and dialog words": 'a" and "Delete habit',
    "tag-like": "<b>bold</b><i>it</i>",
}


def measure(page, width):
    return page.evaluate(
        """(width) => {
          const doc = document.documentElement;
          const r = (el) => { const b = el.getBoundingClientRect(); return [Math.round(b.left), Math.round(b.top), Math.round(b.right), Math.round(b.bottom)]; };
          const h3 = document.querySelector('h3.habit-name');
          const trash = document.querySelector('.habit-head .icon-btn');
          const row = document.querySelector('li.habit');
          const hit = document.elementFromPoint((r(trash)[0] + r(trash)[2]) / 2, (r(trash)[1] + r(trash)[3]) / 2);
          const cs = getComputedStyle(h3);
          return { scrollWidth: doc.scrollWidth, overflowX: doc.scrollWidth > width, h3: r(h3), trash: r(trash), row: r(row),
                   h3InsideRow: r(h3)[0] >= r(row)[0] && r(h3)[2] <= r(row)[2], trashHittable: hit === trash || trash.contains(hit),
                   h3Height: r(h3)[3] - r(h3)[1], dir: cs.direction, bidi: cs.unicodeBidi, wrap: cs.overflowWrap };
        }""",
        width,
    )


def main():
    SHOTS.mkdir(exist_ok=True)
    with Run() as run:
        b, base = run.browser, run.base
        print("--- layout and bidi per name (stored by another page, sample first row only)")
        print(f"{'case':<34} {'w':>4} scrollW overflow h3Inside trashHit h3H  dir/bidi")
        for label, name in NAMES.items():
            cps = len(list(name))
            for width in (320, 360, 390):
                ctx, page, log = open_app(b, base, storage=state_text([{"name": name, "done": ["2026-10-08"]}]), viewport=(width, 780))
                m = measure(page, width)
                flag = "" if (not m["overflowX"] and m["h3InsideRow"] and m["trashHittable"]) else "  <-- PROBLEM"
                print(f"{label:<34} {width:>4} {m['scrollWidth']:>7} {str(m['overflowX']):>8} {str(m['h3InsideRow']):>8} {str(m['trashHittable']):>8} {m['h3Height']:>4} {m['dir']}/{m['bidi']}{flag}  ({cps} cps)", flush=True)
                if width == 360 and label in ("40 W (widest latin)", "zalgo 1 base + 39 marks", "RLO + latin, no PDF", "RLO then ' pwned' (spoof tail)", "40 ZWSP (invisible)", "40 emoji"):
                    slug = "".join(c if c.isalnum() else "-" for c in label)[:30]
                    page.screenshot(path=str(SHOTS / f"list-{slug}.png"))
                    page.locator(".habit-head .icon-btn").first.click()
                    d = page.evaluate("() => { const d = document.querySelector('dialog').getBoundingClientRect(); const t = document.querySelector('#del-title'); const a = document.querySelector('.dialog-actions').getBoundingClientRect(); return {dialog: [Math.round(d.left), Math.round(d.top), Math.round(d.right), Math.round(d.bottom)], titleText: t.textContent, titleKids: t.children.length, actions: [Math.round(a.left), Math.round(a.top), Math.round(a.right), Math.round(a.bottom)], innerH: innerHeight, innerW: innerWidth}; }")
                    page.screenshot(path=str(SHOTS / f"dialog-{slug}.png"))
                    fits = d["dialog"][0] >= 0 and d["dialog"][2] <= d["innerW"] and d["dialog"][1] >= 0 and d["dialog"][3] <= d["innerH"]
                    print(f"      dialog box {d['dialog']} in viewport {d['innerW']}x{d['innerH']}: fits={fits}; title kids={d['titleKids']}", flush=True)
                ctx.close()

        print("--- 12 habits, all 40 W, 360 x 780: does the page still work (scrollable, last trash reachable)?")
        names = [("W" * 38) + f"{i:02d}" for i in range(12)]
        ctx, page, log = open_app(b, base, storage=state_text([{"name": n, "done": []} for n in names]), viewport=(360, 780))
        m = page.evaluate("() => ({scrollW: document.documentElement.scrollWidth, scrollH: document.documentElement.scrollHeight, rows: document.querySelectorAll('li.habit').length})")
        print("   ", m)
        page.locator("li.habit").last.locator(".icon-btn").click()
        print("    dialog opens for the last row:", page.evaluate("() => document.querySelector('dialog').open"))
        ctx.close()

        print("--- bidi spill: does an unterminated override in a name reorder the dialog's own words? (visual check in shots/)")
    print("done")


if __name__ == "__main__":
    main()
