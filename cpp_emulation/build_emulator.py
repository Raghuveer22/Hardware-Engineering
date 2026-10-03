#!/usr/bin/env python3
"""
==============================================================================
File: cpp_emulation/build_emulator.py
Description: Cross-Platform Build Script for C++ Cycle-Accurate Verilator Emulator
Works on: macOS (Apple Silicon & Intel), Windows (Native & WSL2), and Linux.

Mental Model:
1. Runs Verilator to convert SystemVerilog RTL -> C++ model classes.
2. Dynamically locates VERILATOR_ROOT and C++ compiler.
3. Compiles the testbench and Verilated model into an executable.
4. Optionally runs the cycle-accurate emulator to verify 4x4 GEMM output.
==============================================================================
"""

import os
import sys
import shutil
import platform
import subprocess
import argparse
from pathlib import Path

PROJ_DIR = Path(__file__).resolve().parent.parent
CPP_DIR = PROJ_DIR / "cpp_emulation"
VERILATED_DIR = CPP_DIR / "verilated"
RTL_DIR = PROJ_DIR / "rtl"

def find_verilator_root():
    """Dynamically determine VERILATOR_ROOT across macOS, Linux, and Windows."""
    # 1. Check environment variable
    if "VERILATOR_ROOT" in os.environ and Path(os.environ["VERILATOR_ROOT"]).exists():
        return Path(os.environ["VERILATOR_ROOT"])

    # 2. Query verilator binary
    verilator_bin = shutil.which("verilator")
    if verilator_bin:
        try:
            res = subprocess.run(["verilator", "-getenv", "VERILATOR_ROOT"], capture_output=True, text=True, timeout=5)
            val = res.stdout.strip()
            if val and Path(val).exists():
                return Path(val)
        except Exception:
            pass

    # 3. Common fallback directories
    search_paths = [
        Path("/opt/homebrew/share/verilator"),
        Path("/usr/local/share/verilator"),
        Path("/usr/share/verilator"),
        Path(r"C:\msys64\mingw64\share\verilator"),
        Path(r"C:\msys64\ucrt64\share\verilator"),
    ]
    # Check Homebrew Cellar wildcard if on Mac
    cellar = Path("/opt/homebrew/Cellar/verilator")
    if cellar.exists():
        versions = list(cellar.glob("*/share/verilator"))
        if versions:
            search_paths.insert(0, versions[0])

    for p in search_paths:
        if (p / "include" / "verilated.h").exists():
            return p

    return None

def find_cpp_compiler():
    """Detect available C++17 compiler (clang++, g++, etc.)."""
    env_cxx = os.environ.get("CXX")
    if env_cxx and shutil.which(env_cxx):
        return env_cxx

    candidates = ["clang++", "g++"]
    for c in candidates:
        if shutil.which(c):
            return c
    return None

def build_emulator():
    print(f"\n==================================================================")
    print(f"🔨 BUILDING PRE-SILICON C++ HARDWARE EMULATOR")
    print(f"   Platform: {platform.system()} ({platform.machine()})")
    print(f"==================================================================\n")

    # Check Verilator
    verilator_bin = shutil.which("verilator")
    if not verilator_bin:
        print("❌ Error: 'verilator' executable not found in PATH!")
        print("   macOS:   brew install verilator")
        print("   WSL/Deb: sudo apt-get install verilator")
        print("   Windows: Install via MSYS2 or use WSL2 (recommended)")
        return False

    vroot = find_verilator_root()
    if not vroot or not (vroot / "include" / "verilated.h").exists():
        print(f"❌ Error: Could not locate Verilator include headers in VERILATOR_ROOT ({vroot})")
        return False

    cxx = find_cpp_compiler()
    if not cxx:
        print("❌ Error: No C++ compiler (clang++ or g++) found in PATH!")
        return False

    print(f"  • Verilator:      {verilator_bin}")
    print(f"  • Verilator Root: {vroot}")
    print(f"  • C++ Compiler:   {cxx}")

    # 1. Run Verilator translation
    print("\n[Step 1/2] Verilating SystemVerilog RTL into C++ classes...")
    VERILATED_DIR.mkdir(parents=True, exist_ok=True)

    rtl_sources = [
        str(RTL_DIR / "mac_unit.sv"),
        str(RTL_DIR / "pe.sv"),
        str(RTL_DIR / "systolic_array.sv")
    ]

    verilator_cmd = [
        verilator_bin,
        "--top-module", "systolic_array",
        "--cc",
        "--trace",
        "-I" + str(RTL_DIR),
        *rtl_sources,
        "-Mdir", str(VERILATED_DIR)
    ]

    res = subprocess.run(verilator_cmd, cwd=str(PROJ_DIR))
    if res.returncode != 0:
        print("❌ Verilator translation failed!")
        return False

    # 2. Compile C++ harness + Verilated sources
    print("\n[Step 2/2] Compiling C++ harness and linking emulator binary...")
    include_dir = vroot / "include"
    vltstd_dir = include_dir / "vltstd"

    # Gather runtime .cpp files
    runtime_cpp = [include_dir / "verilated.cpp", include_dir / "verilated_vcd_c.cpp"]
    threads_cpp = include_dir / "verilated_threads.cpp"
    if threads_cpp.exists():
        runtime_cpp.append(threads_cpp)

    # Gather generated verilated .cpp files
    verilated_cpp = list(VERILATED_DIR.glob("Vsystolic_array*.cpp"))

    exe_name = "emulator.exe" if platform.system() == "Windows" else "emulator"
    output_bin = CPP_DIR / exe_name

    compile_cmd = [
        cxx,
        "-std=c++17",
        "-O2",
        f"-I{include_dir}",
        f"-I{vltstd_dir}",
        f"-I{VERILATED_DIR}",
        *[str(p) for p in runtime_cpp],
        *[str(p) for p in verilated_cpp],
        str(CPP_DIR / "main.cpp"),
        "-o", str(output_bin)
    ]

    # Add pthread if on unix/linux
    if platform.system() != "Windows":
        compile_cmd.append("-lpthread")

    res = subprocess.run(compile_cmd, cwd=str(PROJ_DIR))
    if res.returncode != 0:
        print("❌ C++ compilation failed!")
        return False

    print(f"\n✅ Emulator built successfully: {output_bin}\n")
    return output_bin

def main():
    parser = argparse.ArgumentParser(description="Cross-Platform C++ Emulator Builder")
    parser.add_argument("--run", action="store_true", help="Execute the emulator after building")
    args = parser.parse_args()

    bin_path = build_emulator()
    if not bin_path:
        sys.exit(1)

    if args.run:
        print(f"🚀 Executing {bin_path.name}...\n")
        res = subprocess.run([str(bin_path)], cwd=str(PROJ_DIR))
        sys.exit(res.returncode)

if __name__ == "__main__":
    main()
