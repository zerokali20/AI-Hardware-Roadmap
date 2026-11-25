// =============================================================================
// PipeGuard-RV — M1: Branch-Aware Monitor
//
// Passive, synthesizable monitor that extends M0 (alignment + bounds) with:
//   1. Cycle-correct PC transition validation using registered previous-cycle
//      fetch_pc and redirect state.
//   2. Observed branch-redirect validation against EX-stage branch intent
//      (branch_taken, branch_target, invalid_branch, alignment_fault).
//   3. Expected redirect target checking (pc_target == branch_target).
//   4. Conservative acceptance of PC holds (fetch_pc == prev_fetch_pc) when
//      no redirect occurred, because M1 has no stall-context observation.
//
// Observation boundary note:
//   `branch_taken`, `branch_target`, and `invalid_branch` are tapped from the
//   EX-stage branch_unit BEFORE pipeline_control; `branch_redirect`,
//   `pc_target`, and `alignment_fault` are tapped AFTER pipeline_control.
//
// Known limitations:
//   * Cannot distinguish a legitimate load-use/alignment stall from a spurious
//     PC freeze (conservative PC hold acceptance).
//   * Does not check pipeline stage registers (IF/ID, ID/EX) or hazard logic.
// =============================================================================
`include "pipeguard_defs.svh"

module branch_monitor #(
    parameter logic [31:0] PC_MIN = 32'h0000_0000,
    parameter logic [31:0] PC_MAX = 32'h0000_03FC
) (
    input  logic                         clk,
    input  logic                         rst,
    input  logic [31:0]                  fetch_pc,

    input  logic                         branch_redirect,
    input  logic [31:0]                  pc_target,
    input  logic                         branch_taken,
    input  logic [31:0]                  branch_target,
    input  logic                         invalid_branch,
    input  logic                         alignment_fault,

    output logic                         fault_detected,
    output logic                         fault_sticky,
    output logic [`PG_FAULT_CLASS_W-1:0] fault_class
);

    // History from previous posedge clk
    logic        prev_valid;
    logic        prev_rst;
    logic [31:0] prev_fetch_pc;
    logic        prev_redirect;
    logic [31:0] prev_pc_target;

    logic                         misaligned;
    logic                         out_of_bounds;
    logic                         redirect_spurious;
    logic                         redirect_target_err;
    logic                         pc_transition_err;
    logic                         exp_valid_redirect;
    logic                         exp_redirect;
    logic [`PG_FAULT_CLASS_W-1:0] next_class;

    always_comb begin
        // M0 checks
        misaligned    = (fetch_pc[1:0] != 2'b00);
        /* verilator lint_off UNSIGNED */
        out_of_bounds = (fetch_pc < PC_MIN) || (fetch_pc > PC_MAX);
        /* verilator lint_on UNSIGNED */

        // Combinational branch-redirect consistency (current cycle)
        exp_valid_redirect  = branch_taken && !invalid_branch;
        exp_redirect        = exp_valid_redirect && !alignment_fault && (branch_target[1:0] == 2'b00);
        redirect_spurious   = (branch_redirect != exp_redirect);
        redirect_target_err = branch_redirect && (pc_target != branch_target);

        // Registered PC progression check (against previous cycle)
        pc_transition_err = 1'b0;
        if (prev_valid) begin
            if (prev_rst) begin
                pc_transition_err = (fetch_pc != 32'h0000_0000);
            end
            else if (prev_redirect) begin
                redirect_target_err = redirect_target_err || (fetch_pc != prev_pc_target);
            end
            else begin
                // No stall context in M1: conservatively accept sequential (+4) or hold (+0)
                pc_transition_err = (fetch_pc != (prev_fetch_pc + 32'd4)) &&
                                    (fetch_pc != prev_fetch_pc);
            end
        end

        fault_detected = !rst && (misaligned || out_of_bounds ||
                                  redirect_spurious || redirect_target_err ||
                                  pc_transition_err);

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
        else if (redirect_spurious) begin
            next_class = `PG_FC_REDIRECT_SPURIOUS;
        end
        else if (pc_transition_err) begin
            next_class = `PG_FC_PC_TRANSITION;
        end
        else begin
            next_class = `PG_FC_NONE;
        end
    end

    always_ff @(posedge clk) begin
        prev_valid     <= 1'b1;
        prev_rst       <= rst;
        prev_fetch_pc  <= fetch_pc;
        prev_redirect  <= branch_redirect;
        prev_pc_target <= pc_target;

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
