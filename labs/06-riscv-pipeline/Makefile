
SIM ?= icarus
TOPLEVEL_LANG = verilog

TEST ?= pc

ifeq ($(TEST),pc)
    VERILOG_SOURCES = $(PWD)/rtl/program_counter.sv
    TOPLEVEL = program_counter
    MODULE = test_program_counter

else ifeq ($(TEST),ifid)
    VERILOG_SOURCES = $(PWD)/rtl/if_id_register.sv
    TOPLEVEL = if_id_register
    MODULE = test_if_id_register

else ifeq ($(TEST),if)
    VERILOG_SOURCES = $(PWD)/rtl/program_counter.sv \
                      $(PWD)/rtl/instruction_memory.sv \
                      $(PWD)/rtl/instruction_fetch.sv
    TOPLEVEL = instruction_fetch
    MODULE = test_instruction_fetch

else ifeq ($(TEST),decode)
    VERILOG_SOURCES = $(PWD)/rtl/rv32i_decoder.sv
    TOPLEVEL = rv32i_decoder
    MODULE = test_rv32i_decoder
else ifeq ($(TEST),imm)
    VERILOG_SOURCES = $(PWD)/rtl/immediate_generator.sv
    TOPLEVEL = immediate_generator
    MODULE = test_immediate_generator
else ifeq ($(TEST),regfile)
    VERILOG_SOURCES = $(PWD)/rtl/register_file.sv
    TOPLEVEL = register_file
    MODULE = test_register_file
else ifeq ($(TEST),ifidstage)
    VERILOG_SOURCES = $(PWD)/rtl/program_counter.sv \
                      $(PWD)/rtl/instruction_memory.sv \
                      $(PWD)/rtl/instruction_fetch.sv \
                      $(PWD)/rtl/if_id_register.sv \
                      $(PWD)/rtl/rv32i_decoder.sv \
                      $(PWD)/rtl/immediate_generator.sv \
                      $(PWD)/rtl/register_file.sv \
                      $(PWD)/rtl/if_id_stage.sv
    TOPLEVEL = if_id_stage
    MODULE = test_if_id_stage
else ifeq ($(TEST),alu)
    VERILOG_SOURCES = $(PWD)/rtl/alu.sv
    TOPLEVEL = alu
    MODULE = test_alu
else ifeq ($(TEST),aluctrl)
    VERILOG_SOURCES = $(PWD)/rtl/alu_control.sv
    TOPLEVEL = alu_control
    MODULE = test_alu_control
else ifeq ($(TEST),idex)
    VERILOG_SOURCES = $(PWD)/rtl/id_ex_register.sv
    TOPLEVEL = id_ex_register
    MODULE = test_id_ex_register
else ifeq ($(TEST),execute)
    VERILOG_SOURCES = $(PWD)/rtl/id_ex_register.sv \
                      $(PWD)/rtl/alu_control.sv \
                      $(PWD)/rtl/alu.sv \
                      $(PWD)/rtl/branch_unit.sv \
                      $(PWD)/rtl/execute_stage.sv
    TOPLEVEL = execute_stage
    MODULE = test_execute_stage
else ifeq ($(TEST),branch)
    VERILOG_SOURCES = $(PWD)/rtl/branch_unit.sv
    TOPLEVEL = branch_unit
    MODULE = test_branch_unit
else ifeq ($(TEST),exbranch)
    VERILOG_SOURCES = $(PWD)/rtl/id_ex_register.sv \
                      $(PWD)/rtl/alu_control.sv \
                      $(PWD)/rtl/alu.sv \
                      $(PWD)/rtl/branch_unit.sv \
                      $(PWD)/rtl/execute_stage.sv
    TOPLEVEL = execute_stage
    MODULE = test_execute_branch
else ifeq ($(TEST),pipectrl)
    VERILOG_SOURCES = $(PWD)/rtl/pipeline_control.sv
    TOPLEVEL = pipeline_control
    MODULE = test_pipeline_control
