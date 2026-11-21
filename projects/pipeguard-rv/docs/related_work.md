# Related Work & Context — PipeGuard-RV

## 1. Context and Prior Art

Hardware-assisted Control-Flow Integrity (CFI) and microarchitectural fault detection have been extensively explored in literature. PipeGuard-RV builds upon concepts established by prior hardware security architectures while maintaining a focused, open-source educational scope.

### 1.1 Hardware Control-Flow Integrity (CFI)

- **MAFIA (Microarchitectural Attack and Fault Integrity Architecture):**  
  MAFIA proposes hardware extensions for tracking control flow through cryptographic branch signatures or shadow call stacks directly integrated into the processor pipeline. While effective against ROP attacks, MAFIA architectures typically require custom instruction set extensions, tag memories, or cryptographic hash accelerators that impose significant silicon area and memory bandwidth overheads.
  
- **DExIE (Dual-Execution with Invariant Enforcement):**  
  DExIE and related architectures explore decoupled dual-core or fine-grained execution invariant checking. By validating decoded control signals against pre-computed compiler metadata or duplicate execution slices, DExIE achieves high coverage against transient faults and malicious perturbations. However, duplicated hardware pipelines approach Dual Modular Redundancy (DMR) overheads (>50–100% logic increase).

- **Hardware Watchdogs & Signature Monitoring (e.g., Watchdog Timers, CFI Coprocessors):**  
  Traditional external coprocessors monitor PC buses over dedicated trace ports. While non-intrusive to core execution, their observation is delayed by trace export pipelines, leading to multi-cycle detection latencies during which corrupted instructions may commit state to the register file or memory.

---

## 2. Positioning and Scientific Contribution

> **Scientific Posture:**  
> PipeGuard-RV does **not** claim to be the first hardware fault detector for RISC-V processors, nor does it claim novel cryptographic CFI primitives.

Instead, PipeGuard-RV's contributions lie in an **empirical, open-source microarchitectural trade-off evaluation**:

1. **Quantified Granularity vs. Cost Spectrum:**  
   Direct comparison across four uniform, well-defined configurations (B0 baseline, M0 architectural PC monitor, M1 branch-aware monitor, and M2 pipeline-hazard-aware monitor) on the exact same 5-stage RV32I pipeline.
   
2. **Microarchitectural Hazard Invariants:**  
   Investigating whether snooping internal pipeline control arbitration (`load_use_stall`, `id_ex_flush`, `branch_redirect`) provides measurable fault detection advantages before instruction commit compared to simpler architectural PC tracking.

3. **Fully Open & Reproducible Methodology:**  
   Providing a complete open-source artifact using freely available tools (Icarus Verilog, cocotb, Yosys, SymbiYosys, Python) where every claim is validated by automated CI regressions and reproducible fault injection campaigns.
