from pydantic import BaseModel, EmailStr, constr, ConfigDict

class UserCreate(BaseModel):
    name: constr(min_length=1, max_length=50)
    email: EmailStr
    password: constr(min_length=6)

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    password: str

    model_config = ConfigDict(from_attributes=True)
