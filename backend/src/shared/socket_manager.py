from fastapi import WebSocket
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New WebSocket client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Send message to all connected clients in parallel with timeout."""
        if not self.active_connections:
            return

        import asyncio

        # Snapshot list first — disconnect() mutates self.active_connections
        # so iterating it directly while removing items would skip entries.
        connections = list(self.active_connections)
        logger.info(f"[WS-BROADCAST] Sending to {len(connections)} client(s)")
        
        # Create tasks for all connections
        async def send_to_client(websocket: WebSocket):
            try:
                # 5 second timeout for each send to prevent hanging on slow clients
                await asyncio.wait_for(websocket.send_json(message), timeout=5.0)
                return None  # success — no action needed
            except Exception as e:
                logger.error(f"[WS-BROADCAST] Error sending to a client: {e}")
                return websocket  # signal: this connection should be removed

        # Run all sends in parallel.
        # No return_exceptions=True — inner try/except already handles all errors,
        # so gather will never see an unhandled exception from send_to_client.
        results = await asyncio.gather(*(send_to_client(conn) for conn in connections))
        
        # Cleanup failed connections
        to_remove = [res for res in results if res is not None]
        for ws in to_remove:
            self.disconnect(ws)
            
        if to_remove:
            logger.info(f"[WS-BROADCAST] Removed {len(to_remove)} dead connection(s).")

# Global instance
manager = ConnectionManager()
