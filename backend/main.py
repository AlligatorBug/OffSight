# main.py = FastAPI app entry point -> all the @app.stuff

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.websocket import router as ws_router

app = FastAPI(title="OffSight API")

# CORS: allows the React frontend to talk to the backend (different ports) 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # "*" = accept requests from anywhere 
    allow_methods=["*"],
    allow_headers=["*"],
)

# register the WebSocket routes defined in websocket.py
app.include_router(ws_router)

# /health to see if server is alive 
@app.get("/health")
def health():
    return {"status": "ok"}
