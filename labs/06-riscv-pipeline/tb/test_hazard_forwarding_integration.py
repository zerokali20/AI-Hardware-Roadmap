
import cocotb
from cocotb.triggers import Timer


R_TYPE = 0b0110011
I_TYPE = 0b0010011
LOAD = 0b0000011
STORE = 0b0100011
BRANCH = 0b1100011
JAL = 0b1101111


async def setup(dut, **kwargs):
    values = {
        "if_id_rs1": 0,
        "if_id_rs2": 0,
        "if_id_opcode": R_TYPE,
        "id_ex_rs1": 0,
        "id_ex_rs2": 0,
        "id_ex_rd": 0,
        "id_ex_mem_read": 0,
        "ex_mem_rd": 0,
        "ex_mem_reg_write": 0,
        "ex_mem_mem_to_reg": 0,
        "mem_wb_rd": 0,
        "mem_wb_reg_write": 0,
        "branch_taken_ex": 0,
        "branch_target_ex": 0,
        "invalid_branch_ex": 0,
    }

    values.update(kwargs)

    for name, value in values.items():
        getattr(dut, name).value = value

    await Timer(1, unit="ns")


def check(dut, **expected):
    for name, value in expected.items():
        actual = int(getattr(dut, name).value)
        assert actual == value, (
            f"{name}: expected {value}, got {actual}"
        )


@cocotb.test()
async def test_normal_operation(dut):
    await setup(dut)

    check(
        dut,
        stall_request=0,
        pc_stall=0,
        pc_redirect=0,
        if_id_stall=0,
        id_ex_flush=0,
        forward_a=0,
        forward_b=0,
    )


@cocotb.test()
async def test_load_use_rs1(dut):
    await setup(
        dut,
        id_ex_rd=5,
        id_ex_mem_read=1,
        if_id_rs1=5,
        if_id_opcode=R_TYPE,
    )

    check(
        dut,
        stall_request=1,
        pc_stall=1,
        if_id_stall=1,
        id_ex_stall=0,
        id_ex_flush=1,
    )


@cocotb.test()
async def test_load_use_rs2(dut):
    await setup(
        dut,
        id_ex_rd=7,
        id_ex_mem_read=1,
        if_id_rs1=2,
        if_id_rs2=7,
        if_id_opcode=R_TYPE,
    )

    check(
        dut,
        stall_request=1,
        pc_stall=1,
        if_id_stall=1,
        id_ex_flush=1,
    )


@cocotb.test()
async def test_no_false_immediate_hazard(dut):
    await setup(
        dut,
        id_ex_rd=7,
        id_ex_mem_read=1,
        if_id_rs1=2,
        if_id_rs2=7,
        if_id_opcode=I_TYPE,
    )

    check(
        dut,
        stall_request=0,
        pc_stall=0,
        id_ex_flush=0,
    )


@cocotb.test()
async def test_store_dependency(dut):
    await setup(
        dut,
        id_ex_rd=9,
        id_ex_mem_read=1,
        if_id_rs1=2,
        if_id_rs2=9,
        if_id_opcode=STORE,
    )

    check(
        dut,
        stall_request=1,
        pc_stall=1,
        id_ex_flush=1,
    )


@cocotb.test()
async def test_ex_mem_forwarding(dut):
    await setup(
        dut,
        id_ex_rs1=5,
        id_ex_rs2=6,
        ex_mem_rd=5,
        ex_mem_reg_write=1,
    )

    check(
        dut,
        forward_a=2,
        forward_b=0,
        stall_request=0,
    )


@cocotb.test()
async def test_mem_wb_forwarding(dut):
    await setup(
        dut,
        id_ex_rs1=3,
        id_ex_rs2=4,
        mem_wb_rd=4,
        mem_wb_reg_write=1,
    )

    check(
        dut,
        forward_a=0,
        forward_b=1,
    )


@cocotb.test()
async def test_ex_mem_priority(dut):
    await setup(
        dut,
        id_ex_rs1=5,
        ex_mem_rd=5,
        ex_mem_reg_write=1,
        mem_wb_rd=5,
        mem_wb_reg_write=1,
    )

    check(dut, forward_a=2)


@cocotb.test()
async def test_newer_load_blocks_old_forwarding(dut):
    await setup(
        dut,
        id_ex_rs1=5,
        ex_mem_rd=5,
        ex_mem_reg_write=1,
        ex_mem_mem_to_reg=1,
        mem_wb_rd=5,
        mem_wb_reg_write=1,
    )

    check(dut, forward_a=0)


@cocotb.test()
async def test_zero_register_ignored(dut):
    await setup(
        dut,
        id_ex_rs1=0,
        id_ex_rd=0,
        id_ex_mem_read=1,
        if_id_rs1=0,
        ex_mem_rd=0,
        ex_mem_reg_write=1,
    )

    check(
        dut,
        stall_request=0,
        forward_a=0,
    )


@cocotb.test()
async def test_branch_redirect(dut):
    await setup(
        dut,
        branch_taken_ex=1,
        branch_target_ex=0x100,
    )

    check(
        dut,
        pc_redirect=1,
        pc_target=0x100,
        if_id_flush=1,
        id_ex_flush=1,
        pc_stall=0,
    )


@cocotb.test()
async def test_branch_priority_over_hazard(dut):
    await setup(
        dut,
        id_ex_rd=5,
        id_ex_mem_read=1,
        if_id_rs1=5,
        branch_taken_ex=1,
        branch_target_ex=0x200,
    )

    check(
        dut,
        stall_request=1,
        pc_redirect=1,
        pc_stall=0,
        if_id_flush=1,
        id_ex_flush=1,
    )


@cocotb.test()
async def test_misaligned_branch(dut):
    await setup(
        dut,
        branch_taken_ex=1,
        branch_target_ex=0x102,
    )

    check(
        dut,
        alignment_fault=1,
        pc_redirect=0,
        pc_stall=1,
    )


@cocotb.test()
async def test_stall_clears(dut):
    await setup(
        dut,
        id_ex_rd=5,
        id_ex_mem_read=1,
        if_id_rs1=5,
    )

    check(dut, stall_request=1)

    dut.id_ex_mem_read.value = 0
    await Timer(1, unit="ns")

    check(
        dut,
        stall_request=0,
        pc_stall=0,
        if_id_stall=0,
        id_ex_flush=0,
    )
