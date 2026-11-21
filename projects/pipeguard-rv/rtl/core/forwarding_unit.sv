
module forwarding_unit (
    input  logic [4:0] id_ex_rs1,
    input  logic [4:0] id_ex_rs2,

    input  logic [4:0] ex_mem_rd,
    input  logic       ex_mem_reg_write,
    input  logic       ex_mem_mem_to_reg,

    input  logic [4:0] mem_wb_rd,
    input  logic       mem_wb_reg_write,

    output logic [1:0] forward_a,
    output logic [1:0] forward_b
);

    logic ex_match_rs1;
    logic ex_match_rs2;
    logic wb_match_rs1;
    logic wb_match_rs2;

    always_comb begin
        ex_match_rs1 = ex_mem_reg_write &&
                       ex_mem_rd != 5'd0 &&
                       ex_mem_rd == id_ex_rs1;

        ex_match_rs2 = ex_mem_reg_write &&
                       ex_mem_rd != 5'd0 &&
                       ex_mem_rd == id_ex_rs2;

        wb_match_rs1 = mem_wb_reg_write &&
                       mem_wb_rd != 5'd0 &&
                       mem_wb_rd == id_ex_rs1;

        wb_match_rs2 = mem_wb_reg_write &&
                       mem_wb_rd != 5'd0 &&
                       mem_wb_rd == id_ex_rs2;

        forward_a = 2'b00;
        forward_b = 2'b00;

        // The newest matching instruction always takes priority.
        // A load in EX/MEM blocks forwarding of an older WB value.
        if (ex_match_rs1) begin
            if (!ex_mem_mem_to_reg)
                forward_a = 2'b10;
        end
        else if (wb_match_rs1) begin
            forward_a = 2'b01;
        end

        if (ex_match_rs2) begin
            if (!ex_mem_mem_to_reg)
                forward_b = 2'b10;
        end
        else if (wb_match_rs2) begin
            forward_b = 2'b01;
        end
    end

endmodule
