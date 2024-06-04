from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime
from typing import Optional

class UsuarioBase(BaseModel):
    nome_completo: str = Field(..., max_length=255)
    email: EmailStr
    data_nascimento: date
    sexo_biologico: str = Field(..., max_length=1, pattern='^(M|F)$')
    formulario: Optional[dict] = None
    status_formulario: Optional[str] = Field('Não iniciado', pattern='^(Preenchido|Em andamento|Não iniciado)$')

class UsuarioCreate(UsuarioBase):
    senha: str = Field(..., min_length=6)

class UsuarioUpdate(UsuarioBase):
    pass

class Usuario(UsuarioBase):
    id: int
    data_criacao: datetime
    senha: str

    class Config:
        orm_mode = True