# 🚀 AI Hardware Roadmap

> **A practical, open-source learning path from RTL design and verification to FPGA AI accelerators, RISC-V architecture, hardware compilers, and neuromorphic computing.**

---

## 📌 About

**AI Hardware Roadmap** is an open-source learning project for students, developers, and hardware enthusiasts who want to explore the intersection of **computer architecture, digital hardware, machine learning, and AI acceleration**.

The goal is to build a practical path connecting:

```text
Algorithms
    ↓
Machine Learning
    ↓
Quantization
    ↓
Hardware-Aware ML
    ↓
RTL Design
    ↓
Verification
    ↓
FPGA Acceleration
    ↓
Accelerator Architecture
    ↓
Hardware Compilers
    ↓
Neuromorphic Computing
```

Rather than studying these areas separately, this repository focuses on **learning by building, testing, benchmarking, and contributing to real open-source projects**.

---

## 🎯 Project Goals

- Learn professional RTL verification workflows
- Explore open-source FPGA and EDA tools
- Understand RISC-V processor architectures
- Learn formal hardware verification
- Explore quantized neural networks
- Build FPGA-based AI accelerators
- Study modern AI accelerator architectures
- Understand MLIR and hardware compiler infrastructure
- Explore neuromorphic and event-driven computing
- Contribute to established open-source projects
- Build reproducible AI hardware experiments
- Create a structured learning path for future students

---

## 🗺️ Learning Roadmap

```text
Digital Logic & Computer Architecture
                 │
                 ▼
           RTL Design
              VHDL
                 │
                 ▼
        RTL Verification
         cocotb + GHDL
                 │
                 ▼
      Synthesis & Simulation
       Yosys + Verilator
                 │
                 ▼
       RISC-V Architecture
              Ibex
                 │
                 ▼
       Formal Verification
          SymbiYosys
                 │
                 ▼
    Quantized Machine Learning
       PyTorch + Brevitas
                 │
                 ▼
          FPGA AI
        hls4ml + FINN
                 │
                 ▼
    Accelerator Architecture
 Gemmini + gem5 + Timeloop
                 │
                 ▼
       Hardware Compilers
         MLIR + CIRCT
                 │
                 ▼
    Neuromorphic Computing
 snnTorch + NIR + NeuroBench
                 │
                 ▼
    AI Accelerator Capstone
```

---

## 🧭 Roadmap Stages

| Stage | Topic | Main Technologies | Goal |
|:---:|---|---|---|
| 01 | RTL Verification | VHDL, Python, cocotb, GHDL | Automated hardware verification |
| 02 | Synthesis | Yosys, Verilator | Understand RTL synthesis and simulation |
| 03 | Processor Systems | RISC-V, Ibex | Work with production-quality processor designs |
| 04 | Formal Verification | SymbiYosys | Verify hardware properties |
| 05 | Quantized ML | PyTorch, Brevitas | Understand low-precision neural networks |
| 06 | FPGA AI | hls4ml, FINN | Convert ML models into hardware |
| 07 | Accelerator Architecture | Gemmini, gem5, SCALE-Sim, Timeloop | Study accelerator performance |
| 08 | Hardware Compilers | LLVM, MLIR, CIRCT | Understand software-to-hardware lowering |
| 09 | Neuromorphic Computing | snnTorch, NIR, NeuroBench | Explore event-driven computation |
| 10 | Capstone | Integrated Toolchain | Build an end-to-end AI hardware system |

---

## 📂 Repository Structure

```text
AI-Hardware-Roadmap/
│
├── README.md
├── CONTRIBUTING.md
├── LICENSE
│
├── roadmap/
│   ├── 00-getting-started.md
│   ├── 01-rtl-verification.md
│   ├── 02-riscv-and-formal.md
│   ├── 03-quantization.md
│   ├── 04-fpga-ai.md
│   ├── 05-accelerator-architecture.md
│   ├── 06-hardware-compilers.md
│   └── 07-neuromorphic.md
│
├── labs/
│   ├── 01-cocotb-basics/
│   ├── 02-vhdl-alu-verification/
│   ├── 03-register-file-verification/
│   ├── 04-riscv-verification/
│   ├── 05-formal-verification/
│   ├── 06-quantized-ml/
│   └── 07-fpga-ai/
│
├── projects/
│   ├── verified-riscv/
│   ├── quantized-accelerator/
│   ├── accelerator-benchmark/
│   └── neuromorphic-benchmark/
│
├── open-source/
│   ├── contribution-guide.md
│   ├── good-first-issues.md
│   └── contribution-log.md
│
├── resources/
│   ├── books.md
│   ├── courses.md
│   ├── papers.md
│   └── tools.md
│
└── docs/
    ├── setup/
    ├── concepts/
    └── troubleshooting/
```

