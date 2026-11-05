
import cocotb
from cocotb.triggers import Timer


async def tick(dut):
    dut.clk.value = 0
    await Timer(5, unit="ns")
    dut.clk.value = 1
    await Timer(5, unit="ns")
    dut.clk.value = 0
    await Timer(1, unit="ns")


def drive(dut, **kwargs):
    for name, value in kwargs.items():
        getattr(dut, name).value = value


def check(dut, **kwargs):
    for name, expected in kwargs.items():
        actual = int(getattr(dut, name).value)
        assert actual == expected, (
            f"{name}: expected {expected:#x}, got {actual:#x}"
        )


async def initialize(dut):
    drive(
        dut,
        clk=0,
        rst=1,
        stall=0,
        flush=0,
        pc_in=0,
        alu_result_in=0,
        mem_read_data_in=0,
        link_address_in=0,
        rd_in=0,
        reg_write_in=0,
        mem_to_reg_in=0,
        jump_in=0,
    )

    await tick(dut)
    dut.rst.value = 0
    await Timer(1, unit="ns")


async def issue(dut, **kwargs):
    drive(
        dut,
        pc_in=0,
        alu_result_in=0,
        mem_read_data_in=0,
        link_address_in=0,
        rd_in=0,
        reg_write_in=0,
        mem_to_reg_in=0,
        jump_in=0,
    )
    drive(dut, **kwargs)
    await tick(dut)


@cocotb.test()
async def test_reset(dut):
    await initialize(dut)

    check(
        dut,
        wb_data=0,
        wb_rd=0,
        wb_reg_write=0,
        wb_pc=0,
    )


@cocotb.test()
async def test_alu_writeback(dut):
    await initialize(dut)

    await issue(
        dut,
        pc_in=0x100,
        alu_result_in=42,
        rd_in=5,
        reg_write_in=1,
    )

    check(
        dut,
        wb_data=42,
        wb_rd=5,
        wb_reg_write=1,
        wb_pc=0x100,
    )


@cocotb.test()
async def test_load_writeback(dut):
    await initialize(dut)

    await issue(
        dut,
        alu_result_in=0x200,
        mem_read_data_in=0xDEADBEEF,
        rd_in=10,
        reg_write_in=1,
        mem_to_reg_in=1,
    )

    check(
        dut,
        wb_data=0xDEADBEEF,
        wb_rd=10,
        wb_reg_write=1,
    )


@cocotb.test()
async def test_jump_writeback(dut):
    await initialize(dut)

    await issue(
        dut,
        pc_in=0x300,
        link_address_in=0x304,
        rd_in=1,
        reg_write_in=1,
        jump_in=1,
    )

    check(
        dut,
        wb_data=0x304,
        wb_rd=1,
        wb_reg_write=1,
    )


@cocotb.test()
async def test_jump_priority(dut):
    await initialize(dut)

    await issue(
        dut,
        alu_result_in=100,
        mem_read_data_in=200,
        link_address_in=300,
        rd_in=1,
        reg_write_in=1,
        mem_to_reg_in=1,
        jump_in=1,
    )

    check(dut, wb_data=300)


@cocotb.test()
async def test_memory_priority_over_alu(dut):
    await initialize(dut)

    await issue(
        dut,
        alu_result_in=100,
        mem_read_data_in=200,
        rd_in=2,
        reg_write_in=1,
        mem_to_reg_in=1,
    )

    check(dut, wb_data=200)


@cocotb.test()
async def test_x0_write_protection(dut):
    await initialize(dut)

    await issue(
        dut,
        alu_result_in=12345,
        rd_in=0,
        reg_write_in=1,
    )

    check(
        dut,
        wb_rd=0,
        wb_reg_write=0,
    )


@cocotb.test()
async def test_reg_write_disabled(dut):
    await initialize(dut)

    await issue(
        dut,
        alu_result_in=999,
        rd_in=7,
        reg_write_in=0,
    )

    check(
        dut,
        wb_data=999,
        wb_rd=7,
        wb_reg_write=0,
    )


@cocotb.test()
async def test_stall_holds_writeback(dut):
    await initialize(dut)

    await issue(
        dut,
        alu_result_in=100,
        rd_in=3,
        reg_write_in=1,
    )

    dut.stall.value = 1
    dut.alu_result_in.value = 500
    dut.rd_in.value = 9

    await tick(dut)

    check(
        dut,
        wb_data=100,
        wb_rd=3,
        wb_reg_write=1,
    )


@cocotb.test()
async def test_flush_disables_writeback(dut):
    await initialize(dut)

    await issue(
        dut,
        alu_result_in=777,
        rd_in=8,
        reg_write_in=1,
    )

    dut.flush.value = 1
    await tick(dut)

    check(
        dut,
        wb_data=0,
        wb_rd=0,
        wb_reg_write=0,
    )


@cocotb.test()
async def test_multiple_writebacks(dut):
    await initialize(dut)

    for i in range(1, 11):
        await issue(
            dut,
            pc_in=i * 4,
            alu_result_in=i * 100,
            rd_in=i,
            reg_write_in=1,
        )

        check(
            dut,
            wb_data=i * 100,
            wb_rd=i,
            wb_reg_write=1,
            wb_pc=i * 4,
        )


@cocotb.test()
async def test_reset_suppresses_writeback(dut):
    await initialize(dut)

    await issue(
        dut,
        alu_result_in=456,
        rd_in=6,
        reg_write_in=1,
    )

    dut.rst.value = 1
    await Timer(1, unit="ns")

    check(dut, wb_reg_write=0)

    await tick(dut)

    check(
        dut,
        wb_data=0,
        wb_rd=0,
        wb_reg_write=0,
    )
