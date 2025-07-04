# documentation/main.py
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

app = FastAPI(title="Documentation Service")

SHARED_STORAGE_PATH = "/shared"

@app.get("/health")
def health_check():
    """
    Provides a health check endpoint for the service.
    """
    return {"status": "ok", "service": "documentation"}

@app.get("/reports/{job_id}/{format}")
def download_report(job_id: int, format: str):
    """
    Allows downloading of a generated report.
    Format can be 'md' or 'pdf'.
    """
    if format not in ["md", "pdf"]:
        raise HTTPException(status_code=400, detail="Invalid format requested. Use 'md' or 'pdf'.")

    file_name = f"final_report.{format}"
    file_path = os.path.join(SHARED_STORAGE_PATH, str(job_id), "reports", file_name)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Report file not found.")

    return FileResponse(path=file_path, filename=file_name, media_type=f"application/{format}")

