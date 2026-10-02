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

DUT_CONFIGS = {
    "adder": {
        "sources": ["rtl/adder.sv"],
        "toplevel": "adder",
        "module": "test_adder",
        "test_dir": "labs"
    },
    "multiplier_int8": {
        "sources": ["rtl/multiplier_int8.sv"],
        "toplevel": "multiplier_int8",
        "module": "test_multiplier",
        "test_dir": "labs"
    },
    "mac_unit": {
        "sources": ["rtl/mac_unit.sv"],
        "toplevel": "mac_unit",
        "module": "test_mac",
        "test_dir": "labs"
    },
    "pe": {
        "sources": ["rtl/mac_unit.sv", "rtl/pe.sv"],
        "toplevel": "pe",
        "module": "test_pe",
        "test_dir": "tests"
    },
    "systolic_array": {
        "sources": ["rtl/mac_unit.sv", "rtl/pe.sv", "rtl/systolic_array.sv"],
        "toplevel": "systolic_array",
        "module": "test_systolic_array",
        "test_dir": "tests"
    },
    "sqrt": {
        "sources": ["rtl/sqrt.sv"],
        "toplevel": "sqrt",
        "module": "test_sqrt",
        "test_dir": "labs"
    },
    "softmax": {
        "sources": ["rtl/softmax.sv"],
        "toplevel": "softmax",
        "module": "test_softmax",
        "test_dir": "labs"
    }
}

def run_simulation(dut_name="pe", simulator="icarus", waves=True):
    """
    Compiles RTL and executes the corresponding Python Cocotb test module.
    """
    if dut_name not in DUT_CONFIGS:
        raise ValueError(f"Unknown DUT: {dut_name}. Choose from: {list(DUT_CONFIGS.keys())}")

    proj_dir = Path(__file__).resolve().parent.parent
    config = DUT_CONFIGS[dut_name]
    sources = [proj_dir / s for s in config["sources"]]
    toplevel = config["toplevel"]
    module = config["module"]
    test_dir = proj_dir / config["test_dir"]
    build_dir = proj_dir / "sim" / f"sim_build_{dut_name}_{simulator}"

    print(f"\n🚀 Running Cocotb Simulation:")
    print(f"   - DUT: {dut_name}")
    print(f"   - Simulator: {simulator}")
    print(f"   - Build Dir: {build_dir}\n")

    runner = get_runner(simulator)
    compile_args = ["-g2012"] if simulator == "icarus" else ["-Wno-WIDTHEXPAND", "-Wno-WIDTHTRUNC"]

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
        test_dir=test_dir,
        build_dir=build_dir,
        waves=waves
    )

# Entry point for CLI invocation
if __name__ == "__main__":
    choices = list(DUT_CONFIGS.keys()) + ["all"]
    parser = argparse.ArgumentParser(description="Run Cocotb Hardware Tests")
    parser.add_argument("--dut", choices=choices, default="all",
                        help="Which DUT to simulate (default: all)")
    parser.add_argument("--sim", choices=["icarus", "verilator"], default="icarus",
                        help="Simulator to use: 'icarus' or 'verilator' (default: icarus)")
    parser.add_argument("--no-waves", action="store_true", help="Disable waveform dumping")
    args = parser.parse_args()

    if args.dut == "all":
        for dut in DUT_CONFIGS:
            run_simulation(dut, args.sim, waves=not args.no_waves)
    else:
        run_simulation(args.dut, args.sim, waves=not args.no_waves)
