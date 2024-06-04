from pydantic import BaseModel, Field

class MedicoBase(BaseModel):
    crm: str = Field(..., max_length=50)
    especialidade: str = Field(..., max_length=255)

class MedicoCreate(MedicoBase):
    id_usuario: int

class Medico(MedicoBase):
    id_usuario: int

    class Config:
        orm_mode = True