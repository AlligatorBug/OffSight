# tracker.py: who is who across frames?
# detection alone has a problem, each frame is processed independently :-(
# ByteTrack solves this by watching how boxes move between frames
# input = 1 video frame
# output = same Detections object but now each one has a tracker_id attached

import supervision as sv
from .detector import PlayerDetector


class PlayerTracker:
    def __init__(self, model_path: str = "yolov8x.pt", confidence: float = 0.3):
        """
        Initializes the player tracker.
        Wraps PlayerDetector with ByteTrack to assign consistent
        IDs to each player across frames.

        Args:
            model_path: Path to YOLOv8 weights.
            confidence: Minimum detection confidence threshold (0-1).
        """
        self.detector = PlayerDetector(model_path=model_path, confidence=confidence)

        # ByteTrack — assigns and maintains a unique track ID per player
        # lost_track_buffer: how many frames to keep a player's ID alive
        # when they're temporarily hidden or off screen
        self.tracker = sv.ByteTrack(lost_track_buffer=30)

        # Annotators
        self.box_annotator = sv.BoxAnnotator(
            thickness=2,
            text_thickness=1,
            text_scale=0.5
        )
        self.trace_annotator = sv.TraceAnnotator(
            thickness=2,
            trace_length=50     # draws a trail showing where the player has been
        )

    def track(self, frame):
        """
        Runs detection + tracking on a single frame.

        Args:
            frame: A BGR image (numpy array from OpenCV).

        Returns:
            A supervision Detections object where each detection now has
            a consistent tracker_id that persists across frames.
        """
        # Step 1: detect players in this frame
        detections = self.detector.detect(frame)

        # Step 2: pass detections to ByteTrack to assign/maintain track IDs
        detections = self.tracker.update_with_detections(detections)

        return detections

    def track_video(self, video_path: str, output_path: str = "output_tracked.mp4"):
        """
        Runs detection + tracking on every frame of a video
        and saves the annotated output.

        Args:
            video_path:  Path to the input football match video.
            output_path: Path to save the annotated output video.
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

            # Run detection + tracking
            detections = self.track(frame)

            # Build labels using the persistent tracker ID
            # At this stage we just show the ID — names come later
            # once OCR and name matching are wired in
            labels = [
                f"ID {tracker_id}"
                for tracker_id in detections.tracker_id
            ]

            # Draw movement trails
            annotated_frame = self.trace_annotator.annotate(
                scene=frame.copy(),
                detections=detections
            )

            # Draw bounding boxes + ID labels on top
            annotated_frame = self.box_annotator.annotate(
                scene=annotated_frame,
                detections=detections,
                labels=labels
            )

            out.write(annotated_frame)

        cap.release()
        out.release()
        print(f"\nDone. Saved to: {output_path}")
        print(f"Tracked players across {frame_num} frames.")


if __name__ == "__main__":
    # Quick test — point this at any football clip
    tracker = PlayerTracker(
        model_path="yolov8x.pt",
        confidence=0.3
    )

    tracker.track_video(
        video_path="../../data/samples/match_clip.mp4",
        output_path="../../data/samples/match_clip_tracked.mp4"
    )