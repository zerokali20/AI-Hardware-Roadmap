// =============================================================================
// PipeGuard-RV — Formal Properties for M1 (branch_monitor)
//
// Proves (bounded model checking via yosys-smtbmc / SymbiYosys):
//   Mode ASSUME_CLEAN=0 (unconstrained inputs):
//     1. Reset suppression & sticky persistence
//     2. Invalid observation responses (misaligned, OOB, spurious redirect,
//        target mismatch, non-seq/non-hold jump without redirect)
//   Mode ASSUME_CLEAN=1 (valid RV32I sequential/redirect/hold assumptions):
//     3. Zero false positives (!fault_detected && !fault_sticky)
// =============================================================================
`include "pipeguard_defs.svh"

module m1_formal #(
    parameter bit          ASSUME_CLEAN = 1'b0,
    parameter logic [31:0] PC_MIN       = 32'h0000_0000,
    parameter logic [31:0] PC_MAX       = 32'h0000_03FC
) (
    input logic        clk,
    input logic        rst,
    input logic [31:0] fetch_pc,
    input logic        branch_redirect,
    input logic [31:0] pc_target,
    input logic        branch_taken,
    input logic [31:0] branch_target,
    input logic        invalid_branch,
    input logic        alignment_fault
);

    logic                         fault_detected;
    logic                         fault_sticky;
    logic [`PG_FAULT_CLASS_W-1:0] fault_class;

    branch_monitor #(
        .PC_MIN (PC_MIN),
        .PC_MAX (PC_MAX)
    ) dut (
        .clk             (clk),
        .rst             (rst),
        .fetch_pc        (fetch_pc),
        .branch_redirect (branch_redirect),
        .pc_target       (pc_target),
        .branch_taken    (branch_taken),
        .branch_target   (branch_target),
        .invalid_branch  (invalid_branch),
        .alignment_fault (alignment_fault),
        .fault_detected  (fault_detected),
        .fault_sticky    (fault_sticky),
        .fault_class     (fault_class)
    );

    logic                         f_past_valid;
    logic                         f_prev_rst;
    logic                         f_prev_detected;
    logic                         f_prev_sticky;
    logic [`PG_FAULT_CLASS_W-1:0] f_prev_class;
    logic [31:0]                  f_prev_pc;
    logic                         f_prev_redirect;
    logic [31:0]                  f_prev_pc_target;

    initial f_past_valid = 1'b0;

    always @(posedge clk) begin
        f_past_valid     <= 1'b1;
        f_prev_rst       <= rst;
        f_prev_detected  <= fault_detected;
        f_prev_sticky    <= fault_sticky;
        f_prev_class     <= fault_class;
        f_prev_pc        <= fetch_pc;
        f_prev_redirect  <= branch_redirect;
        f_prev_pc_target <= pc_target;
    end

    always @(*) begin
        if (!f_past_valid) assume(rst);
    end

    // Clean environment assumptions (models legal pipeline_control + program_counter)
    always @(*) begin
        if (ASSUME_CLEAN) begin
            assume(alignment_fault == (branch_taken && !invalid_branch && (branch_target[1:0] != 2'b00)));
            assume(branch_redirect == (branch_taken && !invalid_branch && !alignment_fault));
            assume(pc_target == branch_target);
            if (!rst) begin
                assume(fetch_pc[1:0] == 2'b00);
                assume(fetch_pc >= PC_MIN && fetch_pc <= PC_MAX);
                if (f_past_valid) begin
                    if (f_prev_rst)
                        assume(fetch_pc == 32'h0000_0000);
                    else if (f_prev_redirect)
                        assume(fetch_pc == f_prev_pc_target);
                    else
                        assume((fetch_pc == f_prev_pc + 32'd4) || (fetch_pc == f_prev_pc));
                end
            end
        end
    end

    always @(*) begin
        if (rst) begin
            assert(!fault_detected);
        end
        else begin
            // Invalid observations must assert fault_detected
            if (fetch_pc[1:0] != 2'b00 || fetch_pc < PC_MIN || fetch_pc > PC_MAX)
                assert(fault_detected);
            if (branch_redirect && (!branch_taken || invalid_branch || alignment_fault ||
                                    pc_target != branch_target || branch_target[1:0] != 2'b00))
                assert(fault_detected);
            if (f_past_valid && !f_prev_rst && !f_prev_redirect &&
                (fetch_pc != f_prev_pc + 32'd4) && (fetch_pc != f_prev_pc))
                assert(fault_detected);
        end

        if (ASSUME_CLEAN) begin
            assert(!fault_detected);
        end
    end

    always @(posedge clk) begin
        if (f_past_valid) begin
            if (f_prev_rst) begin
                assert(!fault_sticky);
                assert(fault_class == `PG_FC_NONE);
            end
            else if (f_prev_sticky) begin
                assert(fault_sticky);
                assert(fault_class == f_prev_class);
            end
            else if (f_prev_detected) begin
                assert(fault_sticky);
                assert(fault_class != `PG_FC_NONE);
            end
            else begin
                assert(!fault_sticky);
                assert(fault_class == `PG_FC_NONE);
            end

            if (ASSUME_CLEAN) begin
                assert(!fault_sticky);
                assert(fault_class == `PG_FC_NONE);
            end
        end
    end

endmodule
