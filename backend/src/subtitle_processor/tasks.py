# subtitle_processor/tasks.py
import os
from celery import Celery
from subtitle_processor.parsers import parse_subtitles
from subtitle_processor.summarizer import summarize_text
from subtitle_processor.topic_extractor import extract_topics
from subtitle_processor.models import SubtitleAnalysisResult

# Celery configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
celery_app = Celery("subtitle_tasks", broker=REDIS_URL, backend=REDIS_URL)

@celery_app.task(name="process_subtitles")
def process_subtitles(job_id: int, file_path: str):
    """
    A Celery task that orchestrates the entire subtitle processing pipeline.
    """
    print(f"Job {job_id}: Starting subtitle processing for {file_path}")
    
    # In a real system, you would use a shared volume (e.g., MinIO) to get the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Parse Subtitles
    # self.update_state(state='PROGRESS', meta={'current': 10, 'total': 100, 'status': 'Parsing subtitles...'})
    utterances = parse_subtitles(file_path, content)
    
    # 2. Summarize Utterances (can be done in parallel)
    # self.update_state(state='PROGRESS', meta={'current': 40, 'total': 100, 'status': 'Summarizing utterances...'})
    for u in utterances:
        u.summary = summarize_text(u.text)

    # 3. Extract Topics
    # self.update_state(state='PROGRESS', meta={'current': 80, 'total': 100, 'status': 'Extracting topics...'})
    topics = extract_topics(utterances)

    # self.update_state(state='SUCCESS', meta={'current': 100, 'total': 100, 'status': 'Completed'})
    
    result = SubtitleAnalysisResult(utterances=utterances, topics=topics)
    
    print(f"Job {job_id}: Finished subtitle processing.")
    
    # Return result as a dictionary for JSON serialization
    return result.model_dump()

