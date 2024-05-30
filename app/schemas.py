from pydantic import BaseModel
from datetime import date
from typing import Optional

class UsuarioCreate(BaseModel):
    nome_completo: str
    email: str
    senha: str
    data_nascimento: date
    sexo_biologico: str
    formulario: Optional[dict] = None
    status_formulario: Optional[str] = "Não iniciado"

class MedicoCreate(BaseModel):
    id_usuario: int
    crm: str
    especialidade: str
