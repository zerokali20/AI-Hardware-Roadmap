# PipeGuard-RV — baseline snapshot regression (Phase 1)
#
# Runs the UNMODIFIED Lab 06 cocotb testbenches (labs/06-riscv-pipeline/tb)
# against the project-local RTL snapshot in projects/pipeguard-rv/rtl/core.
# The Lab 06 tree is only read; nothing is written into it.
#
# Usage (WSL, from this directory, with a cocotb venv active):
#   make SUITE=cpu
# The suite -> (toplevel, module, sources) mapping mirrors
# labs/06-riscv-pipeline/Makefile at commit 4b7643e. Every suite is compiled
# from the snapshot sources only, and every suite gets its own SIM_BUILD
# directory so a stale build of another toplevel can never be reused
# (the Phase 0 `pipectrl` infrastructure error).

SIM            ?= icarus
TOPLEVEL_LANG  := verilog
SUITE          ?= cpu

THIS_DIR  := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
PROJ_DIR  := $(abspath $(THIS_DIR)/../..)
CORE      := $(PROJ_DIR)/rtl/core
LAB06_TB  := $(abspath $(PROJ_DIR)/../../labs/06-riscv-pipeline/tb)

c = $(addprefix $(CORE)/,$(1))

FETCH   := program_counter.sv instruction_memory.sv instruction_fetch.sv
FRONT   := $(FETCH) if_id_register.sv rv32i_decoder.sv immediate_generator.sv register_file.sv if_id_stage.sv
EXEC    := id_ex_register.sv alu_control.sv alu.sv branch_unit.sv
CPU_ALL := $(FRONT) id_ex_register.sv alu.sv alu_control.sv branch_unit.sv forwarding_unit.sv \
           hazard_detection_unit.sv pipeline_control.sv execute_forwarding_stage.sv ex_mem_register.sv \
           data_memory.sv memory_stage.sv mem_wb_register.sv writeback_stage.sv riscv_pipeline_cpu.sv

