# Lab 03: Stateful Register File Verification with cocotb

## Overview

This lab introduces **stateful RTL verification** using VHDL, GHDL, Python, and cocotb.

Unlike the combinational circuits verified in the previous labs, a register file stores data across clock cycles. Verification therefore requires tracking the internal state of the design over time rather than checking only the immediate relationship between inputs and outputs.

The design implemented in this lab is an **8 × 8-bit register file** with:

- 8 registers
- 8-bit data width
- 1 synchronous write port
- 2 asynchronous read ports
- synchronous reset
- write-enable control

The cocotb testbench verifies basic read/write behavior, reset behavior, write protection, all register addresses, repeated writes, and long randomized stateful operation sequences.

A Python reference model is used as the expected state of the register file and is continuously compared against the VHDL implementation.

---

## Learning Objectives

The main objectives of this lab are to:

- understand verification of sequential RTL
- generate and control clocks using cocotb
- synchronize testbench operations with clock edges
- verify synchronous register writes
- verify asynchronous register reads
- verify synchronous reset behavior
- verify write-enable protection
- maintain a software reference model of hardware state
- perform directed stateful verification
- perform randomized stateful verification
- inspect sequential behavior using waveforms
- inject RTL faults and confirm that the testbench detects them
- run the complete verification suite automatically using GitHub Actions

---

## Register File Architecture

The register file contains eight independent 8-bit registers.

```text
                    ┌──────────────────────┐
 write_data[7:0] ──►│                      │
                    │                      ├──► read_data1[7:0]
 write_addr[2:0] ──►│    8 × 8 Register   │
                    │        File          ├──► read_data2[7:0]
   write_enable ───►│                      │
                    │                      │
          clock ───►│                      │
                    └──────────────────────┘
                         ▲            ▲
                         │            │
                  read_addr1     read_addr2
```

### Write Port

The write port is synchronous.

A register is updated only on the rising edge of the clock when:

```text
write_enable = 1
```

The selected register is determined by:

```text
write_addr
```

and receives:

```text
write_data
```

Conceptually:

```text
Rising clock edge
       │
       ▼
write_enable = 1?
       │
   ┌───┴───┐
   │       │
  Yes      No
   │       │
   ▼       ▼
 Write    Keep
register  state
```

---

## Read Ports

The register file contains two independent asynchronous read ports.

```text
read_addr1 ──► Register File ──► read_data1
read_addr2 ──► Register File ──► read_data2
```

Changing either read address changes the corresponding output without requiring another clock edge.

This allows two registers to be observed simultaneously.

---

## Reset Behavior

The register file uses a synchronous reset.

When:

```text
reset = 1
```

the reset is applied on the next rising clock edge.

All eight registers are then cleared to zero.

```text
R0 = 0
R1 = 0
R2 = 0
R3 = 0
R4 = 0
R5 = 0
R6 = 0
R7 = 0
```

The testbench verifies reset behavior after first storing non-zero values. This confirms that reset actually clears existing state rather than simply relying on the initial register values.

---

## Project Structure

```text
03-register-file-verification/
│
├── rtl/
│   └── register_file.vhd
│
├── tests/
│   └── test_register_file.py
│
├── Makefile
├── requirements.txt
└── README.md
```

The GitHub Actions workflow for this lab is stored at the repository level:

```text
.github/workflows/lab03-register-file-verification.yml
```

---

## Tools Used

| Tool | Purpose |
|---|---|
| VHDL | Register-file RTL implementation |
| GHDL | VHDL compilation and simulation |
| Python | Verification logic and reference model |
| cocotb | Python-based RTL verification |
| GTKWave | Waveform inspection |
| Make | Simulation automation |
| GitHub Actions | Continuous integration |

---

## RTL Design

The register storage is represented as an array of eight 8-bit vectors:

```vhdl
type register_array is array (0 to 7)
    of std_logic_vector(7 downto 0);

signal registers : register_array :=
    (others => (others => '0'));
```

Writes and reset operations occur inside a clocked process:

```vhdl
process(clk)
begin
    if rising_edge(clk) then
        if reset = '1' then
            registers <= (others => (others => '0'));
        elsif write_enable = '1' then
            registers(to_integer(unsigned(write_addr)))
                <= write_data;
        end if;
    end if;
end process;
```

The two read ports are asynchronous:

```vhdl
read_data1 <= registers(
    to_integer(unsigned(read_addr1))
);

read_data2 <= registers(
    to_integer(unsigned(read_addr2))
);
```

---

## cocotb Clock Generation

Sequential verification requires an active simulation clock.

The testbench generates a 10 ns clock using:

```python
cocotb.start_soon(
    Clock(dut.clk, 10, unit="ns").start()
)
```

