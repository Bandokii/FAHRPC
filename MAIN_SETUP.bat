@echo off
REM FAHRPC UV Setup Script (Windows Batch)
REM Installs uv package manager and syncs dependencies

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo ====================================
echo   FAHRPC UV Setup
echo   Installing uv Package Manager
echo ====================================
echo.

REM Step 1: Install uv
echo [1/2] Installing uv package manager...
where uv >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('uv --version 2^>^&1') do set UV_VERSION=%%i
    echo [OK] uv is already installed: !UV_VERSION!
) else (
    echo [INFO] uv not found, installing...
    powershell -Command "irm https://astral.sh/uv/install.ps1 | iex" >nul 2>&1
    
    REM Check if uv actually installed despite PowerShell exit code
    where uv >nul 2>&1
    if %errorlevel% equ 0 (
        for /f "tokens=*" %%i in ('uv --version 2^>^&1') do set UV_VERSION=%%i
        echo [OK] uv installed successfully: !UV_VERSION!
    ) else (
        echo [ERROR] Failed to install uv
        echo Please install manually from: https://docs.astral.sh/uv/
        echo.
        echo Waiting before running main setup...
        timeout /t 3 /nobreak
    )
)

REM Step 2: Sync dependencies (continue even if error)
echo.
echo [2/2] Installing dependencies with uv sync...
echo.
uv sync
echo.
echo [OK] UV setup completed
echo.
echo Continuing with main setup...
timeout /t 2 /nobreak

REM Now run the main setup script
call useTheOtherSetup.bat
exit /b 0
