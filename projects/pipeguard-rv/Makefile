# PipeGuard-RV — Project Makefile
#
# Primary interface for simulation, linting, synthesis, formal verification,
# and analysis. Run inside WSL (Icarus Verilog, Verilator, Yosys, SymbiYosys).
#
# Phase status:
#   Phase 0: COMPLETE (audit)
#   Phase 1: COMPLETE (26-file baseline snapshot + 30-suite/319-test regression)
#   Phase 2: COMPLETE (B0 observation top, lockstep equivalence, lint, synthesis)
#   Phase 3: COMPLETE (M0 pc_monitor, unit + fault-inject + lockstep, synthesis)
#   Phase 4: COMPLETE (M1 branch_monitor & M2 pipeline_monitor, tests, synthesis)
#   Phase 5: COMPLETE (Bounded model checking via yosys-smtbmc + Z3, depth 25)
#   Phase 6+: TODO (fault campaign, analysis, reproducibility)

SHELL      := /usr/bin/env bash
PROJECT    := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
LAB06_VENV := $(abspath $(PROJECT)/../../labs/06-riscv-pipeline/.venv/bin/activate)
TB_DIR     := $(PROJECT)/tb
RESULTS    := $(PROJECT)/results
SYNTH_DIR  := $(PROJECT)/synthesis

CONFIG ?= b0

.PHONY: all help baseline-test test monitor-test smoke lint formal synth analyze reproduce clean

all: help

help:
	@echo "PipeGuard-RV Makefile"
	@echo "====================="
	@echo ""
	@echo "Available now (Phase 0–2):"
	@echo "  baseline-test   Run all 30 Lab 06 suites against rtl/core snapshot (319 tests)"
	@echo "  test            Run project tests for CONFIG=$(CONFIG) (b0 supported)"
	@echo "  smoke           Run quick baseline + B0 lockstep equivalence"
	@echo "  lint            Run Verilator lint on pipeguard_cpu"
	@echo "  synth           Run Yosys synthesis for CONFIG=$(CONFIG) (b0 supported)"
	@echo "  clean           Remove sim_build/, __pycache__, *.vcd, *.vvp, *.fst"
	@echo ""
	@echo "Later phases (will fail until implemented):"
	@echo "  monitor-test    Phase 3+ (M0/M1/M2 unit and integration tests)"
	@echo "  formal          Phase 5  (SymbiYosys BMC)"
	@echo "  analyze         Phase 8  (Analysis and figure generation)"
	@echo "  reproduce       Phase 9  (Full end-to-end reproduction)"

## baseline-test: Run all 30 Lab 06 suites against the rtl/core snapshot
baseline-test:
	@echo "=== PipeGuard-RV: Snapshot Baseline Regression (30 suites) ==="
	bash -c 'if [ -f "$(LAB06_VENV)" ]; then source "$(LAB06_VENV)"; fi; \
	         bash "$(PROJECT)/scripts/run_baseline_regression.sh"'

## test: Run project tests for CONFIG=<b0|m0|m1|m2>
test:
ifeq ($(CONFIG),b0)
	@echo "=== PipeGuard-RV: B0 Lock-Step Equivalence ==="
	bash -c 'if [ -f "$(LAB06_VENV)" ]; then source "$(LAB06_VENV)"; fi; \
	         mkdir -p "$(TB_DIR)/results"; \
	         rm -rf "$(TB_DIR)/sim_build/b0_equiv" "$(TB_DIR)/results/b0_equiv.xml"; \
	         make -C "$(TB_DIR)" SUITE=b0_equiv && \
	         python3 "$(PROJECT)/scripts/check_results.py" "$(TB_DIR)/results/b0_equiv.xml"'
else ifeq ($(CONFIG),m0)
	$(MAKE) monitor-test CONFIG=m0
	@echo "=== PipeGuard-RV: M0 Lock-Step & Fault-Injection ==="
	bash -c 'if [ -f "$(LAB06_VENV)" ]; then source "$(LAB06_VENV)"; fi; \
	         mkdir -p "$(TB_DIR)/results"; \
	         rm -rf "$(TB_DIR)/sim_build/m0_equiv" "$(TB_DIR)/results/m0_equiv.xml"; \
	         make -C "$(TB_DIR)" SUITE=m0_equiv && \
	         python3 "$(PROJECT)/scripts/check_results.py" "$(TB_DIR)/results/m0_equiv.xml"'
