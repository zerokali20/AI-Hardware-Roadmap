
module hazard_forwarding_integration (
    input  logic [4:0] if_id_rs1,
    input  logic [4:0] if_id_rs2,
    input  logic [6:0] if_id_opcode,

    input  logic [4:0] id_ex_rs1,
    input  logic [4:0] id_ex_rs2,
    input  logic [4:0] id_ex_rd,
    input  logic       id_ex_mem_read,

    input  logic [4:0] ex_mem_rd,
    input  logic       ex_mem_reg_write,
    input  logic       ex_mem_mem_to_reg,

    input  logic [4:0] mem_wb_rd,
    input  logic       mem_wb_reg_write,

    input  logic        branch_taken_ex,
    input  logic [31:0] branch_target_ex,
    input  logic        invalid_branch_ex,

    output logic [1:0] forward_a,
    output logic [1:0] forward_b,
    output logic       stall_request,

    output logic        pc_stall,
    output logic        pc_redirect,
    output logic [31:0] pc_target,
    output logic        if_id_stall,
    output logic        if_id_flush,
    output logic        id_ex_stall,
    output logic        id_ex_flush,
    output logic        alignment_fault
);

    hazard_detection_unit hazard_unit (
        .id_ex_rd(id_ex_rd),
        .id_ex_mem_read(id_ex_mem_read),
        .if_id_rs1(if_id_rs1),
        .if_id_rs2(if_id_rs2),
        .if_id_opcode(if_id_opcode),
        .stall_request(stall_request)
    );

    forwarding_unit forwarding_unit_inst (
        .id_ex_rs1(id_ex_rs1),
        .id_ex_rs2(id_ex_rs2),

        .ex_mem_rd(ex_mem_rd),
        .ex_mem_reg_write(ex_mem_reg_write),
        .ex_mem_mem_to_reg(ex_mem_mem_to_reg),

        .mem_wb_rd(mem_wb_rd),
        .mem_wb_reg_write(mem_wb_reg_write),

        .forward_a(forward_a),
        .forward_b(forward_b)
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
