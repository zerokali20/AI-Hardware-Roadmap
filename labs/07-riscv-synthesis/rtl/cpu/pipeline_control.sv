
module pipeline_control (
    input  logic        branch_taken_ex,
    input  logic [31:0] branch_target_ex,
    input  logic        stall_request,
    input  logic        invalid_branch_ex,

    output logic        pc_stall,
    output logic        pc_redirect,
    output logic [31:0] pc_target,
    output logic        if_id_stall,
    output logic        if_id_flush,
    output logic        id_ex_stall,
    output logic        id_ex_flush,
    output logic        alignment_fault
);

    logic valid_redirect;

    always_comb begin
        valid_redirect = branch_taken_ex &&
                         !invalid_branch_ex;

        alignment_fault = valid_redirect &&
                          (branch_target_ex[1:0] != 2'b00);

        pc_redirect = valid_redirect && !alignment_fault;
        pc_target   = branch_target_ex;

        // Default operation
        pc_stall    = stall_request;
        if_id_stall = stall_request;
        if_id_flush = 1'b0;
        id_ex_stall = 1'b0;
        id_ex_flush = stall_request;

        // Taken branch or jump has priority over stalls.
        if (pc_redirect) begin
            pc_stall    = 1'b0;
            if_id_stall = 1'b0;
            if_id_flush = 1'b1;
            id_ex_stall = 1'b0;
            id_ex_flush = 1'b1;
        end

        // Misaligned targets are reported, not redirected.
        // Exception handling will be added later.
        if (alignment_fault) begin
            pc_stall    = 1'b1;
            if_id_stall = 1'b1;
            if_id_flush = 1'b0;
            id_ex_stall = 1'b0;
            id_ex_flush = 1'b1;
        end
    end

endmodule

