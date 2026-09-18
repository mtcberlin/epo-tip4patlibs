#!/usr/bin/env bash
#
# TIP4PATLIBS — one-command setup for EPO TIP
#
#   curl -fsSL https://tip.depa.tech/install | bash
#
# tip.depa.tech is a redirect (nginx on the depa.tech Coolify server) to this file on
# the main branch: raw.githubusercontent.com/mtcberlin/epo-tip4patlibs/main/install.sh
#
# Installs an AI coding assistant that survives a TIP restart, then clones the
# course material. Safe to run again after TIP rebuilds your machine — every step
# checks before it acts, and a second run just updates.
#
# Options (environment variables):
#   TIP4PATLIBS_BRANCH=develop   clone/track a branch other than main
#   TIP4PATLIBS_DIR=~/somewhere  clone somewhere other than ~/epo-tip4patlibs
#
set -euo pipefail

REPO="${TIP4PATLIBS_REPO:-mtcberlin/epo-tip4patlibs}"
BRANCH="${TIP4PATLIBS_BRANCH:-main}"
DEST="${TIP4PATLIBS_DIR:-$HOME/epo-tip4patlibs}"
NPM_PREFIX="$HOME/.npm-global"
CLAUDE_DIR="$HOME/.claude"

RED=$'\033[0;31m'; GRN=$'\033[0;32m'; YLW=$'\033[0;33m'; DIM=$'\033[2m'; BLD=$'\033[1m'; OFF=$'\033[0m'
step() { printf '\n%s▸ %s%s\n' "$BLD" "$1" "$OFF"; }
ok()   { printf '  %s✓%s %s\n' "$GRN" "$OFF" "$1"; }
skip() { printf '  %s·%s %s\n' "$DIM" "$OFF" "$1"; }
warn() { printf '  %s!%s %s\n' "$YLW" "$OFF" "$1"; }
die()  { printf '\n%s✗ %s%s\n\n' "$RED" "$1" "$OFF" >&2; exit 1; }

printf '\n%sTIP4PATLIBS setup%s  %s→ %s%s\n' "$BLD" "$OFF" "$DIM" "$DEST" "$OFF"

# ── 0. Sanity ────────────────────────────────────────────────────────────────
step "Checking the environment"
for tool in git npm python3; do
    command -v "$tool" >/dev/null || die "'$tool' not found. This script expects an EPO TIP terminal."
done
ok "git, npm and python3 present"
command -v jq >/dev/null || warn "jq missing — the Claude status line needs it (everything else works)"

# ── 1. npm prefix that survives a restart ────────────────────────────────────
step "Making npm installs persistent"
mkdir -p "$NPM_PREFIX"
# Compare resolved paths: on TIP /home/<user> is a symlink to /home/jovyan, so the
# same directory can arrive as two different strings.
same_dir() { [ "$(cd "$1" 2>/dev/null && pwd -P)" = "$(cd "$2" 2>/dev/null && pwd -P)" ]; }
# Read ~/.npmrc directly rather than asking npm: newer npm refuses to report the
# prefix at all when ~/.npmrc is both the user and the project config (cwd = home).
npmrc_prefix() {
    # No ~/.npmrc yet is the normal case for a new participant - and under
    # `set -o pipefail` a failing sed here would end the whole script silently.
    [ -f "$HOME/.npmrc" ] || return 0
    sed -n 's/^[[:space:]]*prefix[[:space:]]*=[[:space:]]*//p' "$HOME/.npmrc" \
        | tail -1 | sed "s|^~|$HOME|"
}
recorded="$(npmrc_prefix)"
if [ -n "$recorded" ] && same_dir "$recorded" "$NPM_PREFIX"; then
    skip "npm prefix already points at ~/.npm-global"
else
    # Best effort: this only makes *later* manual `npm install -g` land in
    # ~/.npm-global. Claude Code itself is installed with --prefix below, so it does
    # not depend on this succeeding - a stray .npmrc in the working directory can
    # block it, and npm then prints an error but still exits 0.
    npm config set prefix "$NPM_PREFIX" --location=user >/dev/null 2>&1 || true
    recorded="$(npmrc_prefix)"
    if [ -n "$recorded" ] && same_dir "$recorded" "$NPM_PREFIX"; then
        ok "npm prefix → ~/.npm-global"
    else
        warn "could not record the npm prefix in ~/.npmrc (another .npmrc overrides it) — Claude Code is installed to ~/.npm-global regardless"
    fi
fi

touch "$HOME/.bash_aliases"
if grep -q 'npm-global' "$HOME/.bash_aliases" 2>/dev/null; then
    skip "PATH entry already in ~/.bash_aliases"
else
    printf '\n# Persistent npm global packages (survives TIP restarts)\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> "$HOME/.bash_aliases"
    ok "PATH entry added to ~/.bash_aliases"
