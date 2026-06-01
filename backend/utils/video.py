"""Video loading and frame extraction utilities."""
import cv2
from pathlib import Path


def load_video(path: str | Path):
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise IOError(f"Cannot open video: {path}")
    return cap


def extract_frames(cap, skip: int = 1):
    """Yields every `skip`-th frame from a VideoCapture."""
    idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if idx % skip == 0:
            yield frame
        idx += 1
