@echo off
REM ==============================================================================
REM Master Execution Script for Windows Command Prompt (CMD)
REM ==============================================================================

cd /d "%~dp0"

IF EXIST ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

echo ======================================================================
echo 🎯 1. RUNNING PYTHON COCOTB TESTBENCHES (PE ^& Systolic Array)
echo ======================================================================
python sim\run.py --dut all --sim icarus
IF %ERRORLEVEL% NEQ 0 (
    echo Error running Cocotb tests!
    exit /b %ERRORLEVEL%
)

echo.
echo ======================================================================
echo 🎯 2. BUILDING ^& RUNNING C++ VERILATOR CYCLE-ACCURATE EMULATOR
echo ======================================================================
python cpp_emulation\build_emulator.py --run
IF %ERRORLEVEL% NEQ 0 (
    echo Error building/running C++ emulator!
    exit /b %ERRORLEVEL%
)

echo.
echo ======================================================================
echo ✨ ALL HARDWARE VERIFICATION ^& PRE-SILICON EMULATION TESTS PASSED!
echo ======================================================================
