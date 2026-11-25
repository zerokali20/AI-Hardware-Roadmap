"""Integration, lock-step false-positive, and synthetic fault-injection tests for M0.

Runs against tb_lockstep with MONITOR_CFG=1 (pipeguard_cpu instantiating
pc_monitor alongside unmodified rtl/core/riscv_pipeline_cpu).
"""
import cocotb
from cocotb.handle import Force, Release
from cocotb.triggers import Timer

from programs import directed, random_program
from test_b0_equivalence import (
    check_arch_state,
    check_cycle,
    check_events,
    load_and_reset,
    tick,
)

FC_NONE = 0
FC_PC_MISALIGNED = 1
FC_PC_OUT_OF_BOUNDS = 2


async def run_m0_lockstep(dut, prog):
    await load_and_reset(dut, prog.words)
    events = {"redirect": 0, "stall": 0, "align": 0}
    check_cycle(dut, 0, prog.name, events)
    for cyc in range(1, prog.cycles + 1):
        await tick(dut)
        check_cycle(dut, cyc, prog.name, events)
    check_arch_state(dut, prog)
    check_events(prog, events)


@cocotb.test()
async def test_m0_directed_lockstep_zero_fp(dut):
    """All 15 directed programs pass lock-step with 0 false positives in M0."""
    for prog in directed():
        dut._log.info(f"M0 directed lockstep: {prog.name}")
        await run_m0_lockstep(dut, prog)


@cocotb.test()
async def test_m0_random_lockstep_zero_fp(dut):
    """All 10 random RV32I programs pass lock-step with 0 false positives in M0."""
    for seed in range(10):
        prog = random_program(seed=seed, length=48)
        dut._log.info(f"M0 random lockstep: {prog.name}")
        await run_m0_lockstep(dut, prog)


@cocotb.test()
async def test_m0_fault_inject_misaligned(dut):
    """Single-bit transient fault on PC[1] is detected as FC_PC_MISALIGNED."""
    prog = directed()[0]  # sequential
    await load_and_reset(dut, prog.words)
    for _ in range(3):
        await tick(dut)

    pc_reg = dut.dut_cpu.u_core.frontend.fetch_unit.pc_unit.pc
    orig_pc = int(pc_reg.value)
    pc_reg.value = Force(orig_pc ^ 0x2)
    await Timer(1, unit="ns")

    assert int(dut.dut_fault_detected.value) == 1
    assert int(dut.dut_fault_sticky.value) == 0

    await tick(dut)
    assert int(dut.dut_fault_sticky.value) == 1
    assert int(dut.dut_fault_class.value) == FC_PC_MISALIGNED

    pc_reg.value = Release()
    await Timer(1, unit="ns")
    await tick(dut)
    assert int(dut.dut_fault_sticky.value) == 1
    assert int(dut.dut_fault_class.value) == FC_PC_MISALIGNED


@cocotb.test()
async def test_m0_fault_inject_out_of_bounds(dut):
    """Single-bit transient fault on PC[10] (0x400+) is detected as FC_PC_OUT_OF_BOUNDS."""
    prog = directed()[0]
    await load_and_reset(dut, prog.words)
    for _ in range(3):
        await tick(dut)

    pc_reg = dut.dut_cpu.u_core.frontend.fetch_unit.pc_unit.pc
    orig_pc = int(pc_reg.value)
    pc_reg.value = Force(orig_pc ^ 0x400)
    await Timer(1, unit="ns")

    assert int(dut.dut_fault_detected.value) == 1
    await tick(dut)
    assert int(dut.dut_fault_sticky.value) == 1
    assert int(dut.dut_fault_class.value) == FC_PC_OUT_OF_BOUNDS

    pc_reg.value = Release()
    await tick(dut)
    assert int(dut.dut_fault_sticky.value) == 1
    assert int(dut.dut_fault_class.value) == FC_PC_OUT_OF_BOUNDS


@cocotb.test()
async def test_m0_aligned_in_range_blind_spot(dut):
    """Aligned in-range PC bit-flip (PC[3]) is NOT detected by M0 (known limitation)."""
    prog = directed()[0]
    await load_and_reset(dut, prog.words)
    for _ in range(3):
        await tick(dut)

    pc_reg = dut.dut_cpu.u_core.frontend.fetch_unit.pc_unit.pc
    orig_pc = int(pc_reg.value)
    pc_reg.value = Force(orig_pc ^ 0x8)  # aligned, inside [0x000, 0x3FC]
    await Timer(1, unit="ns")

    assert int(dut.dut_fault_detected.value) == 0
    await tick(dut)
    assert int(dut.dut_fault_sticky.value) == 0
    assert int(dut.dut_fault_class.value) == FC_NONE

    pc_reg.value = Release()
