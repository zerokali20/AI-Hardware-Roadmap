#!/usr/bin/env bash
# PipeGuard-RV — Bounded Model Checking (BMC) runner for M0, M1, M2
#
# Uses Yosys's built-in formal SAT engine (`sat -seq <depth> -set-assumes
# -prove-asserts -verify`), matching Lab 05's formal flow, so proofs run fast
# without requiring the optional `sby` frontend. Equivalent SymbiYosys `.sby`
# configs (m0.sby, m1.sby, m2.sby) are kept alongside for sby-equipped hosts.
#
# Usage: bash formal/run_formal.sh [m0|m1|m2|all] [depth]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJ_DIR="$(dirname "$SCRIPT_DIR")"
TARGET="${1:-all}"
DEPTH="${2:-25}"
WORKDIR="$SCRIPT_DIR/workdir"

command -v yosys >/dev/null || { echo "ERROR: yosys not found"; exit 2; }
mkdir -p "$WORKDIR"

# Yosys >= 0.36 emits edge-triggered $check cells that require `async2sync`
# followed by `chformal -lower` before `sat` can import them. Yosys 0.33 emits
# $assert/$assume directly and does not have `-lower`.
LOWER_CMD=""
if yosys -Q -p "help chformal" 2>/dev/null | grep -q -- "-lower"; then
    LOWER_CMD="async2sync; chformal -lower"
fi

run_one() {
    local cfg="$1"
    local mon_sv="$2"
    local top="$3"

    for mode in 0 1; do
        local tag="invariants"
        if [ "$mode" -eq 1 ]; then tag="clean"; fi
        local log="$WORKDIR/${cfg}_${tag}_sat.log"

        echo "=== Formal BMC: ${cfg} (${tag}, ASSUME_CLEAN=${mode}, depth=${DEPTH}) ==="
        yosys -Q -T -l "$log" -p "
            read_verilog -sv -formal -I${PROJ_DIR}/rtl/common ${PROJ_DIR}/rtl/monitors/${mon_sv} ${SCRIPT_DIR}/${top}.sv
            chparam -set ASSUME_CLEAN ${mode} ${top}
            prep -top ${top}
            ${LOWER_CMD}
            flatten
            opt
            sat -seq ${DEPTH} -set-assumes -prove-asserts -verify -timeout 60
        " | grep -E "SAT proof|SUCCESS|ERROR|FAIL|Time spent" || true
        grep -q "SAT proof finished - no model found: SUCCESS!" "$log"
        echo "PASS: ${cfg}_${tag} (depth=${DEPTH})"
    done
}

case "$TARGET" in
    m0) run_one m0 pc_monitor.sv m0_formal ;;
    m1) run_one m1 branch_monitor.sv m1_formal ;;
    m2) run_one m2 pipeline_monitor.sv m2_formal ;;
    all)
        run_one m0 pc_monitor.sv m0_formal
        run_one m1 branch_monitor.sv m1_formal
        run_one m2 pipeline_monitor.sv m2_formal
        ;;
    *)
        echo "ERROR: unknown formal config '$TARGET' (use m0, m1, m2, or all)"
        exit 1
        ;;
esac

echo "=== All requested formal BMC checks PASSED (depth=${DEPTH}) ==="
