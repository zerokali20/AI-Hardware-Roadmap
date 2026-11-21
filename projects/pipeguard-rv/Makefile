# PipeGuard-RV — Project Makefile
#
# Primary interface for simulation, synthesis, formal verification, and analysis.
# Most targets require WSL (Icarus Verilog, Yosys, SymbiYosys run under Linux).
# Run from Windows: `wsl -e bash -c "make <target>"` or open a WSL terminal.
#
# Phase status:
#   Phase 0: COMPLETE (audit)
#   Phase 1: IN PROGRESS (baseline snapshot)
#   Phase 2+: TODO (B0 wrapper, monitors, formal, campaign)

LAB06_DIR  := /mnt/d/AI-Hardware-Roadmap/labs/06-riscv-pipeline
PROJECT    := /mnt/d/AI-Hardware-Roadmap/projects/pipeguard-rv
RTL_CORE   := $(PROJECT)/rtl/core
RTL_MON    := $(PROJECT)/rtl/monitors
RTL_TOP    := $(PROJECT)/rtl/top
TB_DIR     := $(PROJECT)/tb
RESULTS    := $(PROJECT)/results
SYNTH_DIR  := $(PROJECT)/synthesis
FORMAL_DIR := $(PROJECT)/formal

CONFIG ?= b0

.PHONY: all test baseline-test monitor-test smoke formal synth analyze reproduce clean help

## Default target — show help
all: help

## help: Show available targets
help:
	@echo "PipeGuard-RV Makefile"
	@echo "====================="
	@echo ""
	@echo "Baseline (Phase 0/1 — available now):"
	@echo "  baseline-test   Run Lab 06 regression suites (cpu, cpuhaz, cpuisa, cpumembranch)"
	@echo ""
	@echo "Research targets (Phase 2+ required — will print NOT YET IMPLEMENTED):"
	@echo "  test            Run all project tests for CONFIG=<b0|m0|m1|m2>"
	@echo "  monitor-test    Run monitor-specific unit and integration tests"
	@echo "  smoke           Run fault-injection smoke campaign (10 faults x 4 workloads)"
	@echo "  formal          Run SymbiYosys BMC for CONFIG=<b0|m0|m1|m2>"
	@echo "  synth           Run Yosys synthesis for CONFIG=<b0|m0|m1|m2>"
	@echo "  analyze         Process results/ and generate figures"
	@echo "  reproduce       Re-run full campaign from scratch and compare results"
	@echo "  clean           Remove sim_build/, __pycache__, *.vcd, *.vvp, build/"
	@echo ""
	@echo "Examples:"
	@echo "  make baseline-test"
	@echo "  make synth CONFIG=m0"
	@echo "  make formal CONFIG=m1"

## baseline-test: Run the four verified Lab 06 regression suites (Phase 0/1 verified)
## Requires WSL with Lab 06 .venv activated.
baseline-test:
	@echo "=== PipeGuard-RV: Lab 06 Baseline Regression ==="
	@echo "Baseline SHA: 0be8905 | cocotb 2.1.0 | iverilog 12.0"
	@echo ""
	@echo "--- Suite: cpu (5 tests) ---"
	cd $(LAB06_DIR) && source .venv/bin/activate && make clean && make TEST=cpu
	@echo ""
	@echo "--- Suite: cpuhaz (7 tests) ---"
	cd $(LAB06_DIR) && source .venv/bin/activate && make clean && make TEST=cpuhaz
	@echo ""
	@echo "--- Suite: cpuisa (6 tests) ---"
	cd $(LAB06_DIR) && source .venv/bin/activate && make clean && make TEST=cpuisa
	@echo ""
	@echo "--- Suite: cpumembranch (15 tests) ---"
	cd $(LAB06_DIR) && source .venv/bin/activate && make clean && make TEST=cpumembranch
	@echo ""
	@echo "=== Baseline complete: expected 33/33 PASS ==="

## test: Run all project tests for a given CONFIG (Phase 2+ required)
test:
	@echo "ERROR: 'make test CONFIG=$(CONFIG)' — NOT YET IMPLEMENTED"
	@echo "       Requires Phase 2 (B0 wrapper) or later."
	@echo "       See IMPLEMENTATION_PLAN.md Phase 2–4."
	@exit 1

## monitor-test: Run monitor-specific tests (Phase 3+ required)
monitor-test:
	@echo "ERROR: 'make monitor-test CONFIG=$(CONFIG)' — NOT YET IMPLEMENTED"
	@echo "       Requires Phase 3 (M0 PC monitor) or later."
	@echo "       See IMPLEMENTATION_PLAN.md Phase 3."
	@exit 1

## smoke: Fault injection smoke campaign (Phase 6 required)
smoke:
	@echo "ERROR: 'make smoke CONFIG=$(CONFIG)' — NOT YET IMPLEMENTED"
	@echo "       Requires Phase 6 (Fault Injection Campaign)."
	@echo "       See IMPLEMENTATION_PLAN.md Phase 6."
	@exit 1

## formal: SymbiYosys formal verification — BMC (Phase 5 required)
formal:
	@echo "ERROR: 'make formal CONFIG=$(CONFIG)' — NOT YET IMPLEMENTED"
	@echo "       Requires Phase 5 (Formal Verification)."
	@echo "       Yosys 0.33 + SymbiYosys must be installed in WSL."
	@echo "       See IMPLEMENTATION_PLAN.md Phase 5."
	@exit 1

## synth: Yosys synthesis and area report (Phase 2 required for B0 baseline)
synth:
	@echo "ERROR: 'make synth CONFIG=$(CONFIG)' — NOT YET IMPLEMENTED"
	@echo "       Requires Phase 2 (B0 wrapper RTL) for CONFIG=b0,"
	@echo "       or Phase 3–4 for monitor configs."
	@echo "       See IMPLEMENTATION_PLAN.md Phase 7."
	@exit 1

## analyze: Process raw results and generate figures (Phase 8 required)
analyze:
	@echo "ERROR: 'make analyze' — NOT YET IMPLEMENTED"
	@echo "       Requires Phase 8 (Analysis and Paper Draft)."
	@echo "       Needs results/raw/fault_campaign_*.csv from Phase 6."
	@echo "       See IMPLEMENTATION_PLAN.md Phase 8."
	@exit 1

## reproduce: Full end-to-end reproduction run (Phase 9 required)
reproduce:
	@echo "ERROR: 'make reproduce' — NOT YET IMPLEMENTED"
	@echo "       Requires Phase 9 (Reproducibility Package)."
	@echo "       See IMPLEMENTATION_PLAN.md Phase 9."
	@exit 1

## clean: Remove simulation build artefacts
clean:
	@echo "=== Cleaning PipeGuard-RV build artefacts ==="
	rm -rf $(PROJECT)/sim_build
	rm -rf $(PROJECT)/build
	find $(PROJECT) -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	find $(PROJECT) -name "*.pyc"  -delete 2>/dev/null || true
	find $(PROJECT) -name "*.vcd"  -delete 2>/dev/null || true
	find $(PROJECT) -name "*.vvp"  -delete 2>/dev/null || true
	find $(PROJECT) -name "*.fst"  -delete 2>/dev/null || true
	@echo "Clean complete."
