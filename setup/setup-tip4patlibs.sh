#!/bin/bash
# ============================================================
# TIP4PATLIBs Environment Setup Script
# ============================================================
# Run this once on a fresh EPO TIP JupyterLab to set up
# everything you need for the TIP4PATLIBs conference notebooks.
#
# Usage:
#   Open a terminal in JupyterLab and run:
#     bash setup-tip4patlibs.sh
#
# What it does:
#   1. Creates a Python virtual environment at ~/.venvs/tip4patlibs
#   2. Installs any extra packages from requirements.txt
#   3. Registers a Jupyter kernel "TIP4PATLIBs (Conference)"
#   4. Verifies everything works
#
# After setup:
#   - Refresh JupyterLab (F5) to see the new kernel
#   - Open a notebook → Kernel → Change Kernel → "TIP4PATLIBs (Conference)"
# ============================================================

set -e

VENV_DIR="$HOME/.venvs/tip4patlibs"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REQ_FILE="$SCRIPT_DIR/requirements.txt"
KERNEL_NAME="tip4patlibs"
KERNEL_DISPLAY="TIP4PATLIBs (Conference)"

echo "============================================"
echo "  TIP4PATLIBs Environment Setup"
echo "============================================"
echo ""

# Step 1: Create virtual environment
if [ -d "$VENV_DIR" ]; then
    echo "[1/4] Virtual environment already exists at $VENV_DIR"
    read -p "      Recreate it? (y/N) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "      Removing old environment..."
        rm -rf "$VENV_DIR"
    else
        echo "      Keeping existing environment."
    fi
fi

if [ ! -d "$VENV_DIR" ]; then
    echo "[1/4] Creating virtual environment..."
    /opt/conda/bin/python -m venv --system-site-packages "$VENV_DIR"
    echo "      Created at $VENV_DIR"
else
    echo "[1/4] Using existing virtual environment."
fi

# Step 2: Install extra packages from requirements.txt
echo "[2/4] Installing packages..."
if [ -f "$REQ_FILE" ]; then
    # Check if requirements.txt has any actual packages (non-comment, non-empty lines)
    pkg_lines=$(grep -v '^#' "$REQ_FILE" | grep -v '^$' | wc -l)
    if [ "$pkg_lines" -gt 0 ]; then
        "$VENV_DIR/bin/pip" install -r "$REQ_FILE"
        echo "      Installed $pkg_lines package(s) from requirements.txt"
    else
        echo "      No extra packages needed (requirements.txt has no entries)."
    fi
else
    echo "      No requirements.txt found — skipping."
fi

# Step 3: Register Jupyter kernel
echo "[3/4] Registering Jupyter kernel..."
"$VENV_DIR/bin/python" -m ipykernel install --user \
    --name="$KERNEL_NAME" \
    --display-name="$KERNEL_DISPLAY"
echo "      Kernel '$KERNEL_DISPLAY' registered."

# Step 4: Verify
echo "[4/4] Verifying setup..."
echo ""

# Check Python
py_version=$("$VENV_DIR/bin/python" --version 2>&1)
echo "      Python:    $py_version"

# Check EPO packages
if "$VENV_DIR/bin/python" -c "import epo.tipdata.patstat" 2>/dev/null; then
    echo "      PATSTAT:   OK (epo.tipdata.patstat importable)"
else
    echo "      PATSTAT:   WARNING - epo.tipdata.patstat not importable"
fi

# Check kernel
if jupyter kernelspec list 2>/dev/null | grep -q "$KERNEL_NAME"; then
    echo "      Kernel:    OK ($KERNEL_DISPLAY)"
else
    echo "      Kernel:    WARNING - not found in kernel list"
fi

# Disk usage
size=$(du -sh "$VENV_DIR" 2>/dev/null | cut -f1)
echo "      Disk:      $size"

echo ""
echo "============================================"
echo "  Setup complete!"
echo ""
echo "  Next steps:"
echo "  1. Refresh JupyterLab in your browser (F5)"
echo "  2. Open a notebook"
echo "  3. Kernel → Change Kernel → '$KERNEL_DISPLAY'"
echo "============================================"
