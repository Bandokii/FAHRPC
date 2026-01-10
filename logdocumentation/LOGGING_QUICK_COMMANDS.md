# FAHRPC Logging - Quick Reference

**Just looking for answers?** This is your page. One-page cheat sheet for all logging.

---

## Log Locations (Copy-Paste Ready)

### Setup Log
```
C:\Users\YourUsername\FAHRPC\fahrpc_setup.log
```

### Runtime Log (Main diagnostics)
```
%LOCALAPPDATA%\Bandokii\fahrpc\fah_error_log.txt
```

### Full Path (Windows 10/11)
```
C:\Users\YourUsername\AppData\Local\Bandokii\fahrpc\fah_error_log.txt
```

---

## Instant Commands (Copy-Paste Ready)

### View Runtime Log Live
```powershell
Get-Content -Path "$env:LOCALAPPDATA\Bandokii\fahrpc\fah_error_log.txt" -Wait
```

### View Last 50 Lines
```powershell
Get-Content -Path "$env:LOCALAPPDATA\Bandokii\fahrpc\fah_error_log.txt" -Tail 50
```

### Find All Errors
```powershell
Select-String "\[ERROR\|\[CRITICAL" "$env:LOCALAPPDATA\Bandokii\fahrpc\fah_error_log.txt"
```

### Find GPU Errors
```powershell
Select-String "hardware\.py" "$env:LOCALAPPDATA\Bandokii\fahrpc\fah_error_log.txt" | 
  Select-String "\[ERROR"
```

### Find FAH Connection Errors
```powershell
Select-String "FAH\|scraper" "$env:LOCALAPPDATA\Bandokii\fahrpc\fah_error_log.txt" | 
  Select-String "\[ERROR"
```

### Find Discord Errors
```powershell
Select-String "discord\|RPC" "$env:LOCALAPPDATA\Bandokii\fahrpc\fah_error_log.txt" | 
  Select-String "\[ERROR"
```

### Open Config Directory
```powershell
explorer "$env:LOCALAPPDATA\Bandokii\fahrpc"
```

### Open Installation Directory
```powershell
explorer "C:\Users\$env:USERNAME\FAHRPC"
```

---

## Log Format at a Glance

```
[TIMESTAMP] [LEVEL   ] module.function():line - Message
[EXCEPTION] ExceptionType: Details
[STACK TRACE]:
  Full traceback...
```

### Example
```
[2025-01-10 14:32:45] [ERROR  ] hardware.py.get_nvidia_data():85 - Failed to get Nvidia GPU data: NVML Error
[EXCEPTION] NVMLError_FunctionNotFound: driver not loaded
[STACK TRACE]:
  File "hardware.py", line 85, in get_nvidia_data
    temp = pynvml.nvmlDeviceGetTemperature(handle, 0)
```

---

## Field Meanings

| Field | Means | Example |
|-------|-------|---------|
| `[2025-01-10 14:32:45]` | When it happened | Timestamp |
| `[ERROR]` | Severity level | DEBUG, INFO, WARNING, ERROR, CRITICAL |
| `hardware.py` | Which file | Module filename |
| `get_nvidia_data()` | Which function | Function name |
| `:85` | Which line | Line number in code |
| `Failed to get GPU data` | What went wrong | Error description |
| `[EXCEPTION]` | Error type | The exception that was raised |
| `[STACK TRACE]` | Where it failed | Full call chain to root cause |

---

## Quick Troubleshooting

| Problem | Check Log | Look For |
|---------|-----------|----------|
| **Setup failed** | `fahrpc_setup.log` | `[STEP X/6]` with ERROR below |
| **App won't start** | `fah_error_log.txt` | `[ERROR]` near beginning |
| **GPU not detected** | `fah_error_log.txt` | `[STARTUP]` → GPU section with `Found 0` |
| **FAH not connecting** | `fah_error_log.txt` | `FAH connection lost: Connection refused` |
| **Discord not working** | `fah_error_log.txt` | `Discord.*connection.*ERROR` |
| **App crashes** | `fah_error_log.txt` | `[STACK TRACE]:` at crash point |
| **Config problem** | `fah_error_log.txt` | `[CONFIG]` section for details |

