
module execute_forwarding_stage (
    input logic clk, rst, stall, flush,

    input logic [31:0] pc_in,
    input logic [31:0] rs1_data_in, rs2_data_in,
    input logic [31:0] immediate_in,
    input logic [4:0] rd_in, rs1_in, rs2_in,
    input logic [2:0] funct3_in,
    input logic [6:0] funct7_in, opcode_in,

    input logic reg_write_in, mem_read_in,
    input logic mem_write_in, mem_to_reg_in,
    input logic alu_src_in, branch_in, jump_in,

    input logic [31:0] ex_mem_forward_data,
    input logic [4:0] ex_mem_rd,
    input logic ex_mem_reg_write,
    input logic ex_mem_mem_to_reg,

    input logic [31:0] mem_wb_forward_data,
    input logic [4:0] mem_wb_rd,
    input logic mem_wb_reg_write,

    output logic [31:0] alu_result,
    output logic [31:0] store_data,
    output logic [31:0] execute_pc,
    output logic [4:0] execute_rd,
    output logic [2:0] execute_funct3,

    output logic execute_reg_write,
    output logic execute_mem_read,
    output logic execute_mem_write,
    output logic execute_mem_to_reg,
    output logic execute_jump,

    output logic alu_zero, alu_less_than,
    output logic invalid_operation,
    output logic branch_taken,
    output logic [31:0] branch_target,
    output logic [31:0] link_address,
    output logic invalid_branch,

    output logic [1:0] forward_a, forward_b,
    output logic unresolved_load_dependency
);

    logic [31:0] rs1_value, rs2_value, imm_value;
    logic [31:0] operand_a, forwarded_rs2, operand_b;
    logic [4:0] rs1_addr, rs2_addr;
    logic [2:0] funct3_value;
    logic [6:0] funct7_value, opcode_value;
    logic alu_src_value, branch_value, jump_value;
    logic [3:0] alu_operation;
    logic raw_invalid_operation;
    logic uses_rs1, uses_rs2;

    logic [1:0] raw_forward_a, raw_forward_b;

    id_ex_register pipeline_reg (
        .clk(clk), .rst(rst), .stall(stall), .flush(flush),
        .pc_in(pc_in),
        .rs1_data_in(rs1_data_in),
        .rs2_data_in(rs2_data_in),
        .immediate_in(immediate_in),
        .rd_in(rd_in), .rs1_in(rs1_in), .rs2_in(rs2_in),
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
        .immediate_out(imm_value),
        .rd_out(execute_rd),
        .rs1_out(rs1_addr),
        .rs2_out(rs2_addr),
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

    assign execute_funct3 = funct3_value;
    assign execute_jump = jump_value;

    always_comb begin
        uses_rs1 = 1'b0;
        uses_rs2 = 1'b0;

        case (opcode_value)
            7'b0110011, // R-type
            7'b0100011, // Store
            7'b1100011: begin // Branch
                uses_rs1 = 1'b1;
                uses_rs2 = 1'b1;
            end

            7'b0010011, // I-type
            7'b0000011, // Load
            7'b1100111: begin // JALR
                uses_rs1 = 1'b1;
            end

            default: begin
            end
        endcase
    end

    forwarding_unit forwarding_unit_inst (
        .id_ex_rs1(rs1_addr),
        .id_ex_rs2(rs2_addr),
        .ex_mem_rd(ex_mem_rd),
        .ex_mem_reg_write(ex_mem_reg_write),
        .ex_mem_mem_to_reg(ex_mem_mem_to_reg),
        .mem_wb_rd(mem_wb_rd),
        .mem_wb_reg_write(mem_wb_reg_write),
        .forward_a(raw_forward_a),
        .forward_b(raw_forward_b)
    );

    assign forward_a = uses_rs1 ? raw_forward_a : 2'b00;
    assign forward_b = uses_rs2 ? raw_forward_b : 2'b00;

    always_comb begin
        operand_a = rs1_value;
        forwarded_rs2 = rs2_value;
         // Forward register operands when needed.
        case (forward_a)
            2'b01: operand_a = mem_wb_forward_data;
            2'b10: operand_a = ex_mem_forward_data;
            default: begin
            end
        endcase

        case (forward_b)
            2'b01: forwarded_rs2 = mem_wb_forward_data;
            2'b10: forwarded_rs2 = ex_mem_forward_data;
            default: begin
            end
        endcase
        // LUI and AUIPC use special ALU operand A values.
        case (opcode_value)
            7'b0110111: operand_a=32'b0; //LUI
            7'b0010111: operand_a=execute_pc; //AUIPC
            default: begin
            end
        endcase
    end

    assign operand_b = alu_src_value
                     ? imm_value : forwarded_rs2;

    assign store_data = forwarded_rs2;

    // A newer load in EX/MEM cannot supply its value
    // through the EX/MEM ALU forwarding path.
    assign unresolved_load_dependency =
        ex_mem_reg_write &&
        ex_mem_mem_to_reg &&
        ex_mem_rd != 5'd0 &&
        ((uses_rs1 && rs1_addr == ex_mem_rd) ||
         (uses_rs2 && rs2_addr == ex_mem_rd));

    alu_control control_unit (
        .opcode(opcode_value),
        .funct3(funct3_value),
        .funct7(funct7_value),
        .alu_op(alu_operation),
        .invalid_operation(raw_invalid_operation)
    );

    alu execution_alu (
        .a(operand_a),
        .b(operand_b),
        .alu_control(alu_operation),
        .result(alu_result),
        .zero(alu_zero),
        .less_than(alu_less_than)
    );

    assign invalid_operation =
        (opcode_value != 7'b0000000) &&
        raw_invalid_operation;

    branch_unit branch_jump_unit (
        .pc(execute_pc),
        .rs1_data(operand_a),
        .rs2_data(forwarded_rs2),
        .immediate(imm_value),
        .opcode(opcode_value),
        .funct3(funct3_value),
        .branch_taken(branch_taken),
        .branch_target(branch_target),
        .link_address(link_address),
        .invalid_branch(invalid_branch)
    );

endmodule
