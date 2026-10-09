"""Serves the project root on a free 127.0.0.1 port, runs the commands given, then stops the server by its exact PID.

usage (cwd = project root): python -B serve_and_run.py <command> [<command> ...]
Each <command> is one quoted string. The text {BASE} in a command is replaced with the app's address, such as
http://127.0.0.1:54321/ (it ends with a slash). A command runs with the project root as its working directory.
Exit code: the first non-zero exit code of a command, else 0. The server is stopped in a finally block, and the script
prints whether its port still accepts connections afterwards. It starts nothing else and kills nothing but its own server.
"""
import pathlib
import shlex
import socket
import subprocess
import sys
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[6]  # docs/modules/app/qa/security-solver/<stamp>/ is six levels deep


def free_port():
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def accepts(port):
    try:
        socket.create_connection(("127.0.0.1", port), timeout=0.5).close()
    except OSError:
        return False
    return True


def main():
    commands = sys.argv[1:]
    port = free_port()
    server = subprocess.Popen(
        [sys.executable, "-B", "-m", "http.server", str(port), "--bind", "127.0.0.1"],
        cwd=str(ROOT), stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    print(f"[serve_and_run] started http.server pid {server.pid} on 127.0.0.1:{port}, root {ROOT}", flush=True)
    code = 0
    try:
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=1).close()
                break
            except OSError:
                time.sleep(0.25)
        else:
            raise RuntimeError("the server did not answer")
        base = f"http://127.0.0.1:{port}/"
        for text in commands:
            command = shlex.split(text.replace("{BASE}", base), posix=True)
            print(f"[serve_and_run] run: {' '.join(command)}", flush=True)
            result = subprocess.run(command, cwd=str(ROOT), timeout=300)
            print(f"[serve_and_run] exit code {result.returncode}", flush=True)
            if result.returncode != 0 and code == 0:
                code = result.returncode
    finally:
        subprocess.run(["taskkill", "/PID", str(server.pid), "/T", "/F"], capture_output=True, timeout=15)
        try:
            server.wait(timeout=10)
        except subprocess.TimeoutExpired:
            server.kill()
        deadline = time.monotonic() + 10
        while accepts(port) and time.monotonic() < deadline:
            time.sleep(0.25)
        print(f"[serve_and_run] stopped pid {server.pid}; 127.0.0.1:{port} accepts connections: {accepts(port)}", flush=True)
    sys.exit(code)


main()
