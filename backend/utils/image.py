"""Image preprocessing, cropping, and sharpening utilities."""
import cv2
import numpy as np


def preprocess(frame, size: tuple[int, int] = (640, 640)):
    return cv2.resize(frame, size)


def crop_player(frame, bbox: tuple[int, int, int, int]):
    x1, y1, x2, y2 = bbox
    return frame[y1:y2, x1:x2]


def sharpen(image):
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    return cv2.filter2D(image, -1, kernel)
