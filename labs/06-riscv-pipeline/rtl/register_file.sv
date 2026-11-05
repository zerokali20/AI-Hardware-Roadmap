
module register_file (
    input  logic        clk,
    input  logic        rst,

    input  logic        reg_write,
    input  logic [4:0]  write_addr,
    input  logic [31:0] write_data,

    input  logic [4:0]  read_addr1,
    input  logic [4:0]  read_addr2,

    output logic [31:0] read_data1,
    output logic [31:0] read_data2
);

    logic [31:0] registers [0:31];

    integer i;

    // Synchronous reset and writeback
    always_ff @(posedge clk) begin
        if (rst) begin
            for (i = 0; i < 32; i = i + 1)
                registers[i] <= 32'b0;
        end
        else if (reg_write && write_addr != 5'd0) begin
            registers[write_addr] <= write_data;
        end
    end

    // Two asynchronous read ports
    always_comb begin
        read_data1 = (read_addr1 == 5'd0)
                   ? 32'b0 : registers[read_addr1];

        read_data2 = (read_addr2 == 5'd0)
                   ? 32'b0 : registers[read_addr2];
    end

endmodule
