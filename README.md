# FAHRPC - Folding@Home Discord Rich Presence

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green)](license)
[![Windows](https://img.shields.io/badge/Platform-Windows-blue)](https://www.microsoft.com/windows/)

Monitor your Folding@Home GPU progress directly in Discord with real-time status updates, GPU stats, and performance metrics.

## Features

- 🎮 **Discord Rich Presence** - Display folding progress in your Discord status
- 💻 **GPU Monitoring** - Real-time GPU utilization and temperature tracking
- 🔍 **Dual GPU Support** - Monitor NVIDIA and AMD GPUs simultaneously
- 📊 **Live Stats** - Total points earned and work units completed
- 🔄 **Auto-Reconnect** - Graceful reconnection with exponential backoff
- 🌡️ **Temperature Alerts** - Color-coded temperature warnings
- 🎛️ **System Tray** - Minimize to tray with quick access menu
- ⚡ **Lightweight** - Minimal CPU and memory usage
- 🔧 **Configurable** - Full customization via config.json

## What You'll See

Your Discord status will display:
- Current project ID and work unit progress
- GPU model, utilization, and temperature
- Total Folding@Home points and completed work units
- Real-time updates every 15 seconds

## Requirements

- **Windows 10/11** - Windows operating system
- **Discord** - Running and logged in
- **Folding@Home** - With web interface enabled (port 7396)
- **GPU** - NVIDIA or AMD with updated drivers
- **Internet** - For Discord and FAH stats server

> **Note:** Python is NOT required to be pre-installed. The setup script handles everything automatically!

## Installation (Zip Download)

### Step 1: Download

1. Go to the [Releases](https://github.com/Bandokii/FAHRPC/releases) page
2. Download the latest `FAHRPC-vX.X.X.zip` file
3. Extract the zip to your desired location (e.g., `C:\FAHRPC`)

### Step 2: Run Setup

1. Open the extracted `FAHRPC` folder
2. **Double-click `setup.bat`**
3. Wait for setup to complete (first run may take 1-2 minutes)

The setup script automatically:
- Installs the uv package manager (if needed)
- Creates a virtual environment
- Installs all Python dependencies
- Downloads browser components for web scraping
- Generates the `run_fahrpc.bat` launcher

### Step 3: Launch

1. **Double-click `run_fahrpc.bat`**
2. Check your Discord status - you should see Folding@Home info!

That's it! 🎉

## Usage

### Running FAHRPC

Simply **double-click `run_fahrpc.bat`** in your FAHRPC folder.

The application will:
- Connect to Discord
- Monitor your Folding@Home progress
- Display stats in your Discord status
- Minimize to system tray

### System Tray

Once running, FAHRPC sits in your system tray. Right-click the icon to:
- Show/hide console window
- Restart application
- Exit cleanly

### Configuration

Edit `config.json` to customize:
- Discord client ID
- Folding@Home interface URL
- Temperature thresholds and colors
- GPU monitoring (NVIDIA/AMD)
- Update interval (default: 15 seconds)
- Display options

**Default configuration works out of the box!**

## Autostart (Optional)

### Using Task Scheduler (Recommended)

1. Press `Windows+R` → type `taskschd.msc`
2. Click "Create Basic Task"
3. Name: `FAHRPC`, Trigger: `At startup`
4. Action: Start program
5. Program: `C:\FAHRPC\run_fahrpc.bat` (use your actual path)

### Using Startup Folder

1. Press `Windows+R` → type `shell:startup`
2. Create a shortcut to `run_fahrpc.bat` in this folder

## Troubleshooting

### Discord Not Connecting
- Ensure Discord is running and logged in
- Check Windows Firewall isn't blocking FAHRPC
- FAHRPC auto-retries every 15 seconds

### Folding@Home Not Detected
- Ensure F@H is running
- Enable web interface in F@H settings
- Verify it's on `localhost:7396` (or update config.json)
- Restart both F@H and FAHRPC

### GPU Stats Not Showing
- Update GPU drivers (NVIDIA or AMD)
- Check `fah_error_log.txt` for hardware errors
- Verify GPU is enabled in `config.json`

### High CPU Usage
- Increase `update_interval` in config.json
- Disable unused GPU type in config.json
- Check web scraper timeouts in error log

### Setup Issues
- Ensure stable internet connection
- Run `setup.bat` again (safe to run multiple times)
- May require 500MB+ free disk space for browser components

## Updating

To update FAHRPC:
1. Download the latest zip from [Releases](https://github.com/Bandokii/FAHRPC/releases)
2. Extract and replace your existing files (keep your `config.json` if customized)
3. Run `setup.bat` again to update dependencies

## Uninstall

To remove FAHRPC:
1. **Delete the FAHRPC folder** - This removes all application files and the virtual environment

> **Note:** The uv package manager will remain on your system. If you don't need it, see the [uv uninstallation guide](https://docs.astral.sh/uv/getting-started/installation/#uninstallation).

## Advanced Installation (Optional)

For developers or advanced users who prefer command-line installation:

### Global Command Installation

After running `setup.bat`, you can install FAHRPC as a global command:

```bash
uv tool install .
```

Then run from anywhere with:
```bash
fahrpc
```

### Install from PyPI

```bash
pip install fahrpc
# or
uv tool install fahrpc
```

## Dependencies

All dependencies are automatically installed by `setup.bat`. For reference:

### Python Packages
- **playwright** - Web scraping and browser automation
- **pypresence** - Discord RPC integration
- **nvidia-ml-py** - NVIDIA GPU monitoring
- **pyadl** - AMD GPU monitoring
- **pystray** - System tray icon
- **Pillow** - Image handling

## Project Structure

```
FAHRPC/
├── src/fahrpc/           # Main package
│   ├── main.py          # Entry point
│   ├── config.py        # Configuration
│   ├── hardware.py      # GPU monitoring
│   ├── scraper.py       # Web scraping
│   ├── discord_rpc.py   # Discord integration
│   ├── logger.py        # Error logging
│   ├── tray.py          # System tray
│   └── __init__.py      # Package definition
├── config.json          # User settings
├── pyproject.toml       # Project metadata
├── setup.bat            # Installation script
└── run_fahrpc.bat       # Launcher (created by setup)
```

## Development

Clone the repository:

```bash
git clone https://github.com/Bandokii/FAHRPC.git
cd FAHRPC
```

Run in development mode:

```bash
uv run python -m fahrpc.main
```

Build distribution:

```bash
uv build
```

## License

MIT License - See [license](license) file for details

## Credits

**Original Creator:** Bandokii  
**AI Collaborator:** GitHub Copilot  
**Refactoring & Modernization:** January 2026

## Support

- 📖 See `README.txt` for detailed documentation
- 🆘 Check `fah_error_log.txt` for troubleshooting
- 🐛 Report issues on [GitHub Issues](https://github.com/Bandokii/FAHRPC/issues)
- 💬 Start discussions on [GitHub Discussions](https://github.com/Bandokii/FAHRPC/discussions)

## FAQ

**Q: Do I need Python installed?**  
A: No! The setup script handles everything automatically, including Python.

**Q: Does this work on Linux/macOS?**  
A: Currently Windows-only due to system tray integration and GPU driver dependencies.

**Q: Can I use custom GPU names?**  
A: Yes! Edit the `hardware.nvidia.strip_prefix` and `hardware.amd.strip_prefix` values in config.json

**Q: Does this impact Folding@Home performance?**  
A: No, FAHRPC only reads data. It has minimal CPU/memory overhead (~50MB RAM).

**Q: Can I monitor remote FAH instances?**  
A: Yes, update the `foldingathome.web_url` in config.json to point to another machine's IP:port

**Q: How do I update FAHRPC?**  
A: Download the latest zip, extract over your existing folder, and run `setup.bat` again.

## Changelog

### Version 1.0.0 (January 2026)
- Initial PyPI release
- Modern Python src layout
- Command-line entry point
- Full GPU monitoring
- Discord Rich Presence
- System tray integration
- Comprehensive error logging

---

**Happy Folding!** 🏠💪
