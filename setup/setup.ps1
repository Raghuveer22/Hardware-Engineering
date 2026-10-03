# ==============================================================================
# Automated Setup Script for Windows PowerShell
# ==============================================================================

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location -Path $RepoRoot

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "🛠️  SETTING UP AI HARDWARE & PRE-SILICON EMULATION PLATFORM (WINDOWS)" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Platform & Toolchain Checks
Write-Host "[1/4] Checking Hardware Toolchains..." -ForegroundColor Cyan

$missingTools = @()

if (-not (Get-Command "iverilog" -ErrorAction SilentlyContinue)) {
    $missingTools += "Icarus Verilog (iverilog)"
}

if (-not (Get-Command "verilator" -ErrorAction SilentlyContinue)) {
    $missingTools += "Verilator (C++ Cycle Emulator)"
}

$hasCpp = (Get-Command "g++" -ErrorAction SilentlyContinue) -or 
          (Get-Command "clang++" -ErrorAction SilentlyContinue) -or 
          (Get-Command "cl.exe" -ErrorAction SilentlyContinue)

if (-not $hasCpp) {
    $missingTools += "C++ Compiler (g++, clang++, or MSVC cl.exe)"
}

if ($missingTools.Count -gt 0) {
    Write-Host "⚠️  Some recommended hardware tools were not found:" -ForegroundColor Yellow
    foreach ($tool in $missingTools) {
        Write-Host "    - $tool" -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "💡 WINDOWS INSTALLATION TIPS:" -ForegroundColor Cyan
    Write-Host "  Option A (Recommended for EDA: WSL2 Ubuntu):"
    Write-Host "    Run in Administrator PowerShell: wsl --install"
    Write-Host "    Then run ./setup/setup.sh inside WSL Ubuntu terminal."
    Write-Host ""
    Write-Host "  Option B (Native Windows with Winget):"
    Write-Host "    iverilog:  winget install -e --id Bleyer.IcarusVerilog"
    Write-Host "    Graphviz:  winget install Graphviz.Graphviz"
    Write-Host "    Compiler:  Install MSYS2 (https://www.msys2.org/) or Visual Studio C++"
    Write-Host ""
} else {
    Write-Host "  ✅ Core hardware toolchains detected." -ForegroundColor Green
}

# 2. Check Python
Write-Host "[2/4] Checking Python Installation..." -ForegroundColor Cyan
$PythonBin = $null

if (Get-Command "python" -ErrorAction SilentlyContinue) {
    $PythonBin = "python"
} elseif (Get-Command "py" -ErrorAction SilentlyContinue) {
    $PythonBin = "py"
}

if (-not $PythonBin) {
    Write-Host "❌ Python 3 was not found! Please install Python from https://www.python.org/ or via:" -ForegroundColor Red
    Write-Host "   winget install Python.Python.3.12" -ForegroundColor Yellow
    exit 1
}

$pyVersion = & $PythonBin --version
Write-Host "  ✅ Using $pyVersion ($PythonBin)" -ForegroundColor Green

# 3. Create & Setup Virtual Environment
Write-Host ""
Write-Host "[3/4] Setting up Python Virtual Environment (.venv)..." -ForegroundColor Cyan

if (-not (Test-Path ".\.venv")) {
    Write-Host "  Creating virtual environment in .venv..."
    & $PythonBin -m venv .venv
} else {
    Write-Host "  Virtual environment already exists in .venv."
}

$VenvPython = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    $VenvPython = $PythonBin
}

Write-Host "  Upgrading pip and installing requirements..."
& $VenvPython -m pip install --upgrade pip --quiet
& $VenvPython -m pip install -r requirements.txt --quiet
Write-Host "  ✅ Python dependencies installed." -ForegroundColor Green

# 4. Run Diagnostics
Write-Host ""
Write-Host "[4/4] Verifying System Setup..." -ForegroundColor Cyan
& $VenvPython "$PSScriptRoot\check_env.py"

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Green
Write-Host "🎉 SETUP COMPLETED!" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps in Windows PowerShell:"
Write-Host "  1. Activate virtual environment:  .\.venv\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host "  2. Run all tests and emulator:     .\build_and_run.ps1 (or python run_all.py)" -ForegroundColor Cyan
Write-Host "  3. Launch live 2D visualizer:      python visualizer\serve.py" -ForegroundColor Cyan
Write-Host "  4. Explore interactive schematics: Start-Process schematics\index.html" -ForegroundColor Cyan
Write-Host ""
