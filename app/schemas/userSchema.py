from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime

class UserBase(BaseModel):
    full_name: str = Field(..., max_length=255)
    email: EmailStr
    birth_date: date
    biological_sex: str = Field(..., max_length=1, pattern='^(M|F)$')

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserUpdate(UserBase):
    pass

class User(UserBase):
    id: int
    creation_date: datetime
    password: str

    class Config:
        orm_mode = True
