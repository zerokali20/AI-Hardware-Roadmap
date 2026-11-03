
module register_file (
    input  logic       clk,
    input  logic       rst,
    input  logic       write_enable,
    input  logic [1:0] write_addr,
    input  logic [7:0] write_data,
    input  logic [1:0] read_addr,
    output logic [7:0] read_data
);

    logic [7:0] registers [0:3];

    integer i;

    always_ff @(posedge clk) begin
        if (rst) begin
            for (i = 0; i < 4; i = i + 1)
                registers[i] <= 8'h00;
        end
        else if (write_enable) begin
            registers[write_addr] <= write_data;
        end
    end

    assign read_data = registers[read_addr];

endmodule
