    ╔══════════════════════════════════════════════════╗
    ║                      FAHRPC                      ║
    ║    Discord Rich Presence for Folding@Home        ║
    ║          GPU Monitoring & Stats Display          ║
    ╚══════════════════════════════════════════════════╝


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


SETUP INSTRUCTIONS
═══════════════════════════════════════════════════════

Step 1: Install Dependencies
───────────────────────────────
  1. Run DPSETUP.bat as Administrator
  2. This will automatically:
     • Set PowerShell execution policy
     • Run the dependency installation script (dpscript.ps1)
     • Install all required Python packages
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
  1. Run: python main.py
  2. The console window will appear (or hide to tray if configured)
  3. Status messages show connection state:
     [OK] Discord connection stable.
     [OK] FAH connection restored.
  4. Open Discord and you should see your folding status!

Step 4: Access Console (Optional)
──────────────────────────────────
FAHRPC can run hidden in the system tray:
  • Right-click the tray icon to show/hide console
  • Use menu options to restart or exit


TRAY ICON MENU
═══════════════════════════════════════════════════════

When running, FAHRPC provides a system tray icon with options:

  Show Console    - Display the console window
  Hide Console    - Hide console (app continues running)
  Restart FAHRPC  - Gracefully restart the application
  Exit            - Cleanly shut down FAHRPC


MAKE FAHRPC RUN ON STARTUP
═══════════════════════════════════════════════════════

To automatically start FAHRPC when Windows boots:

  1. Create a shortcut to main.py
  2. Press Windows+R and type: shell:startup
  3. Press Enter to open the Startup folder
  4. Paste the main.py shortcut into this folder
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
  • Discord client ID
  • Update interval (default: 15 seconds)
  • Temperature thresholds and display colors
  • Which GPUs to monitor (NVIDIA/AMD)
  • Log file location

Default configuration works out of the box - no changes needed to get started!


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
  • Confirm it's running on localhost:7396
  • Restart both F@H and FAHRPC

GPU Stats Not Showing
  • Ensure GPU drivers are installed
  • NVIDIA: Requires NVIDIA GPU driver
  • AMD: Requires AMD driver/library
  • Check fah_error_log.txt for hardware errors

High CPU Usage
  • Reduce update_interval in config.json
  • Disable unused GPU type in config.json
  • Check if web scraper is timing out


LOG FILES
═══════════════════════════════════════════════════════

fah_error_log.txt - Contains detailed logs of:
  • Connection attempts and status changes
  • Web scraper errors
  • GPU monitoring data
  • Discord RPC updates
  • Any issues encountered

Check this file to diagnose problems!
	
    
	  
	 
	 
	  
	  
	  
  