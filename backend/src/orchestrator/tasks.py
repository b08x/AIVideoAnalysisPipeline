# orchestrator/tasks.py
from celery import Celery, chain, group
import time
import os
import random
from sqlalchemy.orm import Session
from orchestrator.models import Job, JobStatus, SessionLocal
from orchestrator.progress_manager import progress_manager
from orchestrator.logging_config import worker_logger, create_job_logger

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
    logger = create_job_logger(job_id, worker_logger)
    logger.info(f"Updating job status to {status}")
    
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            old_status = job.status
            job.status = status
            db.commit()
            logger.info(f"Job status updated: {old_status} -> {status}")
        else:
            logger.error(f"Job not found in database")
    except Exception as e:
        logger.error(f"Error updating job status: {e}")
        db.rollback()
        raise
    finally:
        db.close()


@celery_app.task(name="process_video_job")
def process_video_job(job_id: int, video_path: str, subtitle_path: str):
    """
    Asynchronous task to process a video job with detailed progress monitoring.
    """
    logger = create_job_logger(job_id, worker_logger)
    logger.info(f"=== STARTING VIDEO PROCESSING JOB ===")
    logger.info(f"Video path: {video_path}")
    logger.info(f"Subtitle path: {subtitle_path}")
    
    try:
        # Update job status to processing
        logger.info("Updating job status to PROCESSING")
        update_job_status(job_id, JobStatus.PROCESSING)
        
        # Send initial progress
        logger.info("Sending initialization progress")
        progress_manager.send_stage_start(
            job_id, "initialization", 
            "Starting video analysis pipeline"
        )
        
        # Verify files exist
        logger.info("Verifying input files exist")
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        if not os.path.exists(subtitle_path):
            raise FileNotFoundError(f"Subtitle file not found: {subtitle_path}")
        
        logger.info(f"Video file size: {os.path.getsize(video_path)} bytes")
        logger.info(f"Subtitle file size: {os.path.getsize(subtitle_path)} bytes")

        # For now, let's use a simplified approach with actual processing
        # We'll simulate real processing but with actual data structures
        
        # Stage 1: Process subtitles (parsing, summarizing, topic modeling)
        logger.info("=== STAGE 1: SUBTITLE PROCESSING ===")
        progress_manager.send_stage_start(
            job_id, "subtitle_processing", 
            "Parsing and analyzing subtitle content"
        )
        
        try:
            # Import and use actual subtitle processing functions
            from subtitle_processor.parsers import parse_subtitles
            from subtitle_processor.summarizer import summarize_text
            from subtitle_processor.topic_extractor import extract_topics
            
            # Step 1: Read and parse subtitle file
            progress_manager.send_step_progress(
                job_id, "subtitle_processing", "parsing", 1, 4,
                {"description": "Reading subtitle file"}
            )
            
            with open(subtitle_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            utterances = parse_subtitles(subtitle_path, content)
            
            progress_manager.send_step_progress(
                job_id, "subtitle_processing", "parsing", 2, 4,
                {"description": f"Parsed {len(utterances)} utterances"}
            )
            
            # Step 2: Summarize utterances (add summary to each utterance)
            progress_manager.send_step_progress(
                job_id, "subtitle_processing", "summarizing", 3, 4,
                {"description": f"Summarizing {len(utterances)} utterances"}
            )
            
            for i, utterance in enumerate(utterances):
                try:
                    utterance.summary = summarize_text(utterance.text)
                    if i % max(1, len(utterances) // 10) == 0:  # Update every 10%
                        progress_manager.send_step_progress(
                            job_id, "subtitle_processing", "summarizing", 3, 4,
                            {"description": f"Summarized {i+1}/{len(utterances)} utterances"}
                        )
                except Exception as e:
                    print(f"Failed to summarize utterance: {e}")
                    utterance.summary = None
            
            # Step 3: Extract topics
            progress_manager.send_step_progress(
                job_id, "subtitle_processing", "topic_extraction", 4, 4,
                {"description": "Extracting topics using AI clustering"}
            )
            
            topics = extract_topics(utterances)
            
            subtitle_result = {
                "utterances": [u.__dict__ for u in utterances],
                "topics": [t.__dict__ for t in topics]
            }
            
            progress_manager.send_stage_complete(
                job_id, "subtitle_processing", 
                {"utterances_count": len(utterances), "topics_count": len(topics)}
            )
            
            print(f"Job {job_id}: Completed stage 'subtitle_processing' - Found {len(utterances)} utterances, {len(topics)} topics")
        except Exception as e:
            progress_manager.send_error(job_id, "subtitle_processing", str(e))
            print(f"Job {job_id}: Error in subtitle_processing: {e}")
            subtitle_result = {"utterances": [], "topics": []}
        
        # Stage 2: Validate video
        progress_manager.send_stage_start(
            job_id, "video_validation", 
            "Validating video format, duration, and resolution"
        )
        
        try:
            from video_processor.validator import VideoValidator
            
            progress_manager.send_step_progress(
                job_id, "video_validation", "format_check", 1, 3,
                {"description": "Checking video format compatibility"}
            )
            
            validator = VideoValidator(video_path)
            is_valid = validator.validate()
            error_msg = validator.get_error() if not is_valid else None
            
            progress_manager.send_step_progress(
                job_id, "video_validation", "validation_complete", 3, 3,
                {"description": f"Video validation {'passed' if is_valid else 'failed'}"}
            )
            
            validation_result = {"valid": is_valid, "error": error_msg}
            
            progress_manager.send_stage_complete(
                job_id, "video_validation", 
                {"is_valid": is_valid, "error": error_msg}
            )
            
            print(f"Job {job_id}: Completed stage 'video_validation' - Valid: {is_valid}")
        except Exception as e:
            progress_manager.send_error(job_id, "video_validation", str(e))
            print(f"Job {job_id}: Error in video_validation: {e}")
            validation_result = {"valid": False, "error": str(e)}
        
        # Stage 3: Extract frames from video  
        progress_manager.send_stage_start(
            job_id, "frame_extraction", 
            "Extracting keyframes for visual analysis"
        )
        
        try:
            from video_processor.frame_extractor import FrameExtractor
            
            progress_manager.send_step_progress(
                job_id, "frame_extraction", "setup", 1, 3,
                {"description": "Setting up frame extraction"}
            )
            
            output_dir = os.path.join('/shared', str(job_id), 'frames')
            os.makedirs(output_dir, exist_ok=True)
            
            progress_manager.send_step_progress(
                job_id, "frame_extraction", "extracting", 2, 3,
                {"description": "Extracting keyframes from video"}
            )
            
            extractor = FrameExtractor(video_path, output_dir)
            frame_paths = extractor.extract_keyframes()
            
            progress_manager.send_step_progress(
                job_id, "frame_extraction", "complete", 3, 3,
                {"description": f"Extracted {len(frame_paths)} keyframes"}
            )
            
            frame_result = {"frame_paths": frame_paths}
            
            progress_manager.send_stage_complete(
                job_id, "frame_extraction", 
                {"frames_extracted": len(frame_paths)}
            )
            
            print(f"Job {job_id}: Completed stage 'frame_extraction' - Extracted {len(frame_paths)} frames")
        except Exception as e:
            progress_manager.send_error(job_id, "frame_extraction", str(e))
            print(f"Job {job_id}: Error in frame_extraction: {e}")
            frame_result = {"frame_paths": []}
        
        # Stage 4: Analyze frames with vision AI
        progress_manager.send_stage_start(
            job_id, "visual_analysis", 
            "Analyzing frames with AI vision models"
        )
        
        try:
            from vision_analyzer.analyzer import process_single_frame
            frame_paths = frame_result.get('frame_paths', [])
            
            if frame_paths:
                # Limit to first 5 frames for demo to avoid long processing times
                frames_to_analyze = frame_paths[:5]
                analyses = []
                
                progress_manager.send_step_progress(
                    job_id, "visual_analysis", "setup", 1, len(frames_to_analyze) + 2,
                    {"description": f"Preparing to analyze {len(frames_to_analyze)} frames"}
                )
                
                for i, frame_path in enumerate(frames_to_analyze):
                    progress_manager.send_step_progress(
                        job_id, "visual_analysis", f"analyzing_frame_{i+1}", i + 2, len(frames_to_analyze) + 2,
                        {"description": f"Analyzing frame {i+1}/{len(frames_to_analyze)}", "frame_path": frame_path}
                    )
                    
                    context = f"Frame {i+1} from video analysis"
                    analysis = process_single_frame(frame_path, context)
                    analyses.append(analysis.__dict__ if hasattr(analysis, '__dict__') else analysis)
                
                progress_manager.send_step_progress(
                    job_id, "visual_analysis", "complete", len(frames_to_analyze) + 2, len(frames_to_analyze) + 2,
                    {"description": f"Completed analysis of {len(analyses)} frames"}
                )
                
                vision_result = {"analyses": analyses}
                
                progress_manager.send_stage_complete(
                    job_id, "visual_analysis", 
                    {"frames_analyzed": len(analyses), "total_frames": len(frame_paths)}
                )
                
                print(f"Job {job_id}: Completed stage 'visual_analysis' - Analyzed {len(analyses)} frames")
            else:
                vision_result = {"analyses": []}
                
                progress_manager.send_stage_complete(
                    job_id, "visual_analysis", 
                    {"frames_analyzed": 0, "reason": "No frames available"}
                )
                
                print(f"Job {job_id}: Completed stage 'visual_analysis' - No frames to analyze")
        except Exception as e:
            progress_manager.send_error(job_id, "visual_analysis", str(e))
            print(f"Job {job_id}: Error in visual_analysis: {e}")
            vision_result = {"analyses": []}
        
        # Stage 5: Generate final report
        progress_manager.send_stage_start(
            job_id, "report_generation", 
            "Generating comprehensive analysis report"
        )
        
        try:
            from documentation.generator import ReportGenerator
            
            progress_manager.send_step_progress(
                job_id, "report_generation", "setup", 1, 4,
                {"description": "Setting up report generator"}
            )
            
            generator = ReportGenerator()
            
            progress_manager.send_step_progress(
                job_id, "report_generation", "aggregating", 2, 4,
                {"description": "Aggregating analysis data"}
            )
            
            aggregated_data = {
                'job_id': job_id,
                'subtitle_analysis': subtitle_result,
                'video_validation': validation_result,
                'frame_extractions': frame_result,
                'visual_analysis': vision_result
            }
            
            output_dir = os.path.join('/shared', str(job_id), 'reports')
            os.makedirs(output_dir, exist_ok=True)
            
            progress_manager.send_step_progress(
                job_id, "report_generation", "generating", 3, 4,
                {"description": "Generating report content"}
            )
            
            # Generate report content
            report_content = generator.generate(job_id, aggregated_data)
            
            # Save markdown report
            md_path = os.path.join(output_dir, 'final_report.md')
            generator.save_report(report_content, md_path)
            
            progress_manager.send_step_progress(
                job_id, "report_generation", "saving", 4, 4,
                {"description": f"Report saved to {md_path}"}
            )
            
            report_result = {"markdown_path": md_path, "content": report_content}
            
            progress_manager.send_stage_complete(
                job_id, "report_generation", 
                {"report_path": md_path, "report_size": len(report_content)}
            )
            
            print(f"Job {job_id}: Completed stage 'report_generation' - Generated report at {md_path}")
        except Exception as e:
            progress_manager.send_error(job_id, "report_generation", str(e))
            print(f"Job {job_id}: Error in report_generation: {e}")
            report_result = {"error": str(e)}

        # Update job status to completed and send final completion message
        update_job_status(job_id, JobStatus.COMPLETED)
        
        progress_manager.send_completion(job_id, {
            "total_stages_completed": 5,
            "subtitle_analysis": subtitle_result,
            "video_validation": validation_result,
            "frame_extraction": frame_result,
            "visual_analysis": vision_result,
            "report_generation": report_result
        })
        
        print(f"Finished processing for job_id: {job_id}")
        return {"status": "completed", "job_id": job_id}
        
    except Exception as e:
        print(f"Error processing job {job_id}: {e}")
        update_job_status(job_id, JobStatus.FAILED)
        raise

