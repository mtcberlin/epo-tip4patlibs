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
  * `from module import name`        -> `name` is defined in `module`
  * `module.name`, `alias.name`,
    `package.submodule.name`         -> `name` is defined there
  * a bare `name` in a file that
    does `from module import *`      -> the file or `module` defines it
  * `__all__` of a module            -> every listed name is defined (else `import *` fails)
  * every code cell                  -> the guard can read it; a cell it cannot read fails
`module` is one of the course's own, tracked in git: `<module>.py` or `<module>/__init__.py`
beside the file, in a folder directly below it, or in a folder above it.

What it does not see, so a green result is not a test run:
  * attributes of objects (`kit.Answer.label`) and whether a function still behaves;
  * a module of ours that is missing altogether: it looks like a third-party package. The
    search is also wider than Python's own, so a module that exists but is not on `sys.path`
    passes;
  * a name whose binding it cannot follow: one that is a module in one branch and something
    else in another, one a function rebinds through `global`, or a module that builds its
    names at run time (`globals()`, `__getattr__`, a third-party `import *`);
  * the body of a cell magic other than `%%time`, `%%timeit`, `%%capture`, `%%prun`.
Only running the notebook on TIP shows that it works.

    python3 .github/scripts/check_notebook_refs.py
"""

from __future__ import annotations

import ast
import builtins
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKIP = ("9_misc/legacy/",)  # archived worked examples, kept as a record and not maintained
TRACKED: set[Path] = set()  # the tracked .py files: an untracked folder never resolves

PYTHON_CELL_MAGICS = {"time", "timeit", "capture", "prun"}  # the cell below them is Python
PYTHON_LINE_MAGICS = {"time", "timeit", "prun"}  # `%time expr`: the rest of the line is Python
NAMESPACE_MAGICS = {"run", "pylab", "load", "store"}  # bring names in that nobody can see here
GIVEN = set(dir(builtins)) | {"display", "get_ipython", "In", "Out", "exit", "quit", "_", "__", "___"}
SCOPES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)
COMPREHENSIONS = (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)


def bindings(nodes: list[ast.AST]) -> list[tuple[str, ast.AST]]:
    """(name, the node that binds it) for one scope; nested scopes are not entered."""
    found: list[tuple[str, ast.AST]] = []
    stack = list(reversed(nodes))
    while stack:
        node = stack.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            found.append((node.name, node))
            continue
        if isinstance(node, (ast.Lambda, *COMPREHENSIONS)):
            continue
        if isinstance(node, ast.Import):
            found += [(a.asname or a.name.split(".")[0], node) for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            found += [(a.asname or a.name, node) for a in node.names]
        elif isinstance(node, ast.Name) and not isinstance(node.ctx, ast.Load):
            found.append((node.id, node))
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            found += [(n, node) for n in node.names]
        elif isinstance(node, ast.ExceptHandler) and node.name:
            found.append((node.name, node))
        elif isinstance(node, (ast.MatchAs, ast.MatchStar)) and node.name:
            found.append((node.name, node))
        elif isinstance(node, ast.MatchMapping) and node.rest:
            found.append((node.rest, node))
        stack.extend(reversed(list(ast.iter_child_nodes(node))))
    return found


def literal_names(node: ast.AST) -> list[str] | None:
    if isinstance(node, (ast.List, ast.Tuple)) and all(
        isinstance(e, ast.Constant) and isinstance(e.value, str) for e in node.elts
    ):
        return [e.value for e in node.elts]
    return None


class Module:
    """What a module defines at top level, read from its source."""

    def __init__(self, path: Path):
        _cache[path] = self  # before reading on: two modules may star-import each other
        self.path = path
        self.package_dir = path.parent if path.name == "__init__.py" else None
        self.names: set[str] = set()
        self.exported: list[str] | None = None  # a literal __all__
        self.open = False  # defines names that cannot be read off the source
        self._stars: list[Module] = []
        try:
            self.tree = ast.parse(path.read_bytes(), str(path))
        except (SyntaxError, ValueError, OSError):  # reported by check_course.py's compile rule
            self.tree, self.open = ast.Module(body=[], type_ignores=[]), True
        dynamic_all = False
        for name, node in bindings(self.tree.body):
            if isinstance(node, (ast.Global, ast.Nonlocal)):
                continue
            if name == "*":
                source = find_module(node.module or "", self.dirs(node.level), node.level)
                if source is None:
                    self.open = True
                else:
                    self._stars.append(source)
                continue
            self.names.add(name)
            if name == "__getattr__":
                self.open = True
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Global):  # `global x` in a function binds a module name
                self.names.update(node.names)
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in ("globals", "locals") or (node.func.id == "vars" and not node.args):
                    self.open = True
            elif isinstance(node, ast.Attribute) and node.attr == "modules":
                self.open = True  # sys.modules[__name__].x = ...
            elif isinstance(node, ast.Name) and node.id == "__all__" and isinstance(node.ctx, ast.Load):
                dynamic_all = True  # __all__.append(...), __all__ + [...]
        for node in self.tree.body:
            target = getattr(node, "target", None) or (node.targets[0] if isinstance(node, ast.Assign) else None)
            if not (isinstance(target, ast.Name) and target.id == "__all__"):
                continue
            names = literal_names(node.value) if getattr(node, "value", None) is not None else None
            if names is None:
                dynamic_all = True
            elif isinstance(node, ast.AugAssign):
                self.exported = (self.exported or []) + names
            else:
                self.exported = names
        if dynamic_all:
            self.exported = None

    def dirs(self, level: int) -> list[Path]:
        if not level:
            return search_dirs(self.path.parent)
        base = self.path.parent
        for _ in range(level - 1):
            base = base.parent
        return [base]

    def _all_names(self, seen: set[Path]) -> tuple[set[str], bool]:
        if self.path in seen:
            return set(), False
        seen.add(self.path)
        names, is_open = set(self.names), self.open
        for source in self._stars:
            more, source_open = source._star(seen)
            names |= more
            is_open = is_open or source_open
        return names, is_open

    def _star(self, seen: set[Path]) -> tuple[set[str], bool]:
        names, is_open = self._all_names(seen)
        if self.exported is not None:
            return set(self.exported), is_open
        return {n for n in names if not n.startswith("_")}, is_open

    def star_names(self) -> set[str]:
        return self._star(set())[0]

    def is_open(self) -> bool:
        return self._all_names(set())[1]

    def submodule(self, name: str) -> "Module | None":
        return load(self.package_dir, name) if self.package_dir else None

    def has(self, name: str) -> bool:
        names, is_open = self._all_names(set())
        return is_open or name in names or self.submodule(name) is not None


_cache: dict[Path, Module] = {}


def load(directory: Path, name: str) -> Module | None:
    for path in (directory / name / "__init__.py", directory / f"{name}.py"):
        if path in TRACKED and path.is_file():
            return _cache.get(path) or Module(path)
    return None


def search_dirs(directory: Path) -> list[Path]:
    """Where a file in `directory` finds the course's modules: beside it, one folder below
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
    for i, directory in enumerate(dirs):
        if i and not level and parts[0] in sys.stdlib_module_names:
            continue  # only a file right beside the importer shadows the standard library
        module = load(directory, parts[0])
        for part in parts[1:]:
            module = module.submodule(part) if module else None
        if module:
            return module
    return None


