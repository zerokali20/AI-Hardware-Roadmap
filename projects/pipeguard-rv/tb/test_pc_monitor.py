"""Unit tests for rtl/monitors/pc_monitor.sv (M0).

Verifies:
  1. Reset behaviour: alarms cleared on rst, and invalid PCs during rst do not
     trigger fault_detected or latch fault_sticky.
  2. Legal aligned in-range PCs (sequential and non-sequential jumps) produce
     zero alarms.
  3. Misaligned PCs (bits [1:0] != 0) assert fault_detected and latch
     fault_sticky with fault_class == 1 (PG_FC_PC_MISALIGNED).
  4. Out-of-bounds PCs (> PC_MAX) assert fault_detected and latch fault_sticky
     with fault_class == 2 (PG_FC_PC_OUT_OF_BOUNDS).
  5. Priority when both misaligned and out-of-bounds: PG_FC_PC_MISALIGNED wins.
  6. Sticky persistence: fault_detected clears when PC returns to legal,
     fault_sticky and first fault_class persist until rst=1.
"""
import cocotb
from cocotb.triggers import Timer

FC_NONE = 0
FC_PC_MISALIGNED = 1
FC_PC_OUT_OF_BOUNDS = 2


async def tick(dut):
    dut.clk.value = 0
    await Timer(5, unit="ns")
    dut.clk.value = 1
    await Timer(5, unit="ns")
    dut.clk.value = 0
    await Timer(1, unit="ns")


async def reset_dut(dut, pc_during_rst=0):
    dut.rst.value = 1
    dut.fetch_pc.value = pc_during_rst
    await Timer(1, unit="ns")
    await tick(dut)
    assert int(dut.fault_detected.value) == 0
    assert int(dut.fault_sticky.value) == 0
    assert int(dut.fault_class.value) == FC_NONE
    dut.rst.value = 0
    dut.fetch_pc.value = 0
    await Timer(1, unit="ns")


@cocotb.test()
async def test_reset_suppression(dut):
    """Invalid PC while rst=1 must not trigger or latch an alarm."""
    await reset_dut(dut, pc_during_rst=0xFFFF_FFFB)
    assert int(dut.fault_detected.value) == 0
    assert int(dut.fault_sticky.value) == 0
    assert int(dut.fault_class.value) == FC_NONE


@cocotb.test()
async def test_valid_sequential_and_nonsequential_pcs(dut):
    """Valid aligned PCs in [0x000, 0x3FC], including jumps, never alarm."""
    await reset_dut(dut)
    legal_pcs = [0x000, 0x004, 0x008, 0x100, 0x020, 0x3FC, 0x000, 0x244]
    for pc in legal_pcs:
        dut.fetch_pc.value = pc
        await Timer(1, unit="ns")
        assert int(dut.fault_detected.value) == 0, f"False positive at PC=0x{pc:08x}"
        await tick(dut)
        assert int(dut.fault_sticky.value) == 0
        assert int(dut.fault_class.value) == FC_NONE


@cocotb.test()
async def test_misaligned_pc_detection_and_sticky(dut):
    """Misaligned in-range PCs trigger FC_PC_MISALIGNED and latch until rst."""
    for offset in (1, 2, 3):
        await reset_dut(dut)
        bad_pc = 0x010 + offset
        dut.fetch_pc.value = bad_pc
        await Timer(1, unit="ns")
        assert int(dut.fault_detected.value) == 1
        assert int(dut.fault_sticky.value) == 0  # not clocked yet
        await tick(dut)
        assert int(dut.fault_sticky.value) == 1
        assert int(dut.fault_class.value) == FC_PC_MISALIGNED

        # Return PC to legal; fault_detected drops, sticky & class persist
        dut.fetch_pc.value = 0x014
        await Timer(1, unit="ns")
        assert int(dut.fault_detected.value) == 0
        assert int(dut.fault_sticky.value) == 1
        assert int(dut.fault_class.value) == FC_PC_MISALIGNED

        # Second different fault does not overwrite first fault_class
        dut.fetch_pc.value = 0x800
        await tick(dut)
        assert int(dut.fault_sticky.value) == 1
        assert int(dut.fault_class.value) == FC_PC_MISALIGNED


@cocotb.test()
async def test_out_of_bounds_pc_detection(dut):
    """Aligned PCs > PC_MAX (0x3FC) trigger FC_PC_OUT_OF_BOUNDS."""
    for bad_pc in (0x400, 0x1000, 0xFFFF_FFFC):
        await reset_dut(dut)
        dut.fetch_pc.value = bad_pc
        await Timer(1, unit="ns")
        assert int(dut.fault_detected.value) == 1
        await tick(dut)
        assert int(dut.fault_sticky.value) == 1
        assert int(dut.fault_class.value) == FC_PC_OUT_OF_BOUNDS


@cocotb.test()
async def test_misaligned_priority_over_oob(dut):
    """When both misaligned and out-of-bounds, FC_PC_MISALIGNED takes priority."""
    await reset_dut(dut)
    dut.fetch_pc.value = 0x402  # > 0x3FC AND misaligned
    await Timer(1, unit="ns")
    assert int(dut.fault_detected.value) == 1
    await tick(dut)
    assert int(dut.fault_sticky.value) == 1
    assert int(dut.fault_class.value) == FC_PC_MISALIGNED

    # Reset clears sticky and class
    await reset_dut(dut)
    assert int(dut.fault_sticky.value) == 0
    assert int(dut.fault_class.value) == FC_NONE
