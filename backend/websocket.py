# websocket.py: a WebSocket is a persistent 2-way connection between frontend and backend -> unlike normal HTTP requests (send -> wait -> receive)
# WebSockets let the backend push updates to the frontend at any time -> how processing progress gets streamed live 
# HTTP = backend is completely reactive, only sends data when frontend asks for it
# WebSocket = backend constantly changing, backend just pushes new updates to frontend (frontend listens to backend)

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept() # accept the connection from frontend
    try:
        while True:
            data = await websocket.receive_text() # wait for a message
            # TODO: process frame data through pipeline
            await websocket.send_text(f"echo: {data}")
    except WebSocketDisconnect:
        pass # client disconnected, clean exit
