# ocr.py: what is their jersey number?
# player crop -> zoom into torso region -> scale up to 2.5x -> sharpen -> EasyOCR reads it -> "10"
# tries color, normal threshold, and inverted threshold to handle all kit styles
# uses majority voting across last 30 frames per player

import cv2
import numpy as np
import easyocr
from collections import defaultdict


class JerseyOCR:
    def __init__(self):
        self.reader = easyocr.Reader(['en'], gpu=False)
        self.number_history = defaultdict(list)
        self.history_window = 30

    def _extract_torso(self, crop):
        h, w = crop.shape[:2]
        # Wider crop: 20%-75% to catch numbers higher or lower on the kit
        torso = crop[int(h * 0.2): int(h * 0.75), :]
        # Upscale for better OCR
        torso = cv2.resize(torso, None, fx=2.5, fy=2.5, interpolation=cv2.INTER_CUBIC)
        # Sharpen
        kernel = np.array([[0, -1, 0],
                           [-1, 5, -1],
                           [0, -1, 0]])
        return cv2.filter2D(torso, -1, kernel)

    def _make_candidates(self, torso_bgr):
        gray = cv2.cvtColor(torso_bgr, cv2.COLOR_BGR2GRAY)
        _, thresh_normal = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        thresh_inverted = cv2.bitwise_not(thresh_normal)
        return [
            torso_bgr,                                          # color — EasyOCR handles this natively
            cv2.cvtColor(thresh_normal, cv2.COLOR_GRAY2BGR),   # dark numbers on light kit
            cv2.cvtColor(thresh_inverted, cv2.COLOR_GRAY2BGR), # light numbers on dark kit
        ]

    def _read_from_image(self, img):
        results = self.reader.readtext(img, allowlist='0123456789')
        for (_, text, confidence) in results:
            text = text.strip()
            if confidence < 0.7:
                continue
            if text.isdigit():
                number = int(text)
                if 1 <= number <= 99:
                    return number
        return None

    def read_number(self, crop):
        torso = self._extract_torso(crop)
        for candidate in self._make_candidates(torso):
            number = self._read_from_image(candidate)
            if number is not None:
                return number
        return None

    def update_history(self, tracker_id, number):
        self.number_history[tracker_id].append(number)
        if len(self.number_history[tracker_id]) > self.history_window:
            self.number_history[tracker_id].pop(0)

    def get_confirmed_number(self, tracker_id):
        valid_reads = [n for n in self.number_history[tracker_id] if n is not None]
        if not valid_reads:
            return None
        best = max(set(valid_reads), key=valid_reads.count)
        # require at least 3 consistent reads before committing to a number
        if valid_reads.count(best) < 3:
            return None
        return best

    def process_frame(self, frame, detections):
        confirmed_numbers = {}

        for i, tracker_id in enumerate(detections.tracker_id):
            x1, y1, x2, y2 = detections.xyxy[i].astype(int)
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)

            crop = frame[y1:y2, x1:x2]
            if crop.size == 0:
                confirmed_numbers[tracker_id] = None
                continue

            try:
                number = self.read_number(crop)
            except Exception:
                number = None

            self.update_history(tracker_id, number)
            confirmed_numbers[tracker_id] = self.get_confirmed_number(tracker_id)

        return confirmed_numbers


if __name__ == "__main__":
    ocr = JerseyOCR()
    test_crop = cv2.imread("../../data/samples/player_crop.jpg")
    if test_crop is not None:
        number = ocr.read_number(test_crop)
        print(f"Detected jersey number: {number}")
    else:
        print("No test image found. Drop a player crop at data/samples/player_crop.jpg")
