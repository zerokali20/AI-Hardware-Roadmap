
import cocotb
from cocotb.triggers import Timer


async def tick(dut):
    dut.clk.value = 0
    await Timer(5, unit="ns")
    dut.clk.value = 1
    await Timer(5, unit="ns")
    dut.clk.value = 0
    await Timer(1, unit="ns")


def drive(dut, **values):
    for name, value in values.items():
        getattr(dut, name).value = value


async def settle():
    await Timer(1, unit="ns")


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
        read_addr1=0,
        read_addr2=0,
    )

    await tick(dut)
    dut.rst.value = 0
    await settle()


async def issue(dut, **values):
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
    drive(dut, **values)
    await tick(dut)


async def commit(dut):
    # Capture a bubble while the previous WB result
    # is committed into the register file.
    await issue(dut)


async def read_register(dut, address):
    dut.read_addr1.value = address
    await settle()
    return int(dut.read_data1.value)


@cocotb.test()
async def test_reset_registers(dut):
    await initialize(dut)

    for reg in range(32):
        assert await read_register(dut, reg) == 0


@cocotb.test()
async def test_alu_writeback(dut):
    await initialize(dut)

    await issue(
        dut,
        alu_result_in=42,
        rd_in=5,
        reg_write_in=1,
    )

    assert int(dut.wb_data.value) == 42
    assert int(dut.wb_rd.value) == 5
    assert int(dut.wb_reg_write.value) == 1

    # Result is not committed until the next edge.
    assert await read_register(dut, 5) == 0

    await commit(dut)
    assert await read_register(dut, 5) == 42


@cocotb.test()
async def test_load_writeback(dut):
    await initialize(dut)

    await issue(
        dut,
        alu_result_in=0x100,
        mem_read_data_in=0xDEADBEEF,
        rd_in=10,
        reg_write_in=1,
        mem_to_reg_in=1,
    )

    await commit(dut)

    assert await read_register(dut, 10) == 0xDEADBEEF


@cocotb.test()
async def test_jump_writeback(dut):
    await initialize(dut)

    await issue(
        dut,
        pc_in=0x200,
        link_address_in=0x204,
        rd_in=1,
        reg_write_in=1,
        jump_in=1,
    )

    await commit(dut)

    assert await read_register(dut, 1) == 0x204


@cocotb.test()
async def test_x0_protection(dut):
    await initialize(dut)

    await issue(
        dut,
        alu_result_in=999,
        rd_in=0,
        reg_write_in=1,
    )

    assert int(dut.wb_reg_write.value) == 0

    await commit(dut)

    assert await read_register(dut, 0) == 0


@cocotb.test()
async def test_write_disabled(dut):
    await initialize(dut)

    await issue(
        dut,
        alu_result_in=123,
        rd_in=7,
        reg_write_in=0,
    )

    await commit(dut)

    assert await read_register(dut, 7) == 0


@cocotb.test()
async def test_consecutive_writes(dut):
    await initialize(dut)

    for i in range(1, 11):
        await issue(
            dut,
            alu_result_in=i * 100,
            rd_in=i,
            reg_write_in=1,
        )

    await commit(dut)

    for i in range(1, 11):
        assert await read_register(dut, i) == i * 100


@cocotb.test()
async def test_two_read_ports(dut):
    await initialize(dut)

    await issue(
        dut,
        alu_result_in=111,
        rd_in=3,
        reg_write_in=1,
    )

    await issue(
        dut,
        alu_result_in=222,
        rd_in=4,
        reg_write_in=1,
    )

    await commit(dut)

    drive(dut, read_addr1=3, read_addr2=4)
    await settle()

    assert int(dut.read_data1.value) == 111
    assert int(dut.read_data2.value) == 222


@cocotb.test()
async def test_overwrite_register(dut):
    await initialize(dut)

    await issue(
        dut,
        alu_result_in=100,
        rd_in=8,
        reg_write_in=1,
    )

    await issue(
        dut,
        alu_result_in=200,
        rd_in=8,
        reg_write_in=1,
    )

    await commit(dut)

    assert await read_register(dut, 8) == 200


@cocotb.test()
async def test_flush_prevents_new_write(dut):
    await initialize(dut)

    # First commit an existing value.
    await issue(
        dut,
        alu_result_in=55,
        rd_in=6,
        reg_write_in=1,
    )
    await commit(dut)

    # Flush a new instruction before it enters MEM/WB.
    drive(
        dut,
        alu_result_in=999,
        rd_in=6,
        reg_write_in=1,
        flush=1,
    )

    await tick(dut)
    dut.flush.value = 0

    await commit(dut)

    assert await read_register(dut, 6) == 55


@cocotb.test()
async def test_stall_holds_pending_writeback(dut):
    await initialize(dut)

    await issue(
        dut,
        alu_result_in=77,
        rd_in=9,
        reg_write_in=1,
    )

    dut.stall.value = 1

    drive(
        dut,
        alu_result_in=999,
        rd_in=10,
        reg_write_in=1,
    )

    await tick(dut)

    assert int(dut.wb_data.value) == 77
    assert int(dut.wb_rd.value) == 9
    assert await read_register(dut, 9) == 77
    assert await read_register(dut, 10) == 0

    dut.stall.value = 0
    await commit(dut)


@cocotb.test()
async def test_reset_clears_written_registers(dut):
    await initialize(dut)

    await issue(
        dut,
        alu_result_in=0xCAFEBABE,
        rd_in=12,
        reg_write_in=1,
    )
    await commit(dut)

    assert await read_register(dut, 12) == 0xCAFEBABE

    dut.rst.value = 1
    await tick(dut)
    dut.rst.value = 0

    assert await read_register(dut, 12) == 0
