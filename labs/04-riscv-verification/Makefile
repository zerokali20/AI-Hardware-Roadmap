SIM = ghdl
TOPLEVEL_LANG = vhdl

VHDL_SOURCES = $(PWD)/rtl/rv32i_decoder.vhd

TOPLEVEL = rv32i_decoder
COCOTB_TEST_MODULES = tests.test_rv32i_decoder

include $(shell cocotb-config --makefiles)/Makefile.sim
