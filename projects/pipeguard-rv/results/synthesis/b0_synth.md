# B0 Baseline Synthesis Report — PipeGuard-RV

| Field | Value |
|---|---|
| **Configuration** | `B0` (`pipeguard_cpu #(.MONITOR_CFG(0))`) |
| **Date** | 2026-11-24 |
| **Tool** | Yosys 0.33 (git sha1 `2584903a060`) |
| **Command** | `MONITOR_CFG=0 CFG_NAME=b0 OUT_DIR=results/synthesis yosys -Q -l results/synthesis/b0_synth.log -c synthesis/synth.tcl` |
| **Synthesis flow** | `synth -top pipeguard_cpu -noabc` (matches Lab 07 `synth_cpu.sh`) |
| **Raw stat output** | `results/synthesis/b0_stat.txt` |

## Top-Level Generic Cell Summary (`pipeguard_cpu`, `MONITOR_CFG=0`)

| Metric | Count |
|---|---:|
| **Total generic cells** | **77,241** |
| **Flip-flops (sequential)** | **9,756** |
| — `$_DFFE_PP_` | 8,192 |
| — `$_SDFFCE_PN0P_` | 1,024 |
| — `$_SDFFE_PP0N_` | 505 |
| — `$_SDFFE_PP0P_` | 32 |
| — `$_SDFFE_PP1N_` | 3 |
| **Combinational cells** | **67,485** |
| — `$_MUX_` | 52,155 |
| — `$_AND_` | 10,144 |
| — `$_OR_` | 4,301 |
| — `$_XOR_` | 489 |
| — `$_NOT_` | 396 |
| **Wires / wire bits** | 19,795 / 82,620 |

## Methodology & Limitations

- **Generic cells only:** Yosys `synth -noabc` maps to technology-independent Yosys internal cells (`$_AND_`, `$_MUX_`, `$_DFFE_PP_`, etc.). These counts are **not** physical silicon area, LUT count, operating frequency, or power.
- **Included memories:** Both `instruction_memory` (256 × 32-bit ROM initialized from `programs/test_program.hex`) and `data_memory` (`MEM_SIZE=1024` bytes → 8,192 `$_DFFE_PP_` flip-flops) and `register_file` (32 × 32-bit → 1,024 `$_SDFFCE_PN0P_` flip-flops) are synthesized as flip-flop arrays/mux trees, accounting for the bulk of the 77,241 cells.
- **B0 monitor logic:** Zero monitor cells; `fault_detected`, `fault_sticky`, and `fault_class` are tied constant `0` in `g_b0`. Unused `obs_*` wires in `pipeguard_cpu` are removed by `opt_clean`.
