@echo off
REM FAHRPC Setup Script (Windows Batch)
REM Installs dependencies and prepares the virtual environment

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo ====================================
echo   FAHRPC Setup Script
echo   Ultra-Fast Python Manager
echo ====================================
echo.
echo This setup will:
echo   1. Check/install uv package manager
echo   2. Create virtual environment (.venv/)
echo   3. Install all Python dependencies
echo   4. Create RUN_FAHRPC.bat launcher
echo.
set /p CONFIRM="Continue with setup? (y/n): "
if /i not "%CONFIRM%"=="y" (
    echo [INFO] Setup cancelled.
    pause
    exit /b 0
)

echo.
echo ====================================
echo   Starting Setup Process...
echo ====================================
echo.

REM Step 1: Check if uv is installed
echo [1/3] Checking uv installation...
where uv >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('uv --version 2^>^&1') do set UV_VERSION=%%i
    echo [OK] uv is installed: !UV_VERSION!
) else (
    echo [INFO] uv not found, installing...
    
    REM Step 2: Install uv
    echo [2/3] Installing uv...
    powershell -Command "irm https://astral.sh/uv/install.ps1 | iex"
    
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install uv
        echo Please install manually from: https://docs.astral.sh/uv/
        pause
        exit /b 1
    )
    echo [OK] uv installed successfully
    goto :sync_deps
)

echo [2/3] uv already installed, skipping...

:sync_deps
REM Step 3: Sync dependencies
echo [3/3] Installing dependencies with uv sync...
echo.
uv sync
if %errorlevel% neq 0 (
    echo [ERROR] Failed to sync dependencies
    pause
    exit /b 1
)
echo.
echo [OK] Dependencies installed successfully

REM Step 4: Create launcher if it doesn't exist
if not exist "RUN_FAHRPC.bat" (
    echo [4/4] Creating launcher script...
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
)

REM Summary
echo ====================================
echo   Setup Complete!
echo ====================================
echo.
echo [OK] FAHRPC has been successfully installed and configured.
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
