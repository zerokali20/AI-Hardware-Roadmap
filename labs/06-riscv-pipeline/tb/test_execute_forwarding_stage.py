
import cocotb
from cocotb.triggers import Timer

ADD = 0b0110011
ADDI = 0b0010011
LOAD = 0b0000011
STORE = 0b0100011
BRANCH = 0b1100011
JALR = 0b1100111
JAL = 0b1101111


async def tick(dut):
    dut.clk.value = 0
    await Timer(5, unit="ns")
    dut.clk.value = 1
    await Timer(5, unit="ns")
    dut.clk.value = 0
    await Timer(1, unit="ns")


async def settle():
    await Timer(1, unit="ns")


def drive(dut, **values):
    for name, value in values.items():
        getattr(dut, name).value = value


def check(dut, **expected):
    for name, value in expected.items():
        actual = int(getattr(dut, name).value)
        assert actual == value, (
            f"{name}: expected {value:#x}, got {actual:#x}"
        )


async def initialize(dut):
    drive(
        dut,
        clk=0, rst=1, stall=0, flush=0,
        pc_in=0, rs1_data_in=0, rs2_data_in=0,
        immediate_in=0, rd_in=0, rs1_in=0, rs2_in=0,
        funct3_in=0, funct7_in=0, opcode_in=0,
        reg_write_in=0, mem_read_in=0,
        mem_write_in=0, mem_to_reg_in=0,
        alu_src_in=0, branch_in=0, jump_in=0,
        ex_mem_forward_data=0,
        ex_mem_rd=0,
        ex_mem_reg_write=0,
        ex_mem_mem_to_reg=0,
        mem_wb_forward_data=0,
        mem_wb_rd=0,
        mem_wb_reg_write=0,
    )
    await tick(dut)
    dut.rst.value = 0
    await settle()


async def issue(dut, **values):
    drive(
        dut,
        pc_in=0, rs1_data_in=0, rs2_data_in=0,
        immediate_in=0, rd_in=0, rs1_in=0, rs2_in=0,
        funct3_in=0, funct7_in=0, opcode_in=0,
        reg_write_in=0, mem_read_in=0,
        mem_write_in=0, mem_to_reg_in=0,
        alu_src_in=0, branch_in=0, jump_in=0,
    )
    drive(dut, **values)
    await tick(dut)


@cocotb.test()
async def test_normal_add(dut):
    await initialize(dut)
    await issue(
        dut, opcode_in=ADD,
        rs1_data_in=10, rs2_data_in=20
    )
    check(dut, alu_result=30, forward_a=0, forward_b=0)


@cocotb.test()
async def test_ex_mem_forward_rs1(dut):
    await initialize(dut)
    drive(
        dut, ex_mem_rd=5,
        ex_mem_reg_write=1,
        ex_mem_forward_data=100
    )
    await issue(
        dut, opcode_in=ADD,
        rs1_in=5, rs2_in=6,
        rs1_data_in=1, rs2_data_in=20
    )
    check(dut, forward_a=2, alu_result=120)


@cocotb.test()
async def test_ex_mem_forward_rs2(dut):
    await initialize(dut)
    drive(
        dut, ex_mem_rd=6,
        ex_mem_reg_write=1,
        ex_mem_forward_data=30
    )
    await issue(
        dut, opcode_in=ADD,
        rs1_in=5, rs2_in=6,
        rs1_data_in=10, rs2_data_in=1
    )
    check(dut, forward_b=2, alu_result=40)


@cocotb.test()
async def test_mem_wb_forward_rs1(dut):
    await initialize(dut)
    drive(
        dut, mem_wb_rd=5,
        mem_wb_reg_write=1,
        mem_wb_forward_data=50
    )
    await issue(
        dut, opcode_in=ADD,
        rs1_in=5, rs2_in=6,
        rs1_data_in=1, rs2_data_in=7
    )
    check(dut, forward_a=1, alu_result=57)


@cocotb.test()
async def test_two_forwarding_sources(dut):
    await initialize(dut)
    drive(
        dut,
        ex_mem_rd=5,
        ex_mem_reg_write=1,
        ex_mem_forward_data=30,
        mem_wb_rd=6,
        mem_wb_reg_write=1,
        mem_wb_forward_data=40
    )
    await issue(
        dut, opcode_in=ADD,
        rs1_in=5, rs2_in=6
    )
    check(dut, forward_a=2, forward_b=1, alu_result=70)


