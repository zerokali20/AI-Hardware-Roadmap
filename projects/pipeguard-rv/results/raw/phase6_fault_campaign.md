# Phase 6 Fault-Injection Campaign Report — PipeGuard-RV

| Field | Value |
|---|---|
| **Date** | 2026-11-26 |
| **Simulator** | Icarus Verilog 12.0 + cocotb 2.1.0 |
| **Fault Model** | Single-cycle transient bit-flip (`Force`/`Release`) on PC, branch-control, and pipeline-control signals |
| **Seed** | `20261126` (identical schedule across `B0`, `M0`, `M1`, `M2`) |
| **Summary Datasets** | `results/processed/campaign_summary_smoke.csv`, `results/processed/campaign_summary_full.csv` |

## 1. Smoke Campaign Summary (`experiments/configs/smoke.yaml`)

- **Scope:** 4 workloads × 7 fault targets × 1 injection = **28 experiments per config** (112 total)
- **Relevant deviations:** 22 (6 masked, 0 nonactivated, 0 timeout, 0 invalid)
- **Fault-free cycles:** 215 per config (0 false positives across all 4 configs)

| Config | Detected / Relevant | Coverage | Mean Latency (cyc) | FPR |
|---|---:|---:|---:|---:|
| `B0` | 0 / 22 | 0.00% | — | 0.00% |
| `M0` | 8 / 22 | 36.36% | 0.00 | 0.00% |
| `M1` | 16 / 22 | 72.73% | 0.00 | 0.00% |
| `M2` | 22 / 22 | 100.00% | 0.00 | 0.00% |

## 2. Full Campaign Summary (`experiments/configs/full.yaml`)

- **Scope:** 8 workloads × 9 fault targets × 3 injections = **216 experiments per config** (864 total)
- **Relevant deviations:** 185 (31 masked, 0 nonactivated, 0 timeout, 0 invalid)
- **Fault-free cycles:** 450 per config (0 false positives across all 4 configs)

### Overall Coverage, Latency & False-Positive Rate

| Config | Detected / Relevant | Coverage | Mean Latency (cyc) | Max Latency (cyc) | FPR |
|---|---:|---:|---:|---:|---:|
| `B0` | 0 / 185 | **0.00%** | — | — | 0.00% |
| `M0` | 48 / 185 | **25.95%** | 0.00 | 0 | 0.00% |
| `M1` | 96 / 185 | **51.89%** | 0.0104 | 1 | 0.00% |
| `M2` | 156 / 185 | **84.32%** | 0.1346 | 21 | 0.00% |

### Detection Coverage by Fault Category (`full` campaign)

| Fault Category | Relevant | `B0` | `M0` | `M1` | `M2` |
|---|---:|---:|---:|---:|---:|
| `pc` (`pc_misaligned`, `pc_oob`, `pc_inrange`) | 72 | 0.00% (0/72) | 66.67% (48/72) | **100.00%** (72/72) | **100.00%** (72/72) |
| `branch_control` (`branch_redirect`, `branch_taken`, `branch_target`) | 54 | 0.00% (0/54) | 0.00% (0/54) | 44.44% (24/54) | 46.30% (25/54) |
| `pipeline_control` (`pc_stall`, `load_use_stall`, `id_ex_flush`) | 59 | 0.00% (0/59) | 0.00% (0/59) | 0.00% (0/59) | **100.00%** (59/59) |

## 3. Key Empirical Findings

1. **M1 closes M0's aligned in-range PC blind spot:** `pc` detection rises from `66.67%` (M0) to `100.00%` (M1, M2).
2. **M2 closes M1's pipeline-control blind spot:** `pipeline_control` detection rises from `0.00%` (M0, M1) to `100.00%` (M2), while maintaining `0.00%` false-positive rate across all 450 fault-free cycles.
3. **Shared-signal boundary on EX-stage branch intent:** Neither M1 nor M2 detects direct corruptions to `branch_taken` or `branch_target` at the EX-stage output (accounting for the 29 undetected `branch_control` deviations in M2), because both monitors observe `branch_taken` and `branch_target` as their branch-intent reference rather than independently recomputing branch resolution from `rs1`/`rs2`/immediate.
