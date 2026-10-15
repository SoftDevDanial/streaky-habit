"""Fidelity gate runner for Streaks v1.1.0 task 28 (fidelity finder, read-only on the product).

Run from the project root:  python -B <this file> <batch>
batch:
  controls   every golden against itself served by the app's server, at each viewport the gate uses for it,
             and the negative control (today.html against the app with no state flag) at the three viewports.
             Evidence: docs/modules/app/qa/fidelity-controls/<ts>/<control>-<screen>-<WxH>/
  captures   the 23 captures of qa.md "Fidelity gate". Evidence: docs/modules/app/qa/fidelity-<screen>-<WxH>/<ts>/
  noblur     extra (not the gate): the five after-load scripts without their last blur line, one viewport each,
             to show what the blur hides. Evidence: docs/modules/app/qa/fidelity-checklist/<given ts>/noblur/...
One http.server per batch, started here and stopped here, its port checked refusing. Every wait is bounded.
Writes only relative paths under docs/modules/app/qa/. Never writes to docs/design/.
"""
import datetime
import hashlib
import json
import pathlib
import socket
import subprocess
import sys
import time
import urllib.request

import numpy as np
from PIL import Image

ROOT = pathlib.Path.cwd()
if ROOT.name != "streaks" or not (ROOT / "index.html").is_file() or not (ROOT / "docs" / "design").is_dir():
    sys.exit(f"run from the streaks project root, not {ROOT}")

HARNESS = "{sdlc}/harness/fidelity.py"
FIXED = "2026-10-10T09:00:00"
QA = "docs/modules/app/qa"
FID = "tests/browser/fidelity/"
SEED_SAMPLE = FID + "seed-sample.js"
SEED_TWELVE = FID + "seed-twelve.js"
PHONE = ["360x780", "390x844"]
ALL = PHONE + ["1280x800"]
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
RUN_TIMEOUT = 240  # seconds per harness run
BATCH_BUDGET = 540  # seconds, no new run starts after this

CAPTURES = [
    ("today", ALL, ["--candidate-init-script", SEED_SAMPLE]),
    ("day-editor", ALL, ["--candidate-init-script", SEED_SAMPLE, "--candidate-after-load", FID + "open-day-editor.js"]),
    ("year-view", ALL, ["--candidate-init-script", SEED_SAMPLE, "--candidate-after-load", FID + "open-year-view.js"]),
    ("overview", PHONE, ["--candidate-init-script", SEED_SAMPLE, "--candidate-after-load", FID + "open-overview.js"]),
    ("overview-year", ALL, ["--candidate-init-script", SEED_SAMPLE, "--candidate-after-load", FID + "open-overview-year.js"]),
    ("delete-dialog", ALL, ["--candidate-init-script", SEED_SAMPLE, "--candidate-after-load", FID + "open-delete-dialog.js"]),
    ("today-empty", ALL, []),
    ("today-full", ALL, ["--candidate-init-script", SEED_TWELVE]),
]


def stamp():
    return datetime.datetime.now().strftime("%Y%m%d-%H%M%S")


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, timeout=30).stdout.strip()


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def accepts(port):
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.5):
            return True
    except OSError:
        return False


def start_server():
    port = free_port()
    cmd = [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"]
    proc = subprocess.Popen(cmd, cwd=ROOT, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL, creationflags=NO_WINDOW)
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(f"http.server exited early with {proc.returncode}")
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=1) as r:
                r.read()
            return proc, port, cmd
        except OSError:
            time.sleep(0.25)
    stop_server(proc, port)
    raise RuntimeError("gave up after 10 s waiting for http.server")


def stop_server(proc, port):
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"], capture_output=True, timeout=15)
        proc.wait(timeout=5)
    refused = False
    for _ in range(20):  # bounded, 5 s
        if not accepts(port):
            refused = True
            break
        time.sleep(0.25)
    return {"server_pid": proc.pid, "port": port, "exit_code": proc.returncode, "port_refuses": refused}


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def exact(out):
    """Independent read of the two PNGs: the 0.1 count again, and every pixel that differs at any level."""
    g = Image.open(out / "golden.png").convert("RGBA")
    c = Image.open(out / "candidate.png").convert("RGBA")
    info = {"golden_sha256": sha(out / "golden.png"), "candidate_sha256": sha(out / "candidate.png")}
    info["png_bytes_identical"] = info["golden_sha256"] == info["candidate_sha256"]
    w, h = min(g.width, c.width), min(g.height, c.height)
    ga = np.asarray(g.crop((0, 0, w, h)), dtype=np.int32)
    ca = np.asarray(c.crop((0, 0, w, h)), dtype=np.int32)
    delta = np.abs(ga - ca)
    any_mask = delta.max(axis=2) > 0
    dist = np.sqrt(((ga[..., :3] - ca[..., :3]) ** 2).sum(axis=2)) / 441.6729559300637
    info["recount_mismatch_at_0_1"] = int((dist > 0.1).sum())
    info["pixels_differing_any_level"] = int(any_mask.sum())
    info["max_channel_delta"] = int(delta.max()) if delta.size else 0
    if any_mask.any():
        ys, xs = np.nonzero(any_mask)
        info["any_level_box_xywh"] = [int(xs.min()), int(ys.min()), int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)]
    if (dist > 0.1).any():
        ys, xs = np.nonzero(dist > 0.1)
        info["mismatch_box_xywh"] = [int(xs.min()), int(ys.min()), int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)]
    return info


