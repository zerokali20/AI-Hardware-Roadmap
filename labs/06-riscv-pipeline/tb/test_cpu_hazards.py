
import cocotb
from cocotb.triggers import Timer


NOP = 0x00000013
JAL_SELF = 0x0000006F


def addi(rd, rs1, imm):
    return (
        ((imm & 0xFFF) << 20)
        | (rs1 << 15)
        | (0 << 12)
        | (rd << 7)
        | 0x13
    )


def add(rd, rs1, rs2):
    return (
        (rs2 << 20)
        | (rs1 << 15)
        | (0 << 12)
        | (rd << 7)
        | 0x33
    )


def lw(rd, rs1, imm):
    return (
        ((imm & 0xFFF) << 20)
        | (rs1 << 15)
        | (2 << 12)
        | (rd << 7)
        | 0x03
    )


def sw(rs2, rs1, imm):
    imm &= 0xFFF
    return (
        ((imm >> 5) << 25)
        | (rs2 << 20)
        | (rs1 << 15)
        | (2 << 12)
        | ((imm & 0x1F) << 7)
        | 0x23
    )


def beq(rs1, rs2, imm):
    imm &= 0x1FFF
    return (
        (((imm >> 12) & 1) << 31)
        | (((imm >> 5) & 0x3F) << 25)
        | (rs2 << 20)
        | (rs1 << 15)
        | (((imm >> 1) & 0xF) << 8)
        | (((imm >> 11) & 1) << 7)
        | 0x63
    )


def jalr(rd, rs1, imm):
    return (
        ((imm & 0xFFF) << 20)
        | (rs1 << 15)
        | (rd << 7)
        | 0x67
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

    for i in range(64):
        rom[i].value = NOP

    for i, instruction in enumerate(program):
        rom[i].value = instruction

    await Timer(1, unit="ns")
    await tick(dut)

    dut.rst.value = 0
    await Timer(1, unit="ns")


async def run(dut, cycles=30):
    for _ in range(cycles):
        await tick(dut)


def reg(dut, index):
    return int(dut.frontend.regfile.registers[index].value)


def memory_word(dut, address):
    memory = dut.memory_unit.data_mem_unit.memory
    return sum(
        int(memory[address + i].value) << (8 * i)
        for i in range(4)
    )


@cocotb.test()
async def test_ex_mem_forwarding(dut):
    await setup(dut, [
        addi(1, 0, 7),
        addi(2, 1, 5),
        addi(3, 2, 4),
        JAL_SELF,
    ])

    await run(dut)

    assert reg(dut, 1) == 7
    assert reg(dut, 2) == 12
    assert reg(dut, 3) == 16


@cocotb.test()
async def test_mem_wb_forwarding(dut):
    await setup(dut, [
        addi(1, 0, 9),
        NOP,
        addi(2, 1, 3),
        JAL_SELF,
    ])

    await run(dut)

    assert reg(dut, 1) == 9
    assert reg(dut, 2) == 12


@cocotb.test()
async def test_load_use_stall(dut):
    await setup(dut, [
        addi(1, 0, 25),
        sw(1, 0, 0),
        lw(2, 0, 0),
        addi(3, 2, 5),
        JAL_SELF,
    ])

    stalls = 0

    for _ in range(30):
        await Timer(1, unit="ns")

        if int(dut.load_use_stall.value):
            stalls += 1

        await tick(dut)

    assert stalls >= 1, "Expected a load-use stall"
    assert reg(dut, 2) == 25
    assert reg(dut, 3) == 30


@cocotb.test()
async def test_store_data_forwarding(dut):
    await setup(dut, [
        addi(1, 0, 42),
        sw(1, 0, 4),
        lw(2, 0, 4),
        JAL_SELF,
    ])

    await run(dut)

    assert memory_word(dut, 4) == 42
    assert reg(dut, 2) == 42


@cocotb.test()
async def test_taken_branch_flush(dut):
    await setup(dut, [
        addi(1, 0, 5),
        addi(2, 0, 5),
        beq(1, 2, 12),
        addi(3, 0, 99),
        addi(4, 0, 88),
        addi(5, 0, 33),
        JAL_SELF,
    ])

    await run(dut)

    assert reg(dut, 3) == 0
    assert reg(dut, 4) == 0
    assert reg(dut, 5) == 33


@cocotb.test()
async def test_untaken_branch(dut):
    await setup(dut, [
        addi(1, 0, 5),
        addi(2, 0, 6),
        beq(1, 2, 8),
        addi(3, 0, 77),
        JAL_SELF,
    ])

    await run(dut)

    assert reg(dut, 3) == 77


@cocotb.test()
async def test_jalr_link_and_target(dut):
    await setup(dut, [
        addi(1, 0, 16),
        jalr(5, 1, 0),
        addi(2, 0, 99),
        NOP,
        addi(3, 0, 42),
        JAL_SELF,
    ])

    await run(dut)

    assert reg(dut, 5) == 8
    assert reg(dut, 2) == 0
    assert reg(dut, 3) == 42
