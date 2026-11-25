# PipeGuard-RV — Implementation Plan

> **Project:** PipeGuard-RV — Lightweight Hardware Fault-Detection Monitors for a 5-Stage RISC-V Pipeline  
> **Baseline SHA:** `0be8905` (branch: `main`)  
> **Plan last updated:** 2026-11-21  
> **Status key:** ✅ COMPLETE · 🔄 IN PROGRESS · ⬜ TODO

---

## Phase Dependency Graph

```
Phase 0 (Audit) ──► Phase 1 (Baseline Snapshot)
                         │
                         ▼
                    Phase 2 (B0 Monitor Wrapper)
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
         Phase 3 (M0)         Phase 2 side-products
              │
         Phase 4 (M1 / M2)
              │
         Phase 5 (Formal)
              │
         Phase 6 (Fault Campaign)
              │
         Phase 7 (Synthesis)
              │
         Phase 8 (Analysis & Paper)
              │
         Phase 9 (Reproducibility)
```

---

## Phase 0 — Repository Audit & Environment Verification ✅ COMPLETE

**Goal:** Establish a verified, reproducible baseline before writing a single line of research code.

### Tasks
- [x] **P0.1** Record HEAD SHA: `0be8905` (branch: `main`)
- [x] **P0.2** Enumerate Lab 06 RTL: 24 `.sv` files in `labs/06-riscv-pipeline/rtl/`
- [x] **P0.3** Compare Lab 07 RTL with Lab 06 RTL — confirmed verbatim copy (diff clean)
- [x] **P0.4** Read `riscv_pipeline_cpu.sv` — identify all top-level observable output ports
- [x] **P0.5** Read `pipeline_control.sv` — document priority logic (redirect > stall)
- [x] **P0.6** Read `hazard_detection_unit.sv`, `branch_unit.sv`, `execute_forwarding_stage.sv`, `instruction_fetch.sv`
- [x] **P0.7** Confirm WSL tool versions: iverilog 12.0, Yosys 0.33, Python 3.12.3, GNU Make 4.3, cocotb 2.1.0
- [x] **P0.8** Run Lab 06 regression — actual results:
  - `cpu`: 5/5 PASS
  - `cpuhaz`: 7/7 PASS
  - `cpuisa`: 6/6 PASS
  - `cpumembranch`: 15/15 PASS
  - `pipectrl`: INFRA ERROR (VPI toplevel mismatch — stale `sim_build/`, **not an RTL bug**)
  - **Total: 33 tests run, 33 PASS, 0 FAIL**
- [x] **P0.9** Document signal observability map (see `docs/signal_map.md`)
- [x] **P0.10** Create project skeleton directory structure

### Acceptance Criteria
- HEAD SHA recorded and reproducible with `git log --oneline -1`
- Signal map distinguishes observable vs. internal-only wires with RTL evidence
- All regression pass/fail counts verified by actual simulator output — no fabrication

### Findings & Notes
- Lab 06 README claims "30 suites / 329 tests"; actual run found 4 clean suites totalling 33 tests (the 30-suite claim includes unit-level targets; `pipectrl` suite had stale `sim_build` infra error)
- `pipectrl` stale-sim error is **not** a CPU RTL defect; must `make clean` before re-running
- Internal signals (`pc_stall`, `if_id_flush`, `if_id_stall`, `id_ex_flush`, etc.) are **NOT** observable at the top-level ports — the monitor adapter design must account for this

---

## Phase 1 — Baseline CPU Snapshot ✅ COMPLETE

**Goal:** Copy canonical Lab 06 RTL into the research project, re-run pipectrl clean, establish the unmodified golden reference.

### Tasks
- [x] **P1.1** Copy all 26 `.sv` files from `labs/06-riscv-pipeline/rtl/` → `projects/pipeguard-rv/rtl/core/` (byte-identical, verified via `sha256sum -c SHA256SUMS`)
- [x] **P1.2** Create `rtl/core/PROVENANCE.md` and `rtl/core/SHA256SUMS` documenting source, SHA, date, and no-edit policy
- [x] **P1.3** Re-run `pipectrl` suite with `make clean` first — recorded 10/10 PASS
- [x] **P1.4** Run full 30-suite regression against `rtl/core/` via `tb/baseline/Makefile` — recorded **319/319 PASS** (`FAIL=0`, `SKIP=0`, `results/processed/baseline_regression_summary.csv`)
- [x] **P1.5** Create `results/raw/phase1_baseline_regression.md` with full results table
- [x] **P1.6** Create `scripts/setup.sh`, `scripts/check_results.py`, and `scripts/run_baseline_regression.sh`
- [x] **P1.7** Verify Lab 06 `.venv` is used for simulation
- [ ] **P1.8** Tag baseline commit: `git tag pipeguard-rv-baseline-0` (deferred until user commits/approves)

