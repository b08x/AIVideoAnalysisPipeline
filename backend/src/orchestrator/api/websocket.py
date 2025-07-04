# orchestrator/api/websocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import json
import redis
import os
from typing import Dict, Any
from datetime import datetime
from orchestrator.logging_config import websocket_logger

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
            try:
                # Add timestamp to all progress messages
                message_with_timestamp = {
                    **message,
                    "timestamp": datetime.now().isoformat()
                }
                await self.active_connections[job_id].send_text(json.dumps(message_with_timestamp))
            except Exception as e:
                print(f"Error sending progress to job {job_id}: {e}")
                # Remove broken connection
                self.disconnect(job_id)

    async def send_stage_progress(self, job_id: str, stage: str, progress: int, details: Dict[str, Any] = None):
        """Send detailed stage progress with optional details"""
        message = {
            "type": "stage_progress",
            "stage": stage,
            "progress": progress,
            "details": details or {}
        }
        await self.send_progress(job_id, message)

    async def send_step_progress(self, job_id: str, stage: str, step: str, progress: int, total_steps: int, details: Dict[str, Any] = None):
        """Send detailed step progress within a stage"""
        message = {
            "type": "step_progress", 
            "stage": stage,
            "step": step,
            "progress": progress,
            "total_steps": total_steps,
            "details": details or {}
        }
        await self.send_progress(job_id, message)

    async def send_error(self, job_id: str, stage: str, error: str):
        """Send error message for a specific stage"""
        message = {
            "type": "error",
            "stage": stage,
            "error": error
        }
        await self.send_progress(job_id, message)

    async def send_completion(self, job_id: str, result: Dict[str, Any] = None):
        """Send job completion message"""
        message = {
            "type": "completion",
            "result": result or {}
        }
        await self.send_progress(job_id, message)


manager = ConnectionManager()


async def listen_for_progress_updates(job_id: str, websocket: WebSocket):
    """Listen for Redis pub/sub messages and forward them to WebSocket"""
    redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
    websocket_logger.info(f"Setting up Redis listener for job {job_id} on {redis_url}")
    
    try:
        redis_client = redis.from_url(redis_url)
        pubsub = redis_client.pubsub()
        
        channel = f"job_progress_{job_id}"
        websocket_logger.info(f"Subscribing to Redis channel: {channel}")
        pubsub.subscribe(channel)
        
        websocket_logger.info(f"Starting message loop for job {job_id}")
        message_count = 0
        
        while True:
            try:
                message = pubsub.get_message(timeout=1.0)
                if message and message['type'] == 'message':
                    message_count += 1
                    websocket_logger.debug(f"Job {job_id}: Received message #{message_count}")
                    try:
                        # Forward the message to WebSocket client
                        message_data = message['data'].decode('utf-8')
                        websocket_logger.debug(f"Job {job_id}: Forwarding message: {message_data[:200]}...")
                        await websocket.send_text(message_data)
                    except Exception as e:
                        websocket_logger.error(f"Job {job_id}: Error forwarding message to WebSocket: {e}")
                        break
                elif message is None:
                    # No message received, check if WebSocket is still connected
                    try:
                        await websocket.ping()
                        websocket_logger.debug(f"Job {job_id}: WebSocket ping successful")
                    except Exception as e:
                        websocket_logger.warning(f"Job {job_id}: WebSocket ping failed, client disconnected: {e}")
                        break
                else:
                    # Other message types (subscribe confirmation, etc.)
                    websocket_logger.debug(f"Job {job_id}: Received Redis message type: {message['type']}")
                    
            except Exception as e:
                websocket_logger.error(f"Job {job_id}: Error in message loop: {e}")
                break
                
    except Exception as e:
        websocket_logger.error(f"Job {job_id}: Error setting up Redis listener: {e}")
    finally:
        try:
            websocket_logger.info(f"Job {job_id}: Cleaning up Redis connection")
            pubsub.unsubscribe(channel)
            pubsub.close()
            redis_client.close()
            websocket_logger.info(f"Job {job_id}: Redis cleanup completed, processed {message_count} messages")
        except Exception as e:
            websocket_logger.error(f"Job {job_id}: Error during Redis cleanup: {e}")


@router.websocket("/jobs/{job_id}/progress")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint for sending real-time progress updates for a job.
    Listens to Redis pub/sub for progress updates from processing tasks.
    """
    websocket_logger.info(f"WebSocket connection request for job {job_id}")
    
    try:
        await manager.connect(job_id, websocket)
        websocket_logger.info(f"WebSocket connected for job {job_id}")
        
        # Send initial connection message
        await manager.send_progress(job_id, {
            "type": "connected",
            "message": f"Connected to job {job_id} progress stream"
        })
        websocket_logger.info(f"Sent initial connection message for job {job_id}")
        
        # Start listening for progress updates from Redis
        websocket_logger.info(f"Starting Redis listener for job {job_id}")
        await listen_for_progress_updates(job_id, websocket)

    except WebSocketDisconnect:
        manager.disconnect(job_id)
        websocket_logger.info(f"Client for job {job_id} disconnected normally")
    except Exception as e:
        websocket_logger.error(f"Error in websocket for job {job_id}: {e}")
        manager.disconnect(job_id)
        raise

