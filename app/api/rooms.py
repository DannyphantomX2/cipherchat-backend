import secrets
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Room, RoomMember, Message, User
from app.schemas.schemas import RoomCreate, RoomJoin, RoomResponse, MessageResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/rooms", tags=["rooms"])

def _is_member(db: Session, room_id: int, user_id: int) -> bool:
    return db.query(RoomMember).filter(
        RoomMember.room_id == room_id,
        RoomMember.user_id == user_id
    ).first() is not None

@router.post("", response_model=RoomResponse, status_code=201)
def create_room(payload: RoomCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    room = Room(
        name=payload.name,
        invite_code=secrets.token_urlsafe(9)[:12],
        created_by=current_user.id
    )
    db.add(room)
    db.flush()
    db.add(RoomMember(room_id=room.id, user_id=current_user.id))
    db.commit()
    db.refresh(room)
    return room

@router.get("", response_model=list[RoomResponse])
def list_rooms(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    memberships = db.query(RoomMember).filter(RoomMember.user_id == current_user.id).all()
    room_ids = [m.room_id for m in memberships]
    return db.query(Room).filter(Room.id.in_(room_ids)).all()

@router.post("/join", response_model=RoomResponse)
def join_room(payload: RoomJoin, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    room = db.query(Room).filter(Room.invite_code == payload.invite_code).first()
    if not room:
        raise HTTPException(status_code=404, detail="Invalid invite code")
    if _is_member(db, room.id, current_user.id):
        return room
    db.add(RoomMember(room_id=room.id, user_id=current_user.id))
    db.commit()
    db.refresh(room)
    return room

@router.get("/{room_id}", response_model=RoomResponse)
def get_room(room_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not _is_member(db, room_id, current_user.id):
        raise HTTPException(status_code=403, detail="Not a member of this room")
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room

@router.get("/{room_id}/messages", response_model=list[MessageResponse])
def get_messages(room_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not _is_member(db, room_id, current_user.id):
        raise HTTPException(status_code=403, detail="Not a member of this room")
    msgs = (
        db.query(Message)
        .filter(Message.room_id == room_id)
        .order_by(Message.created_at.desc())
        .limit(50)
        .all()
    )
    result = []
    for msg in msgs:
        try:
            recipients = json.loads(msg.recipients) if isinstance(msg.recipients, str) else msg.recipients
        except Exception:
            recipients = {}
        result.append(MessageResponse(
            id=msg.id,
            room_id=msg.room_id,
            sender_id=msg.sender_id,
            recipients=recipients,
            created_at=msg.created_at.isoformat()
        ))
    return result
