
import cocotb
from cocotb.triggers import Timer

NOP = 0x00000013
MASK32 = 0xFFFFFFFF


def addi(rd, rs1, imm):
    return (
        ((imm & 0xFFF) << 20)
        | (rs1 << 15)
        | (rd << 7)
        | 0x13
    )


def lui(rd, imm20):
    return (
        ((imm20 & 0xFFFFF) << 12)
        | (rd << 7)
        | 0x37
    )


def load(rd, rs1, imm, funct3):
    return (
        ((imm & 0xFFF) << 20)
        | (rs1 << 15)
        | (funct3 << 12)
        | (rd << 7)
        | 0x03
    )


def store(rs2, rs1, imm, funct3):
    imm &= 0xFFF
    return (
        (((imm >> 5) & 0x7F) << 25)
        | (rs2 << 20)
        | (rs1 << 15)
        | (funct3 << 12)
        | ((imm & 0x1F) << 7)
        | 0x23
    )


def branch(rs1, rs2, imm, funct3):
    assert imm % 2 == 0
    assert -4096 <= imm <= 4094

    imm &= 0x1FFF

    return (
        (((imm >> 12) & 1) << 31)
        | (((imm >> 5) & 0x3F) << 25)
        | (rs2 << 20)
        | (rs1 << 15)
        | (funct3 << 12)
        | (((imm >> 1) & 0xF) << 8)
        | (((imm >> 11) & 1) << 7)
        | 0x63
    )


def jal(rd, imm):
    assert imm % 2 == 0

    imm &= 0x1FFFFF

    return (
        (((imm >> 20) & 1) << 31)
        | (((imm >> 1) & 0x3FF) << 21)
        | (((imm >> 11) & 1) << 20)
        | (((imm >> 12) & 0xFF) << 12)
        | (rd << 7)
        | 0x6F
    )


def stop():
    return jal(0, 0)


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

    # Data memory does not reset its byte array.
    # Clear the locations used by these tests.
    memory = dut.memory_unit.data_mem_unit.memory

    for i in range(64):
        memory[i].value = 0

    await Timer(1, unit="ns")
    await tick(dut)

    dut.rst.value = 0
    await Timer(1, unit="ns")


async def run(dut, cycles=35):
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
async def test_byte_store_load(dut):
    await setup(dut, [
        addi(1, 0, 127),
        store(1, 0, 0, 0),  # SB
        load(2, 0, 0, 0),   # LB
        load(3, 0, 0, 4),   # LBU
        stop(),
    ])

    await run(dut)

    assert reg(dut, 2) == 127
    assert reg(dut, 3) == 127
    assert memory_word(dut, 0) == 127


@cocotb.test()
async def test_signed_byte_extension(dut):
    await setup(dut, [
        addi(1, 0, -1),
        store(1, 0, 1, 0),
        load(2, 0, 1, 0),
        load(3, 0, 1, 4),
        stop(),
    ])

    await run(dut)

    assert reg(dut, 2) == 0xFFFFFFFF
    assert reg(dut, 3) == 0x000000FF


@cocotb.test()
async def test_halfword_store_load(dut):
    await setup(dut, [
        lui(1, 0x00008),
        addi(1, 1, 0x123),
        store(1, 0, 4, 1),  # SH
        load(2, 0, 4, 1),   # LH
        load(3, 0, 4, 5),   # LHU
        stop(),
    ])

    await run(dut)

    assert reg(dut, 2) == 0xFFFF8123
    assert reg(dut, 3) == 0x00008123


@cocotb.test()
async def test_word_store_load(dut):
    await setup(dut, [
        lui(1, 0x12345),
        addi(1, 1, 0x678),
        store(1, 0, 8, 2),
        load(2, 0, 8, 2),
        stop(),
    ])

    await run(dut)

    assert reg(dut, 2) == 0x12345678
    assert memory_word(dut, 8) == 0x12345678


@cocotb.test()
async def test_partial_store_preserves_other_bytes(dut):
    await setup(dut, [
        lui(1, 0x11223),
        addi(1, 1, 0x344),
        store(1, 0, 12, 2),
        addi(2, 0, 0x55),
        store(2, 0, 13, 0),
        load(3, 0, 12, 2),
        stop(),
    ])

    await run(dut)

    assert reg(dut, 3) == 0x11225544


