"""
WebSocket Router
Real-time session updates and timer synchronization
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
import asyncio
import logging

logger = logging.getLogger("focus_engine.websockets")
router = APIRouter()

# Active WebSocket connections
active_connections: Dict[str, Set[WebSocket]] = {}

@router.websocket("/session/{session_id}")
async def websocket_session_updates(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time session updates"""

    await websocket.accept()

    # Add connection to active connections
    if session_id not in active_connections:
        active_connections[session_id] = set()
    active_connections[session_id].add(websocket)

    logger.info(f"WebSocket connected for session {session_id}")

    try:
        while True:
            # Listen for messages from client
            data = await websocket.receive_text()
            message = json.loads(data)

            # Echo message back to all connections for this session
            if session_id in active_connections:
                for connection in active_connections[session_id].copy():
                    try:
                        await connection.send_text(data)
                    except:
                        active_connections[session_id].discard(connection)

    except WebSocketDisconnect:
        # Remove connection
        if session_id in active_connections:
            active_connections[session_id].discard(websocket)
            if not active_connections[session_id]:
                del active_connections[session_id]

        logger.info(f"WebSocket disconnected for session {session_id}")

async def broadcast_session_update(session_id: str, update_data: dict):
    """Broadcast update to all connections for a session"""

    if session_id in active_connections:
        message = json.dumps(update_data)
        for connection in active_connections[session_id].copy():
            try:
                await connection.send_text(message)
            except:
                active_connections[session_id].discard(connection)
