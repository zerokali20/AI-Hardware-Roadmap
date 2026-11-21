
module instruction_memory #(
    parameter MEM_DEPTH = 256,
    parameter MEM_FILE = "programs/test_program.hex"
)(
    input  logic [31:0] address,
    output logic [31:0] instruction
);

    logic [31:0] memory [0:MEM_DEPTH-1];

    integer i;

    initial begin
        // Default to illegal instructions
        for (i = 0; i < MEM_DEPTH; i = i + 1)
            memory[i] = 32'h00000000;

        // Load machine-code program
        $readmemh(MEM_FILE, memory);
    end

    // Asynchronous instruction read
    always_comb begin
        if ((address[1:0] == 2'b00) &&
            ((address >> 2) < MEM_DEPTH))
            instruction = memory[address >> 2];
        else
            instruction = 32'h00000000;
    end

endmodule