---

## 🧪 Labs

Every lab aims to turn a concept into something that can be **built, tested, and measured**.

Each lab will contain:

- 📖 Short theoretical introduction
- ⚙️ Environment setup
- 💻 Source code
- 🧪 Automated tests
- 📝 Exercises
- 📊 Expected results
- 🛠️ Troubleshooting
- 📚 Further reading
- 🏆 Optional challenge

### Hardware Requirements

| Symbol | Requirement |
|:---:|---|
| 🟢 | No hardware required |
| 🟡 | Hardware optional |
| 🔴 | Physical hardware required |

The early stages are designed to work entirely through **simulation and open-source software**.

---

## 🚧 Current Progress

### Phase 01: RTL Verification

**Status:** `In Progress`

- [ ] Set up WSL/Linux development environment
- [ ] Install GHDL
- [ ] Install cocotb
- [ ] Install Yosys
- [ ] Install Verilator
- [ ] Run first cocotb simulation
- [ ] Verify a VHDL ALU
- [ ] Add randomized ALU testing
- [ ] Verify a register file
- [ ] Add GitHub Actions CI
- [ ] Reproduce an upstream issue
- [ ] Submit first open-source pull request

---

## 🔬 First Learning Track

The first stage moves from traditional waveform-based testing toward automated RTL verification.

```text
VHDL Module
     │
     ▼
GHDL Simulation
     │
     ▼
cocotb Testbench
     │
     ▼
Python Reference Model
     │
     ▼
Randomized Testing
     │
     ▼
Automatic PASS / FAIL
     │
     ▼
Regression Testing
     │
     ▼
GitHub Actions CI
```

### First Milestone

```text
VHDL ALU + GHDL + cocotb
             ↓
Automated & Reproducible Verification
```

---

## 🏗️ Major Projects

### 1️⃣ Verified RISC-V / Processor Subsystem

Build and verify a processor subsystem using:

- `cocotb`
- `GHDL`
- `Verilator`
- `Yosys`
- `SymbiYosys`
- `RISC-V`

**Goal:** Demonstrate RTL design, automated verification, synthesis, and formal verification.

---

### 2️⃣ Quantized Neural Network Accelerator

Build a small neural network and move it toward hardware acceleration.

```text
PyTorch
   ↓
Brevitas
   ↓
Quantized Model
   ↓
hls4ml / FINN
   ↓
Hardware Representation
   ↓
Simulation / FPGA
```

Measurements will include:

- Accuracy
- Model size
- Precision
- Latency
- Throughput
- FPGA resource usage

---

### 3️⃣ AI Accelerator Architecture Study

Study how different architectural decisions affect AI workloads.

Tools may include:

- Gemmini
- gem5
- SCALE-Sim
- Timeloop
- Accelergy

Experiments will investigate:

- Systolic array dimensions
- Dataflow
- Memory hierarchy
- Cache configuration
- Numerical precision
- Latency
- Throughput
- Energy estimates

---

### 4️⃣ Neuromorphic Computing Benchmark

Explore spiking neural networks and event-driven computing.

```text
snnTorch
   ↓
Spiking Neural Network
   ↓
NIR
   ↓
NeuroBench
   ↓
Benchmark & Analysis
```

The goal is to compare conventional neural networks and neuromorphic approaches using measurable results.

---

## 🌍 Open-Source Contribution Journey

Learning how to work inside existing engineering projects is a major part of this roadmap.

```text
Build Project From Source
          ↓
Find an Issue
          ↓
Reproduce the Problem
          ↓
Create Minimal Reproducer
          ↓
Write Failing Test
          ↓
Find Root Cause
          ↓
Implement Fix
          ↓
Run Regression Tests
          ↓
Submit Pull Request
          ↓
Respond to Review
          ↓
Merged Contribution
```

