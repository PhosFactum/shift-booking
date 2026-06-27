from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class UserRole(str, Enum):
    employee = "employee"
    admin = "admin"


# Auth
class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[UserRole] = None


# Users
class UserOut(BaseModel):
    id: int
    username: str
    role: UserRole

    class Config:
        from_attributes = True


# Rooms
class RoomBase(BaseModel):
    name: str
    capacity: int


class RoomOut(RoomBase):
    id: int

    class Config:
        from_attributes = True


# Bookings
class BookingCreate(BaseModel):
    room_id: int
    date: datetime  # дата, время игнорируем
    start_time: str  # "HH:MM"
    end_time: str  # "HH:MM"


class BookingOut(BaseModel):
    id: int
    room_id: int
    user_id: int
    date: datetime
    start_time: str
    end_time: str
    created_at: datetime

    class Config:
        from_attributes = True
