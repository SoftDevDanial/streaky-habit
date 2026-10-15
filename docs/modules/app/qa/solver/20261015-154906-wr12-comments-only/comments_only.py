"""Proves a change touched comments, plus the one allowed docstring, and no code.

Usage: python -B comments_only.py <before-rev> <after: WORKTREE or a rev> [<out-folder relative to the project root>]

Compares each file's code between <before-rev> and the after side three ways:
  1. ast.dump with every docstring replaced by `pass` (a comment never reaches the AST);
  2. the token stream with COMMENT, NL and docstring tokens left out (catches a changed literal, a name, a spacing of
     code that the AST would normalise);
  3. the docstrings, by qualified name: only the names in ALLOWED_DOCSTRING_CHANGES may differ.
Then three controls prove the check can fail: one token of code changed, one docstring changed that is not allowed,
and (the opposite direction) a comment added, which must stay equal. The before side is run against itself first.
Writes comments-only.txt and word-diff.txt into the out folder (relative path, the project root is the cwd).
"""
import ast
import io
import os
import subprocess
import sys
import tokenize

ROOT = "{workspace}/examples/streaks"
FILES = [
    "tests/browser/conftest.py",
    "tests/browser/test_day_editor.py",
    "tests/browser/test_overview.py",
    "tests/browser/test_year.py",
    "tests/browser/test_popups.py",
]
ALLOWED_DOCSTRING_CHANGES = {"tests/browser/conftest.py": {"watch_close"}}


def git_show(rev, path):
    out = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True, check=True, timeout=60).stdout
    return out.decode("utf-8").replace("\r\n", "\n")


def worktree(path):
    with open(path, "rb") as handle:
        return handle.read().decode("utf-8").replace("\r\n", "\n")


def load(side, path):
    return worktree(path) if side == "WORKTREE" else git_show(side, path)


def docstring_nodes(tree):
    """(qualified name, the docstring Expr node) for the module and every class and function."""
    found = []

    def walk(node, prefix):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                name = f"{prefix}{child.name}"
                first = child.body[0] if child.body else None
                if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
                    found.append((name, first))
                walk(child, name + ".")
            else:
                walk(child, prefix)

    first = tree.body[0] if tree.body else None
    if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
        found.append(("<module>", first))
    walk(tree, "")
    return found


def analyse(source):
    tree = ast.parse(source)
    nodes = docstring_nodes(tree)
    docstrings = {name: node.value.value for name, node in nodes}
    spans = [(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset) for _, node in nodes]
    for _, node in nodes:  # the docstring becomes `pass` so only code is left in the dump
        node.value = ast.Constant(value=None)
    dump = ast.dump(tree)

    def inside(position):
        row, col = position
        return any((s[0], s[1]) <= (row, col) < (s[2], s[3]) for s in spans)

    tokens = []
    for tok in tokenize.generate_tokens(io.StringIO(source).readline):
        if tok.type in (tokenize.COMMENT, tokenize.NL):
            continue
        if inside(tok.start):
            continue
        tokens.append((tok.type, tok.string))
    return dump, tokens, docstrings


def compare(path, before_src, after_src):
    b_dump, b_tokens, b_docs = analyse(before_src)
    a_dump, a_tokens, a_docs = analyse(after_src)
    docs_changed = sorted(name for name in set(b_docs) | set(a_docs) if b_docs.get(name) != a_docs.get(name))
    allowed = ALLOWED_DOCSTRING_CHANGES.get(path, set())
    problems = []
    if b_dump != a_dump:
        problems.append("AST differs")
    if b_tokens != a_tokens:
        problems.append("code tokens differ")
    unexpected = [name for name in docs_changed if name not in allowed]
    if unexpected:
        problems.append(f"docstring changed that is not allowed: {unexpected}")
    return problems, docs_changed


def main():
    before_rev, after_side = sys.argv[1], sys.argv[2]
    out_folder = sys.argv[3] if len(sys.argv) > 3 else None
    os.chdir(ROOT)
    lines = [f"comments-only check, before {before_rev}, after {after_side}"]
    failed = False

    for path in FILES:
        before_src, after_src = load(before_rev, path), load(after_side, path)
        problems, docs_changed = compare(path, before_src, after_src)
        verdict = "SAME CODE" if not problems else "DIFFERENT: " + "; ".join(problems)
        lines.append(f"{path}: {verdict}; docstrings changed: {docs_changed or 'none'}")
        failed = failed or bool(problems)

    lines.append("controls (each changes an in-memory copy of the before side, no file is written):")
    # Control 0: the before side against itself is equal. Control 1: one code token changed must be caught.
    path = "tests/browser/test_year.py"
    before_src = load(before_rev, path)
    problems, _ = compare(path, before_src, before_src)
    lines.append(f"  C0 before against itself: {'equal' if not problems else problems}")
    failed = failed or bool(problems)

    mutated = before_src.replace("page.mouse.click(5, 5)", "page.mouse.click(6, 5)", 1)
    assert mutated != before_src
    problems, _ = compare(path, before_src, mutated)
    lines.append(f"  C1 one code token changed (click(5, 5) to click(6, 5)): {'CAUGHT ' + str(problems) if problems else 'MISSED'}")
    failed = failed or not problems

    # Control 2: a docstring changed anywhere but the allowed name must be caught.
    path = "tests/browser/conftest.py"
    before_src = load(before_rev, path)
    mutated = before_src.replace("Fails after `seconds`.", "Fails after `seconds` (changed).", 1)
    assert mutated != before_src
    problems, docs_changed = compare(path, before_src, mutated)
    lines.append(f"  C2 the docstring of wait_for_close changed: {'CAUGHT ' + str(problems) if problems else 'MISSED'}")
    failed = failed or not problems

    # Control 3: a comment added, a comment removed and a comment reworded are all invisible to the check.
    path = "tests/browser/test_popups.py"
    before_src = load(before_rev, path)
    mutated = before_src.replace("wait_closed(page, top)\n", "wait_closed(page, top)  # a new comment\n", 1)
    assert mutated != before_src
    problems, _ = compare(path, before_src, mutated)
    lines.append(f"  C3 a comment added: {'equal, as it must be' if not problems else 'WRONGLY FLAGGED ' + str(problems)}")
    failed = failed or bool(problems)

    lines.append("RESULT: " + ("FAIL" if failed else "PASS, comments and the watch_close docstring only"))
    text = "\n".join(lines) + "\n"
    print(text)

    if out_folder:
        diff_cmd = ["git", "diff", "--word-diff", before_rev]
        if after_side != "WORKTREE":
            diff_cmd.append(after_side)
        diff_cmd += ["--"] + FILES
        diff = subprocess.run(diff_cmd, capture_output=True, check=True, timeout=60).stdout.decode("utf-8", "replace")
        os.makedirs(out_folder, exist_ok=False)
        with open(os.path.join(out_folder, "comments-only.txt"), "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        with open(os.path.join(out_folder, "word-diff.txt"), "w", encoding="utf-8", newline="\n") as handle:
            handle.write(" ".join(diff_cmd[:3]) + "\n\n" + diff)
        print("wrote", sorted(os.listdir(out_folder)))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
