# M1 & M2 Synthesis Comparison Report — PipeGuard-RV

| Field | Value |
|---|---|
| **Date** | 2026-11-25 |
| **Tool** | Yosys 0.33 (git sha1 `2584903a060`) |
| **Synthesis flow** | `synth -top pipeguard_cpu -noabc` |
| **Raw stat outputs** | `results/synthesis/{b0,m0,m1,m2}_stat.txt` |

## Comparative Generic Cell Overhead (B0, M0, M1, M2)

| Configuration | Total Cells | Delta vs. B0 | Overhead (%) | Flip-Flops | Comb. Cells |
|---|---:|---:|---:|---:|---:|
| **B0** (`MONITOR_CFG=0`, unprotected) | 77,241 | — | — | 9,756 | 67,485 |
| **M0** (`MONITOR_CFG=1`, `pc_monitor`) | 77,345 | +104 | +0.135% | 9,759 (+3) | 67,586 (+101) |
| **M1** (`MONITOR_CFG=2`, `branch_monitor`) | 77,803 | +562 | +0.728% | 9,826 (+70) | 67,977 (+492) |
| **M2** (`MONITOR_CFG=3`, `pipeline_monitor`) | 78,380 | +1,139 | +1.475% | 9,926 (+170) | 68,454 (+969) |

## Notes & Limitations

- Generic cell counts are technology-independent Yosys internal primitives (`synth -noabc`), not physical silicon area, LUT count, operating frequency, or power.
- All configurations include identical `instruction_memory` (256 × 32-bit ROM) and `data_memory` (`MEM_SIZE=1024` bytes → 8,192 `$_DFFE_PP_` FFs), so relative percentage overhead reflects the monitor cost against the unmapped flip-flop memory arrays as well as the pipeline datapath.
