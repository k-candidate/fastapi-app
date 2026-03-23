from datetime import date

from sqlalchemy import Date, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(64), primary_key=True)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
