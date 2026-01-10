@echo off
REM FAHRPC Complete Setup Script (Windows Batch)
REM Installs uv package manager, dependencies, playwright, and creates launcher
REM Features: Intelligent retry logic for failed steps

setlocal enabledelayedexpansion
cd /d "%~dp0"

REM Setup tracking variables
set RETRY_COUNT=0
set MAX_RETRIES=2
set UV_FAILED=0
set DEPS_FAILED=0
set PLAYWRIGHT_FAILED=0

echo.
echo ====================================
echo   FAHRPC Setup
echo   Complete Installation
echo ====================================
echo.

REM Create log file for setup
set SETUP_LOGFILE=%~dp0fahrpc_setup.log
echo [%date% %time%] === FAHRPC Setup Started === >> "%SETUP_LOGFILE%"
echo [%date% %time%] Install Location: %~dp0 >> "%SETUP_LOGFILE%"
echo [%date% %time%] Python Version Check >> "%SETUP_LOGFILE%"
python --version >> "%SETUP_LOGFILE%" 2>&1
echo. >> "%SETUP_LOGFILE%"

REM Step 1: Install uv if needed
echo [1/6] Checking uv package manager...
echo [%date% %time%] [STEP 1/6] Checking uv package manager >> "%SETUP_LOGFILE%"
where uv >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('uv --version 2^>^&1') do set UV_VERSION=%%i
    echo [OK] uv is installed: !UV_VERSION!
    echo [%date% %time%] uv found: !UV_VERSION! >> "%SETUP_LOGFILE%"
) else (
    echo [INFO] uv not found, installing...
    echo [%date% %time%] uv not found, beginning installation >> "%SETUP_LOGFILE%"
    powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 | iex" >> "%SETUP_LOGFILE%" 2>&1
    echo [INFO] Updating PATH for uv...
    echo [%date% %time%] Updating PATH for uv >> "%SETUP_LOGFILE%"
    REM Add uv to PATH
    set "PATH=C:\Users\%USERNAME%\.local\bin;%PATH%"
    REM Also update system PATH for future sessions
    setx PATH "C:\Users\%USERNAME%\.local\bin;%PATH%" >nul 2>&1
    call "C:\Users\%USERNAME%\.local\bin\uv.exe" --version >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] uv installed successfully
        for /f "tokens=*" %%i in ('"C:\Users\%USERNAME%\.local\bin\uv.exe" --version 2^>^&1') do set UV_VERSION=%%i
        echo [%date% %time%] uv installed successfully: !UV_VERSION! >> "%SETUP_LOGFILE%"
    ) else (
        echo [WARNING] uv may not be in PATH, but attempting to continue...
        echo [%date% %time%] WARNING: uv installation status unknown >> "%SETUP_LOGFILE%"
        set UV_FAILED=1
    )
)
echo.

REM Step 2: Sync dependencies (uv reads pyproject.toml automatically)
REM Use Python 3.12 explicitly to avoid compatibility issues with Python 3.14+
echo [2/6] Installing Python dependencies (Attempt 1/!MAX_RETRIES!)...
echo [%date% %time%] [STEP 2/6] Installing dependencies from pyproject.toml >> "%SETUP_LOGFILE%"
echo [%date% %time%] Using Python 3.12 for compatibility >> "%SETUP_LOGFILE%"
uv sync --python 3.12 >> "%SETUP_LOGFILE%" 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Dependency sync had issues on first attempt
    echo [%date% %time%] WARNING: Dependency sync failed on attempt 1 >> "%SETUP_LOGFILE%"
    set DEPS_FAILED=1
) else (
    echo [%date% %time%] Dependencies installed successfully >> "%SETUP_LOGFILE%"
    set DEPS_FAILED=0
)
echo [OK] Dependencies pass 1 complete
echo.

REM Step 3: Install Playwright browser (required for web scraping)
echo [3/6] Installing Playwright Chromium browser (Attempt 1/!MAX_RETRIES!)...
echo [%date% %time%] [STEP 3/6] Installing Playwright Chromium browser >> "%SETUP_LOGFILE%"
uv run --python 3.12 playwright install chromium >> "%SETUP_LOGFILE%" 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Playwright installation had issues on first attempt
    echo [%date% %time%] WARNING: Playwright installation failed on attempt 1 >> "%SETUP_LOGFILE%"
    set PLAYWRIGHT_FAILED=1
) else (
    echo [%date% %time%] Playwright installed successfully >> "%SETUP_LOGFILE%"
    set PLAYWRIGHT_FAILED=0
)
echo [OK] Playwright pass 1 complete
echo.

