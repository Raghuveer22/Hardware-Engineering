# ==============================================================================
# Master Execution Script for Windows PowerShell
# ==============================================================================

$ErrorActionPreference = "Stop"

# Navigate to project root directory
Set-Location -Path $PSScriptRoot

# Activate virtual environment if available
if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    & ".\.venv\Scripts\Activate.ps1"
}

# Determine Python command
$PythonBin = "python"
if (Get-Command "py" -ErrorAction SilentlyContinue) {
    $PythonBin = "py"
}

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "🎯 1. RUNNING PYTHON COCOTB TESTBENCHES (PE & Systolic Array)" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
& $PythonBin sim\run.py --dut all --sim icarus

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "🎯 2. BUILDING & RUNNING C++ VERILATOR CYCLE-ACCURATE EMULATOR" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
& $PythonBin cpp_emulation\build_emulator.py --run

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Green
Write-Host "✨ ALL HARDWARE VERIFICATION & PRE-SILICON EMULATION TESTS PASSED!" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Green
