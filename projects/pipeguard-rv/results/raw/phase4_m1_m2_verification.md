# Phase 4 Verification Report — M1 (`branch_monitor`) & M2 (`pipeline_monitor`)

| Field | Value |
|---|---|
| **Date** | 2026-11-25 |
| **Simulator** | Icarus Verilog 12.0 (stable) + cocotb 2.1.0 |
| **Linter** | Verilator 5.020 |

## 1. Unit Tests

- **`branch_mon` (`tb/test_branch_monitor.py`, `make monitor-test CONFIG=m1`):** `TESTS=4 PASS=4 FAIL=0 SKIP=0`
  - `test_valid_seq_branch_and_hold`, `test_aligned_in_range_pc_jump_without_redirect`, `test_spurious_redirect_and_dropped_redirect`, `test_redirect_target_mismatch`.
- **`pipe_mon` (`tb/test_pipeline_monitor.py`, `make monitor-test CONFIG=m2`):** `TESTS=4 PASS=4 FAIL=0 SKIP=0`
  - `test_valid_pipeline_progression_and_stall`, `test_spurious_pc_freeze_caught_by_m2`, `test_load_use_stall_inconsistency`, `test_redirect_priority_and_stage_progress`.

## 2. Lock-Step Zero-FP & Synthetic Fault-Injection Tests

Executed across all four configurations (`b0_equiv`, `m0_equiv`, `m1_equiv`, `m2_equiv`) after updating `tb/test_b0_equivalence.py`'s `load_and_reset` to zero-initialize `data_memory` (preventing 4-state `X` propagation from uninitialized loads into branch comparators):

- **`b0_equiv` (`MONITOR_CFG=0`):** `TESTS=2 PASS=2 FAIL=0 SKIP=0`
- **`m0_equiv` (`MONITOR_CFG=1`):** `TESTS=5 PASS=5 FAIL=0 SKIP=0`
- **`m1_equiv` (`MONITOR_CFG=2`):** `TESTS=5 PASS=5 FAIL=0 SKIP=0`
  - 0 false positives across 15 directed + 10 random RV32I programs.
  - Catches aligned in-range `PC[3]` jump and spurious `branch_redirect`; conservatively accepts `pc_stall=1` hold.
- **`m2_equiv` (`MONITOR_CFG=3`):** `TESTS=5 PASS=5 FAIL=0 SKIP=0`
  - 0 false positives across 15 directed + 10 random RV32I programs.
  - Catches spurious `pc_stall=1` (missed by M1), dropped `load_use_stall`, and dropped `id_ex_flush`.

## 3. Verilator Lint

`verilator --lint-only -Wall -Wno-UNUSEDSIGNAL -Wno-WIDTHEXPAND` exited **0** for `MONITOR_CFG` = 0, 1, 2, and 3.
