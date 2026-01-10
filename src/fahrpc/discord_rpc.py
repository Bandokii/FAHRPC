"""
Discord RPC module for FAHRPC
Manages Discord Rich Presence connection and updates with retry logic
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from pypresence import AioPresence

logger = logging.getLogger('FAHRPC')

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
            await self.rpc.update(
                details=details,
                state=state,
                large_image="folding-at-home-logo",
                start=int(datetime.now().replace(
                    hour=0, minute=0, second=0, microsecond=0
                ).timestamp()),
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
