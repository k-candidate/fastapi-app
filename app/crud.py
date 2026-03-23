from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User


async def get_user(session: AsyncSession, username: str) -> User | None:
    result = await session.execute(
        select(User).where(User.username == username)
    )
    return result.scalars().first()


async def upsert_user(session: AsyncSession, username: str, dob: date) -> None:
    existing_user = await get_user(session, username)
    if existing_user:
        existing_user.date_of_birth = dob
        await session.commit()
        return

    user = User(username=username, date_of_birth=dob)
    session.add(user)
    await session.commit()
