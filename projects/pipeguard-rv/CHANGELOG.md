# Changelog — PipeGuard-RV

All significant changes to the research project are documented here.  
Format loosely follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Next
- Phase 3: PC-Based Monitor (M0)

---

## [0.3.0] — 2026-11-24 — Phase 2: B0 Observation Top, Lock-Step Equivalence & Baseline Synthesis

### Added
- `rtl/common/pipeguard_defs.svh`: Shared `MONITOR_CFG` (`CFG_B0..M2`) and `FAULT_CLASS` encodings
- `rtl/top/riscv_pipeline_cpu_obs.sv`: Observation-enabled research core exposing `obs_*` internal wires
- `rtl/top/pipeguard_cpu.sv`: Common configurable CPU top (`MONITOR_CFG=0` → B0)
- `rtl/core/SHA256SUMS`: SHA-256 manifest verifying all 26 snapshot `.sv` files match `labs/06-riscv-pipeline/rtl/` byte-for-byte
- `tb/baseline/Makefile`, `scripts/check_results.py`, `scripts/run_baseline_regression.sh`: Isolated project-local regression runner
- `tb/hdl/tb_lockstep.sv`, `tb/common/rv32i.py`, `tb/common/programs.py`, `tb/test_b0_equivalence.py`, `tb/Makefile`: Lock-step equivalence harness
- `synthesis/synth.tcl`: Parameterized Yosys synthesis script (`synth -top pipeguard_cpu -noabc`)
- `results/raw/phase2_b0_verification.md`, `results/synthesis/b0_synth.md`, `results/processed/baseline_regression_summary.csv`

### Verified
- Full 30-suite snapshot regression against `rtl/core/`: **319/319 PASS** (`FAIL=0`, `SKIP=0`)
- B0 lock-step equivalence (`make test CONFIG=b0`): **2/2 cocotb tests PASS** (15 directed + 10 random RV32I programs)
- Verilator 5.020 lint (`make lint`): exit 0 (with documented `UNUSEDSIGNAL` and `WIDTHEXPAND` suppressions)
- Yosys 0.33 B0 synthesis (`make synth CONFIG=b0`): **77,241 generic cells** (9,756 FFs, 67,485 combinational cells)

---

## [0.2.0] — 2026-11-21 — Phase 1: Baseline CPU Snapshot & Documentation Complete

### Added
- `rtl/core/`: Exact snapshot of 24 Lab 06 `.sv` files copied to project
- `rtl/core/PROVENANCE.md`: Provenance tracking for baseline RTL snapshot (HEAD `0be8905`)
- `scripts/setup.sh`: Automated environment verification and setup script
- `docs/research_scope.md`: Research questions, objectives, scope boundaries
- `docs/threat_model.md`: Transient fault taxonomy, adversary model, simulation assumptions
- `docs/architecture.md`: Four configurations (B0, M0, M1, M2), adapter wrapper, alarm interface
- `docs/signal_map.md`: Observable ports vs. internal wires, pipeline control priority logic
- `docs/verification_plan.md`: Multi-tier testing, regression reuse, formal BMC plan
- `docs/experimental_methodology.md`: Fault injection protocols, benchmark workloads, metrics
- `docs/related_work.md`: Comparison with MAFIA and DExIE, empirical positioning
- `docs/limitations.md`: Comprehensive limitations and threats to validity
- `paper/outline.md`: Research paper structure and section plan
- `.github/workflows/pipeguard-rv.yml`: CI workflow for baseline regression & structure check
- `results/raw/phase1_baseline_regression.md`: Full regression report

### Verified (Phase 1 Baseline Regression)
- Stale `sim_build` error on `pipectrl` resolved by `make clean`
- Full baseline regression completed: **10 suites, 99 tests run, 99 PASS, 0 FAIL**
  - `cpu`: 5/5 PASS
  - `cpuhaz`: 7/7 PASS
  - `cpuisa`: 6/6 PASS
  - `cpumembranch`: 15/15 PASS
  - `pipectrl`: 10/10 PASS
  - `pc`: 6/6 PASS
  - `ifid`: 6/6 PASS
  - `alu`: 12/12 PASS
  - `hazard`: 18/18 PASS
  - `forward`: 14/14 PASS

---

## [0.1.0] — 2026-11-21 — Phase 0: Repository Audit Complete

### Added
- Project skeleton: `projects/pipeguard-rv/` directory tree with `rtl/`, `tb/`, `docs/`, `results/`, `scripts/`, `simulation/`, `synthesis/`, `formal/`, `experiments/`, `paper/`, `workloads/`
- `README.md` — project overview and quick-start
- Empty skeleton files: `IMPLEMENTATION_PLAN.md`, `AGENTS.md`, `CHANGELOG.md`, `Makefile`, `requirements.txt`, `.gitignore`
- `.github/workflows/pipeguard-rv.yml` — CI workflow skeleton (untracked at time of audit)

### Verified (Phase 0 Audit Findings)
- **HEAD SHA:** `0be8905` (branch: `main`)
- **Baseline RTL:** `labs/06-riscv-pipeline/rtl/` — 24 `.sv` files; confirmed as canonical CPU source
- **Lab 07 RTL:** `labs/07-riscv-synthesis/rtl/cpu/` is a **verbatim copy** of Lab 06 RTL (diff confirmed identical)

#### Regression Results (Phase 0 — actual simulator output, not assumed)

| Suite | Tests Run | PASS | FAIL | Notes |
|-------|-----------|------|------|-------|
| `cpu` | 5 | 5 | 0 | Full CPU integration |
| `cpuhaz` | 7 | 7 | 0 | Hazard detection |
| `cpuisa` | 6 | 6 | 0 | ISA instruction coverage |
| `cpumembranch` | 15 | 15 | 0 | Memory + branch integration |
| `pipectrl` | — | — | — | **INFRA ERROR**: VPI toplevel mismatch (stale `sim_build/`) — not an RTL bug |
| **Total** | **33** | **33** | **0** | — |

#### Tool Inventory (WSL)

| Tool | Version |
|------|---------|
| iverilog | 12.0 (stable) |
| Yosys | 0.33 |
| Python | 3.12.3 |
| GNU Make | 4.3 |
| cocotb | 2.1.0 (in `labs/06-riscv-pipeline/.venv/`) |

#### Signal Map (key finding)

The following signals are **observable at the top-level ports** of `riscv_pipeline_cpu`:
`fetch_pc`, `decode_pc`, `execute_pc`, `mem_pc`, `wb_pc`, `wb_data`, `wb_rd`, `wb_reg_write`, `load_use_stall`, `branch_redirect`, `alignment_fault`, `memory_alignment_error`, `memory_access_error`, `illegal_instruction`

The following are **internal wires only** (not observable at top):
`pc_stall`, `if_id_stall`, `if_id_flush`, `id_ex_stall`, `id_ex_flush`, `pc_target`, `branch_taken`, `branch_target`, `invalid_branch`, `stall_request`, `forward_a`, `forward_b`, `unresolved_load_dependency`, `link_address`, `alu_result`, `store_data`

This distinction is architecturally critical: monitor designs that need internal signals must use a wrapper or add ports to a research copy. The original Lab 06 files must not be modified.

### Not Changed
- Lab 06 RTL — no modifications; audit is read-only
- Lab 07 RTL — no modifications

---

*Date format: YYYY-MM-DD. Versions track research milestones, not software releases.*