# Lab 06 compiles cpuisa / cpumembranch / cpuperf from $(wildcard rtl/*.sv);
# mirror that with every snapshot source file.
ALL_CORE := $(notdir $(wildcard $(CORE)/*.sv))

ifeq ($(SUITE),pc)
  SRC := program_counter.sv
  COCOTB_TOPLEVEL := program_counter
  COCOTB_TEST_MODULES := test_program_counter
else ifeq ($(SUITE),if)
  SRC := $(FETCH)
  COCOTB_TOPLEVEL := instruction_fetch
  COCOTB_TEST_MODULES := test_instruction_fetch
else ifeq ($(SUITE),ifid)
  SRC := if_id_register.sv
  COCOTB_TOPLEVEL := if_id_register
  COCOTB_TEST_MODULES := test_if_id_register
else ifeq ($(SUITE),decode)
  SRC := rv32i_decoder.sv
  COCOTB_TOPLEVEL := rv32i_decoder
  COCOTB_TEST_MODULES := test_rv32i_decoder
else ifeq ($(SUITE),imm)
  SRC := immediate_generator.sv
  COCOTB_TOPLEVEL := immediate_generator
  COCOTB_TEST_MODULES := test_immediate_generator
else ifeq ($(SUITE),regfile)
  SRC := register_file.sv
  COCOTB_TOPLEVEL := register_file
  COCOTB_TEST_MODULES := test_register_file
else ifeq ($(SUITE),ifidstage)
  SRC := $(FRONT)
  COCOTB_TOPLEVEL := if_id_stage
  COCOTB_TEST_MODULES := test_if_id_stage
else ifeq ($(SUITE),alu)
  SRC := alu.sv
  COCOTB_TOPLEVEL := alu
  COCOTB_TEST_MODULES := test_alu
else ifeq ($(SUITE),aluctrl)
  SRC := alu_control.sv
  COCOTB_TOPLEVEL := alu_control
  COCOTB_TEST_MODULES := test_alu_control
else ifeq ($(SUITE),idex)
  SRC := id_ex_register.sv
  COCOTB_TOPLEVEL := id_ex_register
  COCOTB_TEST_MODULES := test_id_ex_register
else ifeq ($(SUITE),execute)
  SRC := $(EXEC) execute_stage.sv
  COCOTB_TOPLEVEL := execute_stage
  COCOTB_TEST_MODULES := test_execute_stage
else ifeq ($(SUITE),branch)
  SRC := branch_unit.sv
  COCOTB_TOPLEVEL := branch_unit
  COCOTB_TEST_MODULES := test_branch_unit
else ifeq ($(SUITE),exbranch)
  SRC := $(EXEC) execute_stage.sv
  COCOTB_TOPLEVEL := execute_stage
  COCOTB_TEST_MODULES := test_execute_branch
else ifeq ($(SUITE),pipectrl)
  SRC := pipeline_control.sv
  COCOTB_TOPLEVEL := pipeline_control
  COCOTB_TEST_MODULES := test_pipeline_control
else ifeq ($(SUITE),pipeint)
  SRC := program_counter.sv if_id_register.sv id_ex_register.sv branch_unit.sv pipeline_control.sv pipeline_integration.sv
  COCOTB_TOPLEVEL := pipeline_integration
  COCOTB_TEST_MODULES := test_pipeline_integration
else ifeq ($(SUITE),exmem)
  SRC := ex_mem_register.sv
  COCOTB_TOPLEVEL := ex_mem_register
  COCOTB_TEST_MODULES := test_ex_mem_register
else ifeq ($(SUITE),dmem)
  SRC := data_memory.sv
  COCOTB_TOPLEVEL := data_memory
  COCOTB_TEST_MODULES := test_data_memory
else ifeq ($(SUITE),memstage)
  SRC := ex_mem_register.sv data_memory.sv memory_stage.sv
  COCOTB_TOPLEVEL := memory_stage
  COCOTB_TEST_MODULES := test_memory_stage
else ifeq ($(SUITE),memwb)
  SRC := mem_wb_register.sv
  COCOTB_TOPLEVEL := mem_wb_register
  COCOTB_TEST_MODULES := test_mem_wb_register
else ifeq ($(SUITE),wb)
  SRC := mem_wb_register.sv writeback_stage.sv
  COCOTB_TOPLEVEL := writeback_stage
  COCOTB_TEST_MODULES := test_writeback_stage
else ifeq ($(SUITE),wbint)
  SRC := mem_wb_register.sv writeback_stage.sv register_file.sv register_writeback_integration.sv
  COCOTB_TOPLEVEL := register_writeback_integration
  COCOTB_TEST_MODULES := test_register_writeback_integration
else ifeq ($(SUITE),forward)
  SRC := forwarding_unit.sv
  COCOTB_TOPLEVEL := forwarding_unit
  COCOTB_TEST_MODULES := test_forwarding_unit
else ifeq ($(SUITE),hazard)
  SRC := hazard_detection_unit.sv
  COCOTB_TOPLEVEL := hazard_detection_unit
  COCOTB_TEST_MODULES := test_hazard_detection_unit
else ifeq ($(SUITE),hazint)
  SRC := forwarding_unit.sv hazard_detection_unit.sv pipeline_control.sv hazard_forwarding_integration.sv
  COCOTB_TOPLEVEL := hazard_forwarding_integration
  COCOTB_TEST_MODULES := test_hazard_forwarding_integration
else ifeq ($(SUITE),exforward)
  SRC := id_ex_register.sv alu.sv alu_control.sv branch_unit.sv forwarding_unit.sv execute_forwarding_stage.sv
  COCOTB_TOPLEVEL := execute_forwarding_stage
  COCOTB_TEST_MODULES := test_execute_forwarding_stage
else ifeq ($(SUITE),cpu)
  SRC := $(CPU_ALL)
  COCOTB_TOPLEVEL := riscv_pipeline_cpu
  COCOTB_TEST_MODULES := test_riscv_pipeline_cpu
else ifeq ($(SUITE),cpuhaz)
  SRC := $(CPU_ALL)
  COCOTB_TOPLEVEL := riscv_pipeline_cpu
  COCOTB_TEST_MODULES := test_cpu_hazards
else ifeq ($(SUITE),cpuisa)
  SRC := $(ALL_CORE)
  COCOTB_TOPLEVEL := riscv_pipeline_cpu
  COCOTB_TEST_MODULES := test_cpu_rv32i
else ifeq ($(SUITE),cpumembranch)
  SRC := $(ALL_CORE)
  COCOTB_TOPLEVEL := riscv_pipeline_cpu
  COCOTB_TEST_MODULES := test_cpu_memory_branch
else ifeq ($(SUITE),cpuperf)
  SRC := $(ALL_CORE)
  COCOTB_TOPLEVEL := riscv_pipeline_cpu
  COCOTB_TEST_MODULES := test_cpu_performance
  COMPILE_ARGS += -DENABLE_PERF_MONITOR
else
  $(error Unknown SUITE=$(SUITE))
endif

VERILOG_SOURCES := $(call c,$(SRC))
SIM_BUILD       := $(THIS_DIR)/sim_build/$(SUITE)
COCOTB_RESULTS_FILE := $(THIS_DIR)/results/$(SUITE).xml

export PYTHONPATH := $(LAB06_TB):$(PYTHONPATH)

include $(shell cocotb-config --makefiles)/Makefile.sim
