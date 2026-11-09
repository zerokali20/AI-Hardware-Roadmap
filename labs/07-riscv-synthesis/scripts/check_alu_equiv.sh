
#!/usr/bin/env bash
set -euo pipefail

mkdir -p reports

echo "===================================="
echo " ALU RTL vs Netlist Equivalence Check"
echo "===================================="

yosys -l reports/alu_equivalence.log -p '
    read_verilog -sv rtl/alu.sv
    proc
    flatten
    opt
    design -stash gold

    design -reset
    read_verilog netlist/alu_synth.v
    proc
    flatten
    opt
    design -stash gate

    design -reset
    design -copy-from gold -as gold alu
    design -copy-from gate -as gate alu

    equiv_make gold gate equiv
    hierarchy -top equiv
    equiv_simple
    equiv_status -assert
'

echo
echo "PASS: ALU RTL and synthesized netlist are equivalent."