### Acceptance Criteria
- `rtl/core/` contains all 26 `.sv` files matching Lab 06 by SHA-256 ✅
- Full 30-suite snapshot regression verified: 319/319 PASS ✅
- `results/processed/baseline_regression_summary.csv` and `results/raw/phase1_baseline_regression.md` recorded with actual numbers ✅

### Dependencies
- Phase 0 ✅ complete

### Blockers
- None currently; `pipectrl` stale-sim is a known non-RTL issue resolvable with `make clean`

---

## Phase 2 — Unprotected Baseline Wrapper (B0) ✅ COMPLETE

**Goal:** Create an observation-enabled research core copy and common configurable top-level (`pipeguard_cpu`) with `MONITOR_CFG=0` (B0), proving lock-step equivalence with the unmodified snapshot and establishing the Yosys B0 baseline.

### Tasks
- [x] **P2.1** Define shared configuration & fault-class encodings (`rtl/common/pipeguard_defs.svh`)
- [x] **P2.2** Create `rtl/top/riscv_pipeline_cpu_obs.sv` — research copy exposing internal observation wires (`obs_*`) without altering logic
- [x] **P2.3** Create `rtl/top/pipeguard_cpu.sv` — common configurable top (`MONITOR_CFG=0` → B0)
- [x] **P2.4** Write cocotb lock-step equivalence harness (`tb/hdl/tb_lockstep.sv`, `tb/common/rv32i.py`, `tb/common/programs.py`, `tb/test_b0_equivalence.py`)
- [x] **P2.5** Run `make test CONFIG=b0` — **2/2 cocotb tests PASS** (15 directed + 10 random RV32I programs, cycle-for-cycle match)
- [x] **P2.6** Run Yosys synthesis on B0 (`make synth CONFIG=b0`) — **77,241 generic cells** (9,756 FFs, 67,485 combinational)
- [x] **P2.7** Document B0 synthesis and verification in `results/synthesis/b0_synth.md` and `results/raw/phase2_b0_verification.md`
- [x] **P2.8** Lint with Verilator (`make lint`) — exits 0 (with documented `UNUSEDSIGNAL` and `WIDTHEXPAND` suppressions)

### Acceptance Criteria
- Wrapper compiles and all 15 directed + 10 random programs pass lock-step equivalence ✅
- B0 synthesis report captured (Yosys generic cells only, not silicon area) ✅
- Zero test regressions from wrapper introduction ✅

### Dependencies
- Phase 1 complete

---

## Phase 3 — PC-Based Monitor (M0) ✅ COMPLETE

**Goal:** Implement the simplest monitor: validate PC 4-byte alignment and configurable instruction memory bounds without flagging valid non-sequential branches/jumps.

### Tasks
- [x] **P3.1** Specify M0 detection logic: alignment (`fetch_pc[1:0] != 2'b00`) + bounds (`PC_MIN <= fetch_pc <= PC_MAX`), reset-safe, deterministic priority
- [x] **P3.2** Create `rtl/monitors/pc_monitor.sv`
- [x] **P3.3** Wire `MONITOR_CFG = PG_CFG_M0` into `rtl/top/pipeguard_cpu.sv`
- [x] **P3.4** Write unit tests for `pc_monitor.sv` (`tb/test_pc_monitor.py`) — **5/5 PASS**
- [x] **P3.5** Write integration + synthetic PC fault-injection tests (`tb/test_m0_integration.py`) — **5/5 PASS**
- [x] **P3.6** Confirm 0 false positives across all 15 directed + 10 random RV32I programs in lock-step
- [x] **P3.7** Run Yosys synthesis for M0 (`make synth CONFIG=m0`) — **77,345 cells** (+104 cells / +0.135% vs. B0)
- [x] **P3.8** Document M0 alarm interface, verification (`results/raw/phase3_m0_verification.md`), and synthesis (`results/synthesis/m0_synth.md`)

### Acceptance Criteria
- M0 detects injected misaligned and out-of-bounds PC faults with 0-cycle combinational / 1-edge registered latency ✅
- False positive rate = 0 across all 25 lock-step workloads ✅
- Synthesis overhead documented relative to B0 (+104 generic cells, +3 FFs) ✅

