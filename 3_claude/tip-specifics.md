# TIP Environment Specifics

Notes on the EPO Technology Intelligence Platform (TIP) runtime environment,
gathered from inspecting a live JupyterHub container (March 2025).

---

## Container filesystem layout

TIP runs as a Kubernetes pod with a JupyterHub single-user container.
The default user inside the image is `jovyan` (Jupyter convention); at startup
a symlink `/home/<your-username> → /home/jovyan` is created so that `$HOME`
resolves correctly.

### Mounts

| Mount target | Device / source | Persistent? | Notes |
|---|---|---|---|
| `/` | overlay | No | Container image, rebuilt on every restart |
| `/home/jovyan` | `/dev/sdf` (30 GB, ext4) | **Yes** | Your personal volume — survives restarts |
| `/home/jovyan/training` | EmptyDir + Git worktree | No | EPO training notebooks, read-only (UID 65533) |
| `/home/jovyan/.cache` | EmptyDir | No | Ephemeral cache, cleared on restart |
| `/opt/conda` | overlay | No | Conda environment from the container image |
| `/opt/epo_customizations/icons` | bind mount (ro) | No | EPO UI customizations |
| `/opt/release-info` | bind mount (ro) | No | TIP release metadata |
| `/usr/bin/init_scripts` etc. | bind mount (ro) | No | EPO startup scripts |

**Key takeaway:** Only `/home/jovyan` is persistent (shown as `/` in JupyterLab's
file browser). Everything under `/opt/conda`, `/usr/local`, and the actual system
root filesystem (`/`) is ephemeral — rebuilt from the container image on every restart.

### Training materials

The `~/training/` directory is a **Kubernetes EmptyDir volume** populated via a
Git worktree checkout at pod startup. All files are owned by UID 65533 (not your
user) and the directory is effectively read-only. Contents include official EPO
notebooks for PATSTAT, EP full-text data, OPS, and patent family analysis.

---

## Startup scripts & dotfile persistence

The init script `/usr/bin/init_juser.sh` runs on **every container start** and
overwrites several dotfiles with EPO defaults from `/opt/resources/`:

```bash
cp /opt/resources/profile  /home/jovyan/.profile
cp /opt/resources/bashrc   /home/jovyan/.bashrc
cp /opt/resources/condarc  /home/jovyan/.condarc
```

Any customizations to these files are lost after a restart.

Additionally, `conda init` runs on every start (appends to `.bashrc`), and
`/usr/bin/init_juser_main.sh` overwrites `.condarc` a second time.

### Dotfile persistence overview

| File | Persistent? | Reason |
|---|---|---|
| `.bashrc` | **No** | Overwritten from `/opt/resources/bashrc` on every start |
| `.profile` | **No** | Overwritten from `/opt/resources/profile` on every start |
| `.condarc` | **No** | Overwritten twice (init_juser.sh + init_juser_main.sh) |
| `.bash_aliases` | **Yes** | Not touched by any init script |
| `.gitconfig` | **Yes** | Not touched by any init script |
| `.npmrc` | **Yes** | Not touched by any init script |
| `.ssh/` | **Yes** | Not touched by any init script |
| `.claude/` | **Yes** | Not touched by any init script |
| `.claude.json` | **Yes** | Not touched by any init script |

**Rule of thumb:** Put all customizations in `.bash_aliases` (sourced by
`.bashrc`), never in `.bashrc` itself — they will be overwritten.

### Other init-time cleanup

Depending on pod configuration, additional scripts may run:

- `cleanup.sh` — `rm -rf ~/.local/lib/python*` (removes pip user-site packages)
- `listerine.sh` — `rm -rf .local .jupyter .ipython` (aggressive cleanup, only
  runs if set as `ADDITIONAL_INIT_SCRIPT` env var)
- `clean_jlab_environment.sh` — removes a specific `attr` package that conflicts
  with JupyterLab

---

## Consequences for tool installation

Anything installed into `/opt/conda` (e.g. `npm install -g`, `pip install`)
is lost after a container restart because it lives on the overlay filesystem.
To make installations persistent, they must target your home directory.

### Python packages

TIP provides `epo.tipdata.patstat` and other EPO libraries in the base conda
environment at `/opt/conda/lib/python3.12/site-packages/`. When using a
project-level venv, these are invisible by default. The patstat-mcp server
handles this automatically (see `server.py:_tip_available()`), but for your
own venvs you have two options:

```bash
# Option A: create venv with system site-packages access
python -m venv --system-site-packages .venv

# Option B: add a .pth file to bridge the gap
echo "/opt/conda/lib/python3.12/site-packages" \
  > .venv/lib/python3.12/site-packages/conda-system.pth
```

---

## Installing Claude Code persistently on TIP

By default `npm install -g` writes to `/opt/conda/` which is lost on restart.
The fix: redirect npm's global prefix to a persistent directory in your home.

### One-time setup (copy & paste into terminal)

```bash
# 1. Create persistent directory for npm global packages
mkdir -p ~/.npm-global

# 2. Tell npm to use it
npm config set prefix ~/.npm-global

# 3. Add to PATH permanently (via .bash_aliases, which TIP sources on login)
#    Skip if you already have this line in .bash_aliases
grep -q 'npm-global' ~/.bash_aliases 2>/dev/null || \
  sed -i '1i # Persistent npm global packages (survives container restarts)\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' ~/.bash_aliases

# 4. Activate for current session
export PATH="$HOME/.npm-global/bin:$PATH"

# 5. Install Claude Code
npm install -g @anthropic-ai/claude-code

# 6. Verify
claude --version
```

### After a container restart

Claude should be available immediately — no reinstallation needed.
If `claude` is not found, run `source ~/.bash_aliases` or open a new terminal.

### Updating Claude Code

The initial install must use npm (no Homebrew on TIP). After that, Claude's
built-in upgrade command works:

```bash
# Preferred (uses Claude's native updater)
claude upgrade

# Alternative (via npm directly)
npm update -g @anthropic-ai/claude-code
```
