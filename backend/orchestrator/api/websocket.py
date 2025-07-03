# orchestrator/api/websocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import json

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, job_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[job_id] = websocket

    def disconnect(self, job_id: str):
        if job_id in self.active_connections:
            del self.active_connections[job_id]

    async def send_progress(self, job_id: str, message: dict):
        if job_id in self.active_connections:
            await self.active_connections[job_id].send_text(json.dumps(message))


manager = ConnectionManager()


@router.websocket("/jobs/{job_id}/progress")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint for sending real-time progress updates for a job.
    """
    await manager.connect(job_id, websocket)
    try:
        # This is a placeholder loop to simulate sending progress updates.
        # In a real application, updates would be pushed from the processing tasks.
        for i in range(101):
            await manager.send_progress(
                job_id, {"phase": "processing", "progress_percent": i}
            )
            await asyncio.sleep(1)
        await manager.send_progress(job_id, {"phase": "completed", "progress_percent": 100})

    except WebSocketDisconnect:
        manager.disconnect(job_id)
        print(f"Client for job {job_id} disconnected")
    except Exception as e:
        print(f"An error occurred in websocket for job {job_id}: {e}")
        manager.disconnect(job_id)

