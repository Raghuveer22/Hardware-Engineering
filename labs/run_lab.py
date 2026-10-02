#!/usr/bin/env python3
"""
==============================================================================
File: labs/run_lab.py
Description: Master test runner for all lab testbenches using Cocotb.
Supports: Lab 00 (Adder), Lab 01 (Multiplier), Lab 02 (MAC),
          Lab 03 (PE), Lab 04 (Systolic Array), Lab 05 (Sqrt),
          Lab 06 (Softmax), Lab 07 (rsqrt), Lab 08 (exp2_sfu).
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

    if lab_id in ["lab00", "lab00_adder", "adder"]:
        sources = [rtl_dir / "adder.sv"]
        toplevel = "adder"
        module = "test_adder"
        test_dir = labs_dir
    elif lab_id in ["lab01", "lab01_multiplier", "multiplier"]:
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
    elif lab_id in ["lab05", "lab05_sqrt", "sqrt"]:
        sources = [rtl_dir / "sqrt.sv"]
        toplevel = "sqrt"
        module = "test_sqrt"
        test_dir = labs_dir
    elif lab_id in ["lab06", "lab06_softmax", "softmax"]:
        sources = [rtl_dir / "softmax.sv"]
        toplevel = "softmax"
        module = "test_softmax"
        test_dir = labs_dir
    elif lab_id in ["lab07", "lab07_rsqrt", "rsqrt"]:
        sources = [rtl_dir / "rsqrt.sv"]
        toplevel = "rsqrt"
        module = "test_rsqrt"
        test_dir = labs_dir
    elif lab_id in ["lab08", "lab08_exp2_sfu", "lab08_exponential_sfu", "exp2_sfu"]:
        sources = [rtl_dir / "exp2_sfu.sv"]
        toplevel = "exp2_sfu"
        module = "test_exp2_sfu"
        test_dir = labs_dir
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
    LAB_CHOICES = ["lab00", "lab01", "lab02", "lab03", "lab04", "lab05", "lab06", "lab07", "lab08", "all"]
    parser = argparse.ArgumentParser(description="Run Lab Tests")
    parser.add_argument("--lab", default="all",
                        choices=LAB_CHOICES,
                        help="Which lab to test (default: all)")
    parser.add_argument("--sim", default="icarus", choices=["icarus", "verilator"])
    args = parser.parse_args()

    if args.lab == "all":
        for lab in ["lab00", "lab01", "lab02", "lab03", "lab04", "lab05", "lab06", "lab07", "lab08"]:
            run_lab_test(lab, args.sim)
    else:
        run_lab_test(args.lab, args.sim)

