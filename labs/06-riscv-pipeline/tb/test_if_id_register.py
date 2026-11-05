
import cocotb
from cocotb.triggers import Timer


async def tick(dut):
    dut.clk.value = 0
    await Timer(5, unit="ns")
    dut.clk.value = 1
    await Timer(5, unit="ns")
    dut.clk.value = 0
    await Timer(1, unit="ns")


async def initialize(dut):
    dut.clk.value = 0
    dut.rst.value = 1
    dut.stall.value = 0
    dut.flush.value = 0
    dut.pc_in.value = 0
    dut.instruction_in.value = 0
    await tick(dut)
    dut.rst.value = 0


@cocotb.test()
async def test_reset(dut):
    await initialize(dut)
    assert int(dut.pc_out.value) == 0
    assert int(dut.instruction_out.value) == 0x00000013


@cocotb.test()
async def test_capture(dut):
    await initialize(dut)

    dut.pc_in.value = 0x100
    dut.instruction_in.value = 0x00500093
    await tick(dut)

    assert int(dut.pc_out.value) == 0x100
    assert int(dut.instruction_out.value) == 0x00500093


@cocotb.test()
async def test_stall(dut):
    await initialize(dut)

    dut.pc_in.value = 0x100
    dut.instruction_in.value = 0x00500093
    await tick(dut)

    dut.stall.value = 1
    dut.pc_in.value = 0x104
    dut.instruction_in.value = 0x00A00113

    for _ in range(3):
        await tick(dut)
        assert int(dut.pc_out.value) == 0x100
        assert int(dut.instruction_out.value) == 0x00500093


@cocotb.test()
async def test_flush(dut):
    await initialize(dut)

    dut.pc_in.value = 0x100
    dut.instruction_in.value = 0x00500093
    await tick(dut)

    dut.flush.value = 1
    await tick(dut)

    assert int(dut.pc_out.value) == 0
    assert int(dut.instruction_out.value) == 0x00000013


@cocotb.test()
async def test_flush_priority(dut):
    await initialize(dut)

    dut.stall.value = 1
    dut.flush.value = 1
    dut.pc_in.value = 0x100
    dut.instruction_in.value = 0x00500093

    await tick(dut)

    assert int(dut.pc_out.value) == 0
    assert int(dut.instruction_out.value) == 0x00000013


@cocotb.test()
async def test_resume_after_stall(dut):
    await initialize(dut)

    dut.stall.value = 1
    dut.pc_in.value = 0x100
    dut.instruction_in.value = 0x00500093
    await tick(dut)

    dut.stall.value = 0
    await tick(dut)

    assert int(dut.pc_out.value) == 0x100
    assert int(dut.instruction_out.value) == 0x00500093
