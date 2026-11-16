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

    def test_the_course_itself(self):
        self.assertEqual(guard.problems(REAL_ROOT), [])


if __name__ == "__main__":
    unittest.main()
