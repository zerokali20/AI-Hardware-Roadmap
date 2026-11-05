
import cocotb
from cocotb.triggers import Timer


DATA_FIELDS = {
    "pc": 0x100,
    "rs1_data": 25,
    "rs2_data": 10,
    "immediate": 5,
    "rd": 3,
    "rs1": 1,
    "rs2": 2,
    "funct3": 0,
    "funct7": 0,
    "opcode": 0x33,
    "reg_write": 1,
    "mem_read": 0,
    "mem_write": 0,
    "mem_to_reg": 0,
    "alu_src": 0,
    "branch": 0,
    "jump": 0,
}


async def tick(dut):
    dut.clk.value = 0
    await Timer(5, unit="ns")
    dut.clk.value = 1
    await Timer(5, unit="ns")
    dut.clk.value = 0
    await Timer(1, unit="ns")


def set_inputs(dut, values):
    for name, value in values.items():
        getattr(dut, f"{name}_in").value = value


def check_outputs(dut, expected):
    for name, value in expected.items():
        actual = int(getattr(dut, f"{name}_out").value)
        assert actual == value, (
            f"{name}: expected {value}, got {actual}"
        )


async def initialize(dut):
    dut.clk.value = 0
    dut.rst.value = 1
    dut.stall.value = 0
    dut.flush.value = 0

    set_inputs(dut, {name: 0 for name in DATA_FIELDS})
    await tick(dut)
    dut.rst.value = 0


@cocotb.test()
async def test_reset(dut):
    await initialize(dut)
    check_outputs(dut, {name: 0 for name in DATA_FIELDS})


@cocotb.test()
async def test_capture(dut):
    await initialize(dut)
    set_inputs(dut, DATA_FIELDS)
    await tick(dut)
    check_outputs(dut, DATA_FIELDS)


@cocotb.test()
async def test_stall(dut):
    await initialize(dut)

    set_inputs(dut, DATA_FIELDS)
    await tick(dut)

    dut.stall.value = 1
    set_inputs(dut, {name: 0 for name in DATA_FIELDS})

    for _ in range(3):
        await tick(dut)
        check_outputs(dut, DATA_FIELDS)


@cocotb.test()
async def test_flush(dut):
    await initialize(dut)

    set_inputs(dut, DATA_FIELDS)
    await tick(dut)

    dut.flush.value = 1
    await tick(dut)

    check_outputs(dut, {name: 0 for name in DATA_FIELDS})


@cocotb.test()
async def test_flush_priority(dut):
    await initialize(dut)

    set_inputs(dut, DATA_FIELDS)
    await tick(dut)

    dut.stall.value = 1
    dut.flush.value = 1
    await tick(dut)

    check_outputs(dut, {name: 0 for name in DATA_FIELDS})


@cocotb.test()
async def test_resume_after_stall(dut):
    await initialize(dut)

    dut.stall.value = 1
    set_inputs(dut, DATA_FIELDS)
    await tick(dut)

    check_outputs(dut, {name: 0 for name in DATA_FIELDS})

    dut.stall.value = 0
    await tick(dut)

    check_outputs(dut, DATA_FIELDS)


@cocotb.test()
async def test_control_signals(dut):
    await initialize(dut)

    values = DATA_FIELDS.copy()
    values.update({
        "opcode": 0x03,
        "reg_write": 1,
        "mem_read": 1,
        "mem_write": 0,
        "mem_to_reg": 1,
        "alu_src": 1,
    })

    set_inputs(dut, values)
    await tick(dut)

    check_outputs(dut, values)


@cocotb.test()
async def test_store_control(dut):
    await initialize(dut)

    values = DATA_FIELDS.copy()
    values.update({
        "opcode": 0x23,
        "reg_write": 0,
        "mem_read": 0,
        "mem_write": 1,
        "alu_src": 1,
    })

    set_inputs(dut, values)
    await tick(dut)

    check_outputs(dut, values)


@cocotb.test()
async def test_branch_control(dut):
    await initialize(dut)

    values = DATA_FIELDS.copy()
    values.update({
        "opcode": 0x63,
        "reg_write": 0,
        "branch": 1,
    })

    set_inputs(dut, values)
    await tick(dut)

    check_outputs(dut, values)


@cocotb.test()
async def test_jump_control(dut):
    await initialize(dut)

    values = DATA_FIELDS.copy()
    values.update({
        "opcode": 0x6F,
        "jump": 1,
    })

    set_inputs(dut, values)
    await tick(dut)

    check_outputs(dut, values)
