
module mem_wb_register (
    input  logic        clk,
    input  logic        rst,
    input  logic        stall,
    input  logic        flush,

    input  logic [31:0] pc_in,
    input  logic [31:0] alu_result_in,
    input  logic [31:0] mem_read_data_in,
    input  logic [31:0] link_address_in,
    input  logic [4:0]  rd_in,

    input  logic        reg_write_in,
    input  logic        mem_to_reg_in,
    input  logic        jump_in,

    output logic [31:0] pc_out,
    output logic [31:0] alu_result_out,
    output logic [31:0] mem_read_data_out,
    output logic [31:0] link_address_out,
    output logic [4:0]  rd_out,

    output logic        reg_write_out,
    output logic        mem_to_reg_out,
    output logic        jump_out
);

    always_ff @(posedge clk) begin
        if (rst || flush) begin
            pc_out            <= 32'b0;
            alu_result_out    <= 32'b0;
            mem_read_data_out <= 32'b0;
            link_address_out  <= 32'b0;
            rd_out            <= 5'b0;

            reg_write_out     <= 1'b0;
            mem_to_reg_out    <= 1'b0;
            jump_out          <= 1'b0;
        end
        else if (!stall) begin
            pc_out            <= pc_in;
            alu_result_out    <= alu_result_in;
            mem_read_data_out <= mem_read_data_in;
            link_address_out  <= link_address_in;
            rd_out            <= rd_in;

            reg_write_out     <= reg_write_in;
            mem_to_reg_out    <= mem_to_reg_in;
            jump_out          <= jump_in;
        end
    end

endmodule
