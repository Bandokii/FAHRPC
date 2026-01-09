@echo off
REM FAHRPC Uninstall Script
REM Removes all FAHRPC files, virtual environment, and uv installation

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo ====================================
echo   FAHRPC Uninstall Script
echo   Complete System Cleanup
echo ====================================
echo.
echo WARNING: This will remove all FAHRPC files and uv.
echo Your project folder can be safely deleted afterward.
echo.
set /p CONFIRM="Continue with uninstall? (y/n): "
if /i not "%CONFIRM%"=="y" (
    echo [INFO] Uninstall cancelled.
    pause
    exit /b 0
)

echo.
echo ====================================
echo   Starting Uninstall Process...
echo ====================================
echo.

echo [1/5] Stopping FAHRPC if running...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq*main.py*" >nul 2>&1
timeout /t 1 /nobreak >nul
echo [OK] Process cleanup complete
echo.

echo [2/5] Removing virtual environment...
if exist ".venv" (
    rmdir /s /q ".venv"
    echo [OK] Virtual environment removed
) else (
    echo [NOT FOUND] Virtual environment not installed
)
echo.

echo [3/5] Removing generated files...
if exist "RUN_FAHRPC.bat" (
    del /q "RUN_FAHRPC.bat"
    echo [OK] RUN_FAHRPC.bat removed
) else (
    echo [NOT FOUND] RUN_FAHRPC.bat
)
if exist "uv.lock" (
    del /q "uv.lock"
    echo [OK] uv.lock removed
) else (
    echo [NOT FOUND] uv.lock
)
if exist "fahrpc.egg-info" (
    rmdir /s /q "fahrpc.egg-info"
    echo [OK] fahrpc.egg-info removed
) else (
    echo [NOT FOUND] fahrpc.egg-info
)
if exist "fah_error_log.txt" (
    del /q "fah_error_log.txt"
    echo [OK] fah_error_log.txt removed
) else (
    echo [NOT FOUND] fah_error_log.txt
)
if exist "setup_log.txt" (
    del /q "setup_log.txt"
    echo [OK] setup_log.txt removed
) else (
    echo [NOT FOUND] setup_log.txt
)
if exist "setup_error_log.txt" (
    del /q "setup_error_log.txt"
    echo [OK] setup_error_log.txt removed
) else (
    echo [NOT FOUND] setup_error_log.txt
)
echo.

echo [4/5] Removing autostart entries...
REM Remove from Task Scheduler
schtasks /delete /tn "FAHRPC" /f >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Task Scheduler entry removed
) else (
    echo [NOT FOUND] Task Scheduler entry
)

REM Remove from Startup folder
if exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\FAHRPC.bat" (
    del /q "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\FAHRPC.bat"
    echo [OK] Startup folder entry removed
) else (
    echo [NOT FOUND] Startup folder entry
)
if exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\RUN_FAHRPC.bat" (
    del /q "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\RUN_FAHRPC.bat"
    echo [OK] Startup launcher removed
) else (
    echo [NOT FOUND] Startup launcher
)
echo.

echo [5/5] Uninstalling uv...
where uv >nul 2>&1
if %errorlevel% equ 0 (
    powershell -Command "& $env:USERPROFILE\.cargo\bin\uv.exe self uninstall --yes" >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] uv uninstalled
    ) else (
        echo [NOT FOUND] uv installation
    )
) else (
    echo [NOT FOUND] uv - not installed
)
echo.

echo ====================================
echo   Uninstall Complete!
echo ====================================
echo.
echo [OK] FAHRPC has been successfully uninstalled.
echo.
echo Your system has been restored to its previous state.
echo The FAHRPC project folder can now be deleted if desired.
echo.
pause
exit /b 0
