// =============================================================================
// PipeGuard-RV — M0: Program-Counter-Based Monitor
//
// Passive, synthesizable monitor that validates the Fetch PC against:
//   1. 4-byte word alignment  (fetch_pc[1:0] == 2'b00)
//   2. Configurable legal instruction memory bounds (PC_MIN <= fetch_pc <= PC_MAX)
//
// Design notes:
//   * Does NOT flag non-sequential PC transitions because valid branches, JAL,
//     and JALR instructions legitimately change the PC.
//   * Combinational detection (`fault_detected`) evaluates the current `fetch_pc`
//     when `!rst`.
//   * Registered sticky latch (`fault_sticky`) and first-fault classification
//     (`fault_class`) update on `posedge clk` when `fault_detected && !fault_sticky`,
//     and clear synchronously on `rst`.
//   * Priority when both rules fire in the same cycle: misalignment takes
//     precedence over out-of-bounds (`PG_FC_PC_MISALIGNED` > `PG_FC_PC_OUT_OF_BOUNDS`).
//
// Known limitations (documented in docs/limitations.md):
//   * Blind to aligned, in-range PC deviations (e.g. a single-bit flip in
//     PC[9:2] that lands on another valid word address inside [PC_MIN, PC_MAX]).
//   * Does not verify branch/jump targets or pipeline stall/flush consistency.
// =============================================================================
`include "pipeguard_defs.svh"

module pc_monitor #(
    parameter logic [31:0] PC_MIN = 32'h0000_0000,
    parameter logic [31:0] PC_MAX = 32'h0000_03FC  // 256 words * 4 - 4
) (
    input  logic                         clk,
    input  logic                         rst,
    input  logic [31:0]                  fetch_pc,

    output logic                         fault_detected,
    output logic                         fault_sticky,
    output logic [`PG_FAULT_CLASS_W-1:0] fault_class
);

    logic                         misaligned;
    logic                         out_of_bounds;
    logic [`PG_FAULT_CLASS_W-1:0] next_class;

    always_comb begin
        misaligned     = (fetch_pc[1:0] != 2'b00);
        /* verilator lint_off UNSIGNED */
        out_of_bounds  = (fetch_pc < PC_MIN) || (fetch_pc > PC_MAX);
        /* verilator lint_on UNSIGNED */
        fault_detected = !rst && (misaligned || out_of_bounds);

        if (rst) begin
            next_class = `PG_FC_NONE;
        end
        else if (misaligned) begin
            next_class = `PG_FC_PC_MISALIGNED;
        end
        else if (out_of_bounds) begin
            next_class = `PG_FC_PC_OUT_OF_BOUNDS;
        end
        else begin
            next_class = `PG_FC_NONE;
        end
    end

    always_ff @(posedge clk) begin
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
