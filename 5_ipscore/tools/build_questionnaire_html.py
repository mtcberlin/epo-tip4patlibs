#!/usr/bin/env python3
"""Build the standalone questionnaire HTML — a *generated* artifact, not part of the notebook
chain and never hand-edited.

Reads `ipscore_spec.json` (the 40 questions) and `worked_example.json` (starting values) and
writes `0_questionnaire_tool.html` next to `0_questionnaire.ipynb`: a single self-contained
page, vanilla JS, no build step to open it, same paginated single-page-app pattern as the
Dennemeyer IPScore / NPV Target Planner tools (see `9_misc/legacy/startwithtip`'s course notes and
`7_ipscore/`). It never computes an NPV — collecting answers is the only job here, so it stays
usable even where PATSTAT is not reachable. Its "Download my answers" button saves a
`questionnaire.json` shaped exactly like `ipscore_kit.save_questionnaire()` expects; drop that
file into `0_questionnaire_upload/` and notebook 0's loader cell registers it for notebooks
2, 3 and 4 to read.

Usage: python3 build_questionnaire_html.py [--check]
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SPEC_PATH = ROOT / "ipscore_spec.json"
EXAMPLE_PATH = ROOT / "worked_example.json"
OUT_PATH = ROOT / "0_questionnaire_tool.html"

ACCENT = "#be0f05"
INK = "#0b0b0b"
INK_SECONDARY = "#475569"
INK_MUTED = "#94a3b8"
SURFACE = "#fcfcfb"
GRID = "#e2e8f0"
PANEL = "#f8fafc"


def _js(value) -> str:
    """`json.dumps`, but safe to splice into a `<script>` block."""
    return json.dumps(value, ensure_ascii=False).replace("</", "<\\/")


def load_data():
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    example = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))
    sections = [{"key": s["key"], "title": s["title"]} for s in spec["sections"]]
    questions = [
        {
            "id": q["id"],
            "section": q["section"],
            "factor": q["factor"],
            "question": q["question"],
            "explanation": q["explanation"],
            "answers": q["answers"],
            "money": bool(q.get("oek")),
        }
        for q in spec["questions"]
    ]
    defaults = {
        "patent": {k: v for k, v in example["patent"].items() if k != "reference"},
        "financials": dict(example["financials"]),
        "financials_note": example.get("financials_note", ""),
        "scores": dict(example["scores"]),
    }
    return sections, questions, defaults


PATENT_FIELDS = [
    ("publication", "Publication number", "text", "e.g. EP1234567B1"),
    ("docdb_family_id", "DOCDB family ID", "number", "what notebook 2's PATSTAT queries key off"),
    ("applicant", "Applicant", "text", ""),
    ("field", "Technical field", "text", ""),
    ("title", "Title", "text", ""),
    ("plain_title", "Plain-language title", "text", "a one-line, non-technical description"),
]

FINANCIAL_FIELDS = [
    ("turnover", "Business turnover (EUR)", "money"),
    ("direct_costs", "Direct costs (EUR)", "money"),
    ("indirect_costs", "Indirect costs (EUR)", "money"),
    ("depreciation", "Provision for depreciation (EUR)", "money"),
    ("depreciation_period", "Depreciation period (years)", "years"),
    ("business_area_share", "Business area share of turnover (%)", "percent"),
    ("discount_rate", "Discount rate (%)", "percent"),
]


def build_html() -> str:
    sections, questions, defaults = load_data()

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>TIP4PATLIBS &ndash; IPScore questionnaire</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  :root {{
    --accent: {ACCENT}; --ink: {INK}; --ink2: {INK_SECONDARY}; --muted: {INK_MUTED};
    --surface: {SURFACE}; --grid: {GRID}; --panel: {PANEL};
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
    background: var(--surface); color: var(--ink);
  }}
  header {{
    text-align: center; padding: 40px 24px 24px;
  }}
  header .badge {{
    display: inline-block; background: var(--accent); color: #fff; padding: 12px 20px;
    border-radius: 12px; font-size: 28px; font-weight: 800; letter-spacing: -0.5px;
    margin-bottom: 14px;
  }}
  header .sub {{ color: var(--ink2); font-size: 15px; max-width: 640px; margin: 0 auto; line-height: 1.6; }}
  #steps {{
    display: flex; justify-content: center; gap: 6px; margin: 22px 0 8px; flex-wrap: wrap;
  }}
  .step-dot {{
    width: 11px; height: 11px; border-radius: 50%; background: var(--grid); cursor: pointer;
  }}
  .step-dot.done {{ background: var(--accent); }}
  .step-dot.current {{ background: var(--ink); }}
  main {{ max-width: 760px; margin: 0 auto; padding: 8px 24px 60px; }}
  .page {{ display: none; }}
  .page.active {{ display: block; }}
  h2 {{ font-size: 20px; margin: 18px 0 4px; }}
  .hint {{ color: var(--ink2); font-size: 13.5px; line-height: 1.6; margin-bottom: 20px; }}
  label.field {{ display: block; margin-bottom: 16px; }}
  label.field span {{ display: block; font-size: 13px; font-weight: 600; margin-bottom: 4px; }}
  label.field small {{ display: block; font-weight: 400; color: var(--muted); margin-top: 2px; }}
  input[type=text], input[type=number] {{
    width: 100%; padding: 9px 12px; border: 1px solid var(--grid); border-radius: 8px;
    font-size: 14px; font-family: inherit;
  }}
  textarea {{
    width: 100%; padding: 9px 12px; border: 1px solid var(--grid); border-radius: 8px;
    font-size: 14px; font-family: inherit; min-height: 60px;
  }}
  .question {{
    border: 1px solid var(--grid); border-radius: 10px; padding: 14px 16px; margin-bottom: 14px;
    background: #fff;
  }}
  .question .qid {{ font-weight: 700; font-size: 13.5px; }}
  .question .money {{ color: var(--accent); font-size: 12px; font-weight: 700; margin-left: 6px; }}
  .question .qtext {{ font-size: 14px; margin: 4px 0 10px; }}
  .question .opt {{ display: block; font-size: 13.5px; padding: 4px 0; cursor: pointer; }}
  .question .opt input {{ margin-right: 8px; }}
  .question .help-toggle {{
    font-size: 12px; color: var(--muted); cursor: pointer; margin-top: 6px; display: inline-block;
  }}
  .question .help {{ display: none; font-size: 12.5px; color: var(--ink2); margin-top: 6px; line-height: 1.5; }}
  .question .help.open {{ display: block; }}
  .nav {{ display: flex; justify-content: space-between; margin-top: 28px; }}
  button {{
    font-family: inherit; font-size: 14px; font-weight: 600; padding: 10px 20px; border-radius: 8px;
    border: none; cursor: pointer;
  }}
  button.primary {{ background: var(--accent); color: #fff; }}
  button.secondary {{ background: var(--panel); color: var(--ink2); border: 1px solid var(--grid); }}
  button:disabled {{ opacity: 0.4; cursor: default; }}
  .summary-block {{ border: 1px solid var(--grid); border-radius: 10px; padding: 14px 18px; margin-bottom: 14px; }}
  .summary-block h3 {{ font-size: 14px; margin: 0 0 8px; }}
  .summary-row {{ display: flex; justify-content: space-between; font-size: 13px; padding: 3px 0; gap: 12px; }}
  .summary-row .k {{ color: var(--ink2); }}
  .summary-row .v {{ font-weight: 600; text-align: right; }}
  #error {{ color: var(--accent); font-size: 13px; margin-top: 10px; display: none; }}
  #downloaded {{ display: none; background: #f0fdf4; border: 1px solid #bbf7d0; color: #166534;
    border-radius: 10px; padding: 14px 18px; margin-top: 16px; font-size: 13.5px; line-height: 1.6; }}
</style>
</head>
<body>
<header>
  <div class="badge">TIP4PATLIBS &ndash; IPScore questionnaire</div>
  <div class="sub">
    Answer these once for a real patent, then download your answers and hand the file back to
    whoever is running the PATSTAT valuation &mdash; nothing here is sent anywhere or computed
    into a value. That happens afterwards, on TIP.
  </div>
</header>
<div id="steps"></div>
<main>
  <div id="pages"></div>
  <div class="nav">
    <button class="secondary" id="prevBtn" onclick="prevPage()">&larr; Back</button>
    <button class="primary" id="nextBtn" onclick="nextPage()">Next &rarr;</button>
  </div>
  <div id="error"></div>
  <div id="downloaded"></div>
</main>
<script>
const SECTIONS = {_js(sections)};
const QUESTIONS = {_js(questions)};
const DEFAULTS = {_js(defaults)};
const PATENT_FIELDS = {_js(PATENT_FIELDS)};
const FINANCIAL_FIELDS = {_js(FINANCIAL_FIELDS)};

const state = {{
  patent: {{...DEFAULTS.patent}},
  financials: {{...DEFAULTS.financials}},
  financials_note: DEFAULTS.financials_note,
  scores: {{...DEFAULTS.scores}},
}};

let PAGE_COUNT = 0;
let current = 0;

function questionsFor(sectionKey) {{
  return QUESTIONS.filter(q => q.section === sectionKey);
}}

function fieldHtml(id, labelText, kind, help, value) {{
  const inputType = (kind === "text") ? "text" : "number";
  const step = (kind === "percent") ? "0.1" : (kind === "years" ? "0.5" : "1");
  return `<label class="field">
    <span>${{labelText}}</span>
    <input type="${{inputType}}" step="${{step}}" data-field="${{id}}" value="${{value}}">
    ${{help ? `<small>${{help}}</small>` : ""}}
  </label>`;
}}

function buildPatentPage() {{
  let html = `<h2>The patent</h2>
    <div class="hint">Six fields identify the patent. The family ID is what notebook 2's
    PATSTAT queries key off once it runs on TIP; the rest is display text carried through the
    reports and the tool.</div>`;
  for (const [id, label, kind, help] of PATENT_FIELDS) {{
    html += fieldHtml(id, label, kind, help, state.patent[id]);
  }}
  return html;
}}

function buildSectionPage(section) {{
  let html = `<h2>${{section.key}} &middot; ${{section.title}}</h2>
    <div class="hint">Pick the answer that fits each question. Every answer starts on a
    plausible default &mdash; change any of them, or leave them as they are.</div>`;
  for (const q of questionsFor(section.key)) {{
    const tag = q.money ? '<span class="money">&#128176; feeds the NPV</span>' : "";
    html += `<div class="question" id="q-${{q.id}}">
      <span class="qid">${{q.id}} &mdash; ${{q.factor}}</span>${{tag}}
      <div class="qtext">${{q.question}}</div>`;
    q.answers.forEach((a, i) => {{
      const n = i + 1;
      const checked = (state.scores[q.id] === n) ? "checked" : "";
      html += `<label class="opt">
        <input type="radio" name="score-${{q.id}}" value="${{n}}" ${{checked}}
               onchange="setScore('${{q.id}}', ${{n}})"> ${{n}} &ndash; ${{a}}
      </label>`;
    }});
    html += `<span class="help-toggle" onclick="toggleHelp('${{q.id}}')">why this is asked</span>
      <div class="help" id="help-${{q.id}}">${{q.explanation}}</div>
    </div>`;
  }}
  return html;
}}

function buildFinancialsPage() {{
  let html = `<h2>The company</h2>
    <div class="hint">Seven figures straight from the annual accounts. PATSTAT holds no
    financial data, so these always stay a person's input.</div>`;
  for (const [id, label, kind] of FINANCIAL_FIELDS) {{
    let value = state.financials[id];
    if (kind === "percent") value = (value * 100).toFixed(1);
    html += fieldHtml(id, label, kind, "", value);
  }}
  html += `<label class="field"><span>One-line note on where these figures come from</span>
    <textarea data-field="financials_note">${{state.financials_note}}</textarea></label>`;
  return html;
}}

function buildReviewPage() {{
  const scored = Object.keys(state.scores).length;
  let html = `<h2>Review &amp; download</h2>
    <div class="hint">Check the summary below, then download your answers. Hand the file to
    whoever runs the PATSTAT valuation, or drop it into <code>0_questionnaire_upload/</code>
    yourself if you have access to the notebook.</div>`;

  html += `<div class="summary-block"><h3>Patent</h3>`;
  for (const [id, label] of PATENT_FIELDS) {{
    html += `<div class="summary-row"><span class="k">${{label}}</span><span class="v">${{state.patent[id]}}</span></div>`;
  }}
  html += `</div>`;

  html += `<div class="summary-block"><h3>Company figures</h3>`;
  for (const [id, label, kind] of FINANCIAL_FIELDS) {{
    let value = state.financials[id];
    if (kind === "percent") value = (value * 100).toFixed(1) + " %";
    else if (kind === "money") value = Number(value).toLocaleString() + " EUR";
    html += `<div class="summary-row"><span class="k">${{label}}</span><span class="v">${{value}}</span></div>`;
  }}
  html += `</div>`;

  html += `<div class="summary-block"><h3>Questionnaire</h3>
    <div class="summary-row"><span class="k">Answers given</span><span class="v">${{scored}} of 40</span></div>
  </div>`;

  html += `<button class="primary" onclick="downloadAnswers()">&#128229; Download my answers (questionnaire.json)</button>
    <div id="downloaded"></div>`;
  return html;
}}

function toggleHelp(qid) {{
  document.getElementById("help-" + qid).classList.toggle("open");
}}

function setScore(qid, n) {{
  state.scores[qid] = n;
}}

function readPageInputs() {{
  document.querySelectorAll("input[data-field], textarea[data-field]").forEach(el => {{
    const id = el.dataset.field;
    if (id === "financials_note") {{
      state.financials_note = el.value;
    }} else if (id in state.patent) {{
      state.patent[id] = (id === "docdb_family_id") ? parseInt(el.value || "0", 10) : el.value;
    }} else if (id in state.financials) {{
      let v = parseFloat(el.value || "0");
      const field = FINANCIAL_FIELDS.find(f => f[0] === id);
      if (field && field[2] === "percent") v = v / 100;
      state.financials[id] = v;
    }}
  }});
}}

function buildPages() {{
  const container = document.getElementById("pages");
  const parts = [buildPatentPage()];
  for (const s of SECTIONS) parts.push(buildSectionPage(s));
  parts.push(buildFinancialsPage());
  parts.push(buildReviewPage());
  PAGE_COUNT = parts.length;

  container.innerHTML = parts.map((html, i) =>
    `<div class="page" id="page-${{i}}">${{html}}</div>`).join("");

  const steps = document.getElementById("steps");
  steps.innerHTML = parts.map((_, i) =>
    `<div class="step-dot" id="dot-${{i}}" onclick="goToPage(${{i}})"></div>`).join("");
}}

function goToPage(n) {{
  readPageInputs();
  current = Math.max(0, Math.min(PAGE_COUNT - 1, n));
  document.querySelectorAll(".page").forEach((el, i) => el.classList.toggle("active", i === current));
  document.querySelectorAll(".step-dot").forEach((el, i) => {{
    el.classList.toggle("current", i === current);
    el.classList.toggle("done", i < current);
  }});
  document.getElementById("prevBtn").disabled = (current === 0);
  document.getElementById("nextBtn").style.visibility = (current === PAGE_COUNT - 1) ? "hidden" : "visible";
  if (current === PAGE_COUNT - 1) {{
    document.getElementById("page-" + current).innerHTML = buildReviewPage();
  }}
  document.getElementById("error").style.display = "none";
  window.scrollTo(0, 0);
}}

function nextPage() {{ goToPage(current + 1); }}
function prevPage() {{ goToPage(current - 1); }}

function downloadAnswers() {{
  readPageInputs();
  const missingPatent = PATENT_FIELDS.filter(([id]) => !state.patent[id] && state.patent[id] !== 0);
  if (missingPatent.length) {{
    const err = document.getElementById("error");
    err.style.display = "block";
    err.textContent = "Please fill in: " + missingPatent.map(f => f[1]).join(", ");
    return;
  }}
  const payload = {{
    patent: state.patent,
    financials: state.financials,
    financials_note: state.financials_note,
    scores: state.scores,
  }};
  const blob = new Blob([JSON.stringify(payload, null, 2)], {{type: "application/json"}});
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "questionnaire.json";
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
  const box = document.getElementById("downloaded");
  box.style.display = "block";
  box.innerHTML = "&#9989; Saved <code>questionnaire.json</code> to your downloads folder. " +
    "Drop that file into <code>0_questionnaire_upload/</code> next to this notebook, then run " +
    "notebook 0's loader cell.";
}}

document.addEventListener("DOMContentLoaded", () => {{
  buildPages();
  goToPage(0);
}});
</script>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true",
                         help="only run the Node syntax check, do not write the file")
    args = parser.parse_args()

    html = build_html()

    script = html.split("<script>", 1)[1].rsplit("</script>", 1)[0]
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
        f.write(script)
        tmp_path = f.name
    try:
        result = subprocess.run(["node", "--check", tmp_path], capture_output=True, text=True)
    finally:
        Path(tmp_path).unlink()
    if result.returncode != 0:
        raise SystemExit(f"generated JS failed to parse:\n{result.stderr}")
    print("✓ generated <script> block is syntactically valid JS")

    if not args.check:
        OUT_PATH.write_text(html, encoding="utf-8")
        print(f"✓ wrote {OUT_PATH} ({OUT_PATH.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
