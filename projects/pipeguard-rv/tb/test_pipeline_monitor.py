"""Unit tests for rtl/monitors/pipeline_monitor.sv (M2)."""
import cocotb
from cocotb.triggers import Timer

FC_NONE = 0
FC_PC_TRANSITION = 3
FC_STALL_INCONSIST = 6
FC_FLUSH_INCONSIST = 7
FC_REDIRECT_PRIORITY = 8
FC_STAGE_PROGRESS = 9


async def tick(dut):
    dut.clk.value = 0
    await Timer(5, unit="ns")
    dut.clk.value = 1
    await Timer(5, unit="ns")
    dut.clk.value = 0
    await Timer(1, unit="ns")


def clear_inputs(dut):
    dut.fetch_pc.value = 0
    dut.decode_pc.value = 0
    dut.execute_pc.value = 0
    dut.mem_pc.value = 0
    dut.wb_pc.value = 0
    dut.branch_redirect.value = 0
    dut.pc_target.value = 0
    dut.branch_taken.value = 0
    dut.branch_target.value = 0
    dut.invalid_branch.value = 0
    dut.alignment_fault.value = 0
    dut.load_use_stall.value = 0
    dut.pc_stall.value = 0
    dut.id_ex_stall.value = 0
    dut.id_ex_flush.value = 0
    dut.id_opcode.value = 0x13
    dut.id_rs1.value = 0
    dut.id_rs2.value = 0
    dut.ex_rd.value = 0
    dut.ex_mem_read.value = 0


async def reset_dut(dut):
    dut.rst.value = 1
    clear_inputs(dut)
    await Timer(1, unit="ns")
    await tick(dut)
    dut.rst.value = 0
    await Timer(1, unit="ns")


@cocotb.test()
async def test_valid_pipeline_progression_and_stall(dut):
    """Normal progression and legitimate load-use stall produce zero alarms."""
    await reset_dut(dut)
    # Cycle 0: IF=0
    dut.fetch_pc.value = 0x000
    await Timer(1, unit="ns")
    assert int(dut.fault_detected.value) == 0
    await tick(dut)

    # Cycle 1: IF=4, ID=0
    dut.fetch_pc.value = 0x004
    dut.decode_pc.value = 0x000
    await Timer(1, unit="ns")
    assert int(dut.fault_detected.value) == 0
    await tick(dut)

    # Cycle 2: IF=8, ID=4 (ADD x3, x1, x0), EX=0 (LW x1, ...) -> load-use stall!
    dut.fetch_pc.value = 0x008
    dut.decode_pc.value = 0x004
    dut.execute_pc.value = 0x000
    dut.id_opcode.value = 0x33  # R-type
    dut.id_rs1.value = 1
    dut.id_rs2.value = 0
    dut.ex_rd.value = 1
    dut.ex_mem_read.value = 1
    dut.load_use_stall.value = 1
    dut.pc_stall.value = 1
    dut.id_ex_flush.value = 1
    await Timer(1, unit="ns")
    assert int(dut.fault_detected.value) == 0
    await tick(dut)

    # Cycle 3: IF=8 (held), ID=4 (held), EX=0 (flushed!), MEM=0
    dut.ex_mem_read.value = 0
    dut.ex_rd.value = 0
    dut.load_use_stall.value = 0
    dut.pc_stall.value = 0
    dut.id_ex_flush.value = 0
    dut.execute_pc.value = 0x000  # flushed bubble
    dut.mem_pc.value = 0x000
    await Timer(1, unit="ns")
    assert int(dut.fault_detected.value) == 0
    await tick(dut)
    assert int(dut.fault_sticky.value) == 0


@cocotb.test()
async def test_spurious_pc_freeze_caught_by_m2(dut):
    """Spurious PC hold without stall (accepted by M1) is caught by M2 as FC_PC_TRANSITION."""
    await reset_dut(dut)
    dut.fetch_pc.value = 0x000
    await tick(dut)
    dut.fetch_pc.value = 0x000  # held without pc_stall=1
    dut.decode_pc.value = 0x000
    await Timer(1, unit="ns")
    assert int(dut.fault_detected.value) == 1
    await tick(dut)
    assert int(dut.fault_sticky.value) == 1
    assert int(dut.fault_class.value) == FC_PC_TRANSITION


@cocotb.test()
async def test_load_use_stall_inconsistency(dut):
    """Dropped load_use_stall when hazard exists -> FC_STALL_INCONSIST."""
    await reset_dut(dut)
    dut.fetch_pc.value = 0x000
    dut.id_opcode.value = 0x13  # I-type
    dut.id_rs1.value = 2
    dut.ex_rd.value = 2
    dut.ex_mem_read.value = 1
    dut.load_use_stall.value = 0  # fault: should be 1
    dut.pc_stall.value = 1
    dut.id_ex_flush.value = 1
    await Timer(1, unit="ns")
    assert int(dut.fault_detected.value) == 1
    await tick(dut)
    assert int(dut.fault_sticky.value) == 1
    assert int(dut.fault_class.value) == FC_STALL_INCONSIST


@cocotb.test()
async def test_redirect_priority_and_stage_progress(dut):
    """Redirect vs alignment_fault priority violation and stage progression error."""
    # Priority violation: branch_taken with misaligned target but branch_redirect=1
    await reset_dut(dut)
    dut.fetch_pc.value = 0x000
    dut.branch_taken.value = 1
    dut.branch_target.value = 0x022  # misaligned
    dut.pc_target.value = 0x022
    dut.alignment_fault.value = 0    # fault: should be 1
    dut.branch_redirect.value = 1    # fault: should be 0
    await Timer(1, unit="ns")
    assert int(dut.fault_detected.value) == 1
    await tick(dut)
    assert int(dut.fault_sticky.value) == 1
    assert int(dut.fault_class.value) == FC_REDIRECT_PRIORITY

    # Stage progression violation: decode_pc fails to advance from prev_fetch_pc
    await reset_dut(dut)
    dut.fetch_pc.value = 0x000
    await tick(dut)
    dut.fetch_pc.value = 0x004
    dut.decode_pc.value = 0x008  # expected 0x000
    await Timer(1, unit="ns")
    assert int(dut.fault_detected.value) == 1
    await tick(dut)
    assert int(dut.fault_sticky.value) == 1
    assert int(dut.fault_class.value) == FC_STAGE_PROGRESS
