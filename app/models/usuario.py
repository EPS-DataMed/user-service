import enum
from sqlalchemy import Column, Integer, String, Date, Enum, ForeignKey, TIMESTAMP, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from .base import Base

class StatusEnum(enum.Enum):
    Preenchido = "Preenchido"
    EmAndamento = "Em andamento"
    NaoIniciado = "Não iniciado"

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nome_completo = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    senha = Column(String, nullable=False)
    data_nascimento = Column(Date, nullable=False)
    sexo_biologico = Column(String(1), nullable=False)
    data_criacao = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP')
    formulario = Column(JSONB)
    status_formulario = Column(String, nullable=False, default="Não iniciado")

class Dependente(Base):
    __tablename__ = "dependentes"
    id_usuario = Column(Integer, ForeignKey('usuarios.id'), primary_key=True)
    id_dependente = Column(Integer, ForeignKey('usuarios.id'), primary_key=True)
    confirmado = Column(Boolean, default=False)
