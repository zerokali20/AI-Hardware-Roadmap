# 🧪 Verification and Regression

[← Project README](../README.md) · [Architecture](architecture.md) · [Performance](performance.md)

## Verification approach

The project uses **cocotb 2.x**, Python testbenches, and **Icarus Verilog** to test RTL from small components to complete CPU execution.

| Level | Examples of verified behavior |
|---|---|
| Component | PC, register file, decoder, immediate generator, ALU, branch unit, memories |
| Pipeline registers | IF/ID, ID/EX, EX/MEM, MEM/WB reset/hold/flush and data propagation |
| Integration | Execute, memory, writeback, forwarding, hazard coordination |
| Full CPU | Program execution, arithmetic, hazards, memory access, branch/jump behavior |
| Performance | Independent, forwarding, load-use, not-taken, taken, and JAL workloads |

## Final regression summary

| Metric | Observed result |
|---|---:|
| Passing suites | **30** |
| Failing suites | **0** |
| Previously tallied passing tests | **329** |
| Performance tests | **6 / 6 passing** |

The 329 count comes from the previously verified per-suite test totals. The regression script's printed summary reports **suite-level** success rather than independently summing each suite's test count.

## Reproduce the regression

```bash
source .venv/bin/activate
chmod +x scripts/run_regression.sh
./scripts/run_regression.sh
```

The script runs these targets:

```text
pc if ifid decode imm regfile ifidstage
alu aluctrl idex execute branch exbranch
pipectrl pipeint exmem dmem memstage
memwb wb wbint forward hazard hazint
exforward cpu cpuhaz cpuisa cpumembranch cpuperf
```

Each suite is run after `make clean`, with output written to `logs/<suite>.log`. The `logs/` directory is intentionally Git-ignored.

### Useful individual commands

```bash
make clean && make TEST=alu
make clean && make TEST=exforward
make clean && make TEST=cpu
make clean && make TEST=cpuhaz
make clean && make TEST=cpuisa
make clean && make TEST=cpumembranch
make clean && make TEST=cpuperf
```

## Important verification checks

- Forwarded values reach dependent ALU operations without unnecessary stalls.
- Load-use dependencies insert a bubble and preserve the expected register results.
- Taken branches and jumps redirect the PC and prevent wrong-path register updates.
- Byte and halfword loads apply the appropriate sign or zero extension.
- Memory alignment and out-of-bounds conditions are detected in tested scenarios.
- LUI and AUIPC produce the intended results in tested instruction sequences.

## Troubleshooting

### Cocotb cannot find the top-level module

Example: `Couldn't find root handle execute_forwarding_stage` after running a CPU test. This typically means an old `sim_build/sim.vvp` was reused. Run:

```bash
make clean && make TEST=exforward
```

### Icarus warnings

Icarus may print warnings about constant selects in `always_*` blocks. Evaluate whether compilation and test assertions succeed rather than treating every warning as a test failure.

### Instruction ROM warning

A `$readmemh` warning about a file containing fewer entries than the full ROM capacity can occur when the test program is shorter than memory. The testbench still needs to verify that unused entries have safe values.

## Remaining verification work

This regression is strong evidence for the **tested functionality**, but does not prove complete RV32I compliance, formal correctness, precise exception behavior, or silicon timing. Further work could include a reference-model scoreboard, randomized program generation, instruction retirement tracing, and hardware synthesis.
