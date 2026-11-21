
module if_id_register (
    input  logic        clk,
    input  logic        rst,
    input  logic        stall,
    input  logic        flush,

    input  logic [31:0] pc_in,
    input  logic [31:0] instruction_in,

    output logic [31:0] pc_out,
    output logic [31:0] instruction_out
);

    localparam logic [31:0] NOP = 32'h00000013;

    always_ff @(posedge clk) begin
        if (rst) begin
            pc_out          <= 32'b0;
            instruction_out <= NOP;
        end
        else if (flush) begin
            pc_out          <= 32'b0;
            instruction_out <= NOP;
        end
        else if (!stall) begin
            pc_out          <= pc_in;
            instruction_out <= instruction_in;
        end
    end

endmodule
