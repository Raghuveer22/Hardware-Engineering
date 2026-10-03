#!/usr/bin/env python3
"""
==============================================================================
File: setup/check_env.py
Description: Cross-Platform Environment Doctor & Dependency Checker
Works on: macOS (Apple Silicon & Intel), Windows (Native & WSL2), and Linux.

Validates:
1. Python version & active virtual environment
2. Core Python libraries (cocotb, numpy, pytest, etc.)
3. SystemVerilog Simulators (Icarus Verilog, Verilator)
4. C++ Compiler with C++17 support (clang++, g++)
5. Verilator Runtime & VERILATOR_ROOT path detection
6. Logic Synthesis & Schematic Tools (Yosys, Graphviz dot)
7. Waveform Viewers (GTKWave, Surfer)
==============================================================================
"""

import os
import sys
import shutil
import platform
import subprocess
from pathlib import Path

# ANSI Color Codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

# Disable ANSI colors on legacy Windows consoles if unsupported
if platform.system() == "Windows" and os.environ.get("TERM") is None and not os.environ.get("WT_SESSION"):
    GREEN = RED = YELLOW = CYAN = BOLD = RESET = ""

def print_header(title):
    print(f"\n{BOLD}{CYAN}{'=' * 70}{RESET}")
    print(f"{BOLD}{CYAN}🔍 {title}{RESET}")
    print(f"{BOLD}{CYAN}{'=' * 70}{RESET}")

def print_status(item, ok, message, is_warning=False):
    if ok:
        mark = f"{GREEN}✅ PASS{RESET}"
    elif is_warning:
        mark = f"{YELLOW}⚠️  WARN{RESET}"
    else:
        mark = f"{RED}❌ FAIL{RESET}"
    print(f"  [{mark}] {BOLD}{item:<26}{RESET} {message}")

def get_tool_version(cmd, flag="--version"):
    try:
        res = subprocess.run([cmd, flag], capture_output=True, text=True, timeout=5)
        out = (res.stdout or res.stderr).splitlines()
        return out[0].strip() if out else "installed"
    except Exception:
        return "installed"

def check_cpp17(compiler):
    """Test if the C++ compiler supports -std=c++17."""
    try:
        res = subprocess.run(
            [compiler, "-std=c++17", "-x", "c++", "-", "-o", os.devnull],
            input="int main(){ return 0; }",
            capture_output=True,
            text=True,
            timeout=5
        )
        return res.returncode == 0
    except Exception:
        return False

def get_verilator_root():
    """Detect Verilator root directory using CLI, pkg-config, or standard locations."""
    if shutil.which("verilator"):
        try:
            res = subprocess.run(["verilator", "-getenv", "VERILATOR_ROOT"], capture_output=True, text=True, timeout=5)
            path = res.stdout.strip()
            if path and Path(path).exists():
                return path
        except Exception:
            pass

    # Standard fallback candidates
    candidates = [
        "/opt/homebrew/share/verilator",             # macOS ARM Homebrew
        "/usr/local/share/verilator",                 # macOS Intel / Linux /usr/local
        "/usr/share/verilator",                       # Linux apt package
        r"C:\msys64\mingw64\share\verilator",         # Windows MSYS2 MinGW64
        r"C:\msys64\ucrt64\share\verilator",          # Windows MSYS2 UCRT64
    ]
    for c in candidates:
        if Path(c).exists():
            return c
    return None

