# M0 Synthesis Report & Overhead vs. B0 — PipeGuard-RV

| Field | Value |
|---|---|
| **Configuration** | `M0` (`pipeguard_cpu #(.MONITOR_CFG(1))`) |
| **Date** | 2026-11-25 |
| **Tool** | Yosys 0.33 (git sha1 `2584903a060`) |
| **Command** | `MONITOR_CFG=1 CFG_NAME=m0 OUT_DIR=results/synthesis yosys -Q -l results/synthesis/m0_synth.log -c synthesis/synth.tcl` |
| **Synthesis flow** | `synth -top pipeguard_cpu -noabc` |
| **Raw stat output** | `results/synthesis/m0_stat.txt` |

## Comparison: M0 vs. B0 (Yosys Generic Cells)

| Metric | B0 (`MONITOR_CFG=0`) | M0 (`MONITOR_CFG=1`) | Delta (M0 − B0) | Overhead (%) |
|---|---:|---:|---:|---:|
| **Total generic cells** | **77,241** | **77,345** | **+104** | **+0.135%** |
| **Flip-flops (sequential)** | **9,756** | **9,759** | **+3** | **+0.031%** |
| — `$_DFFE_PP_` | 8,192 | 8,192 | 0 | — |
| — `$_SDFFCE_PN0P_` | 1,024 | 1,024 | 0 | — |
| — `$_SDFFE_PP0N_` | 505 | 505 | 0 | — |
| — `$_SDFFE_PP0P_` | 32 | 35 | +3 | — |
| — `$_SDFFE_PP1N_` | 3 | 3 | 0 | — |
| **Combinational cells** | **67,485** | **67,586** | **+101** | **+0.150%** |
| — `$_MUX_` | 52,155 | 52,156 | +1 | — |
| — `$_AND_` | 10,144 | 10,195 | +51 | — |
| — `$_OR_` | 4,301 | 4,313 | +12 | — |
| — `$_XOR_` | 489 | 489 | 0 | — |
| — `$_NOT_` | 396 | 433 | +37 | — |
| **Wires / wire bits** | 19,795 / 82,620 | 19,841 / 82,817 | +46 / +197 | — |

## Notes & Limitations

- The +3 flip-flops in `M0` correspond to `fault_sticky` (1 bit) and the 2 active bits of `fault_class` (`PG_FC_PC_MISALIGNED=1`, `PG_FC_PC_OUT_OF_BOUNDS=2`; bits `[3:2]` are constant `0` in M0 and optimized away).
- Generic cell counts are technology-independent Yosys internal primitives (`synth -noabc`), not physical silicon area, LUT count, operating frequency, or power.
