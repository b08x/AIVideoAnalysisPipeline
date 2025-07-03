# subtitle_processor/models.py
from pydantic import BaseModel, Field
from typing import List, Optional

class Utterance(BaseModel):
    """
    Represents a single utterance from a subtitle file,
    including timing, text, and an optional summary.
    """
    start_time: float = Field(..., description="Start time of the utterance in seconds.")
    end_time: float = Field(..., description="End time of the utterance in seconds.")
    text: str = Field(..., description="The text content of the utterance.")
    summary: Optional[str] = Field(None, description="A brief summary of the utterance.")

class Topic(BaseModel):
    """
    Represents a topic derived from a cluster of utterances.
    """
    topic_id: int = Field(..., description="Unique identifier for the topic.")
    topic_name: str = Field(..., description="A concise name for the topic.")
    utterance_indices: List[int] = Field(..., description="List of indices of utterances belonging to this topic.")
    summary: Optional[str] = Field(None, description="A summary of the entire topic.")

class SubtitleAnalysisResult(BaseModel):
    """
    A container for the full analysis result of a subtitle file.
    """
    utterances: List[Utterance]
    topics: List[Topic]

