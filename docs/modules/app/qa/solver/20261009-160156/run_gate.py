"""Runs tests/browser/live_e2e.py against a server this script starts and stops, for the WR-13 before/after check.

usage: python -B run_gate.py <out folder inside the project, relative to the project root>

It reuses conftest._StaticServer (a `python -m http.server <free port> --bind 127.0.0.1` child that is
killed by PID and whose port is re-checked) and calls live_e2e.run(), the function the script's own
command line calls. The official cold-boot gate run is the orchestrator's, not this one.
"""
import pathlib
import sys

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT / "tests" / "browser"))

import conftest  # noqa: E402
import live_e2e  # noqa: E402

out = (ROOT / sys.argv[1]).resolve()
if ROOT not in out.parents:
    sys.exit(f"the output folder must be inside the project: {out}")
server = conftest._StaticServer(ROOT)
try:
    server.start()
    code = live_e2e.run(f"http://127.0.0.1:{server.port}/", out)
finally:
    server.stop()
sys.exit(code)
