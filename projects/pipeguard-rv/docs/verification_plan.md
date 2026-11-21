# Verification Plan — PipeGuard-RV

## 1. Multi-Tier Verification Strategy

PipeGuard-RV employs a four-tier verification methodology to guarantee that fault monitors introduce **zero false positives**, detect **injected faults**, and maintain full **RTL compatibility** with the baseline processor core.

```
+----------------------------------------------------------------------------------+
| Layer 1: Baseline Preservation Regression (cocotb + iverilog)                   |
| Ensure 100% pass on unmodified Lab 06 test suite across all wrapped configs      |
+----------------------------------------------------------------------------------+
                                        |
+----------------------------------------------------------------------------------+
| Layer 2: Static Linting & Semantic Checks (Verilator Lint)                       |
| Strict zero-warning policy on width mismatches, latch inferral, unused nets      |
+----------------------------------------------------------------------------------+
                                        |
+----------------------------------------------------------------------------------+
| Layer 3: Formal Invariant Verification (SymbiYosys BMC)                          |
| Formally prove safety properties: fault_detected == 0 under all valid ISA flows  |
+----------------------------------------------------------------------------------+
                                        |
+----------------------------------------------------------------------------------+
| Layer 4: Fault Injection Verification (cocotb Directed & Random Campaigns)       |
| Quantify true detection, latency to alarm, and fault propagation dynamics        |
+----------------------------------------------------------------------------------+
```

---

## 2. Test Suites and Regression Reuse

### 2.1 Baseline Suite Reuse (Lab 06 Integration)
All monitor configurations (B0, M0, M1, M2) must run the complete verified baseline regression without failure. Phase 1 established a verified baseline of **99 passing tests across 10 test suites**:

1. `cpu` (5 tests): Full RV32I pipeline instruction sequence integration.
2. `cpuhaz` (7 tests): Data hazard resolution, forwarding paths, and load-use stalls.
3. `cpuisa` (6 tests): Arithmetic, logical, and shift ISA instruction verification.
4. `cpumembranch` (15 tests): Load/store operations, branch condition branches, and jumps.
5. `pipectrl` (10 tests): Pipeline flush, stall, and branch redirect state arbitration.
6. `pc` (6 tests): Program counter sequential increment, stall, and jump load.
7. `ifid` (6 tests): IF/ID pipeline register latching, stall, and synchronous flush.
8. `alu` (12 tests): RV32I ALU arithmetic and logic operations.
9. `hazard` (18 tests): Load-use hazard detection logic and stall assertion.
10. `forward` (14 tests): ALU operand bypass and forwarding arbitration.

**Acceptance Gate:** Any wrapped configuration (B0–M2) asserting `fault_detected` during the baseline suite is classified as having a **false positive** and fails the acceptance gate.

---

## 3. Monitor Unit & Integration Verification

Each monitor component undergoes focused unit-level testing in `tb/unit/`:

### 3.1 `test_pc_monitor.py`
- Stimulates legal sequential step ($+4$).
- Tests valid branches and jumps with assert flag.
- Injects single-bit flips into PC signals: verifies `fault_detected` asserts within 1 cycle.
- Injects misaligned PC ($PC[1:0] \neq 00$): verifies immediate detection.

### 3.2 `test_branch_monitor.py`
- Stimulates taken/untaken branch sequences.
- Injects fake redirect signal without branch instruction: checks spurious redirect detection.
- Injects branch target bit flips: checks branch target verification logic.
- Verifies sticky latch behavior (`fault_sticky` remains 1 until `fault_clear`).

### 3.3 `test_pipeline_monitor.py`
- Stimulates load-use stall sequences: verifies hazard invariant compliance.
- Injects corrupted stall request: checks bubble-consistency invariants.
- Validates exception latching on data memory alignment errors.

---

## 4. Formal Verification with SymbiYosys (Phase 5)

Using Yosys 0.33 and SymbiYosys in WSL, Bounded Model Checking (BMC) verifies core assertions:

### Formal Properties (SystemVerilog Assertions)
```systemverilog
// Invariant 1: No false alarms during valid uncorrupted execution
property p_no_false_alarm;
    @(posedge clk) disable iff (!reset_n)
    (!fault_injected) |-> (!fault_detected);
endproperty
assert property (p_no_false_alarm);

// Invariant 2: Fault persistence
property p_fault_sticky_persistence;
    @(posedge clk) disable iff (!reset_n)
    fault_detected |=> fault_sticky;
endproperty
assert property (p_fault_sticky_persistence);
```

**Depth Target:** 20–30 bounded cycles covering multi-stage hazard resolution pipelines.

---

## 5. Verification Matrix Summary

| Configuration | Lab 06 Regression (99 tests) | Unit Testbench | Verilator Lint | SymbiYosys BMC | Fault Injection Sweep |
|---|---|---|---|---|---|
| **B0** (Baseline) | Required (99/99) | `tb_top_b0` | Clean | N/A | Reference (0% Det) |
| **M0** (PC Mon) | Required (99/99) | `test_pc_monitor` | Clean | Depth 20 | Class A Faults |
| **M1** (Branch Mon) | Required (99/99) | `test_branch_mon` | Clean | Depth 20 | Class A + B Faults |
| **M2** (Pipeline Mon) | Required (99/99) | `test_pipe_mon` | Clean | Depth 25 | Class A + B + C Faults |