### Dependencies
- Phase 2 complete

---

## Phase 4 — Branch-Aware Monitor (M1) and Pipeline-Aware Monitor (M2) ✅ COMPLETE

**Goal:** Implement M1 (branch-redirect & PC-transition awareness) and M2 (pipeline-control, hazard, stall/flush, and stage-progression awareness).

### Tasks — M1
- [x] **P4.1** Specify M1 detection logic: M0 rules + cycle-correct PC transition, redirect validity/target, conservative hold
- [x] **P4.2** Create `rtl/monitors/branch_monitor.sv`
- [x] **P4.3** Wire `MONITOR_CFG = PG_CFG_M1` into `rtl/top/pipeguard_cpu.sv`
- [x] **P4.4** Unit and integration tests for M1 (`tb/test_branch_monitor.py` 4/4, `tb/test_m1_integration.py` 5/5)
- [x] **P4.5** Confirm 0 false positives across all 25 lock-step workloads
- [x] **P4.6** Yosys synthesis for M1 — **77,803 cells** (+562 / +0.728% vs. B0)

### Tasks — M2
- [x] **P4.7** Specify M2 detection logic: independent hazard recomputation, redirect priority, stall/flush consistency, stage progression
- [x] **P4.8** Create `rtl/monitors/pipeline_monitor.sv`
- [x] **P4.9** Wire `MONITOR_CFG = PG_CFG_M2` into `rtl/top/pipeguard_cpu.sv`
- [x] **P4.10** Unit and integration tests for M2 (`tb/test_pipeline_monitor.py` 4/4, `tb/test_m2_integration.py` 5/5)
- [x] **P4.11** Confirm 0 false positives across all 25 lock-step workloads
- [x] **P4.12** Yosys synthesis for M2 — **78,380 cells** (+1,139 / +1.475% vs. B0)

### Acceptance Criteria
- Both M1 and M2 pass all unit, lock-step zero-FP, and fault-injection tests ✅
- Verilator lint and Yosys synthesis complete for all 4 configurations (`B0`, `M0`, `M1`, `M2`) ✅

### Dependencies
- Phase 3 complete (M0 as template for M1 / M2 extension)

---

## Phase 5 — Formal Verification (SymbiYosys) ⬜ TODO

**Goal:** Formally verify safety property: when no fault injected, `fault_detected` is never asserted (no false positives). Bounded Model Checking (BMC) only — not full induction.

### Tasks
- [ ] **P5.1** Write SVA assertions for each monitor: `assert property (!fault_detected)` under clean operation
- [ ] **P5.2** Create `.sby` configuration file for each monitor (B0 / M0 / M1 / M2)
- [ ] **P5.3** Run `make formal CONFIG=m0` — record BMC depth and result
- [ ] **P5.4** Run `make formal CONFIG=m1`
- [ ] **P5.5** Run `make formal CONFIG=m2`
- [ ] **P5.6** Document any counter-examples found and fixes made
- [ ] **P5.7** Commit final `.sby` and results to `formal/`

### Acceptance Criteria
- BMC passes for all three monitor configs to depth ≥ 20 cycles (or document why not)
- All counter-examples (if any) resolved or explicitly acknowledged as limitations

### Dependencies
- Phase 4 complete; SymbiYosys (from Yosys 0.33 install) confirmed available

---

## Phase 6 — Fault Injection Campaign ⬜ TODO

**Goal:** Synthetic RTL fault injection — single transient bit-flip on PC, branch-control, and pipeline-control signals — and measurement of detection coverage per monitor.

### Tasks
- [ ] **P6.1** Design fault injection framework (`tb/fault_inject/`) — cocotb signal force API
- [ ] **P6.2** Define fault catalog: target signals × workloads × timing → YAML config
- [ ] **P6.3** Implement smoke campaign (`make smoke CONFIG=m0`): 10 faults × 4 workloads
- [ ] **P6.4** Implement full campaign: systematic sweep per fault catalog
- [ ] **P6.5** Run full campaign for B0 (control — expect 0% detection)
- [ ] **P6.6** Run full campaign for M0
- [ ] **P6.7** Run full campaign for M1
- [ ] **P6.8** Run full campaign for M2
- [ ] **P6.9** Collect raw results to `results/raw/fault_campaign_*.csv`
- [ ] **P6.10** Compute detection coverage, false positive rate, detection latency per config

### Acceptance Criteria
- Raw CSV results committed (not fabricated)
- Coverage numbers reproducible by running `make reproduce`
- B0 detection = 0% (confirms fault injection is functioning)

