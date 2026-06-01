# Offsight 🎯

**Offsight** is an end-to-end computer vision pipeline that automatically detects, tracks, and identifies football players in match footage.

It combines **object detection**, **multi-object tracking**, **OCR**, and **appearance-based Re-ID** to locate every player on the pitch, follow them as they move, and display their real names on screen — even when jersey numbers are hidden, blurred, or obscured.

Offsight identifies players primarily through jersey number recognition, but falls back to a layered system when numbers aren't visible — using player appearance (body shape, jersey color, kit details), positional continuity, and temporal majority voting to maintain robust identification through occlusion, camera cuts, and fast motion.

Built at the intersection of sports technology and applied AI, Offsight turns raw match footage into labeled, analyzable data for coaches, analysts, and broadcasters.

---

## Tech Stack

| Layer | Tool |
|---|---|
| Detection | YOLOv8 (Ultralytics) |
| Tracking | ByteTrack + Supervision |
| OCR | PaddleOCR + OpenCV |
| Re-ID | OSNet + StrongSORT |
| Backend | FastAPI + WebSockets |
| Frontend | React |
| Deployment | Docker + HuggingFace Spaces |

### 🔍 Detection
- **YOLOv8** (Ultralytics) — detecting players in each frame

### 🎯 Tracking
- **ByteTrack** — maintaining consistent player IDs across frames
- **Supervision** (Roboflow) — tracking utilities and video annotation helpers

### 🔢 Jersey OCR
- **PaddleOCR** — reading jersey numbers from cropped torso regions
- **OpenCV** — image preprocessing (sharpening, contrast boost before OCR)

### 🧍 Appearance Re-ID
- **OSNet** (torchreid) — matching player appearance when jersey number isn't visible
- **StrongSORT** — combines tracking + Re-ID into one pipeline

### 🎥 Video Processing
- **OpenCV** — frame extraction, annotation, video output

### 🗂️ Name Matching
- **Pandas** — loading and querying squad CSV (jersey number → player name)

### ⚙️ Backend
- **FastAPI** — handling video upload and processing requests
- **WebSockets** — streaming real-time processing progress to the frontend

### 🖥️ Frontend
- **React** — full design control for a production-grade, professional UI

### 📦 Deployment
- **Docker** — containerizing the full pipeline
- **HuggingFace Spaces** — free GPU hosting for your demo
