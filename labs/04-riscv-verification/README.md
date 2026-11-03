# Lab 04: RISC-V RV32I Instruction Decoder Verification with cocotb

## Overview

This lab introduces instruction-level verification using the **RISC-V RV32I instruction set architecture**.

The goal is to design and verify a VHDL instruction decoder capable of extracting common RISC-V instruction fields and reconstructing immediate values for several RV32I instruction formats.

Unlike the earlier labs, which focused on arithmetic blocks and stateful storage, this lab moves verification closer to the processor architecture level. A 32-bit RISC-V instruction is supplied to the VHDL decoder, and a Python reference model independently calculates the expected decoded fields.

The hardware implementation is then checked against this model using both directed and randomized cocotb tests.

The lab covers:

- R-type instructions
- I-type instructions
- S-type instructions
- B-type instructions
- Signed immediate reconstruction
- Python instruction encoders
- Python reference decoding
- Directed verification
- Randomized verification
- Waveform analysis
- Fault injection
- Continuous integration

---

## Learning Objectives

By completing this lab, the following concepts are practiced:

- Understanding the structure of 32-bit RISC-V instructions
- Extracting instruction fields from RTL
- Understanding RV32I instruction formats
- Encoding RISC-V instructions using Python
- Reconstructing split immediate fields
- Sign-extending immediate values
- Building a software reference decoder
- Comparing RTL behavior against a reference model
- Writing directed cocotb tests
- Performing randomized instruction verification
- Debugging instruction decoding using waveforms
- Testing verification quality through fault injection
- Running hardware verification automatically with GitHub Actions

---

## RISC-V Instruction Structure

RV32I instructions are 32 bits wide.

Different instruction types arrange their fields differently, but several fields occupy common bit positions.

### Common Fields

| Field | Instruction Bits | Width |
|---|---:|---:|
| `opcode` | `[6:0]` | 7 bits |
| `rd` | `[11:7]` | 5 bits |
| `funct3` | `[14:12]` | 3 bits |
| `rs1` | `[19:15]` | 5 bits |
| `rs2` | `[24:20]` | 5 bits |
| `funct7` | `[31:25]` | 7 bits |

The decoder exposes these bit fields directly while also generating a 32-bit sign-extended immediate for the supported immediate-based instruction formats.

---

## R-Type Instructions

R-type instructions perform register-to-register operations.

The format is:

```text
31       25 24    20 19    15 14  12 11     7 6       0
+----------+--------+--------+------+--------+----------+
|  funct7  |  rs2   |  rs1   |funct3|   rd   |  opcode  |
+----------+--------+--------+------+--------+----------+
```

The lab verifies the main RV32I integer R-type operations.

| Instruction | funct7 | funct3 | opcode |
|---|---|---|---|
| ADD | `0000000` | `000` | `0110011` |
| SUB | `0100000` | `000` | `0110011` |
| SLL | `0000000` | `001` | `0110011` |
| SLT | `0000000` | `010` | `0110011` |
| SLTU | `0000000` | `011` | `0110011` |
| XOR | `0000000` | `100` | `0110011` |
| SRL | `0000000` | `101` | `0110011` |
| SRA | `0100000` | `101` | `0110011` |
| OR | `0000000` | `110` | `0110011` |
| AND | `0000000` | `111` | `0110011` |

For example:

```asm
add x5, x6, x7
```

uses:

```text
rd  = x5
rs1 = x6
rs2 = x7

funct7 = 0000000
funct3 = 000
opcode = 0110011
```

---

## I-Type Instructions

I-type instructions replace the `rs2` field with a 12-bit immediate.

```text
31                   20 19    15 14  12 11     7 6       0
+----------------------+--------+------+--------+----------+
|      imm[11:0]       |  rs1   |funct3|   rd   |  opcode  |
+----------------------+--------+------+--------+----------+
```

The decoder supports I-type immediate generation for:

- Arithmetic immediate instructions
- Load instructions
- JALR

Supported opcode groups include:

```text
0010011 -> I-type arithmetic
0000011 -> Loads
1100111 -> JALR
```

For example:

```asm
addi x5, x6, 10
```

contains:

```text
immediate = 10
rs1       = x6
rd        = x5
funct3    = 000
opcode    = 0010011
```

---

## S-Type Instructions

S-type instructions are used for memory stores.

Unlike I-type instructions, the immediate is split across two locations.

```text
31          25 24    20 19    15 14  12 11        7 6       0
+-------------+--------+--------+------+------------+----------+
| imm[11:5]   |  rs2   |  rs1   |funct3| imm[4:0]  |  opcode  |
+-------------+--------+--------+------+------------+----------+
```

