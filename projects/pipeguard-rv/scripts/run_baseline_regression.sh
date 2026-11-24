#!/usr/bin/env bash
# PipeGuard-RV — run the Lab 06 regression suites against the project-local
# RTL snapshot (rtl/core). Usage:  bash scripts/run_baseline_regression.sh [suite ...]
# With no arguments all 30 Lab 06 suites are run (cpuwave is excluded: it is a
# waveform-dump variant of `cpu`, not a separate suite in Lab 06's own script).
set -u
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJ_DIR="$(dirname "$SCRIPT_DIR")"
BASE_DIR="$PROJ_DIR/tb/baseline"

ALL_SUITES=(pc if ifid decode imm regfile ifidstage alu aluctrl idex execute
            branch exbranch pipectrl pipeint exmem dmem memstage memwb wb wbint
            forward hazard hazint exforward cpu cpuhaz cpuisa cpumembranch cpuperf)
if [ "$#" -gt 0 ]; then SUITES=("$@"); else SUITES=("${ALL_SUITES[@]}"); fi

command -v cocotb-config >/dev/null || { echo "ERROR: cocotb not on PATH (activate a venv; see scripts/setup.sh)"; exit 2; }
command -v iverilog      >/dev/null || { echo "ERROR: iverilog not found"; exit 2; }

mkdir -p "$BASE_DIR/results" "$BASE_DIR/logs"
XMLS=()
for s in "${SUITES[@]}"; do
    rm -rf "$BASE_DIR/sim_build/$s" "$BASE_DIR/results/$s.xml"
    echo "Running suite $s ..."
    make -C "$BASE_DIR" SUITE="$s" > "$BASE_DIR/logs/$s.log" 2>&1 || echo "  make exited non-zero for $s (see tb/baseline/logs/$s.log)"
    XMLS+=("$BASE_DIR/results/$s.xml")
done

python3 "$SCRIPT_DIR/check_results.py" --summary "$PROJ_DIR/results/processed/baseline_regression_summary.csv" "${XMLS[@]}"
