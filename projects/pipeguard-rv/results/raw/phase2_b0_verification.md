# Phase 2 Verification Report — Snapshot Regression & B0 Lock-Step Equivalence

| Field | Value |
|---|---|
| **Date** | 2026-11-24 |
| **Simulator** | Icarus Verilog 12.0 (stable) + cocotb 2.1.0 |
| **Linter** | Verilator 5.020 |
| **Snapshot RTL** | `projects/pipeguard-rv/rtl/core/*.sv` (26 files, SHA-256 verified against `labs/06-riscv-pipeline/rtl/`) |

## 1. Project-Local Snapshot Regression (30 Suites)

Executed via `bash scripts/run_baseline_regression.sh` using `tb/baseline/Makefile` (per-suite isolated `sim_build/<suite>` and strict JUnit XML verification via `scripts/check_results.py`).

- **Suites run:** 30 / 30 (`pc`, `if`, `ifid`, `decode`, `imm`, `regfile`, `ifidstage`, `alu`, `aluctrl`, `idex`, `execute`, `branch`, `exbranch`, `pipectrl`, `pipeint`, `exmem`, `dmem`, `memstage`, `memwb`, `wb`, `wbint`, `forward`, `hazard`, `hazint`, `exforward`, `cpu`, `cpuhaz`, `cpuisa`, `cpumembranch`, `cpuperf`)
- **Total individual tests:** **319** (`PASS=319`, `FAIL=0`, `SKIP=0`)
- **Summary CSV:** `results/processed/baseline_regression_summary.csv`
- **Note vs. Lab 06 README:** Lab 06 README reports 329 tests across 30 suites; running the unmodified Lab 06 testbenches against the identical RTL snapshot on this machine yields **319** tests across 30 suites (all passing).

## 2. B0 Lock-Step Equivalence (`tb/test_b0_equivalence.py`)

Executed via `make -C tb SUITE=b0_equiv` (`tb_lockstep` instantiating `riscv_pipeline_cpu` alongside `pipeguard_cpu #(.MONITOR_CFG(0))`):

- `test_b0_directed_lockstep`: **PASS** — 15 directed programs (`sequential`, `branch_taken_forward`, `branch_not_taken`, `backward_loop`, `jal_jalr_call_return`, `load_use_hazard`, `forwarding_chain`, `load_then_branch`, `flush_squash`, `real_nops`, `consecutive_branches`, `signed_branches`, `lui_auipc`, `misaligned_jalr_target`, `misaligned_load`).
- `test_b0_random_lockstep`: **PASS** — 10 seeded-random 48-instruction RV32I programs (`seed=0..9`, 200 cycles each).
- **Result:** `TESTS=2 PASS=2 FAIL=0 SKIP=0` (cycle-for-cycle match on all 14 CPU outputs, final `x0..x31`, final `data_memory`, and `fault_detected=0`, `fault_sticky=0`, `fault_class=0`).

## 3. Verilator Lint

Executed `verilator --lint-only -Wall -Wno-UNUSEDSIGNAL -Wno-WIDTHEXPAND -Irtl/common --top-module pipeguard_cpu ...`:
- **Exit code:** 0
- **Suppressed warnings:** `UNUSEDSIGNAL` (B0 leaves `obs_*` bundle unused; core has 7 unused internal wires in `execute_forwarding_stage` / `riscv_pipeline_cpu_obs`) and `WIDTHEXPAND` (pre-existing in unmodified `rtl/core/data_memory.sv:66`).
