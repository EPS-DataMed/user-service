from pydantic import BaseModel
from typing import Optional

class DependentBase(BaseModel):
    dependent_id: int
    confirmed: Optional[bool] = False

class DependentCreate(DependentBase):
    user_id: int

class Dependent(DependentBase):
    user_id: int

    class Config:
        orm_mode = True
