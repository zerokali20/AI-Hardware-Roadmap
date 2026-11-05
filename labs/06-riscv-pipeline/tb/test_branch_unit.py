
import cocotb
from cocotb.triggers import Timer


MASK = 0xFFFFFFFF

BRANCH = 0x63
JAL = 0x6F
JALR = 0x67


async def check(
    dut,
    opcode,
    funct3=0,
    pc=0x100,
    a=0,
    b=0,
    imm=8,
    taken=0,
    target=None,
    invalid=0,
):
    dut.opcode.value = opcode
    dut.funct3.value = funct3
    dut.pc.value = pc & MASK
    dut.rs1_data.value = a & MASK
    dut.rs2_data.value = b & MASK
    dut.immediate.value = imm & MASK

    await Timer(1, unit="ns")

    actual_taken = int(dut.branch_taken.value)
    actual_invalid = int(dut.invalid_branch.value)
    actual_link = int(dut.link_address.value)

    assert actual_taken == taken
    assert actual_invalid == invalid
    assert actual_link == ((pc + 4) & MASK)

    if target is not None:
        actual_target = int(dut.branch_target.value)
        assert actual_target == (target & MASK), (
            f"Expected target {target & MASK:#010x}, "
            f"got {actual_target:#010x}"
        )


@cocotb.test()
async def test_beq_taken(dut):
    await check(
        dut, BRANCH, funct3=0,
        a=10, b=10,
        taken=1, target=0x108
    )


@cocotb.test()
async def test_beq_not_taken(dut):
    await check(
        dut, BRANCH, funct3=0,
        a=10, b=20,
        taken=0, target=0x108
    )


@cocotb.test()
async def test_bne_taken(dut):
    await check(
        dut, BRANCH, funct3=1,
        a=10, b=20,
        taken=1, target=0x108
    )


@cocotb.test()
async def test_bne_not_taken(dut):
    await check(
        dut, BRANCH, funct3=1,
        a=10, b=10,
        taken=0
    )


@cocotb.test()
async def test_blt_signed(dut):
    await check(
        dut, BRANCH, funct3=4,
        a=0xFFFFFFFF, b=1,
        taken=1
    )

    await check(
        dut, BRANCH, funct3=4,
        a=1, b=0xFFFFFFFF,
        taken=0
    )


@cocotb.test()
async def test_bge_signed(dut):
    await check(
        dut, BRANCH, funct3=5,
        a=0xFFFFFFFF, b=1,
        taken=0
    )

    await check(
        dut, BRANCH, funct3=5,
        a=5, b=5,
        taken=1
    )


@cocotb.test()
async def test_bltu_unsigned(dut):
    await check(
        dut, BRANCH, funct3=6,
        a=1, b=0xFFFFFFFF,
        taken=1
    )

    await check(
        dut, BRANCH, funct3=6,
        a=0xFFFFFFFF, b=1,
        taken=0
    )


@cocotb.test()
async def test_bgeu_unsigned(dut):
    await check(
        dut, BRANCH, funct3=7,
        a=0xFFFFFFFF, b=1,
        taken=1
    )

    await check(
        dut, BRANCH, funct3=7,
        a=1, b=0xFFFFFFFF,
        taken=0
    )


@cocotb.test()
async def test_negative_branch_offset(dut):
    await check(
        dut, BRANCH, funct3=0,
        pc=0x100,
        a=7, b=7,
        imm=-4,
        taken=1,
        target=0xFC
    )


@cocotb.test()
async def test_jal(dut):
    await check(
        dut, JAL,
        pc=0x200,
        imm=16,
        taken=1,
        target=0x210
    )


@cocotb.test()
async def test_jalr_alignment(dut):
    await check(
        dut, JALR,
        pc=0x100,
        a=0x201,
        imm=4,
        taken=1,
        target=0x204
    )


@cocotb.test()
async def test_jalr_negative_offset(dut):
    await check(
        dut, JALR,
        pc=0x100,
        a=0x300,
        imm=-8,
        taken=1,
        target=0x2F8
    )


@cocotb.test()
async def test_invalid_branch_funct3(dut):
    await check(
        dut, BRANCH,
        funct3=2,
        taken=0,
        invalid=1
    )


@cocotb.test()
async def test_invalid_jalr_funct3(dut):
    await check(
        dut, JALR,
        funct3=1,
        taken=0,
        invalid=1
    )


@cocotb.test()
async def test_non_branch_instruction(dut):
    await check(
        dut, opcode=0x33,
        taken=0,
        target=0x104
    )


@cocotb.test()
async def test_address_wraparound(dut):
    await check(
        dut, JAL,
        pc=0xFFFFFFFC,
        imm=8,
        taken=1,
        target=0x00000004
    )
