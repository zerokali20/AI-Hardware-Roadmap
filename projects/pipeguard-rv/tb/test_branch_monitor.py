"""Unit tests for rtl/monitors/branch_monitor.sv (M1)."""
import cocotb
from cocotb.triggers import Timer

FC_NONE = 0
FC_PC_MISALIGNED = 1
FC_PC_OUT_OF_BOUNDS = 2
FC_PC_TRANSITION = 3
FC_REDIRECT_TARGET = 4
FC_REDIRECT_SPURIOUS = 5


async def tick(dut):
    dut.clk.value = 0
    await Timer(5, unit="ns")
    dut.clk.value = 1
    await Timer(5, unit="ns")
    dut.clk.value = 0
    await Timer(1, unit="ns")


def clear_inputs(dut):
    dut.fetch_pc.value = 0
    dut.branch_redirect.value = 0
    dut.pc_target.value = 0
    dut.branch_taken.value = 0
    dut.branch_target.value = 0
    dut.invalid_branch.value = 0
    dut.alignment_fault.value = 0


async def reset_dut(dut):
    dut.rst.value = 1
    clear_inputs(dut)
    await Timer(1, unit="ns")
    await tick(dut)
    dut.rst.value = 0
    await Timer(1, unit="ns")


@cocotb.test()
async def test_valid_seq_branch_and_hold(dut):
    """Sequential +4, valid taken branch redirect, and conservative PC hold never alarm."""
    await reset_dut(dut)
    # Cycle 0: PC=0 -> next 4
    for pc in (0x000, 0x004, 0x008):
        dut.fetch_pc.value = pc
        await Timer(1, unit="ns")
        assert int(dut.fault_detected.value) == 0
        await tick(dut)

    # Taken branch at 0x00C -> target 0x040
    dut.fetch_pc.value = 0x00C
    dut.branch_taken.value = 1
    dut.branch_target.value = 0x040
    dut.branch_redirect.value = 1
    dut.pc_target.value = 0x040
    await Timer(1, unit="ns")
    assert int(dut.fault_detected.value) == 0
    await tick(dut)

    # Next cycle: PC=0x040, redirect cleared
    clear_inputs(dut)
    dut.fetch_pc.value = 0x040
    await Timer(1, unit="ns")
    assert int(dut.fault_detected.value) == 0
    await tick(dut)

    # Conservative hold (PC stays 0x040 without redirect) -> accepted by M1
    dut.fetch_pc.value = 0x040
    await Timer(1, unit="ns")
    assert int(dut.fault_detected.value) == 0
    await tick(dut)
    assert int(dut.fault_sticky.value) == 0


@cocotb.test()
async def test_aligned_in_range_pc_jump_without_redirect(dut):
    """Non-sequential aligned in-range PC jump (0x004 -> 0x020) without redirect is caught."""
    await reset_dut(dut)
    dut.fetch_pc.value = 0x000
    await tick(dut)
    dut.fetch_pc.value = 0x004
    await tick(dut)

    dut.fetch_pc.value = 0x020  # aligned, in-range, no redirect
    await Timer(1, unit="ns")
    assert int(dut.fault_detected.value) == 1
    await tick(dut)
    assert int(dut.fault_sticky.value) == 1
    assert int(dut.fault_class.value) == FC_PC_TRANSITION


@cocotb.test()
async def test_spurious_redirect_and_dropped_redirect(dut):
    """Spurious branch_redirect without branch_taken, and dropped redirect, are caught."""
    # Spurious redirect
    await reset_dut(dut)
    dut.fetch_pc.value = 0x000
    dut.branch_redirect.value = 1
    dut.pc_target.value = 0x020
    await Timer(1, unit="ns")
    assert int(dut.fault_detected.value) == 1
    await tick(dut)
    assert int(dut.fault_sticky.value) == 1
    assert int(dut.fault_class.value) == FC_REDIRECT_TARGET or int(dut.fault_class.value) == FC_REDIRECT_SPURIOUS

    # Dropped redirect (branch_taken=1, valid aligned target, branch_redirect=0)
    await reset_dut(dut)
    dut.fetch_pc.value = 0x000
    dut.branch_taken.value = 1
    dut.branch_target.value = 0x020
    dut.branch_redirect.value = 0
    await Timer(1, unit="ns")
    assert int(dut.fault_detected.value) == 1
    await tick(dut)
    assert int(dut.fault_sticky.value) == 1
    assert int(dut.fault_class.value) == FC_REDIRECT_SPURIOUS


@cocotb.test()
async def test_redirect_target_mismatch(dut):
    """Redirect lands at wrong PC on next cycle -> FC_REDIRECT_TARGET."""
    await reset_dut(dut)
    dut.fetch_pc.value = 0x000
    dut.branch_taken.value = 1
    dut.branch_target.value = 0x040
    dut.branch_redirect.value = 1
    dut.pc_target.value = 0x040
    await tick(dut)

    clear_inputs(dut)
    dut.fetch_pc.value = 0x044  # expected 0x040
    await Timer(1, unit="ns")
    assert int(dut.fault_detected.value) == 1
    await tick(dut)
    assert int(dut.fault_sticky.value) == 1
    assert int(dut.fault_class.value) == FC_REDIRECT_TARGET
