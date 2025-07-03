# video_processor/frame_extractor.py
import cv2
import os
import numpy as np
from typing import List

class FrameExtractor:
    """
    Extracts keyframes from a video based on scene change detection.
    """
    def __init__(self, video_path: str, output_dir: str, threshold: float = 30.0):
        self.video_path = video_path
        self.output_dir = output_dir
        self.threshold = threshold  # Threshold for scene change detection
        os.makedirs(self.output_dir, exist_ok=True)
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            raise IOError(f"Cannot open video file: {video_path}")

    def extract_keyframes(self) -> List[str]:
        """
        Extracts frames that are considered keyframes (e.g., at scene changes).
        
        Returns:
            A list of file paths to the extracted keyframes.
        """
        keyframes = []
        last_hist = None
        frame_number = 0
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            # Convert frame to grayscale and calculate histogram
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            current_hist = cv2.calcHist([gray_frame], [0], None, [256], [0, 256])
            cv2.normalize(current_hist, current_hist, 0, 1, cv2.NORM_MINMAX)

            if last_hist is not None:
                # Compare histograms to detect scene change
                diff = cv2.compareHist(last_hist, current_hist, cv2.HISTCMP_BHATTACHARYYA)
                if diff > self.threshold / 100.0: # Normalize threshold
                    frame_path = self._save_frame(frame, frame_number)
                    keyframes.append(frame_path)
            else:
                # Save the very first frame
                frame_path = self._save_frame(frame, frame_number)
                keyframes.append(frame_path)

            last_hist = current_hist
            frame_number += 1
        
        self.cap.release()
        return keyframes

    def _save_frame(self, frame: np.ndarray, frame_number: int) -> str:
        """Saves a single frame to the output directory."""
        timestamp = self.cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
        filename = f"frame_{frame_number}_time_{timestamp:.2f}.jpg"
        output_path = os.path.join(self.output_dir, filename)
        cv2.imwrite(output_path, frame)
        return output_path

