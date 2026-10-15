"""Derive the compact capture from the raw stdout of rs9a_views.py (security finder, re-check 2026-10-15).
Kept lines: the engine line, 'added Read' (header, band, standIn, pageErrors), every year view line, every
'changed storage' line (stored text compared byte for byte with the value right after 'added Read'), 'browser closed',
the server lines. Dropped: the snapshot lines between presses, headingIds, headerText, banners, firstLabels.
Kept fields are copied as they are, except titles (first and last) and openKeys (first two and last)."""
import json, sys
for line in open(sys.argv[1], encoding="utf-8"):
    if not line.startswith("{"):
        print(line.rstrip()); continue
    r = json.loads(line)
    st = r.get("step", "")
    c = r.get("case")
    if c is None:
        print(json.dumps(r)); continue
    if st == "added Read":
        out = {k: r.get(k) for k in ("engine", "case", "step", "answers", "header", "band", "standIn", "pageErrors")}
    elif "Year" in st:
        out = {k: r[k] for k in ("engine", "case", "step", "answers", "isOpen", "months", "titles", "daysPerMonth", "openControls",
                                  "openKeys", "openKeysPassingIsDateKey", "closed", "blank", "lead", "duplicateIds", "pageErrors", "lastError") if k in r}
        if out.get("titles") and len(out["titles"]) > 2:
            out["titles"] = [out["titles"][0], out["titles"][-1]]
        if out.get("openKeys") and len(out["openKeys"]) > 3:
            out["openKeys"] = [out["openKeys"][0], out["openKeys"][1], "...", out["openKeys"][-1]]
    elif "changed storage" in st or st == "browser closed":
        out = r
    else:
        continue
    print(json.dumps(out, ensure_ascii=True))
