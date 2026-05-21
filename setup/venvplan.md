# Plan: Set Up 3 Python Virtual Environments on EPO TIP

## Context

You need 3 isolated Python environments for developing notebooks on the EPO TIP JupyterLab platform:
1. **tip4patlibs** - Final deliverables (3 notebooks for PATLIB conference)
2. **patlib-dev** - Playground/experimentation
3. **mtc-codefest2026** - Additional mtc project

**Why venv instead of conda:** The conda package cache (`/tmp/conda/pkgs`) is not writable, and EPO packages (`epo.tipdata.patstat`) are not on conda-forge. Python venv with `--system-site-packages` inherits all 335 base packages (including EPO tools) automatically, uses minimal disk (~15MB per env vs ~2.6GB), and requires no workarounds.

**tibcli:** Not available in this environment - skipping start menu integration.

---

## Step 1: Create venvs directory and 3 virtual environments

```bash
mkdir -p ~/.venvs
/opt/conda/bin/python -m venv --system-site-packages ~/.venvs/tip4patlibs
/opt/conda/bin/python -m venv --system-site-packages ~/.venvs/patlib-dev
/opt/conda/bin/python -m venv --system-site-packages ~/.venvs/mtc-codefest2026
```

Location: `~/.venvs/` (clean, standard, separate from project code)

## Step 2: Register each as a Jupyter kernel

```bash
~/.venvs/tip4patlibs/bin/python -m ipykernel install --user --name=tip4patlibs --display-name="TIP4PATLIBs (Conference)"
~/.venvs/patlib-dev/bin/python -m ipykernel install --user --name=patlib-dev --display-name="PATLIB Dev (Playground)"
~/.venvs/mtc-codefest2026/bin/python -m ipykernel install --user --name=mtc-codefest2026 --display-name="mtc Codefest 2026"
```

Kernels go to `~/.local/share/jupyter/kernels/` (user-level, no admin needed).

## Step 3: Add shell convenience aliases

Create/update `~/.bash_aliases` with activation shortcuts:
- `activate-tip4patlibs`
- `activate-patlib-dev`
- `activate-mtc`
- `venv-status`

Source it from `~/.bashrc` if not already done.

## Step 4: Create a management script

Create `~/.venvs/manage-venvs.sh` with commands:
- `status` - show all venvs, sizes, kernels
- `install <venv> <pkg>` - install package in specific venv
- `recreate-kernels` - re-register all kernels (troubleshooting)

## Step 5: Create requirements.txt templates

Place empty/template `requirements.txt` in each project directory:
- `~/tip4patlibs/requirements.txt`
- `~/epo_codefest_2026/requirements.txt`
- For patlib-dev: decide location later

These track ONLY packages beyond the 335 EPO base packages.

## Step 6: Verify everything works

Run verification:
- All 3 venvs exist and Python works
- EPO packages (`epo.tipdata.patstat`) accessible from each venv
- `jupyter kernelspec list` shows 4 kernels (base + 3 new)
- Refresh JupyterLab browser, confirm kernels appear in dropdown

---

## Files to create/modify

| File | Action |
|------|--------|
| `~/.venvs/tip4patlibs/` | Create (venv) |
| `~/.venvs/patlib-dev/` | Create (venv) |
| `~/.venvs/mtc-codefest2026/` | Create (venv) |
| `~/.local/share/jupyter/kernels/tip4patlibs/kernel.json` | Auto-created by ipykernel |
| `~/.local/share/jupyter/kernels/patlib-dev/kernel.json` | Auto-created by ipykernel |
| `~/.local/share/jupyter/kernels/mtc-codefest2026/kernel.json` | Auto-created by ipykernel |
| `~/.bash_aliases` | Create (activation aliases) |
| `~/.bashrc` | Edit (source bash_aliases if needed) |
| `~/.venvs/manage-venvs.sh` | Create (management script) |
| `~/tip4patlibs/requirements.txt` | Create (template) |
| `~/epo_codefest_2026/requirements.txt` | Create (template) |

## Disk impact

- 3 venvs with `--system-site-packages`: ~15-45MB total
- Current free space: 17GB - plenty of room
- Saves ~7.8GB compared to full conda environments

## Daily workflow after setup

- **In JupyterLab**: Select kernel from dropdown when creating/opening notebooks
- **In terminal**: `activate-tip4patlibs` then `pip install <package>` then `deactivate`
- **Track additions**: Update `requirements.txt` after installing packages
- **Share**: Recipients just need `requirements.txt` + notebooks (base TIP env covers everything else)
