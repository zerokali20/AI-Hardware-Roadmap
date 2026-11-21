
module alu_control (
    input  logic [6:0] opcode,
    input  logic [2:0] funct3,
    input  logic [6:0] funct7,

    output logic [3:0] alu_op,
    output logic       invalid_operation
);

    localparam ALU_ADD  = 4'b0000;
    localparam ALU_SUB  = 4'b0001;
    localparam ALU_AND  = 4'b0010;
    localparam ALU_OR   = 4'b0011;
    localparam ALU_XOR  = 4'b0100;
    localparam ALU_SLL  = 4'b0101;
    localparam ALU_SRL  = 4'b0110;
    localparam ALU_SRA  = 4'b0111;
    localparam ALU_SLT  = 4'b1000;
    localparam ALU_SLTU = 4'b1001;

    always_comb begin
        alu_op = ALU_ADD;
        invalid_operation = 1'b0;

        case (opcode)

            // R-type arithmetic and logic
            7'b0110011: begin
                case (funct3)
                    3'b000: begin
                        if (funct7 == 7'b0000000)
                            alu_op = ALU_ADD;
                        else if (funct7 == 7'b0100000)
                            alu_op = ALU_SUB;
                        else
                            invalid_operation = 1'b1;
                    end

                    3'b001: begin
                        alu_op = ALU_SLL;
                        if (funct7 != 7'b0000000)
                            invalid_operation = 1'b1;
                    end

                    3'b010: begin
                        alu_op = ALU_SLT;
                        if (funct7 != 7'b0000000)
                            invalid_operation = 1'b1;
                    end

                    3'b011: begin
                        alu_op = ALU_SLTU;
                        if (funct7 != 7'b0000000)
                            invalid_operation = 1'b1;
                    end

                    3'b100: begin
                        alu_op = ALU_XOR;
                        if (funct7 != 7'b0000000)
                            invalid_operation = 1'b1;
                    end

                    3'b101: begin
                        if (funct7 == 7'b0000000)
                            alu_op = ALU_SRL;
                        else if (funct7 == 7'b0100000)
                            alu_op = ALU_SRA;
                        else
                            invalid_operation = 1'b1;
                    end

                    3'b110: begin
                        alu_op = ALU_OR;
                        if (funct7 != 7'b0000000)
                            invalid_operation = 1'b1;
                    end

                    3'b111: begin
                        alu_op = ALU_AND;
                        if (funct7 != 7'b0000000)
                            invalid_operation = 1'b1;
                    end
                endcase
            end

            // I-type arithmetic and logic
            7'b0010011: begin
                case (funct3)
                    3'b000: alu_op = ALU_ADD;
                    3'b010: alu_op = ALU_SLT;
                    3'b011: alu_op = ALU_SLTU;
                    3'b100: alu_op = ALU_XOR;
                    3'b110: alu_op = ALU_OR;
                    3'b111: alu_op = ALU_AND;

                    3'b001: begin
                        alu_op = ALU_SLL;
                        if (funct7 != 7'b0000000)
                            invalid_operation = 1'b1;
                    end

                    3'b101: begin
                        if (funct7 == 7'b0000000)
                            alu_op = ALU_SRL;
                        else if (funct7 == 7'b0100000)
                            alu_op = ALU_SRA;
                        else
                            invalid_operation = 1'b1;
                    end
                endcase
            end

            // Loads, stores, LUI, AUIPC, JAL, JALR
            7'b0000011,
            7'b0100011,
            7'b0110111,
            7'b0010111,
            7'b1101111,
            7'b1100111: begin
                alu_op = ALU_ADD;
            end

            // Branch comparison uses subtraction.
            // Branch unit will handle signed/unsigned conditions.
            7'b1100011: begin
                alu_op = ALU_SUB;
            end

            default: begin
                invalid_operation = 1'b1;
            end

        endcase
    end

endmodule
