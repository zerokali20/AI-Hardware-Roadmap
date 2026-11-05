
import cocotb
from cocotb.triggers import Timer


NOP = 0x00000013
BRANCH = 0x63
JAL = 0x6F
JALR = 0x67
ADDI = 0x13


async def settle():
    await Timer(1, unit="ns")


async def tick(dut):
    dut.clk.value = 0
    await Timer(5, unit="ns")
    dut.clk.value = 1
    await Timer(5, unit="ns")
    dut.clk.value = 0
    await settle()


def check(dut, **expected):
    for name, value in expected.items():
        actual = int(getattr(dut, name).value)
        assert actual == value, (
            f"{name}: expected {value:#x}, got {actual:#x}"
        )


def set_decode(
    dut,
    opcode=ADDI,
    funct3=0,
    rs1=0,
    rs2=0,
    imm=0,
    rd=0,
    reg_write=0,
    mem_write=0,
):
    dut.decode_opcode.value = opcode
    dut.decode_funct3.value = funct3
    dut.decode_funct7.value = 0
    dut.decode_rs1_data.value = rs1 & 0xFFFFFFFF
    dut.decode_rs2_data.value = rs2 & 0xFFFFFFFF
    dut.decode_immediate.value = imm & 0xFFFFFFFF
    dut.decode_rd.value = rd
    dut.decode_reg_write.value = reg_write
    dut.decode_mem_write.value = mem_write


async def initialize(dut):
    dut.clk.value = 0
    dut.rst.value = 1
    dut.stall_request.value = 0
    dut.fetch_instruction.value = NOP
    set_decode(dut)

    await tick(dut)

    dut.rst.value = 0
    await settle()


async def load_execute(dut, **kwargs):
    # First populate IF/ID with a fetch cycle.
    dut.fetch_instruction.value = NOP
    await tick(dut)

    # Then transfer supplied decode values into ID/EX.
    set_decode(dut, **kwargs)
    await tick(dut)
    await settle()


@cocotb.test()
async def test_reset(dut):
    await initialize(dut)

    check(
        dut,
        fetch_pc=0,
        if_id_instruction=NOP,
        execute_opcode=0,
        pc_redirect=0,
        alignment_fault=0,
    )


@cocotb.test()
async def test_normal_pc_increment(dut):
    await initialize(dut)

    for expected in (4, 8, 12, 16):
        await tick(dut)
        check(dut, fetch_pc=expected)


@cocotb.test()
async def test_if_id_capture(dut):
    await initialize(dut)

    dut.fetch_instruction.value = 0x00500093

    await tick(dut)

    check(
        dut,
        fetch_pc=4,
        if_id_pc=0,
        if_id_instruction=0x00500093,
    )


@cocotb.test()
async def test_hazard_stall(dut):
    await initialize(dut)

    dut.fetch_instruction.value = 0x00500093
    await tick(dut)

    check(dut, fetch_pc=4)

    dut.stall_request.value = 1
    dut.fetch_instruction.value = 0x00A00113

    await settle()
    check(dut, id_ex_flush=1)

    await tick(dut)

    check(
        dut,
        fetch_pc=4,
        if_id_instruction=0x00500093,
        execute_opcode=0,
        execute_reg_write=0,
        execute_mem_write=0,
    )


@cocotb.test()
async def test_beq_redirect_and_flush(dut):
    await initialize(dut)

    await load_execute(
        dut,
        opcode=BRANCH,
        funct3=0,
        rs1=10,
        rs2=10,
        imm=16,
    )

    # Branch was decoded at PC=0.
    check(
        dut,
        execute_pc=0,
        pc_redirect=1,
        pc_target=16,
        if_id_flush=1,
        id_ex_flush=1,
    )

    await tick(dut)

    check(
        dut,
        fetch_pc=16,
        if_id_instruction=NOP,
        execute_opcode=0,
        execute_reg_write=0,
        execute_mem_write=0,
        pc_redirect=0,
    )


@cocotb.test()
async def test_branch_not_taken(dut):
    await initialize(dut)

    await load_execute(
        dut,
        opcode=BRANCH,
        funct3=0,
        rs1=10,
        rs2=20,
        imm=16,
    )

    check(dut, pc_redirect=0)

    await tick(dut)

    check(
        dut,
        fetch_pc=12,
        alignment_fault=0,
    )


@cocotb.test()
async def test_branch_priority_over_stall(dut):
    await initialize(dut)

    await load_execute(
        dut,
        opcode=BRANCH,
        funct3=0,
        rs1=5,
        rs2=5,
        imm=32,
    )

    dut.stall_request.value = 1
    await settle()

    check(
        dut,
        pc_redirect=1,
        pc_target=32,
        if_id_flush=1,
        id_ex_flush=1,
    )

    await tick(dut)

    check(
        dut,
        fetch_pc=32,
        if_id_instruction=NOP,
        execute_opcode=0,
    )


@cocotb.test()
async def test_jal_redirect(dut):
    await initialize(dut)

    await load_execute(
        dut,
        opcode=JAL,
        imm=64,
        rd=1,
        reg_write=1,
    )

    check(
        dut,
        pc_redirect=1,
        pc_target=64,
    )

    await tick(dut)

    check(
        dut,
        fetch_pc=64,
        execute_reg_write=0,
    )


@cocotb.test()
async def test_jalr_redirect(dut):
    await initialize(dut)

    await load_execute(
        dut,
        opcode=JALR,
        funct3=0,
        rs1=0x101,
        imm=8,
        rd=1,
        reg_write=1,
    )

    # (0x101 + 8) with bit zero cleared = 0x108.
    check(
        dut,
        pc_redirect=1,
        pc_target=0x108,
    )

    await tick(dut)
    check(dut, fetch_pc=0x108)


@cocotb.test()
async def test_misaligned_target(dut):
    await initialize(dut)

    await load_execute(
        dut,
        opcode=JAL,
        imm=6,
    )

    check(
        dut,
        alignment_fault=1,
        pc_redirect=0,
        id_ex_flush=1,
    )

    previous_pc = int(dut.fetch_pc.value)

    await tick(dut)

    check(
        dut,
        fetch_pc=previous_pc,
        execute_opcode=0,
        execute_reg_write=0,
    )


@cocotb.test()
async def test_resume_after_stall(dut):
    await initialize(dut)

    dut.stall_request.value = 1
    await tick(dut)

    check(dut, fetch_pc=0)

    dut.stall_request.value = 0
    await settle()
    await tick(dut)

    check(dut, fetch_pc=4)
