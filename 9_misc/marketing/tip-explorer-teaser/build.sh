#!/bin/bash
# Renders tip-explorer-teaser.html into tip-explorer-teaser.mp4 (1920x1080, 25 fps, 23.4 s loop).
# Needs a headless Chromium (Playwright's chrome-headless-shell or Google Chrome) and ffmpeg.
#   CHROME=/path/to/chrome ./build.sh
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
chrome="${CHROME:-$(ls "$HOME"/Library/Caches/ms-playwright/chromium_headless_shell-*/*/chrome-headless-shell 2>/dev/null | tail -1)}"
work="$(mktemp -d)"
cp -R "$here/shots" "$work/"
{ echo '<!doctype html><html lang="en"><head><meta charset="utf-8"></head><body>'
  cat "$here/tip-explorer-teaser.html"; echo '</body></html>'; } > "$work/render.html"
mkdir -p "$work/frames" "$work/profiles"
frame() {  # one still: the page renders time t when called with ?t=
  local i=$1 t f; t=$(echo "scale=3; $i/25" | bc); f=$(printf "%04d" "$i")
  "$chrome" --headless --disable-gpu --hide-scrollbars --window-size=1920,1080 --virtual-time-budget=3000 \
    --user-data-dir="$work/profiles/p$i" --screenshot="$work/frames/f$f.png" "file://$work/render.html?t=$t" >/dev/null 2>&1
}
export -f frame; export chrome work
seq 0 584 | xargs -P 10 -I{} bash -c 'frame {}'
ffmpeg -loglevel error -y -framerate 25 -i "$work/frames/f%04d.png" -c:v libx264 -profile:v high \
  -pix_fmt yuv420p -crf 18 -movflags +faststart "$here/tip-explorer-teaser.mp4"
cp "$work/frames/f0100.png" "$here/tip-explorer-teaser-still.png"
echo "done: $here/tip-explorer-teaser.mp4 (work files in $work)"