ASSIGNED_MAGIC = re.compile(r"^(\s*)([A-Za-z_][\w, ]*?)\s*=\s*[%!].*$")
HELP = re.compile(r"^\s*(\?{1,2}\s*[\w.]+|[\w.]+\s*\?{1,2})\s*$")


def cell_source(source: str) -> tuple[str | None, bool]:
    """A cell as plain Python (None: not Python), and whether it pulls in unseen names."""
    lines, unseen = source.split("\n"), False
    first = next((i for i, line in enumerate(lines) if line.strip()), None)
    if first is not None and lines[first].lstrip().startswith("%%"):
        magic = lines[first].lstrip()[2:].split(" ")[0].strip()
        if magic not in PYTHON_CELL_MAGICS:
            return None, False
        lines[first] = ""
    out, continued = [], False
    for line in lines:
        indent, text = line[: len(line) - len(line.lstrip())], line.strip()
        if continued:  # the rest of a `!command \` that runs over several lines
            continued = text.endswith("\\")
            out.append("")
        elif text[:1] == "!" or HELP.match(line):
            continued = text[:1] == "!" and text.endswith("\\")
            out.append(indent + "pass")
        elif text[:1] == "%":
            magic, _, rest = text[1:].partition(" ")
            unseen = unseen or magic in NAMESPACE_MAGICS
            keep = rest if magic in PYTHON_LINE_MAGICS and not rest.lstrip().startswith("-") else ""
            out.append(indent + (keep.strip() or "pass"))
        elif ASSIGNED_MAGIC.match(line):
            out.append(ASSIGNED_MAGIC.sub(r"\1\2 = None", line))
        else:
            out.append(line)
    return "\n".join(out), unseen


