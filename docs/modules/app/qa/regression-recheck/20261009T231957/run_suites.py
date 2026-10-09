"""Runs the two suites once each, as the README gives them, and saves the tail of each output.

usage: python -B run_suites.py <project root>
  node --test "tests/**/*.test.js"                      (README: 99 expected)
  python -m pytest tests/browser -q -p no:cacheprovider   (README: 179 expected; conftest starts and stops its own two servers)
Each child is waited for. The script prints and saves the same text as suites_output.txt next to itself. It writes no other file.
"""
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = pathlib.Path(sys.argv[1]).resolve()
LOG = []


def say(text=""):
    print(text, flush=True)
    LOG.append(text)


def run(title, command):
    say(f"=== {title}")
    say("$ " + " ".join(command))
    done = subprocess.run(command, cwd=str(ROOT), text=True, encoding="utf-8", errors="replace",
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=900,
                          env={**__import__("os").environ, "PYTHONDONTWRITEBYTECODE": "1"})
    lines = [line for line in done.stdout.splitlines() if line.strip()]
    for line in lines[-14:]:
        say("   " + line)
    say(f"exit code {done.returncode}")
    say()


try:
    run("unit tests", ["node", "--test", "tests/**/*.test.js"])
    run("browser tests", [sys.executable, "-B", "-m", "pytest", "tests/browser", "-q", "-p", "no:cacheprovider"])
finally:
    (HERE / "suites_output.txt").write_text("\n".join(LOG) + "\n", encoding="utf-8")