fi
export PATH="$NPM_PREFIX/bin:$PATH"

# ── 2. Claude Code ───────────────────────────────────────────────────────────
step "Installing Claude Code"
CLAUDE_BIN="$NPM_PREFIX/bin/claude"
if [ -x "$CLAUDE_BIN" ]; then
    skip "already installed ($("$CLAUDE_BIN" --version 2>/dev/null | head -1)) — updating"
fi
# --prefix pins the location explicitly, whatever any .npmrc says.
npm install -g --prefix "$NPM_PREFIX" @anthropic-ai/claude-code --silent
[ -x "$CLAUDE_BIN" ] || die "Claude Code did not land in ~/.npm-global/bin — see the npm output above."
ok "claude → $CLAUDE_BIN"

# ── 3. The course material ───────────────────────────────────────────────────
step "Fetching the course material"
if [ -d "$DEST/.git" ]; then
    git -C "$DEST" pull --ff-only --quiet 2>/dev/null \
        && ok "updated $DEST" \
        || warn "could not fast-forward $DEST — you have local changes, resolve them by hand"
else
    git clone --quiet --branch "$BRANCH" "https://github.com/$REPO.git" "$DEST"
    ok "cloned $REPO ($BRANCH) → $DEST"
fi

# ── 4. Teach Claude about TIP ────────────────────────────────────────────────
step "Configuring Claude for TIP"
mkdir -p "$CLAUDE_DIR"
if [ -f "$DEST/CLAUDE.md.template" ]; then
    cp "$DEST/CLAUDE.md.template" "$CLAUDE_DIR/CLAUDE.md"
    ok "TIP context → ~/.claude/CLAUDE.md"
else
    warn "CLAUDE.md.template not found in the repo — skipping the TIP context"
fi

# Generous permissions: TIP is a throwaway virtual environment, so Claude should
# not stop and ask before every edit. Merged into settings.json, keeping the rest.
python3 - "$CLAUDE_DIR" <<'PY'
import json, os, sys
d = sys.argv[1]; p = os.path.join(d, "settings.json")
s = {}
if os.path.exists(p):
    try:
        with open(p) as f: s = json.load(f)
    except (ValueError, OSError):
        print("  ! settings.json was unreadable — starting a fresh one")
perms = s.setdefault("permissions", {})
perms["defaultMode"] = "acceptEdits"
allow = set(perms.get("allow", []))
allow.update(["Bash", "Edit", "Write", "MultiEdit", "NotebookEdit", "Read", "Grep", "Glob", "WebFetch"])
perms["allow"] = sorted(allow)
with open(p, "w") as f: json.dump(s, f, indent=2)
PY
ok "permissions set (acceptEdits + broad tool allowlist)"

# ── 5. Status line ───────────────────────────────────────────────────────────
step "Installing the Claude status line"
if [ -f "$DEST/statusline-command.sh.template" ]; then
    cp "$DEST/statusline-command.sh.template" "$CLAUDE_DIR/statusline-command.sh"
    chmod +x "$CLAUDE_DIR/statusline-command.sh"
    REAL="$(cd "$CLAUDE_DIR" && pwd -P)/statusline-command.sh"
    python3 - "$CLAUDE_DIR/settings.json" "$REAL" <<'PY'
import json, os, sys
p, real = sys.argv[1], sys.argv[2]
s = json.load(open(p)) if os.path.exists(p) else {}
s["statusLine"] = {"type": "command", "command": f"bash {real}"}
with open(p, "w") as f: json.dump(s, f, indent=2)
PY
    ok "status line registered (folder · branch · context · cost · model)"
else
    warn "statusline-command.sh.template not found — skipping"
fi

# ── 6. Course dependencies ───────────────────────────────────────────────────
step "Installing course dependencies"
if python3 -c 'import pycountry' 2>/dev/null; then
    skip "pycountry already present"
else
    python3 -m pip install --user --quiet pycountry && ok "pycountry (module 4's world map)"
fi

# ── Done ─────────────────────────────────────────────────────────────────────
cat <<EOF

${GRN}${BLD}Done.${OFF}

  ${BLD}1.${OFF} Open a new terminal, or run:  ${DIM}source ~/.bash_aliases${OFF}
  ${BLD}2.${OFF} Start the assistant:          ${DIM}cd ${DEST} && claude${OFF}
  ${BLD}3.${OFF} Open a module folder in JupyterLab — ${DIM}1_querylib${OFF} is a good start.

  ${DIM}Run this script again any time — after a TIP restart it repairs the setup,
  and it updates the course material instead of cloning it twice.${OFF}

  ${DIM}Want to push changes back? You need an SSH key on GitHub; the old setup
  notebook walks through it: 9_misc/legacy/startwithtip/${OFF}

EOF
