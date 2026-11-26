"""Documented RV32I benchmark workloads for the PipeGuard-RV fault-injection campaign.

Provides 8 deterministic workloads covering all required control-flow and
pipeline hazard patterns:
  1. sequential          — linear ALU execution, zero redirects
  2. conditional_branch  — taken and not-taken conditional branches
  3. loop                — iterative backward-branch loop
  4. jal_jalr            — direct call (JAL) and indirect return (JALR)
  5. load_use_hazard     — back-to-back load-use dependencies triggering stalls
  6. pipeline_flush      — repeated control-hazard squashes
  7. mixed               — combined ALU, load/store, branch, jump, and hazard
  8. iot_controller      — simulated embedded IoT sensor-threshold controller

All workloads end with `HALT = jal(0, 0)` and specify an exact observation
window (`cycles`) and expected final register assertions (`expected_regs`) so
that fault-free reference traces can be independently validated.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tb" / "common"))
from rv32i import (
    NOP,
    add,
    addi,
    beq,
    bge,
    blt,
    bne,
    jal,
    jalr,
    lw,
    sub,
    sw,
)

HALT = jal(0, 0)

WORKLOADS = {
    "sequential": {
        "description": "Linear ALU sequence with no branches or stalls before halt.",
        "cycles": 35,
        "words": [
            addi(1, 0, 5),
            addi(2, 0, 7),
            add(3, 1, 2),       # x3 = 12
            sub(4, 2, 1),       # x4 = 2
            addi(5, 3, -1),     # x5 = 11
            add(6, 5, 4),       # x6 = 13
            addi(7, 6, 4),      # x7 = 17
            HALT,
        ],
        "expected_regs": {3: 12, 4: 2, 5: 11, 6: 13, 7: 17},
    },
    "conditional_branch": {
        "description": "Mix of taken and not-taken conditional branches (BEQ, BNE, BLT).",
        "cycles": 45,
        "words": [
            addi(1, 0, 10),
            addi(2, 0, 10),
            beq(1, 2, 12),      # taken -> skip 2 instrs
            addi(3, 0, 99),     # squashed
            addi(3, 0, 88),     # squashed
            bne(1, 2, 12),      # not taken
            addi(4, 0, 4),      # x4 = 4
            blt(4, 1, 8),       # taken -> skip 1 instr
            addi(5, 0, 77),     # squashed
            addi(6, 0, 6),      # x6 = 6
            HALT,
        ],
        "expected_regs": {3: 0, 4: 4, 5: 0, 6: 6},
    },
    "loop": {
        "description": "Iterative backward-branch loop summing 1..5 into x3.",
        "cycles": 70,
        "words": [
            addi(1, 0, 0),      # counter i = 0
            addi(2, 0, 5),      # limit = 5
            addi(3, 0, 0),      # sum = 0
            addi(1, 1, 1),      # 12: i += 1
            add(3, 3, 1),       # 16: sum += i
            bne(1, 2, -8),      # 20: if i != 5 branch to 12
            addi(4, 3, 10),     # 24: x4 = 25
            HALT,
        ],
        "expected_regs": {1: 5, 3: 15, 4: 25},
    },
    "jal_jalr": {
        "description": "Subroutine call via JAL and indirect return via JALR.",
        "cycles": 45,
        "words": [
            addi(5, 0, 20),     # 0: arg
            jal(1, 16),         # 4: call 20 (x1 = 8)
            addi(7, 6, 1),      # 8: x7 = 24
            HALT,               # 12
            NOP,                # 16
            addi(6, 5, 3),      # 20: callee (x6 = 23)
            jalr(0, 1, 0),      # 24: return to 8
        ],
        "expected_regs": {1: 8, 6: 23, 7: 24},
    },
    "load_use_hazard": {
        "description": "Store-load followed immediately by dependent ALU ops triggering load-use stalls.",
        "cycles": 45,
        "words": [
            addi(1, 0, 42),
            addi(2, 0, 16),     # base addr 16
            sw(1, 2, 0),
            lw(3, 2, 0),        # load x3 = 42
            add(4, 3, 1),       # load-use stall -> x4 = 84
            sw(4, 2, 4),
            lw(5, 2, 4),        # load x5 = 84
            addi(6, 5, 6),      # load-use stall -> x6 = 90
            HALT,
        ],
        "expected_regs": {3: 42, 4: 84, 5: 84, 6: 90},
    },
    "pipeline_flush": {
        "description": "Back-to-back control hazards exercising IF/ID and ID/EX flushes.",
        "cycles": 45,
        "words": [
            addi(1, 0, 1),
            jal(0, 16),         # 4 -> 20
            addi(10, 0, 10),    # squashed
            addi(11, 0, 11),    # squashed
            addi(12, 0, 12),    # squashed
            beq(1, 1, 12),      # 20 -> 32
            addi(13, 0, 13),    # squashed
            addi(14, 0, 14),    # squashed
            addi(15, 0, 15),    # 32: x15 = 15
            HALT,
        ],
        "expected_regs": {10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 15},
    },
    "mixed": {
        "description": "Combined ALU, store/load, load-use stall, conditional loop, and JAL.",
        "cycles": 75,
        "words": [
            addi(1, 0, 3),      # count = 3
            addi(2, 0, 32),     # base addr
            addi(3, 0, 0),      # acc = 0
            sw(1, 2, 0),        # 12: store count
            lw(4, 2, 0),        # 16: load count
            add(3, 3, 4),       # 20: load-use stall, acc += count
            addi(1, 1, -1),     # 24: count--
            bne(1, 0, -16),     # 28: loop to 12
            jal(5, 8),          # 32: call +8 -> 40
            HALT,               # 36
            addi(6, 3, 4),      # 40: x6 = 10
            jalr(0, 5, 0),      # 44: return to 36
        ],
        "expected_regs": {1: 0, 3: 6, 6: 10},
    },
    "iot_controller": {
        "description": "Simulated embedded IoT sensor-threshold controller: polls 3 sensor samples, clamps/acts on threshold, writes actuator command to memory.",
        "cycles": 90,
        "words": [
            addi(1, 0, 64),     # 0: MMIO/sensor buffer base addr 64
            addi(2, 0, 25),     # 4: sample 0 = 25
            sw(2, 1, 0),        # 8
            addi(2, 0, 40),     # 12: sample 1 = 40 (above threshold 30)
            sw(2, 1, 4),        # 16
            addi(2, 0, 35),     # 20: sample 2 = 35 (above threshold 30)
            sw(2, 1, 8),        # 24
            addi(3, 0, 30),     # 28: threshold = 30
            addi(4, 0, 0),      # 32: alarm_count = 0
            addi(5, 0, 0),      # 36: idx = 0
            addi(6, 0, 12),     # 40: byte limit = 12
            # loop at 44:
            add(7, 1, 5),       # 44: addr = base + idx
            lw(8, 7, 0),        # 48: read sensor[idx]
            blt(8, 3, 8),       # 52: load-use stall; if sample < 30 skip alarm++
            addi(4, 4, 1),      # 56: alarm_count++
            addi(5, 5, 4),      # 60: idx += 4
            bne(5, 6, -20),     # 64: if idx != 12 loop to 44
            # actuator command: 1 if alarm_count >= 2 else 0
            addi(9, 0, 2),      # 68
            blt(4, 9, 12),      # 72: if alarm_count < 2 -> actuator_off
            addi(10, 0, 1),     # 76: actuator = 1
            sw(10, 1, 16),      # 80: store actuator cmd at addr 80
            HALT,               # 84
            addi(10, 0, 0),     # 88: actuator = 0
            sw(10, 1, 16),      # 92
            HALT,               # 96
        ],
        "expected_regs": {4: 2, 10: 1},
    },
}
