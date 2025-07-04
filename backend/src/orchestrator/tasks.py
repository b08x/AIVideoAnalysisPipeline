# orchestrator/tasks.py
from celery import Celery, chain, group
import time
import os
import random
from sqlalchemy.orm import Session
from orchestrator.models import Job, JobStatus, SessionLocal

# Import actual processing services
from subtitle_processor.tasks import process_subtitles
from video_processor.tasks import validate_video, segment_video, extract_frames
from vision_analyzer.tasks import batch_analyze_frames
from documentation.tasks import generate_report

# Celery configuration using Redis as the broker
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
celery_app = Celery("tasks", broker=REDIS_URL, backend=REDIS_URL)


def update_job_status(job_id: int, status: JobStatus):
    """Update job status in database"""
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.status = status
            db.commit()
            print(f"Updated job {job_id} status to {status}")
        else:
            print(f"Job {job_id} not found in database")
    except Exception as e:
        print(f"Error updating job {job_id} status: {e}")
        db.rollback()
    finally:
        db.close()


@celery_app.task(name="process_video_job")
def process_video_job(job_id: int, video_path: str, subtitle_path: str):
    """
    Asynchronous task to process a video job.
    This is a placeholder for the actual multi-stage processing logic.
    """
    print(f"Starting processing for job_id: {job_id}")
    
    try:
        # Update job status to processing
        update_job_status(job_id, JobStatus.PROCESSING)

        # For now, let's use a simplified approach with actual processing
        # We'll simulate real processing but with actual data structures
        
        # Stage 1: Process subtitles (parsing, summarizing, topic modeling)
        print(f"Job {job_id}: Starting stage 'subtitle_processing'")
        try:
            # Import and use actual subtitle processing functions
            from subtitle_processor.parsers import parse_subtitles
            from subtitle_processor.summarizer import summarize_text
            from subtitle_processor.topic_extractor import extract_topics
            
            # Read and parse subtitle file
            with open(subtitle_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            utterances = parse_subtitles(subtitle_path, content)
            
            # Summarize utterances (add summary to each utterance)
            for utterance in utterances:
                try:
                    utterance.summary = summarize_text(utterance.text)
                except Exception as e:
                    print(f"Failed to summarize utterance: {e}")
                    utterance.summary = None
            
            # Extract topics
            topics = extract_topics(utterances)
            
            subtitle_result = {
                "utterances": [u.__dict__ for u in utterances],
                "topics": [t.__dict__ for t in topics]
            }
            print(f"Job {job_id}: Completed stage 'subtitle_processing' - Found {len(utterances)} utterances, {len(topics)} topics")
        except Exception as e:
            print(f"Job {job_id}: Error in subtitle_processing: {e}")
            subtitle_result = {"utterances": [], "topics": []}
        
        # Stage 2: Validate video
        print(f"Job {job_id}: Starting stage 'video_validation'")
        try:
            from video_processor.validator import VideoValidator
            validator = VideoValidator(video_path)
            is_valid = validator.validate()
            error_msg = validator.get_error() if not is_valid else None
            validation_result = {"valid": is_valid, "error": error_msg}
            print(f"Job {job_id}: Completed stage 'video_validation' - Valid: {is_valid}")
        except Exception as e:
            print(f"Job {job_id}: Error in video_validation: {e}")
            validation_result = {"valid": False, "error": str(e)}
        
        # Stage 3: Extract frames from video  
        print(f"Job {job_id}: Starting stage 'frame_extraction'")
        try:
            from video_processor.frame_extractor import FrameExtractor
            output_dir = os.path.join('/shared', str(job_id), 'frames')
            os.makedirs(output_dir, exist_ok=True)
            extractor = FrameExtractor(video_path, output_dir)
            frame_paths = extractor.extract_keyframes()
            frame_result = {"frame_paths": frame_paths}
            print(f"Job {job_id}: Completed stage 'frame_extraction' - Extracted {len(frame_paths)} frames")
        except Exception as e:
            print(f"Job {job_id}: Error in frame_extraction: {e}")
            frame_result = {"frame_paths": []}
        
        # Stage 4: Analyze frames with vision AI
        print(f"Job {job_id}: Starting stage 'visual_analysis'")
        try:
            from vision_analyzer.analyzer import process_single_frame
            frame_paths = frame_result.get('frame_paths', [])
            
            if frame_paths:
                analyses = []
                for i, frame_path in enumerate(frame_paths[:5]):  # Limit to first 5 frames for demo
                    context = f"Frame {i+1} from video analysis"
                    analysis = process_single_frame(frame_path, context)
                    analyses.append(analysis.__dict__ if hasattr(analysis, '__dict__') else analysis)
                vision_result = {"analyses": analyses}
                print(f"Job {job_id}: Completed stage 'visual_analysis' - Analyzed {len(analyses)} frames")
            else:
                vision_result = {"analyses": []}
                print(f"Job {job_id}: Completed stage 'visual_analysis' - No frames to analyze")
        except Exception as e:
            print(f"Job {job_id}: Error in visual_analysis: {e}")
            vision_result = {"analyses": []}
        
        # Stage 5: Generate final report
        print(f"Job {job_id}: Starting stage 'report_generation'")
        try:
            from documentation.generator import ReportGenerator
            generator = ReportGenerator()
            
            aggregated_data = {
                'job_id': job_id,
                'subtitle_analysis': subtitle_result,
                'video_validation': validation_result,
                'frame_extractions': frame_result,
                'visual_analysis': vision_result
            }
            
            output_dir = os.path.join('/shared', str(job_id), 'reports')
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate report content
            report_content = generator.generate(job_id, aggregated_data)
            
            # Save markdown report
            md_path = os.path.join(output_dir, 'final_report.md')
            generator.save_report(report_content, md_path)
            
            report_result = {"markdown_path": md_path, "content": report_content}
            print(f"Job {job_id}: Completed stage 'report_generation' - Generated report at {md_path}")
        except Exception as e:
            print(f"Job {job_id}: Error in report_generation: {e}")
            report_result = {"error": str(e)}

        # Update job status to completed
        update_job_status(job_id, JobStatus.COMPLETED)
        print(f"Finished processing for job_id: {job_id}")
        return {"status": "completed", "job_id": job_id}
        
    except Exception as e:
        print(f"Error processing job {job_id}: {e}")
        update_job_status(job_id, JobStatus.FAILED)
        raise

