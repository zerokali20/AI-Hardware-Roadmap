
import cocotb
from cocotb.triggers import Timer


async def tick(dut):
    dut.clk.value = 0
    await Timer(5, unit="ns")

    dut.clk.value = 1
    await Timer(5, unit="ns")

    dut.clk.value = 0
    await Timer(1, unit="ns")


@cocotb.test()
async def test_reset(dut):
    dut.clk.value = 0
    dut.rst.value = 1
    dut.stall.value = 0
    dut.branch_taken.value = 0
    dut.branch_target.value = 0

    await tick(dut)

    assert int(dut.pc.value) == 0, "PC reset failed"


@cocotb.test()
async def test_sequential_execution(dut):
    dut.rst.value = 1
    dut.stall.value = 0
    dut.branch_taken.value = 0
    dut.branch_target.value = 0

    await tick(dut)

    dut.rst.value = 0

    for i in range(1, 11):
        await tick(dut)

        expected = i * 4
        actual = int(dut.pc.value)

        assert actual == expected, (
            f"Step {i}: expected PC={expected}, got {actual}"
        )


@cocotb.test()
async def test_stall(dut):
    dut.rst.value = 1
    dut.stall.value = 0
    dut.branch_taken.value = 0
    dut.branch_target.value = 0

    await tick(dut)

    dut.rst.value = 0

    await tick(dut)
    await tick(dut)

    previous_pc = int(dut.pc.value)

    dut.stall.value = 1

    for _ in range(3):
        await tick(dut)
        assert int(dut.pc.value) == previous_pc

    dut.stall.value = 0
    await tick(dut)

    assert int(dut.pc.value) == previous_pc + 4


@cocotb.test()
async def test_branch(dut):
    dut.rst.value = 1
    dut.stall.value = 0
    dut.branch_taken.value = 0
    dut.branch_target.value = 0

    await tick(dut)

    dut.rst.value = 0
    dut.branch_taken.value = 1
    dut.branch_target.value = 0x100

    await tick(dut)

    assert int(dut.pc.value) == 0x100

    dut.branch_taken.value = 0
    await tick(dut)

    assert int(dut.pc.value) == 0x104


@cocotb.test()
async def test_reset_priority(dut):
    dut.rst.value = 1
    dut.stall.value = 1
    dut.branch_taken.value = 1
    dut.branch_target.value = 0x200

    await tick(dut)

    assert int(dut.pc.value) == 0



@cocotb.test()
async def test_branch_priority_over_stall(dut):
    dut.clk.value = 0
    dut.rst.value = 1
    dut.stall.value = 0
    dut.branch_taken.value = 0
    dut.branch_target.value = 0

    # Reset the Program Counter.
    dut.clk.value = 0
    await Timer(5, unit="ns")
    dut.clk.value = 1
    await Timer(5, unit="ns")

    assert int(dut.pc.value) == 0

    # Assert branch and stall simultaneously.
    dut.clk.value = 0
    dut.rst.value = 0
    dut.stall.value = 1
    dut.branch_taken.value = 1
    dut.branch_target.value = 0x300

    await Timer(5, unit="ns")
    dut.clk.value = 1
    await Timer(5, unit="ns")

    # Branch redirection must override the stall.
    assert int(dut.pc.value) == 0x300

    # Remove branch request while keeping the stall.
    dut.clk.value = 0
    dut.branch_taken.value = 0

    await Timer(5, unit="ns")
    dut.clk.value = 1
    await Timer(5, unit="ns")

    # PC must remain at the branch target.
    assert int(dut.pc.value) == 0x300

    # Release the stall.
    dut.clk.value = 0
    dut.stall.value = 0

    await Timer(5, unit="ns")
    dut.clk.value = 1
    await Timer(5, unit="ns")

    # Normal sequential execution resumes.
    assert int(dut.pc.value) == 0x304
