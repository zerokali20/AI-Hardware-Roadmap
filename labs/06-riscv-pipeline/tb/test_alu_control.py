
import cocotb
from cocotb.triggers import Timer


async def check(dut, opcode, funct3, funct7, expected, invalid=0):
    dut.opcode.value = opcode
    dut.funct3.value = funct3
    dut.funct7.value = funct7

    await Timer(1, unit="ns")

    assert int(dut.alu_op.value) == expected
    assert int(dut.invalid_operation.value) == invalid


@cocotb.test()
async def test_r_type_add_sub(dut):
    await check(dut, 0x33, 0, 0x00, 0)
    await check(dut, 0x33, 0, 0x20, 1)


@cocotb.test()
async def test_r_type_logic(dut):
    await check(dut, 0x33, 7, 0x00, 2)  # AND
    await check(dut, 0x33, 6, 0x00, 3)  # OR
    await check(dut, 0x33, 4, 0x00, 4)  # XOR


@cocotb.test()
async def test_r_type_shifts(dut):
    await check(dut, 0x33, 1, 0x00, 5)  # SLL
    await check(dut, 0x33, 5, 0x00, 6)  # SRL
    await check(dut, 0x33, 5, 0x20, 7)  # SRA


@cocotb.test()
async def test_r_type_comparisons(dut):
    await check(dut, 0x33, 2, 0x00, 8)  # SLT
    await check(dut, 0x33, 3, 0x00, 9)  # SLTU


@cocotb.test()
async def test_i_type_arithmetic(dut):
    await check(dut, 0x13, 0, 0x00, 0)  # ADDI
    await check(dut, 0x13, 2, 0x00, 8)  # SLTI
    await check(dut, 0x13, 3, 0x00, 9)  # SLTIU


@cocotb.test()
async def test_i_type_logic(dut):
    await check(dut, 0x13, 7, 0x00, 2)  # ANDI
    await check(dut, 0x13, 6, 0x00, 3)  # ORI
    await check(dut, 0x13, 4, 0x00, 4)  # XORI


@cocotb.test()
async def test_i_type_shifts(dut):
    await check(dut, 0x13, 1, 0x00, 5)  # SLLI
    await check(dut, 0x13, 5, 0x00, 6)  # SRLI
    await check(dut, 0x13, 5, 0x20, 7)  # SRAI


@cocotb.test()
async def test_load_store(dut):
    await check(dut, 0x03, 2, 0x00, 0)
    await check(dut, 0x23, 2, 0x00, 0)


@cocotb.test()
async def test_branch(dut):
    await check(dut, 0x63, 0, 0x00, 1)


@cocotb.test()
async def test_jump(dut):
    await check(dut, 0x6F, 0, 0x00, 0)
    await check(dut, 0x67, 0, 0x00, 0)


@cocotb.test()
async def test_upper_immediates(dut):
    await check(dut, 0x37, 0, 0x00, 0)
    await check(dut, 0x17, 0, 0x00, 0)


@cocotb.test()
async def test_invalid_opcode(dut):
    await check(dut, 0x7F, 0, 0x00, 0, 1)


@cocotb.test()
async def test_invalid_r_type(dut):
    await check(dut, 0x33, 0, 0x7F, 0, 1)


@cocotb.test()
async def test_invalid_shift(dut):
    await check(dut, 0x13, 5, 0x7F, 0, 1)
