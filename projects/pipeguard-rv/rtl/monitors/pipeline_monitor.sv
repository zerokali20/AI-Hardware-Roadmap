// =============================================================================
// PipeGuard-RV — M2: Pipeline-Aware Monitor
//
// Passive, synthesizable monitor that extends M1 with full pipeline-control
// context:
//   1. M0 rules: 4-byte PC alignment + configurable [PC_MIN, PC_MAX] bounds.
//   2. M1 rules: branch redirect validity and target checks.
//   3. Strict PC progression: uses prev_pc_stall to distinguish legitimate
//      stalls from spurious PC freezes (no conservative hold!).
//   4. Independent load-use hazard recomputation from IF/ID and ID/EX fields
//      to avoid circularity when checking `load_use_stall`.
//   5. Redirect priority, stall, and flush consistency against pipeline_control.
//   6. IF/ID, ID/EX, EX/MEM, MEM/WB stage PC progression & bubble checks.
//
// Shared-signal & common-mode limitations (documented in docs/limitations.md):
//   * If a fault simultaneously corrupts both a source register/opcode and the
//     downstream control net identically, or corrupts a shared clock/reset,
//     the monitor cannot detect the common-mode failure.
// =============================================================================
`include "pipeguard_defs.svh"

module pipeline_monitor #(
    parameter logic [31:0] PC_MIN = 32'h0000_0000,
    parameter logic [31:0] PC_MAX = 32'h0000_03FC
) (
    input  logic                         clk,
    input  logic                         rst,

    // Stage PCs
    input  logic [31:0]                  fetch_pc,
    input  logic [31:0]                  decode_pc,
    input  logic [31:0]                  execute_pc,
    input  logic [31:0]                  mem_pc,
    input  logic [31:0]                  wb_pc,

    // Branch / redirect signals
    input  logic                         branch_redirect,
    input  logic [31:0]                  pc_target,
    input  logic                         branch_taken,
    input  logic [31:0]                  branch_target,
    input  logic                         invalid_branch,
    input  logic                         alignment_fault,

    // Pipeline control & hazard signals
    input  logic                         load_use_stall,
    input  logic                         pc_stall,
    input  logic                         id_ex_stall,
    input  logic                         id_ex_flush,

    // IF/ID and ID/EX instruction fields (for independent hazard check)
    input  logic [6:0]                   id_opcode,
    input  logic [4:0]                   id_rs1,
    input  logic [4:0]                   id_rs2,
    input  logic [4:0]                   ex_rd,
    input  logic                         ex_mem_read,

    output logic                         fault_detected,
    output logic                         fault_sticky,
    output logic [`PG_FAULT_CLASS_W-1:0] fault_class
);

    // Registered history
    logic        prev_valid;
    logic        prev_rst;
    logic [31:0] prev_fetch_pc;
    logic [31:0] prev_decode_pc;
    logic [31:0] prev_execute_pc;
    logic [31:0] prev_mem_pc;
    logic        prev_redirect;
    logic [31:0] prev_pc_target;
    logic        prev_pc_stall;
    logic        prev_id_ex_stall;
    logic        prev_id_ex_flush;

    // Independent hazard detection
    logic        uses_rs1, uses_rs2, exp_load_use;

    // Expected pipeline_control outputs
    logic        exp_valid_redirect, exp_align_fault, exp_redirect;
    logic        exp_pc_stall, exp_id_ex_flush;

    // Fault flags
    logic        misaligned, out_of_bounds;
    logic        redirect_target_err, redirect_priority_err;
    logic        stall_inconsist, flush_inconsist;
    logic        pc_transition_err, stage_progress_err;
    logic [`PG_FAULT_CLASS_W-1:0] next_class;

    always_comb begin
        // ---- 1. M0 checks ----------------------------------------------------
        misaligned    = (fetch_pc[1:0] != 2'b00);
        /* verilator lint_off UNSIGNED */
        out_of_bounds = (fetch_pc < PC_MIN) || (fetch_pc > PC_MAX);
        /* verilator lint_on UNSIGNED */

        // ---- 2. Independent load-use hazard recomputation --------------------
        uses_rs1 = 1'b0;
        uses_rs2 = 1'b0;
        case (id_opcode)
            7'b0110011: begin uses_rs1 = 1'b1; uses_rs2 = 1'b1; end // R-type
            7'b0010011: begin uses_rs1 = 1'b1; end                  // I-type ALU
            7'b0000011: begin uses_rs1 = 1'b1; end                  // Load
            7'b0100011: begin uses_rs1 = 1'b1; uses_rs2 = 1'b1; end // Store
            7'b1100011: begin uses_rs1 = 1'b1; uses_rs2 = 1'b1; end // Branch
            7'b1100111: begin uses_rs1 = 1'b1; end                  // JALR
            default:    begin uses_rs1 = 1'b0; uses_rs2 = 1'b0; end
        endcase

        exp_load_use = ex_mem_read && (ex_rd != 5'd0) &&
                       ((uses_rs1 && (id_rs1 == ex_rd)) ||
                        (uses_rs2 && (id_rs2 == ex_rd)));

        // ---- 3. Pipeline-control priority, stall, and flush consistency ------
        exp_valid_redirect = branch_taken && !invalid_branch;
        exp_align_fault    = exp_valid_redirect && (branch_target[1:0] != 2'b00);
        exp_redirect       = exp_valid_redirect && !exp_align_fault;
        exp_pc_stall       = exp_redirect ? 1'b0 : (exp_align_fault ? 1'b1 : exp_load_use);
        exp_id_ex_flush    = exp_redirect || exp_align_fault || exp_load_use;

        redirect_priority_err = (alignment_fault != exp_align_fault) ||
                                (branch_redirect != exp_redirect);
        redirect_target_err   = branch_redirect && (pc_target != branch_target);
        stall_inconsist       = (load_use_stall != exp_load_use) ||
                                (pc_stall != exp_pc_stall) ||
                                (id_ex_stall != 1'b0);
        flush_inconsist       = (id_ex_flush != exp_id_ex_flush);

        // ---- 4. Strict PC & pipeline-stage progression -----------------------
        pc_transition_err  = 1'b0;
        stage_progress_err = 1'b0;

        if (prev_valid) begin
            if (prev_rst) begin
                pc_transition_err  = (fetch_pc != 32'h0000_0000);
                stage_progress_err = (decode_pc != 32'h0) ||
                                     (execute_pc != 32'h0) ||
                                     (mem_pc != 32'h0) ||
                                     (wb_pc != 32'h0);
            end
            else begin
                // Strict Fetch PC check (no conservative hold)
                if (prev_redirect) begin
                    redirect_target_err = redirect_target_err || (fetch_pc != prev_pc_target);
                end
                else if (prev_pc_stall) begin
                    pc_transition_err = (fetch_pc != prev_fetch_pc);
                end
                else begin
                    pc_transition_err = (fetch_pc != (prev_fetch_pc + 32'd4));
                end

                // IF/ID progression (driven by pc_redirect and pc_stall)
                if (prev_redirect) begin
                    if (decode_pc != 32'h0) stage_progress_err = 1'b1;
                end
                else if (prev_pc_stall) begin
                    if (decode_pc != prev_decode_pc) stage_progress_err = 1'b1;
                end
                else begin
                    if (decode_pc != prev_fetch_pc) stage_progress_err = 1'b1;
                end

                // ID/EX progression
                if (prev_id_ex_flush) begin
                    if (execute_pc != 32'h0) stage_progress_err = 1'b1;
                end
                else if (!prev_id_ex_stall) begin
                    if (execute_pc != prev_decode_pc) stage_progress_err = 1'b1;
                end

                // EX/MEM and MEM/WB advance unconditionally every cycle
                if ((mem_pc != prev_execute_pc) || (wb_pc != prev_mem_pc)) begin
                    stage_progress_err = 1'b1;
                end
            end
        end

        fault_detected = !rst && (misaligned || out_of_bounds ||
                                  redirect_target_err || redirect_priority_err ||
                                  stall_inconsist || flush_inconsist ||
                                  pc_transition_err || stage_progress_err);

        if (rst) begin
            next_class = `PG_FC_NONE;
        end
        else if (misaligned) begin
            next_class = `PG_FC_PC_MISALIGNED;
        end
        else if (out_of_bounds) begin
            next_class = `PG_FC_PC_OUT_OF_BOUNDS;
        end
        else if (redirect_target_err) begin
            next_class = `PG_FC_REDIRECT_TARGET;
        end
        else if (redirect_priority_err) begin
            next_class = `PG_FC_REDIRECT_PRIORITY;
        end
        else if (stall_inconsist) begin
            next_class = `PG_FC_STALL_INCONSIST;
        end
        else if (flush_inconsist) begin
            next_class = `PG_FC_FLUSH_INCONSIST;
        end
        else if (pc_transition_err) begin
            next_class = `PG_FC_PC_TRANSITION;
        end
        else if (stage_progress_err) begin
            next_class = `PG_FC_STAGE_PROGRESS;
        end
        else begin
            next_class = `PG_FC_NONE;
        end
    end

    always_ff @(posedge clk) begin
        prev_valid       <= 1'b1;
        prev_rst         <= rst;
        prev_fetch_pc    <= fetch_pc;
        prev_decode_pc   <= decode_pc;
        prev_execute_pc  <= execute_pc;
        prev_mem_pc      <= mem_pc;
        prev_redirect    <= branch_redirect;
        prev_pc_target   <= pc_target;
        prev_pc_stall    <= pc_stall;
        prev_id_ex_stall <= id_ex_stall;
        prev_id_ex_flush <= id_ex_flush;

        if (rst) begin
            fault_sticky <= 1'b0;
            fault_class  <= `PG_FC_NONE;
        end
        else if (fault_detected && !fault_sticky) begin
            fault_sticky <= 1'b1;
            fault_class  <= next_class;
        end
    end

endmodule
