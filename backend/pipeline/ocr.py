# ocr.py: what is their jersey number?
# player crop -> zoom into torso region -> scale up to 2.5x -> sharpen -> convert to black and white -> PaddleOCR reads it -> "10"
# uses majority voting, keeps a history of the last 30 reads for each tracker_id and picks the most common one

import cv2
import numpy as np
from paddleocr import PaddleOCR
from collections import defaultdict


class JerseyOCR:
    def __init__(self):
        """
        Initializes PaddleOCR for jersey number recognition.
        Uses English digit recognition in a lightweight mode.
        """
        self.ocr = PaddleOCR(
            use_angle_cls=True,
            lang="en",
        )

        # Stores a history of jersey number reads per tracker_id
        # { tracker_id: [7, 7, None, 7, 10, 7] }
        # Used for majority voting — take the most common read per player
        self.number_history = defaultdict(list)

        # How many frames of history to use for majority voting
        self.history_window = 30

    def preprocess_crop(self, crop):
        """
        Preprocesses a player crop before passing to OCR.
        Focuses on the torso region where the jersey number lives,
        and sharpens the image to improve OCR accuracy.

        Args:
            crop: BGR image of the full player bounding box.

        Returns:
            Preprocessed torso crop ready for OCR.
        """
        h, w = crop.shape[:2]

        # Focus on the torso — top 30% to 70% of the bounding box
        # The number sits on the chest/back, not the head or legs
        torso = crop[int(h * 0.3): int(h * 0.7), :]

        # Upscale — OCR works much better on larger images
        torso = cv2.resize(torso, None, fx=2.5, fy=2.5, interpolation=cv2.INTER_CUBIC)

        # Sharpen — jersey numbers are often motion blurred
        kernel = np.array([[0, -1, 0],
                           [-1, 5, -1],
                           [0, -1, 0]])
        torso = cv2.filter2D(torso, -1, kernel)

        # Convert to grayscale for cleaner OCR
        torso = cv2.cvtColor(torso, cv2.COLOR_BGR2GRAY)

        # Apply threshold to make number stand out from jersey background
        _, torso = cv2.threshold(torso, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Convert back to BGR — PaddleOCR expects a 3-channel image
        torso = cv2.cvtColor(torso, cv2.COLOR_GRAY2BGR)

        return torso

    def read_number(self, crop):
        """
        Reads a jersey number from a single player crop.

        Args:
            crop: BGR image of the player bounding box.

        Returns:
            Jersey number as an integer, or None if no number was found.
        """
        torso = self.preprocess_crop(crop)

        results = self.ocr.ocr(torso)

        if not results:
            return None

        lines = results[0] if isinstance(results[0], list) else results
        if not lines:
            return None

        for line in lines:
            try:
                if isinstance(line, dict):
                    text = str(line.get('rec_text') or line.get('transcription') or '').strip()
                    confidence = float(line.get('rec_score') or line.get('confidence') or 1.0)
                elif isinstance(line, (list, tuple)):
                    second = line[1]
                    if isinstance(second, (list, tuple)):
                        text = str(second[0]).strip()
                        confidence = float(second[1])
                    elif isinstance(second, str):
                        text = second.strip()
                        confidence = 1.0
                    else:
                        continue
                else:
                    continue
            except (IndexError, KeyError, TypeError, ValueError):
                continue

            if confidence < 0.7:
                continue

            if text.isdigit():
                number = int(text)
                if 1 <= number <= 99:
                    return number

        return None

    def update_history(self, tracker_id, number):
        """
        Adds a jersey number read to that player's history.
        Keeps only the last N reads to stay current.

        Args:
            tracker_id: The ByteTrack ID for this player.
            number:     The jersey number read this frame (or None).
        """
        self.number_history[tracker_id].append(number)

        # Keep history window trimmed
        if len(self.number_history[tracker_id]) > self.history_window:
            self.number_history[tracker_id].pop(0)

    def get_confirmed_number(self, tracker_id):
        """
        Returns the most likely jersey number for a player
        using majority voting across their history.

        Example:
            history = [7, 7, None, 7, 10, 7]
            → returns 7 (appears most often)

        Args:
            tracker_id: The ByteTrack ID for this player.

        Returns:
            Most common jersey number, or None if not enough confident reads.
        """
        history = self.number_history[tracker_id]

        # Filter out None reads
        valid_reads = [n for n in history if n is not None]

        if not valid_reads:
            return None

        # Return the most common number seen
        return max(set(valid_reads), key=valid_reads.count)

    def process_frame(self, frame, detections):
        """
        Runs OCR on every detected player in a frame.
        Updates each player's number history and returns
        their confirmed jersey number.

        Args:
            frame:      Full video frame (BGR numpy array).
            detections: Supervision Detections object with tracker_ids.

        Returns:
            A dict mapping tracker_id → confirmed jersey number (or None).
        """
        confirmed_numbers = {}

        for i, tracker_id in enumerate(detections.tracker_id):
            # Extract the bounding box for this player
            x1, y1, x2, y2 = detections.xyxy[i].astype(int)

            # Clamp coordinates to frame boundaries
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)

            # Crop the player from the frame
            crop = frame[y1:y2, x1:x2]

            if crop.size == 0:
                confirmed_numbers[tracker_id] = None
                continue

            # Read the jersey number from this crop
            number = self.read_number(crop)

            # Update this player's history
            self.update_history(tracker_id, number)

            # Get the majority-voted confirmed number
            confirmed_numbers[tracker_id] = self.get_confirmed_number(tracker_id)

        return confirmed_numbers


if __name__ == "__main__":
    # Quick test on a single image crop
    ocr = JerseyOCR()

    # Load a test image of a player
    test_crop = cv2.imread("../../data/samples/player_crop.jpg")

    if test_crop is not None:
        number = ocr.read_number(test_crop)
        print(f"Detected jersey number: {number}")
    else:
        print("No test image found. Drop a player crop at data/samples/player_crop.jpg")