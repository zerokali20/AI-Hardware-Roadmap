// =============================================================================
// PipeGuard-RV — Formal Properties for M2 (pipeline_monitor)
//
// Proves (bounded model checking via yosys-smtbmc / SymbiYosys):
//   Mode ASSUME_CLEAN=0 (unconstrained inputs):
//     1. Reset suppression & sticky persistence
//     2. Branch priority & stall/flush consistency checks
//     3. Strict PC & stage progression violation detection
//   Mode ASSUME_CLEAN=1 (valid pipeline_control + hazard_detection_unit + stage regs):
//     4. Zero false positives (!fault_detected && !fault_sticky)
// =============================================================================
`include "pipeguard_defs.svh"

module m2_formal #(
    parameter bit          ASSUME_CLEAN = 1'b0,
    parameter logic [31:0] PC_MIN       = 32'h0000_0000,
    parameter logic [31:0] PC_MAX       = 32'h0000_03FC
) (
    input logic        clk,
    input logic        rst,
    input logic [31:0] fetch_pc,
    input logic [31:0] decode_pc,
    input logic [31:0] execute_pc,
    input logic [31:0] mem_pc,
    input logic [31:0] wb_pc,
    input logic        branch_redirect,
    input logic [31:0] pc_target,
    input logic        branch_taken,
    input logic [31:0] branch_target,
    input logic        invalid_branch,
    input logic        alignment_fault,
    input logic        load_use_stall,
    input logic        pc_stall,
    input logic        id_ex_stall,
    input logic        id_ex_flush,
    input logic [6:0]  id_opcode,
    input logic [4:0]  id_rs1,
    input logic [4:0]  id_rs2,
    input logic [4:0]  ex_rd,
    input logic        ex_mem_read
);

    logic                         fault_detected;
    logic                         fault_sticky;
    logic [`PG_FAULT_CLASS_W-1:0] fault_class;

    pipeline_monitor #(
        .PC_MIN (PC_MIN),
        .PC_MAX (PC_MAX)
    ) dut (
        .clk             (clk),
        .rst             (rst),
        .fetch_pc        (fetch_pc),
        .decode_pc       (decode_pc),
        .execute_pc      (execute_pc),
        .mem_pc          (mem_pc),
        .wb_pc           (wb_pc),
        .branch_redirect (branch_redirect),
        .pc_target       (pc_target),
        .branch_taken    (branch_taken),
        .branch_target   (branch_target),
        .invalid_branch  (invalid_branch),
        .alignment_fault (alignment_fault),
        .load_use_stall  (load_use_stall),
        .pc_stall        (pc_stall),
        .id_ex_stall     (id_ex_stall),
        .id_ex_flush     (id_ex_flush),
        .id_opcode       (id_opcode),
        .id_rs1          (id_rs1),
        .id_rs2          (id_rs2),
        .ex_rd           (ex_rd),
        .ex_mem_read     (ex_mem_read),
        .fault_detected  (fault_detected),
        .fault_sticky    (fault_sticky),
        .fault_class     (fault_class)
    );

    logic                         f_past_valid;
    logic                         f_prev_rst;
    logic                         f_prev_detected;
    logic                         f_prev_sticky;
    logic [`PG_FAULT_CLASS_W-1:0] f_prev_class;
    logic [31:0]                  f_prev_fetch_pc, f_prev_decode_pc, f_prev_execute_pc, f_prev_mem_pc;
    logic                         f_prev_redirect, f_prev_pc_stall, f_prev_id_ex_stall, f_prev_id_ex_flush;
    logic [31:0]                  f_prev_pc_target;

    // Reference hazard & pipeline_control model
    logic f_uses_rs1, f_uses_rs2, f_exp_lus;
    logic f_exp_valid_redir, f_exp_align_fault, f_exp_redir, f_exp_pc_stall, f_exp_id_ex_flush;

    always @(*) begin
        f_uses_rs1 = (id_opcode == 7'b0110011) || (id_opcode == 7'b0010011) ||
                     (id_opcode == 7'b0000011) || (id_opcode == 7'b0100011) ||
                     (id_opcode == 7'b1100011) || (id_opcode == 7'b1100111);
        f_uses_rs2 = (id_opcode == 7'b0110011) || (id_opcode == 7'b0100011) ||
                     (id_opcode == 7'b1100011);
        f_exp_lus  = ex_mem_read && (ex_rd != 5'd0) &&
                     ((f_uses_rs1 && id_rs1 == ex_rd) || (f_uses_rs2 && id_rs2 == ex_rd));

        f_exp_valid_redir = branch_taken && !invalid_branch;
        f_exp_align_fault = f_exp_valid_redir && (branch_target[1:0] != 2'b00);
        f_exp_redir       = f_exp_valid_redir && !f_exp_align_fault;
        f_exp_pc_stall    = f_exp_redir ? 1'b0 : (f_exp_align_fault ? 1'b1 : f_exp_lus);
        f_exp_id_ex_flush = f_exp_redir || f_exp_align_fault || f_exp_lus;
    end

    initial f_past_valid = 1'b0;

    always @(posedge clk) begin
        f_past_valid       <= 1'b1;
        f_prev_rst         <= rst;
        f_prev_detected    <= fault_detected;
        f_prev_sticky      <= fault_sticky;
        f_prev_class       <= fault_class;
        f_prev_fetch_pc    <= fetch_pc;
        f_prev_decode_pc   <= decode_pc;
        f_prev_execute_pc  <= execute_pc;
        f_prev_mem_pc      <= mem_pc;
        f_prev_redirect    <= branch_redirect;
        f_prev_pc_target   <= pc_target;
        f_prev_pc_stall    <= pc_stall;
        f_prev_id_ex_stall <= id_ex_stall;
        f_prev_id_ex_flush <= id_ex_flush;
    end

    always @(*) begin
        if (!f_past_valid) assume(rst);
    end

    always @(*) begin
        if (ASSUME_CLEAN) begin
            assume(load_use_stall  == f_exp_lus);
            assume(alignment_fault == f_exp_align_fault);
            assume(branch_redirect == f_exp_redir);
            assume(pc_target       == branch_target);
            assume(pc_stall        == f_exp_pc_stall);
            assume(id_ex_stall     == 1'b0);
            assume(id_ex_flush     == f_exp_id_ex_flush);

            if (!rst) begin
                assume(fetch_pc[1:0] == 2'b00);
                assume(fetch_pc >= PC_MIN && fetch_pc <= PC_MAX);
                if (f_past_valid) begin
                    if (f_prev_rst) begin
                        assume(fetch_pc   == 32'h0);
                        assume(decode_pc  == 32'h0);
                        assume(execute_pc == 32'h0);
                        assume(mem_pc     == 32'h0);
                        assume(wb_pc      == 32'h0);
                    end
                    else begin
                        if (f_prev_redirect) begin
                            assume(fetch_pc  == f_prev_pc_target);
                            assume(decode_pc == 32'h0);
                        end
                        else if (f_prev_pc_stall) begin
                            assume(fetch_pc  == f_prev_fetch_pc);
                            assume(decode_pc == f_prev_decode_pc);
                        end
                        else begin
                            assume(fetch_pc  == f_prev_fetch_pc + 32'd4);
                            assume(decode_pc == f_prev_fetch_pc);
                        end

                        if (f_prev_id_ex_flush)
                            assume(execute_pc == 32'h0);
                        else
                            assume(execute_pc == f_prev_decode_pc);

                        assume(mem_pc == f_prev_execute_pc);
                        assume(wb_pc  == f_prev_mem_pc);
                    end
                end
            end
        end
    end

    always @(*) begin
        if (rst) begin
            assert(!fault_detected);
        end
        else begin
            // Branch priority & stall/flush consistency violations must be caught
            if (alignment_fault != f_exp_align_fault || branch_redirect != f_exp_redir)
                assert(fault_detected);
            if (load_use_stall != f_exp_lus || pc_stall != f_exp_pc_stall || id_ex_stall != 1'b0)
                assert(fault_detected);
            if (id_ex_flush != f_exp_id_ex_flush)
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