@cocotb.test()
async def test_signed_blt(dut):
    await setup(dut, [
        addi(1, 0, -1),
        addi(2, 0, 1),
        branch(1, 2, 8, 4),  # BLT
        addi(3, 0, 99),
        addi(4, 0, 42),
        stop(),
    ])

    await run(dut)

    assert reg(dut, 3) == 0
    assert reg(dut, 4) == 42


@cocotb.test()
async def test_signed_bge(dut):
    await setup(dut, [
        addi(1, 0, 5),
        addi(2, 0, -1),
        branch(1, 2, 8, 5),  # BGE
        addi(3, 0, 99),
        addi(4, 0, 42),
        stop(),
    ])

    await run(dut)

    assert reg(dut, 3) == 0
    assert reg(dut, 4) == 42


@cocotb.test()
async def test_unsigned_bltu(dut):
    await setup(dut, [
        addi(1, 0, 1),
        addi(2, 0, -1),
        branch(1, 2, 8, 6),  # BLTU
        addi(3, 0, 99),
        addi(4, 0, 42),
        stop(),
    ])

    await run(dut)

    assert reg(dut, 3) == 0
    assert reg(dut, 4) == 42


@cocotb.test()
async def test_unsigned_bgeu(dut):
    await setup(dut, [
        addi(1, 0, -1),
        addi(2, 0, 1),
        branch(1, 2, 8, 7),  # BGEU
        addi(3, 0, 99),
        addi(4, 0, 42),
        stop(),
    ])

    await run(dut)

    assert reg(dut, 3) == 0
    assert reg(dut, 4) == 42


@cocotb.test()
async def test_bne_taken(dut):
    await setup(dut, [
        addi(1, 0, 3),
        addi(2, 0, 4),
        branch(1, 2, 8, 1),  # BNE
        addi(3, 0, 99),
        addi(4, 0, 42),
        stop(),
    ])

    await run(dut)

    assert reg(dut, 3) == 0
    assert reg(dut, 4) == 42


@cocotb.test()
async def test_bne_not_taken(dut):
    await setup(dut, [
        addi(1, 0, 3),
        addi(2, 0, 3),
        branch(1, 2, 8, 1),
        addi(3, 0, 77),
        stop(),
    ])

    await run(dut)

    assert reg(dut, 3) == 77


@cocotb.test()
async def test_backward_branch(dut):
    await setup(dut, [
        addi(1, 0, 0),
        addi(2, 0, 3),
        addi(1, 1, 1),
        branch(1, 2, -4, 1),  # BNE backwards
        addi(3, 1, 0),
        stop(),
    ])

    await run(dut, 45)

    assert reg(dut, 1) == 3
    assert reg(dut, 3) == 3


@cocotb.test()
async def test_misaligned_word_load(dut):
    await setup(dut, [
        load(1, 0, 1, 2),
        stop(),
    ])

    detected = False

    for _ in range(15):
        await Timer(1, unit="ns")

        if int(dut.memory_alignment_error.value):
            detected = True

        await tick(dut)

    assert detected, "Expected misaligned load error"


@cocotb.test()
async def test_misaligned_halfword_store(dut):
    await setup(dut, [
        addi(1, 0, 55),
        store(1, 0, 3, 1),
        stop(),
    ])

    detected = False

    for _ in range(15):
        await Timer(1, unit="ns")

        if int(dut.memory_alignment_error.value):
            detected = True

        await tick(dut)

    assert detected, "Expected misaligned store error"
    assert memory_word(dut, 0) == 0


@cocotb.test()
async def test_memory_out_of_bounds(dut):
    await setup(dut, [
        lui(1, 0x00001),
        load(2, 1, 0, 2),
        stop(),
    ])

    detected = False

    for _ in range(15):
        await Timer(1, unit="ns")

        if int(dut.memory_access_error.value):
            detected = True

        await tick(dut)

    assert detected, "Expected out-of-bounds access error"