else ifeq ($(CONFIG),m1)
	$(MAKE) monitor-test CONFIG=m1
	@echo "=== PipeGuard-RV: M1 Lock-Step & Fault-Injection ==="
	bash -c 'if [ -f "$(LAB06_VENV)" ]; then source "$(LAB06_VENV)"; fi; \
	         mkdir -p "$(TB_DIR)/results"; \
	         rm -rf "$(TB_DIR)/sim_build/m1_equiv" "$(TB_DIR)/results/m1_equiv.xml"; \
	         make -C "$(TB_DIR)" SUITE=m1_equiv && \
	         python3 "$(PROJECT)/scripts/check_results.py" "$(TB_DIR)/results/m1_equiv.xml"'
else ifeq ($(CONFIG),m2)
	$(MAKE) monitor-test CONFIG=m2
	@echo "=== PipeGuard-RV: M2 Lock-Step & Fault-Injection ==="
	bash -c 'if [ -f "$(LAB06_VENV)" ]; then source "$(LAB06_VENV)"; fi; \
	         mkdir -p "$(TB_DIR)/results"; \
	         rm -rf "$(TB_DIR)/sim_build/m2_equiv" "$(TB_DIR)/results/m2_equiv.xml"; \
	         make -C "$(TB_DIR)" SUITE=m2_equiv && \
	         python3 "$(PROJECT)/scripts/check_results.py" "$(TB_DIR)/results/m2_equiv.xml"'
else
	@echo "ERROR: Unknown CONFIG=$(CONFIG) (expected b0, m0, m1, or m2)"
	@exit 1
endif

## smoke: Quick CPU baseline suites + B0 lockstep equivalence
smoke:
	bash -c 'if [ -f "$(LAB06_VENV)" ]; then source "$(LAB06_VENV)"; fi; \
	         bash "$(PROJECT)/scripts/run_baseline_regression.sh" cpu cpuhaz cpuisa cpumembranch'
	$(MAKE) test CONFIG=b0

## lint: Run Verilator lint on pipeguard_cpu (B0, M0, M1, M2)
lint:
	cd $(PROJECT) && for cfg in 0 1 2 3; do \
	  verilator --lint-only -Wall -Wno-UNUSEDSIGNAL -Wno-WIDTHEXPAND \
	    -Irtl/common -GMONITOR_CFG=$$cfg --top-module pipeguard_cpu \
	    rtl/core/program_counter.sv rtl/core/instruction_memory.sv rtl/core/instruction_fetch.sv \
	    rtl/core/if_id_register.sv rtl/core/rv32i_decoder.sv rtl/core/immediate_generator.sv \
	    rtl/core/register_file.sv rtl/core/if_id_stage.sv rtl/core/id_ex_register.sv \
	    rtl/core/alu.sv rtl/core/alu_control.sv rtl/core/branch_unit.sv \
	    rtl/core/forwarding_unit.sv rtl/core/hazard_detection_unit.sv rtl/core/pipeline_control.sv \
	    rtl/core/execute_forwarding_stage.sv rtl/core/ex_mem_register.sv \
	    rtl/core/data_memory.sv rtl/core/memory_stage.sv rtl/core/mem_wb_register.sv \
	    rtl/core/writeback_stage.sv rtl/monitors/pc_monitor.sv \
	    rtl/monitors/branch_monitor.sv rtl/monitors/pipeline_monitor.sv \
	    rtl/top/riscv_pipeline_cpu_obs.sv rtl/top/pipeguard_cpu.sv || exit 1; \
	done

## synth: Yosys synthesis for CONFIG=<b0|m0|m1|m2>
synth:
ifeq ($(CONFIG),b0)
	@echo "=== PipeGuard-RV: Yosys Synthesis (CONFIG=b0) ==="
	mkdir -p $(RESULTS)/synthesis
	cd $(PROJECT) && MONITOR_CFG=0 CFG_NAME=b0 OUT_DIR=results/synthesis \
	  yosys -Q -l results/synthesis/b0_synth.log -c synthesis/synth.tcl
else ifeq ($(CONFIG),m0)
	@echo "=== PipeGuard-RV: Yosys Synthesis (CONFIG=m0) ==="
	mkdir -p $(RESULTS)/synthesis
	cd $(PROJECT) && MONITOR_CFG=1 CFG_NAME=m0 OUT_DIR=results/synthesis \
	  yosys -Q -l results/synthesis/m0_synth.log -c synthesis/synth.tcl
