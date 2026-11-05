
module rv32i_decoder (
    input  logic [31:0] instruction,

    output logic [6:0] opcode,
    output logic [4:0] rd,
    output logic [4:0] rs1,
    output logic [4:0] rs2,
    output logic [2:0] funct3,
    output logic [6:0] funct7,

    output logic       reg_write,
    output logic       mem_read,
    output logic       mem_write,
    output logic       mem_to_reg,
    output logic       alu_src,
    output logic       branch,
    output logic       jump,
    output logic       illegal_instruction
);

    // RV32I instruction fields
    assign opcode = instruction[6:0];
    assign rd     = instruction[11:7];
    assign funct3 = instruction[14:12];
    assign rs1    = instruction[19:15];
    assign rs2    = instruction[24:20];
    assign funct7 = instruction[31:25];

    always_comb begin
        // Safe default control signals
        reg_write           = 1'b0;
        mem_read            = 1'b0;
        mem_write           = 1'b0;
        mem_to_reg          = 1'b0;
        alu_src             = 1'b0;
        branch              = 1'b0;
        jump                = 1'b0;
        illegal_instruction = 1'b0;

        case (opcode)

            7'b0110011: begin // R-type
                reg_write = 1'b1;
            end

            7'b0010011: begin // I-type ALU
                reg_write = 1'b1;
                alu_src   = 1'b1;
            end

            7'b0000011: begin // LOAD
                reg_write  = 1'b1;
                mem_read   = 1'b1;
                mem_to_reg = 1'b1;
                alu_src    = 1'b1;
            end

            7'b0100011: begin // STORE
                mem_write = 1'b1;
                alu_src   = 1'b1;
            end

            7'b1100011: begin // BRANCH
                branch = 1'b1;
            end

            7'b1101111: begin // JAL
                reg_write = 1'b1;
                jump      = 1'b1;
            end

            7'b1100111: begin // JALR
                reg_write = 1'b1;
                jump      = 1'b1;
                alu_src   = 1'b1;
            end

            7'b0110111: begin // LUI
                reg_write = 1'b1;
                alu_src   = 1'b1;
            end

            7'b0010111: begin // AUIPC
                reg_write = 1'b1;
                alu_src   = 1'b1;
            end

            default: begin
                illegal_instruction = 1'b1;
            end

        endcase
    end

endmodule
