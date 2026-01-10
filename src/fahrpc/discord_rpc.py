"""
Discord RPC Module for FAHRPC
============================

Manages Discord Rich Presence connection for displaying Folding@Home stats.

Features:
    - Asynchronous connection management
    - Automatic reconnection on disconnect
    - Elapsed time display (resets at midnight)
    - Customizable buttons (Start Folding, GitHub links)
    - Connection status tracking

Discord Application Setup:
    1. Create an application at https://discord.com/developers/applications
    2. Copy the Client ID to config.json
    3. Set up Rich Presence assets (folding-at-home-logo)

Example usage:
    >>> from fahrpc.discord_rpc import DiscordRPC
    >>> discord = DiscordRPC(config)
    >>> await discord.connect()
    >>> await discord.update("Project 12345 - 50%", "GPU: RTX 3070 - 65°C")
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from pypresence import AioPresence

from fahrpc.config import APP_NAME

logger = logging.getLogger(APP_NAME.upper())

class DiscordRPC:
    """Manages Discord Rich Presence with connection status tracking."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize Discord RPC manager.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.rpc: Optional[AioPresence] = None
        self.connected: bool = False

    async def connect(self) -> bool:
        """
        Connect to Discord.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.rpc = AioPresence(self.config['discord']['client_id'])
            await self.rpc.connect()
            self.connected = True
            return True
        except Exception:
            self.rpc = None
            self.connected = False
            return False

    async def update(self, details: str, state: str) -> bool:
        """
        Update Rich Presence.

        Args:
            details: First line of RPC display
            state: Second line of RPC display

        Returns:
            True if update successful, False otherwise
        """
        if not self.connected or not self.rpc:
            return False

        try:
            # Use local time for the elapsed time display
            # Calculate seconds since midnight (local time)
            now = datetime.now()
            midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
            start_timestamp = int(midnight.timestamp())

            await self.rpc.update(
                details=details,
                state=state,
                large_image="folding-at-home-logo",
                start=start_timestamp,
                buttons=self.config['discord']['buttons']
            )
            return True
        except Exception:
            self.connected = False
            self.rpc = None
            return False

    async def clear(self) -> None:
        """Clear the Rich Presence display."""
        if self.rpc:
            try:
                await self.rpc.clear()
            except Exception:
                pass

    async def close(self) -> None:
        """Close the RPC connection and cleanup resources."""
        if self.rpc:
            try:
                await self.rpc.close()
            except Exception:
                pass
        self.connected = False
        self.rpc = None
