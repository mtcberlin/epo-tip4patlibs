"""Report kit — the small contract every analysis in this module follows.

The module is built as a chain of independent analyses across four notebooks. Each
analysis produces exactly two things: **one Plotly figure** and **the tidy dataframe
behind it**. Calling :func:`record` at the end of an analysis cell

  * shows the figure inline (so the workshop sees the result), and
  * saves the figure as an inline HTML *fragment* plus the data as parquet, and notes
    both in a small ``manifest.json`` inside the notebook's output folder.

The final notebook (``4_assemble_report``) then reads every manifest, orders the
contributions by their ``order`` number, and stitches them into

  * one self-contained ``report.html`` (a single embedded plotly.js, all figures
    inline — no iframes, so it renders inside TIP), and
  * one ``report_data.xlsx`` with one sheet per chart (networks contribute two: nodes
    and edges).

Every chart in the report therefore has a matching sheet in the workbook. That is the
whole point: the report is auditable and the numbers are reusable without touching TIP.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

PARTS_DIRNAME = "_report_parts"


def _slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def _parts_dir(output_dir: str | Path) -> Path:
    p = Path(output_dir) / PARTS_DIRNAME
    p.mkdir(parents=True, exist_ok=True)
    return p


def record(
    order: int,
    slug: str,
    title: str,
    fig,
    data,
    *,
    output_dir: str | Path = ".",
    note: str | None = None,
    show: bool = True,
) -> None:
    """Save one analysis contribution and (by default) show it inline.

    Parameters
    ----------
    order
        Integer that fixes this chart's position in the final report. Convention:
        100s = notebook 1 (dataset), 200s = notebook 2 (core landscape),
        300s = notebook 3 (advanced). Leave gaps (110, 120, ...) so charts can be
        inserted later without renumbering.
    slug
        Short identifier, used for the fragment/parquet filenames and the plot div id.
    title
        Human title shown as the section heading in the report and as the workbook
        sheet name (truncated to Excel's 31-char limit).
    fig
        A Plotly figure.
    data
        The tidy dataframe behind the chart, or a ``dict`` mapping a sheet label to a
        dataframe for multi-table charts (e.g. a network → ``{"nodes": ..., "edges": ...}``).
    output_dir
        The notebook's own output folder (e.g. ``"2_core_landscape_analyses_output"``).
    note
        Optional one-line caption shown under the chart in the report.
    show
        Whether to render the figure inline (True for the live notebook).
    """
    parts = _parts_dir(output_dir)

    # 1) the figure as an inline fragment: no <html>, and plotly.js is included once,
    #    later, by the assembler — not per fragment.
    fragment_html = fig.to_html(
        full_html=False, include_plotlyjs=False, div_id=f"fig_{slug}", default_width="100%"
    )
    (parts / f"{slug}.fragment.html").write_text(fragment_html, encoding="utf-8")

    # 2) the data behind it — one parquet per sheet
    sheets = data if isinstance(data, dict) else {"data": data}
    sheet_files: dict[str, str] = {}
    for label, df in sheets.items():
        fname = f"{slug}__{_slugify(label)}.parquet"
        pd.DataFrame(df).to_parquet(parts / fname, index=False)
        sheet_files[label] = fname

    # 3) the manifest entry (manifest keyed by slug, so re-running a cell overwrites it)
    manifest_path = parts / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    manifest[slug] = {
        "order": order,
        "slug": slug,
        "title": title,
        "note": note,
        "fragment": f"{slug}.fragment.html",
        "sheets": sheet_files,
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")

    if show:
        fig.show()


def load_contributions(module_root: str | Path) -> list[dict]:
    """Collect every analysis contribution across the module, ordered.

    Scans ``*/_report_parts/manifest.json`` under ``module_root`` and returns the merged
    entries sorted by their ``order`` number. Each entry's ``fragment`` and ``sheets``
    paths are resolved to absolute paths so the assembler can read them from anywhere.
    """
    root = Path(module_root)
    entries: list[dict] = []
    for manifest_path in sorted(root.glob(f"*/{PARTS_DIRNAME}/manifest.json")):
        parts_dir = manifest_path.parent
        manifest = json.loads(manifest_path.read_text())
        for entry in manifest.values():
            entry = dict(entry)
            entry["fragment_path"] = parts_dir / entry["fragment"]
            entry["sheet_paths"] = {
                label: parts_dir / fname for label, fname in entry["sheets"].items()
            }
            entries.append(entry)
    entries.sort(key=lambda e: e["order"])
    return entries
