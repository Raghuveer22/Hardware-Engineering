#!/usr/bin/env python3
"""
==============================================================================
File: labs/run_lab.py
Description: Master test runner for all lab testbenches using Cocotb.
==============================================================================
"""

import sys
import os
from pathlib import Path
import argparse
from cocotb_tools.runner import get_runner

def run_lab_test(lab_id, simulator="icarus"):
    proj_dir = Path(__file__).resolve().parent.parent
    rtl_dir = proj_dir / "rtl"
    tests_dir = proj_dir / "tests"
    labs_dir = proj_dir / "labs"
    build_dir = proj_dir / "sim" / f"sim_build_{lab_id}_{simulator}"

    print(f"\n========================================================")
    print(f"🚀 RUNNING LAB TEST: {lab_id.upper()}")
    print(f"   Simulator: {simulator}")
    print(f"========================================================\n")

    if lab_id in ["lab01", "lab01_multiplier", "multiplier"]:
        sources = [rtl_dir / "multiplier_int8.sv"]
        toplevel = "multiplier_int8"
        module = "test_multiplier"
        test_dir = labs_dir
    elif lab_id in ["lab02", "lab02_mac", "mac_unit"]:
        sources = [rtl_dir / "mac_unit.sv"]
        toplevel = "mac_unit"
        module = "test_mac"
        test_dir = labs_dir
    elif lab_id in ["lab03", "lab03_pe", "pe"]:
        sources = [rtl_dir / "mac_unit.sv", rtl_dir / "pe.sv"]
        toplevel = "pe"
        module = "test_pe"
        test_dir = tests_dir
    elif lab_id in ["lab04", "lab04_systolic", "systolic_array"]:
        sources = [rtl_dir / "mac_unit.sv", rtl_dir / "pe.sv", rtl_dir / "systolic_array.sv"]
        toplevel = "systolic_array"
        module = "test_systolic_array"
        test_dir = tests_dir
    else:
        raise ValueError(f"Unknown lab: {lab_id}")

    runner = get_runner(simulator)
    compile_args = ["-g2012"] if simulator == "icarus" else ["-Wno-WIDTHEXPAND", "-Wno-WIDTHTRUNC"]

    runner.build(
        sources=sources,
        hdl_toplevel=toplevel,
        build_dir=build_dir,
        build_args=compile_args,
        always=True
    )

    runner.test(
        hdl_toplevel=toplevel,
        test_module=module,
        test_dir=test_dir,
        build_dir=build_dir
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Lab Tests")
    parser.add_argument("--lab", default="all",
                        choices=["lab01", "lab02", "lab03", "lab04", "all"],
                        help="Which lab to test (default: all)")
    parser.add_argument("--sim", default="icarus", choices=["icarus", "verilator"])
    args = parser.parse_args()

    if args.lab == "all":
        for lab in ["lab01", "lab02", "lab03", "lab04"]:
            run_lab_test(lab, args.sim)
    else:
        run_lab_test(args.lab, args.sim)
