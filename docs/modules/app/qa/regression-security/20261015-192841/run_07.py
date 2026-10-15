"""Runs probe_07_delete_guard.py after lib has put tests/browser on sys.path (probe_07 imports conftest before lib).
Usage: python -u -B run_07.py [chromium] [webkit]
"""
import runpy

import lib  # noqa: F401  sets sys.path and dont_write_bytecode

runpy.run_path(str(lib.HERE / "probe_07_delete_guard.py"), run_name="__main__")
