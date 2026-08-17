#!/usr/bin/env python3
"""Render the course documents as branded mtc.berlin A4 handouts.

Each `NN_*.md` in this directory is paired with a `NN_*.yaml` sidecar holding the
title-page metadata, and rendered with the `mtc-pdf` skill into the parent
`course/` directory, where the finished handouts live.

The Markdown is written for reading on screen in a repository; a printed handout
needs three small adjustments, made here on a copy so the sources stay untouched:

1. The leading `# Title` and its italic subtitle line are dropped — the title page
   draws them from the sidecar, so keeping them would print the title twice.
2. The 🎓 / ⚠️ / ⏱ markers become text labels. WeasyPrint's PDF cannot carry colour
   emoji reliably, so the skill strips them — and here they carry meaning, which
   would silently be lost ("Boxes marked  are for ...").
3. The ASCII-art diagram in the overview becomes a Graphviz block, which the skill
   pre-renders to vector SVG. Box-drawing art reflows and misaligns in print.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent   # the Markdown + YAML sources
OUT = HERE.parent                        # the finished handouts, one level up
STAGE = HERE / "_staging"
SKILL = Path.home() / ".claude/skills/mtc-pdf"
BUILD = SKILL / "scripts/build_pdf.py"

# --- 3. the overview's skills → applications diagram, as vector ------------
CHAIN_DOT = """```dot
digraph chain {
  rankdir=LR; compound=true;
  graph [bgcolor="transparent", nodesep=0.22, ranksep=1.0];
  node  [shape=box, style="rounded,filled", fillcolor="#f6e7f0",
         color="#890c58", fontname="Arial", fontsize=11, margin="0.22,0.13"];
  edge  [color="#890c58", arrowsize=0.8, penwidth=1.2];

  subgraph cluster_skills {
    label="SKILLS"; fontname="Arial"; fontsize=11; fontcolor="#890c58";
    color="#d9b8cc"; style="rounded"; margin=14;
    s4 [label="4  Find the right people\\napplicant consolidation"];
    s3 [label="3  Ask PATSTAT a question\\nthe query library"];
    s1 [label="1  Work on TIP at all\\nenvironment, first query"];
    { rank=same; s4; s3; s1; }
  }

  subgraph cluster_apps {
    label="APPLICATIONS"; fontname="Arial"; fontsize=11; fontcolor="#890c58";
    color="#d9b8cc"; style="rounded"; margin=14;
    a8 [label="8  What is one patent worth?\\nmodel → evidence → valuation"];
    a6 [label="6  What does a field look like?\\ncorpus → analyses → report"];
    a5 [label="5  Who is out there?\\nregion → applicants → leads"];
    { rank=same; a8; a6; a5; }
  }

  s3 -> a6 [ltail=cluster_skills, lhead=cluster_apps,
            label="each application\\nconsumes all three", fontname="Arial",
            fontsize=10, fontcolor="#890c58"];
}
```"""

# An untagged fenced block whose body is drawn with box-drawing characters.
_ASCII_DIAGRAM = re.compile(r"^```[ \t]*\n(.*?)\n```[ \t]*$", re.DOTALL | re.MULTILINE)


def _swap_ascii_art(m: "re.Match[str]") -> str:
    return CHAIN_DOT if re.search(r"[─│┌└├┤┐┘]", m.group(1)) else m.group(0)


# --- 4. reflow hard-wrapped prose -----------------------------------------
# The sources are hard-wrapped at ~95 columns for reading diffs. The renderer
# runs Markdown with `nl2br`, so every one of those wraps would become a real
# <br/> and the printed paragraph would break where the *source* breaks, not
# where the *column* ends. Joining continuation lines back into one logical line
# lets the PDF set its own line breaks. Structural lines — headings, list items,
# table rows, rules, fences — always start a new line and are never joined.
_BLOCK_START = re.compile(
    r"""^(?:\s*$              # blank
        |\#{1,6}\             # heading
        |\s*(?:[-*+]|\d+[.)])\  # list item
        |\|                    # table row
        |-{3,}\s*$            # rule
        |```                   # fence
        |\s{4,}\S            # indented block
        )""",
    re.VERBOSE,
)


# A heading, table row or rule is self-contained: the next line always starts a
# new block. A list item, by contrast, absorbs its own wrapped continuation.
_NO_CONTINUATION = re.compile(r"^(?:\s*$|\#{1,6}\s|\||-{3,}\s*$|\s{4,}\S)")


def unwrap_paragraphs(md_text: str) -> str:
    out: list[str] = []
    in_fence = False
    for line in md_text.split("\n"):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence or not out:
            out.append(line)
            continue

        prev = out[-1]
        quoted = line.startswith(">") and prev.startswith(">")
        body = line[1:].lstrip() if quoted else line
        prev_body = prev[1:].lstrip() if prev.startswith(">") else prev

        joinable = (
            (quoted or (not line.startswith(">") and not prev.startswith(">")))
            and body.strip()
            and prev_body.strip()
            and not _BLOCK_START.match(body)
            and not _NO_CONTINUATION.match(prev_body)
            and not prev.endswith("  ")
        )
        if joinable:
            out[-1] = prev.rstrip() + " " + body
        else:
            out.append(line)
    return "\n".join(out)


def to_handout(md_text: str) -> str:
    body = md_text

    # 1. title + italic subtitle live on the title page
    body = re.sub(r"\A#[ \t]+[^\n]*\n+(?:\*[^\n]*\*\n+)?", "", body)

    # 2a. the legend sentences that *name* the markers, before the markers go
    body = re.sub(r"([Bb])oxes marked 🎓", r"\1oxes labelled **Trainer**", body)
    body = re.sub(r"([Bb])oxes marked ⚠️?", r"\1oxes labelled **Trap**", body)

    # 2b. the markers themselves — fold into the callout's bold lead-in
    body = re.sub(r"🎓[ \t]*(?=\*\*)", "", body)
    body = re.sub(r"⚠️?[ \t]*\*\*(.+?)\*\*", r"**Trap — \1**", body)
    body = re.sub(r"⚠️?[ \t]*", "**Trap.** ", body)
    body = body.replace("🎓", "Trainer")
    body = body.replace("⏱", "Time")

    # 3. ASCII art → Graphviz
    body = _ASCII_DIAGRAM.sub(_swap_ascii_art, body)

    # 4. let the PDF choose its own line breaks
    body = unwrap_paragraphs(body)
    return body


# The skill is versioned in the dotfiles repository, not this one, so an older
# checkout renders these documents wrongly and says nothing. One fix matters
# here: a blockquote that is entirely bold becomes the callout's title, and
# before dotfiles 9a2a7f1 everything after the first *emphasis* or `code` span
# inside it was dropped. Several boxes in this course are written that way.
def check_skill() -> None:
    src = BUILD.read_text(encoding="utf-8")
    if "first[0].tail" not in src:
        print("!! the mtc-pdf skill predates the callout-title fix: a fully bold\n"
              "   blockquote will lose everything after its first inline span.\n"
              f"   Update the dotfiles checkout behind {BUILD} (fix: 9a2a7f1).")


def main() -> int:
    check_skill()
    OUT.mkdir(exist_ok=True)
    STAGE.mkdir(exist_ok=True)
    failures = []

    for md in sorted(HERE.glob("[0-9]*.md")):
        cfg = md.with_suffix(".yaml")
        if not cfg.exists():
            print(f"!! no config for {md.name} — skipped")
            failures.append(md.name)
            continue
        staged = STAGE / md.name
        staged.write_text(to_handout(md.read_text(encoding="utf-8")), encoding="utf-8")
        pdf = OUT / f"{md.stem}.pdf"
        cmd = [
            "uv", "run", "--quiet",
            "--with", "weasyprint", "--with", "markdown", "--with", "pyyaml",
            str(BUILD), str(staged), "--config", str(cfg), "-o", str(pdf),
        ]
        env = {"DYLD_FALLBACK_LIBRARY_PATH": "/opt/homebrew/lib"}
        res = subprocess.run(cmd, env={**__import__("os").environ, **env},
                             capture_output=True, text=True)
        if res.returncode != 0:
            print(f"!! {md.name}\n{res.stdout}{res.stderr}")
            failures.append(md.name)
        else:
            print(f"   {pdf.relative_to(OUT)}  ({pdf.stat().st_size // 1024} kB)")

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
