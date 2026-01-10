"""
FAHRPC Main Module - Application Entry Point
============================================

Original Author: Bandokii
AI Collaborator: GitHub Copilot
Version: 1.0.1 (January 2026)

This is the main entry point for FAHRPC. It orchestrates all components:
- Initializes logging, configuration, and hardware monitoring
- Manages the main async event loop
- Handles Discord RPC updates and FAH data scraping
- Coordinates system tray icon and console visibility
- Implements graceful shutdown with signal handling

Application Flow:
    1. main() - Entry point, sets up logging and tray icon
    2. main_loop() - Manages restart/stop events
    3. main_logic() - Core monitoring loop (async)

Console Output:
    - Color-coded status messages (ANSI)
    - ASCII art header with app branding
    - Real-time GPU stats and project progress
    - Timestamp prefixes on all output

Command Line:
    $ fahrpc                   # If installed globally
    $ python -m fahrpc.main    # Direct execution
"""

import asyncio
import logging
import os
import re
import signal
import sys
import threading
import time
from typing import Any, Optional

from fahrpc import (
    DiscordRPC,
    FAHScraper,
    GPUMonitor,
    TrayIcon,
    get_log_path,
    load_config,
    set_console_visibility,
    setup_error_logging,
)

# ============================================================================
# Global State
# ============================================================================
# Threading events for coordinating shutdown and restart between
# the main async loop and the system tray icon thread

restart_event = threading.Event()  # Set by tray menu to trigger restart
stop_event = threading.Event()     # Set by tray menu or signal to trigger shutdown

# Logger instance (initialized in main())
logger: Optional[logging.Logger] = None

# ============================================================================
# Console Formatting Constants
# ============================================================================

# Padding for aligned console output (matches timestamp width)
HARDWARE_PADDING = " " * 13

