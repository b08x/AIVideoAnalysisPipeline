# video_processor/utils.py
import cv2
import os

def create_thumbnail(image_path: str, output_dir: str, size: tuple = (320, 180)) -> str:
    """
    Creates a thumbnail for a given image.

    Args:
        image_path: Path to the source image.
        output_dir: Directory to save the thumbnail.
        size: A tuple representing the (width, height) of the thumbnail.

    Returns:
        The file path of the generated thumbnail.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Could not read image file: {image_path}")

    thumbnail = cv2.resize(img, size, interpolation=cv2.INTER_AREA)
    
    base_filename = os.path.basename(image_path)
    name, ext = os.path.splitext(base_filename)
    thumb_filename = f"{name}_thumb{ext}"
    thumb_path = os.path.join(output_dir, thumb_filename)
    
    os.makedirs(output_dir, exist_ok=True)
    cv2.imwrite(thumb_path, thumbnail)
    
    return thumb_path

def get_video_metadata(video_path: str) -> dict:
    """
    Extracts basic metadata from a video file.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {"error": "Could not open video file."}
    
    metadata = {
        "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        "fps": cap.get(cv2.CAP_PROP_FPS),
        "frame_count": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
        "duration_seconds": cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
    }
    cap.release()
    return metadata
