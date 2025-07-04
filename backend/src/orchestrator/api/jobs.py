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
import orchestrator.models as models
from orchestrator.models import Job, JobStatus
from orchestrator.tasks import process_video_job


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

router = APIRouter()



@router.post("/jobs", status_code=202)
async def create_job(
    video_file: UploadFile = File(...),
    subtitle_file: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    """
    Handles file uploads, creates a job record, and dispatches the main processing task.
    """
    # Create a new job record in the database
    new_job = Job(status=JobStatus.PENDING)
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    job_id = new_job.id

    # Define storage path for this job
    job_storage_path = os.path.join(SHARED_STORAGE_PATH, str(job_id))
    os.makedirs(job_storage_path, exist_ok=True)

    # Save video file
    video_file_path = os.path.join(job_storage_path, video_file.filename)
    with open(video_file_path, "wb") as buffer:
        shutil.copyfileobj(video_file.file, buffer)

    # Save subtitle file if provided
    subtitle_file_path = None
    if subtitle_file:
        subtitle_file_path = os.path.join(job_storage_path, subtitle_file.filename)
        with open(subtitle_file_path, "wb") as buffer:
            shutil.copyfileobj(subtitle_file.file, buffer)

    # Update the job record with file paths
    new_job.video_file_path = video_file_path
    new_job.subtitle_file_path = subtitle_file_path
    db.commit()

    # Dispatch the background task
    process_video_job.delay(job_id, video_file_path, subtitle_file_path)

    return {"job_id": job_id, "status": "pending"}


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