The immediate is reconstructed using:

```text
imm[11:5] = instruction[31:25]
imm[4:0]  = instruction[11:7]
```

Store instructions use opcode:

```text
0100011
```

The tests include store-word examples such as:

```asm
sw x7, 12(x6)
```

as well as negative store offsets.

---

## B-Type Instructions

B-type instructions are used for conditional branches.

Their immediate encoding is more complex because the immediate bits are distributed across the instruction.

```text
31      30       25 24    20 19    15 14  12 11      8 7       6      0
+--------+----------+--------+--------+------+---------+--------+--------+
|imm[12] |imm[10:5] |  rs2   |  rs1   |funct3|imm[4:1]|imm[11] | opcode |
+--------+----------+--------+--------+------+---------+--------+--------+
```

The immediate is reconstructed as:

```text
imm[12]   = instruction[31]
imm[11]   = instruction[7]
imm[10:5] = instruction[30:25]
imm[4:1]  = instruction[11:8]
imm[0]    = 0
```

The final bit is always zero because branch offsets are aligned to two-byte boundaries.

The following branch encodings are exercised:

| Instruction | funct3 |
|---|---|
| BEQ | `000` |
| BNE | `001` |
| BLT | `100` |
| BGE | `101` |
| BLTU | `110` |
| BGEU | `111` |

---

## Immediate Sign Extension

Immediate values are decoded into 32-bit values.

For example, the positive 12-bit value `10` is extended as:

```text
000000001010
        |
        v
00000000000000000000000000001010
```

Negative values require sign extension.

For example, `-1` encoded as a 12-bit immediate is:

```text
111111111111
```

and becomes:

```text
11111111111111111111111111111111
```

The testbench explicitly checks negative immediates so that incorrect zero-extension implementations can be detected.

---

## Project Structure

```text
04-riscv-verification/
|
+-- rtl/
|   +-- rv32i_decoder.vhd
|
+-- tests/
|   +-- test_rv32i_decoder.py
|
+-- Makefile
+-- requirements.txt
+-- README.md
```

### `rtl/rv32i_decoder.vhd`

Contains the VHDL implementation of the RV32I instruction decoder.

### `tests/test_rv32i_decoder.py`

Contains:

- RISC-V instruction encoders
- Sign-extension logic
- Python reference decoder
- Directed tests
- Randomized tests
- Waveform demonstration test

### `Makefile`

Connects cocotb to GHDL and identifies the VHDL top-level design and Python test module.

### `requirements.txt`

Defines the Python dependencies required to reproduce the verification environment.

---

## Tools Used

The lab uses:

- **VHDL** for the RTL implementation
- **GHDL** for VHDL simulation
- **Python** for the reference model and instruction generation
- **cocotb** for verification
- **GTKWave** for waveform inspection
- **Git** for version control
- **GitHub Actions** for continuous integration

---

## RTL Decoder Design

The decoder receives one 32-bit instruction:

```text
instruction[31:0]
```

and exposes:

```text
opcode
rd
funct3
rs1
rs2
funct7
immediate
```

The common fields are extracted directly from their corresponding instruction positions.

Immediate generation is selected according to the instruction opcode.

At the current scope of this lab, immediate reconstruction is implemented for:

```text
I-type
S-type
B-type
```

The decoder is combinational and therefore does not require a clock.

---

## Python Instruction Encoders

The testbench contains independent Python functions for constructing RISC-V instructions.

These include:

```python
encode_r_type(...)
encode_i_type(...)
encode_s_type(...)
encode_b_type(...)
```

Instead of manually writing 32-bit binary instructions, the tests provide architectural fields such as:

```text
rd
rs1
rs2
funct3
funct7
immediate
opcode
```

The encoder then places each value into the correct instruction bit positions.

This makes the tests easier to read and allows thousands of legal instruction combinations to be generated automatically.

---

## Python Reference Decoder

A Python reference decoder provides an independent expected result for each instruction.

The reference model extracts:

```text
opcode
rd
funct3
rs1
rs2
funct7
```

and reconstructs immediate values according to the instruction type.

The verification flow therefore becomes:

```text
                 32-bit instruction
                         |
             +-----------+-----------+
             |                       |
             v                       v
      VHDL RTL Decoder        Python Reference
             |                       |
             v                       v
       Actual values          Expected values
             |                       |
             +-----------+-----------+
                         |
                         v
                       Compare
```

