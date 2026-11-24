// =============================================================================
// PipeGuard-RV — shared definitions
//
// Configuration identifiers and the common alarm-classification encoding used
// by every monitor configuration. Kept in a plain header so all project tools
// (Icarus Verilog, Verilator, Yosys and SymbiYosys) parse it identically.
//
// Fault-class codes 1..15 are a PROVISIONAL allocation made in Phase 2 so that
// the top-level alarm interface width is fixed before any monitor exists.
// Each monitor phase (3: M0, 4: M1/M2) finalises the codes it actually emits
// and documents them in docs/architecture.md. Unused codes are never driven.
// =============================================================================
`ifndef PIPEGUARD_DEFS_SVH
`define PIPEGUARD_DEFS_SVH

// ---- Monitor configuration selection (pipeguard_cpu.MONITOR_CFG) ------------
`define PG_CFG_B0 0  // unprotected reference, no monitor logic
`define PG_CFG_M0 1  // PC-based monitor          (Phase 3)
`define PG_CFG_M1 2  // branch-aware monitor      (Phase 4)
`define PG_CFG_M2 3  // pipeline-aware monitor    (Phase 4)

// ---- Alarm classification ---------------------------------------------------
`define PG_FAULT_CLASS_W 4

`define PG_FC_NONE              4'd0
// M0 (PC-based)
`define PG_FC_PC_MISALIGNED     4'd1
`define PG_FC_PC_OUT_OF_BOUNDS  4'd2
// M1 (branch-aware) — provisional
`define PG_FC_PC_TRANSITION     4'd3
`define PG_FC_REDIRECT_TARGET   4'd4
`define PG_FC_REDIRECT_SPURIOUS 4'd5
// M2 (pipeline-aware) — provisional
`define PG_FC_STALL_INCONSIST   4'd6
`define PG_FC_FLUSH_INCONSIST   4'd7
`define PG_FC_REDIRECT_PRIORITY 4'd8
`define PG_FC_STAGE_PROGRESS    4'd9
`define PG_FC_SIDE_EFFECT       4'd10

`endif