else ifeq ($(TEST),pipeint)
    VERILOG_SOURCES = $(PWD)/rtl/program_counter.sv \
                      $(PWD)/rtl/if_id_register.sv \
                      $(PWD)/rtl/id_ex_register.sv \
                      $(PWD)/rtl/branch_unit.sv \
                      $(PWD)/rtl/pipeline_control.sv \
                      $(PWD)/rtl/pipeline_integration.sv
    TOPLEVEL = pipeline_integration
    MODULE = test_pipeline_integration
else ifeq ($(TEST),exmem)
    VERILOG_SOURCES = $(PWD)/rtl/ex_mem_register.sv
    TOPLEVEL = ex_mem_register
    MODULE = test_ex_mem_register
else ifeq ($(TEST),dmem)
    VERILOG_SOURCES = $(PWD)/rtl/data_memory.sv
    TOPLEVEL = data_memory
    MODULE = test_data_memory
else ifeq ($(TEST),memstage)
    VERILOG_SOURCES = $(PWD)/rtl/ex_mem_register.sv \
                      $(PWD)/rtl/data_memory.sv \
                      $(PWD)/rtl/memory_stage.sv
    TOPLEVEL = memory_stage
    MODULE = test_memory_stage
else ifeq ($(TEST),memwb)
    VERILOG_SOURCES = $(PWD)/rtl/mem_wb_register.sv
    TOPLEVEL = mem_wb_register
    MODULE = test_mem_wb_register
else ifeq ($(TEST),wb)
    VERILOG_SOURCES = $(PWD)/rtl/mem_wb_register.sv \
                      $(PWD)/rtl/writeback_stage.sv
    TOPLEVEL = writeback_stage
    MODULE = test_writeback_stage
else ifeq ($(TEST),wbint)
    VERILOG_SOURCES = $(PWD)/rtl/mem_wb_register.sv \
                      $(PWD)/rtl/writeback_stage.sv \
                      $(PWD)/rtl/register_file.sv \
                      $(PWD)/rtl/register_writeback_integration.sv
    TOPLEVEL = register_writeback_integration
    MODULE = test_register_writeback_integration
else ifeq ($(TEST),forward)
    VERILOG_SOURCES = $(PWD)/rtl/forwarding_unit.sv
    TOPLEVEL = forwarding_unit
    MODULE = test_forwarding_unit
else ifeq ($(TEST),hazard)
    VERILOG_SOURCES = $(PWD)/rtl/hazard_detection_unit.sv
    TOPLEVEL = hazard_detection_unit
    MODULE = test_hazard_detection_unit
else ifeq ($(TEST),hazint)
    VERILOG_SOURCES = $(PWD)/rtl/forwarding_unit.sv \
                      $(PWD)/rtl/hazard_detection_unit.sv \
                      $(PWD)/rtl/pipeline_control.sv \
                      $(PWD)/rtl/hazard_forwarding_integration.sv
    TOPLEVEL = hazard_forwarding_integration
    MODULE = test_hazard_forwarding_integration
else ifeq ($(TEST),exforward)
    VERILOG_SOURCES = $(PWD)/rtl/id_ex_register.sv \
                      $(PWD)/rtl/alu.sv \
                      $(PWD)/rtl/alu_control.sv \
                      $(PWD)/rtl/branch_unit.sv \
                      $(PWD)/rtl/forwarding_unit.sv \
                      $(PWD)/rtl/execute_forwarding_stage.sv
    TOPLEVEL = execute_forwarding_stage
    MODULE = test_execute_forwarding_stage