This approach is stronger than duplicating expected constants throughout individual tests because the same reference model can validate large numbers of generated instructions.

---

## Directed Verification

Directed tests are used first to verify known instruction encodings and important boundary behaviors.

The directed verification covers:

- ADD decoding
- SUB decoding
- Main R-type operations
- ADDI decoding
- Positive I-type immediate
- Negative I-type immediate
- SW decoding
- Positive S-type immediate
- Negative S-type immediate
- BEQ decoding
- Positive branch offset
- Negative branch offset
- Main branch `funct3` encodings

Directed testing makes failures easier to diagnose before moving to large randomized test sets.

---

## Randomized Verification

After the directed tests pass, randomized verification generates large numbers of instruction combinations.

Four randomized test groups are used:

```text
R-type
I-type
S-type
B-type
```

Each group executes approximately:

```text
1,000 randomized instructions
```

giving roughly:

```text
4,000 randomized instruction cases
```

in addition to the directed tests.

### Random R-Type Verification

Random values are generated for:

```text
funct7
rs2
rs1
funct3
rd
```

The resulting 32-bit instruction is passed to both the RTL decoder and the Python reference model.

### Random I-Type Verification

Randomized testing covers:

```text
immediate = -2048 to +2047
rs1
rd
funct3
```

This exercises the complete signed 12-bit immediate range through randomized sampling.

### Random S-Type Verification

Random store instructions vary:

```text
immediate
rs1
rs2
funct3
```

with store `funct3` values corresponding to:

```text
SB
SH
SW
```

### Random B-Type Verification

Random branch testing uses signed branch offsets between:

```text
-4096 and +4094
```

with even offsets only.

The branch test randomly selects among:

```text
BEQ
BNE
BLT
BGE
BLTU
BGEU
```

This is particularly useful because B-type immediates are distributed across several non-contiguous instruction fields.

---

## Test Suite

The completed test suite contains 15 cocotb tests.

| Test | Purpose |
|---|---|
| `test_add_instruction_decode` | Verify ADD field decoding |
| `test_sub_instruction_decode` | Verify SUB field decoding |
| `test_all_r_type_instructions` | Verify main R-type instruction encodings |
| `test_addi_instruction` | Verify ADDI and positive I-type immediate |
| `test_negative_immediate` | Verify negative I-type sign extension |
| `test_sw_instruction` | Verify S-type store decoding |
| `test_negative_s_type_immediate` | Verify negative S-type immediate |
| `test_beq_instruction` | Verify BEQ decoding |
| `test_negative_branch_immediate` | Verify backwards branch offset |
| `test_all_branch_types` | Verify main RV32I branch encodings |
| `test_random_r_type` | Randomized R-type verification |
| `test_random_i_type` | Randomized I-type verification |
| `test_random_s_type` | Randomized S-type verification |
| `test_random_b_type` | Randomized B-type verification |
| `test_waveform_demo` | Generate a readable decoder waveform |

Final regression result:

```text
TESTS=15
PASS=15
FAIL=0
```

---

## Running the Lab

Enter the lab directory:

```bash
cd /mnt/d/AI-Hardware-Roadmap/labs/04-riscv-verification
```

Activate the Python environment:

```bash
source .venv/bin/activate
```

Install dependencies if required:

```bash
python -m pip install -r requirements.txt
```

Run the complete verification suite:

```bash
make clean
make
```

---

## Running Individual Tests

For example, run the R-type randomized test:

```bash
make clean
make COCOTB_TESTCASE=test_random_r_type
```

Run the I-type randomized test:

```bash
make clean
make COCOTB_TESTCASE=test_random_i_type
```

Run the S-type randomized test:

```bash
make clean
make COCOTB_TESTCASE=test_random_s_type
```

Run the B-type randomized test:

```bash
make clean
make COCOTB_TESTCASE=test_random_b_type
```

---

## Waveform Analysis

A dedicated waveform test applies four different instruction formats:

```text
ADD
ADDI
SW
BEQ
```

Generate the waveform with:

```bash
make clean
make COCOTB_TESTCASE=test_waveform_demo SIM_ARGS="--wave=rv32i_decoder_wave.ghw"
```

Open it using:

```bash
gtkwave rv32i_decoder_wave.ghw
```

Useful signals include:

```text
instruction
opcode
rd
funct3
rs1
rs2
funct7
immediate
```

The waveform demonstrates how the decoder outputs change as different instruction formats are applied.

Conceptually:

```text
0 ns             10 ns             20 ns             30 ns
 |                 |                 |                 |
 v                 v                 v                 v
ADD             ADDI -5           SW +12            BEQ +16
R-type          I-type            S-type            B-type
```

