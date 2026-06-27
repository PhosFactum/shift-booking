from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_active_user
from app.models import Room
from app.schemas import RoomOut

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.get("/", response_model=List[RoomOut])
async def list_rooms(
    db: AsyncSession = Depends(get_db), current_user=Depends(get_current_active_user)
):
    result = await db.execute(select(Room))
    rooms = result.scalars().all()
    return rooms
