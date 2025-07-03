# video_processor/segmenter.py
import os
import subprocess
from typing import List, Tuple

class VideoSegmenter:
    """
    Segments a video file into multiple smaller clips using FFmpeg.
    """
    def __init__(self, input_path: str, output_dir: str):
        self.input_path = input_path
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def segment_by_times(self, time_boundaries: List[Tuple[float, float]]) -> List[str]:
        """
        Segments the video based on a list of (start_time, end_time) tuples.

        Args:
            time_boundaries: A list of tuples, where each tuple contains the
                             start and end time in seconds for a segment.

        Returns:
            A list of file paths to the created segments.
        """
        output_paths = []
        for i, (start, end) in enumerate(time_boundaries):
            output_filename = f"segment_{i+1}.mp4"
            output_path = os.path.join(self.output_dir, output_filename)
            
            # FFmpeg command to cut the video without re-encoding for speed
            cmd = [
                'ffmpeg',
                '-i', self.input_path,
                '-ss', str(start),
                '-to', str(end),
                '-c', 'copy',  # Copy codecs to avoid re-encoding
                '-y',          # Overwrite output file if it exists
                output_path
            ]
            
            try:
                # Using subprocess.run for simplicity. For production, consider
                # more robust handling of stdout/stderr and error checking.
                subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output_paths.append(output_path)
                print(f"Successfully created segment: {output_path}")
            except subprocess.CalledProcessError as e:
                print(f"Error creating segment {i+1}: {e.stderr.decode()}")
                # Decide if you want to continue or raise the exception
                # raise e 
        
        return output_paths

