
module if_id_stage (
    input  logic        clk,
    input  logic        rst,
    input  logic        stall,
    input  logic        branch_taken,
    input  logic [31:0] branch_target,

    // Register file writeback interface
    input  logic        wb_enable,
    input  logic [4:0]  wb_addr,
    input  logic [31:0] wb_data,

    // Fetch outputs
    output logic [31:0] fetch_pc,
    output logic [31:0] fetch_instruction,

    // Decode-stage outputs
    output logic [31:0] decode_pc,
    output logic [31:0] decode_instruction,
    output logic [31:0] immediate,
    output logic [31:0] rs1_data,
    output logic [31:0] rs2_data,

    output logic [4:0]  rd,
    output logic [4:0]  rs1,
    output logic [4:0]  rs2,
    output logic [2:0]  funct3,
    output logic [6:0]  funct7,
    output logic [6:0]  opcode,

    output logic        reg_write,
    output logic        mem_read,
    output logic        mem_write,
    output logic        mem_to_reg,
    output logic        alu_src,
    output logic        branch,
    output logic        jump,
    output logic        illegal_instruction
);

    instruction_fetch fetch_unit (
        .clk(clk),
        .rst(rst),
        .stall(stall),
        .branch_taken(branch_taken),
        .branch_target(branch_target),
        .pc(fetch_pc),
        .instruction(fetch_instruction)
    );

    if_id_register pipeline_reg (
        .clk(clk),
        .rst(rst),
        .stall(stall),
        .flush(branch_taken),
        .pc_in(fetch_pc),
        .instruction_in(fetch_instruction),
        .pc_out(decode_pc),
        .instruction_out(decode_instruction)
    );

    rv32i_decoder decoder (
        .instruction(decode_instruction),
        .opcode(opcode),
        .rd(rd),
        .rs1(rs1),
        .rs2(rs2),
        .funct3(funct3),
        .funct7(funct7),
        .reg_write(reg_write),
        .mem_read(mem_read),
        .mem_write(mem_write),
        .mem_to_reg(mem_to_reg),
        .alu_src(alu_src),
        .branch(branch),
        .jump(jump),
        .illegal_instruction(illegal_instruction)
    );

    immediate_generator imm_unit (
        .instruction(decode_instruction),
        .immediate(immediate)
    );

    register_file regfile (
        .clk(clk),
        .rst(rst),
        .reg_write(wb_enable),
        .write_addr(wb_addr),
        .write_data(wb_data),
        .read_addr1(rs1),
        .read_addr2(rs2),
        .read_data1(rs1_data),
        .read_data2(rs2_data)
    );

endmodule
