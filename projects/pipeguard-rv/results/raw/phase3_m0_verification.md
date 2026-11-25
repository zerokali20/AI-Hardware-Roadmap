# Phase 3 Verification Report — M0 (`pc_monitor`)

| Field | Value |
|---|---|
| **Date** | 2026-11-25 |
| **Simulator** | Icarus Verilog 12.0 (stable) + cocotb 2.1.0 |
| **Linter** | Verilator 5.020 |
| **Monitor RTL** | `rtl/monitors/pc_monitor.sv` wired at `MONITOR_CFG=1` in `rtl/top/pipeguard_cpu.sv` |

## 1. Unit Tests (`tb/test_pc_monitor.py`, `make monitor-test CONFIG=m0`)

- `test_reset_suppression`: **PASS** — invalid PC (`0xFFFFFFFB`) during `rst=1` does not assert `fault_detected` or latch `fault_sticky`.
- `test_valid_sequential_and_nonsequential_pcs`: **PASS** — aligned PCs in `[0x000, 0x3FC]`, including non-sequential jumps, produce zero alarms.
- `test_misaligned_pc_detection_and_sticky`: **PASS** — offsets `+1`, `+2`, `+3` assert `fault_detected=1`, latch `fault_sticky=1` with `fault_class=1` (`PG_FC_PC_MISALIGNED`), and retain first fault class across subsequent legal/faulty PCs until `rst=1`.
- `test_out_of_bounds_pc_detection`: **PASS** — aligned PCs `0x400`, `0x1000`, `0xFFFFFFFC` assert `fault_detected=1` and latch `fault_class=2` (`PG_FC_PC_OUT_OF_BOUNDS`).
- `test_misaligned_priority_over_oob`: **PASS** — simultaneous misaligned + out-of-bounds (`0x402`) deterministically reports `PG_FC_PC_MISALIGNED` (`1`); `rst=1` clears sticky state.
- **Total:** `TESTS=5 PASS=5 FAIL=0 SKIP=0`

## 2. Lock-Step False-Positive & Fault-Injection Tests (`tb/test_m0_integration.py`, `make test CONFIG=m0`)

- `test_m0_directed_lockstep_zero_fp`: **PASS** — all 15 directed programs match `riscv_pipeline_cpu` cycle-for-cycle with `fault_detected=0`, `fault_sticky=0`, `fault_class=0` (0 false positives).
- `test_m0_random_lockstep_zero_fp`: **PASS** — all 10 seeded-random 48-instruction RV32I programs match cycle-for-cycle with 0 false positives.
- `test_m0_fault_inject_misaligned`: **PASS** — transient 1-cycle `Force` on `PC[1]` triggers `fault_detected=1` combinationally and latches `fault_sticky=1`, `fault_class=1` on clock edge; persists after `Release()`.
- `test_m0_fault_inject_out_of_bounds`: **PASS** — transient 1-cycle `Force` on `PC[10]` (`^ 0x400`) triggers `fault_detected=1` and latches `fault_sticky=1`, `fault_class=2`.
- `test_m0_aligned_in_range_blind_spot`: **PASS** — transient 1-cycle `Force` on `PC[3]` (`^ 0x8`, aligned and inside `[0x000, 0x3FC]`) is not detected (`fault_detected=0`, `fault_sticky=0`), confirming the documented M0 blind spot.
- **Total:** `TESTS=5 PASS=5 FAIL=0 SKIP=0`

## 3. Verilator Lint

Executed `make lint` (`verilator --lint-only -Wall -Wno-UNUSEDSIGNAL -Wno-WIDTHEXPAND -Irtl/common -GMONITOR_CFG=1 --top-module pipeguard_cpu ...`):
- **Exit code:** 0
- **Note:** `pc_monitor.sv` uses a local `/* verilator lint_off UNSIGNED */` around `fetch_pc < PC_MIN` because `PC_MIN` defaults to `32'h0000_0000` while remaining configurable.
