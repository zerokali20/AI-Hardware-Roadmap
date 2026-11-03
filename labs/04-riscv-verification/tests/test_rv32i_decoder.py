import cocotb
import random

from cocotb.triggers import Timer


def encode_r_type(funct7, rs2, rs1, funct3, rd, opcode):
    """Encode an RV32I R-type instruction."""

    instruction = (
        ((funct7 & 0x7F) << 25)
        | ((rs2 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | ((funct3 & 0x07) << 12)
        | ((rd & 0x1F) << 7)
        | (opcode & 0x7F)
    )

    return instruction

def encode_i_type(immediate, rs1, funct3, rd, opcode):
    """Encode an RV32I I-type instruction."""

    imm12 = immediate & 0xFFF

    instruction = (
        (imm12 << 20)
        | ((rs1 & 0x1F) << 15)
        | ((funct3 & 0x07) << 12)
        | ((rd & 0x1F) << 7)
        | (opcode & 0x7F)
    )

    return instruction

def encode_s_type(immediate, rs2, rs1, funct3, opcode=0b0100011):
    """Encode an RV32I S-type instruction."""

    imm12 = immediate & 0xFFF

    imm_11_5 = (imm12 >> 5) & 0x7F
    imm_4_0 = imm12 & 0x1F

    instruction = (
        (imm_11_5 << 25)
        | ((rs2 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | ((funct3 & 0x07) << 12)
        | (imm_4_0 << 7)
        | (opcode & 0x7F)
    )

    return instruction

def encode_b_type(immediate, rs2, rs1, funct3, opcode=0b1100011):
    """Encode an RV32I B-type instruction."""

    imm13 = immediate & 0x1FFF

    imm_12 = (imm13 >> 12) & 0x01
    imm_11 = (imm13 >> 11) & 0x01
    imm_10_5 = (imm13 >> 5) & 0x3F
    imm_4_1 = (imm13 >> 1) & 0x0F

    instruction = (
        (imm_12 << 31)
        | (imm_10_5 << 25)
        | ((rs2 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | ((funct3 & 0x07) << 12)
        | (imm_4_1 << 8)
        | (imm_11 << 7)
        | (opcode & 0x7F)
    )

    return instruction

def sign_extend(value, bits):
    """Sign-extend a value of 'bits' width to 32 bits."""

    sign_bit = 1 << (bits - 1)

    if value & sign_bit:
        value -= 1 << bits

    return value & 0xFFFFFFFF


def decode_reference(instruction):
    """Python reference model for the RV32I decoder."""

    opcode = instruction & 0x7F
    rd = (instruction >> 7) & 0x1F
    funct3 = (instruction >> 12) & 0x07
    rs1 = (instruction >> 15) & 0x1F
    rs2 = (instruction >> 20) & 0x1F
    funct7 = (instruction >> 25) & 0x7F

    immediate = 0

    # I-type arithmetic, loads, JALR
    if opcode in (
        0b0010011,
        0b0000011,
        0b1100111,
    ):
        imm12 = (instruction >> 20) & 0xFFF
        immediate = sign_extend(imm12, 12)

    # S-type stores
    elif opcode == 0b0100011:

        imm_11_5 = (instruction >> 25) & 0x7F
        imm_4_0 = (instruction >> 7) & 0x1F

        imm12 = (
            (imm_11_5 << 5)
            | imm_4_0
        )

        immediate = sign_extend(imm12, 12)

    # B-type branches
    elif opcode == 0b1100011:

        imm_12 = (instruction >> 31) & 0x01
        imm_11 = (instruction >> 7) & 0x01
        imm_10_5 = (instruction >> 25) & 0x3F
        imm_4_1 = (instruction >> 8) & 0x0F

        imm13 = (
            (imm_12 << 12)
            | (imm_11 << 11)
            | (imm_10_5 << 5)
            | (imm_4_1 << 1)
        )

        immediate = sign_extend(imm13, 13)

    return {
        "opcode": opcode,
        "rd": rd,
        "funct3": funct3,
        "rs1": rs1,
        "rs2": rs2,
        "funct7": funct7,
        "immediate": immediate,
    }



async def check_r_type(
    dut,
    funct7,
    rs2,
    rs1,
    funct3,
    rd,
    opcode=0b0110011,
):
    """Encode and verify an R-type instruction."""

    instruction = encode_r_type(
        funct7=funct7,
        rs2=rs2,
        rs1=rs1,
        funct3=funct3,
        rd=rd,
        opcode=opcode,
    )

    dut.instruction.value = instruction

    await Timer(1, unit="ns")

    assert dut.opcode.value.to_unsigned() == opcode
    assert dut.rd.value.to_unsigned() == rd
    assert dut.rs1.value.to_unsigned() == rs1
    assert dut.rs2.value.to_unsigned() == rs2
    assert dut.funct3.value.to_unsigned() == funct3
    assert dut.funct7.value.to_unsigned() == funct7


async def compare_decoder(dut, instruction):
    """Compare the VHDL decoder against the Python reference model."""

    expected = decode_reference(instruction)

    dut.instruction.value = instruction

    await Timer(1, unit="ns")

    actual_opcode = dut.opcode.value.to_unsigned()
    actual_rd = dut.rd.value.to_unsigned()
    actual_funct3 = dut.funct3.value.to_unsigned()
    actual_rs1 = dut.rs1.value.to_unsigned()
    actual_rs2 = dut.rs2.value.to_unsigned()
    actual_funct7 = dut.funct7.value.to_unsigned()
    actual_immediate = dut.immediate.value.to_unsigned()

    assert actual_opcode == expected["opcode"], (
        f"Opcode mismatch: expected {expected['opcode']:07b}, "
        f"got {actual_opcode:07b}"
    )

    assert actual_rd == expected["rd"], (
        f"rd mismatch: expected {expected['rd']}, got {actual_rd}"
    )

    assert actual_funct3 == expected["funct3"], (
        f"funct3 mismatch: expected {expected['funct3']:03b}, "
        f"got {actual_funct3:03b}"
    )

    assert actual_rs1 == expected["rs1"], (
        f"rs1 mismatch: expected {expected['rs1']}, got {actual_rs1}"
    )

    assert actual_rs2 == expected["rs2"], (
        f"rs2 mismatch: expected {expected['rs2']}, got {actual_rs2}"
    )

    assert actual_funct7 == expected["funct7"], (
        f"funct7 mismatch: expected {expected['funct7']:07b}, "
        f"got {actual_funct7:07b}"
    )

    assert actual_immediate == expected["immediate"], (
        f"Immediate mismatch for instruction 0x{instruction:08X}: "
        f"expected 0x{expected['immediate']:08X}, "
        f"got 0x{actual_immediate:08X}"
    )


@cocotb.test()
async def test_add_instruction_decode(dut):
    """Decode ADD x5, x6, x7."""

    instruction = encode_r_type(
        funct7=0b0000000,
        rs2=7,
        rs1=6,
        funct3=0b000,
        rd=5,
        opcode=0b0110011,
    )

    dut.instruction.value = instruction

    await Timer(1, unit="ns")

    assert dut.opcode.value.to_unsigned() == 0b0110011
    assert dut.rd.value.to_unsigned() == 5
    assert dut.rs1.value.to_unsigned() == 6
    assert dut.rs2.value.to_unsigned() == 7
    assert dut.funct3.value.to_unsigned() == 0b000
    assert dut.funct7.value.to_unsigned() == 0b0000000


@cocotb.test()
async def test_sub_instruction_decode(dut):
    """Decode SUB x10, x11, x12."""

    instruction = encode_r_type(
        funct7=0b0100000,
        rs2=12,
        rs1=11,
        funct3=0b000,
        rd=10,
        opcode=0b0110011,
    )

    dut.instruction.value = instruction

    await Timer(1, unit="ns")

    assert dut.opcode.value.to_unsigned() == 0b0110011
    assert dut.rd.value.to_unsigned() == 10
    assert dut.rs1.value.to_unsigned() == 11
    assert dut.rs2.value.to_unsigned() == 12
    assert dut.funct3.value.to_unsigned() == 0b000
    assert dut.funct7.value.to_unsigned() == 0b0100000



@cocotb.test()
async def test_all_r_type_instructions(dut):
    """Verify the main RV32I R-type instruction encodings."""

    instructions = [
        # name, funct7, funct3
        ("ADD",  0b0000000, 0b000),
        ("SUB",  0b0100000, 0b000),
        ("SLL",  0b0000000, 0b001),
        ("SLT",  0b0000000, 0b010),
        ("SLTU", 0b0000000, 0b011),
        ("XOR",  0b0000000, 0b100),
        ("SRL",  0b0000000, 0b101),
        ("SRA",  0b0100000, 0b101),
        ("OR",   0b0000000, 0b110),
        ("AND",  0b0000000, 0b111),
    ]

    for name, funct7, funct3 in instructions:

        await check_r_type(
            dut,
            funct7=funct7,
            rs2=7,
            rs1=6,
            funct3=funct3,
            rd=5,
        )

        dut._log.info(
            f"{name} decoded correctly"
        )

@cocotb.test()
async def test_random_r_type(dut):
    """Randomized verification of R-type field decoding."""

    for _ in range(1000):

        funct7 = random.randint(0, 0x7F)
        rs2 = random.randint(0, 31)
        rs1 = random.randint(0, 31)
        funct3 = random.randint(0, 7)
        rd = random.randint(0, 31)

        instruction = encode_r_type(
            funct7=funct7,
            rs2=rs2,
            rs1=rs1,
            funct3=funct3,
            rd=rd,
            opcode=0b0110011,
        )

        await compare_decoder(dut, instruction)


@cocotb.test()
async def test_addi_instruction(dut):
    """Decode ADDI x5, x6, 10."""

    instruction = encode_i_type(
        immediate=10,
        rs1=6,
        funct3=0b000,
        rd=5,
        opcode=0b0010011,
    )

    dut.instruction.value = instruction

    await Timer(1, unit="ns")

    assert dut.opcode.value.to_unsigned() == 0b0010011
    assert dut.rd.value.to_unsigned() == 5
    assert dut.rs1.value.to_unsigned() == 6
    assert dut.funct3.value.to_unsigned() == 0b000

    assert dut.immediate.value.to_unsigned() == 10


@cocotb.test()
async def test_negative_immediate(dut):
    """Verify sign extension of a negative I-type immediate."""

    instruction = encode_i_type(
        immediate=-5,
        rs1=10,
        funct3=0b000,
        rd=9,
        opcode=0b0010011,
    )

    dut.instruction.value = instruction

    await Timer(1, unit="ns")

    assert dut.rd.value.to_unsigned() == 9
    assert dut.rs1.value.to_unsigned() == 10

    expected = (-5) & 0xFFFFFFFF

    actual = dut.immediate.value.to_unsigned()

    assert actual == expected, (
        f"Expected 0x{expected:08X}, "
        f"got 0x{actual:08X}"
    )


@cocotb.test()
async def test_random_i_type(dut):
    """Randomized verification of I-type decoding."""

    for _ in range(1000):

        immediate = random.randint(-2048, 2047)
        rs1 = random.randint(0, 31)
        funct3 = random.randint(0, 7)
        rd = random.randint(0, 31)

        instruction = encode_i_type(
            immediate=immediate,
            rs1=rs1,
            funct3=funct3,
            rd=rd,
            opcode=0b0010011,
        )

        await compare_decoder(dut, instruction)

@cocotb.test()
async def test_sw_instruction(dut):
    """Decode SW x7, 12(x6)."""

    instruction = encode_s_type(
        immediate=12,
        rs2=7,
        rs1=6,
        funct3=0b010,
    )

    dut.instruction.value = instruction

    await Timer(1, unit="ns")

    assert dut.opcode.value.to_unsigned() == 0b0100011
    assert dut.rs1.value.to_unsigned() == 6
    assert dut.rs2.value.to_unsigned() == 7
    assert dut.funct3.value.to_unsigned() == 0b010
    assert dut.immediate.value.to_unsigned() == 12

@cocotb.test()
async def test_negative_s_type_immediate(dut):
    """Verify negative S-type immediate sign extension."""

    instruction = encode_s_type(
        immediate=-16,
        rs2=8,
        rs1=10,
        funct3=0b010,
    )

    dut.instruction.value = instruction

    await Timer(1, unit="ns")

    expected = (-16) & 0xFFFFFFFF
    actual = dut.immediate.value.to_unsigned()

    assert dut.rs1.value.to_unsigned() == 10
    assert dut.rs2.value.to_unsigned() == 8

    assert actual == expected, (
        f"Expected 0x{expected:08X}, "
        f"got 0x{actual:08X}"
    )

@cocotb.test()
async def test_random_s_type(dut):
    """Randomized verification of S-type decoding."""

    for _ in range(1000):

        immediate = random.randint(-2048, 2047)
        rs1 = random.randint(0, 31)
        rs2 = random.randint(0, 31)
        funct3 = random.choice([
            0b000,  # SB
            0b001,  # SH
            0b010,  # SW
        ])

        instruction = encode_s_type(
            immediate=immediate,
            rs2=rs2,
            rs1=rs1,
            funct3=funct3,
        )

        await compare_decoder(dut, instruction)

@cocotb.test()
async def test_beq_instruction(dut):
    """Decode BEQ x5, x6, 16."""

    instruction = encode_b_type(
        immediate=16,
        rs2=6,
        rs1=5,
        funct3=0b000,
    )

    dut.instruction.value = instruction

    await Timer(1, unit="ns")

    assert dut.opcode.value.to_unsigned() == 0b1100011
    assert dut.rs1.value.to_unsigned() == 5
    assert dut.rs2.value.to_unsigned() == 6
    assert dut.funct3.value.to_unsigned() == 0b000
    assert dut.immediate.value.to_unsigned() == 16

@cocotb.test()
async def test_negative_branch_immediate(dut):
    """Verify a backwards branch offset."""

    instruction = encode_b_type(
        immediate=-8,
        rs2=4,
        rs1=3,
        funct3=0b001,
    )

    dut.instruction.value = instruction

    await Timer(1, unit="ns")

    expected = (-8) & 0xFFFFFFFF
    actual = dut.immediate.value.to_unsigned()

    assert dut.rs1.value.to_unsigned() == 3
    assert dut.rs2.value.to_unsigned() == 4
    assert dut.funct3.value.to_unsigned() == 0b001

    assert actual == expected, (
        f"Expected 0x{expected:08X}, "
        f"got 0x{actual:08X}"
    )

@cocotb.test()
async def test_all_branch_types(dut):
    """Verify the RV32I branch funct3 encodings."""

    branches = [
        ("BEQ",  0b000),
        ("BNE",  0b001),
        ("BLT",  0b100),
        ("BGE",  0b101),
        ("BLTU", 0b110),
        ("BGEU", 0b111),
    ]

    for name, funct3 in branches:

        instruction = encode_b_type(
            immediate=32,
            rs2=7,
            rs1=6,
            funct3=funct3,
        )

        dut.instruction.value = instruction

        await Timer(1, unit="ns")

        assert dut.opcode.value.to_unsigned() == 0b1100011
        assert dut.rs1.value.to_unsigned() == 6
        assert dut.rs2.value.to_unsigned() == 7
        assert dut.funct3.value.to_unsigned() == funct3
        assert dut.immediate.value.to_unsigned() == 32

        dut._log.info(
            f"{name} decoded correctly"
        )

@cocotb.test()
async def test_random_b_type(dut):
    """Randomized verification of B-type decoding."""

    valid_funct3 = [
        0b000,  # BEQ
        0b001,  # BNE
        0b100,  # BLT
        0b101,  # BGE
        0b110,  # BLTU
        0b111,  # BGEU
    ]

    for _ in range(1000):

        # B-type signed range is -4096 to +4094
        # and branch offsets are multiples of 2.
        immediate = random.randrange(-4096, 4096, 2)

        rs1 = random.randint(0, 31)
        rs2 = random.randint(0, 31)
        funct3 = random.choice(valid_funct3)

        instruction = encode_b_type(
            immediate=immediate,
            rs2=rs2,
            rs1=rs1,
            funct3=funct3,
        )

        await compare_decoder(dut, instruction)

@cocotb.test()
async def test_waveform_demo(dut):
    """Generate a short instruction-decoder waveform."""

    # ADD x5, x6, x7
    instruction = encode_r_type(
        funct7=0b0000000,
        rs2=7,
        rs1=6,
        funct3=0b000,
        rd=5,
        opcode=0b0110011,
    )

    dut.instruction.value = instruction
    await Timer(10, unit="ns")

    # ADDI x9, x10, -5
    instruction = encode_i_type(
        immediate=-5,
        rs1=10,
        funct3=0b000,
        rd=9,
        opcode=0b0010011,
    )

    dut.instruction.value = instruction
    await Timer(10, unit="ns")

    # SW x7, 12(x6)
    instruction = encode_s_type(
        immediate=12,
        rs2=7,
        rs1=6,
        funct3=0b010,
    )

    dut.instruction.value = instruction
    await Timer(10, unit="ns")

    # BEQ x5, x6, 16
    instruction = encode_b_type(
        immediate=16,
        rs2=6,
        rs1=5,
        funct3=0b000,
    )

    dut.instruction.value = instruction
    await Timer(10, unit="ns")