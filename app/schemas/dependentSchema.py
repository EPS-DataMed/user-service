from pydantic import BaseModel
from typing import Optional

class DependenteBase(BaseModel):
    id_dependente: int
    confirmado: Optional[bool] = False

class DependenteCreate(DependenteBase):
    id_usuario: int

class Dependente(DependenteBase):
    id_usuario: int

    class Config:
        orm_mode = True