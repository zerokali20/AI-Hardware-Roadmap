
import cocotb
from cocotb.triggers import Timer


PROGRAM = [
    0x00500093,
    0x00A00113,
    0x002081B3,
    0x00302023,
    0x00002203,
    0x0000006F,
]


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

    await tick(dut)
    dut.rst.value = 0


@cocotb.test()
async def test_instruction_sequence(dut):
    await reset(dut)

    for index, expected_instruction in enumerate(PROGRAM):
        expected_pc = index * 4

        actual_pc = int(dut.pc.value)
        actual_instruction = int(dut.instruction.value)

        assert actual_pc == expected_pc, (
            f"Expected PC {expected_pc:#x}, got {actual_pc:#x}"
        )

        assert actual_instruction == expected_instruction, (
            f"PC {expected_pc:#x}: expected "
            f"{expected_instruction:#010x}, got "
            f"{actual_instruction:#010x}"
        )

        await tick(dut)


@cocotb.test()
async def test_stall_holds_instruction(dut):
    await reset(dut)

    await tick(dut)
    previous_pc = int(dut.pc.value)
    previous_instruction = int(dut.instruction.value)

    dut.stall.value = 1

    for _ in range(3):
        await tick(dut)

        assert int(dut.pc.value) == previous_pc
        assert int(dut.instruction.value) == previous_instruction


@cocotb.test()
async def test_branch_target(dut):
    await reset(dut)

    dut.branch_taken.value = 1
    dut.branch_target.value = 0x10

    await tick(dut)

    assert int(dut.pc.value) == 0x10
    assert int(dut.instruction.value) == PROGRAM[4]


@cocotb.test()
async def test_invalid_address(dut):
    await reset(dut)

    dut.branch_taken.value = 1
    dut.branch_target.value = 0x1000

    await tick(dut)

    assert int(dut.instruction.value) == 0


@cocotb.test()
async def test_unaligned_address(dut):
    await reset(dut)

    dut.branch_taken.value = 1
    dut.branch_target.value = 0x03

    await tick(dut)

    assert int(dut.instruction.value) == 0


@cocotb.test()
async def test_reset_priority(dut):
    await reset(dut)

    dut.rst.value = 1
    dut.stall.value = 1
    dut.branch_taken.value = 1
    dut.branch_target.value = 0x10

    await tick(dut)

    assert int(dut.pc.value) == 0
    assert int(dut.instruction.value) == PROGRAM[0]
