"""Index of the task 28 fidelity run, written into the checklist folder (fidelity finder, read-only on the product).

Run from the project root:  python -B <this file> <checklist folder> <controls folder> <capture folder> ...
Reads each capture's own report.json and run-meta.json (the harness's output, the primary artifacts), writes
<checklist>/gate-summary.json, and copies this session's scratch scripts into <checklist>/scripts/ with their
SHA-256, so the run can be repeated after the scratchpad is gone. Refuses to overwrite.
"""
import hashlib
import json
import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
checklist = pathlib.Path(sys.argv[1])
controls = pathlib.Path(sys.argv[2])
captures = [pathlib.Path(p) for p in sys.argv[3:]]
summary_path = checklist / "gate-summary.json"
scripts_dir = checklist / "scripts"
if summary_path.exists() or scripts_dir.exists():
    sys.exit("refused, the summary or the scripts folder exists")


def row(folder):
    report = json.loads((folder / "report.json").read_text(encoding="utf-8"))
    meta = json.loads((folder / "run-meta.json").read_text(encoding="utf-8"))
    return {"folder": folder.as_posix(), "golden": report["golden"], "viewport": report["viewport"],
            "candidate_init_script": report["candidate_init_script"], "candidate_after_load": report["candidate_after_load"],
            "fixed_time": report["fixed_time"], "color_scheme": report["color_scheme"], "dpr": report["dpr"],
            "threshold": report["threshold"], "full_page": report["full_page"],
            "mismatch_pixels": report["mismatch_pixels"], "dimensions_match": report["dimensions_match"],
            "golden_size": report["golden_size"], "candidate_size": report["candidate_size"],
            "pixels_differing_any_level": meta["exact"]["pixels_differing_any_level"],
            "png_bytes_identical": meta["exact"]["png_bytes_identical"], "exit_code": meta["exit_code"],
            "seconds": meta["seconds"], "head": meta["head"], "server": meta["server"]}


summary = {
    "captures": [row(c) for c in captures],
    "controls": [row(c) for c in sorted(p for p in controls.iterdir() if p.is_dir())],
}
summary["totals"] = {
    "captures": len(summary["captures"]),
    "captures_at_budget": sum(1 for r in summary["captures"] if r["mismatch_pixels"] == 0 and r["dimensions_match"] and r["exit_code"] == 0),
    "positive_controls_at_0": sum(1 for r in summary["controls"] if "positive-" in r["folder"] and r["mismatch_pixels"] == 0 and r["dimensions_match"]),
    "negative_controls_above_0": sum(1 for r in summary["controls"] if "negative-" in r["folder"] and r["mismatch_pixels"] > 0),
}
summary_path.write_text(json.dumps(summary, indent=1), encoding="utf-8")
scripts_dir.mkdir()
digests = {}
for p in sorted(HERE.iterdir()):
    if p.is_file() and p.suffix in (".py", ".js", ".ps1"):
        shutil.copyfile(p, scripts_dir / p.name)
        digests[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
(scripts_dir / "SHA256.json").write_text(json.dumps(digests, indent=1), encoding="utf-8")
print(json.dumps(summary["totals"]), len(digests), "scripts copied")
