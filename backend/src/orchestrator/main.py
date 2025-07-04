# orchestrator/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from orchestrator.api import jobs, websocket
from orchestrator.models import create_db_and_tables
import os

# Create the FastAPI app
app = FastAPI(title="Video RAG Orchestrator")

# Configure CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:80")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(jobs.router, prefix="/api/v1", tags=["Jobs"])
app.include_router(websocket.router, prefix="/ws", tags=["Progress"])



@app.on_event("startup")
def on_startup():
    """
    Event handler for application startup.
    Creates database tables if they don't exist.
    """
    print("Starting up orchestrator service...")
    create_db_and_tables()
    print("Database tables verified.")


@app.get("/health", tags=["Health"])
def health_check():
    """
    Health check endpoint to verify the service is running.
    """
    return {"status": "ok"}

