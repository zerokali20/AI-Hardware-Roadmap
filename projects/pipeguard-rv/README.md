# PipeGuard-RV

**Lightweight Hardware Runtime Monitors for Control-Flow and Pipeline Integrity in Pipelined RISC-V Processors**

PipeGuard-RV is a hardware security and fault-tolerance research framework built around a pipelined RISC-V core. It introduces non-intrusive, cycle-accurate runtime monitors that observe internal processor signals—such as Program Counter (PC) transitions, branch resolutions, and pipeline stall/flush states—to detect transient faults, fault-injection attacks, and control-flow anomalies in real time with minimal area and timing overhead.

---

## Key Features

- **Modular Runtime Monitoring:** Independent hardware monitors (`pc_monitor`, `branch_monitor`, `pipeline_monitor`) that can be evaluated individually or in combined configurations (`M0`, `M1`, `M2`).
- **Non-Intrusive Signal Tapping:** Uses a dedicated `monitor_adapter` to observe pipeline registers without modifying the core datapath logic.
- **Automated Fault-Injection Campaigns:** Configurable YAML-driven simulation sweeps (`smoke` and `full`) injecting bit-flips and transient faults across diverse RISC-V workloads.
- **Formal & Simulation Verification:** Combines Cocotb Python testbenches against a golden reference model with SymbiYosys (`sby`) SystemVerilog Assertions (SVA) to prove zero false positives during valid execution.
- **PPA Overhead Evaluation:** Automated Yosys synthesis flows comparing gate count and area overhead against the unmodified baseline CPU.

---

## Repository Structure

```text
projects/pipeguard-rv/
│
├── README.md                       # Project overview, setup instructions, and usage guide
├── IMPLEMENTATION_PLAN.md          # Development roadmap, milestones, and architectural tasks
├── CHANGELOG.md                    # Version history and notable updates across iterations
├── AGENTS.md                       # Guidelines and context for AI coding agents working in this repo
├── Makefile                        # Build, simulation, formal verification, and synthesis targets
├── requirements.txt                # Python dependencies (cocotb, PyYAML, analysis libraries)
├── .gitignore                      # Git ignore rules for build artifacts, waveforms, and logs
│
├── rtl/                            # Synthesizable SystemVerilog hardware design files
│   ├── core/                       # Base pipelined RISC-V processor RTL (reused from Lab 06)
│   │
│   ├── monitors/                   # Hardware security and anomaly detection monitor modules
│   │   ├── pc_monitor.sv           # Monitors Program Counter (PC) flow and control-flow integrity
│   │   ├── branch_monitor.sv       # Tracks branch/jump targets and misprediction behavior
│   │   └── pipeline_monitor.sv     # Observes pipeline control signals, stalls, and flushes
│   │
│   ├── common/                     # Shared RTL glue logic and alert aggregation
│   │   ├── monitor_adapter.sv      # Taps and formats internal CPU signals for the monitors
│   │   └── alarm_logic.sv          # Aggregates monitor flags into unified fault/anomaly alerts
│   │
│   └── top/                        # Top-level integration wrappers
│       └── pipeguard_cpu.sv        # Top-level module integrating the RISC-V core with PipeGuard monitors
│
├── tb/                             # Cocotb/Python verification testbenches and golden models
│   ├── test_baseline.py            # Functional verification of the unmodified baseline CPU
│   ├── test_pc_monitor.py          # Unit tests for the PC monitor module
│   ├── test_branch_monitor.py      # Unit tests for the branch monitor module
│   ├── test_pipeline_monitor.py    # Unit tests for the pipeline monitor module
│   ├── test_cpu_integration.py     # End-to-end integration tests for the monitored CPU
│   ├── test_fault_campaign.py      # Automated fault-injection test suite
│   └── reference_model.py          # Python golden reference model for expected architectural state
│
├── simulation/                     # Simulation infrastructure and fault-injection utilities
│   ├── fault_harness.sv            # SystemVerilog wrapper for injecting bit-flips and transient faults
│   └── trace_collector.py          # Captures cycle-accurate execution and monitor signal traces
│
├── workloads/                      # RISC-V assembly/C benchmark programs for evaluation
│   ├── linear/                     # Sequential instruction execution without branches
│   ├── conditional_branch/         # Branch-heavy control flow patterns
│   ├── loop/                       # Iterative loop structures and backward branches
│   ├── jal_jalr/                   # Direct and indirect jump/function call workloads
│   ├── load_use_hazard/            # Data hazard sequences triggering pipeline stalls
│   ├── pipeline_flush/             # Control hazard sequences triggering pipeline flushes
│   ├── mixed/                      # Combined general-purpose instruction mixes
│   └── iot_controller/             # Realistic embedded IoT firmware workload
│
├── experiments/                    # Automated fault-injection campaigns and data analysis
│   ├── configs/                    # YAML configuration files defining campaign parameters
│   │   ├── smoke.yaml              # Fast, lightweight configuration for sanity-checking campaigns
│   │   └── full.yaml               # Comprehensive fault-injection sweep configuration
│   ├── run_campaign.py             # Orchestrates batch simulations across workloads and fault models
│   ├── metrics.py                  # Computes detection latency, coverage, and false-positive rates
│   └── analyze_results.py          # Aggregates raw logs and generates summary tables/plots
│
├── formal/                         # Formal verification using SymbiYosys (sby)
│   ├── monitor_properties.sv       # SystemVerilog Assertions (SVA) proving monitor invariants
│   └── monitor.sby                 # SymbiYosys formal verification configuration file
│
├── synthesis/                      # Yosys logic synthesis scripts for area/timing overhead evaluation
│   ├── synth_baseline.ys           # Synthesis script for the unmonitored baseline CPU
│   ├── synth_m0.ys                 # Synthesis script for Monitor Configuration M0
│   ├── synth_m1.ys                 # Synthesis script for Monitor Configuration M1
│   └── synth_m2.ys                 # Synthesis script for Monitor Configuration M2
│
├── scripts/                        # Helper shell scripts for environment setup and automation
│   ├── setup.sh                    # Installs toolchains, Python packages, and configures environment
│   ├── run_tests.sh                # Executes the full verification testbench suite
│   └── reproduce_results.sh        # End-to-end script to reproduce paper experiments and figures
│
├── results/                        # Generated experimental outputs (typically git-ignored)
│   ├── raw/                        # Unprocessed simulation logs and fault-injection dumps
│   ├── processed/                  # Cleaned CSV/JSON datasets and computed metric summaries
│   ├── synthesis/                  # Gate-level netlists, cell counts, and area/timing reports
│   └── figures/                    # Publication-ready plots and charts
│
├── docs/                           # Detailed technical and methodological documentation
│   ├── research_scope.md           # Problem statement, objectives, and research questions
│   ├── threat_model.md             # Targeted fault models, attacker capabilities, and assumptions
│   ├── architecture.md             # Microarchitectural design of the PipeGuard monitors
│   ├── signal_map.md             # Mapping of internal CPU pipeline signals to monitor inputs
│   ├── verification_plan.md        # Simulation and formal verification strategy
│   ├── experimental_methodology.md # Fault campaign setup, metrics, and evaluation protocol
│   ├── related_work.md              # Literature review and comparison with existing approaches
│   └── limitations.md              # Known constraints, edge cases, and future work
│
└── paper/                          # Research manuscript source files
    ├── outline.md                  # Section-by-section paper structure and key arguments
    ├── references.bib              # BibTeX bibliography database
    └── manuscript.tex              # LaTeX source for the research paper