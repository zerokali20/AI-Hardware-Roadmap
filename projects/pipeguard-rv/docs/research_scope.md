# Research Scope — PipeGuard-RV

## 1. Problem Statement

Microarchitectural reliability against transient hardware faults (e.g., radiation-induced single-event upsets, voltage droops, clock glitches, or electromagnetic fault injection) is a critical design requirement for embedded and edge computing systems. Control-flow integrity (CFI) violations induced by transient single-bit flips in the pipeline datapath or control wires can cause arbitrary code execution, system hangs, silent data corruption, or catastrophic failure.

While traditional fault tolerance techniques like Dual Modular Redundancy (DMR) or Triple Modular Redundancy (TMR) provide high coverage, they impose 100% to >200% area and power overheads, making them prohibitive for resource-constrained edge RISC-V microcontrollers. Conversely, purely software-based CFI techniques introduce severe performance and code-size penalties.

**PipeGuard-RV** explores lightweight, microarchitecture-coupled hardware assertion monitors that snoop pipeline state to detect transient control-flow disruptions with minimal hardware area and zero pipeline stall overhead during fault-free operation.

## 2. Research Questions (Hypotheses)

This research project tests specific microarchitectural hypotheses rather than assuming pre-determined outcomes:

- **RQ1 (Detection Coverage vs. Cost):** Can lightweight hardware assertion monitors achieve significant control-flow fault detection coverage (>60–90% on targeted pipeline control faults) with <10% logic cell overhead compared to an unprotected baseline core?
- **RQ2 (Observation Granularity):** What is the incremental fault detection coverage and false-positive risk gained by moving from coarse architectural PC-step monitoring (M0) to branch-aware monitoring (M1) and microarchitectural pipeline-hazard/stall-aware monitoring (M2)?
- **RQ3 (Detection Latency):** Can pipeline-level assertions detect control-flow corruptions within 1–2 clock cycles—before corrupted control signals propagate to memory writeback or irreversible architectural register commits?
- **RQ4 (False-Positive Elimination):** Can pipeline hazard invariants be formally proven (via Bounded Model Checking) to guarantee zero false positives under all valid ISA instruction sequences?

## 3. Evaluated Configurations

The study systematically evaluates four distinct hardware configurations:

1. **B0 (Unprotected Baseline):**
   - The unmodified 5-stage pipelined RV32I core wrapped in the PipeGuard test harness adapter.
   - Provides baseline area, cycle performance, and 0% monitor coverage reference.

2. **M0 (Architectural PC-Step Monitor):**
   - Coarse-grained checker inspecting architectural PC deltas.
   - Asserts an alarm if `PC_next != PC_curr + 4` unless a valid architectural redirect flag is observed.
   - Low overhead, but blind to microarchitectural pipeline stalls, flushes, and branch targets computed across pipeline stages.

3. **M1 (Branch-Aware Control Monitor):**
   - Extends M0 by tracking branch execution, branch targets, and stage-specific flush signals (`branch_redirect`, `execute_pc`, alignment verification).
   - Validates that taken branches target valid 4-byte aligned instruction addresses and correlate with execute-stage branch outcomes.

4. **M2 (Pipeline-Aware Deep Monitor):**
   - Incorporates hazard detection and pipeline stage control invariants:
     - Cross-checks `load_use_stall`, `alignment_fault`, `memory_access_error`, and stage progression.
     - Validates that pipeline bubbles/flushes match decoded hazard events.
     - Intended to maximize detection of internal control-line upsets before writeback commit.

## 4. Scope and Boundaries

### In Scope
- **Target Architecture:** Educational 5-stage in-order pipelined RV32I processor (`labs/06-riscv-pipeline/rtl/`).
- **Fault Model:** Synthetic transient single-bit flips injected into pipeline registers and control wires via simulation force APIs (Icarus Verilog / cocotb).
- **Verification:** Unit simulation, ISA regression validation, cocotb fault injection campaigns, and formal bounded model checking with SymbiYosys.
- **Synthesis Metric:** Standard logic cell counts and generic gate approximations synthesized via Yosys.

### Out of Scope
- Multi-bit upsets (MBU), permanent / stuck-at physical faults, or physical silicon fabrication.
- Production Out-of-Order (OoO) superscalar cores, multi-core interconnects, or cache-coherent memory hierarchies.
- Operating system level fault handlers or trap/exception recovery microcode (PipeGuard provides *detection* and sticky alarm assertion, not autonomous pipeline rollback).
- Physical fault injection equipment (pulsed laser, EMFI probe stations, glitching FPGA boards).

## 5. Scientific Posture

PipeGuard-RV is an empirical, evidence-based exploration. Results depend strictly on executed test runs, formal model proofs, and synthesis runs. No performance, area, or coverage numbers are assumed or claimed prior to empirical experimental validation.
