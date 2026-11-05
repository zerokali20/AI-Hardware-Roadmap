
module register_writeback_integration (
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

    input  logic [4:0]  read_addr1,
    input  logic [4:0]  read_addr2,

    output logic [31:0] read_data1,
    output logic [31:0] read_data2,

    output logic [31:0] wb_data,
    output logic [4:0]  wb_rd,
    output logic        wb_reg_write,
    output logic [31:0] wb_pc
);

    writeback_stage wb_unit (
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

        .wb_data(wb_data),
        .wb_rd(wb_rd),
        .wb_reg_write(wb_reg_write),
        .wb_pc(wb_pc)
    );

    register_file regfile_unit (
        .clk(clk),
        .rst(rst),

        .reg_write(wb_reg_write),
        .write_addr(wb_rd),
        .write_data(wb_data),

        .read_addr1(read_addr1),
        .read_addr2(read_addr2),

        .read_data1(read_data1),
        .read_data2(read_data2)
    );

endmodule
