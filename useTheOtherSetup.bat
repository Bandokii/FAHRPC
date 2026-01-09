@echo off
REM FAHRPC Setup Script (Windows Batch)
REM Prepares the virtual environment and creates launcher (after MAIN_SETUP.bat)

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo ====================================
echo   FAHRPC Setup Script
echo   Finalizing Installation
echo ====================================
echo.
echo This setup will:
echo   1. Create virtual environment (.venv/)
echo   2. Create RUN_FAHRPC.bat launcher
echo.

echo.
echo ====================================
echo   Starting Setup Process...
echo ====================================
echo.

REM Step 1: Create launcher if it doesn't exist
if not exist "RUN_FAHRPC.bat" (
    echo [1/2] Creating launcher script...
    (
        echo @echo off
        echo REM FAHRPC Launcher - Run Folding@Home Discord Rich Presence
        echo REM Can be used for quick launching or added to autostart
        echo.
        echo setlocal enabledelayedexpansion
        echo.
        echo REM Check if virtual environment exists
        echo if not exist ".venv" (
        echo     echo [ERROR] Virtual environment not found!
        echo     echo Please run setup.bat first
        echo     exit /b 1
        echo ^)
        echo.
        echo REM Run the application
        echo uv run python main.py
    ) > RUN_FAHRPC.bat
    echo [OK] Launcher created: RUN_FAHRPC.bat
    echo.
) else (
    echo [1/2] Launcher already exists: RUN_FAHRPC.bat
    echo.
)

REM Step 2: Check if .venv exists

REM Step 2: Check if .venv exists
if exist ".venv" (
    echo [2/2] Virtual environment found: .venv
    echo.
) else (
    echo [2/2] Virtual environment not found
    echo Note: This will be created when you run uv sync
    echo.
)

REM Summary
echo ====================================
echo   Setup Complete!
echo ====================================
echo.
echo [OK] FAHRPC has been successfully set up.
echo.
echo Getting Started:
echo   - Launch FAHRPC by running: RUN_FAHRPC.bat
echo   - Or use command line: uv run python main.py
echo.
echo The RUN_FAHRPC.bat launcher was created for easy access.
echo You can use it to start FAHRPC anytime, or add it to Windows startup.
echo.
echo For detailed instructions and troubleshooting, see README.txt
echo.

pause
exit /b 0
