#!/usr/bin/env bash
# ==============================================================================
# Automated Setup Script for macOS, Linux, and Windows WSL2
# ==============================================================================

set -e

# ANSI Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

echo -e "\n${CYAN}======================================================================${NC}"
echo -e "${CYAN}🛠️  SETTING UP AI HARDWARE & PRE-SILICON EMULATION PLATFORM${NC}"
echo -e "${CYAN}======================================================================${NC}\n"

# 1. Detect Operating System
OS="$(uname -s)"
case "$OS" in
    Darwin*)
        PLATFORM="macOS"
        ;;
    Linux*)
        if grep -qi microsoft /proc/version 2>/dev/null; then
            PLATFORM="WSL2 (Linux on Windows)"
        else
            PLATFORM="Linux"
        fi
        ;;
    *)
        PLATFORM="Unix-like ($OS)"
        ;;
esac

echo -e "  • Detected Platform: ${GREEN}$PLATFORM${NC}"
echo -e "  • Architecture:      ${GREEN}$(uname -m)${NC}"

# 2. Check System EDA Toolchains
echo -e "\n${CYAN}[1/4] Checking Hardware Toolchains (iverilog, verilator, C++)...${NC}"
MISSING_TOOLS=()

if ! command -v iverilog &>/dev/null; then
    MISSING_TOOLS+=("iverilog (Icarus Verilog)")
fi

if ! command -v verilator &>/dev/null; then
    MISSING_TOOLS+=("verilator (C++ Cycle Emulator)")
fi

if ! command -v clang++ &>/dev/null && ! command -v g++ &>/dev/null; then
    MISSING_TOOLS+=("clang++ or g++ (C++17 Compiler)")
fi

if [ ${#MISSING_TOOLS[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Some recommended hardware tools are not installed:${NC}"
    for tool in "${MISSING_TOOLS[@]}"; do
        echo -e "    - $tool"
    done

    if [ "$PLATFORM" = "macOS" ]; then
        if command -v brew &>/dev/null; then
            echo -e "\n${YELLOW}Would you like to install missing tools via Homebrew? (y/N)${NC} "
            read -r response
            if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
                echo -e "${CYAN}Running: brew install icarus-verilog verilator yosys graphviz gtkwave${NC}"
                brew install icarus-verilog verilator yosys graphviz gtkwave || true
            else
                echo -e "You can install them later with: ${CYAN}brew install icarus-verilog verilator yosys graphviz gtkwave${NC}"
            fi
        else
            echo -e "${RED}Homebrew not detected. Please install Homebrew from https://brew.sh${NC}"
            echo -e "Then run: ${CYAN}brew install icarus-verilog verilator yosys graphviz gtkwave${NC}"
        fi
    elif [[ "$PLATFORM" == *"Linux"* ]] || [[ "$PLATFORM" == *"WSL2"* ]]; then
        echo -e "\nTo install on Ubuntu/Debian/WSL, run:"
        echo -e "  ${CYAN}sudo apt update && sudo apt install -y build-essential clang iverilog verilator yosys graphviz gtkwave python3-venv python3-pip${NC}"
    fi
else
    echo -e "  ${GREEN}✅ Core hardware simulation tools detected.${NC}"
fi

# 3. Check Python 3
echo -e "\n${CYAN}[2/4] Checking Python 3 Installation...${NC}"
PYTHON_CMD=""
for cmd in python3.12 python3.11 python3.10 python3.9 python3 python; do
    if command -v "$cmd" &>/dev/null; then
        VER=$("$cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || true)
        MAJOR=$(echo "$VER" | cut -d. -f1)
        MINOR=$(echo "$VER" | cut -d. -f2)
        if [ "$MAJOR" -eq 3 ] && [ "$MINOR" -ge 9 ]; then
            PYTHON_CMD="$cmd"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo -e "${RED}❌ Python >= 3.9 is required but could not be found!${NC}"
    exit 1
fi
echo -e "  ${GREEN}✅ Using Python: $("$PYTHON_CMD" --version) ($PYTHON_CMD)${NC}"

# 4. Set up Virtual Environment
echo -e "\n${CYAN}[3/4] Setting up Python Virtual Environment (.venv)...${NC}"
if [ ! -d ".venv" ]; then
    echo -e "  Creating virtual environment in .venv..."
    "$PYTHON_CMD" -m venv .venv
else
    echo -e "  Virtual environment already exists in .venv."
fi

# Activate venv
source .venv/bin/activate
echo -e "  Upgrading pip and installing requirements..."
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet
echo -e "  ${GREEN}✅ Python dependencies installed successfully.${NC}"

# 5. Run Environment Diagnostics
echo -e "\n${CYAN}[4/4] Verifying System Setup...${NC}"
python "$SCRIPT_DIR/check_env.py"

echo -e "\n${GREEN}======================================================================${NC}"
echo -e "${GREEN}🎉 SETUP COMPLETED SUCCESSFULLY!${NC}"
echo -e "${GREEN}======================================================================${NC}"
echo -e "\nNext Steps:"
echo -e "  1. Activate virtual environment:  ${CYAN}source .venv/bin/activate${NC}"
echo -e "  2. Run all tests and emulator:     ${CYAN}./build_and_run.sh${NC} (or ${CYAN}python run_all.py${NC})"
echo -e "  3. Launch live 2D visualizer:      ${CYAN}python visualizer/serve.py${NC}"
echo -e "  4. Explore interactive schematics: ${CYAN}open schematics/index.html${NC}"
echo -e "  5. Verilog to gate schematic:      ${CYAN}python synthesis/playground_server.py${NC}\n"
