from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # TODO: process frame data through pipeline
            await websocket.send_text(f"echo: {data}")
    except WebSocketDisconnect:
        pass
