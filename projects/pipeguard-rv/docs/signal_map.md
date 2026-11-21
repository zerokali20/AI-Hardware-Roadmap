# Signal Map & Observability Reference — PipeGuard-RV

## 1. Overview and Observability Constraint

A central finding of the Phase 0 audit is that **`riscv_pipeline_cpu.sv` exposes only a subset of pipeline state at its top-level module ports**. While all program counter values along each stage (`fetch_pc` through `wb_pc`) and major hazard/error indicators are exported, critical internal control nets—such as stage-specific stall/flush lines and intermediate branch target calculations—remain internal to the core.

### Architectural Constraint
- External wrapper tops (e.g. `pipeguard_top_b0.sv`, `pipeguard_top_m0.sv`) can directly observe top-level ports.
- Deeper monitors (M1/M2) requiring internal nets (`if_id_stall`, `id_ex_flush`, `branch_taken`, `stall_request`) must use a tapped research wrapper (`rtl/top/`) that exposes these nets without altering the core datapath logic in `rtl/core/`.

---

## 2. Signal Verification Table

This table maps all critical pipeline, datapath, and control signals verified against the canonical SystemVerilog source files in `labs/06-riscv-pipeline/rtl/`.

| Signal Name | Source Module | Pipeline Stage | Width | Observable at Top? | Functional Role / Description |
|---|---|---|---|---|---|
| `fetch_pc` | `instruction_fetch` | IF | 32 | **Yes** | Current address presented to instruction memory |
| `decode_pc` | `if_id_stage` | ID | 32 | **Yes** | PC of instruction currently in decode stage |
| `execute_pc` | `execute_stage` | EX | 32 | **Yes** | PC of instruction currently in execution stage |
| `mem_pc` | `ex_mem_register` | MEM | 32 | **Yes** | PC of instruction currently in memory access stage |
| `wb_pc` | `mem_wb_register` | WB | 32 | **Yes** | PC of instruction completing writeback |
| `wb_data` | `writeback_stage` | WB | 32 | **Yes** | Final architectural data committed to register file |
| `wb_rd` | `mem_wb_register` | WB | 5 | **Yes** | Destination register index committed |
| `wb_reg_write` | `mem_wb_register` | WB | 1 | **Yes** | Register write enable signal at writeback |
| `load_use_stall` | `hazard_detection_unit` | ID | 1 | **Yes** | Active when load-use data dependency stalls IF/ID |
| `branch_redirect` | `pipeline_control` | EX | 1 | **Yes** | Top-level signal driving PC redirect (= internal `pc_redirect`) |
| `alignment_fault` | `pipeline_control` | EX | 1 | **Yes** | Asserted when target address is not 4-byte aligned |
| `memory_alignment_error` | `data_memory` | MEM | 1 | **Yes** | Data memory access address misaligned |
| `memory_access_error` | `data_memory` | MEM | 1 | **Yes** | Data memory access out of bound address |
| `illegal_instruction` | `rv32i_decoder` | ID | 1 | **Yes** | Unrecognized instruction opcode/funct decoded |
| `pc_stall` | `pipeline_control` | IF | 1 | **No (Internal)** | Freezes program counter register |
| `pc_target` | `pipeline_control` | IF | 32 | **No (Internal)** | Multiplexed next-PC address driven into fetch |
| `if_id_stall` | `pipeline_control` | IF/ID | 1 | **No (Internal)** | Freezes IF/ID pipeline register |
| `if_id_flush` | `pipeline_control` | IF/ID | 1 | **No (Internal)** | Clears IF/ID register (inserts bubble / NOP) |
| `id_ex_stall` | `pipeline_control` | ID/EX | 1 | **No (Internal)** | Freezes ID/EX pipeline register |
| `id_ex_flush` | `pipeline_control` | ID/EX | 1 | **No (Internal)** | Clears ID/EX register (inserts bubble / NOP) |
| `branch_taken` | `branch_unit` | EX | 1 | **No (Internal)** | Branch evaluation outcome (condition satisfied) |
| `branch_target` | `branch_unit` | EX | 32 | **No (Internal)** | Calculated target address ($PC_{EX} + \text{imm}$) |
| `invalid_branch` | `branch_unit` | EX | 1 | **No (Internal)** | Target address misaligned ($[1:0] \neq 00$) |
| `stall_request` | `hazard_detection_unit` | ID | 1 | **No (Internal)** | Raw hazard request from load-use detector |
| `forward_a` | `forwarding_unit` | EX | 2 | **No (Internal)** | Forwarding select for ALU operand A |
| `forward_b` | `forwarding_unit` | EX | 2 | **No (Internal)** | Forwarding select for ALU operand B |
| `unresolved_load_dependency` | `hazard_detection_unit` | ID | 1 | **No (Internal)** | Load dependency cannot be resolved by bypass |
| `link_address` | `execute_stage` | EX | 32 | **No (Internal)** | Return address for JAL/JALR ($PC_{EX} + 4$) |
| `alu_result` | `alu` | EX | 32 | **No (Internal)** | Direct 32-bit output of the arithmetic logic unit |
| `store_data` | `execute_stage` | EX | 32 | **No (Internal)** | Forwarded write data routed to memory stage |

---

## 3. Pipeline Control Priority Logic

The internal arbitration in `labs/06-riscv-pipeline/rtl/pipeline_control.sv` enforces strict priority rules between branching, alignment violations, and hazard stalls:

```systemverilog
// 1. Branch redirect & Alignment Evaluation
alignment_fault = valid_redirect && (branch_target[1:0] != 2'b00);
pc_redirect     = valid_redirect && !alignment_fault;

// 2. Redirect Action (Highest Priority)
// Flushes speculative instructions in fetch and decode stages
if_id_flush = pc_redirect;
id_ex_flush = pc_redirect;

// 3. Stall Action (Hazard Stalls)
// If hazard detected, hold PC and IF/ID, bubble ID/EX
pc_stall     = stall_request;
if_id_stall  = stall_request;
id_ex_flush  = id_ex_flush || stall_request;

// 4. Alignment Fault Exception Action
// Freezes PC and IF/ID to trap faulting state, clears execution
pc_stall    |= alignment_fault;
if_id_stall |= alignment_fault;
id_ex_flush |= alignment_fault;
```

### Critical Rules for Invariant Checkers
1. **Redirect Trumps Stall:** When `valid_redirect` occurs, `pc_redirect` flushes the upstream stages regardless of whether `stall_request` is active.
2. **Misaligned Branch Suppresses Redirect:** An alignment fault sets `alignment_fault = 1` and `pc_redirect = 0`. Instead of redirecting to the bad address, the pipeline initiates a freeze/stall.
3. **Ghost Bubbles:** If transient noise flips `id_ex_flush` without either `pc_redirect` or `stall_request` being asserted, an illegitimate bubble is introduced into the datapath. M2 monitors monitor this exact invariant.
