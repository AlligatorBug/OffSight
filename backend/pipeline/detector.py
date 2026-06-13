# input: 1 video frame (a numpy array, a grid of pixel values)
# output: a Detections object -> a list of bounding boxes with confidence scores 
# step 1: find players!!
# detector.py: YOLOv8 = pretrained model that can look at an image and draw boxes around every person it sees 

from ultralytics import YOLO
import supervision as sv
import cv2


class PlayerDetector:
    def __init__(self, model_path: str = "yolov8x.pt", confidence: float = 0.3):
        """
        Initializes the YOLOv8 player detector.

        Args:
            model_path: Path to YOLOv8 weights. Downloads automatically if not found.
            confidence: Minimum confidence threshold for detections (0-1).
        """
        self.model = YOLO(model_path)
        self.confidence = confidence

        # Class 0 in YOLOv8 is "person" — we only want players, not the crowd
        self.player_class_id = 0

    def detect(self, frame):
        """
        Runs detection on a single frame.

        Args:
            frame: A BGR image (numpy array from OpenCV).

        Returns:
            A supervision Detections object containing bounding boxes,
            confidence scores, and class IDs for all detected players.
        """
        results = self.model(frame, conf=self.confidence)[0]
        detections = sv.Detections.from_ultralytics(results)

        # Filter to only keep people (class 0), ignoring ball, goalposts etc.
        detections = detections[detections.class_id == self.player_class_id]

        return detections

    def detect_video(self, video_path: str, output_path: str = "output.mp4"):
        """
        Runs detection on every frame of a video and saves annotated output.

        Args:
            video_path:  Path to the input football match video.
            output_path: Path to save the annotated output video.
        """
        # Open the video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")

        # Get video properties so we can write the output at the same resolution/fps
        width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps    = cap.get(cv2.CAP_PROP_FPS)
        total  = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Set up the output video writer
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        # Set up the bounding box annotator from supervision
        box_annotator = sv.BoxAnnotator(
            thickness=2,
            text_thickness=1,
            text_scale=0.5
        )

        frame_num = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_num += 1
            print(f"Processing frame {frame_num}/{total}", end="\r")

            # Run detection on this frame
            detections = self.detect(frame)

            # Build labels showing confidence score for each detection
            labels = [
                f"Player {confidence:.2f}"
                for confidence in detections.confidence
            ]

            # Draw bounding boxes onto the frame
            annotated_frame = box_annotator.annotate(
                scene=frame.copy(),
                detections=detections,
                labels=labels
            )

            out.write(annotated_frame)

        cap.release()
        out.release()
        print(f"\nDone. Saved to: {output_path}")
        print(f"Total players detected across {frame_num} frames.")


if __name__ == "__main__":
    # Quick test — point this at any football clip
    detector = PlayerDetector(
        model_path="yolov8x.pt",
        confidence=0.3
    )

    detector.detect_video(
        video_path="../../data/samples/match_clip.mp4",
        output_path="../../data/samples/match_clip_detected.mp4"
    )