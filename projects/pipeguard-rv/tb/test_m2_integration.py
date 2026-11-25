"""Integration, lock-step false-positive, and synthetic fault-injection tests for M2."""
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

FC_STALL_INCONSIST = 6
FC_FLUSH_INCONSIST = 7


async def run_m2_lockstep(dut, prog):
    await load_and_reset(dut, prog.words)
    events = {"redirect": 0, "stall": 0, "align": 0}
    check_cycle(dut, 0, prog.name, events)
    for cyc in range(1, prog.cycles + 1):
        await tick(dut)
        check_cycle(dut, cyc, prog.name, events)
    check_arch_state(dut, prog)
    check_events(prog, events)


@cocotb.test()
async def test_m2_directed_lockstep_zero_fp(dut):
    """All 15 directed programs pass lock-step with 0 false positives in M2."""
    for prog in directed():
        dut._log.info(f"M2 directed lockstep: {prog.name}")
        await run_m2_lockstep(dut, prog)


@cocotb.test()
async def test_m2_random_lockstep_zero_fp(dut):
    """All 10 random RV32I programs pass lock-step with 0 false positives in M2."""
    for seed in range(10):
        prog = random_program(seed=seed, length=48)
        dut._log.info(f"M2 random lockstep: {prog.name}")
        await run_m2_lockstep(dut, prog)


@cocotb.test()
async def test_m2_catches_spurious_pc_stall(dut):
    """M2 catches spurious pc_stall=1 (which M1 missed due to conservative hold)."""
    prog = directed()[0]
    await load_and_reset(dut, prog.words)
    for _ in range(2):
        await tick(dut)

    stall = dut.dut_cpu.u_core.pc_stall
    stall.value = Force(1)
    await Timer(1, unit="ns")

    assert int(dut.dut_fault_detected.value) == 1
    await tick(dut)
    assert int(dut.dut_fault_sticky.value) == 1
    assert int(dut.dut_fault_class.value) == FC_STALL_INCONSIST
    stall.value = Release()


@cocotb.test()
async def test_m2_catches_dropped_load_use_stall(dut):
    """M2 catches dropped load_use_stall during an active load-use hazard."""
    prog = [p for p in directed() if p.name == "load_use_hazard"][0]
    await load_and_reset(dut, prog.words)

    lus = dut.dut_cpu.u_core.load_use_stall
    caught = False
    for _ in range(20):
        await Timer(1, unit="ns")
        if int(lus.value) == 1:
            lus.value = Force(0)
            await Timer(1, unit="ns")
            assert int(dut.dut_fault_detected.value) == 1
            await tick(dut)
            assert int(dut.dut_fault_sticky.value) == 1
            assert int(dut.dut_fault_class.value) == FC_STALL_INCONSIST
            lus.value = Release()
            caught = True
            break
        await tick(dut)
    assert caught, "load_use_hazard did not assert load_use_stall"


@cocotb.test()
async def test_m2_catches_dropped_id_ex_flush(dut):
    """M2 catches dropped id_ex_flush during a taken branch redirect."""
    prog = [p for p in directed() if p.name == "branch_taken_forward"][0]
    await load_and_reset(dut, prog.words)

    flush = dut.dut_cpu.u_core.id_ex_flush
    redir = dut.dut_cpu.u_core.branch_redirect
    caught = False
    for _ in range(20):
        await Timer(1, unit="ns")
        if int(redir.value) == 1:
            flush.value = Force(0)
            await Timer(1, unit="ns")
            assert int(dut.dut_fault_detected.value) == 1
            await tick(dut)
            assert int(dut.dut_fault_sticky.value) == 1
            assert int(dut.dut_fault_class.value) == FC_FLUSH_INCONSIST
            flush.value = Release()
            caught = True
            break
        await tick(dut)
    assert caught, "branch_taken_forward did not assert branch_redirect"
