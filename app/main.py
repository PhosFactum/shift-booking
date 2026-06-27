from fastapi import FastAPI

from app.database import Base, engine
from app.routers import auth, bookings, rooms

app = FastAPI(title="Meeting Room Booking", version="0.1.0")

app.include_router(auth.router)
app.include_router(rooms.router)
app.include_router(bookings.router)


@app.on_event("startup")
async def startup():
    # Создаём таблицы (для разработки, позже используйте Alembic)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/")
async def root():
    return {"message": "Meeting Room Booking API"}
