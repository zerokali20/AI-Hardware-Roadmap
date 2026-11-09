
module pipeline_integration (
    input logic clk,
    input logic rst,
    input logic stall_request,

    input logic [31:0] fetch_instruction,

    input logic [31:0] decode_rs1_data,
    input logic [31:0] decode_rs2_data,
    input logic [31:0] decode_immediate,
    input logic [6:0] decode_opcode,
    input logic [2:0] decode_funct3,
    input logic [6:0] decode_funct7,
    input logic [4:0] decode_rd,
    input logic decode_reg_write,
    input logic decode_mem_write,

    output logic [31:0] fetch_pc,
    output logic [31:0] if_id_pc,
    output logic [31:0] if_id_instruction,
    output logic [31:0] execute_pc,
    output logic [6:0] execute_opcode,
    output logic execute_reg_write,
    output logic execute_mem_write,

    output logic pc_redirect,
    output logic [31:0] pc_target,
    output logic if_id_flush,
    output logic id_ex_flush,
    output logic alignment_fault
);

    logic pc_stall;
    logic if_id_stall;
    logic id_ex_stall;

    logic branch_taken_ex;
    logic [31:0] branch_target_ex;
    logic invalid_branch_ex;

    logic [31:0] ex_rs1_data;
    logic [31:0] ex_rs2_data;
    logic [31:0] ex_immediate;
    logic [2:0] ex_funct3;

    program_counter pc_unit (
        .clk(clk),
        .rst(rst),
        .stall(pc_stall),
        .branch_taken(pc_redirect),
        .branch_target(pc_target),
        .pc(fetch_pc)
    );

    if_id_register if_id_unit (
        .clk(clk),
        .rst(rst),
        .stall(if_id_stall),
        .flush(if_id_flush),
        .pc_in(fetch_pc),
        .instruction_in(fetch_instruction),
        .pc_out(if_id_pc),
        .instruction_out(if_id_instruction)
    );

    id_ex_register id_ex_unit (
        .clk(clk),
        .rst(rst),
        .stall(id_ex_stall),
        .flush(id_ex_flush),

        .pc_in(if_id_pc),
        .rs1_data_in(decode_rs1_data),
        .rs2_data_in(decode_rs2_data),
        .immediate_in(decode_immediate),

        .rd_in(decode_rd),
        .rs1_in(5'b0),
        .rs2_in(5'b0),

        .funct3_in(decode_funct3),
        .funct7_in(decode_funct7),
        .opcode_in(decode_opcode),

        .reg_write_in(decode_reg_write),
        .mem_read_in(1'b0),
        .mem_write_in(decode_mem_write),
        .mem_to_reg_in(1'b0),
        .alu_src_in(1'b0),
        .branch_in(decode_opcode == 7'h63),
        .jump_in(
            (decode_opcode == 7'h6F) ||
            (decode_opcode == 7'h67)
        ),

        .pc_out(execute_pc),
        .rs1_data_out(ex_rs1_data),
        .rs2_data_out(ex_rs2_data),
        .immediate_out(ex_immediate),

        .rd_out(),
        .rs1_out(),
        .rs2_out(),
        .funct3_out(ex_funct3),
        .funct7_out(),
        .opcode_out(execute_opcode),

        .reg_write_out(execute_reg_write),
        .mem_read_out(),
        .mem_write_out(execute_mem_write),
        .mem_to_reg_out(),
        .alu_src_out(),
        .branch_out(),
        .jump_out()
    );

    branch_unit branch_unit_inst (
        .pc(execute_pc),
        .rs1_data(ex_rs1_data),
        .rs2_data(ex_rs2_data),
        .immediate(ex_immediate),
        .opcode(execute_opcode),
        .funct3(ex_funct3),

        .branch_taken(branch_taken_ex),
        .branch_target(branch_target_ex),
        .link_address(),
        .invalid_branch(invalid_branch_ex)
    );

    pipeline_control control_unit (
        .branch_taken_ex(branch_taken_ex),
        .branch_target_ex(branch_target_ex),
        .stall_request(stall_request),
        .invalid_branch_ex(invalid_branch_ex),

        .pc_stall(pc_stall),
        .pc_redirect(pc_redirect),
        .pc_target(pc_target),
        .if_id_stall(if_id_stall),
        .if_id_flush(if_id_flush),
        .id_ex_stall(id_ex_stall),
        .id_ex_flush(id_ex_flush),
        .alignment_fault(alignment_fault)
    );

endmodule
