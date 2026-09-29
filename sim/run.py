#!/usr/bin/env python3
"""
==============================================================================
File: sim/run.py
Description: Python Test Runner for Cocotb Hardware Verification
Features:
- Handles path resolution (including paths with spaces)
- Supports multiple simulators ('icarus' and 'verilator')
- Compiles SystemVerilog RTL and runs Python testbenches
==============================================================================
"""

import sys
import os
from pathlib import Path
import argparse
# Import Cocotb's built-in simulation runner utility
from cocotb_tools.runner import get_runner

def run_simulation(dut_name="pe", simulator="icarus", waves=True):
    """
    Compiles RTL and executes the corresponding Python Cocotb test module.
    
    Args:
        dut_name (str): 'pe' or 'systolic_array'
        simulator (str): 'icarus' or 'verilator'
        waves (bool): If True, dumps .fst / .vcd waveform files
    """
    # Resolve directory paths relative to this script
    proj_dir = Path(__file__).resolve().parent.parent
    rtl_dir = proj_dir / "rtl"
    tests_dir = proj_dir / "tests"
    # Build directory where simulator compiles intermediate binaries
    build_dir = proj_dir / "sim" / f"sim_build_{dut_name}_{simulator}"

    print(f"\n🚀 Running Cocotb Simulation:")
    print(f"   - DUT: {dut_name}")
    print(f"   - Simulator: {simulator}")
    print(f"   - RTL Path: {rtl_dir}")
    print(f"   - Build Dir: {build_dir}\n")

    # Select RTL source files, top-level module name, and testbench module based on DUT
    if dut_name == "pe":
        sources = [
            rtl_dir / "mac_unit.sv",
            rtl_dir / "pe.sv"
        ]
        toplevel = "pe"          # Hardware top-level module name in SystemVerilog
        module = "test_pe"       # Python test file in tests/ directory (test_pe.py)
    elif dut_name == "systolic_array":
        sources = [
            rtl_dir / "mac_unit.sv",
            rtl_dir / "pe.sv",
            rtl_dir / "systolic_array.sv"
        ]
        toplevel = "systolic_array" # Hardware top-level module name
        module = "test_systolic_array" # Python test file (test_systolic_array.py)
    else:
        raise ValueError(f"Unknown DUT: {dut_name}. Choose 'pe' or 'systolic_array'.")

    # Obtain simulator runner instance (e.g. Icarus or Verilator)
    runner = get_runner(simulator)
    
    # Configure compiler flags
    compile_args = []
    if simulator == "icarus":
        compile_args.extend(["-g2012"]) # Enable SystemVerilog 2012 support in Icarus
    elif simulator == "verilator":
        compile_args.extend(["-Wno-WIDTHEXPAND", "-Wno-WIDTHTRUNC"])

    # 1. Compile hardware RTL sources into simulation binary
    runner.build(
        sources=sources,
        hdl_toplevel=toplevel,
        build_dir=build_dir,
        build_args=compile_args,
        waves=waves,
        always=True
    )

    # 2. Execute Python testbench against the compiled hardware binary
    runner.test(
        hdl_toplevel=toplevel,
        test_module=module,
        test_dir=tests_dir,
        build_dir=build_dir,
        waves=waves
    )

# Entry point for CLI invocation
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Cocotb Hardware Tests")
    parser.add_argument("--dut", choices=["pe", "systolic_array", "all"], default="all",
                        help="Which DUT to simulate: 'pe', 'systolic_array', or 'all' (default: all)")
    parser.add_argument("--sim", choices=["icarus", "verilator"], default="icarus",
                        help="Simulator to use: 'icarus' or 'verilator' (default: icarus)")
    args = parser.parse_args()

    # If 'all' is selected, run PE unit test first, followed by Systolic Array test
    if args.dut == "all":
        run_simulation("pe", args.sim)
        run_simulation("systolic_array", args.sim)
    else:
        run_simulation(args.dut, args.sim)
