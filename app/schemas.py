from pydantic import BaseModel
from datetime import date
from typing import Optional

class PacienteCreate(BaseModel):
    email: str
    senha: str
    nome: str
    dt_nascimento: date
    formulario: Optional[dict]
    status_formulario: str
    id_responsavel: Optional[int]

class MedicoCreate(BaseModel):
    email: str
    senha: str
    nome: str
    dt_nascimento: date
    crm: str
    especialidade: str
