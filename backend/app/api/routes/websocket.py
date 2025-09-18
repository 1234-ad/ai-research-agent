"""
WebSocket routes for real-time updates.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
import json
import asyncio
from typing import Dict, Set

from app.core.database import get_db
from app.services.research import ResearchService

router = APIRouter()

# Store active WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, request_id: int):
        await websocket.accept()
        if request_id not in self.active_connections:
            self.active_connections[request_id] = set()
        self.active_connections[request_id].add(websocket)

    def disconnect(self, websocket: WebSocket, request_id: int):
        if request_id in self.active_connections:
            self.active_connections[request_id].discard(websocket)
            if not self.active_connections[request_id]:
                del self.active_connections[request_id]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except:
            pass  # Connection might be closed

    async def broadcast_to_request(self, message: str, request_id: int):
        if request_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[request_id]:
                try:
                    await connection.send_text(message)
                except:
                    disconnected.add(connection)
            
            # Remove disconnected connections
            for connection in disconnected:
                self.active_connections[request_id].discard(connection)

manager = ConnectionManager()

@router.websocket("/research/{request_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    request_id: int
):
    """
    WebSocket endpoint for real-time research progress updates.
    
    Clients can connect to this endpoint to receive live updates
    about the research workflow progress.
    """
    await manager.connect(websocket, request_id)
    
    try:
        # Send initial connection message
        await manager.send_personal_message(
            json.dumps({
                "type": "connection",
                "data": {
                    "message": f"Connected to research request {request_id}",
                    "request_id": request_id
                }
            }),
            websocket
        )
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for messages from client (ping/pong, etc.)
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                
                # Handle client messages
                try:
                    message = json.loads(data)
                    if message.get("type") == "ping":
                        await manager.send_personal_message(
                            json.dumps({"type": "pong", "data": {}}),
                            websocket
                        )
                except json.JSONDecodeError:
                    pass
                    
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                await manager.send_personal_message(
                    json.dumps({"type": "ping", "data": {}}),
                    websocket
                )
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, request_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, request_id)

# Function to send progress updates (called from Celery tasks)
async def send_progress_update(request_id: int, step: str, status: str, message: str, progress: int, details: dict = None):
    """
    Send progress update to all connected clients for a research request.
    """
    update_message = json.dumps({
        "type": "progress",
        "data": {
            "step": step,
            "status": status,
            "message": message,
            "progress": progress,
            "details": details or {}
        }
    })
    
    await manager.broadcast_to_request(update_message, request_id)

# Function to send completion update
async def send_completion_update(request_id: int, success: bool, results: dict = None, error: str = None):
    """
    Send completion update to all connected clients.
    """
    completion_message = json.dumps({
        "type": "completion",
        "data": {
            "success": success,
            "results": results,
            "error": error
        }
    })
    
    await manager.broadcast_to_request(completion_message, request_id)