"""T1, T2, T8, T9: hostile saved data through the running app. Prints one line per case.

Each case seeds `streaks.state` from a same-origin page, opens the app, then records: the rows shown, whether the
S5 note shows, the stored text after load, console errors, page errors, JS dialogs, prototype changes against a clean
baseline and the load time. Run: PYTHONDONTWRITEBYTECODE=1 python <this file>   (cwd = project root)
"""
import json
import time
from lib import Run, open_app, state_text, stored, row_names, proto_fingerprint, KEY

ISO = "2026-10-08"
EMPTY = '{"version":1,"habits":[]}'


def snap(page, log, raw, elapsed):
    note = page.locator("div.note").count()
    rows = row_names(page)
    after = stored(page)
    fp = proto_fingerprint(page)
    return {
        "note": note,
        "rows": rows,
        "stored_after": (after if after is None or len(after) < 90 else f"<{len(after)} chars>"),
        "unchanged": after == raw,
        "reset_to_empty": after == EMPTY,
        "console_errors": [c["text"][:90] for c in log.console_errors()],
        "page_errors": log.errors[:2],
        "dialogs": len(log.dialogs),
        "ms": round(elapsed * 1000),
        "fp": fp,
    }


def main():
    with Run() as run:
        b, base = run.browser, run.base
        # clean baseline
        ctx, page, log = open_app(b, base)
        baseline = proto_fingerprint(page)
        ctx.close()

        def case(label, raw, expect=None):
            t0 = time.perf_counter()
            ctx, page, log = open_app(b, base, storage=raw)
            try:
                page.wait_for_selector(".cells .hc", state="attached", timeout=60000)
                elapsed = time.perf_counter() - t0
                r = snap(page, log, raw, elapsed)
                polluted = r["fp"] != baseline
                verdict = ""
                if expect == "unreadable":
                    verdict = "OK" if (r["note"] == 1 and r["reset_to_empty"]) else "UNEXPECTED"
                elif expect == "readable":
                    verdict = "OK" if (r["note"] == 0) else "UNEXPECTED"
                print(f"{label:<58} note={r['note']} rows={len(r['rows'])} reset={r['reset_to_empty']} unchanged={r['unchanged']} "
                      f"polluted={polluted} cons_err={len(r['console_errors'])} page_err={len(r['page_errors'])} "
                      f"dlg={r['dialogs']} {r['ms']}ms {verdict}", flush=True)
                if r["console_errors"] or r["page_errors"]:
                    print("      errors:", r["console_errors"], r["page_errors"], flush=True)
                return r, page, ctx
            except Exception as error:  # noqa: BLE001
                print(f"{label:<58} EXCEPTION {error!r}", flush=True)
                ctx.close()
                return None, None, None

        def close(ctx):
            if ctx:
                ctx.close()

        print("--- prototype pollution and key games (T1, T2)")
        for label, raw, exp in [
            ("T2 __proto__ in habit (spec case)", '{"version":1,"habits":[{"name":"Read","done":[],"__proto__":{"polluted":true}}]}', "readable"),
            ("T2 __proto__ in habit, version-like", '{"version":1,"habits":[{"name":"Read","done":[],"__proto__":{"name":"evil","done":["2026-10-08"]}}]}', "readable"),
            ("T2 constructor.prototype in habit", '{"version":1,"habits":[{"name":"Read","done":[],"constructor":{"prototype":{"polluted":1}}}]}', "readable"),
            ("T2 __proto__ at top level, no version", '{"__proto__":{"version":1,"habits":[]},"habits":[]}', "unreadable"),
            ("T2 __proto__ at top level beside real keys", '{"version":1,"habits":[],"__proto__":{"version":2,"polluted":1}}', "readable"),
            ("T2 habits is __proto__ object", '{"version":1,"habits":{"__proto__":[]}}', "unreadable"),
            ("T2 name __proto__ (a string)", state_text([{"name": "__proto__", "done": []}]), "readable"),
            ("T2 names constructor,toString,valueOf,hasOwnProperty,prototype",
             state_text([{"name": n, "done": [ISO]} for n in ["constructor", "toString", "valueOf", "hasOwnProperty", "prototype", "__defineGetter__", "__proto__"]]), "readable"),
            ("T1 done element __proto__", '{"version":1,"habits":[{"name":"a","done":["__proto__"]}]}', "unreadable"),
            ("T1 done is object", '{"version":1,"habits":[{"name":"a","done":{"0":"2026-10-08","length":1}}]}', "unreadable"),
            ("T1 habits array-like", '{"version":1,"habits":{"0":{"name":"a","done":[]},"length":1}}', "unreadable"),
            ("T1 name object with toString", '{"version":1,"habits":[{"name":{"toString":"x","trim":"y"},"done":[]}]}', "unreadable"),
            ("T1 version 1.0 / 1e0 (JSON numbers equal 1)", '{"version":1.0,"habits":[]}', "readable"),
            ("T1 version true", '{"version":true,"habits":[]}', "unreadable"),
            ("T1 version [1]", '{"version":[1],"habits":[]}', "unreadable"),
            ("T1 duplicate key version last wins 2", '{"version":1,"version":2,"habits":[]}', "unreadable"),
            ("T1 top-level string", '"{}"', "unreadable"),
            ("T1 empty string", "", "unreadable"),
            ("T1 whitespace only", "   ", "unreadable"),
            ("T1 NaN/Infinity tokens", '{"version":NaN,"habits":[]}', "unreadable"),
            ("T1 BOM prefix", "﻿" + EMPTY, "unreadable"),
            ("T1 trailing garbage", EMPTY + "x", "unreadable"),
            ("T1 12 habits ok", state_text([{"name": f"H{i}", "done": []} for i in range(12)]), "readable"),
            ("T1 13 habits", state_text([{"name": f"H{i}", "done": []} for i in range(13)]), "unreadable"),
            ("T1 date with spaces ' 2026-10-08'", '{"version":1,"habits":[{"name":"a","done":[" 2026-10-08"]}]}', "unreadable"),
            ("T1 date unicode digits (arabic-indic)", '{"version":1,"habits":[{"name":"a","done":["٢٠٢٦-10-08"]}]}', "unreadable"),
            ("T1 date newline-suffixed '2026-10-08\\n'", '{"version":1,"habits":[{"name":"a","done":["2026-10-08\\n"]}]}', "unreadable"),
            ("T1 date year 0000", '{"version":1,"habits":[{"name":"a","done":["0000-01-01"]}]}', "unreadable"),
            ("T1 date 9999-12-31 valid, far future", '{"version":1,"habits":[{"name":"a","done":["9999-12-31","0001-01-01"]}]}', "readable"),
            ("T1 name 40 emoji (80 UTF-16 units)", state_text([{"name": "\U0001F600" * 40, "done": []}]), "readable"),
            ("T1 name 41 emoji", state_text([{"name": "\U0001F600" * 41, "done": []}]), "unreadable"),
            ("T1 name with lone surrogate (escaped)", '{"version":1,"habits":[{"name":"a\\ud800b","done":[]}]}', "readable"),
            ("T1 name with NUL", '{"version":1,"habits":[{"name":"a\\u0000b","done":[]}]}', "readable"),
            ("T1 name nbsp-padded", '{"version":1,"habits":[{"name":"\\u00a0a","done":[]}]}', "unreadable"),
        ]:
            r, page, ctx = case(label, raw, exp)
            close(ctx)

        print("--- script injection names stored by another page (T3, T9)")
        payloads = [
            '<img src=x onerror=window.__pwned=1>',
            '<svg onload=window.__pwned=1>',
            'javascript:window.__pwned=1',
            '<script>window.__pwned=1</script>',
            '</h3><img src=x onerror=window.__pwned=1>',
            '"><svg/onload=window.__pwned=1>',
            "'><img src=x onerror=window.__pwned=1>",
            '<a href="javascript:window.__pwned=1">x</a>',
            '<style>*{display:none}</style>',
            '<iframe srcdoc="<script>parent.__pwned=1</script>">',
            '${window.__pwned=1}`{{constructor.constructor("1")()}}',
            '<input autofocus onfocus=window.__pwned=1>',
            '<details open ontoggle=window.__pwned=1>',
            '<base href=//127.0.0.1:1/>',
            '<meta http-equiv=refresh content="0;//127.0.0.1:1/">',
            '<link rel=stylesheet href=//127.0.0.1:1/x.css>',
            '<form action=//127.0.0.1:1/><button>x',
        ]
        for p in payloads:
            if len(list(p)) > 40:
                print(f"   (skip, {len(list(p))} code points > 40, would reset)  {p[:50]}")
                continue
            raw = state_text([{"name": p, "done": [ISO]}])
            r, page, ctx = case(f"stored name {p[:44]!r}", raw, "readable")
            if page:
                info = page.evaluate(
                    """(name) => {
                      const h = document.querySelector('h3.habit-name');
                      const t = document.querySelector('.icon-btn[aria-label^="Delete "]');
                      const hostile = document.querySelectorAll('body img, body iframe, body script, body style, body object, body embed, body a, body math, body base, body meta, body link, body input:not(#new-habit)');
                      const handlers = [...document.querySelectorAll('*')].flatMap(e => [...e.attributes].filter(a => /^on/i.test(a.name)).map(a => e.tagName + '.' + a.name));
                      return {textMatches: h.textContent === name, childElems: h.children.length,
                              labelMatches: t.getAttribute('aria-label') === 'Delete ' + name,
                              hostileCount: hostile.length, handlers, pwned: window.__pwned === undefined ? 'undef' : window.__pwned,
                              baseURI: document.baseURI, headNodes: document.head.children.length};
                    }""",
                    p,
                )
                page.locator('button.icon-btn[aria-label^="Delete "]').click()
                title = page.evaluate("() => { const t = document.querySelector('#del-title'); return {text: t.textContent, kids: t.children.length}; }")
                ok = info["textMatches"] and info["childElems"] == 0 and info["labelMatches"] and info["hostileCount"] == 0 and not info["handlers"] and info["pwned"] == "undef" and title["text"] == f'Delete "{p}"?' and title["kids"] == 0
                print(f"      -> {'OK literal text' if ok else 'PROBLEM'} {info} title_kids={title['kids']} csp_console={[c['text'][:70] for c in log.console if 'Content Security' in c['text'] or 'Refused' in c['text']]}", flush=True)
            close(ctx)

        print("--- size and resource exhaustion at load (T8)")
        big = lambda n: "a" * n
        r, page, ctx = case("T8 4.9M chars of 'a' (not JSON)", big(4_900_000), "unreadable"); close(ctx)
        r, page, ctx = case("T8 4.9M-char habit name", '{"version":1,"habits":[{"name":"' + big(4_900_000) + '","done":[]}]}', "unreadable"); close(ctx)
        r, page, ctx = case("T8 4.9M-char name of astral emoji", '{"version":1,"habits":[{"name":"' + "\U0001F600" * 1_200_000 + '","done":[]}]}', "unreadable"); close(ctx)
        r, page, ctx = case("T8 4.9M-char ignored extra property", '{"version":1,"habits":[],"x":"' + big(4_900_000) + '"}', "readable"); close(ctx)
        r, page, ctx = case("T8 depth 1,000,000 arrays (not valid state)", "[" * 1_000_000 + "]" * 1_000_000, "unreadable"); close(ctx)
        r, page, ctx = case("T8 depth 400,000 inside ignored extra prop", '{"version":1,"habits":[],"x":' + "[" * 400_000 + "]" * 400_000 + "}", "readable"); close(ctx)
        r, page, ctx = case("T8 2M duplicate valid dates (one habit)", '{"version":1,"habits":[{"name":"a","done":[' + ",".join(['"2026-10-08"'] * 380_000) + "]}]}", "readable"); close(ctx)
        r, page, ctx = case("T8 380k unsorted invalid-last (rejects at end)", '{"version":1,"habits":[{"name":"a","done":[' + ",".join(['"2026-10-08"'] * 380_000) + ',"2026-13-01"]}]}', "unreadable"); close(ctx)

        import datetime as dt
        def days(n, start=dt.date(1, 1, 1), step=1):
            return [(start + dt.timedelta(days=i * step)).isoformat() for i in range(n)]
        d400 = days(400_000)
        raw = state_text([{"name": "a", "done": d400}])
        print(f"      (valid 400k consecutive days in one habit: {len(raw)} chars)")
        t0 = time.perf_counter()
        ctx, page, log = open_app(b, base, storage=raw)
        page.wait_for_selector(".habits .habit", timeout=120000)
        print(f"{'T8 valid 400k consecutive days, 1 habit: boot':<58} {round((time.perf_counter()-t0)*1000)}ms  streak={page.locator('.streak').inner_text()!r}", flush=True)
        t1 = time.perf_counter()
        page.locator("button.day").last.click()
        page.wait_for_function("() => document.querySelector('button.day:last-child').getAttribute('aria-pressed') === 'true'")
        print(f"      one tick (full recompute + 5MB save): {round((time.perf_counter()-t1)*1000)}ms; cons_err={len(log.console_errors())} page_err={len(log.errors)}", flush=True)
        ctx.close()
        d12 = [days(33_000, dt.date(1 + i * 90, 1, 1)) for i in range(12)]
        raw = state_text([{"name": f"Habit {i}", "done": d12[i]} for i in range(12)])
        print(f"      (valid 12 x 33k days: {len(raw)} chars)")
        t0 = time.perf_counter()
        ctx, page, log = open_app(b, base, storage=raw)
        page.wait_for_selector(".habits .habit", timeout=120000)
        print(f"{'T8 valid 12 habits x 33k days: boot':<58} {round((time.perf_counter()-t0)*1000)}ms", flush=True)
        t1 = time.perf_counter()
        page.locator("button.day").last.click()
        page.wait_for_function("() => document.querySelector('button.day:last-child').getAttribute('aria-pressed') === 'true'")
        print(f"      one tick: {round((time.perf_counter()-t1)*1000)}ms; cons_err={len(log.console_errors())} page_err={len(log.errors)}", flush=True)
        ctx.close()
        # sparse: every other day (each key starts its own run in bestStreak)
        raw = state_text([{"name": "a", "done": days(190_000, dt.date(1, 1, 1), 2)}])
        t0 = time.perf_counter()
        ctx, page, log = open_app(b, base, storage=raw)
        page.wait_for_selector(".habits .habit", timeout=120000)
        print(f"{'T8 valid 190k alternate days (190k run starts): boot':<58} {round((time.perf_counter()-t0)*1000)}ms  chars={len(raw)}", flush=True)
        ctx.close()

        print("--- loading writes nothing (R16) when readable")
        pretty = json.dumps({"version": 1, "habits": [{"name": "Read", "done": [ISO], "color": "red"}], "theme": "dark"}, indent=2)
        r, page, ctx = case("R16 readable pretty-printed with extras: unchanged", pretty, "readable")
        print("      unchanged after load:", r["unchanged"] if r else None)
        close(ctx)

    print("done")


if __name__ == "__main__":
    main()
