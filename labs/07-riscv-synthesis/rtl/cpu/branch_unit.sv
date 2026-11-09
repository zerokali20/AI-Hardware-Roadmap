
module branch_unit (
    input  logic [31:0] pc,
    input  logic [31:0] rs1_data,
    input  logic [31:0] rs2_data,
    input  logic [31:0] immediate,

    input  logic [6:0]  opcode,
    input  logic [2:0]  funct3,

    output logic        branch_taken,
    output logic [31:0] branch_target,
    output logic [31:0] link_address,
    output logic        invalid_branch
);

    localparam OPCODE_BRANCH = 7'b1100011;
    localparam OPCODE_JAL    = 7'b1101111;
    localparam OPCODE_JALR   = 7'b1100111;

    always_comb begin
        branch_taken  = 1'b0;
        branch_target = pc + 32'd4;
        link_address  = pc + 32'd4;
        invalid_branch = 1'b0;

        case (opcode)

            OPCODE_BRANCH: begin
                branch_target = pc + immediate;

                case (funct3)
                    3'b000:
                        branch_taken = (rs1_data == rs2_data);

                    3'b001:
                        branch_taken = (rs1_data != rs2_data);

                    3'b100:
                        branch_taken =
                            ($signed(rs1_data) < $signed(rs2_data));

                    3'b101:
                        branch_taken =
                            ($signed(rs1_data) >= $signed(rs2_data));

                    3'b110:
                        branch_taken = (rs1_data < rs2_data);

                    3'b111:
                        branch_taken = (rs1_data >= rs2_data);

                    default: begin
                        branch_taken = 1'b0;
                        invalid_branch = 1'b1;
                    end
                endcase
            end

            OPCODE_JAL: begin
                branch_taken  = 1'b1;
                branch_target = pc + immediate;
            end

            OPCODE_JALR: begin
                if (funct3 == 3'b000) begin
                    branch_taken = 1'b1;
                    branch_target =
                        (rs1_data + immediate) & 32'hFFFFFFFE;
                end
                else begin
                    invalid_branch = 1'b1;
                end
            end

            default: begin
                // Not a branch or jump instruction.
            end

        endcase
    end

endmodule
