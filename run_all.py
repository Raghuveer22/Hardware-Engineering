#!/usr/bin/env python3
"""
==============================================================================
File: run_all.py
Description: Master Cross-Platform Test & Emulation Runner
Works on: macOS (Apple Silicon & Intel), Windows (Native & WSL2), and Linux.

Mental Model:
Runs both stages of Pre-Silicon Verification:
  1. Python Cocotb Golden Verification (NumPy bit-accurate checks)
  2. C++ Cycle-Accurate Verilator Emulation (Hardware Driver Simulation)
==============================================================================
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

PROJ_DIR = Path(__file__).resolve().parent

# ANSI Colors
GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

# Ensure venv Python is used if available
def get_python_exe():
    venv_win = PROJ_DIR / ".venv" / "Scripts" / "python.exe"
    venv_unix = PROJ_DIR / ".venv" / "bin" / "python"
    if venv_win.exists():
        return str(venv_win)
    if venv_unix.exists():
        return str(venv_unix)
    return sys.executable

def main():
    parser = argparse.ArgumentParser(description="AI Hardware Platform Master Verification Runner")
    parser.add_argument("--sim", choices=["icarus", "verilator"], default="icarus",
                        help="HDL Simulator for Cocotb (default: icarus)")
    parser.add_argument("--dut", default="all", help="Specific DUT to test (default: all)")
    parser.add_argument("--skip-tests", action="store_true", help="Skip Cocotb Python tests")
    parser.add_argument("--skip-emulator", action="store_true", help="Skip C++ cycle emulator")
    parser.add_argument("--run-labs", action="store_true", help="Also run the full curriculum Labs 00-08")
    args = parser.parse_args()

    py_exe = get_python_exe()

    print(f"\n{BOLD}{CYAN}{'=' * 70}{RESET}")
    print(f"{BOLD}{CYAN}🚀 MASTER PRE-SILICON VERIFICATION & EMULATION SUITE{RESET}")
    print(f"{BOLD}{CYAN}{'=' * 70}{RESET}")
    print(f"  • Python Interpreter: {py_exe}")
    print(f"  • Cocotb Simulator:   {args.sim}")
    print(f"  • Working Directory:  {PROJ_DIR}\n")

    # 1. Run Python Cocotb Verification
    if not args.skip_tests:
        print(f"{BOLD}{CYAN}----------------------------------------------------------------------{RESET}")
        print(f"{BOLD}🎯 STAGE 1: PYTHON COCOTB TESTBENCHES (PE & Systolic Array){RESET}")
        print(f"{BOLD}{CYAN}----------------------------------------------------------------------{RESET}")
        
        sim_script = PROJ_DIR / "sim" / "run.py"
        cmd = [py_exe, str(sim_script), "--dut", args.dut, "--sim", args.sim]
        res = subprocess.run(cmd, cwd=str(PROJ_DIR))
        if res.returncode != 0:
            print(f"\n{BOLD}{RED}❌ STAGE 1 FAILED: Cocotb simulation errors detected.{RESET}")
            sys.exit(res.returncode)
        print(f"\n{BOLD}{GREEN}✅ STAGE 1 PASSED: All Cocotb hardware testbenches verified!{RESET}\n")

    # Optional: Run Labs 00 - 08
    if args.run_labs:
        print(f"{BOLD}{CYAN}----------------------------------------------------------------------{RESET}")
        print(f"{BOLD}🎯 STAGE 1B: CURRICULUM LAB SUITE (Labs 00 - 08){RESET}")
        print(f"{BOLD}{CYAN}----------------------------------------------------------------------{RESET}")
        labs_script = PROJ_DIR / "labs" / "run_lab.py"
        cmd = [py_exe, str(labs_script), "--lab", "all", "--sim", args.sim]
        res = subprocess.run(cmd, cwd=str(PROJ_DIR))
        if res.returncode != 0:
            print(f"\n{BOLD}{RED}❌ LAB SUITE FAILED: Cocotb lab errors detected.{RESET}")
            sys.exit(res.returncode)
        print(f"\n{BOLD}{GREEN}✅ LAB SUITE PASSED: All 9 curriculum labs verified!{RESET}\n")

    # 2. Build and Run C++ Cycle-Accurate Verilator Emulator
    if not args.skip_emulator:
        print(f"{BOLD}{CYAN}----------------------------------------------------------------------{RESET}")
        print(f"{BOLD}🎯 STAGE 2: PRE-SILICON C++ VERILATOR CYCLE-ACCURATE EMULATOR{RESET}")
        print(f"{BOLD}{CYAN}----------------------------------------------------------------------{RESET}")
        
        build_script = PROJ_DIR / "cpp_emulation" / "build_emulator.py"
        cmd = [py_exe, str(build_script), "--run"]
        res = subprocess.run(cmd, cwd=str(PROJ_DIR))
        if res.returncode != 0:
            print(f"\n{BOLD}{RED}❌ STAGE 2 FAILED: C++ Emulator build or execution failed.{RESET}")
            sys.exit(res.returncode)
        print(f"\n{BOLD}{GREEN}✅ STAGE 2 PASSED: C++ Cycle Emulator verified against Golden Model!{RESET}\n")

    print(f"{BOLD}{CYAN}{'=' * 70}{RESET}")
    print(f"{BOLD}{GREEN}✨ ALL HARDWARE VERIFICATION & PRE-SILICON EMULATION TESTS PASSED!{RESET}")
    print(f"{BOLD}{CYAN}{'=' * 70}{RESET}\n")

if __name__ == "__main__":
    main()
