@echo off
:: --- Administrative Elevation Check ---
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [*] Requesting Administrative Privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:: --- NEW: Force the script to stay in its own folder ---
cd /d "%~dp0"

:: --- Script Logic ---
title FAHRPC Setup Launcher
echo =====================================================
echo FAHRPC Environment Unlocker
echo =====================================================

:: 1. Unlock PowerShell Execution Policy
echo [*] Unlocking PowerShell Execution Policy (RemoteSigned)...
powershell.exe -Command "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force"

:: 2. Launch the Verbose Setup Script
if exist "dpscript.ps1" (
    echo [OK] Found dpscript.ps1. Launching...
    echo.
    powershell.exe -ExecutionPolicy Bypass -File "dpscript.ps1"
) else (
    echo [ERROR] dpscript.ps1 not found! 
    echo Current Path: %cd%
    pause
)

exit /b