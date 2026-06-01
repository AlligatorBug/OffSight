from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.websocket import router as ws_router

app = FastAPI(title="OffSight API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ws_router)


@app.get("/health")
def health():
    return {"status": "ok"}
