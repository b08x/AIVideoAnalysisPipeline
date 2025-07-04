# video_processor/main.py
from fastapi import FastAPI

app = FastAPI(title="Video Processing Service")

@app.get("/health")
def health_check():
    """
    Provides a health check endpoint for the service.
    """
    return {"status": "ok", "service": "video-processor"}
