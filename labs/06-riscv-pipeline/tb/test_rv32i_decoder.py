
import cocotb
from cocotb.triggers import Timer


async def decode(dut, instruction):
    dut.instruction.value = instruction
    await Timer(1, unit="ns")


def check(dut, **expected):
    for signal, value in expected.items():
        actual = int(getattr(dut, signal).value)
        assert actual == value, (
            f"{signal}: expected {value}, got {actual}"
        )


@cocotb.test()
async def test_addi(dut):
    # addi x1, x0, 5
    await decode(dut, 0x00500093)

    check(
        dut,
        opcode=0x13,
        rd=1,
        rs1=0,
        reg_write=1,
        alu_src=1,
        mem_read=0,
        mem_write=0,
        illegal_instruction=0,
    )


@cocotb.test()
async def test_add(dut):
    # add x3, x1, x2
    await decode(dut, 0x002081B3)

    check(
        dut,
        opcode=0x33,
        rd=3,
        rs1=1,
        rs2=2,
        funct3=0,
        reg_write=1,
        alu_src=0,
        illegal_instruction=0,
    )


@cocotb.test()
async def test_store(dut):
    # sw x3, 0(x0)
    await decode(dut, 0x00302023)

    check(
        dut,
        opcode=0x23,
        rs1=0,
        rs2=3,
        mem_write=1,
        reg_write=0,
        alu_src=1,
    )


@cocotb.test()
async def test_load(dut):
    # lw x4, 0(x0)
    await decode(dut, 0x00002203)

    check(
        dut,
        opcode=0x03,
        rd=4,
        rs1=0,
        mem_read=1,
        mem_to_reg=1,
        reg_write=1,
    )


@cocotb.test()
async def test_jump(dut):
    # jal x0, 0
    await decode(dut, 0x0000006F)

    check(
        dut,
        opcode=0x6F,
        rd=0,
        jump=1,
        reg_write=1,
        branch=0,
    )


@cocotb.test()
async def test_illegal_opcode(dut):
    await decode(dut, 0xFFFFFFFF)

    check(
        dut,
        illegal_instruction=1,
        reg_write=0,
        mem_read=0,
        mem_write=0,
        branch=0,
        jump=0,
    )


@cocotb.test()
async def test_branch(dut):
    # beq x1, x2, +8
    await decode(dut, 0x00208463)

    check(
        dut,
        opcode=0x63,
        rs1=1,
        rs2=2,
        branch=1,
        reg_write=0,
        jump=0,
    )


@cocotb.test()
async def test_nop(dut):
    # addi x0, x0, 0
    await decode(dut, 0x00000013)

    check(
        dut,
        opcode=0x13,
        rd=0,
        rs1=0,
        reg_write=1,
        alu_src=1,
        illegal_instruction=0,
    )
