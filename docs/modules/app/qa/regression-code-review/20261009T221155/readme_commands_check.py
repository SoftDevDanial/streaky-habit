"""Runs the README's server and live-gate commands as written (only the port is chosen, as the README says <port>).

1. `python -m http.server <port> --bind 127.0.0.1` from the project root: started here, checked to answer, stopped by exact PID.
2. `python tests/browser/live_e2e.py --base-url http://127.0.0.1:<port>/ --out docs/modules/app/qa/regression-code-review/<this run>/live-e2e-check/`
   against that server. The README's own --out example is docs/modules/app/qa/live-e2e/<ts>/, which is the orchestrator's official
   evidence folder, so this check writes its screenshots and json into this review's evidence folder instead. It is a check that the
   command runs on the current code, not the official gate (the orchestrator runs that into docs/regression/<ts>/).
Run: PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python -B readme_commands_check.py   (any cwd)
"""
import pathlib
import socket
import subprocess
import sys
import time
import urllib.request

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[5]
assert (ROOT / "index.html").exists() and (ROOT / "tests" / "browser" / "live_e2e.py").exists(), ROOT
OUT_RELATIVE = "docs/modules/app/qa/regression-code-review/" + HERE.name + "/live-e2e-check/"


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def port_open(port):
    try:
        socket.create_connection(("127.0.0.1", port), timeout=0.5).close()
        return True
    except OSError:
        return False


def main():
    port = free_port()
    command = [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"]
    server = subprocess.Popen(
        command, cwd=str(ROOT), stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    print(f"[server] started pid {server.pid}: python -m http.server {port} --bind 127.0.0.1 (cwd = project root)", flush=True)
    try:
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=1) as reply:
                    print(f"[server] GET / -> {reply.status}, {len(reply.read())} bytes", flush=True)
                break
            except OSError:
                time.sleep(0.25)
        else:
            raise RuntimeError("server did not answer in 15 s")
        gate = [sys.executable, "tests/browser/live_e2e.py", "--base-url", f"http://127.0.0.1:{port}/", "--out", OUT_RELATIVE]
        print("[gate] " + " ".join(gate[1:]), flush=True)
        done = subprocess.run(gate, cwd=str(ROOT), capture_output=True, text=True, timeout=300)
        print(done.stdout.strip())
        if done.stderr.strip():
            print("[gate stderr] " + done.stderr.strip())
        print(f"[gate] exit code {done.returncode}", flush=True)
    finally:
        if server.poll() is None:
            subprocess.run(["taskkill", "/PID", str(server.pid), "/T", "/F"], capture_output=True, timeout=15)
            try:
                server.wait(timeout=10)
            except subprocess.TimeoutExpired:
                server.kill()
        deadline = time.monotonic() + 10
        while port_open(port) and time.monotonic() < deadline:
            time.sleep(0.25)
        print(f"[server] stopped pid {server.pid}; 127.0.0.1:{port} accepts connections: {port_open(port)}", flush=True)


if __name__ == "__main__":
    main()
