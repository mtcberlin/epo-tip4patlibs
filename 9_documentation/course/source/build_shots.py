#!/usr/bin/env python3
"""Cut the workshop deck's screenshots from what the repository already contains.

Modules 3, 5 and 6 ship executed, so their images need no TIP session: this
script rebuilds each one as a small standalone page, photographs it with headless
Chrome and crops it to its content. Modules 1, 2 and 4 ship with cleared outputs
on purpose and cannot be done here — see plan-tipsession-3-screenshots.md.

    uv run --with pillow python build_shots.py

Output lands in shots/NN.png, which is exactly where build_slides.py looks.

Four things here are not obvious and each one cost a wrong image first time:

1. **Light mode.** Module 6's report carries a dark palette behind
   `prefers-color-scheme`. Headless Chrome answers *dark*, so the report renders
   its dark theme — and a forced white background then leaves near-white
   headings on white. `preferredColorScheme=1` picks light and settles it.
2. **Plotly has to come from somewhere.** A recorded chart fragment is only a
   div plus a `Plotly.newPlot` call. The library is extracted out of module 5's
   own assembled report, so the chart is drawn by the same build that produced it.
3. **A pandas header row is not a `<tr>` you can count.** `to_html` writes the
   header as `<tr style="text-align: right;">`, so slicing `<tr>` matches drops
   the first *data* row — in module 3 that is the 1265-family row the whole
   module is about. Slice inside `<tbody>` instead.
4. **Crop to content.** A fixed window leaves half a page of white, and
   build_slides.py fits the image into its frame, so the white would be scaled
   up along with the picture.
"""

from __future__ import annotations

import http.server
import json
import re
import shutil
import socketserver
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

from PIL import Image, ImageChops

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SHOTS = HERE / "shots"
CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
MAX_W = 2200          # a slide frame is 7in wide; more pixels are just bytes
PAD = 28

CSS = """
body{margin:0;background:#fff;font-family:system-ui,-apple-system,'Segoe UI',Arial,sans-serif;color:#1a1a1a}
.wrap{padding:26px 32px}
h1{font-size:20px;margin:0 0 4px;color:#be0f05;font-weight:800;letter-spacing:-.2px}
.sub{font-size:13px;color:#64748b;margin:0 0 20px}
.tag{font-size:11px;font-weight:700;color:#be0f05;text-transform:uppercase;letter-spacing:.4px;margin:0 0 7px}
.cols{display:flex;gap:34px;align-items:flex-start}
.col-l{flex:0 0 690px}.col-r{flex:1}
pre{background:#f8fafc;border-left:3px solid #be0f05;padding:13px 16px;font-size:11.5px;
    line-height:1.5;margin:0;font-family:ui-monospace,Menlo,monospace;white-space:pre}
table{border-collapse:collapse;font-size:12.5px}
th{background:#be0f05;color:#fff;padding:6px 12px;text-align:left;font-weight:600}
td{padding:5px 12px;border-bottom:1px solid #e2e8f0}
tr:nth-child(even) td{background:#fbfcfd}
.dataframe{border:1px solid #e2e8f0}
tbody tr:first-child td{background:#fdf2f2;font-weight:700}
.more{font-size:12px;color:#64748b;margin:11px 0 0;font-style:italic}
"""


# --------------------------------------------------------------------------- #
def page(body: str, width: int | None = None) -> str:
    w = f".wrap{{width:{width}px}}" if width else ""
    return f'<!doctype html><meta charset="utf-8"><style>{CSS}{w}</style>{body}'


def build_04(stage: Path) -> tuple[str, int, int]:
    """Module 3 — the step-1 hit list, beside the query that produced it."""
    nb = json.loads((REPO / "3_patstat_explorer" /
                     "1_Applicant_consolidation_notebook.ipynb").read_text(encoding="utf-8"))
    cell = nb["cells"][4]
    table = "".join(next(o["data"]["text/html"] for o in cell["outputs"]
                         if "text/html" in o.get("data", {})))
    tbody = re.search(r"<tbody>(.*?)</tbody>", table, re.S)
    rows = re.findall(r"<tr.*?</tr>", tbody.group(1), re.S)      # see note 3
    table = table.replace(tbody.group(0), "<tbody>" + "".join(rows[:12]) + "</tbody>")
    code = "".join(cell["source"]).replace("<", "&lt;")
    stage.joinpath("04.html").write_text(page(f"""
<div class="wrap">
  <h1>Step 1 — one company, many spellings</h1>
  <p class="sub">3_patstat_explorer/1_Applicant_consolidation_notebook.ipynb ·
     PATSTAT knows names, not companies</p>
  <div class="cols">
    <div class="col-l"><p class="tag">One query</p><pre>{code}</pre></div>
    <div class="col-r"><p class="tag">…and no single answer</p>{table}
      <p class="more">… {len(rows)} spellings here, capped at 200. Take the biggest row alone<br>
      and you report 1265 for a group that files far more.</p></div>
  </div>
</div>""", width=1560), encoding="utf-8")
    return "03", 1700, 1000


