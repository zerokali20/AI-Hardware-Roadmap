# PipeGuard-RV — Agent Working Rules and Context
# For AI coding agents (Antigravity, Gemini CLI, Copilot, etc.)

---

## 1. Project Identity

**Project:** PipeGuard-RV  
**Goal:** Research lightweight hardware fault-detection monitors for a 5-stage RISC-V pipeline processor.  
**Status:** Phase 1 (Baseline CPU Snapshot) in progress. Phase 0 (Audit) complete.  
**HEAD SHA at project start:** `0be8905`  
**Branch:** `main`

---

## 2. Workspace Paths

| Environment | Path |
|-------------|------|
| Windows (PowerShell) | `D:\AI-Hardware-Roadmap` |
| WSL (bash) | `/mnt/d/AI-Hardware-Roadmap` |
| Lab 06 RTL (canonical, read-only) | `labs/06-riscv-pipeline/rtl/` |
| Lab 06 testbenches | `labs/06-riscv-pipeline/tb/` |
| Lab 06 venv | `labs/06-riscv-pipeline/.venv/` |
| Project root | `projects/pipeguard-rv/` |
| Research RTL core (read-only copy) | `projects/pipeguard-rv/rtl/core/` |
| Monitor RTL (new, write here) | `projects/pipeguard-rv/rtl/monitors/` |
| Wrapper tops (new, write here) | `projects/pipeguard-rv/rtl/top/` |
| Testbenches | `projects/pipeguard-rv/tb/` |
| Results | `projects/pipeguard-rv/results/` |
| Docs | `projects/pipeguard-rv/docs/` |

---

## 3. Critical Architecture Constraints

### 3.1 Signal Observability — This Is Not Optional

The `riscv_pipeline_cpu` top module exposes **only** the following output ports.
Any monitor design that needs other signals MUST use a wrapper or port-added research copy.

**Observable at top-level ports:**

| Signal | Type | Width | Description |
|--------|------|-------|-------------|
| `fetch_pc` | output | 32-bit | PC of instruction in IF stage |
| `decode_pc` | output | 32-bit | PC of instruction in ID stage |
| `execute_pc` | output | 32-bit | PC of instruction in EX stage |
| `mem_pc` | output | 32-bit | PC of instruction in MEM stage |
| `wb_pc` | output | 32-bit | PC of instruction in WB stage |
| `wb_data` | output | 32-bit | Write-back data |
| `wb_rd` | output | 5-bit | Write-back destination register |
| `wb_reg_write` | output | 1-bit | Write-back register-write enable |
| `load_use_stall` | output | 1-bit | Load-use hazard stall active |
| `branch_redirect` | output | 1-bit | Branch/jump redirect active (= `pc_redirect` internally) |
| `alignment_fault` | output | 1-bit | Branch target misaligned |
| `memory_alignment_error` | output | 1-bit | Data memory alignment error |
| `memory_access_error` | output | 1-bit | Data memory access error |
| `illegal_instruction` | output | 1-bit | Illegal instruction detected |

**Internal wires only — NOT observable at top (do NOT design monitors assuming these are ports):**

`pc_stall`, `if_id_stall`, `if_id_flush`, `id_ex_stall`, `id_ex_flush`, `pc_target`, `branch_taken`, `branch_target`, `invalid_branch`, `stall_request`, `forward_a`, `forward_b`, `unresolved_load_dependency`, `link_address`, `alu_result`, `store_data`

### 3.2 Pipeline Control Priority Logic

From `pipeline_control.sv` (verified against actual RTL):

```systemverilog
// Redirect has PRIORITY over stall
alignment_fault = valid_redirect && (branch_target[1:0] != 2'b00);
pc_redirect      = valid_redirect && !alignment_fault;

// When redirect: flush both IF/ID and ID/EX; no stall
if_id_flush = pc_redirect;
id_ex_flush = pc_redirect;

// When stall (load-use): stall PC and IF/ID, flush ID/EX
pc_stall     = stall_request;
if_id_stall  = stall_request;
id_ex_flush  = id_ex_flush || stall_request;  // combinational OR

// When alignment fault: stall (no redirect); flush ID/EX
pc_stall    |= alignment_fault;
if_id_stall |= alignment_fault;
id_ex_flush |= alignment_fault;
```

**Key implications for monitor design:**
- `branch_redirect` being asserted at the top level means a successful redirect — it is NOT asserted on alignment faults (those stall instead)
- `alignment_fault` is asserted at the top level and indicates misaligned branch target; the CPU stalls, not redirects
- Stall and redirect can interact — monitors should NOT assume mutual exclusivity without reading the RTL

### 3.3 Four Research Configurations

| Config | Description | Monitor RTL |
|--------|-------------|-------------|
| B0 | Unprotected baseline — wrapper only, no monitor | None |
| M0 | PC-based monitor — detects unexpected PC jumps | `rtl/monitors/pc_monitor.sv` |
| M1 | Branch-aware monitor — M0 + branch-redirect awareness | `rtl/monitors/branch_monitor.sv` |
| M2 | Pipeline-aware monitor — M1 + load-use stall + alignment-fault awareness | `rtl/monitors/pipeline_monitor.sv` |

---

## 4. Working Rules

### 4.1 Before Modifying Any File
- **Read the file first.** Use `read_file` before `write_file` or `edit_file`.
- **Check the phase.** Only create files in phases that are IN PROGRESS or later.
- **Never edit `rtl/core/*.sv`** — this is the unmodified research snapshot of Lab 06.
- **Never edit `labs/06-riscv-pipeline/`** — the original lab is read-only.

