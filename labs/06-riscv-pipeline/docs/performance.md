# 📊 Pipeline Performance Report

[← Project README](../README.md) · [Architecture](architecture.md) · [Verification](verification.md)

## Goal and methodology

Six short, controlled cocotb benchmarks evaluate the timing effects of forwarding, load-use interlocks, and branch redirects in the five-stage pipeline. Each benchmark stops when **eight intended instructions** have retired, using a simulation-only pipeline-valid monitor.

The reported CPI is:

\[
\mathrm{CPI} = \frac{\mathrm{Measured\ clock\ cycles}}{\mathrm{Retired\ instructions}}
\]

For an eight-instruction sequence in an ideal five-stage pipeline with no stalls, the expected completion time is **8 + 4 = 12 cycles**. The four additional cycles represent pipeline fill/drain overhead under the benchmark's counting convention.

## Measured results

| Workload | Cycles | Retired | Load stalls | Redirects | CPI |
|---|---:|---:|---:|---:|---:|
| Independent arithmetic | **12** | 8 | 0 | 0 | **1.500** |
| Arithmetic forwarding | **12** | 8 | 0 | 0 | **1.500** |
| Load-use dependency | **13** | 8 | 1 | 0 | **1.625** |
| Branch not taken | **12** | 8 | 0 | 0 | **1.500** |
| Branch taken | **14** | 8 | 0 | 1 | **1.750** |
| JAL | **14** | 8 | 0 | 1 | **1.750** |

All six tests passed in the observed run.

## Interpreting the results

### Independent arithmetic: CPI 1.500

Eight independent instructions complete in 12 cycles. This is the reference for the short workloads, **not** a claim that long-running programs have CPI 1.5.

### Forwarding: CPI 1.500

The dependent arithmetic chain also completes in 12 cycles. This indicates that forwarding removes additional stalls for the tested dependencies.

### Load-use: CPI 1.625

A load followed by a dependent instruction inserts one bubble. The result is **13 cycles**, or **one cycle above** the baseline. For this short workload, CPI increases by about **8.33%** relative to 1.500.

### Not-taken branch: CPI 1.500

The not-taken branch continues sequential execution without a redirect, completing in 12 cycles.

### Taken branch and JAL: CPI 1.750

A taken redirect flushes younger instructions. Each tested redirect costs **two additional cycles**, producing 14 cycles for eight retired instructions. The tests also verify that a wrong-path register write does not occur.

## Reproduce the measurements

```bash
make clean
make TEST=cpuperf | tee /tmp/riscv_perf.log
```

Extract the benchmark lines:

```bash
grep -E 'Independent arithmetic:|Forwarding benchmark:|Load-use benchmark:|Branch not taken:|Branch taken:|JAL performance:' /tmp/riscv_perf.log
```

## Measurement boundaries

- These are **simulation cycle counts**, not elapsed real-world execution times or FPGA frequency measurements.
- Each program contains only eight intended retired instructions. Startup/drain overhead has a large effect on CPI.
- The simulation-only valid-bit monitor is suitable for these controlled cases, but a general-purpose retirement interface would be preferable for arbitrary programs, traps, and unusual pipeline stalls.
- No clock frequency, power, area, or application-level throughput was measured.
- Branch penalty values describe this specific EX-stage resolution design and these test sequences.

## Suggested next experiments

1. Run longer programs to reduce the relative startup/drain overhead.
2. Compare independent, dependent, and memory-heavy instruction mixes.
3. Add a committed-instruction trace and compare against a reference ISA model.
4. Measure branch-heavy loops with different taken/not-taken patterns.
5. Synthesize to a target FPGA before making hardware performance claims.
