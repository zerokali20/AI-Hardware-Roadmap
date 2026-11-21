# Limitations and Threats to Validity — PipeGuard-RV

Transparency regarding technical constraints and experimental limitations is essential for rigorous research. Below is an honest enumeration of the architectural, methodological, and physical limitations of PipeGuard-RV.

---

## 1. Physical & Silicon Realism

1. **Simulation-Only Evaluation (No Silicon Realization):**  
   All evaluations are conducted in logic simulation environments (Icarus Verilog co-simulated with cocotb). No physical silicon prototypes (ASIC tape-outs or FPGA emulations) were manufactured. As a result, physical parasitics, wire delays, temperature variations, and layout routing congestion are not captured.

2. **Synthesis Approximations with Generic Cells:**  
   Logic synthesis is executed using Yosys 0.33 targeting generic standard cell primitives. Area metrics are reported as gate/cell counts rather than standard cell library square micrometers ($\mu m^2$) from a commercial PDK (e.g., TSMC 28nm or SkyWater 130nm). Power and critical path timing are similarly uncharacterized.

---

## 2. Fault Model Scope

3. **Single Transient Inversion Assumption:**  
   The fault campaign evaluates discrete, single-bit, single-cycle transient inversions ($0 \to 1$ or $1 \to 0$). Multi-Bit Upsets (MBUs), spatial cluster faults (e.g., charge-sharing among adjacent flip-flops caused by heavy-ion strikes), and permanent stuck-at defects are not modeled.

4. **Synchronous Behavioral Forcing:**  
   Faults are forced synchronously at clock edges via cocotb simulator APIs. Real physical transients (clock glitches, laser pulses) can occur asynchronously during setup/hold windows, producing metastable oscillations that digital simulation cannot replicate.

---

## 3. Microarchitectural & Core Constraints

5. **Educational RV32I Processor Base:**  
   The baseline processor (`riscv_pipeline_cpu`) is an educational 5-stage in-order pipeline. It lacks advanced features found in production embedded cores:
   - No branch prediction or branch target buffer (BTB) (branches are evaluated strictly in EX).
   - No L1 instruction/data caches or virtual memory translation (MMU/PMP).
   - Bare-metal RV32I only (no M-extension multiply/divide, Compressed 'C', or Floating-Point 'F').

6. **Observability vs. Encapsulation Trade-Off:**  
   Several key pipeline control signals (`if_id_stall`, `id_ex_flush`, `branch_taken`, `pc_target`) are internal nets inside `riscv_pipeline_cpu.sv`. Evaluating M2 requires either tapping these nets or introducing a wrapper that exposes them. In real silicon, routing deep internal nets to an external checker adds routing congestion and capacitive loading.

7. **Shared Control Wire Vulnerability (Self-Checking Limits):**  
   If an adversary injects a fault into a shared control wire that is also monitored by the checker, circular dependency can occur: the monitor may read the corrupted signal as intentional processor state. PipeGuard detects *discrepancies* between independent datapath stages; it cannot guarantee detection if a fault affects the monitor's own sensing inputs without redundant sensing paths.
