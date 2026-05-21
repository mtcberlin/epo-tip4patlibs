# Implementation Log: Virtual Environment Setup on EPO TIP

**Date:** 2026-02-11
**Platform:** EPO Technology Intelligence Platform (TIP), JupyterLab
**Python:** 3.12.11 (via `/opt/conda/bin/python`)

---

## What Was Done

Set up 3 isolated Python virtual environments for parallel notebook development on the EPO TIP JupyterLab platform.

### Environments Created

| Venv | Kernel Display Name | Purpose | Size |
|------|-------------------|---------|------|
| `tip4patlibs` | TIP4PATLIBs (Conference) | Final deliverables for PATLIB conference | 13MB |
| `patlib-dev` | PATLIB Dev (Playground) | Experimentation & prototyping | 13MB |
| `mtc-codefest2026` | MTC Codefest 2026 | MTC project work | 13MB |

**Total disk:** 39MB for all 3 environments.

### Files Created

| File | Purpose |
|------|---------|
| `~/.venvs/tip4patlibs/` | Virtual environment |
| `~/.venvs/patlib-dev/` | Virtual environment |
| `~/.venvs/mtc-codefest2026/` | Virtual environment |
| `~/.venvs/manage-venvs.sh` | Management script (status, install, recreate-kernels) |
| `~/.bash_aliases` | Shell shortcuts (activate-tip4patlibs, activate-patlib-dev, activate-mtc, venv-status) |
| `~/tip4patlibs/requirements.txt` | Tracks extra packages beyond TIP base |
| `~/epo_codefest_2026/requirements.txt` | Tracks extra packages beyond TIP base |
| `~/.local/share/jupyter/kernels/*/kernel.json` | Auto-created by ipykernel (3 kernel specs) |

### Files NOT Modified

- `~/.bashrc` — already had a block sourcing `~/.bash_aliases`, no edit needed.

---

## Decision Log

### Why `venv --system-site-packages` instead of conda

This was the key decision of the entire setup. We explored conda first and hit multiple walls:

1. **`/tmp/conda/pkgs` is read-only** — conda's package cache lives there on TIP and is not writable by the user. Every `conda create` or `conda install` fails with permission errors on the cache.
2. **EPO packages not on conda-forge** — `epo.tipdata.patstat`, `epo.tip.use_cases`, and other EPO-specific packages are pip-installed into the base `/opt/conda` environment. They have no conda-forge equivalents.
3. **Size** — A full conda env clone would be ~2.6GB per environment. Three would consume ~7.8GB of the ~17GB free.

The `--system-site-packages` flag on `python -m venv` solves all three:
- No conda cache needed — uses pip, which writes to the venv's own `site-packages`.
- Inherits all 335 base packages (including EPO tools) as read-through from `/opt/conda/lib/python3.12/site-packages`.
- Only 13MB per venv (just symlinks + pip/setuptools metadata).

### Why `~/.venvs/` and not inside project directories

- Keeps venvs separate from git-tracked project code.
- Standard convention, easy to find.
- Management script can iterate over all venvs in one place.

### Why `--user` for kernel install

- No admin/root access needed.
- Kernels go to `~/.local/share/jupyter/kernels/` which JupyterLab picks up automatically.
- Survives TIP platform updates (user home is persistent).

---

## Verification Results

```
=== Venv Python Check ===
  tip4patlibs: Python 3.12.11    ✓
  patlib-dev: Python 3.12.11     ✓
  mtc-codefest2026: Python 3.12.11  ✓

=== EPO Package Import ===
  tip4patlibs: import epo.tipdata.patstat → OK
  patlib-dev: import epo.tipdata.patstat → OK
  mtc-codefest2026: import epo.tipdata.patstat → OK

=== Jupyter Kernels (4 total) ===
  python3          /opt/conda/share/jupyter/kernels/python3
  tip4patlibs      ~/.local/share/jupyter/kernels/tip4patlibs
  patlib-dev       ~/.local/share/jupyter/kernels/patlib-dev
  mtc-codefest2026 ~/.local/share/jupyter/kernels/mtc-codefest2026
```

---

## Lessons Learned

### 1. Conda is not viable on EPO TIP for user-created envs

The TIP platform ships a single managed conda environment at `/opt/conda`. The package cache at `/tmp/conda/pkgs` is read-only. Attempting `conda create`, `conda install`, or even `conda config --add pkgs_dirs` to a writable location hits various failures. Don't go down this path — use `venv` with `--system-site-packages` instead.

### 2. `--system-site-packages` is the crucial flag

Without it, the venv is isolated and you'd need to reinstall all 335 base packages. With it, the venv inherits everything and you only install additions. This is the entire trick that makes lightweight venvs work on TIP.

### 3. ipykernel must be called from the venv's own Python

```bash
# Correct — registers the venv's Python as the kernel
~/.venvs/tip4patlibs/bin/python -m ipykernel install --user --name=tip4patlibs

# Wrong — would register the base Python, defeating the purpose
python -m ipykernel install --user --name=tip4patlibs
```

The kernel.json must point to the venv's `bin/python`, not the base interpreter.

### 4. ~/.bashrc already sources ~/.bash_aliases on this platform

The default Debian-based `.bashrc` on TIP includes a conditional block that sources `~/.bash_aliases` if it exists. No need to edit `.bashrc` — just create the aliases file.

### 5. JupyterLab needs a browser refresh to see new kernels

After registering kernels, they don't appear in the dropdown until you refresh the JupyterLab tab (F5). No server restart needed.

### 6. tibcli is not available

The plan originally considered TIBCO start menu integration via `tibcli`. This tool is not installed on the TIP environment. Not needed for the venv workflow anyway.

---

## Quick Reference: Daily Workflow

### In JupyterLab (GUI)
1. Open or create a notebook
2. Click kernel selector (top-right) → choose "TIP4PATLIBs (Conference)" etc.
3. The notebook now runs in that venv's Python

### In Terminal (installing packages)
```bash
source ~/.bash_aliases        # load shortcuts (auto on new terminals)
activate-tip4patlibs          # activate the venv
pip install some-package      # installs only in this venv
deactivate                    # back to base
```

### Management
```bash
~/.venvs/manage-venvs.sh status              # overview of all venvs
~/.venvs/manage-venvs.sh install tip4patlibs pygwalker  # install into specific venv
~/.venvs/manage-venvs.sh recreate-kernels    # re-register kernels after issues
venv-status                                   # quick check (bash alias)
```

### Sharing notebooks
Recipients on TIP only need:
- The notebook file(s)
- The `requirements.txt` (for any extra packages beyond base)
- They run: `pip install -r requirements.txt` in their own venv
