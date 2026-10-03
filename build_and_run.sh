#!/usr/bin/env bash
# ==============================================================================
# Master Execution Script for Tensor Systolic Array & Pre-Silicon Emulation
# Works on: macOS (Apple Silicon & Intel), Linux, and Windows (WSL / Git Bash)
# ==============================================================================

set -e

# Detect Script and Project Directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment if present
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
elif [ -f ".venv/Scripts/activate" ]; then
    source .venv/Scripts/activate
fi

# Detect Python interpreter
PYTHON_BIN="python3"
if command -v python &>/dev/null; then
    PYTHON_BIN="python"
fi

echo "======================================================================"
echo "🎯 1. RUNNING PYTHON COCOTB TESTBENCHES (PE & Systolic Array)"
echo "======================================================================"
"$PYTHON_BIN" sim/run.py --dut all --sim icarus

echo ""
echo "======================================================================"
echo "🎯 2. BUILDING & RUNNING C++ VERILATOR CYCLE-ACCURATE EMULATOR"
echo "======================================================================"
"$PYTHON_BIN" cpp_emulation/build_emulator.py --run

echo ""
echo "======================================================================"
echo "✨ ALL HARDWARE VERIFICATION & PRE-SILICON EMULATION TESTS PASSED!"
echo "======================================================================"
