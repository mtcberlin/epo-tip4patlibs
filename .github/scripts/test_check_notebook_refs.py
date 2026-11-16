"""The reference guard bites on the defects it was written for, and stays quiet otherwise.

    python3 -m unittest discover -s .github/scripts -p 'test_*.py'
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_notebook_refs as guard  # noqa: E402

REAL_ROOT = guard.ROOT


def notebook(*cells: str) -> str:
    return json.dumps({"cells": [{"cell_type": "code", "source": [c]} for c in cells]})


class Repo:
    """A throwaway git repository with the given files tracked."""

    def __init__(self, files: dict[str, str]):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for name, text in files.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        subprocess.check_call(["git", "init", "-q"], cwd=self.root)
        subprocess.check_call(["git", "add", "-A"], cwd=self.root)

    def problems(self) -> list[str]:
        try:
            return guard.problems(self.root)
        finally:
            self.tmp.cleanup()


class GuardTest(unittest.TestCase):
    def tearDown(self) -> None:
        guard.ROOT = REAL_ROOT
        guard._cache.clear()

    def test_missing_callee_behind_an_alias(self):
        """The 17 September defect: the notebook moved, `save_questionnaire` stayed behind."""
        found = Repo({
            "5/kit.py": "def load():\n    pass\n",
            "5/0.ipynb": notebook("import kit as kit\nkit.load()", "kit.save_questionnaire({})"),
        }).problems()
        self.assertEqual(len(found), 1, found)
        self.assertIn("kit.save_questionnaire", found[0])

    def test_missing_name_in_from_import(self):
        found = Repo({
            "m/core.py": "def initialize():\n    pass\n",
            "m/1.ipynb": notebook("from core import initialize, timed_query"),
        }).problems()
        self.assertEqual(len(found), 1, found)
        self.assertIn("timed_query", found[0])

    def test_all_lists_an_undefined_name(self):
        found = Repo({"m/core.py": "__all__ = ['here', 'gone']\nhere = 1\n"}).problems()
        self.assertEqual(len(found), 1, found)
        self.assertIn("`gone`", found[0])

    def test_package_submodule_and_folder_above(self):
        """Module 3: the notebook finds `dpma/` by walking up, and imports through the package."""
        found = Repo({
            "3/dpma/__init__.py": "from . import fetch\nfrom .parse import parse_hit\n",
            "3/dpma/fetch.py": "class Client:\n    pass\n",
            "3/dpma/parse.py": "def parse_hit():\n    pass\n",
            "3/deep/2.ipynb": notebook(
                "from dpma import fetch, parse_hit\nfrom dpma.parse import parse_hit\nfetch.Client()",
                "fetch.Gone()",
            ),
        }).problems()
        self.assertEqual(len(found), 1, found)
        self.assertIn("fetch.Gone", found[0])

    def test_broken_relative_import_inside_a_package(self):
        found = Repo({
            "3/dpma/__init__.py": "from .parse import parse_hit\n",
            "3/dpma/parse.py": "def other():\n    pass\n",
        }).problems()
        self.assertEqual(len(found), 1, found)
        self.assertIn("parse_hit", found[0])

    def test_quiet_on_what_is_legitimate(self):
        found = Repo({
            "m/core.py": (
                "import os\nstate = None\ntry:\n    import fast as engine\nexcept ImportError:\n    engine = None\n"
                "def setup():\n    global widgets\n    widgets = 1\n"
            ),
            "m/build/render.py": "def main():\n    pass\n",
            "m/1.ipynb": notebook(
                "%matplotlib inline\nimport core, pandas as pd\n!ls\ncore.state = 1\ncore.made_here = 2",
                "print(core.made_here, core.engine, core.widgets, core.os, pd.DataFrame)",
                "if hasattr(core, 'results'):\n    core.results",
                "import sys\nsys.path.insert(0, 'build')\nimport render as r\nr.main()",
                "%%bash\nthis is not python",
                "x = !ls",
            ),
            "9_misc/legacy/old.ipynb": notebook("import core\ncore.gone()"),
            "9_misc/legacy/core.py": "",
        }).problems()
        self.assertEqual(found, [])

    K = "def load():\n    pass\n"

    def test_quiet_when_the_name_means_something_else_there(self):
        """A parameter, a loop variable or a later import of the same name is not the module."""
        found = Repo({
            "5/kit.py": self.K, "5/fetch.py": self.K, "5/err.py": self.K, "5/dpma/__init__.py": "",
            "5/dpma/parse.py": self.K,
            "5/1.ipynb": notebook(
                "import kit, fetch, err\nkit.load()",
                "def show(kit):\n    return kit.title",
                "f = lambda fetch: fetch.status",
                "try:\n    pass\nexcept Exception as err:\n    print(err.args)",
                "rows = [fetch.real for fetch in range(3)]",
                "from dpma import parse\nparse.load()\nfrom urllib import parse\nparse.quote('a')",
                "import pandas as kit\nkit.DataFrame",
                "class kit:\n    x = 1\nkit.x",
            ),
        }).problems()
        self.assertEqual(found, [])

    def test_a_shadow_elsewhere_does_not_switch_the_check_off(self):
        for other_cell in ("def helper():\n    kit = 3", "rows = [kit for kit in range(3)]", "getattr(kit, 'gone', None)"):
            with self.subTest(other_cell):
                found = Repo({"5/kit.py": self.K, "5/1.ipynb": notebook("import kit\nkit.gone()", other_cell)}).problems()
                self.assertEqual(len(found), 1, found)
                self.assertIn("kit.gone", found[0])

    def test_ipython_syntax_does_not_hide_the_cell(self):
        for cell in (
            "%%time\nkit.gone()",
            "%%capture out\nkit.gone()",
            "%time kit.gone()",
            "files = !ls\nkit.gone()",
            "kit.load?\nkit.gone()",
            "t = %timeit -o 1\nkit.gone()",
            "!pip install \\\n    pandas\nkit.gone()",
            "await kit.gone()",
        ):
            with self.subTest(cell):
                found = Repo({"5/kit.py": self.K, "5/1.ipynb": notebook("import kit", cell)}).problems()
                self.assertEqual(len(found), 1, found)
                self.assertIn("kit.gone", found[0])

    def test_a_cell_the_guard_cannot_read_fails(self):
        found = Repo({"5/1.ipynb": notebook("this is ?? not python")}).problems()
        self.assertEqual(len(found), 1, found)
        self.assertIn("cell 0 cannot be read", found[0])

    def test_bare_name_after_star_import(self):
        """Module 1's demo notebook: `from tip4patlibs_core import *`, then `init_patstat()`."""
        files = {
            "1/core.py": "__all__ = ['init']\ndef init():\n    pass\ndef hidden():\n    pass\n",
            "1/2.ipynb": notebook("from core import *\nimport pandas as pd\nx = init()\nprint(len([x]), pd)", "gone()", "hidden()"),
        }
        found = Repo(files).problems()
        self.assertEqual(len(found), 2, found)
        self.assertIn("`gone`", found[0])
        self.assertIn("`hidden`", found[1])
        files["1/2.ipynb"] = notebook("from core import *\nfrom ipywidgets import *\ngone()")
        self.assertEqual(Repo(files).problems(), [])  # a third-party star may define anything

    def test_submodule_chain_and_alias_of_an_alias(self):
        found = Repo({
            "3/dpma/__init__.py": "", "3/dpma/fetch.py": self.K, "3/kit.py": self.K,
            "3/1.ipynb": notebook("import dpma.fetch\ndpma.fetch.load()\ndpma.fetch.gone()", "import kit\nk = kit\nk.lost()"),
        }).problems()
        self.assertEqual(len(found), 2, found)
        self.assertIn("dpma.fetch.gone", found[0])
        self.assertIn("k.lost", found[1])

    def test_function_locals_are_not_module_names(self):
        found = Repo({
            "5/kit.py": "try:\n    def load():\n        gone = 1\nexcept ImportError:\n    pass\n",
            "5/1.ipynb": notebook("import kit\nkit.load()\nkit.gone"),
        }).problems()
        self.assertEqual(len(found), 1, found)

    def test_names_a_module_builds_in_ways_python_allows(self):
        found = Repo({
            "5/base.py": "__all__ = ['a']\n__all__ += ['b']\na = b = 1\n",
            "5/kit.py": "from base import *\nmatch 1:\n    case int() as val:\n        pass\n",
            "5/dyn.py": "globals()['made'] = 1\n",
            "5/1.ipynb": notebook("from kit import a, b, val\nimport dyn\ndyn.made"),
        }).problems()
        self.assertEqual(found, [])

    def test_local_file_does_not_hijack_the_standard_library(self):
        found = Repo({
            "5/build/copy.py": self.K, "types.py": self.K,
            "5/1.ipynb": notebook("import copy, types\ncopy.deepcopy([1])\ntypes.SimpleNamespace()"),
        }).problems()
        self.assertEqual(found, [])

    def test_reports_instead_of_crashing(self):
        found = Repo({
            "5/a.py": "from b import *\n", "5/b.py": "from a import *\n", "5/c.py": "from c import *\n",
            "5/p/__init__.py": "from . import *\n",
            "5/null.ipynb": '{"cells": null}', "5/src.ipynb": '{"cells": [{"cell_type": "code", "source": 5}]}',
            "5/str.ipynb": '{"cells": [{"cell_type": "code", "source": "import a\\na.x"}]}',
        }).problems()
        self.assertEqual(len(found), 3, found)
        self.assertIn("5/null.ipynb: not a notebook", found[0])
        self.assertIn("5/src.ipynb: not a notebook", found[1])
        self.assertIn("a.x", found[2])

    def test_untracked_folder_takes_no_part(self):
        repo = Repo({"5/1.ipynb": notebook("import render\nrender.main()")})
        (repo.root / "5/scratch").mkdir()
        (repo.root / "5/scratch/render.py").write_text("")
        self.assertEqual(repo.problems(), [])

    def test_percent_and_bang_inside_python_are_left_alone(self):
        """Formatters put operators at the start of a line; Markdown images start with `!`."""
        found = Repo({"5/kit.py": self.K + "DEFAULT = 1\n", "5/1.ipynb": notebook(
            "import kit",
            'msg = (\n    "%d rows"\n    % len([1])\n)',
            "ok = (\n    kit.DEFAULT is not None\n    and kit.DEFAULT\n    != 0\n)",
            "x = 7 \\\n    % 3",
            'text = """Stand:\n!wichtig\n%s rows\n![chart](chart.png)"""',
            "%matplotlib inline\nbucket = (\n    hash(str(kit.DEFAULT))\n    % 10\n)\n!ls\nkit.load()",
        )}).problems()
        self.assertEqual(found, [])

    def test_magic_beside_such_python_still_does_not_hide_the_cell(self):
        found = Repo({"5/kit.py": self.K, "5/1.ipynb": notebook(
            "import kit", '%matplotlib inline\ns = """\n%s rows"""\nx = (1\n    % 2)\n!ls\nkit.gone()',
        )}).problems()
        self.assertEqual(len(found), 1, found)
        self.assertIn("kit.gone", found[0])

    def test_quiet_when_the_file_handles_the_miss_itself(self):
        found = Repo({"5/kit.py": self.K, "5/other.py": "def run():\n    pass\n", "5/1.ipynb": notebook(
            "import kit\ntry:\n    from kit import fast_path\nexcept ImportError:\n    fast_path = None",
            "try:\n    kit.nope\nexcept AttributeError:\n    pass",
            "try:\n    import kit as k\nexcept ImportError:\n    import other as k\nk.load()\nk.run()",
        ), "5/2.ipynb": notebook("from kit import *", "%%capture out\nload()", "out.show()\nprint(_i, _oh)")}).problems()
        self.assertEqual(found, [])

    def test_annotation_on_a_missing_name(self):
        found = Repo({"5/kit.py": self.K, "5/1.ipynb": notebook("import kit\ndef f(a: kit.Nope) -> kit.Nope2:\n    pass")}).problems()
        self.assertEqual(len(found), 2, found)

    def test_commands_that_run_over_several_lines(self):
        """Python stumbles inside the continuation (`5_ipscore`), not on the `!` line."""
        for cell in (
            "!python build.py \\\n    5_ipscore/4_tool\nkit.load()",
            "!python build.py -q \\\n    --x 1 \\\n    --since 2026-01-05\nkit.load()",
            "%pip install -q \\\n    pandas \\\n    plotly\nkit.load()",
            "out = !ls \\\n   -la\nkit.load()",
        ):
            with self.subTest(cell):
                files = {"5/kit.py": self.K, "5/1.ipynb": notebook("import kit", cell)}
                self.assertEqual(Repo(files).problems(), [])
                files["5/1.ipynb"] = notebook("import kit", cell.replace("kit.load()", "kit.gone()"))
                self.assertEqual(len(Repo(files).problems()), 1)

    def test_only_a_handler_for_the_miss_makes_it_quiet(self):
        for cell in (
            "try:\n    kit.gone()\nexcept Exception as e:\n    print(e)",
            "try:\n    kit.gone()\nexcept:\n    print('failed')",
            "try:\n    from kit import gone\nexcept Exception as e:\n    print(e)",
            "try:\n    import os\n    def cb(b):\n        kit.gone()\nexcept ImportError:\n    pass",
            "%timeit -n 1 kit.gone()",
            "getattr(kit, 'gone')()",
            "import importlib\nkit = importlib.reload(kit)\nkit.gone()",
        ):
            with self.subTest(cell):
                found = Repo({"5/kit.py": self.K, "5/1.ipynb": notebook("import kit", cell)}).problems()
                self.assertEqual(len(found), 1, found)
                self.assertIn("gone", found[0])

    def test_function_bodies_see_what_the_module_level_ends_with(self):
        found = Repo({"5/kit.py": self.K, "5/1.ipynb": notebook("def run():\n    return kit.gone()", "import kit\nrun()")}).problems()
        self.assertEqual(len(found), 1, found)
        found = Repo({"5/kit.py": self.K, "5/1.ipynb": notebook(
            "import kit\ndef show():\n    return kit.result\nkit = kit.load()",
            "class A:\n    kit = 1\n    def m(self, fetch):\n        return fetch.x, getattr(kit, 'load', None)",
        )}).problems()
        self.assertEqual(found, [])

    def test_the_course_itself(self):
        self.assertEqual(guard.problems(REAL_ROOT), [])


if __name__ == "__main__":
    unittest.main()
