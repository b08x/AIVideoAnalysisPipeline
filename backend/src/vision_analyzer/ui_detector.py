# vision_analyzer/ui_detector.py
import easyocr
import numpy as np
import os
import shutil
import logging
import signal
from typing import List
from vision_analyzer.models import DetectedElement

# Set up logging
logger = logging.getLogger(__name__)

class UIDetector:
    """
    Detects UI elements and text in an image using OCR.
    """
    def __init__(self, languages: List[str] = ['en']):
        # This will download the model on the first run.
        # It's recommended to have this pre-downloaded in the Docker image.
        logger.info(f"Initializing UIDetector with languages: {languages}")
        self.reader = None
        self.languages = languages
        self._initialize_reader()

    def _initialize_reader(self):
        """Initialize EasyOCR reader with error handling for corrupted models."""
        logger.info("Starting EasyOCR reader initialization...")
        
        try:
            logger.info("Creating EasyOCR Reader (this may download models on first run)...")
            self.reader = easyocr.Reader(self.languages, gpu=False) # Set gpu=True if a GPU is available
            logger.info("EasyOCR reader initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing EasyOCR reader: {e}")
            # Try to clear the model cache and retry
            try:
                logger.warning("Attempting to clear EasyOCR model cache...")
                # Clear the EasyOCR model cache directory
                cache_dir = os.path.expanduser('~/.EasyOCR')
                if os.path.exists(cache_dir):
                    logger.info(f"Removing EasyOCR cache directory: {cache_dir}")
                    shutil.rmtree(cache_dir)
                    logger.info("EasyOCR cache cleared, retrying initialization...")
                    self.reader = easyocr.Reader(self.languages, gpu=False)
                    logger.info("EasyOCR reader initialized successfully after cache clear")
                else:
                    logger.info("EasyOCR cache directory not found, retrying initialization...")
                    self.reader = easyocr.Reader(self.languages, gpu=False)
                    logger.info("EasyOCR reader initialized successfully on retry")
            except Exception as retry_error:
                logger.error(f"Failed to initialize EasyOCR reader even after cache clear: {retry_error}")
                logger.warning("Disabling OCR functionality for this session")
                self.reader = None

    def detect(self, image_path: str) -> List[DetectedElement]:
        """
        Performs OCR on the given image and returns a list of detected text elements.
        
        Args:
            image_path: The file path to the image to be analyzed.

        Returns:
            A list of DetectedElement objects.
        """
        # Check if reader is initialized
        if self.reader is None:
            print(f"EasyOCR reader not initialized, skipping OCR for {image_path}")
            return []
            
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

