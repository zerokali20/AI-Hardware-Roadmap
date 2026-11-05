
import cocotb
from cocotb.triggers import Timer

NOP = 0x00000013


def i_type(rd, rs1, imm, funct3=0):
    return (
        ((imm & 0xFFF) << 20)
        | (rs1 << 15)
        | (funct3 << 12)
        | (rd << 7)
        | 0x13
    )


def r_type(rd, rs1, rs2, funct3, funct7=0):
    return (
        (funct7 << 25)
        | (rs2 << 20)
        | (rs1 << 15)
        | (funct3 << 12)
        | (rd << 7)
        | 0x33
    )


def upper_type(rd, imm20, opcode):
    return (
        ((imm20 & 0xFFFFF) << 12)
        | (rd << 7)
        | opcode
    )


async def tick(dut):
    dut.clk.value = 0
    await Timer(5, unit="ns")
    dut.clk.value = 1
    await Timer(5, unit="ns")
    dut.clk.value = 0
    await Timer(1, unit="ns")


async def setup(dut, program):
    dut.clk.value = 0
    dut.rst.value = 1

    rom = dut.frontend.fetch_unit.imem_unit.memory

    for i in range(128):
        rom[i].value = NOP

    for i, instruction in enumerate(program):
        rom[i].value = instruction

    await Timer(1, unit="ns")
    await tick(dut)

    dut.rst.value = 0
    await Timer(1, unit="ns")


async def run(dut, cycles=25):
    for _ in range(cycles):
        await tick(dut)


def reg(dut, index):
    return int(dut.frontend.regfile.registers[index].value)


@cocotb.test()
async def test_add_sub(dut):
    await setup(dut, [
        i_type(1, 0, 30),
        i_type(2, 0, 12),
        r_type(3, 1, 2, 0),
        r_type(4, 1, 2, 0, 0x20),
    ])

    await run(dut)

    assert reg(dut, 3) == 42
    assert reg(dut, 4) == 18


@cocotb.test()
async def test_logical_operations(dut):
    await setup(dut, [
        i_type(1, 0, 12),
        i_type(2, 0, 10),
        r_type(3, 1, 2, 7),  # AND
        r_type(4, 1, 2, 6),  # OR
        r_type(5, 1, 2, 4),  # XOR
        i_type(6, 1, 10, 7), # ANDI
        i_type(7, 1, 10, 6), # ORI
        i_type(8, 1, 10, 4), # XORI
    ])

    await run(dut)

    assert reg(dut, 3) == 8
    assert reg(dut, 4) == 14
    assert reg(dut, 5) == 6
    assert reg(dut, 6) == 8
    assert reg(dut, 7) == 14
    assert reg(dut, 8) == 6


@cocotb.test()
async def test_shift_operations(dut):
    await setup(dut, [
        i_type(1, 0, 16),
        i_type(2, 0, 2),
        r_type(3, 1, 2, 1), # SLL
        r_type(4, 1, 2, 5), # SRL
        i_type(5, 1, 2, 1), # SLLI
        i_type(6, 1, 2, 5), # SRLI
        i_type(7, 0, -16),
        i_type(8, 7, (0x20 << 5) | 2, 5), # SRAI
    ])

    await run(dut)

    assert reg(dut, 3) == 64
    assert reg(dut, 4) == 4
    assert reg(dut, 5) == 64
    assert reg(dut, 6) == 4
    assert reg(dut, 8) == 0xFFFFFFFC


@cocotb.test()
async def test_signed_unsigned_comparisons(dut):
    await setup(dut, [
        i_type(1, 0, -1),
        i_type(2, 0, 1),
        r_type(3, 1, 2, 2), # SLT
        r_type(4, 1, 2, 3), # SLTU
        i_type(5, 1, 1, 2), # SLTI
        i_type(6, 1, 1, 3), # SLTIU
    ])

    await run(dut)

    assert reg(dut, 3) == 1
    assert reg(dut, 4) == 0
    assert reg(dut, 5) == 1
    assert reg(dut, 6) == 0


@cocotb.test()
async def test_lui_ignores_register_source(dut):
    await setup(dut, [
        i_type(1, 0, 9),
        upper_type(5, 0x00008, 0x37),
    ])

    await run(dut)

    assert reg(dut, 5) == 0x00008000, (
        f"LUI expected 0x8000, got {reg(dut, 5):#x}"
    )


@cocotb.test()
async def test_auipc_uses_program_counter(dut):
    await setup(dut, [
        i_type(1, 0, 9),
        upper_type(5, 0x00008, 0x17),
    ])

    await run(dut)

    assert reg(dut, 5) == 0x00008004, (
        f"AUIPC expected 0x8004, got {reg(dut, 5):#x}"
    )
