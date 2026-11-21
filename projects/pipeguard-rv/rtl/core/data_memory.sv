
module data_memory #(
    parameter int MEM_SIZE = 1024
)(
    input  logic        clk,
    input  logic        rst,
    input  logic        mem_read,
    input  logic        mem_write,
    input  logic [31:0] address,
    input  logic [31:0] write_data,
    input  logic [2:0]  funct3,

    output logic [31:0] read_data,
    output logic        alignment_error,
    output logic        access_error
);

    logic [7:0] memory [0:MEM_SIZE-1];

    logic valid_access;
    logic [2:0] access_size;
    logic [31:0] raw_data;
    logic invalid_operation;

    always_comb begin
        access_size = 3'd0;
        invalid_operation = 1'b0;

        if (mem_read && mem_write) begin
            invalid_operation = 1'b1;
        end
        else if (mem_read) begin
            case (funct3)
                3'b000, 3'b100: access_size = 3'd1;
                3'b001, 3'b101: access_size = 3'd2;
                3'b010:         access_size = 3'd4;
                default:        invalid_operation = 1'b1;
            endcase
        end
        else if (mem_write) begin
            case (funct3)
                3'b000: access_size = 3'd1;
                3'b001: access_size = 3'd2;
                3'b010: access_size = 3'd4;
                default: invalid_operation = 1'b1;
            endcase
        end

        alignment_error = 1'b0;

        if (mem_read || mem_write) begin
            if (access_size == 3'd2 && address[0] != 1'b0)
                alignment_error = 1'b1;

            if (access_size == 3'd4 && address[1:0] != 2'b00)
                alignment_error = 1'b1;
        end

        access_error = 1'b0;

        if (mem_read || mem_write) begin
            if (invalid_operation)
                access_error = 1'b1;
            else if (address >= MEM_SIZE)
                access_error = 1'b1;
            else if (access_size > MEM_SIZE - address)
                access_error = 1'b1;
        end

        valid_access = (mem_read || mem_write) &&
                       !alignment_error &&
                       !access_error;
    end

    // Synchronous store operations.
    always_ff @(posedge clk) begin
        if (!rst && mem_write && valid_access) begin
            case (access_size)
                3'd1: begin
                    memory[address] <= write_data[7:0];
                end

                3'd2: begin
                    memory[address]     <= write_data[7:0];
                    memory[address + 1] <= write_data[15:8];
                end

                3'd4: begin
                    memory[address]     <= write_data[7:0];
                    memory[address + 1] <= write_data[15:8];
                    memory[address + 2] <= write_data[23:16];
                    memory[address + 3] <= write_data[31:24];
                end

                default: begin
                end
            endcase
        end
    end

    // Combinational load operations.
    always_comb begin
        raw_data = 32'b0;
        read_data = 32'b0;

        if (mem_read && valid_access) begin
            raw_data[7:0] = memory[address];

            if (access_size >= 3'd2)
                raw_data[15:8] = memory[address + 1];

            if (access_size == 3'd4) begin
                raw_data[23:16] = memory[address + 2];
                raw_data[31:24] = memory[address + 3];
            end

            case (funct3)
                3'b000: read_data = {{24{raw_data[7]}},
                                    raw_data[7:0]};

                3'b001: read_data = {{16{raw_data[15]}},
                                    raw_data[15:0]};

                3'b010: read_data = raw_data;

                3'b100: read_data = {24'b0, raw_data[7:0]};

                3'b101: read_data = {16'b0, raw_data[15:0]};

                default: read_data = 32'b0;
            endcase
        end
    end

endmodule
