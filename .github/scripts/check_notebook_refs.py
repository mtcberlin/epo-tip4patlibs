#!/usr/bin/env python3
"""Every name a notebook takes from the course's own modules exists in that module.

The notebooks ship pre-executed, so a stored output proves nothing about today's code. On
17 September 2026 a merge moved a notebook and left `ipscore_kit.save_questionnaire` behind;
the notebook still looked fine and failed with `AttributeError` once a participant had
answered all forty questions. This check reads the files and would have failed that merge.

It reads, it never imports or runs: standard library only, so it also covers the notebooks
whose modules need `epo.tipdata` and import nowhere but on TIP, and it never executes guest
material.

What it checks, for every tracked notebook and `.py` file outside `9_misc/legacy/`:
  * `from module import name`      -> `name` is defined in `module`
  * `module.name` / `alias.name`   -> `name` is defined in `module`
  * `__all__` of a module          -> every listed name is defined (else `import *` fails)
`module` is one of the course's own: `<module>.py` or `<module>/__init__.py` beside the
notebook, in a folder directly below it, or in a folder above it.

What it cannot see: names used bare after `from module import *`, attributes of objects
(`kit.Answer.label`), a module of ours that is missing altogether (it then looks like a
third-party package), and whether a function still behaves. It is a guard against a missing
callee, not a test run; only running the notebook on TIP shows that it works.

    python3 .github/scripts/check_notebook_refs.py
"""

from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKIP = ("9_misc/legacy/",)  # archived worked examples, kept as a record and not maintained


