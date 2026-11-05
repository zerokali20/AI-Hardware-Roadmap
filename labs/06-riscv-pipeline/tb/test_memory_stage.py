
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
        store_data_in=0,
        link_address_in=0,
        rd_in=0,
        funct3_in=0,
        reg_write_in=0,
        mem_read_in=0,
        mem_write_in=0,
        mem_to_reg_in=0,
        jump_in=0,
    )

    await tick(dut)
    dut.rst.value = 0


async def issue(dut, **kwargs):
    drive(
        dut,
        pc_in=0,
        alu_result_in=0,
        store_data_in=0,
        link_address_in=0,
        rd_in=0,
        funct3_in=0,
        reg_write_in=0,
        mem_read_in=0,
        mem_write_in=0,
        mem_to_reg_in=0,
        jump_in=0,
    )
    drive(dut, **kwargs)
    await tick(dut)


async def store_word(dut, address, value):
    await issue(
        dut,
        alu_result_in=address,
        store_data_in=value,
        funct3_in=0b010,
        mem_write_in=1,
    )
    # Store commits at the following rising edge.
    await issue(dut)


@cocotb.test()
async def test_reset(dut):
    await initialize(dut)

    check(
        dut,
        mem_pc=0,
        mem_alu_result=0,
        mem_rd=0,
        mem_reg_write=0,
        mem_mem_to_reg=0,
        mem_jump=0,
    )


@cocotb.test()
async def test_alu_result_forwarding(dut):
    await initialize(dut)

    await issue(
        dut,
        pc_in=0x100,
        alu_result_in=12345,
        rd_in=7,
        reg_write_in=1,
    )

    check(
        dut,
        mem_pc=0x100,
        mem_alu_result=12345,
        mem_rd=7,
        mem_reg_write=1,
    )


@cocotb.test()
async def test_word_store_and_load(dut):
    await initialize(dut)

    await store_word(dut, 128, 0x12345678)

    await issue(
        dut,
        alu_result_in=128,
        funct3_in=0b010,
        mem_read_in=1,
        mem_to_reg_in=1,
        reg_write_in=1,
        rd_in=5,
    )

    check(
        dut,
        mem_read_data=0x12345678,
        mem_rd=5,
        mem_mem_to_reg=1,
        mem_reg_write=1,
    )


@cocotb.test()
async def test_byte_store_and_unsigned_load(dut):
    await initialize(dut)

    await issue(
        dut,
        alu_result_in=144,
        store_data_in=0xAB,
        funct3_in=0b000,
        mem_write_in=1,
    )
    await issue(dut)

    await issue(
        dut,
        alu_result_in=144,
        funct3_in=0b100,
        mem_read_in=1,
    )

    check(dut, mem_read_data=0xAB)


@cocotb.test()
async def test_signed_byte_load(dut):
    await initialize(dut)

    await issue(
        dut,
        alu_result_in=160,
        store_data_in=0x80,
        funct3_in=0b000,
        mem_write_in=1,
    )
    await issue(dut)

    await issue(
        dut,
        alu_result_in=160,
        funct3_in=0b000,
        mem_read_in=1,
    )

    check(dut, mem_read_data=0xFFFFFF80)


@cocotb.test()
async def test_halfword_store_load(dut):
    await initialize(dut)

    await issue(
        dut,
        alu_result_in=176,
        store_data_in=0xBEEF,
        funct3_in=0b001,
        mem_write_in=1,
    )
    await issue(dut)

    await issue(
        dut,
        alu_result_in=176,
        funct3_in=0b101,
        mem_read_in=1,
    )

    check(dut, mem_read_data=0xBEEF)


@cocotb.test()
async def test_jump_link_forwarding(dut):
    await initialize(dut)

    await issue(
        dut,
        pc_in=0x200,
        link_address_in=0x204,
        rd_in=1,
        reg_write_in=1,
        jump_in=1,
    )

    check(
        dut,
        mem_pc=0x200,
        mem_link_address=0x204,
        mem_rd=1,
        mem_jump=1,
        mem_reg_write=1,
    )


@cocotb.test()
async def test_stall_holds_ex_mem(dut):
    await initialize(dut)

    await issue(
        dut,
        alu_result_in=99,
        rd_in=3,
        reg_write_in=1,
    )

    dut.stall.value = 1
    dut.alu_result_in.value = 500
    dut.rd_in.value = 9

    await tick(dut)

    check(
        dut,
        mem_alu_result=99,
        mem_rd=3,
        mem_reg_write=1,
    )


@cocotb.test()
async def test_flush_clears_ex_mem(dut):
    await initialize(dut)

    await issue(
        dut,
        alu_result_in=300,
        rd_in=10,
        reg_write_in=1,
    )

    dut.flush.value = 1
    await tick(dut)

    check(
        dut,
        mem_alu_result=0,
        mem_rd=0,
        mem_reg_write=0,
    )


@cocotb.test()
async def test_misaligned_load(dut):
    await initialize(dut)

    await issue(
        dut,
        alu_result_in=3,
        funct3_in=0b010,
        mem_read_in=1,
    )

    check(
        dut,
        alignment_error=1,
        mem_read_data=0,
    )
