
#!/usr/bin/env bash
set -euo pipefail

mkdir -p reports

echo "=================================="
echo " RISC-V CPU Synthesis Audit"
echo "=================================="

yosys -l reports/cpu_audit.log -p '
    read_verilog -sv rtl/cpu/*.sv
    hierarchy -check -top riscv_pipeline_cpu
    proc
    opt
    check
    stat
'

echo
echo "CPU synthesis audit completed."
echo "Report: reports/cpu_audit.log"
