# ==============================================================================
# FAHRPC VERBOSE SETUP SCRIPT
# This script automates the installation of Python and all script dependencies.
# ==============================================================================

# --- Setup Error Logging ---
$LogFile = "setup_log.txt"
$ErrorLogFile = "setup_error_log.txt"

# Start transcript to capture all output
Start-Transcript -Path $LogFile -Append

# Custom error handling
$ErrorActionPreference = "Continue"

# --- Custom Logging Function ---
function Write-Log {
    param (
        [Parameter(Mandatory=$true)] [string]$Message,
        [ValidateSet("INFO", "SUCCESS", "WARNING", "ERROR")] [string]$Type = "INFO"
    )
    $Timestamp = Get-Date -Format "HH:mm:ss"
    $Color = switch ($Type) {
        "SUCCESS" { "Green" }
        "WARNING" { "Yellow" }
        "ERROR"   { "Red" }
        default   { "White" }
    }
    Write-Host "[$Timestamp] " -NoNewline -ForegroundColor Gray
    Write-Host "[$Type] " -NoNewline -ForegroundColor $Color
    Write-Host $Message -ForegroundColor $Color
    
    # Also write to error log if it's an error
    if ($Type -eq "ERROR") {
        Add-Content -Path $ErrorLogFile -Value "[$Timestamp] [$Type] $Message"
    }
}

# --- 0. Pre-Flight Checks ---
Write-Log "Initializing FAHRPC Verbose Setup Engine..."
Write-Log "Current User: $env:USERNAME"
Write-Log "OS Version: $((Get-CimInstance Win32_OperatingSystem).Caption)"
Write-Log "Log files: $LogFile and $ErrorLogFile"

# --- 1. Python Installation via Winget ---
Write-Log "Phase 1: Verifying Python Environment..."
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Log "Python not detected in PATH. Searching Winget for Python 3..." "WARNING"
    try {
        $wingetOutput = winget install -e --id Python.Python.3 --source winget --accept-package-agreements --accept-source-agreements 2>&1
        Write-Log "Python installation triggered. Note: A manual restart of this terminal may be required." "SUCCESS"
        
        # Refresh PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    } catch {
        Write-Log "Failed to install Python via Winget. Please install manually from python.org." "ERROR"
        Write-Log "Error details: $_" "ERROR"
        Stop-Transcript
        exit 1
    }
} else {
    $pyVersion = python --version 2>&1
    Write-Log "Python is already present: $pyVersion" "SUCCESS"
}

# --- 2. Pip Upgrade & Health Check ---
Write-Log "Phase 2: Verifying Pip (Python Package Manager)..."
try {
    Write-Log "Sending command: python -m pip install --upgrade pip"
    $pipOutput = python -m pip install --upgrade pip 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Log "Pip successfully updated to latest version." "SUCCESS"
    } else {
        Write-Log "Pip upgrade returned non-zero exit code. Output: $pipOutput" "WARNING"
    }
} catch {
    Write-Log "Could not update Pip. Error: $_" "WARNING"
    Add-Content -Path $ErrorLogFile -Value "Pip upgrade error: $_"
}

# --- 3. Dependency Installation ---
Write-Log "Phase 3: Installing required Python libraries..."
$libraries = @("playwright", "pypresence", "nvidia-ml-py", "pystray", "Pillow", "pyadl")
$failedLibraries = @()

foreach ($lib in $libraries) {
    Write-Log "Attempting to install: $lib"
    try {
        $installResult = pip install $lib 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Successfully installed: $lib" "SUCCESS"
        } else {
            Write-Log "Error installing $lib. Exit code: $LASTEXITCODE" "ERROR"
            Add-Content -Path $ErrorLogFile -Value "Failed to install $lib : $installResult"
            $failedLibraries += $lib
        }
    } catch {
        Write-Log "Exception while installing $lib : $_" "ERROR"
        Add-Content -Path $ErrorLogFile -Value "Exception installing $lib : $_"
        $failedLibraries += $lib
    }
}

# --- 4. Playwright Infrastructure (UPDATED: Visible output) ---
Write-Log "Phase 4: Configuring Playwright browser binaries..."
Write-Log "Playwright requires a specific Chromium build for web scraping."
Write-Host ""
Write-Host "----------------------------------------" -ForegroundColor Cyan
Write-Host "Playwright Installation Output:" -ForegroundColor Cyan
Write-Host "----------------------------------------" -ForegroundColor Cyan

try {
    # Show the output instead of hiding it
    python -m playwright install chromium
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "----------------------------------------" -ForegroundColor Cyan
        Write-Log "Chromium binary is now ready for use by FAHRPC." "SUCCESS"
    } else {
        Write-Host "----------------------------------------" -ForegroundColor Cyan
        Write-Log "Playwright installation returned non-zero exit code." "WARNING"
        Add-Content -Path $ErrorLogFile -Value "Playwright install exit code: $LASTEXITCODE"
    }
} catch {
    Write-Host "----------------------------------------" -ForegroundColor Cyan
    Write-Log "Failed to initialize Playwright via python -m. Trying fallback..." "WARNING"
    Add-Content -Path $ErrorLogFile -Value "Playwright primary method failed: $_"
    
    try {
        playwright install chromium
        Write-Log "Fallback initialization successful." "SUCCESS"
    } catch {
        Write-Log "Failed to initialize Playwright. Scraper logic may fail." "ERROR"
        Add-Content -Path $ErrorLogFile -Value "Playwright fallback failed: $_"
        $failedLibraries += "playwright-chromium"
    }
}

# --- 5. Installation Verification ---
Write-Log "Phase 5: Verifying installation..."
try {
    $verifyResult = python -c "import playwright, pypresence, pynvml, pystray, PIL; print('All core imports successful')" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Log "Installation verification passed!" "SUCCESS"
    } else {
        Write-Log "Some imports failed. Check error log for details." "WARNING"
        Add-Content -Path $ErrorLogFile -Value "Import verification output: $verifyResult"
    }
} catch {
    Write-Log "Could not verify imports: $_" "WARNING"
}

# --- 6. Final Summary ---
Write-Log "========================================================="
if ($failedLibraries.Count -eq 0) {
    Write-Log "SETUP COMPLETE: Environment is ready for fah_presence.py" "SUCCESS"
} else {
    Write-Log "SETUP COMPLETED WITH ERRORS" "WARNING"
    Write-Log "Failed components: $($failedLibraries -join ', ')" "ERROR"
    Write-Log "Check $ErrorLogFile for detailed error information." "WARNING"
}
Write-Log "========================================================="
Write-Log "Full setup log saved to: $LogFile" "INFO"
Write-Log "IMPORTANT: If you just installed Python, RESTART THIS TERMINAL now." "WARNING"

# Stop transcript
Stop-Transcript

# Implementation of "Press any key to continue"
Write-Host "`nInstallation finished. Press any key to close this window..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Exit with appropriate code
if ($failedLibraries.Count -gt 0) {
    exit 1
} else {
    exit 0
}