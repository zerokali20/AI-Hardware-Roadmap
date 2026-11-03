
module register_file_properties (
    input wire clk
);

    (* anyseq *) reg rst;
    (* anyseq *) reg write_enable;
    (* anyseq *) reg [1:0] write_addr;
    (* anyseq *) reg [7:0] write_data;
    (* anyseq *) reg [1:0] read_addr;

    wire [7:0] read_data;
    wire [7:0] formal_r0;
    wire [7:0] formal_r1;
    wire [7:0] formal_r2;
    wire [7:0] formal_r3;

    register_file dut (
        .clk(clk),
        .rst(rst),
        .write_enable(write_enable),
        .write_addr(write_addr),
        .write_data(write_data),
        .read_addr(read_addr),
        .read_data(read_data),
        .formal_r0(formal_r0),
        .formal_r1(formal_r1),
        .formal_r2(formal_r2),
        .formal_r3(formal_r3)
    );

    reg [7:0] expected [0:3];
    reg initialized = 1'b0;

    integer i;

    always @(posedge clk) begin
        if (rst) begin
            for (i = 0; i < 4; i = i + 1)
                expected[i] <= 8'h00;

            initialized <= 1'b1;
        end
        else if (write_enable) begin
            expected[write_addr] <= write_data;
        end
    end

    // Check that the DUT agrees with the reference model.
    // The first reset must occur before comparisons are valid.
    always @(*) begin
        if (initialized) begin
            assert(formal_r0 == expected[0]);
            assert(formal_r1 == expected[1]);
            assert(formal_r2 == expected[2]);
            assert(formal_r3 == expected[3]);
            assert (read_data == expected[read_addr]);
        end
    end

    reg first_cycle = 1'b1;

    always @(posedge clk) begin
    	if (first_cycle) begin
    	    assume(rst);
	    first_cycle <= 1'b0;
        end
    end

endmodule

