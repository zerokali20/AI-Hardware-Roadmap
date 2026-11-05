
import cocotb
from cocotb.triggers import Timer


R_TYPE = 0b0110011
I_TYPE = 0b0010011
LOAD = 0b0000011
STORE = 0b0100011
BRANCH = 0b1100011
JALR = 0b1100111
JAL = 0b1101111
LUI = 0b0110111
AUIPC = 0b0010111


async def check_hazard(
    dut,
    rd=0,
    mem_read=0,
    rs1=0,
    rs2=0,
    opcode=R_TYPE,
    expected=0,
):
    dut.id_ex_rd.value = rd
    dut.id_ex_mem_read.value = mem_read
    dut.if_id_rs1.value = rs1
    dut.if_id_rs2.value = rs2
    dut.if_id_opcode.value = opcode

    await Timer(1, unit="ns")

    actual = int(dut.stall_request.value)

    assert actual == expected, (
        f"Expected stall={expected}, got {actual}, "
        f"rd={rd}, rs1={rs1}, rs2={rs2}, "
        f"opcode={opcode:07b}"
    )


@cocotb.test()
async def test_no_load(dut):
    await check_hazard(
        dut, rd=5, mem_read=0,
        rs1=5, expected=0
    )


@cocotb.test()
async def test_load_rs1_dependency(dut):
    await check_hazard(
        dut, rd=5, mem_read=1,
        rs1=5, expected=1
    )


@cocotb.test()
async def test_load_rs2_dependency(dut):
    await check_hazard(
        dut, rd=5, mem_read=1,
        rs2=5, expected=1
    )


@cocotb.test()
async def test_both_sources_dependency(dut):
    await check_hazard(
        dut, rd=5, mem_read=1,
        rs1=5, rs2=5, expected=1
    )


@cocotb.test()
async def test_no_dependency(dut):
    await check_hazard(
        dut, rd=5, mem_read=1,
        rs1=3, rs2=4, expected=0
    )


@cocotb.test()
async def test_x0_ignored(dut):
    await check_hazard(
        dut, rd=0, mem_read=1,
        rs1=0, rs2=0, expected=0
    )


@cocotb.test()
async def test_immediate_uses_rs1(dut):
    await check_hazard(
        dut, rd=7, mem_read=1,
        rs1=7, opcode=I_TYPE, expected=1
    )


@cocotb.test()
async def test_immediate_ignores_rs2(dut):
    await check_hazard(
        dut, rd=7, mem_read=1,
        rs1=3, rs2=7,
        opcode=I_TYPE, expected=0
    )


@cocotb.test()
async def test_store_data_dependency(dut):
    await check_hazard(
        dut, rd=8, mem_read=1,
        rs1=2, rs2=8,
        opcode=STORE, expected=1
    )


@cocotb.test()
async def test_store_address_dependency(dut):
    await check_hazard(
        dut, rd=8, mem_read=1,
        rs1=8, rs2=2,
        opcode=STORE, expected=1
    )


@cocotb.test()
async def test_branch_dependency(dut):
    await check_hazard(
        dut, rd=9, mem_read=1,
        rs1=9, rs2=3,
        opcode=BRANCH, expected=1
    )


@cocotb.test()
async def test_jalr_dependency(dut):
    await check_hazard(
        dut, rd=10, mem_read=1,
        rs1=10, opcode=JALR, expected=1
    )


@cocotb.test()
async def test_jal_no_source_dependency(dut):
    await check_hazard(
        dut, rd=5, mem_read=1,
        rs1=5, rs2=5,
        opcode=JAL, expected=0
    )


@cocotb.test()
async def test_lui_no_source_dependency(dut):
    await check_hazard(
        dut, rd=5, mem_read=1,
        rs1=5, rs2=5,
        opcode=LUI, expected=0
    )


@cocotb.test()
async def test_auipc_no_source_dependency(dut):
    await check_hazard(
        dut, rd=5, mem_read=1,
        rs1=5, rs2=5,
        opcode=AUIPC, expected=0
    )


@cocotb.test()
async def test_load_followed_by_load(dut):
    await check_hazard(
        dut, rd=4, mem_read=1,
        rs1=4, opcode=LOAD, expected=1
    )


@cocotb.test()
async def test_load_ignores_rs2_field(dut):
    await check_hazard(
        dut, rd=4, mem_read=1,
        rs1=2, rs2=4,
        opcode=LOAD, expected=0
    )


@cocotb.test()
async def test_hazard_clears(dut):
    await check_hazard(
        dut, rd=5, mem_read=1,
        rs1=5, expected=1
    )

    await check_hazard(
        dut, rd=5, mem_read=0,
        rs1=5, expected=0
    )
