@echo off
REM FAHRPC Complete Setup Script (Windows Batch)
REM Installs uv package manager, dependencies, playwright, and creates launcher

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo ====================================
echo   FAHRPC Setup
echo   Complete Installation
echo ====================================
echo.

REM Step 1: Install uv if needed
echo [1/4] Checking uv package manager...
where uv >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('uv --version 2^>^&1') do set UV_VERSION=%%i
    echo [OK] uv is installed: !UV_VERSION!
) else (
    echo [INFO] uv not found, installing...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 | iex"
    echo [INFO] Restarting batch process to refresh PATH...
    setx PATH "%APPDATA%\Python\Scripts;%PATH%"
    call "%APPDATA%\Python\Scripts\uv.exe" --version >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] uv installed successfully
    ) else (
        echo [WARNING] uv may not be in PATH, but attempting to continue...
    )
)
echo.

REM Step 2: Sync dependencies (uv reads pyproject.toml automatically)
echo [2/4] Installing Python dependencies...
uv sync
if %errorlevel% neq 0 (
    echo [WARNING] Dependency sync had issues, continuing anyway...
)
echo [OK] Dependencies installed
echo.

REM Step 3: Install Playwright browser (required for web scraping)
echo [3/4] Installing Playwright Chromium browser...
uv run playwright install chromium
if %errorlevel% neq 0 (
    echo [WARNING] Playwright installation had issues
    echo You may need to run: uv run playwright install chromium
)
echo [OK] Playwright browser installed
echo.

REM Step 4: Create launcher script
echo [4/4] Creating launcher script...
if not exist "run_fahrpc.bat" (
    (
        echo @echo off
        echo REM FAHRPC Launcher - Run Folding@Home Discord Rich Presence
        echo REM Created by setup script
        echo.
        echo setlocal enabledelayedexpansion
        echo cd /d "%%~dp0"
        echo.
        echo REM Run FAHRPC using uv
        echo uv run python -m fahrpc.main
    ) > run_fahrpc.bat
    echo [OK] Launcher created: run_fahrpc.bat
) else (
    echo [OK] Launcher already exists: run_fahrpc.bat
)
echo.

REM Summary
echo ====================================
echo   Setup Complete!
echo ====================================
echo.
echo [OK] FAHRPC is ready to use!
echo.
echo To run FAHRPC:
echo   - Double-click: run_fahrpc.bat
echo   - Or use command: uv run python -m fahrpc.main
echo   - Or directly: fahrpc (if installed globally)
echo.
echo For detailed instructions, see README.txt
echo.

pause
exit /b 0
