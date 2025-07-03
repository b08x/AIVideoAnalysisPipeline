# subtitle_processor/main.py
from fastapi import FastAPI

app = FastAPI(title="Subtitle Processing Service")

@app.get("/health")
def health_check():
    """
    Provides a health check endpoint for the service.
    """
    return {"status": "ok", "service": "subtitle-processor"}

# In a more complex scenario, you might add endpoints to test parsing,
# summarization, or topic modeling directly.