def notebook_code(path: Path, label: str) -> tuple[list[ast.AST], list[str], bool]:
    """The trees of the code cells, the cells that cannot be read, and the unseen-names flag."""
    trees: list[ast.AST] = []
    errors: list[str] = []
    unseen = False
    cells = json.loads(path.read_text(encoding="utf-8"))["cells"]
    for number, cell in enumerate(cells):
        if cell.get("cell_type") != "code":
            continue
        source = cell.get("source") or ""
        python, cell_unseen = cell_source(source if isinstance(source, str) else "".join(source))
        unseen = unseen or cell_unseen
        if python is None:
            continue
        try:
            flags = ast.PyCF_ONLY_AST | ast.PyCF_ALLOW_TOP_LEVEL_AWAIT
            trees.append(compile(python, label, "exec", flags=flags))
        except (SyntaxError, ValueError) as e:
            errors.append(
                f"{label}: cell {number} cannot be read by the reference guard "
                f"(line {getattr(e, 'lineno', '?')}: {getattr(e, 'msg', e)}); teach "
                "check_notebook_refs.py the syntax rather than leaving the cell unchecked"
            )
    return trees, errors, unseen


class Checker(ast.NodeVisitor):
    """Walks one file in source order and resolves what it takes from the course's modules."""

    def __init__(self, label: str, trees: list[ast.AST], dirs: list[Path], package_dir: Path | None, unseen: bool):
        self.label, self.dirs, self.package_dir = label, dirs, package_dir
        self.errors: list[str] = []
        self.scopes: list[tuple[str, dict[str, Module | None]]] = [("module", {})]
        self.untraceable: set[str] = set()  # rebound through `global` inside a function
        self.guards: list[set[tuple[str, str]]] = []
        self.set_here: set[tuple[str, str]] = set()  # `kit.x = ...` anywhere in the file
        self.stars: list[tuple[str, Module]] = []
        self.unseen = unseen
        self.loads: set[str] = set()
        self.bound: set[str] = set()
        for node in (n for tree in trees for n in ast.walk(tree)):
            if isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Store):
                self.set_here.add((ast.unparse(node.value), node.attr))
            elif isinstance(node, ast.arg):
                self.bound.add(node.arg)
            elif self._call(node, "setattr"):
                self.set_here.add((ast.unparse(node.args[0]), node.args[1].value))
        for tree in trees:
            self.bound.update(name for name, _ in bindings([tree]))
            for node in ast.walk(tree):
                if isinstance(node, (*SCOPES, *COMPREHENSIONS)):
                    self.bound.update(name for name, _ in bindings(list(ast.iter_child_nodes(node))))
        for tree in trees:
            self.visit(tree)
        self._bare_names()

    @staticmethod
    def _call(node: ast.AST, name: str) -> bool:
        return (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == name
            and len(node.args) >= 2
            and isinstance(node.args[1], ast.Constant)
            and isinstance(node.args[1].value, str)
        )

    # -- names ------------------------------------------------------------------------------
    def lookup(self, name: str) -> Module | None:
        if name in self.untraceable:
            return None
        for i in range(len(self.scopes) - 1, -1, -1):
            kind, names = self.scopes[i]
            if kind == "class" and i != len(self.scopes) - 1:
                continue  # a class body is not visible from its methods
            if name in names:
                return names[name]
        return None

    def bind(self, name: str, value: Module | None) -> None:
        if len(self.scopes) == 1:  # module level runs top to bottom; inner scopes are precomputed
            self.scopes[0][1][name] = value

    def resolve(self, node: ast.AST) -> Module | None:
        if isinstance(node, ast.Name):
            return self.lookup(node.id)
        if isinstance(node, ast.Attribute):
            base = self.resolve(node.value)
            return base.submodule(node.attr) if base else None
        return None

    def imported(self, node: ast.Import | ast.ImportFrom, report: bool) -> list[tuple[str, Module | None]]:
        """What an import statement binds; with `report`, also what it asks for in vain."""
        bound: list[tuple[str, Module | None]] = []
        if isinstance(node, ast.Import):
            for a in node.names:
                top = a.name.split(".")[0]
                whole = find_module(a.name, self.dirs)
                if report and whole is None and "." in a.name and find_module(top, self.dirs):
                    self.errors.append(f"{self.label}: `import {a.name}` — no such module in the course")
                bound.append((a.asname or top, whole if a.asname else find_module(top, self.dirs)))
            return bound
        if node.level:
            if self.package_dir is None:
                return [(a.asname or a.name, None) for a in node.names if a.name != "*"]
            base = self.package_dir
            for _ in range(node.level - 1):
                base = base.parent
            module = find_module(node.module or "", [base], node.level)
        else:
            module = find_module(node.module or "", self.dirs)
        shown = "." * node.level + (node.module or "")
        for a in node.names:
            if a.name == "*":
                if report:
                    if module is None:
                        self.unseen = True
                    else:
                        self.stars.append((shown, module))
                continue
            if module is None:
                bound.append((a.asname or a.name, None))
                continue
            bound.append((a.asname or a.name, module.submodule(a.name)))
            if report and not module.has(a.name):
                self.errors.append(
                    f"{self.label}: `from {shown} import {a.name}` — "
                    f"{module.path.relative_to(ROOT)} defines no `{a.name}`"
                )
        return bound

    def inner_scope(self, body: list[ast.AST], params: list[str]) -> dict[str, Module | None]:
        names: dict[str, Module | None] = {p: None for p in params}
        outer: set[str] = set()
        for name, node in bindings(body):
            if isinstance(node, (ast.Global, ast.Nonlocal)):
                outer.add(name)
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                value = dict(self.imported(node, report=False)).get(name)
                names[name] = value if names.get(name, value) is value else None
            elif name != "*":
                names[name] = None
        for name in outer:
            if name in names:
                self.untraceable.add(name)
                del names[name]
        return names

    # -- statements that bind ---------------------------------------------------------------
    def visit_Import(self, node: ast.Import) -> None:
        for name, value in self.imported(node, report=True):
            self.bind(name, value)

    visit_ImportFrom = visit_Import

    def visit_Assign(self, node: ast.Assign) -> None:
        self.visit(node.value)
        module = self.resolve(node.value)
        for target in node.targets:
            if module and isinstance(target, ast.Name):
                self.bind(target.id, module)  # `k = kit`
            else:
                self.visit(target)

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, ast.Load):
            self.loads.add(node.id)
        else:
            self.bind(node.id, None)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        if node.name:
            self.bind(node.name, None)
        self.generic_visit(node)

    def visit_MatchAs(self, node: ast.AST) -> None:
        name = getattr(node, "name", None) or getattr(node, "rest", None)
        if name:
            self.bind(name, None)
        self.generic_visit(node)

    visit_MatchStar = visit_MatchMapping = visit_MatchAs

    # -- scopes -----------------------------------------------------------------------------
    def _enter(self, kind: str, names: dict[str, Module | None], body: list[ast.AST]) -> None:
        self.scopes.append((kind, names))
        for child in body:
            self.visit(child)
        self.scopes.pop()

    def visit_FunctionDef(self, node: ast.AST) -> None:
        args = node.args
        for outside in [*getattr(node, "decorator_list", []), *args.defaults, *args.kw_defaults]:
            if outside is not None:
                self.visit(outside)
        if hasattr(node, "name"):
            self.bind(node.name, None)
        params = [a.arg for a in [*args.posonlyargs, *args.args, *args.kwonlyargs, args.vararg, args.kwarg] if a]
        body = node.body if isinstance(node.body, list) else [node.body]
        self._enter("function", self.inner_scope(body, params), body)

    visit_AsyncFunctionDef = visit_Lambda = visit_FunctionDef

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        for outside in [*node.decorator_list, *node.bases, *node.keywords]:
            self.visit(outside)
        self.bind(node.name, None)
        self._enter("class", self.inner_scope(node.body, []), node.body)

    def visit_ListComp(self, node: ast.AST) -> None:
        children = list(ast.iter_child_nodes(node))
        targets = [n for g in node.generators for n in ast.walk(g.target) if isinstance(n, ast.Name)]
        self._enter("function", {n.id: None for n in targets}, children)

    visit_SetComp = visit_DictComp = visit_GeneratorExp = visit_ListComp

    # -- guards: `if hasattr(kit, "x"): kit.x` ----------------------------------------------
    def _guarded(self, test: ast.AST, inside: list[ast.AST]) -> None:
        self.guards.append(
            {(ast.unparse(n.args[0]), n.args[1].value) for n in ast.walk(test) if self._call(n, "hasattr")}
        )
        for child in inside:
            self.visit(child)
        self.guards.pop()

    def visit_If(self, node: ast.AST) -> None:
        body = node.body if isinstance(node.body, list) else [node.body]
        orelse = node.orelse if isinstance(node.orelse, list) else [node.orelse]
        self._guarded(node.test, [node.test, *body])
        for child in orelse:
            self.visit(child)

    visit_IfExp = visit_While = visit_If

    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        if isinstance(node.op, ast.And):
            self._guarded(node, node.values)
        else:
            self.generic_visit(node)

    # -- the check --------------------------------------------------------------------------
    def visit_Attribute(self, node: ast.Attribute) -> None:
        self.visit(node.value)
        module = self.resolve(node.value)
        if module is None or isinstance(node.ctx, ast.Store) or node.attr.startswith("__"):
            return
        key = (ast.unparse(node.value), node.attr)
        if key in self.set_here or any(key in g for g in self.guards) or module.has(node.attr):
            return
        self.errors.append(
            f"{self.label}: uses `{key[0]}.{node.attr}` — "
            f"{module.path.relative_to(ROOT)} defines no `{node.attr}`"
        )

    def _bare_names(self) -> None:
        if not self.stars or self.unseen or any(m.is_open() for _, m in self.stars):
            return
        provided = set().union(*(m.star_names() for _, m in self.stars))
        sources = ", ".join(sorted({shown for shown, _ in self.stars}))
        for name in sorted(self.loads - self.bound - provided - GIVEN):
            if not (name.startswith("__") and name.endswith("__")):
                self.errors.append(
                    f"{self.label}: uses `{name}` — neither this file nor `from {sources} import *` defines it"
                )


