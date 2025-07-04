# vision_analyzer/ui_detector.py
import easyocr
import numpy as np
from typing import List
from vision_analyzer.models import DetectedElement

class UIDetector:
    """
    Detects UI elements and text in an image using OCR.
    """
    def __init__(self, languages: List[str] = ['en']):
        # This will download the model on the first run.
        # It's recommended to have this pre-downloaded in the Docker image.
        self.reader = easyocr.Reader(languages, gpu=False) # Set gpu=True if a GPU is available

    def detect(self, image_path: str) -> List[DetectedElement]:
        """
        Performs OCR on the given image and returns a list of detected text elements.
        
        Args:
            image_path: The file path to the image to be analyzed.

        Returns:
            A list of DetectedElement objects.
        """
        try:
            # The detail=1 parameter provides bounding box information
            ocr_results = self.reader.readtext(image_path, detail=1)
        except Exception as e:
            print(f"Error during OCR processing for {image_path}: {e}")
            return []

        detected_elements = []
        for (bbox, text, confidence) in ocr_results:
            # The bbox from easyocr is a list of 4 points (top-left, top-right, bottom-right, bottom-left)
            # We convert it to a simpler (x1, y1, x2, y2) format.
            top_left = bbox[0]
            bottom_right = bbox[2]
            simple_bbox = (int(top_left[0]), int(top_left[1]), int(bottom_right[0]), int(bottom_right[1]))

            # Basic classification logic can be expanded here.
            # For now, we'll classify everything as 'text'.
            element_type = "text" # TODO: Add logic to classify buttons, inputs etc.

            detected_elements.append(DetectedElement(
                type=element_type,
                content=text,
                bounding_box=simple_bbox,
                confidence=confidence
            ))
            
        return detected_elements

