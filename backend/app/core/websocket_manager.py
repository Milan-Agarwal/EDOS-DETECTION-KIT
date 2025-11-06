"""
WebSocket Connection Manager for real-time communication
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Any
import json
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for different channels"""

    def __init__(self):
        # Store connections by channel type
        self.active_connections: Dict[str, List[WebSocket]] = {
            "alerts": [],
            "metrics": [],
            "network_traffic": [],
            "logs": [],
        }

    async def connect(self, websocket: WebSocket, channel: str):
        """Connect a client to a specific channel"""
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = []
        self.active_connections[channel].append(websocket)
        logger.info(
            f"Client connected to {channel} channel. Total: {len(self.active_connections[channel])}"
        )

    def disconnect(self, websocket: WebSocket, channel: str):
        """Disconnect a client from a channel"""
        if channel in self.active_connections:
            try:
                self.active_connections[channel].remove(websocket)
                logger.info(
                    f"Client disconnected from {channel} channel. Total: {len(self.active_connections[channel])}"
                )
            except ValueError:
                pass

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to a specific client"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")

    async def broadcast(self, channel: str, data: Any):
        """Broadcast message to all clients in a channel"""
        if channel not in self.active_connections:
            return

        message = json.dumps(data, default=str)
        disconnected_clients = []

        for connection in self.active_connections[channel]:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting to {channel}: {e}")
                disconnected_clients.append(connection)

        # Remove disconnected clients
        for client in disconnected_clients:
            self.disconnect(client, channel)

    def get_connection_count(self, channel: str) -> int:
        """Get number of active connections for a channel"""
        return len(self.active_connections.get(channel, []))

    def get_all_connection_counts(self) -> Dict[str, int]:
        """Get connection counts for all channels"""
        return {
            channel: len(connections)
            for channel, connections in self.active_connections.items()
        }
