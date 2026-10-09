"""Checks on the fidelity gate itself (scratch, read-only on the product). Reuses the harness's own render() and
diff_images() by loading {sdlc}/harness/fidelity.py as a module; changes nothing in it.

1. What the blur in open-delete-dialog.js hides: the same M1 capture without the blur (the Cancel ring) and what is
   focused at that moment.
2. That the script's title check discriminates: the pre-SEC-02 title and a title without the marks are rejected, the
   shipped title is accepted.
3. That the 0-pixel result is repeatable: M1 run again.
4. A control for the sub-threshold noise in M1: the golden's own DOM turned into a native showModal() dialog (the
   .scrim and inert removed) against the static golden and against the app's candidate.png.
Writes gate_honesty.json and the PNGs it renders into the folder honesty/ next to itself.
"""
import importlib.util
import json
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ROOT = Path(r"{workspace}\examples\streaks")
BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:52346/"
HARNESS = Path(r"{sdlc}\harness\fidelity.py")
spec = importlib.util.spec_from_file_location("sdlc_fidelity", HARNESS)
fid = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fid)

SEED = (ROOT / "tests/browser/fidelity/seed-sample.js").read_text(encoding="utf-8")
AFTER = (ROOT / "tests/browser/fidelity/open-delete-dialog.js").read_text(encoding="utf-8")
GOLDEN = ROOT / "docs/design/delete-dialog.html"
FIXED = "2026-10-08T09:00:00"
OUT = HERE / "honesty"
OUT.mkdir(exist_ok=True)

result = {}


def exact(a_png, b_png):
    a = np.asarray(Image.open(a_png).convert("RGBA"), dtype=np.int32)
    b = np.asarray(Image.open(b_png).convert("RGBA"), dtype=np.int32)
    if a.shape != b.shape:
        return {"shapes": [list(a.shape), list(b.shape)]}
    delta = np.abs(a - b).max(axis=2)
    ys, xs = np.nonzero(delta)
    return {"differing_pixels": int((delta > 0).sum()), "max_channel_delta": int(delta.max()),
            "box": [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())] if len(xs) else None,
            "over_gate_threshold": None}


def gate(g_png, c_png, name):
    rep = fid.diff_images(g_png, c_png, OUT / f"{name}-diff.png", 0.1)
    return {k: rep[k] for k in ("mismatch_pixels", "dimensions_match", "golden_size", "candidate_size")}


