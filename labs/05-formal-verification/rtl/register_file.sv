
module register_file (
    input  logic       clk,
    input  logic       rst,
    input  logic       write_enable,
    input  logic [1:0] write_addr,
    input  logic [7:0] write_data,
    input  logic [1:0] read_addr,
    output logic [7:0] read_data

`ifdef FORMAL
    ,
    output wire [7:0] formal_r0,
    output wire [7:0] formal_r1,
    output wire [7:0] formal_r2,
    output wire [7:0] formal_r3
`endif
);

    // Four 8-bit registers
    logic [7:0] registers [0:3];

    integer i;

    // Synchronous reset and write operations
    always_ff @(posedge clk) begin
        if (rst) begin
            for (i = 0; i < 4; i = i + 1) begin
                registers[i] <= 8'h00;
            end
        end
        else if (write_enable) begin
            registers[write_addr] <= write_data;
        end
    end

    // Asynchronous read operation
    assign read_data = registers[read_addr];

    // Internal register visibility for formal verification
`ifdef FORMAL
    assign formal_r0 = registers[0];
    assign formal_r1 = registers[1];
    assign formal_r2 = registers[2];
    assign formal_r3 = registers[3];
`endif

endmodule