### Target Open-Source Ecosystems

| Area | Projects |
|---|---|
| Verification | cocotb, GHDL, Verilator |
| Synthesis / EDA | Yosys, SymbiYosys |
| RISC-V | Ibex |
| FPGA AI | hls4ml, FINN |
| Quantization | Brevitas |
| Accelerators | Gemmini |
| Architecture | gem5 |
| Hardware Compilers | CIRCT, MLIR |
| Embedded AI | ExecuTorch |
| Neuromorphic | snnTorch, NIR, NeuroBench |

---

## 👨‍💻 Who Is This For?

This project may be useful for:

- Computer Engineering students
- Electrical and Electronic Engineering students
- Computer Science students interested in hardware
- FPGA beginners
- RISC-V enthusiasts
- Embedded systems developers
- AI accelerator enthusiasts
- Hardware-aware ML researchers
- ML compiler beginners
- Neuromorphic computing beginners
- Anyone interested in efficient computing systems

---

## 📚 Suggested Prerequisites

### Programming

```text
Python
C / C++
Git & GitHub
Linux basics
```

### Hardware

```text
Digital Logic
Combinational Circuits
Sequential Circuits
Registers
Finite State Machines
Basic HDL
Computer Architecture
```

### Mathematics

```text
Binary Arithmetic
Basic Linear Algebra
Basic Probability
```

Advanced machine-learning knowledge is **not required at the beginning**.

---

## 💡 Project Principles

### 🔨 Learn by Building

Every major concept should lead to working code, an experiment, or a measurable result.

### 🧪 Verify Everything

Hardware should be tested automatically whenever possible rather than relying only on waveform inspection.

### 📊 Measure Performance

AI hardware experiments should report meaningful measurements such as:

```text
Latency
Throughput
Accuracy
Resource Usage
Memory Usage
Energy Estimates
```

### 🌱 Start Small

Small, correct contributions are more useful than large unfinished projects.

### 🔁 Keep It Reproducible

Another learner should be able to clone an experiment, follow the instructions, and reproduce the result.

---

## 🔭 Long-Term Vision

The long-term goal is to grow **AI Hardware Roadmap** into an open-source learning platform covering the journey from digital hardware fundamentals to modern AI computing systems.

Planned additions include:

- [ ] Step-by-step learning tracks
- [ ] Beginner RTL labs
- [ ] Automated verification labs
- [ ] RISC-V exercises
- [ ] FPGA AI exercises
- [ ] AI accelerator projects
- [ ] Hardware compiler tutorials
- [ ] Neuromorphic computing experiments
- [ ] Reproducible benchmarks
- [ ] Research paper reading tracks
- [ ] Open-source contribution guides
- [ ] Student project ideas
- [ ] Troubleshooting guides
- [ ] Community-contributed labs
- [ ] Documentation website

---

## 🤝 Contributing

Contributions are welcome as the project develops.

You can contribute by:

- Fixing documentation
- Improving explanations
- Adding tests
- Reporting setup problems
- Adding exercises
- Adding hardware examples
- Improving reproducibility
- Adding useful resources
- Creating new labs

Please read [`CONTRIBUTING.md`](CONTRIBUTING.md) before submitting a pull request.

---

## 📈 Project Status

> [!IMPORTANT]
> This project is currently under active development.

The roadmap is being built alongside real learning, experimentation, benchmarking, and open-source contributions.

Some sections will remain incomplete until they have been tested and verified.

---

## ⭐ Support the Project

If this roadmap helps you learn something useful:

- ⭐ Star the repository
- 🍴 Fork it and experiment
- 🐛 Report problems
- 💡 Suggest improvements
- 🤝 Contribute a lab or example

---

## 📜 License

This project is open source.

See [`LICENSE`](LICENSE) for details.

---

## 🚀 Start Here

New to the roadmap?

Start with:

### **[00 → Getting Started](roadmap/00-getting-started.md)**

Then continue to:

### **[01 → cocotb Basics](labs/01-cocotb-basics/)**

---

<div align="center">

### Build it. Verify it. Measure it. Understand it.

**AI Hardware Roadmap**

From RTL to intelligent computing hardware.

</div>