"""
FAHRPC - Folding@Home Discord Rich Presence
-------------------------------------------
Original Author: Bandokii
AI Collaborator: Claude Haiku 4.5
Refactored for Efficiency & Multi-GPU Support

Main entry point for modular FAHRPC with improved error handling,
caching, graceful shutdown, and retry logic.
"""

import asyncio
import time
import sys
import os
import re
import threading
import signal
import logging
from typing import Optional, Tuple, List

from modules import (
    load_config,
    setup_error_logging,
    GPUMonitor,
    FAHScraper,
    DiscordRPC,
    TrayIcon,
    set_console_visibility
)

# Global control flags
restart_event = threading.Event()
stop_event = threading.Event()

# Logger
logger: Optional[logging.Logger] = None

# ANSI Color Codes
COLORS = {
    "white": "\033[97m",
    "gray": "\033[90m",
    "red": "\033[91m",
    "blue": "\033[94m",
    "reset": "\033[0m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "orange": "\033[38;5;208m",
}

RE_ANSI = re.compile(r'\033\[[0-9;]*m')

def get_timestamp() -> str:
    """
    Returns a formatted white timestamp string.
    
    Returns:
        Formatted timestamp with ANSI colors
    """
    return f"{COLORS['white']}[{time.strftime('%H:%M:%S')}]{COLORS['reset']}"

def strip_ansi(text: str) -> str:
    """
    Removes ANSI codes to calculate visible string length.
    
    Args:
        text: String containing ANSI codes
        
    Returns:
        String without ANSI codes
    """
    return RE_ANSI.sub('', text)

def get_temp_color(temp: any, config: dict) -> str:
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
    
    if temp < thresholds['low']:
        return COLORS[color_names['low']]
    elif temp < thresholds['medium']:
        return COLORS[color_names['medium']]
    else:
        return COLORS[color_names['high']]

def print_header(config: dict) -> None:
    """
    Prints ASCII logo header.
    
    Args:
        config: Configuration dictionary
    """
    if not config['display']['show_header']:
        return
    
    RED = COLORS['red']
    BLUE = COLORS['blue']
    GRAY = COLORS['gray']
    RESET = COLORS['reset']
    WHITE = COLORS['white']
    
    lines = [
        rf"     {RED}______  ___   _   _{BLUE}  ______ ______  _____          ",
        rf"     {RED}|  ___|/ _ \ | | | |{BLUE} | ___ \| ___ \/  __ \         ",
        rf"     {RED}| |_  / /_\ \| |_| |{BLUE} | |_/ /| |_/ /| /  \/         ",
        rf"     {RED}|  _| |  _  ||  _  |{BLUE} |    / |  __/ | |             ",
        rf"     {RED}| |   | | | || | | |{BLUE} | |\ \ | |    | \__/\         ",
        rf"     {RED}\_|   \_| |_/\_| |_/{BLUE} \_| \_|\_|     \____/         ",
    ]
    
    signature = f"               {GRAY}By Bandokii & Claude{RESET}"
    hz = "═"
    divider = f"           {BLUE}{hz * 14}{WHITE}{hz}{RED}{hz * 14}{RESET}"
    
    print("\n" + "\n".join(lines))
    print(signature)
    print(f"{divider}\n")

async def retry_with_backoff(coro, max_retries: int = 3, initial_delay: float = 1.0) -> Optional[any]:
    """
    Execute a coroutine with exponential backoff retry logic.
    
    Args:
        coro: Coroutine to execute
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds between retries
        
    Returns:
        Result of the coroutine or None if all retries fail
    """
    delay = initial_delay
    for attempt in range(max_retries):
        try:
            return await coro
        except Exception as e:
            if attempt == max_retries - 1:
                logger.warning(f"All retry attempts exhausted: {e}")
                return None
            logger.debug(f"Retry attempt {attempt + 1}/{max_retries} after {delay}s delay: {e}")
            await asyncio.sleep(delay)
            delay *= 2  # Exponential backoff

async def main_logic() -> None:
    """Main application logic."""
    global logger
    
    # Enable ANSI colors on Windows
    if sys.platform == "win32":
        os.system('color')
    
    # Load configuration
    config = load_config()
    
    # Print header
    print_header(config)
    print(f" {get_timestamp()} {COLORS['white']}[*] Initializing Hardware Monitor...{COLORS['reset']}")
    
    # Initialize hardware monitor
    gpu_monitor = GPUMonitor(config)
    hardware_padding = " " * 13
    
    # Display detected hardware
    ts = get_timestamp()
    if gpu_monitor.nvidia_count == 0:
        print(f" {ts} {COLORS['red']}[-] Found Nvidia GPU: 0{COLORS['reset']}")
    else:
        print(f" {ts} {COLORS['green']}[+] Found Nvidia GPU: {gpu_monitor.nvidia_count}{COLORS['reset']}")
        for name in gpu_monitor.nvidia_names:
            print(f"{hardware_padding}└─ {name}")
    
    if gpu_monitor.amd_count == 0:
        print(f" {ts} {COLORS['red']}[-] Found AMD GPU: 0{COLORS['reset']}")
    else:
        print(f" {ts} {COLORS['green']}[+] Found AMD GPU: {gpu_monitor.amd_count}{COLORS['reset']}")
        for dev in gpu_monitor.amd_devices:
            clean_name = dev.adapterName.replace(config['hardware']['amd']['strip_prefix'], "").strip()
            print(f"{hardware_padding}└─ {clean_name}")

    # Intel GPU log output
    
    # Initialize scraper
    print(f" {get_timestamp()} {COLORS['white']}[*] Launching Web Scraper engine...{COLORS['reset']}")
    scraper = FAHScraper(config)
    try:
        await scraper.initialize()
        print(f" {get_timestamp()} {COLORS['green']}[OK] Scraper engine ready.{COLORS['reset']}")
    except Exception as e:
        print(f" {get_timestamp()} {COLORS['red']}[!] Browser Error: {e}{COLORS['reset']}")
        return
    
    # Initialize Discord RPC
    print(f" {get_timestamp()} {COLORS['white']}[*] Attempting Discord connection...{COLORS['reset']}")
    discord = DiscordRPC(config)
    
    # State variables
    global_points, global_wus = "Synchronizing...", "Synchronizing..."
    last_known_project = None
    cycle_index = 0
    was_running_last_check = True
    last_stats_sync_time = 0
    force_stats_sync = False
    sync_status = 'idle'
    fifty_percent_synced = False
    discord_lost_logged = False
    fah_lost_logged = False
    last_discord_status = False
    last_fah_status = False
    
    update_interval = config['foldingathome']['update_interval']
    
    try:
        while not restart_event.is_set() and not stop_event.is_set():
            # Connect to Discord if not connected with retry logic
            if not discord.connected:
                if await discord.connect():
                    if not last_discord_status:
                        print(f" {get_timestamp()} {COLORS['green']}[OK] Discord connection stable.{COLORS['reset']}")
                        last_discord_status = True
                    force_stats_sync = True
                    discord_lost_logged = False
                else:
                    if not discord_lost_logged:
                        print(f" {get_timestamp()} {COLORS['red']}[!] Discord not found.{COLORS['reset']}")
                        print(f"{hardware_padding}└─ Retrying...{COLORS['reset']}")
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
                        print(f" {get_timestamp()} {COLORS['red']}[!] FAH connection lost: {str(e)[:50]}...{COLORS['reset']}")
                        print(f"{hardware_padding}└─ Retrying connection...{COLORS['reset']}")
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
                    current_time = time.time()
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
                            last_stats_sync_time = current_time
                            sync_status = 'synced'
                            # Mark 50% sync as done if triggered by 50%
                            if percent_float >= 50.0:
                                fifty_percent_synced = True
                            print(f" {get_timestamp()} {COLORS['green']}[OK] StatSync: {COLORS['white']}{global_points} pts │ {global_wus} WUs{COLORS['reset']}")
                        else:
                            sync_status = 'idle'
                    
                    # Get GPU data with error handling
                    try:
                        gpu_data, utilizations, temperatures = gpu_monitor.get_all_gpu_data()
                    except Exception as e:
                        if logger:
                            logger.error(f"GPU data retrieval failed: {e}")
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
                            detail_texts.append(f"{indent if idx > 0 else ''}{COLORS['white']}Project{COLORS['reset']} │ {pid} - {COLORS['yellow']}{pct}%{COLORS['reset']}")
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
                                print(f"{hardware_padding}└─ Retrying every {update_interval} seconds...{COLORS['reset']}")
                                discord_lost_logged = True
                    except Exception as e:
                        if logger:
                            logger.debug(f"Discord RPC update failed: {e}")
                        if not discord_lost_logged:
                            discord_lost_logged = True
                else:
                    # Not running, clear RPC
                    try:
                        await discord.clear()
                    except Exception as e:
                        if logger:
                            logger.debug(f"Discord RPC clear failed: {e}")
                
            except Exception as e:
                if logger:
                    logger.error(f"Main loop iteration error: {e}")
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
                logger.error(f"Error closing Discord connection: {e}")
        
        try:
            await scraper.close()
            print(f" {get_timestamp()} {COLORS['green']}[OK] Scraper engine closed.{COLORS['reset']}")
        except Exception as e:
            if logger:
                logger.error(f"Error closing scraper: {e}")
        
        await asyncio.sleep(0.5)
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

if __name__ == "__main__":
    # Load config
    config = load_config()
    
    # Setup error logging
    logger = setup_error_logging(
        config['logging']['error_log_file'],
        config['logging']['suppress_asyncio_warnings']
    )
    
    # Define graceful shutdown handler
    def signal_handler(signum: int, frame) -> None:
        """Handle shutdown signals (SIGTERM, SIGINT)."""
        print(f"\n\n {get_timestamp()} {COLORS['yellow']}[*] Received shutdown signal ({signum})...{COLORS['reset']}")
        stop_event.set()
    
    # Register signal handlers for graceful shutdown
    if sys.platform != "win32":
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
    
    # Set console visibility
    set_console_visibility(not config['display']['start_hidden'])
    
    # Start tray icon
    tray = TrayIcon(config, restart_event, stop_event)
    tray.start()
    
    # Run main loop
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        set_console_visibility(True)
        print(f"\n\n {get_timestamp()} {COLORS['yellow']}[*] Received keyboard interrupt...{COLORS['reset']}")
        stop_event.set()
    except Exception as e:
        set_console_visibility(True)
        print(f"\n {get_timestamp()} {COLORS['red']}[FATAL ERROR]: {e}{COLORS['reset']}")
        input("Press Enter to close...")
    finally:
        GPUMonitor.shutdown()
