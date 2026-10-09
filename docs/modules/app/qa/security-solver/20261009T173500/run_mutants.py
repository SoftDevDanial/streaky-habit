"""Runs the code-review finder's mutant runner `mut.py` with this round's mutants (mutants_security.py next to this file).

usage: python -B run_mutants.py <project root> <baseline | all | id,id,...> <maxfail> [<pytest -k expression>]

mut.py serves the project from memory-patched responses on a free 127.0.0.1 port, runs the browser suite
against it as a child process and stops the server. It writes no file and kills a hung child by the PID it
started. The project root is served as it stands, so the mutants apply to the working tree.
"""
import pathlib
import runpy
import sys

HERE = pathlib.Path(__file__).resolve().parent
REVIEW = HERE.parent.parent / "code-review" / "20261009-154715"
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REVIEW))

import mutants  # noqa: E402  (the reviewer's module: mut.py does `from mutants import MUTANTS`)
import mutants_security  # noqa: E402

mutants.MUTANTS[:] = mutants_security.MUTANTS
sys.argv = [str(REVIEW / "mut.py"), *sys.argv[1:]]
runpy.run_path(str(REVIEW / "mut.py"), run_name="__main__")
