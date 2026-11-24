// =============================================================================
// PipeGuard-RV — observation-enabled research copy of the Lab 06 CPU
//
// Derived from: rtl/core/riscv_pipeline_cpu.sv (byte-identical to
//               labs/06-riscv-pipeline/rtl/riscv_pipeline_cpu.sv, commit 4b7643e)
//
// Changes relative to the original (ALL changes are listed here):
//   1. Module renamed riscv_pipeline_cpu -> riscv_pipeline_cpu_obs so that the
//      unmodified original can be instantiated next to it for lock-step
//      equivalence testing.
//   2. Added output ports prefixed `obs_`. Every obs_ port is a plain
//      continuous assignment of an already-existing internal net. No logic,
//      register, or connection of the original datapath/control is altered.
//   3. The `ifdef ENABLE_WAVEFORM` and `ifdef ENABLE_PERF_MONITOR` blocks of
//      the original were not carried over. Both are disabled by default and
//      are simulation instrumentation only, so the default elaboration of the
//      original and of this copy contain the same functional logic.
//
// Fault-free equivalence with the original is demonstrated by
// tb/test_b0_equivalence.py (lock-step, every output, every cycle).
//
// Observation semantics (see docs/signal_map.md for the full map):
//   * "receiving" = the net that is physically connected to the register it
//     controls.  "generated-only" = produced by pipeline_control but not
//     connected to any register in this core.
//   * obs_pc_stall    receiving: program_counter.stall AND if_id_register.stall
//   * obs_pc_redirect receiving: program_counter.branch_taken AND
//                     if_id_register.flush   (same net as branch_redirect)
//   * obs_if_id_stall_gen / obs_if_id_flush_gen: generated-only. The IF/ID
//     register is driven by pc_stall / pc_redirect instead (see if_id_stage).
//   * obs_id_ex_stall / obs_id_ex_flush: receiving (execute_forwarding_stage).
//   * obs_branch_taken / obs_branch_target / obs_invalid_branch: raw EX-stage
//     branch-unit results, i.e. control INTENT before pipeline_control.
//   * The core has no architectural per-stage valid bits; bubbles are encoded
//     as zeroed registers (IF/ID: pc=0, instr=NOP 0x00000013; ID/EX: all 0).
// =============================================================================

