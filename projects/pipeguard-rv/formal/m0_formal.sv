// =============================================================================
// PipeGuard-RV — Formal Properties for M0 (pc_monitor)
//
// Proves (bounded model checking via yosys-smtbmc / SymbiYosys):
//   Mode ASSUME_CLEAN=0 (unconstrained inputs):
//     1. Reset suppression: rst => !fault_detected; after rst => !fault_sticky && fault_class == 0
//     2. Legal transitions & sticky persistence:
//        - !fault_sticky => fault_class == PG_FC_NONE
//        - fault_sticky && !rst => remains 1 and fault_class stays stable
//        - !rst && fault_detected && !fault_sticky => next(!rst) latches sticky & non-zero class
//     3. Exact response to invalid observations:
//        - !rst && misaligned => fault_detected && next_class == PG_FC_PC_MISALIGNED
//        - !rst && aligned && OOB => fault_detected && next_class == PG_FC_PC_OUT_OF_BOUNDS
//        - !rst && aligned && in-bounds => !fault_detected
//   Mode ASSUME_CLEAN=1 (valid aligned in-range PCs):
//     4. Zero false positives: !fault_detected && !fault_sticky
// =============================================================================
`include "pipeguard_defs.svh"

module m0_formal #(
    parameter bit          ASSUME_CLEAN = 1'b0,
    parameter logic [31:0] PC_MIN       = 32'h0000_0000,
    parameter logic [31:0] PC_MAX       = 32'h0000_03FC
) (
    input logic        clk,
    input logic        rst,
    input logic [31:0] fetch_pc
);

    logic                         fault_detected;
    logic                         fault_sticky;
    logic [`PG_FAULT_CLASS_W-1:0] fault_class;

    pc_monitor #(
        .PC_MIN (PC_MIN),
        .PC_MAX (PC_MAX)
    ) dut (
        .clk            (clk),
        .rst            (rst),
        .fetch_pc       (fetch_pc),
        .fault_detected (fault_detected),
        .fault_sticky   (fault_sticky),
        .fault_class    (fault_class)
    );

    logic                         f_past_valid;
    logic                         f_prev_rst;
    logic                         f_prev_detected;
    logic                         f_prev_sticky;
    logic [`PG_FAULT_CLASS_W-1:0] f_prev_class;
    logic [31:0]                  f_prev_pc;

    initial f_past_valid = 1'b0;

    always @(posedge clk) begin
        f_past_valid    <= 1'b1;
        f_prev_rst      <= rst;
        f_prev_detected <= fault_detected;
        f_prev_sticky   <= fault_sticky;
        f_prev_class    <= fault_class;
        f_prev_pc       <= fetch_pc;
    end

    // Start from reset in cycle 0
    always @(*) begin
        if (!f_past_valid) assume(rst);
    end

    // Optional clean environment assumption
    always @(*) begin
        if (ASSUME_CLEAN && !rst) begin
            assume(fetch_pc[1:0] == 2'b00);
            assume(fetch_pc >= PC_MIN && fetch_pc <= PC_MAX);
        end
    end

    // Combinational invariants
    always @(*) begin
        if (rst) begin
            assert(!fault_detected);
        end
        else begin
            if (fetch_pc[1:0] != 2'b00 || fetch_pc < PC_MIN || fetch_pc > PC_MAX)
                assert(fault_detected);
            else
                assert(!fault_detected);
        end

        if (ASSUME_CLEAN) begin
            assert(!fault_detected);
        end
    end

    // Sequential invariants
    always @(posedge clk) begin
        if (f_past_valid) begin
            // Reset clears sticky and class
            if (f_prev_rst) begin
                assert(!fault_sticky);
                assert(fault_class == `PG_FC_NONE);
            end
            else begin
                // Sticky persistence & first-fault class stability
                if (f_prev_sticky) begin
                    assert(fault_sticky);
                    assert(fault_class == f_prev_class);
                end
                else if (f_prev_detected) begin
                    assert(fault_sticky);
                    if (f_prev_pc[1:0] != 2'b00)
                        assert(fault_class == `PG_FC_PC_MISALIGNED);
                    else
                        assert(fault_class == `PG_FC_PC_OUT_OF_BOUNDS);
                end
                else begin
                    assert(!fault_sticky);
                    assert(fault_class == `PG_FC_NONE);
                end
            end

            if (ASSUME_CLEAN) begin
                assert(!fault_sticky);
                assert(fault_class == `PG_FC_NONE);
            end
        end
    end

endmodule
