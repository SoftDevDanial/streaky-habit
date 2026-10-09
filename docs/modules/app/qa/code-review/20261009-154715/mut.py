"""Mutation runner for the app code review.

usage: python mut.py <work dir> <baseline | all | id,id,...> <maxfail> [<pytest -k expression>]

It serves a pristine copy of the project from memory-patched responses on 127.0.0.1 (a free port, in a
thread of this process), runs the browser suite against it as a child process, then stops the server.
It writes no file. Every child it starts is waited for, and on a timeout the child's process tree is killed
by PID (taskkill /T /F on the PID it started, never by name).
"""
import http.server
import os
import pathlib
import subprocess
import sys
import threading
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from mutants import MUTANTS  # noqa: E402

WORK = pathlib.Path(sys.argv[1]).resolve()
WHICH = sys.argv[2]
MAXFAIL = sys.argv[3]
KEXPR = sys.argv[4] if len(sys.argv) > 4 else None
RUN_TIMEOUT_SECONDS = 420
TYPES = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8"}


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WORK), **kwargs)

    def log_message(self, *args):
        pass

    def do_GET(self):
        path = self.path.split("?", 1)[0].split("#", 1)[0]
        key = "index.html" if path in ("/", "/index.html") else path.lstrip("/")
        body = self.server.patched.get(key)
        if body is None:
            return super().do_GET()
        data = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", TYPES.get(pathlib.PurePosixPath(key).suffix, "application/octet-stream"))
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)


def patched_files(mutant):
    files = {}
    for relpath, old, new in mutant["patches"]:
        text = files.get(relpath)
        if text is None:
            text = (WORK / relpath).read_text(encoding="utf-8")
        found = text.count(old)
        if found != 1:
            raise SystemExit(f"{mutant['id']}: patch text occurs {found} times in {relpath}: {old[:60]!r}")
        files[relpath] = text.replace(old, new)
    return files


def run_one(mutant):
    files = patched_files(mutant)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.patched = files
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    env = dict(os.environ, STREAKS_BASE_URL=f"http://127.0.0.1:{port}/", PYTHONDONTWRITEBYTECODE="1")
    env.pop("STREAKS_SUBPATH_URL", None)
    env.pop("STREAKS_EVIDENCE_DIR", None)
    command = [sys.executable, "-m", "pytest", "tests/browser", "-q", "-p", "no:cacheprovider", "--tb=no", "-rf",
               "--maxfail", MAXFAIL]
    if KEXPR:
        command += ["-k", KEXPR]
    started = time.monotonic()
    proc = subprocess.Popen(command, cwd=str(WORK), env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    print(f"[{mutant['id']}] server port {port}, pytest pid {proc.pid}, runner pid {os.getpid()}", flush=True)
    timed_out = False
    try:
        output, _ = proc.communicate(timeout=RUN_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        timed_out = True
        subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"], capture_output=True, timeout=30)
        output, _ = proc.communicate(timeout=30)
    finally:
        server.shutdown()
        server.server_close()
    seconds = time.monotonic() - started
    lines = [line for line in output.splitlines() if line.strip()]
    failed = [line.split(" - ")[0].replace("FAILED ", "").replace("tests/browser/", "") for line in lines if line.startswith("FAILED")]
    summary = lines[-1] if lines else "(no output)"
    verdict = "TIMEOUT" if timed_out else ("KILLED" if failed or "error" in summary.lower() else "SURVIVED")
    print(f"RESULT {mutant['id']}: {verdict} in {seconds:.0f}s | {mutant['what']}", flush=True)
    print(f"   summary: {summary}", flush=True)
    for name in failed[:8]:
        print(f"   failed: {name}", flush=True)
    if len(failed) > 8:
        print(f"   ... and {len(failed) - 8} more", flush=True)
    if verdict == "KILLED" and not failed:
        print("   (error without FAILED lines)\n" + "\n".join(lines[-6:]), flush=True)


def main():
    if WHICH == "baseline":
        run_one({"id": "baseline", "what": "pristine copy, no patch", "patches": []})
        return
    wanted = None if WHICH == "all" else WHICH.split(",")
    selected = [m for m in MUTANTS if wanted is None or m["id"] in wanted]
    known = {m["id"] for m in MUTANTS}
    for name in wanted or []:
        if name not in known:
            raise SystemExit(f"unknown mutant {name}")
    for mutant in selected:
        run_one(mutant)


main()