def problems(root: Path = ROOT) -> list[str]:
    global ROOT, TRACKED
    ROOT = root.resolve()
    _cache.clear()
    out = subprocess.check_output(["git", "ls-files", "-z", "--", "*.ipynb", "*.py"], cwd=ROOT, text=True)
    files = sorted(p for p in out.split("\0") if p and (ROOT / p).is_file())
    TRACKED = {ROOT / p for p in files if p.endswith(".py")}
    errors: list[str] = []
    for f in files:
        if f.startswith(SKIP):
            continue
        path = ROOT / f
        if f.endswith(".ipynb"):
            try:
                trees, unreadable, unseen = notebook_code(path, f)
            except (ValueError, KeyError, TypeError, AttributeError) as e:
                errors.append(f"{f}: not a notebook the reference guard can read ({type(e).__name__}: {e})")
                continue
            errors += unreadable
            errors += Checker(f, trees, search_dirs(path.parent), None, unseen).errors
            continue
        module = _cache.get(path) or Module(path)
        for name in module.exported or []:
            if not module.has(name):
                errors.append(f"{f}: `__all__` lists `{name}`, which the module does not define")
        errors += Checker(f, [module.tree], search_dirs(path.parent), path.parent, False).errors
    return list(dict.fromkeys(errors))


if __name__ == "__main__":
    found = problems()
    for e in found:
        print("FAIL", e)
    print(f"{len(found)} problem(s)" if found else "notebook references resolve")
    sys.exit(1 if found else 0)
