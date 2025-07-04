# orchestrator/models.py
import enum
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Enum,
    JSON,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func
import os

# Database URL from environment variables
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://dev_user:dev_password@postgres:5432/video_processing"
)

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Enum for Job Status
class JobStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# Job Model
class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    video_file_path = Column(String)
    subtitle_file_path = Column(String)
    results = relationship("JobResult", back_populates="job")
    stages = relationship("ProcessingStage", back_populates="job")


# Processing Stage Model
class ProcessingStage(Base):
    __tablename__ = "processing_stages"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    stage_name = Column(String, index=True)
    status = Column(String, default="pending")  # pending, in_progress, completed, failed
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    details = Column(JSON)
    job = relationship("Job", back_populates="stages")


# Job Result Model
class JobResult(Base):
    __tablename__ = "job_results"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    data = Column(JSON)  # To store utterances, topics, final report, etc.
    job = relationship("Job", back_populates="results")


# Function to create database tables
def create_db_and_tables():
    Base.metadata.create_all(bind=engine)

