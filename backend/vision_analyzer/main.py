# vision_analyzer/main.py
from fastapi import FastAPI

app = FastAPI(title="Vision Analysis Service")

@app.get("/health")
def health_check():
    """
    Provides a health check endpoint for the service.
    """
    return {"status": "ok", "service": "vision-analyzer"}
