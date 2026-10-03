@echo off
REM ==============================================================================
REM Automated Setup Script for Windows Command Prompt (CMD)
REM ==============================================================================

cd /d "%~dp0.."

echo ======================================================================
echo 🛠️  SETTING UP AI HARDWARE PLATFORM (WINDOWS CMD)
echo ======================================================================
echo.

REM Check Python
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python 3 was not found in PATH!
    echo Please install Python 3.10+ and check "Add Python to PATH".
    exit /b 1
)

echo [1/3] Creating Python Virtual Environment (.venv)...
IF NOT EXIST ".venv" (
    python -m venv .venv
) ELSE (
    echo Virtual environment already exists.
)

echo [2/3] Installing Python dependencies...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet

echo.
echo [3/3] Running environment diagnostics...
python "%~dp0check_env.py"

echo.
echo ======================================================================
echo 🎉 SETUP FINISHED!
echo ======================================================================
echo To run tests and emulator:
echo   call .venv\Scripts\activate.bat
echo   build_and_run.bat (or python run_all.py)
echo.
