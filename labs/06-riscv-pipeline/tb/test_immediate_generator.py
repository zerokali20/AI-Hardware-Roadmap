
import cocotb
from cocotb.triggers import Timer


async def check_immediate(dut, instruction, expected):
    dut.instruction.value = instruction
    await Timer(1, unit="ns")

    actual = int(dut.immediate.value)
    expected &= 0xFFFFFFFF

    assert actual == expected, (
        f"Instruction {instruction:#010x}: "
        f"expected {expected:#010x}, got {actual:#010x}"
    )


@cocotb.test()
async def test_i_type_positive(dut):
    # addi x1, x0, 5
    await check_immediate(dut, 0x00500093, 5)


@cocotb.test()
async def test_i_type_negative(dut):
    # addi x1, x0, -1
    await check_immediate(dut, 0xFFF00093, -1)


@cocotb.test()
async def test_i_type_minimum(dut):
    # addi x1, x0, -2048
    await check_immediate(dut, 0x80000093, -2048)


@cocotb.test()
async def test_s_type_positive(dut):
    # sw x3, 12(x0)
    await check_immediate(dut, 0x00302623, 12)


@cocotb.test()
async def test_s_type_negative(dut):
    # sw x3, -4(x0)
    await check_immediate(dut, 0xFE302E23, -4)


@cocotb.test()
async def test_b_type_positive(dut):
    # beq x1, x2, +8
    await check_immediate(dut, 0x00208463, 8)


@cocotb.test()
async def test_b_type_negative(dut):
    # beq x0, x0, -4
    await check_immediate(dut, 0xFE000EE3, -4)


@cocotb.test()
async def test_u_type_lui(dut):
    # lui x1, 0x12345
    await check_immediate(dut, 0x123450B7, 0x12345000)


@cocotb.test()
async def test_u_type_auipc(dut):
    # auipc x1, 0x12345
    await check_immediate(dut, 0x12345097, 0x12345000)


@cocotb.test()
async def test_j_type_zero(dut):
    # jal x0, 0
    await check_immediate(dut, 0x0000006F, 0)


@cocotb.test()
async def test_j_type_positive(dut):
    # jal x1, +8
    await check_immediate(dut, 0x008000EF, 8)


@cocotb.test()
async def test_invalid_opcode(dut):
    await check_immediate(dut, 0xFFFFFFFF, 0)
