// PipeGuard-RV — simulation-only lock-step harness (NOT synthesized)
//
// Instantiates the UNMODIFIED snapshot core (rtl/core/riscv_pipeline_cpu.sv)
// and the research top pipeguard_cpu side by side on the same clock and reset.
// The cocotb test loads identical programs into both instruction memories and
// compares every externally visible output every cycle, plus final register
// file and data memory contents.

`include "pipeguard_defs.svh"

module tb_lockstep #(
    parameter int MONITOR_CFG = 0
);

    logic clk;
    logic rst;

    // Reference (unmodified Lab 06 snapshot)
    logic [31:0] ref_fetch_pc, ref_decode_pc, ref_execute_pc, ref_mem_pc, ref_wb_pc;
    logic [31:0] ref_wb_data;
    logic [4:0]  ref_wb_rd;
    logic        ref_wb_reg_write, ref_load_use_stall, ref_branch_redirect;
    logic        ref_alignment_fault, ref_memory_alignment_error;
    logic        ref_memory_access_error, ref_illegal_instruction;

    // Device under test (research top)
    logic [31:0] dut_fetch_pc, dut_decode_pc, dut_execute_pc, dut_mem_pc, dut_wb_pc;
    logic [31:0] dut_wb_data;
    logic [4:0]  dut_wb_rd;
    logic        dut_wb_reg_write, dut_load_use_stall, dut_branch_redirect;
    logic        dut_alignment_fault, dut_memory_alignment_error;
    logic        dut_memory_access_error, dut_illegal_instruction;
    logic        dut_fault_detected, dut_fault_sticky;
    logic [`PG_FAULT_CLASS_W-1:0] dut_fault_class;

    riscv_pipeline_cpu ref_cpu (
        .clk(clk), .rst(rst),
        .fetch_pc(ref_fetch_pc), .decode_pc(ref_decode_pc),
        .execute_pc(ref_execute_pc), .mem_pc(ref_mem_pc), .wb_pc(ref_wb_pc),
        .wb_data(ref_wb_data), .wb_rd(ref_wb_rd), .wb_reg_write(ref_wb_reg_write),
        .load_use_stall(ref_load_use_stall), .branch_redirect(ref_branch_redirect),
        .alignment_fault(ref_alignment_fault),
        .memory_alignment_error(ref_memory_alignment_error),
        .memory_access_error(ref_memory_access_error),
        .illegal_instruction(ref_illegal_instruction)
    );

    pipeguard_cpu #(.MONITOR_CFG(MONITOR_CFG)) dut_cpu (
        .clk(clk), .rst(rst),
        .fetch_pc(dut_fetch_pc), .decode_pc(dut_decode_pc),
        .execute_pc(dut_execute_pc), .mem_pc(dut_mem_pc), .wb_pc(dut_wb_pc),
        .wb_data(dut_wb_data), .wb_rd(dut_wb_rd), .wb_reg_write(dut_wb_reg_write),
        .load_use_stall(dut_load_use_stall), .branch_redirect(dut_branch_redirect),
        .alignment_fault(dut_alignment_fault),
        .memory_alignment_error(dut_memory_alignment_error),
        .memory_access_error(dut_memory_access_error),
        .illegal_instruction(dut_illegal_instruction),
        .fault_detected(dut_fault_detected),
        .fault_sticky(dut_fault_sticky),
        .fault_class(dut_fault_class)
    );

endmodule
