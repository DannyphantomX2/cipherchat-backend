from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from app.core.database import get_db
from app.models.models import RoomKey, RoomMember, User
from app.schemas.schemas import PublishKeyRequest, RoomKeyResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/rooms", tags=["keys"])

@router.post("/{room_id}/keys", status_code=204)
def publish_key(
    room_id: int,
    payload: PublishKeyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    member = db.query(RoomMember).filter(
        RoomMember.room_id == room_id,
        RoomMember.user_id == current_user.id
    ).first()
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this room")

    existing = db.query(RoomKey).filter(
        RoomKey.room_id == room_id,
        RoomKey.user_id == current_user.id
    ).first()

    if existing:
        existing.public_key = payload.public_key
    else:
        db.add(RoomKey(
            room_id=room_id,
            user_id=current_user.id,
            username=current_user.username,
            public_key=payload.public_key
        ))
    db.commit()

@router.get("/{room_id}/keys", response_model=list[RoomKeyResponse])
def get_keys(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    member = db.query(RoomMember).filter(
        RoomMember.room_id == room_id,
        RoomMember.user_id == current_user.id
    ).first()
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this room")

    return db.query(RoomKey).filter(RoomKey.room_id == room_id).all()
