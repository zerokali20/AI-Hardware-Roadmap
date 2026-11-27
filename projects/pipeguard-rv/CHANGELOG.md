# Changelog — PipeGuard-RV

All significant changes to the research project are documented here.  
Format loosely follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Next
- Phase 9: Reproducibility Package

---

## [0.8.0] — 2026-11-27 — Phase 7 (Comparative Synthesis) & Phase 8 (Analysis, Figures & Paper Draft) Complete

### Added
- `scripts/parse_synth.py`, `results/synthesis/synth_summary.{csv,json}`, `results/synthesis/comparative_synthesis.md`
- `scripts/analyze_results.py`: Generates 6 reproducible figures in `results/figures/` (`fig1_coverage_by_config.png` .. `fig6_coverage_vs_cost.png`)
- `paper/references.bib`, `paper/draft_v1.md`: Complete paper draft with all metrics traced to `results/`

### Verified
- `make synth CONFIG=all` / `parse_synth.py`: Total overhead +0.13% (`M0`), +0.73% (`M1`), +1.47% (`M2`); logic-only excl. memories +1.36% (`M0`), +7.27% (`M1`), +14.87% (`M2`)
- `make analyze`: All 6 figures generated cleanly from measured `full` campaign and synthesis datasets

---

## [0.7.0] — 2026-11-26 — Phase 6: Controlled Fault-Injection Campaign Complete

### Added
- `workloads/workloads.py`, `workloads/README.md`: 8 deterministic RV32I workloads (incl. `iot_controller`)
- `simulation/fault_campaign_tb.py`: Golden-trace cocotb fault-injection harness with independent 6-class outcome classification
- `experiments/configs/{smoke,full}.yaml`, `experiments/run_campaign.py`, `experiments/metrics.py`
- `results/processed/campaign_summary_{smoke,full}.{csv,json}`, `results/raw/phase6_fault_campaign.md`

### Verified
- `make smoke` (112 experiments): `B0` 0.00%, `M0` 36.36%, `M1` 72.73%, `M2` 100.00% (0% FPR across 215 fault-free cycles)
- `make campaign` (`full.yaml`, 864 experiments): `B0` 0.00%, `M0` 25.95%, `M1` 51.89%, `M2` 84.32% (0% FPR across 450 fault-free cycles; 100% on `pc` and `pipeline_control`)

---

## [0.6.0] — 2026-11-25 — Phase 5: Formal Verification (BMC Depth 25) Complete

### Added
- `formal/m0_formal.sv`, `formal/m1_formal.sv`, `formal/m2_formal.sv`: Formal property harnesses (`ASSUME_CLEAN=0` invariants & `ASSUME_CLEAN=1` zero-FP proofs)
- `formal/m0.sby`, `formal/m1.sby`, `formal/m2.sby`, `formal/run_formal.sh`: SymbiYosys configs and Yosys SAT BMC runner
- `results/raw/phase5_formal_verification.md`: Phase 5 proof summary, assumptions, and bounds

### Verified
- `make formal`: **6/6 BMC proofs PASS** at depth 25 (`m0_invariants`, `m0_clean`, `m1_invariants`, `m1_clean`, `m2_invariants`, `m2_clean`) via Yosys 0.33 `sat -seq 25`

---

## [0.5.0] — 2026-11-25 — Phase 4: M1 (`branch_monitor`) & M2 (`pipeline_monitor`) Complete

### Added
- `rtl/monitors/branch_monitor.sv`: Synthesizable M1 monitor (M0 + cycle-correct PC transitions, redirect validity/target checks, conservative PC hold acceptance)
- `rtl/monitors/pipeline_monitor.sv`: Synthesizable M2 monitor (M1 + strict PC progression, independent load-use hazard check, stall/flush/priority consistency, stage PC progression)
- `rtl/top/pipeguard_cpu.sv`: Wired `MONITOR_CFG == PG_CFG_M1` and `PG_CFG_M2`
- `tb/test_branch_monitor.py`, `tb/test_pipeline_monitor.py`, `tb/test_m1_integration.py`, `tb/test_m2_integration.py`
- `results/raw/phase4_m1_m2_verification.md`, `results/synthesis/m1_m2_synth.md`

### Verified
- `branch_mon` (4/4), `pipe_mon` (4/4), `b0_equiv` (2/2), `m0_equiv` (5/5), `m1_equiv` (5/5), `m2_equiv` (5/5): **ALL PASS**
- `make lint` (`MONITOR_CFG=0..3`): Verilator 5.020 exits 0
- `make synth` (`b0`, `m0`, `m1`, `m2`): 77,241 / 77,345 (+0.135%) / 77,803 (+0.728%) / 78,380 (+1.475%) generic cells

---

## [0.4.0] — 2026-11-25 — Phase 3: PC-Based Monitor (M0) Complete

### Added
- `rtl/monitors/pc_monitor.sv`: Synthesizable M0 monitor (4-byte alignment + configurable `[PC_MIN, PC_MAX]` bounds, reset-safe sticky alarm, deterministic `PG_FC_PC_MISALIGNED` > `PG_FC_PC_OUT_OF_BOUNDS` classification)
- `rtl/top/pipeguard_cpu.sv`: Wired `MONITOR_CFG == PG_CFG_M0` to `pc_monitor`
- `tb/test_pc_monitor.py`, `tb/test_m0_integration.py`: Unit tests, 25-program lock-step zero-FP checks, and synthetic PC fault-injection tests
- `results/raw/phase3_m0_verification.md`, `results/synthesis/m0_synth.md`: Phase 3 test and Yosys overhead reports

### Verified
- `make monitor-test CONFIG=m0`: **5/5 PASS**
- `make test CONFIG=m0` (includes `pc_mon` + `m0_equiv`): **5/5 unit + 5/5 integration PASS** (0 false positives across 15 directed + 10 random programs; aligned in-range blind spot confirmed)
- `make lint`: Verilator 5.020 exits 0 with `MONITOR_CFG=1`
- `make synth CONFIG=m0`: **77,345 generic cells** (+104 cells / +0.135% vs. B0; +3 FFs, +101 combinational)

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
