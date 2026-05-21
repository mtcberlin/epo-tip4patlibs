# Environment Setup

## For Trainees (First-Time Setup)

Open a terminal in JupyterLab and run:

```bash
bash setup/setup-tip4patlibs.sh
```

Then refresh your browser (F5) and switch any notebook to the **"TIP4PATLIBs (Conference)"** kernel via **Kernel > Change Kernel**.

That's it. The script creates an isolated Python environment, installs all required packages, and registers the Jupyter kernel.

## What's Inside

| File | Purpose |
|------|---------|
| `setup-tip4patlibs.sh` | One-command setup for trainees |
| `requirements.txt` | Extra packages beyond the 335 TIP base packages |

The setup uses a Python venv with `--system-site-packages` at `~/.venvs/tip4patlibs/`. This inherits all EPO TIP packages (pandas, plotly, sqlalchemy, `epo.tipdata.patstat`, etc.) and only adds what's listed in `requirements.txt`. Total size: ~13MB.

## For Developers

### Installing packages

```bash
activate-tip4patlibs
venv-pip install some-package    # installs AND auto-updates requirements.txt
deactivate
```

`venv-pip` is a wrapper that keeps `requirements.txt` in sync automatically.
Regular `pip install` works too but won't update the requirements file.

### Shell shortcuts (available after `source ~/.bash_aliases`)

| Command | What it does |
|---------|-------------|
| `activate-tip4patlibs` | Activate the venv |
| `activate-patlib-dev` | Activate the dev/playground venv |
| `activate-mtc` | Activate the codefest venv |
| `venv-status` | Show all venvs, sizes, kernel status |
| `venv-pip install <pkg>` | Install + auto-update requirements.txt |

### Management script

```bash
~/.venvs/manage-venvs.sh status               # overview
~/.venvs/manage-venvs.sh install tip4patlibs pygwalker  # install into specific venv
~/.venvs/manage-venvs.sh recreate-kernels      # re-register kernels
```

### Troubleshooting

- **Kernel not in dropdown?** Refresh JupyterLab (F5).
- **Package not found after install?** Restart the kernel (Kernel > Restart).
- **Broken venv?** Re-run `bash setup/setup-tip4patlibs.sh` and choose "y" to recreate.
