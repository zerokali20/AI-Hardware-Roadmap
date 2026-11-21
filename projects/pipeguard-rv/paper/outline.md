# Paper Outline: PipeGuard-RV

**Working Title:**  
*PipeGuard-RV: Evaluating Microarchitectural Pipeline-Aware Invariant Monitors for Transient Fault Detection in RISC-V Pipelines*

---

## Abstract
- **Context:** Vulnerability of resource-constrained RISC-V cores to transient hardware faults and physical fault injection.
- **Problem:** TMR/DMR impose excessive area/power overheads (>100%), while software CFI incurs significant latency.
- **Proposed Approach:** Exploration of lightweight, concurrent hardware assertion monitors snooping pipeline control and hazard states.
- **Configurations:** B0 (baseline), M0 (PC-level), M1 (branch-aware), M2 (pipeline-hazard-aware).
- **Summary of Findings:** *(Placeholder: To be filled upon completion of Phases 6–7)*.

---

## 1. Introduction
- 1.1 Motivation: Edge computing, radiation environments, physical fault injection (clock/voltage/EMFI).
- 1.2 The Dilemma: Dual-modular redundancy vs. low-cost microcontrollers.
- 1.3 PipeGuard-RV Vision: Microarchitecture-coupled invariant checkers that operate in parallel with zero runtime stall penalty.
- 1.4 Key Contributions:
  - Systematic comparison of observation granularity (M0 vs. M1 vs. M2).
  - Open-source, fully reproducible experimental artifact on standard RV32I pipeline.
  - Formal bounded verification of monitor false-positive immunity.

---

## 2. Threat Model & Scope
- 2.1 Adversary capabilities & fault injection mechanisms (SEUs, transient glitches).
- 2.2 Fault taxonomy: PC datapath (Class A), branch logic (Class B), pipeline control (Class C).
- 2.3 Explicit boundaries: Transient single-bit faults only; exclusion of multi-bit, permanent, and side-channel vectors.

---

## 3. Related Work
- 3.1 Hardware Control-Flow Integrity (MAFIA, shadow stacks).
- 3.2 Dual-Execution & Invariant Enforcement (DExIE, decoupled checkers).
- 3.3 External trace monitoring and hardware watchdogs.
- 3.4 Open-source RISC-V verification methodologies.

---

## 4. Baseline Processor Architecture
- 4.1 Classical 5-stage in-order RV32I pipeline (`riscv_pipeline_cpu`).
- 4.2 Pipeline hazard arbitration and priority logic (`pipeline_control.sv`).
- 4.3 Signal observability analysis: Top-level ports vs. internal microarchitectural state.

---

## 5. PipeGuard Monitor Architecture
- 5.1 Design Principles: Non-intrusive snooping, zero performance penalty, bounded latency.
- 5.2 M0: Sequential PC Progression & Alignment Checker.
- 5.3 M1: Branch-Aware Execution Validator.
- 5.4 M2: Pipeline-Hazard and Invariant Cross-Checker.
- 5.5 Universal Alarm & Sticky Latch Interface.
- 5.6 Wrapper integration strategy (`monitor_adapter.sv`).

---

## 6. Formal Verification of Invariants
- 6.1 Safety specification: Proof of zero false alarms on clean code.
- 6.2 SymbiYosys Bounded Model Checking (BMC) methodology.
- 6.3 Invariant formulation and proof results across B0–M2.

---

## 7. Experimental Setup & Methodology
- 7.1 Simulation platform: Icarus Verilog 12.0 + cocotb 2.1.0 in Python 3.12.
- 7.2 Benchmark workloads: Arithmetic compute, control branch loops, hazard stress, memory access.
- 7.3 Fault injection harness: Single-cycle synchronous bit flipping across target signal classes.
- 7.4 Metrics: Detection coverage ($C_{\text{det}}$), detection latency ($L_{\text{det}}$), false positive rate ($FPR$).
- 7.5 Synthesis environment: Yosys 0.33 generic cell synthesis.

---

## 8. Results & Analysis *(Placeholders — to be populated from Phases 6–8)*
- 8.1 Baseline Verification: Confirmation of 99/99 passing tests on unmodified regression.
- 8.2 Fault Detection Coverage:
  - Table: Coverage by configuration (B0, M0, M1, M2) across Fault Classes A, B, C.
  - Discussion of coverage gain from M0 $\to$ M1 $\to$ M2.
- 8.3 Alarm Latency Distribution:
  - CDF plot of detection latency in cycles.
  - Analysis of pre-writeback detection efficacy.
- 8.4 Hardware Area & Synthesis Overhead:
  - Cell counts and percentage delta vs. B0.
  - Evaluation of the coverage-to-overhead Pareto frontier.

---

## 9. Discussion & Limitations
- 9.1 Simulation fidelity vs. physical silicon reality.
- 9.2 The cost of internal signal tapping.
- 9.3 Shared control wire vulnerability and limits of non-replicated checkers.
- 9.4 Generalization to deeper or out-of-order pipelines.

---

## 10. Conclusion & Future Work
- 10.1 Summary of findings.
- 10.2 Future directions: Autonomous pipeline recovery, FPGA fault injection, multi-bit fault extensions.

---

## Artifact Availability
- Full reproducible repository, Makefile targets, and raw experiment CSV logs.
