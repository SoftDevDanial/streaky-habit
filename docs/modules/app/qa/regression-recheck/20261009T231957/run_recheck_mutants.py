"""Re-runs the regression code-review finder's mutant runner against the current tests (regression re-check, 2026-10-09).

usage: python -B run_recheck_mutants.py <project root>

Runs, one runner call at a time:
  1. baseline (pristine app) against test_delete
  2. the six mutants the solver was asked about, against test_delete: G-450, G-600, G-le, G-kbd-delete-open must be KILLED,
     P-kbd-click-passes and G-bubble are expected to SURVIVE (ruled unspecified / equivalent)
  3. the two expected survivors again against the whole browser suite
It calls the finder's `run_mutants.py` (which calls the first review's `mut.py`) as a child process and waits for it. The
mutants are applied in memory by that runner; no project file is written. This script prints to stdout and saves the same
text as `mutants_output.txt` next to itself (its own evidence folder).
"""
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = pathlib.Path(sys.argv[1]).resolve()
RUNNER = ROOT / "docs/modules/app/qa/regression-code-review/20261009T221155/run_mutants.py"
LOG = []


def say(text):
    print(text, flush=True)
    LOG.append(text)


def call(which, maxfail, kexpr=None):
    command = [sys.executable, "-B", str(RUNNER), str(ROOT), which, str(maxfail)]
    if kexpr:
        command.append(kexpr)
    say(f"\n=== {which} (maxfail {maxfail}, -k {kexpr}) ===")
    done = subprocess.run(command, cwd=str(ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=1500)
    say(done.stdout)
    say(f"runner exit code {done.returncode}")


try:
    call("baseline", 999, "test_delete")
    call("G-450,G-600,G-le,G-kbd-delete-open,P-kbd-click-passes,G-bubble", 999, "test_delete")
    call("P-kbd-click-passes,G-bubble", 999)
finally:
    (HERE / "mutants_output.txt").write_text("\n".join(LOG), encoding="utf-8")