---

## Fault Injection

Passing tests alone do not prove that a testbench is effective.

To evaluate the verification environment itself, intentional RTL bugs are introduced and the tests are expected to detect them.

### Fault 1: Incorrect `rd` Field

The correct decoder:

```vhdl
rd <= instruction(11 downto 7);
```

was temporarily changed to an incorrect bit range.

The directed ADD test detected the incorrect destination register.

### Fault 2: Broken Sign Extension

Correct sign extension:

```text
negative immediate
        |
        v
upper bits filled with 1
```

was intentionally replaced with zero extension.

The negative immediate test detected the fault while positive immediate values could still appear correct.

This demonstrates why negative-value testing is important.

### Fault 3: Incorrect B-Type Immediate Reconstruction

One of the scattered B-type immediate bits was intentionally removed from the reconstruction logic.

Randomized B-type verification detected the fault when it generated an instruction that required the affected bit.

This demonstrates an important advantage of randomized verification. A small set of directed instructions may not exercise every possible encoded field combination.

After each experiment, the correct RTL was restored and the complete regression suite was run again.

---

## Continuous Integration

Lab 04 is integrated with GitHub Actions.

The CI workflow automatically:

1. Checks out the repository.
2. Installs GHDL and Make.
3. Configures Python 3.12.
4. Installs the Python dependencies.
5. Verifies the cocotb and GHDL toolchain.
6. Runs the complete RV32I decoder verification suite.

The workflow is triggered when Lab 04 or its CI configuration changes.

This confirms that the verification environment works on a clean machine and does not depend only on the local development environment.

---

## Verification Progress

- [x] Create RV32I instruction decoder
- [x] Understand the 32-bit RISC-V instruction format
- [x] Decode opcode
- [x] Decode rd
- [x] Decode rs1
- [x] Decode rs2
- [x] Decode funct3
- [x] Decode funct7
- [x] Verify R-type instructions
- [x] Verify I-type instructions
- [x] Verify S-type instructions
- [x] Verify B-type instructions
- [x] Decode RISC-V immediate values
- [x] Create Python instruction encoder/reference model
- [x] Add directed instruction tests
- [x] Add randomized decoder verification
- [x] Generate decoder waveforms
- [x] Inject decoder RTL faults
- [x] Verify tests detect injected faults
- [x] Add Lab 04 to GitHub Actions CI

---

## Key Lessons

### 1. Instruction decoding is primarily a bit-placement problem

A decoder must interpret fixed bit positions according to the instruction format. Small indexing mistakes can change registers, operation types, or immediate values.

### 2. RISC-V instruction formats reuse bit positions

Fields such as `opcode`, `rd`, `rs1`, and `rs2` occupy predictable positions, but their meaning depends on the instruction format.

For example, bits that represent `rs2` in an R-type instruction form part of the immediate in an I-type instruction.

### 3. Immediate decoding requires careful reconstruction

I-type immediates are contiguous, while S-type and B-type immediates are split across multiple instruction fields.

B-type decoding is especially useful for learning how ISA-level information maps onto physical instruction bits.

### 4. Signed values require dedicated tests

Positive immediate tests alone cannot reliably detect a broken sign-extension implementation.

Negative I-type, S-type, and B-type cases therefore form an important part of the verification strategy.

### 5. Reference models make randomized verification practical

The Python decoder independently determines the expected result.

This allows thousands of generated instructions to be checked without manually calculating the expected output for every case.

### 6. Directed and randomized tests serve different purposes

Directed tests target known architectural behavior and make failures easy to understand.

Randomized tests explore a much larger input space and can expose combinations that were not anticipated when writing the directed tests.

### 7. Fault injection tests the testbench itself

Deliberately introducing incorrect field extraction, sign extension, and immediate reconstruction confirms that the verification environment can detect realistic RTL errors.

---

## Roadmap Progression

This lab builds directly on the previous verification work:

```text
Lab 01
Basic combinational verification
        |
        v
Lab 02
ALU verification
        |
        v
Lab 03
Stateful register-file verification
        |
        v
Lab 04
RISC-V instruction-level verification
        |
        v
Lab 05
Formal verification
```

Lab 04 represents the transition from verifying isolated digital components to verifying logic that understands a real processor instruction set.

The instruction encoding knowledge, reference-model approach, randomized testing techniques, and fault-injection methodology developed here provide a foundation for later work involving RISC-V cores, formal verification, processor datapaths, and hardware accelerators.