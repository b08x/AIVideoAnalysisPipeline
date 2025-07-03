#!/usr/bin/env python3
"""
Consolidated AI Video Analysis Backend
A simplified FastAPI application that combines all services into one.
"""

import os
import shutil
import sqlite3
import json
import tempfile
from typing import Dict, List, Optional
from datetime import datetime
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Global configuration
UPLOAD_DIR = "/tmp/video_analysis"
DB_PATH = "/tmp/video_analysis.db"

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Data models
class JobStatus(BaseModel):
    job_id: str
    status: str  # pending, processing, completed, failed
    message: str
    created_at: str
    video_filename: Optional[str] = None
    subtitle_filename: Optional[str] = None
    progress: int = 0
    results: Optional[Dict] = None

class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str

# Database setup
def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            status TEXT NOT NULL,
            message TEXT,
            created_at TEXT NOT NULL,
            video_filename TEXT,
            subtitle_filename TEXT,
            progress INTEGER DEFAULT 0,
            results TEXT  -- JSON string
        )
    ''')
    
    conn.commit()
    conn.close()

def get_job_from_db(job_id: str) -> Optional[JobStatus]:
    """Get job from database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM jobs WHERE id = ?', (job_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return JobStatus(
            job_id=row[0],
            status=row[1],
            message=row[2],
            created_at=row[3],
            video_filename=row[4],
            subtitle_filename=row[5],
            progress=row[6],
            results=json.loads(row[7]) if row[7] else None
        )
    return None

def save_job_to_db(job: JobStatus):
    """Save job to database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO jobs 
        (id, status, message, created_at, video_filename, subtitle_filename, progress, results)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        job.job_id,
        job.status,
        job.message,
        job.created_at,
        job.video_filename,
        job.subtitle_filename,
        job.progress,
        json.dumps(job.results) if job.results else None
    ))
    
    conn.commit()
    conn.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    print("🚀 Simplified AI Video Analysis Backend started!")
    print(f"📁 Upload directory: {UPLOAD_DIR}")
    print(f"🗄️  Database: {DB_PATH}")
    yield
    # Shutdown
    print("🔥 Shutting down simplified backend")

# Initialize FastAPI app
app = FastAPI(
    title="AI Video Analysis Pipeline - Simplified", 
    description="Consolidated backend for video analysis",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
@app.get("/api/v1/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "simplified-video-analysis"}

# Job creation endpoint
@app.post("/api/v1/jobs")
async def create_job(
    video: UploadFile = File(...),
    subtitle: UploadFile = File(...),
    config: str = Form(default='{"model": "gemini-2.5-flash", "temperature": 0.7}')
):
    """Create a new video analysis job"""
    
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    
    try:
        # Validate file sizes (basic)
        max_video_size = 100 * 1024 * 1024  # 100MB for testing
        max_subtitle_size = 1 * 1024 * 1024   # 1MB
        
        # Save uploaded files
        video_path = os.path.join(UPLOAD_DIR, f"{job_id}_video_{video.filename}")
        subtitle_path = os.path.join(UPLOAD_DIR, f"{job_id}_subtitle_{subtitle.filename}")
        
        # Save video file
        with open(video_path, "wb") as buffer:
            content = await video.read()
            if len(content) > max_video_size:
                raise HTTPException(status_code=413, detail="Video file too large")
            buffer.write(content)
        
        # Save subtitle file  
        with open(subtitle_path, "wb") as buffer:
            content = await subtitle.read()
            if len(content) > max_subtitle_size:
                raise HTTPException(status_code=413, detail="Subtitle file too large")
            buffer.write(content)
        
        # Create job record
        job = JobStatus(
            job_id=job_id,
            status="pending",
            message="Job created successfully - processing will begin shortly",
            created_at=datetime.now().isoformat(),
            video_filename=video.filename,
            subtitle_filename=subtitle.filename,
            progress=0
        )
        
        # Save to database
        save_job_to_db(job)
        
        # TODO: Start actual processing here
        # For now, just mark as completed with mock results
        job.status = "completed"
        job.progress = 100
        job.message = "Analysis completed successfully (mock implementation)"
        job.results = {
            "video_info": {
                "filename": video.filename,
                "size_bytes": len(content),
                "format": "detected_format"
            },
            "subtitle_info": {
                "filename": subtitle.filename,
                "lines_count": "detected_lines"
            },
            "analysis": {
                "topics": ["Topic 1", "Topic 2", "Topic 3"],
                "summary": "This is a mock analysis summary.",
                "key_insights": [
                    "Mock insight 1",
                    "Mock insight 2", 
                    "Mock insight 3"
                ]
            }
        }
        save_job_to_db(job)
        
        return JobResponse(
            job_id=job_id,
            status="completed", 
            message="Job processed successfully (simplified implementation)"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing files: {str(e)}")

# Job status endpoint
@app.get("/api/v1/jobs/{job_id}")
def get_job_status(job_id: str):
    """Get job status and results"""
    job = get_job_from_db(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job

# Job deletion endpoint
@app.delete("/api/v1/jobs/{job_id}")
def delete_job(job_id: str):
    """Delete a job and its files"""
    job = get_job_from_db(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Clean up files
    try:
        if job.video_filename:
            video_path = os.path.join(UPLOAD_DIR, f"{job_id}_video_{job.video_filename}")
            if os.path.exists(video_path):
                os.remove(video_path)
        
        if job.subtitle_filename:
            subtitle_path = os.path.join(UPLOAD_DIR, f"{job_id}_subtitle_{job.subtitle_filename}")
            if os.path.exists(subtitle_path):
                os.remove(subtitle_path)
    except Exception as e:
        print(f"Error cleaning up files: {e}")
    
    # Remove from database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM jobs WHERE id = ?', (job_id,))
    conn.commit()
    conn.close()
    
    return {"message": "Job deleted successfully"}

# List all jobs endpoint
@app.get("/api/v1/jobs")
def list_jobs():
    """List all jobs"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM jobs ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    
    jobs = []
    for row in rows:
        jobs.append({
            "job_id": row[0],
            "status": row[1], 
            "message": row[2],
            "created_at": row[3],
            "video_filename": row[4],
            "subtitle_filename": row[5],
            "progress": row[6]
        })
    
    return {"jobs": jobs}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)