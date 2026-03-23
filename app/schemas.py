from datetime import date

from pydantic import BaseModel, Field, field_validator


class UserIn(BaseModel):
    dateOfBirth: date = Field(...)

    @field_validator("dateOfBirth")
    @classmethod
    def birth_date_before_today(cls, v: date) -> date:
        if v >= date.today():
            raise ValueError("dateOfBirth must be before today's date")
        return v


class BirthdayMessage(BaseModel):
    message: str
