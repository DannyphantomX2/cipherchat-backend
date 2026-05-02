from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Any

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    model_config = {"from_attributes": True}

class RoomCreate(BaseModel):
    name: str

class RoomJoin(BaseModel):
    invite_code: str

class RoomResponse(BaseModel):
    id: int
    name: str
    invite_code: str
    created_by: int
    created_at: datetime
    model_config = {"from_attributes": True}

class MessageResponse(BaseModel):
    id: int
    room_id: int
    sender_id: int
    recipients: dict[str, Any]
    created_at: str
    model_config = {"from_attributes": True}

class PublishKeyRequest(BaseModel):
    public_key: str

class RoomKeyResponse(BaseModel):
    user_id: int
    username: str
    public_key: str
    model_config = {"from_attributes": True}