# ANSI escape codes for colored terminal output
COLORS = {
    "white": "\033[97m",
    "gray": "\033[90m",
    "red": "\033[91m",
    "blue": "\033[94m",
    "reset": "\033[0m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "orange": "\033[38;5;208m",  # 256-color orange
}

# Regex to strip ANSI codes for length calculations
RE_ANSI = re.compile(r'\033\[[0-9;]*m')


# ============================================================================
# Utility Functions
# ============================================================================

def get_timestamp() -> str:
    """
    Returns a formatted white timestamp string for console output.

    Returns:
        Formatted timestamp like "[HH:MM:SS]" with ANSI colors
    """
    return f"{COLORS['white']}[{time.strftime('%H:%M:%S')}]{COLORS['reset']}"


def strip_ansi(text: str) -> str:
    """
    Removes ANSI escape codes to calculate visible string length.

    Args:
        text: String containing ANSI codes

    Returns:
        String without ANSI codes
    """
    return RE_ANSI.sub('', text)

def get_temp_color(temp: Any, config: dict) -> str:
    """
    Returns the ANSI color code based on temperature thresholds.

    Args:
        temp: Temperature value or "N/A"
        config: Configuration dictionary

    Returns:
        ANSI color code string
    """
    if temp == "N/A":
        return COLORS['white']

    thresholds = config['temperature']['thresholds']
    color_names = config['temperature']['colors']

    # Return color based on temperature thresholds from config
    if temp < thresholds['low']:
        return COLORS[color_names['low']]      # Green: cool
    elif temp < thresholds['medium']:
        return COLORS[color_names['medium']]   # Orange: warm
    else:
        return COLORS[color_names['high']]     # Red: hot


# ============================================================================
# Console Output Functions
# ============================================================================

def print_header(config: dict) -> None:
    """
    Prints the ASCII art FAHRPC logo header to console.

    Args:
        config: Configuration dictionary (checks display.show_header)
    """
    if not config['display']['show_header']:
        return

    # Color assignments for the two-tone FAH | RPC effect
    RED = COLORS['red']
    BLUE = COLORS['blue']
    GRAY = COLORS['gray']
    RESET = COLORS['reset']
    WHITE = COLORS['white']

    # ASCII art - "FAH" in red, "RPC" in blue
    lines = [
        rf"     {RED}______  ___   _   _{BLUE}  ______ ______  _____          ",
        rf"     {RED}|  ___|/ _ \ | | | |{BLUE} | ___ \| ___ \/  __ \         ",
        rf"     {RED}| |_  / /_\ \| |_| |{BLUE} | |_/ /| |_/ /| /  \/         ",
        rf"     {RED}|  _| |  _  ||  _  |{BLUE} |    / |  __/ | |             ",
        rf"     {RED}| |   | | | || | | |{BLUE} | |\ \ | |    | \__/\         ",
        rf"     {RED}\_|   \_| |_/\_| |_/{BLUE} \_| \_|\_|     \____/         ",
    ]

    signature = f"               {GRAY}By Bandokii & GitHub Copilot{RESET}"
    hz = "═"
    divider = f"           {BLUE}{hz * 14}{WHITE}{hz}{RED}{hz * 14}{RESET}"

    print("\n" + "\n".join(lines))
    print(signature)
    print(f"{divider}\n")


# ============================================================================
# Main Application Logic
# ============================================================================

async def main_logic() -> None:
    """
    Core application logic running in the async event loop.

    This function handles:
    - Hardware initialization and detection
    - FAH web scraper setup
    - Discord RPC connection
    - Main monitoring loop with periodic updates
    - Graceful shutdown and cleanup
    """
    global logger

    # Enable ANSI colors on Windows (required for colored output)
    if sys.platform == "win32":
        os.system('color')

    # ========================================================================
    # Startup Logging
    # ========================================================================
    logger.info("=" * 80)
    logger.info("FAHRPC Application Starting")
    logger.info("=" * 80)
    logger.info(f"Platform: {sys.platform}")
    logger.info(f"Python: {sys.version}")
    logger.info(f"Executable: {sys.executable}")

    config = load_config()
    logger.info(f"Configuration loaded from: {get_log_path().parent}")
    logger.debug(f"Config keys: {list(config.keys())}")

    # Print header
    print_header(config)
    print(f" {get_timestamp()} {COLORS['white']}[*] Initializing Hardware Monitor...{COLORS['reset']}")
    logger.info("[STARTUP] Initializing Hardware Monitor")

    # Initialize hardware monitor
    try:
        gpu_monitor = GPUMonitor(config)
        logger.info("[STARTUP] GPUMonitor initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize GPUMonitor: {e}", exc_info=True)
        print(f" {get_timestamp()} {COLORS['red']}[!] GPU Monitor Error: {e}{COLORS['reset']}")
        return

    # Display detected hardware
    ts = get_timestamp()
    if gpu_monitor.nvidia_count == 0:
        print(f" {ts} {COLORS['red']}[-] Found Nvidia GPU: 0{COLORS['reset']}")
        logger.info("[STARTUP] Nvidia GPU count: 0")
    else:
        print(f" {ts} {COLORS['green']}[+] Found Nvidia GPU: {gpu_monitor.nvidia_count}{COLORS['reset']}")
        logger.info(f"[STARTUP] Found {gpu_monitor.nvidia_count} Nvidia GPU(s)")
        for name in gpu_monitor.nvidia_names:
            print(f"{HARDWARE_PADDING}└─ {name}")
            logger.debug(f"[STARTUP] Nvidia GPU: {name}")

    if gpu_monitor.amd_count == 0:
        print(f" {ts} {COLORS['red']}[-] Found AMD GPU: 0{COLORS['reset']}")
        logger.info("[STARTUP] AMD GPU count: 0")
    else:
        print(f" {ts} {COLORS['green']}[+] Found AMD GPU: {gpu_monitor.amd_count}{COLORS['reset']}")
        logger.info(f"[STARTUP] Found {gpu_monitor.amd_count} AMD GPU(s)")
        for dev in gpu_monitor.amd_devices:
            clean_name = dev.adapterName.replace(config['hardware']['amd']['strip_prefix'], "").strip()
            print(f"{HARDWARE_PADDING}└─ {clean_name}")
            logger.debug(f"[STARTUP] AMD GPU: {clean_name}")

    # Initialize scraper
    print(f" {get_timestamp()} {COLORS['white']}[*] Launching Web Scraper engine...{COLORS['reset']}")
    logger.info("[STARTUP] Initializing FAH web scraper")
    scraper = FAHScraper(config)
    logger.debug("[STARTUP] FAHScraper instance created")
    logger.debug(f"[STARTUP] FAH control URL: {config['foldingathome']['web_url']}")
    logger.debug(f"[STARTUP] FAH stats URL: {config['foldingathome']['stats_url']}")

    try:
        logger.info("[STARTUP] Playwright browser initialization starting...")
        await scraper.initialize()
        logger.info("[STARTUP] Playwright browser initialized successfully")
        print(f" {get_timestamp()} {COLORS['green']}[OK] Scraper engine ready.{COLORS['reset']}")
    except Exception as e:
        if logger:
            logger.error(f"[STARTUP] Browser initialization failed: {e}", exc_info=True)
        print(f" {get_timestamp()} {COLORS['red']}[!] Browser Error: {e}{COLORS['reset']}")
        logger.critical("[STARTUP] Cannot continue without web scraper. Shutting down.")
        return

    # Initialize Discord RPC
    print(f" {get_timestamp()} {COLORS['white']}[*] Attempting Discord connection...{COLORS['reset']}")
    logger.info("[STARTUP] Initializing Discord RPC client")
    discord = DiscordRPC(config)
    logger.debug(f"[STARTUP] Discord RPC config: CLIENT_ID={config['discord']['client_id']}")

    # State variables
    global_points, global_wus = "Synchronizing...", "Synchronizing..."
    last_known_project = None
    cycle_index = 0
    was_running_last_check = True
    force_stats_sync = False
    sync_status = 'idle'
    fifty_percent_synced = False
    discord_lost_logged = False
    fah_lost_logged = False
    last_discord_status = False
    last_fah_status = False

    update_interval = config['foldingathome']['update_interval']

    logger.info(f"[STARTUP] Initialization complete. Update interval: {update_interval}s")
    logger.info("[STARTUP] Starting main monitoring loop...")
    logger.info("=" * 80)

    try:
        while not restart_event.is_set() and not stop_event.is_set():
            # Connect to Discord if not connected with retry logic
            if not discord.connected:
                if await discord.connect():
                    if not last_discord_status:
                        logger.info("[MAIN LOOP] Discord connection established")
                        print(f" {get_timestamp()} {COLORS['green']}[OK] Discord connection stable.{COLORS['reset']}")
                        last_discord_status = True
                    force_stats_sync = True
                    discord_lost_logged = False
                else:
                    if not discord_lost_logged:
                        logger.warning("[MAIN LOOP] Discord connection unavailable")
                        print(f" {get_timestamp()} {COLORS['red']}[!] Discord not found.{COLORS['reset']}")
                        print(f"{HARDWARE_PADDING}└─ Retrying...{COLORS['reset']}")
                        discord_lost_logged = True
                        last_discord_status = False
                    await asyncio.sleep(update_interval)
                    continue

            try:
                # Get FAH control data with error handling
                try:
                    percents, proj_ids, is_running = await scraper.get_control_data()
                    last_fah_status = True
                except Exception as e:
                    if not fah_lost_logged:
                        logger.error(f"FAH connection lost: {e}", exc_info=True)
                        err_msg = f"[!] FAH connection lost: {str(e)[:50]}..."
                        print(f" {get_timestamp()} {COLORS['red']}{err_msg}{COLORS['reset']}")
                        print(f"{HARDWARE_PADDING}└─ Retrying connection...{COLORS['reset']}")
                        fah_lost_logged = True
                        last_fah_status = False
                    await asyncio.sleep(update_interval)
                    continue

                if not last_fah_status:
                    print(f" {get_timestamp()} {COLORS['green']}[OK] FAH connection restored.{COLORS['reset']}")
                    last_fah_status = True
                    fah_lost_logged = False

                # Check for status changes
                if is_running and not was_running_last_check:
                    print(f" {get_timestamp()} {COLORS['green']}[+] Folding has started/resumed.{COLORS['reset']}")
                    force_stats_sync = True
                elif not is_running and was_running_last_check:
                    print(f" {get_timestamp()} {COLORS['yellow']}[!] Folding is currently paused.{COLORS['reset']}")

                was_running_last_check = is_running

                if is_running:
                    # Check if we need to sync stats
                    # Use first project for sync logic (legacy behavior)
                    percent_float = 0.0
                    proj_id = proj_ids[0] if proj_ids else "Active"
                    percent = percents[0] if percents else "0"
                    try:
                        percent_float = float(percent)
                    except Exception:
                        pass
                    # Reset 50% sync flag on new project
                    if proj_id != last_known_project:
                        fifty_percent_synced = False
                    needs_pull = (
                        proj_id != last_known_project or
                        (percent_float >= 50.0 and not fifty_percent_synced) or
                        sync_status == 'idle' or
                        force_stats_sync
                    )

                    if needs_pull and sync_status != 'pending':
                        sync_status = 'pending'
                        force_stats_sync = False
                        last_known_project = proj_id
                        print(f" {get_timestamp()} {COLORS['white']}[+] StatSync...{COLORS['reset']}")
                        new_pts, new_wus = await scraper.get_global_stats()
                        if new_pts:
                            global_points, global_wus = new_pts, new_wus
                            sync_status = 'synced'
                            # Mark 50% sync as done if triggered by 50%
                            if percent_float >= 50.0:
                                fifty_percent_synced = True
                            stats_msg = f"{global_points} pts │ {global_wus} WUs"
                            white = COLORS['white']
                            reset = COLORS['reset']
                            print(f" {get_timestamp()} {COLORS['green']}[OK] StatSync: {white}{stats_msg}{reset}")
                        else:
                            sync_status = 'idle'

                    # Get GPU data with error handling
                    try:
                        gpu_data, utilizations, temperatures = gpu_monitor.get_all_gpu_data()
                    except Exception as e:
                        if logger:
                            logger.error(f"GPU data retrieval failed: {e}", exc_info=True)
                        gpu_data, utilizations, temperatures = [], [], []

                    # Format GPU lines for console
                    gpu_lines_console = []
                    for name, util, temp in gpu_data:
                        t_color = get_temp_color(temp, config)
                        temp_display = f"{temp}°c" if temp != "N/A" else "N/A"
                        # Color GPU name by vendor
                        if name in gpu_monitor.nvidia_names:
                            name_colored = f"{COLORS['green']}{name}{COLORS['reset']}"
                        else:
                            name_colored = f"{COLORS['red']}{name}{COLORS['reset']}"
                        gpu_lines_console.append(f"{name_colored} │ {util}% - {t_color}{temp_display}{COLORS['reset']}")

                    # Format for RPC
                    if not gpu_lines_console:
                        rpc_gpu_text = "GPU Info Unavailable"
                        console_output = f"{COLORS['red']}GPU Info Unavailable{COLORS['reset']}"
                    else:
                        total_gpus = len(utilizations)
                        if total_gpus == 1:
                            raw_name = strip_ansi(gpu_lines_console[0].split('│')[0].strip())
                            temp_val = temperatures[0] if temperatures else "N/A"
                            temp_str = f"{temp_val}°c" if temp_val != "N/A" else "N/A"
                            rpc_gpu_text = f"{raw_name} │ {utilizations[0]}% - {temp_str}"
                        else:
                            avg_util = int(sum(utilizations) / total_gpus)
                            avg_temp = int(sum(temperatures) / len(temperatures)) if temperatures else "N/A"
                            temp_str = f"{avg_temp}°c" if avg_temp != "N/A" else "N/A"
                            rpc_gpu_text = f"GPUs: {total_gpus} │ x̄ {avg_util}% - x̄ {temp_str}"

                        # Format console output with padding
                        prefix_str = f"FAH{COLORS['blue']}RPC{COLORS['reset']} -"
                        ts_str = get_timestamp()
                        padding_len = len(strip_ansi(ts_str)) + 1 + len(strip_ansi(prefix_str)) + 1
                        padding_str = " " * padding_len

                        console_output = gpu_lines_console[0]
                        for line in gpu_lines_console[1:]:
                            console_output += f"\n{padding_str}{line}"

                    # Console logging cycles (unchanged)
                    if cycle_index % 2 == 0:
                        indent = ' ' * 21
                        detail_texts = []
                        for idx, (pid, pct) in enumerate(zip(proj_ids, percents)):
                            prefix = indent if idx > 0 else ''
                            white = COLORS['white']
                            yellow = COLORS['yellow']
                            reset = COLORS['reset']
                            proj_line = f"{white}Project{reset} │ {pid} - {yellow}{pct}%{reset}"
                            detail_texts.append(f"{prefix}{proj_line}")
                        console_line_final = "\n".join(detail_texts)
                    else:
                        console_line_final = console_output

                    # Discord Rich Presence cycle logic (separate from console)
                    num_projects = len(proj_ids)
                    discord_cycle = 0
                    if num_projects >= 2:
                        discord_cycle = cycle_index % 3
                        if discord_cycle == 0:
                            detail_text = f"pTotal: {global_points}"
                            state_text = f"WUs Completed: {global_wus}"
                        elif discord_cycle == 1:
                            detail_text = f"Project {proj_ids[0]} - {percents[0]}%"
                            state_text = f"Project {proj_ids[1]} - {percents[1]}%"
                        else:
                            detail_text = rpc_gpu_text
                            state_text = '"hyper modern space heater"'
                    elif num_projects == 1:
                        discord_cycle = cycle_index % 2
                        if discord_cycle == 0:
                            detail_text = f"pTotal: {global_points}"
                            state_text = f"WUs Completed: {global_wus}"
                        else:
                            detail_text = rpc_gpu_text
                            state_text = f"Project {proj_ids[0]} - {percents[0]}%"
                    else:
                        detail_text = f"pTotal: {global_points}"
                        state_text = f"WUs Completed: {global_wus}"

                    # Update Discord RPC with error handling
                    try:
                        if await discord.update(detail_text, state_text):
                            # Project line: [timestamp] FAHRPC - Project │ <project_id> - <percent>%
                            # GPU line: [timestamp] FAHRPC - <gpu info>
                            fah_rpc_colored = f"{COLORS['red']}FAH{COLORS['blue']}RPC{COLORS['reset']}"
                            print(f" {get_timestamp()} {fah_rpc_colored} - {console_line_final}")
                            cycle_index += 1
                        else:
                            if not discord_lost_logged:
                                print(f" {get_timestamp()} {COLORS['red']}[!] Discord not found.{COLORS['reset']}")
                                retry_msg = f"└─ Retrying every {update_interval} seconds..."
                                print(f"{HARDWARE_PADDING}{retry_msg}{COLORS['reset']}")
                                discord_lost_logged = True
                    except Exception as e:
                        if logger:
                            logger.error(f"Discord RPC update failed: {e}", exc_info=True)
                        if not discord_lost_logged:
                            discord_lost_logged = True
                else:
                    # Not running, clear RPC
                    try:
                        await discord.clear()
                    except Exception as e:
                        if logger:
                            logger.error(f"Discord RPC clear failed: {e}", exc_info=True)

            except Exception as e:
                if logger:
                    logger.error(f"Main loop iteration error: {e}", exc_info=True)
                await asyncio.sleep(update_interval)
                continue

            await asyncio.sleep(update_interval)

    finally:
        # Graceful shutdown and cleanup
        print(f"\n {get_timestamp()} {COLORS['yellow']}[*] Shutting down gracefully...{COLORS['reset']}")

        try:
            await discord.close()
            print(f" {get_timestamp()} {COLORS['green']}[OK] Discord connection closed.{COLORS['reset']}")
        except Exception as e:
            if logger:
                logger.error(f"[SHUTDOWN] Error closing Discord connection: {e}", exc_info=True)

        try:
            await scraper.close()
            logger.info("[SHUTDOWN] Web scraper closed")
            print(f" {get_timestamp()} {COLORS['green']}[OK] Scraper engine closed.{COLORS['reset']}")
        except Exception as e:
            if logger:
                logger.error(f"[SHUTDOWN] Error closing scraper: {e}", exc_info=True)

        await asyncio.sleep(0.5)
        if logger:
            logger.info("[SHUTDOWN] Shutdown complete")
            logger.info("=" * 80)
        print(f" {get_timestamp()} {COLORS['green']}[OK] Shutdown complete.{COLORS['reset']}")

async def main_loop() -> None:
    """
    Main wrapper to handle restart/stop logic.

    Manages the application lifecycle including restarts and graceful shutdown.
    """
    while not stop_event.is_set():
        restart_event.clear()
        task = asyncio.create_task(main_logic())

        while not restart_event.is_set() and not stop_event.is_set():
            await asyncio.sleep(1)

        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

        await asyncio.sleep(0.5)

        if restart_event.is_set():
            print(f"\n {get_timestamp()} {COLORS['yellow']}[*] Restarting logic...{COLORS['reset']}")
            await asyncio.sleep(1)

def main() -> None:
    """Entry point for fahrpc command."""
    # Load config
    config = load_config()

    # Setup error logging (use proper app data directory)
    global logger
    log_file = str(get_log_path(config['logging']['error_log_file']))
    logger = setup_error_logging(
        log_file,
        config['logging']['suppress_asyncio_warnings']
    )
    logger.info("=" * 80)
    logger.info("FAHRPC Application Entry Point")
    logger.info("=" * 80)

    # Define graceful shutdown handler
    def signal_handler(signum: int, frame) -> None:
        """Handle shutdown signals (SIGTERM, SIGINT)."""
        logger.warning(f"[SIGNAL] Received signal {signum}, initiating graceful shutdown")
        print(f"\n\n {get_timestamp()} {COLORS['yellow']}[*] Received shutdown signal ({signum})...{COLORS['reset']}")
        stop_event.set()

    # Register signal handlers for graceful shutdown
    if sys.platform != "win32":
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)

    # Set console visibility
    set_console_visibility(not config['display']['start_hidden'])
    logger.info(f"[MAIN] Console visible: {not config['display']['start_hidden']}")

    # Start tray icon
    try:
        logger.info("[MAIN] Starting system tray icon")
        tray = TrayIcon(config, restart_event, stop_event)
        tray.start()
        logger.info("[MAIN] System tray icon started")
    except Exception as e:
        logger.error(f"[MAIN] Failed to start tray icon: {e}", exc_info=True)
        print(f" {get_timestamp()} {COLORS['red']}[!] Tray Error: {e}{COLORS['reset']}")

    # Run main loop
    try:
        logger.info("[MAIN] Starting main event loop")
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        logger.warning("[MAIN] Keyboard interrupt received")
        set_console_visibility(True)
        print(f"\n\n {get_timestamp()} {COLORS['yellow']}[*] Received keyboard interrupt...{COLORS['reset']}")
        stop_event.set()
    except Exception as e:
        logger.error(f"[MAIN] Unhandled exception in main loop: {e}", exc_info=True)
        set_console_visibility(True)
        print(f"\n {get_timestamp()} {COLORS['red']}[FATAL ERROR]: {e}{COLORS['reset']}")
        input("Press Enter to close...")
    finally:
        logger.info("[MAIN] Shutting down GPU monitor")
        try:
            GPUMonitor.shutdown()
        except Exception as e:
            logger.error(f"[MAIN] Error during GPU monitor shutdown: {e}", exc_info=True)
        logger.info("[MAIN] Application exited")

if __name__ == "__main__":
    main()
