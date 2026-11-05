
module hazard_detection_unit (
    input  logic [4:0] id_ex_rd,
    input  logic       id_ex_mem_read,

    input  logic [4:0] if_id_rs1,
    input  logic [4:0] if_id_rs2,
    input  logic [6:0] if_id_opcode,

    output logic       stall_request
);

    logic uses_rs1;
    logic uses_rs2;

    // Identify which source registers the instruction
    // in the Decode stage actually reads.
    always_comb begin
        uses_rs1 = 1'b0;
        uses_rs2 = 1'b0;

        case (if_id_opcode)
            7'b0110011: begin // R-type ALU
                uses_rs1 = 1'b1;
                uses_rs2 = 1'b1;
            end

            7'b0010011: begin // I-type ALU
                uses_rs1 = 1'b1;
            end

            7'b0000011: begin // Loads
                uses_rs1 = 1'b1;
            end

            7'b0100011: begin // Stores
                uses_rs1 = 1'b1;
                uses_rs2 = 1'b1;
            end

            7'b1100011: begin // Branches
                uses_rs1 = 1'b1;
                uses_rs2 = 1'b1;
            end

            7'b1100111: begin // JALR
                uses_rs1 = 1'b1;
            end

            default: begin
                uses_rs1 = 1'b0;
                uses_rs2 = 1'b0;
            end
        endcase
    end

    always_comb begin
        stall_request = 1'b0;

        if (id_ex_mem_read && id_ex_rd != 5'd0) begin
            if ((uses_rs1 && if_id_rs1 == id_ex_rd) ||
                (uses_rs2 && if_id_rs2 == id_ex_rd)) begin

                stall_request = 1'b1;
            end
        end
    end

endmodule
