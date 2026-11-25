# Phase 5 Formal Verification Report — PipeGuard-RV

| Field | Value |
|---|---|
| **Date** | 2026-11-25 |
| **Tool** | Yosys 0.33 (`sat -seq 25 -set-assumes -prove-asserts -verify`) |
| **Command** | `make formal` (`bash formal/run_formal.sh all 25`) |
| **Proof Type** | Bounded Model Checking (BMC), depth = 25 cycles |
| **SymbiYosys Note** | `sby` frontend is not installed in WSL; `.sby` files (`formal/m{0,1,2}.sby`) are provided for `sby`-equipped hosts, while `run_formal.sh` invokes Yosys's built-in SAT BMC engine directly. |

## Bounded Model Checking Results (Depth = 25 Cycles)

| Config | Task | `ASSUME_CLEAN` | Properties Verified | Result |
|---|---|---:|---|---|
| **M0** (`pc_monitor`) | `m0_invariants` | 0 | Reset suppression, sticky persistence, first-fault class stability, alignment/bounds detection | **PASS** (`SAT proof finished - no model found: SUCCESS!`) |
| **M0** (`pc_monitor`) | `m0_clean` | 1 | Zero false positives (`!fault_detected && !fault_sticky`) under legal aligned in-bounds PCs | **PASS** |
| **M1** (`branch_monitor`) | `m1_invariants` | 0 | Reset suppression, sticky persistence, spurious redirect / non-seq jump detection | **PASS** |
| **M1** (`branch_monitor`) | `m1_clean` | 1 | Zero false positives under legal `pipeline_control` + `program_counter` assumptions (incl. conservative hold) | **PASS** |
| **M2** (`pipeline_monitor`) | `m2_invariants` | 0 | Reset suppression, sticky persistence, branch priority & stall/flush consistency | **PASS** |
| **M2** (`pipeline_monitor`) | `m2_clean` | 1 | Zero false positives under legal hazard, control, and stage-progression assumptions | **PASS** |

## Environmental Assumptions & Proof Bounds

- **Initial state:** Cycle 0 starts in reset (`assume(rst)` when `!f_past_valid`).
- **Clean-mode assumptions (`ASSUME_CLEAN=1`):** Inputs satisfy the documented contracts of `program_counter`, `pipeline_control`, `hazard_detection_unit`, and pipeline stage registers.
- **Proof scope limitation:** These are **25-cycle bounded** proofs on the monitor modules themselves (`pc_monitor`, `branch_monitor`, `pipeline_monitor`); they do **not** constitute unbounded induction or full-processor formal correctness.
