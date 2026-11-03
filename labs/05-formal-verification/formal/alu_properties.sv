module alu_properties;

    (* anyseq *) logic [7:0] a;
    (* anyseq *) logic [7:0] b;
    (* anyseq *) logic [2:0] opcode;

    wire [7:0] result;
    wire zero;
    wire carry;

    alu dut (
        .a(a),
        .b(b),
        .opcode(opcode),
        .result(result),
        .zero(zero),
        .carry(carry)
    );

    always_comb begin

        // ADD
        if (opcode == 3'b000) begin
            assert ({carry, result} == ({1'b0, a} + {1'b0, b}));
        end

        // SUB
        if (opcode == 3'b001) begin
            assert (result == (a - b));
        end

        // AND
        if (opcode == 3'b010) begin
            assert (result == (a & b));
        end

        // OR
        if (opcode == 3'b011) begin
            assert (result == (a | b));
        end

        // XOR
        if (opcode == 3'b100) begin
            assert (result == (a ^ b));
        end

        // Shift left
        if (opcode == 3'b101) begin
            assert (result == (a << 1));
        end

        // Shift right
        if (opcode == 3'b110) begin
            assert (result == (a >> 1));
        end

        // Unsigned less-than
        if (opcode == 3'b111) begin
            assert (result == ((a < b) ? 8'h01 : 8'h00));
        end

        // Zero flag must always match the result
        assert (zero == (result == 8'h00));

        // Carry is only used for addition
        if (opcode != 3'b000) begin
            assert (carry == 1'b0);
        end

    end

endmodule
