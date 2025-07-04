# vision_analyzer/analyzer.py
import os
import base64
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from vision_analyzer.prompts import create_vision_prompt
from vision_analyzer.ui_detector import UIDetector
from vision_analyzer.models import FrameAnalysis

# Initialize the AI client for vision analysis
# Using OpenRouter to potentially access various models like GPT-4V or Claude Vision
client = OpenAI(api_key=os.getenv("OPENROUTER_API_KEY"), base_url="https://openrouter.ai/api/v1")

# Initialize the UI detector with error handling
try:
    ui_detector = UIDetector()
except Exception as e:
    print(f"Warning: Failed to initialize UIDetector: {e}")
    ui_detector = None

def encode_image_to_base64(image_path: str) -> str:
    """Encodes an image file to a base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

@retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(3))
def analyze_frame_with_vision_model(image_path: str, prompt: str, model: str = "google/gemini-pro-vision") -> str:
    """
    Sends a frame and a prompt to a vision model for analysis.
    """
    base64_image = encode_image_to_base64(image_path)
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=1024,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling vision model for {image_path}: {e}")
        raise # Reraise to trigger tenacity retry

def process_single_frame(frame_path: str, contextual_text: str) -> FrameAnalysis:
    """
    Orchestrates the full analysis pipeline for a single frame.
    """
    # 1. Generate a specialized prompt
    prompt = create_vision_prompt(contextual_text)

    # 2. Get AI-powered description from the vision model
    try:
        ai_description = analyze_frame_with_vision_model(frame_path, prompt)
        # TODO: Parse the structured data (screen_type, description, etc.) from the model's response
    except Exception as e:
        ai_description = f"Failed to analyze frame with vision model: {e}"

    # 3. Detect UI elements using local OCR
    if ui_detector is not None:
        detected_elements = ui_detector.detect(frame_path)
    else:
        detected_elements = []

    # 4. Assemble the final analysis object
    # This is a simplified assembly; a real implementation would parse the
    # AI response more carefully to populate all fields.
    frame_analysis = FrameAnalysis(
        frame_id=os.path.basename(frame_path),
        screen_type="other", # Placeholder
        description=ai_description,
        detected_elements=detected_elements,
        context_relevance_score=0.0 # Placeholder
    )

    return frame_analysis

