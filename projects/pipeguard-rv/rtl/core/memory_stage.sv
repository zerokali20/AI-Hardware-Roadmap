
module memory_stage (
    input  logic        clk,
    input  logic        rst,
    input  logic        stall,
    input  logic        flush,

    input  logic [31:0] pc_in,
    input  logic [31:0] alu_result_in,
    input  logic [31:0] store_data_in,
    input  logic [31:0] link_address_in,
    input  logic [4:0]  rd_in,
    input  logic [2:0]  funct3_in,

    input  logic        reg_write_in,
    input  logic        mem_read_in,
    input  logic        mem_write_in,
    input  logic        mem_to_reg_in,
    input  logic        jump_in,

    output logic [31:0] mem_pc,
    output logic [31:0] mem_alu_result,
    output logic [31:0] mem_read_data,
    output logic [31:0] mem_link_address,
    output logic [4:0]  mem_rd,

    output logic        mem_reg_write,
    output logic        mem_mem_to_reg,
    output logic        mem_jump,

    output logic        alignment_error,
    output logic        access_error
);

    logic [31:0] registered_store_data;
    logic [2:0]  registered_funct3;
    logic        registered_mem_read;
    logic        registered_mem_write;

    logic [31:0] raw_read_data;

    ex_mem_register ex_mem_unit (
        .clk(clk),
        .rst(rst),
        .stall(stall),
        .flush(flush),

        .pc_in(pc_in),
        .alu_result_in(alu_result_in),
        .store_data_in(store_data_in),
        .link_address_in(link_address_in),
        .rd_in(rd_in),
        .funct3_in(funct3_in),

        .reg_write_in(reg_write_in),
        .mem_read_in(mem_read_in),
        .mem_write_in(mem_write_in),
        .mem_to_reg_in(mem_to_reg_in),
        .jump_in(jump_in),

        .pc_out(mem_pc),
        .alu_result_out(mem_alu_result),
        .store_data_out(registered_store_data),
        .link_address_out(mem_link_address),
        .rd_out(mem_rd),
        .funct3_out(registered_funct3),

        .reg_write_out(mem_reg_write),
        .mem_read_out(registered_mem_read),
        .mem_write_out(registered_mem_write),
        .mem_to_reg_out(mem_mem_to_reg),
        .jump_out(mem_jump)
    );

    data_memory data_mem_unit (
        .clk(clk),
        .rst(rst),
        .mem_read(registered_mem_read),
        .mem_write(registered_mem_write),
        .address(mem_alu_result),
        .write_data(registered_store_data),
        .funct3(registered_funct3),

        .read_data(raw_read_data),
        .alignment_error(alignment_error),
        .access_error(access_error)
    );

    assign mem_read_data = raw_read_data;

endmodule
