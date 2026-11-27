# PipeGuard-RV: Evaluating Pipeline-Aware Lightweight Control-Flow Fault Detection for Resource-Constrained RV32I Processors

## Abstract

Resource-constrained RISC-V processors deployed in embedded and cyber-physical systems face transient hardware faults and fault-injection attacks, yet full hardware redundancy schemes such as Dual/Triple Modular Redundancy (DMR/TMR) impose >100% logic overhead. This paper presents **PipeGuard-RV**, an open-source, reproducible evaluation of three passive, synthesizable hardware runtime monitors—**M0** (program-counter bounds/alignment), **M1** (branch-aware PC transition checking), and **M2** (pipeline-control, hazard, and stage-progression checking)—integrated onto a five-stage in-order RV32I pipeline (`B0` baseline). Across 30 unmodified baseline test suites (319/319 passing), cycle-exact lock-step equivalence checks, 25-cycle Yosys bounded model checking (6/6 passing), and an 864-experiment controlled RTL fault-injection campaign across 8 workloads (including an embedded IoT controller), **M0**, **M1**, and **M2** achieve **25.95%** (48/185), **51.89%** (96/185), and **84.32%** (156/185) detection coverage of relevant deviations with **0.00%** false-positive rate across 450 fault-free cycles per configuration. Yosys 0.33 generic cell synthesis measures **+0.13%** (+104 cells), **+0.73%** (+562 cells), and **+1.47%** (+1,139 cells) total-design cell overhead (or **+1.36%**, **+7.27%**, and **+14.87%** relative to non-memory core logic). We also empirically characterize a key shared-signal limitation: direct single-bit faults on EX-stage branch intent (`branch_taken`, `branch_target`) remain partially invisible (`46.30%` detection in `M2`) without duplicating branch-condition evaluation.

---

## 1. Introduction

Embedded and cyber-physical microcontrollers increasingly rely on open-standard RISC-V cores. While spatial redundancy (DMR/TMR) protects against single-event upsets and fault-injection glitches, its area and power overhead (>100%) is prohibitive for cost- and energy-constrained IoT devices. Lightweight hardware control-flow monitors offer a middle ground by checking microarchitectural invariants concurrently with zero runtime stall penalty.

Rather than claiming to be the first pipeline-aware RISC-V fault detector, **PipeGuard-RV** provides an empirical, fully reproducible **granularity-versus-cost** evaluation on a single five-stage RV32I pipeline (`B0`, `M0`, `M1`, `M2`) using open-source EDA tooling (Icarus Verilog 12.0, cocotb 2.1.0, Verilator 5.020, Yosys 0.33).

---

## 2. Threat Model & Scope

We evaluate single-cycle transient synthetic bit-flip faults (`Force`/`Release` in RTL simulation) across three control-flow fault categories:
- **PC (`pc`):** Misaligned (`PC[1:0]`), out-of-bounds (`PC[10]`), and aligned in-range (`PC[4:2]`) perturbations.
- **Branch Control (`branch_control`):** Flips on `branch_redirect`, EX-stage `branch_taken`, and `branch_target`.
- **Pipeline Control (`pipeline_control`):** Flips on `pc_stall`, `load_use_stall`, and `id_ex_flush`.

Multi-bit upsets, permanent faults, side-channel leakage, and physical silicon fault injection are outside the scope of this study.

---

## 3. Related Work

Hardware Control-Flow Integrity (CFI) architectures such as **MAFIA** [1] use cryptographic signatures and shadow call stacks, while **DExIE** [2] enforces decoupled execution invariants across pipeline stages. Both establish that microarchitectural checking improves security over coarse PC watchdogs, though often with ISA/compiler extensions or substantial logic overhead. PipeGuard-RV complements these works by quantifying the exact coverage, latency, and Yosys cell cost of purely passive, non-intrusive monitors across three observation levels on an unmodified RV32I core.

---

## 4. Baseline Processor & Monitor Architecture

The reference processor (`B0`) is a five-stage in-order RV32I pipeline (`rtl/core/riscv_pipeline_cpu.sv`, 26 SystemVerilog modules, byte-identical to Lab 06 at baseline SHA `0be8905`). Because only 14 signals are exposed at the original top-level ports, `riscv_pipeline_cpu_obs.sv` exports internal observation wires (`obs_*`) without altering any datapath or control logic, and `pipeguard_cpu.sv` selects `B0`/`M0`/`M1`/`M2` via `MONITOR_CFG`.

