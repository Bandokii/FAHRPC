@echo off
REM FAHRPC Launcher - Run Folding@Home Discord Rich Presence
REM Created by setup script

setlocal enabledelayedexpansion
cd /d "%~dp0"

uv run --python 3.12 python -m fahrpc.main
set EXITCODE=%errorlevel%

if %EXITCODE% equ 0 (
    echo [OK] FAHRPC closed normally
    exit /b 0
) else (
    echo.
    echo ERROR: FAHRPC exited with code %EXITCODE%
    pause
    exit /b %EXITCODE%
)
