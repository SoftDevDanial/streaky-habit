"""One-off edit of my own scratch script states_check.py: replace the placeholder K1 field check with a real one."""
import pathlib

p = pathlib.Path(__file__).resolve().parent / "states_check.py"
text = p.read_text(encoding="utf-8")
old_start = text.index('                    k1 = {p: v for p, v in k1_field["picked"].items() if fld["count"] == 1}')
old_end = text.index("                ctx.close()", old_start)
new = '''                    err_field = read(page, "#nh", METHOD)
                    changed = {q: [k1_field["picked"][q], err_field["picked"][q]] for q in METHOD
                               if k1_field["picked"][q] != err_field["picked"][q]}
                    edges = [f"border-{side}-color" for side in SIDES]
                    check(fld, "against K1's field only the edge colour changed, to --danger",
                          sorted(changed) == sorted(edges) and all(v[1] == "rgb(255, 107, 102)" for v in changed.values()), changed)
'''
text = text[:old_start] + new + text[old_end:]
p.write_text(text, encoding="utf-8")
print("patched", p.name)