class Module:
    """What a module defines at top level, read from its source."""

    def __init__(self, path: Path):
        self.path = path
        self.package_dir = path.parent if path.name == "__init__.py" else None
        self.names: set[str] = set()
        self.exported: list[str] | None = None  # a literal __all__
        self.open = False  # defines names we cannot see: __getattr__, or a foreign `import *`
        try:
            self.tree = ast.parse(path.read_bytes(), str(path))
        except SyntaxError:  # reported by check_course.py's compile rule
            self.tree, self.open = ast.Module(body=[], type_ignores=[]), True
        self._collect(self.tree.body)
        for node in ast.walk(self.tree):  # `global x` in a function binds a module name
            if isinstance(node, ast.Global):
                self.names.update(node.names)

    def _collect(self, body: list[ast.stmt]) -> None:
        for node in body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                self.names.add(node.name)
                if node.name == "__getattr__":
                    self.open = True
            elif isinstance(node, ast.Import):
                self.names.update((a.asname or a.name.split(".")[0]) for a in node.names)
            elif isinstance(node, ast.ImportFrom):
                for a in node.names:
                    if a.name != "*":
                        self.names.add(a.asname or a.name)
                        continue
                    source = find_module(node.module or "", self._dirs(node.level), node.level)
                    if source is None:
                        self.open = True
                    else:
                        self.names.update(source.star_names())
                        self.open = self.open or source.open
            else:
                for target in ast.walk(node):  # assignments, also inside if/try/with/for
                    if isinstance(target, ast.Name) and isinstance(target.ctx, ast.Store):
                        self.names.add(target.id)
                    elif isinstance(target, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                        self.names.add(target.name)
                    elif isinstance(target, (ast.Import, ast.ImportFrom)):
                        self._collect([target])
                if (
                    isinstance(node, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets)
                    and isinstance(node.value, (ast.List, ast.Tuple))
                    and all(isinstance(e, ast.Constant) for e in node.value.elts)
                ):
                    self.exported = [e.value for e in node.value.elts]

    def _dirs(self, level: int) -> list[Path]:
        if level:
            base = self.path.parent
            for _ in range(level - 1):
                base = base.parent
            return [base]
        return search_dirs(self.path.parent)

    def star_names(self) -> set[str]:
        if self.exported is not None:
            return set(self.exported)
        return {n for n in self.names if not n.startswith("_")}

    def submodule(self, name: str) -> "Module | None":
        return load(self.package_dir, name) if self.package_dir else None

    def has(self, name: str) -> bool:
        return self.open or name in self.names or self.submodule(name) is not None


_cache: dict[Path, Module] = {}


def load(directory: Path, name: str) -> Module | None:
    for path in (directory / f"{name}.py", directory / name / "__init__.py"):
        if path.is_file():
            if path not in _cache:
                _cache[path] = Module(path)
            return _cache[path]
    return None


def search_dirs(directory: Path) -> list[Path]:
    """Where a notebook in `directory` finds its own modules: beside it, one folder below
    (the `sys.path.insert` case), then every folder above up to the repository root."""
    dirs = [directory]
    dirs += sorted(d for d in directory.iterdir() if d.is_dir() and not d.name.startswith("."))
    parent = directory
    while parent != ROOT and ROOT in parent.parents:
        parent = parent.parent
        dirs.append(parent)
    return dirs


def find_module(dotted: str, dirs: list[Path], level: int = 0) -> Module | None:
    """The course's own module `dotted`, or None when it is somebody else's package."""
    parts = [p for p in dotted.split(".") if p]
    if level and not parts:  # `from . import x`: the package itself
        return load(dirs[0].parent, dirs[0].name)
    for directory in dirs:
        module = load(directory, parts[0])
        for part in parts[1:]:
            module = module.submodule(part) if module else None
        if module:
            return module
    return None


def notebook_code(path: Path) -> list[ast.Module]:
    """One tree per code cell; IPython magics and shell lines are blanked out."""
    trees = []
    for cell in json.loads(path.read_text(encoding="utf-8")).get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        source = "".join(cell.get("source", []))
        if source.lstrip().startswith("%%"):
            continue
        lines = [
            line[: len(line) - len(line.lstrip())] + "pass" if line.lstrip()[:1] in ("%", "!") else line
            for line in source.split("\n")
        ]
        try:
            trees.append(ast.parse("\n".join(lines)))
        except SyntaxError:
            continue  # IPython-only syntax; nothing to resolve in it
    return trees


def problems_in(label: str, trees: list[ast.Module], dirs: list[Path], level_dir: Path | None = None) -> list[str]:
    errors: list[str] = []
    aliases: dict[str, Module] = {}
    rebound: set[str] = set()
    set_here: set[tuple[str, str]] = set()  # (alias, attribute) the file assigns itself
    guarded: set[tuple[str, str]] = set()  # hasattr(alias, "attribute")
    nodes = [n for tree in trees for n in ast.walk(tree)]

    for node in nodes:
        if isinstance(node, ast.Import):
            for a in node.names:
                module = find_module(a.name if a.asname else a.name.split(".")[0], dirs)
                if module:
                    aliases[a.asname or a.name.split(".")[0]] = module
        elif isinstance(node, ast.ImportFrom):
            if node.level and level_dir is None:
                continue
            base = [level_dir] if node.level else dirs
            if node.level:
                for _ in range(node.level - 1):
                    base = [base[0].parent]
            module = find_module(node.module or "", base, node.level)
            if module is None:
                continue
            for a in node.names:
                if a.name == "*":
                    continue
                sub = module.submodule(a.name)
                if sub:
                    aliases[a.asname or a.name] = sub
                elif not module.has(a.name):
                    errors.append(
                        f"{label}: `from {'.' * node.level}{node.module or ''} import {a.name}` — "
                        f"{module.path.relative_to(ROOT)} defines no `{a.name}`"
                    )
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            rebound.add(node.id)
        elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            if isinstance(node.ctx, ast.Store):
                set_here.add((node.value.id, node.attr))
        elif (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in ("hasattr", "getattr", "setattr")
            and len(node.args) >= 2
            and isinstance(node.args[0], ast.Name)
            and isinstance(node.args[1], ast.Constant)
        ):
            guarded.add((node.args[0].id, node.args[1].value))

    for name in rebound:  # the name also holds something that is not the module
        aliases.pop(name, None)

    seen: set[tuple[str, str]] = set()
    for node in nodes:
        if not (isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name)):
            continue
        key = (node.value.id, node.attr)
        module = aliases.get(node.value.id)
        if module is None or key in seen or key in set_here or key in guarded:
            continue
        seen.add(key)
        if not isinstance(node.ctx, ast.Load) or node.attr.startswith("__") or module.has(node.attr):
            continue
        errors.append(
            f"{label}: uses `{node.value.id}.{node.attr}` — "
            f"{module.path.relative_to(ROOT)} defines no `{node.attr}`"
        )
    return errors


def problems(root: Path = ROOT) -> list[str]:
    global ROOT
    ROOT = root.resolve()
    _cache.clear()
    out = subprocess.check_output(["git", "ls-files", "--", "*.ipynb", "*.py"], cwd=ROOT, text=True)
    errors: list[str] = []
    for f in sorted(p for p in out.splitlines() if p and not p.startswith(SKIP)):
        path = ROOT / f
        if f.endswith(".ipynb"):
            try:
                trees = notebook_code(path)
            except (ValueError, AttributeError):
                continue  # reported by check_course.py's notebook rule
            errors += problems_in(f, trees, search_dirs(path.parent))
            continue
        module = load(path.parent, path.stem) if path.name != "__init__.py" else load(path.parent.parent, path.parent.name)
        if module is None or module.path != path:
            module = _cache.setdefault(path, Module(path))
        for name in module.exported or []:
            if not module.has(name):
                errors.append(f"{f}: `__all__` lists `{name}`, which the module does not define")
        errors += problems_in(f, [module.tree], search_dirs(path.parent), level_dir=path.parent)
    return errors


if __name__ == "__main__":
    found = problems()
    for e in found:
        print("FAIL", e)
    print(f"{len(found)} problem(s)" if found else "notebook references resolve")
    sys.exit(1 if found else 0)
