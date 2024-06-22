from pydantic import BaseModel
from typing import Optional

class DependentBase(BaseModel):
    dependent_id: int
    confirmed: Optional[bool] = False

class DependentCreate(DependentBase):
    user_id: int

class Dependent(DependentBase):
    user_id: int
    user_full_name: Optional[str]
    user_birth_date: Optional[str]
    user_email: Optional[str]
    form_status: Optional[str]

    class Config:
        orm_mode = True
