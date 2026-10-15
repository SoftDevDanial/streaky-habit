"""Runs probe_04_csp_network.py after lib has put tests/browser on sys.path (probe_04 imports conftest before lib).
Usage: python -u -B run_04.py [chromium] [webkit]
"""
import runpy

import lib  # noqa: F401  sets sys.path and dont_write_bytecode

runpy.run_path(str(lib.HERE / "probe_04_csp_network.py"), run_name="__main__")