def run_harness(golden, candidate, viewport, flags, out, server, head):
    out = pathlib.Path(out)
    if out.exists():
        raise RuntimeError(f"refused, {out} exists already")
    cmd = [sys.executable, "-B", HARNESS, "--golden", golden, "--candidate", candidate, "--viewport", viewport,
           "--dpr", "1", "--color-scheme", "dark", "--fixed-time", FIXED, *flags, "--out", out.as_posix() + "/"]
    started = datetime.datetime.now().isoformat(timespec="seconds")
    t0 = time.monotonic()
    proc = subprocess.Popen(cmd, cwd=ROOT, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, creationflags=NO_WINDOW)
    try:
        stdout, stderr = proc.communicate(timeout=RUN_TIMEOUT)
        status = "finished"
    except subprocess.TimeoutExpired:
        subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"], capture_output=True, timeout=15)
        stdout, stderr = proc.communicate(timeout=10)
        status = f"gave up after {RUN_TIMEOUT} s, process tree killed"
    meta = {
        "command": cmd, "cwd": str(ROOT), "head": head, "server": server, "started": started,
        "seconds": round(time.monotonic() - t0, 1), "harness_pid": proc.pid, "exit_code": proc.returncode,
        "status": status, "stdout": stdout.strip()[-2000:], "stderr": stderr.strip()[-4000:],
    }
    out.mkdir(parents=True, exist_ok=True)  # only matters when the harness failed before it made the folder
    report = None
    if (out / "report.json").is_file():
        report = json.loads((out / "report.json").read_text(encoding="utf-8"))
        meta["exact"] = exact(out)
    (out / "run-meta.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    row = {"out": out.as_posix(), "exit_code": proc.returncode, "status": status, "seconds": meta["seconds"]}
    if report:
        row.update({k: report[k] for k in ("mismatch_pixels", "mismatch_pct", "dimensions_match", "golden_size", "candidate_size")})
        row.update({k: meta["exact"][k] for k in ("recount_mismatch_at_0_1", "pixels_differing_any_level", "max_channel_delta", "png_bytes_identical")})
    else:
        row["error"] = meta["stderr"][-600:]
    print(json.dumps(row), flush=True)
    return row


def main():
    batch = sys.argv[1]
    head = git("rev-parse", "HEAD")
    tree_before = git("status", "--porcelain", "--", "src", "tests", "index.html", "docs/design")
    t_batch = time.monotonic()
    proc, port, server_cmd = start_server()
    server = {"pid": proc.pid, "port": port, "command": server_cmd}
    print(json.dumps({"batch": batch, "head": head, "server": server, "tree_before": tree_before}), flush=True)
    base = f"http://127.0.0.1:{port}/"
    rows = []
    plan = []
    batch_dir = None
    if batch == "controls":
        batch_dir = pathlib.Path(QA) / "fidelity-controls" / stamp()
        if batch_dir.exists():
            raise SystemExit(f"refused, {batch_dir} exists")
        for screen, viewports, _ in CAPTURES:
            for vp in viewports:
                plan.append((f"./docs/design/{screen}.html", f"{base}docs/design/{screen}.html", vp, [],
                             batch_dir / f"positive-{screen}-{vp}"))
        for vp in ALL:
            plan.append(("./docs/design/today.html", base, vp, [], batch_dir / f"negative-today-{vp}"))
    elif batch == "captures":
        for screen, viewports, flags in CAPTURES:
            for vp in viewports:
                plan.append((f"./docs/design/{screen}.html", base, vp, flags, None, f"{QA}/fidelity-{screen}-{vp}"))
    elif batch == "noblur":
        batch_dir = pathlib.Path(QA) / "fidelity-checklist" / sys.argv[2] / "noblur"
        scratch = pathlib.Path(sys.argv[3])
        for screen, vp, script in [("day-editor", "390x844", "open-day-editor.js"), ("day-editor", "1280x800", "open-day-editor.js"),
                                   ("year-view", "390x844", "open-year-view.js"), ("overview", "390x844", "open-overview.js"),
                                   ("overview-year", "390x844", "open-overview-year.js"), ("delete-dialog", "390x844", "open-delete-dialog.js")]:
            plan.append((f"./docs/design/{screen}.html", base, vp,
                         ["--candidate-init-script", SEED_SAMPLE, "--candidate-after-load", (scratch / ("noblur-" + script)).as_posix()],
                         batch_dir / f"{screen}-{vp}"))
    else:
        raise SystemExit(f"unknown batch {batch}")
    try:
        for item in plan:
            if time.monotonic() - t_batch > BATCH_BUDGET:
                rows.append({"skipped": str(item[:4]), "why": f"batch budget {BATCH_BUDGET} s spent, gave up"})
                print(json.dumps(rows[-1]), flush=True)
                continue
            golden, candidate, vp, flags, out = item[:5]
            if out is None:
                out = pathlib.Path(item[5]) / stamp()
                while out.exists():  # two runs in the same second never share a folder
                    time.sleep(1)
                    out = pathlib.Path(item[5]) / stamp()
            rows.append(run_harness(golden, candidate, vp, flags, out, server, head))
    finally:
        stopped = stop_server(proc, port)
        tree_after = git("status", "--porcelain", "--", "src", "tests", "index.html", "docs/design")
        summary = {"batch": batch, "head": head, "server": server, "stopped": stopped, "tree_before": tree_before,
                   "tree_after": tree_after, "seconds": round(time.monotonic() - t_batch, 1), "rows": rows}
        if batch_dir is not None:
            batch_dir.mkdir(parents=True, exist_ok=True)
            (batch_dir / "batch-summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
        print(json.dumps({"stopped": stopped, "tree_after": tree_after, "seconds": summary["seconds"]}), flush=True)


if __name__ == "__main__":
    main()
