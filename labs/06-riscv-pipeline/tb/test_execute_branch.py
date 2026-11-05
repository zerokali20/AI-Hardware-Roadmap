

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
async def test_beq_taken(dut):
    await initialize(dut)

    await execute(
        dut,
        pc=0x100,
        opcode=0x63,
        funct3=0,
        rs1_data=10,
        rs2_data=10,
        immediate=16,
        branch=1,
    )

    assert int(dut.branch_taken.value) == 1
    assert int(dut.branch_target.value) == 0x110
    assert int(dut.execute_pc.value) == 0x100


@cocotb.test()
async def test_beq_not_taken(dut):
    await initialize(dut)

    await execute(
        dut,
        pc=0x100,
        opcode=0x63,
        funct3=0,
        rs1_data=10,
        rs2_data=20,
        immediate=16,
        branch=1,
    )

    assert int(dut.branch_taken.value) == 0


@cocotb.test()
async def test_blt_signed(dut):
    await initialize(dut)

    await execute(
        dut,
        pc=0x200,
        opcode=0x63,
        funct3=4,
        rs1_data=0xFFFFFFFF,
        rs2_data=5,
        immediate=8,
        branch=1,
    )

    assert int(dut.branch_taken.value) == 1
    assert int(dut.branch_target.value) == 0x208


@cocotb.test()
async def test_jal(dut):
    await initialize(dut)

    await execute(
        dut,
        pc=0x300,
        opcode=0x6F,
        immediate=32,
        jump=1,
        reg_write=1,
        rd=1,
    )

    assert int(dut.branch_taken.value) == 1
    assert int(dut.branch_target.value) == 0x320
    assert int(dut.link_address.value) == 0x304
    assert int(dut.execute_rd.value) == 1


@cocotb.test()
async def test_jalr(dut):
    await initialize(dut)

    await execute(
        dut,
        pc=0x400,
        opcode=0x67,
        funct3=0,
        rs1_data=0x501,
        immediate=8,
        jump=1,
        reg_write=1,
        rd=5,
    )

    assert int(dut.branch_taken.value) == 1
    assert int(dut.branch_target.value) == 0x508
    assert int(dut.link_address.value) == 0x404


@cocotb.test()
async def test_flush_branch(dut):
    await initialize(dut)

    await execute(
        dut,
        pc=0x100,
        opcode=0x63,
        funct3=0,
        rs1_data=10,
        rs2_data=10,
        immediate=16,
        branch=1,
    )

    assert int(dut.branch_taken.value) == 1

    dut.flush.value = 1
    await tick(dut)

    assert int(dut.branch_taken.value) == 0
    assert int(dut.execute_reg_write.value) == 0
    assert int(dut.execute_mem_write.value) == 0


@cocotb.test()
async def test_invalid_branch(dut):
    await initialize(dut)

    await execute(
        dut,
        pc=0x100,
        opcode=0x63,
        funct3=2,
        branch=1,
    )

    assert int(dut.invalid_branch.value) == 1
    assert int(dut.branch_taken.value) == 0


@cocotb.test()
async def test_normal_alu_instruction(dut):
    await initialize(dut)

    await execute(
        dut,
        pc=0x100,
        opcode=0x33,
        funct3=0,
        funct7=0,
        rs1_data=20,
        rs2_data=15,
        reg_write=1,
    )

    assert int(dut.alu_result.value) == 35
    assert int(dut.branch_taken.value) == 0
    assert int(dut.invalid_branch.value) == 0