REM Retry loop for failed steps
:retry_loop
if %RETRY_COUNT% geq %MAX_RETRIES% goto retry_done

if %DEPS_FAILED% equ 0 if %PLAYWRIGHT_FAILED% equ 0 goto retry_done

set /a RETRY_COUNT=!RETRY_COUNT! + 1
set ATTEMPT_NUM=!RETRY_COUNT!
set /a TOTAL_ATTEMPTS=!ATTEMPT_NUM! + 1

echo.
echo ════════════════════════════════════════════════════════════════════
echo RETRY PASS !ATTEMPT_NUM! OF !MAX_RETRIES! - Retrying failed components...
echo ════════════════════════════════════════════════════════════════════
echo.

REM Retry dependencies if failed
if %DEPS_FAILED% equ 1 (
    echo [2/6] Retrying Python dependencies (Attempt !TOTAL_ATTEMPTS!/!MAX_RETRIES!)...
    echo [%date% %time%] Retrying dependencies - Attempt !TOTAL_ATTEMPTS! >> "%SETUP_LOGFILE%"
    uv sync --python 3.12 >> "%SETUP_LOGFILE%" 2>&1
    if %errorlevel% neq 0 (
        echo [WARNING] Dependencies still failing on retry !ATTEMPT_NUM!
        echo [%date% %time%] ERROR: Dependencies still failing after retry >> "%SETUP_LOGFILE%"
    ) else (
        echo [OK] Dependencies recovered on retry !ATTEMPT_NUM!
        echo [%date% %time%] SUCCESS: Dependencies recovered on retry >> "%SETUP_LOGFILE%"
        set DEPS_FAILED=0
    )
    echo.
)

REM Retry Playwright if failed
if %PLAYWRIGHT_FAILED% equ 1 (
    echo [3/6] Retrying Playwright installation (Attempt !TOTAL_ATTEMPTS!/!MAX_RETRIES!)...
    echo [%date% %time%] Retrying Playwright - Attempt !TOTAL_ATTEMPTS! >> "%SETUP_LOGFILE%"
    timeout /t 2 /nobreak >nul
    uv run --python 3.12 playwright install chromium >> "%SETUP_LOGFILE%" 2>&1
    if %errorlevel% neq 0 (
        echo [WARNING] Playwright still failing on retry !ATTEMPT_NUM!
        echo [%date% %time%] ERROR: Playwright still failing after retry >> "%SETUP_LOGFILE%"
    ) else (
        echo [OK] Playwright recovered on retry !ATTEMPT_NUM!
        echo [%date% %time%] SUCCESS: Playwright recovered on retry >> "%SETUP_LOGFILE%"
        set PLAYWRIGHT_FAILED=0
    )
    echo.
)

goto retry_loop

:retry_done

REM Step 4: Create launcher script
echo [4/6] Creating launcher script...
echo [%date% %time%] [STEP 4/6] Creating launcher script >> "%SETUP_LOGFILE%"
if not exist "run_fahrpc.bat" (
    (
        echo @echo off
        echo REM FAHRPC Launcher - Run Folding@Home Discord Rich Presence
        echo REM Created by setup script
        echo.
        echo setlocal enabledelayedexpansion
        echo cd /d "%%~dp0"
        echo.
        echo uv run --python 3.12 python -m fahrpc.main
        echo set EXITCODE=%%errorlevel%%
        echo.
        echo if %%EXITCODE%% equ 0 ^(
        echo     echo [OK] FAHRPC closed normally
        echo     exit /b 0
        echo ^) else ^(
        echo     echo.
        echo     echo ERROR: FAHRPC exited with code %%EXITCODE%%
        echo     pause
        echo     exit /b %%EXITCODE%%
        echo ^)
    ) > run_fahrpc.bat
    echo [OK] Launcher created: run_fahrpc.bat
    echo [%date% %time%] Launcher script created successfully >> "%SETUP_LOGFILE%"
) else (
    echo [OK] Launcher already exists: run_fahrpc.bat
    echo [%date% %time%] Launcher script already exists >> "%SETUP_LOGFILE%"
)
echo.

