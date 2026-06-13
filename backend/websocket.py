# websocket.py: a WebSocket is a persistent 2-way connection between frontend and backend -> unlike normal HTTP requests (send -> wait -> receive)
# WebSockets let the backend push updates to the frontend at any time -> how processing progress gets streamed live 
# HTTP = backend is completely reactive, only sends data when frontend asks for it
# WebSocket = backend constantly changing, backend just pushes new updates to frontend (frontend listens to backend)

import json
import asyncio
import tempfile
import os
import cv2
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.pipeline.tracker import PlayerTracker
from backend.pipeline.ocr import JerseyOCR
from backend.pipeline.matcher import PlayerMatcher
from backend.pipeline.reid import ReID
from backend.pipeline.annotator import PlayerAnnotator

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept() # accept the connection from frontend
    try:
        # 1. receive metadata from frontend
        meta = await websocket.receive_text()
        meta = json.loads(meta)

        await websocket.send_text(json.dumps({
            "status": "received",
            "message": "metadata received, waiting for video..."
        }))

        # 2. receive video bytes from frontend
        video_bytes = await websocket.receive_bytes()

        await websocket.send_text(json.dumps({
            "status": "received",
            "message": "video received, initialising pipeline..."
        }))

        # 3. save video to a temp file on disk
        with tempfile.NamedTemporaryFile(
            suffix=".mp4",
            delete=False
        ) as tmp:
            tmp.write(video_bytes)
            tmp_video_path = tmp.name

        # 4. initialise pipeline 
        tracker  = PlayerTracker(model_path="yolov8x.pt", confidence=0.3)
        ocr      = JerseyOCR()
        matcher  = PlayerMatcher()
        reid     = ReID()
        annotator = PlayerAnnotator()

        # load squad if provided
        if meta.get("squad_csv"):
            matcher.load_from_csv(meta["squad_csv"])

        await websocket.send_text(json.dumps({
            "status": "processing",
            "message": "pipeline initialised, starting processing..."
        }))

        # 5. process the video
        output_path = tmp_video_path.replace(".mp4", "_annotated.mp4")

        await process_video(
            websocket=websocket,
            tracker=tracker,
            ocr=ocr,
            matcher=matcher,
            reid=reid,
            annotator=annotator,
            video_path=tmp_video_path,
            output_path=output_path
        )

        # 6. send done message
        await websocket.send_text(json.dumps({
            "status": "done",
            "output_path": output_path
        }))

    except WebSocketDisconnect:
        pass # client disconnected, clean exit
    finally:
        # clean up temp files
        if 'tmp_video_path' in locals() and os.path.exists(tmp_video_path):
            os.remove(tmp_video_path)


async def process_video(websocket, tracker, ocr, matcher, reid, annotator, video_path, output_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_path}")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    frame_num = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_num += 1
        await websocket.send_text(json.dumps({
            "status": "processing",
            "frame": frame_num,
            "total": total
        }))

        await asyncio.sleep(0)

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
        annotated_frame = annotator.annotate(
            frame, detections, matched_names, confirmed_numbers
        )

        out.write(annotated_frame)

    cap.release()
    out.release()
    print(f"\nDone. Saved annotated video to: {output_path}")