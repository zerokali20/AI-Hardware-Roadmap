
import cocotb
from cocotb.triggers import Timer


async def settle():
    await Timer(1, unit="ns")


async def tick(dut):
    dut.clk.value = 0
    await Timer(5, unit="ns")
    dut.clk.value = 1
    await Timer(5, unit="ns")
    dut.clk.value = 0
    await Timer(1, unit="ns")


async def reset(dut):
    dut.clk.value = 0
    dut.rst.value = 1
    dut.stall.value = 0
    dut.branch_taken.value = 0
    dut.branch_target.value = 0
    dut.wb_enable.value = 0
    dut.wb_addr.value = 0
    dut.wb_data.value = 0
    await tick(dut)
    dut.rst.value = 0


@cocotb.test()
async def test_initial_fetch(dut):
    await reset(dut)

    assert int(dut.fetch_pc.value) == 0
    assert int(dut.fetch_instruction.value) == 0x00500093

    # IF/ID contains a NOP immediately after reset
    assert int(dut.decode_instruction.value) == 0x00000013


@cocotb.test()
async def test_instruction_pipeline(dut):
    await reset(dut)

    await tick(dut)

    assert int(dut.decode_pc.value) == 0
    assert int(dut.decode_instruction.value) == 0x00500093
    assert int(dut.rd.value) == 1
    assert int(dut.rs1.value) == 0
    assert int(dut.immediate.value) == 5
    assert int(dut.reg_write.value) == 1

    await tick(dut)

    assert int(dut.decode_pc.value) == 4
    assert int(dut.decode_instruction.value) == 0x00A00113
    assert int(dut.rd.value) == 2
    assert int(dut.immediate.value) == 10


@cocotb.test()
async def test_register_writeback_and_read(dut):
    await reset(dut)

    # Write x1 = 25 using the external writeback interface
    dut.wb_enable.value = 1
    dut.wb_addr.value = 1
    dut.wb_data.value = 25

    await tick(dut)
    dut.wb_enable.value = 0

    # First decoded instruction is addi x1, x0, 5
    assert int(dut.decode_instruction.value) == 0x00500093

    # Move to the second instruction, then the third
    await tick(dut)
    await tick(dut)

    # Third instruction: add x3, x1, x2
    assert int(dut.decode_instruction.value) == 0x002081B3
    assert int(dut.rs1.value) == 1
    assert int(dut.rs2.value) == 2
    assert int(dut.rs1_data.value) == 25
    assert int(dut.rs2_data.value) == 0


@cocotb.test()
async def test_pipeline_stall(dut):
    await reset(dut)
    await tick(dut)

    saved_pc = int(dut.decode_pc.value)
    saved_instruction = int(dut.decode_instruction.value)
    saved_fetch_pc = int(dut.fetch_pc.value)

    dut.stall.value = 1

    for _ in range(3):
        await tick(dut)
        assert int(dut.decode_pc.value) == saved_pc
        assert int(dut.decode_instruction.value) == saved_instruction
        assert int(dut.fetch_pc.value) == saved_fetch_pc


@cocotb.test()
async def test_branch_flush(dut):
    await reset(dut)
    await tick(dut)

    dut.branch_taken.value = 1
    dut.branch_target.value = 0x10
    await tick(dut)

    assert int(dut.fetch_pc.value) == 0x10
    assert int(dut.decode_instruction.value) == 0x00000013

    dut.branch_taken.value = 0
    await tick(dut)

    assert int(dut.decode_pc.value) == 0x10
    assert int(dut.decode_instruction.value) == 0x00002203


@cocotb.test()
async def test_store_decode(dut):
    await reset(dut)

    # Advance until sw x3, 0(x0) reaches decode
    for _ in range(4):
        await tick(dut)

    assert int(dut.decode_instruction.value) == 0x00302023
    assert int(dut.mem_write.value) == 1
    assert int(dut.reg_write.value) == 0
    assert int(dut.rs2.value) == 3
    assert int(dut.immediate.value) == 0
