
import cocotb
from cocotb.triggers import Timer


FIELDS = (
    "pc",
    "alu_result",
    "mem_read_data",
    "link_address",
    "rd",
    "reg_write",
    "mem_to_reg",
    "jump",
)


def drive(dut, **values):
    for field, value in values.items():
        getattr(dut, f"{field}_in").value = value


def check(dut, **expected):
    for field, expected_value in expected.items():
        actual = int(getattr(dut, f"{field}_out").value)
        assert actual == expected_value, (
            f"{field}: expected {expected_value:#x}, "
            f"got {actual:#x}"
        )


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

    drive(dut, **{field: 0 for field in FIELDS})

    await tick(dut)

    dut.rst.value = 0
    await Timer(1, unit="ns")


@cocotb.test()
async def test_reset(dut):
    await initialize(dut)
    check(dut, **{field: 0 for field in FIELDS})


@cocotb.test()
async def test_alu_result(dut):
    await initialize(dut)

    drive(
        dut,
        pc=0x100,
        alu_result=42,
        rd=5,
        reg_write=1,
    )

    await tick(dut)

    check(
        dut,
        pc=0x100,
        alu_result=42,
        rd=5,
        reg_write=1,
    )


@cocotb.test()
async def test_memory_read_data(dut):
    await initialize(dut)

    drive(
        dut,
        mem_read_data=0xDEADBEEF,
        rd=10,
        reg_write=1,
        mem_to_reg=1,
    )

    await tick(dut)

    check(
        dut,
        mem_read_data=0xDEADBEEF,
        rd=10,
        reg_write=1,
        mem_to_reg=1,
    )


@cocotb.test()
async def test_jump_link(dut):
    await initialize(dut)

    drive(
        dut,
        pc=0x200,
        link_address=0x204,
        rd=1,
        reg_write=1,
        jump=1,
    )

    await tick(dut)

    check(
        dut,
        pc=0x200,
        link_address=0x204,
        rd=1,
        reg_write=1,
        jump=1,
    )


@cocotb.test()
async def test_stall(dut):
    await initialize(dut)

    drive(
        dut,
        alu_result=100,
        rd=3,
        reg_write=1,
    )
    await tick(dut)

    dut.stall.value = 1

    drive(
        dut,
        alu_result=200,
        rd=7,
        reg_write=0,
    )
    await tick(dut)

    check(
        dut,
        alu_result=100,
        rd=3,
        reg_write=1,
    )


@cocotb.test()
async def test_resume_after_stall(dut):
    await initialize(dut)

    dut.stall.value = 1
    drive(dut, alu_result=500)
    await tick(dut)

    check(dut, alu_result=0)

    dut.stall.value = 0
    await tick(dut)

    check(dut, alu_result=500)


@cocotb.test()
async def test_flush(dut):
    await initialize(dut)

    drive(
        dut,
        pc=0x100,
        alu_result=99,
        mem_read_data=88,
        link_address=0x104,
        rd=5,
        reg_write=1,
        mem_to_reg=1,
        jump=1,
    )
    await tick(dut)

    dut.flush.value = 1
    await tick(dut)

    check(dut, **{field: 0 for field in FIELDS})


@cocotb.test()
async def test_flush_priority_over_stall(dut):
    await initialize(dut)

    drive(dut, alu_result=777, reg_write=1)
    await tick(dut)

    dut.stall.value = 1
    dut.flush.value = 1
    await tick(dut)

    check(dut, alu_result=0, reg_write=0)


@cocotb.test()
async def test_multiple_cycles(dut):
    await initialize(dut)

    for i in range(1, 11):
        drive(
            dut,
            pc=i * 4,
            alu_result=i * 100,
            rd=i,
            reg_write=1,
        )

        await tick(dut)

        check(
            dut,
            pc=i * 4,
            alu_result=i * 100,
            rd=i,
            reg_write=1,
        )


@cocotb.test()
async def test_all_fields_capture(dut):
    await initialize(dut)

    values = {
        "pc": 0x100,
        "alu_result": 0x12345678,
        "mem_read_data": 0xABCDEF01,
        "link_address": 0x104,
        "rd": 15,
        "reg_write": 1,
        "mem_to_reg": 1,
        "jump": 1,
    }

    drive(dut, **values)
    await tick(dut)
    check(dut, **values)


@cocotb.test()
async def test_reset_priority(dut):
    await initialize(dut)

    drive(dut, alu_result=123, reg_write=1)
    await tick(dut)

    dut.rst.value = 1
    dut.stall.value = 1
    dut.flush.value = 1

    await tick(dut)

    check(dut, **{field: 0 for field in FIELDS})


@cocotb.test()
async def test_no_write_control(dut):
    await initialize(dut)

    drive(
        dut,
        alu_result=0xCAFEBABE,
        rd=9,
        reg_write=0,
    )

    await tick(dut)

    check(
        dut,
        alu_result=0xCAFEBABE,
        rd=9,
        reg_write=0,
    )