- **M0 (`pc_monitor.sv`):** Validates 4-byte alignment (`fetch_pc[1:0] == 0`) and configurable bounds (`[0x000, 0x3FC]`).
- **M1 (`branch_monitor.sv`):** Adds cycle-correct PC progression checks, `branch_redirect` vs. EX-stage intent validation, and conservative PC-hold acceptance (since M1 lacks stall context).
- **M2 (`pipeline_monitor.sv`):** Adds strict PC progression using `pc_stall`, independent load-use hazard recomputation from IF/ID and ID/EX fields, redirect-over-stall priority verification, `id_ex_flush` consistency, and stage PC progression across IF/ID, ID/EX, EX/MEM, and MEM/WB.

All monitors expose a uniform alarm interface (`fault_detected`, `fault_sticky`, `fault_class`), cleared only by `rst`.

---

## 5. Verification & Bounded Formal Proofs

1. **Baseline Snapshot Regression:** All 30 Lab 06 suites pass against `rtl/core/` (**319/319 tests PASS**, `FAIL=0`).
2. **Lock-Step Equivalence:** `pipeguard_cpu` (`B0`, `M0`, `M1`, `M2`) matches `riscv_pipeline_cpu` cycle-for-cycle across 15 directed and 10 seeded-random RV32I programs with **0 false positives**.
3. **Verilator Lint:** `verilator --lint-only` exits 0 across `MONITOR_CFG=0..3` (with documented `UNUSEDSIGNAL` and pre-existing `WIDTHEXPAND` suppressions).
4. **Bounded Model Checking:** Yosys 0.33 `sat -seq 25` proves reset suppression, sticky persistence, invalid-observation response, and zero false positives under clean-environment assumptions (`6/6 PASS` at depth 25).

---

## 6. Experimental Setup & Results

We executed `full.yaml` (**216 fault experiments per configuration**, **864 total**) across 8 deterministic workloads (`sequential`, `conditional_branch`, `loop`, `jal_jalr`, `load_use_hazard`, `pipeline_flush`, `mixed`, `iot_controller`). Of 216 injections per config, 31 were masked and **185 caused relevant architectural or control-flow deviations** relative to the golden fault-free trace.

### 6.1 Detection Coverage & False-Positive Rate

| Config | Overall Coverage ($N=185$) | `pc` ($N=72$) | `branch_control` ($N=54$) | `pipeline_control` ($N=59$) | Mean Latency (cyc) | FPR (450 cyc) |
|---|---:|---:|---:|---:|---:|---:|
| **B0** | 0.00% (0/185) | 0.00% | 0.00% | 0.00% | — | 0.00% |
| **M0** | 25.95% (48/185) | 66.67% | 0.00% | 0.00% | 0.00 | 0.00% |
| **M1** | 51.89% (96/185) | **100.00%** | 44.44% | 0.00% | 0.0104 | 0.00% |
| **M2** | **84.32%** (156/185) | **100.00%** | 46.30% | **100.00%** | 0.1346 | 0.00% |

See `results/figures/fig1_coverage_by_config.png`, `fig2_coverage_by_category.png`, `fig3_false_positive_comparison.png`, and `fig4_latency_distribution.png`.

### 6.2 Hardware Overhead (Yosys 0.33 Generic Cells)

| Config | Total Cells | Delta vs. B0 | Total Overhead | Monitor Cells | Logic-Only Overhead (excl. mem) |
|---|---:|---:|---:|---:|---:|
| **B0** | 77,241 | — | — | 0 | — |
| **M0** | 77,345 | +104 | +0.13% | 104 (3 FF, 101 comb) | +1.36% |
| **M1** | 77,803 | +562 | +0.73% | 557 (70 FF, 487 comb) | +7.27% |
| **M2** | 78,380 | +1,139 | +1.47% | 1,139 (170 FF, 969 comb) | +14.87% |

See `results/figures/fig5_hardware_overhead.png` and `fig6_coverage_vs_cost.png`.

---

## 7. Discussion & Limitations

- **Why M2 outperforms M1:** Pipeline-control awareness eliminates M1's conservative PC-hold blind spot, raising `pipeline_control` coverage from **0.00% to 100.00%** at a cost of +577 additional cells over M1.
- **Shared-signal boundary:** M2 misses 29 of 54 `branch_control` deviations when `branch_taken` or `branch_target` is corrupted directly at the EX-stage output, because M1/M2 treat EX-stage branch intent as a trusted reference. Closing this gap requires independent branch-comparator replication.
- **Generic cell synthesis:** Yosys `-noabc` cell counts do not represent physical ASIC area, FPGA LUTs, $f_{\max}$, or power.

---

## 8. Conclusion

Pipeline-control awareness (`M2`) improves control-flow and pipeline fault-detection coverage from **25.95% (`M0`)** and **51.89% (`M1`)** to **84.32% (`M2`)** with zero false positives and **+1.47%** total Yosys generic cell overhead (**+14.87%** of non-memory core logic). All RTL, formal harnesses, simulation scripts, and datasets are reproducible from `projects/pipeguard-rv/`.
