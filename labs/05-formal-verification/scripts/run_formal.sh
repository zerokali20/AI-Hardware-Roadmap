
#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
mkdir -p build

echo "================================="
echo "Lab 05: Formal Verification"
echo "================================="

echo "[1/2] Verifying ALU..."

yosys -Q -T -l build/alu_formal.log -p "
read_verilog -formal -sv rtl/alu.sv formal/alu_properties.sv
prep -top alu_properties -flatten
sat -verify -prove-asserts -timeout 60
"

echo "[PASS] ALU formal verification"

echo "[2/2] Verifying register file..."

yosys -Q -T -l build/register_formal.log -p "
read_verilog -formal -sv rtl/register_file.sv formal/register_file_properties.sv
prep -top register_file_properties -flatten
memory_map
opt_clean
sat -seq 10 -tempinduct -set-assumes -prove-asserts -verify -timeout 60
"

echo "[PASS] Register-file induction proof"
echo "================================="
echo "All formal verification checks PASSED"
echo "================================="