module riscv_pipeline_cpu_obs (
    input logic clk,
    input logic rst,

    output logic [31:0] fetch_pc,
    output logic [31:0] decode_pc,
    output logic [31:0] execute_pc,
    output logic [31:0] mem_pc,
    output logic [31:0] wb_pc,

    output logic [31:0] wb_data,
    output logic [4:0]  wb_rd,
    output logic        wb_reg_write,

    output logic        load_use_stall,
    output logic        branch_redirect,
    output logic        alignment_fault,
    output logic        memory_alignment_error,
    output logic        memory_access_error,
    output logic        illegal_instruction,

    // ---- Observation ports (research addition, wires only) ------------------
    // IF / ID
    output logic [31:0] obs_fetch_instruction,
    output logic [31:0] obs_decode_instruction,
    output logic [6:0]  obs_id_opcode,
    output logic [4:0]  obs_id_rs1,
    output logic [4:0]  obs_id_rs2,
    // Pipeline control: receiving nets
    output logic        obs_pc_stall,
    output logic        obs_pc_redirect,
    output logic [31:0] obs_pc_target,
    output logic        obs_id_ex_stall,
    output logic        obs_id_ex_flush,
    // Pipeline control: generated-only nets (not connected to IF/ID)
    output logic        obs_if_id_stall_gen,
    output logic        obs_if_id_flush_gen,
    // EX-stage branch intent (before pipeline_control)
    output logic        obs_branch_taken,
    output logic [31:0] obs_branch_target,
    output logic        obs_invalid_branch,
    // EX-stage register fields (for independent hazard recomputation)
    output logic [4:0]  obs_ex_rd,
    output logic        obs_ex_mem_read,
    output logic        obs_ex_mem_write,
    output logic        obs_ex_reg_write,
    output logic        obs_ex_jump
);

    // Decode signals
    logic [31:0] fetch_instruction;
    logic [31:0] decode_instruction;
    logic [31:0] immediate;
    logic [31:0] rs1_data, rs2_data;
    logic [31:0] decode_rs1_data, decode_rs2_data;
    logic [4:0] rd, rs1, rs2;
    logic [2:0] funct3;
    logic [6:0] funct7, opcode;

    logic reg_write, mem_read, mem_write;
    logic mem_to_reg, alu_src, branch, jump;

    // Pipeline control
    logic pc_stall, if_id_stall, if_id_flush;
    logic id_ex_stall, id_ex_flush;
    logic [31:0] pc_target;

    // Execute outputs
    logic [31:0] alu_result, store_data;
    logic [31:0] branch_target, link_address;
    logic [4:0] execute_rd;
    logic [2:0] execute_funct3;
    logic execute_reg_write, execute_mem_read;
    logic execute_mem_write, execute_mem_to_reg;
    logic execute_jump;
    logic alu_zero, alu_less_than;
    logic invalid_operation, invalid_branch;
    logic branch_taken;
    logic [1:0] forward_a, forward_b;
    logic unresolved_load_dependency;

    // Memory outputs
    logic [31:0] mem_alu_result;
    logic [31:0] mem_read_data;
    logic [31:0] mem_link_address;
    logic [4:0] mem_rd;
    logic mem_reg_write, mem_mem_to_reg, mem_jump;

    logic [31:0] ex_mem_forward_data;

    // IF + ID, including the register file
    if_id_stage frontend (
        .clk(clk),
        .rst(rst),
        .stall(pc_stall),
        .branch_taken(branch_redirect),
        .branch_target(pc_target),

        .wb_enable(wb_reg_write),
        .wb_addr(wb_rd),
        .wb_data(wb_data),

        .fetch_pc(fetch_pc),
        .fetch_instruction(fetch_instruction),
        .decode_pc(decode_pc),
        .decode_instruction(decode_instruction),
        .immediate(immediate),
        .rs1_data(rs1_data),
        .rs2_data(rs2_data),

        .rd(rd),
        .rs1(rs1),
        .rs2(rs2),
        .funct3(funct3),
        .funct7(funct7),
        .opcode(opcode),

        .reg_write(reg_write),
        .mem_read(mem_read),
        .mem_write(mem_write),
        .mem_to_reg(mem_to_reg),
        .alu_src(alu_src),
        .branch(branch),
        .jump(jump),
        .illegal_instruction(illegal_instruction)
    );

    // Writeback-to-Decode bypass handles a register
    // being read while the same register is written.
    assign decode_rs1_data =
        wb_reg_write && wb_rd == rs1 && rs1 != 5'd0
        ? wb_data : rs1_data;

    assign decode_rs2_data =
        wb_reg_write && wb_rd == rs2 && rs2 != 5'd0
        ? wb_data : rs2_data;

    // Load-use dependency detection
    hazard_detection_unit hazard_unit (
        .id_ex_rd(execute_rd),
        .id_ex_mem_read(execute_mem_read),
        .if_id_rs1(rs1),
        .if_id_rs2(rs2),
        .if_id_opcode(opcode),
        .stall_request(load_use_stall)
    );

    // Branch and stall coordination
    pipeline_control control_unit (
        .branch_taken_ex(branch_taken),
        .branch_target_ex(branch_target),
        .stall_request(load_use_stall),
        .invalid_branch_ex(invalid_branch),

        .pc_stall(pc_stall),
        .pc_redirect(branch_redirect),
        .pc_target(pc_target),
        .if_id_stall(if_id_stall),
        .if_id_flush(if_id_flush),
        .id_ex_stall(id_ex_stall),
        .id_ex_flush(id_ex_flush),
        .alignment_fault(alignment_fault)
    );

    // EX/MEM forwarding must select the jump link
    // address for JAL and JALR instructions.
    assign ex_mem_forward_data =
        mem_jump ? mem_link_address : mem_alu_result;

    execute_forwarding_stage execute_unit (
        .clk(clk),
        .rst(rst),
        .stall(id_ex_stall),
        .flush(id_ex_flush),

        .pc_in(decode_pc),
        .rs1_data_in(decode_rs1_data),
        .rs2_data_in(decode_rs2_data),
        .immediate_in(immediate),
        .rd_in(rd),
        .rs1_in(rs1),
        .rs2_in(rs2),
        .funct3_in(funct3),
        .funct7_in(funct7),
        .opcode_in(opcode),

        .reg_write_in(reg_write),
        .mem_read_in(mem_read),
        .mem_write_in(mem_write),
        .mem_to_reg_in(mem_to_reg),
        .alu_src_in(alu_src),
        .branch_in(branch),
        .jump_in(jump),

        .ex_mem_forward_data(ex_mem_forward_data),
        .ex_mem_rd(mem_rd),
        .ex_mem_reg_write(mem_reg_write),
        .ex_mem_mem_to_reg(mem_mem_to_reg),

        .mem_wb_forward_data(wb_data),
        .mem_wb_rd(wb_rd),
        .mem_wb_reg_write(wb_reg_write),

        .alu_result(alu_result),
        .store_data(store_data),
        .execute_pc(execute_pc),
        .execute_rd(execute_rd),
        .execute_funct3(execute_funct3),

        .execute_reg_write(execute_reg_write),
        .execute_mem_read(execute_mem_read),
        .execute_mem_write(execute_mem_write),
        .execute_mem_to_reg(execute_mem_to_reg),
        .execute_jump(execute_jump),

        .alu_zero(alu_zero),
        .alu_less_than(alu_less_than),
        .invalid_operation(invalid_operation),
        .branch_taken(branch_taken),
        .branch_target(branch_target),
        .link_address(link_address),
        .invalid_branch(invalid_branch),

        .forward_a(forward_a),
        .forward_b(forward_b),
        .unresolved_load_dependency(
            unresolved_load_dependency
        )
    );

    memory_stage memory_unit (
        .clk(clk),
        .rst(rst),
        .stall(1'b0),
        .flush(1'b0),

        .pc_in(execute_pc),
        .alu_result_in(alu_result),
        .store_data_in(store_data),
        .link_address_in(link_address),
        .rd_in(execute_rd),
        .funct3_in(execute_funct3),

        .reg_write_in(execute_reg_write),
        .mem_read_in(execute_mem_read),
        .mem_write_in(execute_mem_write),
        .mem_to_reg_in(execute_mem_to_reg),
        .jump_in(execute_jump),

        .mem_pc(mem_pc),
        .mem_alu_result(mem_alu_result),
        .mem_read_data(mem_read_data),
        .mem_link_address(mem_link_address),
        .mem_rd(mem_rd),
        .mem_reg_write(mem_reg_write),
        .mem_mem_to_reg(mem_mem_to_reg),
        .mem_jump(mem_jump),

        .alignment_error(memory_alignment_error),
        .access_error(memory_access_error)
    );

    writeback_stage writeback_unit (
        .clk(clk),
        .rst(rst),
        .stall(1'b0),
        .flush(1'b0),

        .pc_in(mem_pc),
        .alu_result_in(mem_alu_result),
        .mem_read_data_in(mem_read_data),
        .link_address_in(mem_link_address),
        .rd_in(mem_rd),

        .reg_write_in(mem_reg_write),
        .mem_to_reg_in(mem_mem_to_reg),
        .jump_in(mem_jump),

        .wb_data(wb_data),
        .wb_rd(wb_rd),
        .wb_reg_write(wb_reg_write),
        .wb_pc(wb_pc)
    );

    // ---- Observation assignments (research addition) ------------------------
    assign obs_fetch_instruction  = fetch_instruction;
    assign obs_decode_instruction = decode_instruction;
    assign obs_id_opcode          = opcode;
    assign obs_id_rs1             = rs1;
    assign obs_id_rs2             = rs2;

    assign obs_pc_stall           = pc_stall;
    assign obs_pc_redirect        = branch_redirect;
    assign obs_pc_target          = pc_target;
    assign obs_id_ex_stall        = id_ex_stall;
    assign obs_id_ex_flush        = id_ex_flush;

    assign obs_if_id_stall_gen    = if_id_stall;
    assign obs_if_id_flush_gen    = if_id_flush;

    assign obs_branch_taken       = branch_taken;
    assign obs_branch_target      = branch_target;
    assign obs_invalid_branch     = invalid_branch;

    assign obs_ex_rd              = execute_rd;
    assign obs_ex_mem_read        = execute_mem_read;
    assign obs_ex_mem_write       = execute_mem_write;
    assign obs_ex_reg_write       = execute_reg_write;
    assign obs_ex_jump            = execute_jump;

endmodule