### 4.2 Before Claiming a Test Passes
- Run the actual simulator command and capture the output.
- Record exact pass/fail counts as reported by cocotb/pytest.
- Do NOT claim `33 PASS` without running the tests; do NOT fabricate or extrapolate counts.
- If a test produces an infra error (e.g., stale `sim_build/`), run `make clean` first and document both results.

### 4.3 Fabrication Is Forbidden
- Never invent test results, coverage numbers, cell counts, or detection rates.
- Never fill in a results table with placeholder numbers that look real (e.g., "92% detection").
- Placeholder text must be clearly marked: "PLACEHOLDER — experiment not yet run" or similar.
- If asked to report a result, run the experiment or leave the field blank.

### 4.4 Git Discipline
- Do NOT push to remote without explicit user instruction.
- Do NOT create new branches without explicit user instruction.
- Commit messages must include phase number and brief description.
- Tag format: `pipeguard-rv-baseline-0` for the Phase 1 baseline commit.

### 4.5 File Ownership
See §6 (File Ownership Map). Do not create files in a phase you do not own without coordination.

---

## 5. What NOT to Do

| Prohibited Action | Reason |
|-------------------|--------|
| Edit `labs/06-riscv-pipeline/**` | Original lab — must remain untouched for reproducibility |
| Edit `rtl/core/*.sv` | Unmodified research snapshot — treat as read-only |
| Fabricate test counts, coverage %, or synthesis numbers | Academic integrity; results must be real |
| Push to remote | User must authorise all pushes |
| Create new git branches | User must authorise branch creation |
| Assume internal signals are observable | They are not — see §3.1 |
| Claim `pipectrl` passed without re-running clean | Phase 0 found stale-sim infra error — must `make clean` first |
| Use non-WSL tool paths in simulation commands | Icarus and Yosys are WSL tools; use `wsl -e bash -c "..."` from PowerShell |

---

## 6. File Ownership Map

| File/Directory | Owner Phase | Notes |
|----------------|-------------|-------|
| `rtl/core/*.sv` | Phase 1 (read-only copy) | Created by baseline-snapshot worker; never modified |
| `rtl/core/PROVENANCE.md` | Phase 1 | Documents source SHA and no-edit policy |
| `rtl/top/monitor_adapter.sv` | Phase 2 | Wrapper that adds internal ports for monitor access |
| `rtl/top/pipeguard_top_b0.sv` | Phase 2 | B0 configuration top |
| `rtl/monitors/pc_monitor.sv` | Phase 3 | M0 monitor |
| `rtl/top/pipeguard_top_m0.sv` | Phase 3 | M0 configuration top |
| `rtl/monitors/branch_monitor.sv` | Phase 4 | M1 monitor |
| `rtl/monitors/pipeline_monitor.sv` | Phase 4 | M2 monitor |
| `rtl/top/pipeguard_top_m1.sv` | Phase 4 | M1 configuration top |
| `rtl/top/pipeguard_top_m2.sv` | Phase 4 | M2 configuration top |
| `tb/` | Phases 2–6 | Per-phase and per-monitor testbenches |
| `results/raw/` | Phases 1–7 | Raw simulator and synthesis output; never hand-edited |
| `results/synthesis/` | Phase 7 | Parsed Yosys output |
| `results/figures/` | Phase 8 | Generated by analysis scripts |
| `docs/` | Phase 0–1 | Architecture docs; updated each phase as needed |
| `paper/` | Phase 8 | Paper draft; must cite results from `results/` |
| `formal/` | Phase 5 | SymbiYosys `.sby` files and results |
| `scripts/` | Phases 1–9 | Setup, reproduction, analysis scripts |
| `IMPLEMENTATION_PLAN.md` | Coordinator | Update status checkboxes each phase |
| `CHANGELOG.md` | Coordinator | Log each phase completion |

---

## 7. Phase Dependency Rules

A phase may not begin until all its prerequisites are ✅ COMPLETE:

```
Phase 0 → Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5
                                              ↓           ↓
                                         Phase 6     Phase 5
                                              ↓
                     Phase 7 (also needs Phase 2–4 for monitor RTL)
                              ↓
                         Phase 8 (needs 6 + 7)
                              ↓
                         Phase 9
```

Do NOT begin monitor RTL work (Phase 3+) until the B0 wrapper (Phase 2) compiles and passes regression.

---

## 8. Simulation Commands (WSL)

```bash
# Activate Lab 06 venv (from WSL)
source /mnt/d/AI-Hardware-Roadmap/labs/06-riscv-pipeline/.venv/bin/activate

# Run a specific test suite
cd /mnt/d/AI-Hardware-Roadmap/labs/06-riscv-pipeline
make clean && make TEST=cpu

# Run from PowerShell
wsl -e bash -c "cd /mnt/d/AI-Hardware-Roadmap/labs/06-riscv-pipeline && source .venv/bin/activate && make clean && make TEST=cpu 2>&1 | tail -20"
```

---

## 9. Alarm Interface (Monitor Output)

All monitors expose a common alarm interface:

| Signal | Width | Description |
|--------|-------|-------------|
| `fault_detected` | 1-bit | Combinational — fault condition active this cycle |
| `fault_sticky` | 1-bit | Registered — latches high until reset; cleared by `fault_clear` input |
| `fault_class` | 3-bit | Fault category: `3'b001` = PC jump, `3'b010` = branch, `3'b100` = pipeline-ctrl |

---

## 10. Contact and Escalation

If you hit a blocker not covered by these rules:
1. Post to the swarm board: `@coordinator <description of blocker>`
2. Do NOT invent a workaround that changes the architecture — wait for a decision
3. Do NOT modify lab files or push to remote as a workaround
