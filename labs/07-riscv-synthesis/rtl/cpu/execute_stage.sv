
module execute_stage (
    input  logic        clk,
    input  logic        rst,
    input  logic        stall,
    input  logic        flush,

    input  logic [31:0] pc_in,
    input  logic [31:0] rs1_data_in,
    input  logic [31:0] rs2_data_in,
    input  logic [31:0] immediate_in,

    input  logic [4:0]  rd_in,
    input  logic [4:0]  rs1_in,
    input  logic [4:0]  rs2_in,
    input  logic [2:0]  funct3_in,
    input  logic [6:0]  funct7_in,
    input  logic [6:0]  opcode_in,

    input  logic        reg_write_in,
    input  logic        mem_read_in,
    input  logic        mem_write_in,
    input  logic        mem_to_reg_in,
    input  logic        alu_src_in,
    input  logic        branch_in,
    input  logic        jump_in,

    output logic [31:0] alu_result,
    output logic [31:0] store_data,
    output logic [31:0] execute_pc,
    output logic [4:0]  execute_rd,

    output logic        execute_reg_write,
    output logic        execute_mem_read,
    output logic        execute_mem_write,
    output logic        execute_mem_to_reg,

    output logic        alu_zero,
    output logic        alu_less_than,
    output logic        invalid_operation,
    output logic	    branch_taken,
    output logic [31:0] branch_target,
    output logic [31:0] link_address,
    output logic	    invalid_branch

);

    logic [31:0] rs1_value;
    logic [31:0] rs2_value;
    logic [31:0] immediate_value;

    logic [4:0] rd_value;
    logic [4:0] rs1_value_addr;
    logic [4:0] rs2_value_addr;

    logic [2:0] funct3_value;
    logic [6:0] funct7_value;
    logic [6:0] opcode_value;

    logic alu_src_value;
    logic branch_value;
    logic jump_value;

    logic [31:0] operand_b;
    logic [3:0]  alu_operation;
    logic raw_invalid_operation;    

    id_ex_register pipeline_reg (
        .clk(clk),
        .rst(rst),
        .stall(stall),
        .flush(flush),

        .pc_in(pc_in),
        .rs1_data_in(rs1_data_in),
        .rs2_data_in(rs2_data_in),
        .immediate_in(immediate_in),

        .rd_in(rd_in),
        .rs1_in(rs1_in),
        .rs2_in(rs2_in),
        .funct3_in(funct3_in),
        .funct7_in(funct7_in),
        .opcode_in(opcode_in),

        .reg_write_in(reg_write_in),
        .mem_read_in(mem_read_in),
        .mem_write_in(mem_write_in),
        .mem_to_reg_in(mem_to_reg_in),
        .alu_src_in(alu_src_in),
        .branch_in(branch_in),
        .jump_in(jump_in),

        .pc_out(execute_pc),
        .rs1_data_out(rs1_value),
        .rs2_data_out(rs2_value),
        .immediate_out(immediate_value),

        .rd_out(rd_value),
        .rs1_out(rs1_value_addr),
        .rs2_out(rs2_value_addr),
        .funct3_out(funct3_value),
        .funct7_out(funct7_value),
        .opcode_out(opcode_value),

        .reg_write_out(execute_reg_write),
        .mem_read_out(execute_mem_read),
        .mem_write_out(execute_mem_write),
        .mem_to_reg_out(execute_mem_to_reg),
        .alu_src_out(alu_src_value),
        .branch_out(branch_value),
        .jump_out(jump_value)
    );

    alu_control control_unit (
        .opcode(opcode_value),
        .funct3(funct3_value),
        .funct7(funct7_value),
        .alu_op(alu_operation),
        .invalid_operation(raw_invalid_operation)
    );

    assign operand_b = alu_src_value
                     ? immediate_value
                     : rs2_value;

    alu execution_alu (
        .a(rs1_value),
        .b(operand_b),
        .alu_control(alu_operation),
        .result(alu_result),
        .zero(alu_zero),
        .less_than(alu_less_than)
    );

    assign store_data = rs2_value;
    assign execute_rd = rd_value;
    assign invalid_operation = (opcode_value != 7'b0000000) && raw_invalid_operation;

    branch_unit branch_jump_unit (
    	.pc(execute_pc),
    	.rs1_data(rs1_value),
    	.rs2_data(rs2_value),
    	.immediate(immediate_value),

    	.opcode(opcode_value),
    	.funct3(funct3_value),

    	.branch_taken(branch_taken),
    	.branch_target(branch_target),
    	.link_address(link_address),
    	.invalid_branch(invalid_branch)
    );

endmodule