def build_06(stage: Path) -> tuple[str, int, int]:
    """Module 5 — one chart out of the assembled landscape report."""
    root = REPO / "5_patentreports/2_antibiotic_resistance_rebuild"
    report = (root / "4_report/antibiotic_resistance_report.html").read_text(encoding="utf-8")
    lib = max(re.finditer(r"<script[^>]*>(.*?)</script>", report, re.S),
              key=lambda m: len(m.group(1))).group(1)            # see note 2
    stage.joinpath("plotly.js").write_text(lib, encoding="utf-8")
    frag = (root / "2_core_landscape_analyses_output/_report_parts"
                   "/applicants_by_sector.fragment.html").read_text(encoding="utf-8")
    stage.joinpath("06.html").write_text(
        page(f"""<script src="plotly.js"></script>
<div class="wrap">
  <h1>Antibiotic resistance — applicants by institutional sector</h1>
  <p class="sub">One of 13 charts in the assembled landscape report ·
     2_core_landscape_analyses.ipynb, step 10</p>
  {frag}
</div>"""), encoding="utf-8")
    return "05", 1600, 800


def build_08(stage: Path) -> tuple[str, int, int]:
    """Module 6 — the report's verdict, with every other section hidden."""
    report = (REPO / "6_ipscore_rebuild/4_tool/ipscore_valuation.html").read_text(encoding="utf-8")
    hide = ("<style>section:not(#verdict){display:none!important}"
            "nav,footer,.nav,.toc{display:none!important}</style>")
    stage.joinpath("08.html").write_text(report.replace("</head>", hide + "</head>", 1),
                                         encoding="utf-8")
    return "06", 1600, 1000


def shoot(stage: Path, name: str, w: int, h: int, port: int) -> Path:
    raw = stage / f"{name}.raw.png"
    subprocess.run([str(CHROME), "--headless", "--disable-gpu", "--hide-scrollbars",
                    f"--window-size={w},{h}", "--force-device-scale-factor=2",
                    "--blink-settings=preferredColorScheme=1",   # see note 1
                    "--virtual-time-budget=6000", f"--screenshot={raw}",
                    f"http://127.0.0.1:{port}/{name}.html"],
                   capture_output=True, text=True, check=True)
    return raw


def crop(raw: Path, dest: Path) -> tuple[int, int]:
    im = Image.open(raw).convert("RGB")
    bg = Image.new("RGB", im.size, im.getpixel((5, 5)))
    mask = ImageChops.difference(im, bg).convert("L").point(lambda p: 255 if p > 6 else 0)
    l, t, r, b = mask.getbbox()
    out = im.crop((max(0, l - PAD), max(0, t - PAD),
                   min(im.width, r + PAD), min(im.height, b + PAD)))
    if out.width > MAX_W:
        out = out.resize((MAX_W, round(out.height * MAX_W / out.width)), Image.LANCZOS)
    out.save(dest, optimize=True)
    return out.size


def main() -> int:
    if not CHROME.exists():
        print(f"!! Chrome not found at {CHROME}"); return 1
    SHOTS.mkdir(exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="tip4patlibs-shots-"))
    try:
        specs = [build_04(stage), build_06(stage), build_08(stage)]

        class Q(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *a, **k): super().__init__(*a, directory=str(stage), **k)
            def log_message(self, *a): pass

        with socketserver.TCPServer(("127.0.0.1", 0), Q) as srv:
            port = srv.server_address[1]
            threading.Thread(target=srv.serve_forever, daemon=True).start()
            for name, w, h in specs:
                size = crop(shoot(stage, name, w, h, port), SHOTS / f"{name}.png")
                kb = (SHOTS / f"{name}.png").stat().st_size // 1024
                print(f"   shots/{name}.png  {size[0]}x{size[1]}  ({kb} kB)")
            srv.shutdown()
    finally:
        shutil.rmtree(stage, ignore_errors=True)

    missing = [n for n in ("01", "02", "04") if not (SHOTS / f"{n}.png").exists()]
    if missing:
        print(f"   still missing: {', '.join(missing)} — those need a TIP session "
              f"(plan-tipsession-3-screenshots.md)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
