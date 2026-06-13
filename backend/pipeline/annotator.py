# annotator.py: runs all 4 steps for every frame and draws the results
"""
For every frame:
detections = tracker.track(frame)           # Problem 1 + 2
confirmed_numbers = ocr.process_frame(...)  # Problem 3
matched_names = matcher.match_frame(...)    # Problem 4
annotated_frame = annotator.annotate(...)   # Draw it all
"""

import cv2
import numpy as np
import supervision as sv


class PlayerAnnotator:
    def __init__(self):
        """
        Initializes the annotator with box, trace, and label styles.
        This is the final step in the pipeline — it takes all the data
        produced by tracker, OCR, and matcher and draws it onto the frame.
        """
        # Bounding box drawing
        self.box_annotator = sv.BoxAnnotator(
            thickness=2,
            text_thickness=1,
            text_scale=0.5
        )

        # Movement trail behind each player
        self.trace_annotator = sv.TraceAnnotator(
            thickness=2,
            trace_length=50
        )

        # Colors for home vs away teams
        # Will be assigned based on jersey color clustering later
        self.home_color  = (255, 100, 100)   # blue  (BGR)
        self.away_color  = (100, 100, 255)   # red   (BGR)
        self.unknown_color = (180, 180, 180) # gray  (BGR)

        # Font settings for name labels drawn manually with OpenCV
        self.font       = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = 0.55
        self.font_thickness = 2

    def _get_label(self, tracker_id, matched_names, confirmed_numbers):
        """
        Builds the display label for a single player.

        Priority:
            1. Player name if matched        → "Messi"
            2. Jersey number if OCR found it → "#10"
            3. Tracker ID as fallback        → "ID 3"

        Args:
            tracker_id:       ByteTrack ID for this player.
            matched_names:    Dict { tracker_id: player_name or None }
            confirmed_numbers: Dict { tracker_id: jersey_number or None }

        Returns:
            Label string to display above the bounding box.
        """
        name   = matched_names.get(tracker_id)
        number = confirmed_numbers.get(tracker_id)

        if name:
            return name
        elif number:
            return f"#{number}"
        else:
            return f"ID {tracker_id}"

    def _draw_label(self, frame, label, x1, y1, color):
        """
        Draws a filled background pill with the player label above
        their bounding box. Cleaner than supervision's default text.

        Args:
            frame:  The video frame to draw on.
            label:  Text to display.
            x1, y1: Top-left corner of the bounding box.
            color:  BGR color for the background pill.
        """
        # Measure text size so we can size the background pill
        (text_w, text_h), baseline = cv2.getTextSize(
            label, self.font, self.font_scale, self.font_thickness
        )

        padding = 5

        # Background pill position — sits just above the bounding box
        pill_x1 = x1
        pill_y1 = y1 - text_h - padding * 2 - baseline
        pill_x2 = x1 + text_w + padding * 2
        pill_y2 = y1

        # Clamp to frame boundaries so labels don't go off screen
        pill_y1 = max(0, pill_y1)

        # Draw filled rectangle background
        cv2.rectangle(frame, (pill_x1, pill_y1), (pill_x2, pill_y2), color, -1)

        # Draw the text on top
        cv2.putText(
            frame,
            label,
            (pill_x1 + padding, pill_y2 - baseline - 1),
            self.font,
            self.font_scale,
            (255, 255, 255),   # white text
            self.font_thickness,
            cv2.LINE_AA
        )

    def annotate(self, frame, detections, matched_names, confirmed_numbers):
        """
        Draws the full annotation onto a frame:
            - Movement trails
            - Bounding boxes
            - Name / number / ID labels

        Args:
            frame:             Raw video frame (BGR numpy array).
            detections:        Supervision Detections with tracker_ids.
            matched_names:     Dict { tracker_id: player_name or None }
            confirmed_numbers: Dict { tracker_id: jersey_number or None }

        Returns:
            Annotated frame as a BGR numpy array.
        """
        annotated = frame.copy()

        # Draw movement trails first so boxes render on top
        annotated = self.trace_annotator.annotate(
            scene=annotated,
            detections=detections
        )

        # Draw bounding boxes
        annotated = self.box_annotator.annotate(
            scene=annotated,
            detections=detections,
            labels=[""] * len(detections)   # blank — we draw labels manually below
        )

        # Draw name labels above each bounding box
        for i, tracker_id in enumerate(detections.tracker_id):
            x1, y1, x2, y2 = detections.xyxy[i].astype(int)

            label = self._get_label(tracker_id, matched_names, confirmed_numbers)

            # Color the label based on whether we have a confirmed name
            name = matched_names.get(tracker_id)
            if name:
                color = self.home_color   # confirmed player — blue
            elif confirmed_numbers.get(tracker_id):
                color = self.away_color   # number found, no name yet — red
            else:
                color = self.unknown_color  # unknown — gray

            self._draw_label(annotated, label, x1, y1, color)

        return annotated

    def annotate_video(
        self,
        video_path: str,
        output_path: str,
        tracker,
        ocr,
        matcher,
        reid
    ):
        """
        Full pipeline annotation on a complete video.
        Ties tracker, OCR, and matcher together frame by frame
        and writes the annotated output.

        Args:
            video_path:  Path to input match footage.
            output_path: Path to save annotated output video.
            tracker:     PlayerTracker instance.
            ocr:         JerseyOCR instance.
            matcher:     PlayerMatcher instance.
        """
        import cv2

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")

        width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps    = cap.get(cv2.CAP_PROP_FPS)
        total  = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        frame_num = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_num += 1
            print(f"Processing frame {frame_num}/{total}", end="\r")

            # Step 1: detect + track
            detections = tracker.track(frame)

            # Step 2: OCR jersey numbers
            confirmed_numbers = ocr.process_frame(frame, detections)

            # for players OCR failed on, try Re-ID
            for i, (tracker_id, number) in enumerate(confirmed_numbers.items()):
                x1, y1, x2, y2 = detections.xyxy[i].astype(int)
                crop = frame[y1:y2, x1:x2]
                embedding = reid.extract_features(crop)
                if number is None:
                    matched_id = reid.match(embedding)
                    if matched_id is not None:
                        confirmed_numbers[tracker_id] = confirmed_numbers[matched_id]
                else:
                    reid.update_gallery(tracker_id, embedding)

            # Step 3: match numbers to names
            matched_names = matcher.match_frame(confirmed_numbers)

            # Step 4: annotate and write frame
            annotated_frame = self.annotate(
                frame, detections, matched_names, confirmed_numbers
            )

            out.write(annotated_frame)

        cap.release()
        out.release()
        print(f"\nDone. Saved annotated video to: {output_path}")


if __name__ == "__main__":
    from tracker import PlayerTracker
    from ocr import JerseyOCR
    from matcher import PlayerMatcher
    from reid import ReID

    tracker = PlayerTracker(model_path="yolov8x.pt", confidence=0.3)
    ocr     = JerseyOCR()
    matcher = PlayerMatcher()
    reid = ReID()

    matcher.load_from_csv("../../data/squads/test_squad.csv")

    annotator = PlayerAnnotator()

    annotator.annotate_video(
        video_path="../../data/samples/match_clip.mp4",
        output_path="../../data/samples/match_clip_annotated.mp4",
        tracker=tracker,
        ocr=ocr,
        matcher=matcher,
        reid=reid
    )