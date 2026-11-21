#!/bin/bash
# PipeGuard-RV environment setup script
# Run from WSL: bash scripts/setup.sh
# Or from the project root: bash scripts/setup.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "============================================================"
echo "  PipeGuard-RV Environment Setup"
echo "  Project: $PROJECT_DIR"
echo "============================================================"

# ---------------------------------------------------------------------------
# 1. Check required tools
# ---------------------------------------------------------------------------
check_tool() {
    local tool="$1"
    local version_flag="${2:---version}"
    if command -v "$tool" &>/dev/null; then
        local ver
        ver="$("$tool" $version_flag 2>&1 | head -1)"
        echo "[OK]  $tool — $ver"
    else
        echo "[MISSING] $tool — not found in PATH"
        MISSING_TOOLS+=("$tool")
    fi
}

MISSING_TOOLS=()
check_tool iverilog "-V"
check_tool yosys    "--version"
check_tool python3  "--version"
check_tool make     "--version"

if [ ${#MISSING_TOOLS[@]} -gt 0 ]; then
    echo ""
    echo "WARNING: The following tools are missing: ${MISSING_TOOLS[*]}"
    echo "Install them before running simulations:"
    echo "  sudo apt-get install iverilog yosys make"
    echo "  (python3 is typically pre-installed on Ubuntu WSL)"
fi

# ---------------------------------------------------------------------------
# 2. Create virtual environment if not present
# ---------------------------------------------------------------------------
VENV_DIR="$PROJECT_DIR/.venv"
if [ ! -d "$VENV_DIR" ]; then
    echo ""
    echo "Creating Python virtual environment at $VENV_DIR ..."
    python3 -m venv "$VENV_DIR"
    echo "[OK]  .venv created"
else
    echo "[OK]  .venv already exists at $VENV_DIR"
fi

# ---------------------------------------------------------------------------
# 3. Activate venv and install requirements
# ---------------------------------------------------------------------------
# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"

REQUIREMENTS="$PROJECT_DIR/requirements.txt"
if [ -f "$REQUIREMENTS" ]; then
    echo ""
    echo "Installing Python requirements from requirements.txt ..."
    pip install --quiet -r "$REQUIREMENTS"
    echo "[OK]  requirements installed"
else
    echo "WARNING: $REQUIREMENTS not found — skipping pip install"
fi

# ---------------------------------------------------------------------------
# 4. Print final tool version summary
# ---------------------------------------------------------------------------
echo ""
echo "============================================================"
echo "  Tool Versions"
echo "============================================================"
echo "iverilog : $(iverilog -V 2>&1 | head -1 || echo 'not found')"
echo "yosys    : $(yosys --version 2>&1 | head -1 || echo 'not found')"
echo "python3  : $(python3 --version 2>&1)"
echo "pip      : $(pip --version 2>&1 | head -1)"
echo "cocotb   : $(python3 -c 'import cocotb; print(cocotb.__version__)' 2>&1 || echo 'not installed')"
echo "make     : $(make --version 2>&1 | head -1 || echo 'not found')"
echo "============================================================"
echo "Setup complete. Activate the venv with:"
echo "  source $VENV_DIR/bin/activate"
echo "============================================================"