@cocotb.test()
async def test_ex_mem_priority(dut):
    await initialize(dut)
    drive(
        dut,
        ex_mem_rd=5,
        ex_mem_reg_write=1,
        ex_mem_forward_data=100,
        mem_wb_rd=5,
        mem_wb_reg_write=1,
        mem_wb_forward_data=20
    )
    await issue(
        dut, opcode_in=ADD,
        rs1_in=5, rs2_data_in=1
    )
    check(dut, forward_a=2, alu_result=101)


@cocotb.test()
async def test_immediate_preserved(dut):
    await initialize(dut)
    drive(
        dut, ex_mem_rd=5,
        ex_mem_reg_write=1,
        ex_mem_forward_data=20
    )
    await issue(
        dut, opcode_in=ADDI,
        rs1_in=5, rs2_in=5,
        immediate_in=7,
        alu_src_in=1
    )
    check(
        dut, forward_a=2, forward_b=0,
        alu_result=27
    )


@cocotb.test()
async def test_store_data_forwarding(dut):
    await initialize(dut)
    drive(
        dut, mem_wb_rd=6,
        mem_wb_reg_write=1,
        mem_wb_forward_data=0x12345678
    )
    await issue(
        dut, opcode_in=STORE,
        rs1_data_in=100,
        rs2_in=6,
        immediate_in=8,
        alu_src_in=1,
        mem_write_in=1
    )
    check(
        dut,
        alu_result=108,
        store_data=0x12345678,
        forward_b=1
    )


@cocotb.test()
async def test_branch_forwarding(dut):
    await initialize(dut)
    drive(
        dut, ex_mem_rd=5,
        ex_mem_reg_write=1,
        ex_mem_forward_data=10
    )
    await issue(
        dut, opcode_in=BRANCH,
        pc_in=0x100,
        rs1_in=5, rs2_in=6,
        rs1_data_in=0,
        rs2_data_in=10,
        immediate_in=16,
        funct3_in=0
    )
    check(
        dut,
        branch_taken=1,
        branch_target=0x110,
        forward_a=2
    )


@cocotb.test()
async def test_jalr_forwarding(dut):
    await initialize(dut)
    drive(
        dut, mem_wb_rd=5,
        mem_wb_reg_write=1,
        mem_wb_forward_data=0x200
    )
    await issue(
        dut, opcode_in=JALR,
        pc_in=0x100,
        rs1_in=5,
        immediate_in=12,
        alu_src_in=1,
        jump_in=1
    )
    check(
        dut,
        branch_taken=1,
        branch_target=0x20C,
        link_address=0x104,
        forward_a=1
    )


@cocotb.test()
async def test_newer_load_dependency(dut):
    await initialize(dut)
    drive(
        dut,
        ex_mem_rd=5,
        ex_mem_reg_write=1,
        ex_mem_mem_to_reg=1,
        mem_wb_rd=5,
        mem_wb_reg_write=1,
        mem_wb_forward_data=99
    )
    await issue(
        dut, opcode_in=ADD,
        rs1_in=5, rs2_data_in=1
    )
    check(
        dut,
        forward_a=0,
        unresolved_load_dependency=1
    )


@cocotb.test()
async def test_unused_source_ignored(dut):
    await initialize(dut)
    drive(
        dut, ex_mem_rd=5,
        ex_mem_reg_write=1,
        ex_mem_forward_data=99
    )
    await issue(
        dut, opcode_in=JAL,
        rs1_in=5, rs2_in=5,
        pc_in=0x100,
        immediate_in=16,
        jump_in=1
    )
    check(
        dut,
        forward_a=0,
        forward_b=0,
        unresolved_load_dependency=0,
        branch_target=0x110
    )


@cocotb.test()
async def test_zero_register_not_forwarded(dut):
    await initialize(dut)
    drive(
        dut, ex_mem_rd=0,
        ex_mem_reg_write=1,
        ex_mem_forward_data=999
    )
    await issue(
        dut, opcode_in=ADD,
        rs1_in=0, rs2_in=0,
        rs1_data_in=0, rs2_data_in=0
    )
    check(dut, forward_a=0, forward_b=0, alu_result=0)


@cocotb.test()
async def test_flush_clears_instruction(dut):
    await initialize(dut)
    await issue(
        dut, opcode_in=ADD,
        rs1_data_in=10,
        rs2_data_in=20,
        reg_write_in=1
    )

    dut.flush.value = 1
    await tick(dut)

    check(
        dut,
        execute_reg_write=0,
        execute_rd=0,
        forward_a=0,
        forward_b=0
    )
