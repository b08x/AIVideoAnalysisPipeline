# orchestrator/api/jobs.py
from fastapi import (
    APIRouter,
    File,
    UploadFile,
    HTTPException,
    Depends,
    Request,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
import shutil
import orchestrator.models as models
from orchestrator.models import Job, JobStatus
from orchestrator.tasks import process_video_job
from orchestrator.logging_config import orchestrator_logger


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
    orchestrator_logger.info("=== NEW JOB CREATION REQUEST ===")
    orchestrator_logger.info(f"Video file: {video_file.filename if video_file else 'None'}")
    orchestrator_logger.info(f"Subtitle file: {subtitle_file.filename if subtitle_file else 'None'}")
    
    # Basic validation
    if not video_file or not video_file.filename:
        orchestrator_logger.error("Video file validation failed: no file provided")
        raise HTTPException(status_code=422, detail="Video file is required")
    
    if video_file.filename == "":
        orchestrator_logger.error("Video file validation failed: empty filename")
        raise HTTPException(status_code=422, detail="Video filename cannot be empty")
    # Create a new job record in the database
    orchestrator_logger.info("Creating new job record in database")
    new_job = Job(status=JobStatus.PENDING)
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    job_id = new_job.id
    orchestrator_logger.info(f"Created job with ID: {job_id}")

    # Define storage path for this job
    job_storage_path = os.path.join(SHARED_STORAGE_PATH, str(job_id))
    orchestrator_logger.info(f"Creating job storage directory: {job_storage_path}")
    os.makedirs(job_storage_path, exist_ok=True)

    # Save video file
    video_file_path = os.path.join(job_storage_path, video_file.filename)
    orchestrator_logger.info(f"Saving video file to: {video_file_path}")
    with open(video_file_path, "wb") as buffer:
        shutil.copyfileobj(video_file.file, buffer)
    orchestrator_logger.info(f"Video file saved, size: {os.path.getsize(video_file_path)} bytes")

    # Save subtitle file if provided
    subtitle_file_path = None
    if subtitle_file:
        subtitle_file_path = os.path.join(job_storage_path, subtitle_file.filename)
        orchestrator_logger.info(f"Saving subtitle file to: {subtitle_file_path}")
        with open(subtitle_file_path, "wb") as buffer:
            shutil.copyfileobj(subtitle_file.file, buffer)
        orchestrator_logger.info(f"Subtitle file saved, size: {os.path.getsize(subtitle_file_path)} bytes")
    else:
        orchestrator_logger.info("No subtitle file provided")

    # Update the job record with file paths
    orchestrator_logger.info("Updating job record with file paths")
    new_job.video_file_path = video_file_path
    new_job.subtitle_file_path = subtitle_file_path
    db.commit()
    orchestrator_logger.info("Job record updated successfully")

    # Dispatch the background task to the default queue
    orchestrator_logger.info(f"Dispatching background task for job {job_id}")
    orchestrator_logger.info(f"Task args: job_id={job_id}, video_path={video_file_path}, subtitle_path={subtitle_file_path}")
    
    try:
        task_result = process_video_job.apply_async(args=[job_id, video_file_path, subtitle_file_path], queue='default')
        orchestrator_logger.info(f"Task dispatched successfully, task_id: {task_result.id}")
    except Exception as e:
        orchestrator_logger.error(f"Failed to dispatch task: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start processing: {e}")

    orchestrator_logger.info(f"Job {job_id} creation completed successfully")
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


@router.get("/jobs/{job_id}/report")
def get_report(job_id: int, format: str = "md", db: Session = Depends(get_db)):
    """
    Download the generated report for a completed job.
    Supports both 'md' (markdown) and 'pdf' formats.
    """
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != JobStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Job not completed yet")
    
    # Report file paths
    report_dir = os.path.join(SHARED_STORAGE_PATH, str(job_id), "reports")
    
    if format.lower() == "pdf":
        report_path = os.path.join(report_dir, "final_report.pdf")
        media_type = "application/pdf"
        filename = f"video_analysis_report_{job_id}.pdf"
    else:  # default to markdown
        report_path = os.path.join(report_dir, "final_report.md")
        media_type = "text/markdown"
        filename = f"video_analysis_report_{job_id}.md"
    
    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail=f"Report file not found: {format}")
    
    return FileResponse(
        path=report_path,
        media_type=media_type,
        filename=filename
    )

