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
- **Python 3.10+** - Installed automatically by setup
- **Discord** - Running and logged in
- **Folding@Home** - With web interface enabled (port 7396)
- **GPU** - NVIDIA or AMD with updated drivers
- **Internet** - For Discord and FAH stats server

## Installation

### Quick Start (Windows)

1. **Download** the FAHRPC folder
2. **Run** `setup.bat` (double-click)
3. **Launch** `run_fahrpc.bat` when setup completes
4. **View** your Folding@Home progress in Discord!

The setup script automatically:
- Installs uv package manager (if needed)
- Creates a virtual environment
- Installs all dependencies
- Generates the launcher script

### Global Installation (Advanced)

After initial setup, install globally for system-wide access:

```bash
uv tool install .
```

Then simply type `fahrpc` from anywhere to start the application.

## Usage

### Run FAHRPC

**Option 1: Batch Launcher (Easiest)**
```
Double-click run_fahrpc.bat
```

**Option 2: Command Line**
```bash
uv run python -m fahrpc.main
```

**Option 3: Global Command (If installed globally)**
```bash
fahrpc
```

### System Tray Menu

Right-click the FAHRPC icon in your system tray to:
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
5. Program: `cmd.exe`
6. Arguments: `/c "cd /d C:\path\to\FAHRPC && uv run python -m fahrpc.main"`

### Using Global Command

If installed globally with `uv tool install .`:

```
Arguments: /c "fahrpc"
```

### Using Startup Folder

1. Press `Windows+R` → type `shell:startup`
2. Create batch file with:
```batch
@echo off
cd /d "C:\path\to\FAHRPC"
uv run python -m fahrpc.main
```

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

### Playwright Installation Issues
- Ensure stable internet connection
- Run `setup.bat` again (idempotent)
- May require 500MB+ free disk space

## Uninstall

To remove FAHRPC, simply **delete the FAHRPC folder**. This removes all application files and the virtual environment.

Note: The **uv package manager will remain** on your system as a standalone tool. If you don't need uv for other projects, you can uninstall it separately by following the [official uv uninstallation instructions](https://docs.astral.sh/uv/getting-started/installation/#uninstallation).

## Dependencies

### Python Packages
- **playwright** - Web scraping and browser automation
- **pypresence** - Discord RPC integration
- **nvidia-ml-py** - NVIDIA GPU monitoring
- **pyadl** - AMD GPU monitoring
- **pystray** - System tray icon
- **Pillow** - Image handling

### External Software
- **uv** - Ultra-fast Python package manager (installed by setup)
- **Discord** - Discord client application
- **Folding@Home** - FAH client with web interface

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

## Publishing

To publish to PyPI:

1. Update version in `pyproject.toml`
2. Run `uv build`
3. Run `uv publish`

Users can then install with:
```bash
pip install fahrpc
uv tool install fahrpc
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

**Q: Does this work on Linux/macOS?**  
A: Currently Windows-only due to system tray integration and GPU driver dependencies. Cross-platform support would require refactoring.

**Q: Can I use custom GPU names?**  
A: Yes! Edit the `hardware.nvidia.strip_prefix` and `hardware.amd.strip_prefix` values in config.json

**Q: Does this impact Folding@Home performance?**  
A: No, FAHRPC only reads data. It has minimal CPU/memory overhead (~50MB RAM).

**Q: Can I monitor remote FAH instances?**  
A: Yes, update the `foldingathome.web_url` in config.json to point to another machine's IP:port

**Q: Is my Discord client ID exposed?**  
A: No, it's stored locally in config.json. The client ID is public by design.

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