def main():
    os_name = platform.system()
    machine = platform.machine()
    is_wsl = "microsoft" in platform.uname().release.lower()
    
    print_header(f"AI HARDWARE PLATFORM DIAGNOSTICS ({os_name} {machine}{' [WSL2]' if is_wsl else ''})")
    print(f"  Operating System: {platform.platform()}")
    print(f"  Python Binary:    {sys.executable}")
    print(f"  Working Directory:{Path.cwd()}\n")

    issues_found = []
    warnings_found = []

    # --------------------------------------------------------------------------
    # 1. PYTHON & VIRTUAL ENVIRONMENT
    # --------------------------------------------------------------------------
    py_ver = sys.version_info
    py_ok = (py_ver.major == 3 and py_ver.minor >= 9)
    py_msg = f"{py_ver.major}.{py_ver.minor}.{py_ver.micro}"
    if not py_ok:
        py_msg += " (Requires Python >= 3.9)"
        issues_found.append("Python >= 3.9 required")
    print_status("Python Version", py_ok, py_msg)

    in_venv = (sys.prefix != getattr(sys, "base_prefix", sys.prefix))
    if in_venv:
        print_status("Virtual Environment", True, f"Active ({Path(sys.prefix).name})")
    else:
        print_status("Virtual Environment", False, "Not inside a virtual environment (.venv)", is_warning=True)
        warnings_found.append("Not inside a virtual environment. Run setup script or activate .venv.")

    # --------------------------------------------------------------------------
    # 2. PYTHON PACKAGES
    # --------------------------------------------------------------------------
    core_pkgs = {
        "cocotb": "Cocotb (RTL Verification Framework)",
        "numpy": "NumPy (Golden Matrix Tensor Math)",
        "pytest": "PyTest (Unit Testing Suite)",
        "tabulate": "Tabulate (Console Tables)",
        "rich": "Rich (Terminal Formatting)"
    }
    for pkg, desc in core_pkgs.items():
        try:
            mod = __import__(pkg)
            v = getattr(mod, "__version__", "installed")
            print_status(f"Python: {pkg}", True, f"v{v} ({desc})")
        except ImportError:
            print_status(f"Python: {pkg}", False, f"Missing! Run: pip install {pkg}")
            issues_found.append(f"Missing Python package: {pkg}")

    # Optional animation packages
    for opt_pkg in ["manim", "python-pptx"]:
        try:
            pkg_name = opt_pkg.replace("-", "_")
            __import__(pkg_name)
            print_status(f"Optional: {opt_pkg}", True, "Installed")
        except ImportError:
            print_status(f"Optional: {opt_pkg}", False, "Not installed (only needed for video rendering / slides)", is_warning=True)

    # --------------------------------------------------------------------------
    # 3. HARDWARE SIMULATORS & VERIFICATION TOOLS
    # --------------------------------------------------------------------------
    print_header("HARDWARE SIMULATOR TOOLCHAIN")

    # Icarus Verilog
    iverilog_bin = shutil.which("iverilog")
    if iverilog_bin:
        ver = get_tool_version("iverilog", "-v")
        print_status("Icarus Verilog (iverilog)", True, f"{iverilog_bin} [{ver}]")
    else:
        print_status("Icarus Verilog (iverilog)", False, "Not found in PATH!")
        issues_found.append("iverilog is required for Cocotb simulation")

    # Verilator
    verilator_bin = shutil.which("verilator")
    if verilator_bin:
        ver = get_tool_version("verilator", "--version")
        print_status("Verilator (Cycle Emulator)", True, f"{verilator_bin} [{ver}]")
        vroot = get_verilator_root()
        if vroot:
            include_dir = Path(vroot) / "include"
            if (include_dir / "verilated.h").exists():
                print_status("Verilator Include Root", True, str(vroot))
            else:
                print_status("Verilator Include Root", False, f"verilated.h missing in {include_dir}", is_warning=True)
                warnings_found.append("VERILATOR_ROOT headers not found.")
        else:
            print_status("Verilator Include Root", False, "Could not locate VERILATOR_ROOT include dir", is_warning=True)
            warnings_found.append("Verilator include directory could not be auto-detected.")
    else:
        print_status("Verilator (Cycle Emulator)", False, "Not found in PATH (needed for C++ emulator & fast simulation)", is_warning=True)
        warnings_found.append("verilator is missing (used for C++ emulator).")

    # --------------------------------------------------------------------------
    # 4. C++ COMPILER (FOR PRE-SILICON C++ EMULATOR)
    # --------------------------------------------------------------------------
    print_header("C++ COMPILER TOOLCHAIN")
    compilers = ["clang++", "g++"]
    found_compiler = None
    for comp in compilers:
        comp_path = shutil.which(comp)
        if comp_path:
            supports_cpp17 = check_cpp17(comp)
            status_text = f"{comp_path} (C++17: {'Supported' if supports_cpp17 else 'Unsupported'})"
            if supports_cpp17:
                found_compiler = comp
                print_status(f"C++ Compiler ({comp})", True, status_text)
                break
            else:
                print_status(f"C++ Compiler ({comp})", False, status_text, is_warning=True)

    if not found_compiler:
        print_status("C++ Compiler", False, "No C++17-capable compiler (clang++ or g++) found in PATH!")
        issues_found.append("C++17 compiler (clang++ or g++) required to build cycle-accurate emulator")

    # --------------------------------------------------------------------------
    # 5. SYNTHESIS, SCHEMATICS & WAVEFORMS
    # --------------------------------------------------------------------------
    print_header("LOGIC SYNTHESIS & WAVEFORM TOOLS")

    yosys_bin = shutil.which("yosys")
    if yosys_bin:
        ver = get_tool_version("yosys", "-V")
        print_status("Yosys Logic Synthesizer", True, f"{yosys_bin} [{ver}]")
    else:
        print_status("Yosys Logic Synthesizer", False, "Not found in PATH (needed for gate-level synthesis)", is_warning=True)
        warnings_found.append("yosys is missing (only needed for synthesis/synthesize.py).")

    dot_bin = shutil.which("dot")
    if dot_bin:
        print_status("Graphviz (dot)", True, f"{dot_bin}")
    else:
        print_status("Graphviz (dot)", False, "Not found in PATH (needed for PNG schematic rendering)", is_warning=True)
        warnings_found.append("graphviz (dot) is missing (needed for schematic PNGs).")

    gtkwave_bin = shutil.which("gtkwave") or shutil.which("surfer")
    if gtkwave_bin:
        print_status("Waveform Viewer", True, f"{gtkwave_bin}")
    else:
        print_status("Waveform Viewer", False, "Neither gtkwave nor surfer found (recommended for viewing .vcd/.fst files)", is_warning=True)

    # --------------------------------------------------------------------------
    # DIAGNOSTIC SUMMARY & ACTIONABLE FIXES
    # --------------------------------------------------------------------------
    print_header("DIAGNOSTIC SUMMARY")

    if not issues_found and not warnings_found:
        print(f"\n{BOLD}{GREEN}✨ CONGRATULATIONS! Your system is 100% ready for AI Hardware Engineering!{RESET}")
        print(f"👉 To run all tests and C++ emulator:  {CYAN}./build_and_run.sh{RESET} (or {CYAN}python run_all.py{RESET})")
        return 0

    if not issues_found:
        print(f"\n{BOLD}{GREEN}✅ All core requirements are satisfied!{RESET}")
        if warnings_found:
            print(f"{YELLOW}A few optional components were flagged:{RESET}")
            for w in warnings_found:
                print(f"  • {w}")
        return 0

    print(f"\n{BOLD}{RED}⚠️  Issues detected that require attention:{RESET}")
    for issue in issues_found:
        print(f"  • {issue}")

    print(f"\n{BOLD}{CYAN}🛠️  ACTIONABLE FIXES FOR YOUR OPERATING SYSTEM:{RESET}")

    if os_name == "Darwin":
        print(f"\n{BOLD}macOS (Homebrew):{RESET}")
        print(f"  Run the following commands in your terminal:")
        print(f"  {CYAN}brew update{RESET}")
        print(f"  {CYAN}brew install icarus-verilog verilator yosys graphviz gtkwave{RESET}")
        print(f"  {CYAN}./setup/setup.sh{RESET}")

    elif os_name == "Windows":
        if is_wsl:
            print(f"\n{BOLD}Windows Subsystem for Linux (WSL2 Ubuntu/Debian):{RESET}")
            print(f"  Run inside WSL terminal:")
            print(f"  {CYAN}sudo apt update && sudo apt install -y build-essential clang iverilog verilator yosys graphviz gtkwave python3-venv python3-pip{RESET}")
            print(f"  {CYAN}./setup/setup.sh{RESET}")
        else:
            print(f"\n{BOLD}Windows (Native):{RESET}")
            print(f"  Option A (Recommended for EDA: WSL2):")
            print(f"    Open PowerShell as Administrator and run: {CYAN}wsl --install{RESET}")
            print(f"    Then clone and run this repo inside Ubuntu on WSL2.")
            print(f"\n  Option B (Native Windows with Winget / Installers):")
            print(f"    1. Icarus Verilog: {CYAN}winget install -e --id Bleyer.IcarusVerilog{RESET}")
            print(f"       (Or download from: https://bleyer.org/icarus/ - ensure 'Add to PATH' is checked)")
            print(f"    2. Graphviz:       {CYAN}winget install Graphviz.Graphviz{RESET}")
            print(f"    3. C++ Compiler:   Install Visual Studio C++ build tools or MinGW (MSYS2)")
            print(f"    4. Run setup:      {CYAN}powershell -ExecutionPolicy Bypass -File .\\setup\\setup.ps1{RESET}")

    else:
        print(f"\n{BOLD}Linux (Debian/Ubuntu):{RESET}")
        print(f"  {CYAN}sudo apt update && sudo apt install -y build-essential clang iverilog verilator yosys graphviz gtkwave python3-venv python3-pip{RESET}")
        print(f"  {CYAN}./setup/setup.sh{RESET}")

    print()
    return 1

if __name__ == "__main__":
    sys.exit(main())
