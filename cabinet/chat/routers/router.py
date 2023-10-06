from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()

@router.get('/')
async def main():
    return FileResponse('templates/main.html')


@router.get('/registration')
async def registration():
    return FileResponse('templates/registration.html')


@router.get('/chat')
async def chat():
    return FileResponse('templates/chat.html')


@router.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            data = data.split()
            await manager.broadcast(f"{data[0]}: {data[1]}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client left the chat")
