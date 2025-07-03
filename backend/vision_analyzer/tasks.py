# vision_analyzer/tasks.py
import os
from celery import Celery, group
from analyzer import process_single_frame

# Celery configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
celery_app = Celery("vision_tasks", broker=REDIS_URL, backend=REDIS_URL)

@celery_app.task(name="analyze_frame")
def analyze_frame(job_id: int, frame_path: str, contextual_text: str):
    """
    Celery task to analyze a single video frame.
    """
    print(f"Job {job_id}: Analyzing frame {frame_path}")
    analysis_result = process_single_frame(frame_path, contextual_text)
    print(f"Job {job_id}: Finished analyzing frame {frame_path}")
    return analysis_result.model_dump() # Return as dict for JSON serialization

@celery_app.task(name="batch_analyze_frames")
def batch_analyze_frames(job_id: int, frame_paths: list, contexts: list):
    """
    Analyzes a batch of frames in parallel using a Celery group.
    """
    if len(frame_paths) != len(contexts):
        raise ValueError("The number of frame paths must match the number of contexts.")

    # Create a group of parallel tasks
    analysis_group = group(
        analyze_frame.s(job_id, frame_path, context)
        for frame_path, context in zip(frame_paths, contexts)
    )

    # Execute the group and get the results
    result_group = analysis_group.apply_async()
    
    # You can wait for the results if needed, or handle them asynchronously
    # collected_results = result_group.get()
    # return collected_results
    
    return {"status": "batch_analysis_started", "task_group_id": result_group.id}

