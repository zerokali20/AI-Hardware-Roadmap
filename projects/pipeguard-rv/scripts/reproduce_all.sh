#!/usr/bin/env bash
# PipeGuard-RV — End-to-End Reproducibility Script (Phase 9)
#
# Re-runs every verification, formal, synthesis, fault-injection, and analysis
# step from a clean checkout and verifies that deterministic summary metrics
# reproduce without discrepancy.
#
# Usage (from WSL):
#   bash scripts/reproduce_all.sh
#   SKIP_30_BASELINE=1 bash scripts/reproduce_all.sh   # faster smoke check
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJ_DIR="$(dirname "$SCRIPT_DIR")"
LAB06_VENV="$(cd "$PROJ_DIR/../.." && pwd)/labs/06-riscv-pipeline/.venv/bin/activate"

cd "$PROJ_DIR"

if [ -f "$PROJ_DIR/.venv/bin/activate" ] && "$PROJ_DIR/.venv/bin/python" -c "import cocotb" 2>/dev/null; then
    source "$PROJ_DIR/.venv/bin/activate"
elif [ -f "$LAB06_VENV" ]; then
    source "$LAB06_VENV"
fi

echo "=== [1/7] Verifying RTL snapshot provenance (SHA-256) ==="
(cd "$PROJ_DIR/rtl/core" && sha256sum -c SHA256SUMS)

echo "=== [2/7] Baseline CPU regression ==="
if [ "${SKIP_30_BASELINE:-0}" -eq 1 ]; then
    bash "$PROJ_DIR/scripts/run_baseline_regression.sh" cpu cpuhaz cpuisa cpumembranch
else
    make baseline-test
fi

echo "=== [3/7] Monitor unit, lock-step equivalence & fault tests (B0, M0, M1, M2) ==="
make test CONFIG=b0
make test CONFIG=m0
make test CONFIG=m1
make test CONFIG=m2

echo "=== [4/7] Verilator lint (MONITOR_CFG=0..3) ==="
make lint

echo "=== [5/7] Formal bounded model checking (depth=25) ==="
make formal

echo "=== [6/7] Yosys synthesis (B0, M0, M1, M2) + stat parsing ==="
make synth CONFIG=all

echo "=== [7/7] Controlled fault-injection campaigns (smoke + full) & analysis ==="
make smoke
make campaign
if python3 -c "import matplotlib, pandas, numpy" 2>/dev/null; then
    make analyze
else
    echo "NOTE: matplotlib/pandas not in active Python; skipping figure regeneration (CSV/JSON verified)."
fi

echo "=== PipeGuard-RV end-to-end reproduction COMPLETE ==="
