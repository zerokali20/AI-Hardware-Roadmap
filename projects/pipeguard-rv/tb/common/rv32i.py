"""Minimal RV32I machine-code encoder used by PipeGuard-RV testbenches.

Only the instruction formats needed by the project workloads are provided.
Each function returns a 32-bit instruction word. Immediates are given as
signed Python integers and are range-checked so that a test can never
silently encode a truncated offset.
"""

NOP = 0x00000013  # addi x0, x0, 0 — a REAL instruction, distinct from a bubble

OP_LUI, OP_AUIPC, OP_JAL, OP_JALR = 0x37, 0x17, 0x6F, 0x67
OP_BRANCH, OP_LOAD, OP_STORE, OP_IMM, OP_REG = 0x63, 0x03, 0x23, 0x13, 0x33


def _chk(val, bits, name, signed=True):
    lo, hi = (-(1 << (bits - 1)), (1 << (bits - 1)) - 1) if signed else (0, (1 << bits) - 1)
    if not lo <= val <= hi:
        raise ValueError(f"{name}={val} out of range [{lo},{hi}]")


def _reg(*rs):
    for r in rs:
        if not 0 <= r < 32:
            raise ValueError(f"bad register x{r}")


def r_type(rd, rs1, rs2, funct3, funct7=0):
    _reg(rd, rs1, rs2)
    return (funct7 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | OP_REG


def i_type(rd, rs1, imm, funct3=0, opcode=OP_IMM):
    _reg(rd, rs1)
    _chk(imm, 12, "imm")
    return ((imm & 0xFFF) << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode


def s_type(rs2, rs1, imm, funct3=2):
    _reg(rs1, rs2)
    _chk(imm, 12, "imm")
    imm &= 0xFFF
    return ((imm >> 5) << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | ((imm & 0x1F) << 7) | OP_STORE


def b_type(rs1, rs2, offset, funct3):
    _reg(rs1, rs2)
    _chk(offset, 13, "branch offset")
    if offset & 1:
        raise ValueError("branch offset must be even")
    o = offset & 0x1FFF
    return (((o >> 12) & 1) << 31) | (((o >> 5) & 0x3F) << 25) | (rs2 << 20) | (rs1 << 15) \
        | (funct3 << 12) | (((o >> 1) & 0xF) << 8) | (((o >> 11) & 1) << 7) | OP_BRANCH


def j_type(rd, offset):
    _reg(rd)
    _chk(offset, 21, "jal offset")
    if offset & 1:
        raise ValueError("jal offset must be even")
    o = offset & 0x1FFFFF
    return (((o >> 20) & 1) << 31) | (((o >> 1) & 0x3FF) << 21) | (((o >> 11) & 1) << 20) \
        | (((o >> 12) & 0xFF) << 12) | (rd << 7) | OP_JAL


def u_type(rd, imm20, opcode):
    _reg(rd)
    _chk(imm20, 20, "imm20", signed=False)
    return (imm20 << 12) | (rd << 7) | opcode


# Convenience mnemonics
def addi(rd, rs1, imm): return i_type(rd, rs1, imm, 0)
def add(rd, rs1, rs2): return r_type(rd, rs1, rs2, 0)
def sub(rd, rs1, rs2): return r_type(rd, rs1, rs2, 0, 0x20)
def lw(rd, rs1, imm): return i_type(rd, rs1, imm, 2, OP_LOAD)
def sw(rs2, rs1, imm): return s_type(rs2, rs1, imm, 2)
def beq(rs1, rs2, off): return b_type(rs1, rs2, off, 0)
def bne(rs1, rs2, off): return b_type(rs1, rs2, off, 1)
def blt(rs1, rs2, off): return b_type(rs1, rs2, off, 4)
def bge(rs1, rs2, off): return b_type(rs1, rs2, off, 5)
def jal(rd, off): return j_type(rd, off)
def jalr(rd, rs1, imm): return i_type(rd, rs1, imm, 0, OP_JALR)
def lui(rd, imm20): return u_type(rd, imm20, OP_LUI)
def auipc(rd, imm20): return u_type(rd, imm20, OP_AUIPC)
