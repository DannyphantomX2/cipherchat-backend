from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.security import decode_access_token
from app.models.models import RoomMember, Message
from collections import defaultdict
import json

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.rooms: dict[int, list[WebSocket]] = defaultdict(list)

    async def connect(self, room_id: int, ws: WebSocket):
        await ws.accept()
        self.rooms[room_id].append(ws)

    def disconnect(self, room_id: int, ws: WebSocket):
        if ws in self.rooms[room_id]:
            self.rooms[room_id].remove(ws)

    async def broadcast(self, room_id: int, message: dict):
        for connection in self.rooms[room_id]:
            await connection.send_text(json.dumps(message))

manager = ConnectionManager()

@router.websocket("/ws/{room_id}")
async def websocket_endpoint(
    room_id: int,
    ws: WebSocket,
    token: str = Query(...)
):
    user_id = decode_access_token(token)
    if user_id is None:
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    db: Session = SessionLocal()
    try:
        member = db.query(RoomMember).filter(
            RoomMember.room_id == room_id,
            RoomMember.user_id == user_id
        ).first()
        if not member:
            await ws.close(code=status.WS_1008_POLICY_VIOLATION)
            return
    finally:
        db.close()

    await manager.connect(room_id, ws)
    try:
        while True:
            data = await ws.receive_text()
            payload = json.loads(data)

            # payload format: { "recipients": { "userId": { "ciphertext": "...", "iv": "..." } } }
            # or for solo:    { "recipients": { "solo": { "ciphertext": "...", "iv": "none" } } }
            recipients_json = json.dumps(payload.get("recipients", {}))

            db = SessionLocal()
            try:
                msg = Message(
                    room_id=room_id,
                    sender_id=user_id,
                    recipients=recipients_json
                )
                db.add(msg)
                db.commit()
                db.refresh(msg)
                out = {
                    "id": msg.id,
                    "room_id": msg.room_id,
                    "sender_id": msg.sender_id,
                    "recipients": payload.get("recipients", {}),
                    "created_at": msg.created_at.isoformat()
                }
            finally:
                db.close()

            await manager.broadcast(room_id, out)

    except WebSocketDisconnect:
        manager.disconnect(room_id, ws)