### Dependencies
- Phase 4 complete; Phase 5 formal results inform which faults are structurally undetectable

---

## Phase 7 — Synthesis & Area/Timing Analysis ⬜ TODO

**Goal:** Yosys synthesis for all four configs — record cell count and estimated area overhead per monitor.

### Tasks
- [ ] **P7.1** Write synthesis script for each config in `synthesis/`
- [ ] **P7.2** Run `make synth CONFIG=b0` — record cell count baseline
- [ ] **P7.3** Run `make synth CONFIG=m0` — record overhead
- [ ] **P7.4** Run `make synth CONFIG=m1` — record overhead
- [ ] **P7.5** Run `make synth CONFIG=m2` — record overhead
- [ ] **P7.6** Parse Yosys JSON output with `scripts/parse_synth.py` → `results/synthesis/`
- [ ] **P7.7** Generate area overhead table

### Acceptance Criteria
- Synthesis uses Yosys generic cells only (not silicon — this is a known limitation, see `docs/limitations.md`)
- All four configs synthesise without errors
- Overhead reported as percentage increase relative to B0

### Dependencies
- Phase 2 complete (B0 baseline synthesis establishes reference)
- Monitor RTL complete (Phases 3–4)

---

## Phase 8 — Analysis, Visualisation & Paper Draft ⬜ TODO

**Goal:** Analyse fault campaign results, generate figures, and write the research paper.

### Tasks
- [ ] **P8.1** Run `scripts/analyze_results.py` — generate summary statistics
- [ ] **P8.2** Generate figures: detection coverage bar chart, latency CDF, overhead scatter
- [ ] **P8.3** Write paper draft in `paper/` following `paper/outline.md`
- [ ] **P8.4** Fill in Results section with actual numbers from Phases 6–7
- [ ] **P8.5** Write Discussion and Limitations sections — honest about Yosys-only, simulation-only
- [ ] **P8.6** Internal review: check all claims against raw data

### Acceptance Criteria
- Every number in the paper traceable to a raw data file in `results/`
- No fabricated metrics; limitations explicitly stated

### Dependencies
- Phases 6 and 7 complete

---

## Phase 9 — Reproducibility Package ⬜ TODO

**Goal:** Ensure any reader can re-run the full experiment from scratch with one command.

### Tasks
- [ ] **P9.1** Write `scripts/reproduce_all.sh` — end-to-end script from clone to results
- [ ] **P9.2** Test on clean WSL environment (fresh clone, no `.venv`)
- [ ] **P9.3** Document exact Docker or Conda alternative setup (optional)
- [ ] **P9.4** Pin all tool versions in `docs/experimental_methodology.md`
- [ ] **P9.5** Final `make reproduce` smoke test passes from clean checkout
- [ ] **P9.6** Archive results ZIP for paper submission

### Acceptance Criteria
- `bash scripts/reproduce_all.sh` completes without manual intervention on a clean WSL install
- Reproduced numbers match committed `results/` files within floating-point tolerance

### Dependencies
- All previous phases complete

---

## Summary Table

| Phase | Name | Status | Key Deliverable |
|-------|------|--------|-----------------|
| 0 | Repository Audit | ✅ COMPLETE | Signal map, baseline regression, tool inventory |
| 1 | Baseline CPU Snapshot | ✅ COMPLETE | 26-file `rtl/core/` copy (`SHA256SUMS`), 30 suites / 319 tests PASS |
| 2 | B0 Wrapper | ✅ COMPLETE | `riscv_pipeline_cpu_obs.sv`, `pipeguard_cpu.sv`, B0 lock-step + Yosys (77,241 cells) |
| 3 | M0 PC Monitor | ✅ COMPLETE | `pc_monitor.sv`, 5/5 unit + 5/5 integration PASS, +104 cells vs. B0 |
| 4 | M1 / M2 Monitors | ✅ COMPLETE | `branch_monitor.sv`, `pipeline_monitor.sv`, all tests + synth PASS |
| 5 | Formal Verification | ⬜ TODO | `.sby` files, BMC results |
| 6 | Fault Campaign | ⬜ TODO | `results/raw/fault_campaign_*.csv`, coverage metrics |
| 7 | Synthesis Analysis | ⬜ TODO | `results/synthesis/`, overhead table |
| 8 | Paper Draft | ⬜ TODO | `paper/draft_v1.md` with real numbers |
| 9 | Reproducibility | ⬜ TODO | `scripts/reproduce_all.sh`, archived results |
