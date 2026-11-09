
#!/usr/bin/env bash
set -euo pipefail

mkdir -p reports netlist

echo "======================================"
echo " RISC-V Five-Stage CPU Logic Synthesis"
echo "======================================"

if [[ ! -f programs/test_program.hex ]]; then
    echo "ERROR: programs/test_program.hex is missing."
    exit 1
fi

echo "Running Yosys synthesis..."

if yosys -Q -l reports/cpu_synthesis.log -p '
    read_verilog -sv rtl/cpu/*.sv
    hierarchy -check -top riscv_pipeline_cpu
    synth -top riscv_pipeline_cpu -noabc
    check
    stat
    write_verilog -noattr netlist/riscv_cpu_synth.v
'; then
    echo
    echo "PASS: CPU synthesis completed."
    echo "Netlist: netlist/riscv_cpu_synth.v"
    echo "Report:  reports/cpu_synthesis.log"
else
    echo
    echo "FAIL: CPU synthesis encountered an error."
    echo "Inspect reports/cpu_synthesis.log"
    exit 1
fi
