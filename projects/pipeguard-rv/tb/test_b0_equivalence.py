"""Lock-step equivalence tests for PipeGuard-RV B0 (unprotected research top).

Instantiates tb_lockstep (unmodified rtl/core/riscv_pipeline_cpu.sv alongside
pipeguard_cpu #(.MONITOR_CFG(0))) and verifies that for every directed and
seeded-random RV32I program:
  1. Every externally observable CPU port matches cycle-for-cycle.
  2. Final register file (x0..x31) and data memory (0..MEM_SIZE-1) match.
  3. B0 alarm outputs remain deasserted (fault_detected=0, fault_sticky=0,
     fault_class=0) on every cycle.
  4. Each directed program exercises its documented pipeline events (`expect`)
     and achieves its expected architectural register values (`regs`).
"""
import cocotb
from cocotb.triggers import Timer

from programs import IMEM_WORDS, directed, random_program
from rv32i import NOP

OBS_PORTS = [
    "fetch_pc",
    "decode_pc",
    "execute_pc",
    "mem_pc",
    "wb_pc",
    "wb_data",
    "wb_rd",
    "wb_reg_write",
    "load_use_stall",
    "branch_redirect",
    "alignment_fault",
    "memory_alignment_error",
    "memory_access_error",
    "illegal_instruction",
]


async def tick(dut):
    dut.clk.value = 0
    await Timer(5, unit="ns")
    dut.clk.value = 1
    await Timer(5, unit="ns")
    dut.clk.value = 0
    await Timer(1, unit="ns")


async def load_and_reset(dut, words):
    dut.clk.value = 0
    dut.rst.value = 1

    ref_imem = dut.ref_cpu.frontend.fetch_unit.imem_unit.memory
    dut_imem = dut.dut_cpu.u_core.frontend.fetch_unit.imem_unit.memory

    for i in range(IMEM_WORDS):
        w = words[i] if i < len(words) else NOP
        ref_imem[i].value = w
        dut_imem[i].value = w

    await Timer(1, unit="ns")
    await tick(dut)
    dut.rst.value = 0
    await Timer(1, unit="ns")


def check_cycle(dut, cyc, prog_name, events):
    for p in OBS_PORTS:
        r_raw = getattr(dut, f"ref_{p}").value
        d_raw = getattr(dut, f"dut_{p}").value
        r_str = str(r_raw)
        d_str = str(d_raw)
        assert r_str == d_str, (
            f"[{prog_name}] cycle {cyc}: port {p} mismatch: "
            f"ref={r_str} dut={d_str}"
        )

    assert str(dut.dut_fault_detected.value) == "0", f"[{prog_name}] cycle {cyc}: B0 fault_detected != 0"
    assert str(dut.dut_fault_sticky.value) == "0", f"[{prog_name}] cycle {cyc}: B0 fault_sticky != 0"
    assert int(dut.dut_fault_class.value) == 0, f"[{prog_name}] cycle {cyc}: B0 fault_class != 0"

    if str(dut.ref_branch_redirect.value) == "1":
        events["redirect"] += 1
    if str(dut.ref_load_use_stall.value) == "1":
        events["stall"] += 1
    if str(dut.ref_alignment_fault.value) == "1":
        events["align"] += 1


def check_arch_state(dut, prog):
    ref_rf = dut.ref_cpu.frontend.regfile.registers
    dut_rf = dut.dut_cpu.u_core.frontend.regfile.registers
    for r in range(32):
        rv = str(ref_rf[r].value)
        dv = str(dut_rf[r].value)
        assert rv == dv, f"[{prog.name}] x{r} mismatch: ref={rv} dut={dv}"

    for r_idx, expected in prog.regs.items():
        actual = int(dut_rf[r_idx].value)
        exp_u32 = expected & 0xFFFFFFFF
        assert actual == exp_u32, (
            f"[{prog.name}] arch check x{r_idx}: expected 0x{exp_u32:08x}, got 0x{actual:08x}"
        )

    ref_dmem = dut.ref_cpu.memory_unit.data_mem_unit.memory
    dut_dmem = dut.dut_cpu.u_core.memory_unit.data_mem_unit.memory
    for addr in range(len(ref_dmem)):
        rv = str(ref_dmem[addr].value)
        dv = str(dut_dmem[addr].value)
        assert rv == dv, f"[{prog.name}] dmem[{addr}] mismatch: ref={rv} dut={dv}"


def check_events(prog, events):
    if "redirect" in prog.expect:
        assert events["redirect"] > 0, f"[{prog.name}] expected branch_redirect >= 1, got 0"
    if "stall" in prog.expect:
        assert events["stall"] > 0, f"[{prog.name}] expected load_use_stall >= 1, got 0"
    if "align" in prog.expect:
        assert events["align"] > 0, f"[{prog.name}] expected alignment_fault >= 1, got 0"


async def run_program(dut, prog):
    await load_and_reset(dut, prog.words)
    events = {"redirect": 0, "stall": 0, "align": 0}
    check_cycle(dut, 0, prog.name, events)
    for cyc in range(1, prog.cycles + 1):
        await tick(dut)
        check_cycle(dut, cyc, prog.name, events)
    check_arch_state(dut, prog)
    check_events(prog, events)


@cocotb.test()
async def test_b0_directed_lockstep(dut):
    """Run all 15 directed programs in lock-step between ref_cpu and B0."""
    for prog in directed():
        dut._log.info(f"Running directed lockstep: {prog.name}")
        await run_program(dut, prog)


@cocotb.test()
async def test_b0_random_lockstep(dut):
    """Run 10 seeded-random RV32I programs in lock-step between ref_cpu and B0."""
    for seed in range(10):
        prog = random_program(seed=seed, length=48)
        dut._log.info(f"Running random lockstep: {prog.name}")
        await run_program(dut, prog)
