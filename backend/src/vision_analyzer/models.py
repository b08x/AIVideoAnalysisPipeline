# vision_analyzer/models.py
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Tuple

class DetectedElement(BaseModel):
    """
    Represents a single UI element or piece of text detected in a frame.
    """
    type: Literal["text", "button", "input", "image", "icon", "code_block", "diagram"] = Field(..., description="The type of element detected.")
    content: str = Field(..., description="The textual content of the element (from OCR) or a description.")
    bounding_box: Tuple[int, int, int, int] = Field(..., description="The (x1, y1, x2, y2) coordinates of the element.")
    confidence: float = Field(..., description="The confidence score of the detection/OCR.")

class FrameAnalysis(BaseModel):
    """
    Contains the detailed analysis for a single video frame.
    """
    frame_id: str = Field(..., description="Identifier for the frame (e.g., its filename).")
    screen_type: Literal["code_editor", "terminal", "diagram", "webpage", "presentation", "other"] = Field(..., description="The classified type of screen content.")
    description: str = Field(..., description="A detailed textual description of the frame's content.")
    detected_elements: List[DetectedElement] = Field(..., description="A list of UI elements found in the frame.")
    context_relevance_score: float = Field(..., description="A score from 0.0 to 1.0 indicating how relevant the visual content is to the provided textual context.")

class VisualAnalysisResult(BaseModel):
    """
    A wrapper for a batch of frame analysis results.
    """
    job_id: int
    analyses: List[FrameAnalysis]