else ifeq ($(TEST),cpu)
    VERILOG_SOURCES = $(PWD)/rtl/program_counter.sv \
                      $(PWD)/rtl/instruction_memory.sv \
                      $(PWD)/rtl/instruction_fetch.sv \
                      $(PWD)/rtl/if_id_register.sv \
                      $(PWD)/rtl/rv32i_decoder.sv \
                      $(PWD)/rtl/immediate_generator.sv \
                      $(PWD)/rtl/register_file.sv \
                      $(PWD)/rtl/if_id_stage.sv \
                      $(PWD)/rtl/id_ex_register.sv \
                      $(PWD)/rtl/alu.sv \
                      $(PWD)/rtl/alu_control.sv \
                      $(PWD)/rtl/branch_unit.sv \
                      $(PWD)/rtl/forwarding_unit.sv \
                      $(PWD)/rtl/hazard_detection_unit.sv \
                      $(PWD)/rtl/pipeline_control.sv \
                      $(PWD)/rtl/execute_forwarding_stage.sv \
                      $(PWD)/rtl/ex_mem_register.sv \
                      $(PWD)/rtl/data_memory.sv \
                      $(PWD)/rtl/memory_stage.sv \
                      $(PWD)/rtl/mem_wb_register.sv \
                      $(PWD)/rtl/writeback_stage.sv \
                      $(PWD)/rtl/riscv_pipeline_cpu.sv
    TOPLEVEL = riscv_pipeline_cpu
    MODULE = test_riscv_pipeline_cpu
else ifeq ($(TEST),cpuhaz)
    VERILOG_SOURCES = $(PWD)/rtl/program_counter.sv \
                      $(PWD)/rtl/instruction_memory.sv \
                      $(PWD)/rtl/instruction_fetch.sv \
                      $(PWD)/rtl/if_id_register.sv \
                      $(PWD)/rtl/rv32i_decoder.sv \
                      $(PWD)/rtl/immediate_generator.sv \
                      $(PWD)/rtl/register_file.sv \
                      $(PWD)/rtl/if_id_stage.sv \
                      $(PWD)/rtl/id_ex_register.sv \
                      $(PWD)/rtl/alu.sv \
                      $(PWD)/rtl/alu_control.sv \
                      $(PWD)/rtl/branch_unit.sv \
                      $(PWD)/rtl/forwarding_unit.sv \
                      $(PWD)/rtl/hazard_detection_unit.sv \
                      $(PWD)/rtl/pipeline_control.sv \
                      $(PWD)/rtl/execute_forwarding_stage.sv \
                      $(PWD)/rtl/ex_mem_register.sv \
                      $(PWD)/rtl/data_memory.sv \
                      $(PWD)/rtl/memory_stage.sv \
                      $(PWD)/rtl/mem_wb_register.sv \
                      $(PWD)/rtl/writeback_stage.sv \
                      $(PWD)/rtl/riscv_pipeline_cpu.sv
    TOPLEVEL = riscv_pipeline_cpu
    MODULE = test_cpu_hazards
else ifeq ($(TEST),cpuisa)
    VERILOG_SOURCES = $(wildcard $(PWD)/rtl/*.sv)
    TOPLEVEL = riscv_pipeline_cpu
    MODULE = test_cpu_rv32i
else ifeq ($(TEST),cpumembranch)
    VERILOG_SOURCES = $(wildcard $(PWD)/rtl/*.sv)
    TOPLEVEL = riscv_pipeline_cpu
    MODULE = test_cpu_memory_branch
else ifeq ($(TEST),cpuwave)
    VERILOG_SOURCES = $(wildcard $(PWD)/rtl/*.sv)
    TOPLEVEL = riscv_pipeline_cpu
    MODULE = test_riscv_pipeline_cpu
    COMPILE_ARGS += -DENABLE_WAVEFORM
else ifeq ($(TEST),cpuperf)
    VERILOG_SOURCES = $(wildcard $(PWD)/rtl/*.sv)
    TOPLEVEL = riscv_pipeline_cpu
    MODULE = test_cpu_performance
    COMPILE_ARGS += -DENABLE_PERF_MONITOR
else
    $(error Unknown TEST=$(TEST). Use pc or if)

endif

export PYTHONPATH := $(PWD)/tb:$(PYTHONPATH)

include $(shell cocotb-config --makefiles)/Makefile.sim

