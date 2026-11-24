// =============================================================================
// PipeGuard-RV — common configurable CPU top level
//
// One top for every research configuration so that B0, M0, M1 and M2 differ
// ONLY in the monitor instantiated here (selected by MONITOR_CFG) and expose
// identical external ports:
//   * every output port of the original riscv_pipeline_cpu, unchanged
//   * the common alarm interface: fault_detected, fault_sticky, fault_class
//
// Alarm interface contract (all configurations):
//   fault_detected : a monitor rule fired for the observation sampled in this
//                    cycle (meaning finalised per monitor; 0 in B0)
//   fault_sticky   : registered, set by fault_detected, cleared only by rst
//   fault_class    : pipeguard_pkg::FC_* code of the first alarm since reset
//                    (FC_NONE while fault_sticky == 0)
// There is deliberately no software/port-driven alarm clear: a clear input
// would itself be a fault-injection target. Reset is the only clear.
//
// Monitor configurations not yet implemented fail elaboration (instantiation
// of an undefined module) instead of silently producing an unprotected core.
// =============================================================================

`include "pipeguard_defs.svh"

module pipeguard_cpu #(
    parameter int MONITOR_CFG = `PG_CFG_B0
) (
    input  logic        clk,
    input  logic        rst,

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

    output logic                           fault_detected,
    output logic                           fault_sticky,
    output logic [`PG_FAULT_CLASS_W-1:0]   fault_class
);

    // Observation bundle (consumed only by monitors)
    logic [31:0] obs_fetch_instruction, obs_decode_instruction;
    logic [6:0]  obs_id_opcode;
    logic [4:0]  obs_id_rs1, obs_id_rs2;
    logic        obs_pc_stall, obs_pc_redirect;
    logic [31:0] obs_pc_target;
    logic        obs_id_ex_stall, obs_id_ex_flush;
    logic        obs_if_id_stall_gen, obs_if_id_flush_gen;
    logic        obs_branch_taken, obs_invalid_branch;
    logic [31:0] obs_branch_target;
    logic [4:0]  obs_ex_rd;
    logic        obs_ex_mem_read, obs_ex_mem_write, obs_ex_reg_write, obs_ex_jump;

    riscv_pipeline_cpu_obs u_core (
        .clk                    (clk),
        .rst                    (rst),
        .fetch_pc               (fetch_pc),
        .decode_pc              (decode_pc),
        .execute_pc             (execute_pc),
        .mem_pc                 (mem_pc),
        .wb_pc                  (wb_pc),
        .wb_data                (wb_data),
        .wb_rd                  (wb_rd),
        .wb_reg_write           (wb_reg_write),
        .load_use_stall         (load_use_stall),
        .branch_redirect        (branch_redirect),
        .alignment_fault        (alignment_fault),
        .memory_alignment_error (memory_alignment_error),
        .memory_access_error    (memory_access_error),
        .illegal_instruction    (illegal_instruction),

        .obs_fetch_instruction  (obs_fetch_instruction),
        .obs_decode_instruction (obs_decode_instruction),
        .obs_id_opcode          (obs_id_opcode),
        .obs_id_rs1             (obs_id_rs1),
        .obs_id_rs2             (obs_id_rs2),
        .obs_pc_stall           (obs_pc_stall),
        .obs_pc_redirect        (obs_pc_redirect),
        .obs_pc_target          (obs_pc_target),
        .obs_id_ex_stall        (obs_id_ex_stall),
        .obs_id_ex_flush        (obs_id_ex_flush),
        .obs_if_id_stall_gen    (obs_if_id_stall_gen),
        .obs_if_id_flush_gen    (obs_if_id_flush_gen),
        .obs_branch_taken       (obs_branch_taken),
        .obs_branch_target      (obs_branch_target),
        .obs_invalid_branch     (obs_invalid_branch),
        .obs_ex_rd              (obs_ex_rd),
        .obs_ex_mem_read        (obs_ex_mem_read),
        .obs_ex_mem_write       (obs_ex_mem_write),
        .obs_ex_reg_write       (obs_ex_reg_write),
        .obs_ex_jump            (obs_ex_jump)
    );

    generate
        if (MONITOR_CFG == `PG_CFG_B0) begin : g_b0
            // Unprotected reference: no monitor logic, alarms tied low.
            assign fault_detected = 1'b0;
            assign fault_sticky   = 1'b0;
            assign fault_class    = `PG_FC_NONE;
        end
        else begin : g_unsupported
            // M0/M1/M2 are added in Phases 3-4. Until then any other value is
            // an elaboration error in every tool (undefined module).
            pipeguard_monitor_cfg_not_implemented u_cfg_error ();
        end
    endgenerate

endmodule