with sync_playwright() as pw:
    # ---- 1. without the blur
    no_blur = AFTER.replace("document.activeElement.blur();", "")
    assert no_blur != AFTER, "the blur line was not found"
    for vp in ((390, 844), (1280, 800)):
        tag = f"{vp[0]}x{vp[1]}"
        fid.render(pw, GOLDEN.as_posix(), vp, 1, OUT / f"M1-{tag}-golden.png", True, "light", (), None, None, FIXED)
        fid.render(pw, BASE, vp, 1, OUT / f"M1-{tag}-noblur.png", True, "light", (), SEED, no_blur, FIXED)
        fid.render(pw, BASE, vp, 1, OUT / f"M1-{tag}-blur-repeat.png", True, "light", (), SEED, AFTER, FIXED)
        result[f"without_blur_{tag}"] = {**gate(OUT / f"M1-{tag}-golden.png", OUT / f"M1-{tag}-noblur.png", f"M1-{tag}-noblur"),
                                         "exact_vs_golden": exact(OUT / f"M1-{tag}-golden.png", OUT / f"M1-{tag}-noblur.png")}
        result[f"with_blur_repeat_{tag}"] = {**gate(OUT / f"M1-{tag}-golden.png", OUT / f"M1-{tag}-blur-repeat.png", f"M1-{tag}-blur-repeat"),
                                             "exact_vs_golden": exact(OUT / f"M1-{tag}-golden.png", OUT / f"M1-{tag}-blur-repeat.png")}
        # where the no-blur pixels are
        d = Image.open(OUT / f"M1-{tag}-noblur-diff.png").convert("RGBA")
        arr = np.asarray(d)
        red = np.nonzero((arr[..., 0] == 255) & (arr[..., 1] == 0) & (arr[..., 2] == 60))
        if len(red[0]):
            result[f"without_blur_{tag}"]["mismatch_box"] = [int(red[1].min()), int(red[0].min()), int(red[1].max()), int(red[0].max())]

    # ---- what is focused when the script reaches the blur
    browser = pw.chromium.launch(args=["--force-color-profile=srgb", "--hide-scrollbars"])
    ctx = browser.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=1, reduced_motion="reduce", color_scheme="light", bypass_csp=True)
    page = ctx.new_page()
    page.clock.set_fixed_time(fid.datetime.fromisoformat(FIXED))
    page.add_init_script(SEED)
    page.goto(BASE, wait_until="networkidle")
    page.evaluate("async () => { " + no_blur + "\n }")
    focus_before_blur = page.evaluate(
        "() => { const a = document.activeElement; const cs = getComputedStyle(a); return { tag: a.tagName, text: a.textContent.trim(), focusVisible: a.matches(':focus-visible'), outline: cs.outlineWidth + ' ' + cs.outlineStyle + ' ' + cs.outlineColor, offset: cs.outlineOffset }; }")
    page.evaluate("() => document.activeElement.blur()")
    focus_after_blur = page.evaluate("() => { const a = document.activeElement; return { tag: a.tagName, inDialog: !!a.closest('dialog'), dialogOpen: document.querySelector('dialog.dialog').open, modal: document.querySelector('dialog.dialog').matches(':modal') }; }")
    result["focus_when_the_script_reaches_the_blur"] = focus_before_blur
    result["state_after_the_blur"] = focus_after_blur
    ctx.close()

    # ---- 2. the title check discriminates
    expected = 'Delete "\\u{2068}Read 20 pages\\u{2069}"?'
    assert expected in AFTER
    variants = {
        "shipped_title_in_script": AFTER,
        "pre_SEC02_title_in_script": AFTER.replace(expected, 'Delete "Read 20 pages"?'),
        "marks_swapped_in_script": AFTER.replace(expected, 'Delete "\\u{2069}Read 20 pages\\u{2068}"?'),
        "no_closing_mark_in_script": AFTER.replace(expected, 'Delete "\\u{2068}Read 20 pages"?'),
    }
    outcomes = {}
    for name, body in variants.items():
        ctx = browser.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=1, reduced_motion="reduce", color_scheme="light", bypass_csp=True)
        page = ctx.new_page()
        page.clock.set_fixed_time(fid.datetime.fromisoformat(FIXED))
        page.add_init_script(SEED)
        page.goto(BASE, wait_until="networkidle")
        try:
            page.evaluate("async () => { " + body + "\n }")
            outcomes[name] = "accepted (no throw)"
        except Exception as exc:  # noqa: BLE001
            outcomes[name] = "rejected: " + str(exc).splitlines()[0][:120]
        title = page.evaluate("() => document.querySelector('#del-title').textContent")
        outcomes[name + "__title_in_page"] = json.dumps(title)
        ctx.close()
    result["title_check"] = outcomes
    # the script text itself
    result["script_title_line"] = [ln for ln in AFTER.splitlines() if "unexpected dialog title" in ln]

    # ---- 4. control: the golden's own DOM as a native modal
    for vp in ((390, 844), (1280, 800)):
        tag = f"{vp[0]}x{vp[1]}"
        ctx = browser.new_context(viewport={"width": vp[0], "height": vp[1]}, device_scale_factor=1, reduced_motion="reduce", color_scheme="light", bypass_csp=True)
        page = ctx.new_page()
        page.clock.set_fixed_time(fid.datetime.fromisoformat(FIXED))
        page.add_init_script(fid.FREEZE_INIT_JS)
        page.goto(GOLDEN.as_uri(), wait_until="networkidle")
        page.evaluate(
            """() => {
              document.querySelector('.scrim').remove();
              document.querySelector('.page').removeAttribute('inert');
              const d = document.querySelector('dialog.dialog');
              d.removeAttribute('open');
              d.showModal();
              document.activeElement.blur();
            }"""
        )
        page.add_style_tag(content=fid.FREEZE_CSS)
        page.wait_for_timeout(300)
        page.screenshot(path=str(OUT / f"M1-{tag}-golden-native.png"), full_page=True, animations="disabled")
        ctx.close()
        cand = max((p for p in (ROOT / f"docs/modules/app/qa/fidelity-delete-dialog-{tag}").iterdir() if p.is_dir()), key=lambda p: p.name) / "candidate.png"
        result[f"control_native_golden_{tag}"] = {
            "native_golden_vs_static_golden": {**gate(OUT / f"M1-{tag}-golden.png", OUT / f"M1-{tag}-golden-native.png", f"M1-{tag}-nativecontrol"),
                                               "exact": exact(OUT / f"M1-{tag}-golden.png", OUT / f"M1-{tag}-golden-native.png")},
            "native_golden_vs_app_candidate": {**gate(OUT / f"M1-{tag}-golden-native.png", cand, f"M1-{tag}-native-vs-app"),
                                               "exact": exact(OUT / f"M1-{tag}-golden-native.png", cand)},
        }
    browser.close()

(HERE / "gate_honesty.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(result, indent=1, ensure_ascii=False))
