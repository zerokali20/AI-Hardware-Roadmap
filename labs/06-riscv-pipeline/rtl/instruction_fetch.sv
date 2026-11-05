
module instruction_fetch (
    input  logic        clk,
    input  logic        rst,
    input  logic        stall,
    input  logic        branch_taken,
    input  logic [31:0] branch_target,

    output logic [31:0] pc,
    output logic [31:0] instruction
);

    program_counter pc_unit (
        .clk(clk),
        .rst(rst),
        .stall(stall),
        .branch_taken(branch_taken),
        .branch_target(branch_target),
        .pc(pc)
    );

    instruction_memory imem_unit (
        .address(pc),
        .instruction(instruction)
    );

endmodule
