
import cocotb
from cocotb.triggers import Timer

NOP = 0x00000013


def addi(rd, rs1, imm):
    return (
        ((imm & 0xFFF) << 20)
        | (rs1 << 15)
        | (rd << 7)
        | 0x13
    )


def add(rd, rs1, rs2):
    return (
        (rs2 << 20)
        | (rs1 << 15)
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
        (((imm >> 5) & 0x7F) << 25)
        | (rs2 << 20)
        | (rs1 << 15)
        | (2 << 12)
        | ((imm & 0x1F) << 7)
        | 0x23
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

    memory = dut.memory_unit.data_mem_unit.memory

    for i in range(64):
        memory[i].value = 0

    await Timer(1, unit="ns")
    await tick(dut)

    dut.rst.value = 0
    await Timer(1, unit="ns")


def reg(dut, index):
    return int(dut.frontend.regfile.registers[index].value)


def metrics(dut):
    return {
        "cycles": int(dut.perf_cycles.value),
        "retired": int(dut.perf_retired.value),
        "load_stalls": int(dut.perf_load_stalls.value),
        "redirects": int(dut.perf_redirects.value),
    }


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


def jal(rd, imm):
    imm &= 0x1FFFFF

    return (
        (((imm >> 20) & 1) << 31)
        | (((imm >> 1) & 0x3FF) << 21)
        | (((imm >> 11) & 1) << 20)
        | (((imm >> 12) & 0xFF) << 12)
        | (rd << 7)
        | 0x6F
    )


async def run_until_retired(dut, expected):
    # Read counters after a complete cycle, then stop
    # once the requested number of instructions retire.
    for _ in range(100):
        await tick(dut)

        result = metrics(dut)

        if result["retired"] >= expected:
            return result

    raise AssertionError("Benchmark did not finish within 100 cycles")


@cocotb.test()
async def test_independent_arithmetic_performance(dut):
    program = [
        addi(1, 0, 5),
        addi(2, 0, 10),
        addi(3, 0, 15),
        addi(4, 0, 20),
        addi(5, 0, 25),
        addi(6, 0, 30),
        addi(7, 0, 35),
        addi(8, 0, 40),
    ]

    await setup(dut, program)

    result = await run_until_retired(dut, len(program))

    assert reg(dut, 1) == 5
    assert reg(dut, 8) == 40

    assert result["retired"] == 8
    assert result["load_stalls"] == 0

    cpi = result["cycles"] / result["retired"]

    dut._log.info(
        "Independent arithmetic: cycles=%d retired=%d CPI=%.3f",
        result["cycles"],
        result["retired"],
        cpi,
    )


@cocotb.test()
async def test_forwarding_performance(dut):
    program = [
        addi(1, 0, 5),
        addi(2, 1, 5),
        addi(3, 2, 5),
        addi(4, 3, 5),
        addi(5, 4, 5),
        addi(6, 5, 5),
        addi(7, 6, 5),
        addi(8, 7, 5),
    ]

    await setup(dut, program)

    result = await run_until_retired(dut, len(program))

    assert reg(dut, 8) == 40
    assert result["retired"] == 8
    assert result["load_stalls"] == 0

    cpi = result["cycles"] / result["retired"]

    dut._log.info(
        "Forwarding benchmark: cycles=%d retired=%d CPI=%.3f",
        result["cycles"],
        result["retired"],
        cpi,
    )


@cocotb.test()
async def test_load_use_performance(dut):
    program = [
        addi(1, 0, 20),
        sw(1, 0, 0),
        lw(2, 0, 0),
        addi(3, 2, 5),
        addi(4, 3, 5),
        addi(5, 4, 5),
        addi(6, 5, 5),
        addi(7, 6, 5),
    ]

    await setup(dut, program)

    result = await run_until_retired(dut, len(program))

    assert reg(dut, 7) == 45
    assert result["retired"] == 8
    assert result["load_stalls"] >= 1

    cpi = result["cycles"] / result["retired"]

    dut._log.info(
        "Load-use benchmark: cycles=%d retired=%d stalls=%d CPI=%.3f",
        result["cycles"],
        result["retired"],
        result["load_stalls"],
        cpi,
    )


@cocotb.test()
async def test_branch_not_taken_performance(dut):
    program = [
        addi(1, 0, 5),
        addi(2, 0, 10),
        beq(1, 2, 8),
        addi(3, 0, 30),
        addi(4, 0, 40),
        addi(5, 0, 50),
        addi(6, 0, 60),
        addi(7, 0, 70),
    ]

    await setup(dut, program)

    result = await run_until_retired(dut, 8)

    assert reg(dut, 3) == 30
    assert reg(dut, 7) == 70
    assert result["retired"] == 8
    assert result["redirects"] == 0
    assert result["load_stalls"] == 0

    dut._log.info(
        "Branch not taken: cycles=%d retired=%d redirects=%d CPI=%.3f",
        result["cycles"],
        result["retired"],
        result["redirects"],
        result["cycles"] / result["retired"],
    )


@cocotb.test()
async def test_branch_taken_performance(dut):
    program = [
        addi(1, 0, 5),
        addi(2, 0, 10),
        beq(1, 1, 8),
        addi(3, 0, 99),  # Must be flushed
        addi(4, 0, 40),
        addi(5, 0, 50),
        addi(6, 0, 60),
        addi(7, 0, 70),
        addi(8, 0, 80),
    ]

    await setup(dut, program)

    result = await run_until_retired(dut, 8)

    assert reg(dut, 3) == 0, "Wrong-path instruction executed"
    assert reg(dut, 4) == 40
    assert reg(dut, 8) == 80
    assert result["retired"] == 8
    assert result["redirects"] == 1
    assert result["load_stalls"] == 0

    dut._log.info(
        "Branch taken: cycles=%d retired=%d redirects=%d CPI=%.3f",
        result["cycles"],
        result["retired"],
        result["redirects"],
        result["cycles"] / result["retired"],
    )


@cocotb.test()
async def test_jump_performance(dut):
    program = [
        addi(1, 0, 5),
        addi(2, 0, 10),
        jal(0, 8),
        addi(3, 0, 99),  # Must be flushed
        addi(4, 0, 40),
        addi(5, 0, 50),
        addi(6, 0, 60),
        addi(7, 0, 70),
        addi(8, 0, 80),
    ]

    await setup(dut, program)

    result = await run_until_retired(dut, 8)

    assert reg(dut, 3) == 0, "Wrong-path instruction executed"
    assert reg(dut, 4) == 40
    assert reg(dut, 8) == 80
    assert result["retired"] == 8
    assert result["redirects"] == 1
    assert result["load_stalls"] == 0

    dut._log.info(
        "JAL performance: cycles=%d retired=%d redirects=%d CPI=%.3f",
        result["cycles"],
        result["retired"],
        result["redirects"],
        result["cycles"] / result["retired"],
    )
