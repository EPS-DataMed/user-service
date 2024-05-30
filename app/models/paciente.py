import enum
from sqlalchemy import Column, Integer, String, Date, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from .base import Base

class StatusEnum(enum.Enum):
    Preenchido = "Preenchido"
    EmAndamento = "Em andamento"
    NaoIniciado = "Não iniciado"

class Paciente(Base):
    __tablename__ = "pacientes"
    id_usuario = Column(Integer, primary_key=True, index=True)
    formulario = Column(JSONB)
    status_formulario = Column(Enum(StatusEnum), nullable=False)
    email = Column(String, unique=True, nullable=False)
    senha = Column(String, nullable=False)
    nome = Column(String, nullable=False)
    dt_nascimento = Column(Date, nullable=False)
    criado_em = Column(Date, nullable=False)
    id_responsavel = Column(Integer, ForeignKey('pacientes.id_usuario'))

    responsavel = relationship("Paciente", remote_side=[id_usuario])
