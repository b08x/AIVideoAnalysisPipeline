# orchestrator/tasks.py
from celery import Celery
import time
import os
import random

# Celery configuration using Redis as the broker
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
celery_app = Celery("tasks", broker=REDIS_URL, backend=REDIS_URL)


@celery_app.task(name="process_video_job")
def process_video_job(job_id: int, video_path: str, subtitle_path: str):
    """
    Asynchronous task to process a video job.
    This is a placeholder for the actual multi-stage processing logic.
    """
    print(f"Starting processing for job_id: {job_id}")

    # Simulate a multi-stage process
    stages = [
        "parsing_subtitles",
        "summarizing_utterances",
        "topic_modeling",
        "video_segmentation",
        "frame_extraction",
        "visual_analysis",
        "report_generation",
    ]

    for stage in stages:
        print(f"Job {job_id}: Starting stage '{stage}'")
        # Here you would call other services/tasks
        time.sleep(random.randint(5, 15))  # Simulate work
        print(f"Job {job_id}: Completed stage '{stage}'")

    print(f"Finished processing for job_id: {job_id}")
    return {"status": "completed", "job_id": job_id}

