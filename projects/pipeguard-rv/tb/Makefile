# PipeGuard-RV — Phase 2+ testbench Makefile
#
# Runs lockstep equivalence and monitor tests using cocotb + iverilog.
# Usage (from WSL with cocotb venv active):
#   make SUITE=b0_equiv

SIM            ?= icarus
TOPLEVEL_LANG  := verilog
SUITE          ?= b0_equiv

THIS_DIR := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
PROJ_DIR := $(abspath $(THIS_DIR)/..)
CORE     := $(PROJ_DIR)/rtl/core
COMMON   := $(PROJ_DIR)/rtl/common
TOP      := $(PROJ_DIR)/rtl/top
MON      := $(PROJ_DIR)/rtl/monitors
TB_HDL   := $(THIS_DIR)/hdl
TB_COM   := $(THIS_DIR)/common

CORE_SRCS := \
	$(CORE)/program_counter.sv \
	$(CORE)/instruction_memory.sv \
	$(CORE)/instruction_fetch.sv \
	$(CORE)/if_id_register.sv \
	$(CORE)/rv32i_decoder.sv \
	$(CORE)/immediate_generator.sv \
	$(CORE)/register_file.sv \
	$(CORE)/if_id_stage.sv \
	$(CORE)/id_ex_register.sv \
	$(CORE)/alu.sv \
	$(CORE)/alu_control.sv \
	$(CORE)/branch_unit.sv \
	$(CORE)/forwarding_unit.sv \
	$(CORE)/hazard_detection_unit.sv \
	$(CORE)/pipeline_control.sv \
	$(CORE)/execute_forwarding_stage.sv \
	$(CORE)/ex_mem_register.sv \
	$(CORE)/data_memory.sv \
	$(CORE)/memory_stage.sv \
	$(CORE)/mem_wb_register.sv \
	$(CORE)/writeback_stage.sv \
	$(CORE)/riscv_pipeline_cpu.sv

COMMON_SRCS :=
TOP_SRCS    := $(TOP)/riscv_pipeline_cpu_obs.sv $(TOP)/pipeguard_cpu.sv
COMPILE_ARGS += -I$(COMMON)

ifeq ($(SUITE),b0_equiv)
  VERILOG_SOURCES     := $(CORE_SRCS) $(COMMON_SRCS) $(TOP_SRCS) $(TB_HDL)/tb_lockstep.sv
  COCOTB_TOPLEVEL     := tb_lockstep
  COCOTB_TEST_MODULES := test_b0_equivalence
  COMPILE_ARGS        += -Ptb_lockstep.MONITOR_CFG=0
else
  $(error Unknown SUITE=$(SUITE))
endif

SIM_BUILD           := $(THIS_DIR)/sim_build/$(SUITE)
COCOTB_RESULTS_FILE := $(THIS_DIR)/results/$(SUITE).xml

export PYTHONPATH := $(THIS_DIR):$(TB_COM):$(PYTHONPATH)

include $(shell cocotb-config --makefiles)/Makefile.sim