The testbench can then synchronize operations with:

```python
await RisingEdge(dut.clk)
```

This is an important difference from the previous combinational verification labs.

For sequential hardware, **when an input is applied matters as much as what value is applied**.

---

## Verification Strategy

The register file is verified in several stages.

### 1. Basic Write and Read

A known value is written to one register.

The value is then read through both read ports.

Example:

```text
Write:
R3 = 42

Read port 1:
R3 → 42

Read port 2:
R3 → 42
```

This confirms basic synchronous writing and dual-port reading.

---

### 2. Reset Verification

Several registers are first given non-zero values.

The synchronous reset is then asserted and a rising clock edge is generated.

After reset, all eight registers must contain zero.

This verifies that reset clears existing hardware state.

---

### 3. Write-Enable Verification

A register is first given a known value.

An overwrite is then attempted while:

```text
write_enable = 0
```

The original value must remain unchanged.

This verifies that writes cannot occur when the write port is disabled.

---

### 4. All Register Addresses

Each of the eight registers is written with a unique value.

Example:

```text
R0 = 11
R1 = 22
R2 = 33
R3 = 44
R4 = 55
R5 = 66
R6 = 77
R7 = 88
```

The testbench then reads every address and confirms that each register preserved its own value.

This helps detect address decoding and storage errors.

---

### 5. Repeated Writes and Overwrites

The same register is written several times.

Example:

```text
R5 = 40
R5 = 150
R5 = 255
R5 = 0
```

After each write, the latest value must be returned.

This verifies correct state replacement across multiple clock cycles.

---

## Python Reference Model

The major addition in this lab is a software model of the hardware state.

The model represents the eight registers using a Python list:

```python
class RegisterFileModel:
    def __init__(self):
        self.registers = [0] * 8

    def reset(self):
        self.registers = [0] * 8

    def write(self, address, value):
        self.registers[address] = value & 0xFF

    def read(self, address):
        return self.registers[address]
```

Conceptually:

```text
VHDL Register File             Python Reference Model

R0                              model[0]
R1                              model[1]
R2                              model[2]
R3          <────────────>      model[3]
R4                              model[4]
R5                              model[5]
R6                              model[6]
R7                              model[7]
```

After hardware operations, the RTL state is compared against the Python model.

This makes it possible to verify long sequences of state changes without manually calculating every expected register value.

---

## Directed Stateful Verification

The reference model is first tested using a controlled sequence.

Example:

```text
RESET
  │
  ▼
WRITE R2 = 42
  │
  ▼
COMPARE MODEL
  │
  ▼
WRITE R5 = 200
  │
  ▼
COMPARE MODEL
  │
  ▼
OVERWRITE R2 = 100
  │
  ▼
COMPARE MODEL
  │
  ▼
WRITE R7 = 255
  │
  ▼
COMPARE MODEL
  │
  ▼
RESET
  │
  ▼
COMPARE MODEL
```

After each operation, all register values are checked against the Python model.

---

## Randomized Stateful Verification

The testbench performs **1,000 randomized operations** against the register file.

Operations include:

```text
WRITE
DISABLED WRITE
READ
RESET
```

A typical random sequence may look like:

```text
WRITE R3 = 72
READ R3 / R6
WRITE R7 = 255
DISABLED WRITE R3 = 9
WRITE R1 = 100
RESET
READ R7 / R1
WRITE R4 = 33
...
```

The Python model is updated whenever a valid state-changing operation occurs.

After every randomized operation, the hardware state is compared with the expected model state.

```text
Random Operation
       │
       ├──────────────► VHDL Register File
       │
       └──────────────► Python Model
                              │
                              ▼
                     Expected State
                              │
            ┌─────────────────┘
            ▼
      Compare RTL State
            │
       ┌────┴────┐
       │         │
      PASS      FAIL
```

This is stronger than testing isolated input/output pairs because errors can appear only after a particular sequence of earlier operations.

---

## Test Suite

The completed verification suite contains eight cocotb tests:

| Test | Purpose |
|---|---|
| `test_basic_write_and_read` | Basic synchronous write and dual-port read |
| `test_reset_clears_registers` | Verify synchronous reset clears stored state |
| `test_write_enable` | Prevent writes when write-enable is low |
| `test_all_registers` | Verify all eight register addresses |
| `test_register_overwrite` | Verify repeated writes and overwrites |
| `test_reference_model` | Compare RTL state against Python model |
| `test_random_stateful_operations` | Run 1,000 randomized stateful operations |
| `test_waveform_demo` | Generate a short sequence for waveform inspection |

Final regression result:

```text
TESTS=8
PASS=8
FAIL=0
```

---

## Waveform Analysis

A dedicated waveform test generates a short and readable sequence containing:

