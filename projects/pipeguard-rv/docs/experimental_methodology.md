# Experimental Methodology — PipeGuard-RV

> **Notice:** PipeGuard-RV is an active research project. As of Phase 1, baseline CPU RTL verification is complete (99/99 tests pass). **No fault injection campaign results or synthesis area numbers exist yet.** This document defines the exact experimental protocols, metrics, and automation procedures to ensure rigorous, reproducible data collection in Phases 6 and 7.

---

## 1. Fault Injection Framework

### 1.1 Synthetic RTL Fault Primitives
Fault injection is performed in Python testbenches via `cocotb` signal forcing hooks:
- **Fault Primitive:** Single-cycle bit inversion ($b \gets \neg b$).
- **Timing:** Synchronized to the rising clock edge (`await RisingEdge(dut.clk)`).
- **Duration:** 1 clock period, after which the signal is released or returned to driving logic to model a transient Single Event Transient (SET) or Single Event Upset (SEU).

### 1.2 Target Signal Fault Catalog
Fault targets are defined in YAML configuration files (`experiments/config/fault_catalog.yaml`):
1. **PC Datapath:** `fetch_pc[i]`, `pc_target[i]` for bit indices $i \in \{0, 1, 2, \dots, 31\}$.
2. **Branch Unit Control:** `branch_taken`, `invalid_branch`, `branch_redirect`, `branch_target[i]`.
3. **Pipeline Control:** `load_use_stall`, `if_id_stall`, `if_id_flush`, `id_ex_stall`, `id_ex_flush`.

---

## 2. Benchmark Workloads

Fault campaigns evaluate workloads chosen to exercise varied pipeline behaviors:
1. **Sequential Compute (`workloads/arithmetic.hex`):** Heavy ALU operations (ADD, SUB, AND, OR, SLT) with minimal branch activity.
2. **Control-Intensive Loop (`workloads/branches.hex`):** Nested loops, forward/backward conditional branches, and subroutines (JAL/JALR).
3. **Hazard Stress (`workloads/hazards.hex`):** Frequent load-use dependencies requiring pipeline stalls, followed immediately by forwarded ALU operands.
4. **Memory Access (`workloads/mem_access.hex`):** Dense stride memory stores and loads exercising alignment boundaries.

---

## 3. Campaign Structure

### 3.1 Smoke Campaign (`make smoke CONFIG=<cfg>`)
- Rapid sanity check run during development and CI.
- Sample: 10 fixed faults across the 4 benchmark workloads (40 trials total).
- Execution time: < 30 seconds.
- Purpose: Verify fault injector instrumentation, testbench harnesses, and alarm latching without lengthy simulations.

### 3.2 Full Systematic Campaign (`make campaign CONFIG=<cfg>`)
- Comprehensive sweep covering all target signal bits across multiple execution cycle offsets $t \in [T_{\text{start}}, T_{\text{end}}]$.
- Sample size: $> 1,000$ fault injections per configuration ($N \ge 4,000$ total trials).
- Repetition: Deterministic pseudo-random seed recording ensures bit-exact reproduction.

---

## 4. Evaluation Metrics

### 4.1 Detection Coverage ($C_{\text{det}}$)
The ratio of injected faults that trigger the monitor alarm relative to total injected faults:
$$C_{\text{det}} = \frac{N_{\text{detected}}}{N_{\text{injected}}} \times 100\%$$

Classified into:
- **Detected ($N_{\text{detected}}$):** `fault_detected` or `fault_sticky` asserted within observation window.
- **Silent / Masked ($N_{\text{masked}}$):** Fault had no impact on architectural state or control flow (e.g., bit flip on unused high address bits or dead pipeline stage).
- **Silent Data Corruption (SDC):** Fault altered architectural state (`wb_data`, memory, or PC path) without triggering `fault_detected`.

### 4.2 False Positive Rate ($FPR$)
$$FPR = \frac{N_{\text{false\_alarms}}}{N_{\text{clean\_cycles}}} \times 100\%$$
- Evaluated over the 99-test baseline regression suite with zero fault injection.
- **Design Target:** Strictly $0.0\%$. Any non-zero FPR indicates an erroneous invariant.

### 4.3 Detection Latency ($L_{\text{det}}$)
The elapsed clock cycles from fault injection ($t_{\text{inj}}$) to the rising edge of `fault_detected` ($t_{\text{alarm}}$):
$$L_{\text{det}} = t_{\text{alarm}} - t_{\text{inj}}$$
- Reported as minimum, median, and 95th percentile cycles.

### 4.4 Hardware Area Overhead
Synthesized using open-source Yosys 0.33 targeting generic logic cells.
- **Metrics:** Total cell count, Flip-Flop count, LUT/gate equivalents.
- **Overhead Delta:**
$$\Delta_{\text{area}} = \frac{\text{Cells}_{Mx} - \text{Cells}_{B0}}{\text{Cells}_{B0}} \times 100\%$$

---

## 5. Data Collection & Archival

Raw trial logs are saved to structured CSV files:
`results/raw/fault_campaign_<CONFIG>_<TIMESTAMP>.csv`

Each row records:
```csv
trial_id,config,workload,target_signal,bit_index,injection_cycle,detected,detection_latency,fault_class,sdc_flag
```

Data processing scripts (`scripts/analyze_results.py`) aggregate the raw CSVs into summary tables in `results/processed/` and generate publication-quality figures in `results/figures/`.
