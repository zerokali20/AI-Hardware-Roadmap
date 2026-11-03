module alu (
    input  logic [7:0] a,
    input  logic [7:0] b,
    input  logic [2:0] opcode,

    output logic [7:0] result,
    output logic       zero,
    output logic       carry
);

    logic [8:0] temp;

    always_comb begin

        result = 8'h00;
        carry  = 1'b0;
        temp   = 9'h000;

        case (opcode)

            3'b000: begin
                // ADD
                temp   = {1'b0, a} + {1'b0, b};
                result = temp[7:0];
                carry  = temp[8];
            end

            3'b001: begin
                // SUB
                result = a - b;
            end

            3'b010: begin
                // AND
                result = a & b;
            end

            3'b011: begin
                // OR
                result = a | b;
            end

            3'b100: begin
                // XOR
                result = a ^ b;
            end

            3'b101: begin
                // Shift left
                result = a << 1;
            end

            3'b110: begin
                // Shift right
                result = a >> 1;
            end

            3'b111: begin
                // Unsigned less-than
                result = (a < b) ? 8'h01 : 8'h00;
            end

        endcase
    end

    assign zero = (result == 8'h00);

endmodule
