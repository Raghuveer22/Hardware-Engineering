#!/usr/bin/env bash
# ==============================================================================
# Master Execution Script for Tensor Systolic Array & Pre-Silicon Emulation
# ==============================================================================

set -e

# Activate virtual environment
source .venv/bin/activate

echo "======================================================================"
echo "🎯 1. RUNNING PYTHON COCOTB TESTBENCHES (PE & Systolic Array)"
echo "======================================================================"
python sim/run.py --dut all --sim icarus

echo ""
echo "======================================================================"
echo "🎯 2. BUILDING & RUNNING C++ VERILATOR CYCLE-ACCURATE EMULATOR"
echo "======================================================================"
verilator --top-module systolic_array --cc --trace -Irtl rtl/mac_unit.sv rtl/pe.sv rtl/systolic_array.sv -Mdir cpp_emulation/verilated

clang++ -std=c++17 \
    -I/opt/homebrew/share/verilator/include \
    -I/opt/homebrew/share/verilator/include/vltstd \
    -Icpp_emulation/verilated \
    /opt/homebrew/share/verilator/include/verilated.cpp \
    /opt/homebrew/share/verilator/include/verilated_vcd_c.cpp \
    /opt/homebrew/share/verilator/include/verilated_threads.cpp \
    cpp_emulation/verilated/Vsystolic_array*.cpp \
    cpp_emulation/main.cpp \
    -o cpp_emulation/emulator

./cpp_emulation/emulator

echo ""
echo "======================================================================"
echo "✨ ALL HARDWARE VERIFICATION & PRE-SILICON EMULATION TESTS PASSED!"
echo "======================================================================"
