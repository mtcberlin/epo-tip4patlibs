"""Writes tip-explorer-teaser-standalone.html: the slide as ONE file, images embedded, so it can be
mailed and opened with a double-click. Standard library only.  python3 make_standalone.py"""
import base64, re
from pathlib import Path

here = Path(__file__).resolve().parent
html = (here / "tip-explorer-teaser.html").read_text(encoding="utf-8")

def embed(m):
    path = here / m.group(1)
    mime = "image/png" if path.suffix == ".png" else "image/jpeg"
    return '"data:%s;base64,%s"' % (mime, base64.b64encode(path.read_bytes()).decode())

html = re.sub(r'"(shots/[^"]+\.(?:png|jpg))"', embed, html)
head = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1"></head><body>')
(here / "tip-explorer-teaser-standalone.html").write_text(head + html + "</body></html>", encoding="utf-8")
print("written", here / "tip-explorer-teaser-standalone.html")
