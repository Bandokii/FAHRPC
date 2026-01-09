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
echo WARNING: This will remove all FAHRPC files.
echo UV must be uninstalled separately.
echo Running this file will create instructions for uv removal
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

echo [5/5] Creating uv uninstall instructions...
(
    echo uv Uninstallation Instructions
    echo ==============================
    echo.
    echo uv is installed at: %%USERPROFILE%%.local\bin\uv.exe
    echo.
    echo To completely remove uv from your system, follow these steps:
    echo.
    echo STEP 1: Clean up stored data ^(optional^)
    echo -------
    echo   - uv cache clean
    echo   - rm -r "$(uv python dir)"
    echo   - rm -r "$(uv tool dir)"
    echo.
    echo STEP 2: Remove uv binaries
    echo -------
    echo Run the following commands in PowerShell as Administrator:
    echo.
    echo   rm %%HOME%%.local\bin\uv.exe
    echo   rm %%HOME%%.local\bin\uvx.exe
    echo   rm %%HOME%%.local\bin\uvw.exe
    echo.
    echo STEP 3: Remove uv from PATH ^(if needed^)
    echo -------
    echo 1. Open Windows Settings ^> System ^> About ^> Advanced system settings
    echo 2. Click "Environment Variables"
    echo 3. Under "User variables" or "System variables", find PATH
    echo 4. Remove the entry: %%USERPROFILE%%.local\bin
    echo 5. Click OK and restart your terminal
    echo.
    echo STEP 4: Verify removal
    echo -------
    echo Run: where uv
    echo Expected result: "INFO: Could not find files for the given pattern^(s^)."
    echo.
    echo For more information on uv installation and uninstallation:
    echo https://docs.astral.sh/uv/getting-started/installation/#next-steps
) > UV_UNINSTALL.txt
echo [OK] uv uninstall instructions saved to UV_UNINSTALL.txt
echo.     Please refer to this file for manual uv removal steps
echo.

echo ====================================
echo   Uninstall Complete!
echo ====================================
echo.
echo [OK] FAHRPC has been successfully uninstalled.
echo.
echo Your system has been partially restored to its previous state.
echo The FAHRPC project folder can now be deleted if desired.
echo.
echo IMPORTANT NOTES:
echo ================
echo 1. uv package manager: Requires SEPARATE manual uninstallation.
echo    See UV_UNINSTALL.txt for detailed instructions.
echo.
echo 2. Python: Was not removed. If you installed Python separately,
echo    you may uninstall it manually through Windows Settings.
echo.
pause
exit /b 0