REM Step 5: Create desktop shortcut
echo [5/6] Creating desktop shortcut...
echo [%date% %time%] [STEP 5/6] Creating desktop shortcut >> "%SETUP_LOGFILE%"
for /f "tokens=*" %%i in ('powershell -NoProfile -Command "Write-Host ([System.Environment]::GetFolderPath('Desktop'))"') do set DESKTOP=%%i

if not exist "%DESKTOP%\FAHRPC.lnk" (
    powershell -NoProfile -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Cursor]::Current = [System.Windows.Forms.Cursors]::WaitCursor; $ws = New-Object -ComObject WScript.Shell; $sc = $ws.CreateShortcut('%DESKTOP%\FAHRPC.lnk'); $sc.TargetPath = '%~dp0run_fahrpc.bat'; $sc.WorkingDirectory = '%~dp0'; $sc.Description = 'Folding@Home Discord Rich Presence'; $sc.Save();" >> "%SETUP_LOGFILE%" 2>&1
    if %errorlevel% equ 0 (
        echo [OK] Desktop shortcut created: FAHRPC.lnk
        echo [%date% %time%] Desktop shortcut created successfully >> "%SETUP_LOGFILE%"
    ) else (
        echo [WARNING] Could not create desktop shortcut, but setup is complete
        echo [%date% %time%] WARNING: Could not create desktop shortcut >> "%SETUP_LOGFILE%"
    )
) else (
    echo [OK] Desktop shortcut already exists: FAHRPC.lnk
    echo [%date% %time%] Desktop shortcut already exists >> "%SETUP_LOGFILE%"
)
echo.

REM Step 6: Verify dependencies and test imports
echo [6/6] Verifying installation...
echo [%date% %time%] [STEP 6/6] Verifying installation >> "%SETUP_LOGFILE%"

REM Final dependency status check
if %DEPS_FAILED% equ 1 (
    echo.
    echo [!] WARNING: Dependencies may still be incomplete
    echo    This could affect functionality
    echo    Try running: uv sync
    echo.
    echo [%date% %time%] WARNING: Dependencies incomplete >> "%SETUP_LOGFILE%"
)

if %PLAYWRIGHT_FAILED% equ 1 (
    echo.
    echo [!] WARNING: Playwright installation incomplete
    echo    This is required for web scraping
    echo    Try running: uv run playwright install chromium
    echo.
    echo [%date% %time%] WARNING: Playwright incomplete >> "%SETUP_LOGFILE%"
)

echo [%date% %time%] Testing Python imports... >> "%SETUP_LOGFILE%"
uv run --python 3.12 python -c "import sys, importlib.util; deps=['playwright','pypresence','pynvml','pystray','PIL','pyadl','platformdirs']; missing=[d for d in deps if not importlib.util.find_spec(d)]; (print(f'ERROR: Missing {missing}'), sys.exit(1)) if missing else None; from fahrpc import load_config, DiscordRPC, GPUMonitor, FAHScraper, TrayIcon; print('OK: All dependencies and modules verified')" >> "%SETUP_LOGFILE%" 2>&1
if %errorlevel% equ 0 (
    echo [OK] All dependencies verified
    echo [%date% %time%] All dependencies verified successfully >> "%SETUP_LOGFILE%"
) else (
    echo [WARNING] Dependency verification had issues
    echo Please check the error messages above
    echo [%date% %time%] WARNING: Dependency verification failed >> "%SETUP_LOGFILE%"
)
echo.

REM Summary
echo ====================================
echo   Setup Complete!
echo ====================================
echo.
echo [OK] FAHRPC is ready to use!
echo.
echo Setup Summary:
if %DEPS_FAILED% equ 0 (
    echo   - Python dependencies: OK
) else (
    echo   - Python dependencies: NEEDS ATTENTION (see warnings above)
)
if %PLAYWRIGHT_FAILED% equ 0 (
    echo   - Playwright browser: OK
) else (
    echo   - Playwright browser: NEEDS ATTENTION (see warnings above)
)
echo   - Launcher script: Created
echo   - Desktop shortcut: Created
echo.
echo To run FAHRPC:
echo   - Desktop shortcut: FAHRPC.lnk
echo   - Or double-click: run_fahrpc.bat
echo   - Or use command: uv run python -m fahrpc.main
echo   - Or directly: fahrpc (if installed globally)
echo.
echo For detailed instructions, see README.md
echo.

pause
exit /b 0
