# Threat Model and Fault Taxonomy — PipeGuard-RV

## 1. Motivation and Attacker Profile

### 1.1 Physical Adversary Motivation
In physical security and high-reliability operating contexts (aerospace, automotive safety microcontrollers, secure enclaves), processors are exposed to transient faults:
- **Environmental Radiation / SEUs:** Cosmic ray neutron strikes or alpha particle ionization causing single-event upsets (SEUs) in internal flip-flops and combinational logic.
- **Physical Fault Injection (FI):** Adversaries with physical access employing non-invasive or semi-invasive techniques (clock glitching, supply voltage undervolting, Laser Fault Injection [LFI], Electromagnetic Fault Injection [EMFI]) to bypass authentication, skip authorization checks, or alter program flow.

### 1.2 Simulation Model for Evaluation
PipeGuard-RV operates strictly in digital logic simulation (Icarus Verilog co-simulated via Python cocotb). We abstract physical fault mechanisms into precise, discrete microarchitectural fault primitives injected via simulator force/deposit hooks at exact clock cycle edges.

## 2. Targeted Fault Models

The fault injection framework specifically targets transient single-bit upsets (1-cycle pulse flips: $0 \to 1$ or $1 \to 0$) in three microarchitectural subsystems:

### 2.1 Class A: Program Counter Datapath Faults
- **Target Signals:** `fetch_pc`, `pc_target`, `program_counter` register state.
- **Microarchitectural Effect:**
  - Corrupting PC bits causes sequential flow to leap into unmapped or misaligned memory regions.
  - Bit-flips in lower bits ($PC[1:0]$) produce instruction alignment faults.
  - Bit-flips in upper bits jump to arbitrary code or data segments.

### 2.2 Class B: Branch Evaluation and Target Signals
- **Target Signals:** `branch_taken`, `branch_target`, `invalid_branch`, `branch_redirect`.
- **Microarchitectural Effect:**
  - False branch taken: Condition evaluates false, but control logic initiates redirect to an arbitrary or computed target.
  - Suppressed branch: Condition evaluates true, but branch is ignored, causing sequential execution past a jump/guard.
  - Branch target corruption: Correctly taken branch redirects to a corrupted destination.

### 2.3 Class C: Pipeline Hazard and Control Signals
- **Target Signals:** `load_use_stall`, `if_id_stall`, `if_id_flush`, `id_ex_stall`, `id_ex_flush`, `stall_request`, `forward_a`, `forward_b`.
- **Microarchitectural Effect:**
  - Suppressed flush on branch redirect: Stale instructions in IF/ID or ID/EX continue executing alongside redirected instructions (instruction duplication / ghost instructions).
  - Spurious flush: Pipeline flushes without cause, creating silent instruction loss.
  - Corrupted stall: Failure to stall on load-use hazard leads to raw data hazards and executing with uninitialized/stale operand data.

## 3. Assumptions

1. **Golden Hardware Base:** The underlying standard cell logic and silicon fabric are free of permanent physical defects (stuck-at faults) and fabrication errors prior to the transient event.
2. **Single-Fault Hypothesis:** Only a single microarchitectural node is faulted within any given clock cycle interval (standard single-fault assumption for transient analysis).
3. **Monitor Integrity:** The PipeGuard monitor logic is assumed hardened, synthesized close to checked registers, or placed in a dedicated hardened logic enclave (evaluating self-faulting monitors is out of scope).
4. **Clock and Reset Stability:** System master clock and synchronous active-low reset lines are non-glitched during normal test execution.

## 4. Out-of-Scope Security Domains

The following domains are explicitly out of scope for PipeGuard-RV:
- **Permanent / Stuck-at Hardware Faults:** Requires scan-chain BIST (Built-In Self-Test) or ECC/parity cell architectures.
- **Multi-bit Random Upsets:** Beyond double-bit or random byte corruptions unless handled incidentally by parity.
- **Physical Side-Channel Attacks:** Power analysis (DPA/CPA), electromagnetic emanation analysis, or timing cache side-channels (e.g., Spectre/Meltdown).
- **Software Exploitation / Memory Corruption:** Buffer overflows, ROP/JOP chains executing entirely within valid architectural ISA rules that do not trigger hardware control-flow anomalies.
- **Full Privilege / Multi-Ring Architectures:** S-Mode, U-Mode, virtual memory translation (MMU/PMP), or trap return semantics (`mret`/`sret`), as the baseline is a bare-metal RV32I educational pipeline.
