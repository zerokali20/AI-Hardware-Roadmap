# Comparative Synthesis Report (Phase 7) — PipeGuard-RV

| Field | Value |
|---|---|
| **Date** | 2026-11-27 |
| **Tool** | Yosys 0.33 (git sha1 `2584903a060`) |
| **Synthesis Flow** | `synth -top pipeguard_cpu -noabc` (`synthesis/synth.tcl`) |
| **Parsed Outputs** | `results/synthesis/synth_summary.csv`, `results/synthesis/synth_summary.json` |

## 1. Whole-Design Generic Cell Overhead (vs. B0)

| Config | Total Cells | Delta | Overhead (%) | Flip-Flops | Comb. Cells |
|---|---:|---:|---:|---:|---:|
| **B0** (`MONITOR_CFG=0`) | 77,241 | — | — | 9,756 | 67,485 |
| **M0** (`MONITOR_CFG=1`) | 77,345 | +104 | +0.13% | 9,759 (+3) | 67,586 (+101) |
| **M1** (`MONITOR_CFG=2`) | 77,803 | +562 | +0.73% | 9,826 (+70) | 67,977 (+492) |
| **M2** (`MONITOR_CFG=3`) | 78,380 | +1,139 | +1.47% | 9,926 (+170) | 68,454 (+969) |

## 2. Monitor-Only Module Resources & Logic-Only Overhead (Excluding Memories)

Because `instruction_memory` and `data_memory` (`MEM_SIZE=1024` bytes → 8,192 `$_DFFE_PP_` FFs) synthesize into flip-flop/mux arrays totaling ~69.6k cells in `B0`, we also report overhead relative to the **non-memory logic core** (`7,659` cells in `B0`):

| Config | Monitor Module | Mon. Total | Mon. FFs | Mon. Comb. | Logic-Only Cells (excl. mem) | Logic-Only Overhead (%) |
|---|---|---:|---:|---:|---:|---:|
| **B0** | None | 0 | 0 | 0 | 7,659 | — |
| **M0** | `pc_monitor` | 104 | 3 | 101 | 7,763 | **+1.36%** |
| **M1** | `branch_monitor` | 557 | 70 | 487 | 8,216 | **+7.27%** |
| **M2** | `pipeline_monitor` | 1,139 | 170 | 969 | 8,798 | **+14.87%** |

## 3. Limitations

- Generic cell counts (`$_AND_`, `$_MUX_`, `$_DFFE_PP_`, etc.) from `synth -noabc` are technology-independent logic complexity metrics, **not** physical silicon area ($\mu\text{m}^2$), FPGA LUT/FF utilization, power, or maximum operating frequency ($f_{\max}$).
