"""SEC-06 fix sketch, verified in memory only (page.route; src/ is not touched).

The sketch strips the bidirectional format characters from the COPY of the name that goes into the dialog title, and keeps the
FSI and PDI around it. The characters stripped are U+202A to U+202E, U+2066 to U+2069, U+0085, U+001C to U+001E and U+2029,
written in the patched JavaScript as escape text. The stored name and the list are unchanged (the list's h3 isolates its own
text). Every name of probe_06 (the five of the suite, the extra names, and the two names of the accepted U+2069 / paragraph
separator residual) and every name of probe_08 (the SEC-06 names and controls) is measured with it. Expected: every title
in place.
Run: PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python -B <this file>   (cwd = project root)
"""
from chars import BS, js_escapes, js_range
from lib import ROOT, Run
from probe_06_sec02_title import FIVE, MORE, RESIDUAL, ok, title_spots
from probe_08_sec02_unmatched_initiator import NAMES as INITIATOR_NAMES

STRIP = "/[" + js_range(0x202A, 0x202E) + js_range(0x2066, 0x2069).replace(BS + "u2066", BS + "u2066") + js_escapes(0x0085) + js_range(0x001C, 0x001E) + js_escapes(0x2029) + "]/g"
SKETCH = '$("#del-title").textContent = `Delete "' + BS + "u{2068}${habitName.replace(" + STRIP + ', "")}' + BS + 'u{2069}"?`;'


def main():
    with Run() as run:
        say = run.say
        say(f"  patched title line: {SKETCH}")
        view = (ROOT / "src/view.js").read_text(encoding="utf-8")
        fixed_line = '$("#del-title").textContent = `Delete "' + BS + "u{2068}${habitName}" + BS + 'u{2069}"?`;'
        assert view.count(fixed_line) == 1
        sketch = view.replace(fixed_line, SKETCH)
        groups = (("suite names", FIVE), ("extra names", MORE), ("accepted U+2069 / separator residual", RESIDUAL), ("SEC-06 names and controls", INITIATOR_NAMES))
        total = in_place_now = in_place_sketch = 0
        for group, names in groups:
            say(f"  -- {group} --")
            for label, name in names.items():
                now = title_spots(run, name)
                with_sketch = title_spots(run, name, sketch)
                total += 1
                in_place_now += ok(now)
                in_place_sketch += ok(with_sketch)
                say(f"    {label:48s} as shipped: {'in place' if ok(now) else 'QUOTES MOVED':12s} | with the sketch: {'in place' if ok(with_sketch) else 'QUOTES MOVED':12s}")
        say(f"  names measured: {total}; in place as shipped: {in_place_now}; in place with the sketch: {in_place_sketch}")
    run.finish("probe_10")


if __name__ == "__main__":
    main()