- reset
- register writes
- simultaneous reads
- register overwrite
- final reset

Generate the waveform with:

```bash
make clean
make COCOTB_TESTCASE=test_waveform_demo SIM_ARGS="--wave=register_file_wave.ghw"
```

Open it using:

```bash
gtkwave register_file_wave.ghw
```

Useful signals to inspect:

```text
clk
reset
write_enable
write_addr
write_data
read_addr1
read_addr2
read_data1
read_data2
```

The waveform makes the difference between synchronous and asynchronous behavior visible.

For writes:

```text
write_addr + write_data + write_enable
                  │
                  ▼
            rising edge
                  │
                  ▼
           register updated
```

For reads:

```text
read_addr changes
        │
        ▼
read_data changes
```

No additional clock edge is required for the asynchronous read ports.

---

## Fault Injection

Intentional RTL bugs were introduced to confirm that the verification environment can detect incorrect hardware behavior.

### Fault 1: Incorrect Write Enable

The write-enable condition was deliberately reversed.

Correct:

```vhdl
elsif write_enable = '1' then
```

Faulty:

```vhdl
elsif write_enable = '0' then
```

The write-enable test detected the error.

---

### Fault 2: Incorrect Reset Condition

The reset condition was deliberately reversed.

Correct:

```vhdl
if reset = '1' then
```

Faulty:

```vhdl
if reset = '0' then
```

The reset verification detected the incorrect behavior.

---

### Fault 3: Incorrect Write Address

All writes were deliberately redirected to register zero:

```vhdl
registers(0) <= write_data;
```

instead of:

```vhdl
registers(to_integer(unsigned(write_addr)))
    <= write_data;
```

The all-register test and randomized stateful verification detected the address corruption.

These experiments demonstrate that a useful verification environment should not only pass a correct implementation. It should also fail when realistic RTL bugs are introduced.

---

## Running the Lab

### Create and activate the Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Run the complete verification suite

```bash
make clean
make
```

Expected final result:

```text
TESTS=8
PASS=8
FAIL=0
```

### Run an individual test

For example:

```bash
make clean
make COCOTB_TESTCASE=test_random_stateful_operations
```

---

## Continuous Integration

The complete Lab 03 verification suite is integrated with GitHub Actions.

The workflow is stored in:

```text
.github/workflows/lab03-register-file-verification.yml
```

For each relevant push or pull request, GitHub Actions:

1. checks out the repository
2. installs GHDL and Make
3. configures Python 3.12
4. installs the Python dependencies
5. verifies the cocotb installation
6. runs the complete register-file verification suite

This ensures that the verification environment works on a clean machine and does not depend only on the local development setup.

The CI workflow passes with all eight tests.

---

## Verification Progress

- [x] Create 8 × 8-bit VHDL register file
- [x] Generate a clock using cocotb
- [x] Verify synchronous register writes
- [x] Verify asynchronous reads
- [x] Verify both read ports
- [x] Verify reset behavior
- [x] Verify write-enable behavior
- [x] Create Python register-file reference model
- [x] Add directed stateful testing
- [x] Add randomized stateful verification
- [x] Verify all register addresses
- [x] Test repeated writes and overwrites
- [x] Generate register-file waveforms
- [x] Introduce intentional sequential RTL bugs
- [x] Verify the testbench detects the bugs
- [x] Add Lab 03 to GitHub Actions CI

---

## Key Lessons

This lab introduces the transition from combinational verification to **stateful sequential verification**.

The main lessons are:

1. Sequential hardware must be verified relative to clock edges.
2. Reset behavior should be tested after creating non-zero state.
3. Write-enable logic must preserve state when writes are disabled.
4. Multiple registers require verification of both storage and address selection.
5. A software reference model provides a reliable expected state.
6. Randomized operation sequences can expose bugs that isolated tests may miss.
7. Comparing the complete hardware state after operations provides stronger checking.
8. Waveforms remain useful for understanding timing and debugging failures.
9. Intentional fault injection helps measure the effectiveness of a testbench.
10. CI verifies that the project can run reproducibly outside the developer's local environment.

---

## Roadmap Progression

This lab builds directly on the previous verification work:

```text
Lab 01
8-bit Adder
    │
    ▼
Basic cocotb Verification
    │
    ▼
Lab 02
8-bit ALU
    │
    ▼
Reference Model + Exhaustive Verification
    │
    ▼
Lab 03
8 × 8 Register File
    │
    ▼
Clocked + Stateful Verification
    │
    ▼
Lab 04
RISC-V Verification
```

Lab 03 establishes the clocked and stateful verification techniques required for more complex processor components.

The next stage applies these ideas to **RISC-V verification**, where arithmetic, register state, instruction behavior, and processor-level execution begin to come together.