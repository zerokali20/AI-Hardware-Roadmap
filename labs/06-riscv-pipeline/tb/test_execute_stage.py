
import cocotb
from cocotb.triggers import Timer


FIELDS = {
    "pc": 0,
    "rs1_data": 0,
    "rs2_data": 0,
    "immediate": 0,
    "rd": 0,
    "rs1": 0,
    "rs2": 0,
    "funct3": 0,
    "funct7": 0,
    "opcode": 0,
    "reg_write": 0,
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


async def initialize(dut):
    dut.clk.value = 0
    dut.rst.value = 1
    dut.stall.value = 0
    dut.flush.value = 0

    for name, value in FIELDS.items():
        getattr(dut, f"{name}_in").value = value

    await tick(dut)
    dut.rst.value = 0


async def execute(dut, **changes):
    values = FIELDS.copy()
    values.update(changes)

    for name, value in values.items():
        getattr(dut, f"{name}_in").value = value

    await tick(dut)


@cocotb.test()
async def test_add(dut):
    await initialize(dut)

    await execute(
        dut,
        opcode=0x33,
        funct3=0,
        funct7=0,
        rs1_data=25,
        rs2_data=10,
        rd=3,
        reg_write=1,
    )

    assert int(dut.alu_result.value) == 35
    assert int(dut.execute_rd.value) == 3
    assert int(dut.execute_reg_write.value) == 1


@cocotb.test()
async def test_sub(dut):
    await initialize(dut)

    await execute(
        dut,
        opcode=0x33,
        funct3=0,
        funct7=0x20,
        rs1_data=25,
        rs2_data=10,
        reg_write=1,
    )

    assert int(dut.alu_result.value) == 15


@cocotb.test()
async def test_addi(dut):
    await initialize(dut)

    await execute(
        dut,
        opcode=0x13,
        funct3=0,
        rs1_data=20,
        rs2_data=999,
        immediate=5,
        alu_src=1,
        reg_write=1,
    )

    assert int(dut.alu_result.value) == 25


@cocotb.test()
async def test_and(dut):
    await initialize(dut)

    await execute(
        dut,
        opcode=0x33,
        funct3=7,
        rs1_data=0xFF00,
        rs2_data=0x0FF0,
    )

    assert int(dut.alu_result.value) == 0x0F00


@cocotb.test()
async def test_or(dut):
    await initialize(dut)

    await execute(
        dut,
        opcode=0x33,
        funct3=6,
        rs1_data=0xF000,
        rs2_data=0x00FF,
    )

    assert int(dut.alu_result.value) == 0xF0FF


@cocotb.test()
async def test_slt_signed(dut):
    await initialize(dut)

    await execute(
        dut,
        opcode=0x33,
        funct3=2,
        rs1_data=0xFFFFFFFF,
        rs2_data=1,
    )

    assert int(dut.alu_result.value) == 1


@cocotb.test()
async def test_slt_unsigned(dut):
    await initialize(dut)

    await execute(
        dut,
        opcode=0x33,
        funct3=3,
        rs1_data=0xFFFFFFFF,
        rs2_data=1,
    )

    assert int(dut.alu_result.value) == 0


@cocotb.test()
async def test_load_address(dut):
    await initialize(dut)

    await execute(
        dut,
        opcode=0x03,
        funct3=2,
        rs1_data=0x100,
        immediate=12,
        alu_src=1,
        mem_read=1,
        mem_to_reg=1,
        reg_write=1,
    )

    assert int(dut.alu_result.value) == 0x10C
    assert int(dut.execute_mem_read.value) == 1


@cocotb.test()
async def test_store_address(dut):
    await initialize(dut)

    await execute(
        dut,
        opcode=0x23,
        funct3=2,
        rs1_data=0x200,
        rs2_data=0xDEADBEEF,
        immediate=8,
        alu_src=1,
        mem_write=1,
    )

    assert int(dut.alu_result.value) == 0x208
    assert int(dut.store_data.value) == 0xDEADBEEF
    assert int(dut.execute_mem_write.value) == 1


@cocotb.test()
async def test_stall(dut):
    await initialize(dut)

    await execute(
        dut,
        opcode=0x33,
        rs1_data=10,
        rs2_data=20,
        reg_write=1,
    )

    dut.stall.value = 1

    await execute(
        dut,
        opcode=0x33,
        rs1_data=100,
        rs2_data=200,
        reg_write=1,
    )

    assert int(dut.alu_result.value) == 30


@cocotb.test()
async def test_flush(dut):
    await initialize(dut)

    await execute(
        dut,
        opcode=0x23,
        mem_write=1,
        alu_src=1,
        rs1_data=100,
        immediate=4,
    )

    dut.flush.value = 1
    await tick(dut)

    assert int(dut.execute_mem_write.value) == 0
    assert int(dut.execute_reg_write.value) == 0
    assert int(dut.invalid_operation.value) == 0


@cocotb.test()
async def test_invalid_operation(dut):
    await initialize(dut)

    await execute(
        dut,
        opcode=0x33,
        funct3=0,
        funct7=0x7F,
        reg_write=1,
    )

    assert int(dut.invalid_operation.value) == 1
