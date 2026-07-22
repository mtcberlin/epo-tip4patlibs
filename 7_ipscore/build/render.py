#!/usr/bin/env python3
"""Render the Dennemeyer IPscore / NPV Planner HTML tools from build/data + build/templates.

Usage: python3 render.py [--promote]
  --promote   after rendering to build/dist/, copy the results over the live
              files in Dennemeyer/ (only do this after reviewing the diff).
"""
import json
import sys
from pathlib import Path

import jinja2

ROOT = Path(__file__).resolve().parent.parent  # /home/jovyan/Dennemeyer
BUILD = ROOT / "build"
DATA = BUILD / "data"
TEMPLATES = BUILD / "templates"
DIST = BUILD / "dist"
DIST.mkdir(exist_ok=True)

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(str(TEMPLATES)),
    trim_blocks=False,
    lstrip_blocks=False,
    keep_trailing_newline=True,
)
env.filters["tojson"] = lambda v: json.dumps(v, ensure_ascii=False)


def _jsq(value):
    """Escape a value for safe embedding inside an existing single-quoted JS
    string literal in the template (backslash, then single quote). This is the
    fix for the exact bug BUILD_LOG.md documents: an apostrophe in translated
    text (e.g. Italian "dell'azienda") silently truncates a '...' JS string and
    kills the whole <script> block."""
    s = str(value)
    return s.replace("\\", "\\\\").replace("'", "\\'")


env.filters["jsq"] = _jsq


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def render_ipscore(lang, demo_flag):
    ui = load(f"ipscore_ui_strings_{lang}.json")
    qs = load(f"ipscore_questions_{lang}.json")
    tmpl = env.get_template("ipscore_template.html.j2")
    return tmpl.render(
        ui=ui,
        qs_json=json.dumps(qs, ensure_ascii=False),
        std5_json=json.dumps(_std5_for(lang), ensure_ascii=False),
        sec_names_json=json.dumps(ui["sec_names"], ensure_ascii=False),
        action_plan_json=_js_action_plan(ui["action_plan"]),
        demo=load(f"ipscore_demo_{lang}.json") if demo_flag else None,
    )


def render_npv_planner(lang):
    ui = load(f"npv_ui_strings_{lang}.json")
    insights = load(f"npv_insights_{lang}.json")
    demo = load(f"npv_demo_{lang}.json")
    tmpl = env.get_template("npv_planner_template.html.j2")
    return tmpl.render(
        ui=ui,
        insights_json=json.dumps(insights["INSIGHTS"], ensure_ascii=False),
        param_meta_json=json.dumps(insights["PARAM_META"], ensure_ascii=False),
        param_tips_json=json.dumps(insights["PARAM_TIPS"], ensure_ascii=False),
        oek_cards_json=json.dumps(insights["OEK_CARDS"], ensure_ascii=False),
        qual_questions_json=json.dumps(insights["QUAL_QUESTIONS"], ensure_ascii=False),
        demo=demo,
    )


def _std5_for(lang):
    # STD5 is the 5-point Likert scale label set; identical in role across all IPscore
    # questions but expressed per language. Kept alongside ui_strings for symmetry.
    return {
        "it": ["No", "In misura ridotta", "In qualche misura", "In larga misura", "In grandissima misura"],
        "en": ["No", "To a limited extent", "To some extent", "To a large extent", "To a very large extent"],
    }[lang]


def _js_action_plan(action_plan):
    # Rendered as a JS object literal (not JSON) to match the original `var s = {A:'...', ...}` style.
    parts = ", ".join(f"{k}:{json.dumps(v, ensure_ascii=False)}" for k, v in action_plan.items())
    return "{" + parts + "}"


def main():
    promote = "--promote" in sys.argv

    outputs = {
        "IPscore_IT.html": render_ipscore("it", demo_flag=False),
        "IPscore_IT_Demo.html": render_ipscore("it", demo_flag=True),
        "IPscore_EN_Demo.html": render_ipscore("en", demo_flag=True),
        "NPV_Target_Planner_EN.html": render_npv_planner("en"),
        "NPV_Target_Planner_IT.html": render_npv_planner("it"),
    }

    for fname, content in outputs.items():
        out_path = DIST / fname
        out_path.write_text(content, encoding="utf-8")
        print(f"rendered {fname} -> {out_path} ({len(content)} bytes)")

    if promote:
        for fname in outputs:
            (ROOT / fname).write_text((DIST / fname).read_text(encoding="utf-8"), encoding="utf-8")
            print(f"promoted {fname} over live file")


if __name__ == "__main__":
    main()
