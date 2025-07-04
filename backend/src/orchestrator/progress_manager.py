# orchestrator/progress_manager.py
import redis
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime
from orchestrator.logging_config import progress_logger


class ProgressManager:
    """
    Manages progress updates for job processing stages using Redis pub/sub.
    This allows Celery tasks to send progress updates that can be received by WebSocket handlers.
    """
    
    def __init__(self):
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        progress_logger.info(f"Initializing ProgressManager with Redis URL: {redis_url}")
        try:
            self.redis_client = redis.from_url(redis_url)
            # Test the connection
            self.redis_client.ping()
            progress_logger.info("Redis connection established successfully")
        except Exception as e:
            progress_logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    def _publish_progress(self, job_id: int, message: Dict[str, Any]):
        """Publish progress message to Redis channel"""
        try:
            channel = f"job_progress_{job_id}"
            message_with_timestamp = {
                **message,
                "timestamp": datetime.now().isoformat()
            }
            
            progress_logger.debug(f"Publishing to channel '{channel}': {message}")
            result = self.redis_client.publish(channel, json.dumps(message_with_timestamp))
            progress_logger.debug(f"Message published to {result} subscribers")
            
        except Exception as e:
            progress_logger.error(f"Error publishing progress for job {job_id}: {e}")
            raise
    
    def send_stage_start(self, job_id: int, stage: str, description: str):
        """Signal the start of a processing stage"""
        progress_logger.info(f"Job {job_id}: Starting stage '{stage}' - {description}")
        message = {
            "type": "stage_progress",
            "stage": stage,
            "progress": 0,
            "details": {"description": description, "status": "started"}
        }
        self._publish_progress(job_id, message)
    
    def send_stage_progress(self, job_id: int, stage: str, progress: int, details: Optional[Dict[str, Any]] = None):
        """Update progress for a processing stage"""
        progress_logger.debug(f"Job {job_id}: Stage '{stage}' progress: {progress}%")
        message = {
            "type": "stage_progress",
            "stage": stage,
            "progress": progress,
            "details": details or {}
        }
        self._publish_progress(job_id, message)
    
    def send_stage_complete(self, job_id: int, stage: str, result: Optional[Dict[str, Any]] = None):
        """Signal completion of a processing stage"""
        progress_logger.info(f"Job {job_id}: Completed stage '{stage}'")
        message = {
            "type": "stage_progress",
            "stage": stage,
            "progress": 100,
            "details": {"status": "completed", "result": result or {}}
        }
        self._publish_progress(job_id, message)
    
    def send_step_progress(self, job_id: int, stage: str, step: str, current: int, total: int, details: Optional[Dict[str, Any]] = None):
        """Update progress for a specific step within a stage"""
        progress = int((current / total) * 100) if total > 0 else 0
        progress_logger.debug(f"Job {job_id}: Stage '{stage}' step '{step}': {current}/{total} ({progress}%)")
        message = {
            "type": "step_progress",
            "stage": stage,
            "step": step,
            "progress": progress,
            "current": current,
            "total": total,
            "details": details or {}
        }
        self._publish_progress(job_id, message)
    
    def send_error(self, job_id: int, stage: str, error: str):
        """Send error message for a stage"""
        progress_logger.error(f"Job {job_id}: Error in stage '{stage}': {error}")
        message = {
            "type": "error",
            "stage": stage,
            "error": error
        }
        self._publish_progress(job_id, message)
    
    def send_completion(self, job_id: int, result: Optional[Dict[str, Any]] = None):
        """Send job completion message"""
        progress_logger.info(f"Job {job_id}: Processing completed successfully")
        message = {
            "type": "completion",
            "result": result or {}
        }
        self._publish_progress(job_id, message)


# Global instance will be created lazily
_progress_manager = None

def get_progress_manager():
    """Lazy initialization of ProgressManager to avoid blocking module import"""
    global _progress_manager
    if _progress_manager is None:
        try:
            progress_logger.info("Initializing ProgressManager (lazy initialization)...")
            _progress_manager = ProgressManager()
            progress_logger.info("ProgressManager initialized successfully")
        except Exception as e:
            progress_logger.error(f"Failed to initialize ProgressManager: {e}")
            raise
    return _progress_manager

# Backward compatibility - this will initialize on first access
class ProgressManagerProxy:
    def __getattr__(self, name):
        manager = get_progress_manager()
        return getattr(manager, name)

progress_manager = ProgressManagerProxy()