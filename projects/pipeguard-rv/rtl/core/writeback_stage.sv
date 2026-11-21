
module writeback_stage (
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

    output logic [31:0] wb_data,
    output logic [4:0]  wb_rd,
    output logic        wb_reg_write,
    output logic [31:0] wb_pc
);

    logic [31:0] registered_alu_result;
    logic [31:0] registered_mem_data;
    logic [31:0] registered_link_address;

    logic registered_reg_write;
    logic registered_mem_to_reg;
    logic registered_jump;

    mem_wb_register mem_wb_unit (
        .clk(clk),
        .rst(rst),
        .stall(stall),
        .flush(flush),

        .pc_in(pc_in),
        .alu_result_in(alu_result_in),
        .mem_read_data_in(mem_read_data_in),
        .link_address_in(link_address_in),
        .rd_in(rd_in),

        .reg_write_in(reg_write_in),
        .mem_to_reg_in(mem_to_reg_in),
        .jump_in(jump_in),

        .pc_out(wb_pc),
        .alu_result_out(registered_alu_result),
        .mem_read_data_out(registered_mem_data),
        .link_address_out(registered_link_address),
        .rd_out(wb_rd),

        .reg_write_out(registered_reg_write),
        .mem_to_reg_out(registered_mem_to_reg),
        .jump_out(registered_jump)
    );

    always_comb begin
        if (registered_jump)
            wb_data = registered_link_address;
        else if (registered_mem_to_reg)
            wb_data = registered_mem_data;
        else
            wb_data = registered_alu_result;
    end

    assign wb_reg_write = registered_reg_write &&
                          (wb_rd != 5'd0) &&
                          !rst;

endmodule
