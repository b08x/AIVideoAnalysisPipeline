# orchestrator/api/jobs.py
from fastapi import (
    APIRouter,
    File,
    UploadFile,
    HTTPException,
    Depends,
    Request,
)
from sqlalchemy.orm import Session
import os
import shutil
import models
# from tasks import process_video_job  # Temporarily commented to fix startup

router = APIRouter()

# Simple health check endpoint
@router.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "orchestrator"}

# Dependency to get a DB session
def get_db():
    db = models.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Define file size limits
MAX_VIDEO_SIZE = 2 * 1024 * 1024 * 1024  # 2 GB
MAX_SUBTITLE_SIZE = 10 * 1024 * 1024  # 10 MB
SHARED_STORAGE_PATH = "/shared"


@router.post("/jobs", status_code=202)
async def create_job(request: Request):
    """
    Create a test processing job (accepts form data but returns mock response for now).
    """
    # Read and consume the request body to prevent connection issues
    try:
        form = await request.form()
        video_file = form.get("video")
        subtitle_file = form.get("subtitle") 
        config = form.get("config")
        
        # Log what we received for debugging
        print(f"Received files: video={video_file.filename if video_file else None}, subtitle={subtitle_file.filename if subtitle_file else None}")
        print(f"Config: {config}")
        
    except Exception as e:
        print(f"Error reading form data: {e}")
    
    # Return a mock response for now
    return {
        "job_id": 123, 
        "status": "pending", 
        "message": "Test job created successfully - files received and processing will be implemented soon"
    }


@router.get("/jobs/{job_id}")
def get_job_status(job_id: int, db: Session = Depends(get_db)):
    """
    Retrieve the status and results of a specific job.
    """
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.delete("/jobs/{job_id}", status_code=204)
def cancel_job(job_id: int, db: Session = Depends(get_db)):
    """
    Cancel a running job. (Note: This is a simplified implementation)
    """
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # In a real system, you would need to revoke the Celery task
    # from celery.app.control import Control
    # celery_app.control.revoke(task_id, terminate=True)
    job.status = models.JobStatus.FAILED
    db.commit()

    return {"message": "Job cancellation requested"}

