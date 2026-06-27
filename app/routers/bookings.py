from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_active_user
from app.models import Booking, Room, User, UserRole
from app.schemas import BookingCreate, BookingOut

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("/", response_model=BookingOut)
async def create_booking(
    booking_data: BookingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # Проверяем существование комнаты
    room = await db.get(Room, booking_data.room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    # Проверяем пересечение броней
    existing = await db.execute(
        select(Booking).where(
            and_(
                Booking.room_id == booking_data.room_id,
                Booking.date == booking_data.date.date(),
                Booking.start_time < booking_data.end_time,
                Booking.end_time > booking_data.start_time,
            )
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Time slot already booked")

    new_booking = Booking(
        room_id=booking_data.room_id,
        user_id=current_user.id,
        date=booking_data.date,
        start_time=booking_data.start_time,
        end_time=booking_data.end_time,
    )
    db.add(new_booking)
    await db.commit()
    await db.refresh(new_booking)
    return new_booking


@router.delete("/{booking_id}", status_code=204)
async def cancel_booking(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    booking = await db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Используем getattr для безопасного получения значений и явное приведение типов
    is_admin = getattr(current_user, "role", None)
    if is_admin is not None:
        is_admin = is_admin.value == UserRole.admin.value
    else:
        is_admin = False

    # Получаем id пользователя и владельца брони
    current_user_id = getattr(current_user, "id", 0)
    booking_user_id = getattr(booking, "user_id", 0)
    is_owner = current_user_id == booking_user_id

    if not is_admin and not is_owner:
        raise HTTPException(
            status_code=403, detail="Not allowed to cancel this booking"
        )
    await db.delete(booking)
    await db.commit()
