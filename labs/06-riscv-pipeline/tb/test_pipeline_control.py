
import cocotb
from cocotb.triggers import Timer


async def apply(
    dut,
    taken=0,
    target=0x100,
    stall=0,
    invalid=0
):
    dut.branch_taken_ex.value = taken
    dut.branch_target_ex.value = target
    dut.stall_request.value = stall
    dut.invalid_branch_ex.value = invalid

    await Timer(1, unit="ns")


def check(dut, **expected):
    for name, value in expected.items():
        actual = int(getattr(dut, name).value)
        assert actual == value, (
            f"{name}: expected {value}, got {actual}"
        )


@cocotb.test()
async def test_normal_operation(dut):
    await apply(dut)

    check(
        dut,
        pc_stall=0,
        pc_redirect=0,
        if_id_stall=0,
        if_id_flush=0,
        id_ex_stall=0,
        id_ex_flush=0,
        alignment_fault=0,
    )


@cocotb.test()
async def test_stall_request(dut):
    await apply(dut, stall=1)

    check(
        dut,
        pc_stall=1,
        pc_redirect=0,
        if_id_stall=1,
        if_id_flush=0,
        id_ex_stall=0,
        id_ex_flush=1,
    )


@cocotb.test()
async def test_branch_redirect(dut):
    await apply(dut, taken=1, target=0x200)

    check(
        dut,
        pc_redirect=1,
        pc_stall=0,
        pc_target=0x200,
        if_id_flush=1,
        id_ex_flush=1,
    )


@cocotb.test()
async def test_branch_priority_over_stall(dut):
    await apply(
        dut,
        taken=1,
        target=0x300,
        stall=1,
    )

    check(
        dut,
        pc_redirect=1,
        pc_stall=0,
        if_id_stall=0,
        if_id_flush=1,
        id_ex_stall=0,
        id_ex_flush=1,
    )


@cocotb.test()
async def test_invalid_branch(dut):
    await apply(
        dut,
        taken=1,
        target=0x400,
        invalid=1,
    )

    check(
        dut,
        pc_redirect=0,
        if_id_flush=0,
        id_ex_flush=0,
    )


@cocotb.test()
async def test_misaligned_target(dut):
    await apply(
        dut,
        taken=1,
        target=0x102,
    )

    check(
        dut,
        alignment_fault=1,
        pc_redirect=0,
        pc_stall=1,
        if_id_stall=1,
        id_ex_flush=1,
    )


@cocotb.test()
async def test_aligned_target(dut):
    await apply(
        dut,
        taken=1,
        target=0x104,
    )

    check(
        dut,
        alignment_fault=0,
        pc_redirect=1,
        pc_target=0x104,
    )


@cocotb.test()
async def test_misalignment_priority(dut):
    await apply(
        dut,
        taken=1,
        target=0x102,
        stall=1,
    )

    check(
        dut,
        alignment_fault=1,
        pc_redirect=0,
        pc_stall=1,
        if_id_stall=1,
        id_ex_flush=1,
    )


@cocotb.test()
async def test_no_fault_when_not_taken(dut):
    await apply(
        dut,
        taken=0,
        target=0x102,
    )

    check(
        dut,
        alignment_fault=0,
        pc_redirect=0,
        pc_stall=0,
    )


@cocotb.test()
async def test_target_passthrough(dut):
    await apply(
        dut,
        taken=1,
        target=0xFFFFFFFC,
    )

    check(
        dut,
        pc_redirect=1,
        pc_target=0xFFFFFFFC,
        alignment_fault=0,
    )
