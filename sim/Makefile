# ==============================================================================
# Makefile for Cocotb Simulation
# Supports: SIM=verilator or SIM=icarus
# ==============================================================================

SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PWD = $(shell pwd)
WP = $(PWD)/..

ifeq ($(DUT),pe)
    VERILOG_SOURCES = $(WP)/rtl/mac_unit.sv $(WP)/rtl/pe.sv
    TOPLEVEL = pe
    MODULE = test_pe
else
    VERILOG_SOURCES = $(WP)/rtl/mac_unit.sv $(WP)/rtl/pe.sv $(WP)/rtl/systolic_array.sv
    TOPLEVEL = systolic_array
    MODULE = test_systolic_array
endif

# Extra compiler arguments
ifeq ($(SIM),verilator)
    COMPILE_ARGS += -Wno-WIDTHEXPAND -Wno-WIDTHTRUNC --trace
endif

ifeq ($(SIM),icarus)
    COMPILE_ARGS += -g2012
endif

# Include Cocotb standard simulator makefiles
include $(shell cocotb-config --makefiles)/Makefile.sim
