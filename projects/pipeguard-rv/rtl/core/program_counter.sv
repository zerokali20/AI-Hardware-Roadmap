module program_counter (
    input  logic        clk,
    input  logic        rst,
    input  logic        stall,
    input  logic        branch_taken,
    input  logic [31:0] branch_target,
    output logic [31:0] pc
);

    always_ff @(posedge clk) begin
        if (rst)
            pc <= 32'h00000000;
        else if (branch_taken)
            pc <= branch_target;
        else if (stall)
            pc <= pc;
        else
            pc <= pc + 32'd4;
    end

endmodule
