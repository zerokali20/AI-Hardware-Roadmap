"""Integration, lock-step false-positive, and synthetic fault-injection tests for M1."""
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
FC_PC_TRANSITION = 3
FC_REDIRECT_SPURIOUS = 5


async def run_m1_lockstep(dut, prog):
    await load_and_reset(dut, prog.words)
    events = {"redirect": 0, "stall": 0, "align": 0}
    check_cycle(dut, 0, prog.name, events)
    for cyc in range(1, prog.cycles + 1):
        await tick(dut)
        check_cycle(dut, cyc, prog.name, events)
    check_arch_state(dut, prog)
    check_events(prog, events)


@cocotb.test()
async def test_m1_directed_lockstep_zero_fp(dut):
    """All 15 directed programs pass lock-step with 0 false positives in M1."""
    for prog in directed():
        dut._log.info(f"M1 directed lockstep: {prog.name}")
        await run_m1_lockstep(dut, prog)


@cocotb.test()
async def test_m1_random_lockstep_zero_fp(dut):
    """All 10 random RV32I programs pass lock-step with 0 false positives in M1."""
    for seed in range(10):
        prog = random_program(seed=seed, length=48)
        dut._log.info(f"M1 random lockstep: {prog.name}")
        await run_m1_lockstep(dut, prog)


@cocotb.test()
async def test_m1_catches_aligned_in_range_pc_jump(dut):
    """M1 catches aligned in-range PC[3] jump that M0 missed."""
    prog = directed()[0]
    await load_and_reset(dut, prog.words)
    for _ in range(3):
        await tick(dut)

    pc_reg = dut.dut_cpu.u_core.frontend.fetch_unit.pc_unit.pc
    orig_pc = int(pc_reg.value)
    pc_reg.value = Force(orig_pc ^ 0x8)
    await Timer(1, unit="ns")

    assert int(dut.dut_fault_detected.value) == 1
    await tick(dut)
    assert int(dut.dut_fault_sticky.value) == 1
    assert int(dut.dut_fault_class.value) == FC_PC_TRANSITION
    pc_reg.value = Release()


@cocotb.test()
async def test_m1_catches_spurious_redirect(dut):
    """M1 catches spurious branch_redirect=1 during sequential execution."""
    prog = directed()[0]
    await load_and_reset(dut, prog.words)
    for _ in range(2):
        await tick(dut)

    redir = dut.dut_cpu.u_core.branch_redirect
    redir.value = Force(1)
    await Timer(1, unit="ns")

    assert int(dut.dut_fault_detected.value) == 1
    await tick(dut)
    assert int(dut.dut_fault_sticky.value) == 1
    assert int(dut.dut_fault_class.value) == FC_REDIRECT_SPURIOUS
    redir.value = Release()


@cocotb.test()
async def test_m1_conservative_hold_blind_spot(dut):
    """M1 conservatively accepts a spurious PC hold when stall is unavailable."""
    prog = directed()[0]
    await load_and_reset(dut, prog.words)
    for _ in range(2):
        await tick(dut)

    stall = dut.dut_cpu.u_core.pc_stall
    stall.value = Force(1)
    await tick(dut)
    stall.value = Release()
    await Timer(1, unit="ns")

    assert int(dut.dut_fault_detected.value) == 0
    assert int(dut.dut_fault_sticky.value) == 0
