    ╔══════════════════════════════════════════════════╗
    ║                      FAHRPC                      ║
    ║    Discord Rich Presence for Folding@Home        ║
    ║          GPU Monitoring & Stats Display          ║
    ╚══════════════════════════════════════════════════╝
               By Bandokii & VScode copilot

WHAT IS FAHRPC?
═══════════════════════════════════════════════════════

FAHRPC is a Windows application that displays your Folding@Home progress
as Discord Rich Presence. While you're folding, your Discord status shows:

  • Current project ID and work unit progress
  • GPU model, utilization, and temperature
  • Personal Folding@Home score and completed work units
  • Real-time status updates every 15 seconds

The app also monitors your GPU (NVIDIA or AMD) to track performance and
automatically disables Rich Presence when folding is paused or connections
are lost.


PROJECT STRUCTURE
═══════════════════════════════════════════════════════

FAHRPC uses a modern Python src layout for better packaging and distribution:

  FAHRPC/
  ├── src/fahrpc/           (Main package directory)
  │   ├── __init__.py       (Package exports)
  │   ├── main.py           (Application entry point)
  │   ├── config.py         (Configuration loading)
  │   ├── logger.py         (Error logging)
  │   ├── hardware.py       (GPU monitoring)
  │   ├── scraper.py        (Web scraping)
  │   ├── discord_rpc.py    (Discord integration)
  │   └── tray.py           (System tray icon)
  ├── config.json           (User configuration)
  ├── main.py               (Root wrapper for compatibility)
  ├── pyproject.toml        (Project metadata & dependencies)
  ├── setup.bat             (Complete setup script)
  ├── run_fahrpc.bat        (Launcher, created by setup)
  └── README.txt            (This file)


SETUP INSTRUCTIONS
═══════════════════════════════════════════════════════

Step 1: Run Setup
─────────────────
  1. Run setup.bat (double-click it)
  2. This will automatically:
     • Check if uv is installed (installs if missing)
     • Create virtual environment (.venv/)
     • Install all required Python packages
     • Download Playwright Chromium browser
     • Create run_fahrpc.bat launcher for quick execution
  3. Monitor the console for any errors
  4. Check fah_error_log.txt if issues occur


Step 2: Verify Requirements
─────────────────────────────
After setup completes, ensure you have installed:
  ✓ Discord (running and logged in)
  ✓ Folding@Home (with web interface enabled on port 7396)
  ✓ GPU drivers (NVIDIA or AMD)

Step 3: Start FAHRPC
─────────────────────
Option A: Use the launcher (easiest)
  1. Double-click run_fahrpc.bat (created by setup.bat)
  2. The console window will appear with status messages
  3. Open Discord and you should see your folding status!

Option B: Command line
  1. Open command prompt or PowerShell in the project folder
  2. Run: uv run python -m fahrpc.main
  3. Status messages show connection state:
     [OK] Discord connection stable.
     [OK] FAH connection restored.

Option C: Global installation (advanced)
  1. After setup, run: uv tool install .
  2. Then simply type: fahrpc (from anywhere on your system)
  3. This installs FAHRPC as a global command-line tool

Step 4: Access Console (Optional)
──────────────────────────────────
FAHRPC can run hidden in the system tray:
  • Right-click the tray icon to show/hide console
  • Use menu options to restart or exit


TRAY ICON MENU
═══════════════════════════════════════════════════════

When running, FAHRPC provides a system tray icon with options to manage the
application without closing the main window.

Available Options:
  Show Console    - Display the console window for monitoring
  Hide Console    - Hide console to system tray (app continues running silently)
  Restart FAHRPC  - Gracefully restart the application
  Exit            - Cleanly shut down FAHRPC

The icon appears in your Windows system tray with the app name and allows easy
control without opening the console window.


UNINSTALLING FAHRPC
═══════════════════════════════════════════════════════

To remove FAHRPC:

  1. Delete the FAHRPC project folder

That's it! All application files and the virtual environment are removed.

Note: The uv package manager will remain on your system as a standalone tool.
If you don't need uv for other projects, you can uninstall it separately by
following the official instructions at:

  https://docs.astral.sh/uv/getting-started/installation/#uninstallation


MAKE FAHRPC RUN ON STARTUP
═══════════════════════════════════════════════════════

Option A: Using Task Scheduler (Recommended)
──────────────────────────────────────────────
  1. Press Windows+R and type: taskschd.msc
  2. Click "Create Basic Task"
  3. Name it "FAHRPC" and click Next
  4. Set trigger to "At startup" and click Next
  5. Set action to "Start a program"
  6. Set program to: cmd.exe
  7. Set arguments to: /c "cd /d path\to\FAHRPC && uv run python -m fahrpc.main"
     (Replace path\to\FAHRPC with your actual FAHRPC folder path)
  8. Click Finish

Option B: Global command startup (if using 'uv tool install')
──────────────────────────────────────────────────────────────
  1. Follow steps 1-5 above
  2. Set program to: cmd.exe
  3. Set arguments to: /c "fahrpc"
  4. This will start FAHRPC as a global command

Option C: Using Startup Folder (Simple)
─────────────────────────────────────────
  1. Press Windows+R and type: shell:startup
  2. Press Enter to open the Startup folder
  3. Create a new batch file with this content:
     @echo off
     cd /d "C:\path\to\FAHRPC"
     uv run python -m fahrpc.main
     (Replace C:\path\to\FAHRPC with your actual FAHRPC folder path)
  4. Save it in the Startup folder
  5. FAHRPC will now launch automatically on next boot


