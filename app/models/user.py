from pydantic import BaseModel, EmailStr, constr

class UserCreate(BaseModel):
    name: constr(min_length=1, max_length=50)
    email: EmailStr
    password: constr(min_length=6)

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    password: str

    class Config:
        orm_mode = True

