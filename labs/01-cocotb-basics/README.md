# Lab 01: cocotb Basics with VHDL and GHDL

> 🟢 **Hardware Required:** No  
> **Difficulty:** Beginner  
> **Status:** In Progress

## Overview

This lab introduces automated RTL verification using **cocotb**, **Python**, and **GHDL**.

Instead of creating a traditional VHDL testbench, Python is used to drive inputs into a VHDL design, read the hardware outputs, and automatically verify whether the design behaves correctly.

The first Design Under Test (DUT) is a simple **8-bit unsigned adder**.

---

## Learning Objectives

By completing this lab, you will learn how to:

- Write a simple VHDL module
- Compile VHDL using GHDL
- Understand the concept of a Design Under Test (DUT)
- Use cocotb to control VHDL signals from Python
- Create expected results using a Python reference model
- Automatically compare expected and actual hardware outputs
- Perform randomized hardware verification
- Build a reproducible RTL verification workflow

---

## Verification Flow

```text
Random Test Inputs
        |
        v
+------------------+
|  Python / cocotb |
+--------+---------+
         |
         | a, b
         v
+------------------+
|      GHDL        |
|    Simulator     |
+--------+---------+
         |
         v
+------------------+
|   VHDL Adder     |
|      DUT         |
+--------+---------+
         |
         | result
         v
+------------------+
| Python Reference |
|      Model       |
+--------+---------+
         |
         v
  Expected == Actual
         |
    +----+----+
    |         |
   PASS      FAIL
```

---

## Project Structure

```text
01-cocotb-basics/
|
├── rtl/
│   └── adder.vhd
|
├── tests/
│   └── test_adder.py
|
├── Makefile
├── requirements.txt
└── README.md
```

---

## Design Under Test

The DUT is an 8-bit unsigned adder.

### Inputs

- `a` - 8-bit unsigned value
- `b` - 8-bit unsigned value

### Output

- `result` - 9-bit unsigned result

The output requires 9 bits because the largest possible addition is:

```text
255 + 255 = 510
```

---

## Tools

This lab uses:

| Tool | Purpose |
|---|---|
| VHDL | Hardware description |
| GHDL | VHDL simulation |
| Python | Verification and reference model |
| cocotb | Python-based RTL verification |
| Make | Automated simulation workflow |

---

## Environment Setup

Install the required system tools:

```bash
sudo apt update
sudo apt install ghdl make python3 python3-pip python3-venv
```

Create a Python virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Install the Python dependencies:

```bash
pip install -r requirements.txt
```

---

## Running the Test

From the lab directory:

```bash
make
```

cocotb will:

1. Start GHDL
2. Compile the VHDL design
3. Load the Python testbench
4. Generate input values
5. Drive the DUT inputs
6. Read the DUT output
7. Calculate the expected result in Python
8. Compare the actual and expected values

---

## Current Verification

The current test performs **1000 randomized input combinations**.

For each iteration:

```python
a = random.randint(0, 255)
b = random.randint(0, 255)
```

The expected value is calculated using Python:

```python
expected = a + b
```

The hardware output is read from the DUT:

```python
actual = dut.result.value.to_unsigned()
```

The values are then compared:

```python
assert actual == expected
```

A mismatch immediately causes the test to fail and reports the failing input combination.

---

## Current Result

```text
TESTS=1
PASS=1
FAIL=0
```

✅ The VHDL adder successfully passed the initial automated verification.

---

## Next Steps

- [x] Configure GHDL
- [x] Configure cocotb
- [x] Create an 8-bit VHDL adder
- [x] Run the first automated test
- [x] Add randomized testing
- [ ] Add directed edge-case testing
- [ ] Test all possible input combinations
- [ ] Generate waveform output
- [ ] Introduce an intentional RTL bug
- [ ] Verify that the testbench detects the bug
- [ ] Add GitHub Actions CI

---

## Key Lesson

This lab demonstrates an important verification principle:

> The hardware implementation and the reference model calculate the result independently, and the verification environment checks whether they agree.

This same concept can later be applied to ALUs, register files, processors, RISC-V cores, and AI accelerators.

---

## Part of AI Hardware Roadmap

This lab is part of the **AI Hardware Roadmap**, an open-source practical learning path covering:

**RTL → Verification → RISC-V → Quantized ML → FPGA AI → AI Accelerators → Hardware Compilers → Neuromorphic Computing**
