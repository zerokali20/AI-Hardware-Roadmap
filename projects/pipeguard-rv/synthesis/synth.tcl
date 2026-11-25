# PipeGuard-RV — Yosys synthesis script
#
# Reuses Lab 07's synthesis flow (`synth -top pipeguard_cpu -noabc`) so cell
# counts are directly comparable across configurations (B0, M0, M1, M2).
#
# Expected environment variables (passed via Makefile):
#   MONITOR_CFG  : 0 (B0), 1 (M0), 2 (M1), 3 (M2)
#   CFG_NAME     : b0 | m0 | m1 | m2
#   OUT_DIR      : output directory for netlist JSON and stat report

yosys -import

set cfg      $::env(MONITOR_CFG)
set cfg_name $::env(CFG_NAME)
set out_dir  $::env(OUT_DIR)

# Read core RTL (excluding unused standalone stage/integration variants that
# duplicate module hierarchies or are simulation-only, matching Lab 06 CPU_ALL)
read_verilog -sv -I rtl/common rtl/core/program_counter.sv
read_verilog -sv rtl/core/instruction_memory.sv
read_verilog -sv rtl/core/instruction_fetch.sv
read_verilog -sv rtl/core/if_id_register.sv
read_verilog -sv rtl/core/rv32i_decoder.sv
read_verilog -sv rtl/core/immediate_generator.sv
read_verilog -sv rtl/core/register_file.sv
read_verilog -sv rtl/core/if_id_stage.sv
read_verilog -sv rtl/core/id_ex_register.sv
read_verilog -sv rtl/core/alu.sv
read_verilog -sv rtl/core/alu_control.sv
read_verilog -sv rtl/core/branch_unit.sv
read_verilog -sv rtl/core/forwarding_unit.sv
read_verilog -sv rtl/core/hazard_detection_unit.sv
read_verilog -sv rtl/core/pipeline_control.sv
read_verilog -sv rtl/core/execute_forwarding_stage.sv
read_verilog -sv rtl/core/ex_mem_register.sv
read_verilog -sv rtl/core/data_memory.sv
read_verilog -sv rtl/core/memory_stage.sv
read_verilog -sv rtl/core/mem_wb_register.sv
read_verilog -sv rtl/core/writeback_stage.sv
read_verilog -sv -I rtl/common rtl/monitors/pc_monitor.sv
read_verilog -sv -I rtl/common rtl/monitors/branch_monitor.sv
read_verilog -sv -I rtl/common rtl/monitors/pipeline_monitor.sv
read_verilog -sv -I rtl/common rtl/top/riscv_pipeline_cpu_obs.sv
read_verilog -sv -I rtl/common rtl/top/pipeguard_cpu.sv

chparam -set MONITOR_CFG $cfg pipeguard_cpu
hierarchy -check -top pipeguard_cpu
synth -top pipeguard_cpu -noabc
check
tee -o ${out_dir}/${cfg_name}_stat.txt stat
write_json ${out_dir}/${cfg_name}_netlist.json
