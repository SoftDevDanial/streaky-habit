"""Runs the first review's mutant runner `mut.py` with the re-check's four extra mutants (mutants_recheck.py, next to this file)
against test_delete, and saves its output as extra_mutants_output.txt next to itself.

usage: python -B run_extra_mutants.py <project root>
mut.py serves the project root from memory-patched responses on a free 127.0.0.1 port, runs the browser suite against it as a
child process and stops the server. It writes no file, and src/ is never touched. This script waits for the child.
"""
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = pathlib.Path(sys.argv[1]).resolve()
REVIEW = HERE.parent.parent / "code-review" / "20261009-154715"

# mut.py does `from mutants import MUTANTS`; this stub module hands it the re-check's list.
DRIVER = f"""
import runpy, sys
sys.dont_write_bytecode = True
sys.path.insert(0, {str(HERE)!r})
sys.path.insert(0, {str(REVIEW)!r})
import mutants, mutants_recheck
mutants.MUTANTS[:] = mutants_recheck.MUTANTS
sys.argv = [{str(REVIEW / 'mut.py')!r}, {str(ROOT)!r}, "all", "999", "test_delete"]
runpy.run_path({str(REVIEW / 'mut.py')!r}, run_name="__main__")
"""

done = subprocess.run([sys.executable, "-B", "-c", DRIVER], cwd=str(ROOT), text=True, stdout=subprocess.PIPE,
                      stderr=subprocess.STDOUT, timeout=1200)
print(done.stdout, flush=True)
print(f"runner exit code {done.returncode}", flush=True)
(HERE / "extra_mutants_output.txt").write_text(done.stdout + f"\nrunner exit code {done.returncode}\n", encoding="utf-8")
