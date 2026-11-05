
import cocotb
from cocotb.triggers import Timer


async def clock_cycle(dut):
    dut.clk.value = 0
    await Timer(5, unit="ns")

    dut.clk.value = 1
    await Timer(5, unit="ns")

    dut.clk.value = 0
    await Timer(1, unit="ns")


async def reset_cpu(dut):
    dut.clk.value = 0
    dut.rst.value = 1

    await clock_cycle(dut)

    dut.rst.value = 0
    await Timer(1, unit="ns")


async def run_cycles(dut, count):
    for _ in range(count):
        await clock_cycle(dut)


def read_register(dut, index):
    return int(
        dut.frontend.regfile.registers[index].value
    )


def read_memory_word(dut, address):
    mem = dut.memory_unit.data_mem_unit.memory

    result = 0
    for i in range(4):
        result |= int(mem[address + i].value) << (8 * i)

    return result


@cocotb.test()
async def test_complete_program(dut):
    await reset_cpu(dut)

    redirect_count = 0

    for _ in range(30):
        if int(dut.branch_redirect.value) == 1:
            assert int(dut.control_unit.pc_target.value) == 0x14
            redirect_count += 1

        await clock_cycle(dut)

    assert read_register(dut, 0) == 0
    assert read_register(dut, 1) == 5
    assert read_register(dut, 2) == 10
    assert read_register(dut, 3) == 15
    assert read_memory_word(dut, 0) == 15
    assert read_register(dut, 4) == 15

    assert redirect_count >= 2, (
        f"Expected repeated JAL redirects, got {redirect_count}"
    )

@cocotb.test()
async def test_register_writeback(dut):
    await reset_cpu(dut)

    await run_cycles(dut, 15)

    assert read_register(dut, 1) == 5
    assert read_register(dut, 2) == 10
    assert read_register(dut, 3) == 15
    assert read_register(dut, 4) == 15


@cocotb.test()
async def test_store_and_load(dut):
    await reset_cpu(dut)

    await run_cycles(dut, 20)

    stored_value = read_memory_word(dut, 0)
    loaded_value = read_register(dut, 4)

    assert stored_value == 15, (
        f"Expected stored value 15, got {stored_value}"
    )

    assert loaded_value == stored_value, (
        "Loaded value does not match stored value"
    )


@cocotb.test()
async def test_jal_self_loop(dut):
    await reset_cpu(dut)

    redirects = 0

    for _ in range(35):
        await Timer(1, unit="ns")

        if int(dut.branch_redirect.value) == 1:
            target = int(dut.control_unit.pc_target.value)

            assert target == 0x14, (
                f"Expected JAL target 0x14, got {target:#x}"
            )

            redirects += 1

        await clock_cycle(dut)

    assert redirects >= 3, (
        f"Expected at least 3 JAL redirects, got {redirects}"
    )


@cocotb.test()
async def test_no_memory_errors(dut):
    await reset_cpu(dut)

    for cycle in range(20):
        await clock_cycle(dut)

        assert int(
            dut.memory_alignment_error.value
        ) == 0, (
            f"Alignment error at cycle {cycle}"
        )

        assert int(
            dut.memory_access_error.value
        ) == 0, (
            f"Memory access error at cycle {cycle}"
        )