HOW IT WORKS
═══════════════════════════════════════════════════════

Discord Rich Presence Display:
  FAHRPC monitors Folding@Home and updates your Discord status with:
  • Project information (ID and completion percentage)
  • GPU statistics (model, utilization, temperature)
  • Personal stats (total points earned, work units completed)

Data Collection:
  • Uses chromium web scraper to monitor local FAH interface (localhost:7396)
  • Fetches global stats from official FAH stats server
  • Queries GPU drivers for real-time hardware data (NVIDIA/AMD)
  • Automatically reconnects if Discord or FAH connections are lost

Automatic Features:
  • Caches stats to reduce server load
  • Retries connections with exponential backoff
  • Clears Discord status when folding is paused
  • Tracks GPU temperature and displays color-coded warnings
  • Logs errors for troubleshooting


CONFIGURATION
═══════════════════════════════════════════════════════

Edit config.json to customize:
  • Discord client ID (default: pre-configured)
  • Folding@Home web interface URL (default: http://localhost:7396/)
  • FAH stats server URL (default: v8-5 stats server)
  • Update interval (default: 15 seconds)
  • Temperature thresholds and display colors
  • Which GPUs to monitor (NVIDIA/AMD) - both enabled by default
  • Display options (start hidden, show header, tray icon file)
  • Log file location (default: fah_error_log.txt)

Default configuration works out of the box - no changes needed to get started!

GPU SUPPORT
──────────
FAHRPC supports dual GPU monitoring:
  • NVIDIA: Full support via nvidia-ml-py (pynvml)
  • AMD: Full support via pyadl

Set enabled: false for either GPU type in config.json to skip detection and 
improve startup time if you don't have that hardware.


TROUBLESHOOTING
═══════════════════════════════════════════════════════

Discord Not Connecting
  • Ensure Discord is running and logged in
  • Check Windows firewall isn't blocking FAHRPC
  • FAHRPC auto-retries - wait a few seconds
  • Check fah_error_log.txt for details

Folding@Home Not Detected
  • Ensure F@H is running
  • Verify web interface is enabled in F@H settings
  • Confirm it's running on localhost:7396 (or update config.json)
  • Restart both F@H and FAHRPC

GPU Stats Not Showing
  • Ensure GPU drivers are installed and up to date
  • NVIDIA: Requires NVIDIA GPU driver with NVML support
  • AMD: Requires AMD driver and pyadl library
  • Check fah_error_log.txt for hardware errors
  • Verify GPU type is enabled in config.json

High CPU Usage
  • Increase update_interval in config.json (currently 15 seconds)
  • Disable unused GPU type in config.json (nvidia or amd)
  • Check if web scraper is timing out - may indicate F@H interface issues

Setup Issues

  Python Not Found After Installation
    • Restart the terminal/command prompt after setup completes
    • If still not found, verify Python installed to C:\Users\[username]\AppData\Local\Programs\Python\
    • Add Python to PATH manually if needed

  Playwright Installation Fails
    • Ensure internet connection is stable
    • Run setup.bat again - installation is idempotent
    • Check fah_error_log.txt for specific errors
    • May require 500MB+ free disk space for Chromium binary

  Administrator Privileges Required
    • setup.bat may require Administrator privileges
    • Right-click setup.bat → Run as Administrator
    • Some policies may require UAC approval

  Import Errors When Running main.py
    • Ensure setup.bat completed without errors
    • Check all dependencies installed: pip list | findstr playwright pypresence nvidia-ml-py pystray Pillow pyadl
    • Run setup.bat again if any packages are missing


LOG FILES
═══════════════════════════════════════════════════════

fah_error_log.txt - Contains detailed logs of:
  • Connection attempts and status changes
  • Web scraper errors
  • GPU monitoring data
  • Discord RPC updates
  • Any issues encountered

Check this file to diagnose problems!

DEPENDENCIES
═══════════════════════════════════════════════════════

FAHRPC requires the following Python packages (automatically installed by setup.bat):

Core Dependencies:
  • playwright          - Web scraping and browser automation
  • pypresence          - Discord RPC connection and updates
  • nvidia-ml-py        - NVIDIA GPU monitoring via pynvml
  • pyadl               - AMD GPU monitoring
  • pystray             - System tray icon management
  • Pillow (PIL)        - Image handling for tray icon

Python Version:
  • Python 3.10 or higher (3.12 recommended)

Dependency Manager:
  • uv - Ultra-fast Python package manager
    Automatically handles virtual environment creation and dependency locking
    No need to manually install pip or manage packages

External Requirements:
  • Windows 10+ operating system
  • Discord client (running and logged in)
  • Folding@Home client with web interface enabled (port 7396)
  • GPU drivers (NVIDIA or AMD, as applicable)
  • Administrator privileges for initial setup (if uv needs to be installed)

All dependencies are installed automatically by setup.bat
uv handles everything - just run setup.bat and you're done!


FUTURE: PUBLISHING TO PYPI
═══════════════════════════════════════════════════════

The new src layout makes FAHRPC ready for PyPI distribution. In the future,
you can publish FAHRPC globally with:

  1. Update version in pyproject.toml
  2. Run: uv build
  3. Run: uv publish

Users will then be able to install FAHRPC with a single command:
  uv tool install fahrpc

Or with pip:
  pip install fahrpc

This requires the project to be published to https://pypi.org
To verify the name "fahrpc" is available:
  Visit: https://pypi.org/project/fahrpc/