---

## Log Levels Explained

| Level | When | Example |
|-------|------|---------|
| **DEBUG** | Development info | GPU read attempts, initialization details |
| **INFO** | Major milestones | Startup complete, main loop started |
| **WARNING** | Recoverable issues | Fallback used, degraded mode |
| **ERROR** | Failed operation | GPU detection failed, connection lost |
| **CRITICAL** | System shutdown | Unrecoverable error, forcing exit |

---

## Error Categories by Module

### `hardware.py` (GPU Monitoring)
- Nvidia GPU detection failed → **Update GPU drivers**
- AMD GPU detection failed → **Install AMD drivers**
- Failed to get Nvidia/AMD GPU data → **Check GPU drivers**

### `scraper.py` (FAH Monitoring)
- FAH control page error → **Ensure FAH running on port 7396**
- FAH stats scraping failed → **Check internet connection**

### `discord_rpc.py` (Discord Updates)
- Discord connection failed → **Start Discord app**
- Discord RPC update failed → **Check Discord running**

### `tray.py` (System Tray Icon)
- Icon load failed → **Check FAHRPC.png in config folder**

### `config.py` (Configuration)
- Configuration error → **Check config.json syntax**
- File not found → **Created default config**

### `main.py` (Orchestration)
- Main loop error → **Check specific module error above**

---

## What Each Setup Step Does

| Step | What | If It Fails |
|------|------|-------------|
| 1/6 | Check uv package manager | Install uv |
| 2/6 | Install 7 Python dependencies | Retry dependencies |
| 3/6 | Install Playwright Chromium | Retry browser install |
| 4/6 | Create launcher script | Check permissions |
| 5/6 | Create desktop shortcut | Check shortcut settings |
| 6/6 | Verify all installed | Rerun setup |

---

## What Each Startup Step Does

| Step | What | If It Fails |
|------|------|-------------|
| System Info | Get platform/Python info | Continue (diagnostic only) |
| Config Load | Load configuration.json | Use defaults or create |
| GPU Init | Detect GPU hardware | Continue without GPU |
| Scraper Init | Start web browser for FAH | Cannot get stats |
| Discord Init | Connect to Discord RPC | Continue without Discord |
| Main Loop | Start monitoring | Crash, check errors |

---

## Log Rotation Details

**Main error log:**
- Current: `fah_error_log.txt` (0-10 MB)
- When full: Creates backup `fah_error_log.txt.1`
- Previous backups: `fah_error_log.txt.2` through `.5`
- Maximum storage: ~60 MB total

---

## Share Logs with Support

```powershell
# Create folder
New-Item -ItemType Directory -Path "$env:USERPROFILE\Desktop\FAHRPC_Logs"

# Copy logs
Copy-Item "C:\Users\$env:USERNAME\FAHRPC\fahrpc_setup.log" "$env:USERPROFILE\Desktop\FAHRPC_Logs\"
Copy-Item "$env:LOCALAPPDATA\Bandokii\fahrpc\fah_error_log.txt" "$env:USERPROFILE\Desktop\FAHRPC_Logs\"
Copy-Item "$env:LOCALAPPDATA\Bandokii\fahrpc\config.json" "$env:USERPROFILE\Desktop\FAHRPC_Logs\"

# Open folder
explorer "$env:USERPROFILE\Desktop\FAHRPC_Logs"
```

---

## Pro Tips

1. **Search for errors**: Use `Select-String "\[ERROR"` to find all errors
2. **Watch live**: Use `-Wait` flag to watch log as app runs
3. **Find section**: Search for `[STARTUP]`, `[CONFIG]`, `[MAIN LOOP]`
4. **Stack trace**: Last line shows root cause
5. **Timestamp**: Match times to see sequence of events

---

## Need More Details?

See `LOGGING_COMPLETE_REFERENCE.md` for comprehensive reference with examples and advanced debugging.

---

**Key Takeaway:** Check `fah_error_log.txt`, search for `[ERROR]`, read the `[STACK TRACE]` section below it. That's your answer! 🎯
