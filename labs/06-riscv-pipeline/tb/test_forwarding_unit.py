
import cocotb
from cocotb.triggers import Timer


async def setup(dut, **kwargs):
    values = {
        "id_ex_rs1": 0,
        "id_ex_rs2": 0,
        "ex_mem_rd": 0,
        "ex_mem_reg_write": 0,
        "ex_mem_mem_to_reg": 0,
        "mem_wb_rd": 0,
        "mem_wb_reg_write": 0,
    }

    values.update(kwargs)

    for name, value in values.items():
        getattr(dut, name).value = value

    await Timer(1, unit="ns")


def check(dut, a, b):
    actual_a = int(dut.forward_a.value)
    actual_b = int(dut.forward_b.value)

    assert actual_a == a, (
        f"forward_a expected {a:02b}, got {actual_a:02b}"
    )
    assert actual_b == b, (
        f"forward_b expected {b:02b}, got {actual_b:02b}"
    )


@cocotb.test()
async def test_no_forwarding(dut):
    await setup(dut, id_ex_rs1=1, id_ex_rs2=2)
    check(dut, 0, 0)


@cocotb.test()
async def test_ex_mem_forward_rs1(dut):
    await setup(
        dut,
        id_ex_rs1=5,
        id_ex_rs2=6,
        ex_mem_rd=5,
        ex_mem_reg_write=1,
    )
    check(dut, 2, 0)


@cocotb.test()
async def test_ex_mem_forward_rs2(dut):
    await setup(
        dut,
        id_ex_rs1=5,
        id_ex_rs2=6,
        ex_mem_rd=6,
        ex_mem_reg_write=1,
    )
    check(dut, 0, 2)


@cocotb.test()
async def test_mem_wb_forward_rs1(dut):
    await setup(
        dut,
        id_ex_rs1=8,
        mem_wb_rd=8,
        mem_wb_reg_write=1,
    )
    check(dut, 1, 0)


@cocotb.test()
async def test_mem_wb_forward_rs2(dut):
    await setup(
        dut,
        id_ex_rs2=9,
        mem_wb_rd=9,
        mem_wb_reg_write=1,
    )
    check(dut, 0, 1)


@cocotb.test()
async def test_both_operands_ex_mem(dut):
    await setup(
        dut,
        id_ex_rs1=4,
        id_ex_rs2=4,
        ex_mem_rd=4,
        ex_mem_reg_write=1,
    )
    check(dut, 2, 2)


@cocotb.test()
async def test_both_operands_mem_wb(dut):
    await setup(
        dut,
        id_ex_rs1=7,
        id_ex_rs2=7,
        mem_wb_rd=7,
        mem_wb_reg_write=1,
    )
    check(dut, 1, 1)


@cocotb.test()
async def test_ex_mem_priority(dut):
    await setup(
        dut,
        id_ex_rs1=5,
        id_ex_rs2=5,
        ex_mem_rd=5,
        ex_mem_reg_write=1,
        mem_wb_rd=5,
        mem_wb_reg_write=1,
    )
    check(dut, 2, 2)


@cocotb.test()
async def test_zero_register_ignored(dut):
    await setup(
        dut,
        id_ex_rs1=0,
        id_ex_rs2=0,
        ex_mem_rd=0,
        ex_mem_reg_write=1,
        mem_wb_rd=0,
        mem_wb_reg_write=1,
    )
    check(dut, 0, 0)


@cocotb.test()
async def test_disabled_register_write(dut):
    await setup(
        dut,
        id_ex_rs1=3,
        id_ex_rs2=4,
        ex_mem_rd=3,
        ex_mem_reg_write=0,
        mem_wb_rd=4,
        mem_wb_reg_write=0,
    )
    check(dut, 0, 0)


@cocotb.test()
async def test_load_not_forwarded_from_ex_mem(dut):
    await setup(
        dut,
        id_ex_rs1=5,
        ex_mem_rd=5,
        ex_mem_reg_write=1,
        ex_mem_mem_to_reg=1,
    )
    check(dut, 0, 0)


@cocotb.test()
async def test_load_with_older_mem_wb_match(dut):
    await setup(
        dut,
        id_ex_rs1=5,
        ex_mem_rd=5,
        ex_mem_reg_write=1,
        ex_mem_mem_to_reg=1,
        mem_wb_rd=5,
        mem_wb_reg_write=1,
    )
    check(dut, 0, 0)


@cocotb.test()
async def test_different_sources(dut):
    await setup(
        dut,
        id_ex_rs1=3,
        id_ex_rs2=4,
        ex_mem_rd=3,
        ex_mem_reg_write=1,
        mem_wb_rd=4,
        mem_wb_reg_write=1,
    )
    check(dut, 2, 1)


@cocotb.test()
async def test_no_register_match(dut):
    await setup(
        dut,
        id_ex_rs1=1,
        id_ex_rs2=2,
        ex_mem_rd=10,
        ex_mem_reg_write=1,
        mem_wb_rd=11,
        mem_wb_reg_write=1,
    )
    check(dut, 0, 0)
