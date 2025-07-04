# video_processor/validator.py
import cv2
from typing import Tuple, Optional

# Supported video formats and their fourcc codes
SUPPORTED_FORMATS = {
    "mp4": cv2.VideoWriter_fourcc(*'mp4v'),
    "webm": cv2.VideoWriter_fourcc(*'VP90'),
    "mkv": cv2.VideoWriter_fourcc(*'X264'),
    "avi": cv2.VideoWriter_fourcc(*'DIVX'),
}

class VideoValidator:
    """
    A class to validate video files based on format, duration, and resolution.
    """
    def __init__(self, file_path: str, max_duration: int = 3600, min_resolution: Tuple[int, int] = (640, 480)):
        self.file_path = file_path
        self.max_duration = max_duration  # in seconds
        self.min_resolution = min_resolution
        self.error = None
        self.cap = cv2.VideoCapture(self.file_path)
        if not self.cap.isOpened():
            self.error = "Failed to open video file."

    def validate(self) -> bool:
        """
        Runs all validation checks on the video file.
        """
        if self.error:
            return False
        
        checks = [
            self._check_format,
            self._check_duration,
            self._check_resolution,
        ]
        
        for check in checks:
            if not check():
                self.cap.release()
                return False
        
        self.cap.release()
        return True

    def _check_format(self) -> bool:
        """Checks if the video format is supported."""
        # This is a basic check; a more robust check might involve ffprobe
        file_extension = self.file_path.split('.')[-1].lower()
        if file_extension not in SUPPORTED_FORMATS:
            self.error = f"Unsupported video format: .{file_extension}"
            return False
        return True

    def _check_duration(self) -> bool:
        """Checks if the video duration is within the allowed limit."""
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if fps > 0 and frame_count > 0:
            duration = frame_count / fps
            if duration > self.max_duration:
                self.error = f"Video duration ({duration:.0f}s) exceeds the maximum limit of {self.max_duration}s."
                return False
        return True

    def _check_resolution(self) -> bool:
        """Checks if the video resolution meets the minimum requirements."""
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if width < self.min_resolution[0] or height < self.min_resolution[1]:
            self.error = f"Video resolution ({width}x{height}) is below the minimum of {self.min_resolution[0]}x{self.min_resolution[1]}."
            return False
        return True

    def get_error(self) -> Optional[str]:
        return self.error

