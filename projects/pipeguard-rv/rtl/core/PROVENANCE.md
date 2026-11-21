# RTL Core Provenance

| Field | Value |
|---|---|
| **Source directory** | `labs/06-riscv-pipeline/rtl/` |
| **Baseline SHA** | `0be8905` |
| **Date copied** | 2026-11-21 |
| **Files copied** | 24 `.sv` files (all files in source directory) |
| **Original license** | Preserved from repository `LICENSE` file |

## Purpose

These files are an **unmodified research snapshot** of the Lab 06 five-stage RISC-V pipeline RTL.

> [!CAUTION]
> **DO NOT EDIT files in `rtl/core/`.**  
> All research modifications, instrumentation wrappers, and monitoring logic must be created in `rtl/top/` as wrapper modules that instantiate the core.  
> Keeping the core unmodified is essential for reproducibility and fair comparison.

## File List

| Module file | Description |
|---|---|
| `riscv_pipeline_cpu.sv` | Top-level CPU (has provenance header comment) |
| `pipeline_control.sv` | Hazard/flush/stall control |
| `instruction_fetch.sv` | IF stage |
| `if_id_stage.sv` / `if_id_register.sv` | IF/ID pipeline register |
| `rv32i_decoder.sv` | Instruction decoder |
| `immediate_generator.sv` | Immediate generator |
| `register_file.sv` | Register file |
| `id_ex_register.sv` | ID/EX pipeline register |
| `alu.sv` / `alu_control.sv` | ALU and control |
| `branch_unit.sv` | Branch resolution |
| `execute_stage.sv` / `execute_forwarding_stage.sv` | EX stage |
| `forwarding_unit.sv` | Data forwarding |
| `hazard_detection_unit.sv` | Load-use hazard detection |
| `ex_mem_register.sv` | EX/MEM pipeline register |
| `data_memory.sv` | Data memory |
| `memory_stage.sv` | MEM stage |
| `mem_wb_register.sv` | MEM/WB pipeline register |
| `writeback_stage.sv` / `register_writeback_integration.sv` | WB stage |
| `pipeline_integration.sv` | Integration |
| `hazard_forwarding_integration.sv` | Hazard+forwarding integration |
| `instruction_memory.sv` | Instruction memory |
| `program_counter.sv` | Program counter |