else ifeq ($(CONFIG),m1)
	@echo "=== PipeGuard-RV: Yosys Synthesis (CONFIG=m1) ==="
	mkdir -p $(RESULTS)/synthesis
	cd $(PROJECT) && MONITOR_CFG=2 CFG_NAME=m1 OUT_DIR=results/synthesis \
	  yosys -Q -l results/synthesis/m1_synth.log -c synthesis/synth.tcl
else ifeq ($(CONFIG),m2)
	@echo "=== PipeGuard-RV: Yosys Synthesis (CONFIG=m2) ==="
	mkdir -p $(RESULTS)/synthesis
	cd $(PROJECT) && MONITOR_CFG=3 CFG_NAME=m2 OUT_DIR=results/synthesis \
	  yosys -Q -l results/synthesis/m2_synth.log -c synthesis/synth.tcl
else
	@echo "ERROR: Unknown CONFIG=$(CONFIG) (expected b0, m0, m1, or m2)"
	@exit 1
endif

monitor-test:
ifeq ($(CONFIG),m0)
	@echo "=== PipeGuard-RV: M0 pc_monitor Unit Tests ==="
	bash -c 'if [ -f "$(LAB06_VENV)" ]; then source "$(LAB06_VENV)"; fi; \
	         mkdir -p "$(TB_DIR)/results"; \
	         rm -rf "$(TB_DIR)/sim_build/pc_mon" "$(TB_DIR)/results/pc_mon.xml"; \
	         make -C "$(TB_DIR)" SUITE=pc_mon && \
	         python3 "$(PROJECT)/scripts/check_results.py" "$(TB_DIR)/results/pc_mon.xml"'
else ifeq ($(CONFIG),m1)
	@echo "=== PipeGuard-RV: M1 branch_monitor Unit Tests ==="
	bash -c 'if [ -f "$(LAB06_VENV)" ]; then source "$(LAB06_VENV)"; fi; \
	         mkdir -p "$(TB_DIR)/results"; \
	         rm -rf "$(TB_DIR)/sim_build/branch_mon" "$(TB_DIR)/results/branch_mon.xml"; \
	         make -C "$(TB_DIR)" SUITE=branch_mon && \
	         python3 "$(PROJECT)/scripts/check_results.py" "$(TB_DIR)/results/branch_mon.xml"'
else ifeq ($(CONFIG),m2)
	@echo "=== PipeGuard-RV: M2 pipeline_monitor Unit Tests ==="
	bash -c 'if [ -f "$(LAB06_VENV)" ]; then source "$(LAB06_VENV)"; fi; \
	         mkdir -p "$(TB_DIR)/results"; \
	         rm -rf "$(TB_DIR)/sim_build/pipe_mon" "$(TB_DIR)/results/pipe_mon.xml"; \
	         make -C "$(TB_DIR)" SUITE=pipe_mon && \
	         python3 "$(PROJECT)/scripts/check_results.py" "$(TB_DIR)/results/pipe_mon.xml"'
else
	@echo "ERROR: Unknown CONFIG=$(CONFIG) for monitor-test (expected m0, m1, or m2)"
	@exit 1
endif

formal:
	@echo "=== PipeGuard-RV: Formal Verification (Yosys SAT BMC, depth=25, CONFIG=$(CONFIG)) ==="
ifeq ($(CONFIG),b0)
	bash $(PROJECT)/formal/run_formal.sh all 25
else
	bash $(PROJECT)/formal/run_formal.sh $(CONFIG) 25
endif

analyze:
	@echo "ERROR: 'make analyze' — NOT YET IMPLEMENTED (requires Phase 8)"
	@exit 1

reproduce:
	@echo "ERROR: 'make reproduce' — NOT YET IMPLEMENTED (requires Phase 9)"
	@exit 1

clean:
	@echo "=== Cleaning PipeGuard-RV build artefacts ==="
	rm -rf $(TB_DIR)/sim_build $(TB_DIR)/results $(TB_DIR)/baseline/sim_build \
	       $(TB_DIR)/baseline/results $(TB_DIR)/baseline/logs $(PROJECT)/sim_build $(PROJECT)/build
	find $(PROJECT) -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	find $(PROJECT) -name "*.pyc" -delete 2>/dev/null || true
	find $(PROJECT) -name "*.vcd" -delete 2>/dev/null || true
	find $(PROJECT) -name "*.vvp" -delete 2>/dev/null || true
	find $(PROJECT) -name "*.fst" -delete 2>/dev/null || true
