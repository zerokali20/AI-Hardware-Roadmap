# System Architecture — PipeGuard-RV

## 1. Architectural Overview

PipeGuard-RV evaluates lightweight, concurrent hardware assertions for fault detection on a classical 5-stage RISC-V in-order processor pipeline. The baseline processor is a standard RV32I design (`riscv_pipeline_cpu`) implementing:
1. **IF (Instruction Fetch):** `instruction_fetch.sv`, `program_counter.sv`, `instruction_memory.sv`
2. **ID (Instruction Decode):** `if_id_stage.sv`, `if_id_register.sv`, `rv32i_decoder.sv`, `register_file.sv`, `immediate_generator.sv`
3. **EX (Execute):** `execute_stage.sv`, `execute_forwarding_stage.sv`, `alu.sv`, `alu_control.sv`, `branch_unit.sv`, `forwarding_unit.sv`
4. **MEM (Memory Access):** `memory_stage.sv`, `data_memory.sv`, `ex_mem_register.sv`
5. **WB (Writeback):** `writeback_stage.sv`, `mem_wb_register.sv`, `register_writeback_integration.sv`
6. **Pipeline Control:** `pipeline_control.sv`, `hazard_detection_unit.sv`

```
+-----------------------------------------------------------------------------------+
| PipeGuard Top Wrapper (pipeguard_top_mX.sv)                                       |
|                                                                                   |
|  +-------------------------------------+      +--------------------------------+  |
|  | Core Pipeline (riscv_pipeline_cpu)  |      | PipeGuard Monitor              |  |
|  |                                     |      | (pc / branch / pipeline)       |  |
|  | IF ---> ID ---> EX ---> MEM ---> WB |      |                                |  |
|  |  |       |       |       |       |  |      |   Invariants & Assertions      |  |
|  +--|-------|-------|-------|-------|--+      +--------------------------------+  |
|     |       |       |       |       |                         ^                   |
|     +=======+=======+=======+=======+====== Tap Bus ==========+                   |
|                                                               |                   |
|                                                     [Alarm Interface]             |
|                                                     - fault_detected              |
|                                                     - fault_sticky                |
|                                                     - fault_class[2:0]            |
+-----------------------------------------------------------------------------------+
```

---

## 2. The Four Configurations

PipeGuard-RV partitions protection levels across four configurations to isolate cost and coverage contributions:

### 2.1 B0: Unprotected Baseline
- Core wrapped in test adapter with zero monitoring logic.
- Serves as the control group for area, power, and timing overhead.
- Expected fault detection coverage: 0.0%.

### 2.2 M0: PC-Based Architectural Checker (`pc_monitor.sv`)
- Snoops `fetch_pc` and `decode_pc`.
- **Invariants Monitored:**
  - Sequential progression: $PC_{t+1} = PC_t + 4$ unless a valid redirect flag is asserted.
  - Alignment invariant: $PC[1:0] == 2'b00$ (32-bit instructions).
- **Overhead:** Minimal (comparator, register, single adder).
- **Limitation:** Blind to internal pipeline pipeline hazards, stalls, and multi-cycle branch latencies.

### 2.3 M1: Branch-Aware Control Monitor (`branch_monitor.sv`)
- Extends M0 with execute-stage branch outcome checking.
- Snoops `branch_redirect`, `execute_pc`, and decoded branch type.
- **Invariants Monitored:**
  - Divergent execution: Verifies that redirects correlate with execute-stage branch/jump decisions.
  - Target alignment: Verifies `branch_target[1:0] == 2'b00`.
  - Suppressed redirect: Flags when a condition is met but redirect is suppressed.

### 2.4 M2: Pipeline-Aware Invariant Monitor (`pipeline_monitor.sv`)
- Deep integration checking pipeline progression, hazards, and exceptions.
- Snoops `load_use_stall`, `alignment_fault`, `memory_alignment_error`, `memory_access_error`, and `illegal_instruction`.
- **Invariants Monitored:**
  - Hazard state consistency: Load-use detection must coincide with IF/ID stall and ID/EX bubble insertion.
  - Exception latching: Alignment or bus errors must prevent instruction writeback.
  - Forwarding consistency: Detects corrupted forward multiplexer states causing stale register reads.

---

## 3. Monitor Adapter & Packaging Strategy

### 3.1 Non-Invasive Core Policy
To preserve the canonical baseline from Lab 06 (`labs/06-riscv-pipeline/rtl/`), the research snapshot in `projects/pipeguard-rv/rtl/core/` is **never modified directly**.

### 3.2 Wrapper Architecture (`monitor_adapter.sv`)
Because several vital pipeline control wires (`if_id_stall`, `if_id_flush`, `pc_target`, `branch_taken`, `stall_request`) are internal nets in `riscv_pipeline_cpu.sv`, the wrapper strategy operates as follows:
- For configurations relying solely on top-level observable ports (`fetch_pc`, `decode_pc`, `execute_pc`, `mem_pc`, `wb_pc`, `load_use_stall`, `branch_redirect`, `alignment_fault`, error lines), the monitor taps top ports directly.
- For deep microarchitectural signals required by M2, a dedicated research top `riscv_pipeline_cpu_tapped.sv` (in `rtl/top/`) instantiates the submodules and exposes internal diagnostic nets to `monitor_adapter.sv`.

---

## 4. Alarm Interface

Every monitor instance provides a uniform 3-signal interface:

```systemverilog
output logic       fault_detected, // Asserted cycle-accurate when invariant fails
output logic       fault_sticky,   // Latched high on fault_detected until synchronous reset
output logic [2:0] fault_class     // Encoded fault domain:
                                   //   3'b001: PC datapath / alignment
                                   //   3'b010: Branch control / target
                                   //   3'b100: Pipeline hazard / stall inconsistency
input  logic       fault_clear     // Optional synchronous alarm acknowledge
```

The alarm interface is non-intrusive: during fault-free operation, no cycle stalls or latency overhead are introduced into the processor pipeline.
