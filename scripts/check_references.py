"""Check that every class and constant used in the skill's Python code blocks exists in manimlib.

    python scripts/check_references.py

Parses each ```python block in SKILL.md and references/*.md and reports every
capitalized name (class or constant) that the file's blocks do not define
themselves and that is neither a builtin nor exported by `from manimlib import *`.
SKILL.md's "These CE names do not exist in manimlib" list is checked the other way:
each name must still be absent. Exit code 1 on any problem, so a manimgl upgrade
that renames, removes or adds such an API fails loudly.

shortcut: lowercase names are skipped because snippets use placeholder variables
(`mob`, `axes`), so bare functions, methods and kwargs are not checked; add
attribute checks if a method rename slips through.
"""

import ast
import builtins
import pathlib
import re
import sys
import warnings

SKILL = pathlib.Path(__file__).resolve().parent.parent / "skills" / "manimgl-video"
BLOCK = re.compile(r"^```python\n(.*?)^```", re.S | re.M)
# SKILL.md's list of Manim CE names; each must stay absent from manimlib.
CE_LIST = re.compile(r"\*\*These CE names do not exist in manimlib\*\*(.*?)\n\n", re.S)


def names(src):
    """(names the block defines, {capitalized name it reads: first line})"""
    defined, used = set(), {}
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Name):
            if not isinstance(node.ctx, ast.Load):
                defined.add(node.id)
            elif node.id[0].isupper():
                used.setdefault(node.id, node.lineno)
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
            defined.add(node.name)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            defined.update((a.asname or a.name).split(".")[0] for a in node.names)
    return defined, used


def main():
    warnings.filterwarnings("ignore")
    sys.argv = ["manimgl"]  # manimlib parses CLI args at import
    ns = {}
    exec("from manimlib import *", ns)
    import manimlib
    known = set(ns) | set(dir(builtins))

    ce = CE_LIST.search((SKILL / "SKILL.md").read_text(encoding="utf-8"))
    ce_names = re.findall(r"`(\w+)`", ce.group(1)) if ce else []
    problems = 0 if ce_names else 1
    if not ce_names:
        print("SKILL.md: CE-only name list not found")
    for name in ce_names:
        if name in ns:
            print(f"SKILL.md: CE-only `{name}` now exists in manimlib; fix the list")
            problems += 1

    files = [SKILL / "SKILL.md", *sorted((SKILL / "references").glob("*.md"))]
    for path in files:
        text = path.read_text(encoding="utf-8")
        defined, used = set(), []  # snippets in one file share definitions (e.g. constants set up earlier)
        for m in BLOCK.finditer(text):
            block_line = text.count("\n", 0, m.start()) + 2
            try:
                d, u = names(m.group(1))
            except SyntaxError as e:
                print(f"{path.name}:{block_line + (e.lineno or 1) - 1}: unparsable block: {e.msg}")
                problems += 1
                continue
            defined |= d
            used += [(block_line + ln - 1, n) for n, ln in u.items()]
        for line, name in sorted(used):
            if name not in defined and name not in known:
                print(f"{path.name}:{line}: `{name}` is not exported by manimlib")
                problems += 1
    print(f"manimlib {getattr(manimlib, '__version__', '?')}: {problems} problem(s) in {len(files)} files")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
