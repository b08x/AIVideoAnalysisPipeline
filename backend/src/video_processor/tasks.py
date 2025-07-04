# video_processor/tasks.py
import os
from celery import Celery
from video_processor.validator import VideoValidator
from video_processor.segmenter import VideoSegmenter
from video_processor.frame_extractor import FrameExtractor

# Celery configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
celery_app = Celery("video_tasks", broker=REDIS_URL, backend=REDIS_URL)

@celery_app.task(name="validate_video")
def validate_video(job_id: int, file_path: str):
    """Validates a video file."""
    print(f"Job {job_id}: Validating video {file_path}")
    validator = VideoValidator(file_path)
    if not validator.validate():
        error = validator.get_error()
        print(f"Job {job_id}: Validation failed - {error}")
        # In a real system, you'd update the job status to 'failed'
        raise ValueError(error)
    print(f"Job {job_id}: Video validation successful.")
    return {"status": "validated", "file_path": file_path}

@celery_app.task(name="segment_video")
def segment_video(job_id: int, file_path: str, time_boundaries: list):
    """Segments a video based on time boundaries."""
    output_dir = f"/shared/{job_id}/segments"
    print(f"Job {job_id}: Segmenting video {file_path} into {output_dir}")
    segmenter = VideoSegmenter(file_path, output_dir)
    segment_paths = segmenter.segment_by_times(time_boundaries)
    print(f"Job {job_id}: Video segmentation completed.")
    return {"status": "segmented", "segment_paths": segment_paths}

@celery_app.task(name="extract_frames")
def extract_frames(job_id: int, video_path: str):
    """Extracts keyframes from a video."""
    output_dir = f"/shared/{job_id}/frames"
    print(f"Job {job_id}: Extracting frames from {video_path} into {output_dir}")
    extractor = FrameExtractor(video_path, output_dir)
    keyframe_paths = extractor.extract_keyframes()
    print(f"Job {job_id}: Frame extraction completed.")
    return {"status": "frames_extracted", "keyframe_paths": keyframe_paths}
