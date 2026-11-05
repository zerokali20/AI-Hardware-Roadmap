
import random

import cocotb
from cocotb.triggers import Timer


MASK = 0xFFFFFFFF

ALU_ADD = 0
ALU_SUB = 1
ALU_AND = 2
ALU_OR = 3
ALU_XOR = 4
ALU_SLL = 5
ALU_SRL = 6
ALU_SRA = 7
ALU_SLT = 8
ALU_SLTU = 9


def signed32(value):
    value &= MASK
    return value - (1 << 32) if value & 0x80000000 else value


def expected_result(a, b, op):
    a &= MASK
    b &= MASK
    shift = b & 0x1F

    operations = {
        ALU_ADD: lambda: (a + b) & MASK,
        ALU_SUB: lambda: (a - b) & MASK,
        ALU_AND: lambda: a & b,
        ALU_OR: lambda: a | b,
        ALU_XOR: lambda: a ^ b,
        ALU_SLL: lambda: (a << shift) & MASK,
        ALU_SRL: lambda: a >> shift,
        ALU_SRA: lambda: (signed32(a) >> shift) & MASK,
        ALU_SLT: lambda: int(signed32(a) < signed32(b)),
        ALU_SLTU: lambda: int(a < b),
    }

    return operations[op]()


async def check_alu(dut, a, b, op):
    dut.a.value = a & MASK
    dut.b.value = b & MASK
    dut.alu_control.value = op

    await Timer(1, unit="ns")

    expected = expected_result(a, b, op)
    actual = int(dut.result.value)

    assert actual == expected, (
        f"ALU op={op}, a={a:#010x}, b={b:#010x}: "
        f"expected {expected:#010x}, got {actual:#010x}"
    )

    assert int(dut.zero.value) == int(expected == 0)

    assert int(dut.less_than.value) == int(
        signed32(a) < signed32(b)
    )


@cocotb.test()
async def test_add(dut):
    await check_alu(dut, 10, 20, ALU_ADD)
    await check_alu(dut, MASK, 1, ALU_ADD)


@cocotb.test()
async def test_sub(dut):
    await check_alu(dut, 20, 10, ALU_SUB)
    await check_alu(dut, 5, 10, ALU_SUB)


@cocotb.test()
async def test_and(dut):
    await check_alu(dut, 0xF0F0, 0x0FF0, ALU_AND)


@cocotb.test()
async def test_or(dut):
    await check_alu(dut, 0xF000, 0x00FF, ALU_OR)


@cocotb.test()
async def test_xor(dut):
    await check_alu(dut, 0xAAAA, 0x5555, ALU_XOR)


@cocotb.test()
async def test_sll(dut):
    await check_alu(dut, 1, 4, ALU_SLL)
    await check_alu(dut, 1, 32, ALU_SLL)


@cocotb.test()
async def test_srl(dut):
    await check_alu(dut, 0x80000000, 4, ALU_SRL)


@cocotb.test()
async def test_sra(dut):
    await check_alu(dut, 0x80000000, 4, ALU_SRA)
    await check_alu(dut, 0xFFFFFFFF, 3, ALU_SRA)


@cocotb.test()
async def test_slt(dut):
    await check_alu(dut, 0xFFFFFFFF, 1, ALU_SLT)
    await check_alu(dut, 1, 0xFFFFFFFF, ALU_SLT)


@cocotb.test()
async def test_sltu(dut):
    await check_alu(dut, 0xFFFFFFFF, 1, ALU_SLTU)
    await check_alu(dut, 1, 0xFFFFFFFF, ALU_SLTU)


@cocotb.test()
async def test_zero_flag(dut):
    await check_alu(dut, 100, 100, ALU_SUB)
    await check_alu(dut, 0, 0, ALU_ADD)


@cocotb.test()
async def test_randomized(dut):
    rng = random.Random(42)

    for _ in range(1000):
        a = rng.getrandbits(32)
        b = rng.getrandbits(32)
        op = rng.randrange(10)

        await check_alu(dut, a, b, op)
