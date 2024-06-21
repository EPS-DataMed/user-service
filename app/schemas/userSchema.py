from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime
from typing import Optional

class UserBase(BaseModel):
    full_name: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    birth_date: Optional[date] = None
    biological_sex: Optional[str] = Field(None, max_length=1, pattern='^(M|F)$')

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserUpdate(UserBase):
    pass

class User(BaseModel):
    id: int
    full_name: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    birth_date: Optional[date] = None
    biological_sex: Optional[str] = Field(None, max_length=1, pattern='^(M|F)$')
    creation_date: datetime
    password: str

    class Config:
        orm_mode = True

class UserUpdatePassword(BaseModel):
    old_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)

class DoctorBase(BaseModel):
    crm: str = Field(..., max_length=50)
    specialty: str = Field(..., max_length=255)

class Doctor(DoctorBase):
    user_id: int

    class Config:
        orm_mode = True

class UserWithDoctor(User):
    doctor: Optional[Doctor] = None

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True
