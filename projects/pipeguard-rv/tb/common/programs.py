"""Directed and seeded-random RV32I programs for PipeGuard-RV verification.

Each directed program records which pipeline events it is REQUIRED to exercise
(`expect`), so a test that claims to cover e.g. load-use hazards fails if the
event never actually occurs. Event names:
    redirect   - branch_redirect asserted at least once
    stall      - load_use_stall asserted at least once
    align      - alignment_fault asserted at least once
    no_redirect- branch_redirect never asserted
"""
import random
from dataclasses import dataclass, field

from rv32i import (NOP, add, addi, auipc, beq, bge, blt, bne, jal, jalr, lui,
                   lw, sub, sw, i_type, r_type, OP_LOAD)

IMEM_WORDS = 256  # instruction_memory MEM_DEPTH default in the Lab 06 core


@dataclass
class Program:
    name: str
    words: list
    cycles: int = 60
    expect: set = field(default_factory=set)
    # architectural register values that must hold at the end (sanity check
    # that the program did what it is documented to do)
    regs: dict = field(default_factory=dict)


HALT = jal(0, 0)  # self-loop: deterministic end-of-program


def directed():
    p = []
    p.append(Program("sequential", [
        addi(1, 0, 5), addi(2, 0, 7), add(3, 1, 2), sub(4, 2, 1),
        addi(5, 3, -1), add(6, 5, 4), HALT],
        expect={"no_redirect_before_halt"}, regs={3: 12, 4: 2, 5: 11, 6: 13}))
    p.append(Program("branch_taken_forward", [
        addi(1, 0, 5), addi(2, 0, 5), beq(1, 2, 12),
        addi(3, 0, 1), addi(3, 0, 2),              # skipped
        addi(4, 0, 7), HALT],
        expect={"redirect"}, regs={3: 0, 4: 7}))
    p.append(Program("branch_not_taken", [
        addi(1, 0, 5), addi(2, 0, 5), bne(1, 2, 12),
        addi(3, 0, 1), addi(4, 0, 2), HALT],
        expect={"no_redirect_before_halt"}, regs={3: 1, 4: 2}))
    p.append(Program("backward_loop", [
        addi(1, 0, 0), addi(2, 0, 5),
        addi(1, 1, 1), bne(1, 2, -4),               # loop body at 8, branch at 12
        addi(3, 0, 9), HALT],
        cycles=80, expect={"redirect"}, regs={1: 5, 3: 9}))
    p.append(Program("jal_jalr_call_return", [
        jal(1, 16),                                  # 0: call 16
        addi(7, 0, 7),                               # 4: after return
        HALT,                                        # 8
        NOP,                                         # 12
        addi(6, 0, 3),                               # 16: callee
        jalr(0, 1, 0)],                              # 20: return to 4
        expect={"redirect"}, regs={1: 4, 6: 3, 7: 7}))
    p.append(Program("load_use_hazard", [
        addi(1, 0, 42), addi(2, 0, 8), sw(1, 2, 0),
        lw(3, 2, 0), add(4, 3, 3),                   # load-use stall
        sw(4, 2, 4), lw(5, 2, 4), addi(6, 5, 1), HALT],
        expect={"stall"}, regs={3: 42, 4: 84, 5: 84, 6: 85}))
    p.append(Program("forwarding_chain", [
        addi(1, 0, 1), add(2, 1, 1), add(3, 2, 1), add(4, 3, 2), sub(5, 4, 1), HALT],
        regs={2: 2, 3: 3, 4: 5, 5: 4}))
    p.append(Program("load_then_branch", [
        addi(1, 0, 3), addi(2, 0, 16), sw(1, 2, 0),
        lw(3, 2, 0), beq(3, 1, 12),                  # stall, then taken branch
        addi(4, 0, 1), addi(4, 0, 2),                # skipped
        addi(5, 0, 5), HALT],
        expect={"stall", "redirect"}, regs={3: 3, 4: 0, 5: 5}))
    p.append(Program("flush_squash", [
        addi(1, 0, 1), jal(0, 16),                   # 4: jump to 20
        addi(10, 0, 10), addi(11, 0, 11), addi(12, 0, 12),   # squashed / skipped
        addi(13, 0, 13), HALT],
        expect={"redirect"}, regs={10: 0, 11: 0, 12: 0, 13: 13}))
    p.append(Program("real_nops", [
        NOP, NOP, addi(1, 0, 1), NOP, addi(2, 1, 1), NOP, NOP, HALT],
        regs={1: 1, 2: 2}))
    p.append(Program("consecutive_branches", [
        addi(1, 0, 1), beq(0, 0, 8), addi(9, 0, 9), beq(0, 0, 8), addi(9, 0, 8),
        bne(0, 1, 8), addi(9, 0, 7), addi(2, 0, 2), HALT],
        expect={"redirect"}, regs={2: 2, 9: 0}))
    p.append(Program("signed_branches", [
        addi(1, 0, -3), addi(2, 0, 2), blt(1, 2, 8), addi(3, 0, 1),
        bge(2, 1, 8), addi(4, 0, 1), addi(5, 0, 5), HALT],
        expect={"redirect"}, regs={3: 0, 4: 0, 5: 5}))
    p.append(Program("lui_auipc", [
        lui(1, 0x12345), auipc(2, 0x1), addi(3, 1, 0x67), HALT],
        regs={1: 0x12345000, 2: 0x1004, 3: 0x12345067}))
    p.append(Program("misaligned_jalr_target", [
        addi(1, 0, 6), jalr(0, 1, 0),                # target 6: bit1 set
        addi(2, 0, 2), addi(3, 0, 3), HALT],
        cycles=30, expect={"align"}))
    p.append(Program("misaligned_load", [
        addi(1, 0, 2), lw(2, 1, 0), addi(3, 0, 3), HALT],
        regs={3: 3}))
    return p


def random_program(seed: int, length: int = 48) -> Program:
    """Seeded random RV32I program. Not required to be meaningful: it only
    has to be identical for both cores. Branch/jump offsets are kept inside
    the program so that control flow mostly stays in initialised ROM."""
    rng = random.Random(seed)
    words = []
    for pc_idx in range(length):
        k = rng.random()
        rd, rs1, rs2 = rng.randrange(1, 8), rng.randrange(0, 8), rng.randrange(0, 8)
        if k < 0.35:
            words.append(i_type(rd, rs1, rng.randrange(-64, 64), rng.choice([0, 2, 3, 4, 6, 7])))
        elif k < 0.55:
            f3, f7 = rng.choice([(0, 0), (0, 0x20), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (5, 0x20), (6, 0), (7, 0)])
            words.append(r_type(rd, rs1, rs2, f3, f7))
        elif k < 0.65:
            words.append(sw(rs2, 0, 4 * rng.randrange(0, 16)))
        elif k < 0.75:
            words.append(lw(rd, 0, 4 * rng.randrange(0, 16)))
        elif k < 0.80:
            words.append(i_type(rd, rs1, rng.randrange(0, 8), 2, OP_LOAD))   # possibly misaligned
        elif k < 0.92:
            off = 4 * rng.randrange(-min(pc_idx, 6), 7)
            if off == 0:
                off = 8
            words.append([beq, bne, blt, bge][rng.randrange(4)](rs1, rs2, off))
        elif k < 0.97:
            off = 4 * rng.randrange(1, 6)
            words.append(jal(rng.choice([0, 1]), off))
        else:
            words.append(jalr(rng.choice([0, 1]), 0, 4 * rng.randrange(0, length) + rng.choice([0, 0, 0, 2])))
    words.append(HALT)
    return Program(f"random_seed{seed}", words, cycles=200)
