import re
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import date

from fastapi import Depends, FastAPI, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud, db, models
from .schemas import BirthdayMessage, UserIn

USERNAME_RE = re.compile(r"^[A-Za-z]+$")


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    async with db.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield


app = FastAPI(title="Birthday API", lifespan=lifespan)


def validate_username(username: str) -> None:
    if not USERNAME_RE.fullmatch(username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="username must contain letters only",
        )


def next_birthday(dob: date, today: date) -> date:
    for year in (today.year, today.year + 1):
        try:
            candidate = date(year=year, month=dob.month, day=dob.day)
        except ValueError:
            candidate = date(year=year, month=3, day=1)

        if candidate >= today:
            return candidate

    return date(year=today.year + 1, month=3, day=1)


def calculate_days_to_birthday(dob: date, today: date) -> int:
    return (next_birthday(dob, today) - today).days


@app.put("/hello/{username}", status_code=status.HTTP_204_NO_CONTENT)
async def create_or_update_user(
    payload: UserIn,
    username: str = Path(..., min_length=1, max_length=64),
    session: AsyncSession = Depends(db.get_session),
) -> None:
    validate_username(username)
    await crud.upsert_user(session, username, payload.dateOfBirth)


@app.get("/hello/{username}", response_model=BirthdayMessage)
async def get_birthday_message(
    username: str = Path(..., min_length=1, max_length=64),
    session: AsyncSession = Depends(db.get_session),
) -> BirthdayMessage:
    validate_username(username)

    user = await crud.get_user(session, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found",
        )

    days = calculate_days_to_birthday(user.date_of_birth, date.today())
    if days == 0:
        return BirthdayMessage(message=f"Hello, {username}! Happy birthday!")

    return BirthdayMessage(
        message=f"Hello, {username}! Your birthday is in {days} day(s)"
    )
