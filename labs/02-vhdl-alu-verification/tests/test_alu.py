import random

import cocotb
from cocotb.triggers import Timer


# ALU opcodes
ADD = 0b000
SUB = 0b001
AND = 0b010
OR  = 0b011
XOR = 0b100
SLL = 0b101
SRL = 0b110
SLT = 0b111


def alu_reference(a, b, opcode):
    """
    Python reference model for the 8-bit VHDL ALU.

    Returns:
        result, carry, zero
    """

    carry = 0

    if opcode == ADD:
        full_result = a + b
        result = full_result & 0xFF
        carry = 1 if full_result > 0xFF else 0

    elif opcode == SUB:
        result = (a - b) & 0xFF

    elif opcode == AND:
        result = a & b

    elif opcode == OR:
        result = a | b

    elif opcode == XOR:
        result = a ^ b

    elif opcode == SLL:
        result = (a << 1) & 0xFF

    elif opcode == SRL:
        result = a >> 1

    elif opcode == SLT:
        result = 1 if a < b else 0

    else:
        result = 0

    zero = 1 if result == 0 else 0

    return result, carry, zero


async def drive_and_check(dut, a, b, opcode):
    """Apply inputs to the DUT and compare against the Python model."""

    dut.a.value = a
    dut.b.value = b
    dut.opcode.value = opcode

    await Timer(1, unit="ns")

    expected_result, expected_carry, expected_zero = alu_reference(
        a, b, opcode
    )

    actual_result = dut.result.value.to_unsigned()
    actual_carry = int(dut.carry.value)
    actual_zero = int(dut.zero.value)

    assert actual_result == expected_result, (
        f"Result mismatch: "
        f"a={a}, b={b}, opcode={opcode:03b}, "
        f"expected={expected_result}, got={actual_result}"
    )

    assert actual_carry == expected_carry, (
        f"Carry mismatch: "
        f"a={a}, b={b}, opcode={opcode:03b}, "
        f"expected={expected_carry}, got={actual_carry}"
    )

    assert actual_zero == expected_zero, (
        f"Zero mismatch: "
        f"a={a}, b={b}, opcode={opcode:03b}, "
        f"expected={expected_zero}, got={actual_zero}"
    )


@cocotb.test()
async def test_directed_operations(dut):
    """Directed tests covering every ALU operation."""

    test_cases = [
        # a,   b,   opcode
        (10,   20,  ADD),
        (255,  1,   ADD),
        (0,    0,   ADD),

        (20,   10,  SUB),
        (10,   20,  SUB),
        (50,   50,  SUB),

        (0xAA, 0x55, AND),
        (0xFF, 0x0F, AND),

        (0xA0, 0x05, OR),
        (0x00, 0x00, OR),

        (0xAA, 0xFF, XOR),
        (0xFF, 0xFF, XOR),

        (1,    0,   SLL),
        (128,  0,   SLL),

        (128,  0,   SRL),
        (1,    0,   SRL),

        (10,   20,  SLT),
        (20,   10,  SLT),
        (20,   20,  SLT),
    ]

    for a, b, opcode in test_cases:
        await drive_and_check(dut, a, b, opcode)


@cocotb.test()
async def test_random_operations(dut):
    """Randomized verification across all ALU operations."""

    for _ in range(1000):
        a = random.randint(0, 255)
        b = random.randint(0, 255)
        opcode = random.randint(0, 7)

        await drive_and_check(dut, a, b, opcode)