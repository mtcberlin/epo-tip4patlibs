#!/usr/bin/env python3
"""Course invariants that CI enforces. Standard library only, so it runs anywhere.

Each check is one rule from CLAUDE.md ("Rules that must hold"). The notebooks ship
pre-executed, so their stored output is no evidence that the code still runs; these checks
look at the files themselves.

    python3 .github/scripts/check_course.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TIP_TOOLS = [
    "4_patentreports/antibiotic_resistance/tip_tools.py",
    "5_ipscore/tip_tools.py",
    "9_misc/ipscore/tip_tools.py",
]
GUEST_EXECUTED = "4_patentreports/"  # Riccardo's reports: executed and folded, never re-run
FORBIDDEN_TRACKED = ["0_questionnaire_output/"]  # a participant's own answers


def tracked(*patterns: str) -> list[str]:
    out = subprocess.check_output(["git", "ls-files", "--", *patterns], cwd=ROOT, text=True)
    return [p for p in out.splitlines() if p]


def main() -> int:
    errors: list[str] = []

    # Rule: every Python file compiles (this is what the broken tip_tools.py docstring failed).
    for f in tracked("*.py"):
        try:
            compile((ROOT / f).read_bytes(), f, "exec")
        except SyntaxError as e:
            errors.append(f"does not compile: {f}:{e.lineno}: {e.msg}")

    # Rule: the tip_tools.py copies are byte-identical, and no unlisted copy exists.
    blobs = {p: (ROOT / p).read_bytes() for p in TIP_TOOLS if (ROOT / p).exists()}
    for p in TIP_TOOLS:
        if p not in blobs:
            errors.append(f"missing tip_tools copy: {p}")
    if len(set(blobs.values())) > 1:
        errors.append("tip_tools.py copies differ: " + ", ".join(blobs))
    for p in tracked("*tip_tools.py"):
        if p not in TIP_TOOLS:
            errors.append(f"unlisted tip_tools copy (add it to its header and here): {p}")

    # Rule: every notebook is valid JSON with cells; guest reports ship executed and folded.
    for f in tracked("*.ipynb"):
        try:
            nb = json.loads((ROOT / f).read_text(encoding="utf-8"))
            cells = nb["cells"]
        except (ValueError, KeyError) as e:
            errors.append(f"not a readable notebook: {f}: {e}")
            continue
        if not f.startswith(GUEST_EXECUTED):
            continue
        for i, c in enumerate(cells):
            if c.get("cell_type") != "code" or not "".join(c.get("source", [])).strip():
                continue
            if not c.get("execution_count") or not c.get("outputs"):
                errors.append(f"guest notebook cell not executed: {f} cell {i}")
            if not c.get("metadata", {}).get("jupyter", {}).get("source_hidden"):
                errors.append(f"guest notebook cell not folded: {f} cell {i}")

    # Rule: a participant's own answers are never committed.
    for p in tracked():
        if any(bad in p for bad in FORBIDDEN_TRACKED):
            errors.append(f"participant data tracked: {p}")

    # Rule: install.sh parses (participants pipe it into bash).
    r = subprocess.run(["bash", "-n", str(ROOT / "install.sh")], capture_output=True, text=True)
    if r.returncode:
        errors.append(f"install.sh does not parse: {r.stderr.strip()}")

    for e in errors:
        print("FAIL", e)
    print(f"{len(errors)} problem(s)" if errors else "course invariants hold")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
